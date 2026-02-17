import requests
import time
from datetime import datetime
from config.settings import HH_API_URL
from models.vacancy_model import Vacancy
from models.skill_model import Skill

class HHParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HH-Parser/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_vacancies(self, per_page=20, pages=1, area=None, search_text=None):
        if area is None:
            area = 113  
            
        if search_text is None:
            search_text = 'IT OR программист OR разработчик'
        
        all_vacancies = []
        
        for page in range(pages):
            params = {
                'text': search_text,
                'area': area,
                'per_page': per_page,
                'page': page,
                'only_with_salary': 'false',  
                'period': 30  
            }
            
            try:
                print(f"Запрос страницы {page+1}...")
                response = self.session.get(HH_API_URL, params=params, timeout=30)
                
                if response.status_code == 400:
                    print(f"Ошибка 400.")
                    params_simple = {
                        'text': 'программист',
                        'area': area,
                        'per_page': 10,
                        'page': page
                    }
                    response = self.session.get(HH_API_URL, params=params_simple, timeout=30)
                
                response.raise_for_status()
                data = response.json()
                
                items = data.get('items', [])
                print(f"Найдено вакансий на странице {page+1}: {len(items)}")
                
                for item in items:
                    vacancy = self.parse_vacancy(item)
                    if vacancy:
                        all_vacancies.append(vacancy)
                
                pages_total = data.get('pages', 1)
                if page >= pages_total - 1:
                    print(f"Это последняя страница (всего {pages_total})")
                    break
                
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке страницы {page+1}: {e}")
                if hasattr(e, 'response') and e.response:
                    print(f"Ответ API: {e.response.text[:200]}")
                continue
            except Exception as e:
                print(f"Неожиданная ошибка: {e}")
                continue
        
        print(f"Всего собрано вакансий: {len(all_vacancies)}")
        return all_vacancies
    
    def parse_vacancy(self, item):
        try:
            vacancy_id = item.get('id')
            title = item.get('name', '')
            
            published_at = item.get('published_at', '')
            if published_at:
                try:
                    publication_date = datetime.fromisoformat(published_at.replace('Z', '+00:00')).date()
                except:
                    publication_date = datetime.now().date()
            else:
                publication_date = datetime.now().date()
            
            salary = item.get('salary')
            salary_from = None
            salary_to = None
            salary_currency = None
            salary_gross = None
            
            if salary:
                salary_from = salary.get('from')
                salary_to = salary.get('to')
                salary_currency = salary.get('currency')
                salary_gross = salary.get('gross')
            
            employer = item.get('employer', {})
            company_id = employer.get('id')
            company_name = employer.get('name', '')
            
            area = item.get('area', {})
            area_id = area.get('id')
            area_name = area.get('name', '')
            
            schedule = item.get('schedule', {})
            schedule_name = schedule.get('name', '')
            
            snippet = item.get('snippet', {})
            responsibility = snippet.get('responsibility', '')
            requirement = snippet.get('requirement', '')
            
            vacancy = Vacancy(
                hh_id=vacancy_id,
                title=title,
                company_hh_id=company_id,
                area_hh_id=area_id,
                salary_from=salary_from,
                salary_to=salary_to,
                salary_currency=salary_currency,
                salary_gross=salary_gross,
                schedule=schedule_name,
                snippet_responsibility=responsibility,
                snippet_requirement=requirement,
                company_name=company_name,
                area_name=area_name
            )
            
            vacancy.publication_date = publication_date
            
            return vacancy
            
        except Exception as e:
            print(f"Ошибка парсинга вакансии {item.get('id', 'N/A')}: {e}")
            return None
    
    def extract_skills_from_vacancy(self, vacancy_id):
        try:
            print(f"Загрузка навыков для вакансии {vacancy_id}")
            response = self.session.get(f"{HH_API_URL}/{vacancy_id}", timeout=30)
            response.raise_for_status()
            data = response.json()
            
            skills = []
            key_skills = data.get('key_skills', [])
            
            for skill in key_skills:
                skill_name = skill.get('name', '').strip()
                if skill_name:
                    skills.append(Skill(vacancy_id, skill_name))
            
            if skills:
                print(f"Найдено навыков: {len(skills)}")
            else:
                print("Навыки не найдены")
            
            return skills
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке навыков для вакансии {vacancy_id}: {e}")
            return []
    
    def fetch_vacancies_with_skills(self, per_page=10, pages=1, area=None):
        print("Начало загрузки вакансий с навыками")

        vacancies = self.fetch_vacancies(per_page=per_page, pages=pages, area=area)
        
        all_skills = []
        total_vacancies = len(vacancies)
        
        if total_vacancies == 0:
            print("Нет вакансий для извлечения навыков")
            return [], []
        
        print(f"Извлечение навыки для {total_vacancies} вакансий")
        
        for i, vacancy in enumerate(vacancies):
            print(f"Вакансия {i+1}/{total_vacancies}: {vacancy.title[:50]}...")
            skills = self.extract_skills_from_vacancy(vacancy.vacancy_id)
            all_skills.extend(skills)

            time.sleep(0.3)
        
        print(f"Всего извлечено навыков: {len(all_skills)}")
        return vacancies, all_skills
    
    def test_api_connection(self):
        try:
            test_params = {
                'text': 'тест',
                'per_page': 1
            }
            response = self.session.get(HH_API_URL, params=test_params, timeout=10)
            
            if response.status_code == 200:
                print("✓ API HH доступен")
                return True
            else:
                print(f"X API HH недоступен. Код: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"X Ошибка соединения с API HH: {e}")
            return False
        
def extract_company_and_area_data(self, vacancy_data):
    """Извлечь данные компании и региона из вакансии"""
    company_data = None
    area_data = None
    
    employer = vacancy_data.get('employer', {})
    if employer and employer.get('id'):
        company_data = {
            'company_hh_id': employer.get('id'),
            'company_name': employer.get('name', '')
        }
    
    area = vacancy_data.get('area', {})
    if area and area.get('id'):
        area_data = {
            'area_hh_id': area.get('id'),
            'area_name': area.get('name', '')
        }
    
    return company_data, area_data

def fetch_and_save_all_data(self, per_page=10, pages=1, area=113):
    """Загрузить и сохранить все данные: вакансии, компании, регионы, навыки"""
    print("Загрузка полных данных с HH...")
    
    # Загружаем вакансии
    vacancies = self.fetch_vacancies(per_page=per_page, pages=pages, area=area)
    
    all_companies = []
    all_areas = []
    all_vacancies = []
    all_skills = []
    
    # Собираем уникальные компании и регионы
    companies_seen = set()
    areas_seen = set()
    
    for vacancy in vacancies:
        # Сохраняем вакансию
        all_vacancies.append(vacancy)
        
        # Извлекаем компанию
        if vacancy.company_id and vacancy.company_id not in companies_seen:
            from models.company_model import Company
            company = Company(
                company_hh_id=vacancy.company_id,
                company_name=vacancy.company_name or "Неизвестная компания"
            )
            all_companies.append(company)
            companies_seen.add(vacancy.company_id)
        
        # Извлекаем регион
        if vacancy.area_id and vacancy.area_id not in areas_seen:
            from models.area_model import Area
            area_obj = Area(
                area_hh_id=vacancy.area_id,
                area_name=vacancy.area_name or "Неизвестный регион"
            )
            all_areas.append(area_obj)
            areas_seen.add(vacancy.area_id)
        
        # Извлекаем навыки
        skills = self.extract_skills_from_vacancy(vacancy.vacancy_id)
        all_skills.extend(skills)
        time.sleep(0.3)  # Задержка
    
    return {
        'vacancies': all_vacancies,
        'companies': all_companies,
        'areas': all_areas,
        'skills': all_skills
    }