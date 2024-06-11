from telegram import InlineKeyboardButton as IKButton


def not_env_variable(var):
  return f"Environment variable {var} is not set. The boot was not initialized."


def set_language(user, opt="opt"):
  if opt == "opt":
    return [
      [
        IKButton("ES", callback_data="welcome-es"),
        IKButton("EN", callback_data="welcome-en"),
      ]
    ]
  else:
    return f"<b>{user['first_name']}</b>!!\n\nPara cambiar el idioma del contenido, usa el botón ES-español o EN-inglés.\n\nTo switch content language, press the ES-Spanish or EN-English button."


def welcome(user):
  if user.language == "es":
    return f"Hola {user.telegram_name}, yo soy tu bot."
  else:
    return f"Hello {user.telegram_name}, I am your bot."


def pinned_message(context):
  return f"Para acceder a las opciones de opinar sobre la colaboración de los compañeros, del profesor/a y de los recursos, inicia una conversación en privado con el bot EDUtrack @{context.bot.username} (click en el usuario o buscalo directamente en Telegram).\n\nTo access the options to opine on the collaboration of classmates, teacher and resources, start a private conversation with the EDUtrack @{context.bot.username} bot (click on the user or search it directly in Telegram)."


def file_ready_for_download(lang):
  if lang == "es":
    return "Archivo listo para su descarga."
  else:
    return "File ready for download."


def error_upload_file(lang, file=""):
  if lang == "es":
    return f"Hubo un error al subir el archivo {file}\nPor favor reviselo e inténtalo de nuevo."
  else:
    return (
      f"There was an error uploading the file {file}\nPlease check it and try again."
    )


def ok_upload_file(lang, file=""):
  if lang == "es":
    return f"El archivo {file} se subio correctamente."
  else:
    return f"The file {file} was uploaded correctly"


def email_syntax_error(lang, email):
  if lang == "es":
    return f'El email "{email}" no tiene la sintaxis correcta, asegurate de haberlo escrito correctamente.'
  else:
    return f'The email "{email}" does not have the correct syntax, make sure you typed it correctly.'


def wrong_command_group(lang, context):
  bot_username = context.bot.username
  if lang == "es":
    return f"Lo siento este comando no tiene ninguna función en el Grupo. Hablame en chat privado. @{bot_username}"

  else:
    return (
      f"Sorry this command has no function in the Group. Talk to me on a private chat. @{bot_username}",
    )


def wrong_num_arguments(lang):
  if lang == "es":
    return "La cantidad de argumentos para el comando es incorrecta.\n"
  else:
    return "The number of arguments for the command is incorrect.\n"


def file_not_created(lang):
  if lang == "es":
    return "Lo siento el archivo no pudo ser creado."
  else:
    return "I'm sorry the file couldn't be created."


def linguistic_arf(lang, arf_text):
  if lang == "es":
    if arf_text == "irrecoverable":
      return "Irrecuperable"
    if arf_text == "very_critical":
      return "Muy Crítico"
    if arf_text == "critical":
      return "Crítico"
    if arf_text == "moderate":
      return "Moderado"
    if arf_text == "low":
      return "Bajo"
    if arf_text == "none":
      return "Ninguno"
  else:
    return arf_text.replace("_", " ").capitalize()


def teacher_criteria(lang, criterion):
  if lang == "es":
    if criterion == "T_VOCALIZACION":
      return f"Vocalización"
    if criterion == "T_DOMINIO_TEMA":
      return f"Dominio del tema"
    if criterion == "T_CERCANIA":
      return f"Cercania"
    if criterion == "T_ATENCION_AUDIENCIA":
      return f"Atención a la audiencia"
    if criterion == "T_CLARIDAD_EXPRESIONES":
      return f"Claridad en las expresiones"
    if criterion == "C_CALIDAD_TRANSPARENCIAS":
      return f"Calidad de las transparancias"
    if criterion == "C_CALIDAD_EJEMPLOS":
      return f"Calidad de los ejemplos"
    if criterion == "C_CONTENIDOS_NIVEL":
      return f"Contenidos adaptados al nivel"
  else:
    if criterion == "T_VOCALIZACION":
      return f"Vocalization"
    if criterion == "T_DOMINIO_TEMA":
      return f"Mastery of the subject"
    if criterion == "T_CERCANIA":
      return f"Closeness"
    if criterion == "T_ATENCION_AUDIENCIA":
      return f"Audience Attention"
    if criterion == "T_CLARIDAD_EXPRESIONES":
      return f"Clarity of expressions"
    if criterion == "C_CALIDAD_TRANSPARENCIAS":
      return f"Quality of the transparencies"
    if criterion == "C_CALIDAD_EJEMPLOS":
      return f"Quality of the examples"
    if criterion == "C_CONTENIDOS_NIVEL":
      return f"Contents adapted to the level"


def scale_7_labels(lang, label):
  if lang == 'es':
    if label == "Lousy":
      return "Pésimo"
    if label == "Very Bad":
      return "Muy malo"
    if label == "Bad":
      return "Malo"
    if label == "Normal":
      return "Normal"
    if label == "Good":
      return "Bueno"
    if label == "Very Good":
      return "Muy Bueno"
    if label == "Excellent":
      return "Excelente"
  else:
    return label


def scale_7(lang, callback_data):
  back_menu = "-".join(callback_data.split("-")[:-1])
  if lang == "es":
    return [
      [
        IKButton("Pésimo/a", callback_data=callback_data + "-s_0"),
        IKButton("Muy malo/a", callback_data=callback_data + "-s_1"),
        IKButton("Malo/a", callback_data=callback_data + "-s_2"),
      ],
      [IKButton("Normalito", callback_data=callback_data + "-s_3")],
      [
        IKButton("Bueno/a", callback_data=callback_data + "-s_4"),
        IKButton("Muy bueno/a", callback_data=callback_data + "-s_5"),
        IKButton("Excelente", callback_data=callback_data + "-s_6"),
      ],
      [IKButton("Regresar", callback_data=back_menu)],
    ]
  else:

    return [
      [
        IKButton("Lousy", callback_data=callback_data + "-s_0"),
        IKButton("Very Bad", callback_data=callback_data + "-s_1"),
        IKButton("Bad", callback_data=callback_data + "-s_2"),
      ],
      [IKButton("Normal", callback_data=callback_data + "-s_3")],
      [
        IKButton("Good", callback_data=callback_data + "-s_4"),
        IKButton("Very Good", callback_data=callback_data + "-s_5"),
        IKButton("Excellent", callback_data=callback_data + "-s_6"),
      ],
      [IKButton("Back", callback_data=back_menu)],
    ]


def unauthorized_user(lang, context):
  if lang == "es":
    return f"Lo siento no eres un usuario autorizado para crear grupos con EDUtrack {context.bot.first_name}"
  else:
    return f"Sorry you are not an authorized user to create groups with EDUtrack {context.bot.first_name}"


def change_language(lang):
  if lang == "es":
    return f"He cambiado tu idioma a <b>Español.</b>"
  else:
    return f"I changed your language to <b>English.</b>"


back_text = {"es": "Regresar", "en": "Back"}

help_send_manual = {
  "es": "files/guides/ES/EDUtrack_manual_estudiante.pdf",
  "en": "files/guides/EN/EDUtrack_student_manual.pdf",
}


def help(lang, context):
  bot_username = context.bot.username
  if lang == "es":
    return f"El bot con el que se estarás trabajando en esta asignatura soy yo @{bot_username}, en el manual solo se usa @EDUTrack_bot como ejemplo."
  else:
    return f"The bot you will be working with in this subject is me @{bot_username}, the manual only uses EDUTrack_bot as an example."

def change_profile_text(user,context):
  if user.language == "es":
    if user.is_teacher:
      return f"Te encuentras en modo docente. Escribe el comando /menu para ver las opciones."
    else:
      return f"Te encuentras en modo estudiante. Escribe el comando /menu para ver las opciones."
  else:
    if user.is_teacher:
      return f"You are in teacher mode. Type the command /menu to see the options."
    else:
      return f"You are in student mode. type the command /menu to see the options."
    