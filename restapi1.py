import os
import requests
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DOCKER_SERVICE_URL = 'http://localhost:8080/analyze'  
TIMEOUT = 300

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'APK Analysis Backend'})

@app.route('/analyze', methods=['POST'])
def analyze_apk():
    # Get uploaded file
    file = request.files['file']
    
    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Send to Docker
    try:
        with open(filepath, 'rb') as apk_file:
            files = {'file': apk_file}
            response = requests.post(DOCKER_SERVICE_URL, files=files, timeout=TIMEOUT)
        
        # Cleanup
        os.remove(filepath)
        
        # Return response
        return response.json()
    
    except requests.exceptions.ConnectionError:
        # Cleanup
        os.remove(filepath)
        return jsonify({
            'success': False,
            'error': 'Docker service unavailable',
            'message': f'Could not connect to Docker service at {DOCKER_SERVICE_URL}',
            'filename': filename
        }), 503
    
    except requests.exceptions.Timeout:
        # Cleanup
        os.remove(filepath)
        return jsonify({
            'success': False,
            'error': 'Docker service timeout',
            'message': 'Docker service did not respond within timeout period',
            'filename': filename
        }), 504
    
    except Exception as e:
        # Cleanup
        os.remove(filepath)
        return jsonify({
            'success': False,
            'error': 'Service error',
            'message': str(e),
            'filename': filename
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)