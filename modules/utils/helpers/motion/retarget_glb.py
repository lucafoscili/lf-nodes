"""GLB target admission, append-only motion animation, and bounded CPU skinning.

Scene node TRS defines retarget rest; inverse bind matrices belong only to
skinning. No scene, material, mesh, existing animation, or original BIN byte is
rewritten. This adapter never saves files or downloads assets.
"""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np

from ...glb_texture import pack_glb, read_glb
from ...glb_transform import _graph


_COMPONENTS = {5120: 'i1', 5121: 'u1', 5122: '<i2', 5123: '<u2', 5125: '<u4', 5126: '<f4'}
_WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def _rotations():
    from .retarget import quaternion_from_matrix, quaternion_to_matrix
    return quaternion_from_matrix, quaternion_to_matrix


def _blob(source):
    return bytes(source) if isinstance(source, (bytes, bytearray, memoryview)) else Path(source).read_bytes()


def _accessor(document, binary, index):
    """Decode embedded, strided/normalized accessors, including sparse patches."""
    try:
        accessor = document['accessors'][index]
        dtype = np.dtype(_COMPONENTS[accessor['componentType']])
        width = _WIDTHS[accessor['type']]
        count = accessor['count']
        if type(index) is not int or index < 0 or type(count) is not int or count < 0:
            raise ValueError('Invalid GLB accessor index or count.')
        def read(view_index, offset, rows, columns, component):
            view = document['bufferViews'][view_index]
            if type(view_index) is not int or view_index < 0:
                raise ValueError('Invalid GLB accessor bufferView.')
            if 'EXT_meshopt_compression' in view.get('extensions', {}):
                raise ValueError('GLB EXT_meshopt_compression geometry requires a separate decoder.')
            stride = view.get('byteStride', columns * component.itemsize)
            required = 0 if rows == 0 else (rows - 1) * stride + columns * component.itemsize
            if (type(offset) is not int or offset < 0 or type(stride) is not int
                    or stride < columns * component.itemsize or offset + required > view['byteLength']):
                raise ValueError('GLB accessor extends outside its bufferView.')
            return np.ndarray((rows, columns), dtype=component, buffer=binary,
                              offset=view.get('byteOffset', 0) + offset,
                              strides=(stride, component.itemsize)).copy()
        if 'bufferView' in accessor:
            values = read(accessor['bufferView'], accessor.get('byteOffset', 0), count, width, dtype)
        else:
            values = np.zeros((count, width), dtype=dtype)
        if 'sparse' in accessor:
            sparse = accessor['sparse']
            indices = sparse['indices']
            if indices['componentType'] not in (5121, 5123, 5125):
                raise ValueError('GLB sparse indices must be unsigned integers.')
            rows = read(indices['bufferView'], indices.get('byteOffset', 0), sparse['count'], 1,
                        np.dtype(_COMPONENTS[indices['componentType']])).ravel()
            if np.any(rows >= count) or len(np.unique(rows)) != len(rows):
                raise ValueError('GLB sparse accessor indices are invalid.')
            patches = sparse['values']
            values[rows] = read(patches['bufferView'], patches.get('byteOffset', 0), len(rows), width, dtype)
        if accessor.get('normalized') and dtype.kind in 'iu':
            info = np.iinfo(dtype)
            values = np.maximum(values.astype(np.float64) / info.max, -1)
        if not np.isfinite(values).all():
            raise ValueError('GLB accessor contains nonfinite values.')
        return values[:, 0] if width == 1 else values
    except (KeyError, IndexError, TypeError, OverflowError) as error:
        raise ValueError(f'Unsupported or malformed GLB accessor {index}.') from error


def _local_matrix(node):
    if 'matrix' in node:
        matrix = np.asarray(node['matrix'], dtype=np.float64)
        if matrix.shape != (16,) or any(key in node for key in ('translation', 'rotation', 'scale')):
            raise ValueError('GLB node matrix must contain 16 values and cannot coexist with TRS.')
        matrix = matrix.reshape(4, 4).T.copy()
    else:
        translation = np.asarray(node.get('translation', [0, 0, 0]), dtype=np.float64)
        rotation = np.asarray(node.get('rotation', [0, 0, 0, 1]), dtype=np.float64)
        scale = np.asarray(node.get('scale', [1, 1, 1]), dtype=np.float64)
        if translation.shape != (3,) or rotation.shape != (4,) or scale.shape != (3,):
            raise ValueError('GLB node TRS dimensions are invalid.')
        if not np.isclose(np.linalg.norm(rotation), 1, atol=1e-5):
            raise ValueError('GLB node rotation must be a unit xyzw quaternion.')
        matrix = np.eye(4)
        matrix[:3, :3] = _rotations()[1](rotation) * scale[None, :]
        matrix[:3, 3] = translation
    if not np.isfinite(matrix).all() or not np.allclose(matrix[3], [0, 0, 0, 1]):
        raise ValueError('GLB node transform must be finite and affine.')
    return matrix


def _world_matrices(local, parents):
    result = np.empty_like(local)
    done = set()
    def visit(index):
        if index not in done:
            parent = parents.get(index)
            result[index] = local[index] if parent is None else visit(parent) @ local[index]
            done.add(index)
        return result[index]
    for index in range(len(local)):
        visit(index)
    return result


def load_glb_target(source, bone_map=None):
    """Load one named skin; expose joints and their complete scene ancestry.

    ``bone_map`` may be a source-name -> target-name dict or pair sequence; when
    supplied the measured +Y-up/+Z-facing contract is checked immediately.
    """
    document, binary = read_glb(_blob(source))
    nodes, parents, _ = _graph(document)
    if len(document.get('skins', [])) != 1:
        raise ValueError('Motion retargeting requires exactly one GLB skin.')
    joint_nodes = document['skins'][0]['joints']
    names = [nodes[index].get('name') for index in joint_nodes]
    if any(not isinstance(name, str) or not name.strip() for name in names) or len(set(names)) != len(names):
        raise ValueError('Every GLB skin joint must have a distinct nonempty name.')
    if any('matrix' in nodes[index] for index in joint_nodes):
        raise ValueError('Animated GLB skin joints must use TRS, not matrix transforms; export joint TRS first.')
    selected = set(joint_nodes)
    for index in joint_nodes:
        while index in parents:
            index = parents[index]
            selected.add(index)
    node_indices = sorted(selected)
    local = np.stack([_local_matrix(node) for node in nodes])
    world = _world_matrices(local, parents)
    local_rotations = []
    for index in range(len(nodes)):
        if index not in selected:
            local_rotations.append([0, 0, 0, 1])
            continue
        if np.linalg.det(local[index, :3, :3]) < 0:
            # The solve chains rotations only; a mirror would pose every descendant wrongly.
            raise ValueError(f'GLB node {nodes[index].get("name", index)!r} is mirrored (negative scale); '
                             'retargeting needs an unmirrored skeleton.')
        if 'matrix' not in nodes[index]:
            local_rotations.append(nodes[index].get('rotation', [0, 0, 0, 1]))
            continue
        basis = local[index, :3, :3]
        scale = np.linalg.norm(basis, axis=0)
        unit = basis / np.maximum(scale, 1e-30)
        if (np.any(scale < 1e-10)
                or not np.allclose(unit.T @ unit, np.eye(3), atol=1e-6)):
            raise ValueError('GLB matrix ancestor must decompose to nonsingular TRS without shear.')
        local_rotations.append(_rotations()[0](unit))
    from .retarget import local_to_world_rotations
    rotations = local_to_world_rotations(np.asarray(local_rotations),
                                        [parents.get(index, -1) for index in range(len(nodes))])
    used_names = set(names)
    skeleton_names = []
    for index in node_indices:
        name = nodes[index].get('name')
        if index not in joint_nodes and (not isinstance(name, str) or not name or name in used_names):
            name = f'__lf_node_{index}'
            while name in used_names:
                name += '_'
        skeleton_names.append(name)
        used_names.add(name)
    lookup = {node: index for index, node in enumerate(node_indices)}
    skeleton = {'names': skeleton_names,
                'parents': np.array([lookup[parents[node]] if node in parents else -1 for node in node_indices]),
                'rest_positions': world[node_indices, :3, 3].copy(),
                'rest_rotations': rotations[node_indices]}
    target = dict(document=document, binary=binary, joint_nodes=joint_nodes,
                  node_indices=node_indices, skeleton=skeleton, parents=parents,
                  local_matrices=local, world_matrices=world)
    if bone_map is not None:
        target['axis_report'] = validate_glb_axes(target, bone_map)
    return target


def validate_glb_axes(target, pairs):
    """Measure mapped pelvis, head (or neck) and left hip; never rotate or infer from names."""
    pairs = dict(pairs)
    skeleton = target['skeleton']
    up_joint = 'head' if 'head' in pairs else 'neck'
    try:
        indices = {key: skeleton['names'].index(pairs[key]) for key in ('pelvis', up_joint, 'left_hip')}
    except (KeyError, ValueError) as error:
        raise ValueError('GLB axis admission requires mapped pelvis, head or neck, and left_hip joints.') from error
    if any(target['node_indices'][index] not in target['joint_nodes'] for index in indices.values()):
        raise ValueError('Mapped GLB axis joints must identify skin joints, not scene ancestors.')
    points = skeleton['rest_positions']
    up = points[indices[up_joint]] - points[indices['pelvis']]
    left = points[indices['left_hip']] - points[indices['pelvis']]
    height = np.linalg.norm(up)
    width = np.linalg.norm(left)
    if height < 1e-8 or up[1] <= 1e-8:
        raise ValueError(f'GLB rest must be +Y-up: measured pelvis-to-{up_joint} {up.tolist()}; no automatic axis correction.')
    if width < 1e-8 or left[0] <= 1e-8:
        raise ValueError(f'GLB rest must face +Z (left hip on +X): measured pelvis-to-left-hip {left.tolist()}; no automatic turn.')
    return {'up': '+Y', 'forward': '+Z', 'up_joint': up_joint, 'pelvis_to_head' if up_joint == 'head' else 'pelvis_to_neck': up.tolist(), 'pelvis_to_left_hip': left.tolist()}


def append_glb_animation(target, solved, fps, pelvis_name, report=None):
    """Append one LINEAR clip; joints rotate, and only the pelvis and any followers translate.

    ``solved['follower_positions']`` (optional, {joint name: [frames, 3]} WORLD
    positions) becomes a translation channel per follower, after the pelvis's.
    """
    fps = float(fps)
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError('Animation fps must be positive and finite.')
    rotations = np.asarray(solved['local_rotations'], dtype=np.float64)
    positions = np.asarray(solved['root_positions'], dtype=np.float64)
    count = len(rotations)
    if (rotations.shape != (count, len(target['node_indices']), 4) or not count
            or positions.shape != (count, 3) or not np.isfinite(rotations).all()
            or not np.isfinite(positions).all() or not np.allclose(np.linalg.norm(rotations, axis=-1), 1, atol=1e-5)):
        raise ValueError('Retarget result must contain finite unit local rotations and world pelvis positions for every frame.')
    skeleton = target['skeleton']
    try:
        root_index = skeleton['names'].index(pelvis_name)
        root_node = target['node_indices'][root_index]
    except ValueError as error:
        raise ValueError('Pelvis must identify a named GLB skin joint.') from error
    if root_node not in target['joint_nodes']:
        raise ValueError('Pelvis must identify a named GLB skin joint.')
    placed = {root_node: positions}
    for name, values in (solved.get('follower_positions') or {}).items():
        values = np.asarray(values, dtype=np.float64)
        index = skeleton['names'].index(name) if name in skeleton['names'] else None
        if (index is None or target['node_indices'][index] not in target['joint_nodes'] or values.shape != (count, 3)
                or not np.isfinite(values).all() or target['node_indices'][index] in placed):
            raise ValueError(f'Follower {name!r} must be a named GLB skin joint with finite world positions per frame.')
        placed[target['node_indices'][index]] = values
    def depth(node):
        return 0 if node not in target['parents'] else 1 + depth(target['parents'][node])
    # Ancestors first: a translated joint's parent matrix includes any translated ancestor.
    order = sorted(placed, key=lambda node: (depth(node), node != root_node, node))
    translations = {node: [] for node in order}
    for frame in range(count):
        local = target['local_matrices'].copy()
        for index, node in enumerate(target['node_indices']):
            if node in target['joint_nodes']:
                scale = np.asarray(target['document']['nodes'][node].get('scale', [1, 1, 1]), dtype=np.float64)
                local[node, :3, :3] = _rotations()[1](rotations[frame, index]) * scale[None, :]
        for position, node in enumerate(order):
            if position == 0 or depth(node) > depth(order[position - 1]):
                world = _world_matrices(local, target['parents'])
            node_parent = target['parents'].get(node)
            parent = np.eye(4) if node_parent is None else world[node_parent]
            translation = (np.linalg.inv(parent) @ np.append(placed[node][frame], 1))[:3]
            translations[node].append(translation)
            local[node, :3, 3] = translation
    document = copy.deepcopy(target['document'])
    binary = bytearray(target['binary'])
    accessors, views = document.setdefault('accessors', []), document.setdefault('bufferViews', [])
    def add(values, kind, bounds=False):
        values = np.asarray(values, dtype='<f4')
        binary.extend(b'\0' * (-len(binary) % 4))
        view = len(views)
        views.append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': values.nbytes})
        binary.extend(values.tobytes())
        accessor = {'bufferView': view, 'componentType': 5126, 'count': count, 'type': kind}
        if bounds:
            accessor.update(min=[float(values.min())], max=[float(values.max())])
        accessors.append(accessor)
        return len(accessors) - 1
    times = add(np.arange(count) / fps, 'SCALAR', True)
    animation = {'name': 'LF Motion Retarget', 'samplers': [], 'channels': [], 'extras': {
        'lf_motion_retarget': {'fps': fps, 'frame_count': count, 'scale': float(solved['scale']),
                              'rest_pelvis': skeleton['rest_positions'][root_index].tolist(),
                              'root_joint': pelvis_name, 'root_node': root_node, 'report': report or {}}}}
    def channel(node, path, values, kind):
        animation['samplers'].append({'input': times, 'output': add(values, kind), 'interpolation': 'LINEAR'})
        animation['channels'].append({'sampler': len(animation['samplers']) - 1, 'target': {'node': node, 'path': path}})
    for index, node in enumerate(target['node_indices']):
        if node in target['joint_nodes']:
            # Quaternion signs must agree for glTF's shortest-path interpolation.
            values = rotations[:, index].copy()
            for frame in range(1, count):
                if values[frame - 1] @ values[frame] < 0:
                    values[frame] *= -1
            channel(node, 'rotation', values, 'VEC4')
    channel(root_node, 'translation', translations[root_node], 'VEC3')
    for node in order:
        if node != root_node:
            channel(node, 'translation', translations[node], 'VEC3')
    document.setdefault('animations', []).append(animation)
    document['buffers'][0]['byteLength'] = len(binary)
    return pack_glb(document, binary)


def _cofactors(matrices):
    """Cofactor matrices of 3x3 ``matrices``: what carries a normal through each (the inverse transpose scaled by
    the determinant, defined for a singular matrix too); a rotation's is itself."""
    c0, c1, c2 = matrices[..., :, 0], matrices[..., :, 1], matrices[..., :, 2]
    return np.stack([np.cross(c1, c2), np.cross(c2, c0), np.cross(c0, c1)], axis=-1)


def glb_meshes(source, batch_size=16):
    """Return repeatable world-space mesh batches, combined faces, clip metadata.

    Only the latest appended LF animation is evaluated. Original clips remain
    intact and inactive. All JOINTS_n/WEIGHTS_n sets contribute, normalized once
    per vertex across sets. Mesh nodes follow the selected glTF scene.
    Primitives of one node drawing the same vertex accessors (one buffer split
    by material) share their vertices once.

    ``mesh_batches.normals`` is ``'stored'`` when every primitive carries
    NORMAL, else ``'faces'``. ``mesh_batches(normals=True)`` (stored only)
    yields ``(positions, unit normals)``: each vertex's NORMAL skinned as its
    position is, so a mesh split at UV seams or between parts shades as its
    author smoothed it, creases and back-to-back cards kept.
    """
    target = load_glb_target(source)
    document, binary = target['document'], target['binary']
    try:
        animation = document['animations'][-1]
        metadata = copy.deepcopy(animation['extras']['lf_motion_retarget'])
        count, fps = metadata['frame_count'], metadata['fps']
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError('GLB preview requires a latest LF motion retarget animation.') from error
    if type(batch_size) is not int or batch_size < 1 or type(count) is not int or count < 1 or not np.isfinite(fps) or fps <= 0:
        raise ValueError('GLB animation count, fps, and batch size must be positive.')
    channels = []
    expected_times = np.arange(count) / fps
    for channel in animation['channels']:
        sampler = animation['samplers'][channel['sampler']]
        times = _accessor(document, binary, sampler['input'])
        values = _accessor(document, binary, sampler['output'])
        path = channel['target']['path']
        if sampler.get('interpolation', 'LINEAR') != 'LINEAR' or times.shape != (count,) or not np.allclose(times, expected_times, rtol=1e-6, atol=1e-7):
            raise ValueError('LF GLB animation must use LINEAR samples at its declared fps.')
        if path not in ('rotation', 'translation') or values.shape != (count, 4 if path == 'rotation' else 3):
            raise ValueError('Unsupported LF GLB animation channel.')
        channels.append((channel['target']['node'], path, values))
    nodes = document['nodes']
    if document.get('scenes'):
        try:
            roots = document['scenes'][document.get('scene', 0)]['nodes']
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError('GLB selected scene is invalid.') from error
    else:
        roots = [index for index in range(len(nodes)) if index not in target['parents']]
    active = set()
    def descend(index):
        if index not in active:
            active.add(index)
            for child in nodes[index].get('children', []):
                descend(child)
    for index in roots:
        descend(index)
    skin = document['skins'][0]
    inverse = (_accessor(document, binary, skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
               if 'inverseBindMatrices' in skin else np.repeat(np.eye(4)[None], len(target['joint_nodes']), axis=0))
    if inverse.shape != (len(target['joint_nodes']), 4, 4):
        raise ValueError('GLB inverse bind matrix count must match skin joints.')
    primitives, all_faces, vertex_offset, shared = [], [], 0, {}
    for node_index in sorted(active):
        node = nodes[node_index]
        if 'mesh' not in node:
            continue
        for primitive in document['meshes'][node['mesh']]['primitives']:
            if primitive.get('mode', 4) != 4:
                raise ValueError('GLB preview supports triangle primitives.')
            if 'KHR_draco_mesh_compression' in primitive.get('extensions', {}):
                raise ValueError('GLB KHR_draco_mesh_compression geometry requires a separate decoder.')
            attributes = primitive['attributes']
            key = (node_index, tuple(sorted(attributes.items())), repr(primitive.get('targets', [])))
            if key in shared:
                offset, size = shared[key]
                faces = (_accessor(document, binary, primitive['indices']) if 'indices' in primitive else np.arange(size))
                if faces.dtype.kind not in 'iu' or faces.size % 3 or np.any(faces < 0) or np.any(faces >= size):
                    raise ValueError('GLB triangle indices are invalid.')
                all_faces.append(faces.reshape(-1, 3).astype(np.int32) + offset)
                continue
            positions = _accessor(document, binary, attributes['POSITION'])
            if positions.ndim != 2 or positions.shape[1] != 3:
                raise ValueError('GLB POSITION must be VEC3.')
            morphs = primitive.get('targets', [])
            rest_weights = np.asarray(node.get('weights', document['meshes'][node['mesh']].get('weights', [0] * len(morphs))), dtype=np.float64)
            if rest_weights.shape != (len(morphs),) or not np.isfinite(rest_weights).all():
                raise ValueError('GLB rest morph weights must match its morph target count.')
            positions = positions.astype(np.float64)
            for weight, morph in zip(rest_weights, morphs):
                if weight and 'POSITION' in morph:
                    delta = _accessor(document, binary, morph['POSITION'])
                    if delta.shape != positions.shape:
                        raise ValueError('GLB morph POSITION must match its base POSITION shape.')
                    positions += weight * delta
            normals = None
            if 'NORMAL' in attributes:
                normals = _accessor(document, binary, attributes['NORMAL']).astype(np.float64)
                if normals.shape != positions.shape or not np.isfinite(normals).all():
                    raise ValueError('GLB NORMAL must be one finite VEC3 per vertex.')
                for weight, morph in zip(rest_weights, morphs):
                    if weight and 'NORMAL' in morph:
                        delta = _accessor(document, binary, morph['NORMAL'])
                        if delta.shape != normals.shape:
                            raise ValueError('GLB morph NORMAL must match its base NORMAL shape.')
                        normals += weight * delta
            faces = (_accessor(document, binary, primitive['indices']) if 'indices' in primitive else np.arange(len(positions)))
            if faces.dtype.kind not in 'iu' or faces.size % 3 or np.any(faces < 0) or np.any(faces >= len(positions)):
                raise ValueError('GLB triangle indices are invalid.')
            all_faces.append(faces.reshape(-1, 3).astype(np.int32) + vertex_offset)
            shared[key] = (vertex_offset, len(positions))
            vertex_offset += len(positions)
            joints, weights = None, None
            if 'skin' in node:
                if node['skin'] != 0:
                    raise ValueError('GLB mesh must use the sole supported skin.')
                sets = sorted(key[7:] for key in attributes if key.startswith('JOINTS_'))
                if not sets or {key[8:] for key in attributes if key.startswith('WEIGHTS_')} != set(sets):
                    raise ValueError('Every GLB JOINTS_n set needs its matching WEIGHTS_n set.')
                joints = np.concatenate([_accessor(document, binary, attributes[f'JOINTS_{key}']) for key in sets], axis=1)
                weights = np.concatenate([_accessor(document, binary, attributes[f'WEIGHTS_{key}']) for key in sets], axis=1)
                if (joints.shape != weights.shape or len(joints) != len(positions) or joints.dtype.kind not in 'iu'
                        or np.any(joints >= len(inverse)) or np.any(joints < 0) or np.any(weights < 0)):
                    raise ValueError('GLB skin joint indices or weights are invalid.')
                total = weights.sum(axis=1, keepdims=True)
                if np.any(total <= 1e-12):
                    raise ValueError('Every skinned GLB vertex needs a positive total weight.')
                weights = weights / total
            primitives.append((node_index, np.column_stack([positions, np.ones(len(positions))]), joints, weights,
                               normals))
    if not primitives or not any(len(face) for face in all_faces):
        raise ValueError('GLB selected scene has no renderable triangles.')
    faces = np.concatenate(all_faces)
    def frame_world(frame):
        local = target['local_matrices'].copy()
        for node, path, values in channels:
            if path == 'rotation':
                scale = np.asarray(nodes[node].get('scale', [1, 1, 1]), dtype=np.float64)
                local[node, :3, :3] = _rotations()[1](values[frame]) * scale[None, :]
            else:
                local[node, :3, 3] = values[frame]
        return _world_matrices(local, target['parents'])
    stored = all(row[4] is not None for row in primitives)
    def mesh_batches(normals=False):
        if normals and not stored:
            raise ValueError('GLB primitives without NORMAL have no stored normals to skin.')
        for start in range(0, count, batch_size):
            batch, turned = [], []
            for frame in range(start, min(start + batch_size, count)):
                world = frame_world(frame)
                skin_matrices = world[target['joint_nodes']] @ inverse
                cofactors = _cofactors(skin_matrices[:, :3, :3]) if normals else None
                meshes, rows = [], []
                for node, positions, joints, weights, vertex_normals in primitives:
                    if joints is None:
                        vertices = positions @ world[node].T
                        if normals:
                            rows.append(vertex_normals @ _cofactors(world[node, :3, :3]).T)
                    else:
                        # glTF local palette inv(meshWorld)*jointWorld*IBM,
                        # followed by meshWorld, cancels to jointWorld*IBM.
                        vertices = np.einsum('vwij,vj,vw->vi', skin_matrices[joints], positions, weights)
                        if normals:
                            rows.append(np.einsum('vwij,vj,vw->vi', cofactors[joints], vertex_normals, weights))
                    meshes.append(vertices[:, :3])
                batch.append(np.concatenate(meshes).astype(np.float32))
                if normals:
                    rows = np.concatenate(rows)
                    turned.append((rows / np.maximum(np.linalg.norm(rows, axis=1, keepdims=True), 1e-12))
                                  .astype(np.float32))
            yield (np.stack(batch), np.stack(turned)) if normals else np.stack(batch)
    mesh_batches.normals = 'stored' if stored else 'faces'
    root_node = metadata.get('root_node')
    if type(root_node) is not int or root_node not in target['joint_nodes']:
        raise ValueError('LF GLB animation must identify its pelvis skin joint.')
    mesh_batches.root_positions = np.stack([frame_world(frame)[root_node, :3, 3] for frame in range(count)])
    return mesh_batches, faces, metadata
