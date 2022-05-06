from .mtcnn_opencv import MTCNN
from .align_trans import get_reference_facial_points, warp_and_crop_face
import numpy as np


class DetectionMtcnn():
    def __init__(self):
        self.detector = MTCNN()
        self.reference = get_reference_facial_points(default_square=True)

    def get_cropped_face(self, image):
        """
        INPUT: 
              image: image must be RGB 
        OUTPUT:
              outputs bounding box, cropped face, 5 facial landmarks
        """
        result = self.detector.detect_faces(image)
        if len(result) < 1:
            return None, None, None
        bbox = []
        landmarks = []
        cropface = []
        for i, data in enumerate(result):
            rbbox = data['box']
            keypoints = data['keypoints']
            r_landmarks = [list(keypoints['left_eye']), list(keypoints['right_eye']), list(keypoints['nose']),
                           list(keypoints['mouth_left']), list(keypoints['mouth_right'])]
            warped_face = warp_and_crop_face(np.array(image), r_landmarks, self.reference, crop_size=(112, 112))
            landmarks.append(r_landmarks)
            bbox.append(rbbox)
            cropface.append(warped_face)

        return cropface, bbox, landmarks
