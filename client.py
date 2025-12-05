"""
Deadlift AI API Client Library
Provides easy integration with the Flask backend API
"""

import requests
import base64
import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from pathlib import Path


class DeadliftAIClient:
    """Client for interacting with Deadlift AI Flask API"""
    
    def __init__(self, api_url: str = 'http://localhost:5000'):
        """
        Initialize the API client
        
        Args:
            api_url: Base URL of the Flask API (default: http://localhost:5000)
        """
        self.api_url = api_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """
        Check if the API is running and healthy
        
        Returns:
            bool: True if API is healthy, False otherwise
        """
        try:
            response = self.session.get(f'{self.api_url}/health', timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def detect_from_file(self, image_path: str) -> Dict:
        """
        Detect pose from an image file
        
        Args:
            image_path: Path to image file (jpg, png, etc.)
            
        Returns:
            dict: Detection results including stage, class, probability, counter
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        return self.detect_from_bytes(image_data)
    
    def detect_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect pose from image bytes
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            dict: Detection results
        """
        image_b64 = base64.b64encode(image_bytes).decode()
        return self.detect(image_b64)
    
    def detect_from_array(self, image_array: np.ndarray) -> Dict:
        """
        Detect pose from numpy array (OpenCV format)
        
        Args:
            image_array: Numpy array in BGR format
            
        Returns:
            dict: Detection results
        """
        success, buffer = cv2.imencode('.jpg', image_array)
        if not success:
            raise ValueError("Failed to encode image array")
        
        return self.detect_from_bytes(buffer.tobytes())
    
    def detect(self, image_b64: str) -> Dict:
        """
        Detect pose from base64 encoded image
        
        Args:
            image_b64: Base64 encoded image string
            
        Returns:
            dict: Detection results with keys:
                - stage: Current body stage (up/down)
                - class: Predicted pose class
                - probability: Confidence score (0-1)
                - counter: Current rep count
                - annotated_image: Base64 encoded result image
                - landmarks_detected: Boolean indicating if landmarks were found
        """
        try:
            response = self.session.post(
                f'{self.api_url}/detect',
                json={'image': image_b64},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    def stream_detect(self, frame_b64: str) -> Dict:
        """
        Process a video stream frame
        
        Args:
            frame_b64: Base64 encoded frame
            
        Returns:
            dict: Detection results with annotated frame
        """
        try:
            response = self.session.post(
                f'{self.api_url}/stream',
                json={'frame': frame_b64},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    def stream_detect_from_array(self, frame_array: np.ndarray) -> Dict:
        """
        Process a video frame from numpy array
        
        Args:
            frame_array: Numpy array in BGR format
            
        Returns:
            dict: Detection results
        """
        success, buffer = cv2.imencode('.jpg', frame_array)
        if not success:
            raise ValueError("Failed to encode frame")
        
        frame_b64 = base64.b64encode(buffer.tobytes()).decode()
        return self.stream_detect(frame_b64)
    
    def get_status(self) -> Dict:
        """
        Get current session status without processing
        
        Returns:
            dict: Current status with keys:
                - counter: Current rep count
                - current_stage: Current body stage
                - class: Last detected class
                - probability: Last confidence score
        """
        try:
            response = self.session.get(
                f'{self.api_url}/status',
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    def reset(self) -> Dict:
        """
        Reset the rep counter and stage tracking
        
        Returns:
            dict: Reset confirmation with new counter value
        """
        try:
            response = self.session.post(
                f'{self.api_url}/reset',
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {e}")
    
    def save_annotated_image(self, result: Dict, output_path: str) -> None:
        """
        Save annotated image from API result
        
        Args:
            result: Result dictionary from detect() containing 'annotated_image'
            output_path: Path where to save the image
        """
        if 'annotated_image' not in result:
            raise ValueError("Result does not contain 'annotated_image'")
        
        image_b64 = result['annotated_image']
        image_bytes = base64.b64decode(image_b64)
        
        with open(output_path, 'wb') as f:
            f.write(image_bytes)


class DeadliftSession:
    """Manages a workout session with the API"""
    
    def __init__(self, client: DeadliftAIClient):
        """
        Initialize a workout session
        
        Args:
            client: DeadliftAIClient instance
        """
        self.client = client
        self.stats = {
            'total_reps': 0,
            'frames_processed': 0,
            'average_confidence': 0,
            'detections': []
        }
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame in the session
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            dict: Detection result
        """
        result = self.client.stream_detect_from_array(frame)
        
        self.stats['frames_processed'] += 1
        self.stats['total_reps'] = result.get('counter', 0)
        
        if result.get('probability', 0) > 0:
            current_avg = self.stats['average_confidence']
            n = self.stats['frames_processed']
            self.stats['average_confidence'] = (
                (current_avg * (n - 1) + result['probability']) / n
            )
        
        self.stats['detections'].append({
            'frame': self.stats['frames_processed'],
            'stage': result.get('stage'),
            'class': result.get('class'),
            'probability': result.get('probability'),
            'counter': result.get('counter')
        })
        
        return result
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        return {
            'total_reps': self.stats['total_reps'],
            'frames_processed': self.stats['frames_processed'],
            'average_confidence': round(self.stats['average_confidence'], 3),
            'detections_count': len(self.stats['detections'])
        }
    
    def reset(self) -> Dict:
        """Reset the session"""
        self.client.reset()
        self.stats = {
            'total_reps': 0,
            'frames_processed': 0,
            'average_confidence': 0,
            'detections': []
        }
        return {'message': 'Session reset'}


# Example usage
if __name__ == '__main__':
    # Initialize client
    client = DeadliftAIClient('http://localhost:5000')
    
    # Check API health
    if client.health_check():
        print("✓ API is running")
    else:
        print("✗ API is not responding")
        exit(1)
    
    # Example 1: Detect from image file
    print("\n--- Example 1: Detect from Image File ---")
    try:
        result = client.detect_from_file('frame.jpg')
        print(f"Stage: {result['stage']}")
        print(f"Class: {result['class']}")
        print(f"Confidence: {result['probability']:.2%}")
        print(f"Reps: {result['counter']}")
    except FileNotFoundError:
        print("No test image found")
    
    # Example 2: Get current status
    print("\n--- Example 2: Get Status ---")
    status = client.get_status()
    print(f"Current counter: {status['counter']}")
    print(f"Current stage: {status['current_stage']}")
    
    # Example 3: Stream processing with OpenCV
    print("\n--- Example 3: Stream Processing ---")
    cap = cv2.VideoCapture(0)
    session = DeadliftSession(client)
    
    frame_count = 0
    while frame_count < 30:  # Process 30 frames
        ret, frame = cap.read()
        if not ret:
            break
        
        result = session.process_frame(frame)
        frame_count += 1
        
        if frame_count % 10 == 0:
            stats = session.get_session_stats()
            print(f"Processed {stats['frames_processed']} frames, "
                  f"Reps: {stats['total_reps']}, "
                  f"Avg Confidence: {stats['average_confidence']:.2%}")
    
    cap.release()
    
    print("\n--- Session Summary ---")
    final_stats = session.get_session_stats()
    print(f"Total frames: {final_stats['frames_processed']}")
    print(f"Total reps: {final_stats['total_reps']}")
    print(f"Average confidence: {final_stats['average_confidence']:.2%}")
