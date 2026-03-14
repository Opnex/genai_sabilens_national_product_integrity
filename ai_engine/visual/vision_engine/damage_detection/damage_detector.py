"""
Measures image sharpness using Laplacian variance and maps it
to a discrete damage_score for downstream use.

IMPORTANT TO NOTE_ WHAT THIS MEASURES:
  This is a SCAN QUALITY detector, not a physical damage detector.
  blur_value measures how sharp the photo is, not whether the
  product label is physically torn or faded.

  A sharp photo of a damaged label will score damage_score=0.1.
  A blurry photo of a pristine label will score damage_score=0.8.
  A4 Fusion Engine needs BOTH values to handle these cases correctly.

OUTPUT CONTRACT (breaking change from previous version):
  damage_score() previously returned a float (0.1 | 0.4 | 0.8).
  It now returns a dict with both blur_value and damage_score.

  A4 Fusion Engine, VisualPipeline.analyze(), and any other caller
  MUST be updated to unpack the dict instead of using a float directly.

BLUR VALUE INTERPRETATION:
  blur_value < 5    → extreme blur - image almost certainly unusable
  blur_value 5-19   → heavy blur  - NAFDAC number may still be readable
  blur_value 20-59  → moderate    - OCR degraded but workable
  blur_value >= 60  → sharp       → normal scan quality

DAMAGE SCORE BANDS (unchanged):
  0.8 → blur_value < 20   (heavy blur)
  0.4 → blur_value 20–59  (moderate blur)
  0.1 → blur_value >= 60  (sharp image)
"""

import cv2


class DamageDetector:

    def blur_score(self, image_path: str) -> float:
        """
        Compute the Laplacian variance of the image as a sharpness score.

        Higher values = sharper image.
        Lower values  = more blur.

        Args:
            image_path: File path to the product image (JPG, PNG, etc.)

        Returns:
            Raw Laplacian variance as a float.
            Typical range: 0.5 (extremely blurry) to 500+ (very sharp).
        """
        img  = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def damage_score(self, image_path: str) -> dict:
        """
        Compute scan quality and map to a discrete damage band.

        BREAKING CHANGE: Previously returned a float.
          Now returns a dict - all callers must be updated.

        Args:
            image_path: File path to the product image.

        Returns:
            Dict with two keys:

            "damage_score" (float): Discrete scan quality band.
                0.8 → heavy blur  (blur_value < 5)
                0.4 → moderate    (blur_value 5-24)
                0.1 → sharp       (blur_value >= 25)

            "blur_value" (float): Raw Laplacian variance score.
                A4 uses this to distinguish blur=2 from blur=19
                (both are damage_score=0.8 but very different situations).
                Also used to decide whether to save the image for
                model retraining and to generate the correct user
                rescan message.

        Example:
            detector = DamageDetector()
            result   = detector.damage_score("label.jpg")

            damage = result["damage_score"]   # 0.8
            blur   = result["blur_value"]     # 14.3
        """
        blur = self.blur_score(image_path)

        if blur < 5:
            damage = 0.8   # Heavy blur - scan quality too low for reliable Visual/OCR
        elif blur < 25:
            damage = 0.4   # Moderate blur - OCR degraded, Regulatory takes more weight
        else:
            damage = 0.1   # Sharp image - normal pipeline

        return {
            "damage_score": damage,
            "blur_value":   round(blur, 4),
        }