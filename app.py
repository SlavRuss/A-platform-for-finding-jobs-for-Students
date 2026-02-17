from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import psycopg2
from config.settings import DB_CONFIG
from database.user_crud import UserCRUD
from database.vacancy_crud import VacancyCRUD
from database.recommendation_crud import RecommendationCRUD
from parsers.hh_parser import HHParser

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        port=DB_CONFIG['port']
    )
    conn.autocommit = True
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/vladivostok_companies')
def get_vladivostok_companies():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            c.company_hh_id,
            c.company_name,
            COUNT(v.vacancy_hh_id) as vacancy_count,
            MIN(v.publication_date) as first_vacancy_date,
            MAX(v.publication_date) as last_vacancy_date
        FROM msod4.companies c
        JOIN msod4.vacancies v ON c.company_hh_id = v.company_hh_id
        WHERE v.area_hh_id = 22
        GROUP BY c.company_hh_id, c.company_name
        ORDER BY vacancy_count DESC
        LIMIT 50
        """
        
        cursor.execute(query)
        companies = cursor.fetchall()
        
        result = []
        for company in companies:
            result.append({
                'id': company[0],
                'name': company[1],
                'vacancy_count': company[2],
                'first_vacancy': company[3].strftime('%d.%m.%Y') if company[3] else None,
                'last_vacancy': company[4].strftime('%d.%m.%Y') if company[4] else None
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/students')
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            s.student_id,
            s.full_name,
            s.skills,
            s.city_id,
            COALESCE(a.area_name, 'Не указан') as city_name,
            COUNT(DISTINCT r.vacancy_hh_id) as recommendation_count,
            s.skill_ids
        FROM msod4.students s
        LEFT JOIN msod4.areas a ON s.city_id = a.area_hh_id
        LEFT JOIN msod4.recommendations r ON s.student_id = r.student_id
        GROUP BY s.student_id, s.full_name, s.skills, s.city_id, a.area_name, s.skill_ids
        ORDER BY s.student_id
        """
        
        cursor.execute(query)
        students = cursor.fetchall()
        
        result = []
        for student in students:
            skill_names = []
            if student[6]:
                for skill_id in student[6]:
                    cursor.execute("SELECT skill_name FROM msod4.skills WHERE skill_id = %s", (skill_id,))
                    skill = cursor.fetchone()
                    if skill:
                        skill_names.append(skill[0])
            
            result.append({
                'id': student[0],
                'full_name': student[1],
                'skills': skill_names,
                'city_id': student[3],
                'city_name': student[4],
                'recommendation_count': student[5],
                'skill_ids': student[6]
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/students/add', methods=['POST'])
def add_student():
    data = request.json
    user_crud = UserCRUD()
    
    try:
        student_id = data.get('student_id')
        full_name = data.get('full_name')
        skill_ids = data.get('skill_ids', [])
        city_id = data.get('city_id', 113)
        
        if not student_id or not full_name:
            return jsonify({'error': 'ID и ФИО обязательны'}), 400
        
        skill_ids_str = ','.join(map(str, skill_ids)) if skill_ids else ''
        user_crud.add_user(student_id, full_name, skill_ids_str, city_id)
        
        return jsonify({'success': True, 'message': 'Студент добавлен'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students/<int:student_id>/delete', methods=['DELETE'])
def delete_student(student_id):
    user_crud = UserCRUD()
    
    try:
        user_crud.delete_user(student_id)
        return jsonify({'success': True, 'message': 'Студент удален'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/skills')
def get_skills():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT skill_id, skill_name FROM msod4.skills ORDER BY skill_name")
        skills = cursor.fetchall()
        
        result = [{'id': s[0], 'name': s[1]} for s in skills]
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/areas')
def get_areas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT area_hh_id, area_name FROM msod4.areas ORDER BY area_name")
        areas = cursor.fetchall()
        
        result = [{'id': a[0], 'name': a[1]} for a in areas]
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vacancies')
def get_vacancies():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        limit = request.args.get('limit', 50, type=int)
        area_id = request.args.get('area_id', type=int)
        
        query = """
        SELECT 
            v.vacancy_hh_id,
            v.title,
            v.publication_date,
            v.salary_from,
            v.salary_to,
            v.salary_currency,
            c.company_name,
            a.area_name,
            ARRAY_AGG(DISTINCT vs.skill) as skills
        FROM msod4.vacancies v
        LEFT JOIN msod4.companies c ON v.company_hh_id = c.company_hh_id
        LEFT JOIN msod4.areas a ON v.area_hh_id = a.area_hh_id
        LEFT JOIN msod4.vacancy_skills vs ON v.vacancy_hh_id = vs.vacancy_hh_id
        WHERE v.archive = false AND (v.on_deleted = false OR v.on_deleted IS NULL)
        """
        
        params = []
        
        if area_id:
            query += " AND v.area_hh_id = %s"
            params.append(area_id)
        
        query += """
        GROUP BY v.vacancy_hh_id, v.title, v.publication_date, 
                 v.salary_from, v.salary_to, v.salary_currency,
                 c.company_name, a.area_name
        ORDER BY v.publication_date DESC NULLS LAST
        LIMIT %s
        """
        params.append(limit)
        
        cursor.execute(query, params)
        vacancies = cursor.fetchall()
        
        result = []
        for vacancy in vacancies:
            salary = None
            if vacancy[3] or vacancy[4]:
                if vacancy[3] and vacancy[4]:
                    salary = f"{vacancy[3]:,} - {vacancy[4]:,} {vacancy[5] or ''}".strip()
                elif vacancy[3]:
                    salary = f"от {vacancy[3]:,} {vacancy[5] or ''}".strip()
                elif vacancy[4]:
                    salary = f"до {vacancy[4]:,} {vacancy[5] or ''}".strip()
            
            result.append({
                'id': vacancy[0],
                'title': vacancy[1],
                'publication_date': vacancy[2].strftime('%d.%m.%Y') if vacancy[2] else None,
                'salary': salary,
                'company': vacancy[6] or 'Не указано',
                'area': vacancy[7] or 'Не указано',
                'skills': [skill for skill in vacancy[8] if skill] if vacancy[8] else []
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/vacancies/load', methods=['POST'])
def load_vacancies():
    data = request.json
    area_id = data.get('area_id', 113)
    parser = HHParser()
    vacancy_crud = VacancyCRUD()
    
    try:
        vacancies = parser.fetch_vacancies(per_page=20, pages=1, area=area_id, search_text="программист OR разработчик")
        
        if vacancies:
            vacancy_crud.add_vacancies_batch(vacancies)
            
            for vacancy in vacancies:
                skills = parser.extract_skills_from_vacancy(vacancy.vacancy_id)
                if skills:
                    from database.skill_crud import SkillCRUD
                    skill_crud = SkillCRUD()
                    skill_crud.add_skills_batch(skills)
            
            return jsonify({'success': True, 'message': f'Загружено {len(vacancies)} вакансий'})
        else:
            return jsonify({'error': 'Не удалось загрузить вакансии'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/vacancies/refresh', methods=['POST'])
def refresh_vacancies():
    data = request.json
    area_id = data.get('area_id', 113)
    parser = HHParser()
    vacancy_crud = VacancyCRUD()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM msod4.vacancy_skills WHERE vacancy_hh_id IN (SELECT vacancy_hh_id FROM msod4.vacancies WHERE area_hh_id = %s)", (area_id,))
        cursor.execute("DELETE FROM msod4.recommendations WHERE vacancy_hh_id IN (SELECT vacancy_hh_id FROM msod4.vacancies WHERE area_hh_id = %s)", (area_id,))
        cursor.execute("DELETE FROM msod4.vacancies WHERE area_hh_id = %s", (area_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        vacancies = parser.fetch_vacancies(per_page=20, pages=2, area=area_id, search_text="программист OR разработчик OR it")
        
        if vacancies:
            vacancy_crud.add_vacancies_batch(vacancies)
            
            for vacancy in vacancies:
                skills = parser.extract_skills_from_vacancy(vacancy.vacancy_id)
                if skills:
                    from database.skill_crud import SkillCRUD
                    skill_crud = SkillCRUD()
                    skill_crud.add_skills_batch(skills)
            
            return jsonify({'success': True, 'message': f'Загружено {len(vacancies)} вакансий'})
        else:
            return jsonify({'error': 'Не удалось загрузить вакансии'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM msod4.students")
        stats['students_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM msod4.vacancies WHERE archive = false AND (on_deleted = false OR on_deleted IS NULL)")
        stats['vacancies_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM msod4.companies")
        stats['companies_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT skill) FROM msod4.vacancy_skills")
        stats['unique_skills'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM msod4.recommendations")
        stats['recommendations_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM msod4.vacancies WHERE area_hh_id = 22 AND archive = false AND (on_deleted = false OR on_deleted IS NULL)")
        stats['vladivostok_vacancies'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(DISTINCT company_hh_id) 
            FROM msod4.vacancies 
            WHERE area_hh_id = 22 AND archive = false AND (on_deleted = false OR on_deleted IS NULL)
        """)
        stats['vladivostok_companies'] = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT skill, COUNT(*) as count
            FROM msod4.vacancy_skills vs
            JOIN msod4.vacancies v ON vs.vacancy_hh_id = v.vacancy_hh_id
            WHERE v.archive = false AND (v.on_deleted = false OR v.on_deleted IS NULL)
            GROUP BY skill
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_skills'] = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/<int:student_id>/recommendations')
def get_student_recommendations(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        SELECT 
            r.recommendation_id,
            r.vacancy_hh_id,
            r.match_score,
            r.created_at,
            v.title,
            v.company_hh_id,
            v.area_hh_id,
            a.area_name,
            c.company_name,
            ARRAY_AGG(DISTINCT vs.skill) as skills
        FROM msod4.recommendations r
        JOIN msod4.vacancies v ON r.vacancy_hh_id = v.vacancy_hh_id
        LEFT JOIN msod4.areas a ON v.area_hh_id = a.area_hh_id
        LEFT JOIN msod4.companies c ON v.company_hh_id = c.company_hh_id
        LEFT JOIN msod4.vacancy_skills vs ON v.vacancy_hh_id = vs.vacancy_hh_id
        WHERE r.student_id = %s AND v.archive = false AND (v.on_deleted = false OR v.on_deleted IS NULL)
        GROUP BY r.recommendation_id, r.vacancy_hh_id, r.match_score, r.created_at,
                 v.title, v.company_hh_id, v.area_hh_id, a.area_name, c.company_name
        ORDER BY r.match_score DESC
        LIMIT 20
        """
        
        cursor.execute(query, (student_id,))
        recommendations = cursor.fetchall()
        
        result = []
        for rec in recommendations:
            result.append({
                'recommendation_id': rec[0],
                'vacancy_id': rec[1],
                'match_score': float(rec[2]),
                'created_at': rec[3].strftime('%d.%m.%Y %H:%M') if rec[3] else None,
                'title': rec[4],
                'company_id': rec[5],
                'area_id': rec[6],
                'area_name': rec[7],
                'company_name': rec[8],
                'skills': [skill for skill in rec[9] if skill] if rec[9] else []
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/student/<int:student_id>/recommendations/generate', methods=['POST'])
def generate_student_recommendations(student_id):
    data = request.json
    limit = data.get('limit', 10)
    rec_crud = RecommendationCRUD()
    
    try:
        recommendations = rec_crud.recommend_for_student(student_id, limit=limit)
        
        if recommendations:
            saved = rec_crud.save_recommendations(student_id, recommendations)
            return jsonify({'success': True, 'message': f'Создано {saved} рекомендаций', 'count': saved})
        else:
            return jsonify({'success': False, 'message': 'Нет подходящих вакансий', 'count': 0})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/debug/db_check')
def debug_db_check():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        result = {}
        
        # Проверяем все таблицы
        tables = ['students', 'vacancies', 'companies', 'areas', 'recommendations', 'vacancy_skills', 'skills']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM msod4.{table}")
                count = cursor.fetchone()[0]
                result[f'{table}_count'] = count
                
                # Покажем примеры данных
                if count > 0:
                    cursor.execute(f"SELECT * FROM msod4.{table} LIMIT 1")
                    columns = [desc[0] for desc in cursor.description]
                    result[f'{table}_sample'] = dict(zip(columns, cursor.fetchone()))
                else:
                    result[f'{table}_sample'] = 'No data'
                    
            except Exception as e:
                result[f'{table}_error'] = str(e)
        
        # Проверим конкретно статистику
        cursor.execute("""
            SELECT 
                COUNT(*) as total_vacancies,
                COUNT(CASE WHEN archive = false AND (on_deleted = false OR on_deleted IS NULL) THEN 1 END) as active_vacancies
            FROM msod4.vacancies
        """)
        vac_stats = cursor.fetchone()
        result['vacancy_stats'] = {
            'total': vac_stats[0],
            'active': vac_stats[1]
        }
        
        # Проверим Владивосток
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT company_hh_id) as companies
            FROM msod4.vacancies 
            WHERE area_hh_id = 22
        """)
        vlad_stats = cursor.fetchone()
        result['vladivostok'] = {
            'vacancies': vlad_stats[0],
            'companies': vlad_stats[1]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/debug/statistics_query')
def debug_statistics_query():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        result = {}
        
        # Проверим каждый запрос по отдельности
        queries = {
            'students': "SELECT COUNT(*) FROM msod4.students",
            'vacancies': "SELECT COUNT(*) FROM msod4.vacancies WHERE archive = false AND (on_deleted = false OR on_deleted IS NULL)",
            'companies': "SELECT COUNT(*) FROM msod4.companies",
            'unique_skills': "SELECT COUNT(DISTINCT skill) FROM msod4.vacancy_skills",
            'recommendations': "SELECT COUNT(*) FROM msod4.recommendations",
            'vlad_vacancies': "SELECT COUNT(*) FROM msod4.vacancies WHERE area_hh_id = 22 AND archive = false AND (on_deleted = false OR on_deleted IS NULL)",
            'vlad_companies': "SELECT COUNT(DISTINCT company_hh_id) FROM msod4.vacancies WHERE area_hh_id = 22 AND archive = false AND (on_deleted = false OR on_deleted IS NULL)"
        }
        
        for name, query in queries.items():
            try:
                cursor.execute(query)
                result[name] = cursor.fetchone()[0]
            except Exception as e:
                result[name] = f"Error: {str(e)}"
        
        # Проверим топ навыки
        try:
            cursor.execute("""
                SELECT skill, COUNT(*) as count
                FROM msod4.vacancy_skills vs
                JOIN msod4.vacancies v ON vs.vacancy_hh_id = v.vacancy_hh_id
                WHERE v.archive = false AND (v.on_deleted = false OR v.on_deleted IS NULL)
                GROUP BY skill
                ORDER BY count DESC
                LIMIT 10
            """)
            result['top_skills'] = cursor.fetchall()
        except Exception as e:
            result['top_skills_error'] = str(e)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)