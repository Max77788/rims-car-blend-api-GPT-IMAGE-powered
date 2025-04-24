# Car Wheel Image Blender API

A Flask-based REST API that blends car and wheel images using OpenAI's image editing capabilities. The service accepts URLs of two images (a car and a wheel) and returns a blended composite image.

## Features

- RESTful endpoint for image blending
- Supports various image resolutions (landscape, portrait, square)
- Automatic image format handling and conversion
- Production/development environment configuration
- Temporary file cleanup

## Prerequisites

- Python 3.x
- OpenAI API key
- Flask
- Pillow (PIL)
- python-dotenv

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
IS_PRODUCTION=false
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Send a POST request to `/blend` endpoint:
```bash
curl -X POST http://localhost:5000/blend \
  -H "Content-Type: application/json" \
  -d '{
    "car_url": "https://example.com/car.jpg",
    "wheel_url": "https://example.com/wheel.jpg"
  }'
```

The API will return a PNG image of the blended result.

## API Reference

### POST /blend

Blends two images together using OpenAI's image editing API.

**Request Body:**
```json
{
  "car_url": "string (required)",
  "wheel_url": "string (required)"
}
```

**Response:**
- Success: PNG image (200 OK)
- Error: JSON with error message (400, 502, or 500)

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `IS_PRODUCTION`: Set to "true" for production mode (default: "false")

## Error Handling

- 400: Missing or invalid request parameters
- 502: Error fetching images from provided URLs
- 500: Internal server error

## License

MIT License