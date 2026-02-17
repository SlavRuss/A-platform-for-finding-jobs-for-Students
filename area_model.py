from datetime import datetime

class Area:
    def __init__(self, area_hh_id, area_name):
        self.area_hh_id = area_hh_id
        self.area_name = area_name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_tuple(self):
        return (self.area_hh_id, self.area_name, self.created_at, self.updated_at)