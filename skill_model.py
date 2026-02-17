from datetime import datetime

class Skill:
    def __init__(self, vacancy_hh_id, skill_name):
        self.vacancy_hh_id = vacancy_hh_id
        self.skill_name = skill_name
    
    def to_tuple(self):
        return (self.vacancy_hh_id, self.skill_name)