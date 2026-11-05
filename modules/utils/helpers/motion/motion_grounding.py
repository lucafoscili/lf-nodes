"""Stand a captured SMPL-X motion on one floor by its target body's own feet.

Run only inside RGB MoCap's pinned runtime (beside ``rgb_mocap_bridge.py``), never inside the Comfy host: it
imports the app's ``mocap.correction`` and ``mocap.contact_trajectory`` lazily and edits nothing of the app.

A monocular capture under a fixed-camera assumption reads camera motion as body motion, and a foot it cannot
see is often guessed standing on its heel. Before the app's Motion Correction solves the legs on the target
body, ``prepare`` takes the capture in steps:

- ``camera_drift``: the drift along the floor, read off the material under the most planted held foot (heel
  and toe blended by the app's support weights), carried across frames with no held foot, smoothed and taken
  out of the root. A planted foot's material only moves because the camera did.
- ``stand_upright``, under a camera that pushes in: along the camera's horizontal view, the pelvis stays over
  the middle of both soles at its offset from the opening stance, turned with the body's heading; across the
  view the capture stands. A push-in is read from the data, as the drift along the camera's view
  (``push_in_reading``), unless the caller says.
- ``flatten_heels``: a held foot on its heel with its toes lifted by a few centimetres is pitched about its
  ankle until its toes meet the floor; a foot on its toes stays as it is.
- ``planted`` spans (seconds) hold both feet on the floor whatever the capture's static confidence says.

``solve`` runs the app's solver on prepared arrays with the app's recorded options, and ``seat_on_floor``
rests a seat that sinks below the floor after the solve on it, bending the legs to keep the ankles. ``stand``
runs all three. Arrays follow the app: ``root`` (n, 3) the pelvis joint in metres, ``quat`` (n, 22, 4)
local joint quaternions, w first, Y up.
"""

from __future__ import annotations

# SMPL-X joints: the ankle and foot (toe) joints of the app's feet 0 and 1, each leg's hip, knee and ankle,
# the joints Motion Correction solves, and the joints whose skin a seat rests on (pelvis and hips).
FEET = (("left", (7, 10)), ("right", (8, 11)))
LEGS = ((1, 4, 7), (2, 5, 8))
SOLVED_JOINTS = (1, 2, 4, 5, 7, 8)
SEAT_JOINTS = (0, 1, 2)
DEFAULTS = dict(
    drift_smooth_seconds=0.15,  # the camera's drift is smoothed with this Gaussian sigma
    upright_smooth_seconds=0.1,  # the pelvis's shift over the feet under a push-in, smoothed
    opening_seconds=0.5,  # the opening stance whose pelvis-over-feet offset a push-in keeps
    flat_toes=(0.005, 0.06),  # metres: a held foot on its heel with its toes up by this much is set flat
    flat_smooth_seconds=0.1,  # its pitch eases in and out over this sigma
    seat_smooth_seconds=0.1,  # a seat's rise onto the floor eases in and out over this sigma
    push_in_metres=0.15,  # drift along the camera's view beyond this reads as a push-in
)


def rotation_between(a, b):
    """The smallest rotations taking each direction in a onto the matching one in b, as matrices."""
    import numpy as np
    from scipy.spatial.transform import Rotation
    a = a / np.linalg.norm(a, axis=-1, keepdims=True)
    b = b / np.linalg.norm(b, axis=-1, keepdims=True)
    axis = np.cross(a, b)
    sin = np.linalg.norm(axis, axis=-1, keepdims=True)
    angle = np.arctan2(sin, (a * b).sum(axis=-1, keepdims=True))
    return Rotation.from_rotvec(np.where(sin > 1e-12, axis / np.maximum(sin, 1e-12), 0.0) * angle).as_matrix()


def as_quat(matrices):
    """Rotation matrices as Motion Correction's quaternions, w first."""
    from scipy.spatial.transform import Rotation
    return Rotation.from_matrix(matrices).as_quat()[..., [3, 0, 1, 2]]


def arrays_from_params(params, rest_pelvis):
    """SMPL-X world parameters (global_orient, body_pose, transl) as the solver's root and quaternions."""
    import numpy as np
    from scipy.spatial.transform import Rotation
    n = len(params["transl"])
    rotvec = np.concatenate([np.asarray(params["global_orient"])[:, None],
                             np.asarray(params["body_pose"]).reshape(n, 21, 3)], axis=1)
    quat = Rotation.from_rotvec(rotvec.reshape(-1, 3)).as_quat().reshape(n, 22, 4)[..., [3, 0, 1, 2]]
    return np.asarray(params["transl"], dtype="float64") + rest_pelvis, quat


def to_world(raw, root, quat, rest_pelvis):
    """Solved arrays as world parameters, as the app writes its result: the capture's root orientation, upper
    body and fingers, the solved legs (SOLVED_JOINTS) and the root."""
    import numpy as np
    from scipy.spatial.transform import Rotation
    n = len(root)
    pose = Rotation.from_quat(quat[..., [1, 2, 3, 0]].reshape(-1, 4)).as_rotvec().reshape(n, 22, 3)
    body_pose = np.array(raw["body_pose"], dtype="float64", copy=True)
    for joint in SOLVED_JOINTS:
        body_pose[:, 3 * (joint - 1):3 * joint] = pose[:, joint]
    return dict(global_orient=raw["global_orient"], body_pose=body_pose, transl=root - rest_pelvis,
                left_hand_pose=raw["left_hand_pose"], right_hand_pose=raw["right_hand_pose"])


def view_directions(camera_orient, world_orient):
    """The camera's horizontal view per frame in the world, (n, 3): the in-camera root orientation against the
    world one gives each frame's world-to-camera rotation, whose z row (OpenCV) is where it looks."""
    import numpy as np
    from scipy.spatial.transform import Rotation
    to_camera = (Rotation.from_rotvec(camera_orient) * Rotation.from_rotvec(world_orient).inv()).as_matrix()
    view = to_camera[:, 2].copy()
    view[:, 1] = 0
    return view / np.linalg.norm(view, axis=1, keepdims=True)


def camera_drift(probes, held, fps, smooth_seconds=DEFAULTS["drift_smooth_seconds"]):
    """The camera's drift along the floor, (n, 2) in x and z, read off the held feet (see the module note)."""
    import numpy as np
    from scipy.ndimage import gaussian_filter1d
    from mocap.contact_trajectory import support_weights
    n = len(probes)
    toes = support_weights(probes, held, fps)
    patches = probes.reshape(n, 2, 2, 3)[..., [0, 2]]  # frame, foot, heel or toe, x and z
    share = 0.5 * (toes[1:] + toes[:-1])[..., None]
    step = (1 - share) * np.diff(patches[:, :, 0], axis=0) + share * np.diff(patches[:, :, 1], axis=0)
    speed = np.where(held[1:] & held[:-1], np.linalg.norm(step, axis=-1), np.inf)
    known = np.isfinite(speed.min(axis=1))
    if not known.any():
        raise ValueError("No foot is held over two frames running, so nothing reads the camera's drift.")
    drift = step[np.arange(n - 1), speed.argmin(axis=1)]
    for axis in range(2):
        drift[:, axis] = np.interp(np.arange(n - 1), np.flatnonzero(known), drift[known, axis])
    total = np.zeros((n, 2))
    total[1:] = np.cumsum(gaussian_filter1d(drift, smooth_seconds * fps, axis=0, mode="nearest"), axis=0)
    return total


def push_in_reading(drift, view):
    """How far the camera moved along its own horizontal view over the clip (metres, the largest excursion from
    the first frame): a camera pushing in or pulling out, which a fixed-camera capture reads as walking."""
    import numpy as np
    along = drift[:, 0] * view[:, 0] + drift[:, 1] * view[:, 2]
    return float(np.abs(along - along[0]).max())


def stand_upright(geometry, root, quat, view, opening, fps, smooth_seconds=DEFAULTS["upright_smooth_seconds"]):
    """Under a camera that pushes in: along its horizontal view, (n, 3), the pelvis stays over the middle of the
    soles as it stood through the first `opening` frames, that offset turned with the heading; across the view
    the capture stands. The root moves and both legs swing at the hips, so the feet stay where they were and the
    ankles keep their world rotation. Returns the root, the quaternions and how far the pelvis moved per frame."""
    import numpy as np
    from scipy.ndimage import gaussian_filter1d
    from mocap.correction import fk
    positions, rotations = fk(geometry.rest[:22], root, quat)
    feet = geometry.sample(root, quat)[0].mean(axis=1)  # both feet, always: the held ones alone jump at each change
    forward = rotations[:, 0] @ np.array([0.0, 0.0, 1.0])
    forward[:, 1] = 0
    forward /= np.linalg.norm(forward, axis=1, keepdims=True)
    left = np.cross(np.array([0.0, 1.0, 0.0]), forward)
    offset = root - feet
    offset[:, 1] = 0
    ahead = (offset * forward).sum(axis=1)[:opening].mean()
    aside = (offset * left).sum(axis=1)[:opening].mean()
    shift = ((ahead * forward + aside * left - offset) * view).sum(axis=1)
    delta = gaussian_filter1d(shift, smooth_seconds * fps, mode="nearest")[:, None] * view
    quat = quat.copy()
    for hip, knee, ankle in LEGS:
        leg = positions[:, ankle] - positions[:, hip]
        swing = rotation_between(leg, leg - delta)
        quat[:, hip] = as_quat(np.einsum("tji,tjk->tik", rotations[:, 0], swing @ rotations[:, hip]))
        quat[:, ankle] = as_quat(np.einsum("tji,tjk->tik", swing @ rotations[:, knee], rotations[:, ankle]))
    return root + delta, quat, np.linalg.norm(delta, axis=1)


def flatten_heels(geometry, root, quat, held, fps, rounds=2, toes=DEFAULTS["flat_toes"],
                  smooth_seconds=DEFAULTS["flat_smooth_seconds"]):
    """A held foot standing on its heel with its toes lifted by `toes` (metres), pitched about its ankle until
    the front of its sole meets the back; a foot on its toes stays as it is. The pitch eases in and out, and a
    second round takes up what the first left. Returns the quaternions and the pitch given each frame and foot."""
    import numpy as np
    from scipy.ndimage import gaussian_filter1d
    from scipy.spatial.transform import Rotation
    from mocap.correction import fk
    n = len(root)
    quat = quat.copy()
    given = np.zeros((n, 2))
    for _ in range(rounds):
        probes = geometry.sample(root, quat)[0]
        rotations = fk(geometry.rest[:22], root, quat)[1]
        need, axes = np.zeros((n, 2)), np.zeros((n, 2, 3))
        for k in range(2):
            heel, toe = probes[:, 2 * k], probes[:, 2 * k + 1]
            lift = toe[:, 1] - heel[:, 1]
            run = (toe - heel) * np.array([1.0, 0.0, 1.0])
            length = np.linalg.norm(run, axis=1)
            on = held[:, k] & (lift > toes[0]) & (lift < toes[1])
            need[:, k] = np.where(on, np.arctan2(lift, np.maximum(length, 1e-3)), 0.0)
            axes[:, k] = np.cross(np.array([0.0, 1.0, 0.0]), run / np.maximum(length, 1e-9)[:, None])
        need = gaussian_filter1d(need, smooth_seconds * fps, axis=0, mode="nearest")
        given += need
        for k, (_, (ankle, _)) in enumerate(FEET):
            pitch = Rotation.from_rotvec(axes[:, k] * need[:, k, None]).as_matrix()
            parent = rotations[:, geometry.parents[ankle]]
            quat[:, ankle] = as_quat(np.einsum("tji,tjk->tik", parent, pitch @ rotations[:, ankle]))
    return quat, given


def planted_frames(spans, fps, n):
    """Seconds spans [[first, last], ...] as a boolean (n,) mask; a span outside the clip refuses."""
    import numpy as np
    mask = np.zeros(n, bool)
    for first, last in spans:
        a, b = round(first * fps), round(last * fps)
        if not 0 <= a < b <= n:
            raise ValueError(f"Planted span {first}-{last} s lies outside the {n / fps:.2f} s clip.")
        mask[a:b] = True
    return mask


def prepare(geometry, root, quat, probabilities, held, fps, view, *, planted=(), push_in=None, settings=None):
    """The capture prepared for the solve, as the module note says. `held` (n, 2) are the feet the app's own
    correction held; `probabilities` (n, 4) the heel and toe static confidences, left then right; `view` the
    camera's horizontal view (view_directions). `push_in` None reads it from the drift along the view. Returns
    the root, quaternions, probabilities and held feet, the drift, the push-in reading and a line per step."""
    import numpy as np
    s = dict(DEFAULTS, **(settings or {}))
    probabilities, held = np.array(probabilities, dtype="float64", copy=True), np.array(held, bool, copy=True)
    root = np.array(root, dtype="float64", copy=True)
    mask = planted_frames(planted, fps, len(root))
    probabilities[mask], held[mask] = 1.0, True
    drift = camera_drift(geometry.sample(root, quat)[0], held, fps, s["drift_smooth_seconds"])
    reading = push_in_reading(drift, view)
    root[:, [0, 2]] -= drift
    steps = [f"the camera's drift taken out: {np.linalg.norm(drift[-1]) * 100:.1f} cm over the clip, at most "
             f"{np.linalg.norm(drift, axis=1).max() * 100:.1f} cm ({reading * 100:.1f} cm along its view)"]
    pushed = reading > s["push_in_metres"] if push_in is None else bool(push_in)
    if pushed:
        root, quat, moved = stand_upright(geometry, root, quat, view, round(s["opening_seconds"] * fps), fps,
                                          s["upright_smooth_seconds"])
        steps.append(("a push-in read from the camera" if push_in is None else "a push-in, as told")
                     + f": the pelvis kept over the feet along its view, moved by up to {moved.max() * 100:.1f} cm")
    quat, pitch = flatten_heels(geometry, root, quat, held, fps, toes=s["flat_toes"],
                                smooth_seconds=s["flat_smooth_seconds"])
    degrees = np.rad2deg(np.abs(pitch))
    steps.append(f"held feet on their heels set flat: up to {degrees.max():.1f} degrees; frames pitched over 2 "
                 f"degrees: left {(degrees[:, 0] > 2).sum()}, right {(degrees[:, 1] > 2).sum()}")
    if mask.any():
        steps.append("both feet planted at " + ", ".join(f"{a}-{b} s" for a, b in planted))
    return dict(root=root, quat=quat, probabilities=probabilities, held=held, drift=drift, push_in=pushed,
                push_in_reading=reading, steps=steps)


def solve(geometry, root, quat, probabilities, fps, options):
    """The app's solver on prepared arrays, with the options its correction recorded. Returns the root, the
    quaternions and its report."""
    import numpy as np
    from mocap.correction import correct_arrays
    out_root, out_quat = np.empty_like(root), np.empty_like(quat)
    report = correct_arrays(geometry.rest[:22], root, quat, geometry.sample(root, quat)[0], probabilities, fps,
                            None if options["auto_floor"] else float(options["floor"]), output=(out_root, out_quat),
                            preset=options["preset"], contact_ranges=None if options["foot_lock"] else [[], []],
                            pelvis_offset=options["pelvis_offset"], mode=options["mode"],
                            foot_enabled=options["foot_lock"])[2]
    return out_root, out_quat, report


def raise_pelvis(geometry, root, quat, rise):
    """The pelvis raised by `rise` (metres per frame) with each leg bent at its hip and knee, in the knee's own
    plane, so its ankle stays where it was with its world rotation. Returns the root and the quaternions."""
    import numpy as np
    from scipy.spatial.transform import Rotation
    from mocap.correction import fk
    positions, rotations = fk(geometry.rest[:22], root, quat)
    up = np.zeros_like(root)
    up[:, 1] = rise
    moving = rise > 0
    out = quat.copy()
    for hip, knee, ankle in LEGS:
        h, k, a = positions[:, hip] + up, positions[:, knee], positions[:, ankle]
        thigh = np.linalg.norm(k - positions[:, hip], axis=1)
        shin = np.linalg.norm(a - k, axis=1)
        reach = np.linalg.norm(a - h, axis=1)
        toward = (a - h) / reach[:, None]
        reach = np.clip(reach, np.abs(thigh - shin) + 1e-4, thigh + shin - 1e-4)
        bend = np.arccos(np.clip((thigh ** 2 + reach ** 2 - shin ** 2) / (2 * thigh * reach), -1.0, 1.0))
        side = np.cross(toward, k - h)  # the old knee's side of the line from the raised hip to the ankle
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        knee_at = h + thigh[:, None] * np.einsum(
            "tij,tj->ti", Rotation.from_rotvec(side * bend[:, None]).as_matrix(), toward)
        turn = rotation_between(k - positions[:, hip], knee_at - h)
        hip_world = turn @ rotations[:, hip]
        knee_world = rotation_between(np.einsum("tij,tj->ti", turn, a - k), a - knee_at) @ turn @ rotations[:, knee]
        for joint, local in ((hip, np.einsum("tji,tjk->tik", rotations[:, 0], hip_world)),
                             (knee, np.einsum("tji,tjk->tik", hip_world, knee_world)),
                             (ankle, np.einsum("tji,tjk->tik", knee_world, rotations[:, ankle]))):
            out[moving, joint] = as_quat(local[moving])
    return root + up, out


def seat_on_floor(geometry, root, quat, floor, fps, seat_lowest, rounds=2,
                  smooth_seconds=DEFAULTS["seat_smooth_seconds"]):
    """Where the seat sinks below the floor while the solve holds the feet on it, the pelvis rises until the seat
    rests on the floor, easing in and out, and the legs bend to keep the ankles (raise_pelvis); a second round
    takes up what the first left. `seat_lowest(root, quat)` gives each frame's lowest height of the skin
    SEAT_JOINTS carry, on the target body. Returns the root, the quaternions and the rise per frame."""
    import numpy as np
    from scipy.ndimage import gaussian_filter1d, maximum_filter1d
    total = np.zeros(len(root))
    for _ in range(rounds):
        sink = np.maximum(floor - seat_lowest(root, quat), 0)
        if not sink.any():
            break
        reach = round(smooth_seconds * fps)
        envelope = maximum_filter1d(sink, size=2 * reach + 1, mode="nearest")
        rise = np.maximum(gaussian_filter1d(envelope, smooth_seconds * fps, mode="nearest"), sink)
        root, quat = raise_pelvis(geometry, root, quat, rise)
        total += rise
    return root, quat, total


def stand(geometry, root, quat, probabilities, held, fps, view, options, *, planted=(), push_in=None,
          seat_lowest=None, settings=None):
    """prepare, solve and, given `seat_lowest`, seat_on_floor. Returns the solved root and quaternions, the floor,
    the feet the solve held (n, 2), its report, the push-in reading and a line per step."""
    import numpy as np
    s = dict(DEFAULTS, **(settings or {}))
    ready = prepare(geometry, root, quat, probabilities, held, fps, view, planted=planted, push_in=push_in,
                    settings=s)
    out_root, out_quat, report = solve(geometry, ready["root"], ready["quat"], ready["probabilities"], fps, options)
    floor = float(report["floor"])
    steps = ready["steps"] + [f"solved: floor {floor * 100:.2f} cm, {len(report['segments'])} holds, goal error at "
                              f"most {report['max_contact_goal_error_m'] * 100:.2f} cm"]
    if seat_lowest is not None:
        out_root, out_quat, rise = seat_on_floor(geometry, out_root, out_quat, floor, fps, seat_lowest,
                                                 smooth_seconds=s["seat_smooth_seconds"])
        if rise.any():
            steps.append(f"the seat rested on the floor: the pelvis raised by up to {rise.max() * 100:.1f} cm over "
                         f"{(rise > 0.005).sum()} frames, the legs bent to keep the feet where they stand")
    contact = np.zeros((len(root), 2), bool)
    for segment in report["segments"]:
        contact[segment["start"]:segment["end"], segment["foot"]] = True
    return dict(root=out_root, quat=out_quat, floor=floor, contact=contact, report=report, push_in=ready["push_in"],
                push_in_reading=ready["push_in_reading"], steps=steps)
