from flask import Flask, request, jsonify
from urllib.parse import unquote
import re
from pyproj import Transformer

app = Flask(__name__)

def dms_to_decimal(dms_str):
    match = re.match(r"(\d+)[°:\s]+(\d+)'[\s]*(\d+(?:\.\d+)?)?\"?[\s]*([NSEW])", dms_str.strip(), re.IGNORECASE)
    if not match:
        return None
    degrees, minutes, seconds, direction = match.groups()
    decimal = float(degrees) + float(minutes) / 60 + (float(seconds) if seconds else 0) / 3600
    if direction.upper() in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_coords_from_link(text):
    decoded = unquote(text.strip())
    match = re.search(r'@([0-9.\-]+),([0-9.\-]+)', decoded)
    if match:
        return float(match.group(1)), float(match.group(2))

    match = re.search(r'q=([0-9.\-]+),([0-9.\-]+)', decoded)
    if match:
        return float(match.group(1)), float(match.group(2))

    match = re.match(r'^\s*([0-9.\-]+)\s*[, ]\s*([0-9.\-]+)\s*$', decoded)
    if match:
        return float(match.group(1)), float(match.group(2))

    dms_matches = re.findall(r'\d+°\d+\'\d+(?:\.\d+)?["]?[NSEW]', decoded)
    if len(dms_matches) == 2:
        lat = dms_to_decimal(dms_matches[0])
        lon = dms_to_decimal(dms_matches[1])
        if lat is not None and lon is not None:
            return lat, lon
    return None

def wgs84_to_itm(lat, lon):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:2039", always_xy=True)
    x, y = transformer.transform(lon, lat)
    return round(x), round(y)

@app.route('/convert', methods=['GET'])
def convert():
    link = request.args.get('input')
    if not link:
        return jsonify({"error": "Missing input parameter"}), 400

    coords = extract_coords_from_link(link)
    if not coords:
        return jsonify({"error": "Invalid or unsupported format"}), 400

    lat, lon = coords
    x, y = wgs84_to_itm(lat, lon)
    return jsonify({
        "input": link,
        "latitude": lat,
        "longitude": lon,
        "itm_x": x,
        "itm_y": y
    })

if __name__ == '__main__':
    app.run(debug=True)
