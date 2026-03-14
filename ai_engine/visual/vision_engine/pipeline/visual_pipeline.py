"""
Orchestrates the full Visual pipeline for one product scan.

PIPELINE:
  1. RegionDetector  → crops brand_logo region from image (YOLO)
  2. SimilarityEngine → compares logo crop against reference embeddings
  3. DamageDetector  → measures scan quality (Laplacian blur)
  4. Fuse into confidence score and return structured output

OUTPUT CONTRACT (what Fusion Engine expects):
  {
      "product":          str,    # Best matched product name from embedding store
      "Visual Similarity": float, # Raw cosine similarity 0.0-1.0 (pre-damage)
      "damage_score":     float,  # Discrete band: 0.1 | 0.4 | 0.8
      "blur_value":       float,  # Raw Laplacian variance for scan triage
      "confidence":       float,  # damage-adjusted similarity (Visual Similarity x (1 - damage_score))
      "verdict":          str,    # "Authentic" | "Suspicious" | "Fake"
  }

BREAKING CHANGE NOTE_:
  damage_detector.damage_score() now returns a dict instead of a float.
  This file has been updated to unpack that dict correctly.
  If you revert damage_detector.py to the old float return, this file will break.
"""

import sys
import json
from vision_engine.similarity.similarity_engine     import SimilarityEngine
from vision_engine.damage_detection.damage_detector import DamageDetector
from vision_engine.regions.yolo_detector            import RegionDetector


class VisualPipeline:

    def __init__(self):
        import os
        _BASE = os.path.dirname(os.path.abspath(__file__))
        self.sim_engine = SimilarityEngine(
            os.path.join(_BASE, "..", "embeddings", "reference_embeddings.pkl")
        )
        self.region_detector = RegionDetector()
        self.damage_detector = DamageDetector()

    def classify(self, confidence: float) -> str:
        """
        Map damage-adjusted confidence to a verdict label.
        Thresholds aligned to orchestrator/pipeline.py.

        Args:
            confidence: Damage-adjusted similarity score 0.0-1.0.

        Returns:
            "Authentic"  if confidence >= 0.75
            "Suspicious" if confidence >= 0.45
            "Fake"       if confidence <  0.45
        """
        if confidence >= 0.75:
            return "Authentic"
        elif confidence >= 0.45:
            return "Suspicious"
        else:
            return "Fake"

    def analyze(self, image_path: str) -> dict:
        """
        Run the full visual analysis pipeline on one product image.

        Steps:
          1. Detect brand logo region with YOLO (falls back to full image).
          2. Compare logo crop against reference embeddings.
          3. Measure scan quality with DamageDetector.
          4. Compute damage-adjusted confidence.
          5. Return structured output for A4 Fusion Engine.

        Args:
            image_path: File path to the product image (JPG, PNG, etc.)

        Returns:
            Dict matching the FusionEngine-VisualInput contract:
            {
                "product":           str,    # matched product name
                "Visual Similarity": float,  # raw cosine similarity 0.0-1.0
                "damage_score":      float,  # 0.1 | 0.4 | 0.8
                "blur_value":        float,  # raw Laplacian value 
                "confidence":        float,  # similarity x (1 - damage_score)
                "verdict":           str,    # Authentic | Suspicious | Fake
            }
        """
        # Detect logo region (YOLO), fall back to full image
        regions    = self.region_detector.detect_regions(image_path)
        logo_input = regions["brand_logo"] if "brand_logo" in regions else image_path


        # Similarity comparison against reference embeddings
        similarity = self.sim_engine.compare(logo_input)

        # Scan quality measurement
        # damage_result is now a dict: {"damage_score": float, "blur_value": float}
        damage_result = self.damage_detector.damage_score(image_path)
        damage_score  = damage_result["damage_score"]   # 0.1 | 0.4 | 0.8
        blur_value    = damage_result["blur_value"]     # raw Laplacian - passed to Fusion

        # Damage-adjusted confidence
        confidence = similarity["similarity"] * (1 - damage_score)

        # Verdict
        verdict = self.classify(confidence)

        return {
            "product":           similarity["product"],
            "Visual Similarity": similarity["similarity"],
            "damage_score":      damage_score,
            "blur_value":        blur_value,      # Fusion uses this for scan triage
            "confidence":        round(confidence, 4),
            "verdict":           verdict,
        }

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python visual_pipeline.py path/to/image.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    print(f"\nRunning VisualPipeline on: {image_path}\n")

    pipeline = VisualPipeline()
    result   = pipeline.analyze(image_path)

    print("===== Output=======================================")
    print(json.dumps(result, indent=2))

    print("\n====Contract Check================================")
    required = [
        "product", "Visual Similarity", "damage_score",
        "blur_value", "confidence", "verdict",
    ]
    all_ok = True
    for field in required:
        val    = result.get(field, "MISSING")
        status = "CONTRACT FULLFILLED" if val != "MISSING" else "CONTRACT FAILED"
        if val == "MISSING":
            all_ok = False
        print(f"  {status}  {field}: {val}")

    print()
    if all_ok:
        print("All contract fields present. Visual output is ready for Fusion.")
    else:
        print("Missing fields: Fusion visual_adapter will use defaults for those.")

