from . import CATEGORY
from ...utils.constants import FUNCTION, Input

# region LF_LoadAndEditImages
class LF_LoadAndEditImages:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "ui_widget": (Input.LF_IMAGE_EDITOR, {
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
    "LF_LoadAndEditImages": LF_LoadAndEditImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadAndEditImages": "Load and edit images",
}
# endregion