import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': '89.223.65.229',
    'database': 'msod_database',
    'schema': 'msod4',
    'user': 'neural_net_designer',
    'password': 'Relu@C0nv0lute',
    'port': 5432
}

HH_API_URL = 'https://api.hh.ru/vacancies'

# Специализации для IT вакансий
IT_SPECIALIZATIONS = [
    1,    # Информационные технологии, интернет, телеком
    2,    # Разработка, программирование
    3,    # Тестирование
    4,    # Аналитика
    5,    # Дизайн
    9,    # Администрирование
    10,   # Безопасность
    12,   # Data Science
]

# Таблицы в базе данных
TABLE_STUDENTS = 'students'  
TABLE_VACANCIES = 'vacancies'  
TABLE_VACANCY_SKILLS = 'vacancy_skills' 
TABLE_RECOMMENDATIONS = 'recommendations'

# Новые таблицы для Части 2
TABLE_SKILLS = 'skills'
TABLE_COMPANIES = 'companies'
TABLE_AREAS = 'areas'
TABLE_STUDENT_SKILLS = 'student_skills'

# Предопределенные навыки с ID
PREDEFINED_SKILLS = [
    (1, 'Python'),
    (2, 'Java'),
    (3, 'JavaScript'),
    (4, 'SQL'),
    (5, 'HTML'),
    (6, 'CSS'),
    (7, 'React'),
    (8, 'Vue'),
    (9, 'Angular'),
    (10, 'Django'),
    (11, 'Flask'),
    (12, 'Spring'),
    (13, 'Docker'),
    (14, 'Kubernetes'),
    (15, 'Git'),
    (16, 'PostgreSQL'),
    (17, 'MySQL'),
    (18, 'MongoDB'),
    (19, 'Redis'),
    (20, 'AWS'),
    (21, 'Azure'),
    (22, 'Linux'),
    (23, 'Машинное обучение'),
    (24, 'ML'),
    (25, 'AI'),
    (26, 'Анализ данных'),
    (27, 'Power BI'),
    (28, 'Tableau'),
    (29, 'Excel'),
    (30, 'Pandas'),
    (31, 'NumPy'),
    (32, 'TensorFlow'),
    (33, 'PyTorch'),
    (34, 'ООП'),
    (35, 'REST API'),
    (36, 'C++'),
    (37, 'C#'),
    (38, '.NET'),
    (39, 'PHP'),
    (40, 'Go'),
    (41, 'Ruby'),
    (42, 'Swift'),
    (43, 'Kotlin'),
    (44, 'TypeScript'),
    (45, 'Node.js'),
    (46, 'Express.js'),
    (47, 'Vue.js'),
    (48, 'React Native'),
    (49, 'Flutter'),
    (50, 'Android')
]

# Регионы России
RUSSIAN_REGIONS = {
    1: 'Москва',
    2: 'Санкт-Петербург',
    3: 'Екатеринбург',
    4: 'Новосибирск',
    5: 'Казань',
    6: 'Нижний Новгород',
    7: 'Красноярск',
    8: 'Челябинск',
    9: 'Самара',
    10: 'Уфа',
    11: 'Ростов-на-Дону',
    12: 'Краснодар',
    13: 'Пермь',
    14: 'Воронеж',
    15: 'Волгоград',
    16: 'Саратов',
    17: 'Тюмень',
    18: 'Тольятти',
    19: 'Ижевск',
    20: 'Барнаул',
    22: 'Владивосток',
    113: 'Россия'
}