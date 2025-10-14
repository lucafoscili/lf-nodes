import re

# region SplitSVGs
def split_svgs(svg_string) -> list[str]:
    """
    Split and extract <svg>...</svg> fragments from a variety of input shapes.
    Parameters
    ----------
    svg_string : Any
        The input that may contain one or more SVG fragments. Supported input types:
        - None: treated as no content and results in an empty list.
        - bytes or bytearray: decoded as UTF-8; on decode error the decoder falls back
          to UTF-8 with errors='ignore'.
        - list or tuple: each element is converted to a string (bytes decoded where possible,
          dicts will try "value" or "lfValue" keys), and all parts are joined with newline
          before extraction.
        - dict: the function will attempt to use dict.get("value") or dict.get("lfValue"),
          otherwise str(dict) is used.
        - other types: converted to str(...) and processed.
    Returns
    -------
    list[str]
        A list of SVG fragment strings that match the pattern "<svg...></svg>".
        Matching is case-insensitive and uses a non-greedy regular expression to find
        each <svg>...</svg> block. If no SVG fragments are found or input is None,
        an empty list is returned.
    Behavior and notes
    ------------------
    - Extraction is performed with a simple regular expression (non-greedy, case-insensitive).
      This is sufficient for many common inputs but may not correctly handle malformed HTML/XML,
      commented-out SVGs, or certain nested/complex cases.
    - The function attempts best-effort conversions (decoding bytes, extracting common dict keys)
      rather than raising on unexpected input types. Unexpected errors (e.g., from extremely
      large inputs or unusual object __str__ implementations) may still propagate.
    - When provided a sequence, items that are dicts will preferentially use "value" or "lfValue".
      Other items are stringified; bytes within sequences are decoded similarly to top-level bytes.
    Examples
    --------
    >>> split_svgs(None)
    []
    >>> split_svgs(b'<svg></svg>')
    ['<svg></svg>']
    >>> split_svgs(['<svg>a</svg>', b'<svg>b</svg>'])
    ['<svg>a</svg>', '<svg>b</svg>']
    """
    if svg_string is None:
        return []

    # bytes -> decode
    if isinstance(svg_string, (bytes, bytearray)):
        try:
            svg_string = svg_string.decode("utf-8")
        except Exception:
            svg_string = svg_string.decode("utf-8", errors="ignore")

    elif isinstance(svg_string, (list, tuple)):
        parts: list[str] = []
        for item in svg_string:
            if isinstance(item, (bytes, bytearray)):
                try:
                    parts.append(item.decode("utf-8"))
                except Exception:
                    parts.append(str(item))
            elif isinstance(item, dict):
                parts.append(item.get("value") or item.get("lfValue") or str(item))
            else:
                parts.append(str(item))
        svg_string = "\n".join(parts)

    elif isinstance(svg_string, dict):
        svg_string = svg_string.get("value") or svg_string.get("lfValue") or str(svg_string)

    else:
        svg_string = str(svg_string)

    pattern = re.compile(r"<svg[\s\S]*?<\/svg>", re.IGNORECASE)
    
    return pattern.findall(svg_string or "")
# endregion