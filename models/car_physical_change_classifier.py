import io
import os
import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms, models

from config import settings


class CarPhysicalChangeClassifier:
    def __init__(self, model_path = None):
        self.MODEL_WEIGHTS_PATH = model_path or settings.CLASSIFIER_MODEL_PATH

        self.IMG_HEIGHT = 320
        self.IMG_WIDTH = 320
        self.NUM_COMPONENTS = 5
        self.COMPONENT_NAMES = [
            "front_left",
            "front_right",
            "rear_left",
            "rear_right",
            "hood"
        ]

        if not os.path.exists(self.MODEL_WEIGHTS_PATH):
            raise Exception(f"ERROR: Model weights not found at {self.MODEL_WEIGHTS_PATH}")


        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        self.inference_model = None

        self.eval_transforms = transforms.Compose([
            transforms.Resize((self.IMG_HEIGHT, self.IMG_WIDTH)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])


    def load_model(self):
        inference_model = models.efficientnet_b3(weights=None)

        features_number = inference_model.classifier[1].in_features
        inference_model.classifier[1] = nn.Linear(features_number, self.NUM_COMPONENTS)

        if os.path.exists(self.MODEL_WEIGHTS_PATH):
            try:
                inference_model.load_state_dict(torch.load(self.MODEL_WEIGHTS_PATH, map_location=self.device))
                print(f"Model weights loaded successfully from {self.MODEL_WEIGHTS_PATH}")
            except Exception as e:
                raise Exception(f"Error loading model weights: {e}")
        else:
            raise Exception(f"Error loading model weights: {e}")

        self.inference_model = inference_model.to(self.device)
        self.inference_model.eval()
        print("Model is in evaluation mode.")


    def preprocess_image(self, image_path):
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.eval_transforms(image)
            return image_tensor.unsqueeze(0)
        except FileNotFoundError:
            print(f"Error: Image not found at {image_path}")
            return None
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None

    def preprocess_image_bytes(self, image_bytes: bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return self.eval_transforms(image).unsqueeze(0)  # Add batch dimension
        except Exception as e:
            raise ValueError(f"Invalid image file or error during preprocessing: {e}")


    def predict_image(self, image_tensor):
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            outputs = self.inference_model(image_tensor)

            probabilities = torch.sigmoid(outputs)

            predictions_binary = (probabilities > 0.5).float()

            predictions_binary_np = predictions_binary.cpu().numpy().squeeze()
            probabilities_np = probabilities.cpu().numpy().squeeze()

            results = {}
            print("\n--- Predictions ---")
            for i, name in enumerate(self.COMPONENT_NAMES):
                state = "Open" if predictions_binary_np[i] == 1 else "Closed"
                probability = probabilities_np[i]
                results[name] = {'state': state, 'confidence_open': float(probability)}
                print(f"{name}: {state} (Confidence for 'Open': {probability:.4f})")
            return results


if __name__ == '__main__':
    model = CarPhysicalChangeClassifier(model_path='checkpoints/efficientnet_b3_multilabel_best.pth')
    model.load_model()

    TEST_IMAGE_PATH = 'datasets/test.png'
    input_tensor = model.preprocess_image(TEST_IMAGE_PATH)
    predictions = model.predict_image(input_tensor)

    print("FINISH...")
    print(predictions)

