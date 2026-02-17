import psycopg2
from psycopg2 import sql
from config.settings import DB_CONFIG

class DatabaseConnection:
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                port=self.config['port']
            )
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SET search_path TO {}").format(
                    sql.Identifier(self.config['schema'])
                ))
            return conn
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            raise
    
    def execute_query(self, query, params=None, fetch=False):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Ошибка запроса: {e}")
            raise
        finally:
            conn.close()