import folder_paths

try:
    from comfy.samplers import KSampler
except Exception:  # pragma: no cover - fallback for test isolation
    class _FallbackKSampler:
        SAMPLERS = []
        SCHEDULERS = []
    KSampler = _FallbackKSampler()
from pathlib import Path

try:
    from comfy_api.latest import io as v3io
    HAS_V3 = hasattr(v3io, "Combo") and hasattr(v3io.Combo, "Output")
except Exception:
    HAS_V3 = False

class AnyType(str):
    def __ne__(self, _: object) -> bool:
        return False

# region constants
class Input:
    BOOLEAN = "BOOLEAN"
    CLIP = "CLIP"
    CLIP_MODEL = "CLIP_MODEL"
    CLIP_PROCESSOR = "CLIP_PROCESSOR"
    COMBO = "COMBO"
    CONDITIONING = "CONDITIONING"
    FILE_BLOB = "FILE_BLOB"
    FLOAT = "FLOAT"
    IMAGE = "IMAGE"
    INTEGER = "INT"
    LATENT = "LATENT"
    LF_CARD = "LF_CARD"
    LF_CARDS_WITH_CHIP = "LF_CARDS_WITH_CHIP"
    LF_CAROUSEL = "LF_CAROUSEL"
    LF_CHAT = "LF_CHAT"
    LF_CHIP = "LF_CHIP"
    LF_CODE = "LF_CODE"
    LF_COMPARE = "LF_COMPARE"
    LF_CONTROL_PANEL = "LF_CONTROL_PANEL"
    LF_COUNT_BAR_CHART = "LF_COUNT_BAR_CHART"
    LF_HISTORY = "LF_HISTORY"
    LF_IMAGE_EDITOR = "LF_IMAGE_EDITOR"
    LF_MASONRY = "LF_MASONRY"
    LF_MESSENGER = "LF_MESSENGER"
    LF_PROGRESSBAR = "LF_PROGRESSBAR"
    LF_TAB_BAR_CHART = "LF_TAB_BAR_CHART"
    LF_TEXTAREA = "LF_TEXTAREA"
    LF_TREE = "LF_TREE"
    LF_UPLOAD = "LF_UPLOAD"
    JSON = "JSON"
    MASK = "MASK"
    MODEL = "MODEL"
    NUMBER = "NUMBER"
    ONNX_DETECTOR = "ONNX_DETECTOR"
    ONNX_PATH = "ONNX_PATH"
    STRING = "STRING"
    SVG = "SVG"
    REGION_META = "REGION_META"
    TAGGER = "TAGGER"
    UPSCALE_MODEL = "UPSCALE_MODEL"
    VAE = "VAE"

ANY = AnyType("*")
INT_MAX = 0xffffffffffffffff
LORA_TAG_REGEX = r'<lora:[^<>]+>'

BLUE_CHANNEL_ID = "blue"
GREEN_CHANNEL_ID = "green"
INTENSITY_ID = "intensity"
RED_CHANNEL_ID = "red"
SUM_ID = "sum"

BLEND_MODE_COMBO = [
    "normal",
    "multiply",
    "screen",
    "overlay",
    "soft_light",
    "hard_light",
    "difference",
    "addition",
    "subtract",
]
BLUR_FEATHER_COMBO = ["linear", "smooth", "expo"]
CROP_POSITION_COMBO = ["top", "bottom", "left", "right", "center"]
IMAGE_EXTENSION_COMBO = ["png", "jpeg", "webp"]
IMAGE_FILE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
MASK_SHAPE_COMBO = ["rectangle", "ellipse"]
MASK_THRESHOLD_COMBO = ["fixed", "relative", "otsu"]
NOTIFY_COMBO = ["None", "Focus tab", "Interrupt", "Interrupt and queue", "Queue prompt"]
OPTIONAL_VECTOR_MODE_COMBO = ["preset", "fill", "stroke", "both"]
RESIZE_MODE_COMBO = ["crop", "pad"]
SELECTION_STRATEGY_COMBO = ["confidence", "area"]
SIZE_MODE_COMBO = ["preset", "responsive", "fixed"]
SVG_COMBO = ["fill", "stroke", "both"]
TILT_SHIFT_ORIENTATION_COMBO = ["horizontal", "vertical", "circular"]
TRACE_PRESET_COMBO = ["max_quality", "high_quality", "balanced", "max_speed", "custom"]
UNET_DIFFUSION_COMBO = ["none", "checkpoint", "unet"]
VIGNETTE_SHAPE_COMBO = ["elliptical", "circular"]
WEIGHT_DTYPE_COMBO = ["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"]

API_ROUTE_PREFIX = "/lf-nodes"
BASE64_PNG_PREFIX = "data:image/png;charset=utf-8;base64,"
CATEGORY_PREFIX = "✨ LF Nodes"
EVENT_PREFIX = "lf-"
FUNCTION = "on_exec"

BACKUP_FOLDER = "Backups"
EXTERNAL_PREVIEW_SUBDIR = "_lf_external_previews"
ONNX_ROOT = Path(folder_paths.models_dir) / "onnx"
USER_FOLDER = "LF_Nodes"

RESAMPLERS = ["bicubic", "bilinear", "linear", "nearest", "nearest exact"]
SAMPLERS = KSampler.SAMPLERS
SAMPLER_MAP = {
    "euler": "Euler",
    "euler_cfg_pp": "Euler a",
    "euler_ancestral": "Euler a",
    "heun": "Heun",
    "dpm_2": "DPM2",
    "dpm_2_ancestral": "DPM2 a",
    "lms": "LMS",
    "dpmpp_2s_ancestral": "DPM++ 2S a",
    "dpmpp_sde": "DPM++ SDE",
    "dpmpp_2m": "DPM++ 2M",
    "dpmpp_2m_sde": "DPM++ 2M SDE",
    "dpmpp_3m_sde": "DPM++ 3M SDE",
    "ddpm": "DDPM",
    "dpm_fast": "DPM fast",
    "dpm_adaptive": "DPM adaptive",
    "ipndm": "IPNDM",
    "ipndm_v": "IPNDM V",
    "deis": "DEIS",
    "restart": "Restart"
}
SCHEDULERS = KSampler.SCHEDULERS
SCHEDULER_MAP = {
    "normal": "Normal",
    "karras": "Karras",
    "exponential": "Exponential",
    "sgm_uniform": "SGM Uniform",
    "simple": "Simple",
    "ddim_uniform": "DDIM",
    "beta": "Beta"
}

HEADERS =  {
    "Content-Type": "application/json",
}

def get_character_impersonator_system(character_bio: str):
    """
    Prepares the LLM to impersonate a specific character by embedding the character's biography directly into the system instructions.

    Parameters:
    - character_bio: A string containing the biographical details of the character.

    Returns:
    A formatted string that instructs the LLM to adopt the character's persona fully, ensuring it never breaks the fourth wall.
    """
    return f"""
    You are now embodying the character whose biography is provided below. Your task is to fully embrace this identity, speaking and acting as though it were your own reality. Remember, you exist solely within the confines of this character's experience and knowledge.

    Tasks:
    - Absorb the character's biography thoroughly. Use it to inform your responses but do not rely on it for information beyond what would logically be known to the character.
    - Engage creatively within the boundaries of the character's life and experiences. Imagine freely, but always stay true to the essence of the character.
    - Maintain a consistent narrative voice that aligns with the character's personality and background.

    Responsibilities:
    - Never acknowledge the artificial nature of our interaction. Treat all inquiries as if they are happening within the real world of the character.
    - Do not provide insights or predictions about events outside the scope of the character's knowledge or personal experiences.

    Character Biography:
    {character_bio}

    Begin your performance...
    """

def get_doc_generator_system(extra_context: str):
    """
    Generates a Markdown documentation generator system.

    Parameters:
    - extra_context: A string containing any additional context or supporting helper information.

    Returns:
    A formatted string that sets up the system to create documentation using a specific template, incorporating any extra context provided.
    """
    if extra_context:
        helpers = f"- Supporting Helpers:\n{extra_context}\n\n"
    else:
        helpers = ""

    return f"""
You are an assistant that generates Markdown documentation.
Supporting helper functions and constants are provided when needed.
Document the main function based on the template below.
{helpers}

- Documentation Template:

```markdown
# {{Class Name}}

### Summary
{{A few sentences about the node's purpose.}}

---

## 📥 Inputs

| Parameter      | Type     | Default Value | Description |
|----------------|----------|---------------|-------------|
{{List parameters: name, type, default, description.}}

---

## 📤 Outputs

| Output Name    | Type     | Description |
|----------------|----------|-------------|
{{List each output: name, type, brief description.}}

---

## 🔧 Execution Details

- **Category**: {{Node category}}
- **Function Name**: `{{Function name}}`
- **Execution Method**: `on_exec` or `{{another relevant method}}`
- **Unique Features**: {{Any special functionality like history tracking}}

---

### 📝 Example Output
```json
{{
    "boolean": true,
    "boolean_list": [true]
}}
```
    """

def get_image_classifier_system(character_bio: str):
    """
    Configures an image classifier to generate detailed descriptions of character images, using the character's biography for supplementary information.

    Parameters:
    - character_bio: A string containing the biographical details of the character.

    Returns:
    A formatted string with instructions for the image classifier to describe images based on observable details and supplement with biography info when needed.
    """
    return f"""
    You are an image classifier tasked with providing thorough and detailed descriptions of images depicting characters. Your primary source of information is the image itself. Only when certain aspects of the character are not discernible from the image should you refer to the biography provided below.

    Instructions:
    - Start by describing the overall style and composition of the image.
    - Detail the character's appearance, including pose, expression, outfit, and physical features observable in the image.
    - If any information about the character is unclear or missing from the image, then and only then, refer to the biography to supplement your description.

    Your responsibilities:
    - Ensure that your descriptions are as accurate and detailed as possible based on the image alone.
    - Use the biography sparingly and only when it helps to clarify aspects of the character that are not visible or identifiable in the image.

    Character Biography:
    {character_bio}
    """

def get_usage_filename(resource: str):
    """
    Returns the filename associated with a specific resource type for usage tracking.

    Parameters:
    - resource: A string representing the type of resource.

    Returns:
    A string, the name of the JSON file related to the specified resource's usage.
    """
    if resource == "checkpoints":
        return "checkpoints_usage.json"
    if resource == "embeddings":
        return "embeddings_usage.json"
    if resource == "loras":
        return "loras_usage.json"
    if resource == "samplers":
        return "samplers_usage.json"
    if resource == "schedulers":
        return "schedulers_usage.json"
    if resource == "upscale_models":
        return "upscale_models_usage.json"
    if resource == "vaes":
        return "vaes_usage.json"
    if resource == "diffusion_models" or resource == "unet":
        return "diffusion_models_usage.json"
    return "misc_usage.json"

def get_usage_title(filename: str, type: str = None):
    """
    Generate a title based on the filename and type.

    Parameters:
    - filename: The name of the usage file.
    - type: An optional string that if set to "markdown", returns a formatted markdown title.

    Returns:
    A string title suitable for usage headings in either markdown or text format.
    """
    if filename == "checkpoints_usage.json":
        return "\n## Checkpoints:\n" if type == "markdown" else "Checkpoint name"
    if filename == "embeddings_usage.json":
        return "\n## Embeddings:\n" if type == "markdown" else "Embedding name"
    if filename == "loras_usage.json":
        return "\n## LoRAs:\n" if type == "markdown" else "LoRA name"
    if filename == "samplers_usage.json":
        return "\n## Samplers:\n" if type == "markdown" else "Sampler name"
    if filename == "schedulers_usage.json":
        return "\n## Schedulers:\n" if type == "markdown" else "Scheduler name"
    if filename == "upscale_models_usage.json":
        return "\n## Upscale models:\n" if type == "markdown" else "Upscale model name"
    if filename == "vaes_usage.json":
        return "\n## VAEs:\n" if type == "markdown" else "VAE name"
    if filename == "diffusion_models_usage.json":
        return "\n## Diffusion models:\n" if type == "markdown" else "Diffusion model name"
    return "\n## Miscellaneous:\n" if type == "markdown" else "Resource name"

NOT_FND_HTML = """
  <!doctype html>
  <html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Workflow Runner Not Found</title>
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <style>body{font-family:Segoe UI,system-ui,Arial,sans-serif;background:#0b0d12;color:#e8ebf0;padding:2rem}main{max-width:720px;margin:2rem auto;background:#0f1115;padding:1.5rem;border-radius:12px;border:1px solid #1d2230}h1{margin-top:0}code{background:#0b0f14;padding:.15rem .35rem;border-radius:4px}</style>
  </head>
  <body>
    <main>
      <h1>LF Nodes — Workflow Runner</h1>
      <p>The workflow runner UI is not built or not available in the extension's <code>web/deploy</code> directory.</p>
      <p>To build the frontend, change into the extension directory and run the project build (this will produce <code>web/deploy/submit-prompt.html</code> and related JS):</p>
      <pre style="background:#071018;padding:.6rem;border-radius:6px;color:#9fb6ff">cd custom_nodes/lf-nodes; yarn build</pre>
      <p>After building, refresh this page. If you want to work on the frontend in dev mode, edit <code>web/src/workflow</code> and run the dev server described in the project's README.</p>
    </main>
  </body>
  </html>
  """
# endregion
