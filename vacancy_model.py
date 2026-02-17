from datetime import datetime

class Vacancy:
    def __init__(self, hh_id, title, company_hh_id=None, area_hh_id=None, 
                 salary_from=None, salary_to=None, salary_currency=None,
                 salary_gross=None, schedule=None, snippet_responsibility=None,
                 snippet_requirement=None, real_salary=None, id_prof=None,
                 company_name=None, area_name=None):
        self.vacancy_id = hh_id 
        self.title = title
        self.publication_date = datetime.now().date()
        self.company_id = company_hh_id  
        self.area_id = area_hh_id  
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = salary_currency
        self.salary_gross = salary_gross if salary_gross is not None else False
        self.schedule = schedule
        self.snippet_responsibility = snippet_responsibility
        self.snippet_requirement = snippet_requirement
        self.real_salary = real_salary if real_salary is not None else 0.0
        self.profession_id = id_prof  
        self.company_name = company_name
        self.area_name = area_name
        self.created_at = datetime.now()  
        self.updated_at = datetime.now()  
    
    def __str__(self):
        return f"Vacancy({self.vacancy_id}: {self.title})"