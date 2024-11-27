from wimu import *

import hmac
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
#from streamlit_navigation_bar import st_navbar
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.let_it_rain import rain
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.app_logo import add_logo

f=open("css/tableInf.css")
css=f.read()
f.close()


f=open("css/table_play.css")
css_p=f.read()
f.close()