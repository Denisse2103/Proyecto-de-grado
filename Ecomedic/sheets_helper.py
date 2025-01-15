import gspread
from google.oauth2.service_account import Credentials

# Define el alcance de la API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def connect_to_sheets():
    # Ruta a las credenciales
    credentials = Credentials.from_service_account_file(
        'c:/Users/USER/Downloads/mi_proyecto/credentials.json',
        scopes=SCOPES
    )

    # Conéctate a Google Sheets
    client = gspread.authorize(credentials)
    return client
