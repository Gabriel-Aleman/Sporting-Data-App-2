from headers import *
wimuApp.ses_play()
st.header("Informe completo", divider=True)
add_vertical_space(2)
t1,t2,t3=st.tabs(["Informe completo","Informe x Jugador", "Informe x Jugador"])



with t1:

    with stylable_container(
        "bses",
        css_styles=css,
    ): st.write(wimuApp.styledInform.iloc[0:100].to_html(), unsafe_allow_html=True)
with t2:

    st.write(wimuApp.infxPlay.iloc[0:100].to_html(), unsafe_allow_html=True)
with t3:

    with stylable_container(
        "bses",
        css_styles=css,
    ): st.write(wimuApp.infxSes.iloc[0:100].to_html(), unsafe_allow_html=True)