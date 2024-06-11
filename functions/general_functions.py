import inspect
import logging
import operator
import os
import re
import sys
import random
from datetime import datetime, timedelta
from functools import reduce
from unicodedata import normalize

from colorama import Back, Fore, init
from config import config_file as cfg
from config import db_sqlite_connection as sqlite
from config.create_files_format import create_files
from functions.user_types import Student, Teacher

from functions import bot_functions as b_fun

def config_subject():
  try:
    # If they don't exist, create the tables in the DB
    sql = 'SELECT count(*) FROM sqlite_master WHERE type = "table"'
    if not sqlite.execute_sql(sql, fetch="fetchone")[0]:
      sqlite.create_db()

    # Check if the subject is configured
    cfg.config_files_set = are_config_files_set()

    # Check for active activities
    sql = "SELECT COUNT(*) FROM evaluation_scheme WHERE active=1"
    if sqlite.execute_sql(sql, fetch="fetchone")[0]:
      cfg.active_activities = True

    # Get the date of the Monday of the week in which the course starts
    start_date = cfg.subject_data["start_date"]
    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    cfg.day_start_week = get_weekday_start(start_date)

    #

    # Get the admins for each planet
    sql = f"SELECT _id, admins FROM planet_admins"
    planets = sqlite.execute_sql(sql, fetch="fetchall", as_dict=True)
    if planets:
      planets = dict(planets)
      for planet in planets:
        admins = planets[planet]
        if admins:
          cfg.admins_list[planet] = set(admins.split(","))
        else:
          cfg.admins_list[planet] = set()
        cfg.active_meetings.update({planet: {"users": {}, "meeting": ""}})

    # Get the name and email associated with the Telegram ID of each registered student.
    cfg.registered_stu = sqlite.table_DB_to_df("registered_students")

    # Gets the tree of the evaluation scheme
    b_fun.eva_scheme_tree()

    # Set activate_evaluations
    sql = f"SELECT activate_evaluations FROM subject_data"
    cfg.subject_data["activate_evaluations"] = sqlite.execute_sql(
      sql, fetch="fetchone"
    )[0]

    # Get the resources up to the current week
    cfg.resources["week"] = get_week("num")
    get_resources()

    # GET ignore_categories
    sql = f"SELECT ignore_categories FROM subject_data"
    categories = sqlite.execute_sql(sql, fetch="fetchone")[0]
    if categories:
      cfg.subject_data["ignore_categories"] = set(categories.split(";"))

  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False

def print_except(function, *extra_info):
  try:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    error_text = f"""====================
    ERROR IN FUNCTION {function}
    {exc_type}
    {exc_obj}
    line:{exc_tb.tb_lineno}
    """
    if extra_info:
      for element in extra_info:
        error_text += "\n   " + str(element)
    error_text += "\n===================="
    print(Back.RED + error_text + Back.RESET)
    logging.info(error_text)
  except:
    error_path = f"{error_text}\n\n{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)

def get_user_data(user_data, planet=""):
  try:
    if user_data.username:
      if user_is_teacher(user_data.id):
        user = Teacher(user_data, planet)
      else:
        user = Student(user_data, planet)
        if not user.planet:
          sql = f"SELECT COUNT (*) FROM registered_students WHERE _id = {user._id}"
          if sqlite.execute_sql(sql, fetch="fetchone")[0]:
            sql = f"SELECT planet FROM registered_students where _id = {user._id}"
            user.planet = sqlite.execute_sql(sql, fetch="fetchone")[0]
          else:
            sql = f"SELECT planet FROM students_file where username = '{user_data.username}'"
            user.planet = sqlite.execute_sql(sql, fetch="fetchone")
      # print(user)
      return user
    return False
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False

def get_weekday_start(date):
  try:
    day = date.strftime("%A")
    if day != "Monday":
      for i in range(1, 8):
        monday_date = date - timedelta(days=i)
        day = monday_date.strftime("%A")
        if day == "Monday":
          return monday_date
    else:
      return date
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False

def send_Msg(context, user, text="", mode="HTML", query=""):
  """EDUtrack envía un mensaje al chat especificado.
  chat_id => ID a donde se enviará el mensaje.
  text => Texto del Mensaje.
  mode => Formato del mensaje (HTML ó Markdown).

  """
  try:
    user_id = user.real_id
    #if user.is_teacher:
    #  if user.student_view:
    #    user_id = user.student_id
    if not query:
      context.bot.sendMessage(chat_id=user_id, parse_mode=mode, text=text)
    else:
      query.edit_message_text(parse_mode=mode, text=text, reply_markup=reply_markup)
  except:
    print_except(inspect.stack()[0][3], user_id)

def create_new_user(cotext, user):
  try:
      planets = ["-VENUS-","-MARTE-","-LATIERRA-","-SATURNO-","-URANO-"]
      planet =  planets[random.randint(0,4)]
      email = f"mail_{user._id}@demo.com"
      sql = f"""INSERT INTO registered_students VALUES
                ('{user._id}','{user.telegram_name}',"{email}",'{user.username}', '{planet}')"""
      sqlite.execute_sql(sql)
      cfg.registered_stu = sqlite.table_DB_to_df("registered_students")
  except:
    print_except(inspect.stack()[0][3], user._id)

### CHECARLO CON CREATE GRADES
def get_week(action):
  try:
    today = datetime.now()
    difference = today - cfg.day_start_week
    if cfg.subject_data["start_vacations"] != "dd/mm/yyyy" and cfg.subject_data["start_vacations"]:
      start_vacations = datetime.strptime(
        cfg.subject_data["start_vacations"], "%d/%m/%Y"
      )
      if today >= start_vacations:
        end_vacations = datetime.strptime(cfg.subject_data["end_vacations"], "%d/%m/%Y")
        if today > end_vacations:
          vacations_days = end_vacations - start_vacations
        else:
          vacations_days = today - start_vacations
        difference -= vacations_days + timedelta(days=1)

    num_week = int(difference.days / 7) + 1
    course_weeks = cfg.subject_data["course_weeks"]
    if num_week > int(course_weeks):
      num_week = int(course_weeks)
    if action == "num":
      return num_week
    elif action == "text":
      text_week = "week_"
      if len(course_weeks) != len(str(num_week)):
        text_week += "0" * (len(course_weeks) - len(str(num_week)))
      text_week += str(num_week)
      return text_week
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False


def validate_email(email):
  try:
    if re.match(r"^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$", email.lower()):
      return True
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False


def user_is_teacher(user_id):
  # sql = f"SELECT COUNT(*) FROM teachers WHERE telegram_id={user_id}"
  sql = f"SELECT COUNT(*) FROM telegram_users WHERE _id={user_id} AND is_teacher =  1"
  try:
    return sqlite.execute_sql(sql, fetch="fetchone")[0]
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)


def are_config_files_set(table_name=""):
  try:
    # TODO: VERIFICAR AQUI SI EXISTE O NO O COMO HACER SIN QUE HAYA TABLAS
    sql_stu = "SELECT count(*) FROM students_file"
    sql_act = "SELECT count(*) FROM activities"
    if (
      sqlite.execute_sql(sql_stu, fetch="fetchone")[0]
      and sqlite.execute_sql(sql_act, fetch="fetchone")[0]
    ):
      return True
    return False
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)


def remove_file(file):
  """Recibe el path de un archivo y sí existe lo elimina así como su versión html."""
  try:
    if os.path.isfile(file):
      os.remove(file)
    file = file[:-4] + ".html"
    if os.path.isfile(file):
      os.remove(file)
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)


def dataframes_comparison(df1, df2, which="all"):
  """Find rows which are different between two DataFrames.
    all - Shows the union between the dataframes.
    no_repeat - Shows only the elements that are not repeated.
    both - Shows only the repeated elements.
    only_left - Shows only the elements on the left that are not on the right.
    only_right - Shows only the elements on the right that are not on the left.

    """
  comparison_df = df1.merge(df2, indicator=True, how="outer")
  if which == "all":
    diff_df = comparison_df
  elif which == "no_repeat":
    diff_df = comparison_df[comparison_df["_merge"] != "both"]
  else:
    diff_df = comparison_df[comparison_df["_merge"] == which]
  return diff_df


def db_to_csv_html(df, file, headers=[], title="", date=True, mode="w+"):
  """Guarda la información del cursor almacenado en 'elements' de la base de datos en un archivo 'csv' y 'html' en el path almacenado en 'file'.

    Arguments:
        elements {pymongo.cursor.Cursor} -- Resgistros a guardar en los archivos.
        file {str} -- Path y nombre del archivo sin extensión donde se almacenan los archivos.
        headers {list} -- Lista con el orden de los encabezados para un archivo
        title {str} -- Título que llevara el archivo HTML.
        date {bool} -- Si es True agregara la fecha al final del archivo.

    Returns:
        [bool] -- 'True' si se crean correctamente los archivos 'False' si se genera una excepción.
    """
  try:
    # df = pd.DataFrame(list(elements))
    # TODO: Verificar si no afecta a textos
    if "activities" in file:
      df.sort_values(by=["_id"], inplace=True)
    elif "students" in file:
      df.sort_values(by=["email"], inplace=True)
      for element in ["_jeovani@correo.ugr.es", "_burrita@correo.ugr.es"]:
        df = df.drop(df[df.loc[:, "email"] == element].index)
    if headers:
      df = df[headers]
    if "grades" in file:
      df2 = df.mean()
      df2["_id"] = "PROMEDIOS"
      df = df.append(df2, ignore_index=True)
    df = df.round(2)
    create_files(file, df, title, date, mode=mode)
    return True
  except:
    print_except(inspect.stack()[0][3])
    return False


def strip_accents(string):
  """Recibe un string y elimina los acentos y lo devuelve en mayúsculas."""
  try:
    string = re.sub(
      r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+",
      r"\1",
      normalize("NFD", string),
      0,
      re.I,
    )
    string = normalize("NFC", string)
    return string.upper()
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)


# REVISAR SI SE UTILIZA EL ESQUEMA
def get_evaluation_scheme_tree():
  try:
    cfg.evaluation_scheme = {}
    sql = f"SELECT _id, weight FROM activities WHERE weight > 0"
    weights = dict(sqlite.execute_sql(sql, fetch="fetchall", as_dict=True))
    sql = f"SELECT _id, category FROM activities WHERE category <> ''"
    categories = dict(sqlite.execute_sql(sql, fetch="fetchall", as_dict=True))

    parent = []
    for activity in weights:
      parent = get_path_dict([activity], categories)
      maplist = []
      for element in parent:
        category_grade = weights[element] if element != "SUBJECT" else 1
        maplist.append(element)
        if not get_from_dict(cfg.evaluation_scheme, maplist):
          set_in_dict(
            cfg.evaluation_scheme,
            maplist,
            {},
            # {"value": category_grade, "category_score": 0, "subject_score": 0},
          )
    new = {"_id": "SUBJECT"}
    new.update(cfg.evaluation_scheme["SUBJECT"])
    # del new["category_score"]
    return cfg.evaluation_scheme
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False


def notify_teachers(context, text):
  try:
    sql = "SELECT telegram_id FROM TEACHERS"
    teachers = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
    for teacher in teachers:
      context.bot.sendMessage(chat_id=teacher, parse_mode="HTML", text=text)

  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False


def get_resources():
  try:
    num_week = get_week("num")
    sql = (
      f"SELECT * FROM activities WHERE week < {cfg.resources['week']} and section <> ''"
    )
    resources_data = sqlite.table_DB_to_df("activities", sql=sql, index="_id")
    for resource in list(resources_data.index):
      section = resources_data.loc[resource]["section"]
      if not section in cfg.resources:
        cfg.resources[section] = {resource}
      else:
        cfg.resources[section].add(resource)
    cfg.resources["week"] = num_week
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)
    return False


## Dictionary functions
def get_path_elements(element_list, categories, reverse=True):
  def path_element(element_path):
    try:
      if element_path[0] != "SUBJECT":
        element_path.insert(0, categories[element_path[0]])
        parent = path_element(element_path)
      return element_path
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      print_except(error_path)
      return False

  try:
    path = {}
    for element in element_list:
      path[element] = path_element([element])
      if reverse:
        path[element].reverse()
    return path
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    print_except(error_path)


def get_from_dict(dataDict, mapList):
  try:
    return reduce(operator.getitem, mapList, dataDict)
  except:
    # NO MODIFICAR
    return False


def set_in_dict(dataDict, mapList, value):
  get_from_dict(dataDict, mapList[:-1])[mapList[-1]] = value


## END Dictionary funtions
