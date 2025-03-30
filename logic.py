import sqlite3
from config import DATABASE

skills = [(_,) for _ in ['Python', 'SQL', 'API', 'Telegram']]
statuses = [(_,) for _ in ['На этапе проектирования', 'В процессе разработки', 'Разработан. Готов к использованию.', 'Обновлен', 'Завершен. Не поддерживается']]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.create_tables()
        self.default_insert()

    def create_tables(self):
        with sqlite3.connect(self.database) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id)
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT UNIQUE
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT UNIQUE
                        )''')
            conn.commit()
        print("База данных успешно создана.")

    def __executemany(self, sql, data):
        with sqlite3.connect(self.database) as conn:
            conn.executemany(sql, data)
            conn.commit()

    def __select_data(self, sql, data=tuple()):
        with sqlite3.connect(self.database) as conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    def default_insert(self):
        self.__executemany('INSERT OR IGNORE INTO skills (skill_name) VALUES(?)', skills)
        self.__executemany('INSERT OR IGNORE INTO status (status_name) VALUES(?)', statuses)

    def insert_project(self, data):
        print(f"Data to insert: {data}")
        sql = 'INSERT OR IGNORE INTO projects (user_id, project_name, description, url, status_id) VALUES(?, ?, ?, ?, ?)'
        self.__executemany(sql, [data])

    def insert_skill(self, user_id, project_name, skill):
        project = self.__select_data('SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', (project_name, user_id))
        if not project:
            print(f"Проект '{project_name}' не найден для пользователя {user_id}")
            return
        project_id = project[0][0]

        skill_res = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))
        if not skill_res:
            print(f"Навык '{skill}' не найден")
            return
        skill_id = skill_res[0][0]

        self.__executemany('INSERT OR IGNORE INTO project_skills VALUES (?, ?)', [(project_id, skill_id)])

    def get_statuses(self):
        return self.__select_data('SELECT status_name FROM status')

    def get_status_id(self, status_name):
        res = self.__select_data('SELECT status_id FROM status WHERE status_name = ?', (status_name,))
        return res[0][0] if res else None

    def get_projects(self, user_id):
        return self.__select_data('SELECT * FROM projects WHERE user_id = ?', (user_id,))

    def get_project_id(self, project_name, user_id):
        res = self.__select_data('SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', (project_name, user_id))
        return res[0][0] if res else None

    def get_skills(self):
        return self.__select_data('SELECT * FROM skills')

    def get_project_skills(self, project_name):
        res = self.__select_data('''
        SELECT skill_name FROM projects 
        JOIN project_skills ON projects.project_id = project_skills.project_id 
        JOIN skills ON skills.skill_id = project_skills.skill_id 
        WHERE project_name = ?''', (project_name,))
        return ', '.join(x[0] for x in res)

    def update_projects(self, param, value, project_name, user_id):
        sql = f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?"
        self.__executemany(sql, [(value, project_name, user_id)])

    def delete_project(self, user_id, project_id):
        self.__executemany("DELETE FROM projects WHERE user_id = ? AND project_id = ?", [(user_id, project_id)])

    def delete_skill(self, project_id, skill_id):
        self.__executemany("DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?", [(skill_id, project_id)])

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    #manager.insert_project((1, 'Project 1', 'Описание проекта', 'http://example.com', 1))
    manager.default_insert()
    print(manager.get_statuses())
    
    #projects = manager.get_projects(1)

    #print("Проекты для user_id = 1:", projects)
