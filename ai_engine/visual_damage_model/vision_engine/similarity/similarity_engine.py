import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from vision_engine.models.feature_extractor import FeatureExtractor
from vision_engine.regions.region_cropper import RegionCropper

class SimilarityEngine:
    def __init__(self, embedding_path):
        self.cropper = RegionCropper()
        
        with open(embedding_path, 'rb') as f:
            self.embedding_store = pickle.load(f)
        
        print("Loaded products:", self.embedding_store.keys())
        
        self.extractor = FeatureExtractor()

    def compare(self, image_path):
        
        cropped = self.cropper.crop_center(image_path)
        
        query_embedding = self.extractor.extract_from_array(cropped)
        
        scores = {}
        
        for product, embeddings in self.embedding_store.items():
            
            similarities = []
            
            for emb in embeddings:
                sim = cosine_similarity(
                    query_embedding.reshape(1, -1), 
                    emb.reshape(1, -1)
                    )[0][0]
                
                similarities.append(sim)
            
            scores[product] = max(similarities)
        
        best_match = max(scores, key=scores.get)
        
        return {
            "product": best_match,
            "similarity": float(scores[best_match])
        
        }
        
        
        
        