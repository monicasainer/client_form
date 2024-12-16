
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload,MediaIoBaseUpload
import streamlit as st
from utils.extract import Extract
from io import BytesIO
import os


class Transform:

    def __init__(self) -> None:
        return None

    def capital_letters(name) ->str:
        """
        Converts the input string to uppercase and ensures there is only one space between words.

        Args:
            name (str): The input string to be converted to uppercase.

        Returns:
            str: A new string with all characters in uppercase and only one space between words.
        """
        new_name = str(name).upper()
        words = new_name.split()
        cleaned_name = ' '.join(words)

        return cleaned_name

    def lowercase_letters(name) ->str:
        """
        Converts the input string to lowercase and ensures there is only one space between words.

        Args:
            name (str): The input string to be converted to lowercase.

        Returns:
            str: A new string with all characters in lowercase and only one space between words.
        """
        new_name = str(name).lower()
        words = new_name.split()
        cleaned_name = ' '.join(words)

        return cleaned_name

    def rename_file_in_drive(file_id,albaran_id,date_str)-> None:
        """
        Renames a file in Google Drive to "<albaran_id>_<date_str>" using its file ID.

        Args:
            file_id (str): The ID of the file in Google Drive to rename.
            albaran_id (str): Document ID for the new file name.
            date_str (str): Date string to append to the new file name.

        Environment:
            PATH_TO_CREDENTIALS (str): Path to Google API credentials file.

        Returns:
            None
        """
        path = os.getenv("PATH_TO_CREDENTIALS")
        scope = ["https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"]
        # creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)

        # Load the credentials
        creds = service_account.Credentials.from_service_account_file(path, scopes=scope)
        drive_service = build('drive', 'v3', credentials=creds)

        # New name for the file
        new_name = f"{albaran_id}_{date_str}"

        # Perform the rename operation
        file_metadata = {'name': new_name}
        updated_file = drive_service.files().update(
            fileId=file_id,
            body=file_metadata,
            fields='id, name'
        ).execute()

        print(f"File renamed successfully to: {updated_file.get('name')}")

    def convert_to_google_docs(file_id, delete_original=False) -> str:
        """
        Converts a DOCX file to Google Docs format and optionally deletes the original DOCX file.

        :param file_id: The file ID of the DOCX file to convert.
        :param drive_service: The authenticated Drive service object.
        :param delete_original: If True, deletes the original DOCX file after conversion.
        :return: The file ID of the newly created Google Docs file.
        """
        path = os.getenv("PATH_TO_CREDENTIALS")
        scope = ["https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"]

        # creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        # Load the credentials
        creds = service_account.Credentials.from_service_account_file(path, scopes=scope)
        drive_service = build('drive', 'v3', credentials=creds)
        # Define the Google Docs MIME type
        google_docs_mime_type = 'application/vnd.google-apps.document'

        # Convert the file by copying it to a new file in Google Docs format
        file_metadata = {
            'mimeType': google_docs_mime_type
        }

        # Copy the file and convert to Google Docs format
        converted_file = drive_service.files().copy(fileId=file_id, body=file_metadata).execute()

        print(f"File converted successfully. New Google Docs File ID: {converted_file['id']}")

        # Optionally delete the original DOCX file
        if delete_original:
            try:
                drive_service.files().delete(fileId=file_id).execute()
                print(f"Original DOCX file (ID: {file_id}) deleted successfully.")
            except Exception as e:
                print(f"An error occurred while deleting the original file: {e}")

        # Return the ID of the converted Google Docs file
        return converted_file['id']

    def convert_doc_to_pdf_and_save(document_id, pdf_name) -> None:
        """
        Exports a Google Document as a PDF and saves it to Google Drive.

        Args:
            document_id (str): ID of the Google Document to convert.
            pdf_name (str): Name for the saved PDF file.

        Returns:
            pdf_file_id (str): File ID of the created PDF.
        """
        # Authenticate and create service clients for Google Drive and Docs
        scope=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]
        # creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)

        creds_path = os.getenv("PATH_TO_CREDENTIALS")
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"]
         )
        drive_service = build("drive", "v3", credentials=creds)

        # Step 1: Export the Google Doc as a PDF
        pdf_file = BytesIO()
        request = drive_service.files().export_media(fileId=document_id, mimeType="application/pdf")
        downloader = MediaIoBaseDownload(pdf_file, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        pdf_file.seek(0)  # Reset the pointer to the beginning of the file

        # Step 2: Get the folder ID and upload the PDF to Google Drive
        folder_id = Extract.get_folder_id_of_document(document_id)
        pdf_metadata = {
            "name": f"{pdf_name}.pdf",  # Name the PDF file in Google Drive
            "parents": [folder_id]  # Specify the folder ID where it should be saved
        }
        media = MediaIoBaseUpload(pdf_file, mimetype="application/pdf")

        pdf_file_uploaded = drive_service.files().create(body=pdf_metadata, media_body=media, fields="id").execute()
        pdf_file_id = pdf_file_uploaded.get("id")
        print(f"PDF file saved to Google Drive with ID: {pdf_file_id}")
        return pdf_file_id
