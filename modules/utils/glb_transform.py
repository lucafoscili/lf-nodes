"""Pure, pose-preserving uniform scale of selected skinned joint subtrees.

``transform_document`` has no Comfy or package imports and can be loaded by
file path by offline callers. The GLB facade shares the existing codec.
"""
import copy
import math


def _finite(value, label):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number.')
    return value


def _node_index(value, nodes, label):
    if type(value) is not int or not 0 <= value < len(nodes):
        raise ValueError(f'{label} must identify an existing GLB node.')
    return value


def _graph(document):
    """Validate the graph and joints touched by reparenting, without an asset audit."""
    if not isinstance(document, dict) or not isinstance(document.get('nodes'), list):
        raise ValueError('GLB must contain a nodes array.')
    nodes = document['nodes']
    parents = {}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict) or not isinstance(node.get('children', []), list):
            raise ValueError('GLB nodes and children must form a valid hierarchy.')
        for child in node.get('children', []):
            _node_index(child, nodes, 'GLB child')
            if child in parents:
                raise ValueError('GLB hierarchy must not repeat children or share parents.')
            parents[child] = index
    visited = set()
    for index in range(len(nodes)):
        chain = set()
        current = index
        while current not in visited:
            if current in chain:
                raise ValueError('GLB hierarchy contains a cycle.')
            chain.add(current)
            if current not in parents:
                break
            current = parents[current]
        visited.update(chain)
    skins = document.get('skins', [])
    if not isinstance(skins, list):
        raise ValueError('GLB skins must be an array.')
    joints = set()
    for skin in skins:
        if not isinstance(skin, dict) or not isinstance(skin.get('joints'), list):
            raise ValueError('Each GLB skin must contain a joints array.')
        seen = set()
        for joint in skin['joints']:
            _node_index(joint, nodes, 'GLB skin joint')
            if joint in seen:
                raise ValueError('GLB skin joints must be distinct.')
            seen.add(joint)
        if not seen:
            raise ValueError('GLB skin joints must not be empty.')
        if 'skeleton' in skin:
            _node_index(skin['skeleton'], nodes, 'GLB skin skeleton')
        joints.update(seen)
    return nodes, parents, joints


def transform_document(document, controls):
    """Return ``(independent_document, report)`` for factor-bearing selectors.

    Each control has nodeIndex, factor, optional expected nodeName, and optional
    anchorLocal (defaults to [0, 0, 0]). Roots must be distinct, nonoverlapping
    skin joints. The source joint retains its animated TRS; a new static child
    becomes its deform joint and parents its old children. No channel, sampler,
    accessor, inverse bind matrix, or binary payload is rewritten.
    """
    if not isinstance(controls, list):
        raise ValueError('Scale controls must be an array of node selectors.')
    nodes, parents, joints = _graph(document)
    selected, prepared = set(), []
    for control in controls:
        if not isinstance(control, dict):
            raise ValueError('Each scale control must be a node selector object.')
        index = _node_index(control.get('nodeIndex'), nodes, 'nodeIndex')
        if index in selected:
            raise ValueError('Scale target nodes must be distinct.')
        selected.add(index)
        if index not in joints:
            raise ValueError(f'Scale target node {index} must be a skin joint.')
        if 'nodeName' in control and (not isinstance(control['nodeName'], str)
                                     or nodes[index].get('name') != control['nodeName']):
            raise ValueError(f'Scale target nodeName does not match node {index}.')
        factor = _finite(control.get('factor'), 'factor')
        if not 0.01 <= factor <= 2:
            raise ValueError('factor must be between 0.01 and 2 (1 to 200 percent).')
        anchor = control.get('anchorLocal', [0, 0, 0])
        if not isinstance(anchor, (list, tuple)) or len(anchor) != 3:
            raise ValueError('anchorLocal must contain exactly three finite numbers.')
        anchor = [_finite(value, 'anchorLocal') for value in anchor]
        prepared.append(dict(control, anchorLocal=anchor, factor=factor))
    for index in selected:
        parent = parents.get(index)
        while parent is not None:
            if parent in selected:
                raise ValueError('Scale targets must have nonoverlapping joint subtrees.')
            parent = parents.get(parent)

    result = copy.deepcopy(document)
    anchored_roots = []
    # Extracted from the consumer's anchored-joint experiment; the same static
    # wrapper handles zero and nonzero anchors without touching animation data.
    for row in prepared:
        if row['factor'] == 1:
            continue
        node_index, factor = row['nodeIndex'], row['factor']
        node = result['nodes'][node_index]
        wrapper_index = len(result['nodes'])
        wrapper = dict(name=f"{node.get('name', node_index)} scale",
                       translation=[(1 - factor) * value for value in row['anchorLocal']],
                       scale=[factor] * 3)
        if node.get('children'):
            wrapper['children'] = node['children']
        node['children'] = [wrapper_index]
        result['nodes'].append(wrapper)
        for skin in result.get('skins', []):
            skin['joints'] = [wrapper_index if joint == node_index else joint for joint in skin['joints']]
        anchored_roots.append(dict(nodeIndex=node_index, deformNodeIndex=wrapper_index,
                                   anchorLocal=list(row['anchorLocal']), factor=factor))
    return result, dict(controls=copy.deepcopy(prepared), changedScaleChannels=0,
                        anchoredRoots=anchored_roots, clipCount=len(result.get('animations', [])))


def scale_glb_nodes(blob, targets, percent=100):
    """Scale one JSON recipe's joint group and return GLB bytes, with no writes.

    100 percent returns the exact original bytes after recipe/GLB validation.
    Empty or null recipes are allowed only for that identity operation.
    """
    percent = _finite(percent, 'percent')
    if not 1 <= percent <= 200:
        raise ValueError('percent must be between 1 and 200.')
    if targets is None:
        targets = {}
    if not isinstance(targets, dict):
        raise ValueError('targets must be a JSON object with a nodes array, or null.')
    minimum = _finite(targets.get('minPercent', 1), 'minPercent')
    maximum = _finite(targets.get('maxPercent', 200), 'maxPercent')
    if not 1 <= minimum <= maximum <= 200:
        raise ValueError('Recipe minPercent/maxPercent must form a range within 1 to 200.')
    if not minimum <= percent <= maximum:
        raise ValueError(f'percent must be within this recipe range ({minimum} to {maximum}).')
    selectors = targets.get('nodes', [])
    if not isinstance(selectors, list) or any(not isinstance(row, dict) for row in selectors):
        raise ValueError('targets.nodes must be an array of node selector objects.')
    if percent != 100 and not selectors:
        raise ValueError('No configured nodes: supply targets.nodes before changing percent from 100.')
    from .glb_texture import read_glb, pack_glb
    document, binary = read_glb(blob)
    if not selectors:
        return blob
    result, _ = transform_document(document, [dict(row, factor=percent / 100) for row in selectors])
    return blob if percent == 100 else pack_glb(result, binary)
