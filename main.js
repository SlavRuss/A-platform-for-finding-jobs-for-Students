document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
    loadVladivostokCompanies();
    loadStudents();
    loadVacancies();
    loadStudentsForSelect();
    loadSkills();
    loadAreas();
});

let currentStudentId = null;

function showSection(sectionId) {
    const sections = document.querySelectorAll('.dashboard');
    sections.forEach(section => {
        section.classList.remove('active-section');
    });
    
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active-section');
    }
    
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    if (targetSection) {
        targetSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    switch(sectionId) {
        case 'dashboard':
            loadStatistics();
            loadVladivostokCompanies();
            break;
        case 'students':
            loadStudents();
            loadSkills();
            loadAreas();
            break;
        case 'vacancies':
            loadVacancies();
            loadAreas();
            break;
        case 'recommendations':
            loadStudentsForSelect();
            break;
    }
}

function scrollToDashboard() {
    showSection('dashboard');
}

function toggleAddStudent() {
    const form = document.getElementById('add-student-form');
    const icon = document.getElementById('accordion-icon');
    
    if (form.style.display === 'none') {
        form.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    } else {
        form.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    }
}

async function loadStatistics() {
    console.log('Loading statistics...');
    
    const statsElements = {
        'students-count': document.getElementById('students-count'),
        'vacancies-count': document.getElementById('vacancies-count'),
        'vladivostok-companies': document.getElementById('vladivostok-companies'),
        'recommendations-count': document.getElementById('recommendations-count'),
        'unique-skills': document.getElementById('unique-skills'),
        'vladivostok-vacancies': document.getElementById('vladivostok-vacancies')
    };
    
    const skillsBody = document.getElementById('skills-body');
    
    try {
        skillsBody.innerHTML = `
            <tr>
                <td colspan="3" class="loading">
                    <div class="spinner"></div>
                    <div>Загрузка статистики...</div>
                </td>
            </tr>
        `;
        
        const response = await fetch('/api/statistics');
        const data = await response.json();
        
        console.log('Statistics data received:', data);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (statsElements['students-count']) 
            statsElements['students-count'].textContent = (data.students_count || 0).toLocaleString('ru-RU');
        
        if (statsElements['vacancies-count']) 
            statsElements['vacancies-count'].textContent = (data.vacancies_count || 0).toLocaleString('ru-RU');
        
        if (statsElements['vladivostok-companies']) 
            statsElements['vladivostok-companies'].textContent = (data.vladivostok_companies || 0).toLocaleString('ru-RU');
        
        if (statsElements['recommendations-count']) 
            statsElements['recommendations-count'].textContent = (data.recommendations_count || 0).toLocaleString('ru-RU');
        
        if (statsElements['unique-skills']) 
            statsElements['unique-skills'].textContent = (data.unique_skills || 0).toLocaleString('ru-RU');
        
        if (statsElements['vladivostok-vacancies']) 
            statsElements['vladivostok-vacancies'].textContent = (data.vladivostok_vacancies || 0).toLocaleString('ru-RU');
        
        skillsBody.innerHTML = '';
        
        if (data.top_skills && data.top_skills.length > 0) {
            const totalCount = data.top_skills.reduce((sum, skill) => sum + skill.count, 0);
            
            data.top_skills.forEach(skill => {
                const percentage = totalCount > 0 ? ((skill.count / totalCount) * 100).toFixed(1) : 0;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${skill.skill}</strong></td>
                    <td><span class="badge badge-primary">${skill.count}</span></td>
                    <td>
                        <div style="background: #e3f2fd; border-radius: 4px; height: 8px; margin-top: 5px;">
                            <div style="background: #1a73e8; width: ${percentage}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                        <div style="margin-top: 5px; font-size: 0.9rem; color: #666;">${percentage}%</div>
                    </td>
                `;
                skillsBody.appendChild(row);
            });
        } else {
            skillsBody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 2rem;">Нет данных о навыках</td></tr>';
        }
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
        skillsBody.innerHTML = '<tr><td colspan="3" style="text-align: center; padding: 2rem; color: #d32f2f;">Ошибка загрузки данных</td></tr>';
    }
}

async function loadVladivostokCompanies() {
    const companiesBody = document.getElementById('companies-body');
    
    try {
        companiesBody.innerHTML = `
            <tr>
                <td colspan="5" class="loading">
                    <div class="spinner"></div>
                    <div>Загрузка компаний Владивостока...</div>
                </td>
            </tr>
        `;
        
        const response = await fetch('/api/vladivostok_companies');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        companiesBody.innerHTML = '';
        
        if (data.length > 0) {
            data.forEach(company => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="badge badge-info">${company.id}</span></td>
                    <td><strong>${company.name}</strong></td>
                    <td><span class="badge badge-success">${company.vacancy_count}</span></td>
                    <td>${company.first_vacancy || '—'}</td>
                    <td>${company.last_vacancy || '—'}</td>
                `;
                companiesBody.appendChild(row);
            });
        } else {
            companiesBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem;">Нет данных о компаниях Владивостока</td></tr>';
        }
    } catch (error) {
        console.error('Ошибка загрузки компаний:', error);
        companiesBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: #d32f2f;">Ошибка загрузки данных</td></tr>';
    }
}

async function loadSkills() {
    try {
        const response = await fetch('/api/skills');
        const data = await response.json();
        
        const skillSelects = document.querySelectorAll('.skill-select');
        skillSelects.forEach(select => {
            select.innerHTML = '<option value="">Выберите навык</option>';
            data.forEach(skill => {
                const option = document.createElement('option');
                option.value = skill.id;
                option.textContent = skill.name;
                select.appendChild(option);
            });
        });
        
        return data;
    } catch (error) {
        console.error('Ошибка загрузки навыков:', error);
        return [];
    }
}

async function loadAreas() {
    try {
        const response = await fetch('/api/areas');
        const data = await response.json();
        
        const areaSelects = document.querySelectorAll('.area-select, #student-city');
        areaSelects.forEach(select => {
            if (select.id === 'student-city') {
                select.innerHTML = '';
                const defaultOption = document.createElement('option');
                defaultOption.value = "113";
                defaultOption.textContent = "Россия";
                select.appendChild(defaultOption);
            } else {
                select.innerHTML = '<option value="">Выберите город</option>';
            }
            
            data.sort((a, b) => a.name.localeCompare(b.name)).forEach(area => {
                const option = document.createElement('option');
                option.value = area.id;
                option.textContent = area.name;
                select.appendChild(option);
            });
        });
    } catch (error) {
        console.error('Ошибка загрузки городов:', error);
    }
}

async function loadStudents() {
    const studentsBody = document.getElementById('students-body');
    
    try {
        studentsBody.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    <div class="spinner"></div>
                    <div>Загрузка учеников...</div>
                </td>
            </tr>
        `;
        
        const response = await fetch('/api/students');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        studentsBody.innerHTML = '';
        
        if (data.length > 0) {
            data.forEach(student => {
                const skillsHtml = student.skills && student.skills.length > 0 
                    ? `<div class="skills-list">${student.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}</div>`
                    : '<span style="color: #999;">Нет навыков</span>';
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="badge badge-primary">${student.id}</span></td>
                    <td><strong>${student.full_name}</strong></td>
                    <td>${skillsHtml}</td>
                    <td>${student.city_name}</td>
                    <td><span class="badge ${student.recommendation_count > 0 ? 'badge-success' : 'badge-warning'}">${student.recommendation_count}</span></td>
                    <td>
                        <button class="btn btn-primary" style="padding: 0.3rem 0.8rem; font-size: 0.9rem;" onclick="showRecommendations(${student.id}, '${student.full_name.replace(/'/g, "\\'")}')">
                            <i class="fas fa-eye"></i> Рекомендации
                        </button>
                        <button class="btn btn-danger" style="padding: 0.3rem 0.8rem; font-size: 0.9rem;" onclick="deleteStudent(${student.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                studentsBody.appendChild(row);
            });
        } else {
            studentsBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem;">Нет данных о студентах</td></tr>';
        }
    } catch (error) {
        console.error('Ошибка загрузки студентов:', error);
        studentsBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #d32f2f;">Ошибка загрузки данных</td></tr>';
    }
}

async function loadStudentsForSelect() {
    const studentSelect = document.getElementById('student-select');
    
    try {
        const response = await fetch('/api/students');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        while (studentSelect.options.length > 1) {
            studentSelect.remove(1);
        }
        
        if (data.length > 0) {
            data.forEach(student => {
                const option = document.createElement('option');
                option.value = student.id;
                option.textContent = `${student.id} - ${student.full_name} (${student.recommendation_count} рекомендаций)`;
                studentSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Ошибка загрузки списка студентов:', error);
    }
}

async function addStudent() {
    const studentId = document.getElementById('student-id').value;
    const fullName = document.getElementById('student-name').value;
    const cityId = document.getElementById('student-city').value || 113;
    
    const skillSelects = document.querySelectorAll('#student-skills-container select');
    const skillIds = [];
    skillSelects.forEach(select => {
        if (select.value) {
            skillIds.push(parseInt(select.value));
        }
    });
    
    if (!studentId || !fullName) {
        alert('Заполните ID и ФИО студента');
        return;
    }
    
    try {
        const response = await fetch('/api/students/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                student_id: parseInt(studentId),
                full_name: fullName,
                skill_ids: skillIds,
                city_id: parseInt(cityId)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Студент добавлен');
            document.getElementById('student-id').value = '';
            document.getElementById('student-name').value = '';
            document.getElementById('student-skills-container').innerHTML = `
                <select class="skill-select" style="padding: 0.5rem; border: 2px solid #ddd; border-radius: 4px; width: 100%;">
                    <option value="">Выберите навык</option>
                </select>
            `;
            loadSkills();
            loadStudents();
            loadStudentsForSelect();
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Ошибка добавления студента:', error);
        alert('Ошибка при добавлении студента');
    }
}

function addSkillField() {
    const container = document.getElementById('student-skills-container');
    const newSelect = document.createElement('select');
    newSelect.className = 'skill-select';
    newSelect.style = 'padding: 0.5rem; border: 2px solid #ddd; border-radius: 4px; width: 100%; margin-top: 0.5rem;';
    newSelect.innerHTML = '<option value="">Выберите навык</option>';
    
    const skills = document.querySelectorAll('.skill-select option');
    const skillOptions = new Map();
    skills.forEach(option => {
        if (option.value) {
            skillOptions.set(option.value, option.textContent);
        }
    });
    
    skillOptions.forEach((name, id) => {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = name;
        newSelect.appendChild(option);
    });
    
    container.appendChild(newSelect);
}

async function deleteStudent(studentId) {
    if (!confirm('Удалить студента?')) return;
    
    try {
        const response = await fetch(`/api/students/${studentId}/delete`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Студент удален');
            loadStudents();
            loadStudentsForSelect();
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Ошибка удаления студента:', error);
        alert('Ошибка при удалении студента');
    }
}

async function loadVacancies(areaId = null) {
    const vacanciesBody = document.getElementById('vacancies-body');
    
    try {
        vacanciesBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    <div class="spinner"></div>
                    <div>Загрузка вакансий...</div>
                </td>
            </tr>
        `;
        
        let url = '/api/vacancies?limit=50';
        if (areaId) {
            url += `&area_id=${areaId}`;
            const areaSelect = document.getElementById('vacancy-area-select');
            if (areaSelect) areaSelect.value = areaId;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        vacanciesBody.innerHTML = '';
        
        if (data.length > 0) {
            data.forEach(vacancy => {
                const displaySkills = vacancy.skills && vacancy.skills.length > 0 
                    ? vacancy.skills.slice(0, 3)
                    : [];
                const hiddenSkills = vacancy.skills && vacancy.skills.length > 3
                    ? vacancy.skills.slice(3)
                    : [];
                
                const skillsHtml = `
                    <div class="skills-container" data-vacancy="${vacancy.id}">
                        <div class="skills-list visible-skills">
                            ${displaySkills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                        </div>
                        ${hiddenSkills.length > 0 ? `
                            <div class="skills-list hidden-skills" id="skills-${vacancy.id}" style="display: none; margin-top: 0.5rem;">
                                ${hiddenSkills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                            </div>
                            <button class="btn-show-skills" onclick="toggleSkills('${vacancy.id}', ${hiddenSkills.length})">
                                <i class="fas fa-plus-circle"></i> +${hiddenSkills.length}
                            </button>
                        ` : ''}
                    </div>
                `;
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="badge badge-info">${vacancy.id}</span></td>
                    <td><strong>${vacancy.title}</strong></td>
                    <td>${vacancy.company}</td>
                    <td>${vacancy.area}</td>
                    <td>${vacancy.salary ? `<span style="color: #2e7d32; font-weight: 600;">${vacancy.salary}</span>` : '—'}</td>
                    <td>${vacancy.publication_date || '—'}</td>
                    <td>${skillsHtml}</td>
                `;
                vacanciesBody.appendChild(row);
            });
        } else {
            vacanciesBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">Нет данных о вакансиях</td></tr>';
        }
    } catch (error) {
        console.error('Ошибка загрузки вакансий:', error);
        vacanciesBody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: #d32f2f;">Ошибка загрузки данных</td></tr>';
    }
}

function toggleSkills(vacancyId, totalHidden) {
    const hiddenSkillsDiv = document.getElementById(`skills-${vacancyId}`);
    const button = event.currentTarget;
    
    if (hiddenSkillsDiv.style.display === 'none') {
        hiddenSkillsDiv.style.display = 'flex';
        hiddenSkillsDiv.style.flexWrap = 'wrap';
        hiddenSkillsDiv.style.gap = '0.5rem';
        button.innerHTML = '<i class="fas fa-minus-circle"></i> скрыть';
    } else {
        hiddenSkillsDiv.style.display = 'none';
        button.innerHTML = `<i class="fas fa-plus-circle"></i> +${totalHidden}`;
    }
}

async function loadVacanciesByCity(areaId) {
    await loadVacancies(areaId);
}

async function loadAndRefreshVacancies() {
    const areaSelect = document.getElementById('vacancy-area-select');
    const areaId = areaSelect.value;
    
    if (!areaId) {
        alert('Выберите город для обновления');
        return;
    }
    
    const cityName = areaSelect.options[areaSelect.selectedIndex].text;
    
    if (!confirm(`Удалить все вакансии из города ${cityName} и загрузить новые?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/vacancies/refresh', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({area_id: parseInt(areaId)})
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            loadVacancies(parseInt(areaId));
            loadStatistics();
            loadVladivostokCompanies();
        } else {
            alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
        }
    } catch (error) {
        console.error('Ошибка обновления вакансий:', error);
        alert('Ошибка при загрузке вакансий');
    }
}

function onStudentSelectChange() {
    const studentId = document.getElementById('student-select').value;
    currentStudentId = studentId;
    
    if (studentId) {
        loadStudentRecommendations(studentId);
    } else {
        document.getElementById('recommendations-content').innerHTML = `
            <div class="info-box">
                <div class="info-icon">
                    <i class="fas fa-info-circle"></i>
                </div>
                <div class="info-text">
                    <h3>Система рекомендаций</h3>
                    <p>Выберите студента для просмотра рекомендаций или создайте новые.</p>
                </div>
            </div>
        `;
    }
}

async function generateRecommendationsForSelected() {
    const studentId = document.getElementById('student-select').value;
    const limit = document.getElementById('recommendation-limit').value;
    
    if (!studentId) {
        alert('Выберите студента');
        return;
    }
    
    try {
        const response = await fetch(`/api/student/${studentId}/recommendations/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({limit: parseInt(limit)})
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Создано ${data.count} рекомендаций`);
            loadStudentRecommendations(studentId);
            loadStudents();
            loadStudentsForSelect();
        } else {
            alert(data.message || 'Ошибка при создании рекомендаций');
        }
    } catch (error) {
        console.error('Ошибка создания рекомендаций:', error);
        alert('Ошибка при создании рекомендаций');
    }
}

async function generateRecommendations(studentId) {
    const limit = document.getElementById('recommendation-limit').value;
    
    try {
        const response = await fetch(`/api/student/${studentId}/recommendations/generate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({limit: parseInt(limit)})
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Создано ${data.count} рекомендаций`);
            loadStudentRecommendations(studentId);
            loadStudents();
            loadStudentsForSelect();
        } else {
            alert(data.message || 'Ошибка при создании рекомендаций');
        }
    } catch (error) {
        console.error('Ошибка создания рекомендаций:', error);
        alert('Ошибка при создании рекомендаций');
    }
}

async function loadStudentRecommendations(studentId) {
    const recommendationsContent = document.getElementById('recommendations-content');
    
    if (!studentId) {
        recommendationsContent.innerHTML = `
            <div class="info-box">
                <div class="info-icon">
                    <i class="fas fa-info-circle"></i>
                </div>
                <div class="info-text">
                    <h3>Система рекомендаций</h3>
                    <p>Выберите студента для просмотра рекомендаций или создайте новые.</p>
                </div>
            </div>
        `;
        return;
    }
    
    try {
        recommendationsContent.innerHTML = `
            <div class="loading" style="padding: 2rem; text-align: center;">
                <div class="spinner"></div>
                <div>Загрузка рекомендаций...</div>
            </div>
        `;
        
        const response = await fetch(`/api/student/${studentId}/recommendations`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const studentName = document.getElementById('student-select').options[
            document.getElementById('student-select').selectedIndex
        ]?.text.split(' - ')[1] || studentId;
        
        if (data.length > 0) {
            let html = `<h3 style="margin-bottom: 1.5rem; color: #1a73e8;">Рекомендации для студента ${studentId} (${studentName})</h3>`;
            
            data.forEach(rec => {
                const matchPercentage = (rec.match_score * 100).toFixed(1);
                let matchClass = 'low';
                if (rec.match_score > 0.6) matchClass = 'high';
                else if (rec.match_score > 0.3) matchClass = 'medium';
                
                const skillsHtml = rec.skills && rec.skills.length > 0 
                    ? `<div class="skills-list">${rec.skills.slice(0, 5).map(skill => `<span class="skill-tag">${skill}</span>`).join('')}${rec.skills.length > 5 ? `<span class="skill-tag">+${rec.skills.length - 5}</span>` : ''}</div>`
                    : '<span style="color: #999;">Нет данных о навыках</span>';
                
                html += `
                    <div class="recommendation-card">
                        <div class="recommendation-header">
                            <div>
                                <div class="recommendation-title">${rec.title}</div>
                                <div class="recommendation-meta">
                                    <span><i class="fas fa-building"></i> ${rec.company_name || 'Не указано'}</span>
                                    <span><i class="fas fa-map-marker-alt"></i> ${rec.area_name || 'Не указано'}</span>
                                    <span><i class="fas fa-calendar"></i> ${rec.created_at || '—'}</span>
                                </div>
                            </div>
                            <div class="match-score ${matchClass}">${matchPercentage}%</div>
                        </div>
                        <div class="recommendation-skills">
                            <strong>Требуемые навыки:</strong>
                            ${skillsHtml}
                        </div>
                    </div>
                `;
            });
            
            recommendationsContent.innerHTML = html + `
                <button class="btn btn-primary" onclick="generateRecommendations(${studentId})" style="margin-top: 1rem;">
                    <i class="fas fa-sync-alt"></i> Обновить рекомендации
                </button>
            `;
        } else {
            recommendationsContent.innerHTML = `
                <div class="info-box">
                    <div class="info-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="info-text">
                        <h3>Нет рекомендаций</h3>
                        <p>Для студента ${studentName} не найдено подходящих рекомендаций.</p>
                        <button class="btn btn-primary" onclick="generateRecommendations(${studentId})">
                            <i class="fas fa-sync-alt"></i> Создать рекомендации
                        </button>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Ошибка загрузки рекомендаций:', error);
        recommendationsContent.innerHTML = `
            <div class="info-box" style="border-left-color: #d32f2f;">
                <div class="info-icon" style="color: #d32f2f;">
                    <i class="fas fa-exclamation-circle"></i>
                </div>
                <div class="info-text">
                    <h3 style="color: #d32f2f;">Ошибка загрузки</h3>
                    <p>${error.message}</p>
                </div>
            </div>
        `;
    }
}

function showRecommendations(studentId, studentName) {
    showSection('recommendations');
    const studentSelect = document.getElementById('student-select');
    if (studentSelect) {
        studentSelect.value = studentId;
        loadStudentRecommendations(studentId);
    }
}