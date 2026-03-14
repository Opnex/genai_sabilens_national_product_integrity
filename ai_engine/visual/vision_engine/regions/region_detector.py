from ultralytics import YOLO
import cv2


class RegionDetector:
    def __init__(self, model_path="runs/detect/train2/weights/best.pt"):
        self.model = YOLO(model_path)

    def detect_regions(self, image_path):

        image = cv2.imread(image_path)

        results = self.model(image, conf=0.1)[0]

        regions = {"full_image": image}

        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]
            
            print("Detected:", label)
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            crop = image[y1:y2, x1:x2]

            label = self.model.names[cls_id]

            regions[label] = crop

        return regions 