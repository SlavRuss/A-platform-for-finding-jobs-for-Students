from config.database import DatabaseConnection
from config.settings import TABLE_VACANCIES
from models.vacancy_model import Vacancy
from psycopg2 import sql

class VacancyCRUD:
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = TABLE_VACANCIES
    
    def check_vacancies_table_structure(self):
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'msod4' AND table_name = 'vacancies'
        ORDER BY ordinal_position
        """
        return self.db.execute_query(query, fetch=True)
    
    def print_table_structure(self):
        """Вывести структуру таблицы"""
        structure = self.check_vacancies_table_structure()
        print(f"\nСтруктура таблицы {self.table_name}:")
        print("-" * 80)
        for col in structure:
            print(f"  {col[0]:25s} | {col[1]:15s} | Nullable: {col[2]}")
    
    def add_vacancy(self, vacancy):
        """Добавить вакансию в БД"""
        try:
            query = f"""
            INSERT INTO {self.table_name} (
                vacancy_hh_id, title, publication_date,
                company_hh_id, area_hh_id, 
                salary_from, salary_to, salary_currency, salary_gross,
                schedule, snippet_responsibility, snippet_requirement,
                real_salary, id_prof,
                archive, on_deleted, date_added, date_updated
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (vacancy_hh_id) 
            DO UPDATE SET 
                title = EXCLUDED.title,
                publication_date = EXCLUDED.publication_date,
                company_hh_id = EXCLUDED.company_hh_id,
                area_hh_id = EXCLUDED.area_hh_id,
                salary_from = EXCLUDED.salary_from,
                salary_to = EXCLUDED.salary_to,
                salary_currency = EXCLUDED.salary_currency,
                salary_gross = EXCLUDED.salary_gross,
                schedule = EXCLUDED.schedule,
                snippet_responsibility = EXCLUDED.snippet_responsibility,
                snippet_requirement = EXCLUDED.snippet_requirement,
                real_salary = EXCLUDED.real_salary,
                id_prof = EXCLUDED.id_prof,
                archive = EXCLUDED.archive,
                on_deleted = EXCLUDED.on_deleted,
                date_updated = EXCLUDED.date_updated
            """
            
            values = (
                vacancy.vacancy_id,
                vacancy.title,
                vacancy.publication_date,
                vacancy.company_id,
                vacancy.area_id,
                vacancy.salary_from,
                vacancy.salary_to,
                vacancy.salary_currency,
                vacancy.salary_gross,
                vacancy.schedule,
                vacancy.snippet_responsibility,
                vacancy.snippet_requirement,
                vacancy.real_salary,
                vacancy.profession_id,
                False,
                False,
                vacancy.created_at,
                vacancy.updated_at
            )
            
            self.db.execute_query(query, values)
            return True
            
        except Exception as e:
            print(f"Ошибка при добавлении вакансии {vacancy.vacancy_id}: {e}")
            return False
    
    def add_vacancies_batch(self, vacancies):
        success_count = 0
        error_count = 0
        
        for vacancy in vacancies:
            if self.add_vacancy(vacancy):
                success_count += 1
            else:
                error_count += 1
        
        print(f"Добавлено/обновлено {success_count} вакансий")
        if error_count > 0:
            print(f"Ошибок при добавлении: {error_count}")
    
    def get_all_vacancies(self):
        query = f"SELECT * FROM {self.table_name} ORDER BY publication_date DESC, date_added DESC"
        return self.db.execute_query(query, fetch=True)
    
    def get_vacancy_by_id(self, vacancy_id):
        query = f"SELECT * FROM {self.table_name} WHERE vacancy_hh_id = %s"
        result = self.db.execute_query(query, (vacancy_id,), fetch=True)
        return result[0] if result else None
    
    def delete_vacancy(self, vacancy_id):
        query = f"DELETE FROM {self.table_name} WHERE vacancy_hh_id = %s"
        self.db.execute_query(query, (vacancy_id,))
        print(f"Вакансия с ID {vacancy_id} удалена")
    
    def delete_all_vacancies(self):
        query = f"DELETE FROM {self.table_name}"
        self.db.execute_query(query)
        print("Все вакансии удалены")
    
    def count_vacancies(self):
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else 0