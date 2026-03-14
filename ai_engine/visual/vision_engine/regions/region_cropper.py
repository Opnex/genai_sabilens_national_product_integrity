from turtle import width

import cv2

class RegionCropper:
    
    def crop_center(self, image_path):
        img = cv2.imread(image_path)
        
        h,w, _ = img.shape
        
        # Crop central 60% area
        x1 = int(w * 0.2)
        x2 = int(w * 0.8)
        
        y1 = int(h * 0.2)
        y2 = int(h * 0.8)
        
        cropped = img[y1:y2, x1:x2]
        
        return cropped