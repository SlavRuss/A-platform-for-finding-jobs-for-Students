import psycopg2
from psycopg2 import sql
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_connection():
    try:
        from config.database import DatabaseConnection
        db = DatabaseConnection()
        conn = db.get_connection()
        print("✓ Подключение к БД успешно установлено")
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_schema()")
            schema = cursor.fetchone()[0]
            print(f"✓ Текущая схема: {schema}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"X Ошибка подключения: {e}")
        return False

def create_tables():
    try:
        from database.user_crud import UserCRUD
        from database.vacancy_crud import VacancyCRUD
        from database.skill_crud import SkillCRUD
        
        user_crud = UserCRUD()
        vacancy_crud = VacancyCRUD()
        skill_crud = SkillCRUD()
        
        user_crud.create_user_table()
        vacancy_crud.create_vacancy_table()
        skill_crud.create_skill_table()
        
        print("✓ Все таблицы успешно созданы")
        return True
    except Exception as e:
        print(f"Х Ошибка при создании таблиц: {e}")
        return False