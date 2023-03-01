#import pathlib
#p = pathlib.Path(__file__).absolute().parents[1] #root folder, p/"Documents
#print (p)

import re

texto = "Valor aproximado dos tributos deste cupom R$ (conforme Lei Fed 12. 741/2012) 2322 1247 5084 1103 4999 5923 0027 5390 0881 0358 8298 Consumidor 2322 1247 5084 1103 4999 5923 0027 5390 0881 0358 8299,"
reg_pattern =  '\d{44}|(\d{4}\s){11}'
texto_encontrado = re.search(reg_pattern, texto)

print(texto_encontrado.group())


#44
# (\d{4}\s){11}
# \d{44}
#\d{44}|(\d{4}\s){11}






