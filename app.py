from functions import blend_car_and_wheel_images
import os
import base64
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, jsonify, send_file
from openai import OpenAI
from PIL import Image
from io import BytesIO
import requests
import math
import uuid

# Load environment variables from .env
load_dotenv(find_dotenv())

IS_PRODUCTION = os.environ.get("IS_PRODUCTION", "false").lower() == "true"

TMP_DIR = "/tmp" if IS_PRODUCTION else "tmp"

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable")
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Flask application
app = Flask(__name__)

@app.route('/blend', methods=['POST'])
def blend_route():
    """
    HTTP endpoint to accept two image URLs (car and wheel) and return the blended image as base64.
    Expects a JSON payload with fields 'car_url' and 'wheel_url'.
    The car image will be center-cropped to a 4:3 aspect ratio before blending.
    """
    data = request.get_json(force=True)
    if not data or 'car_url' not in data or 'wheel_url' not in data:
        return jsonify({'error': 'JSON with both "car_url" and "wheel_url" is required.'}), 400

    car_url = data['car_url']
    wheel_url = data['wheel_url']

    try:
        # Fetch images from URLs
        print(f"Fetching car image from: {car_url}")
        car_resp = requests.get(car_url)
        print(f"Car fetch status: {car_resp.status_code}")
        car_resp.raise_for_status()

        print(f"Fetching wheel image from: {wheel_url}")
        wheel_resp = requests.get(wheel_url)
        print(f"Wheel fetch status: {wheel_resp.status_code}")
        wheel_resp.raise_for_status()

        # Open images
        car_img = Image.open(BytesIO(car_resp.content))
        wheel_img = Image.open(BytesIO(wheel_resp.content))
        print("Opened both images successfully")

        width, height = car_img.size
        print(f"Car image is {width}×{height} pixels")

        resolution = ""
        
        if width > height:
            resolution = "landscape"
        elif width < height:
            resolution = "portrait"
        else:
            resolution = "square"
        
        print(f"Resolution to use: {resolution}")

        # Prepare file-like objects for API
        car_buffer = BytesIO()
        car_img.save(car_buffer, format='PNG')
        car_buffer.seek(0)

        wheel_buffer = BytesIO()
        wheel_img.save(wheel_buffer, format='PNG')
        wheel_buffer.seek(0)

        # Save a local copy of the car and wheel images
        local_car_path = f"{TMP_DIR}/car_{str(uuid.uuid4())[:4]}.png"
        local_wheel_path = f"{TMP_DIR}/wheel_{str(uuid.uuid4())[:4]}.png"
        print(f"Saving car buffer to: {local_car_path}")
        open(local_car_path, 'wb').write(car_buffer.getvalue())
        print(f"Saved car image to: {local_car_path}")

        print(f"Saving wheel buffer to: {local_wheel_path}")
        open(local_wheel_path, 'wb').write(wheel_buffer.getvalue())
        print(f"Saved wheel image to: {local_wheel_path}")

        try:
            print(f"Calling blend_car_and_wheel_images with paths: {local_car_path}, {local_wheel_path}")
            blended_b64 = blend_car_and_wheel_images(local_car_path, local_wheel_path, resolution=resolution)
            print(f"Received blended image, length of base64: {len(blended_b64)} characters")
        except Exception as blend_error:
            print(f"Error during blending: {blend_error}")
            return jsonify({'error': 'Blending failed', 'details': str(blend_error)}), 500
        
        
        
        # Decode the Base64 into bytes
        blended_bytes = base64.b64decode(blended_b64)
        
        # Wrap in a BytesIO stream so send_file can read it like a file
        img_io = BytesIO(blended_bytes)
        img_io.seek(0)
        
        # return jsonify({'image_b64': blended_b64}), 200

        # Stream it back as an image/png
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False,   # True → tell browser to download; False → display inline
            download_name='blended.png'
        )

    except requests.HTTPError as http_err:
        print(f"HTTP error when fetching images: {http_err}")
        return jsonify({'error': f'HTTP error when fetching images: {http_err}'}), 502
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure tmp directory exists
    os.makedirs('tmp', exist_ok=True)
    # Run Flask app on default port 5000
    app.run(debug=not IS_PRODUCTION, port=5000)