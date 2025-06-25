import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pymongo
import hmac
import pandas as pd
import calendar

##################################################################
# Password
def check_password():
    """Returns `True` if the user has the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop()

##################################################################

@st.cache_resource
def get_data():
    mongo_uri = st.secrets["mongouri"]
    client = pymongo.MongoClient(mongo_uri)
    db = client.ANTIGUEDAD
    collection = db.SKECHERS_GT
    data = list(collection.find())
    df = pd.DataFrame(data)
    return df

##################################################################

st.set_page_config(page_title="ANTIGUEDAD SKECHERS GT", layout="wide")

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 36px;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">ANTIGUEDAD SKECHERS</h1>', unsafe_allow_html=True)

##################################################################

df = get_data()

if '_id' in df.columns:
    df.drop(columns=['_id'], inplace=True)

df = df[df['Stock_Actual'] >= 1]

st.write("Total Stock Actual for SKECHERS:", f"{df['Stock_Actual'].sum():,.0f}")

df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], errors='coerce')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pais = st.multiselect('País', sorted(df['Pais'].dropna().unique()))
with col2:
    sap = st.multiselect('SAP', sorted(df['Codigo_SAP'].dropna().unique()))
with col3:
    years = sorted(df['Fecha_Ingreso'].dt.year.dropna().unique())
    selected_years = st.multiselect('Año de Ingreso', years)
with col4:
    month_nums = sorted(df['Fecha_Ingreso'].dt.month.dropna().unique())
    month_options = [calendar.month_name[int(m)] for m in month_nums]
    month_name_to_num = {calendar.month_name[i]: i for i in range(1, 13)}
    selected_months = st.multiselect('Mes de Ingreso', month_options)
with col5:
    estilo = st.multiselect('Estilo', sorted(df['U_Estilo'].dropna().unique()))

df_filtered = df.copy()

if pais:
    df_filtered = df_filtered[df_filtered['Pais'].isin(pais)]
if sap:
    df_filtered = df_filtered[df_filtered['Codigo_SAP'].isin(sap)]
if selected_years:
    df_filtered = df_filtered[df_filtered['Fecha_Ingreso'].dt.year.isin(selected_years)]
if selected_months:
    selected_month_nums = [month_name_to_num[m] for m in selected_months]
    df_filtered = df_filtered[df_filtered['Fecha_Ingreso'].dt.month.isin(selected_month_nums)]
if estilo:
    df_filtered = df_filtered[df_filtered['U_Estilo'].isin(estilo)]

df_filtered2 = df_filtered.copy()

df_filtered2['Meses_En_Inventario'] = ((datetime.datetime.now() - df_filtered2['Fecha_Ingreso']).dt.days // 30)
df_filtered2['Meses_En_Inventario'] = df_filtered2['Meses_En_Inventario'].astype('Int64')

df_filtered2 = df_filtered2.dropna(subset=['Meses_En_Inventario'])
df_filtered2 = df_filtered2[['Pais', 'Stock_Actual', 'Meses_En_Inventario']].reset_index(drop=True)

def assign_group(mes):
    if mes <= 6:
        return '1-6 meses'
    elif mes <= 11:
        return '7-11 meses'
    elif mes <= 23:
        return '12-23 meses'
    else:
        return '24+ meses'

df_filtered2['Grupo_Meses'] = df_filtered2['Meses_En_Inventario'].apply(assign_group)

group_sums = df_filtered2.groupby('Grupo_Meses')['Stock_Actual'].sum().to_dict()
total_stock = df_filtered2['Stock_Actual'].sum()

kpi1 = group_sums.get('1-6 meses', 0) / total_stock
kpi2 = group_sums.get('7-11 meses', 0) / total_stock
kpi3 = group_sums.get('12-23 meses', 0) / total_stock
kpi4 = group_sums.get('24+ meses', 0) / total_stock

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="1-6 meses", value=f"{kpi1:.2%}")
with col2:
    st.metric(label="7-11 meses", value=f"{kpi2:.2%}")
with col3:
    st.metric(label="12-23 meses", value=f"{kpi3:.2%}")
with col4:
    st.metric(label="24+ meses", value=f"{kpi4:.2%}")

df_kpi = pd.DataFrame({
    'Rango de Meses': ['1-6 meses', '7-11 meses', '12-23 meses', '24+ meses'],
    'Total Stock': [group_sums.get('1-6 meses', 0), group_sums.get('7-11 meses', 0),
                    group_sums.get('12-23 meses', 0), group_sums.get('24+ meses', 0)],
    'Porcentaje del Total': [kpi1, kpi2, kpi3, kpi4]
})

df_kpi['Porcentaje del Total'] = df_kpi['Porcentaje del Total'].apply(lambda x: f"{x:.2%}")
df_kpi['Total Stock'] = df_kpi['Total Stock'].apply(lambda x: f"{x:,.0f}")
st.dataframe(df_kpi, use_container_width=True)

df_filtered2['Meses_En_Inventario_Grouped'] = df_filtered2['Meses_En_Inventario'].apply(
    lambda x: '24+ meses' if x >= 24 else f"{x} meses"
)

df_monthly = df_filtered2.groupby('Meses_En_Inventario_Grouped')['Stock_Actual'].sum().reset_index()
df_monthly.columns = ['Meses_En_Inventario', 'Total Stock']

df_monthly['SortOrder'] = df_monthly['Meses_En_Inventario'].apply(lambda x: int(x.split()[0]) if x != '24+ meses' else 999)
df_monthly = df_monthly.sort_values('SortOrder').drop(columns='SortOrder').reset_index(drop=True)

def extract_month(x):
    return int(x.split()[0]) if x != '24+ meses' else 999

df_monthly['Mes_Numeric'] = df_monthly['Meses_En_Inventario'].apply(extract_month)
df_monthly['Grupo'] = df_monthly['Mes_Numeric'].apply(assign_group)

# Calculate group percentages
group_percentages = (
    df_monthly.groupby('Grupo')['Total Stock'].sum()
    .apply(lambda x: f"{x / df_monthly['Total Stock'].sum():.2%}")
    .to_dict()
)

# Add percentage label to first row of each group
df_monthly['Porcentaje del Total'] = ''
for group, porcentaje in group_percentages.items():
    first_index = df_monthly[df_monthly['Grupo'] == group].index[0]
    df_monthly.at[first_index, 'Porcentaje del Total'] = f"{porcentaje} ({group})"

# Fixed drop: Removed 'Total_Stock_Numeric' that doesn't exist
df_monthly.drop(columns=['Mes_Numeric', 'Grupo'], inplace=True)

st.subheader("Total Stock por Meses en Inventario")
st.dataframe(df_monthly, use_container_width=True)

