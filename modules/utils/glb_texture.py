"""Replace one GLB base-color binding without re-exporting its scene."""
import copy
import json
import struct
from io import BytesIO


def _index(value, entries, label):
    if type(value) is not int or not 0 <= value < len(entries):
        raise ValueError(f"Invalid GLB {label} index.")
    return entries[value]


def read_glb(blob):
    """Admit GLB 2 with one embedded buffer and no external image resources."""
    if len(blob) < 28 or struct.unpack_from('<4sII', blob) != (b'glTF', 2, len(blob)):
        raise ValueError('Expected a complete GLB 2 file.')
    offset, chunks = 12, []
    while offset < len(blob):
        if offset + 8 > len(blob):
            raise ValueError('Truncated GLB chunk header.')
        size, kind = struct.unpack_from('<II', blob, offset)
        offset += 8
        if size % 4 or offset + size > len(blob):
            raise ValueError('Invalid GLB chunk size.')
        chunks.append((kind, blob[offset:offset + size]))
        offset += size
    if [kind for kind, _ in chunks] != [0x4E4F534A, 0x004E4942]:
        raise ValueError('Expected exactly JSON and BIN GLB chunks.')
    try:
        document = json.loads(chunks[0][1])
        binary = chunks[1][1]
        if document['asset']['version'] != '2.0':
            raise ValueError('Expected glTF asset version 2.0.')
        buffers = document['buffers']
        if len(buffers) != 1 or 'uri' in buffers[0]:
            raise ValueError('Only self-contained GLB files with one embedded buffer are supported.')
        length = buffers[0]['byteLength']
        if type(length) is not int or length < 0 or not 0 <= len(binary) - length <= 3:
            raise ValueError('Invalid GLB buffer length.')
        views = document.get('bufferViews', [])
        for view in views:
            start, size = view.get('byteOffset', 0), view['byteLength']
            if (view.get('buffer', 0) != 0 or type(start) is not int or type(size) is not int
                    or start < 0 or size < 0 or start + size > length):
                raise ValueError('Invalid GLB buffer view range.')
        for image in document.get('images', []):
            if 'uri' in image or 'bufferView' not in image:
                raise ValueError('Only embedded GLB images are supported; external/data URIs are not supported.')
            _index(image['bufferView'], views, 'image bufferView')
    except (KeyError, TypeError, AttributeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Unsupported or malformed GLB schema.') from exc
    return document, binary


def apply_texture_to_glb(blob, image, material_index=0):
    """Embed PIL RGB/RGBA pixels; preserve source binary and every other binding.

    Material alphaMode, alphaCutoff and factors remain authoritative. RGBA alpha
    is encoded unchanged; an OPAQUE material still ignores it when rendered.
    """
    if image.mode not in ('RGB', 'RGBA'):
        raise ValueError('GLB texture must be RGB or RGBA.')
    document, binary = read_glb(blob)
    try:
        material = _index(material_index, document.get('materials', []), 'material')
        binding = material['pbrMetallicRoughness']['baseColorTexture']
        textures = document['textures']
        texture = _index(binding['index'], textures, 'base-color texture')
        _index(texture['source'], document['images'], 'texture source')
        # Alternate image-source extensions would override our replacement.
        if texture.get('extensions'):
            raise ValueError('Texture-source extensions are not supported for the selected texture.')
        if 'sampler' in texture:
            _index(texture['sampler'], document.get('samplers', []), 'sampler')
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('Selected material must have an embedded base-color texture.') from exc
    png = BytesIO()
    image.save(png, format='PNG')
    payload = png.getvalue()
    views = document['bufferViews']
    views.append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': len(payload)})
    document['images'].append({'bufferView': len(views) - 1, 'mimeType': 'image/png'})
    replacement = copy.deepcopy(texture)
    replacement['source'] = len(document['images']) - 1
    textures.append(replacement)
    binding['index'] = len(textures) - 1
    binary += payload
    document['buffers'][0]['byteLength'] = len(binary)
    binary += b'\0' * (-len(binary) % 4)
    encoded = json.dumps(document, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
    encoded += b' ' * (-len(encoded) % 4)
    return (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(binary))
            + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
            + struct.pack('<II', len(binary), 0x004E4942) + binary)
