"""
src/preprocessing/face_detector.py
MTCNN-based face detector.
"""
import cv2
from mtcnn import MTCNN

class FaceDetector:
    def __init__(self, min_face_size=20, confidence=0.9):
        self.detector = MTCNN(min_face_size=min_face_size)
        self.confidence = confidence

    def detect(self, image):
        """
        Detects faces in an image.
        
        Args:
            image (np.ndarray): Image in RGB format.
            
        Returns:
            list: A list of dictionaries, where each dict contains 'box' and 'confidence'.
        """
        faces = self.detector.detect_faces(image)
        return [f for f in faces if f['confidence'] >= self.confidence]

    def crop_face(self, image, box, margin=0.2):
        """
        Crops a face from an image using the bounding box.
        
        Args:
            image (np.ndarray): The input image.
            box (list): Bounding box [x, y, w, h].
            margin (float): Margin to add around the face.
            
        Returns:
            np.ndarray: The cropped face.
        """
        x, y, w, h = box
        
        # Apply margin
        x_margin = int(w * margin)
        y_margin = int(h * margin)
        
        x_start = max(0, x - x_margin)
        y_start = max(0, y - y_margin)
        x_end = min(image.shape[1], x + w + x_margin)
        y_end = min(image.shape[0], y + h + y_margin)

        return image[y_start:y_end, x_start:x_end]
