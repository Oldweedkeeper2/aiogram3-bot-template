import secrets


def generate_token():
    secret_token = secrets.token_urlsafe(32)  # генерируйте секретный токен для вашего вебхука
    return secret_token
