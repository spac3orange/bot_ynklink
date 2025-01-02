import aiohttp
import hashlib
import uuid
import xml.etree.ElementTree as ET
from environs import Env
from urllib.parse import urlparse

# Загрузка переменных окружения
env = Env()
env.read_env()
merch_id, merch_api = env('MERCH_ID'), env('MERCH_API')


def generate_signature(script_name, params, secret_key):
    """
    Генерация подписи для запроса к FreedomPay.

    :param script_name: Имя вызываемого скрипта.
    :param params: Словарь с параметрами запроса.
    :param secret_key: Секретный ключ мерчанта.
    :return: Подпись в виде строки MD5.
    """
    # Сортируем параметры по алфавиту
    sorted_params = sorted(params.items())

    # Формируем строку для подписи
    signature_base = f"{script_name};" + ";".join(f"{k}={v}" for k, v in sorted_params if v) + f";{secret_key}"

    # Генерация подписи (MD5)
    return hashlib.md5(signature_base.encode('utf-8')).hexdigest()


def get_script_name(url):
    """
    Извлекает имя вызываемого скрипта из URL.

    :param url: Полный URL.
    :return: Имя скрипта.
    """
    parsed_url = urlparse(url)
    script_name = parsed_url.path.split("/")[-1]  # Имя скрипта от последнего "/"
    return script_name

def parse_xml_response(xml_text):
    """Парсит XML-ответ и возвращает словарь."""
    root = ET.fromstring(xml_text)
    return {child.tag: child.text for child in root}

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

    # Определяем имя вызываемого скрипта
    url = "https://test-api.freedompay.kz/g2g/payment_page"
    script_name = get_script_name(url)

    # Генерация подписи
    secret_key = 'ZbwJ2h5j4HQqGvZp'
    payment_data["pg_sig"] = generate_signature(script_name, payment_data, secret_key)

    # Асинхронный запрос
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payment_data) as response:
            if response.status == 200:
                # Обработка XML-ответа
                xml_text = await response.text()
                result = parse_xml_response(xml_text)

                if result.get("pg_status") == "Ok":
                    print("URL для оплаты:", result["pg_redirect_url"])
                else:
                    print("Ошибка:", result.get("pg_error_description"))
            else:
                print("Ошибка HTTP:", response.status, await response.text())