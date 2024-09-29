from utils.transform import Transform
from utils.extract import Extract
from utils.load import Load
from datetime import datetime
import streamlit as st
from uuid import uuid4

def app():

    st.header('Formulario de nuevos clientes')

    # Cargar los datos
    data = Extract.load_data("Informacion_de_clientes","clientes")

    # Extraer valores únicos de la columna 'nombre'
    df_unique = data['nombre'].drop_duplicates()
    names_list = df_unique.unique()

    # Crear formulario de Streamlit
    with st.form(key='company_form', clear_on_submit=True):
        company_name = st.text_input("Nombre del nuevo cliente:")
        transformed_name = Transform.capital_letters(company_name)

        # Validar si el nombre ya existe
        if transformed_name in names_list and transformed_name:
            st.warning(f"¡La compañía '{transformed_name}' ya existe! Clica en 'Modificar'")

            # Deshabilitar el resto de los campos si el nombre ya existe
            st.text_input("CIF:", disabled=True)
            st.text_input("Dirección de correo electrónico:", disabled=True)
            st.number_input("Número de teléfono:", step=1, disabled=True)
            st.text_input("Dirección:", disabled=True)
            st.number_input("Código postal:", step=1, disabled=True)
            st.text_input("Municipio:", disabled=True)
            st.text_input("Provincia:", disabled=True)
            st.text_input("País:", disabled=True)
            st.number_input("Número de empleados:", step=1, disabled=True)
            st.selectbox("Industria",
                         ("AGRICULTURA, SILVICULTURA Y PESCA", "MINERÍA Y CANTERAS", "MANUFACTURAS",
                          "SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO",
                          "ABASTECIMIENTO DE AGUA; ALCANTARILLADO, GESTIÓN DE RESIDUOS Y ACTIVIDADES DE REMEDIACIÓN",
                          "CONSTRUCCIÓN", "COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACIÓN DE VEHÍCULOS DE MOTOR Y MOTOCICLETAS",
                          "TRANSPORTE Y ALMACENAMIENTO", "ACTIVIDADES DE ALOJAMIENTO Y SERVICIO DE ALIMENTACIÓN",
                          "INFORMACIÓN Y COMUNICACIÓN", "ACTIVIDADES FINANCIERAS Y DE SEGUROS",
                          "ACTIVIDADES INMOBILIARIAS", "ACTIVIDADES PROFESIONALES, CIENTÍFICAS Y TÉCNICAS",
                          "ACTIVIDADES DE SERVICIOS ADMINISTRATIVOS Y DE APOYO",
                          "ADMINISTRACIÓN PÚBLICA Y DEFENSA; SEGURIDAD SOCIAL OBLIGATORIA",
                          "EDUCACIÓN", "ACTIVIDADES DE SALUD HUMANA Y TRABAJO SOCIAL",
                          "ARTES, ENTRETENIMIENTO Y RECREACIÓN", "OTRAS ACTIVIDADES DE SERVICIO",
                          "ACTIVIDADES DE LOS HOGARES COMO EMPLEADORES; ACTIVIDADES DE PRODUCCIÓN DE BIENES Y SERVICIOS NO DIFERENCIADOS DE LOS HOGARES PARA USO PROPIO",
                          "ACTIVIDADES DE ORGANIZACIONES Y ORGANISMOS EXTRATERRITORIALES"), disabled=True)
            st.date_input("Fecha actual", format="DD/MM/YYYY", disabled=True)
            st.text_area("Información Additional", disabled=True)

        else:
            # Si no hay coincidencia, permitir la entrada de datos
            cif = st.text_input("CIF:")
            email = st.text_input("Dirección de correo electrónico:")
            email_warning = False

            # Validar en tiempo real el formato del correo electrónico
            if email and "@" not in email:
                email_warning = True
                st.warning("¡No es una dirección de correo electrónico válida!")

            if not email_warning:
                email = Transform.lowercase_letters(email)
                phone = st.number_input("Número de teléfono:", step=1)
                address = st.text_input("Dirección:")
                address  = Transform.capital_letters(address)
                code = st.number_input("Código postal:", step=1)
                municipality = st.text_input("Municipio:")
                municipality = Transform.capital_letters(municipality)
                city = st.text_input("Provincia:")
                city = Transform.capital_letters(city)
                country = st.text_input("País:")
                country = Transform.capital_letters(country)
                n_employees = st.number_input("Número de empleados:", step=1)
                industry = st.selectbox("Industria",
                                        ("AGRICULTURA, SILVICULTURA Y PESCA", "MINERÍA Y CANTERAS", "MANUFACTURAS",
                                         "SUMINISTRO DE ELECTRICIDAD, GAS, VAPOR Y AIRE ACONDICIONADO",
                                         "ABASTECIMIENTO DE AGUA; ALCANTARILLADO, GESTIÓN DE RESIDUOS Y ACTIVIDADES DE REMEDIACIÓN",
                                         "CONSTRUCCIÓN", "COMERCIO AL POR MAYOR Y AL POR MENOR; REPARACIÓN DE VEHÍCULOS DE MOTOR Y MOTOCICLETAS",
                                         "TRANSPORTE Y ALMACENAMIENTO", "ACTIVIDADES DE ALOJAMIENTO Y SERVICIO DE ALIMENTACIÓN",
                                         "INFORMACIÓN Y COMUNICACIÓN", "ACTIVIDADES FINANCIERAS Y DE SEGUROS",
                                         "ACTIVIDADES INMOBILIARIAS", "ACTIVIDADES PROFESIONALES, CIENTÍFICAS Y TÉCNICAS",
                                         "ACTIVIDADES DE SERVICIOS ADMINISTRATIVOS Y DE APOYO",
                                         "ADMINISTRACIÓN PÚBLICA Y DEFENSA; SEGURIDAD SOCIAL OBLIGATORIA",
                                         "EDUCACIÓN", "ACTIVIDADES DE SALUD HUMANA Y TRABAJO SOCIAL",
                                         "ARTES, ENTRETENIMIENTO Y RECREACIÓN", "OTRAS ACTIVIDADES DE SERVICIO",
                                         "ACTIVIDADES DE LOS HOGARES COMO EMPLEADORES; ACTIVIDADES DE PRODUCCIÓN DE BIENES Y SERVICIOS NO DIFERENCIADOS DE LOS HOGARES PARA USO PROPIO",
                                         "ACTIVIDADES DE ORGANIZACIONES Y ORGANISMOS EXTRATERRITORIALES"))
                date = st.date_input("Fecha actual", format="DD/MM/YYYY")
                info = st.text_area("Información Adicional")
                info = Transform.capital_letters(info)

                # Preparar datos para guardar
                date_str = date.strftime("%Y-%m-%d")
                ingestion_date = datetime.now()
                ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")
                customer_id = str(uuid4())
                version = 1

                row = [customer_id, transformed_name, cif, email, phone, address, code, municipality, city, country, n_employees, industry, date_str, info, version, ingestion_date_str]

        # Mover el botón dentro del bloque del formulario
        submit_button = st.form_submit_button(label='¡Listo!')

        # Acciones después de enviar el formulario
        if submit_button and transformed_name not in names_list and not email_warning:
            Load().append_row("Informacion_de_clientes", "clientes", row)
            st.success("¡Guardado con éxito!")
