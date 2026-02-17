from config.database import DatabaseConnection
from config.settings import TABLE_VACANCY_SKILLS
from models.skill_model import Skill

class SkillCRUD:
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = TABLE_VACANCY_SKILLS
    
    def check_skills_table_structure(self):
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'msod4' AND table_name = 'vacancy_skills'
        ORDER BY ordinal_position
        """
        return self.db.execute_query(query, fetch=True)
    
    def print_table_structure(self):
        """Вывести структуру таблицы"""
        structure = self.check_skills_table_structure()
        print(f"\nСтруктура таблицы {self.table_name}:")
        print("-" * 80)
        for col in structure:
            print(f"  {col[0]:25s} | {col[1]:15s} | Nullable: {col[2]}")
    
    def add_skill(self, skill):
        query = f"""
        INSERT INTO {self.table_name} (vacancy_hh_id, skill)
        VALUES (%s, %s)
        ON CONFLICT (vacancy_hh_id, skill) DO NOTHING
        """
        self.db.execute_query(query, (skill.vacancy_hh_id, skill.skill_name))
    
    def add_skills_batch(self, skills):
        for skill in skills:
            self.add_skill(skill)
        print(f"Добавлено {len(skills)} навыков")
    
    def get_all_skills(self):
        query = f"""
        SELECT skill, COUNT(*) as count 
        FROM {self.table_name} 
        GROUP BY skill 
        ORDER BY count DESC
        """
        return self.db.execute_query(query, fetch=True)
    
    def get_skills_by_vacancy(self, vacancy_id):
        query = f"SELECT skill FROM {self.table_name} WHERE vacancy_hh_id = %s"
        return self.db.execute_query(query, (vacancy_id,), fetch=True)
    
    def delete_skill(self, skill_name, vacancy_id=None):
        if vacancy_id:
            query = f"DELETE FROM {self.table_name} WHERE vacancy_hh_id = %s AND skill = %s"
            self.db.execute_query(query, (vacancy_id, skill_name))
            print(f"Навык '{skill_name}' для вакансии {vacancy_id} удален")
        else:
            query = f"DELETE FROM {self.table_name} WHERE skill = %s"
            self.db.execute_query(query, (skill_name,))
            print(f"Навык '{skill_name}' удален")
    
    def delete_all_skills(self):
        query = f"DELETE FROM {self.table_name}"
        self.db.execute_query(query)
        print("Все навыки удалены")
    
    def count_skills(self):
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else 0