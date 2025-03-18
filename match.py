import requests
import json
import urllib.parse
from tinder_client import TinderClient

def main():
    # ======= Paso 1: Autenticación =======
    phone_number = input("Ingresa tu número de teléfono (ej. +34123456789): ")
    print("Iniciando proceso de autenticación...")
    
    # Crear instancia del cliente de Tinder (asegúrate de que TinderClient esté configurado correctamente)
    client = TinderClient()
    
    # Inicia la autenticación vía SMS (authLogin)
    login_response = client.authLogin(phone_number)
    print("Respuesta de login:", login_response)
    
    # Ingresa el OTP recibido por SMS
    otp_phone = input("Ingresa el código OTP recibido por teléfono: ")
    otp_response = client.verifyOtp(phone_number, otp_phone)
    print("Respuesta de verificación OTP:", otp_response)
    
    # Si la respuesta indica que se requiere verificación por email, solicita el OTP de email
    if "validate_email_otp_state" in otp_response:
        otp_email = input("Ingresa el código OTP recibido por email: ")
        # Llama al método verifyEmail para enviar el OTP de email
        email_response = client.verifyEmail(otp_email)
        print("Respuesta de verificación de email:", email_response)
    
    # Llamar a getAuthToken() para obtener el token final de autenticación
    auth_response = client.getAuthToken()
    print("Respuesta de getAuthToken:", auth_response)
    
    if not client.xAuthToken:
        print("Error: No se pudo obtener el token de autenticación.")
        return
    print("Token de autenticación obtenido:", client.xAuthToken)
    
    # ======= Paso 2: Consultar los Matches usando proxy =======
    headers = {
        "X-Auth-Token": client.xAuthToken,
        "User-Agent": client.userAgent,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "os-version": client.osVersion,
        "persistent-device-id": client.persistentDeviceId,
        "install-id": client.installId,
        "app-session-id": client.appSessionId,
        "app-version": client.appVersion,
        "platform": client.platform,
        "language": client.language,
    }
    
    # Configuración del proxy en el formato dado:
    username = ""
    password = ""  # Nota: caracteres especiales deben ser codificados
    encoded_username = urllib.parse.quote(username)
    encoded_password = urllib.parse.quote(password)
    proxy_url = f"http://{encoded_username}:{encoded_password}@rotating.proxyempire.io:9004"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    matches_url = "https://api.gotinder.com/v2/matches?count=60"
    
    try:
        print("Realizando petición a Tinder para obtener matches (usando proxy)...")
        response = requests.get(matches_url, headers=headers, proxies=proxies, timeout=30)
        if response.status_code == 200:
            matches_data = response.json()
            print("Matches obtenidos:")
            print(json.dumps(matches_data, indent=2))
        else:
            print("Error al obtener matches. Código:", response.status_code)
            print("Respuesta:", response.text)
    except Exception as e:
        print("Ocurrió un error durante la petición:", e)

if __name__ == "__main__":
    main()
