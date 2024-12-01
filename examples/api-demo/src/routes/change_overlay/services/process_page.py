import cv2
from PIL import Image

from .pix_to_image import pix_to_image


def process_page(pix, color_mask):
    """Processes a single page and applies a color mask."""
    img_array = pix_to_image(pix)

    # Convert to grayscale
    gray_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Apply threshold
    _, mask = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    # Apply color mask
    img_array[mask == 255] = color_mask

    return Image.fromarray(img_array)
