from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import APIRouter
import csv

from models.main import Prompt
from models.main import VideoPath
import google.generativeai as genai
GOOGLE_API_KEY='AIzaSyC4GHf6eOoLbtne4dWMASheYvArnsXNedw'

genai.configure(api_key=GOOGLE_API_KEY)




def CsvtoStr(path:VideoPath):
    # Open the CSV file for reading
    with open(path, newline='') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)
        
        # Initialize an empty string to store the CSV data
        csv_data_string = ""
        
        # Iterate over each row in the CSV
        for row in csv_reader:
            # Convert the row to a string and append it to the csv_data_string
            # Here, we join each element in the row with a comma and add a newline at the end
            csv_data_string += ",".join(row) + "\n"

    # At this point, csv_data_string contains the data from the CSV file as a string
    return csv_data_string








async def chat_with_openai(prompt_data: Prompt):
    prompt=f"""I will give you data in form of csv file which have information of objects from YOLO processing
    and i want a string of a description of whole 
    scene. Give me scene description in one line. its for blind people.
    Create a detailed and vivid scene description for a blind person based on the information provided in a CSV file
    containing frame ID, class name, confidence level, and boundary box coordinates (x and y values) for objects detected
    in each frame of a video. The description should convey the spatial relationships between objects, their sizes,
    and any actions or movements they may be performing. 
    It should also provide context and help the listener visualize the scene as accurately as possible. it is view from mobile camera of the person. Also tell if he is going to hit something.
    Make it short.
    Here is csv data:{prompt_data}"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        # response = model.generate_content(prompt,stream=True)
      # Await the response coroutine
        response_stream = await model.generate_content_async(prompt, stream=True)

        # Ensure response_stream is an async iterable
        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text
        # return response.text
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
