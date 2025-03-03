import os
import base64
import cv2
import numpy as np
import pandas as pd
import time
import gradio as gr
import matplotlib.pyplot as plt
from openai import OpenAI
from pydantic import BaseModel, Field
import logging
import tempfile

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o-mini"

class AnomalyDetection(BaseModel):
    """Generate a confidence score for the anomaly detection"""
    is_anomaly: bool = Field(description="True if the image is an anomaly, False otherwise")
    confidence_score: float = Field(description="Confidence score between 0 and 1 representing likelihood of anomaly")

def encode_image_from_array(image_array):
    """Convert a numpy array to base64 encoded image"""
    success, encoded_image = cv2.imencode('.jpg', image_array)
    if not success:
        raise ValueError("Could not encode image")
    return base64.b64encode(encoded_image.tobytes()).decode('utf-8')

def detect_anomaly(frame):
    """Determine if the frame contains an anomaly"""
    base64_image = encode_image_from_array(frame)
    
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a Test Engineer checking Camera App on Windows. When analyzing images, provide: 1) whether there is an issue/anomaly (true/false) and 2) a confidence score that represents the LIKELIHOOD OF AN ANOMALY being present (where 0 = definitely no anomaly, 1 = definitely an anomaly).",
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

def process_video(video_path, progress=gr.Progress()):
    """Process video for anomalies and return results dataframe"""
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
    
    # For MVP, process every 10th frame to reduce API calls
    sample_rate = 30
    logger.info(f"Processing every {sample_rate} frame(s)")
    
    # Initialize results storage
    results = []
    
    frame_index = 0
    
    # Create progress bar
    progress(0, desc="Analyzing video...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video
        
        # Only process every Nth frame
        if frame_index % sample_rate == 0:
            # Calculate timestamp
            timestamp = frame_index / fps
            
            try:
                # Update progress
                progress_value = frame_index / frame_count
                progress(progress_value, desc=f"Analyzing frame {frame_index}/{frame_count}")
                
                # Detect anomaly
                result = detect_anomaly(frame)
                
                # Store results
                results.append({
                    "frame_index": frame_index,
                    "timestamp": timestamp,
                    "is_anomaly": result.is_anomaly,
                    "confidence_score": result.confidence_score
                })
                
                # Add delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing frame {frame_index}: {str(e)}")
        
        frame_index += 1
    
    # Release video capture
    cap.release()
    
    # Convert results to DataFrame
    df_results = pd.DataFrame(results)
    
    # Compute progress complete
    progress(1.0, desc="Analysis complete!")
    
    return df_results, video_path

def create_plot(df_results):
    """Create a plot of anomaly confidence scores over time"""
    plt.figure(figsize=(10, 4))
    plt.plot(df_results['timestamp'], df_results['confidence_score'], 'r-')
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    plt.fill_between(df_results['timestamp'], df_results['confidence_score'], alpha=0.3, color='red')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Anomaly Confidence Score')
    plt.title('Video Anomaly Detection Results')
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    
    # Create a temporary file to save the plot
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        plt.savefig(temp_file.name, bbox_inches='tight')
        plt.close()
        return temp_file.name

def analyze_video(video_file, progress=gr.Progress()):
    """Main function to process video and generate outputs for Gradio"""
    if video_file is None:
        return None, None, None
    
    # Process the video
    df_results, video_path = process_video(video_file, progress)
    
    # Create the confidence score plot
    plot_path = create_plot(df_results)
    
    # Generate summary text
    anomaly_count = df_results['is_anomaly'].sum()
    max_confidence = df_results['confidence_score'].max()
    avg_confidence = df_results['confidence_score'].mean()
    
    if anomaly_count > 0:
        max_conf_row = df_results[df_results['is_anomaly']].sort_values(
            by='confidence_score', ascending=False
        ).iloc[0]
        max_time = max_conf_row['timestamp']
        summary = f"Analysis complete! Found {anomaly_count} potential anomalies.\n"
        summary += f"Highest confidence: {max_confidence:.2f} at {max_time:.2f} seconds.\n"
        summary += f"Average confidence score: {avg_confidence:.2f}"
    else:
        summary = f"Analysis complete! No anomalies detected.\n"
        summary += f"Maximum confidence score: {max_confidence:.2f}\n"
        summary += f"Average confidence score: {avg_confidence:.2f}"
    
    return plot_path, summary

# Create the Gradio interface
with gr.Blocks(title="Camera App Anomaly Detector") as app:
    gr.Markdown("## Camera App Anomaly Detector")
    gr.Markdown("Upload a video to analyze for anomalies.")
    
    with gr.Row():
        video_input = gr.Video(label="Upload Video", width=400, height=400)
    
    with gr.Row():
        analyze_button = gr.Button("Analyze Video")
    
    with gr.Row():
        # with gr.Column():
        #     video_output = gr.Video(label="Video")
        with gr.Column():
            plot_output = gr.Image(label="Anomaly Confidence Over Time")
    
    with gr.Row():
        summary_output = gr.Textbox(label="Analysis Summary")
    
    analyze_button.click(
        fn=analyze_video,
        inputs=[video_input],
        outputs=[plot_output, summary_output]
    )

# Launch the app
if __name__ == "__main__":
    app.launch()