import io

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

from config import settings


class CarPhysicalChangeExplainer:
    def __init__(self):
        self.processor = None
        self.model = None
        self.device = "cpu"

    def load_model(self):
        self.processor = BlipProcessor.from_pretrained(settings.EXPLAINER_MODEL_HF)
        self.model = BlipForConditionalGeneration.from_pretrained(settings.EXPLAINER_MODEL_HF)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def preprocess_image_bytes(self, image_bytes: bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return self.processor(image, return_tensors="pt").to(self.device)
        except Exception as e:
            raise ValueError(f"Invalid image file or error during preprocessing: {e}")

    def completions(self, input_processor):
        # Generate caption
        with torch.no_grad():
            out = self.model.generate(**input_processor, max_length=50, num_beams=4)

        return self.processor.decode(out[0], skip_special_tokens=True)


