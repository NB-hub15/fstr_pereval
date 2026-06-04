import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('FSTR_DB_HOST', 'localhost'),
            port=os.getenv('FSTR_DB_PORT', '5432'),
            dbname='fstr_db_rbaj',
            user=os.getenv('FSTR_DB_LOGIN', 'postgres'),
            password=os.getenv('FSTR_DB_PASS', '')
        )
        self.cursor = self.conn.cursor()

    def add_user(self, email, fam, name, otc, phone):
        """Добавляет пользователя или обновляет существующего по email"""
        self.cursor.execute("""
            INSERT INTO users (email, fam, name, otc, phone)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                fam = EXCLUDED.fam,
                name = EXCLUDED.name,
                otc = EXCLUDED.otc,
                phone = EXCLUDED.phone
            RETURNING id
        """, (email, fam, name, otc, phone))
        return self.cursor.fetchone()[0]

    def add_coords(self, latitude, longitude, height):
        """Добавляет координаты и возвращает их ID"""
        self.cursor.execute("""
            INSERT INTO coords (latitude, longitude, height)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (latitude, longitude, height))
        return self.cursor.fetchone()[0]

    def add_pereval(self, beauty_title, title, other_titles, connect, user_id, coords_id, add_time=None,
                    level_winter=None, level_summer=None, level_autumn=None, level_spring=None):
        """Добавляет перевал со статусом 'new' и возвращает его ID"""
        from datetime import datetime
        if add_time is None:
            add_time = datetime.now()
        self.cursor.execute("""
            INSERT INTO pereval (beauty_title, title, other_titles, connect, add_time, user_id, coords_id, status, level_winter, level_summer, level_autumn, level_spring)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'new', %s, %s, %s, %s)
            RETURNING id
        """, (beauty_title, title, other_titles, connect, add_time, user_id, coords_id, level_winter, level_summer,
              level_autumn, level_spring))
        return self.cursor.fetchone()[0]

    def add_image(self, pereval_id, data, title):
        """Добавляет фотографию к перевалу"""
        self.cursor.execute("""
            INSERT INTO images (pereval_id, data, title)
            VALUES (%s, %s, %s)
        """, (pereval_id, data, title))

    def execute_query(self, query: str, params: tuple = ()):
        """Выполняет SELECT-запрос и возвращает все строки (Модуль 27, стр. 3-4)"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def commit(self):
        """Фиксирует изменения в БД"""
        self.conn.commit()

    def close(self):
        """Закрывает соединение с БД"""
        self.cursor.close()
        self.conn.close()