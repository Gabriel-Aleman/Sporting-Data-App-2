from headers import *
from streamlit_extras.app_logo import add_logo

image_path = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTD-ViQjMELIoVlV44DnXliYZoV2knLJ218zQ&s"

st.set_page_config(
    page_title="SFC DATA APP",
    page_icon=image_path
)
st.logo("https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Sporting_Football_Club_2019.png/157px-Sporting_Football_Club_2019.png")




with st.sidebar:
    st.write("Hola mundo")
# Redondear bordes de la imagen usando HTML y CSS
html_code = f"""
<style>
img {{
    border-radius: 15px;
}}
</style>
<img src="{image_path}" width="100">
"""

# Título de la aplicación
#--------------------------------------------------------------------------
col1, col2 = st.columns([1,5])
with col2:
    colored_header(
        label="SFC: Data - APP",
        description="¡Somos Sporting, Somos Pura Vida!",
        color_name="violet-70",
    )
#st.header("SFC: Data - APP",divider=True)
with col1:
    st.markdown(html_code, unsafe_allow_html=True)
add_vertical_space(1)
#--------------------------------------------------------------------------
#TODO: Actualizar el apartado para ingresar el token


fr= wimuApp.inform.sort_values(by="Fecha")["Fecha"].iloc[0]
fr = datetime.strptime(fr,  "%Y-%m-%d %H:%M")

lr= wimuApp.inform.sort_values(by="Fecha")["Fecha"].iloc[-1]
lr = datetime.strptime(lr,  "%Y-%m-%d %H:%M")

if 'listAlreadyDone' not in st.session_state:
    st.session_state.listAlreadyDone = False
if 'df' not in st.session_state:
    st.session_state.df =  wimuApp.inform
if "bd" not in st.session_state:

    st.session_state.bd = fr
if "ed" not in st.session_state:

    st.session_state.ed = lr

if "df"not in st.session_state:
    st.session_state.df = wimuApp.inform

tab1, tab2 = st.tabs(["📄Informe", "📊Estadísticas"])

with tab1:
    with st.expander("### • Filtros"):

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            ops_MD= ["Todos"]
            ops_MD.extend(pd.unique(wimuApp.session["matchDay"]))
            with st.popover("⚽ X MD"):
                md = st.selectbox("Qué MD le interesa", ops_MD)
        with col2:
            ops_Pos= ["Todos"]
            ops_Pos.extend(pd.unique(wimuApp.players["Posición"]))
            with st.popover("📍 X Posición"):
                pos = st.selectbox("Qué posisición le interesa",ops_Pos)
        with col3: 
            with st.popover("⏰ X duración"):
                t = st.slider("Filtrar por duración:", wimuApp.inform["Duración"].min(), wimuApp.inform["Duración"].max(), (wimuApp.inform["Duración"].min(),wimuApp.inform["Duración"].max()))
                limInf,limSup = t
        with col4:
            with st.popover("📅 X fecha"):
                st.session_state.ed= st.date_input("Fecha de fin", value=lr, min_value=fr, max_value=lr)
                st.session_state.bd= st.date_input("Fecha de inicio", value=fr, min_value=fr, max_value=lr)
        st.info(f"**MD**:{md}   ‎‎‎     **Posición**:{pos}  ‎‎‎      **Duración**: {limInf}-{limSup} (min)")
    wimuApp.infXMD(md)
    st.session_state.df=wimuApp.styledInform[wimuApp.styledInform['Jugador'].isin(wimuApp.jugxPos[pos])] if pos!="Todos" else wimuApp.styledInform
    st.session_state.df=st.session_state.df.query("Duración <=@limSup and Duración >=@limInf")
    st.session_state.df["Fecha"]=pd.to_datetime(st.session_state.df["Fecha"])
    st.session_state.df=st.session_state.df.query("Fecha >=@st.session_state.bd and Fecha <=@st.session_state.ed")
    st.session_state.df = st.session_state.df
    #TODO: Mover parte superior

    # Redondear a 2 decimales solo las columnas numéricas
    st.session_state.df[st.session_state.df.select_dtypes(include='number').columns] = st.session_state.df.select_dtypes(include='number').round(2)
    
    st.dataframe(st.session_state.df.reset_index(drop=True))
    col1, col2= st.columns([27,14])

    #with col2:
    with col2:
        with stylable_container(
            "bses",
            css_styles= """
            {
                font-family: 'Lexend', sans-serif;
                background-color: #002746; /* Azul oscuro */
                color: white; /* Texto blanco */
                padding: 15px;
                border-radius: 5px;
                display: inline-block; /* Para ajustar al contenido */
            }""",
        ):    st.write(f"📝 {len(st.session_state.df)} datos en la busqueda")


with tab2:
    df_data=st.session_state.df[st.session_state.df.columns[4:]]
    with st.expander("Descripción general", expanded=True):
        st.dataframe(df_data.describe().round(2))
    with st.expander("Promedios", expanded=True):
        df_mean =df_data.mean().round(2)
        df_mean.name = "Promedios"
        st.dataframe(pd.DataFrame(df_mean).T)
    with st.expander("Desviación estandar", expanded=True):
        df_std =df_data.std().round(2)
        df_std.name = "Desviación estandar"
        st.dataframe(pd.DataFrame(df_std).T)
    with st.expander("Suma", expanded=True):
        df_sum=df_data.sum().round(2)
        df_sum.name ="Suma"
        st.dataframe(pd.DataFrame(df_sum).T)
        
#if not(st.session_state.listAlreadyDone):
#    with st.spinner("Cargando sesiones"):
#        wimuApp.getAllSessions()
#    wimuApp.findNewSes()
#    st.session_state.listAlreadyDone = True
#
#if len(wimuApp.nuevasSesiones)!=0:
#    col1, col2 = st.columns(2)
#    with col1:
#        st.info(f"Se han encontrado {len(wimuApp.nuevasSesiones)} nuevas sesiones")
#    with col2:
#        st.button("Añadir sesiones nuevas a la base de datos")
#
#with st.expander("Listado de sesiones"):
#    st.dataframe(wimuApp.session)
