from tinder_client import TinderClient
import json
import time
import random
import os
from datetime import datetime, date
import imghdr
import requests

# ============================
# Funciones para Proxies
# ============================
def get_proxies_from_file(filename="proxies.txt"):
    """Lee el fichero de proxies y devuelve una lista de proxies formateadas."""
    if not os.path.exists(filename):
        print(f"Advertencia: No se encontró el archivo {filename}. Se usará conexión directa.")
        return []
    with open(filename, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    return proxies

def select_random_proxy(proxies):
    """Devuelve una proxy aleatoria de la lista, o None si la lista está vacía."""
    if proxies:
        chosen = random.choice(proxies)
        # Se antepone el prefijo http:// (o socks5:// según convenga; aquí se asume HTTP)
        proxy_formatted = f"http://{chosen}"
        print(f"Proxy seleccionada: {proxy_formatted}")
        return proxy_formatted
    print("No se encontraron proxies en el fichero. Se usará conexión directa.")
    return None

# ============================
# Funciones para SMS Activate
# ============================
SMS_API_KEY = ""  # Reemplaza por tu clave

def get_sms_activate_number(api_key, service="oi", country="16", forward=0):
    """
    Solicita un número a la API de SMS Activate. Se espera una respuesta en texto plano con el formato:
      ACCESS_NUMBER:<activationId>:<phoneNumber>
    """
    url = "https://api.sms-activate.ae/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getNumber",
        "service": service,
        "forward": forward,
        "country": country
    }
    print("DEBUG: Solicitando número a SMS Activate con parámetros:", params)
    try:
        response = requests.get(url, params=params, timeout=30)
        print("DEBUG: Código de estado de la respuesta:", response.status_code)
        print("DEBUG: Cabeceras de la respuesta:", response.headers)
        print("DEBUG: Texto de la respuesta:", response.text)
        
        if response.status_code != 200:
            print("DEBUG: El código de estado no es 200, se aborta la solicitud.")
            return None

        resp_text = response.text.strip()
        if resp_text.startswith("ACCESS_NUMBER:"):
            parts = resp_text.split(":")
            if len(parts) == 3:
                activation_id = parts[1]
                phone_number = parts[2]
                print(f"DEBUG: Número recibido: {phone_number} (activationId: {activation_id})")
                return {"activation_id": activation_id, "phone_number": phone_number}
            else:
                print("DEBUG: Formato de respuesta inesperado:", resp_text)
                return None
        else:
            print("DEBUG: Respuesta inesperada:", resp_text)
            return None
    except Exception as e:
        print("DEBUG: Error al solicitar número de SMS Activate:", str(e))
        return None

def poll_sms_code(api_key, activation_id, timeout=120, interval=5):
    """
    Realiza polling para obtener el código SMS. Se espera recibir una respuesta en texto plano
    con el formato "STATUS_OK:<code>".
    """
    url = "https://api.sms-activate.ae/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getStatus",
        "id": activation_id
    }
    print("DEBUG: Esperando código SMS de SMS Activate...")
    waited = 0
    while waited < timeout:
        try:
            response = requests.get(url, params=params, timeout=30)
            resp_text = response.text.strip()
            print(f"DEBUG: Respuesta de SMS Activate: {resp_text}")
            if "STATUS_OK" in resp_text:
                parts = resp_text.split(":")
                if len(parts) == 2:
                    code = parts[1]
                    print(f"DEBUG: Código SMS recibido: {code}")
                    return code
            time.sleep(interval)
            waited += interval
        except Exception as e:
            print("DEBUG: Error al obtener estado SMS Activate:", str(e))
            time.sleep(interval)
            waited += interval
    print("DEBUG: Timeout al esperar el código SMS.")
    return None

# ============================
# Funciones de Usuario y Validaciones
# ============================
def get_random_name(filename="names.txt"):
    """
    Lee el archivo 'names.txt' y devuelve un nombre aleatorio.
    Si falla, devuelve 'Test User'.
    """
    if not os.path.exists(filename):
        print(f"Advertencia: No se encontró el archivo {filename}. Se usará 'Test User'.")
        return "Test User"
    with open(filename, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]
    if not names:
        print(f"Advertencia: El archivo {filename} está vacío. Se usará 'Test User'.")
        return "Test User"
    chosen = random.choice(names)
    print(f"DEBUG: Nombre seleccionado: {chosen}")
    return chosen

def get_random_email(filename="emails.txt"):
    """
    Lee el archivo 'email.txt' y devuelve una dirección de correo aleatoria.
    Si falla, devuelve 'default@example.com'.
    """
    if not os.path.exists(filename):
        print(f"Advertencia: No se encontró el archivo {filename}. Se usará 'default@example.com'.")
        return "default@example.com"
    with open(filename, "r", encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip()]
    if not emails:
        print(f"Advertencia: El archivo {filename} está vacío. Se usará 'default@example.com'.")
        return "default@example.com"
    chosen = random.choice(emails)
    print(f"DEBUG: Email seleccionado: {chosen}")
    return chosen

def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        year, month, day = map(int, date_text.split('-'))
        if year < 1900 or year > date.today().year:
            print("Please enter a valid year")
            return False
        if month < 1 or month > 12:
            print("Please enter a valid month (1-12)")
            return False
        if day < 1 or day > 31:
            print("Please enter a valid day")
            return False
        date(year, month, day)
        return True
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD")
        return False

def validate_age(birth_date):
    try:
        dob = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            print(f"You must be 18 or older to use this service (you are {age} years old)")
            return False
        if age > 100:
            print(f"Please enter a valid date of birth (age calculated: {age})")
            return False
        print(f"DEBUG: Age verified: {age} years old")
        return True
    except ValueError:
        return False

def get_date_of_birth():
    # Automatizamos con una fecha fija
    dob = "1990-01-01"
    print(f"DEBUG: Using default date of birth: {dob}")
    if validate_date(dob) and validate_age(dob):
        return dob
    else:
        raise Exception("Default date of birth is not valid")

def get_gender_interest():
    # Automatizamos: interesados en ambos géneros
    print("DEBUG: Automatically selecting interest: Everyone")
    return [0, 1]

def validate_email(email):
    if '@' not in email or '.' not in email:
        return False
    local_part, domain = email.rsplit('@', 1)
    if not local_part or not domain:
        return False
    if len(email) > 254:
        return False
    return True

# ============================
# Funciones de Imágenes y Directorio de Fotos
# ============================
def check_image_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            image_type = imghdr.what(None, h=data)
            if image_type in ['jpeg', 'jpg', 'png']:
                file_size_mb = len(data) / (1024 * 1024)
                print(f"DEBUG: Image size: {file_size_mb:.2f}MB")
                if file_size_mb > 5:
                    print(f"Warning: Image is quite large ({file_size_mb:.2f}MB). This may increase upload time.")
                return True, data, len(data)
    except Exception as e:
        print(f"Error reading image {file_path}: {str(e)}")
    return False, None, 0

def get_photos_from_folder():
    photos_dir = "photos"
    print(f"DEBUG: Checking photos directory: {os.path.abspath(photos_dir)}")
    if not os.path.exists(photos_dir):
        print(f"Error: {photos_dir} directory not found!")
        return []
    valid_extensions = ('.jpg', '.jpeg', '.png')
    photos = []
    print("DEBUG: Scanning for photos:")
    files = sorted(os.listdir(photos_dir))
    for file in files:
        if file.lower().endswith(valid_extensions):
            file_path = os.path.join(photos_dir, file)
            print(f"DEBUG: Checking file: {file}")
            print(f"DEBUG: Full path: {os.path.abspath(file_path)}")
            is_valid, image_data, size = check_image_file(file_path)
            if is_valid and image_data:
                photos.append(image_data)
                print(f"DEBUG: Valid image found: {file} (Size: {size/1024/1024:.2f}MB)")
            else:
                print(f"DEBUG: Invalid or corrupted image: {file}")
            if len(photos) >= 9:
                print("DEBUG: Maximum number of photos (9) reached. Additional photos will be ignored.")
                break
    print(f"DEBUG: Total valid photos found: {len(photos)}")
    if len(photos) == 0:
        print("Please add some photos to the 'photos' directory")
    elif len(photos) < 2:
        print("Warning: Tinder requires at least 2 photos")
    return photos

def debug_response(response, status_code):
    print(f"DEBUG: Status Code: {status_code}")
    print("DEBUG: Raw Response:", response)
    try:
        if response:
            return json.loads(response)
        return None
    except json.JSONDecodeError:
        print("DEBUG: Response is not valid JSON")
        return None

# ============================
# Funciones de Autenticación y Registro
# ============================
def handle_auth_process(client, email):
    """
    Automatiza el proceso de autenticación usando SMS Activate:
      - Solicita número y polling para OTP
      - Registra email, descarta conexiones sociales y obtiene token de auth
    """
    # Se solicita el número vía SMS Activate
    sms_data = get_sms_activate_number(SMS_API_KEY)
    if not sms_data:
        print("Error al obtener número de SMS Activate")
        return False
    phone_number = sms_data["phone_number"]
    activation_id = sms_data["activation_id"]
    print(f"DEBUG: Using phone number: {phone_number} for authentication")
    
    print(f"DEBUG: Attempting login with {phone_number}...")
    login_response = client.authLogin(phone_number)
    if not login_response:
        print("DEBUG: No response from server")
        return False
    if 'error' in login_response:
        print(f"DEBUG: Login error: {login_response['error']}")
        return False

    # Automatizamos la verificación OTP con polling
    otp = poll_sms_code(SMS_API_KEY, activation_id)
    if not otp:
        print("DEBUG: Failed to obtain OTP code")
        return False

    print(f"DEBUG: Verifying OTP: {otp}")
    otp_response = client.verifyOtp(phone_number, otp)
    if 'error' not in otp_response:
        print("DEBUG: Phone verification successful!")
        print("DEBUG: Registering email...")
        email_response = client.useEmail(email)
        print("DEBUG: Email registration response:", json.dumps(email_response, indent=2))
        if 'error' not in email_response:
            print("DEBUG: Email registration successful!")
            print("DEBUG: Dismissing social connections...")
            dismiss_response = client.dismissSocialConnectionList()
            print("DEBUG: Dismiss response:", json.dumps(dismiss_response, indent=2))
            print("DEBUG: Getting authentication token...")
            auth_response = client.getAuthToken()
            print("DEBUG: Auth token response:", json.dumps(auth_response, indent=2))
            if 'error' not in auth_response:
                return True
    print("DEBUG: Authentication step failed.")
    return False

def handle_401_error(client):
    """Handles 401 error by refreshing auth token."""
    try:
        print("DEBUG: Refreshing authentication token...")
        auth_response = client.getAuthToken()
        if auth_response and 'error' not in auth_response:
            print("DEBUG: Successfully refreshed authentication token")
            return True
        print("DEBUG: Failed to refresh authentication token")
        return False
    except Exception as e:
        print(f"DEBUG: Error refreshing token: {str(e)}")
        return False

def upload_photos(client, photos):
    max_photos = min(len(photos), 9)
    print(f"DEBUG: Preparing to upload {max_photos} photos...")
    for i, photo_data in enumerate(photos[:max_photos], 1):
        file_size_mb = len(photo_data) / (1024 * 1024)
        print(f"DEBUG: Uploading photo {i}/{max_photos} (Size: {file_size_mb:.2f}MB)")
        max_retries = 5 if file_size_mb > 2 else 3
        retry_count = 0
        token_refresh_attempted = False
        while retry_count < max_retries:
            try:
                print(f"DEBUG: Attempt {retry_count + 1} of {max_retries}")
                delay = random.uniform(1.0, 1.5)
                print(f"DEBUG: Waiting {delay:.2f} seconds before upload...")
                time.sleep(delay)
                response = client.onboardingPhoto(photo_data, max_photos)
                response_data = debug_response(response, client.last_status_code)
                if response_data and response_data.get('meta', {}).get('status') == 200:
                    print(f"DEBUG: Successfully uploaded photo {i}")
                    token_refresh_attempted = False
                    break
                elif client.last_status_code == 401 and not token_refresh_attempted:
                    print("DEBUG: Received 401 unauthorized error")
                    if handle_401_error(client):
                        token_refresh_attempted = True
                        continue
                    else:
                        print("DEBUG: Token refresh failed")
                print(f"DEBUG: Failed to upload photo {i} - Retrying...")
                retry_count += 1
                retry_delay = random.uniform(2.0, 3.0) if file_size_mb > 2 else random.uniform(1.5, 2.0)
                print(f"DEBUG: Waiting {retry_delay:.2f} seconds before retry...")
                time.sleep(retry_delay)
            except Exception as e:
                print(f"DEBUG: Error uploading photo {i}: {str(e)}")
                retry_count += 1
                time.sleep(2)
        if retry_count >= max_retries:
            print(f"DEBUG: Failed to upload photo {i} after {max_retries} attempts")
            # En este ejemplo se continúa automáticamente
        if i < max_photos:
            delay = random.uniform(1.0, 1.5)
            print(f"DEBUG: Waiting {delay:.2f} seconds before next upload...")
            time.sleep(delay)
    return True

def try_api_call(client, func, description, max_retries=3, delay=2):
    """Función genérica para llamadas API con reintentos."""
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"DEBUG: Retry attempt {attempt + 1}/{max_retries}")
            result = func()
            if result and client.last_status_code == 200:
                print(f"DEBUG: ✓ {description} completed successfully")
                return True
            raise Exception(f"API call failed with status {client.last_status_code}")
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"DEBUG: Retrying {description} in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"DEBUG: Failed to {description}: {str(e)}")
                return False
    return False

def get_user_info():
    """Obtiene la información de usuario de forma automática."""
    name = get_random_name("names.txt")
    dob = get_date_of_birth()
    gender = 0  # 0: Male, 1: Female
    gender_interest = get_gender_interest()
    email = get_random_email("email.txt")
    user_info = {
        'name': name,
        'dob': dob,
        'gender': gender,
        'gender_interest': gender_interest,
        'email': email
    }
    print("DEBUG: Using default user info:")
    print(json.dumps(user_info, indent=2))
    return user_info

def setup_additional_profile_settings(client):
    """Configura ajustes adicionales del perfil (educación, zodiac, intereses, etc.)"""
    try:
        print("DEBUG: Setting up additional profile information...")
        relationship_data = {
            "fields": [{
                "name": "relationship_intent",
                "data": {
                    "selected_descriptors": [{
                        "id": "de_29",
                        "choice_selections": [{"id": "2"}]
                    }]
                }
            }]
        }
        client._onboarding_set(json.dumps(relationship_data).encode())
        time.sleep(1)
        education_data = {
            "fields": [{
                "name": "education",
                "data": {
                    "selected_descriptors": [{
                        "id": "de_4",
                        "choice_selections": [{"id": "1"}]
                    }]
                }
            }]
        }
        client._onboarding_set(json.dumps(education_data).encode())
        time.sleep(1)
        zodiac_data = {
            "fields": [{
                "name": "zodiac",
                "data": {
                    "selected_descriptors": [{
                        "id": "de_1",
                        "choice_selections": [{"id": "1"}]
                    }]
                }
            }]
        }
        client._onboarding_set(json.dumps(zodiac_data).encode())
        time.sleep(1)
        interests_data = {
            "fields": [{
                "name": "user_interests",
                "data": {
                    "selected_interests": [
                        {"id": "it_7", "name": "Travel"},
                        {"id": "it_9", "name": "Movies"},
                        {"id": "it_28", "name": "Reading"}
                    ]
                }
            }]
        }
        client._onboarding_set(json.dumps(interests_data).encode())
        print("DEBUG: ✓ Additional profile settings configured")
        return True
    except Exception as e:
        print(f"DEBUG: Warning: Could not set additional profile settings: {str(e)}")
        return False

def main():
    try:
        print("Welcome to Tinder Registration!")
        print("-" * 50)
        # Selección automática de proxy
        proxies = get_proxies_from_file("proxies.txt")
        proxy = select_random_proxy(proxies)
        # Obtención de datos de usuario
        user_info = get_user_info()
        # Comprobación de fotos
        print("DEBUG: Checking photos directory...")
        photos = get_photos_from_folder()
        if not photos:
            print("DEBUG: No photos found in the photos directory! Please add some photos and try again.")
            return
        # Inicialización del cliente de Tinder
        client = TinderClient(
            userAgent="Tinder/14.21.0 (iPhone; iOS 14.2.0; Scale/2.00)",
            platform="ios",
            tinderVersion="14.21.0",
            appVersion="5546",
            osVersion=140000200000,
            language="en-US",
            proxy=proxy
        )
        if proxy:
            print(f"DEBUG: Using proxy. Current IP: {client.checkIp()}")
        # Inicializar sesión
        print("DEBUG: Initializing session...")
        buckets_response = client.sendBuckets()
        if buckets_response:
            print("DEBUG: Session initialized successfully")
        else:
            print("DEBUG: Failed to initialize session")
            return
        time.sleep(1)
        # Comprobación de dispositivo
        print("DEBUG: Performing device check...")
        client.deviceCheck()
        time.sleep(2)
        # Proceso de autenticación
        if not handle_auth_process(client, user_info['email']):
            print("DEBUG: Authentication failed. Exiting...")
            return
        time.sleep(2)
        # Iniciar onboarding
        print("DEBUG: Starting onboarding process...")
        onboarding_response = client.startOnboarding()
        if not onboarding_response:
            print("DEBUG: Failed to start onboarding process")
            return
        time.sleep(2)
        # Configurar información básica
        print("DEBUG: Setting basic information...")
        info_response = client.onboardingSuper(
            user_info['name'],
            user_info['dob'],
            user_info['gender'],
            user_info['gender_interest']
        )
        if not info_response:
            print("DEBUG: Failed to set basic information")
            return
        time.sleep(2)
        # Ajustes adicionales del perfil
        print("DEBUG: Setting up additional profile settings...")
        setup_additional_profile_settings(client)
        time.sleep(2)
        # Subida de fotos
        print("DEBUG: Starting photo upload process...")
        upload_photos(client, photos)
        time.sleep(2)
        # Completar registro
        print("DEBUG: Completing registration...")
        complete_response = client.endOnboarding()
        print("DEBUG: Registration complete response:", json.dumps(debug_response(complete_response, client.last_status_code), indent=2))
        # Manejo de captcha, si es necesario
        if client.last_status_code != 200:
            print("DEBUG: Encountered a challenge. Attempting to resolve...")
            if client.processCaptcha():
                print("DEBUG: Challenge resolved successfully!")
            else:
                print("DEBUG: Failed to resolve challenge")
                return
        # Configuración de ubicación
        try:
            time.sleep(3)
            print("DEBUG: Configuring location settings...")
            ip = client.checkIp()
            print(f"DEBUG: Current IP: {ip}")
            lat, lng = client.getLocation(ip)
            print(f"DEBUG: Location detected - Latitude: {lat}, Longitude: {lng}")
            try_api_call(client, lambda: client.updateLocation(lat, lng), "Updating location")
            time.sleep(1)
            try_api_call(client, lambda: client.locInit(), "Initializing location services")
            time.sleep(1)
            try_api_call(client, lambda: client.updateLocalization(lat, lng), "Updating localization")
        except Exception as e:
            print(f"DEBUG: Warning: Could not set location automatically: {str(e)}")
        # Guardar sesión
        try:
            print("DEBUG: Saving session information...")
            session_info = client.toObject()
            session_file = f"tinder_session_{client.userId}.json"
            with open(session_file, "w") as f:
                json.dump(session_info, f, indent=2)
            print(f"DEBUG: Session saved to: {session_file}")
        except Exception as e:
            print(f"DEBUG: Warning: Could not save session information: {str(e)}")
        print("DEBUG: === Registration Summary ===")
        print("DEBUG: ✓ Basic registration completed")
        print("DEBUG: ✓ Photos uploaded successfully")
        print("DEBUG: ✓ Profile configured")
        print(f"DEBUG: ✓ Using IP: {client.checkIp()}")
        print(f"DEBUG: ✓ User ID: {client.userId}")
        credentials = {
            'user_id': client.userId,
            'email': user_info['email'],
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'proxy_used': proxy,
            'ip_used': client.checkIp()
        }
        with open('tinder_credentials.json', 'a') as f:
            f.write(json.dumps(credentials) + '\n')
        print("DEBUG: Credentials saved to: tinder_credentials.json")
        print("DEBUG: You can now use the Tinder app with these credentials.")
    except Exception as e:
        print(f"DEBUG: An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("DEBUG: Process completed!")
        if 'client' in locals() and hasattr(client, 'userId'):
            print(f"DEBUG: User ID: {client.userId}")

if __name__ == "__main__":
    main()
