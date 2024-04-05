import streamlit as st
import pandas as pd
import plotly.express as px
import webbrowser as wb
import openpyxl
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
from io import BytesIO

today_date = datetime.now().strftime('%Y-%m-%d')

st.set_page_config(page_title="TikTok Report", page_icon="🚚", layout="wide")

st.title("🚚 Genuine Inside (M) Sdn. Bhd. - TIKTOK Report📋")
st.markdown("##")

st.header("TikTok File Upload")
tiktok_file = st.file_uploader(".xlsx file",type=['xlsx'])
df_tiktok = pd.read_excel(tiktok_file)
st.write("*If Error: open file, enable editing and save (CTRL+S) before reupload*")
df_tiktok.drop([0], axis=0, inplace=True)
df_tiktok_new=df_tiktok[['Created Time','Paid Time','RTS Time','Order ID','Shipping Provider Name','Tracking ID']].copy()
df_tiktok_new['tarikh'] = pd.to_datetime(df_tiktok['Created Time']).dt.date
df_tiktok_new = df_tiktok_new.drop_duplicates(subset='Order ID', keep="first")
df_tiktok_new=df_tiktok_new.sort_values(by='tarikh', ascending=True)
df_tiktok_new.reset_index(inplace=True)
df_tiktok_new = df_tiktok_new.drop('index', axis=1)
st.write("UPLOAD SUCCESS")

#select date on tiktok_file
st.markdown("#")
tarikh = st.multiselect(
"Select Date:",
options=df_tiktok_new["tarikh"].unique()
)
tiktok_filtered = df_tiktok_new.query(
"tarikh == @tarikh"
)
tiktok_filtered=tiktok_filtered.drop(['tarikh'], axis=1)
tiktok_filtered=tiktok_filtered.sort_values(by='Tracking ID', ascending=True)
tiktok_filtered.reset_index(inplace=True)
tiktok_filtered = tiktok_filtered.drop('index', axis=1)

st.write("______________________________________________________________________________________")
st.header("WMS File Upload")
wms_file = st.file_uploader(".xls file",type=['xls'])
df_wms = pd.read_html(wms_file)
df_wms=df_wms[0]
df_wms_new=df_wms[['Marketplace','Tracking No.','Order No.','Order Date','Batch No.','Pick No.','Status','Truck No.','Pick By','Sort By','Pack By','Load By','Updated On']].copy()
df_wms_new.rename(columns = {'Order Date':'tarikh'}, inplace = True)
df_wms_new = df_wms_new.drop_duplicates(subset='Order No.', keep="first")

filtered_df_wms_new = df_wms_new[df_wms_new['Marketplace'] == 'Shopee']
filtered_df_wms_new_INDEX=filtered_df_wms_new.index

df_wms_new.drop(filtered_df_wms_new_INDEX, inplace=True)
df_wms_new=df_wms_new.drop(['Marketplace'], axis=1)
df_wms_new=df_wms_new.sort_values(by='Tracking No.', ascending=True)
df_wms_new.reset_index(inplace=True)
df_wms_new = df_wms_new.drop('index', axis=1)
st.write("UPLOAD SUCCESS")

st.markdown("#")
st.write("")
df_compare=pd.concat([df_wms_new['Tracking No.'], tiktok_filtered['Tracking ID']])
df_compare2=df_compare.duplicated(keep=False)
df_compare3=pd.concat([df_compare, df_compare2], axis=1)
df_compare3.reset_index(inplace=True)
df_compare3 = df_compare3.drop('index', axis=1)
df_compare3['ID'] = np.where((df_compare3[1] == True), df_compare3[0], np.nan)

df_unique=df_compare3[['ID',1]].copy()
df_unique = df_unique.drop_duplicates(subset='ID', keep="first")

tiktok_filtered['WMS'] = np.where(tiktok_filtered['Tracking ID'].isin(df_wms_new['Tracking No.']), True, False)
tiktok_filtered.sort_values(['WMS', 'Tracking ID'], ascending=[False, True], inplace=True)
tiktok_filtered.reset_index(inplace=True)
tiktok_filtered = tiktok_filtered.drop('index', axis=1)

df_wms_new['Tiktok'] = np.where(df_wms_new['Tracking No.'].isin(df_compare3['ID']), df_wms_new['Tracking No.'], np.nan)
df_wms_new=df_wms_new.dropna(subset=['Tiktok'])
df_wms_new = df_wms_new.drop('Tiktok', axis=1)
df_wms_new.reset_index(inplace=True)
df_wms_new = df_wms_new.drop('index', axis=1)

df_final=pd.concat([tiktok_filtered, df_wms_new], axis=1)
#df_final=df_final.sort_values(by='WMS', ascending=True)
df_final.rename(columns = {'tarikh':'Order Date'}, inplace = True) 
df_final.reset_index(inplace=True)
df_final = df_final.drop('index', axis=1)
df_final

highlight = [False]
style_row_mapping = ['background:grey' if x in highlight else 'background:white' for x in df_final.WMS]
df_highlighted = df_final.style.apply(lambda x: style_row_mapping , axis = 0)

# Function to write DataFrames to an Excel file in memory
def dfs_to_excel(df_list, sheet_list):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for dataframe, sheet in zip(df_list, sheet_list):
            dataframe.to_excel(writer, sheet_name=sheet, index=False)
    output.seek(0)
    return output

df_list = [df_final]
sheet_list = ['Sheet1']

# Convert DataFrames to Excel in memory
excel_file = dfs_to_excel(df_list, sheet_list)

# Streamlit download button
st.download_button(
    label="Download Excel file",
    data=excel_file,
    file_name=f"TikTok_Report_{today_date}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
#df_final=df_final.style.apply(custom_style, axis=1)
#df_final
