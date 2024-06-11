import inspect
import operator
import os
import threading
from datetime import datetime, timedelta
from urllib.request import urlopen

import config.config_file as cfg
import config.db_sqlite_connection as sqlite
import pandas as pd
from telegram import InlineKeyboardButton as IKBtn
from telegram import InlineKeyboardMarkup as IKMarkup
from text_language import general_lang as g_lang
from text_language import student_lang as s_lang
from text_language import teacher_lang as t_lang

from functions import bot_functions as b_fun
from functions import general_functions as g_fun


class User:
  def __init__(self, user_data, planet=""):
    self._id = int(user_data["id"])
    self.real_id = self._id
    self.telegram_name = (
      user_data.full_name if hasattr(user_data, "full_name") else user_data["full_name"]
    )
    self.username = user_data["username"].upper()
    self.language = user_data["language_code"]
    self.planet = g_fun.strip_accents(planet)
    self.email = ""

    if self.language != "es":
      self.language = "en"
    
    sql=f"SELECT COUNT(*) FROM telegram_users WHERE _id={self._id}"
    if (sqlite.execute_sql(sql, "fetchone")[0]):
      sql = f"SELECT is_teacher FROM telegram_users WHERE _id={self._id}"
      self.is_teacher = sqlite.execute_sql(sql,fetch="fetchone")[0]
    else:
      self.add_telegram_user()
      self.create_demo_grades()
    self.set_selected_language()
    
   
    
    #if not self.is_teacher:
    #  self._id = 9999

  def create_demo_grades(self):
    try:
      sql = f"SELECT * FROM grades WHERE email='demo@correo.ugr.es'"
      demo_grades = list(sqlite.execute_sql(sql, fetch="fetchall")[0])
      demo_grades[0] = f"mail_{self._id}@demo.com"
      demo_grades = tuple(demo_grades)
      sql = f"INSERT INTO grades VALUES {demo_grades}"
      sqlite.execute_sql(sql)
      
      sql = f"SELECT * FROM actual_grades WHERE email='demo@correo.ugr.es'"
      demo_grades = list(sqlite.execute_sql(sql, fetch="fetchall")[0])
      demo_grades[0] = f"mail_{self._id}@demo.com"
      demo_grades = tuple(demo_grades)
      sql = f"INSERT INTO actual_grades VALUES {demo_grades}"
      sqlite.execute_sql(sql)
      
      sql = f"SELECT * FROM linguistic_risk_factor WHERE email='demo@correo.ugr.es'"
      demo_grades = list(sqlite.execute_sql(sql, fetch="fetchall")[0])
      demo_grades[0] = f"mail_{self._id}@demo.com"
      demo_grades = tuple(demo_grades)
      sql = f"INSERT INTO linguistic_risk_factor VALUES {demo_grades}"
      sqlite.execute_sql(sql)
      
      
      sql = f"SELECT * FROM risk_factor WHERE email='demo@correo.ugr.es'"
      demo_grades = list(sqlite.execute_sql(sql, fetch="fetchall")[0])
      demo_grades[0] = f"mail_{self._id}@demo.com"
      demo_grades = tuple(demo_grades)
      sql = f"INSERT INTO risk_factor VALUES {demo_grades}"
      sqlite.execute_sql(sql)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False  

  def add_telegram_user(self):
    try:
      sql = f"INSERT OR IGNORE INTO telegram_users VALUES ('{self._id}', '{self.telegram_name}','{self.username}','{self.is_teacher}', '{self.language}');"
      if not sqlite.execute_sql(sql):
        return False
      return True
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def set_selected_language(self):
    """It maintains the language selected by the user."""
    try:
      sql = f"SELECT language, username FROM telegram_users WHERE _id={self._id}"
      language = sqlite.execute_sql(sql, "fetchone")
      if language:
        self.language = language[0]

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def reg_messages(self, update):
    def get_message_type():
      try:
        message_type = ""
        if chat.text:
          message_type = "TEXT"
        elif chat.video or chat.video_note:
          message_type = "VIDEO"
        elif chat.voice:
          message_type = "VOICE"
        elif chat.sticker:
          message_type = "STICKER"
        elif chat.document:
          type_document = chat.document.mime_type.split("/")
          type_document = type_document[0]
          if type_document == "video":
            message_type = "GIF"
          elif type_document == "image":
            message_type = "IMAGE"
          else:
            message_type = "DOCUMENT"
        elif chat.photo:
          message_type = "IMAGE"
        elif chat.poll:
          message_type = "QUIZ"
        return message_type
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      chat = update.message
      message_type = get_message_type()
      if message_type and message_type != "QUIZ":
        meeting_data = cfg.active_meetings[self.planet]
        meeting = meeting_data["meeting"][-1] if meeting_data["meeting"] else -1

        table = "teacher_messages" if self.is_teacher else "student_messages"

        sql = f"""SELECT COUNT(*) FROM {table}
                  WHERE _id = {self._id}
                    and planet = '{self.planet}'
                    and meeting = {meeting} """
        if not sqlite.execute_sql(sql, fetch="fetchone")[0]:
          sql = f"""INSERT OR IGNORE INTO {table} (_id, planet, meeting)
                      VALUES({self._id}, '{self.planet}', {meeting})"""
          sqlite.execute_sql(sql)

        sql = f"""UPDATE {table} SET {message_type} = {message_type} + 1
                  WHERE _id = {self._id}
                    and planet = '{self.planet}'
                    and meeting = {meeting} """
        sqlite.execute_sql(sql)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def set_teacher_view(self,update):
    try:
      sql=f"""SELECT student_view FROM teachers
        WHERE email = (SELECT email FROM telegram_users
        WHERE telegram_id={self._id} )"""
      return sqlite.execute_sql(sql, "fetchone")[0]
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

class Student(User):
  def __init__(self, user_data, planet):
    self.is_teacher = 0
    super().__init__(user_data, planet)

  def register_student(self, from_planet=False):
    def register():
      try:
        sql = f"SELECT * FROM students_file WHERE username = '{self.username}'"
        user_data = sqlite.execute_sql(sql, fetch="fetchone", as_dict=True)
        planet = self.planet

        if user_data:
          if not planet:
            planet = user_data["planet"]
          user_data = dict(user_data)
          values = f"""{self._id}, '{user_data["last_name"]}, {user_data["first_name"]}', '{user_data["email"]}', '{self.username}', '{planet}'"""
          sql = f"INSERT INTO registered_students VALUES({values})"
          sqlite.execute_sql(sql)
        elif from_planet:
          values = f"""{self._id}, "", "", '{self.username}', '{planet}'"""
          sql = f"INSERT INTO registered_students VALUES({values})"
          sqlite.execute_sql(sql)
          cfg.registered_stu = sqlite.table_DB_to_df("registered_students")

        else:
          return False
        return True
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def check_if_change(registered_user):
      try:
        changes = []
        if self.planet and self.planet != registered_user["planet"]:
          planet = self.planet.upper()
          changes.append(f"planet = '{planet}'")
        if self.username and self.username != registered_user["username"]:
          changes.append(f"username = '{self.username}'")

        if not registered_user["full_name"]:
          sql = f"SELECT last_name, first_name FROM students_file where username='{self.username}'"
          name = sqlite.execute_sql(sql, fetch="fetchone")
          if name:
            full_name = f"{name[0]}, {name[1]}"
            changes.append(f"full_name = '{full_name}'")
        if not registered_user["email"]:
          sql = f"SELECT email FROM students_file where username = '{self.username}'"
          email = sqlite.execute_sql(sql, fetch="fetchone")
          if email:
            changes.append(f"email = '{email[0]}'")
        changes = ",".join(changes)
        if changes:
          sql = f"UPDATE registered_students SET {changes} WHERE _id = {self._id}"
          sqlite.execute_sql(sql)
        return True
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      sql = f"SELECT * FROM registered_students WHERE _id={self._id}"
      registered_user = sqlite.execute_sql(sql, fetch="fetchone", as_dict=True)
      if not registered_user:
        if register():
          return True
      else:
        if check_if_change(dict(registered_user)):
          return True
      return False
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def user_send_message(self, update, context):
    try:
      chat = update._effective_message
      from_planet = False
      if cfg.config_files_set:
        if chat.chat_id < 0:
          from_planet = True

        if self.register_student(from_planet):
          if chat.chat_id < 0:
            self.reg_messages(update)
          else:
            text = s_lang.welcome(self.language, context)
            context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
        else:
          text = s_lang.check_email(self.language, "registration")
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
      else:
        if chat.chat_id > 0:
          text = s_lang.not_config_files_set(self.language, context)
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def main_menu(self, update, context):
    try:
      print(
        f"\n{'='*50}\n{self._id} - {self.username} - {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n{'='*50}"
      )
      sql = f"SELECT COUNT(*) FROM registered_students WHERE _id = {self._id}"
      if sqlite.execute_sql(sql, fetch="fetchone")[0]:
        text, options = s_lang.main_menu(self.language)
        keyboard = options
        reply_markup = IKMarkup(keyboard)
        update.message.reply_text(
          parse_mode="HTML", text=text, reply_markup=reply_markup
        )
      else:
        text = s_lang.check_email(self.language, "registration")
        context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def my_grade(self, context, query=""):
    def get_student_grades():
      try:
        sql = f"""SELECT _id FROM activities WHERE weight >0
              and _id not in (SELECT category FROM activities WHERE category <> '')"""
        activities = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)

        sql = f"SELECT * FROM grades WHERE email = '{email}'"
        df_grades_activities = sqlite.execute_sql(sql, df=True)
        sql = f"SELECT * FROM actual_grades WHERE email = '{email}'"
        df_grades_categories = sqlite.execute_sql(sql, df=True)
        df_grades = pd.concat(
          [df_grades_activities[activities], df_grades_categories], axis=1
        )
        df_grades = df_grades[sorted(df_grades.columns)].T
        df_grades.columns = ["grade"]
        return df_grades
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        raise

    def get_student_data():
      try:
        sql = f"""SELECT l.{actual_week}, a.SUBJECT, g._MAX_POSSIBLE_GRADE
                  FROM  linguistic_risk_factor l
                  INNER JOIN grades g
                  ON l.email = g.email
                  INNER JOIN actual_grades a
                  ON l.email = a.email
                  WHERE l.email = '{email}'"""
        data = sqlite.execute_sql(sql, fetch="fetchone")
        linguistic_arf = g_lang.linguistic_arf(self.language, data[0])
        max_activity_grade = float(cfg.subject_data["max_activity_grade"])
        student_data = {}
        if data:
          student_data["linguistic"] = linguistic_arf
          student_data["actual_grade"] = round(data[1], 3)
          student_data["max_possible_grade"] = round(data[2], 3)
        return student_data
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def get_activities_list(eva_scheme, def_grades, text="", level=1):
      try:
        for element in eva_scheme:
          act_name = df_act_names.loc[element]["name"]
          act_name = act_name if act_name else element
          grade = str(round(def_grades.loc[element]["grade"], 3))
          if eva_scheme[element]:
            if df_act_names.loc[element]["visible"]:
              spaces = " " if level == 1 else "  " * level
              text += f"\n\n{spaces}* {act_name} = {grade}"
            text = get_activities_list(eva_scheme[element], def_grades, text, level + 1)
          else:
            if df_act_names.loc[element]["visible"]:
              text += f"\n{'  '*level}   -{act_name} = {grade}"
        return text
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      actual_week = g_fun.get_week("text")
      num_week = g_fun.get_week("num")
      if cfg.active_activities:
        df_reg_stu = cfg.registered_stu.copy()
        if self._id in list(df_reg_stu["_id"]):
          email = df_reg_stu[df_reg_stu["_id"] == self._id]["email"].item()
          if email:
            df_grades = get_student_grades()
            student_data = get_student_data()

            # GET ACTIVITIES LIST
            columns = "_id, name, visible"
            df_act_names = sqlite.table_DB_to_df(
              "activities", columns=columns, index=True
            )
            student_data["activities"] = get_activities_list(
              cfg.evaluation_scheme["SUBJECT"], df_grades
            )

            text = s_lang.my_grade(self.language, "grades", num_week, student_data)
            if query:
              query.edit_message_text(parse_mode="HTML", text=text)
            else:
              context.bot.sendMessage(
                chat_id=int(self._id), parse_mode="HTML", text=text
              )

          else:
            text = s_lang.my_grade(self.language, "no_email", num_week)
            if query:
              query.edit_message_text(parse_mode="HTML", text=text)
            else:
              context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
            text = s_lang.check_email(self.language, "registration")

      else:
        text = s_lang.my_grade(self.language, "no_active", num_week)
        if query:
          query.edit_message_text(parse_mode="HTML", text=text)
        else:
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def opn_tea_practice(self, context, query, selections):
    def select_criterion():
      try:
        if category == "teacher":
          criteria = {
            criterion for criterion in cfg.teacher_criteria if "T_" in criterion
          }
        else:
          criteria = {
            criterion for criterion in cfg.teacher_criteria if "C_" in criterion
          }

        # if email:
        sql = f"""SELECT criterion FROM opn_teacher_practice
        WHERE _id = '{self._id}' and week = {num_week}"""
        evaluated_criteria = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        if evaluated_criteria:
          criteria = criteria - set(evaluated_criteria)

        criteria_dict = {}
        for criterion in criteria:
          criterion_name = g_lang.teacher_criteria(self.language, criterion)
          criteria_dict[criterion_name] = criterion
        criteria = sorted(criteria_dict.items()) if criteria_dict else []

        keyboard = []
        for criterion in criteria:
          keyboard.append(
            [
              IKBtn(
                criterion[0], callback_data=f"s_menu-opn-tp-{category}-{criterion[1]}"
              )
            ]
          )
        back = "-".join(selections[:-1])
        keyboard.append([IKBtn(g_lang.back_text[self.language], callback_data=back)])

        if len(keyboard) == 1:
          text = s_lang.opn_tea_practice(self.language, "no_criteria", week=num_week)
        else:
          text = s_lang.opn_tea_practice(self.language, "choice_criterion", num_week)
        b_fun.show_menu(query, text, keyboard, context, self._id)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def select_value():
      try:
        criterion_name = g_lang.teacher_criteria(self.language, criterion)
        options = g_lang.scale_7(self.language, query.data)
        text = s_lang.opn_tea_practice(
          self.language, "criterion", num_week, criterion_name
        )
        b_fun.show_menu(query, text, options)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def set_value():
      try:
        sql = f"""INSERT OR IGNORE INTO opn_teacher_practice
              VALUES({self._id}, {num_week}, '{criterion}', '{value}')"""
        sqlite.execute_sql(sql)
        text = s_lang.opn_tea_practice(self.language, "success", num_week)
        query.edit_message_text(parse_mode="HTML", text=text)

        self.opn_tea_practice(context, query="", selections=selections[:-2])
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      num_week = g_fun.get_week("num")

      criterion = value = ""
      category = selections[3]

      if len(selections) > 4:
        criterion = selections[4]
        if len(selections) > 5:
          value = selections[5]
          set_value()
        else:
          select_value()
      else:
        select_criterion()

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def opn_collaboration(self, context, query, selections):
    def select_classmate():
      try:
        self.planet = "JUPITER"
        sql_classmates = f"""SELECT _id FROM planet_users
                        WHERE planet = '{self.planet}' and _id <> {self._id}"""
        sql_evaluated = f"""SELECT classmate_id FROM opn_collaboration
                        WHERE _id = {self._id} and planet = '{self.planet}'"""
        sql = f"""SELECT _id, full_name FROM registered_students
                WHERE _id <>{self._id} and
                _id in ({sql_classmates}) and _id not in ({sql_evaluated})"""
        classmates = sqlite.execute_sql(sql, fetch="fetchall", as_dict=True)
        if classmates:
          classmates = dict(classmates)
          classmates = sorted(classmates.items(), key=operator.itemgetter(1))

        keyboard = []
        for classmate in classmates:
          keyboard.append(
            [IKBtn(classmate[1], callback_data=f"s_menu-opn-coll-{classmate[0]}")]
          )
        back = "-".join(selections[:-1])
        keyboard.append([IKBtn(g_lang.back_text[self.language], callback_data=back)])
        if len(keyboard) == 1:
          text = s_lang.opn_collaboration(self.language, "no_classmates", num_week)
        else:
          text = s_lang.opn_collaboration(self.language, "choice", num_week)
        b_fun.show_menu(query, text, keyboard, context, self._id)

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def select_value():
      try:
        df_stu_reg = cfg.registered_stu.copy()
        df_stu_reg.set_index("_id", inplace=True)
        data = {}
        data["name"] = df_stu_reg.loc[classmate]["full_name"]
        data["username"] = df_stu_reg.loc[classmate]["username"]
        options = g_lang.scale_7(self.language, query.data)
        text = s_lang.opn_collaboration(self.language, "scale", num_week, data)
        b_fun.show_menu(query, text, options)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def set_value():
      try:
        sql = f"""INSERT OR IGNORE INTO opn_collaboration
              VALUES({self._id}, '{self.planet}',{classmate},{num_week},'{value}')"""
        sqlite.execute_sql(sql)
        text = s_lang.opn_collaboration(self.language, "success", num_week)
        query.edit_message_text(parse_mode="HTML", text=text)
        self.opn_collaboration(context, query="", selections=selections[:-2])

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      # actual_week = g_fun.get_week("text")
      num_week = g_fun.get_week("num")
      classmate = value = ""

      if len(selections) > 3:
        classmate = int(selections[3])
        if len(selections) > 4:
          value = selections[4]
          set_value()
        else:
          select_value()
      else:
        select_classmate()
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def opn_rsrcs(self, context, query, selections):
    def select_section():
      try:
        sections = sorted(cfg.resources)
        sections.remove("week")
        keyboard = []
        for section in sections:
          sql = f"""SELECT COUNT(resource) FROM opn_resources
                  WHERE _id = {self._id} and section = '{section}'"""
          rsrcs_evaluated = sqlite.execute_sql(sql, fetch="fetchone")[0]
          if rsrcs_evaluated < len(cfg.resources[section]):
            keyboard.append(
              [IKBtn(section, callback_data=f"s_menu-opn-rsrcs-{section}")]
            )
            """ for resource in cfg.resources[section]:
              if resource not in resources_evaluated:
                keyboard.append(
                  [IKBtn(section, callback_data=f"s_menu-opn-rsrcs-{section}")]
                )
                break """
        back = "-".join(selections[:-1])
        keyboard.append([IKBtn(g_lang.back_text[self.language], callback_data=back)])

        if len(keyboard) == 1:
          text = s_lang.opn_resources(self.language, "no_section")
        else:
          text = s_lang.opn_resources(self.language, "section")
        b_fun.show_menu(query, text, keyboard, context, self._id)

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def select_resource():
      try:
        sql_evaluated = f"""SELECT resource FROM opn_resources
                          WHERE _id = {self._id} and section = '{section}'"""
        sql = f"""SELECT _id FROM activities
                WHERE section = '{section}' and week < {num_week}
                and _id not in ({sql_evaluated})"""
        resources = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        keyboard = []
        if resources:
          for resource in sorted(resources):
            resource_name = rsrc_name[resource] if rsrc_name[resource] else resource
            keyboard.append(
              [
                IKBtn(
                  resource_name, callback_data=f"s_menu-opn-rsrcs-{section}-{resource}"
                )
              ]
            )
        back = "-".join(selections[:-1])
        keyboard.append([IKBtn(g_lang.back_text[self.language], callback_data=back)])
        if len(keyboard) == 1:
          text = s_lang.opn_resources(self.language, "no_resources")
        else:
          text = s_lang.opn_resources(self.language, "rsrc")
        b_fun.show_menu(query, text, keyboard, context, self._id)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def select_value():
      try:
        resource_name = rsrc_name[resource]
        options = g_lang.scale_7(self.language, query.data)
        text = s_lang.opn_resources(self.language, "scale", resource)
        b_fun.show_menu(query, text, options)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def set_value():
      try:
        sql = f"""INSERT OR IGNORE INTO opn_resources
              VALUES({self._id},'{section}', '{resource}','{value}')"""
        sqlite.execute_sql(sql)
        text = s_lang.opn_resources(self.language, "success")
        query.edit_message_text(parse_mode="HTML", text=text)
        self.opn_rsrcs(context, query="", selections=selections[:-2])
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      # actual_week = g_fun.get_week("text")
      num_week = g_fun.get_week("num")
      if cfg.resources["week"] < num_week:
        g_fun.get_resources()
      section = resource = value = ""

      sql = "SELECT _id, name FROM activities WHERE section <> ''"
      rsrc_name = sqlite.execute_sql(sql, fetch="fetchall", as_dict=True)
      if rsrc_name:
        rsrc_name = dict(rsrc_name)

      if len(selections) > 3:
        section = selections[3]
        if len(selections) > 4:
          resource = selections[4]
          if len(selections) > 5:
            value = selections[5]
            set_value()
          else:
            select_value()
        else:
          select_resource()
      else:
        select_section()

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def opn_tea_meetings(self, context, query, selections):
    def select_meeting():
      try:
        sql_meetings_evaluated = f"""SELECT DISTINCT meeting
                                  FROM opn_teacher_meetings
                                  where _id = {self._id}"""
        sql = f"""SELECT DISTINCT meeting FROM teacher_messages
                WHERE meeting <> -1
                and meeting not in ({sql_meetings_evaluated})"""
        meetings = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        keyboard = []
        for meeting in meetings:
          keyboard.append(
            [IKBtn(f"Meeting {meeting}", callback_data=f"s_menu-opn-tp-meet-{meeting}")]
          )
        back = "-".join(selections[:-1])
        keyboard.append([IKBtn(g_lang.back_text[self.language], callback_data=back)])
        if len(keyboard) == 1:
          text = s_lang.opn_tea_meeting(self.language, "no_meetings")
          b_fun.show_menu(query, text, keyboard, context, self._id)

        else:
          text = s_lang.opn_tea_meeting(self.language, "text_meeting")
          b_fun.show_menu(query, text, keyboard, context, self._id)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def select_value():
      try:
        options = g_lang.scale_7(self.language, query.data)
        text = s_lang.opn_tea_meeting(self.language, "scale", meeting)
        b_fun.show_menu(query, text, options)

        """ g_fun.show_menu(
          query,
          g_lang.scale_7(user["language"], query.data),
          stu_lang.opn_tea_meet(user["language"], "scale", meeting_num),
        ) """
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def set_value():
      try:
        sql = f"""INSERT OR IGNORE INTO opn_teacher_meetings
        VALUES ({self._id}, {meeting}, '{value}')"""
        sqlite.execute_sql(sql)
        text = s_lang.opn_tea_meeting(self.language, "success")
        query.edit_message_text(parse_mode="HTML", text=text)

        self.opn_tea_meetings(context, query="", selections=selections[:-2])
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      if len(selections) > 4:
        meeting = selections[4]
        if len(selections) > 5:
          value = selections[5]
          set_value()
        else:
          select_value()
      else:
        select_meeting()

        """  g_fun.show_menu(
          query, keyboard, stu_lang.opn_tea_meet(user["language"], "no_meetings")
        ) """

      """ if db.opn_teacher_meetings.find_one():
        meeting = value = "" """

    except:
      g_fun.print_except(inspect.stack()[0][3], self.__str__(), selections)

  def opn_planet(self, context, query, selections):
    def select_value():
      try:
        options = g_lang.scale_7(self.language, query.data)
        text = s_lang.opn_planet(self.language, "scale", self.planet)
        b_fun.show_menu(query, text, options)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def set_value():
      try:
        sql = f"""INSERT OR IGNORE INTO opn_planet
        VALUES ({self._id}, '{self.planet}', {num_week}, '{value}')"""
        sqlite.execute_sql(sql)

        self.opn_planet(context, query="", selections=selections[:-1])
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      num_week = g_fun.get_week("num")
      sql = f"""SELECT COUNT(*) FROM opn_planet
                WHERE _id={self._id} and planet = '{self.planet}'"""
      if self.planet and not sqlite.execute_sql(sql, fetch="fetchone")[0]:
        if len(selections) > 3:
          value = selections[3]
          set_value()
        else:
          select_value()
      else:
        back = "-".join(selections[:-1])
        keyboard = [[IKBtn(g_lang.back_text[self.language], callback_data=back)]]
        if self.planet:
          text = s_lang.opn_planet(self.language, "already")
        else:
          text = s_lang.opn_planet(self.language, "no_planet")
        b_fun.show_menu(query, text, keyboard, context, self._id)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def eva_autoevaluation(self, context, query, selections):
    def check_status():
      """Check if some questions have already been answered, start or finish the self-assessment."""
      try:
        sql = f"SELECT COUNT(*) FROM eva_autoevaluation WHERE _id = {self._id}"
        num_questions = sqlite.execute_sql(sql, fetch="fetchone")[0]
        if not num_questions:
          text, options = s_lang.eva_autoevaluation(self.language, "init")
          b_fun.show_menu(query, text, options)
        elif num_questions < 5:
          text, options = s_lang.eva_autoevaluation(self.language, "continue")
          b_fun.show_menu(query, text, options)
        else:
          text = s_lang.eva_autoevaluation(self.language, "success")
          query.edit_message_text(parse_mode="HTML", text=text)

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def show_questions():
      """Displays the corresponding question or feedback."""
      try:
        question = ""
        if selections[3] == "init":
          question = "Q1"
        elif selections[3] == "continue":
          sql = f"""SELECT MAX(question) FROM eva_autoevaluation
                  WHERE _id = {self._id}"""
          question = sqlite.execute_sql(sql, fetch="fetchone")[0]
          question = f"Q{str(question+1)}"
        elif selections[3] == "end":
          text = s_lang.eva_autoevaluation(self.language, "success")
          query.edit_message_text(parse_mode="HTML", text=text)
        else:
          question = selections[3]

        if question:
          text, options = s_lang.eva_autoevaluation(
            self.language, "question", question=question
          )
          b_fun.show_menu(query, text, options)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def set_value():
      """Saves in the database the value corresponding to each question."""
      try:
        question = selections[3]
        num_question = int(question[1:])
        value = int(selections[4])

        if question == "Q3":
          value = 1 if value == 0 else 0

        sql = f"""SELECT COUNT(*) FROM eva_autoevaluation
                  WHERE _id = {self._id} and question = {num_question}"""
        if not sqlite.execute_sql(sql, fetch="fetchone")[0]:
          sql = f"""INSERT OR IGNORE INTO eva_autoevaluation
                  VALUES({self._id}, {num_question}, {value})"""
          sqlite.execute_sql(sql)

        next_question = "end" if num_question == 5 else "Q" + str(num_question + 1)

        text, options = s_lang.eva_autoevaluation(
          self.language, "response", question=f"R{question}", next_=next_question
        )
        b_fun.show_menu(query, text, options)

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      if len(selections) == 3:
        check_status()
      elif len(selections) == 4:
        show_questions()

      elif len(selections) == 5:
        set_value()

      return True

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def eva_collaboration(self, context, query, selections):
    def select_classmate():
      try:
        sql_classmates = f"""SELECT _id FROM planet_users
                        WHERE planet = '{self.planet}' and _id <> {self._id}"""
        sql_evaluated = f"""SELECT classmate_id FROM eva_collaboration
                        WHERE _id = {self._id} and planet = '{self.planet}'"""
        sql = f"""SELECT _id, full_name FROM registered_students
                WHERE _id <>{self._id} and
                _id in ({sql_classmates}) and _id not in ({sql_evaluated})"""
        classmates = sqlite.execute_sql(sql, fetch="fetchall", as_dict=True)
        if classmates:
          classmates = dict(classmates)
          classmates = sorted(classmates.items(), key=operator.itemgetter(1))
        keyboard = []
        for classmate in classmates:
          keyboard.append(
            [IKBtn(classmate[1], callback_data=f"s_menu-eva-coll-{classmate[0]}")]
          )
        back = "-".join(selections[:-1])
        keyboard.append([IKBtn(g_lang.back_text[self.language], callback_data=back)])
        if len(keyboard) == 1:
          text = s_lang.eva_collaboration(self.language, "no_classmates")
        else:
          text = s_lang.eva_collaboration(self.language, "choice")
        b_fun.show_menu(query, text, keyboard, context, self._id)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def select_value():
      try:
        df_stu_reg = cfg.registered_stu.copy()
        print(df_stu_reg.head(5))
        df_stu_reg.set_index("_id", inplace=True)
        data = {}
        print(df_stu_reg.loc[classmate])
        data["name"] = df_stu_reg.loc[classmate]["full_name"]
        data["username"] = df_stu_reg.loc[classmate]["username"]
        options = g_lang.scale_7(self.language, query.data)
        text = s_lang.eva_collaboration(self.language, "scale", data)
        b_fun.show_menu(query, text, options)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def set_value():
      try:
        sql = f"""INSERT OR IGNORE INTO eva_collaboration
              VALUES({self._id}, '{self.planet}',{classmate},'{value}')"""
        sqlite.execute_sql(sql)
        text = s_lang.eva_collaboration(self.language, "success")
        query.edit_message_text(parse_mode="HTML", text=text)
        self.eva_collaboration(context, query="", selections=selections[:-2])
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      if len(selections) > 3:
        classmate = int(selections[3])
        if len(selections) > 4:
          value = selections[4]
          set_value()
        else:
          select_value()
      else:
        select_classmate()

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def eva_teacher(self, context, query, selections):
    try:
      sql = f"""SELECT COUNT(*) FROM eva_teacher WHERE _id= {self._id}"""
      if not sqlite.execute_sql(sql, fetch="fetchone")[0]:
        if len(selections) == 3:
          text = s_lang.eva_teacher(self.language, "scale")
          options = g_lang.scale_7(self.language, query.data)
          b_fun.show_menu(query, text, options)

        elif len(selections) == 4:
          value = selections[3]
          sql = f"""INSERT OR IGNORE INTO eva_teacher
                  VALUES({self._id},'{value}')"""
          sqlite.execute_sql(sql)
          self.eva_teacher(context, query, selections[:-1])
      else:
        text = s_lang.eva_teacher(self.language, "sucess")
        query.edit_message_text(parse_mode="HTML", text=text)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def suggestion(self, update, context):
    try:
      if context.args:
        emails = cfg.registered_stu.copy()
        emails = emails.set_index("_id")
        message = " ".join(context.args)
        email = emails.loc[self._id]["email"]
        today = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        sql = f"INSERT INTO suggestions VALUES({self._id}, '{email}', '{today}', '{message}')"
        sqlite.execute_sql(sql)
        text = s_lang.suggestion(self.language, "save")
        context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
      else:
        text = s_lang.suggestion(self.language, "empty")
        context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def check_email(self, update, context):
    try:
      if not self.register_student():
        if len(context.args) == 1:
          email = context.args[0].lower()
          if g_fun.validate_email(email):
            sql = f"SELECT COUNT(*) FROM registered_students WHERE email='{email}'"
            if sqlite.execute_sql(sql, "fetchone")[0]:
              # Tenia registration como accion
              text = s_lang.check_email(self.language, "exists_email")
              context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
              return True
            else:
              sql = f"SELECT * FROM students_file WHERE email='{email}'"
              student = sqlite.execute_sql(sql, fetch="fetchone", as_dict=True)
              if student:
                student = dict(student)
                values = f"{self._id}, '{student['last_name']}, {student['first_name']}', '{email}', '{self.username}','{student['planet']}'"
                sql = f"INSERT INTO registered_students VALUES({values})"
                sqlite.execute_sql(sql)
                cfg.registered_stu[self._id] = email
                if student["planet"]:
                  cfg.active_meetings.update(
                    {student["planet"]: {"users": {}, "meeting": ""}}
                  )
                text = s_lang.check_email(self.language, "success", email)
                context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
                text = s_lang.welcome(self.language, context, "long")
                context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
                cfg.registered_stu = sqlite.table_DB_to_df("registered_students")
                return True

              else:
                text = s_lang.check_email(self.language, "not_found")
                context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
          else:
            text = g_lang.email_syntax_error(self.language, email)
            context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
        elif len(context.args) < 1:
          text = s_lang.check_email(self.language, "no_args")
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
        else:
          text = s_lang.check_email(self.language, "many_args", " ".join(context.args))
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
      else:
        sql = f"SELECT email FROM registered_students WHERE _id={self._id}"
        email_DB = sqlite.execute_sql(sql, "fetchone")
        if email_DB:
          text = s_lang.check_email(self.language, "registered_user", email_DB[0])
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def __str__(self):
    return f"""
    ===============================
      STUDENT
      ID: {self._id}
      Telegram_name: {self.telegram_name}
      Username: {self.username}
      Is_teacher : {self.is_teacher}
      Language: {self.language}
      Planet: {self.planet}
      {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}
    ==============================="""


class Teacher(User):
  def __init__(self, user_data, planet):
    #self.is_teacher = 1
    super().__init__(user_data, planet)
    

  def user_send_message(self, update, context):
    def is_configuration_file(doc):
      try:
        if doc.file_name == "grades_format.csv":
          return "grades"
        elif doc.file_name in cfg.list_config_files:
          sql_stu = f"SELECT count(*) FROM students_file"
          sql_act = f"SELECT count(*) FROM activities"
          if (
            doc.file_name == "students_format.csv"
            and sqlite.execute_sql(sql_stu, "fetchone")[0]
          ) or (
            doc.file_name == "activities_format.csv"
            and sqlite.execute_sql(sql_act, "fetchone")[0]
          ):
            return "exists"
          else:
            return True
        else:
          return False
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())

    try:
      chat = update._effective_message
      if cfg.config_files_set and not chat.document:
        if chat.chat_id < 0:
          b_fun.get_admins_group(context, chat.chat_id, self.planet)
          self.reg_messages(update)
        else:
          text = t_lang.welcome_text(self.language, context, "short")
          context.bot.sendMessage(chat_id=self._id, text=text)

      elif chat.document:
        # Check if the document is a configuration document.
        if chat.chat_id > 0:
          doc = chat.document
          config_file = is_configuration_file(doc)
          if config_file:
            if config_file == "grades":
              if cfg.config_files_set:
                input_file = context.bot.get_file(doc.file_id)
                f_path = input_file["file_path"]
                df_grades = pd.read_csv(urlopen(f_path), encoding="UTF-8-sig")
                df_grades = b_fun.data_preparation(df_grades, "grades")
                thread_grades = threading.Thread(
                  target=b_fun.thread_grade_activities, args=(context, df_grades, self)
                )
                thread_grades.start()
              else:
                text = t_lang.config_files(self.language, "no_set_up")
                context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
                b_fun.config_files_set(update, context, self)
            elif config_file == "exists":
              text = t_lang.config_files(self.language, "exists_in_DB", doc.file_name)
              context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
            else:
              b_fun.config_files_upload(update, context, self)

      else:
        if chat.chat_id > 0:
          text = t_lang.config_files(self.language, "no_set_up")
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
          b_fun.config_files_set(update, context, self)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())

  def main_menu(self, update, context):
    try:
      print(
        f"\n{'='*50}\n{self._id} - {self.username} - {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n{'='*50}"
      )
      text, options = t_lang.main_menu(self.language)
      keyboard = options
      reply_markup = IKMarkup(keyboard)
      update.message.reply_text(parse_mode="HTML", text=text, reply_markup=reply_markup)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def activities_view(self, update, context, option, query=""):
    try:
      if not os.path.exists("files/download"):
        os.makedirs("files/download")
      if option == "all":
        file = "files/download/all_activities"
        activities = sqlite.table_DB_to_df("activities")
        title = t_lang.title_file(self.language, "ALL ACTIVITIES")
      elif option == "qualifying":
        file = "files/download/qualifying_activities"
        sql = f"SELECT * FROM activities WHERE weight>0"
        activities = sqlite.execute_sql(sql, df=True)
        title = t_lang.title_file(self.language, "QUALIFYING ACTIVITIES")
      elif option == "resources":
        file = "files/download/resources_activities"
        sql = f"SELECT * FROM activities WHERE name<>''"
        activities = sqlite.execute_sql(sql, df=True)
        title = t_lang.title_file(self.language, "RESOURCES ACTIVITIES")
      if g_fun.db_to_csv_html(activities, file, title=title, date=False):
        reply_markup = ""
        text = g_lang.file_ready_for_download(self.language)
        query.edit_message_text(parse_mode="HTML", text=text, reply_markup=reply_markup)
      else:
        text = g_lang.file_not_created(self.language)

      context.bot.sendDocument(chat_id=self._id, document=open(f"{file}.csv", "rb"))
      context.bot.sendDocument(chat_id=self._id, document=open(f"{file}.html", "rb"))
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def grade_activity_cmd(self, update, context):
    try:
      args = context.args
      if len(args) >= 3:
        activity_id = args[0].upper()
        sql = f"SELECT COUNT(_id) FROM activities WHERE _id= '{activity_id}';"
        if sqlite.execute_sql(sql, fetch="fetchone")[0]:
          #  separate_students(args, activity_id)
          students_grades = " ".join(args[1:]).split(";")
          if students_grades[-1] == "":
            students_grades.remove("")

          students = {}
          if students_grades and students_grades != [""]:
            grades_error = ""
            duplicated_students = []
            for student in students_grades:
              print(student)
              data = (student.strip(" ")).split(" ")
              email = data[0]
              try:
                grade = float(" ".join(data[1:]))
                if email not in students and email not in duplicated_students:
                  students[email] = float(grade)
                elif email not in duplicated_students:
                  duplicated_students.append(email)
                  del students[email]
              except:
                grades_error += "\n" + " ".join(data)

            text = ""
            title = True
            if grades_error:
              text = t_lang.menu_act_grade(self.language, "grades_error", grades_error)
              title = False
            if duplicated_students:
              duplicated_students = "\n" + "\n".join(duplicated_students)
              if not title:
                text += "\n\n"
              text += t_lang.menu_act_grade(
                self.language, "duplicated_stu", duplicated_students, title=title
              )
              context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
            df_grades = pd.DataFrame(
              list(students.items()), columns=["email", activity_id]
            )
            if not df_grades.empty:
              thread_grades = threading.Thread(
                target=b_fun.thread_grade_activities, args=(context, df_grades, self)
              )
              thread_grades.start()
            else:
              text = t_lang.menu_act_grade(self.language, "no_students", title=False)
              context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)

        else:
          text = t_lang.menu_act_grade(
            self.language, "unregistered_act", activity_id, 1
          )
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)

      else:
        text = t_lang.menu_act_grade(self.language, "no_arguments")
        context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def students_view(self, update, context, option, query=""):
    try:
      if not os.path.exists("files/download"):
        os.makedirs("files/download")
      if option == "file":
        file = "files/download/students_format"
        students = sqlite.table_DB_to_df("students_file")
        title = t_lang.title_file(self.language, "STUDENTS_FORMAT")
      elif option == "reg":
        file = "files/download/registered_students"
        students = sqlite.table_DB_to_df("registered_students")
        if not students.empty:
          title = t_lang.title_file(self.language, "STUDENTS REGISTERED")
        else:
          text = t_lang.menu_stu_view(self.language, "no_elements_registered")
          query.edit_message_text(parse_mode="HTML", text=text)
          return False
      if g_fun.db_to_csv_html(students, file, title=title, date=False):
        reply_markup = ""
        text = g_lang.file_ready_for_download(self.language)
        query.edit_message_text(parse_mode="HTML", text=text, reply_markup=reply_markup)
      else:
        text = g_lang.file_not_created(self.language)

      context.bot.sendDocument(chat_id=self._id, document=open(f"{file}.csv", "rb"))
      context.bot.sendDocument(chat_id=self._id, document=open(f"{file}.html", "rb"))
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def modify_student(self, update, context):
    def modify_email():
      try:
        username = context.args[0].upper()
        cfg.registered_stu.set_index("username", inplace=True)
        if username in cfg.registered_stu.index:
          new_email = context.args[1].lower()
          if g_fun.validate_email(new_email):
            student = cfg.registered_stu.loc[username]
            if student["email"]:
              tables = [
                "students_file",
                "actual_grades",
                "grades",
                "linguistic_risk_factor",
                "risk_factor",
              ]

              for table in tables:
                sqlite.change_primary_key(table, student["email"], new_email)

              for table in ["suggestions", "registered_students"]:
                sql = f"UPDATE '{table}' SET email = '{new_email}' WHERE email='{student['email']}'"
                sqlite.execute_sql(sql)
            else:
              sql = f"""UPDATE registered_students SET email = '{new_email}'
                      WHERE username = '{username}'"""
              sqlite.execute_sql(sql)

              sql = f"""UPDATE students_file
                      SET username = '{username}', planet = '{student["planet"]}'
                      WHERE email = '{new_email}'"""
              sqlite.execute_sql(sql)
            text = t_lang.menu_stu_modify(self.language, "success", data="email")
            context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
          else:
            text = g_lang.email_syntax_error(self.language, new_email)
            context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
        else:
          text = t_lang.menu_stu_modify(
            self.language, "unregistered_user", data=username
          )
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def modify_name():
      try:
        sql = f"SELECT first_name, last_name FROM students_file where email = '{email}'"
        student_data = sqlite.execute_sql(sql, fetch="fetchone", as_dict=True)
        if student_data:
          student_data = dict(student_data)
          if column == "first_name":
            full_name = f"{student_data['last_name']}, {value}"
          else:
            full_name = f"{value}, {student_data['first_name']}"
          sql = (
            f"UPDATE students_file SET '{column}' = '{value}' WHERE email ='{email}'"
          )
          sqlite.execute_sql(sql)
          sql = f"""UPDATE registered_students SET full_name = '{full_name}'
                    WHERE email ='{email}'"""
          sqlite.execute_sql(sql)
          text = t_lang.menu_stu_modify(self.language, "success", data=column)
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      if len(context.args) == 2:
        modify_email()
      elif len(context.args) >= 3:
        email = context.args[0]
        if g_fun.validate_email(email):
          column = context.args[1].lower()
          value = " ".join(context.args[2:]).upper()
          cfg.registered_stu.set_index("email", inplace=True)
          if email in cfg.registered_stu.index:
            if column == "first_name" or column == "last_name":
              modify_name()
            else:
              text = t_lang.menu_stu_modify(self.language, "column_error", data=column)
              context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
          else:
            text = t_lang.menu_stu_modify(
              self.language, "unregistered_email", data=email
            )
            context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
        else:
          text = g_lang.email_syntax_error(self.language, email)
          context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
      else:
        text = g_lang.wrong_num_arguments(self.language)
        context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
        text = t_lang.menu_stu_modify(
          self.language, "cmd", headers="first_name\nlast_name"
        )
        context.bot.sendMessage(chat_id=self._id, parse_mode="HTML", text=text)
      cfg.registered_stu = sqlite.table_DB_to_df("registered_students")
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def reports(self, update, context, selections, query=""):
    def create_report(elements=False, mode="w+"):
      try:
        if type(elements) != bool:
          first_column = elements.columns[0]
          elements.sort_values(by=[first_column], inplace=True)
          if g_fun.db_to_csv_html(elements, file, title=title, date=False, mode=mode):
            context.bot.sendDocument(
              chat_id=self._id, document=open(f"{file}.csv", "rb")
            )
            context.bot.sendDocument(
              chat_id=self._id, document=open(f"{file}.html", "rb")
            )
            text = g_lang.file_ready_for_download(self.language)
            query.edit_message_text(parse_mode="HTML", text=text)
        else:
          text = "FUNCION EN DESARROLLO\n\n" + g_lang.file_not_created(self.language)
          query.edit_message_text(parse_mode="HTML", text=text)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    def get_linguistic_term(values):
      try:
        average = sum(values) / len(values)
        if average > 5.5:
          label = "s_6"
          ling_term = g_lang.scale_7_labels(self.language, "Excellent")
        elif average > 4.5:
          label = "s_5"
          ling_term = g_lang.scale_7_labels(self.language, "Very Good")
        elif average > 3.5:
          label = "s_4"
          ling_term = g_lang.scale_7_labels(self.language, "Good")
        elif average > 2.5:
          label = "s_3"
          ling_term = g_lang.scale_7_labels(self.language, "Normal")
        elif average > 1.5:
          label = "s_2"
          ling_term = g_lang.scale_7_labels(self.language, "Bad")
        elif average > 0.5:
          label = "s_1"
          ling_term = g_lang.scale_7_labels(self.language, "Very Bad")
        else:
          label = "s_0"
          ling_term = g_lang.scale_7_labels(self.language, "Lousy")
        return (average, label, ling_term)
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    def add_total_row(df, pos_sum_col, pos_sum_row):
      try:
        first_column = df.columns[0]
        df["TOTAL"] = 0
        df["TOTAL"] = df.iloc[:, pos_sum_col:-1].sum(axis=1)
        df.loc["TOTAL"] = df.iloc[:, pos_sum_row:].sum(axis=0)
        df.loc["TOTAL", first_column] = "_TOTAL"
        return df
      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False

    try:
      report_type = selections[2]
      folder_path = "files/download/reports"
      if not os.path.exists(folder_path):
        os.makedirs(folder_path)

      if report_type == "grades":
        file = f"{folder_path}/Grades"
        sql = f"SELECT * FROM grades"
        df_grades = sqlite.execute_sql(sql, df=True)
        title = t_lang.title_file(self.language, "GRADE REPORT")
        create_report(df_grades)

      elif report_type == "ARF":
        file = f"{folder_path}/ARF"
        action = selections[3]
        if action == "ling":
          sql = f"SELECT * FROM linguistic_risk_factor"
          title = t_lang.title_file(
            self.language, "LIGUISTIC REPORT ACADEMIC RISK FACTOR"
          )
        elif action == "risk":
          file = f"{folder_path}/students_at_risk"
          week = g_fun.get_week("text")
          sql = f"SELECT email,{week} FROM linguistic_risk_factor WHERE {week} in ('moderate','critical', 'very critical')"
          title = t_lang.title_file(self.language, "STUDENTS AT ACADEMIC RISK REPORT")
        df_risk = sqlite.execute_sql(sql, df=True)
        create_report(df_risk)

      elif report_type == "meetings":
        action = selections[3]
        sql = f"SELECT MAX(meeting) FROM meetings_attendance"
        last_meeting = sqlite.execute_sql(sql, fetch="fetchone")[0]
        if last_meeting >= 0:
          if action == "att":
            try:
              file = f"{folder_path}/Meetings_attendance"
              df_attendance = cfg.registered_stu[["_id", "email"]].copy()
              df_attendance.set_index("_id", inplace=True)
              for i in range(0, last_meeting + 1):
                df_attendance[f"Meeting {i}"] = 0
                sql = f"SELECT _id FROM meetings_attendance WHERE meeting = {i}"
                df_students = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
                df_attendance.loc[df_students, f"Meeting {i}"] = 1
              add_total_row(df_attendance, 1, 1)

              title = t_lang.title_file(self.language, "GENERAL MESSAGE REPORT")
              create_report(df_attendance)
            except:
              error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
              g_fun.print_except(error_path)
              return False
          if action == "meet":

            def select_meeting():
              keyboard = []
              for i in range(0, last_meeting + 1):
                keyboard.append(
                  [
                    IKBtn(
                      f"Meeting {i}", callback_data=f"t_menu-reports-meetings-meet-{i}"
                    )
                  ]
                )
              keyboard.append([IKBtn("Atrás", callback_data="t_menu-reports")])

              if len(keyboard) == 1:
                print("No se ha realizado ningun meeting")
                self.reports(update, context, selections[:-2], query)
              else:
                text = t_lang.menu_report_meeting_msgs(self.language)
                b_fun.show_menu(query, text, keyboard)

            def prepare_report():
              df_students = cfg.registered_stu[["_id", "email", "planet"]].copy()
              sql = f"""SELECT A.email, B.* FROM registered_students A
                        LEFT JOIN student_messages B ON a._id = B._id
                        WHERE B.meeting = {meeting}"""
              df_meetings_msgs = sqlite.execute_sql(sql, df=True)
              empty_students = list(
                set(df_students["_id"]) - set(df_meetings_msgs["_id"])
              )
              df_students = df_students[df_students["_id"].isin(empty_students)]

              df_students.set_index("_id", inplace=True)
              df_meetings_msgs.set_index("_id", inplace=True)

              df_meetings_msgs = pd.concat([df_meetings_msgs, df_students])
              df_meetings_msgs["meeting"] = meeting
              df_meetings_msgs.fillna(0.0, inplace=True)
              return df_meetings_msgs

            try:
              file = f"{folder_path}/Msgs_x_meeting"
              if len(selections) == 4:
                select_meeting()
                return True
              elif len(selections) == 5:
                meeting = selections[4]
                df_meetings_msgs = prepare_report()
                add_total_row(df_meetings_msgs, 3, 3)
                title = t_lang.title_file(
                  self.language, "OUT OF MEETINGS PARTICIPATION REPORT"
                )
                create_report(df_meetings_msgs)

            except:
              error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
              g_fun.print_except(error_path)
              return False
          if action == "out":
            try:
              file = f"{folder_path}/Msgs_out_meetings"
              df_students = cfg.registered_stu[["_id", "email", "planet"]].copy()
              sql = f"""SELECT A.email, B.* FROM registered_students A
                      LEFT JOIN student_messages B ON a._id = B._id
                      WHERE B.meeting = -1"""
              df_meetings_msgs = sqlite.execute_sql(sql, df=True)
              empty_students = list(
                set(df_students["_id"]) - set(df_meetings_msgs["_id"])
              )
              df_students = df_students[df_students["_id"].isin(empty_students)]
              df_students.set_index("_id", inplace=True)
              df_meetings_msgs.set_index("_id", inplace=True)

              df_meetings_msgs = pd.concat([df_meetings_msgs, df_students])
              df_meetings_msgs.drop(["meeting"], axis=1, inplace=True)
              df_meetings_msgs.fillna(0.0, inplace=True)
              add_total_row(df_meetings_msgs, 2, 2)

              title = t_lang.title_file(
                self.language, "OUT OF MEETINGS PARTICIPATION REPORT"
              )
              create_report(df_meetings_msgs)

            except:
              error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
              g_fun.print_except(error_path)
              return False
          if action == "general":
            try:
              file = f"{folder_path}/General_messages"
              df_emails = cfg.registered_stu[["_id", "email"]].copy()
              df_emails.set_index("_id", inplace=True)
              sql = "SELECT * FROM student_messages"
              df_students = sqlite.execute_sql(sql, df=True)
              df_students.set_index("_id", inplace=True)
              df_students.insert(0, "email", "")
              for student in df_students.index:
                df_students.loc[student, "email"] = df_emails.loc[student, "email"]
              add_total_row(df_students, 3, 3)

              title = t_lang.title_file(self.language, "GENERAL MESSAGE REPORT")
              create_report(df_students)
            except:
              error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
              g_fun.print_except(error_path)
              return False

      elif report_type == "eva_teacher":
        file = f"{folder_path}/Eva_teacher"
        sql = f"SELECT value FROM eva_teacher"
        values = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        values = [float(value[-1]) for value in values]
        average, label, ling_term = get_linguistic_term(values)
        df_teacher_eva = pd.DataFrame(
          {"evaluation": [average], "label": [label], "linguistic_term": [ling_term]}
        )

        title = t_lang.title_file(self.language, "TEACHER EVALUATION REPORT")
        create_report(df_teacher_eva)

      elif report_type == "eva_resources":
        file = f"{folder_path}/Eva_resources"
        resources = cfg.resources
        df_resources = pd.DataFrame(
          columns=[
            "_id",
            "name",
            "section",
            "evaluation",
            "label",
            "linguistic_term",
            "num_values",
          ]
        )
        for section in resources:
          if section == "week":
            continue
          for resource in resources[section]:
            sql = f"""SELECT value fROM opn_resources
                      WHERE resource = '{resource}'"""
            values = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
            if values:
              values = [float(value[-1]) for value in values]
              average, label, ling_term = get_linguistic_term(values)
            else:
              average = label = ling_term = "-"
            sql = f"SELECT name FROM activities WHERE _id='{resource}'"
            rsrc_name = sqlite.execute_sql(sql, fetch="fetchone")[0]
            df_resources = df_resources.append(
              {
                "_id": resource,
                "name": rsrc_name,
                "section": section,
                "evaluation": average,
                "label": label,
                "linguistic_term": ling_term,
                "num_values": len(values),
              },
              ignore_index=True,
            )

        title = t_lang.title_file(self.language, "RESOURCES EVALUATION REPORT")
        create_report(df_resources)

      elif report_type == "eva_p2p":
        file = f"{folder_path}/Eva_peer_colaboration"
        sql = "SELECT DISTINCT _id FROM eva_collaboration"
        evaluators = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        if cfg.subject_data["activate_evaluations"]:
          data = {}
          sql = "SELECT _id FROM registered_students"
          reg_students = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
          data["num_reg_students"] = len(reg_students)
          data["num_evaluators"] = len(evaluators)
          data["pct_evaluators"] = round(len(evaluators) * 100 / len(reg_students), 1)

          if data["pct_evaluators"] < 100:
            no_evaluators = tuple(set(reg_students) - set(evaluators))

            sql = f"""SELECT full_name FROM registered_students WHERE _id in {no_evaluators} """
            no_evaluators_names = sqlite.execute_sql(
              sql, fetch="fetchall", as_list=True
            )
            no_evaluators_names.sort()
            data["no_evaluators_names"] = "\n".join(no_evaluators_names)
            text = t_lang.report_peer_eva(self.language, "missing", data)
          else:
            text = t_lang.report_peer_eva(self.language, "all_students", data)
          query.edit_message_text(parse_mode="HTML", text=text)
        else:
          sql = "SELECT COUNT (*) FROM report_eva_collaboration"
          if not sqlite.execute_sql(sql, fetch="fetchone")[0]:
            sql = "SELECT COUNT(*) FROM eva_collaboration"
            if sqlite.execute_sql(sql, fetch="fetchone")[0]:
              df_students = cfg.registered_stu[["_id", "email"]].copy()
              df_students["evaluation_obtained"] = 0.0
              df_students["label"] = ""
              df_students["linguistic_term"] = ""
              df_students["grade"] = 0.0
              df_students["evaluated_peers"] = 0
              df_students.set_index("_id", inplace=True)
              sql = "SELECT DISTINCT classmate_id FROM eva_collaboration"
              students_evaluated = sqlite.execute_sql(
                sql, fetch="fetchall", as_list=True
              )
              sql = "SELECT * FROM grades"
              df_grades = sqlite.execute_sql(sql, df=True)
              df_grades.set_index("email", inplace=True)
              for student in students_evaluated:
                sql = f"""SELECT value FROM eva_collaboration
                      WHERE classmate_id = {student}"""
                values = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
                values = [float(value[-1]) for value in values]
                average, label, ling_term = get_linguistic_term(values)
                df_students.loc[student, "evaluation_obtained"] = average
                df_students.loc[student, "label"] = label
                df_students.loc[student, "linguistic_term"] = ling_term
                grade = average * 10 / 6
                df_students.loc[student, "grade"] = round(grade, 3)
                if student in evaluators:
                  df_students.loc[student, "evaluated_peers"] = 1
                email = df_students.loc[student]["email"]
                df_grades.loc[email]["FC_ML_EVA_COMPAÑERO"] = grade
              sqlite.save_elements_in_DB(df_students, "report_eva_collaboration")
              # #TODO:ESTA COMENTADO PARA QUE LA DRA INDIQUE SI QUIERE QUE SE AJUSTE AUTOMATICAMENTE.
              # sqlite.save_elements_in_DB(df_grades, "grades")

            else:
              text = t_lang.report_peer_eva(self.language, "no_evaluation")
              query.edit_message_text(parse_mode="HTML", text=text)
              return False
          sql = "SELECT * FROM report_eva_collaboration"
          title = t_lang.title_file(
            self.language, "CLASSMATES EVALUATION REPORT IN MEETINGS"
          )
          df_eva_collaboration = sqlite.execute_sql(sql, df=True)
          create_report(df_eva_collaboration)

      elif report_type == "autoeva":
        file = f"{folder_path}/Autoevaluations"
        if not cfg.subject_data["activate_evaluations"]:
          sql = "SELECT COUNT(*) FROM eva_autoevaluation"
          if sqlite.execute_sql(sql, fetch="fetchone")[0]:
            sql = "SELECT DISTINCT _id FROM eva_autoevaluation"
            df_students = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
            df_autoevaluation = cfg.registered_stu[["_id", "email"]].copy()
            df_autoevaluation["evaluation"] = 0.0
            df_autoevaluation["grade"] = 0.0
            df_autoevaluation.set_index("_id", inplace=True)
            for student in df_students:
              sql = f"""SELECT SUM(value) FROM eva_autoevaluation
                        WHERE _id = {student}"""
              total = sqlite.execute_sql(sql, fetch="fetchone")[0]
              df_autoevaluation.loc[student, "evaluation"] = total
              df_autoevaluation.loc[student, "grade"] = total * 10 / 5
            title = t_lang.title_file(self.language, "AUTOEVALUATION REPORT")
            create_report(df_autoevaluation)
          else:
            text = t_lang.repor_autoeva(self.language, "no_evaluation")
            query.edit_message_text(parse_mode="HTML", text=text)
            return False
        else:
          text = t_lang.repor_autoeva(self.language, "eva_open")
          query.edit_message_text(parse_mode="HTML", text=text)
          return False

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def activate_eva(self, update, context, query):
    try:
      chat_id = update.callback_query.message.chat_id
      flag = 0
      if chat_id > 0:
        flag = 1 if cfg.subject_data["activate_evaluations"] == 0 else 0
        sql = "SELECT COUNT(*) FROM report_eva_collaboration"
        if flag == 1 and sqlite.execute_sql(sql, fetch="fetchone")[0]:
          sqlite.execute_sql("DELETE FROM report_eva_collaboration")
        sql = f"UPDATE subject_data SET activate_evaluations={flag}"
        sqlite.execute_sql(sql)
        cfg.subject_data["activate_evaluations"] = flag
        text = t_lang.menu_activate_eva(self.language, flag)
        query.edit_message_text(parse_mode="HTML", text=text)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def send_msg_planets(self, update, context):
    try:
      chat_id = update._effective_chat.id
      if chat_id > 0:
        sql = "SELECT DISTINCT chat_id FROm planets"
        planets = sqlite.execute_sql(sql, "fecthall", as_list=True)
        print(context.args)
        text = " ".join(context.args)
        text = text.replace("\\n", "\n")
        text = text.replace("\\t", "\t\t")
        for planet in planets:
          context.bot.sendMessage(chat_id=planet, parse_mode="HTML", text=text)

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

  def set_meetings(self, update, context, chat="", change_grades=False):
    def set_meeting_attendance():
      try:
        sql = f"SELECT DISTINCT _id FROM student_messages WHERE meeting = {meeting_num}"
        students = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        df_students = pd.DataFrame(students, columns=["_id"])
        df_students["meeting"] = meeting_num
        df_students_DB = sqlite.table_DB_to_df("meetings_attendance")
        df_attendance = pd.concat([df_students_DB, df_students])
        df_attendance = df_attendance.drop_duplicates()
        sqlite.save_elements_in_DB(df_attendance, "meetings_attendance")

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    def get_score_meetings():
      """Guarda la calificación de cada estudiante que ha participado en el meeting especificado.

            Arguments:
                planet {str} -- Nombre del planeta
                meeting {[type]} -- ID del meeting
            """
      try:
        meeting_id = f"ML_{meeting.upper()}"
        sql = f"""SELECT email FROM registered_students WHERE _id in
                (SELECT _id FROM meetings_attendance WHERE meeting = '{meeting_num}')"""
        students_email = sqlite.execute_sql(sql, fetch="fetchall", as_list=True)
        emails = "','".join(students_email)
        df_grades = sqlite.table_DB_to_df(
          "grades", columns=f"email, {meeting_id}", index=True
        )

        for student in students_email:
          if student:
            # TODO: REVISAR LA CALIFICACION SOBRE 10 ó SOBRE 1
            df_grades.loc[student][meeting_id] = 10

        df_grades.insert(0, column="email", value=df_grades.index)
        df_grades.reset_index(drop=True, inplace=True)
        meeting_data = (meeting, self.planet)
        thread_grade_meeting = threading.Thread(
          target=b_fun.thread_grade_activities,
          args=(context, df_grades, self, meeting_data),
        )
        thread_grade_meeting.start()

      except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path, self.__str__())
        return False

    try:
      args = context.args
      planet = g_fun.strip_accents(chat.chat.title)
      if len(args) == 1:
        try:
          meeting_num = int(args[0])
        except:
          text = t_lang.meeting(self.language, "is_not_a_number", args[0])
          context.bot.sendMessage(chat_id=chat.chat_id, parse_mode="HTML", text=text)
          return False
        else:
          meeting = f"meeting_{meeting_num}"
          if chat.text.startswith("/start_meeting"):
            if planet not in cfg.active_meetings:
              cfg.active_meetings.update({planet: {"users": {}, "meeting": meeting}})
            elif not cfg.active_meetings[planet]["meeting"]:
              cfg.active_meetings[planet]["meeting"] = meeting
              text = t_lang.meeting(self.language, "start", meeting_num)
              context.bot.sendMessage(
                chat_id=chat.chat_id, parse_mode="HTML", text=text
              )
            else:
              text = t_lang.meeting(self.language, "active", meeting_num)
              context.bot.sendMessage(
                chat_id=chat.chat_id, parse_mode="HTML", text=text
              )

          elif chat.text.startswith("/end_meeting"):
            if cfg.active_meetings[planet]["meeting"]:
              if meeting in cfg.active_meetings[planet]["meeting"]:
                cfg.active_meetings[planet]["meeting"] = ""
                # cfg.closed_meetings.add(meeting)
                text = t_lang.meeting(self.language, "end", meeting_num)
                context.bot.sendMessage(
                  chat_id=chat.chat_id, parse_mode="HTML", text=text
                )
                # Guarda en la base de datos la asisencia a meetings
                set_meeting_attendance()
                get_score_meetings()

              else:
                meeting_num = cfg.active_meetings[planet]["meeting"][-1]
                text = t_lang.meeting(self.language, "finish_no_active", meeting_num)
                context.bot.sendMessage(
                  chat_id=chat.chat_id, parse_mode="HTML", text=text
                )
            else:
              text = t_lang.meeting(self.language, "none_active", meeting_num)
              context.bot.sendMessage(
                chat_id=chat.chat_id, parse_mode="HTML", text=text
              )
      else:
        if not args:
          if cfg.active_meetings:
            if cfg.active_meetings[planet]:
              if cfg.active_meetings[planet]["meeting"]:
                meeting_num = cfg.active_meetings[planet]["meeting"][-1]
                text = t_lang.meeting(self.language, "no_number", meeting_num)
                context.bot.sendMessage(
                  chat_id=chat.chat_id, parse_mode="HTML", text=text
                )
                return False

          text = t_lang.meeting(self.language, "no_number")
          context.bot.sendMessage(chat_id=chat.chat_id, parse_mode="HTML", text=text)
          return False
        else:
          text = t_lang.meeting(self.language, "error_args")
          context.bot.sendMessage(chat_id=chat.chat_id, parse_mode="HTML", text=text)
        return False

    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path, self.__str__())
      return False

 
  def __str__(self):
    return f"""
    ===============================
      TEACHER
      ID: {self._id}
      Telegram_name: {self.telegram_name}
      Username: {self.username}
      Is_teacher : {self.is_teacher}
      Language: {self.language}
      Planet: {self.planet}
      Student_view: {self.student_view}
      {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}
    ==============================="""
