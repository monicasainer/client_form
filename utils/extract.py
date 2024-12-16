from google.oauth2 import service_account
from gspread_pandas import Spread, Client
from googleapiclient.discovery import build
import pandas as pd
import os
import re
import streamlit as st

class Extract:
    def __init__(self) -> None:
        return None

    @st.cache_resource()
    def load_data(spreadsheet_name, worksheet_name) -> None:
        """
        Load data from Google Sheets.
        """
        # Disable SSL certificate verification (use with caution)
        # ssl._create_default_https_context = ssl._create_unverified_context

        # Define the scopes for Google Sheets and Google Drive access
        scope = ["https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"]

        # credentials = service_account.Credentials.from_service_account_info(
        # st.secrets["gcp_service_account"], scopes=scope)

        path = os.getenv("PATH_TO_CREDENTIALS")

        credentials = service_account.Credentials.from_service_account_file(f"{path}", scopes=scope)

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
        df = df.reset_index(drop=True)

        return df

    def delete_file_from_google_drive(file_id):
        """
        Deletes a file from Google Drive using its file ID.

        Args:
            file_id (str): ID of the file to delete from Google Drive.

        Returns:
            None

        Raises:
            Exception: If an error occurs during deletion.
        """
        scopes = ["https://www.googleapis.com/auth/drive"]
        # creds = service_account.Credentials.from_service_account_info( st.secrets["gcp_service_account"], scopes=scopes)

        creds_path = os.getenv("PATH_TO_CREDENTIALS")
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=creds)

        try:
            drive_service.files().delete(fileId=file_id).execute()
            print(f"File with ID {file_id} deleted successfully.")
        except Exception as e:
            print(f"An error occurred while deleting the file: {e}")

    def delete_file_from_image_url(image_url) -> None:
        """
        Deletes a Google Drive file using the file ID extracted from an image URL.

        Args:
            image_url (str): Public URL of the image file in Google Drive.

        Returns:
            None

        Raises:
            ValueError: If no valid file ID is found in the provided URL.
        """

        # Extract the file ID from the image URL using a regular expression
        match = re.search(r"uc\?export=view&id=([a-zA-Z0-9_-]+)", image_url)
        if match:
            file_id = match.group(1)
            print(f"Extracted file ID: {file_id}")

            # Authenticate and delete the file
            Extract.delete_file_from_google_drive(file_id)
        else:
            print("No valid file ID found in the provided image URL.")

    def remove_unnecesary_rows(document_id)->None:
        """
        Removes rows containing specific placeholders from a Google Document.

        Args:
            document_id (str): ID of the Google Document to clean.

        Returns:
            None
        """

        path = os.getenv("PATH_TO_CREDENTIALS")
        scope = ["https://www.googleapis.com/auth/documents"]
        # creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)

        # Load the credentials
        creds = service_account.Credentials.from_service_account_file(path, scopes=scope)
        doc_service = build('docs', 'v1', credentials=creds)

        # Fetch the document content
        document = doc_service.documents().get(documentId=document_id).execute()
        content = document.get('body').get('content', [])

        pattern = r'\[\w+ \d+\]'
        # Function to extract text from Google Doc content
        def extract_text(content):
            text = ""
            for element in content:
                if 'paragraph' in element:
                    for paragraph_element in element['paragraph']['elements']:
                        if 'textRun' in paragraph_element:
                            text += paragraph_element['textRun']['content']
            return text

        # Extract text from content
        doc_text = extract_text(content)

        # Find all words with '[' or ']'
        words_with_brackets = re.findall(pattern, doc_text)
        print(words_with_brackets)
        requests = []
        def delete_text():
            for word in reversed(words_with_brackets):  # Start from the end of the list
                requests.append({
                    'replaceAllText': {
                        'replaceText': '' ,
                        'containsText': {
                            'text': word,
                            'matchCase': True
                        }
                    }
                })
            return requests
        # Send the batch request to delete all specified words
        requests=delete_text()
        result = doc_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        print("Delete requests executed:", result)

    def get_folder_id_of_document(document_id)-> str:
        """
        Retrieves the folder ID of a Google Document given its document ID.

        :param document_id: The ID of the Google Document.
        :param creds_path: The path to the service account credentials JSON file.
        :return: The folder ID if found, otherwise None.
        """
        scope=["https://www.googleapis.com/auth/drive"]
        # creds = service_account.Credentials.from_service_account_info(
        # st.secrets["gcp_service_account"], scopes=scope)

        creds_path = os.getenv("PATH_TO_CREDENTIALS")
        # Authenticate and create a service client for Google Drive
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=creds)

        try:
            # Retrieve the file metadata
            file_metadata = drive_service.files().get(fileId=document_id, fields="parents").execute()
            parents = file_metadata.get('parents', [])

            if parents:
                folder_id = parents[0]  # Get the first parent folder ID
                print(f"Folder ID for the document {document_id}: {folder_id}")
                return folder_id
            else:
                print(f"The document {document_id} is not in any folder.")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
