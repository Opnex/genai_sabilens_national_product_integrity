import pickle

with open("vision_engine/embeddings/reference_embeddings.pkl", 'rb') as f:
    data = pickle.load(f)
    
print("Products in embedding database:")
print(list(data.keys()))

for product, embeddings in data.items():
    print(f"{product}: {len(embeddings)} images")