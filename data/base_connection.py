import asyncpg


class DataBase:
    @staticmethod
    async def connection(user='', password='', host='localhost', port='',
                         database='') -> asyncpg.Connection:
        # Устанавливаем соединение с базой данных
        return await asyncpg.connect(user=user, password=password, host=host, port=port, database=database)
