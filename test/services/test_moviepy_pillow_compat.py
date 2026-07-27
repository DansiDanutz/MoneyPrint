import numpy as np
from moviepy import CompositeVideoClip, ImageClip, TextClip
from PIL import Image


def test_moviepy_image_text_pipeline_with_pillow_12(tmp_path):
    source = tmp_path / "source.png"
    Image.new("RGBA", (8, 6), (255, 0, 0, 128)).save(source)

    image = ImageClip(str(source), transparent=True).resized(new_size=(16, 12)).with_duration(0.1)
    text = TextClip(
        text="Pillow 12",
        font_size=12,
        color="white",
        bg_color="black",
    ).with_duration(0.1)
    composite = CompositeVideoClip(
        [image, text.with_position("center")],
        size=(16, 12),
    )

    try:
        frame = composite.get_frame(0)
        assert frame.shape == (12, 16, 3)
        Image.fromarray(np.asarray(frame, dtype=np.uint8)).save(tmp_path / "frame.png")
        assert (tmp_path / "frame.png").stat().st_size > 0
    finally:
        composite.close()
        text.close()
        image.close()
