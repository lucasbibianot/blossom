import re
import json
import textract
import PyPDF2
import pandas as pd
import numpy as np
import datetime


def date_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def parser_texto(text_p, pagina, total_pagina, start=0):
    if pagina > total_pagina:
        return ''
    texto = text_p[start::]
    match_s = re.search(r'Duration[^.]', texto)
    match_e = re.search(r'© Oracle Corporation[^.]', texto)
    texto_pagina = texto[match_s.end():match_e.start()-1:]
    return texto_pagina + parser_texto(text_p, pagina+1, total_pagina, match_e.end())


def tratar_retorno(linha):
    datas = re.findall(r'[\d]{1,2}/[\d]{1,2}/[\d]{1,2}', linha)
    data = re.search(r'[\d]{1,2}/[\d]{1,2}/[\d]{1,2}', linha)
    percent = re.search(r'% ', linha[data.end()::])
    percent_fim = re.search(r'%', linha[data.end()+percent.end()::])    
    percent_conclusao = linha[percent.end()+data.end():percent.end()+data.end()+percent_fim.end():]
    cod_tarefa = re.search(r'[A-Z]{0,1}[\d]+', linha)
    descricao = linha[cod_tarefa.end():data.start():]
    start_d = np.datetime64(datetime.datetime.strptime(datas[0], '%d/%m/%y'))
    end_d = np.datetime64(datetime.datetime.strptime(datas[0], '%d/%m/%y'))
    if len(datas) > 1:
        end_d = np.datetime64(datetime.datetime.strptime(datas[1], '%d/%m/%y'))
    return {"cod_tarefa": str(cod_tarefa.group()), "descricao": descricao, "start": start_d, "end": end_d, "conclusao": percent_conclusao}


def carregar_dataframe(nom_arquivo, encoding='UTF-8'):
    with open(f'{nom_arquivo}', 'rb') as arquivo:
        text = textract.process(f'{nom_arquivo}', method='tesseract')
        texto = text.decode(encoding)
        pdf_reader = PyPDF2.PdfFileReader(arquivo)
        retorno = parser_texto(texto, 1, pdf_reader.numPages)
        linhas = re.findall(r'\n[A-Z]{0,1}[\d]+.+', retorno)
        df = pd.DataFrame([tratar_retorno(linha) for linha in linhas])
        return df


if __name__ == "__main__":
    nom_arquivo = r'/media/lucas/DADOS/Downloads/PDFs/033-18n.pdf'
    text = textract.process(f'{nom_arquivo}', method='tesseract')
    texto = text.decode('UTF-8')
    pdf_reader = PyPDF2.PdfFileReader(nom_arquivo)
    retorno = parser_texto(texto, 1, pdf_reader.numPages)
    linhas = re.findall(r'\n[A-Z]{0,1}[\d]+.+', retorno)
    linhas_filtro = [tratar_retorno(linha) for linha in linhas]
    with open('result.txt', 'w') as arq:
        arq.writelines('['+','.join([json.dumps(linha, default=date_converter)
                                     for linha in linhas_filtro])+']')
