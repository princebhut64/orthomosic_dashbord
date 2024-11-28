from flask import Flask, render_template, request, jsonify, send_file
import os
import requests
import rasterio
import matplotlib.pyplot as plt

app = Flask(__name__, static_folder='public', template_folder='templates')

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simulated location data for dropdowns
data = {
    'countries': ['India'],
    'states': ['Gujarat', 'Madhya Pradesh', 'Maharashtra'],
    'cities': ['Ahmedabad', 'Mumbai','Rajkot'],
    'projects': ['Project A', 'Project B', 'Project C']
}

def get_coordinates(country, state, city):
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    url = f"https://nominatim.openstreetmap.org/search.php?q={city}%2C+{state}%2C+{country}&format=jsonv2"
    response = requests.request("GET",url,headers=headers)
    print(response)
    if response:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        else:
            return None, None
    else:
        return None, None

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/upload', methods=['POST'])
def upload_file():
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
            fig, ax = plt.subplots()
            rasterio.plot.show(src, ax=ax)
            plt.savefig(os.path.join('public', 'orthomosaic.png'))
    except Exception as e:
        return jsonify({'error': f'Failed to process TIFF file: {str(e)}'}), 500

    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/get_data', methods=['GET'])
def get_data():
    country = request.args.get('country')
    state = request.args.get('state')
    city = request.args.get('city')
    project = request.args.get('project')
    print(country, state, city)
    
    # Fetch coordinates dynamically
    lat, lon = get_coordinates(country, state, city)
    if lat and lon:
        coords = [float(lat), float(lon)]
    else:
        coords = [23.0225, 72.5714]  # Default to Ahmedabad if coordinates not found

    response_data = {
        'status': 'success',
        'message': f'Data for {project} in {city}, {state}, {country}',
        'coords': coords
    }
    return jsonify(response_data)

# @app.route('/orthomosaic')
# def get_orthomosaic():
#     return send_file('public/orthomosaic.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
