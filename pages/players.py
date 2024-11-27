from headers import *
st.header("Jugadores", divider=True)


with stylable_container(
    "bses",
    css_styles=css_p,
): st.write(wimuApp.players.reset_index(drop=True).to_html(), unsafe_allow_html=True)