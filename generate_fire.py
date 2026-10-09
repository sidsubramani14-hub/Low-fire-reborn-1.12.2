from PIL import Image
import math
import os

# Minecraft 1.12.2 Low Fire Texture Animation
# Output: texture_fire_layer.png
# Size: 32 x 1024 pixels (32 frames of 32 x 32)
# Requires: pip install Pillow

WIDTH = 32
FRAME_HEIGHT = 32
FRAME_COUNT = 32
FLAME_HEIGHT = 8

OUTPUT_FILE = "texture_fire_layer.png"

# Vibrant Minecraft PvP flame palette
TRANSPARENT = (0, 0, 0, 0)
DARK_RED = (0xC4, 0x20, 0x00, 255)
ORANGE = (0xFF, 0x6A, 0x00, 255)
YELLOW = (0xFF, 0xD8, 0x00, 255)

PALETTE = [DARK_RED, ORANGE, YELLOW]


def periodic_noise(x, frame, frequency=1.0, phase=0.0):
    """Return smooth periodic motion used only to position hard pixels."""
    angle = 2.0 * math.pi * frame / FRAME_COUNT
    return (
        math.sin(x * frequency + angle + phase)
        + 0.45 * math.sin(x * frequency * 2.0 - angle + phase)
        + 0.25 * math.cos(x * frequency * 3.0 + 2.0 * angle)
    )


def flame_height(x, frame):
    """Calculate a looping, integer-height flame silhouette."""
    motion = periodic_noise(x, frame, frequency=0.31)
    height = 3.4 + motion * 1.65
    return max(1, min(FLAME_HEIGHT, int(round(height))))


def draw_frame(frame_index):
    """Create one crisp 32x32 low-fire animation frame."""
    frame = Image.new("RGBA", (WIDTH, FRAME_HEIGHT), TRANSPARENT)
    pixels = frame.load()

    # All pixels above y=24 remain completely transparent.
    for y in range(24):
        for x in range(WIDTH):
            pixels[x, y] = TRANSPARENT

    # Build the flame upward from the bottom edge.
    heights = [
        flame_height(x, frame_index)
        for x in range(WIDTH)
    ]

    for x in range(WIDTH):
        height = heights[x]

        for offset in range(height):
            y = 31 - offset

            # Dark red outer flame at the lowest and outermost pixels.
            if offset == 0:
                color = DARK_RED
            elif offset < height * 0.40:
                color = ORANGE
            elif offset < height * 0.75:
                color = ORANGE
            else:
                color = YELLOW

            # Create crisp, angular flame tips and interior highlights.
            highlight = periodic_noise(
                x, frame_index, frequency=0.48, phase=1.2
            )

            if offset >= height - 2 and highlight > 0.25:
                color = YELLOW
            elif offset == 1 and highlight < -0.65:
                color = DARK_RED

            pixels[x, y] = color

    # Add a continuous, solid orange/red base to anchor the flame.
    for x in range(WIDTH):
        pixels[x, 31] = DARK_RED if x % 7 == 0 else ORANGE

    # Add small yellow pixel highlights near the flame tips.
    for x in range(WIDTH):
        height = heights[x]

        if height >= 4:
            tip_y = 31 - height + 1
            highlight_motion = periodic_noise(
                x, frame_index, frequency=0.67, phase=2.1
            )

            if highlight_motion > 0.15 and 24 <= tip_y <= 31:
                pixels[x, tip_y] = YELLOW

    # Guarantee that the top 24 rows are entirely transparent.
    for y in range(24):
        for x in range(WIDTH):
            pixels[x, y] = TRANSPARENT

    return frame


def generate_texture():
    """Generate the complete vertically stacked 32-frame sprite sheet."""
    sheet = Image.new(
        "RGBA",
        (WIDTH, FRAME_HEIGHT * FRAME_COUNT),
        TRANSPARENT
    )

    for frame_index in range(FRAME_COUNT):
        frame = draw_frame(frame_index)
        sheet.paste(
            frame,
            (0, frame_index * FRAME_HEIGHT)
        )

    # Ensure the final image has the exact required dimensions.
    assert sheet.size == (32, 1024)

    # Save as a lossless PNG with full alpha transparency.
    sheet.save(OUTPUT_FILE, format="PNG", optimize=False)

    print(f"Created: {os.path.abspath(OUTPUT_FILE)}")
    print(f"Dimensions: {sheet.width} x {sheet.height}")
    print(f"Frames: {FRAME_COUNT} (32 x 32 each)")
    print("Transparent area: rows 0-23 of every frame")
    print("Flame area: rows 24-31 of every frame")


if __name__ == "__main__":
    generate_texture()
