""" Execute actions in google cloud: upload file in cloud storage, detect text in document storaged and stream data extracted to BigQuery
    
    Functions:
    upload_blob(bucket_name:str, source_file_name:str, destination_blob_name:str) -> str
    detect_text_uri(uri:str) -> str
    upload_data_bigquery(invoice_number:str, extraction_date:str, file_name:str, requester:str)

"""

import re
from google.cloud import storage
from google.cloud import vision
from google.cloud import bigquery

def upload_blob(bucket_name:str, source_file_name:str, destination_blob_name:str) -> str:
    """ Uploads a file to the bucket

    Parameters:
    bucket_name (str): The ID of your GCS bucket
    source_file_name (str): The path to your file to upload
    destination_blob_name (str): The ID of your GCS object

    Returns:
    gcs_path (str): URI of document in clud storage

    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

    #Create cloud storage path (URI) to unput in the detect_text_uri function
    gcs_path = f"gs://{bucket_name}/{destination_blob_name}"
    return gcs_path

def detect_text_uri(uri:str) -> str:
    """Detects text in the file located in Google Cloud Storage"""
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    # For each text extracted apply the regex rule and try to find the invoice number 
    for text in texts:
        print('\n"{}"'.format(text.description))
        
        #Apply regex rule in the text extracted to found invoice number
        reg_pattern =  '\d{44}|(\d{4}\s){11}'
        text_found = re.search(reg_pattern, text.description)

        # Stop after found the text
        if text_found != None:
            invoice_no = text_found.group().replace(" ", "")
            break
    
    print(invoice_no)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    
    return invoice_no 

def upload_data_bigquery(invoice_number:str, extraction_date:str, file_name:str, requester:str):
    """Stream extracted data into big query"""
    
    # Construct a BigQuery client object.
    client = bigquery.Client()

    # Assign the table id that has the following structure "project-name.dataset-name.table-name"
    table_id = "invoice-reader-374817.invoice_data.EXTRACTED_DATA"

    # Define row to insert. The dictionary key is the column name of table schema in bigquery
    rows_to_insert = [
        {"Extraction_date": extraction_date, "Requester": requester, "Invoice_number": invoice_number, "File":file_name}
    ]

    # Make an API request.
    errors = client.insert_rows_json(table_id, rows_to_insert)  
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))




   