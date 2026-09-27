"""Scale a selected group of GLB skin joints, preserving animation tracks."""
from io import BytesIO

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.glb_transform import scale_glb_nodes


def _single(value, name):
    if isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError(f'{name} requires exactly one value; batches/lists are not supported.')
        value = value[0]
    return value


class LF_ScaleGLBNodes:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'glb': (Input.FILE_3D_GLB, {'tooltip': 'Exactly one self-contained GLB. Source files are read only.'}),
            'targets': (Input.JSON, {'tooltip': 'Object with nodes selectors (nodeIndex, optional nodeName/anchorLocal) and optional minPercent/maxPercent.'}),
            'percent': (Input.FLOAT, {'default': 100.0, 'min': 1.0, 'max': 200.0, 'step': 1.0,
                                    'tooltip': 'Uniform scale for this group. 100 preserves the original GLB bytes.'}),
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.FILE_3D_GLB,)
    RETURN_NAMES = ('glb',)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ('In-memory GLB with scaled joint subtrees; original animation tracks and embedded resources preserved.',)

    def on_exec(self, glb, targets, percent=100.0):
        glb, targets, percent = (_single(glb, 'glb'), _single(targets, 'targets'), _single(percent, 'percent'))
        from comfy_api.latest import Types
        if not isinstance(glb, Types.File3D) or glb.format != 'glb':
            raise ValueError('glb requires a FILE_3D_GLB File3D input.')
        result = scale_glb_nodes(glb.get_bytes(), targets, percent)
        return (Types.File3D(BytesIO(result), file_format='glb'),)


NODE_CLASS_MAPPINGS = {'LF_ScaleGLBNodes': LF_ScaleGLBNodes}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_ScaleGLBNodes': 'Scale GLB Nodes'}
