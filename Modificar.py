from utils.transform import Transform
from utils.extract import Extract
from utils.load import Load
from datetime import datetime
import streamlit as st

def app():

    st.header('Formulario de nuevos clientes')

    # Cargar los datos
    data = Extract.load_data("Informacion_de_clientes", "clientes")

    # Extraer valores únicos de la columna 'nombre'
    df_unique = data['razón_social'].drop_duplicates()
    names_list = df_unique.unique()

    # Seleccionar la compañía fuera del formulario para que sea dinámico
    company_name = st.selectbox("Compañía:", tuple(names_list),index=False)

    # Filtrar los datos con base en el nombre de la compañía seleccionado
    if company_name:
        df_filtered = data[data['razón_social'] == company_name]

        # Mostrar los detalles del cliente con la versión máxima
        df_max_v = df_filtered.loc[df_filtered['versión'].idxmax()]

        st.write(f"Has seleccionado la compañía: {df_max_v['razón_social']}")

        # Lista de campos modificables
        fields = [
            "CIF", "Email", "Teléfono", "Dirección",
            "Código Postal", "Municipio", "Provincia",
            "País", "Número de empleados", "Industria"
        ]

        email_warning = False

        # Crear multiselect para que el usuario elija los campos a modificar
        selected_fields = st.multiselect("Seleccione los campos que desea modificar:", fields)

        # Crear formulario de Streamlit dentro del bloque condicional
        with st.form(key='company_form', clear_on_submit=True):

            # Campos seleccionados para modificar
            cif = df_max_v['cif']
            if "CIF" in selected_fields:
                cif = st.text_input(f"CIF (Actual: {df_max_v['cif']}):")

            email = df_max_v['correo_electrónico']
            if "Email" in selected_fields:
                email = st.text_input(f"Email (Actual: {df_max_v['correo_electrónico']}):")
                email_warning = False
                # Validar en tiempo real el formato del correo electrónico
                if "@" not in email:
                    email_warning = True
                    st.warning("¡No es una dirección de correo electrónico válida!")
                if not email_warning and email:
                    email = Transform.lowercase_letters(email)

            phone = df_max_v['teléfono']
            if "Teléfono" in selected_fields:
                phone_input = st.number_input(f"Teléfono (Actual: {df_max_v['teléfono']}):",step=1)
                # Check for empty input before conversion
                phone = int(phone_input) if phone_input else df_max_v['teléfono']

            address = df_max_v['domicilio']
            if "Dirección" in selected_fields:
                address = st.text_input(f"Dirección (Actual: {df_max_v['domicilio']}):")
                address = Transform.capital_letters(address)

            code = df_max_v['codigo_postal']
            if "Código Postal" in selected_fields:
                code_input = st.number_input(f"Código Postal (Actual: {df_max_v['codigo_postal']}):",step=1)
                # Check for empty input before conversion
                code = int(code_input) if code_input else df_max_v['codigo_postal']

            municipality = df_max_v['municipio']
            if "Municipio" in selected_fields:
                municipality = st.text_input(f"Municipio (Actual: {df_max_v['municipio']}):")
                municipality = Transform.capital_letters(municipality)

            city = df_max_v['provincia']
            if "Provincia" in selected_fields:
                city = st.text_input(f"Provincia (Actual: {df_max_v['provincia']}):")
                city = Transform.capital_letters(city)

            country = df_max_v['país']
            if "País" in selected_fields:
                country = st.text_input(f"País (Actual: {df_max_v['país']}):")
                country = Transform.capital_letters(country)

            n_employees = df_max_v['n_empleados']
            if "Número de empleados" in selected_fields:
                n_employees_input = st.number_input(f"Número de empleados (Actual: {df_max_v['n_empleados']}):",step=1)
                # Check for empty input before conversion
                n_employees = int(n_employees_input) if n_employees_input else df_max_v['n_empleados']

            industry = df_max_v['industria']
            if "Industria" in selected_fields:
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

            # Campos adicionales
            date = st.date_input("Fecha actual", format="DD/MM/YYYY")
            info = st.text_area("Información Adicional")
            info = Transform.capital_letters(info)

            # Preparar datos para guardar
            date_str = date.strftime("%Y-%m-%d")
            ingestion_date = datetime.now()
            ingestion_date_str = ingestion_date.strftime("%Y-%m-%d %H:%M:%S")

            # Convertir valores numéricos de pandas a tipos nativos de Python
            customer_id = str(df_max_v['cliente_id'])
            version = int(df_max_v['versión']) + 1

            row = [customer_id, company_name, cif, email, phone, address, code, municipality, city, country, n_employees, industry, date_str, info, version, ingestion_date_str]

            # Botón de envío
            submit_button = st.form_submit_button(label='¡Listo!')

            # Acciones después de enviar el formulario
            if submit_button and not email_warning:
                Load().append_row("Informacion_de_clientes", "clientes", row)
                st.success("¡Guardado con éxito!")
