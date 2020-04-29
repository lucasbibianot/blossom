import uuid
import shutil
import streamlit as st
import pandas as pd
import ler_pdf
import os


def cabecalho():
    st.title('Análise de avanço semanal')


def rodape():
    st.info('Blossom - Liliany Bibiano')


@st.cache
def construir_dataframe(file_v1, file_v2):
    df_1 = ler_pdf.carregar_dataframe(file_v1)
    df_2 = ler_pdf.carregar_dataframe(file_v2)
    df_2.columns = ['cod_tarefa', 'descricao_atual',
                    'start_atual', 'end_atual']
    df_join = df_1.set_index('cod_tarefa').join(df_2.set_index('cod_tarefa'))
    df_filtro = df_join[df_join['end_atual'] != df_join['end']]
    st.dataframe(df_filtro)


def sidebar_parametros():
    tmpdirname = f'/tmp/{uuid.uuid4()}'
    os.mkdir(tmpdirname)
    fp_v1 = f'{tmpdirname}/v1.pdf'
    fp_v2 = f'{tmpdirname}/v2.pdf'
    data_avanco = st.sidebar.date_input('Selecione a data de avanço')
    uploaded_v1 = st.sidebar.file_uploader(
        "Selecione o PDF inicial", type="pdf")
    if uploaded_v1 is not None:
        with open(fp_v1, 'wb') as writer:
            writer.write(uploaded_v1.read())
        uploaded_v2 = st.sidebar.file_uploader(
            "Selecione o PDF final", type="pdf")
        if uploaded_v2 is not None:
            with open(fp_v2, 'wb') as writer:
                writer.write(uploaded_v2.read())
                construir_dataframe(fp_v1, fp_v2)
    shutil.rmtree(tmpdirname)


def main():
    cabecalho()
    sidebar_parametros()
    rodape()


if __name__ == "__main__":
    main()
