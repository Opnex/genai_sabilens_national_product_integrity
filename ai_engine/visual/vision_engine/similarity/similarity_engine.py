import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vision_engine.models.feature_extractor import FeatureExtractor
from vision_engine.regions.region_cropper import RegionCropper

class SimilarityEngine:
    def __init__(self, embedding_path):
        with open(embedding_path, "rb") as f:
            self.embedding_store = pickle.load(f)

        # print("Loaded products:", self.embedding_store.keys())

        self.extractor = FeatureExtractor()

    def compare(self, image_path: str) -> dict:
        """
        Compare a query image against all reference embeddings.

        Args:
            image_path: Path to the query image (full product scan).

        Returns:
            {
                "product":    str,    # Best matched product name
                "similarity": float,  # Cosine similarity 0.0–1.0
            }
        """
        # Extract and L2-normalise query — must match how embeddings were built
        query_embedding = self._extract_normalised(image_path)

        scores = {}
        for product, embeddings in self.embedding_store.items():
            similarities = [
                cosine_similarity(
                    query_embedding.reshape(1, -1),
                    emb.reshape(1, -1)
                )[0][0]
                for emb in embeddings
            ]
            scores[product] = float(max(similarities))

        best_match = max(scores, key=scores.get)
        return {
            "product":    best_match,
            "similarity": scores[best_match],
        }

    def _extract_normalised(self, image_path: str) -> np.ndarray:
        """Extract features and L2-normalise. Must match generate_embeddings.py."""
        vec  = self.extractor.extract(image_path)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm

# class SimilarityEngine:
#     def __init__(self, embedding_path):
#         self.cropper = RegionCropper()
        
#         with open(embedding_path, 'rb') as f:
#             self.embedding_store = pickle.load(f)
        
#         print("Loaded products:", self.embedding_store.keys())
        
#         self.extractor = FeatureExtractor()

#     def compare(self, image_path):

#         query_embedding = self.extractor.extract(image_path)

#         scores = {}
#         for product, embeddings in self.embedding_store.items():
#             similarities = []
#             for emb in embeddings:
#                 sim = cosine_similarity(
#                     query_embedding.reshape(1, -1),
#                     emb.reshape(1, -1)
#                 )[0][0]
#                 similarities.append(sim)
#             scores[product] = max(similarities)

#         best_match = max(scores, key=scores.get)

#         top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
#         print(f"DEBUG top 5 matches: {top5}")

#         return {
#             "product":    best_match,
#             "similarity": float(scores[best_match])
#         }

#     # def compare(self, image_path):
        
#     #     cropped = self.cropper.crop_center(image_path)
        
#     #     query_embedding = self.extractor.extract_from_array(cropped)
        
#     #     scores = {}
        
#     #     for product, embeddings in self.embedding_store.items():
            
#     #         similarities = []
            
#     #         for emb in embeddings:
#     #             sim = cosine_similarity(
#     #                 query_embedding.reshape(1, -1), 
#     #                 emb.reshape(1, -1)
#     #                 )[0][0]
                
#     #             similarities.append(sim)
            
#     #         scores[product] = max(similarities)
        
#     #     best_match = max(scores, key=scores.get)
        
#     #     return {
#     #         "product": best_match,
#     #         "similarity": float(scores[best_match])
        
#     #     }
        
        
        
        