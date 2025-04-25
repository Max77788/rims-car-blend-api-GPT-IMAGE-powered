import base64
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from PIL import Image
from io import BytesIO
import requests

import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def crop_to_aspect(image: Image.Image, aspect_ratio: float) -> Image.Image:
    """
    Crop the PIL Image to the given aspect ratio (width/height) centered.
    """
    width, height = image.size
    current_ratio = width / height
    target_ratio = aspect_ratio

    if current_ratio > target_ratio:
        # too wide: crop width
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        # too tall: crop height
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))

    return image


def blend_car_and_wheel_images(car_image_path, wheel_image_path, resolution="landscape"):
    """
    Blend a car image with a wheel image using OpenAI's image editing API.
    car_image_path and wheel_image_path should be file paths to PNG images.
    """
    # Log input paths
    print(f"blend_car_and_wheel_images called with: {car_image_path}, {wheel_image_path}, resolution={resolution}")

    # Define the prompt for blending
    prompt = f"""
    Blend the car and wheel images together..
    """
    
    resolutions = {"square":"1024x1024", "portrait":"1024x1536", "landscape":"1536x1024"}

    # Call the OpenAI API to blend the images
    print("Opening image files...")
    
    print("Files opened, calling OpenAI API...")
    with open(car_image_path, "rb") as car_file, \
         open(wheel_image_path, "rb") as wheel_file:

        try:
            result = client.images.edit(
                model="gpt-image-1",
                image=[car_file, wheel_file],
                prompt=prompt,
                size="1536x1024"  # or dynamic
            )
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e  # Let it bubble up and be caught by the caller
    
    print("Received response from OpenAI API")

    # Decode the base64 image data
    image_base64 = result.data[0].b64_json
    print(f"Base64 length: {len(image_base64)} characters")
    image_bytes = base64.b64decode(image_base64)

    # Save to file
    output_path = "blended_image.png"
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    print(f"Saved blended image to {output_path}")

    # Clean up temporary inputs
    try:
        os.remove(car_image_path)
        print(f"Deleted temporary file: {car_image_path}")
    except Exception as e:
        print(f"Error deleting {car_image_path}: {e}")

    try:
        os.remove(wheel_image_path)
        print(f"Deleted temporary file: {wheel_image_path}")
    except Exception as e:
        print(f"Error deleting {wheel_image_path}: {e}")

    return image_base64
        

# blend_car_and_wheel_images("tmp/car_8d20.png", "tmp/wheel_a680.png")