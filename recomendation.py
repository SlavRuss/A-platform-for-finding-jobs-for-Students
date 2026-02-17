from config.database import DatabaseConnection
from config.settings import TABLE_RECOMMENDATIONS, TABLE_STUDENTS, TABLE_VACANCIES, TABLE_VACANCY_SKILLS, TABLE_AREAS, TABLE_COMPANIES, TABLE_SKILLS, TABLE_STUDENT_SKILLS

class RecommendationCRUD:
    def __init__(self):
        self.db = DatabaseConnection()
    
    @staticmethod
    def jaccard_similarity(set1, set2):
        if not set1 and not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def get_student_data(self, student_id):
        query = f"""
        SELECT skill_ids, city_id 
        FROM {TABLE_STUDENTS} 
        WHERE student_id = %s
        """
        result = self.db.execute_query(query, (student_id,), fetch=True)
        if result:
            skill_ids = set(result[0][0]) if result[0][0] else set()
            city_id = result[0][1]
            return skill_ids, city_id
        return set(), None
    
    def get_vacancy_skills_ids(self, vacancy_id):
        query = f"""
        SELECT vs.skill, s.skill_id
        FROM {TABLE_VACANCY_SKILLS} vs
        LEFT JOIN {TABLE_SKILLS} s ON LOWER(vs.skill) = LOWER(s.skill_name)
        WHERE vs.vacancy_hh_id = %s AND s.skill_id IS NOT NULL
        """
        result = self.db.execute_query(query, (vacancy_id,), fetch=True)
        return {row[1] for row in result} if result else set()
    
    def get_all_vacancies_data(self):
        query = f"""
        SELECT v.vacancy_hh_id, v.title, v.area_hh_id
        FROM {TABLE_VACANCIES} v
        WHERE v.archive = false AND v.on_deleted = false
        """
        return self.db.execute_query(query, fetch=True)
    
    def calculate_score(self, student_skill_ids, vacancy_skill_ids, student_city, vacancy_city):
        skill_score = self.jaccard_similarity(student_skill_ids, vacancy_skill_ids)
        
        city_bonus = 0.3 if student_city and vacancy_city and student_city == vacancy_city else 0.0
        
        total_score = 0.7 * skill_score + 0.3 * city_bonus
        
        return total_score
    
    def recommend_for_student(self, student_id, limit=10):
        student_skill_ids, student_city = self.get_student_data(student_id)
        
        if not student_skill_ids:
            return []
        
        vacancies_data = self.get_all_vacancies_data()
        scored_vacancies = []
        
        for vac_id, title, vac_city in vacancies_data:
            vacancy_skill_ids = self.get_vacancy_skills_ids(vac_id)
            
            if not vacancy_skill_ids:
                continue
            
            score = self.calculate_score(
                student_skill_ids, 
                vacancy_skill_ids, 
                student_city, 
                vac_city
            )
            
            if score > 0:
                scored_vacancies.append((vac_id, title, score, vac_city))
        
        scored_vacancies.sort(key=lambda x: x[2], reverse=True)
        return scored_vacancies[:limit]
    
    def save_recommendations(self, student_id, recommendations):
        delete_query = f"""
        DELETE FROM {TABLE_RECOMMENDATIONS} 
        WHERE student_id = %s
        """
        self.db.execute_query(delete_query, (student_id,))
        
        saved_count = 0
        for vac_id, title, score, vac_city in recommendations:
            insert_query = f"""
            INSERT INTO {TABLE_RECOMMENDATIONS} 
            (student_id, vacancy_hh_id, match_score, created_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (student_id, vacancy_hh_id) 
            DO UPDATE SET 
                match_score = EXCLUDED.match_score,
                created_at = NOW()
            """
            self.db.execute_query(insert_query, (student_id, vac_id, score))
            saved_count += 1
        
        return saved_count
    
    def recommend_for_all_students(self, limit=10):
        query = f"SELECT student_id FROM {TABLE_STUDENTS}"
        students = self.db.execute_query(query, fetch=True)
        
        if not students:
            print("Нет студентов в БД")
            return
        
        total_recommendations = 0
        for student_row in students:
            student_id = student_row[0]
            recommendations = self.recommend_for_student(student_id, limit)
            
            if recommendations:
                saved = self.save_recommendations(student_id, recommendations)
                total_recommendations += saved
            else:
                print(f"Студент {student_id}: нет подходящих вакансий")
        
        print(f"Создано {total_recommendations} рекомендаций")
    
    def get_recommendations(self, student_id):
        query = f"""
        SELECT r.recommendation_id, r.vacancy_hh_id, r.match_score, r.created_at,
               v.title, v.company_hh_id, v.area_hh_id,
               a.area_name, c.company_name
        FROM {TABLE_RECOMMENDATIONS} r
        JOIN {TABLE_VACANCIES} v ON r.vacancy_hh_id = v.vacancy_hh_id
        LEFT JOIN {TABLE_AREAS} a ON v.area_hh_id = a.area_hh_id
        LEFT JOIN {TABLE_COMPANIES} c ON v.company_hh_id = c.company_hh_id
        WHERE r.student_id = %s
        ORDER BY r.match_score DESC
        """
        return self.db.execute_query(query, (student_id,), fetch=True)