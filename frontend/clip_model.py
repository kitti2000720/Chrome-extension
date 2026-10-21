import torch
import torch.nn.functional as F
import open_clip
from PIL import Image


class CLIPModel:
    def __init__(self):
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="openai"
        )
        self.tokenizer = open_clip.get_tokenizer("ViT-B-32")

    def classify(self, image_path):
        try:
            image = self.preprocess(Image.open(image_path)).unsqueeze(0)
            text = self.tokenizer([
                "bank login page",
                "normal website",
                "phishing website"
            ])

            with torch.no_grad():
                image_features = self.model.encode_image(image)
                text_features = self.model.encode_text(text)

            probs = (image_features @ text_features.T).softmax(dim=-1)

            return {
                "bank_login": probs[0][0].item(),
                "normal": probs[0][1].item(),
                "phishing": probs[0][2].item()
            }

        except Exception as e:
            return {
                "error": str(e),
                "bank_login": 0,
                "normal": 0,
                "phishing": 0
            }

    def _encode_pil(self, img: Image.Image) -> torch.Tensor:
        tensor = self.preprocess(img.convert("RGB")).unsqueeze(0)
        with torch.no_grad():
            feat = self.model.encode_image(tensor)
        return F.normalize(feat, dim=-1)

    def image_similarity(self, path1: str, path2: str) -> float:
        try:
            f1 = self._encode_pil(Image.open(path1))
            f2 = self._encode_pil(Image.open(path2))
            return float((f1 @ f2.T).item())
        except Exception:
            return 0.0

    def image_similarity_pil(self, img1: Image.Image, img2: Image.Image) -> float:
        try:
            f1 = self._encode_pil(img1)
            f2 = self._encode_pil(img2)
            return float((f1 @ f2.T).item())
        except Exception:
            return 0.0