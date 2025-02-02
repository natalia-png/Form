from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'clientes-registrados.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

try:
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    print("El archivo JSON funciona correctamente.")
except Exception as e:
    print(f"Error con el archivo JSON: {e}")
