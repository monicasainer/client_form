from google.oauth2 import service_account
from gspread_pandas import Spread, Client
import pandas as pd
import os
import ssl
import streamlit as st

class Extract:
    def __init__(self) -> None:
        return None

    @st.cache_resource()
    def load_data(spreadsheet_name, worksheet_name):
        """
        Load data from Google Sheets.
        """
        # Disable SSL certificate verification (use with caution)
        # ssl._create_default_https_context = ssl._create_unverified_context

        # Define the scopes for Google Sheets and Google Drive access
        scope = ["https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"]

        # Load service account credentials from Streamlit secrets
        # credentials = service_account.Credentials.from_service_account_info(
        #     st.secrets["gcp_service_account"],
        #     scopes=scope
        # )
        # credentials = ServiceAccountCredentials.from_json_keyfile_name('testingdb-b6d4d-d0a2646c069a.json', scope)
        path= os.getenv('PATH_TO_CREDENTIALS')
        credentials = service_account.Credentials.from_service_account_file(f'{path}',  # Update this with the path to your JSON file
        scopes=scope)

        # Create a client to interact with Google Sheets using the credentials
        clients = Client(scope=scope, creds=credentials)

        # Define the name of the spreadsheet to access
        spreadsheet_name = "Informacion_de_clientes"

        # Create a Spread object to manage the spreadsheet
        spread = Spread(spreadsheet_name, client=clients)

        # Open the spreadsheet and retrieve the list of worksheets
        sh = clients.open(spreadsheet_name)
        worksheet_list = sh.worksheets()

        worksheet = sh.worksheet(worksheet_name)

        df = pd.DataFrame(worksheet.get_all_records())

        return df
