import hashlib
from environs import Env
import aiohttp
import hashlib
import uuid
import xml.etree.ElementTree as ET
from environs import Env
from urllib.parse import urlparse
import random
import string
import asyncio


env = Env()
env.read_env()
merch_id = env.int('MERCH_ID')
merch_api = env.str('MERCH_API')

def parse_xml_response(xml_text):
    """Парсит XML-ответ и возвращает словарь."""
    root = ET.fromstring(xml_text)
    return {child.tag: child.text for child in root}


async def create_payment_page():
    # Основные данные платежа
    payment_data = {
        "pg_order_id": '23',  # Уникальный ID заказа
        "pg_merchant_id": merch_id,  # Ваш ID мерчанта
        "pg_amount": '25',  # Сумма платежа (строка)
        "pg_description": "test",  # Описание
        "pg_salt": 'molbulak',  # Случайная строка
    }

    # Определяем имя вызываемого скрипта
    url = "https://api.freedompay.kz/init_payment.php"
    script_name = 'init_payment.php'

    # Генерация подписи
    secret_key = merch_api  # Замените на настоящий секретный ключ
    signature = generate_signature(script_name, payment_data, secret_key)
    payment_data["pg_sig"] = signature

    # Отладка: проверка данных перед отправкой
    print("Данные для отправки:", payment_data)

    # Асинхронный запрос
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payment_data) as response:
            if response.status == 200:
                # Обработка XML-ответа
                xml_text = await response.text()
                result = parse_xml_response(xml_text)
                print(result)
                if result.get("pg_status") == "ok":
                    print("URL для оплаты:", result["pg_redirect_url"])
                else:
                    print("Ошибка:", result.get("pg_error_description"))
            else:
                print("Ошибка HTTP:", response.status, await response.text())



def generate_signature(script_name, data, secret_key):
    # Преобразуем все значения в строки
    data = {key: str(value) for key, value in data.items()}

    # Сортируем данные в алфавитном порядке по ключам
    sorted_items = sorted(data.items())

    # Получаем только значения, для конкатенации в нужном порядке
    sorted_values = [value for _, value in sorted_items]

    # Конкатенируем имя скрипта, параметры и секретный ключ
    concatenated_string = f"{script_name};" + ";".join(sorted_values) + f";{secret_key}"

    # Отладка: выводим сгенерированную строку
    print("Сгенерированная строка для подписи:", concatenated_string)

    # Генерируем MD5 хэш
    return hashlib.md5(concatenated_string.encode('utf-8')).hexdigest()

# Пример данных
data = {
    'pg_order_id': '23',
    'pg_merchant_id': merch_id,
    'pg_amount': '25',
    'pg_description': 'test',
    'pg_salt': 'molbulak',
}
secret_key = merch_api
script_name = 'init_payment.php'

# Генерация подписи
signature = generate_signature(script_name, data, secret_key)
print("Сгенерированная подпись:", signature)
asyncio.run(create_payment_page())
