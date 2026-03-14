import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vision_engine.pipeline.visual_pipeline import VisualPipeline

pipeline = VisualPipeline()

result = pipeline.analyze("test_images/kelloggs_cornflakes_front.jpg")

print("\n================ SABILENS VISUAL INSPECTION ================\n")

print("Detected Product Match :", result["product"])
print()

print("Visual Similarity Score:", round(result["Visual Similarity"], 3))
print("Damage Score           :", round(result["damage_score"], 3))
print("Authenticity Confidence:", round(result["confidence"], 3))

print("\nFINAL VERDICT:", result["verdict"].upper())

print("\n============================================================\n")