# main.py
from database.user_crud import UserCRUD
from database.vacancy_crud import VacancyCRUD
from database.skill_crud import SkillCRUD
from database.recommendation_crud import RecommendationCRUD
from parsers.hh_parser import HHParser

def initialize_database():
    print("Инициализация работы с базой данных")
    
    user_crud = UserCRUD()
    vacancy_crud = VacancyCRUD()
    skill_crud = SkillCRUD()
    
    print("\nПроверка структуры таблиц:")
    
    print("\n1) Таблица students:")
    students_structure = user_crud.check_students_table_structure()
    for col in students_structure:
        print(f"  - {col[0]} ({col[1]})")
    
    print("\n2) Таблица vacancies:")
    vacancies_structure = vacancy_crud.check_vacancies_table_structure()
    for col in vacancies_structure:
        print(f"  - {col[0]} ({col[1]})")
    
    print("\n3) Таблица vacancy_skills:")
    skills_structure = skill_crud.check_skills_table_structure()
    for col in skills_structure:
        print(f"  - {col[0]} ({col[1]})")
    
    print("\nБД готова к работе")

def user_management_menu():
    user_crud = UserCRUD()
    
    has_city = user_crud.check_table_has_city()
    
    while True:
        print("\n===Меню управление студентами===")
        print("1) Добавить студента")
        print("2) Просмотреть всех студентов")
        print("3) Найти студента по ID")
        print("4) Найти студента с навыками из таблицы skills")
        print("5) Удалить студента")
        print("6) Удалить всех студентов")
        print("7) Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            try:
                student_id = int(input("ID студента: "))
                full_name = input("ФИО: ")
                print("ID навыков через запятую (навыки брать из таблицы skills):")
                skill_ids_input = input("ID навыков: ")
                
                city_id = None
                if has_city:
                    print("\n1 - Москва, 2 - СПб, 3 - Екатеринбург, 4 - Новосибирск, 5 - Казань, 22 - Владивосток, 113 - Россия")
                    city_input = input("ID города (Enter для России): ").strip()
                    if city_input:
                        city_id = int(city_input) if city_input != "0" else None
                    else:
                        city_id = 113
                
                added_count = user_crud.add_user(student_id, full_name, skill_ids_input, city_id)
                print(f"Студент {full_name} добавлен. Связано навыков: {added_count}")
            except ValueError:
                print("Ошибка ввода числа")
            
        elif choice == '2':
            users = user_crud.get_all_users()
            if users:
                print(f"\nВсего студентов: {len(users)}")
                for user in users:
                    print(f"ID: {user[0]}")
                    print(f"ФИО: {user[1]}")
                    print(f"Навыки: {user[2] if user[2] else 'Нет'}")
                    if user[4]:
                        print(f"ID навыков: {user[4]}")
                    if has_city:
                        city_display = user[3] if user[3] is not None else "Не указан"
                        city_name = user_crud.get_city_name(user[3]) if user[3] is not None else "Не указан"
                        print(f"Город: {city_name} (ID: {city_display})")
                    print("-" * 40)
            else:
                print("Студенты не найдены")
                
        elif choice == '3':
            try:
                student_id = int(input("Введите ID студента: "))
                user = user_crud.get_user_by_id(student_id)
                if user:
                    print(f"ID: {user[0]}")
                    print(f"ФИО: {user[1]}")
                    print(f"Навыки: {user[2] if user[2] else 'Нет'}")
                    if has_city:
                        city_display = user[3] if user[3] is not None else "Не указан"
                        city_name = user_crud.get_city_name(user[3]) if user[3] is not None else "Не указан"
                        print(f"Город: {city_name} (ID: {city_display})")
                    if user[4]:
                        print(f"ID навыков: {user[4]}")
                else:
                    print("Студент не найден")
            except ValueError:
                print("ID должен быть числом")

        elif choice == '4':
            try:
                student_id = int(input("Введите ID студента: "))
                user = user_crud.get_user_with_skills(student_id)
                if user:
                    print(f"ID: {user[0]}")
                    print(f"ФИО: {user[1]}")
                    
                    if user[2]:
                        skills_text = user[2] if isinstance(user[2], list) else [user[2]]
                        for skill in skills_text:
                            print(f"  • {skill}")
                    
                    if user[4]:
                        print(f"ID навыков: {user[4]}")
                    
                    if user[5] and any(user[5]):
                        skill_names = user[5]
                        skill_ids_detail = user[6] if user[6] else []
                        
                        for i, skill_name in enumerate(skill_names, 1):
                            if skill_name:
                                skill_id = skill_ids_detail[i-1] if i-1 < len(skill_ids_detail) else "N/A"
                                print(f"  {i:2d}. {skill_name} (ID: {skill_id}")
                    else:
                        print(f"Нет связанных навыков")
                    
                    if has_city:
                        city_display = user[3] if user[3] is not None else "Не указан"
                        city_name = user_crud.get_city_name(user[3]) if user[3] is not None else "Не указан"
                        print(f"Город: {city_name} (ID: {city_display})")
                else:
                    print("Студент не найден")
            except ValueError:
                print("ID должен быть числом")
                
        elif choice == '5':
            try:
                student_id = int(input("Введите ID студента для удаления: "))
                user = user_crud.get_user_by_id(student_id)
                if user:
                    confirm = input(f"Удалить студента '{user[1]}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        user_crud.delete_user(student_id)
                        print("Студент удален")
                else:
                    print("Студент не найден")
            except ValueError:
                print("ID должен быть числом")
            
        elif choice == '6':
            confirm = input("Удалить ВСЕХ студентов? (yes/no): ")
            if confirm.lower() == 'yes':
                confirm2 = input("Введите 'DELETE ALL': ")
                if confirm2 == 'DELETE ALL':
                    user_crud.delete_all_users()
                    print("Все студенты удалены")
                else:
                    print("Отменено")
            else:
                print("Отменено")
                
        elif choice == '7':
            break

def vacancy_management_menu():
    vacancy_crud = VacancyCRUD()
    parser = HHParser()
    
    while True:
        print("\n===Меню управление вакансиями===")
        print("1) Показать вакансии из БД")
        print("2) Загрузить IT вакансии с HH")
        print("3) Загрузить вакансии с навыками")
        print("4) Найти вакансию по ID")
        print("5) Удалить вакансию")
        print("6) Удалить все вакансию")
        print("7) Тест подключения к HH API")
        print("8) Проверить структуру таблицы vacancies")
        print("9) Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            vacancies = vacancy_crud.get_all_vacancies()
            if vacancies:
                print(f"\nВсего вакансий в БД: {len(vacancies)}")
                print("\nПоследние 10 вакансий:")
                print("=" * 80)
                for vac in vacancies[:10]:
                    print(f"ID вакансии: {vac[0]}")
                    print(f"Название: {vac[1]}")
                    print(f"Дата публикации: {vac[2]}")
                    if len(vac) > 4 and vac[4]:
                        print(f"Регион ID: {vac[4]}")
                    if len(vac) > 5 and vac[5]:
                        print(f"Зарплата от: {vac[5]}")
                    if len(vac) > 6 and vac[6]:
                        print(f"Зарплата до: {vac[6]}")
                    print("-" * 40)
                if len(vacancies) > 10:
                    print(f"\nИ еще {len(vacancies) - 10} вакансий в БД")
            else:
                print("\nВ базе данных нет вакансий")
                
        elif choice == '2':
            try:
                print("\n=== Загрузка IT вакансий с HeadHunter ===")
                
                print("Регионы: 1-Москва, 2-СПб, 3-Екатеринбург, 4-Новосибирск, 5-Казань, 22-Владивосток, 113-Россия")
                area_input = input("ID региона (Enter для России): ").strip()
                area = int(area_input) if area_input else 113
                
                pages = int(input("Страниц для загрузки (1-3): ") or "1")
                per_page = int(input("Вакансий на странице (10-50): ") or "20")
                
                search_text = input("Текст поиска (Enter для 'программист'): ").strip()
                if not search_text:
                    search_text = "программист"
                
                print(f"\nНачинаю загрузку...")
                print(f"Регион: {area}")
                print(f"Поиск: '{search_text}'")
                print(f"Страниц: {pages}")
                print(f"На странице: {per_page}")
                
                vacancies = parser.fetch_vacancies(
                    per_page=per_page,
                    pages=pages,
                    area=area,
                    search_text=search_text
                )
                
                if vacancies:
                    print(f"\nУспешно собрано {len(vacancies)} вакансий")
                    
                    confirm = input("Сохранить в базу данных? (yes/no): ")
                    if confirm.lower() == 'yes':
                        vacancy_crud.add_vacancies_batch(vacancies)
                        print("Вакансии сохранены в БД")
                    else:
                        print("Сохранение отменено")
                else:
                    print("Не удалось загрузить вакансии")
                    
            except ValueError as e:
                print(f"Ошибка ввода: {e}")
            except Exception as e:
                print(f"Ошибка: {e}")
                
        elif choice == '3':
            try:
                print("\n=== Загрузка вакансий с навыками ===")
                print("(Этот процесс может занять несколько минут)")
                
                area = int(input("ID региона (Enter=113 Россия): ") or "113")
                pages = int(input("Страниц (рекомендуется 1-2): ") or "1")
                per_page = int(input("Вакансий на странице (рекомендуется 10): ") or "10")
                
                confirm = input(f"\nЗагрузить {pages * per_page} вакансий с навыками? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("Отменено")
                    continue
                
                vacancies, skills = parser.fetch_vacancies_with_skills(
                    per_page=per_page,
                    pages=pages,
                    area=area
                )
                
                if vacancies:
                    vacancy_crud.add_vacancies_batch(vacancies)
                    print(f"Сохранено {len(vacancies)} вакансий")
                    
                    if skills:
                        skill_crud = SkillCRUD()
                        skill_crud.add_skills_batch(skills)
                        print(f"Сохранено {len(skills)} навыков")
                    else:
                        print("Навыки не найдены")
                else:
                    print("Не удалось загрузить вакансии")
                    
            except Exception as e:
                print(f"Ошибка: {e}")
                
        elif choice == '4':
            vacancy_id = input("Введите ID вакансии: ").strip()
            if vacancy_id:
                vacancy = vacancy_crud.get_vacancy_by_id(vacancy_id)
                if vacancy:
                    print(f"\n=== Вакансия найдена ===")
                    print(f"ID: {vacancy[0]}")
                    print(f"Название: {vacancy[1]}")
                    print(f"Дата публикации: {vacancy[2]}")
                    
                    field_names = [
                        "company_hh_id", "area_hh_id", "salary_from", "salary_to",
                        "salary_currency", "salary_gross", "schedule", 
                        "snippet_responsibility", "snippet_requirement",
                        "real_salary", "id_prof", "archive", "on_deleted",
                        "date_added", "date_updated"
                    ]
                    
                    for i in range(3, len(vacancy)):
                        if vacancy[i] is not None:
                            field_name = field_names[i-3] if i-3 < len(field_names) else f"Поле {i}"
                            print(f"{field_name}: {vacancy[i]}")
                    
                    print("=" * 40)
                else:
                    print("Вакансия не найдена")
                    
        elif choice == '5':
            vacancy_id = input("Введите ID вакансии для удаления: ").strip()
            if vacancy_id:
                vacancy = vacancy_crud.get_vacancy_by_id(vacancy_id)
                if vacancy:
                    confirm = input(f"Удалить вакансию '{vacancy[1]}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        vacancy_crud.delete_vacancy(vacancy_id)
                    else:
                        print("Удаление отменено")
                else:
                    print("Вакансия не найден")
                    
        elif choice == '6':
            confirm = input("Удалить ВСЕ вакансии? (yes/no): ")
            if confirm.lower() == 'yes':
                confirm2 = input("Это необратимо! Введите 'DELETE ALL': ")
                if confirm2 == 'DELETE ALL':
                    vacancy_crud.delete_all_vacancies()
                else:
                    print("Удаление отменено")
            else:
                print("Удаление отменено")
                    
        elif choice == '7':
            print("\nТестирование подключения к HH API...")
            if parser.test_api_connection():
                print("✓ Соединение с API HH успешно установлено")
            else:
                print("✗ Не удалось подключиться к API HH")
                
        elif choice == '8':
            print("\nСтруктура таблицы vacancies:")
            vacancy_crud.print_table_structure()
                
        elif choice == '9':
            break

def skill_management_menu():
    skill_crud = SkillCRUD()
    parser = HHParser()
    
    while True:
        print("\n===Меню управление навыками (вакансии)===")
        print("1) Загрузить навыки с HH")
        print("2) Просмотреть все навыки")
        print("3) Просмотреть навыки вакансии")
        print("4) Удалить навык")
        print("5) Удалить все навыки")
        print("6) Проверить структуру таблицы vacancy_skills")
        print("7) Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            try:
                pages = int(input("Сколько страниц вакансий обработать: "))
                if pages < 1 or pages > 5:
                    print("Ошибка: кол-во страниц должно быть от 1 до 5")
                    continue
                
                print("Загрузка вакансий и навыков...")
                vacancies, skills = parser.fetch_vacancies_with_skills(pages=pages)
                
                if skills:
                    skill_crud.add_skills_batch(skills)
                    print(f"Загружено {len(skills)} навыков")
                else:
                    print("Не удалось загрузить навыки")
                    
            except ValueError:
                print("Ошибка: введите число")
            
        elif choice == '2':
            skills = skill_crud.get_all_skills()
            if skills:
                print(f"\nВсего уникальных навыков: {len(skills)}")
                print("\nТоп-20 навыков:")
                print("-" * 50)
                for i, skill in enumerate(skills[:20], 1):
                    print(f"{i:2d}. {skill[0]:30s} - {skill[1]:4d} вакансий")
                if len(skills) > 20:
                    print(f"\nИ еще {len(skills) - 20} навыков")
            else:
                print("Навыки не найдены")
                
        elif choice == '3':
            try:
                vacancy_id = input("Введите ID вакансии: ")
                skills = skill_crud.get_skills_by_vacancy(vacancy_id)
                if skills:
                    print(f"\nНавыки для вакансии {vacancy_id}:")
                    print("-" * 40)
                    for skill in skills:
                        print(f"  - {skill[0]}")
                    print(f"Всего: {len(skills)} навыков")
                else:
                    print("Навыки не найдены для этой вакансии")
            except Exception as e:
                print(f"Ошибка: {e}")
                
        elif choice == '4':
            skill_name = input("Введите название навыка для удаления: ")
            vacancy_id = input("Введите ID вакансии (оставьте пустым для удаления везде): ")
            if vacancy_id.strip():
                skill_crud.delete_skill(skill_name, vacancy_id)
            else:
                skill_crud.delete_skill(skill_name)
            
        elif choice == '5':
            confirm = input("Удалить ВСЕ навыки? (yes/no): ")
            if confirm.lower() == 'yes':
                confirm2 = input("Это необратимо! Введите 'DELETE ALL': ")
                if confirm2 == 'DELETE ALL':
                    skill_crud.delete_all_skills()
                else:
                    print("Удаление отменено")
            else:
                print("Удаление отменено")
                
        elif choice == '6':
            print("\nСтруктура таблицы vacancy_skills:")
            skill_crud.print_table_structure()
                
        elif choice == '7':
            break

def company_management_menu():
    from database.company_crud import CompanyCRUD
    
    company_crud = CompanyCRUD()
    
    while True:
        print("\n===Меню управление компаниями===")
        print("1) Показать все компании")
        print("2) Найти компанию по ID")
        print("3) Удалить компанию")
        print("4) Удалить все компании")
        print("5) Проверить структуру таблицы companies")
        print("6) Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            companies = company_crud.get_all_companies()
            if companies:
                print(f"\nВсего компаний: {len(companies)}")
                print("-" * 60)
                for company in companies:
                    print(f"ID: {company[0]}")
                    print(f"Название: {company[1]}")
                    print(f"Дата добавления: {company[2]}")
                    print("-" * 40)
            else:
                print("Компании не найдены")
                
        elif choice == '2':
            try:
                company_id = int(input("Введите ID компании: "))
                company = company_crud.get_company_by_id(company_id)
                if company:
                    print(f"\nНайдена компания:")
                    print(f"ID: {company[0]}")
                    print(f"Название: {company[1]}")
                    print(f"Дата добавления: {company[2]}")
                    print(f"Дата обновления: {company[3]}")
                else:
                    print("Компания не найдена")
            except ValueError:
                print("Ошибка: ID должен быть числом")
                
        elif choice == '3':
            try:
                company_id = int(input("Введите ID компании для удаления: "))
                company = company_crud.get_company_by_id(company_id)
                if company:
                    confirm = input(f"Удалить компанию '{company[1]}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        company_crud.delete_company(company_id)
                    else:
                        print("Удаление отменено")
                else:
                    print("Компания не найден")
            except ValueError:
                print("Ошибка: ID должен быть числом")
            
        elif choice == '4':
            confirm = input("Удалить ВСЕ компании? (yes/no): ")
            if confirm.lower() == 'yes':
                confirm2 = input("Это необратимо! Введите 'DELETE ALL': ")
                if confirm2 == 'DELETE ALL':
                    company_crud.delete_all_companies()
                else:
                    print("Удаление отменено")
            else:
                print("Удаление отменено")
                
        elif choice == '5':
            print("\nСтруктура таблицы companies:")
            company_crud.print_table_structure()
                
        elif choice == '6':
            break

def area_management_menu():
    from database.area_crud import AreaCRUD
    
    area_crud = AreaCRUD()
    
    while True:
        print("\n===Меню управление регионами===")
        print("1) Показать все регионы")
        print("2) Найти регион по ID")
        print("3) Удалить регион")
        print("4) Удалить все регионы")
        print("5) Проверить структуру таблицы areas")
        print("6) Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            areas = area_crud.get_all_areas()
            if areas:
                print(f"\nВсего регионов: {len(areas)}")
                print("-" * 60)
                for area in areas:
                    print(f"ID: {area[0]}")
                    print(f"Название: {area[1]}")
                    print(f"Дата добавления: {area[2]}")
                    print("-" * 40)
            else:
                print("Регионы не найдены")
                
        elif choice == '2':
            try:
                area_id = int(input("Введите ID региона: "))
                area = area_crud.get_area_by_id(area_id)
                if area:
                    print(f"\nНайден регион:")
                    print(f"ID: {area[0]}")
                    print(f"Название: {area[1]}")
                    print(f"Дата добавления: {area[2]}")
                    print(f"Дата обновления: {area[3]}")
                else:
                    print("Регион не найден")
            except ValueError:
                print("Ошибка: ID должен быть числом")
                
        elif choice == '3':
            try:
                area_id = int(input("Введите ID региона для удаления: "))
                area = area_crud.get_area_by_id(area_id)
                if area:
                    confirm = input(f"Удалить регион '{area[1]}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        area_crud.delete_area(area_id)
                    else:
                        print("Удаление отменено")
                else:
                    print("Регион не найден")
            except ValueError:
                print("Ошибка: ID должен быть числом")
            
        elif choice == '4':
            confirm = input("Удалить ВСЕ регионы? (yes/no): ")
            if confirm.lower() == 'yes':
                confirm2 = input("Это необратимо! Введите 'DELETE ALL': ")
                if confirm2 == 'DELETE ALL':
                    area_crud.delete_all_areas()
                else:
                    print("Удаление отменено")
            else:
                print("Удаление отменено")
                
        elif choice == '5':
            print("\nСтруктура таблицы areas:")
            area_crud.print_table_structure()
                
        elif choice == '6':
            break

def skill_management_menu_new():
    from database.skill_crud_new import SkillCRUDNew
    
    skill_crud = SkillCRUDNew()
    
    while True:
        print("\n===Меню управление навыками (новая схема)===")
        print("1) Инициализировать предопределенные навыки")
        print("2) Показать все навыки")
        print("3) Добавить новый навык")
        print("4) Найти навык по названию")
        print("5) Найти навык по ID")
        print("6) Удалить навык")
        print("7) Проверить структуру таблицы skills")
        print("8) Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            confirm = input("Инициализировать предопределенные навыки? (yes/no): ")
            if confirm.lower() == 'yes':
                skill_crud.initialize_predefined_skills()
            else:
                print("Отменено")
                
        elif choice == '2':
            skills = skill_crud.get_all_skills()
            if skills:
                print(f"\nВсего навыков: {len(skills)}")
                print("-" * 60)
                for skill in skills:
                    print(f"ID: {skill[0]}")
                    print(f"Название: {skill[1]}")
                    print(f"Дата добавления: {skill[2]}")
                    print("-" * 40)
            else:
                print("Навыки не найдены")
                
        elif choice == '3':
            skill_name = input("Введите название нового навыка: ").strip()
            if skill_name:
                skill_id = skill_crud.add_skill(skill_name)
                if skill_id:
                    print(f"Навык '{skill_name}' добавлен с ID: {skill_id}")
                else:
                    print("Ошибка при добавлении навыка")
            else:
                print("Название навыка не может быть пустым")
                
        elif choice == '4':
            skill_name = input("Введите название навыка для поиска: ").strip()
            if skill_name:
                skill = skill_crud.get_skill_by_name(skill_name)
                if skill:
                    print(f"\nНайден навык:")
                    print(f"ID: {skill[0]}")
                    print(f"Название: {skill[1]}")
                    print(f"Дата добавления: {skill[2]}")
                else:
                    print(f"Навык '{skill_name}' не найден")
            else:
                print("Название навыка не может быть пустым")
                
        elif choice == '5':
            try:
                skill_id = int(input("Введите ID навыка: "))
                skill = skill_crud.get_skill_by_id(skill_id)
                if skill:
                    print(f"\nНайден навык:")
                    print(f"ID: {skill[0]}")
                    print(f"Название: {skill[1]}")
                    print(f"Дата добавления: {skill[2]}")
                else:
                    print(f"Навык с ID {skill_id} не найден")
            except ValueError:
                print("Ошибка: ID должен быть числом")
                
        elif choice == '6':
            try:
                skill_id = int(input("Введите ID навыка для удаления: "))
                skill = skill_crud.get_skill_by_id(skill_id)
                if skill:
                    confirm = input(f"Удалить навык '{skill[1]}'? (yes/no): ")
                    if confirm.lower() == 'yes':
                        skill_crud.delete_skill(skill_id)
                        print(f"Навык удален")
                    else:
                        print("Удаление отменено")
                else:
                    print("Навык не найден")
            except ValueError:
                print("Ошибка: ID должен быть числом")
            
        elif choice == '7':
            print("\nСтруктура таблицы skills:")
            skill_crud.print_table_structure()
                
        elif choice == '8':
            break

def load_full_data_menu():
    from parsers.hh_parser import HHParser
    
    parser = HHParser()
    
    print("\n=== Загрузка полных данных с HH ===")
    print("(Загружает вакансии, компании, регионы и навыки)")
    
    try:
        area = int(input("ID региона (Enter=113 Россия): ") or "113")
        pages = int(input("Страниц для загрузки (1-2): ") or "1")
        per_page = int(input("Вакансий на странице (10-20): ") or "10")
        
        confirm = input(f"\nЗагрузить {pages * per_page} вакансий со всеми данными? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Отменено")
            return
        
        print("\nНачинаю загрузку...")
        
        vacancies = parser.fetch_vacancies(
            per_page=per_page,
            pages=pages,
            area=area,
            search_text="программист"
        )
        
        if not vacancies:
            print("Не удалось загрузить вакансии")
            return
        
        print(f"\nЗагружено {len(vacancies)} вакансий")
        
        from database.vacancy_crud import VacancyCRUD
        from database.company_crud import CompanyCRUD
        from database.area_crud import AreaCRUD
        from database.skill_crud import SkillCRUD
        
        vacancy_crud = VacancyCRUD()
        company_crud = CompanyCRUD()
        area_crud = AreaCRUD()
        skill_crud = SkillCRUD()
        
        print("\nСохранение данных в БД...")
        
        companies_seen = set()
        areas_seen = set()
        all_skills = []
        
        for vacancy in vacancies:
            if vacancy.company_id and vacancy.company_id not in companies_seen:
                from models.company_model import Company
                company = Company(
                    company_hh_id=vacancy.company_id,
                    company_name=vacancy.company_name or "Неизвестная компания"
                )
                company_crud.add_company(company)
                companies_seen.add(vacancy.company_id)
            
            if vacancy.area_id and vacancy.area_id not in areas_seen:
                from models.area_model import Area
                area_obj = Area(
                    area_hh_id=vacancy.area_id,
                    area_name=vacancy.area_name or "Неизвестный регион"
                )
                area_crud.add_area(area_obj)
                areas_seen.add(vacancy.area_id)
        
        vacancy_crud.add_vacancies_batch(vacancies)
        print(f"Сохранено {len(vacancies)} вакансий")
        print(f"Сохранено {len(companies_seen)} компаний")
        print(f"Сохранено {len(areas_seen)} регионов")
        
        load_skills = input("\nЗагрузить навыки для этих вакансий? (yes/no): ")
        if load_skills.lower() == 'yes':
            for vacancy in vacancies:
                skills = parser.extract_skills_from_vacancy(vacancy.vacancy_id)
                all_skills.extend(skills)
            
            if all_skills:
                skill_crud.add_skills_batch(all_skills)
                print(f"Сохранено {len(all_skills)} навыков")
            else:
                print("Навыки не найдены")
        
        print("\n✓ Все данные успешно загружены")
        
    except Exception as e:
        print(f"Ошибка: {e}")

def recommendation_management_menu():
    try:
        from database.recommendation_crud import RecommendationCRUD
        rec_crud = RecommendationCRUD()
    except ImportError:
        print("Модуль рекомендаций не найден")
        print("Создайте файл database/recommendation_crud.py")
        return
    
    while True:
        print("\n===Меню рекомендаций===")
        print("1) Создать рекомендации для всех студентов")
        print("2) Создать рекомендации для конкретного студента")
        print("3) Показать рекомендации студента")
        print("4) Удалить все рекомендации")
        print("5) Вернуться в главное меню")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            try:
                limit = int(input("Сколько рекомендаций на студента (по умолчанию 10): ") or "10")
                rec_crud.recommend_for_all_students(limit)
            except Exception as e:
                print(f"Ошибка: {e}")
                
        elif choice == '2':
            try:
                student_id = int(input("ID студента: "))
                limit = int(input("Сколько рекомендаций (по умолчанию 10): ") or "10")
                recommendations = rec_crud.recommend_for_student(student_id, limit)
                if recommendations:
                    saved = rec_crud.save_recommendations(student_id, recommendations)
                    print(f"Сохранено {saved} рекомендаций")
                else:
                    print("Нет подходящих вакансий для этого студента")
            except ValueError:
                print("Ошибка: ID должен быть числом")
            except Exception as e:
                print(f"Ошибка: {e}")
                
        elif choice == '3':
            try:
                student_id = int(input("ID студента: "))
                recommendations = rec_crud.get_recommendations(student_id)
                if recommendations:
                    print(f"\nРекомендации для студента {student_id}:")
                    print("=" * 80)
                    for rec in recommendations:
                        print(f"ID рекомендации: {rec[0]}")
                        print(f"ID вакансии: {rec[1]}")
                        print(f"Совпадение: {rec[2]:.2%}")
                        print(f"Название: {rec[4]}")
                        if rec[5]:
                            print(f"Компания ID: {rec[5]}")
                        if rec[6]:
                            print(f"Регион ID: {rec[6]}")
                        if rec[7]:
                            print(f"Регион: {rec[7]}")
                        if rec[8]:
                            print(f"Компания: {rec[8]}")
                        print(f"Дата создания: {rec[3]}")
                        print("-" * 40)
                    print(f"Всего рекомендаций: {len(recommendations)}")
                else:
                    print("Нет рекомендаций для этого студента")
            except ValueError:
                print("Ошибка: ID должен быть числом")
            except Exception as e:
                print(f"Ошибка: {e}")
                
        elif choice == '4':
            confirm = input("Удалить ВСЕ рекомендации? (yes/no): ")
            if confirm.lower() == 'yes':
                rec_crud.clear_all_recommendations()
            else:
                print("Отменено")
                
        elif choice == '5':
            break

def check_database_structure():
    from database.user_crud import UserCRUD
    from database.vacancy_crud import VacancyCRUD
    from database.skill_crud import SkillCRUD
    from database.company_crud import CompanyCRUD
    from database.area_crud import AreaCRUD
    from database.skill_crud_new import SkillCRUDNew
    
    user_crud = UserCRUD()
    vacancy_crud = VacancyCRUD()
    skill_crud = SkillCRUD()
    company_crud = CompanyCRUD()
    area_crud = AreaCRUD()
    skill_crud_new = SkillCRUDNew()
    
    print("\n=== Проверка структуры таблиц в БД ===")
    
    print("\n1) Таблица students:")
    user_crud.print_table_structure()
    
    print("\n2) Таблица vacancies:")
    vacancy_crud.print_table_structure()
    
    print("\n3) Таблица vacancy_skills:")
    skill_crud.print_table_structure()
    
    print("\n4) Таблица companies:")
    company_crud.print_table_structure()
    
    print("\n5) Таблица areas:")
    area_crud.print_table_structure()
    
    print("\n6) Таблица skills:")
    skill_crud_new.print_table_structure()
    
    print("\n=== Статистика БД ===")
    try:
        vacancies_count = vacancy_crud.count_vacancies()
        print(f"Вакансий в БД: {vacancies_count}")
    except:
        print("Вакансий в БД: ошибка подсчета")
    
    try:
        skills_count = skill_crud_new.count_skills()
        print(f"Навыков в skills: {skills_count}")
    except:
        print("Навыков в skills: ошибка подсчета")
    
    try:
        vacancy_skills_count = skill_crud.count_skills()
        print(f"Навыков в vacancy_skills: {vacancy_skills_count}")
    except:
        print("Навыков в vacancy_skills: ошибка подсчета")
    
    try:
        companies_count = company_crud.count_companies()
        print(f"Компаний в БД: {companies_count}")
    except:
        print("Компаний в БД: ошибка подсчета")
    
    try:
        areas_count = area_crud.count_areas()
        print(f"Регионов в БД: {areas_count}")
    except:
        print("Регионов в БД: ошибка подсчета")
    
    try:
        users_count = len(user_crud.get_all_users())
        print(f"Студентов в БД: {users_count}")
    except:
        print("Студентов в БД: ошибка подсчета")
    
    print("\nСтруктура БД проверена")

def main():
    initialize_database()
    
    while True:
        print("\n===Главное меню консоли разработчика===")
        print("1) Управление студентами")
        print("2) Управление вакансиями")
        print("3) Управление навыками (вакансии)")
        print("4) Управление компаниями")
        print("5) Управление регионами")
        print("6) Управление навыками (новая схема)")
        print("7) Загрузить полные данные с HH")
        print("8) Рекомендации для студентов")
        print("9) Проверить структуру БД")
        print("10) Инициализировать БД (создать таблицы)")
        print("11) Добавить внешние ключи")
        print("12) Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            user_management_menu()
        elif choice == '2':
            vacancy_management_menu()
        elif choice == '3':
            skill_management_menu()
        elif choice == '4':
            company_management_menu()
        elif choice == '5':
            area_management_menu()
        elif choice == '6':
            skill_management_menu_new()
        elif choice == '7':
            load_full_data_menu()
        elif choice == '8':
            recommendation_management_menu()
        elif choice == '9':
            check_database_structure()
        elif choice == '10':
            from database.init_database import create_tables
            create_tables()
        elif choice == '11':
            from database.init_database import add_foreign_keys
            add_foreign_keys()
        elif choice == '12':
            print("Выход из консоли")
            break
        else:
            print("Неверный выбор")

if __name__ == "__main__":
    main()