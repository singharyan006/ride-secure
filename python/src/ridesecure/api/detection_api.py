"""
RideSecure API Integration
Flask/FastAPI endpoints for detection service integration
"""

from flask import Flask, request, jsonify, Response
import cv2
import numpy as np
import base64
import json
from typing import Dict, Any
import logging
from io import BytesIO
from PIL import Image

from ridesecure.detection import DetectionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
detection_service = DetectionService()

logger.info("🌐 RideSecure API server initialized")


@app.route('/', methods=['GET'])
def api_info():
    """API information and available endpoints"""
    return jsonify({
        'service': 'RideSecure Detection API',
        'version': '1.0.0',
        'status': 'running',
        'description': 'Real-time helmet violation detection system',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'POST /detect/image': 'Single image detection',
            'POST /detect/video': 'Video file processing',
            'POST /detect/stream': 'Real-time stream processing',
            'POST /java/detect': 'Java application integration',
            'GET /statistics': 'Detection statistics',
            'GET /config': 'Get configuration',
            'POST /config': 'Update configuration'
        },
        'usage': {
            'java_integration': 'Use POST /java/detect with base64 encoded image data',
            'web_integration': 'Use POST /detect/image for web applications',
            'streaming': 'Use POST /detect/stream for real-time processing'
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'RideSecure Detection API',
        'version': '1.0.0'
    })


@app.route('/detect/image', methods=['POST'])
def detect_image():
    """
    Detect violations in a single image
    
    Expected JSON payload:
    {
        "image": "base64_encoded_image",
        "timestamp": 1234567890  // optional
    }
    """
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'Missing image data'}), 400
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        image = Image.open(BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Get timestamp
        timestamp_ms = data.get('timestamp', 0)
        
        # Process frame
        result = detection_service.process_single_frame(frame, timestamp_ms)
        
        # Encode annotated frame back to base64
        _, buffer = cv2.imencode('.jpg', result['annotated_frame'])
        annotated_image_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'violations_count': len(result['violations']),
            'violations': result['violations'],
            'helmet_detections': len(result['helmet_detections']),
            'plate_detections': len(result['plate_detections']),
            'processing_time_ms': result['processing_time_ms'],
            'annotated_image': annotated_image_b64
        })
        
    except Exception as e:
        logger.error(f"❌ Image detection error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/detect/video', methods=['POST'])
def detect_video():
    """
    Process uploaded video file for violations
    
    Expects multipart/form-data with video file
    """
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        
        # Save uploaded file temporarily
        temp_path = f"/tmp/{video_file.filename}"
        video_file.save(temp_path)
        
        # Process video
        results = detection_service.process_video_file(temp_path)
        
        # Clean up temporary file
        import os
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"❌ Video processing error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/detect/stream', methods=['POST'])  
def detect_stream():
    """
    Real-time stream processing endpoint
    Processes individual frames from video stream
    """
    try:
        # Similar to detect_image but optimized for streaming
        data = request.get_json()
        
        if 'frame' not in data:
            return jsonify({'error': 'Missing frame data'}), 400
        
        # Decode frame
        frame_data = base64.b64decode(data['frame'])
        frame_image = Image.open(BytesIO(frame_data))
        frame = cv2.cvtColor(np.array(frame_image), cv2.COLOR_RGB2BGR)
        
        # Process with lighter config for real-time
        timestamp_ms = data.get('timestamp', 0)
        result = detection_service.process_single_frame(frame, timestamp_ms)
        
        # Return only essential data for streaming
        return jsonify({
            'violations_count': len(result['violations']),
            'violations': [{
                'type': v['violation_type'],
                'confidence': v['confidence_score'],
                'bbox': v['location_bbox'],
                'plate': v['license_plate']['text'] if v['license_plate'] else None
            } for v in result['violations']],
            'processing_time_ms': result['processing_time_ms']
        })
        
    except Exception as e:
        logger.error(f"❌ Stream processing error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get detection service statistics"""
    try:
        stats = detection_service.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"❌ Statistics error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update detection service configuration"""
    try:
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'config': detection_service.config
            })
        
        elif request.method == 'POST':
            new_config = request.get_json()
            detection_service.config.update(new_config)
            
            return jsonify({
                'success': True,
                'message': 'Configuration updated',
                'config': detection_service.config
            })
            
    except Exception as e:
        logger.error(f"❌ Config management error: {e}")
        return jsonify({'error': str(e)}), 500


# Java Integration Helper Functions
def create_java_compatible_response(violations: list, frame_info: dict) -> dict:
    """
    Create response format compatible with Java application
    Matches the expected format from DatabaseService
    """
    return {
        'detectionId': frame_info.get('detection_id', ''),
        'videoFile': frame_info.get('video_file', ''),
        'timestamp': frame_info.get('timestamp_ms', 0),
        'violationsDetected': len(violations),
        'violationDetails': [
            {
                'violationType': v['violation_type'],
                'confidenceScore': v['confidence_score'],
                'boundingBox': {
                    'x': v['location_bbox'][0],
                    'y': v['location_bbox'][1], 
                    'width': v['location_bbox'][2],
                    'height': v['location_bbox'][3]
                },
                'licensePlate': v['license_plate']['text'] if v['license_plate'] else None,
                'plateConfidence': v['license_plate']['confidence'] if v['license_plate'] else 0.0
            }
            for v in violations
        ]
    }


@app.route('/java/detect', methods=['POST'])
def java_detect_endpoint():
    """
    Specialized endpoint for Java application integration
    Returns data in format expected by RideSecureSwingApp
    """
    try:
        data = request.get_json()
        
        # Decode image from Java
        image_data = base64.b64decode(data['imageData'])
        image = Image.open(BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Process frame
        result = detection_service.process_single_frame(
            frame, 
            data.get('timestamp', 0)
        )
        
        # Format for Java compatibility
        java_response = create_java_compatible_response(
            result['violations'],
            {
                'detection_id': data.get('detectionId', ''),
                'video_file': data.get('videoFile', ''),
                'timestamp_ms': data.get('timestamp', 0)
            }
        )
        
        return jsonify(java_response)
        
    except Exception as e:
        logger.error(f"❌ Java integration error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("🚀 Starting RideSecure API server...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )