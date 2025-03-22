import streamlit as st # type: ignore
import pandas as pd # type: ignore
from datetime import date
import os
import io
import mxlreader as mxl
import txtreader as txt
import crdreader as crd
import sqlitereader as sql
import dfwriter as dfw
import zipfile
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

#Utility



def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Add filters")
    if not modify:
        return df
    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df

def get_file_type(x):
    '''RETURN STRING FILE EXTENSION'''
    extension = os.path.splitext(x)[1]
    return extension


#Utility


uploaded_file = st.file_uploader("Choose a file", type=['.mxl','.txt'])
if uploaded_file is not None:
    type = get_file_type(uploaded_file.name)
    print(type)
    if type == '.mxl':
        t= mxl.MXL(uploaded_file)
        df = t.getPoints()
    if type == '.txt':
        t = txt.TXT(uploaded_file)
        df = t.getPoints()
    if type == ".crd":
        t = crd.CRDREADER(uploaded_file)
        df = t.read_crd()
    if type == '.bak':
        t = sql.SQL(uploaded_file.getvalue())
        df = t.getPntsCodesLayers()
        t.close()


    st.dataframe(filter_dataframe(df),hide_index=True)
    t = dfw.DFWRITER(df)
    layer_date = t.createFldTxt()
    #layer = t.createTXTNoDates()
    

    href1 = f'<a href=\"data:file/zip;base64,{layer_date}\" download="Files.zip">Download files as Layer-Date (e.g. AB-STORM 3-22-25)</a>'
    st.markdown(href1, unsafe_allow_html=True)
    # href2 = f'<a href=\"data:file/zip;base64,{layer}\" download="Files.zip">Download files as Layer (AB-STORM)</a>'
    # st.markdown(href2, unsafe_allow_html=True)


    # output_csv = df.to_csv(index=False).encode('utf-8')
    # t = dfw.DFWRITER(df)
    # zipper = t.createFldTxt()
    # with open('Files.zip', 'w') as file:
    #     btn = st.download_button(
    #         label="Download layer - date files",
    #         data=zipper,
    #         file_name = "Files.zip",
    #         mime = "application/zip"
    #     )
    #st.download_button("Download as one file", output_csv, file_name = "v.csv", mime="text/csv"):
    #dtbut = st.download_button('Download layer - date files', zipper, mime="application/zip",file_name = "FILES.zip")
    
