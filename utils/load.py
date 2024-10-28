from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from gspread import authorize
import streamlit as st
from io import BytesIO
from PIL import Image

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
        # path = os.getenv("PATH_TO_CREDENTIALS")

        # credentials = service_account.Credentials.from_service_account_file(f"{path}", scopes=scope)

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

    def upload_to_drive(file_name, mime_type, folder_id, client_id) -> str:
        """
        Copies a specified file in Google Drive to a subfolder for a given client.
        Creates the subfolder if it doesn't exist.

        Args:
            folder_id (str): The ID of the parent folder where the client's folder is located.
            client_id (str): Identifier for the client, used to name the subfolder.
            file_name (str): Name of the file to copy into the client-specific folder.

        Environment:
            PATH_TO_CREDENTIALS (str): Path to the Google API credentials file.

        Returns:
            str: The ID of the copied file in the client's subfolder.

        Raises:
            Exception: If the specified file is not found in the parent folder.
        """
        # Authenticate using the service account credentials

        # path = os.getenv("PATH_TO_CREDENTIALS")
        scope = ["https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"]

        creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope)

        # Load the credentials
        # creds = service_account.Credentials.from_service_account_file(path, scopes=scope)
        drive_service = build('drive', 'v3', credentials=creds)

        # Check if the subfolder (with client_id) exists
        query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{client_id}' and trashed = false"
        response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()

        # If the folder exists, get its ID
        if len(response.get('files')) > 0:
            client_folder_id = response['files'][0]['id']
        else:
            # If the folder does not exist, create it
            folder_metadata = {
                'name': client_id,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [folder_id]
            }
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            client_folder_id = folder.get('id')

        # Search for the file by name in the specified folder (folder_id)
        search_query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
        search_response = drive_service.files().list(q=search_query, fields='files(id, name)').execute()

        if len(search_response.get('files')) == 0:
            raise Exception(f"File '{file_name}' not found in folder with ID '{folder_id}'")

        # Get the file ID of the file to be copied
        file_id = search_response['files'][0]['id']

        # Now we will copy the existing Google Docs file into the client's folder
        file_metadata = {
            'parents': [client_folder_id]  # Copy to the client folder
        }

        # Perform the copy operation
        copied_file = drive_service.files().copy(fileId=file_id, body=file_metadata).execute()

        return copied_file.get('id')

    def replace_placeholders_in_doc(document_id, customer_details) -> None:
        """
        Replaces placeholders in a Google Doc with customer-specific/tasks specific details.

        Args:
            document_id (str): The ID of the Google Document.
            customer_details (dict): Mapping of placeholders to replacement text.

        Returns:
            None
        """
        scope = ["https://www.googleapis.com/auth/documents"]
        # path = os.getenv("PATH_TO_CREDENTIALS")
        # Load the credentials
        creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope)

        # creds = service_account.Credentials.from_service_account_file(path, scopes=scope)
        doc_service = build('docs', 'v1', credentials=creds)

        # Fetch the document content
        document = doc_service.documents().get(documentId=document_id).execute()
        content = document.get('body').get('content', [])

        # Prepare a list of requests for each placeholder
        requests = []

        for element in content:
            # Loop through the document content, looking for table cells
            if 'table' in element:
                table = element['table']
                for row in table['tableRows']:
                    for cell in row['tableCells']:
                        for paragraph in cell['content']:
                            if 'paragraph' in paragraph:
                                for element in paragraph['paragraph']['elements']:
                                    if 'textRun' in element:
                                        text = element['textRun']['content']
                                        # Replace placeholders in text with corresponding values
                                        for placeholder, replacement in customer_details.items():
                                            if placeholder in text:
                                                requests.append({
                                                    'replaceAllText': {
                                                        'containsText': {
                                                            'text': placeholder,
                                                            'matchCase': True
                                                        },
                                                        'replaceText': replacement
                                                    }
                                                })
                # Handle paragraphs outside of tables
            elif 'paragraph' in element:
                for paragraph in element['paragraph']['elements']:
                    if 'textRun' in paragraph:
                        text = paragraph['textRun']['content']
                        # Replace placeholders in text with corresponding values
                        for placeholder, replacement in customer_details.items():
                            if placeholder in text:
                                requests.append({
                                    'replaceAllText': {
                                        'containsText': {
                                            'text': placeholder,
                                            'matchCase': True
                                        },
                                        'replaceText': replacement
                                    }
                                })
        # Execute the batch update with all replacement requests
        if requests:
            result = doc_service.documents().batchUpdate(
                documentId=document_id, body={'requests': requests}
            ).execute()

            print(f"Replaced {len(requests)} placeholders in the document.")
        else:
            print("No placeholders found.")

    def upload_image_to_google_drive(canvas_result)->tuple:
        """
        Uploads an image from a BytesIO buffer to Google Drive, makes it publicly accessible,
        and returns its ID and public URL.

        Args:
            canvas_result: Object containing the image data as a NumPy array.

        Returns:
            tuple: (str, str) The Google Drive file ID and public URL of the uploaded image.
        """

        # path = os.getenv("PATH_TO_CREDENTIALS")
        scope =["https://www.googleapis.com/auth/drive"]

        # Load credentials
        # creds = service_account.Credentials.from_service_account_file(
        #     path, scopes=["https://www.googleapis.com/auth/drive"]
        # )
        creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope)


        drive_service = build('drive', 'v3', credentials=creds)

        img_data = canvas_result.image_data
        im = Image.fromarray(img_data.astype("uint8"), mode="RGBA")

        background = Image.new("RGBA", im.size, "WHITE")
        im = Image.alpha_composite(background, im).convert("RGB")  # Convert to "RGB" to remove alpha

                                # Save the image temporarily
        # Save image in-memory to upload
        buffered = BytesIO()
        im.save(buffered, format="PNG")
        buffered.seek(0)

        # Define the file metadata for Drive
        folder_id = st.secrets["folder_id"]
        file_metadata = {
            "name": "your_image.png",  # Name of the file in Google Drive
            "parents": [str(folder_id)]    # Specify the folder to upload to
        }

        # Upload the image to Google Drive
        media = MediaIoBaseUpload(buffered, mimetype="image/png")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        # Make the image publicly accessible

        image_id = file.get("id")
        drive_service.permissions().create(
            fileId=image_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()
        image_link = f"https://drive.google.com/uc?export=view&id={image_id}"  # Direct link to view the image
        return image_id, image_link

    def insert_image_in_document(document_id, image_link)->None:
        """
        Inserts an image at the end of a Google Doc and centers it.

        Args:
            document_id (str): ID of the Google Document.
            image_link (str): Public URL of the image to insert.

        Returns:
            None
        """

        # path = os.getenv("PATH_TO_CREDENTIALS")
        scope = ["https://www.googleapis.com/auth/documents"]

        # Load the credentials
        creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope)
        # creds = service_account.Credentials.from_service_account_file(path, scopes=scope)
        doc_service = build('docs', 'v1', credentials=creds)

        document = doc_service.documents().get(documentId=document_id).execute()
        end_index = document['body']['content'][-1]['endIndex'] - 1
        # Prepare requests for inserting image in Google Doc
        requests = [
            # Insert image at the end of the document
            {
                "insertInlineImage": {
                    "location": {
                        "index": end_index,  # 1 is the start, use -1 for the end
                    },
                    "uri": image_link,
                    "objectSize": {
                        "height": {"magnitude": 300, "unit": "PT"},  # Adjust as needed
                        "width": {"magnitude": 300, "unit": "PT"}
                    }
                }
            },
            # Center the image
            {
                "updateParagraphStyle": {
                    "range": {
                        "startIndex": end_index,
                        "endIndex": end_index + 1
                    },
                    "paragraphStyle": {
                        "alignment": "CENTER"
                    },
                    "fields": "alignment"
                }
            }
        ]

        # Execute requests to insert and center the image
        doc_service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()

        print("Image uploaded and added to the document successfully!")
