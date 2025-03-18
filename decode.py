token_hex = ""
decoded_bytes = bytes.fromhex(token_hex)
print("Token en bytes:", decoded_bytes)
# Si quieres intentar convertirlo a string (puede no ser legible):
try:
    decoded_str = decoded_bytes.decode("utf-8")
    print("Token decodificado (UTF-8):", decoded_str)
except UnicodeDecodeError:
    print("El token no se puede decodificar a UTF-8")
