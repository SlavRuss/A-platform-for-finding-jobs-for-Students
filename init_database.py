from config.database import DatabaseConnection

try:
    from config.settings import PREDEFINED_SKILLS
except ImportError:
    # Запасной список навыков если PREDEFINED_SKILLS не определен
    PREDEFINED_SKILLS = [
        (1, 'Python'),
        (2, 'Java'),
        (3, 'JavaScript'),
        (4, 'SQL'),
        (5, 'HTML'),
        (6, 'CSS'),
        (7, 'React'),
        (8, 'Vue'),
        (9, 'Angular'),
        (10, 'Django'),
        (11, 'Flask'),
        (12, 'Spring'),
        (13, 'Docker'),
        (14, 'Kubernetes'),
        (15, 'Git'),
        (16, 'PostgreSQL'),
        (17, 'MySQL'),
        (18, 'MongoDB'),
        (19, 'Redis'),
        (20, 'AWS'),
        (21, 'Azure'),
        (22, 'Linux')
    ]

def create_tables():
    """Создать все необходимые таблицы"""
    db = DatabaseConnection()
    
    queries = [
        # Таблица skills
        """
        CREATE TABLE IF NOT EXISTS msod4.skills (
            skill_id SERIAL PRIMARY KEY,
            skill_name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Таблица companies
        """
        CREATE TABLE IF NOT EXISTS msod4.companies (
            company_hh_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Таблица areas
        """
        CREATE TABLE IF NOT EXISTS msod4.areas (
            area_hh_id INTEGER PRIMARY KEY,
            area_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Добавить колонку skill_ids в students
        """
        ALTER TABLE msod4.students 
        ADD COLUMN IF NOT EXISTS skill_ids INTEGER[]
        """,
        
        # Таблица student_skills
        """
        CREATE TABLE IF NOT EXISTS msod4.student_skills (
            student_id INTEGER REFERENCES msod4.students(student_id),
            skill_id INTEGER REFERENCES msod4.skills(skill_id),
            PRIMARY KEY (student_id, skill_id)
        )
        """
    ]
    
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            print("Создание таблиц...")
            for query in queries:
                cursor.execute(query)
            conn.commit()
            print("✓ Таблицы успешно созданы")
            
            # Инициализируем предопределенные навыки
            print("\nИнициализация предопределенных навыков...")
            added_count = 0
            for skill_id, skill_name in PREDEFINED_SKILLS:
                try:
                    query = """
                    INSERT INTO msod4.skills (skill_id, skill_name)
                    VALUES (%s, %s)
                    ON CONFLICT (skill_id) 
                    DO UPDATE SET skill_name = EXCLUDED.skill_name
                    """
                    cursor.execute(query, (skill_id, skill_name))
                    added_count += 1
                except Exception as e:
                    print(f"  Ошибка при добавлении навыка {skill_name}: {e}")
            
            conn.commit()
            print(f"✓ Инициализировано {added_count} навыков")
            
    except Exception as e:
        print(f"✗ Ошибка при создании таблиц: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

def add_foreign_keys():
    """Добавить внешние ключи после заполнения данных"""
    db = DatabaseConnection()
    
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            
            # Проверить существуют ли таблицы
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'msod4' 
                    AND table_name = 'companies'
                )
            """)
            companies_exists = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'msod4' 
                    AND table_name = 'areas'
                )
            """)
            areas_exists = cursor.fetchone()[0]
            
            if not companies_exists or not areas_exists:
                print("✗ Таблицы companies и areas не существуют")
                print("   Сначала запустите create_tables()")
                return
            
            # Проверить есть ли данные в таблицах
            cursor.execute("SELECT COUNT(*) FROM msod4.companies")
            companies_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM msod4.areas")
            areas_count = cursor.fetchone()[0]
            
            if companies_count == 0 or areas_count == 0:
                print(f"✗ Таблицы пусты: companies={companies_count}, areas={areas_count}")
                print("   Сначала заполните таблицы данными (загрузите вакансии)")
                return
            
            print(f"✓ Проверка пройдена: companies={companies_count}, areas={areas_count}")
            
            # Удалить существующие ограничения если есть
            print("\nУдаление старых ограничений...")
            try:
                cursor.execute("""
                    ALTER TABLE msod4.vacancies 
                    DROP CONSTRAINT IF EXISTS fk_vacancies_company
                """)
                cursor.execute("""
                    ALTER TABLE msod4.vacancies 
                    DROP CONSTRAINT IF EXISTS fk_vacancies_area
                """)
            except Exception as e:
                print(f"  Примечание: {e}")
            
            # Добавить внешние ключи
            print("Добавление внешних ключей...")
            cursor.execute("""
                ALTER TABLE msod4.vacancies
                ADD CONSTRAINT fk_vacancies_company 
                FOREIGN KEY (company_hh_id) 
                REFERENCES msod4.companies(company_hh_id)
                ON DELETE SET NULL
            """)
            
            cursor.execute("""
                ALTER TABLE msod4.vacancies
                ADD CONSTRAINT fk_vacancies_area 
                FOREIGN KEY (area_hh_id) 
                REFERENCES msod4.areas(area_hh_id)
                ON DELETE SET NULL
            """)
            
            conn.commit()
            print("✓ Внешние ключи успешно добавлены")
            
    except Exception as e:
        print(f"✗ Ошибка при добавлении внешних ключей: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

def check_database_state():
    """Проверить состояние базы данных"""
    db = DatabaseConnection()
    
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            
            print("=== Состояние базы данных ===")
            
            # Таблицы
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'msod4'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"\nТаблицы в схеме msod4 ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Внешние ключи
            try:
                cursor.execute("""
                    SELECT
                        tc.table_name, 
                        kcu.column_name, 
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name 
                    FROM 
                        information_schema.table_constraints AS tc 
                        JOIN information_schema.key_column_usage AS kcu
                          ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                          ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                      AND tc.table_schema = 'msod4'
                """)
                foreign_keys = cursor.fetchall()
                print(f"\nВнешние ключи ({len(foreign_keys)}):")
                for fk in foreign_keys:
                    print(f"  - {fk[0]}.{fk[1]} → {fk[2]}.{fk[3]}")
            except:
                print("\nВнешние ключи: не удалось получить информацию")
            
            # Проверить конкретные таблицы
            check_tables = ['skills', 'companies', 'areas', 'student_skills', 'vacancies', 'students']
            for table in check_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM msod4.{table}")
                    count = cursor.fetchone()[0]
                    print(f"\n{table}: {count} записей")
                except Exception as e:
                    print(f"\n{table}: таблица не существует или ошибка: {e}")
            
    except Exception as e:
        print(f"✗ Ошибка при проверке состояния БД: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Инициализация базы данных...")
    print("\nЗапустите:")
    print("1. create_tables() - для создания таблиц")
    print("2. Загрузите вакансии через main.py")
    print("3. add_foreign_keys() - для добавления внешних ключей")