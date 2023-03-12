import os
import io 
import re
from google.cloud import vision


# Google authentication using a service account file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ServiceAccountToken.json"

client = vision.ImageAnnotatorClient()

FILE_NAME = '1.JPEG'
FOLDER_PATH = 'Documents_test/New'
#FOLDER_PATH = 'Documents_test/Success'

with io.open(f'{FOLDER_PATH}/{FILE_NAME}','rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)
response = client.text_detection(image=image)
response_json = response.text_annotations

with io.open(f'{FOLDER_PATH}/Extraction.txt','w',encoding="utf-8") as extracted_data:
    extracted_data.write(response_json[0].description)

with io.open(f'{FOLDER_PATH}/Extraction.txt','r', encoding="utf-8") as extracted_data:
    extracted_text = extracted_data.read()

#regex_pattern =  '\d{44}|\n(\d{1,4}\s){10}\d{1,4}'
regex_pattern =  '\d{44}|(?<!.)(\d{1,4}\s){10}\d{1,4}'
text_found = re.search(regex_pattern, extracted_text)
print(text_found.group())
formated_text_found = text_found.group().strip().replace(" ", "")
print(formated_text_found)
print(len(formated_text_found))





   
