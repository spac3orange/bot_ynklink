import pandas as pd
from app.crud.models import UserData
from app.crud import AsyncSessionLocal

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
            record = {key: (value if pd.notna(value) else "Нет") for key, value in record.items()}

            user_data = UserData(
                number=record['Номер телефона'],
                city=record['Город'],
                document=record['Номер документа'],
                name=record['Имя'],
                comment=record['Комментарий']
            )

            session.add(user_data)

        try:
            await session.commit()
            print("Данные успешно импортированы.")
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при сохранении данных в базе: {e}")


if __name__ == '__main__':
    import asyncio

    excel_file = "template.xlsx"

    asyncio.run(import_excel_to_db(excel_file))
