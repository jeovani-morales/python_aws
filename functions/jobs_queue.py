# from datetime import time, datetime
import datetime
import inspect
import sys
from time import localtime, sleep, time

import config.config_file as cfg
import config.db_sqlite_connection as sqlite
import pandas as pd
import pytz
import telegram.ext

from functions import bot_functions as b_fun
from functions import general_functions as g_fun
from functions.user_types import Student


def weekly_arf(context):
  try:
    if cfg.config_files_set:
      if cfg.active_activities:
        user_data = {}
        df_students_data = sqlite.table_DB_to_df("telegram_users", index=True)

        for student in cfg.registered_stu["_id"]:  # students.index:
          data = df_students_data.loc[student]
          user_data["id"] = data.name
          user_data["full_name"] = data.telegram_name
          user_data["username"] = data.username
          user_data["language_code"] = data.language
          user = Student(user_data, "")
          user.my_grade(context)
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def set_resources_week(context):
  try:
    cfg.resources["week"] = g_fun.get_week("num")
    g_fun.get_resources()
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def calculate_weekly_grades(context):
  try:
    madrid = pytz.timezone("Europe/Madrid")
    local_date = madrid.localize(datetime.datetime.now())
    print(local_date)

    user = context.bot
    user.language = ""
    user._id = 970_331_050
    if cfg.config_files_set:
      sql_categories = "SELECT DISTINCT category FROM activities WHERE category <>''"
      sql = f"""SELECT _id FROM evaluation_scheme WHERE active = 1
                and _id not in ({sql_categories})"""
      active_activities = sqlite.execute_sql(sql, fetch="fetch_all", as_list=True)
      if active_activities:
        active_activities = "email," + ",".join(active_activities)
        df_grades = sqlite.table_DB_to_df("grades", columns=active_activities)
        b_fun.thread_grade_activities(context, df_grades, user, weekly_grade=True)

  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def check_changes_telegram_names(context):
  try:
    sql = "SELECT _id, telegram_name from telegram_users"
    telegram_names = sqlite.execute_sql(sql, fetch="fetchall", as_dict=True)
    if telegram_names:
      telegram_names = dict(telegram_names)
      sql = "SELECT _id, chat_id FROM planets"
      planets = sqlite.execute_sql(sql, fetch="fetchall", as_dict=True)
      if planets:
        planets = dict(planets)
        for planet in planets:
          chat_id = planets[planet]
          sql = f"SELECT _id FROM registered_students WHERE planet = '{planet}'"
          students = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
          for student in students:
            stu_data = context.bot.getChatMember(chat_id, student)["user"]
            full_name = stu_data.full_name
            if telegram_names[student] != full_name:
              sql = f"""UPDATE telegram_users SET telegram_name = '{full_name}'
                      WHERE _id={student}"""
              sqlite.execute_sql(sql)
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False


def start_jobs(bot_jobs):
  try:
    # Set the time zone
    # target_tzinfo = datetime.timezone(datetime.timedelta(hours=+2))

    target_tzinfo = pytz.timezone("Europe/Madrid")

    target_time = datetime.time(hour=12, minute=30, tzinfo=target_tzinfo)
    job_weekly_arf = bot_jobs.run_daily(weekly_arf, target_time, days=(0, 4))

    target_time = datetime.time(hour=1, minute=30, tzinfo=target_tzinfo)
    job_set_calculate_grades = bot_jobs.run_daily(
      calculate_weekly_grades, target_time, days=(0, 1, 2, 3, 4, 5, 6)
    )

    target_time = datetime.time(hour=2, tzinfo=target_tzinfo)
    job_set_resources_week = bot_jobs.run_daily(
      set_resources_week, target_time, days=(0,)
    )
    target_time = datetime.time(hour=2, minute=30, tzinfo=target_tzinfo)
    job_check_telegram_names_changes = bot_jobs.run_daily(
      check_changes_telegram_names, target_time, days=(0, 1, 2, 3, 4, 5, 6)
    )

    # ENVIA MENSAJES A LOS ESTUDIANTES
    # job_minute = bot_jobs.run_repeating(weekly_arf, interval=3000, first=1)
    # SOLO CALCULA LAS CALIFICACIONES
    # job_minute = bot_jobs.run_repeating(calculate_weekly_grades, interval=1000, first=1)
    """ job_minute = bot_jobs.run_repeating(
      check_changes_telegram_names, interval=3000, first=1
    ) """
  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False
