from flask import Flask, request, jsonify
from urllib.parse import unquote
import re
from pyproj import Transformer

app = Flask(__name__)

# Home route (avoid 404 error)
@app.route('/')
def home():
    return "✅ Coordinate Conversion API is running!"

# Convert DMS string to decimal
def dms_to_decimal(dms_str):
    match = re.match(r"(\d+)[°:\s]+(\d+)'[\s]*(\d+(?:\.\d+)?)?\"?[\s]*([NSEW])", dms_str.strip(), re.IGNORECASE)
    if not match:
        return None
    degrees, minutes, seconds, direction = match.groups()
    decimal = float(degrees) + float(minutes) / 60 + (float(seconds) if seconds else 0) / 3600
    if direction.upper() in ['S', 'W']:
        decimal = -decimal
    return decimal

# Extract coordinates from various formats in a string/link
def extract_coords_from_link(text):
    decoded = unquote(text.strip())

    # Match @lat,lon
    match = re.search(r'@([0-9.\-]+),([0-9.\-]+)', decoded)
    if match:
        return float(match.group(1)), float(match.group(2))

    # Match q=lat,lon
    match = re.search(r'q=([0-9.\-]+),([0-9.\-]+)', decoded)
    if match:
        return float(match.group(1)), float(match.group(2))
