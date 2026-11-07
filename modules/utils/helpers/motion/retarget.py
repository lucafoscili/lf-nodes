"""Skeleton-generic motion transfer using NumPy only.

Skeleton dictionaries contain ``names``, ``parents`` (indices, -1 for roots),
``rest_positions`` [joints, 3] and ``rest_rotations`` [joints, 4], both WORLD.
All quaternions are xyzw, Hamilton products, active rotations in a Y-up frame.
Pairs are (source name, target name); chains contain source/target name lists.
Translations other than the root remain the target adapter's rest translations.
"""

from __future__ import annotations

import numpy as np


_EPS = 1e-10
_IDENTITY = np.array([0., 0., 0., 1.])
_FINGERS = ("thumb", "index", "middle", "ring", "pinky", "little")


def quaternion_normalize(value):
    """Normalize finite nonzero xyzw quaternions, preserving leading axes."""
    value = np.asarray(value, dtype=np.float64)
    if value.shape[-1:] != (4,) or not np.isfinite(value).all():
        raise ValueError("Quaternions must be finite arrays ending in 4 values.")
    norm = np.linalg.norm(value, axis=-1, keepdims=True)
    if np.any(norm < _EPS):
        raise ValueError("Quaternions must be nonzero.")
    return value / norm


def quaternion_multiply(left, right):
    """Hamilton product: apply right, then left (NumPy broadcasting)."""
    left, right = np.broadcast_arrays(np.asarray(left, float), np.asarray(right, float))
    xyz = left[..., 3:] * right[..., :3] + right[..., 3:] * left[..., :3]
    xyz += np.cross(left[..., :3], right[..., :3])
    w = left[..., 3:] * right[..., 3:] - np.sum(left[..., :3] * right[..., :3], axis=-1, keepdims=True)
    return np.concatenate((xyz, w), axis=-1)


def quaternion_inverse(value):
    value = quaternion_normalize(value)
    return value * np.array([-1., -1., -1., 1.])


def quaternion_rotate(rotation, vector):
    rotation = quaternion_normalize(rotation)
    vector = np.asarray(vector, dtype=np.float64)
    cross = 2 * np.cross(rotation[..., :3], vector)
    return vector + rotation[..., 3:] * cross + np.cross(rotation[..., :3], cross)


def axis_angle_to_quaternion(value):
    """Convert rotation vectors in radians to xyzw, including zero angles."""
    value = np.asarray(value, dtype=np.float64)
    if value.shape[-1:] != (3,) or not np.isfinite(value).all():
        raise ValueError("Axis angles must be finite arrays ending in 3 values.")
    angle = np.linalg.norm(value, axis=-1, keepdims=True)
    factor = .5 * np.sinc(angle / (2 * np.pi))
    return np.concatenate((value * factor, np.cos(angle / 2)), axis=-1)


def quaternion_to_matrix(value):
    q = quaternion_normalize(value)
    x, y, z, w = np.moveaxis(q, -1, 0)
    return np.stack((1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w),
                     2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w),
                     2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)), axis=-1).reshape(q.shape[:-1] + (3, 3))


def quaternion_from_matrix(value):
    """Convert proper rotation matrices to normalized xyzw quaternions."""
    value = np.asarray(value, dtype=np.float64)
    if value.shape[-2:] != (3, 3) or not np.isfinite(value).all():
        raise ValueError("Rotation matrices must be finite arrays ending in [3, 3].")
    result = []
    for matrix in value.reshape(-1, 3, 3):
        # Select the largest squared component, avoiding unstable division near pi.
        candidates = np.array([1+matrix[0, 0]-matrix[1, 1]-matrix[2, 2],
                               1-matrix[0, 0]+matrix[1, 1]-matrix[2, 2],
                               1-matrix[0, 0]-matrix[1, 1]+matrix[2, 2],
                               1+np.trace(matrix)])
        index = int(np.argmax(candidates))
        q = np.empty(4)
        q[index] = np.sqrt(max(candidates[index], 0)) / 2
        denominator = 4 * q[index]
        if denominator < _EPS:
            raise ValueError("Rotation matrix does not describe a proper rotation.")
        if index == 3:
            q[:3] = [matrix[2, 1]-matrix[1, 2], matrix[0, 2]-matrix[2, 0], matrix[1, 0]-matrix[0, 1]]
            q[:3] /= denominator
        else:
            j, k = (index + 1) % 3, (index + 2) % 3
            q[j] = (matrix[j, index] + matrix[index, j]) / denominator
            q[k] = (matrix[k, index] + matrix[index, k]) / denominator
            q[3] = (matrix[k, j] - matrix[j, k]) / denominator
        result.append(q)
    return quaternion_normalize(np.asarray(result).reshape(value.shape[:-2] + (4,)))


def quaternion_slerp(start, end, weight):
    """Shortest-hemisphere spherical interpolation of cumulative orientations."""
    start, end = np.broadcast_arrays(quaternion_normalize(start), quaternion_normalize(end))
    dot = np.sum(start * end, axis=-1, keepdims=True)
    end = np.where(dot < 0, -end, end)
    dot = np.clip(np.abs(dot), 0., 1.)
    angle = np.arccos(dot)
    sine = np.sin(angle)
    weight = np.asarray(weight, dtype=np.float64)[..., None]
    denominator = np.maximum(sine, _EPS)
    spherical = (np.sin((1-weight)*angle) * start + np.sin(weight*angle) * end) / denominator
    return quaternion_normalize(np.where(dot > .9995, (1-weight)*start + weight*end, spherical))


def shortest_arc_rotation(start, end):
    """Smallest active rotation from start to end; degenerate rays give identity."""
    start, end = np.broadcast_arrays(np.asarray(start, float), np.asarray(end, float))
    a_norm, b_norm = np.linalg.norm(start, axis=-1, keepdims=True), np.linalg.norm(end, axis=-1, keepdims=True)
    valid = (a_norm > _EPS) & (b_norm > _EPS)
    a, b = start / np.maximum(a_norm, _EPS), end / np.maximum(b_norm, _EPS)
    dot = np.clip(np.sum(a*b, axis=-1, keepdims=True), -1., 1.)
    q = np.concatenate((np.cross(a, b), 1+dot), axis=-1)
    # Pick a stable perpendicular axis for opposite rays.
    basis = np.eye(3)[np.argmin(np.abs(a), axis=-1)]
    axis = np.cross(a, basis)
    axis /= np.maximum(np.linalg.norm(axis, axis=-1, keepdims=True), _EPS)
    q = np.where(dot < -1 + _EPS, np.concatenate((axis, np.zeros_like(dot)), axis=-1), q)
    return quaternion_normalize(np.where(valid, q, _IDENTITY))


def bind_alignment(target_ray, source_ray, *, flatten=False, name):
    """A = shortest arc carrying a target bind ray onto a source bind ray (Y-up).

    ``flatten`` projects both rays onto the horizontal XZ plane first. A zero
    ray is refused, naming the target bone ``name``, never aligned as identity.
    """
    if flatten:
        target_ray, source_ray = np.array(target_ray, float), np.array(source_ray, float)
        target_ray[1] = source_ray[1] = 0
    for side, ray in (("target", target_ray), ("source", source_ray)):
        if np.linalg.norm(ray) < _EPS:
            raise ValueError(f"Bind ray for target bone {name!r} has zero length on its {side} side"
                             f"{' after flatten_slope' if flatten else ''}; its joints coincide.")
    return shortest_arc_rotation(target_ray, source_ray)


def _parent_order(parents):
    parents = np.asarray(parents)
    if parents.ndim != 1 or not np.issubdtype(parents.dtype, np.integer):
        raise ValueError("Skeleton parents must be an integer array.")
    if np.any(parents < -1) or np.any(parents >= len(parents)):
        raise ValueError("Skeleton parent index is out of range.")
    order, placed, pending = [], set(), set(range(len(parents)))
    while pending:
        ready = [i for i in sorted(pending) if parents[i] == -1 or parents[i] in placed]
        if not ready:
            raise ValueError("Skeleton parents contain a cycle.")
        order.extend(ready)
        placed.update(ready)
        pending.difference_update(ready)
    return order


def world_to_local_rotations(world_rotations, parents):
    world = quaternion_normalize(world_rotations)
    if world.shape[-2] != len(parents):
        raise ValueError("Rotation joint count does not match parents.")
    _parent_order(parents)
    result = world.copy()
    for index, parent in enumerate(parents):
        if parent >= 0:
            result[..., index, :] = quaternion_multiply(quaternion_inverse(world[..., parent, :]), world[..., index, :])
    return quaternion_normalize(result)


def local_to_world_rotations(local_rotations, parents):
    local = quaternion_normalize(local_rotations)
    if local.shape[-2] != len(parents):
        raise ValueError("Rotation joint count does not match parents.")
    result = local.copy()
    for index in _parent_order(parents):
        parent = parents[index]
        if parent >= 0:
            result[..., index, :] = quaternion_multiply(result[..., parent, :], local[..., index, :])
    return quaternion_normalize(result)


def _skeleton(skeleton):
    names = list(skeleton["names"])
    if not names or any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError("Skeleton names must be unique nonempty strings.")
    parents = np.asarray(skeleton["parents"])
    _parent_order(parents)
    positions = np.asarray(skeleton["rest_positions"], dtype=np.float64)
    rotations = quaternion_normalize(skeleton["rest_rotations"])
    if parents.shape != (len(names),) or positions.shape != (len(names), 3) or rotations.shape != (len(names), 4):
        raise ValueError("Skeleton rest arrays must match the joint names.")
    if not np.isfinite(positions).all():
        raise ValueError("Skeleton rest positions must be finite.")
    return dict(names=names, parents=parents, rest_positions=positions, rest_rotations=rotations)


def _indices(skeleton, names):
    lookup = {name: index for index, name in enumerate(skeleton["names"])}
    try:
        return [lookup[name] for name in names]
    except KeyError as error:
        raise ValueError(f"Unknown skeleton bone: {error.args[0]}") from error


def _distance(skeleton, ancestor, child):
    distance = 0
    while child != ancestor and child >= 0:
        child = skeleton["parents"][child]
        distance += 1
    return distance if child == ancestor else None


def _direction(skeleton, index, mapped, semantic, mapped_semantics=None):
    preferred = {"pelvis": ("spine1", "spine2", "spine3", "neck", "head"),
                 "spine3": ("neck", "head")}.get(semantic, ())
    # The source anatomy identifies the designated branch even when its first
    # control is omitted from the map. The receiver uses its mapped counterpart.
    if preferred and mapped_semantics is None and preferred[0] in skeleton["names"]:
        child = skeleton["names"].index(preferred[0])
        if _distance(skeleton, index, child) is not None:
            return skeleton["rest_positions"][child] - skeleton["rest_positions"][index]
    candidates = [(depth, child) for child in mapped if child != index
                  for depth in [_distance(skeleton, index, child)] if depth is not None]
    if candidates:
        semantics = mapped_semantics or {}
        chosen = next((child for name in preferred for _, child in candidates
                       if semantics.get(child, skeleton["names"][child]) == name), None)
        if chosen is None:
            chosen = min(candidates)[1]
        return skeleton["rest_positions"][chosen] - skeleton["rest_positions"][index]
    if any(finger in semantic.lower() for finger in _FINGERS):
        parent = skeleton["parents"][index]
        if parent >= 0:
            return skeleton["rest_positions"][index] - skeleton["rest_positions"][parent]
    return None


def alignment_rotations(source_skeleton, target_skeleton, pairs, *, keep_rest_facing=(), flatten_slope=()):
    """Return one bind alignment A per pair, carrying target rays to source rays.

    Mapped leaves inherit their nearest mapped target ancestor's alignment.
    Terminal finger rays continue their incoming segment. Policies name targets;
    flatten_slope projects bind rays into XZ and never changes animated motion.
    """
    source, target = _skeleton(source_skeleton), _skeleton(target_skeleton)
    pairs = list(pairs)
    source_ids = _indices(source, [row[0] for row in pairs])
    target_ids = _indices(target, [row[1] for row in pairs])
    _indices(target, [*keep_rest_facing, *flatten_slope])
    keep, flat = set(keep_rest_facing), set(flatten_slope)
    target_semantics = {ti: source["names"][si] for si, ti in zip(source_ids, target_ids)}
    result, by_target = np.tile(_IDENTITY, (len(pairs), 1)), {}
    order = {index: position for position, index in enumerate(_parent_order(target["parents"]))}
    for row in sorted(range(len(pairs)), key=lambda i: order[target_ids[i]]):
        si, ti = source_ids[row], target_ids[row]
        if target["names"][ti] not in keep:
            ds = _direction(source, si, source_ids, source["names"][si])
            dt = _direction(target, ti, target_ids, source["names"][si], target_semantics)
            if ds is not None and dt is not None:
                result[row] = bind_alignment(dt, ds, flatten=target["names"][ti] in flat, name=target["names"][ti])
            else:
                parent = target["parents"][ti]
                while parent >= 0 and parent not in by_target:
                    parent = target["parents"][parent]
                if parent >= 0:
                    result[row] = by_target[parent]
        by_target[ti] = result[row]
    return result


def _chain_alignment(source, target, si, ti, source_ids, target_ids, target_semantics, keep, flat):
    """Bind alignment at a chain sample; terminal controls inherit ancestor rays."""
    original_target = ti
    if target["names"][ti] in keep:
        return _IDENTITY
    ds = _direction(source, si, source_ids, source["names"][si])
    dt = _direction(target, ti, target_ids, source["names"][si], target_semantics)
    while ds is None:
        si = source["parents"][si]
        if si < 0:
            return _IDENTITY
        if si in source_ids:
            ds = _direction(source, si, source_ids, source["names"][si])
    while dt is None:
        ti = target["parents"][ti]
        if ti < 0:
            return _IDENTITY
        if ti in target_ids:
            if target["names"][ti] in keep:
                return _IDENTITY
            dt = _direction(target, ti, target_ids, target_semantics.get(ti, source["names"][si]), target_semantics)
    flatten = target["names"][original_target] in flat or target["names"][ti] in flat
    return bind_alignment(dt, ds, flatten=flatten, name=target["names"][original_target])


def chain_stations(skeleton, controls):
    """Normalized bind arc length of each control along its actual ancestry, 0 to 1.

    ``skeleton`` needs ``parents`` and world ``rest_positions``; ``controls`` are
    joint indices, parent to child. Unmapped joints between two controls add
    their segments. A control that is not a descendant of the one before it, or
    two controls at one position, is refused.
    """
    parents, positions = skeleton["parents"], np.asarray(skeleton["rest_positions"], dtype=np.float64)
    stations = [0.]
    for previous, current in zip(controls, controls[1:]):
        length, index, steps = 0., current, 0
        while index != previous:
            parent = parents[index]
            steps += 1
            if parent < 0 or steps > len(parents):
                raise ValueError("Chain controls must follow parent-child ancestry.")
            length += np.linalg.norm(positions[index] - positions[parent])
            index = parent
        if length < _EPS:
            raise ValueError("Chain controls have coincident bind stations.")
        stations.append(stations[-1] + length)
    return np.asarray(stations) / stations[-1] if len(stations) > 1 else np.array([0.])


def station_bracket(source_stations, station):
    """The two source controls around a bind station and the slerp weight between them."""
    count = len(source_stations)
    lower = max(0, min(int(np.searchsorted(source_stations, station, side="right")) - 1, count - 1))
    upper = min(lower + 1, count - 1)
    if lower == upper:
        return lower, upper, 0.
    span = source_stations[upper] - source_stations[lower]
    return lower, upper, float(np.clip((station - source_stations[lower]) / span, 0, 1))


def resample_chain_rotations(world_rotations, source_stations, target_stations):
    """Resample cumulative WORLD orientations by normalized bind arc length.

    Equal counts retain ordered correspondence. Unlike local-bend interpolation,
    this preserves both endpoint orientations without multiplying bends twice.
    """
    rotations = quaternion_normalize(world_rotations)
    source_stations, target_stations = np.asarray(source_stations, float), np.asarray(target_stations, float)
    if rotations.shape[-2] != len(source_stations) or not len(source_stations) or not len(target_stations):
        raise ValueError("Chain stations must match nonempty rotation controls.")
    if not np.isfinite(source_stations).all() or not np.isfinite(target_stations).all() or np.any(np.diff(source_stations) <= 0):
        raise ValueError("Source chain stations must be finite and strictly increasing.")
    if len(source_stations) == len(target_stations):
        return rotations.copy()
    result = []
    for station in target_stations:
        lower, upper, weight = station_bracket(source_stations, station)
        result.append(quaternion_slerp(rotations[..., lower, :], rotations[..., upper, :], weight))
    return np.stack(result, axis=-2)


def leg_scale(source_skeleton, target_skeleton, pairs):
    """Target/source left thigh+shin length, requiring all three mapped joints."""
    source, target = _skeleton(source_skeleton), _skeleton(target_skeleton)
    mapping = dict(pairs)
    names = ("left_hip", "left_knee", "left_ankle")
    if not all(name in mapping for name in names):
        raise ValueError("Root scale requires mapped left_hip, left_knee and left_ankle; otherwise pass an explicit scale.")
    source_ids, target_ids = _indices(source, names), _indices(target, [mapping[name] for name in names])
    lengths = [sum(np.linalg.norm(sk["rest_positions"][b]-sk["rest_positions"][a]) for a, b in zip(ids, ids[1:]))
               for sk, ids in ((source, source_ids), (target, target_ids))]
    if min(lengths) < _EPS:
        raise ValueError("Mapped left thigh and shin must have nonzero combined length.")
    return float(lengths[1] / lengths[0])


def retarget_motion(source_world_rotations, source_root_positions, source_skeleton, target_skeleton, pairs,
                    *, chains=(), keep_rest_facing=(), flatten_slope=(), scale=None):
    """Transfer mapped world motion and return target locals and WORLD root track.

    W_target = W_source * inverse(W_source_rest) * A * W_target_rest.
    Unmapped joints retain their true target rest LOCAL rotation while following
    their animated parent. A target bone belongs to one pair or one chain.
    """
    source, target = _skeleton(source_skeleton), _skeleton(target_skeleton)
    world = quaternion_normalize(source_world_rotations)
    root = np.asarray(source_root_positions, dtype=np.float64)
    if world.ndim != 3 or world.shape[1] != len(source["names"]) or not len(world):
        raise ValueError("Source world rotations must have shape [frames, source joints, 4].")
    if root.shape != (len(world), 3) or not np.isfinite(root).all():
        raise ValueError("Source root positions must have shape [frames, 3] and be finite.")
    pairs = [tuple(row) for row in pairs]
    if any(len(row) != 2 for row in pairs) or len({row[1] for row in pairs}) != len(pairs):
        raise ValueError("Pairs require unique target bones and source/target name pairs.")
    source_ids = _indices(source, [row[0] for row in pairs])
    target_ids = _indices(target, [row[1] for row in pairs])
    plans = []
    # Chains are mapped anatomy too: the pelvis must see a chain-only spine1,
    # and ordinary leaves may inherit an alignment from a chain control.
    direction_mapping = {tn: sn for sn, tn in pairs}
    for chain in chains:
        sn, tn = list(chain["source"]), list(chain["target"])
        if not sn or not tn or len(set(sn)) != len(sn) or len(set(tn)) != len(tn):
            raise ValueError("Chains require nonempty unique source and target name runs.")
        sis, tis = _indices(source, sn), _indices(target, tn)
        shared = [name for name in tn if name in direction_mapping]
        if shared:
            raise ValueError(f"Target bone {shared[0]!r} is named by more than one pair or chain.")
        ss, ts = chain_stations(source, sis), chain_stations(target, tis)
        plans.append((sis, tis, ss, ts))
        for position, target_name in enumerate(tn):
            nearest = position if len(sis) == len(tis) else int(np.argmin(np.abs(ss-ts[position])))
            direction_mapping.setdefault(target_name, sn[nearest])
    direction_pairs = [(sn, tn) for tn, sn in direction_mapping.items()]
    direction_alignments = alignment_rotations(source, target, direction_pairs,
                                              keep_rest_facing=keep_rest_facing, flatten_slope=flatten_slope)
    by_target_name = {tn: alignment for (_, tn), alignment in zip(direction_pairs, direction_alignments)}
    alignments = [by_target_name[tn] for _, tn in pairs]
    desired = {}
    for si, ti, alignment in zip(source_ids, target_ids, alignments):
        delta = quaternion_multiply(world[:, si], quaternion_inverse(source["rest_rotations"][si]))
        desired[ti] = quaternion_multiply(quaternion_multiply(delta, alignment), target["rest_rotations"][ti])
    mapped_source = sorted(set(source_ids).union(*(set(plan[0]) for plan in plans)))
    mapped_target = sorted(set(target_ids).union(*(set(plan[1]) for plan in plans)))
    target_semantics = {target["names"].index(tn): sn for sn, tn in direction_pairs}
    for sis, tis, ss, ts in plans:
        # Alignment of each source control to each target station precedes slerp.
        for position, ti in enumerate(tis):
            station = ss[position] if len(sis) == len(tis) else ts[position]
            lower, upper, weight = station_bracket(ss, station)
            samples = []
            for si in (sis[lower], sis[upper]):
                alignment = _chain_alignment(source, target, si, ti, mapped_source, mapped_target,
                                             target_semantics, keep_rest_facing, flatten_slope)
                delta = quaternion_multiply(world[:, si], quaternion_inverse(source["rest_rotations"][si]))
                samples.append(quaternion_multiply(quaternion_multiply(delta, alignment), target["rest_rotations"][ti]))
            desired[ti] = quaternion_slerp(samples[0], samples[1], weight)
    rest_local = world_to_local_rotations(target["rest_rotations"], target["parents"])
    output = np.broadcast_to(rest_local, (len(world), len(rest_local), 4)).copy()
    output_world = output.copy()
    for ti in _parent_order(target["parents"]):
        parent = target["parents"][ti]
        if ti in desired:
            output[:, ti] = desired[ti] if parent < 0 else quaternion_multiply(quaternion_inverse(output_world[:, parent]), desired[ti])
        output_world[:, ti] = output[:, ti] if parent < 0 else quaternion_multiply(output_world[:, parent], output[:, ti])
    root_row = next((i for i, (name, _) in enumerate(pairs) if name == "pelvis"), None)
    if root_row is None:
        root_row = next((i for i, si in enumerate(source_ids) if source["parents"][si] < 0), None)
    if root_row is None:
        raise ValueError("Pairs must map the source pelvis or a source root bone.")
    si, ti = source_ids[root_row], target_ids[root_row]
    scale = leg_scale(source, target, pairs) if scale is None else float(scale)
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("Root motion scale must be positive and finite.")
    return {"local_rotations": quaternion_normalize(output),
            "root_positions": target["rest_positions"][ti] + (root-source["rest_positions"][si])*scale,
            "scale": scale}
