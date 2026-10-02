"""Rasterize game-native indexed glyphs with an opaque one-pixel black rim."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def outlined_glyph(character, font, palette):
    # Keep the previous 18x18 face and its baseline; add one pixel on every side.
    face = Image.new('L', (18, 18))
    box = font.getbbox(character)
    ImageDraw.Draw(face).text(
        ((18-box[2]+box[0])//2-box[0], (18-box[3]+box[1])//2-box[1]),
        character, font=font, fill=255)
    padded = Image.new('L', (20, 20))
    padded.paste(face, (1, 1))
    coverage = np.asarray(padded)
    # No blurred shadow: a full eight-neighbour rim surrounds the face.
    silhouette = padded.point(lambda value: 255 if value else 0)
    rim = np.asarray(silhouette.filter(ImageFilter.MaxFilter(3))) > 0
    lookup = np.array([3+int(np.argmin(abs(palette[3:16, 0].astype(int)-v)))
                       for v in range(256)], dtype=np.uint8)
    # Index 0 is near-transparent black; index 2 is near-transparent magenta
    # and produces coloured fringes when the PS2 filters texture edges.
    result = np.zeros((20, 20), dtype=np.uint8)
    result[rim] = 3  # Original opaque black, original CLUT/alpha unchanged.
    result[coverage > 0] = lookup[coverage[coverage > 0]]
    return result
