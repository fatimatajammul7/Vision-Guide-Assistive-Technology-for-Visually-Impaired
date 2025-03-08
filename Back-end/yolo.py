
import pandas as pd

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
    
    
process_file('detections.csv')