import logging
import os
import base64
from datetime import datetime
from openai import OpenAI
from pydantic import BaseModel, Field

# https://platform.openai.com/docs/guides/vision

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o-mini"

class AnomalyDetection(BaseModel):
    """First LLM call: Generate a confidence score for the anomaly detection"""
    is_anomaly: bool = Field(description="True if the image is an anomaly, False otherwise")
    confidence_score: float = Field(description="Confidence score between 0 and 1 that it is an anomaly")



# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def detect_anomaly(base64_image):
    """First LLM call to determine if input is an anomaly"""
    logger.info("Starting anomaly detection analysis")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You a Test Engineer checking Camera App on Windows.",
            },
            {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Is there any issue in this image?",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
        ],
        response_format=AnomalyDetection,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Anomaly detection complete - Is anomaly: {result.is_anomaly}, Confidence: {result.confidence_score:.2f}"
    )
    return result


if __name__ == "__main__":
    image_path = r"C:\Users\sfudally\Desktop\__Projects__\Automating-CameraApp-with-Vision-Language-Action-model\data\images\bug_1.png"
    base64_image  = encode_image(image_path)

    result = detect_anomaly(base64_image)
    print(result)

