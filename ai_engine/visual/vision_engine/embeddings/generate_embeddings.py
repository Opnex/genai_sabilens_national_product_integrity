"""
Generates reference embeddings for the SimilarityEngine.

IMPROVEMENTS OVER ORIGINAL:
  1. L2-normalises every embedding before saving - this makes cosine similarity
     more discriminative. Without normalisation, magnitude differences dominate
     and all scores cluster around 0.2.
  2. Stores ONLY front.jpg as the primary embedding per product.
     Back/side/top views confuse the matcher when query is always a front scan.
     All views are stored as secondary - primary is always compared first.
  3. Prints a similarity sanity check after building  each product's front.jpg
     should score >= 0.85 against its own embedding. If it doesn't, the extractor
     is not discriminative enough for that product.

USAGE:
    python generate_embeddings.py

OUTPUT:
    vision_engine/embeddings/reference_embeddings.pkl
"""

import os
import pickle
import numpy as np
from vision_engine.models.feature_extractor import FeatureExtractor
from sklearn.metrics.pairwise import cosine_similarity

DATASET_PATH = "reference_dataset"
OUTPUT_PATH  = "vision_engine/embeddings/reference_embeddings.pkl"
PRIMARY_VIEW = "front.jpg"   # Always compared frst and must exist in every product folder


def l2_normalise(vec: np.ndarray) -> np.ndarray:
    """L2-normalise a vector. Makes cosine similarity purely angle-based."""
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def main():
    extractor      = FeatureExtractor()
    embedding_store = {}
    missing_fronts  = []

    print(f"\nBuilding embeddings from: {DATASET_PATH}\n")

    for product in sorted(os.listdir(DATASET_PATH)):
        product_path = os.path.join(DATASET_PATH, product)
        if not os.path.isdir(product_path):
            continue

        images = os.listdir(product_path)
        embedding_store[product] = []

        # Always extract front.jpg first if it exists
        front_path = os.path.join(product_path, PRIMARY_VIEW)
        if os.path.exists(front_path):
            emb = l2_normalise(extractor.extract(front_path))
            embedding_store[product].append(emb)
            print(f"{product}  front.jpg extracted")
        else:
            missing_fronts.append(product)
            print(f"{product} : no front.jpg found, using all views")

        # Add remaining views as secondary embeddings
        for image_file in images:
            if image_file == PRIMARY_VIEW:
                continue   # already added above
            image_path = os.path.join(product_path, image_file)
            if not image_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            emb = l2_normalise(extractor.extract(image_path))
            embedding_store[product].append(emb)

    # Save
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(embedding_store, f)

    print(f"\nEmbeddings saved to {OUTPUT_PATH}")
    print(f"   Products: {len(embedding_store)}")
    print(f"   Total embeddings: {sum(len(v) for v in embedding_store.values())}")

    if missing_fronts:
        print(f"\nProducts missing front.jpg: {missing_fronts}")
        print("   Add front.jpg to these folders for best matching accuracy.")

    # Sanity check, each product's front.jpg vs its own embedding
    print("\nSelf-similarity sanity check (should all be >= 0.85)")
    low_scores = []

    for product in sorted(embedding_store.keys()):
        front_path = os.path.join(DATASET_PATH, product, PRIMARY_VIEW)
        if not os.path.exists(front_path):
            continue

        query = l2_normalise(extractor.extract(front_path))
        scores = [
            cosine_similarity(query.reshape(1, -1), emb.reshape(1, -1))[0][0]
            for emb in embedding_store[product]
        ]
        best = max(scores)
        status = "OK" if best >= 0.85 else "WARNING"
        print(f"  {status} {product}: {best:.4f}")
        if best < 0.85:
            low_scores.append((product, best))

    if low_scores:
        print(f"\nLow self-similarity products: {low_scores}")
        print("   These products may match poorly in production.")
        print("   Consider adding more/better reference images.")
    else:
        print("\nAll products pass self-similarity check.")


if __name__ == "__main__":
    main()




# import os
# import pickle
# from vision_engine.models.feature_extractor import FeatureExtractor

# Dataset_path = "reference_dataset"
# output_path = "vision_engine/embeddings/reference_embeddings.pkl"

# extractor = FeatureExtractor()

# embedding_store = {}

# for product in os.listdir(Dataset_path):
    
#     product_path = os.path.join(Dataset_path, product)
    
#     if not os.path.isdir(product_path):
#         continue
    
#     embedding_store[product] = []
    
#     for image in os.listdir(product_path):
        
#         image_path = os.path.join(product_path, image)
        
#         embedding = extractor.extract(image_path)
        
#         embedding_store[product].append(embedding)
        
# with open(output_path, 'wb') as f:
#     pickle.dump(embedding_store, f)
    
# print("Reference embeddings generated and saved to", output_path)