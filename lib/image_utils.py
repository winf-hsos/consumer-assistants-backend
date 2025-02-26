import os
import base64
from pathlib import Path
from typing import Optional, Union

# Define base directory
MAIN_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = MAIN_DIR / "data/images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def ensure_path(path: Union[str, Path]) -> Path:
    """Ensure the input is a Path object."""
    return path if isinstance(path, Path) else Path(path)

def path_to_str(path: Union[str, Path]) -> str:
    """Convert a Path object to a string."""
    return str(ensure_path(path))

def save_image(image_data: bytes, img_name: str, path: Optional[Union[str, Path]] = None) -> Path:
    """Save an image to the specified path."""
    path = ensure_path(path) if path else IMAGE_DIR
    image_path = path / f"{img_name}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_data)
    return image_path

def read_image(image_path: Union[str, Path]) -> bytes:
    """Read an image from the given path."""
    image_path = ensure_path(image_path)
    with open(image_path, "rb") as f:
        return f.read()

def encode_image_base64(image_path: Union[str, Path]) -> str:
    """Encode an image to a base64 string."""
    image_path = ensure_path(image_path)
    image_data = read_image(image_path)
    return base64.b64encode(image_data).decode("utf-8")

def decode_image_base64(base64_string: str) -> bytes:
    """Decode a base64 string to image bytes."""
    return base64.b64decode(base64_string)

def encode_image_openai_format(image_path: Union[str, Path]) -> str:
    """Encode an image in OpenAI-compatible base64 format."""
    image_path = ensure_path(image_path)
    file_extension = image_path.suffix.lstrip(".")  # Get file extension (e.g., jpg, png)
    base64_image = encode_image_base64(image_path)
    return f"data:image/{file_extension};base64,{base64_image}"
