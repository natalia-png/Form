import os
from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cargar variables de entorno desde un archivo .env
load_dotenv()

app = Flask(__name__)

# Verificar que FLASK_SECRET_KEY esté configurada
if not os.getenv('FLASK_SECRET_KEY'):
    raise RuntimeError("FLASK_SECRET_KEY no está configurada. Asegúrate de configurarla en Render o en .env.")

app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Ahora se toma de variables de entorno

# Configuración de Google Sheets según el entorno
if os.getenv("RENDER"):  # Detectar si estamos en Render
    SERVICE_ACCOUNT_FILE = "/etc/secrets/clientes-registrados.json"
else:  # Configuración local
    SERVICE_ACCOUNT_FILE = "clientes-registrados.json"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

try:
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open('Clientes Registrados')
    worksheet = spreadsheet.sheet1
except Exception as e:
    print(f"Error en la conexión con Google Sheets: {e}")

# Función para enviar notificaciones por correo electrónico
def enviar_notificacion():
    sender_email = "nataliarubio@hye-arquitectos.online"
    sender_password = "Nataliarubio22"
    recipient_email = "nataliarubio@hye-arquitectos.online"  # Cambiar por el destinatario deseado
    smtp_server = "smtp.zoho.com"
    smtp_port = 465

    try:
        # Crear el mensaje del correo
        mensaje = MIMEMultipart()
        mensaje["From"] = sender_email
        mensaje["To"] = recipient_email
        mensaje["Subject"] = "Nuevo registro en Clientes Registrados"
        body = """
        Se ha registrado un nuevo cliente en la base de datos.
        Por favor, verifique los detalles en Google Sheets.
        """
        mensaje.attach(MIMEText(body, "plain"))

        # Conectar al servidor SMTP y enviar el correo
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, mensaje.as_string())
            print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

@app.route('/')
def formulario():
    return render_template('form.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        # Capturar los datos del formulario
        tipo_cliente = request.form.get('tipo_cliente')
        identificacion = request.form.get('identificacion')
        nombre_empresa = request.form.get('nombre_empresa')
        nit = request.form.get('nit')
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        motivo = request.form.get('motivo')
        aceptar_contrato = request.form.get('aceptar-contrato')

        # Validar que se haya aceptado el contrato
        if not aceptar_contrato:
            flash('Debe aceptar el tratamiento de datos para continuar.', 'error')
            return redirect(url_for('formulario'))

        # Validar campos requeridos
        if tipo_cliente == "particular" and not identificacion:
            flash('El número de identificación es obligatorio para clientes particulares.')
            return redirect(url_for('formulario'))

        if tipo_cliente == "empresa" and (not nombre_empresa or not nit):
            flash('El nombre de la empresa y el NIT son obligatorios para empresas.')
            return redirect(url_for('formulario'))

        # Ajustar valores según el tipo de cliente
        if tipo_cliente == "particular":
            nombre_empresa = ""
            nit = ""
        elif tipo_cliente == "empresa":
            identificacion = ""

        # Procesar el registro en Google Sheets
        worksheet.append_row([
            tipo_cliente, 
            identificacion, 
            nombre_empresa, 
            nit, 
            nombre, 
            email, 
            telefono, 
            motivo
        ])

        # Enviar notificación por correo
        enviar_notificacion()

        # Confirmar que se completó
        flash('El registro se ha enviado exitosamente.', 'success')
        return redirect(url_for('formulario'))

    except Exception as e:
        flash(f'Ocurrió un error al registrar los datos: {e}', 'error')
        return redirect(url_for('formulario'))

if __name__ == '__main__':
    app.run(debug=True)
