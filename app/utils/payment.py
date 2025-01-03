import aiohttp
import hashlib
import uuid
import xml.etree.ElementTree as ET
from environs import Env
from urllib.parse import urlparse
import random
import string


env = Env()
env.read_env()
merch_id = env.int('MERCH_ID')
merch_api = env.str('MERCH_API')

def parse_xml_response(xml_text):
    root = ET.fromstring(xml_text)
    return {child.tag: child.text for child in root}


def get_script_name(url):
    parsed_url = url.split("?")[0]
    return parsed_url.split("/")[-1]


def generate_signature(script_name, data, secret_key):
    data = {key: str(value) for key, value in data.items()}
    sorted_items = sorted(data.items())
    sorted_values = [value for _, value in sorted_items]
    concatenated_string = f"{script_name};" + ";".join(sorted_values) + f";{secret_key}"
    print("Сгенерированная строка для подписи:", concatenated_string)
    return hashlib.md5(concatenated_string.encode('utf-8')).hexdigest()


async def create_payment_page(amount):
    payment_data = {
        "pg_order_id": "00102",  # Уникальный ID заказа
        "pg_merchant_id": merch_id,  # Ваш ID мерчанта
        "pg_amount": amount,  # Сумма платежа (строка)
        "pg_description": "Описание",  # Описание
        "pg_salt": uuid.uuid4().hex,  # Случайная строка
        "pg_testing_mode": "1",  # Режим (строка)
    }

    url = "https://api.freedompay.kz/init_payment.php"
    script_name = "init_payment.php"
    secret_key = merch_api
    signature = generate_signature(script_name, payment_data, secret_key)
    payment_data["pg_sig"] = signature
    print("Данные для отправки:", payment_data)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payment_data) as response:
            if response.status == 200:
                # Обработка XML-ответа
                xml_text = await response.text()
                result = parse_xml_response(xml_text)

                if result.get("pg_status") == "ok":
                    print("URL для оплаты:", result["pg_redirect_url"])
                    return result['pg_payment_id'], result['pg_redirect_url']
                else:
                    print("Ошибка:", result.get("pg_error_description"))
            else:
                print("Ошибка HTTP:", response.status, await response.text())


async def get_payment_status(payment_id, tarif):
    url = 'https://api.freedompay.kz/get_status3.php'
    script_name = 'get_status3.php'
    pg_salt = uuid.uuid4().hex
    data = {
        "pg_merchant_id": merch_id,
        "pg_payment_id": payment_id,
        "pg_salt": pg_salt
    }
    secret_key = merch_api
    pg_sig = generate_signature(script_name, data, secret_key)
    data["pg_sig"] = pg_sig
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                # Обработка XML-ответа
                xml_text = await response.text()
                result = parse_xml_response(xml_text)
                print(result)
                return result['pg_payment_status']
            else:
                raise ValueError('Ошибка')
            #     if result.get("pg_status") == "ok":
            #         print("URL для оплаты:", result["pg_redirect_url"])
            #         return result['pg_payment_id'], result['pg_redirect_url']
            #     else:
            #         print("Ошибка:", result.get("pg_error_description"))
            # else:
            #     print("Ошибка HTTP:", response.status, await response.text())
