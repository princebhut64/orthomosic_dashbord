from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import rasterio
import numpy as np
import folium
from PIL import Image

app = Flask(__name__, static_folder='public', template_folder='templates')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simulated location data for dropdowns
data = {
    'countries': ['India'],
    'states': ['Gujarat', 'Madhya Pradesh', 'Maharashtra','Indore'],
    'cities': ['Ahmedabad', 'Mumbai', 'Rajkot','Surat','Vadodara','Junagadh'],
    'projects': ['Project A', 'Project B', 'Project C']
}

def get_coordinates(country, state, city):
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    url = f"https://nominatim.openstreetmap.org/search.php?q={city},+{state},+{country}&format=jsonv2"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        location_data = response.json()[0]
        return float(location_data['lat']), float(location_data['lon'])
    return None, None

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/upload_tiff', methods=['POST'])
def upload_tiff():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Process the TIFF file
    try:
        with rasterio.open(filepath) as src:
            bounds = src.bounds
            epsg_code = src.crs.to_epsg()
            metadata = {
                'bounds': {
                    'left': bounds.left,
                    'bottom': bounds.bottom,
                    'right': bounds.right,
                    'top': bounds.top
                },
                'epsg': epsg_code
            }

            # Read all bands
            bands = src.read([1, 2, 3])
            rgb = np.dstack(bands)

            # Normalize the RGB image
            rgb_normalized = np.clip(rgb, 0, 255).astype(np.uint8)

            # Save the RGB image as a PNG
            image_path = os.path.join(UPLOAD_FOLDER, 'tiff_image.png')
            img = Image.fromarray(rgb_normalized)
            img.save(image_path)

            # Map creation
            center_lat = (bounds.bottom + bounds.top) / 2
            center_lon = (bounds.left + bounds.right) / 2
            m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

            # Add the TIFF image as an overlay
            folium.raster_layers.ImageOverlay(
                image=image_path,
                bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
                opacity=0.6
            ).add_to(m)

            # Save the map
            map_path = os.path.join(UPLOAD_FOLDER, 'map_with_tiff.html')
            m.save(map_path)

        return jsonify({'message': 'TIFF file uploaded successfully', 'metadata': metadata, 'map_url': '/map_with_tiff'})

    except Exception as e:
        return jsonify({'error': f'Failed to process TIFF file: {str(e)}'}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    country = request.args.get('country')
    state = request.args.get('state')
    city = request.args.get('city')
    project = request.args.get('project')

    # Fetch coordinates dynamically
    lat, lon = get_coordinates(country, state, city)
    coords = [lat, lon] if lat and lon else [23.0225, 72.5714]  # Default to Ahmedabad
    print(coords)
    response_data = {
        'status': 'success',
        'message': f'Data for {project} in {city}, {state}, {country}',
        'coords': coords
    }
    return jsonify(response_data)

@app.route('/orthomosaic', methods=['GET'])
def orthomosaic():
    image_path = os.path.join(UPLOAD_FOLDER, 'tiff_image.png')
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    return jsonify({'error': 'Orthomosaic image not found'}), 404

@app.route('/map_with_tiff')
def map_with_tiff():
    return send_file(os.path.join(UPLOAD_FOLDER, 'map_with_tiff.html'), mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)
