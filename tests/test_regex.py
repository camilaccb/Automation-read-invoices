from src.gcp import detect_text_uri
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ServiceAccountToken.json"

def test_quando_numero_da_invoice_é_encontrado_invoice_tem_44_caracteres():
    entrada = "gs://invoice-reader-documents/Invoice_f125e16c-e9ba-42c0-8907-4b0e9be9fde8.jpg" #dado
    esperado = 44   #dado
    resultado = len(detect_text_uri(entrada))   #quando 
    assert esperado == resultado   #então
    
    #Test escrito em 1 linha
    #assert len(detect_text_uri(gs://invoice-reader-documents/Invoice_f125e16c-e9ba-42c0-8907-4b0e9be9fde8.jpg) == 44