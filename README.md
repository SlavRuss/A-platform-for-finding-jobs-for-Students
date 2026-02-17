Веб-Система мониторинга вакансий по бизнес-ролям

Веб-приложение для мониторинга IT-вакансий с HeadHunter, управления студентами и генерации рекомендаций на основе навыков.

===============================================================

Чтобы запустить:

- Python 3.8+
- PostgreSQL 12+
- Git

python -m venv .venv

.venv\Scripts\activate

Сайт:

python app.py

Консоль разработчика:

python main.py

Открыть http://127.0.0.1:5000

===============================================================
Важные файлы
===============================================================

Бэкенд (Python/Flask)
- app.py - основной файл приложения, REST API endpoints
- main.py - консольный интерфейс для разработчика
- parsers/hh_parser.py - парсер вакансий с HeadHunter API

===============================================================

База данных (PostgreSQL)
- config/database.py - подключение к БД
- config/settings.py - конфигурация и настройки
- database/init_database.py - инициализация таблиц

===============================================================

CRUD операции
- database/user_crud.py - управление студентами
- database/vacancy_crud.py - управление вакансиями
- database/skill_crud.py - управление навыками вакансий
- database/skill_crud_new.py - управление справочником навыков
- database/company_crud.py - управление компаниями
- database/area_crud.py - управление регионами
- database/recommendation_crud.py - генерация рекомендаций

===============================================================

Модели данных
- models/user_model.py - модель студента
- models/vacancy_model.py - модель вакансии
- models/skill_model.py - модель навыка
- models/company_model.py - модель компании
- models/area_model.py - модель региона

===============================================================

Фронтенд
- templates/index.html - главная страница
- static/css/style.css - стили
- static/js/main.js - клиентская логика

===============================================================

Структура базы данных

 Основные таблицы (схема msod4)

 students - студенты, их навыки и город 
 vacancies - вакансии с HeadHunter  
 companies - компании-работодатели  
 areas - регионы и города России 
 skills - навыки общие
 student_skills - связь студентов с навыками  
 vacancy_skills - навыки, требуемые в вакансиях  
 recommendations - рекомендации для студентов 

===============================================================

Структура проекта:

vacancy-monitoring/
├── requirements.txt
├── app.py
├── main.py
├── cleanup.py
├── init_database.py
├── load_regions.py
├── regions.py
├── config/
│   ├── __init__.py
│   ├── database.py
│   └── settings.py
├── database/
│   ├── __init__.py
│   ├── area_crud.py
│   ├── company_crud.py
│   ├── init_database.py
│   ├── recommendation.py
│   ├── recommendation_crud.py
│   ├── skill_crud.py
│   ├── skill_crud_new.py
│   ├── user_crud.py
│   └── vacancy_crud.py
├── models/
│   ├── __init__.py
│   ├── area_model.py
│   ├── company_model.py
│   ├── skill_model.py
│   ├── user_model.py
│   └── vacancy_model.py
├── parsers/
│   ├── __init__.py
│   └── hh_parser.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   └── index.html
└── utils/
    └── helpers.py

===============================================================
