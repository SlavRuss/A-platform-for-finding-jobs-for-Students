from config.database import DatabaseConnection
from config.settings import TABLE_AREAS

class AreaCRUD:
    def __init__(self):
        self.db = DatabaseConnection()
        self.table_name = TABLE_AREAS
    
    def add_area(self, area):
        query = f"""
        INSERT INTO {self.table_name} (area_hh_id, area_name, created_at, updated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (area_hh_id) 
        DO UPDATE SET 
            area_name = EXCLUDED.area_name,
            updated_at = EXCLUDED.updated_at
        """
        self.db.execute_query(query, area.to_tuple())
    
    def add_areas_batch(self, areas):
        for area in areas:
            self.add_area(area)
        print(f"Добавлено/обновлено {len(areas)} регионов")
    
    def get_area_by_id(self, area_hh_id):
        query = f"SELECT * FROM {self.table_name} WHERE area_hh_id = %s"
        result = self.db.execute_query(query, (area_hh_id,), fetch=True)
        return result[0] if result else None
    
    def get_all_areas(self):
        query = f"SELECT * FROM {self.table_name} ORDER BY area_name"
        return self.db.execute_query(query, fetch=True)
    
    def delete_area(self, area_hh_id):
        query = f"DELETE FROM {self.table_name} WHERE area_hh_id = %s"
        self.db.execute_query(query, (area_hh_id,))
        print(f"Регион с ID {area_hh_id} удален")
    
    def delete_all_areas(self):
        query = f"DELETE FROM {self.table_name}"
        self.db.execute_query(query)
        print("Все регионы удалены")
    
    def count_areas(self):
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self.db.execute_query(query, fetch=True)
        return result[0][0] if result else 0
    
    def print_table_structure(self):
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'msod4' AND table_name = 'areas'
        ORDER BY ordinal_position
        """
        structure = self.db.execute_query(query, fetch=True)
        print(f"\nСтруктура таблицы {self.table_name}:")
        print("-" * 80)
        for col in structure:
            print(f"  {col[0]:25s} | {col[1]:15s} | Nullable: {col[2]}")