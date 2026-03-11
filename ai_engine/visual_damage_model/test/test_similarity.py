from vision_engine.similarity.similarity_engine import SimilarityEngine

engine = SimilarityEngine("vision_engine/embeddings/reference_embeddings.pkl")

result = engine.compare("reference_dataset/Kelloggs_cornflakes_300g/front.jpg")

print(result)