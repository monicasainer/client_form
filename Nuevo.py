from utils.transform import Transform
from utils.extract import Extract
from utils.load import Load
from datetime import datetime
import streamlit as st
from uuid import uuid4

def app():
    st.header('Formulario de nuevos clientes')

    # @st.cache_resource()
    # Load the data from the Google Sheet
    data = Extract.load_data("Informacion_de_clientes","clientes")

    # Fetch unique values from 'nombre' and 'correo electrónico' columns
    df_unique = data['nombre'].drop_duplicates()
    names_list = df_unique.unique()   # Unique company names

    # Create the Streamlit form
    with st.form(key='company_form'):
        st.write("### Formulario de Nuevo Cliente")

        # Input field for the company name
        company_name = st.text_input("Nombre del nuevo cliente:")

        # Apply the 'change' function to format the company name
        transformed_name = Transform.capital_letters(company_name)

        # Check if the transformed name exists in the data
        if transformed_name in names_list:
            st.warning(f"¡La compañia '{transformed_name}' ya existe! Debes clicka en  el siguiente ") #{st.page_link("pages/Modificar.py", label="Link")}

            # Disable further input if name matches
            st.text_input("CIF:", disabled=True)
            st.text_input("Dirección de correo electrónico:", disabled=True)
            st.number_input("Número de teléfono:",step=1, disabled=True)
            st.text_input("Dirección:", disabled=True)
            st.number_input("Código postal:", step=1, disabled=True)
            st.text_input("Municipio:", disabled=True)
            st.text_input("Provincia:", disabled=True)
            st.text_input("País:", disabled=True)
            st.number_input("Número de empleados:", step=1,disabled=True)
            st.selectbox("Industria",
            ("AGRICULTURA, SILVICULTURA Y PESCA",
                "MINERÍA Y CANTERAS",
                "MANUFACTURAS",
                "SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO",
                "ABASTECIMIENTO DE AGUA; ALCANTARILLADO, GESTIÓN DE RESIDUOS Y ACTIVIDADES DE REMEDIACIÓN",
                "CONSTRUCCIÓN",
                "COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACIÓN DE VEHÍCULOS DE MOTOR Y MOTOCICLETAS",
                "TRANSPORTE Y ALMACENAMIENTO",
                "ACTIVIDADES DE ALOJAMIENTO Y SERVICIO DE ALIMENTACIÓN",
                "INFORMACIÓN Y COMUNICACIÓN",
                "ACTIVIDADES FINANCIERAS Y DE SEGUROS",
                "ACTIVIDADES INMOBILIARIAS",
                "ACTIVIDADES PROFESIONALES, CIENTÍFICAS Y TÉCNICAS",
                "ACTIVIDADES DE SERVICIOS ADMINISTRATIVOS Y DE APOYO",
                "ADMINISTRACIÓN PÚBLICA Y DEFENSA; SEGURIDAD SOCIAL OBLIGATORIA",
                "EDUCACIÓN",
                "ACTIVIDADES DE SALUD HUMANA Y TRABAJO SOCIAL",
                "ARTES, ENTRETENIMIENTO Y RECREACIÓN",
                "OTRAS ACTIVIDADES DE SERVICIO",
                "ACTIVIDADES DE LOS HOGARES COMO EMPLEADORES; ACTIVIDADES DE PRODUCCIÓN DE BIENES Y SERVICIOS NO DIFERENCIADOS DE LOS HOGARES PARA USO PROPIO",
                "ACTIVIDADES DE ORGANIZACIONES Y ORGANISMOS EXTRATERRITORIALES"), disabled=True)
            st.date_input("Fecha actual",format="DD/MM/YYYY", disabled=True)
            st.text_area("Información Additional", disabled=True)
        else:

            # If no match, allow further input
            cif = st.text_input("CIF:")
            email = st.text_input("Dirección de correo electrónico:")
            phone = st.number_input("Número de teléfono:", step=1)
            address = st.text_input("Dirección:")
            code = st.number_input("Código postal:", step=1)
            municipality =  st.text_input("Municipio:")
            city = st.text_input("Provincia:")
            country = st.text_input("País:")
            n_employees = st.number_input("Número de empleados:", step=1)
            industry = st.selectbox("Industria",
            ("AGRICULTURA, SILVICULTURA Y PESCA",
                "MINERÍA Y CANTERAS",
                "MANUFACTURAS",
                "SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO",
                "ABASTECIMIENTO DE AGUA; ALCANTARILLADO, GESTIÓN DE RESIDUOS Y ACTIVIDADES DE REMEDIACIÓN",
                "CONSTRUCCIÓN",
                "COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACIÓN DE VEHÍCULOS DE MOTOR Y MOTOCICLETAS",
                "TRANSPORTE Y ALMACENAMIENTO",
                "ACTIVIDADES DE ALOJAMIENTO Y SERVICIO DE ALIMENTACIÓN",
                "INFORMACIÓN Y COMUNICACIÓN",
                "ACTIVIDADES FINANCIERAS Y DE SEGUROS",
                "ACTIVIDADES INMOBILIARIAS",
                "ACTIVIDADES PROFESIONALES, CIENTÍFICAS Y TÉCNICAS",
                "ACTIVIDADES DE SERVICIOS ADMINISTRATIVOS Y DE APOYO",
                "ADMINISTRACIÓN PÚBLICA Y DEFENSA; SEGURIDAD SOCIAL OBLIGATORIA",
                "EDUCACIÓN",
                "ACTIVIDADES DE SALUD HUMANA Y TRABAJO SOCIAL",
                "ARTES, ENTRETENIMIENTO Y RECREACIÓN",
                "OTRAS ACTIVIDADES DE SERVICIO",
                "ACTIVIDADES DE LOS HOGARES COMO EMPLEADORES; ACTIVIDADES DE PRODUCCIÓN DE BIENES Y SERVICIOS NO DIFERENCIADOS DE LOS HOGARES PARA USO PROPIO",
                "ACTIVIDADES DE ORGANIZACIONES Y ORGANISMOS EXTRATERRITORIALES"))
            date = st.date_input("Fecha actual",format="DD/MM/YYYY")
            info = st.text_area("Información Additional")
            date_str = date.strftime("%Y-%m-%d")
            ingestion_date = datetime.now()
            ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")
            customer_id = str(uuid4())

            row = [customer_id,transformed_name, cif, email, phone, address, code, municipality, city, country,n_employees, industry, date_str, info, ingestion_date_str]

        # Submit button for the form
        submit_button = st.form_submit_button(label='¡Listo!')

        # If form is submitted and no match is found
        if submit_button and transformed_name not in names_list:

            Load().append_row("Informacion_de_clientes","clientes",row)
            st.success("¡Guardado con éxito!")
