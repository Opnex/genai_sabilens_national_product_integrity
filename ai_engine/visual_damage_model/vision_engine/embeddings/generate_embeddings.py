import os
import pickle
from vision_engine.models.feature_extractor import FeatureExtractor

Dataset_path = "reference_dataset"
output_path = "vision_engine/embeddings/reference_embeddings.pkl"

extractor = FeatureExtractor()

embedding_store = {}

for product in os.listdir(Dataset_path):
    
    product_path = os.path.join(Dataset_path, product)
    
    if not os.path.isdir(product_path):
        continue
    
    embedding_store[product] = []
    
    for image in os.listdir(product_path):
        
        image_path = os.path.join(product_path, image)
        
        embedding = extractor.extract(image_path)
        
        embedding_store[product].append(embedding)
        
with open(output_path, 'wb') as f:
    pickle.dump(embedding_store, f)
    
print("Reference embeddings generated and saved to", output_path)