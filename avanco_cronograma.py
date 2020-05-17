import uuid
import time
import shutil
import streamlit as st
import pandas as pd
import numpy as np
import ler_pdf
import os


def cabecalho():
    st.title('Análise de avanço semanal')


def rodape():
    st.info('Liliany Bibiano')


@st.cache
def carregar_cronograma(file_v1, file_v2):
    df_1 = ler_pdf.carregar_dataframe(file_v1)
    df_2 = ler_pdf.carregar_dataframe(file_v2)
    df_2.columns = ['cod_tarefa', 'descricao_atual',
                    'start_atual', 'end_atual', 'perc']
    df_2 = df_2[df_2['perc']!= '100%']
    return df_1.set_index('cod_tarefa').join(df_2.set_index('cod_tarefa'))


def calcular_dias(row):
    if pd.notna(row['end_atual']):
        row['qtde_dias'] = np.timedelta64(row['end_atual'] - row['end'])
        row['percentual_impacto'] = (row['qtde_dias'] / np.timedelta64(7, 'D'))
    else:
        row['qtde_dias'] = 0
        row['percentual_impacto'] = 0
    return row


def tratamento_dados(df_join):
    df_filtro = df_join[df_join['end_atual'] != df_join['end']]
    df_filtro.drop(['descricao_atual'], axis=1, inplace=True)
    df_filtro = df_filtro.apply(calcular_dias, axis=1)
    filtro_concluidos = df_filtro['qtde_dias'] == 0
    st.subheader('Tarefas concluídas no período')
    st.dataframe(df_filtro[filtro_concluidos])
    st.subheader('Tarefas em andamento')
    st.dataframe(df_filtro[~filtro_concluidos])
    media_reprogramacao = df_filtro[~filtro_concluidos].qtde_dias.astype(
        'timedelta64[D]').mean()
    st.write(
        f'A reprogramação acarretou em um avanço médio de {media_reprogramacao} dias')


def sidebar_parametros():
    tmpdirname = f'/tmp/{uuid.uuid4()}'
    df = None
    os.mkdir(tmpdirname)
    fp_v1 = f'{tmpdirname}/v1.pdf'
    fp_v2 = f'{tmpdirname}/v2.pdf'
    #data_avanco = st.sidebar.date_input('Selecione a data de avanço')
    uploaded_v1 = st.sidebar.file_uploader(
        "Selecione o PDF inicial", type="pdf")
    if st.sidebar.button('Clique aqui!'):
        my_bar = st.progress(0)
        place = st.empty()
        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1)
        place.success(
            'Te amo muito Liliany, você é muito especial, é a mulher da minha vida. Perdoe as minhas falhas...')
        st.balloons()
    if uploaded_v1 is not None:
        with open(fp_v1, 'wb') as writer:
            writer.write(uploaded_v1.read())
        uploaded_v2 = st.sidebar.file_uploader(
            "Selecione o PDF final", type="pdf")
        if uploaded_v2 is not None:
            with open(fp_v2, 'wb') as writer:
                writer.write(uploaded_v2.read())
                if st.sidebar.button('Analisar'):
                    df = carregar_cronograma(fp_v1, fp_v2)
    shutil.rmtree(tmpdirname)
    return df


def main():
    cabecalho()
    df = sidebar_parametros()
    if df is not None:
        tratamento_dados(df)
    rodape()


if __name__ == "__main__":
    main()
