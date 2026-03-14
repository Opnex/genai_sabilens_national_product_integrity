import torch
import numpy as np
from torchvision.models import resnet50, ResNet50_Weights
import torchvision.transforms as transforms
from PIL import Image

MODEL = None

class FeatureExtractor:
    def __init__(self):
        
        global  MODEL
        
        if MODEL is None:

            model =  model =resnet50(weights=ResNet50_Weights.DEFAULT)

            model = torch.nn.Sequential(*list(model.children())[:-1])

            model.eval()

            MODEL = model

        self.model = MODEL
        
        # Define a transformation pipeline for the input images
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]),
        ])
        
    def extract(self, image_path):
        # Load the image
        image = Image.open(image_path).convert('RGB')
        # Apply the transformations
        image = self.transform(image).unsqueeze(0)  # Add batch dimension

        with torch.no_grad():  # Disable gradient calculation
            features = self.model(image)  # Extract features

        return features.flatten().numpy()  # Return as a numpy array
    
    def extract_from_array(self, img_array):

        img = Image.fromarray(img_array)

        img = self.transform(img).unsqueeze(0)

        with torch.no_grad():
            features = self.model(img)

        return features.flatten().numpy()