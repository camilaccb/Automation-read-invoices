"""
Cenário: Extração do número da nota do documento
Entrada: caminho do arquivo no cloud storage (uri)
Resultado esperado Número da nota extraido com 44 dígitos
Elemento de teste: função detect text_uri
Saída: Tamanho da string extraida do documento 

"""

from pytest import mark
from src.gcp import detect_text_uri
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ServiceAccountToken.json"

uri1 = "gs://invoice-reader-documents/Invoice_f125e16c-e9ba-42c0-8907-4b0e9be9fde8.jpg"
uri2 = "gs://invoice-reader-documents/Invoice_f125e16c-e9ba-42c0-8907-4b0e9be9fde8.jpg"

@mark.parametrizado
@mark.parametrize(
        'entrada,esperado',
        [uri1,uri2]
)
def test_quando_numero_da_invoice_é_encontrado_invoice_tem_44_caracteres(entrada):
    #entrada = "gs://invoice-reader-documents/Invoice_f125e16c-e9ba-42c0-8907-4b0e9be9fde8.jpg" #dado
    #esperado = 44   #dado
    #resultado = len(detect_text_uri(entrada))   #quando 
    #assert esperado == resultado   #então
    
    #Test escrito em 1 linha (teste one step)
    assert len(detect_text_uri(entrada)) == 44

