from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import APIRouter


import requests
import cv2
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


import torch


# Load the processor and the model from the Hugging Face hub
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# Function to generate caption for a given frame
def generate_caption(frame, model, processor, text=None):
    
    
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if text:
        inputs = processor(image, text, return_tensors="pt")
    else:
        inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

# Open the video file
# video_path = "C:/Users/fatim/Desktop/Semester_work/FYPbackend/fypProject/fypBackend/videos/videos_2F1711504783784.mp4_alt_media_token_9c8cf9be-1551-490e-a635-fb7cfbe02bf2"  # Replace with your video path


def generate_caption_blip(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(frame_rate)  # Process one frame per second
    print(frame_rate)
    frame_count = 0
    captions = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            # Generate caption for the current frame
            caption = generate_caption(frame, model, processor)
            captions.append(caption)
            # print(f"Frame {frame_count}: {caption}")

        frame_count += 1

    cap.release()
    return captions[-1]


# Print all captions (optional)
# for i, caption in enumerate(captions):
#     print(f"Caption for frame {i * frame_interval}: {caption}")

