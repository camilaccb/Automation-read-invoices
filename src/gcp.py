import re
from google.cloud import storage
from google.cloud import vision
from google.cloud import bigquery


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    #bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

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

    gcs_path = f"gs://{bucket_name}/{destination_blob_name}"
    return gcs_path


def detect_text_uri(uri):
    """Detects text in the file located in Google Cloud Storage or on the Web."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        reg_pattern =  '\d{44}|(\d{4}\s){11}'
        text_found = re.search(reg_pattern, text.description)

        if text_found != None:
            invoice_no = text_found.group().replace(" ", "")
            break
    
    print(invoice_no)
    return invoice_no

        #vertices = (['({},{})'.format(vertex.x, vertex.y)
                    #for vertex in text.bounding_poly.vertices])

        #print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    

def upload_data_bigquery(invoice_number, extraction_date, file_name, requester):
    """Stream data into big query"""
    
    # Construct a BigQuery client object.
    client = bigquery.Client()

    table_id = "invoice-reader-374817.invoice_data.EXTRACTED_DATA"

    rows_to_insert = [
        {"Extraction_date": extraction_date, "Requester": requester, "Invoice_number": invoice_number, "File":file_name}
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))