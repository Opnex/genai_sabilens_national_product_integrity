from backend.ocr_linguistic.pipeline import run_pipeline
# import json

if __name__ == "__main__":
    image_path = r"reference_dataset\vaseline_blueseal\back.jpg" 

    result = run_pipeline(image_path)

    from pprint import pprint
    pprint(result)