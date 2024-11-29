import numpy as np


def pix_to_image(pix):
    """Converts a Pixmap object to a NumPy array representing the image."""
    bytes = np.frombuffer(pix.samples, dtype=np.uint8)
    img = bytes.reshape(pix.height, pix.width, pix.n)
    return img.copy()
