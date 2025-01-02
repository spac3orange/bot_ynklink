import aiohttp
import hashlib
import uuid
from environs import Env

# Загрузка переменных окружения
env = Env()
merch_id, merch_api = env('MERCH_ID'), env('MERCH_API')

def generate_signature(secret_key, params):
    # Сортируем параметры по алфавиту
    sorted_params = sorted(params.items())
    # Формируем строку для подписи
    signature_base = ";".join(f"{k}={v}" for k, v in sorted_params if v) + f";{secret_key}"
    # Генерируем подпись (MD5)
    return hashlib.md5(signature_base.encode('utf-8')).hexdigest()

async def create_payment_page():
    # Основные данные платежа
    payment_data = {
        "pg_order_id": "ORDER-001",  # Уникальный ID заказа
        "pg_merchant_id": merch_id,   # Ваш ID мерчанта
        "pg_amount": 1000,          # Сумма платежа (например, 1000 = 10.00 KZT)
        "pg_description": "Оплата товара",  # Описание
        "pg_currency": "KZT",       # Валюта
        "pg_salt": uuid.uuid4().hex,  # Случайная строка
        "pg_testing_mode": 1,       # Режим (1 = тестовый)
        "pg_user_phone": "77777777777",  # Телефон клиента
        "pg_success_url": "https://example.com/success",  # URL для успешного платежа
        "pg_failure_url": "https://example.com/failure",  # URL для неуспешного платежа
    }

    # Генерация подписи
    secret_key = merch_api
    payment_data["pg_sig"] = generate_signature(secret_key, payment_data)

    # Асинхронный запрос
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://test-api.freedompay.kz/g2g/payment_page", data=payment_data
        ) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("pg_status") == "Ok":
                    print("URL для оплаты:", result["pg_redirect_url"])
                else:
                    print("Ошибка:", result.get("pg_error_description"))
            else:
                print("Ошибка HTTP:", response.status, await response.text())

