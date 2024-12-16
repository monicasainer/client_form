from utils.transform import Transform
from utils.extract import Extract
from utils.load import Load
from datetime import datetime
from uuid import uuid4
import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas



def app():
    st.header('Formulario de nuevos clientes')

    # Cargar los datos
    data = Extract.load_data("Informacion_de_clientes", "clientes")
    albaran = Extract.load_data("Informacion_de_clientes", "albarán")
    # Extraer valores únicos de la columna 'nombre'
    df_unique = data['razón_social'].drop_duplicates()
    names_list = df_unique.unique()

    opciones = ["Cliente Nuevo", "Cliente Habitual"]

    # Select fields to modify
    selected_fields = st.selectbox("Seleccione los campos que desea modificar:", opciones,index=None)

    if selected_fields == "Cliente Habitual":
        # Select company name outside of the form
        company_name = st.selectbox("Compañía:", tuple(names_list), index=None)

        if company_name:
            # Filter data based on selected company name
            df_filtered = data[data['razón_social'] == company_name]

            if not df_filtered.empty:  # Check if df_filtered is not empty
                df_max_v = df_filtered.loc[df_filtered['versión'].idxmax()]
                cliente_id = df_filtered['cliente_id'].unique()[0]
                print(cliente_id)
                # Display selected company details
                st.write(f"Has seleccionado la compañía: {df_max_v['razón_social']}")
                try:
                    # Convert the column to numeric, forcing errors to NaN (useful for cleaning)
                    albaran['albarán_id'] = pd.to_numeric(albaran['albarán_id'], errors='coerce')

                    # Now calculate the max and ensure it's not NaN
                    albaran_id = int(albaran['albarán_id'].max()) + 1 if not albaran['albarán_id'].isna().all() else 1
                except ValueError as e:
                    # Handle the case where the conversion fails entirely
                    albaran_id = 1  # Default to 1 if there's an error

                st.write("""El DNI y la firma previstos a continuación se utilizarán únicamente para la creación del albarán.
                             En ningún caso se almacenarán individualmente, ni se utilizarán para otros fines distintos al anteriormente descrito.
                             La información prevista sobre la empresa, serán utilizados únicamente para mejorar nuestros servicios.""")
                consent = st.checkbox("Acepto")

                # Dynamically handle the number of tasks
                date = st.date_input("Fecha actual", value=datetime.now())
                num_tasks = st.number_input('¿Cuántas tareas quieres añadir?', min_value=1, step=1)

                list_rows = []
                tasks_row =[]
                for i in range(int(num_tasks)):
                    task_name = st.text_input(f'Describe la tarea {i + 1}:', key=f'task_name_{i}')
                    task_value = st.number_input(f'¿Cuántas horas ha tomado la tarea {i + 1}?', key=f'task_value_{i}', min_value=0)
                    truck = st.selectbox(f'Indica el camión para la tarea {i + 1}:', ("Camión 1", "Camión 2", "Camión 3"), key=f'truck_{i}')
                    driver = st.selectbox(f'Indica el chófer para la tarea {i + 1}:', ("Chófer 1", "Chófer 2", "Chófer 3"), key=f'driver_{i}')
                    new_list = [i+1,task_name,task_value]
                    print (new_list)
                    tasks_row.append(new_list)
                    # Prepare row for each task
                    email = df_max_v['correo_electrónico']
                    date_str = date.strftime("%Y-%m-%d")
                    ingestion_date = datetime.now()
                    ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")

                    row = [int(albaran_id), df_max_v['cliente_id'], company_name, email, task_name, task_value, truck, driver, date_str, consent,ingestion_date_str]
                    list_rows.append(row)
                print(tasks_row)
                if consent:
                    dni = st.text_input("Escribe tu DNI:")
                # Create a canvas component
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                    stroke_width=3,#stroke_width,
                    stroke_color='#000',#stroke_color,
                    background_color='White',#bg_color,
                    update_streamlit=True,
                    height=150,
                    drawing_mode="freedraw",
                    point_display_radius= 0,
                    key="app",
                )

                # Form for submission
                with st.form(key='company_form', clear_on_submit=True):
                    submit_button = st.form_submit_button(label='¡Listo!')

                    if submit_button and consent and canvas_result.image_data is not None:
                        for element in list_rows:
                            Load().append_row("Informacion_de_clientes", "albarán", element)


                        customer_details ={
                            "[Company]":str(company_name),
                            "[Address]":str(df_max_v['domicilio']),
                            "[Municipality]":str(df_max_v['municipio']),
                            "[City]":str(df_max_v['provincia']),
                            "[Phone]":str(df_max_v['teléfono']),
                            "[Email]":str(df_max_v['correo_electrónico']),
                            "[albarán_id]": str(albaran_id),
                            "[Date]":str(date_str),
                            "[Time]": str(ingestion_date.strftime("%H:%M:%S"))
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(cliente_id))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        n_tareas= len(tasks_row)
                        # Create the dictionary
                        result_dict = {}

                        for i in range(n_tareas):
                            result_dict[f"[Tarea {i+1}]"] = str(i +1)
                            result_dict[f"[Descripcion {i+1}]"] = str(tasks_row[i][1])  # Second element (description)
                            result_dict[f"[Horas {i+1}]"] = str(tasks_row[i][2])       # Third element (hours)
                            result_dict["[dni]"] = str(dni)

                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        Extract.remove_unnecesary_rows(new_document_id)
                        image_id, image_link= Load.upload_image_to_google_drive(canvas_result)
                        Load.insert_image_in_document(new_document_id, image_link)
                        Extract.delete_file_from_image_url(image_link)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        Extract.delete_file_from_google_drive(new_document_id)

                        st.success("¡Guardado con éxito!")

                    elif submit_button and consent==False:

                        for element in list_rows:
                            Load().append_row("Informacion_de_clientes", "albarán", element)
                        customer_details ={
                            "[Company]":str(company_name),
                            "[Address]":str(df_max_v['domicilio']),
                            "[Municipality]":str(df_max_v['municipio']),
                            "[City]":str(df_max_v['provincia']),
                            "[Phone]":str(df_max_v['teléfono']),
                            "[Email]":str(df_max_v['correo_electrónico']),
                            "[albarán_id]": str(albaran_id),
                            "[Date]":str(date_str),
                            "[Time]": str(ingestion_date.strftime("%H:%M:%S"))
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(cliente_id))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        n_tareas= len(tasks_row)
                        # Create the dictionary
                        result_dict = {}

                        for i in range(n_tareas):
                            result_dict[f"[Tarea {i+1}]"] = str(i +1)
                            result_dict[f"[Descripcion {i+1}]"] = str(tasks_row[i][1])  # Second element (description)
                            result_dict[f"[Horas {i+1}]"] = str(tasks_row[i][2])       # Third element (hours)
                            result_dict["[dni]"] = str(" ")

                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        Extract.remove_unnecesary_rows(new_document_id)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        Extract.delete_file_from_google_drive(new_document_id)

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

                try:
                    # Convert the column to numeric, forcing errors to NaN (useful for cleaning)
                    albaran['albarán_id'] = pd.to_numeric(albaran['albarán_id'], errors='coerce')

                    # Now calculate the max and ensure it's not NaN
                    albaran_id = int(albaran['albarán_id'].max()) + 1 if not albaran['albarán_id'].isna().all() else 1
                except ValueError as e:
                    # Handle the case where the conversion fails entirely
                    albaran_id = 1  # Default to 1 if there's an error


                st.write("""El DNI previsto a continuación y la firma se utilizarán únicamente para la creación del albarán.
                             En ningún caso se almacenarán individualmente, ni se utilizarán para otros fines distintos al anteriormente descrito.
                             La información prevista sobre la empresa, serán utilizados únicamente para mejorar nuestros servicios.""")

                consent = st.checkbox("Acepto")

                # Prepare data for saving
                date_str = date.strftime("%Y-%m-%d")
                ingestion_date = datetime.now()
                ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")
                customer_id = str(uuid4())
                version = 1

                row_creation = [customer_id, transformed_name, cif, email, phone, address, code, municipality, city, country, n_employees, industry, date_str, info, version, ingestion_date_str]

                num_tasks = st.number_input('¿Cuántas tareas quieres añadir?', min_value=1, step=1)

                list_rows = []
                tasks_row =[]
                for i in range(int(num_tasks)):
                    task_name = st.text_input(f'Describe la tarea {i + 1}:', key=f'task_name_{i}')
                    task_value = st.number_input(f'¿Cuántas horas ha tomado la tarea {i + 1}?', key=f'task_value_{i}', min_value=0)
                    truck = st.selectbox(f'Indica el camión para la tarea {i + 1}:', ("Camión 1", "Camión 2", "Camión 3"), key=f'truck_{i}')
                    driver = st.selectbox(f'Indica el chófer para la tarea {i + 1}:', ("Chófer 1", "Chófer 2", "Chófer 3"), key=f'driver_{i}')
                    new_list = [i+1,task_name,task_value]
                    print (new_list)
                    tasks_row.append(new_list)
                    # Prepare row for each task
                    email = email
                    date_str = date.strftime("%Y-%m-%d")
                    ingestion_date = datetime.now()
                    ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")

                    row = [int(albaran_id), customer_id, transformed_name, email, task_name, task_value, truck, driver, date_str, consent,ingestion_date_str]
                    list_rows.append(row)
                print(tasks_row)
                if consent:
                    dni = st.text_input("Escribe tu DNI:")
                # Create a canvas component
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                    stroke_width=3,#stroke_width,
                    stroke_color='#000',#stroke_color,
                    background_color='White',#bg_color,
                    update_streamlit=True,
                    height=150,
                    drawing_mode="freedraw",
                    point_display_radius= 0,
                    key="app",
                )

                # Form for submission
                with st.form(key='company_form', clear_on_submit=True):
                    submit_button = st.form_submit_button(label='¡Listo!')

                    if submit_button and consent and canvas_result.image_data is not None:
                        Load().append_row("Informacion_de_clientes", "clientes", row_creation)
                        for element in list_rows:
                            Load().append_row("Informacion_de_clientes", "albarán", element)

                        customer_details ={
                            "[Company]":str(transformed_name),
                            "[Address]":str(address),
                            "[Municipality]":str(municipality),
                            "[City]":str(city),
                            "[Phone]":str(phone),
                            "[Email]":str(email),
                            "[albarán_id]": str(albaran_id),
                            "[Date]":str(date_str),
                            "[Time]": str(ingestion_date.strftime("%H:%M:%S"))
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(customer_id))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        n_tareas= len(tasks_row)
                        # Create the dictionary
                        result_dict = {}

                        for i in range(n_tareas):
                            result_dict[f"[Tarea {i+1}]"] = str(i +1)
                            result_dict[f"[Descripcion {i+1}]"] = str(tasks_row[i][1])  # Second element (description)
                            result_dict[f"[Horas {i+1}]"] = str(tasks_row[i][2])       # Third element (hours)
                            result_dict["[dni]"] = str(dni)

                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        Extract.remove_unnecesary_rows(new_document_id)
                        image_id, image_link= Load.upload_image_to_google_drive(canvas_result)
                        Load.insert_image_in_document(new_document_id, image_link)
                        Extract.delete_file_from_image_url(image_link)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        Extract.delete_file_from_google_drive(new_document_id)

                        st.success("¡Guardado con éxito!")

                    elif submit_button and consent==False:
                        Load().append_row("Informacion_de_clientes", "clientes", row_creation)
                        for element in list_rows:
                            Load().append_row("Informacion_de_clientes", "albarán", element)
                        customer_details ={
                            "[Company]":str(transformed_name),
                            "[Address]":str(address),
                            "[Municipality]":str(municipality),
                            "[City]":str(city),
                            "[Phone]":str(phone),
                            "[Email]":str(email),
                            "[albarán_id]": str(albaran_id),
                            "[Date]":str(date_str),
                            "[Time]": str(ingestion_date.strftime("%H:%M:%S"))
                        }
                        folder_id = st.secrets["folder_id"]

                        document_id = Load.upload_to_drive('template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ,folder_id,str(customer_id))
                        Transform.rename_file_in_drive(document_id,albaran_id,date_str)
                        new_document_id = Transform.convert_to_google_docs(document_id, True)
                        Load.replace_placeholders_in_doc(new_document_id,customer_details)

                        n_tareas= len(tasks_row)
                        # Create the dictionary
                        result_dict = {}

                        for i in range(n_tareas):
                            result_dict[f"[Tarea {i+1}]"] = str(i +1)
                            result_dict[f"[Descripcion {i+1}]"] = str(tasks_row[i][1])  # Second element (description)
                            result_dict[f"[Horas {i+1}]"] = str(tasks_row[i][2])       # Third element (hours)
                            result_dict["[dni]"] = str(" ")

                        print(result_dict)
                        Load.replace_placeholders_in_doc(new_document_id,result_dict)
                        Extract.remove_unnecesary_rows(new_document_id)
                        Transform.convert_doc_to_pdf_and_save(new_document_id,f"{albaran_id}_{date_str}")
                        Extract.delete_file_from_google_drive(new_document_id)

                        st.success("¡Guardado con éxito!")

# Run the app
if __name__ == "__main__":
    app()
