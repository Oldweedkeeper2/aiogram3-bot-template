import secrets

secret_token = secrets.token_urlsafe(32)  # генерируйте секретный токен для вашего вебхука
print(secret_token)
