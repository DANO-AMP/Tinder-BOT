import requests
import json
import urllib.parse

def main():
    # Sustituye por tu token real y demás valores
    x_auth_token = ""
    user_agent = "Tinder/14.21.0 (iOS; Scale/2.00)"
    os_version = "14.2"
    persistent_device_id = "8c90535f0c3e412b"
    install_id = "A427FD7C-90BC-4077-9BB4-7C728D1AEB68"
    app_session_id = "825DDA558L.com.cardify.tinder447828318430"
    app_version = "5546"
    platform = "ios"
    language = "en-US"
    
    headers = {
        "X-Auth-Token": x_auth_token,
        "User-Agent": user_agent,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "os-version": os_version,
        "persistent-device-id": persistent_device_id,
        "install-id": install_id,
        "app-session-id": app_session_id,
        "app-version": app_version,
        "platform": platform,
        "language": language,
    }
    
    # Datos de autenticación del proxy
    username = "OWdW52pDnw5GZvRe"
    password = "wifi;uk;;;"  # Nota: estos caracteres necesitan ser codificados
    # Codificar usuario y contraseña
    encoded_username = urllib.parse.quote(username)
    encoded_password = urllib.parse.quote(password)
    
    # Construir la URL del proxy correctamente
    proxy_url = f"http://{encoded_username}:{encoded_password}@rotating.proxyempire.io:9004"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    matches_url = "https://api.gotinder.com/v2/matches?count=60"
    
    try:
        print("Realizando petición a Tinder con proxy...")
        response = requests.get(matches_url, headers=headers, proxies=proxies, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("Matches obtenidos:")
            print(json.dumps(data, indent=2))
        else:
            print("Error al obtener matches. Código:", response.status_code)
            print("Respuesta:", response.text)
    except Exception as e:
        print("Ocurrió un error durante la petición:", e)

if __name__ == "__main__":
    main()
