from headers import *
from streamlit_extras.app_logo import add_logo

image_path = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTD-ViQjMELIoVlV44DnXliYZoV2knLJ218zQ&s"

st.set_page_config(
    page_title="SFC DATA APP",
    page_icon=image_path
)
add_logo("http://placekitten.com/120/120")
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
    st.header("SFC: Data - APP",divider=True)
with col1:
    st.markdown(html_code, unsafe_allow_html=True)
add_vertical_space(1)
#--------------------------------------------------------------------------


if 'listAlreadyDone' not in st.session_state:
    st.session_state.listAlreadyDone = False
if 'df' not in st.session_state:
    st.session_state.df =  wimuApp.inform
if "bd" not in st.session_state:
    st.session_state.bd = wimuApp.inform.sort_values(by="Fecha")["Fecha"].iloc[0]
if "ed" not in st.session_state:
    st.session_state.ed = wimuApp.inform.sort_values(by="Fecha")["Fecha"].iloc[-1]

tab1, tab2 = st.tabs(["Informe", "Estadísticas"])

with tab1:
    #st.markdown("### • Opciones de filtrado:")
    
    col1, co2= st.columns(2)
    with col1:
        with st.expander("### Filtros"):
            with stylable_container(
                key="container_with_border",
                css_styles="""
                    {
                        border-radius: 10px; /* Bordes redondeados */

                        padding: 5px; /* Espaciado interno */
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.6); /* Sombra suave */
                    }
                    """,
            ): c=st.container()
            with c:
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
                        st.session_state.bd= st.date_input("Fecha de inicio")
                        #st.session_state.ed= st.date_input("Fecha de fin")
    with col2:
        datos = [[10, 11, 12, 13],
          [20, 21, 22, 23],
          [30, 31, 32, 33]]
        datos = pd.DataFrame(datos)
        #st.download_button("Descargar informe ⬇️", datos.to_excel())

    wimuApp.infXMD(md)
    df=wimuApp.styledInform[wimuApp.styledInform['Jugador'].isin(wimuApp.jugxPos[pos])] if pos!="Todos" else wimuApp.styledInform
    df=df.query("Duración <=@limSup and Duración >=@limInf")
    df["Fecha"]=pd.to_datetime(df["Fecha"])
    df=df.query("Fecha <=@st.session_state.bd")
    st.session_state.df = df
    #TODO: Mover parte superior

    # Redondear a 2 decimales solo las columnas numéricas
    df[df.select_dtypes(include='number').columns] = df.select_dtypes(include='number').round(2)
    
    st.dataframe(df.reset_index(drop=True))
    col1, col2= st.columns([27,14])

    with col1: st.info(f"**MD**:{md}   ‎‎‎     **Posición**:{pos}  ‎‎‎      **Duración**: {limInf}-{limSup} (min)")
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
        ):    st.write(f"📝 {len(df)} datos en la busqueda")

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
