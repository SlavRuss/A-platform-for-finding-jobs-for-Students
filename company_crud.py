from config.database import DatabaseConnection
from config.settings import TABLE_COMPANIES

class CompanyCRUD:
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = TABLE_COMPANIES
    
    def add_company(self, company):
        query = f"""
        INSERT INTO {self.table_name} (company_hh_id, company_name, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (company_hh_id) 
        DO UPDATE SET 
            company_name = EXCLUDED.company_name,
            updated_at = EXCLUDED.updated_at
        """
        self.db.execute_query(query, company.to_tuple())
    
    def add_companies_batch(self, companies):
        for company in companies:
            self.add_company(company)
        print(f"Добавлено/обновлено {len(companies)} компаний")
    
    def get_company_by_id(self, company_hh_id):
        query = f"SELECT * FROM {self.table_name} WHERE company_hh_id = %s"
        result = self.db.execute_query(query, (company_hh_id,), fetch=True)
        return result[0] if result else None
    
    def get_all_companies(self):
        query = f"SELECT * FROM {self.table_name} ORDER BY company_name"
        return self.db.execute_query(query, fetch=True)
    
    def delete_company(self, company_hh_id):
        query = f"DELETE FROM {self.table_name} WHERE company_hh_id = %s"
        self.db.execute_query(query, (company_hh_id,))
        print(f"Компания с ID {company_hh_id} удалена")
    
    def delete_all_companies(self):
        query = f"DELETE FROM {self.table_name}"
        self.db.execute_query(query)
        print("Все компании удалены")
    
    def count_companies(self):
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else 0
    
    def print_table_structure(self):
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'msod4' AND table_name = 'companies'
        ORDER BY ordinal_position
        """
        structure = self.db.execute_query(query, fetch=True)
        print(f"\nСтруктура таблица {self.table_name}:")
        print("-" * 80)
        for col in structure:
            print(f"  {col[0]:25s} | {col[1]:15s} | Nullable: {col[2]}")