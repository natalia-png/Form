from google.oauth2.service_account import Credentials
import gspread

# Archivo JSON de la cuenta de servicio
SERVICE_ACCOUNT_FILE = 'clientes-registrados.json'

# Scopes necesarios para Google Sheets y Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

try:
    # Autenticación con la cuenta de servicio
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)

    # Abrir la hoja de cálculo
    spreadsheet = gc.open('Clientes Registrados')
    print("Conexión exitosa a Google Sheets.")

    # Prueba de escritura en la hoja de cálculo
    worksheet = spreadsheet.sheet1
    worksheet.update('A1', [[ 'Conexión exitosa' ]])
    print("Dato escrito en Google Sheets correctamente.")

except Exception as e:
    print(f"Error: {e}")

