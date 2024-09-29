from google.oauth2 import service_account
from gspread_pandas import Spread, Client
from gspread import authorize
import pandas as pd
import os
import ssl
import streamlit as st

class Load:
    def __init__(self) -> None:
        pass


    def append_row(self, spreadsheet_name: str, worksheet_name: str, row: list) -> None:
        """
        Append a new row to a specified worksheet in Google Sheets.

        Args:
            spreadsheet_name (str): Name of the spreadsheet.
            worksheet_name (str): Name of the worksheet (tab).
            row (list): A list representing the row to add.
        """
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]

        # Authenticate using the service account credentials
        credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope)

        # Authorize the client
        client = authorize(credentials)

        # Open the spreadsheet
        sh = client.open(spreadsheet_name)
        if not sh:
            raise ValueError(f"Spreadsheet '{spreadsheet_name}' not found.")

        # Open the worksheet by name
        worksheet = sh.worksheet(worksheet_name)
        if not worksheet:
            raise ValueError(f"Worksheet '{worksheet_name}' not found in spreadsheet '{spreadsheet_name}'.")

        # Append the row to the worksheet
        worksheet.append_row(row)
        print(f"Row appended: {row}")
