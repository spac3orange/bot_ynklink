import aiohttp
import hashlib
import uuid
import xml.etree.ElementTree as ET
from environs import Env
from urllib.parse import urlparse
import random
import string


# Загрузка переменных окружения
env = Env()
env.read_env()
merch_id = env.int('MERCH_ID')
merch_api = env.str('MERCH_API')

def parse_xml_response(xml_text):
    """Парсит XML-ответ и возвращает словарь."""
    root = ET.fromstring(xml_text)
    return {child.tag: child.text for child in root}


def generate_signature(script_name, data, secret_key):
    # Сортируем данные в алфавитном порядке
    sorted_items = sorted(data.items())
    # Конкатенируем имя скрипта, параметры и секретный ключ
    concatenated_string = f"{script_name};" + ";".join(f"{key}={value}" for key, value in sorted_items) + f";{secret_key}"
    # Генерируем MD5 хэш
    return hashlib.md5(concatenated_string.encode('utf-8')).hexdigest()

def generate_salt():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def get_script_name(url):
    parsed_url = url.split("?")[0]
    return parsed_url.split("/")[-1]

async def create_payment_page():
    # Основные данные платежа
    payment_data = {
        "pg_order_id": "001",  # Уникальный ID заказа
        "pg_merchant_id": merch_id,  # Ваш ID мерчанта
        "pg_amount": "1000",  # Сумма платежа (всегда строка)
        "pg_description": "Оплата",  # Описание
        "pg_currency": "KZT",  # Валюта
        "pg_salt": generate_salt(),  # Случайная строка
        "pg_testing_mode": "1",  # Режим (всегда строка)
    }

    # Определяем имя вызываемого скрипта
    url = "https://api.freedompay.kz/init_payment.php"
    script_name = get_script_name(url)

    # Генерация подписи
    secret_key = merch_api
    payment_data["pg_sig"] = generate_signature(script_name, payment_data, secret_key)

    # Асинхронный запрос
    print(script_name)
    print(payment_data)
    print(secret_key)
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
