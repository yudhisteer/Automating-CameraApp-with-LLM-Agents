import logging
import os
import base64
import cv2
import pandas as pd
from datetime import datetime
from openai import OpenAI
from pydantic import BaseModel, Field
import time

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


# Function to encode an image as base64
def encode_image_from_array(image_array):
    """Convert a numpy array to base64 encoded image"""
    success, encoded_image = cv2.imencode('.jpg', image_array)
    if not success:
        raise ValueError("Could not encode image")
    return base64.b64encode(encoded_image.tobytes()).decode('utf-8')


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


def process_video(video_path, sample_rate=1, output_dir=None):
    """
    Process a video file for anomaly detection
    
    Args:
        video_path: Path to the video file
        sample_rate: Process every Nth frame (default: 1, process every frame)
        output_dir: Directory to save results (default: None, don't save frames)
    
    Returns:
        DataFrame with anomaly detection results
    """
    # Create output directory if specified
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    logger.info(f"Video loaded: {video_path}")
    logger.info(f"FPS: {fps}, Total Frames: {frame_count}, Duration: {duration:.2f}s")
    logger.info(f"Processing every {sample_rate} frame(s)")
    
    # Initialize results storage
    results = []
    
    frame_index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video
        
        # Only process every Nth frame
        if frame_index % sample_rate == 0:
            # Calculate timestamp
            timestamp = frame_index / fps
            
            # Convert frame to base64
            try:
                base64_image = encode_image_from_array(frame)
                
                # Save frame if output directory is specified
                if output_dir:
                    frame_filename = os.path.join(output_dir, f"frame_{frame_index:06d}.jpg")
                    cv2.imwrite(frame_filename, frame)
                
                # Detect anomaly
                logger.info(f"Processing frame {frame_index} at {timestamp:.2f}s")
                
                # Add delay to avoid rate limiting if needed
                time.sleep(0.1)
                
                result = detect_anomaly(base64_image)
                
                # Store results
                results.append({
                    "frame_index": frame_index,
                    "timestamp": timestamp,
                    "is_anomaly": result.is_anomaly,
                    "confidence_score": result.confidence_score
                })
                
            except Exception as e:
                logger.error(f"Error processing frame {frame_index}: {str(e)}")
        
        frame_index += 1
    
    # Release video capture
    cap.release()
    
    # Convert results to DataFrame
    df_results = pd.DataFrame(results)
    
    # Save results to CSV
    if output_dir:
        csv_path = os.path.join(output_dir, "anomaly_results.csv")
        df_results.to_csv(csv_path, index=False)
        logger.info(f"Results saved to {csv_path}")
    
    return df_results


if __name__ == "__main__":
    video_path = r"C:\Users\sfudally\Desktop\__Projects__\Automating-CameraApp-with-Vision-Language-Action-model\data\videos\bug_1.mp4"
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", f"video_analysis_{timestamp}")
    
    # Process every 5th frame to reduce API calls (adjust as needed)
    results_df = process_video(video_path, sample_rate=5, output_dir=output_dir)
    
    # Display summary of results
    print("\nAnalysis Summary:")
    print(f"Total frames processed: {len(results_df)}")
    print(f"Anomalies detected: {results_df['is_anomaly'].sum()}")
    print(f"Average confidence score: {results_df['confidence_score'].mean():.4f}")
    
    # Find frames with highest anomaly confidence
    if results_df['is_anomaly'].any():
        max_conf_row = results_df[results_df['is_anomaly']].sort_values(by='confidence_score', ascending=False).iloc[0]
        print(f"\nHighest confidence anomaly at frame {max_conf_row['frame_index']} (time: {max_conf_row['timestamp']:.2f}s)")
        print(f"Confidence score: {max_conf_row['confidence_score']:.4f}")