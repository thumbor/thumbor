import os
import unittest
from PIL import Image


class MockConfig:
    def __init__(self):
        self.pillow_resampling_filter = "LANCZOS"
        self.respect_orientation = True


class MockContext:
    def __init__(self):
        self.config = MockConfig()
        self.request = None


class MockRequest:
    def __init__(self):
        self.engine = None


class MockEngine:
    def __init__(self):
        self.context = MockContext()
        self.context.request = MockRequest()
        self.context.request.engine = self
        self.image = None
        self.extension = None
        self.original_mode = None


FIXTURES_PATH = os.path.join(os.path.dirname(__file__), "fixtures")


class TestPILEngineTransparentResize(unittest.TestCase):
    def setUp(self):
        self.engine = MockEngine()

    def create_test_png(self, width, height, has_alpha=True):
        """Creates a test PNG with optional transparency"""
        mode = "RGBA" if has_alpha else "RGB"
        image = Image.new(
            mode, (width, height), (255, 0, 0, 0) if has_alpha else (255, 0, 0)
        )

        # Add some visible content
        if has_alpha:
            # Create a pattern with varying transparency
            for x in range(width):
                for y in range(height):
                    alpha = int((x / width) * 255)
                    image.putpixel((x, y), (255, 0, 0, alpha))
        return image

    def test_resize_transparent_png_wide(self):
        """Test resizing a wide transparent PNG (width >> height)"""
        original_width, original_height = 1000, 100
        target_width, target_height = 500, 50

        # Create wide transparent PNG
        image = self.create_test_png(original_width, original_height)

        # Verify original image has transparency
        self.assertEqual(image.mode, "RGBA")

        # Perform resize
        resized_image = image.resize(
            (target_width, target_height), Image.Resampling.LANCZOS
        )

        # Verify transparency is preserved
        self.assertEqual(resized_image.mode, "RGBA")

        # Verify dimensions
        self.assertEqual(resized_image.size, (target_width, target_height))

        # Verify pixels still have transparency
        pixels = list(resized_image.getdata())
        self.assertTrue(
            any(p[3] < 255 for p in pixels)
        )  # Should have some transparent pixels

    def test_resize_transparent_png_extreme_ratio(self):
        """Test resizing a PNG with extreme aspect ratio"""
        original_width, original_height = 2000, 50  # 40:1 ratio
        target_width, target_height = 1000, 25

        # Create extremely wide transparent PNG
        image = self.create_test_png(original_width, original_height)

        # Verify original image has transparency
        self.assertEqual(image.mode, "RGBA")

        # Perform resize
        resized_image = image.resize(
            (target_width, target_height), Image.Resampling.LANCZOS
        )

        # Verify transparency is preserved
        self.assertEqual(resized_image.mode, "RGBA")

        # Verify dimensions
        self.assertEqual(resized_image.size, (target_width, target_height))

        # Verify pixels still have transparency
        pixels = list(resized_image.getdata())
        self.assertTrue(
            any(p[3] < 255 for p in pixels)
        )  # Should have some transparent pixels

    def test_resize_transparent_png_verify_pixels(self):
        """Test that pixel values and transparency are preserved correctly after resize"""
        width, height = 100, 50

        # Create a simple transparent PNG with known pixel values
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        # Add some pixels with known transparency values
        image.putpixel((0, 0), (255, 0, 0, 255))  # Fully opaque red
        image.putpixel((1, 0), (0, 255, 0, 128))  # Semi-transparent green
        image.putpixel((2, 0), (0, 0, 255, 0))  # Fully transparent blue

        # Fill a larger area with solid color to ensure fully opaque pixels survive resize
        for x in range(10):
            for y in range(10):
                image.putpixel((x, y), (255, 0, 0, 255))

        # Resize the image
        resized_image = image.resize((50, 25), Image.Resampling.LANCZOS)

        # Verify image mode
        self.assertEqual(resized_image.mode, "RGBA")

        # Verify that transparency variations are preserved
        # Due to interpolation during resize, we check for approximate values
        pixels = list(resized_image.getdata())
        max_alpha = max(p[3] for p in pixels)
        min_alpha = min(p[3] for p in pixels)

        # Verify we have a good range of transparency values
        self.assertGreater(max_alpha, 240)  # Close to fully opaque
        self.assertLess(min_alpha, 10)  # Close to fully transparent
        self.assertTrue(
            any(10 < p[3] < 240 for p in pixels)
        )  # Some semi-transparent pixels


if __name__ == "__main__":
    unittest.main()
