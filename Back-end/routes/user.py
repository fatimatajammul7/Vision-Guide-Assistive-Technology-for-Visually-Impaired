import string
from fastapi import APIRouter, Depends, Request, Header,Security,HTTPException
from typing import Annotated

from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
import httpx
import asyncio
import os
import cv2
import csv
from ultralytics import YOLO  
import pandas as pd
import math
from models.main import VideoPath
from routes.llm import CsvtoStr, chat_with_openai
from routes.bard import generate_caption_blip
# import function from llm.py
import sys

router = APIRouter(
    prefix='/user',
    tags=['User']
)


VIDEO_DIR = "videos"
if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

import math
from typing import List, Tuple

# Define a structure for the detected objects
class DetectedObject:
    def __init__(self, frame_id: int, class_name: str, confidence: float, x: float, y: float, width: float, height: float):
        self.frame_id = frame_id
        self.class_name = class_name
        self.confidence = confidence
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self):
        """Calculate the center coordinates of the bounding box"""
        center_x = self.x
        center_y = self.y
        return (center_x, center_y)

# Assuming we have the following camera parameters
FOCAL_LENGTH = 700  # in pixels
KNOWN_WIDTH = 0.5  # known width of the object in meters, for example, a standard size for a person

def calculate_distance_to_object(detected_object: DetectedObject) -> float:
    """
    Estimate the distance from the camera to the object using the bounding box width.
    Uses the pinhole camera model: distance = (known width * focal length) / perceived width
    """
    perceived_width = detected_object.width
    distance = (KNOWN_WIDTH * FOCAL_LENGTH) / perceived_width
    return distance

def process_detected_objects(detected_objects: List[DetectedObject]) -> List[Tuple[int, str, float]]:
    """
    Process a list of detected objects and calculate the distance to each object.
    Returns a list of tuples with (frame_id, class_name, distance).
    """
    results = []
    for obj in detected_objects:
        distance = calculate_distance_to_object(obj)
        results.append((obj.frame_id, obj.class_name, distance))
    return results

# Example usage
detected_objects = [
    DetectedObject(frame_id=1, class_name='person', confidence=0.98, x=100, y=150, width=50, height=100),
    DetectedObject(frame_id=1, class_name='dog', confidence=0.95, x=200, y=250, width=60, height=120),
]

distances = process_detected_objects(detected_objects)
for dist in distances:
    print(f"Distance to {dist[1]} in frame {dist[0]}: {dist[2]:.2f} meters")


async def download_video(url: str, file_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
        else:
            raise HTTPException(status_code=400, detail="Error downloading video")




async def process_video(video_path: str):
    model = YOLO("yolo-Weights\yolov8n-oiv7.pt")
    cap = cv2.VideoCapture(video_path)
     # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(total_frames)
    print(video_path)
    frame_results = []
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, stream=True)

        for r in results:
            boxes = r.boxes

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # Convert to int
                confidence = math.ceil((box.conf[0]*100))/100
                class_name = model.names[box.cls[0].item()]

                frame_results.append({
                    'frame_id': frame_id,
                    'class': class_name,
                    'confidence': confidence,
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                })

            frame_id += 1

    cap.release()

    df = pd.DataFrame(frame_results)
    csv_path = 'detections.csv'  # Consider generating a unique file name
    df.to_csv(csv_path, index=False)
    return csv_path

def process_file(filePath):
    # Load the data from the CSV file
    data = pd.read_csv(filePath)

    # Sort the data based on frame id, class name, and confidence score in descending order
    data = data.sort_values(['frame_id', 'class', 'confidence'], ascending=[True, True, False])

    # Iterate through the sorted data and compare the current row with the previous row
    prev_row = None
    for i, row in data.iterrows():
        if prev_row is not None and prev_row['frame_id'] == row['frame_id'] and prev_row['class'] == row['class']:
            # If the frame id and class name are the same, then compare the confidence score and bounding box coordinates
            if prev_row['confidence'] == row['confidence']:
                # If the confidence score is the same, then keep the row with the largest bounding box
                if (row['x2'] - row['x1']) * (row['y2'] - row['y1']) > (prev_row['x2'] - prev_row['x1']) * (prev_row['y2'] - prev_row['y1']):
                    prev_row = row
            else:
                # If the confidence score is different, then keep both rows
                prev_row = row
        else:
            prev_row = row

    # Remove any duplicate rows based on frame id and class name
    data = data.drop_duplicates(['frame_id', 'class'])
    data.to_csv(filePath, index=False)
    print(data)

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized_filename = ''.join(c if c in valid_chars else '_' for c in filename)
    return sanitized_filename



async def stream_chat_with_openai(prompt_data: str):
    async for chunk in chat_with_openai(prompt_data):
        yield chunk
@router.post("/download/")
async def download_video_endpoint(url: str):
    filename = url.split("/")[-1]  # Simplistic way to name files
    
    sanitized_filename = sanitize_filename(filename)
    file_path = os.path.join(VIDEO_DIR, sanitized_filename)

    await download_video(url, file_path)
    
    try:
        csv_path = await process_video(file_path)
        
        detections=CsvtoStr(csv_path)
        # Stream the response using StreamingResponse
        return StreamingResponse(stream_chat_with_openai(detections), media_type="text/plain")
        # return {"message": "Success", "caption": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/blip/")
async def download_video_endpoint(url: str):
    filename = url.split("/")[-1]  # Simplistic way to name files
    
    sanitized_filename = sanitize_filename(filename)
    file_path = os.path.join(VIDEO_DIR, sanitized_filename)

    await download_video(url, file_path)
    
    try:
        # csv_path = await process_video(file_path)
        response=generate_caption_blip(file_path)
        return {"message": "Success", "caption": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

