#===========================================
# Data to modify
#===========================================

subject_data = {
  "_id": "EDUtrack_Test", # Database name
  "name": "EDUtrack Test", #Subject name
  "start_date": "02/06/2024", # format dd/mm/yyyy
  "course_weeks": "15", # Number of weeks of the course excluding vacation weeks e.g. "15"
  "start_vacations" : "", # format dd/mm/yyyy,  if there aren't vacations = ""
  "end_vacations": "", # format dd/mm/yyyy,  if there aren't vacations = ""
  "max_final_grade": "10", # Highest grade a student can get
  "max_activity_grade": "10", # Highest qualification that an activity can get
  "min_grade_to_pass": "5", # Minimum grade a student must get in order not to fail
  "min_ideal_grade": "8", # A student's ideal grade should be a value between max_final_grade and min_grade_to_pass+1. See the manual for more information on this note.

  "activate_evaluations:": "0", # Don´t modify
  "active_planet_registry": "1", # Don´t modify
  "maintenance": "0", # Don´t modify
  "ignore_categories": set(), # Don´t modify
}

teacher_data = {
  "email": "jeovani@correo.ugr.es", # teacher email
  "name": "Jeovani Morales",
  "telegram_name": "Ayuda EDUtrack",
  "username": "@Ayuda_Edutrack", # Telegram_username
  "telegram_id": "443344899", # To know the teacher's id visit @userinfobot on Telegram from the teacher's account.
  "language": "es", # es for Spanish, en for English

  "is_teacher": 1, # Don´t modify
}

#===================================================
# Don't modify
#===================================================
standby_teachers = False
config_files_set = False
active_activities = False
active_meetings = {}
day_start_week = ""
admins_list = {}
registered_stu = {}
evaluation_scheme = {}
resources = {"week": 0}

teacher_criteria = [
  "T_VOCALIZACION",
  "T_DOMINIO_TEMA",
  "T_CERCANIA",
  "T_ATENCION_AUDIENCIA",
  "T_CLARIDAD_EXPRESIONES",
  "C_CALIDAD_TRANSPARENCIAS",
  "C_CALIDAD_EJEMPLOS",
  "C_CONTENIDOS_NIVEL",
]

activities_headers_file = [
  "_id",
  "name",
  "section",
  "week",
  "weight",
  "visible",
  "category",
]

students_headers_file = ["email", "first_name", "last_name", "username", "planet"]

list_config_files = [
  "students_format.csv",
  "add_students_format.csv",
  "replace_students_format.csv",
  "activities_format.csv",
  "replace_activities_format.csv",
]

tables = {
  "activities": f"""
        _id TEXT NOT NULL PRIMARY KEY,
        name TEXT,
        section TEXT,
        week INTEGER DEFAULT 0,
        weight REAL DEFAULT 0,
        visible INTEGER DEFAULT 0,
        category TEXT
        """,
  "actual_grades": f"""
        email TEXT NOT NULL PRIMARY KEY,
        SUBJECT REAL DEFAULT 0,
        FOREIGN KEY(email) REFERENCES students_file(email)
        """,
  "eva_collaboration": f"""
        _id INTEGER NOT NULL,
        planet TEXT NOT NULL,
        classmate_id INTEGER NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id),
        FOREIGN KEY(planet) REFERENCES planets(_id),
        FOREIGN KEY(classmate_id) REFERENCES telegram_users(_id)
        """,
  "eva_teacher": f"""
        _id INTEGER NOT NULL PRIMARY KEY,
        value TEXT,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "eva_self-evaluation": f"""
        _id INTEGER NOT NULL PRIMARY KEY,
        question INTEGER NOT NULL,
        value INTEGER NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)""",
  "evaluation_scheme": f"""
        _id TEXT NOT NULL PRIMARY KEY,
        category_score REAL NOT NULL DEFAULT 0.0,
        subject_score REAL NOT NULL DEFAULT 0.0,
        active INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(_id) REFERENCES activities(_id)
        """,
  "grades": f"""
        email TEXT NOT NULL PRIMARY KEY,
        _PERFORMANCE_SCORE REAL DEFAULT 0,
        _MAX_ACTUAL_SCORE REAL DEFAULT 0,
        _MAX_POSSIBLE_GRADE REAL DEFAULT 10,
        FOREIGN KEY(email) REFERENCES students_file(email)
        """,
  "linguistic_risk_factor": f"""
        email TEXT NOT NULL PRIMARY KEY,
        FOREIGN KEY(email) REFERENCES students_file(email)
        """,
  "meetings_attendance": f"""
        _id INTEGER NOT NULL,
        meeting INTEGER NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "opn_collaboration": f"""
        _id INTEGER NOT NULL,
        planet TEXT NOT NULL,
        classmate_id INTEGER NOT NULL,
        week INTEGER NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "opn_planet": f"""
        _id INTEGER NOT NULL,
        planet TEXT NOT NULL,
        week INTEGER NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "opn_resources": f"""
        _id TEXT NOT NULL,
        section TEXT,
        resource TEXT NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY(_id) REFERENCES activities(_id)
        """,
  "opn_teacher_meetings": f"""
        _id INTEGER NOT NULL,
        meeting INTEGER NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "opn_teacher_practice": f"""
        _id INTEGER NOT NULL,
        week INTEGER NOT NULL,
        criterion TEXT NOT NULL,
        value TEXT NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "planets": """
        _id TEXT NOT NULL PRIMARY KEY,
        chat_id INTEGER DEFAULT '',
        num_members INTEGER NOT NULL DEFAULT 0,
        active INTEGER NOT NULL DEFAULT 0
        """,
  "planet_admins": """
        _id TEXT NOT NULL PRIMARY KEY,
        admins TEXT,
        FOREIGN KEY(_id) REFERENCES planets(_id)
        """,
  "planet_users": """
        _id INTEGER NOT NULL PRIMARY KEY,
        planet TEXT,
        registered INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id),
        FOREIGN KEY(planet) REFERENCES planets(_id)
        """,
  "registered_students": """
        _id INTEGER NOT NULL PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        username TEXT NOT NULL,
        planet TEXT,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id),
        FOREIGN KEY(email) REFERENCES students_file(email)
        FOREIGN KEY(username) REFERENCES telegram_users(username)
        FOREIGN KEY("planet") REFERENCES "planets"("_id")
        """,
  "report_eva_collaboration": """
        email TEXT NOT NULL PRIMARY KEY,
        evaluation_obtained REAL DEFAULT 0,
        label TEXT DEFAULT '',
        lingustic_term TEXT DEFAULT '',
        grade REAL DEFAULT 0,
        evaluated_peers INTEGER DEFAULT 0,
        FOREIGN KEY(email) REFERENCES students_file(email)
        """,
  "risk_factor": f"""
        email TEXT NOT NULL PRIMARY KEY,
        FOREIGN KEY(email) REFERENCES students_file(email)
        """,
  "students_file": """
        email TEXT NOT NULL PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        planet TEXT,
        FOREIGN KEY(username) REFERENCES telegram_users(username)
        FOREIGN KEY("planet") REFERENCES "planets"("_id")
        """,
  "student_messages": f"""
        _id INTEGER NOT NULL ,
        planet TEXT,
        meeting INTEGER DEFAULT -1,
        TEXT INTEGER DEFAULT 0,
        IMAGE INTEGER DEFAULT 0,
        VIDEO INTEGER DEFAULT 0,
        VOICE INTEGER DEFAULT 0,
        STICKER INTEGER DEFAULT 0,
        GIF INTEGER DEFAULT 0,
        DOCUMENT INTEGER DEFAULT 0,
        LOCATION INTEGER DEFAULT 0,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "suggestions": f"""
        _id TEXT NOT NULL,
        email TEXT NOT NULL,
        date TEXT NOT NULL,
        suggestion TEXT NOT NULL,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        """,
  "subject_data": f"""
        _id TEXT NOT NULL PRIMARY KEY,
        name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        course_weeks INTEGER NOT NULL,
        start_vacations TEXT NOT NULL,
        end_vacations TEXT NOT NULL,
        max_final_grade REAL NOT NULL DEFAULT 10,
        max_activity_grade REAL NOT NULL DEFAULT 10,
        min_grade_to_pass REAL NOT NULL DEFAULT 5,
        min_ideal_grade REAL NOT NULL DEFAULT 10,
        activate_evaluations INTEGER NOT NULL DEFAULT 0,
        active_planet_registry INTEGER NOT NULL DEFAULT 1,
        maintenance INTEGER NOT NULL DEFAULT 0,
        ignore_categories TEXT DEFAULT ''
        """,
  "teachers": """
        email TEXT NOT NULL PRIMARY KEY,
        name TEXT NOT NULL,
        telegram_name TEXT NOT NULL,
        username TEXT NOT NULL,
        telegram_id INTEGER,
        student_view INTEGER NOT NULL DEFULT 0,
        FOREIGN KEY(telegram_id) REFERENCES telegram_users(_id)
        """,
  "teacher_messages": f"""
        _id INTEGER NOT NULL,
        planet TEXT,
        meeting INTEGER DEFAULT -1,
        TEXT INTEGER DEFAULT 0,
        IMAGE INTEGER DEFAULT 0,
        VIDEO INTEGER DEFAULT 0,
        VOICE INTEGER DEFAULT 0,
        STICKER INTEGER DEFAULT 0,
        GIF INTEGER DEFAULT 0,
        DOCUMENT INTEGER DEFAULT 0,
        LOCATION INTEGER DEFAULT 0,
        FOREIGN KEY(_id) REFERENCES telegram_users(_id)
        FOREIGN KEY("planet") REFERENCES "planets"("_id")
        """,
  "telegram_users": """
        _id INTEGER NOT NULL PRIMARY KEY,
        telegram_name TEXT NOT NULL,
        username TEXT NOT NULL,
        is_teacher INTEGER NOT NULL DEFAULT 0,
        language TEXT DEFAULT 'en'
        """,
}


triggers = [
  """
    CREATE TRIGGER IF NOT EXISTS set_user_planet
    AFTER INSERT ON registered_students
    BEGIN
      INSERT OR IGNORE INTO planet_users (_id, planet)
        VALUES ( new._id, new.planet);
      UPDATE planet_users SET registered = 1 WHERE _id = new._id;
      INSERT OR IGNORE INTO planets (_id) VALUES(new.planet);
      UPDATE planets SET num_members = num_members + 1 WHERE _id = new.planet;
      INSERT OR IGNORE INTO student_messages (_id, planet)
        VALUES(new._id, new.planet);
    END;
    """,
  """
    CREATE TRIGGER update_user_planet
      AFTER UPDATE OF planet ON registered_students
      BEGIN
          UPDATE planet_users SET planet = new.planet WHERE _id = new._id;
          INSERT OR IGNORE INTO planets (_id) VALUES(new.planet);
          UPDATE planets SET num_members = num_members + 1 WHERE _id = new.planet;
          UPDATE planets SET num_members = num_members - 1 WHERE _id = old.planet;
      END;
      """,
  """
    CREATE TRIGGER update_is_teacher
      AFTER INSERT ON teachers
      BEGIN
          UPDATE telegram_users SET is_teacher = 1 WHERE _id = new._id;
      END;
  """,
  """
    CREATE TRIGGER insert_planet_admins
      AFTER INSERT ON planets
      BEGIN
          INSERT OR IGNORE INTO planet_admins (_id) VALUES (new._id);
      END;
  """,
]
