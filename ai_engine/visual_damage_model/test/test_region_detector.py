from vision_engine.regions.region_detector import RegionDetector

detector = RegionDetector()

regions = detector.detect_regions("vision_dataset/images/train/kellogs_coco_pops_front.jpg")

print(regions.keys())