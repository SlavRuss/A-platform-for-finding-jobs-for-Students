from datetime import datetime

class Company:
    def __init__(self, company_hh_id, company_name):
        self.company_hh_id = company_hh_id
        self.company_name = company_name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_tuple(self):
        return (self.company_hh_id, self.company_name, self.created_at, self.updated_at)