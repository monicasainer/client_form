from utils.transform import Transform
from utils.extract import Extract
from utils.load import Load
from datetime import datetime
import streamlit as st
from uuid import uuid4

import streamlit as st
import pandas as pd
from datetime import datetime


def app():
    st.header('Formulario de nuevos clientes')

    # Cargar los datos
    data = Extract.load_data("Informacion_de_clientes", "clientes")

    # Extraer valores únicos de la columna 'nombre'
    df_unique = data['nombre'].drop_duplicates()
    names_list = df_unique.unique()

    opciones = ["Cliente Nuevo", "Cliente Habitual"]

    # Select fields to modify
    selected_fields = st.selectbox("Seleccione los campos que desea modificar:", opciones,index=None)

    if selected_fields == "Cliente Habitual":
        # Select company name outside of the form
        company_name = st.selectbox("Compañía:", tuple(names_list), index=None)

        if company_name:
            # Filter data based on selected company name
            df_filtered = data[data['nombre'] == company_name]

            if not df_filtered.empty:  # Check if df_filtered is not empty
                df_max_v = df_filtered.loc[df_filtered['versión'].idxmax()]

                # Display selected company details
                st.write(f"Has seleccionado la compañía: {df_max_v['nombre']}")

                # Dynamically handle the number of tasks
                date = st.date_input("Fecha actual", value=datetime.now())
                num_tasks = st.number_input('¿Cuántas tareas quieres añadir?', min_value=1, step=1)

                list_rows = []
                for i in range(int(num_tasks)):
                    task_name = st.text_input(f'Describe la tarea {i + 1}:', key=f'task_name_{i}')
                    task_value = st.number_input(f'¿Cuántas horas ha tomado la tarea {i + 1}?', key=f'task_value_{i}', min_value=0)
                    truck = st.selectbox(f'Indica el camión para la tarea {i + 1}:', ("Camión 1", "Camión 2", "Camión 3"), key=f'truck_{i}')
                    driver = st.selectbox(f'Indica el chófer para la tarea {i + 1}:', ("Chófer 1", "Chófer 2", "Chófer 3"), key=f'driver_{i}')

                    # Prepare row for each task
                    email = df_max_v['correo_electrónico']
                    date_str = date.strftime("%Y-%m-%d")
                    ingestion_date = datetime.now()
                    ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")
                    row = [df_max_v['cliente_id'], company_name, email, task_name, task_value, truck, driver, date_str, ingestion_date_str]
                    list_rows.append(row)

                # Form for submission
                with st.form(key='company_form', clear_on_submit=True):
                    submit_button = st.form_submit_button(label='¡Listo!')

                    if submit_button:
                        for element in list_rows:
                            Load().append_row("Informacion_de_clientes", "albarán", element)
                        st.success("¡Guardado con éxito!")

            else:
                st.warning("No se encontraron datos para la compañía seleccionada.")

    elif selected_fields == "Cliente Nuevo":
        company_name = st.text_input("Nombre del nuevo cliente:")
        transformed_name = Transform.capital_letters(company_name)

        # Validar si el nombre ya existe
        if transformed_name in names_list and transformed_name:
            st.warning(f"¡La compañía '{transformed_name}' ya existe! Clica en 'Modificar'")

            # Disable other fields if the name already exists
            st.text_input("CIF:", disabled=True)
            st.text_input("Dirección de correo electrónico:", disabled=True)
            st.number_input("Número de teléfono:", step=1, disabled=True)
            st.text_input("Dirección:", disabled=True)
            st.number_input("Código postal:", step=1, disabled=True)
            st.text_input("Municipio:", disabled=True)
            st.text_input("Provincia:", disabled=True)
            st.text_input("País:", disabled=True)
            st.number_input("Número de empleados:", step=1, disabled=True)
            st.selectbox("Industria", (
                "AGRICULTURA, SILVICULTURA Y PESCA", "MINERÍA Y CANTERAS", "MANUFACTURAS",
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
            st.text_area("Información Adicional", disabled=True)

        else:
            # Allow data entry if no match
            cif = st.text_input("CIF:")
            email = st.text_input("Dirección de correo electrónico:")
            email_warning = False

            # Validate email format in real-time
            if email and "@" not in email:
                email_warning = True
                st.warning("¡No es una dirección de correo electrónico válida!")

            if not email_warning:
                email = Transform.lowercase_letters(email)
                phone = st.number_input("Número de teléfono:", step=1)
                address = st.text_input("Dirección:")
                address = Transform.capital_letters(address)
                code = st.number_input("Código postal:", step=1)
                municipality = st.text_input("Municipio:")
                municipality = Transform.capital_letters(municipality)
                city = st.text_input("Provincia:")
                city = Transform.capital_letters(city)
                country = st.text_input("País:")
                country = Transform.capital_letters(country)
                n_employees = st.number_input("Número de empleados:", step=1)
                industry = st.selectbox("Industria", (
                    "AGRICULTURA, SILVICULTURA Y PESCA", "MINERÍA Y CANTERAS", "MANUFACTURAS",
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

                # Prepare data for saving
                date_str = date.strftime("%Y-%m-%d")
                ingestion_date = datetime.now()
                ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")
                customer_id = str(uuid4())
                version = 1

                row_creation = [customer_id, transformed_name, cif, email, phone, address, code, municipality, city, country, n_employees, industry, date_str, info, version, ingestion_date_str]

                num_tasks = st.number_input('¿Cuántas tareas quieres añadir?', min_value=1, step=1)

                list_rows = []
                for i in range(int(num_tasks)):
                    task_name = st.text_input(f'Describe la tarea {i + 1}:', key=f'task_name_{i}')
                    task_name = Transform.capital_letters(task_name)
                    task_value = st.number_input(f'¿Cuántas horas ha tomado la tarea {i + 1}?', key=f'task_value_{i}', min_value=0)
                    truck = st.selectbox(f'Indica el camión para la tarea {i + 1}:', ("CAMION 1", "CAMION 2", "CAMION 3"), key=f'truck_{i}')
                    driver = st.selectbox(f'Indica el chófer para la tarea {i + 1}:', ("CHOFER 1", "CHOFER 2", "CHOFER 3"), key=f'driver_{i}')

                    # Prepare row for each task
                    email_address = email
                    date_str = date.strftime("%Y-%m-%d")
                    ingestion_date = datetime.now()
                    ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")
                    row = [customer_id, company_name, email_address, task_name, task_value, truck, driver, date_str, ingestion_date_str]
                    list_rows.append(row)

                # Form for submission
                with st.form(key='company_form', clear_on_submit=True):
                    submit_button = st.form_submit_button(label='¡Listo!')

                    if submit_button:
                        for element in list_rows:
                            Load().append_row("Informacion_de_clientes", "albarán", element)
                        Load().append_row("Informacion_de_clientes", "clientes", row_creation)
                        st.success("¡Guardado con éxito!")

# Run the app
if __name__ == "__main__":
    app()
