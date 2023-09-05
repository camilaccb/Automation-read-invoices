"""
Cenário: Envio do documento para o cloud storage
Entrada: caminho local do arquivo baixado, nome do bucket de destino e nome do arquivo de destino
Resultado esperado Número da nota extraido com 44 dígitos
Elemento de teste: função upload_blob
Saída: caminho do arquivo no cloud storage (URI) 

"""

from pytest import mark
from src.gcp import upload_blob
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ServiceAccountToken.json"

bucket_name = "invoice-reader-documents"
source_file_name = "Documents/test_unitario1"
destination_blob_name = "gs://invoice-reader-documents/"
esperado = f"gs://{bucket_name}/{destination_blob_name}"

@mark.upload

def test_quando_upload_é_realizado_caminho_do_gcp_é_igual_a_destination_blob_name(entrada):
    assert upload_blob(bucket_name,source_file_name,destination_blob_name) == esperado
