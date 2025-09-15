from . import CATEGORY
from ...utils.constants import FUNCTION, Input

# region LF_UsageStatistics
class LF_UsageStatistics:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "ui_widget": (Input.LF_TAB_BAR_CHART, {
                    "default": {}
                })
            },
        }
    
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ()

    def on_exec(self, **kwargs: dict):
        return ()
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_UsageStatistics": LF_UsageStatistics,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_UsageStatistics": "Usage statistics",
}
# endregion