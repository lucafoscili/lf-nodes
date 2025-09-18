from typing import List, Dict, Any

STRATEGY_CHOICES: List[str] = ["auto", "concat_token", "add_kv", "kv_bias_residual"]
CURVE_CHOICES: List[str] = ["linear", "cosine", "ease_in_out"]

# Preset names offered in nodes to simplify controls.
PRESET_CHOICES: List[str] = [
	"balanced",
	"strong",
	"fine_details",
	"carbon_copy",
	"custom",  # does not override user-provided knobs
]

# Mapping of preset -> default parameters applied when preset != custom.
# These are sensible starting points aimed at identity-preserving IPAdapter.
IPADAPTER_PRESETS: Dict[str, Dict[str, Any]] = {
	"balanced": {
		"strength": 1.0,
		"start_percent": 0.15,
		"end_percent": 0.95,
		"schedule_curve": "cosine",
		"kv_norm_clip": 0.0,
		"strategy": "auto",
	},
	"strong": {
		"strength": 1.4,
		"start_percent": 0.10,
		"end_percent": 0.95,
		"schedule_curve": "cosine",
		"kv_norm_clip": 0.5,
		"strategy": "auto",
	},
	"fine_details": {
		"strength": 0.9,
		"start_percent": 0.60,
		"end_percent": 1.0,
		"schedule_curve": "ease_in_out",
		"kv_norm_clip": 0.0,
		"strategy": "auto",
	},
	"carbon_copy": {
		"strength": 1.8,
		"start_percent": 0.20,
		"end_percent": 0.98,
		"schedule_curve": "cosine",
		"kv_norm_clip": 1.0,
		"strategy": "kv_bias_residual",
	},
}