import inspect
import logging

import config.config_file as cfg
import config.db_sqlite_connection as sqlite
from text_language import bot_lang as b_lang
from text_language import general_lang as g_lang
from text_language import student_lang as s_lang
from text_language import teacher_lang as t_lang

from functions import bot_functions as b_fun
from functions import general_functions as g_fun

##################
# GENERAL COMMANDS


def change_profile(update, context):
  try:
    chat = update._effective_message
    user = g_fun.get_user_data(update._effective_user)
    if chat.chat_id > 0:
      if user:
        user.is_teacher = 0 if user.is_teacher else 1
        sql = f"""UPDATE telegram_users SET is_teacher = {user.is_teacher}
                  WHERE _id='{user._id}'"""
        sqlite.execute_sql(sql)
      text = g_lang.change_profile_text(user, context)
      g_fun.send_Msg(context, user, text)
    else:
      return

  except:
    error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
    g_fun.print_except(error_path)
    return False

def start(update, context):
    """Start a conversation with the user. Register the user in the database and check if the subject is configured to welcome the user.

    Args:
        update (:class:'telegram.update.Update'): Current request received by the bot
        context (:class:'telegram.ext.callbackcontext.CallbackContext'): Context of the current request

    Returns:
        bool: Returns True if the process is performed correctly or False if an error is generated.
    """
    try:
      chat = update._effective_message
      user = g_fun.get_user_data(update._effective_user)
      if chat.chat_id > 0:
        if user:
          logging.info(
            f"User {user.real_id} {user.telegram_name}, start a conversation."
          )
          if user.is_teacher:
            if cfg.config_files_set:
              text = t_lang.welcome_text(user, context, "start")
              g_fun.send_Msg(context, user, text=text)
            else:
              b_fun.config_files_set(update, context, user)
          else:
            if cfg.config_files_set:
              if user.register_student():
                text = s_lang.welcome(user, context, "long")
                g_fun.send_Msg(context, user, text=text)
              else:
                g_fun.create_new_user(context, user)
                text = s_lang.welcome(user, context, "long")
                g_fun.send_Msg(context, user, text=text)
            else:
              text = s_lang.not_config_files_set(user.language, context)
              g_fun.send_Msg(context, user, text=text)
        else:
          text = b_lang.no_username(update._effective_user.language_code)
          update.message.reply_text(text)
          return False
      else:
        text = g_lang.wrong_command_group(user.language, context)
        context.bot.sendMessage(chat_id=chat.chat_id, parse_mode="HTML", text=text)
    except:
      error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
      g_fun.print_except(error_path)

def change_language(update, context):
    """Change the language in which the contents are displayed.

    Args:
        update (:class:'telegram.update.Update'): Current request received by the bot
        context (:class:'telegram.ext.callbackcontext.CallbackContext'): Context of the current request

    Returns:
        bool: Returns True if the process is performed correctly or False if an error is generated.
    """

    try:
        chat = update._effective_message
        user_data = update._effective_user
        if chat.chat_id > 0:
            sql = f"SELECT language FROM telegram_users WHERE _id={user_data.id}"
            language = sqlite.execute_sql(sql, "fetchone")[0]
            new_lang = "es" if language == "en" else "en"
            sql = f"UPDATE telegram_users SET language = '{new_lang}' WHERE _id={user_data.id}"
            sqlite.execute_sql(sql)
            text = g_lang.change_language(new_lang)
            context.bot.sendMessage(chat_id=chat.chat_id, parse_mode="HTML", text=text)
        else:
            text = g_lang.wrong_command_group(user_data.language, context)
            context.bot.sendMessage(chat_id=chat.chat_id, parse_mode="HTML", text=text)

    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def help(update, context):
    try:
        chat_id = update._effective_chat.id
        if chat_id > 0:
            user = g_fun.get_user_data(update._effective_user)
            context.bot.sendDocument(
                chat_id=user._id,
                document=open(g_lang.help_send_manual[user.language], "rb"),
            )
            text = g_lang.help(user.language, context)
            g_fun.send_Msg(context, user, text=text)
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def menu(update, context):
    """[summary]

    Args:
        update ([type]): [description]
        context ([type]): [description]

    Returns:
        [type]: [description]
    """
    try:
        chat = update._effective_message
        if chat.chat_id > 0:
            user = g_fun.get_user_data(update._effective_user)
            if user:
                if cfg.config_files_set:
                    user.main_menu(update, context)
                else:
                    if user.is_teacher:
                        text = t_lang.config_files(user.language, "no_set_up")
                        g_fun.send_Msg(context, user, text=text)
                        b_fun.config_files_set(update, context, user)
                    else:
                        text = s_lang.not_config_files_set(user.language, context)
                        g_fun.send_Msg(context, user, text=text)
            else:
                text = b_lang.no_username(update._effective_user.language_code)
                update.message.reply_text(text)
                return False
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def test_user(update, context):
    try:
        print("Entro en TEST_USER")
        user = g_fun.get_user_data(update._effective_user)
        user.student_view = 1 if not user.student_view else 0
        sql = f"""UPDATE teachers SET student_view={user.student_view}
      WHERE email = (SELECT email FROM telegram_users WHERE telegram_id='{user._id}')"""
        sqlite.execute_sql(sql)
        if user.student_view:
            g_fun.send_Msg(context, user, f"HAS ENTRADO COMO ESTUDIANTE")
        else:
            g_fun.send_Msg(context, user, f"TE ENCUENTRAS EN MODO DOCENTE")

    except:
        g_fun.print_except(
            inspect.stack()[0][3], update._effective_user, update._effective_chat
        )


##################
# TEACHER COMMANDS


def grade_activity(update, context):
    try:
        chat = update._effective_message

        if chat.chat_id > 0:
            user = g_fun.get_user_data(update._effective_user)
            if user:
                if user.is_teacher:
                    user.grade_activity_cmd(update, context)
            else:
                text = b_lang.no_username(update._effective_user.language_code)
                update.message.reply_text(text)
                return False
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def set_meeting(update, context):
    try:
        chat = update._effective_message
        user_data = update._effective_user
        if chat.chat_id < 0:
            planet = g_fun.strip_accents(chat.chat.title)
            user = g_fun.get_user_data(user_data, planet)
            if user:
                if user.is_teacher:
                    user.set_meetings(update, context, chat)
            else:
                text = b_lang.no_username(update._effective_user.language_code)
                update.message.reply_text(text)
                return False
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def modify_student(update, context):
    try:
        chat = update._effective_message
        if chat.chat_id > 0:
            user = g_fun.get_user_data(update._effective_user)
            if user:
                if user.is_teacher:
                    user.modify_student(update, context)
        else:
            text = b_lang.no_username(update._effective_user.language_code)
            update.message.reply_text(text)
            return False
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def add_teacher(update, context):
    try:
        chat = update._effective_message
        user = g_fun.get_user_data(update._effective_user)
        if user:
            if chat.chat_id > 0:
                if len(context.args) == 2:
                    username_teacher = context.args[0].upper()
                    email_teacher = context.args[1].lower()
                    sql = f"SELECT COUNT(*) FROM teachers WHERE username = '{username_teacher}'"
                    if not sqlite.execute_sql(sql, fetch="fetchone")[0]:
                        sql = f"SELECT * FROM telegram_users WHERE username='{username_teacher}'"
                        teacher_data = sqlite.execute_sql(sql, "fetchone", as_dict=True)

                        if teacher_data:
                            teacher_data = dict(teacher_data)
                            values = f"""
              '{email_teacher}', '{teacher_data["telegram_name"]}', '{username_teacher}',{teacher_data["_id"]}
              """
                            sql = f"INSERT INTO teachers VALUES({values})"
                            sqlite.execute_sql(sql)
                            text = t_lang.add_teacher(
                                user.language, "sucess", username_teacher
                            )
                        else:
                            text = t_lang.add_teacher(
                                user.language,
                                "not_found",
                                user.username,
                                context.bot.username,
                            )

                    else:
                        text = t_lang.add_teacher(user.language, "already")
                else:
                    text = g_lang.wrong_num_arguments(
                        user.language
                    ) + t_lang.add_teacher(
                        user.language,
                        "text",
                        bot_username=context.bot.username,
                        title=False,
                    )
                g_fun.send_Msg(context, user, text=text)
        else:
            text = b_lang.no_username(update._effective_user.language_code)
            update.message.reply_text(text)
            return False
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def send_msg_planets(update, context):
    try:
        chat = update._effective_message
        if chat.chat_id > 0:
            user = g_fun.get_user_data(update._effective_user)
            if user:
                if user.is_teacher:
                    user.send_msg_planets(update, context)
            else:
                text = b_lang.no_username(update._effective_user.language_code)
                update.message.reply_text(text)
                return False
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


###################
# STUDENTS COMMANDS


def check_email(update, context):
    try:
        chat = update._effective_message
        user_data = update._effective_user
        if chat.chat_id > 0:
            if cfg.config_files_set:
                user = g_fun.get_user_data(user_data)
                if user:
                    user.check_email(update, context)
                else:
                    text = b_lang.no_username(user_data.language_code)
                    update.message.reply_text(text)
                    return False
            else:
                text = s_lang.not_config_files_set(user.language, context)
                g_fun.send_Msg(context, user, text=text)
    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False


def suggestion(update, context):
    try:
        chat = update._effective_message
        if chat.chat_id > 0:
            user = g_fun.get_user_data(update._effective_user)
            if user:
                user.suggestion(update, context)

    except:
        error_path = f"{inspect.stack()[0][1]} - {inspect.stack()[0][3]}"
        g_fun.print_except(error_path)
        return False
