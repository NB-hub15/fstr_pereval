import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('FSTR_DB_HOST', 'localhost'),
            port=os.getenv('FSTR_DB_PORT', '5432'),
            dbname='fstr_db',
            user=os.getenv('FSTR_DB_LOGIN', 'postgres'),
            password=os.getenv('FSTR_DB_PASS', '')
        )
        self.cursor = self.conn.cursor()

    def add_user(self, email, fam, name, otc, phone):
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
        self.cursor.execute("""
            INSERT INTO coords (latitude, longitude, height)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (latitude, longitude, height))
        return self.cursor.fetchone()[0]

    def add_pereval(self, beauty_title, title, other_titles, connect, user_id, coords_id, add_time=None):
        from datetime import datetime
        if add_time is None:
            add_time = datetime.now()
        self.cursor.execute("""
            INSERT INTO pereval (beauty_title, title, other_titles, connect, add_time, user_id, coords_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'new')
            RETURNING id
        """, (beauty_title, title, other_titles, connect, add_time, user_id, coords_id))
        return self.cursor.fetchone()[0]

    def add_image(self, pereval_id, data, title):
        self.cursor.execute("""
            INSERT INTO images (pereval_id, data, title)
            VALUES (%s, %s, %s)
        """, (pereval_id, data, title))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()