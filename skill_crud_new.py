from config.database import DatabaseConnection
from config.settings import TABLE_SKILLS, TABLE_STUDENT_SKILLS, PREDEFINED_SKILLS

class SkillCRUDNew:
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = TABLE_SKILLS
        self.student_skills_table = TABLE_STUDENT_SKILLS
    
    def initialize_predefined_skills(self):
        added = 0
        for skill_id, skill_name in PREDEFINED_SKILLS:
            try:
                query = f"""
                INSERT INTO {self.table_name} (skill_id, skill_name)
                VALUES (%s, %s)
                ON CONFLICT (skill_id) 
                DO UPDATE SET skill_name = EXCLUDED.skill_name
                """
                self.db.execute_query(query, (skill_id, skill_name))
                added += 1
            except Exception as e:
                print(f"Ошибка при добавлении навыка {skill_name}: {e}")
        
        print(f"Инициализировано {added} навыков")
        return added
    
    def add_skill(self, skill_name):
        query = f"""
        INSERT INTO {self.table_name} (skill_name)
        VALUES (%s)
        RETURNING skill_id
        """
        result = self.db.execute_query(query, (skill_name,), fetch=True)
        return result[0][0] if result else None
    
    def get_skill_by_name(self, skill_name):
        query = f"SELECT * FROM {self.table_name} WHERE skill_name ILIKE %s"
        result = self.db.execute_query(query, (skill_name,), fetch=True)
        return result[0] if result else None
    
    def get_skill_by_id(self, skill_id):
        query = f"SELECT * FROM {self.table_name} WHERE skill_id = %s"
        result = self.db.execute_query(query, (skill_id,), fetch=True)
        return result[0] if result else None
    
    def get_all_skills(self):
        query = f"SELECT * FROM {self.table_name} ORDER BY skill_name"
        return self.db.execute_query(query, fetch=True)
    
    def add_student_skill(self, student_id, skill_id):
        query = f"""
        INSERT INTO {self.student_skills_table} (student_id, skill_id)
        VALUES (%s, %s)
        ON CONFLICT (student_id, skill_id) DO NOTHING
        """
        self.db.execute_query(query, (student_id, skill_id))
    
    def get_student_skills(self, student_id):
        query = f"""
        SELECT s.skill_id, s.skill_name 
        FROM {self.table_name} s
        JOIN {self.student_skills_table} ss ON s.skill_id = ss.skill_id
        WHERE ss.student_id = %s
        ORDER BY s.skill_name
        """
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    def delete_student_skill(self, student_id, skill_id):
        query = f"DELETE FROM {self.student_skills_table} WHERE student_id = %s AND skill_id = %s"
        self.db.execute_query(query, (student_id, skill_id))
    
    def delete_skill(self, skill_id):
        query1 = f"DELETE FROM {self.student_skills_table} WHERE skill_id = %s"
        self.db.execute_query(query1, (skill_id,))
        
        query2 = f"DELETE FROM {self.table_name} WHERE skill_id = %s"
        self.db.execute_query(query2, (skill_id,))
        print(f"Навык с ID {skill_id} удален")
    
    def delete_all_skills(self):
        query1 = f"DELETE FROM {self.student_skills_table}"
        self.db.execute_query(query1)
        
        query2 = f"DELETE FROM {self.table_name}"
        self.db.execute_query(query2)
        print("Все навыки удалены")
    
    def count_skills(self):
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else 0
    
    def print_table_structure(self):
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'msod4' AND table_name = 'skills'
        ORDER BY ordinal_position
        """
        structure = self.db.execute_query(query, fetch=True)
        print(f"\nСтруктура таблицы {self.table_name}:")
        print("-" * 80)
        for col in structure:
            print(f"  {col[0]:25s} | {col[1]:15s} | Nullable: {col[2]}")