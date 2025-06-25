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
    """Returns `True` if the user had the correct password."""
 
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False
 
    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True
 
    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False
 
 
if not check_password():
    st.stop()  # Do not continue if check_password is not True.
 
##################################################################
 
##################################################################
 
# Function to cache data 2
@st.cache_resource
def get_data():
    # Load MongoDB URI from Streamlit secrets
    # Ensure you have defined 'mongouri' in your secrets.toml
    mongo_uri = st.secrets["mongouri"]
 
    # Connect to your MongoDB cluster
    client = pymongo.MongoClient(mongo_uri)
 
    # Select your database
    db = client.ANTIGUEDAD
 
 
    # Select your collection
    collection  = db.COLUMBIA_GT
 
    # Fetch data from the collection
    # Converting cursor to list then to DataFrame
    data = list(collection.find())
    df = pd.DataFrame(data)
 
    # Fetch data from the collection2
    # Converting cursor to list then to DataFrame
    data = list(collection.find())
    df = pd.DataFrame(data)
 
    return df
 
 
################################################################################################################################################################
 
 
#Set the Page title to ANTIGUEDAD ACCESSA
st.set_page_config(page_title="ANTIGUEDAD COLUMBIA GT", layout="wide")
 
#Center the title in the middle of the page
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
 
 
 
 
 
#Center the title in the middle of the dashboard
st.markdown('<h1 class="title">ANTIGUEDAD COLUMBIA</h1>', unsafe_allow_html=True)
 
 
 
 
 
 
 
 
#####################################################################################################################################################################
 
# Get data
df = get_data()
#Drop the _id column if it exists
if '_id' in df.columns:
    df.drop(columns=['_id'], inplace=True)
 
#Drop all rows where Stock_Actual is less than 1
df = df[df['Stock_Actual'] >= 1]
 
 
 
 
 
#Print the sum of the Stock_Actual column
# tHOUSAND SEPARATOR = ','
st.write("Total Stock Actual for COLUMBIA:", f"{df['Stock_Actual'].sum():,.0f}")
#st.write("Total Stock Actual for NEW ERA:", df['Stock_Actual'].sum())
 
 
 
 
 
###########################################################################################################################################################
 
# Ensure Fecha_Ingreso is datetime only once
df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], errors='coerce')
 
# Create four columns for filters
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
 
# Now apply all filters to the same DataFrame
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
 
# Show the filtered DataFrame
 
 
 
#Create a Copy of the filtered DataFrame
df_filtered2 = df_filtered.copy()
 
 
 
#For df_filtered2 create a column for Meses_En_Inventario, Pais. Then create a third column that shows the percent of the total stock for each country. Divide it this way: Month 0-6, 7-11, and 12 to 23
df_filtered2['Meses_En_Inventario'] = ((datetime.datetime.now() - df_filtered2['Fecha_Ingreso']).dt.days // 30).astype(int)
df_filtered2['Pais'] = df_filtered2['Pais'].astype(str)
 
#Drop all colums where Stock_Actual is less than 1
df_filtered2 = df_filtered2[df_filtered2['Stock_Actual'] >= 1]
 
 
#Delete other columns except for Pais, Stock_Actual, Meses_En_Inventario
df_filtered2 = df_filtered2[['Pais', 'Stock_Actual', 'Meses_En_Inventario']]
 
#reset the index
df_filtered2.reset_index(drop=True, inplace=True)
 
 
 
 
 
#Create a copy of df_filtered2
df_mes1 = df_filtered2.copy()
 
# Asegúrate de trabajar con copias limpias
df_mes1 = df_filtered2.copy()
df_mes2 = df_filtered2.copy()
df_mes3 = df_filtered2.copy()
df_mes4 = df_filtered2.copy()
 
# Filtrar por rangos y agregar etiqueta de grupo
df_mes1 = df_mes1[(df_mes1['Meses_En_Inventario'] >= 0) & (df_mes1['Meses_En_Inventario'] <= 6)]
df_mes1['Grupo_Meses'] = '1-6 meses'
 
df_mes2 = df_mes2[(df_mes2['Meses_En_Inventario'] >= 7) & (df_mes2['Meses_En_Inventario'] <= 11)]
df_mes2['Grupo_Meses'] = '7-11 meses'
 
df_mes3 = df_mes3[(df_mes3['Meses_En_Inventario'] >= 12) & (df_mes3['Meses_En_Inventario'] <= 23)]
df_mes3['Grupo_Meses'] = '12-23 meses'
 
df_mes4 = df_mes4[df_mes4['Meses_En_Inventario'] >= 24]
df_mes4['Grupo_Meses'] = '24+ meses'
 
# I want to create KPI cards that calculate the sum of Stock_Actual for each group and divides it by the sum of Stock_Actual for all groups.
kpi1 = df_mes1['Stock_Actual'].sum() / df_filtered2['Stock_Actual'].sum()
kpi2 = df_mes2['Stock_Actual'].sum() / df_filtered2['Stock_Actual'].sum()
kpi3 = df_mes3['Stock_Actual'].sum() / df_filtered2['Stock_Actual'].sum()
kpi4 = df_mes4['Stock_Actual'].sum() / df_filtered2['Stock_Actual'].sum()
 
# Create KPI cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="1-6 meses", value=f"{kpi1:.2%}", delta=f"{kpi1:.2%}")
with col2:
    st.metric(label="7-11 meses", value=f"{kpi2:.2%}", delta=f"{kpi2:.2%}")
with col3:
    st.metric(label="12-23 meses", value=f"{kpi3:.2%}", delta=f"{kpi3:.2%}")
with col4:
    st.metric(label="24+ meses", value=f"{kpi4:.2%}", delta=f"{kpi4:.2%}")
 
 
#Create a new data frame that displays the following columns, range of months, total stock, and percentage of total stock
df_kpi = pd.DataFrame({
    'Rango de Meses': ['1-6 meses', '7-11 meses', '12-23 meses', '24+ meses'],
    'Total Stock': [df_mes1['Stock_Actual'].sum(), df_mes2['Stock_Actual'].sum(), df_mes3['Stock_Actual'].sum(), df_mes4['Stock_Actual'].sum()],
    'Porcentaje del Total': [kpi1, kpi2, kpi3, kpi4]
})
 
#Display the 'Porcentaje del Total' column as a percentage
df_kpi['Porcentaje del Total'] = df_kpi['Porcentaje del Total'].apply(lambda x: f"{x:.2%}")
 
# ADD THOUSAND SEPARATOR TO THE 'Total Stock' COLUMN
df_kpi['Total Stock'] = df_kpi['Total Stock'].apply(lambda x: f"{x:,.0f}")
 
 
# Display the KPI DataFrame
st.dataframe(df_kpi, use_container_width=True)
 
# Step 1: Agrupar meses > 24 antes de agregar
df_filtered2['Meses_En_Inventario_Grouped'] = df_filtered2['Meses_En_Inventario'].apply(
    lambda x: '24+ meses' if x > 24 else f"{x} meses"
)
 
# Step 2: Agrupar por el nuevo campo y sumar el stock
df_monthly = df_filtered2.groupby('Meses_En_Inventario_Grouped')['Stock_Actual'].sum().reset_index()
 
# Step 3: Renombrar columnas
df_monthly.columns = ['Meses_En_Inventario', 'Total_Stock']
 
# Step 4: Formatear 'Total_Stock' con comas
df_monthly['Total_Stock'] = df_monthly['Total_Stock'].apply(lambda x: f"{x:,.0f}")
 
# Step 5: Ordenar por mes numérico, dejando '24+ meses' al final
df_monthly['SortOrder'] = df_monthly['Meses_En_Inventario'].apply(
    lambda x: int(x.split()[0]) if x != '24+ meses' else 999
)
df_monthly = df_monthly.sort_values('SortOrder').drop(columns='SortOrder')
 
# Reiniciar el índice
df_monthly.reset_index(drop=True, inplace=True)
 
# Paso 6: Etiquetar los grupos (0–6, 7–11, 12–23, 24+)
def assign_group(mes):
    if mes <= 6:
        return '0–6 meses'
    elif mes <= 11:
        return '7–11 meses'
    elif mes <= 23:
        return '12–23 meses'
    else:
        return '24+ meses'
 
# Convertir 'Total_Stock' a numérico para cálculos
df_monthly['Total_Stock_Numeric'] = df_monthly['Total_Stock'].str.replace(',', '').astype(float)
 
 
 
 
 
# Asignar grupos por rango de meses
df_monthly['Grupo'] = df_monthly['Meses_En_Inventario'].str.extract(r'(\d+)').astype(float)[0].apply(assign_group)
df_monthly['Grupo'] = df_monthly['Grupo'].fillna('24+ meses')  # Para los casos de "24+ meses"
 
# Calcular porcentaje por grupo con base fija (139348.0)
total_stock = df_monthly['Total_Stock_Numeric'].sum()
 
group_percentages = (
    df_monthly.groupby('Grupo')['Total_Stock_Numeric']
    .sum()
    .apply(lambda x: f"{x / total_stock:.2%}")
    .to_dict()
)
 
 
# Asignar porcentaje con etiqueta a la primera fila de cada grupo
df_monthly['Porcentaje del Total'] = ''
for group, porcentaje in group_percentages.items():
    first_index = df_monthly[df_monthly['Grupo'] == group].index[0]
    # Agregar etiqueta con nombre del grupo entre paréntesis
    etiqueta = f"{porcentaje} ({group})"
    df_monthly.at[first_index, 'Porcentaje del Total'] = etiqueta
 
# Formato final
df_monthly.drop(columns=['Total_Stock_Numeric', 'Grupo'], inplace=True)
df_monthly.rename(columns={'Total_Stock': 'Total Stock'}, inplace=True)
 
# Mostrar en Streamlit
st.subheader("Total Stock por Meses en Inventario")
st.dataframe(df_monthly, use_container_width=True)
 
 
 
 
 
 
 
 
 
 
 