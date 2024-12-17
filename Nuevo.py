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
    df_unique = data['razón_social'].drop_duplicates()
    names_list = df_unique.unique()

    # Crear formulario de Streamlit

    company_name = st.text_input("Razón Social del nuevo cliente:")
    transformed_name = Transform.capital_letters(company_name)

    # Validar si el nombre ya existe
    if transformed_name in names_list and transformed_name:
        st.warning(f"¡La compañía '{transformed_name}' ya existe! Clica en 'Modificar'")

        # Deshabilitar el resto de los campos si el nombre ya existe
        st.text_input("Nombre persona contacto:", disabled=True)
        st.text_input("CIF:", disabled=True)
        st.text_input("Dirección de correo electrónico:", disabled=True)
        st.text_area("Otras direcciones de correo electrónico:", disabled=True)
        st.number_input("Número de teléfono:", step=1, disabled=True)
        st.number_input("Número de teléfono persona de contacto:", disabled=True)
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
        contact_name = st.text_input("Nombre persona contacto:")
        cif = st.text_input("CIF:")
        cif = Transform.capital_letters(cif)
        email = st.text_input("Dirección de correo electrónico:")
        other_emails = st.text_area("Otras direcciones de correo electrónico:")
        email_warning = False

        # Validar en tiempo real el formato del correo electrónico
        if email and "@" not in email:
            email_warning = True
            st.warning("¡No es una dirección de correo electrónico válida!")

        if not email_warning:
            contact_name = Transform.capital_letters(contact_name)
            email = Transform.lowercase_letters(email)
            other_emails = Transform.lowercase_letters(other_emails)
            phone = st.number_input("Número de teléfono:", step=1)
            contact_phone = st.number_input("Número de teléfono persona de contacto:",step=1)
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


            if transformed_name and email and phone and address and code and city and country:
                row = [customer_id, transformed_name, contact_name, cif, email, other_emails, phone, contact_phone,address, code, municipality, city, country, n_employees, industry, date_str, info, version, ingestion_date_str]
                saving_ready = True
            elif not transformed_name:
                st.warning("¡Revisa la razón social!")
                saving_ready = False
            elif not email:
                st.warning("¡Revisa el correo electrónico!")
                saving_ready = False
            elif not phone:
                st.warning("¡Revisa el número de teléfono!")
                saving_ready = False
            elif not address or not code or not city or not country or not municipality or not country:
                st.warning("¡Revisa la dirección!")
                saving_ready = False

    with st.form(key='company_form', clear_on_submit=False):
        # Mover el botón dentro del bloque del formulario
        submit_button = st.form_submit_button(label='¡Listo!')

        # Acciones después de enviar el formulario
        if submit_button and transformed_name not in names_list and not email_warning and saving_ready:
            Load().append_row("Informacion_de_clientes", "clientes", row)
            st.success("¡Guardado con éxito!")
        elif submit_button and (transformed_name in names_list or email_warning or not saving_ready):
            st.warning("¡Revisa los datos antes de guardar!")
