from config.database import DatabaseConnection
from config.settings import TABLE_STUDENTS, TABLE_STUDENT_SKILLS, RUSSIAN_REGIONS
from database.skill_crud_new import SkillCRUDNew

class UserCRUD:
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = TABLE_STUDENTS
        self.skill_crud = SkillCRUDNew()
        self.regions = RUSSIAN_REGIONS
    
    def get_city_name(self, city_id):
        if city_id is None:
            return "Не указан"
        return self.regions.get(city_id, f"Город ID {city_id}")
    
    def check_students_table_structure(self):
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'msod4' AND table_name = 'students'
        ORDER BY ordinal_position
        """
        return self.db.execute_query(query, fetch=True)
    
    def check_table_has_city(self):
        query = """
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema = 'msod4' 
            AND table_name = 'students' 
            AND column_name = 'city_id'
        )
        """
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else False
    
    def print_table_structure(self):
        structure = self.check_students_table_structure()
        print(f"\nСтруктура таблицы {self.table_name}:")
        for col in structure:
            print(f"  {col[0]:25s} | {col[1]:15s} | Nullable: {col[2]}")
    
    def get_available_skills(self):
        skills = self.skill_crud.get_all_skills()
        return skills
    
    def add_user(self, student_id, full_name, skill_ids_input, city_id=None):
        structure = self.check_students_table_structure()
        columns = [col[0] for col in structure]
        
        has_city_id = 'city_id' in columns
        
        skills_text_list = []
        skill_ids = []
        
        if skill_ids_input:
            if isinstance(skill_ids_input, str):
                skill_parts = [s.strip() for s in skill_ids_input.split(',') if s.strip()]
            elif isinstance(skill_ids_input, list):
                skill_parts = skill_ids_input
            else:
                skill_parts = []
            
            for skill_item in skill_parts:
                if skill_item.isdigit():
                    skill_id = int(skill_item)
                    skill_record = self.skill_crud.get_skill_by_id(skill_id)
                    if skill_record:
                        skills_text_list.append(skill_record[1])
                        skill_ids.append(skill_id)
        
        if has_city_id:
            query = f"""
            INSERT INTO {self.table_name} (student_id, full_name, skills, city_id, skill_ids)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (student_id) 
            DO UPDATE SET 
                full_name = EXCLUDED.full_name,
                skills = EXCLUDED.skills,
                city_id = EXCLUDED.city_id,
                skill_ids = EXCLUDED.skill_ids
            """
            self.db.execute_query(query, (student_id, full_name, skills_text_list, city_id, skill_ids))
        else:
            query = f"""
            INSERT INTO {self.table_name} (student_id, full_name, skills, skill_ids)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id) 
            DO UPDATE SET 
                full_name = EXCLUDED.full_name,
                skills = EXCLUDED.skills,
                skill_ids = EXCLUDED.skill_ids
            """
            self.db.execute_query(query, (student_id, full_name, skills_text_list, skill_ids))
        
        for skill_id in skill_ids:
            self.skill_crud.add_student_skill(student_id, skill_id)
        
        return len(skill_ids)
    
    def get_all_users(self):
        query = f"SELECT student_id, full_name, skills, city_id, skill_ids FROM {self.table_name} ORDER BY student_id"
        return self.db.execute_query(query, fetch=True)
    
    def get_user_by_id(self, student_id):
        query = f"SELECT student_id, full_name, skills, city_id, skill_ids FROM {self.table_name} WHERE student_id = %s"
        result = self.db.execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None
    
    def get_user_with_skills(self, student_id):
        query = f"""
        SELECT s.student_id, s.full_name, s.skills, s.city_id, s.skill_ids,
               ARRAY_AGG(sk.skill_name) as skill_names,
               ARRAY_AGG(sk.skill_id) as skill_ids_detail
        FROM {self.table_name} s
        LEFT JOIN {TABLE_STUDENT_SKILLS} ss ON s.student_id = ss.student_id
        LEFT JOIN msod4.skills sk ON ss.skill_id = sk.skill_id
        WHERE s.student_id = %s
        GROUP BY s.student_id, s.full_name, s.skills, s.city_id, s.skill_ids
        """
        result = self.db.execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None
    
    def delete_user(self, student_id):
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM msod4.recommendations WHERE student_id = %s", (student_id,))
                cursor.execute("DELETE FROM msod4.student_skills WHERE student_id = %s", (student_id,))
                cursor.execute(f"DELETE FROM {self.table_name} WHERE student_id = %s", (student_id,))
                conn.commit()
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()
    
    def delete_all_users(self):
        try:
            conn = self.db.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM msod4.recommendations")
                cursor.execute("DELETE FROM msod4.student_skills")
                cursor.execute(f"DELETE FROM {self.table_name}")
                conn.commit()
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()