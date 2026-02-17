from config.database import DatabaseConnection

def delete_unnecessary_tables():

    db = DatabaseConnection()
    
    tables_to_delete = ['users', 'hh_vacancies', 'hh_skills']
    
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            for table in tables_to_delete:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    print(f"✓ Таблица {table} удалена")
                except Exception as e:
                    print(f"✗ Ошибка при удалении таблицы {table}: {e}")
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")

def show_existing_tables():
    db = DatabaseConnection()
    
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'msod4'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print("\nСуществующие таблицы в схеме msod4:")
            for table in tables:
                print(f"  - {table[0]}")
        conn.close()
    except Exception as e:
        print(f"✗ Ошибка: {e}")

if __name__ == "__main__":
    print("Очистка ненужных таблиц...")
    show_existing_tables()
    
    confirm = input("\nУдалить таблицы users, hh_vacancies, hh_skills? (yes/no): ")
    if confirm.lower() == 'yes':
        delete_unnecessary_tables()
        print("\nОставшиеся таблицы:")
        show_existing_tables()
    else:
        print("Отмена операции")