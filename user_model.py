class User:
    def __init__(self, user_id, full_name, skills, city_id=None):
        self.user_id = user_id
        self.full_name = full_name
        self.skills = skills if isinstance(skills, list) else [skills]
        self.city_id = city_id
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'full_name': self.full_name,
            'skills': self.skills,
            'city_id': self.city_id
        }