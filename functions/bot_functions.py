import inspect
import os
import threading
from collections import Counter
from functools import wraps
from urllib.request import urlopen

import config.config_file as cfg
import config.db_sqlite_connection as sqlite
import numpy as np
import pandas as pd
from telegram import ChatAction
from telegram import InlineKeyboardMarkup as IKMarkup
from text_language import bot_lang as b_lang
from text_language import general_lang as g_lang
from text_language import student_lang as s_lang
from text_language import teacher_lang as t_lang

from functions import commands as cmd
from functions import general_functions as g_fun


# Function Decorator
def send_action(action):
  """Decorator that sends 'action' while processing command_func. Displays an indication that the bot is performing an action such as bot is typing

    Args:
        action (str): String with the action displayed by the bot.
    """

  def decorator(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
      context.bot.send_chat_action(
        chat_id=update.effective_message.chat_id, action=action
      )
      return func(update, context, *args, **kwargs)

    return command_func

  return decorator


def user_send_message(update, context):
  """Receives a message from the user that is not a command. Identifies whether the user is a student or a teacher and redirects to the corresponding function.

    Args:
        update (:class:'telegram-Update'): Current request received by the bot
        context (:class:'telegram.ext-CallbackContext'): Context of the current request
    """
  try:
    if update.message:
      chat_id = update.message.chat_id
      planet = g_fun.strip_accents(update.message.chat.title) if chat_id < 0 else ""
      user_data = update._effective_user
      user = g_fun.get_user_data(user_data, planet)
      # get_user_data returns False if the user does not have the username set up
      if user:
        user.user_send_message(update, context)
      else:
        text = b_lang.no_username(user_data.language_code)
        update.message.reply_text(text)
        return False
    else:
      print("ENTRO SIN MENSAJE")
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


# Functions for configuring the course
@send_action(ChatAction.TYPING)
def config_files_set(update, context, user):
  """Sends the teacher the configuration files of the students and the activities, to configure the subject.

    Args:
        context (:class:'telegram.ext-CallbackContext'): Context of the current request.
        user (:class:'user_types.Teacher'): General teacher information.
    """
  try:
    not_set = []
    sql_stu = f"SELECT count(*) FROM students_file"
    if not sqlite.execute_sql(sql_stu, "fetchone")[0]:
      not_set.append("students")

    sql_act = f"SELECT count(*) FROM activities"
    if not sqlite.execute_sql(sql_act, "fetchone")[0]:
      not_set.append("activities")

    if len(not_set) == 2:
      text = t_lang.config_files(user.language, "download", context=context)
      g_fun.send_Msg(context, user, text=text)
      config_files_send_document(context, user, "students")
      config_files_send_document(context, user, "activities")
    else:
      text = t_lang.config_files(user.language, "missing_file", not_set[0])
      g_fun.send_Msg(context, user, text=text)
      config_files_send_document(context, user, not_set[0])
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)


def config_files_send_document(context, user, elements):
  """Sends the 'user' the requested document in 'elements'.

    Args:
        context (:class:'telegram.ext-CallbackContext'): Context of the current request.
        user (:class:'user_types.Teacher'): General teacher information.
        elements (str): Indicator of the document that will be sent to the user 'students' or 'activities'.
    """
  try:
    context.bot.sendDocument(
      chat_id=user._id,
      document=open(b_lang.config_files_send_document(user.language, elements), "rb"),
    )
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)


@send_action(ChatAction.UPLOAD_DOCUMENT)
def config_files_upload(update, context, user):
  """EDUtrack receives a configuration document:
    students_format, add_stundents_format, replace_students_format, activities_format or replace_activities_format. To upload it to the DB.

    Args:
      update (:class:'telegram-Update'): Current request received by the bot.
      context (:class:'telegram.ext-CallbackContext'): Context of the current request.
      user (:class:'user_types.Teacher'): General teacher information.

    Returns:
      bool: Return True if the set up process was completed correctly and False otherwise.
    """

  def check_students_file(df_file):
    """Prepara los datos que se insertaran en la tabla students_file y revisa que los nombres de columnas sean correctos.

        Args:
            df_file (:class:'pandas-DataFrame'): DataFrame with the student records that will be uploaded to the DB.
        Returns:
            bool: Returns True if the check is correct otherwise returns False.
        """
    try:
      df_file = data_preparation(df_file, "students")
      # Elimina los archivos generados al solicitar el reporte de estudiantes.
      g_fun.remove_file("files/download/students_full.csv")
      g_fun.remove_file("files/downlad/students.csv")

      if not set(cfg.students_headers_file).issubset(file_headers):
        headers = ("\n").join(cfg.students_headers_file)
        text = t_lang.config_files(user.language, "header_error", elements=headers)
        g_fun.send_Msg(context, user, text=text)
        config_files_send_document(context, user, "students")
        return False
      return True
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)

  def check_activities_file(df_file):
    """Check that the activities_format file meets the necessary requirements before it is uploaded to the DB.

        Args:
          df_file (:class:'pandas-DataFrame'): DataFrame with the activity records that will be uploaded to the DB.
          elements (str): elements (str): Indicator that you are working with activities.
        """

    def are_categories_defined(root_category):
      """Check if all categories are defined in the "activities_format.csv" file.

      Args:
          root_category (dict): Dictionary with the categories that do not have a parent category.

      Returns:
          bool: Returns True if the only parent category is 'SUBJECT'. False if not.
      """
      try:
        # Check if all categories are defined
        if root_category != {"SUBJECT"}:
          if "SUBJECT" not in root_category:
            text = t_lang.config_files_activities(user.language, "no_main_category")
            g_fun.send_Msg(context, user, text=text)
          else:
            root_category.remove("SUBJECT")

          undefined_categories = "\n".join(root_category)
          if undefined_categories:
            text = t_lang.config_files_activities(
              user.language, "undefined_category", elements=undefined_categories
            )
            g_fun.send_Msg(context, user, text=text)
          return False
        return True
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    def categories_have_parent(category_data):
      """Check if all categories have parent category in the "activities_format.csv" file.

      Args:
        category_data (pandas-DataFrame): DataFrame containing the information of the file "activities.format.csv"

      Returns:
        bool: Return True if all categories have parent category. False if not.
      """
      try:
        no_parent_cat = list(category_data.loc[category_data["category"] == ""]["_id"])
        if no_parent_cat:
          no_parent_cat = "\n".join(no_parent_cat)
          text = t_lang.config_files_activities(
            user.language, "no_parent_cat", elements=no_parent_cat
          )
          g_fun.send_Msg(context, user, text=text)
          return False
        return True
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    def categories_have_weight(category_data):
      """Check if the categories defined in the "activities_format.csv" file have weight.

      Args:
        category_data (pandas-DataFrame): DataFrame containing the information of the file "activities.format.csv"

      Returns:
        bool: Return True if all categories have weight. False if not.
      """
      try:
        weightless_cat = category_data[category_data["_id"] == ""]
        weightless_cat = list(weightless_cat["_id"])
        if weightless_cat:
          weightless_cat = "\n".join(weightless_cat)
          text = t_lang.config_files_activities(
            user.language, "weightless", elements=weightless_cat
          )
          g_fun.send_Msg(context, user, text=text)
          return False
        return True
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    try:
      df_file = data_preparation(df_file, "activities")
      # Elimina los archivos generados al solicitar el reporte de actividades.
      g_fun.remove_file("files/download/all_activities.csv")
      g_fun.remove_file("files/download/qualifying_activities.csv")
      # Revisa los encabezados del archivo

      if not set(cfg.activities_headers_file).issubset(file_headers):
        headers = ("\n").join(cfg.students_headers_file)
        text = t_lang.config_files(user.language, "header_error", elements=headers)
        g_fun.send_Msg(context, user, text=text)
        config_files_send_document(context, user, "activities")
        return False

      # Get the categories file
      file_error = False
      categories = set(filter(None, df_file["category"].unique()))
      root_category = categories - set(df_file["_id"].dropna())
      category_data = df_file.loc[df_file["_id"].isin(categories)]

      if not are_categories_defined(root_category):
        file_error = True

      if not categories_have_parent(category_data):
        file_error = True

      if not categories_have_weight(category_data):
        file_error = True

      if file_error:
        return False
      return True
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)

  def separate_elements(df_file):
    try:
      data_DB = sqlite.table_DB_to_df("students_file")

      all_elements = g_fun.dataframes_comparison(data_DB, df_file).drop(
        ["_merge"], axis=1
      )
      duplicate_elements = list(set(df_file["email"]) & (set(data_DB["email"])))

      new_elements = g_fun.dataframes_comparison(
        data_DB, df_file, which="right_only"
      ).drop(["_merge"], axis=1)

      for element in duplicate_elements:
        new_elements.drop(
          new_elements[new_elements["email"] == element].index, inplace=True
        )

      return (all_elements, duplicate_elements, new_elements)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return Exception

  def create_grades_table(students, add_elements=False):
    """Creates the table 'element_liste database from the file of students and activities uploaded by the teacher.

        Args:
            update (:class:'telegram-Update'): Current request received by the bot.
            context (:class:'telegram.ext-CallbackContext'): Context of the current request.
            students (list): List of students to be saved in the 'grades' table
            add_elements (bool, optional): Indicates if new elements will be added or if the table will be created. Defaults to False.

        Returns:
            bool: Returns True if the process is correct otherwise returns False
        """
    try:
      sql = "SELECT DISTINCT _id FROM activities WHERE weight > 0"
      activities = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
      sql = "SELECT DISTINCT category FROM activities WHERE category <> ''"
      categories = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
      categories.remove("SUBJECT")
      if "SUBJECT" not in activities:
        activities.insert(0, "SUBJECT")
      if not add_elements:
        tables = ["grades", "actual_grades"]
        for table in tables:
          sql = f"DROP TABLE IF EXISTS {table}"
          sqlite.execute_sql(sql)
          sql = f"CREATE TABLE IF NOT EXISTS {table} ({cfg.tables[table]})"
          sqlite.execute_sql(sql)

        for activity in activities:
          sql = f"""ALTER TABLE grades
                  ADD COLUMN '{activity}' REAL DEFAULT 0.0"""
          sqlite.execute_sql(sql)

        for category in sorted(categories):
          sql = f"""ALTER TABLE actual_grades
          ADD COLUMN '{category}' REAL DEFAULT 0.0"""
          sqlite.execute_sql(sql)

      grades_table = sqlite.table_DB_to_df("grades")
      df_students = pd.DataFrame(students, columns=["email"])
      df_grades = pd.concat([grades_table, df_students])
      df_grades.replace({np.nan: 0.0}, inplace=True)
      df_grades = df_grades.sort_values(by=["email"])
      sqlite.save_elements_in_DB(df_grades, "grades")

      # df_scores = sqlite.table_DB_to_df("actual_grades")
      df_categories = pd.concat(
        [df_grades[["email", "SUBJECT"]], df_grades[categories]], axis=1
      )
      sqlite.save_elements_in_DB(df_categories, "actual_grades")
      return True
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  def create_arf_tables(students, add_students=False):
    try:
      students = pd.DataFrame(students, columns=["email"])
      if add_students:
        risk_factor_students = sqlite.table_DB_to_df("risk_factor")
        linguistic_students = sqlite.table_DB_to_df("linguistic_risk_factor")

        all_students = pd.concat([risk_factor_students, students])
        all_students.replace({np.nan: 0.0}, inplace=True)
        all_students = all_students.sort_values(by=["email"])
        sqlite.save_elements_in_DB(all_students, "risk_factor")

        all_students = pd.concat([linguistic_students, students])
        all_students.replace({np.nan: ""}, inplace=True)
        all_students = all_students.sort_values(by=["email"])
        sqlite.save_elements_in_DB(all_students, "linguistic_risk_factor")

      else:
        sqlite.execute_sql("DELETE FROM risk_factor")
        sqlite.execute_sql("DELETE FROM linguistic_risk_factor")

        columns = sqlite.get_columns_names("risk_factor")
        """ sql = f"PRAGMA table_info(risk_factor)"
        table_columns = sqlite.execute_sql(sql, "fetchall")
        columns = [col[1] for col in table_columns]
        """
        course_weeks = cfg.subject_data["course_weeks"]
        for num_week in range(1, int(course_weeks) + 1):
          text_week = "week_" if num_week >= 10 else "week_0"
          text_week += str(num_week)
          students[text_week] = 0.0
          if text_week not in columns:
            sql = f"ALTER TABLE risk_factor ADD COLUMN {text_week} REAL DEFAULT 0.0"
            sqlite.execute_sql(sql)
            sql = f"""ALTER TABLE linguistic_risk_factor
                  ADD COLUMN {text_week} TEXT DEFAULT '' """
            sqlite.execute_sql(sql)

        sqlite.save_elements_in_DB(students, "risk_factor")
        students = students.replace([0.0], "")
        sqlite.save_elements_in_DB(students, "linguistic_risk_factor")
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  def check_new_students(new_students):
    try:
      for student in new_students["email"]:
        stu_data = new_students.loc[new_students["email"] == student]
        username = stu_data["username"].item()
        if username:
          sql = f"SELECT _id FROM registered_students WHERE username = '{username}'"
          student_id = sqlite.execute_sql(sql, fetch="fetchone")
          if student_id:
            student_id = student_id[0]
            # Complete the student's information at registered_students
            first_name = stu_data["first_name"].item()
            last_name = stu_data["last_name"].item()
            full_name = f"{last_name}, {first_name}"
            email = stu_data["email"].item()
            sql = f"""UPDATE registered_students
                      SET full_name = '{full_name}', email = '{email}'
                      WHERE username = '{username}'"""
            sqlite.execute_sql(sql)

            # Check if the student has participated in meetings
            sql = f"""SELECT meeting FROM meetings_attendance
                    WHERE _id = {student_id}"""
            stu_meetings = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
            for meeting in stu_meetings:
              sql = f"UPDATE grades SET ML_MEETING_{meeting}=10 WHERE email = '{email}'"
              sqlite.execute_sql(sql)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  def calculate_grades_new_students(students):
    try:
      sql = f'SELECT category_score FROM evaluation_scheme WHERE _id="SUBJECT"'
      max_actual_score = sqlite.execute_sql(sql, fetch="fetchone")[0]
      if max_actual_score:
        sql = f"""UPDATE grades SET _MAX_ACTUAL_SCORE = {max_actual_score}
                  WHERE _MAX_ACTUAL_SCORE = 0"""
        sqlite.execute_sql(sql, fetch="fetchall")
        df_students = pd.DataFrame(columns=["email", "SUBJECT"])
        df_students["email"] = students
        df_students.replace({np.nan: 0.0}, inplace=True)
        thread_grades = threading.Thread(
          target=thread_grade_activities, args=(context, df_students, user)
        )
        thread_grades.start()
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  try:
    doc = update.message.document
    add_elements = True if "add" in doc.file_name else False

    # Get File from Telegram
    input_file = context.bot.get_file(doc.file_id)
    f_path = input_file["file_path"]  # Get the download path
    f_save_name = f"files/config/{doc.file_name}"  # Path where the file will be saved
    temp = urlopen(f_path)
    df_file = pd.read_csv(urlopen(f_path), encoding="UTF-8-sig")

    file_headers = temp.readline().decode("UTF-8-sig")
    file_headers = file_headers.replace("\n", "")
    file_headers = file_headers.replace("\r", "")
    file_headers = set(file_headers.split(","))

    # Check that the files and column names are correct
    if "students" in doc.file_name:
      table_name = "students_file"
      elements = "students"
      if not check_students_file(df_file):
        return False
    elif "activities" in doc.file_name:
      table_name = elements = "activities"
      if not check_activities_file(df_file):
        return False

    if not os.path.exists("files/config"):
      os.makedirs("files/config")

    if add_elements:
      all_elements, duplicate_elements, new_elements = separate_elements(df_file)
      if new_elements.empty:
        text = t_lang.config_files(user.language, "add_all_exists")
        g_fun.send_Msg(context, user, text=text)
        return False

      upload_data = sqlite.save_file_in_DB(new_elements, table_name, action="append")
      all_elements.to_csv(f_save_name, index=False)

    else:
      upload_data = sqlite.save_elements_in_DB(df_file, table_name)
      df_file.to_csv(f_save_name, index=False)
      if elements == "activities" and upload_data:
        create_evaluation_scheme(df_file[["_id", "weight", "category"]].copy())
        cfg.active_activities = False

    if upload_data:
      if g_fun.are_config_files_set():
        cfg.config_files_set = True
        if add_elements:
          students = list(new_elements["email"])
          if create_grades_table(students, add_elements=True):
            create_arf_tables(students, add_elements)
            check_new_students(new_elements)
            calculate_grades_new_students(students)
            if duplicate_elements:
              elements = "\n".join(duplicate_elements)
              text = t_lang.config_files(
                user.language, "add_duplicates", elements=elements
              )
              text += t_lang.config_files(user.language, "add_no_duplicates")
              g_fun.send_Msg(context, user, text=text)
            else:
              text = t_lang.config_files(user.language, "add_ready", elements=elements)
              g_fun.send_Msg(context, user, text=text)

        else:
          sql = f"SELECT DISTINCT email FROM  students_file"
          students = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
          if create_grades_table(students):
            create_arf_tables(students)
            text = t_lang.welcome_text(user.language, context, "long")
            g_fun.send_Msg(context, user, text=text)
            # sql = "SELECT COUNT (*) FROM evaluation_scheme "
          else:
            text = g_lang.config_files(
              user.language, "error_upload_file", doc.file_name
            )
            g_fun.send_Msg(context, user, text=text)
            config_files_set(context, user)
            return False
      else:
        if "students" in doc.file_name:
          missing_file = "activities_format.csv"
        else:
          missing_file = "students_format.csv"

        text = t_lang.config_files(user.language, "ready_one", missing_file)
        g_fun.send_Msg(context, user, text=text)
    else:
      text = g_lang.error_upload_file(user.language, doc.file_name)
      g_fun.send_Msg(context, user, text=text)
      return False
  except:
    g_fun.print_except(inspect.stack()[0][3])
    file = update.message.document.file_name
    text = g_lang.error_upload_file(user.language, file)
    g_fun.send_Msg(context, user, text=text)


def data_preparation(data, elements):
  """Clean and prepare the dataframe 'data' to be uploaded to the database.

    Args:
        data (:class:'pandas.DataFrame'): Records of the file to be uploaded to the DB.
        elements (str): Indicator of the type of document you want to upload, 'students' or 'activities'.
    Returns:
        [pandas-DataFrame]: DataFrame clean.
    """
  try:
    ID = data.columns[0]
    data.columns = data.columns.str.replace(" ", "_")
    data.columns = data.columns.str.replace("-", "_")
    data.dropna(subset=[ID], inplace=True)

    if elements == "activities":
      data.columns = map(str.lower, data.columns)
      data.replace({"true": 1, "false": 0}, inplace=True)
      data["week"].fillna(0, inplace=True)
      data["visible"].fillna(0, inplace=True)
      data["weight"].fillna(0.0, inplace=True)
      # data["active"] = 0
      data.fillna("", inplace=True)
      for col in ["_id", "section", "category"]:
        data[col] = data[col].str.upper()

    elif elements == "students":
      data.columns = map(str.lower, data.columns)
      data.fillna("", inplace=True)
      for col in data.columns:
        if col != ID:
          data[col] = data[col].str.upper()
        else:
          data[col] = data[col].str.lower()

      data = data.sort_values(ID)
      # VER SI HACE FALTA PARA ALGO
      # data["name"] = data[ID].str.lower()
    elif elements == "grades":
      data.columns = map(str.upper, data.columns)
      data.rename(columns={data.columns[0]: data.columns[0].lower()}, inplace=True)
      data.fillna(0, inplace=True)
      data.replace({"-": 0}, inplace=True)
      grades_cols = list(data.columns[1:])
      data[grades_cols] = data[grades_cols].astype(float)
    return data
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def options_menu(update, context):
  """It identifies the option selected by the user in the menu and directs the flow to the corresponding function.

  Args:
    update (:class:'telegram-Update'): Current request received by the bot.
    context (:class:'telegram.ext-CallbackContext'): Context of the current request.

  Returns:
      bool:
  """
  try:
    query = update.callback_query
    selections = (query.data).split("-")
    print("SELECTIONS", selections)
    choice = selections[-1]
    user = g_fun.get_user_data(update._effective_user)
    if user:
      if len(selections) > 1:
        # STUDENT MENU
        if selections[0] == "s_menu":
          if selections[1] == "back":
            text, options = s_lang.main_menu(user.language)
            show_menu(query, text, options)
          elif selections[1] == "grade":
            user.my_grade(context, query)
          elif selections[1] == "opn":
            if len(selections) == 2:
              text, options = s_lang.menu_opinion(user.language)
              show_menu(query, text, options)
              ## The use of short identifiers such as 'tp' is because telegram callback_data only accepts 64 characters and the user id and the selected rating are saved in later options.
            elif selections[2] == "tp":
              if len(selections) == 3:
                text, options = s_lang.menu_opn_tea_practice(user.language)
                show_menu(query, text, options)
              elif selections[3] == "meet":
                user.opn_tea_meetings(context, query, selections)
              else:
                user.opn_tea_practice(context, query, selections)
            elif selections[2] == "coll":
              user.opn_collaboration(context, query, selections)
            elif selections[2] == "rsrcs":
              user.opn_rsrcs(context, query, selections)
            elif selections[2] == "planet":
              user.opn_planet(context, query, selections)
          elif selections[1] == "eva":
            if cfg.subject_data["activate_evaluations"]:
              if len(selections) == 2:
                text, options = s_lang.menu_evaluate(user.language)
                show_menu(query, text, options)
              elif selections[2] == "auto":
                user.eva_autoevaluation(context, query, selections)
              elif selections[2] == "coll":
                user.eva_collaboration(context, query, selections)
              elif selections[2] == "teacher":
                user.eva_teacher(context, query, selections)
            else:
              text = s_lang.evaluate(user.language, "not_available")
              query.edit_message_text(parse_mode="HTML", text=text)
          elif choice == "change_language":
            cmd.change_language(update, context)
          elif choice == "suggestion":
            text = s_lang.suggestion(user.language, "text")
            query.edit_message_text(parse_mode="HTML", text=text)
          elif choice == "change_profile":
            cmd.change_profile(update, context)
        # TEACHER MENU
        elif selections[0] == "t_menu":
          if selections[1] == "back":
            text, options = t_lang.main_menu(user.language)
            show_menu(query, text, options)
          elif selections[1] == "act":
            if len(selections) == 2:
              text, options = t_lang.menu_act(user.language)
              show_menu(query, text, options)
            elif selections[2] == "view":
              if len(selections) == 3:
                text, options = t_lang.menu_act_view(user.language)
                show_menu(query, text, options)
              else:
                user.activities_view(update, context, selections[3], query)
            elif selections[2] == "grade":
              if len(selections) == 3:
                text, options = t_lang.menu_act_grade(user.language, "menu")
                show_menu(query, text, options)
              elif selections[3] == "upload":
                text = t_lang.menu_act_grade(user.language, "upload")
                query.edit_message_text(parse_mode="HTML", text=text)
                config_files_send_document(context, user, "grades")
              elif selections[3] == "cmd":
                text = t_lang.menu_act_grade(user.language, "cmd")
                query.edit_message_text(parse_mode="HTML", text=text)
            elif selections[2] == "replace":
              text = t_lang.menu_act_replace(user.language)
              query.edit_message_text(parse_mode="HTML", text=text)
              config_files_send_document(context, user, "activities")
            elif selections[2] == "modify":
              headers = "name\nsection\nweek\n"
              text = t_lang.menu_act_modify(user.language, headers)
              query.edit_message_text(parse_mode="HTML", text=text)
            elif selections[2] == "delete":
              text = t_lang.menu_act_delete(user.language)
              query.edit_message_text(parse_mode="HTML", text=text)
            elif selections[2] == "active":
              sql = (
                f"SELECT DISTINCT _id FROM activities WHERE weight>0 AND active <> 1"
              )
              inactive_act = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)

              inactive_act = "\n".join(sorted(inactive_act))
              text = t_lang.menu_act_active(user.language, "text")
              query.edit_message_text(parse_mode="HTML", text=text)
              text = t_lang.menu_act_active(user.language, "activities", inactive_act)
              g_fun.send_Msg(context, user, text=text)
          elif selections[1] == "stu":
            if len(selections) == 2:
              text, options = t_lang.menu_stu(user.language)
              show_menu(query, text, options)
            elif selections[2] == "view":
              if len(selections) == 3:
                text, options = t_lang.menu_stu_view(user.language)
                show_menu(query, text, options)
              else:
                user.students_view(update, context, selections[3], query)
            elif selections[2] == "add":
              text = t_lang.menu_stu_add(user.language)
              query.edit_message_text(parse_mode="HTML", text=text)
              config_files_send_document(context, user, "students")
            elif selections[2] == "modify":
              headers = "First_name\nLast_name\nEmail"
              text = t_lang.menu_stu_modify(user.language, "cmd", headers)
              query.edit_message_text(parse_mode="HTML", text=text)
            elif selections[2] == "delete":
              text = t_lang.menu_stu_delete(user.language)
              query.edit_message_text(parse_mode="HTML", text=text)
          elif selections[1] == "reports":
            if len(selections) == 2:
              text, options = t_lang.menu_reports(user.language)
              text = "FUNCIONES EN DESARROLLO LO SIENTO.\n\n" + text
              show_menu(query, text, options)
            elif selections[2] == "ARF":
              if len(selections) == 3:
                text, options = t_lang.menu_report_arf(user.language)
                show_menu(query, text, options)
              else:
                user.reports(update, context, selections, query)
            elif selections[2] == "meetings":
              if len(selections) == 3:
                text, options = t_lang.menu_report_meeting(user.language)
                show_menu(query, text, options)
              else:
                user.reports(update, context, selections, query)
            else:
              user.reports(update, context, selections, query)
          elif selections[1] == "activate_eva":
            user.activate_eva(update, context, query)
          elif selections[1] == "msg":
            text = t_lang.send_msg_planet(user.language)
            g_fun.send_Msg(context, user, text=text)
          elif choice == "change_profile":
            cmd.change_profile(update, context)
    else:
      text = b_lang.no_username(update._effective_user.language_code)
      update.message.reply_text(text)
      return False

  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def show_menu(query, menu_text, menu_opt, context="", chat_id=""):
  """[summary]

  Args:
      query ([type]): [description]
      menu_text ([type]): [description]
      menu_opt ([type]): [description]
      context (str, optional): [description]. Defaults to "".
      chat_id (str, optional): [description]. Defaults to "".

  Returns:
      [type]: [description]
  """
  try:
    keyboard = menu_opt
    reply_markup = IKMarkup(keyboard)
    if query:
      query.edit_message_text(
        parse_mode="HTML", text=menu_text, reply_markup=reply_markup
      )
    else:
      context.bot.sendMessage(
        chat_id=chat_id, text=menu_text, reply_markup=reply_markup, parse_mode="HTML"
      )
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def create_evaluation_scheme(df_activities_weights=""):
  try:
    sql = f"DROP TABLE IF EXISTS 'evaluation_scheme'"
    sqlite.execute_sql(sql)
    sql = f"CREATE TABLE evaluation_scheme ({cfg.tables['evaluation_scheme']})"
    sqlite.execute_sql(sql)

    df_activities_weights = df_activities_weights.loc[
      df_activities_weights["weight"] > 0
    ].copy()

    # activities = df_activities_weights["_id"]
    df_activities_weights["category_score"] = 0.0
    df_activities_weights["subject_score"] = 0.0
    df_activities_weights["active"] = 0

    df_evaluation_scheme = df_activities_weights[
      ["_id", "category_score", "subject_score", "active"]
    ].copy()
    sqlite.save_elements_in_DB(df_evaluation_scheme, "evaluation_scheme")
    sql = f"INSERT INTO evaluation_scheme VALUES('SUBJECT', 0.0, 0.0, 0)"
    sqlite.execute_sql(sql)

  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def eva_scheme_tree():
  """Crea el esquema de evaluación, que consiste en las categorías y subcategorias, así como su valor en la evaluación."""
  try:
    cfg.evaluation_scheme = {}
    sql = f"""SELECT _id, weight FROM activities
              WHERE weight > 0
              and _id in
                (SELECT _id FROM evaluation_scheme WHERE active =1)"""
    weights = dict(sqlite.execute_sql(sql, fetch="fetchall", as_dict=True))
    sql = f"""SELECT _id, category FROM activities WHERE category <> ''"""
    categories_active = dict(sqlite.execute_sql(sql, fetch="fetchall", as_dict=True))

    for activity in weights:
      path = g_fun.get_path_elements([activity], categories_active, reverse=False)
      parents = path[activity]
      maplist = []
      for element in parents:
        # category_grade = weights[element] if element != "SUBJECT" else 1
        maplist.append(element)
        if not g_fun.get_from_dict(cfg.evaluation_scheme, maplist):
          g_fun.set_in_dict(
            cfg.evaluation_scheme,
            maplist,
            {},
            # {"value": category_grade, "category_score": 0, "subject_score": 0},
          )
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def thread_grade_activities(context, df_grades, user, meeting=False, weekly_grade=0):
  def grade_activities(df_grades, path_file_name):
    def load_grades(df_grades, path_file_name):
      def separate_elements(df_grades_DB, df_grades):
        def find_sub_activities(activity, activities_list=set()):
          sql = f"SELECT _id FROM activities WHERE category='{activity}'"
          sub_activities = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
          for sub_activity in sub_activities:
            if sub_activity in categories:
              find_sub_activities(sub_activity, activities_list)
            else:
              activities_list.update(sub_activities)
          return activities_list

        try:
          ## SEPARATE ELEMENTS
          sql = "SELECT DISTINCT category FROM activities WHERE category <> ''"
          categories = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
          elements = {}
          elements["registered_stu"] = set(df_grades["email"]) & set(
            df_grades_DB["email"]
          )
          elements["unregistered_stu"] = set(df_grades["email"]) - set(
            df_grades_DB["email"]
          )
          elements["duplicated_stu"] = [
            stu for stu, count in Counter(df_grades["email"]).items() if count > 1
          ]

          sql = f"SELECT _id FROM evaluation_scheme  WHERE active=1"
          activities_active = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
          elements["registered_act"] = set(df_grades.columns) & set(
            df_grades_DB.columns
          )
          elements["registered_act"].remove("email")

          sub_activities = []
          for activity in elements["registered_act"]:
            if activity in categories:
              sub_activities = find_sub_activities(activity)
          elements["registered_act"].update(sub_activities)

          elements["non_active_act"] = elements["registered_act"] - set(
            activities_active
          )

          # TODO: Improve to detect more than one duplicate.
          elements["duplicated_act"] = [
            act[:-2] for act in df_grades.columns if ".1" in act
          ]

          unregistered_act = set(df_grades.columns) - set(df_grades_DB.columns)

          elements["unregistered_act"] = {
            act for act in unregistered_act if ".1" not in act
          }
          for element in elements:
            elements[element] = sorted(list(elements[element]))

          ## DELETE ELEMENTS
          students = set(elements["unregistered_stu"] + elements["duplicated_stu"])
          for stu in students:
            df_grades = df_grades.drop(df_grades[df_grades["email"] == stu].index)

          activities_error = list(unregistered_act) + elements["duplicated_act"]
          df_grades = df_grades.drop(activities_error, axis=1)

          return (df_grades, elements)

        except:
          error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
          g_fun.print_except(error_path)
          return False

      def join_dataframes(df_grades_DB, df_grades, students):
        try:
          column_names = df_grades_DB.columns
          new_df = pd.merge(df_grades_DB, df_grades, on="email", how="left")
          new_df.set_index("email", inplace=True)
          all_columns = list(new_df.columns)
          all_columns.reverse()
          for column in all_columns:
            if "_y" in column:
              column_name = column[:-2]
              column_x = column_name + "_x"

              for student in students:
                grade = new_df.loc[student, column]
                new_df.loc[student, column_x] = grade
              new_df.rename(columns={column_x: column_name}, inplace=True)
            else:
              break

          new_df["email"] = new_df.index
          new_df = new_df[column_names]
          new_df.replace({np.nan: 0.0}, inplace=True)
          return new_df
        except:
          error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
          g_fun.print_except(error_path)
          return False

      def show_error_elements(df_grades, elements):
        try:
          title = True
          if df_grades.shape[0] == 0:
            text = t_lang.menu_act_grade(user.language, "no_students", title=title)
            g_fun.send_Msg(context, user, text=text)
            title = False
          if elements["unregistered_stu"]:
            students = "\n".join(elements["unregistered_stu"])
            num_stu = len(elements["unregistered_stu"])
            text = t_lang.menu_act_grade(
              user.language, "unregistered_stu", students, num_stu, title=title
            )
            g_fun.send_Msg(context, user, text=text)
            title = False
          if elements["duplicated_stu"]:
            students = "\n".join(elements["duplicated_stu"])
            num_stu = len(elements["duplicated_stu"])
            text = t_lang.menu_act_grade(
              user.language, "duplicated_stu", students, num_stu, title=title
            )
            g_fun.send_Msg(context, user, text=text)
            title = False
          if df_grades.shape[1] == 1:
            text = t_lang.menu_act_grade(user.language, "no_activities", title=title)
            g_fun.send_Msg(context, user, text=text)
            title = False
          if elements["unregistered_act"]:
            activities = "\n".join(elements["unregistered_act"])
            num_act = len(elements["unregistered_act"])
            text = t_lang.menu_act_grade(
              user.language, "unregistered_act", activities, num_act, title=title
            )
            g_fun.send_Msg(context, user, text=text)
            title = False
          if elements["duplicated_act"]:
            activities = "\n".join(elements["duplicated_act"])
            num_act = len(elements["duplicated_act"])
            text = t_lang.menu_act_grade(
              user.language, "duplicated_act", activities, num_act, title=title
            )
            g_fun.send_Msg(context, user, text=text)
        except:
          error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
          g_fun.print_except(error_path)
          return False

      try:
        sucess = True
        df_grades_DB = sqlite.table_DB_to_df("grades")
        df_grades, elements = separate_elements(df_grades_DB, df_grades)
        if df_grades.shape[0] == 0 or df_grades.shape[1] == 1:
          sucess = False
        else:
          df_grades_to_upload = join_dataframes(
            df_grades_DB, df_grades, elements["registered_stu"]
          )
          df_grades_to_upload.to_csv(path_file_name, index=False)
          sqlite.save_elements_in_DB(df_grades_to_upload, "grades")

        show_error_elements(df_grades, elements)
        return elements if sucess else False

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    def activate_activities(activities):
      try:
        for activity in activities:
          categories = tuple(activities[activity]) + ("SUBJECT", activity)
          sql = f"UPDATE evaluation_scheme SET active = 1 WHERE _id IN {categories}"
          sqlite.execute_sql(sql)
        cfg.active_activities = True
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    def calculate_evaluation_scheme(new_activities=""):
      try:
        sql = f"SELECT _id, weight FROM activities WHERE weight > 0"
        activities_weight = dict(
          sqlite.execute_sql(sql, fetch="fetch_all", as_dict=True)
        )

        for activity in new_activities:
          categories = new_activities[activity][1:]
          actual_element = activity

          subject_score = activities_weight[activity] if activity != "SUBJECT" else 1
          category_score = activities_weight[activity]

          for category in categories:
            # UPDATE REAL GRADE CATEGORY PARENT

            if category != "SUBJECT":
              category_score *= round(activities_weight[category], 10)
              subject_score *= round(activities_weight[category], 10)
            sql = f"UPDATE evaluation_scheme SET category_score = category_score + {category_score} WHERE _id = '{actual_element}'"
            sqlite.execute_sql(sql)

            actual_element = category
          # UPDATE SUBJECT
          sql = f"UPDATE evaluation_scheme SET category_score = category_score + {category_score} WHERE _id = '{actual_element}'"
          sqlite.execute_sql(sql)

          sql = f"UPDATE evaluation_scheme SET subject_score = subject_score + {subject_score} WHERE _id in {tuple(new_activities[activity])}"
          sqlite.execute_sql(sql)
        sql = f"SELECT subject_score FROM evaluation_scheme WHERE _id = 'SUBJECT'"
        max_actual_score = sqlite.execute_sql(sql, fetch="fetchone")[0]
        sql = f"UPDATE grades SET '_MAX_ACTUAL_SCORE' = {max_actual_score}"
        sqlite.execute_sql(sql)
        # cfg.evaluation_scheme = db.evaluation_scheme.find_one({}, {"_id": 0})
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    def calculate_grades(students, activities):
      def check_ignore_categories():
        try:
          activities_non_cats = {
            activity for activity in activities if activity not in categories
          }
          if not weekly_grade:
            for activity in activities:
              activity_parents = g_fun.get_path_elements([activity], parent_cats)
              for category in activity_parents[activity][1:]:
                if category in cfg.subject_data["ignore_categories"]:
                  cfg.subject_data["ignore_categories"].remove(category)
            activate_cats = ";".join(cfg.subject_data["ignore_categories"])
            sql = f"UPDATE subject_data SET ignore_categories = '{activate_cats}'"
            sqlite.execute_sql(sql)

          ignore_cats = {activity for activity in activities if activity in categories}

          cfg.subject_data["ignore_categories"].update(ignore_cats)
          if ignore_cats:
            ignore_cats = ";".join(cfg.subject_data["ignore_categories"])
            sql = f"UPDATE subject_data SET ignore_categories = '{ignore_cats}'"
            sqlite.execute_sql(sql)
        except:
          error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
          g_fun.print_except(error_path)
          return False

      def set_categories_grades(df_grades, activities, parent_cats, higher_cat=set()):
        """It calculates and stores the actual score of each category based on all the activities that were recorded with the activity file.

                Args:
                    df_grades (dataFrame): Contains the grades of the activities of each student in the DB.
                    activities (list or set): List of activities from which the grade of their parent categories will be obtained.
                    parent_cat (dict): Contains each activity with its corresponding parent category.
                    higher_cat (set): Contains the following level of parent categories. Defaults to set().

                Returns:
                    [type]: [description]
                """
        try:
          if activities:
            new_activities = set()
            for activity in activities:
              parent = parent_cats[activity]
              category_parent = g_fun.get_path_elements([parent], parent_cats)
              higher_cat.update(set(category_parent[parent][1:-1]))
              if parent not in cfg.subject_data["ignore_categories"]:
                df_grades[parent] += round(df_grades[activity] * weights[activity], 7)
              if parent != "SUBJECT" and parent not in higher_cat:
                new_activities.add(parent)
                new_activities = {
                  activity for activity in new_activities if activity not in higher_cat
                }

            if new_activities:
              set_categories_grades(df_grades, new_activities, parent_cats, set())
          return df_grades
        except:
          error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
          g_fun.print_except(error_path)
          return False

      def set_actual_grades():
        """Sets the score for each category based only on the activities that are active at that time."""
        try:
          df_eva_scheme = sqlite.table_DB_to_df("evaluation_scheme", index=True)
          for category in categories:
            max_actual_score = df_eva_scheme.loc[category]["category_score"]
            if max_actual_score:
              if category != "SUBJECT":
                grade = df_grades[category]
                weight = weights[category]
                parent = parent_cats[category]
                parent_weight = weights[parent] if parent != "SUBJECT" else 1
                actual_grade = grade * weight * parent_weight / max_actual_score
                df_actual_grades[category] = round(actual_grade, 10)
              else:
                df_actual_grades["SUBJECT"] = df_grades[category] / max_actual_score
          sqlite.save_elements_in_DB(df_actual_grades, "actual_grades")
        except:
          error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
          g_fun.print_except(error_path)
          return False

      try:
        # COMPLETE CATEGORY GRADES
        sql = f"""SELECT _id, weight FROM activities WHERE weight > 0"""
        weights = dict(sqlite.execute_sql(sql, fetch="fetchall", as_dict=True))
        sql = "SELECT DISTINCT category FROM activities WHERE category <> ''"
        categories = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        sql = f"SELECT _id, category FROM activities WHERE category <> ''"
        parent_cats = dict(sqlite.execute_sql(sql, fetch="fetchall", as_dict=True))
        sql = """SELECT _id FROM activities WHERE weight >0
                and _id in (SELECT _id FROM evaluation_scheme WHERE active = 1)
                and _id not in (SELECT category FROM activities WHERE category <> '')"""
        non_category_acts = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)

        df_grades = sqlite.table_DB_to_df("grades")
        check_ignore_categories()
        reset_categories = list(set(categories) - cfg.subject_data["ignore_categories"])
        df_grades[reset_categories] = 0.0
        df_grades = set_categories_grades(df_grades, non_category_acts, parent_cats)
        max_actual_score = df_grades["_MAX_ACTUAL_SCORE"]
        max_activity_grade = float(cfg.subject_data["max_activity_grade"])
        subject = df_grades["SUBJECT"]
        df_grades["_PERFORMANCE_SCORE"] = (
          subject / max_actual_score / max_activity_grade
        )
        subject_score = subject / max_activity_grade
        df_grades["_MAX_POSSIBLE_GRADE"] = (
          1 - max_actual_score + subject_score
        ) * max_activity_grade
        sqlite.save_elements_in_DB(df_grades, "grades")

        ## ACTUAL_GRADES
        actual_grades_columns = sqlite.table_DB_to_df("actual_grades").columns
        df_actual_grades = pd.concat(
          [df_grades["email"], df_grades[categories]], axis=1
        )
        df_actual_grades = df_actual_grades[actual_grades_columns]
        df_actual_grades[df_actual_grades.columns[1:]] = 0.0
        set_actual_grades()
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    try:
      elements = load_grades(df_grades, path_file_name)
      if elements:
        sql = f"SELECT email FROM risk_factor"
        students = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        sql = "SELECT _id, category FROM activities WHERE weight >0"
        categories = dict(sqlite.execute_sql(sql, fetch="fetchall", as_dict=True))
        non_active_activities = elements["non_active_act"]
        non_active_categories = g_fun.get_path_elements(
          non_active_activities, categories, reverse=True
        )
        if non_active_activities:
          activate_activities(non_active_categories)
          calculate_evaluation_scheme(non_active_categories)
        activities = elements["registered_act"]
        activities_with_categories = g_fun.get_path_elements(
          activities, categories, reverse=True
        )

        calculate_grades(students, activities_with_categories)

        get_risk_factor(students)
        return True
      else:
        return False
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  try:
    # sucess = True
    file_name = "grades_format.csv"
    path_file_name = "files/config/" + file_name
    if grade_activities(df_grades, path_file_name):
      eva_scheme_tree()
      if meeting:
        meeting_num = meeting[0]
        planet = meeting[1]
        text = t_lang.meeting(user.language, "sucess", meeting_num, planet)
      else:
        text = t_lang.menu_act_grade(user.language, "sucess")
    else:
      text = g_lang.error_upload_file(user.language, file_name)
    g_fun.send_Msg(context, user, text=text)
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def get_risk_factor(students):
  """Obtains the academic risk factor (arf) of each student and its linguistic representation (linguistic_arf).

    Args:
        students (list): Student list from which the academic risk factor will be obtained.

    Returns:
        [bool]: True if the process is correct False otherwise.
    """

  def calculate_risk_factor():
    """Calculates each student's academic risk factor for the current week and stores it in a DataFrame."""
    try:
      # Rounding off to avoid excessive decimals
      total_earned_score = round(df_grades["SUBJECT"], 10)
      max_actual_score = round(df_grades["_MAX_ACTUAL_SCORE"], 10)

      max_possible_grade = round(df_grades["_MAX_POSSIBLE_GRADE"], 10)
      # remaining_score = max_final_score - max_actual_score
      remaining_score = round(1 - max_actual_score[0], 10)

      academic_risk_factor = (
        total_earned_score + (max_possible_grade * remaining_score)
      ) / max_final_score
      df_risk_factor[actual_week] = round(academic_risk_factor, 10)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  def set_linguistic_arf():
    """Set the linguistic representation of each student's academic risk factor for the current week and store it in a DataFrame."""
    try:
      lower_limit = min_grade_to_pass / max_final_score
      increment = ((ideal_grading - min_grade_to_pass) / max_final_score) / 3
      for student in students:
        risk_factor = df_risk_factor.loc[student][actual_week]

        if risk_factor >= lower_limit + (increment * 3):
          linguistic_arf = "none"
        elif risk_factor >= lower_limit + (increment * 2):
          linguistic_arf = "low"
        elif risk_factor >= lower_limit + increment:
          linguistic_arf = "moderate"
        elif risk_factor >= lower_limit:
          linguistic_arf = "critical"
        else:
          linguistic_arf = "very_critical"
        df_linguistic_arf.loc[student][actual_week] = linguistic_arf
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  try:
    actual_week = g_fun.get_week(action="text")
    max_final_score = float(cfg.subject_data["max_final_grade"])
    min_grade_to_pass = float(cfg.subject_data["min_grade_to_pass"])
    ideal_grading = float(cfg.subject_data["min_ideal_grade"])

    df_grades = sqlite.table_DB_to_df("grades", index=True)
    df_risk_factor = sqlite.table_DB_to_df("risk_factor", index=True)
    df_linguistic_arf = sqlite.table_DB_to_df("linguistic_risk_factor", index=True)

    calculate_risk_factor()
    set_linguistic_arf()

    df_risk_factor.insert(0, column="email", value=df_risk_factor.index)
    sqlite.save_elements_in_DB(df_risk_factor, "risk_factor")
    df_linguistic_arf.insert(0, column="email", value=df_linguistic_arf.index)
    sqlite.save_elements_in_DB(df_linguistic_arf, "linguistic_risk_factor")

    return True
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def get_admins_group(context, chat_id, planet):
  try:
    admins_list = [
      str(admin.user.id) for admin in context.bot.get_chat_administrators(chat_id)
    ]
    new_admins = set(admins_list)
    if cfg.admins_list:
      if planet in cfg.admins_list:
        new_admins = set(admins_list) - cfg.admins_list[planet]

    if str(context.bot.id) in new_admins:
      text = g_lang.pinned_message(context)
      message_id = context.bot.sendMessage(
        chat_id=chat_id, parse_mode="HTML", text=text
      ).message_id
      context.bot.pinChatMessage(chat_id=chat_id, message_id=message_id)
      cfg.admins_list[planet] = set(admins_list)

      sql = f"""UPDATE planet_admins SET admins = '{','.join(admins_list)}'
                WHERE _id = '{planet}'"""
      sqlite.execute_sql(sql)
    return admins_list
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def status_update(update, context):
  def any_admin_is_teacher():
    sql = (
      f"SELECT telegram_id FROM teachers WHERE telegram_id IN ({','.join(admins_list)})"
    )
    if sqlite.execute_sql(sql, fetch="fetchall", as_list=True):
      return True
    else:
      return False

  def check_planet(chat_id):
    def group_name_change(sql):
      try:
        _id_DB = sqlite.execute_sql(sql, fetch="fetchone")[0]
        sqlite.change_primary_key("planets", _id_DB, planet)
        ''' change_name = [planet, chat_id]
        sql = f"SELECT num_members, active FROM planets WHERE chat_id = {chat_id}"
        change_name.extend(list(sqlite.execute_sql(sql, fetch="fetchone")))
        data = tuple(change_name)
        sql = f"""INSERT INTO planets VALUES {data}"""
        sqlite.execute_sql(sql)
        sql = f"""UPDATE planet_admins
                  SET admins = (SELECT admins from planet_admins WHERE _id='{_id_DB}')
                  WHERE _id = '{planet}'"""
        sqlite.execute_sql(sql) '''

        tables_with_planet = [
          "eva_collaboration",
          "opn_collaboration",
          "planet_users",
          "registered_students",
          "student_messages",
          "teacher_messages",
        ]

        for table in tables_with_planet:
          sql = f"UPDATE '{table}' SET planet = '{planet}' WHERE planet = '{_id_DB}'"
          sqlite.execute_sql(sql)

        # sql = f"DELETE FROM planet_admins WHERE _id='{_id_DB}'"
        # sqlite.execute_sql(sql)
        # sql = f"DELETE FROM planets WHERE  _id='{_id_DB}'"
        # sqlite.execute_sql(sql)
        del cfg.active_meetings[_id_DB]
        del cfg.admins_list[_id_DB]
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    try:
      # When certain changes are made, such as making history visible to new members, the group becomes a supergroup and the chat_id changes.
      if upm.migrate_to_chat_id or upm.migrate_from_chat_id:
        if upm.migrate_to_chat_id:
          chat_id = upm.migrate_to_chat_id
          sql = f"UPDATE planets set chat_id = {chat_id} WHERE _id='{planet}'"
          sqlite.execute_sql(sql)
        elif upm.migrate_from_chat_id:
          return chat_id
      else:
        # ADD PLANET: Only the teacher can add a planet.
        if user.is_teacher:
          sql = f"SELECT chat_id FROM planets WHERE _id='{planet}'"
          if not sqlite.execute_sql(sql, fetch="fetchone"):
            sql = f"SELECT _id FROM planets WHERE chat_id={chat_id}"
            if not sqlite.execute_sql(sql, fetch="fetchone"):
              sql = f"""INSERT OR IGNORE INTO planets (_id, chat_id, active)
              VALUES('{planet}','{chat_id}',1)"""
              sqlite.execute_sql(sql)
            else:
              group_name_change(sql)
          cfg.active_meetings.update({planet: {"users": {}, "meeting": ""}})
      return chat_id
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  def new_member_planet(planet):
    try:
      new_member = upm.new_chat_members[0]
      if not new_member["is_bot"]:
        new_member = g_fun.get_user_data(new_member, planet)
        if not new_member.is_teacher:
          new_member.register_student()
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)
      return False

  try:
    upm = update.message
    chat_id = upm.chat_id
    print(
      f"{'#'*20}\n SE HA REGISTRADO UNA ACTUALIZACION DEL ESTATUS EN EL GRUPO\n{'#'*20}"
    )
    print(update, "\n")
    if chat_id < 0:
      planet = g_fun.strip_accents(upm.chat.title)
      user = g_fun.get_user_data(update._effective_user, planet)

      chat_id = check_planet(chat_id)

      admins_list = get_admins_group(context, chat_id, planet)

      ## NEW MEMBER GROUP
      if user.is_teacher or any_admin_is_teacher():
        if upm.new_chat_members:
          new_member_planet(planet)

        ## MEMBER LEFT THE GROUP
        elif upm.left_chat_member:
          user_data = upm.left_chat_member
          sql = f"""UPDATE FROM planets
          sqlite.execute_sql(sql)
                    SET num_members = num_members - 1
                    WHERE _id = '{planet}'"""
      else:
        bot_id = context.bot.id
        text = g_lang.unauthorized_user(user.language, context)
        context.bot.sendMessage(chat_id=chat_id, parse_mode="HTML", text=text)
        context.bot.kickChatMember(chat_id, bot_id)

  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False
