import pandas as pd
from sqlalchemy.exc import IntegrityError
from app.crud.models import UserData
from app.crud import AsyncSessionLocal
import asyncio


async def import_excel_to_db(file_path: str):
    try:
        df = pd.read_excel(file_path, header=None)
    except Exception as e:
        print(f"Ошибка при чтении Excel файла: {e}")
        return

    required_columns = ['Номер телефона', 'Город', 'Номер документа', 'Имя', 'Комментарий']
    df.columns = required_columns

    records = df.to_dict(orient='records')

    async with AsyncSessionLocal() as session:
        for record in records:
            try:
                record = {key: (value if pd.notna(value) else "Нет") for key, value in record.items()}

                user_data = UserData(
                    number=str(record['Номер телефона']),
                    city=str(record['Город']),
                    document=str(record['Номер документа']),
                    name=str(record['Имя']),
                    comment=str(record['Комментарий']) if record['Комментарий'] != "Нет" else None,
                )


                session.add(user_data)

            except ValueError as ve:
                print(f"Ошибка приведения типов для записи {record}: {ve}")
            except Exception as e:
                print(f"Неожиданная ошибка для записи {record}: {e}")

        try:

            await session.commit()
            print("Данные успешно импортированы.")
        except IntegrityError as ie:
            await session.rollback()
            print(f"Ошибка целостности данных: {ie}")
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при сохранении данных в базе: {e}")


if __name__ == '__main__':
    excel_file = "app/template.xlsx"

    asyncio.run(import_excel_to_db(excel_file))
