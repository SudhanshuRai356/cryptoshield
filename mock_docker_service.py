#!/usr/bin/env python3
"""
Mock Docker Service for Testing APK Backend
Runs on port 8080 and simulates APK analysis responses
"""
from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'Mock APK Analyzer'})

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Simulate analysis time
    time.sleep(2)
    
    # Random analysis result for testing
    is_safe = random.choice([True, False, True, True])  # 75% safe for testing
    threat_levels = ['low', 'medium', 'high', 'critical']
    threat_level = random.choice(threat_levels)
    
    if is_safe:
        return jsonify({
            'status': 'safe',
            'safe': True,
            'threat_level': 'none',
            'confidence': random.randint(85, 99),
            'analysis': {
                'malware_detected': False,
                'permissions': 'normal',
                'network_activity': 'clean'
            },
            'message': 'APK appears to be safe'
        })
    else:
        return jsonify({
            'status': 'unsafe',
            'safe': False,
            'threat_level': threat_level,
            'confidence': random.randint(70, 95),
            'analysis': {
                'malware_detected': True,
                'suspicious_permissions': ['SEND_SMS', 'READ_CONTACTS'],
                'network_activity': 'suspicious'
            },
            'message': f'APK shows {threat_level} level threats'
        })

if __name__ == '__main__':
    print("🧪 Starting Mock Docker Service for APK Analysis Testing")
    print("📡 Running on http://localhost:8080")
    print("🔄 This service simulates random analysis results for testing")
    app.run(host='localhost', port=8080, debug=True)
