import streamlit as st
from streamlit_option_menu import option_menu
import Inicio,Modificar,Nuevo,Albaran


class ClientForm:
    def __init__(self) -> None:
        self.apps =[]

    def add_applications(self,title,function):
        self.apps.append({
            "title" : title,
            "function" : function}
        )

    def run():
        with st.sidebar:
            app = option_menu(
                menu_title = "Formulario de cliente",
                options = ['Inicio','Nuevo','Modificar','Albaran'],
                icons = ['house-fill','person-circle','pen'],
                menu_icon = "menu-app",
                default_index = 0,
                styles = {
                    "container":{"padding":"10","background":"grey"},
                    "icon":{"color":"white","font-size":"20px"},
                    "nav-link":{"color":"white","font-size":"20px","text-align":"left","--hover-color":"black"},
                    "nav-link-selected":{"background-color":"#4a4a49"}
                }
            )
        if app == "Inicio":
            Inicio.app()

        if app == "Nuevo":
            Nuevo.app()

        if app == "Modificar":
            Modificar.app()

        if app == "Albaran":
            Albaran.app()
    run()
