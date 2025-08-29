import os
import requests
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Manual CORS handling
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

UPLOAD_FOLDER = 'uploads'
DOCKER_SERVICE_URL = 'http://localhost:8080/analyze'  # Using mock service
TIMEOUT = 300

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'APK Analysis Backend'})

@app.route('/analyze', methods=['POST'])
def analyze_apk():
    try:
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
            
            # File kept in uploads folder for persistence
            # os.remove(filepath)  # Commented out to keep files
            
            # Return response
            return response.json()
            
        except requests.exceptions.ConnectionError:
            # Docker service not available - return mock response but keep file
            return jsonify({
                'success': False,
                'error': 'Docker service unavailable',
                'message': f'Could not connect to {DOCKER_SERVICE_URL}',
                'filename': filename,
                'status': 'File saved but analysis failed'
            })
        except requests.exceptions.Timeout:
            # Timeout - keep file
            return jsonify({
                'success': False,
                'error': 'Analysis timeout',
                'filename': filename,
                'status': 'File saved but analysis timed out'
            })
        except Exception as docker_error:
            # Other Docker errors - keep file
            return jsonify({
                'success': False,
                'error': 'Docker service error',
                'details': str(docker_error),
                'filename': filename,
                'status': 'File saved but analysis failed'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Upload failed',
            'details': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)