from itertools import product
from typing import Any, Dict, List, Tuple
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value

# region LF_JSONPromptCombinator
class LF_JSONPromptCombinator:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, { 
                    "tooltip": "Hierarchical JSON of prompt parts."
                }),
            },
            "optional": {
                "separator": (Input.STRING, {
                    "default": ", ", 
                    "tooltip": "Separator between merged parts."
                }),
                "include_keys": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Include path keys before each leaf."
                }),
                "full_path_keys": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "If true and include_keys, use full path; else only last key."
                }),
                "generate_root_prompts": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Include standalone root-level direct string leaves."
                }),
                "dedupe": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Remove duplicate final prompts."
                }),
                "max_combinations": (Input.INTEGER, {
                    "default": 5000,
                    "min": 1,
                    "max": 200000,
                    "tooltip": "Safety cap."
                }),
                "shuffle": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Randomize order (after generation, before limiting)."
                }),
                "limit": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "tooltip": "If > 0, limit number of prompts after processing."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, False)
    RETURN_NAMES = ("string", "string_list", "count", "json")
    RETURN_TYPES = (Input.STRING, Input.STRING, Input.INTEGER, Input.JSON)

    def on_exec(self, **kwargs: Any) -> Tuple[str, List[str], int, Dict[str, str]]:
        json_input: Dict[str, Any] = normalize_json_input(kwargs.get("json_input", {}))
        separator: str = normalize_list_to_value(kwargs.get("separator", ", "))
        include_keys: bool = bool(normalize_list_to_value(kwargs.get("include_keys", False)))
        full_path_keys: bool = bool(normalize_list_to_value(kwargs.get("full_path_keys", False)))
        generate_root_prompts: bool = bool(normalize_list_to_value(kwargs.get("generate_root_prompts", True)))
        dedupe: bool = bool(normalize_list_to_value(kwargs.get("dedupe", True)))
        max_combinations: int = int(normalize_list_to_value(kwargs.get("max_combinations", 5000)))
        shuffle_flag: bool = bool(normalize_list_to_value(kwargs.get("shuffle", False)))
        limit: int = int(normalize_list_to_value(kwargs.get("limit", 0)))

        def collect_leaves(node: Any, path: List[str]) -> List[Tuple[str, List[str]]]:
            leaves: List[Tuple[str, List[str]]] = []
            if isinstance(node, dict):
                for k, v in node.items():
                    leaves.extend(collect_leaves(v, path + [str(k)]))
            elif isinstance(node, list):
                for idx, v in enumerate(node):
                    leaves.extend(collect_leaves(v, path + [str(idx)]))
            else:
                if node is not None and str(node).strip() != "":
                    leaves.append((str(node), path))
            return leaves

        if not isinstance(json_input, dict):
            prompts: List[str] = [str(json_input)]
            flat_json: Dict[str, str] = {str(i): p for i, p in enumerate(prompts)}
            return ("\n".join(prompts), prompts, len(prompts), flat_json)

        top_level_keys = list(json_input.keys())

        variant_sets: List[List[Tuple[str, List[str]]]] = []
        root_direct_strings: List[Tuple[str, List[str]]] = []
        variant_metadata: List[Dict[str, Any]] = []

        for k in top_level_keys:
            val = json_input[k]
            if isinstance(val, (dict, list)):
                leaves = collect_leaves(val, [k])
                if not leaves:
                    continue
                variant_sets.append(leaves)
                sample_values = [lv for lv, _ in leaves[:5]]
                variant_metadata.append({
                    "key": k,
                    "type": type(val).__name__,
                    "variants": len(leaves),
                    "sample": sample_values,
                })
            else:
                s = str(val)
                if s.strip():
                    root_direct_strings.append((s, [k]))
                    variant_sets.append([(s, [k])])
                    variant_metadata.append({
                        "key": k,
                        "type": "str",
                        "variants": 1,
                        "sample": [s],
                    })

        total_dim = 1
        for vs in variant_sets:
            total_dim *= max(1, len(vs))
            if total_dim > max_combinations:
                break

        combinations: List[str] = []
        truncated: bool = False
        for combo in product(*variant_sets):
            if len(combinations) >= max_combinations:
                truncated = True
                break
            parts = []
            for text, path_keys in combo:
                if include_keys:
                    if full_path_keys:
                        key_prefix = "/".join(path_keys)
                    else:
                        key_prefix = path_keys[-1]
                    parts.append(f"{key_prefix}: {text}")
                else:
                    parts.append(text)
            final_prompt = separator.join(parts)
            combinations.append(final_prompt)

        if generate_root_prompts:
            for text, path_keys in root_direct_strings:
                if include_keys:
                    key_prefix = "/".join(path_keys) if full_path_keys else path_keys[-1]
                    candidate = f"{key_prefix}: {text}"
                else:
                    candidate = text
                combinations.append(candidate)

        if dedupe:
            seen = set()
            deduped = []
            for p in combinations:
                if p not in seen:
                    seen.add(p)
                    deduped.append(p)
            combinations = deduped

        if shuffle_flag:
            from random import shuffle
            shuffle(combinations)

        if limit > 0:
            combinations = combinations[:limit]

        flat_json: Dict[str, str] = {str(i): p for i, p in enumerate(combinations)}
        count: int = len(combinations)
        theoretical_total: int = 1
        for meta in variant_metadata:
            theoretical_total *= max(1, meta.get("variants", 1))
        if generate_root_prompts:
            root_added = len([m for m in variant_metadata if m.get("variants") == 1])
        else:
            root_added = 0

        meta_lines = []
        for meta in variant_metadata:
            sample_preview = ", ".join(meta['sample']) if meta['sample'] else "-"
            if len(sample_preview) > 120:
                sample_preview = sample_preview[:117] + "..."
            meta_lines.append(f"- **{meta['key']}** ({meta['type']}): {meta['variants']} variant(s) | sample: {sample_preview}")
        meta_block = "\n".join(meta_lines) if meta_lines else "_No variant dimensions detected_"

        sample_prompts_preview = combinations[:10]
        sample_block = "\n".join([f"{i+1}. {p}" for i, p in enumerate(sample_prompts_preview)]) if sample_prompts_preview else "_No prompts generated_"

        options_block = f"Separator: `{separator}` | Include Keys: {include_keys} ({'full path' if full_path_keys else 'last key'}) | Root Prompts: {generate_root_prompts} | Dedupe: {dedupe} | Shuffle: {shuffle_flag} | Limit: {limit if limit>0 else 'none'} | Max Comb.: {max_combinations}"

        trunc_note = "Yes" if truncated or theoretical_total > max_combinations else "No"
        dedupe_note = "Yes" if dedupe else "No"

        if count > 3:
            tail_block = "\n" + "\n".join(f"- {p}" for p in combinations[-3:])
        else:
            tail_block = "_Not enough prompts for tail preview_"

        log_markdown = f"""## JSON Prompt Combinator

**Generated:** {count} prompt(s)  
**Theoretical (pre-cap):** {theoretical_total}  
**Truncated:** {trunc_note}  
**Root extras added:** {root_added if generate_root_prompts else 0}  
**Duplicates removed:** {dedupe_note}

### Options
{options_block}

### Dimensions
{meta_block}

### Sample Prompts (first {len(sample_prompts_preview)})
{sample_block}

### Tail (last 3)
{tail_block}

"""

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}jsonpromptcombinator", {
            "node": kwargs.get("node_id"),
            "value": log_markdown,
        })

        return ("\n".join(combinations), combinations, count, flat_json)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_JSONPromptCombinator": LF_JSONPromptCombinator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_JSONPromptCombinator": "JSON Prompt Combinator",
}
# endregion