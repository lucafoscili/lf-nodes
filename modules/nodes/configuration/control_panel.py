from . import CATEGORY
from ...utils.constants import FUNCTION, Input

# region LF_ControlPanel
class LF_ControlPanel:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "ui_widget": (Input.LF_CONTROL_PANEL, {
                    "default": {}
                })
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }
    
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ()

    def on_exec(self, **kwargs: dict):
        return ()
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ControlPanel": LF_ControlPanel,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ControlPanel": "Control panel",
}
# endregion