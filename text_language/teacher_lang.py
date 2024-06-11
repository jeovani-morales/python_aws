from telegram import InlineKeyboardButton as IKBtn

lt = "&lt;"
gt = "&gt;"


def welcome_text(lang, context, action):
  bot_username = context.bot.username
  text = ""
  if lang == "es":
    if action == "short":
      return (
        "Escribe el comando /menu para ver las opciones con las que podemos trabajar."
      )
    if action == "long":
      text = "Hemos terminado de configurar la asignatura.\n\n"
    return f"{text}Bienvenido a EDUtrack <b>{bot_username}</b>. Te ayudaré en esta asignatura manteniendote informado de los estudiantes que están en riesgo de fracaso academico de forma semanal.\n\nAdemás de llevar un control de la comunicación en Telegram de los estudiantes, te proporcionaré informes sobre la opinión colectiva sobre la asignatura recogida mediante EDUtrack.\nMis comandos son:\n\n/menu\n Te mostraré las opciones con las que podemos trabajar juntos.\n\n/change_language\nTe ayudaré a cambiar el idioma en que te muestro los contenidos. Las opciones actuales son Inglés y Español.\n\n/help\nTe informaré sobre el menú de opciones. También podrás acceder al manual de usuario."
  else:
    if action == "short":
      return "Type command /menu to see the options with which we can work together."
    if action == "long":
      text = "We've finished configuring the subject.\n\n"
    return f"{text}<b>{bot_username}</b>, welcome to EDUtrack. I will help you in this course by keeping you informed of students who are at risk of academic failure on a weekly basis.\n\nIn addition to keeping track of students' Telegram communication, I will provide you with reports on the collective opinion on the course collected through EDUtrack.\nMy commands are:\n\n/menu\n I will show you the options with which we can work together.\n\n/change_language\n I will help you switch the language in which I show you the contents. The current options are English and Spanish.\n\n/help\nI'll inform you about the options menu. You will also be able to access the user manual."


def config_files(lang, action, file_name="", elements="", context=""):
  if lang == "es":
    if action == "download":
      bot_username = context.bot.username
      return f"<b>Asistente para la configuración de la asignatura.</b>\n\nBienvenido a EDUtrack <b>{bot_username}</b>. Antes de usar EDUtrack debes terminar de configurar la asignatura. Descarga y edita estos archivos. Cuando los tengas listos <b>enviámelos con el mismo nombre.</b>"
    if action == "ready_one":
      return f"El archivo se ha subido correctamente. Aún falta por subir el archivo <b>{file_name}</b> para finalizar la configuración."
    if action == "replace":
      return f"El archivo se ha subido correctamente."
    if action == "no_set_up":
      return "La asignatura aún no está configurada por completo."
    if action == "header_error":
      return f"El archivo debe contener al menos las siguientes cabeceras de columna:\n{elements}\n\nRevisa el formato del archivo."
    if action == "missing_file":
      file_name = "estudiantes" if file_name == "students" else "actividades"
      return f"El archivo de configuración <b>{file_name}</b> aún no se ha cargado. Recuerda que lo debes subir con el mismo nombre."
    if action == "exists_in_DB":
      if "students" in file_name:
        return f"<b>ARCHIVO EXISTENTE</b>\nLa seccion <b>estudiantes</b> ya existe en la base de datos.\nPara agregar más <b>{elements}</b> renombra el archivo como <b>add_{file_name}</b>.\n\nPara reemplazar todo, renombra el archivo como <b>replace_{file_name}</b>.\nSi utilizas está opción, la sección de calificaciones también se borrará, eliminando todas las calificaciones cargadas previamente."
      else:
        #  The activity file does not allow you to add activities to maintain the correct grading scheme.
        return f"<b>ARCHIVO EXISTENTE</b>\nLa seccion <b>actividades</b> ya existe en la base de datos.\nPara reemplazar las actividades, renombra el archivo como <b>replace_{file_name}</b>.\nSi utilizas está opción, la sección de calificaciones también se borrará, eliminando todas las calificaciones cargadas previamente."
    if action == "add_ready":
      if elements == "students":
        return f"Se han gregado con éxito los estudiantes."
      elif elements == "activities":
        return f"Se han aregado con exito las actividades."
    if action == "add_all_exists":
      return (
        f"Todos los elementos ya existen en la base de datos, no se agrego ninguno."
      )
    if action == "add_duplicates":
      return f"Los siguientes elementos están duplicados:\n{elements}"
    if action == "add_no_duplicates":
      return f"\n\nLos demás elementos se agregaron correctamente."

  else:
    if action == "download":
      bot_username = context.bot.username
      return f"<b>Course setup wizard.</b>\n\nWelcome to EDUtrack <b>{bot_username}</b>. Before using EDUtrack you must finish configuring the course. Download and edit these files. When done, send them to me <b>keeping the file names.</b>"
    if action == "ready_one":
      return f"The file has been uploaded successfully. The <b>{file_name}</b> configuration file has yet to be uploaded."
    if action == "replace":
      return f"The file has been uploaded successfully."
    if action == "no_set_up":
      return "The subject is not yet fully configured."
    if action == "header_error":
      return f"The file must contain at least the following headers:\n{elements}\n\nCheck the file format."
    if action == "missing_file":
      return f"Configuration file <b>{file_name}</b> is not uploaded. Remember to keep the file name."
    if action == "exists_in_DB":
      elements = "students" if "students" in file_name else "activities"
      return f"<b>EXISTING FILE</b>\nSection <b>{elements}</b> already exists in the database.\nTo add more <b>{elements}</b> rename the file to <b>add_{file_name}</b>.\n\nTo replace everything, rename the file to <b>replace_{file_name}</b>.\nIf you use the latter option, the grades section will also be cleared, deleting all previously loaded grades."
    if action == "add_ready":
      return f"Successfully added {elements}"
    if action == "add_all_exists":
      return f"All the elements already exist in the database, none were added."
    if action == "add_duplicates":
      return f"The following items are duplicated:{elements}"
    if action == "add_no_duplicates":
      return f"\n\nThe other elements were added correctly."


def config_files_activities(lang, action, elements=""):
  if lang == "es":
    print(len(elements.split("\n")))
    if action == "no_main_category":
      return "<b>FALTA LA CATEGORÍA SUBJECT</b>\n\nTodos los <b>'_id' calificables</b> deben tener una categoría. Si el <b>'_id'</b> es una categoría superior (no tiene categoría padre), su categoría debe ser <b>'SUBJECT'</b>."
    elif action == "undefined_category":
      msg = "Todas las categorías deben estar definidas en la columna <b>'_id'</b> y tener un peso y categoría establecidos."
      if len(elements.split("\n")) == 1:
        return f"<b>CATEGORÍA NO DEFINIDA</b>\n\nLa categoría {elements} no está definida.\n\n{msg}"
      elif len(elements.split("\n")) > 1:
        return f"<b>CATEGORÍAS NO DEFINIDAS</b>\n\nLas siguientes categorías no están definidas:\n\n{elements}\n\n{msg}"
    elif action == "weightless":
      if len(elements.split("\n")) == 1:
        return f"<b>CATEGORIA SIN PESO</b>\n\nLa categoría <b>{elements}</b> no tiene definido el peso."
      elif len(elements.split("\n")) > 1:
        return f"<b>CATEGORIAS SIN PESO</b>\n\nLas siguientes categorías no tienen definido el peso:\n\n<b>{elements}</b>"
    elif action == "no_parent_cat":
      if len(elements.split("\n")) == 1:
        return f"<b>SIN CATEGORIA PADRE</b>\n\nLa categoría <b>{elements}</b> no tiene definida su categoria padre."
      elif len(elements.split("\n")) > 1:
        return f"<b>CATEGORIAS SIN PESO</b>\n\nLas siguientes categorías no tienen definida la categoria padre:\n\n</b>{elements}</b>"

  else:
    if action == "no_main_category":
      return "<b>SUBJECT CATEGORY MISSING</b>\n\nAll <b>qualifying '_id'</b> must have a category. If <b>'_id'</b> is a higher category (doesn't have a parent category) its category must be <b>'SUBJECT'</b>."
    elif action == "undefined_category":
      msg = "All categories must be defined in column <b>'_id'</b> and have an established weight and category."
      if len(elements.split("\n")) == 1:
        return f"<b>UNDEFINED CATEGORY</b>\n\nThe {elements} category is not defined.\n\n{msg}"
      elif len(elements.split("\n")) > 1:
        return f"<b>UNDEFINED CATEGORIES</b>\\nnThe following categories are not defined:\n\n{elements}\n\n{msg}"
    elif action == "weightless":
      if len(elements.split("\n")) == 1:
        return f"<b>WEIGHTLESS CATEGORY</b>\n\nThe <b>{elements}</b> category has no defined weight."
      elif len(elements.split("\n")) > 1:
        return f"<b>WEIGHTLESS CATEGORIES</b>\n\nThe following categories have no defined weight:\n\n<b>{elements}</b>"
    elif action == "no_parent_cat":
      if len(elements.split("\n")) == 1:
        return f"<b>NO PARENT CATEGORY</b>\n\nThe <b>{elements}</b> category has not defined its parent category."
      elif len(elements.split("\n")) > 1:
        return f"<b>NO PARENT CATEGORY</b>\n\nThe following categories don't have the parent category defined:\n\n<b>{elements}</b>"


def add_teacher(lang, action, username="", bot_username="", title=True):
  if lang == "es":
    Title = "<b>AGREGAR DOCENTE</b>\n" if title else ""
    if action == "text":
      return f"{Title}Solicite al nuevo profesor/a interactuar con el bot @{bot_username}.\nPosteriormente utiliza el comando /add_teacher {lt}username{gt} {lt}email{gt}.\n\n<b>EJEMPLO:</b>\n/add_teacher teacher_username email@teacher.com"
    if action == "sucess":
      return f"{Title}Se ha registrado el profesor/a {username} satisfactoriamente."
    if action == "not_found":
      return (
        f"{Title}El profesor/a {username} no ha interactuado con el bot."
        + "\n\n"
        + add_teacher(lang, "text", bot_username=bot_username, title=False)
      )
    if action == "already":
      return f"{Title}El profesor/a ya se encuentra registrado."
  else:
    Title = "<b>ADD TEACHER</b>\n" if title else ""
    if action == "text":
      return f"{Title}Ask the new teacher to interact with the bot @{bot_username}.\nThen use the command /add_teacher {lt}username{gt} {lt}email{gt}.\n\n<b>EXAMPLE:</b>\n/add_teacher teacher_username email@teacher.com"
    if action == "sucess":
      return f"{Title}The teacher {username} has been successfully registered."
    if action == "not_found":
      return (
        f"{Title}The teacher {username} has not interacted with the bot."
        + "\n\n"
        + add_teacher(lang, "text", bot_username=bot_username, title=False)
      )
    if action == "already":
      return f"{Title}The teacher is already registered."


##### MENUS ###################
def main_menu(lang):
  if lang == "es":
    text = "<b>MENU DOCENTE</b>\nSelecciona una opción:"
    opt = [
      [
        IKBtn("Actividades", callback_data="t_menu-act"),
        IKBtn("Estudiantes", callback_data="t_menu-stu"),
      ],
      [IKBtn("Generar Reportes", callback_data="t_menu-reports")],
      [IKBtn("Activar Evaluaciones", callback_data="t_menu-activate_eva")],
      [IKBtn("Enviar mensaje a los planetas", callback_data="t_menu-msg")],
      [IKBtn("Ser Estudiante", callback_data="t_menu-change_profile")],
      # [IKBtn("ON/OFF registro en planetas", callback_data="t_menu-reg_planet")],
    ]
  else:
    text = "<b>TEACHER MENU</b>\nSelect an option:"
    opt = [
      [
        IKBtn("Activities", callback_data="t_menu-act"),
        IKBtn("Students", callback_data="t_menu-stu"),
      ],
      [IKBtn("Generate Reports", callback_data="t_menu-reports")],
      [IKBtn("Activate Evaluations", callback_data="t_menu-activate_eva")],
      [IKBtn("Send message to the planets", callback_data="t_menu-msg")],
      [IKBtn("Be a Student", callback_data="t_menu-change_profile")],
      # [IKBtn("ON/OFF planet registry", callback_data="t_menu-reg_planet")],
    ]
  return (text, opt)


def title_file(lang, title):
  if lang == "es":
    if title == "STUDENTS_FORMAT":
      return "FORMATO DE ESTUDIANTES"
    elif title == "STUDENTS REGISTERED":
      return "ESTUDIANTES REGISTRADOS"
    elif title == "ALL ACTIVITIES":
      return "TODAS LAS ACTIVIDADES"
    elif title == "QUALIFYING ACTIVITIES":
      return "ACTIVIDADES CALIFICABLES"
    elif title == "RESOURCES ACTIVITIES":
      return "RECURSOS"
    elif title == "GRADE REPORT":
      return "REPORTE DE CALIFICACIONES"
    elif title == "LIGUISTIC REPORT ACADEMIC RISK FACTOR":
      return "REPORTE LINGÜISTICO DEL FACTOR DE RIESGO ACADEMICO"
    elif title == "STUDENTS AT ACADEMIC RISK REPORT":
      return "REPORTE DE ESTUDIANTES EN RIESGO ACADÉMICO"
    elif title == "MEETINGS PARTICIPATION REPORT":
      return "REPORTE DE LA PARTICIPACION EN LOS MEETINGS"
    elif title == "OUT OF MEETINGS PARTICIPATION REPORT":
      return "REPORTE DE PARTICIPACION FUERA DE LOS MEETINGS"
    elif title == "GENERAL MESSAGE REPORT":
      return "REPORTE GENERAL DE MENSAJES"
    elif title == "TEACHER EVALUATION REPORT":
      return "REPORTE DE LA EVALUACION DOCENTE"
    elif title == "RESOURCES EVALUATION REPORT":
      return "REPORTE DE LA EVALUACION DE RECURSOS"
    elif title == "CLASSMATES EVALUATION REPORT IN MEETINGS":
      return "REPORTE DE LA EVALUACION ENTRE COMPAÑEROS EN LOS MEETINGS"
    elif title == "AUTOEVALUATION REPORT":
      return "REPORTE DE AUTOEVALUACION"

  else:
    return title


### MENU ACADEMIC ACTIVITIES  ####################
def menu_act(lang):
  if lang == "es":
    text = "<b>ACTIVIDADES</b>\nSelecciona una opción:"
    opt = [
      [
        IKBtn("Ver Lista", callback_data="t_menu-act-view"),
        IKBtn("Calificar", callback_data="t_menu-act-grade"),
      ],
      [
        IKBtn("Reemplazar", callback_data="t_menu-act-replace"),
        IKBtn("Modificar", callback_data="t_menu-act-modify"),
      ],
      [IKBtn("Activar Actividad", callback_data="t_menu-act-active")],
      [
        IKBtn("Atrás", callback_data="t_menu-back"),
      ],
    ]
  else:
    text = "<b>ACTIVITIES</b>\nSelect an option:"
    opt = [
      [
        IKBtn("View List", callback_data="t_menu-act-view"),
        IKBtn("Grade", callback_data="t_menu-act-grade"),
      ],
      [
        # IKBtn("Add", callback_data="t_menu-act-add"),
        IKBtn("Replace", callback_data="t_menu-act-replace"),
        IKBtn("Modify", callback_data="t_menu-act-modify"),
      ],
      [IKBtn("Activate Activity", callback_data="t_menu-act-active")],
      [IKBtn("Back", callback_data="t_menu-back")],
    ]
  return (text, opt)


def menu_act_view(lang):
  if lang == "es":
    text = "<b>VER LISTA DE ACTIVIDADES</b>\nSelecciona una opción:"
    opt = [
      [IKBtn("Todas las Actividades", callback_data="t_menu-act-view-all")],
      [
        IKBtn(
          "Actividades Calificables",
          callback_data="t_menu-act-view-qualifying",
        )
      ],
      [IKBtn("Recursos", callback_data="t_menu-act-view-resources")],
      [IKBtn("Atrás", callback_data="t_menu-act")],
    ]
  else:
    text = "<b>VIEW ACTIVITIES LIST</b>\nSelect an option:"
    opt = [
      [IKBtn("All Activities", callback_data="t_menu-act-view-all")],
      [IKBtn("Qualifying Activities", callback_data="t_menu-act-view-qualifying")],
      [IKBtn("Back", callback_data="t_menu-act")],
    ]
  return (text, opt)


def menu_act_grade(lang, action, elements="", num_elements="", title=True):
  if lang == "es":
    Title = "<b>CALIFICAR</b>\n" if title else ""
    if action == "menu":
      text = f"{Title}Selecciona una opción:"
      opt = [
        [IKBtn("Subir archivo", callback_data="t_menu-act-grade-upload")],
        [IKBtn("Utilizar comando", callback_data="t_menu-act-grade-cmd")],
        [IKBtn("Atrás", callback_data="t_menu-act")],
      ]
      return (text, opt)
    elif action == "upload":
      return f"{Title}Descarga este archivo como base para crear el archivo de calificaciones. Envialo con el mismo nombre para cargar las calificaciones."
    elif action == "cmd":
      return f"{Title}Escribe el comando\n<code>/grade_activity {lt}id_actividad{gt} {lt}email_estudiante{gt} {lt}calificación{gt}</code>;\n\nCada estudiante debe separarse con el signo punto y coma ';' salvo el último\n\nEjemplo:\n<code>/grade_activity Prueba_1\nejemplo@correo.ugr.es 8.5;\nejemplo2@gmail.com 9.6;\nejemplo3@hotmail.com 9</code>"

    elif action == "unregistered_stu":
      if num_elements == 1:
        return f"{Title}El estudiante <b>{elements}</b> no se encuentra registrado."
      else:
        return f"{Title}Los siguientes <b>{num_elements}</b> estudiantes no se encuentran registrados:\n<b>{elements}</b>"
    elif action == "unregistered_act":
      if num_elements == 1:
        return f"{Title}La actividad <b>{elements}</b> no se encuentra registrada."
      else:
        return f"{Title}Las siguientes <b>{num_elements}</b> actividades no se encuentran registradas:\n<b>{elements}</b>"
    elif action == "duplicated_stu":
      if num_elements == 1:
        return f"{Title}El estudiante <b>{elements}</b> se encuentra duplicado."
      else:
        return f"{Title}Los siguientes <b>{num_elements}</b> estudiantes se encuentran duplicados:\n<b>{elements}</b>"
    elif action == "duplicated_act":
      if num_elements == 1:
        return (
          f"{Title}La actividad <b>{elements}</b> se encuentra duplicada en el archivo."
        )
      else:
        return f"{Title}Las siguientes <b>{num_elements}</b> actividades se encuentran duplicadas en el archivo:\n<b>{elements}</b>"
    elif action == "no_students":
      return f"{Title}No se pudo registrar ningún estudiante en la base de datos."
    elif action == "no_activities":
      return f"{Title}No se pudo registrar ninguna actividad en la base de datos."
    elif action == "no_arguments":
      return (
        f"{Title}El comando no tiene los argumentos necesarios.\n\n"
        + menu_act_grade(lang, "cmd", title=False)
      )
    elif action == "grades_error":
      return f"{Title}Se encontro un problema en los siguientes registros:\n{elements}"
    elif action == "sucess":
      return f"{Title}Se registraron las calificaciones."
    elif action == "no_registration":
      return f"{Title}No se registro ninguna calificación."

  else:
    Title = "<b>GRADE</b>\n" if title else ""
    if action == "menu":
      text = f"{Title}Select an option:"
      opt = [
        [IKBtn("Upload File", callback_data="t_menu-act-grade-upload")],
        [IKBtn("Use Command", callback_data="t_menu-act-grade-cmd")],
        [IKBtn("Back", callback_data="t_menu-act")],
      ]
      return (text, opt)
    elif action == "upload":
      return f"{Title}Download this file as a basis for creating the grade file. Send it with the same name to load the grades."
    elif action == "cmd":
      return f"{Title}Type the command\n<code>/grade_activity {lt}id_activity{gt} {lt}student email{gt} {lt}grade{gt}</code>;\n\nEach student is separated with the semicolon char ';' except the last one\n\nExample:\n<code>/grade_activity Test_1\nexample@correo.ugr.es 8.5;\nexample2@gmail.es 9.6;\nexample3@hotmail.es 9</code>"
    elif action == "unregistered_stu":
      if num_elements == 1:
        return f"{Title}The student <b>{elements}</b> is not registered."
      else:
        return f"{Title}The following students are not registered:\n<b>{elements}</b>"
    elif action == "unregistered_act":
      if num_elements == 1:
        return f"{Title}The activity <b>{elements}</b> is not registered."
      else:
        return f"{Title}The following activities are not registered:\n<b>{elements}</b>"
    elif action == "duplicated_stu":
      if num_elements == 1:
        return f"{Title}The student <b>{elements}</b> is duplicated in the file."
      else:
        return f"{Title}The following <b>{num_elements}</b> students are duplicated in the file:\n<b>{elements}</b>"
    elif action == "duplicated_act":
      if num_elements == 1:
        return f"{Title}The activity <b>{elements}</b> is duplicated in the file."
      else:
        return f"{Title}The following <b>{num_elements}</b> activities are duplicated in the file:\n<b>{elements}</b>"
    elif action == "no_students":
      return f"{Title}No students could be registered in the database."
    elif action == "no_activities":
      return f"{Title}No activities could be registered in the database."
    elif action == "no_arguments":
      return (
        f"{Title}The command does not have the necessary arguments.\n\n"
        + menu_act_grade(lang, "cmd", title=False)
      )
    elif action == "grades_error":
      return f"{Title}A problem was found in the following records:\n{elements}"
    elif action == "sucess":
      return f"{Title}The grades were registered."
    elif action == "no_registration":
      return f"{Title}No grades were recorded."


def menu_act_replace(lang):
  if lang == "es":
    return "<b>REEMPLAZAR ACTIVIDADES:</b>\nPara reemplazar el archivo de configuración de actividades, sube un archivo con el nombre <b>replace_activities_format.csv</b> con el formato <b>activities_format</b>.\n\n<b>Nota: Ten en cuenta que hacer esto reemplazara la base de datos de calificaciones también</b>."
  else:
    return "<b>REPLACE ACTIVITIES:</b>\nTo replace the activity configuration file, upload a file named <b>replace_activities_format.csv</b> with format <b>activities_format</b>.\n\n<b>Note: Please note that doing this will replace the grades database as well</b>."


def menu_act_modify(lang, headers=""):
  if lang == "es":
    return f"<b>MODIFICAR ACTIVIDAD:</b>\nPara modificar una actividad escribe el comando\n<code>/modify_activity {lt}id actividad{gt} {lt}campo a modificar{gt} {lt}nuevo contenido{gt}</code>\n\nLos campos que puedes modificar son:\n{headers}\n\n<b>Ejemplos:</b>\n<code>/modify_activity GLOSARIO week 4</code> (Modifica la semana de la actividad)\n\n<code>/modify_activity GLOSARIO name Glosario del tema 2</code> (Modifica el nombre de la actividad)"
  else:
    return f"<b>MODIFY ACTIVITY:</b>\nTo modify an activity, type command\n<code>/modify_activity {lt}id activity{gt} {lt}field to modify{gt} {lt}new content{gt}</code>\n\nThe fields you can modify are:\n{headers}\n\n<b>Example:</b>\n<code>/modify_activity GLOSSARY week 4</code> (modify the activity week).\n\n<code>/modify_activity GLOSSARY name Topic 2 Glossary</code> (modifies the activity name)"


def menu_act_delete(lang):
  if lang == "es":
    return f"<b>ELIMINAR ACTIVIDAD:</b>\nPara eliminar una actividad, escribe el comando <code>/delete_activity {lt}id actividad{gt}</code>\n\n<b>Ejemplo:</b>\n<code>/delete_activity GLOSARIO</code>"
  else:
    return f"<b>DELETE ACTIVITY:</b>\nTo delete an activity, type command <code>/delete_activity {ly}id activity{gt}</code>\n\n<b>Example:</b>\n<code>/delete_activity GLOSSARY</code>"


def menu_act_active(lang, action, activities=""):
  if lang == "es":
    if action == "text":
      return f"<b>ACTIVAR ACTIVIDAD:</b>\nPara activar una actividad escribe el comando\n<code>/active_activity {lt}id actividad{gt}</code>\n\n<b>Ejemplo:</b>\n\n<code>/active_activity GLOSARIO</code>"
    elif action == "activities":
      return f"Los id de las actividades inactivas son:\n\n{activities}"
    elif action == "no_arguments":
      return f"Después del comando debes escribir el id de una actividad no activa."
    elif action == "processing":
      return f"Estoy activando <b>{activities}</b> y recalculando la evaluación de los estudiantes. Te enviare un mensaje cuando termine."
    elif action == "end":
      return f"He terminado de activar la actividad <b>{activities}</b>"
  else:
    if action == "text":
      return f"<b>ACTIVE ACTIVITY:</b>\nTo activate an activity type the command:\n<code>/active_activity {lt}id activity{gt}</code>\n\n<b>Example:</b>\n<code>/active_activity GLOSSARY</code>"
    elif action == "activities":
      return f"The id's of inactive activities are:\n\n{activities}"
    elif action == "no_arguments":
      return f"After the command you must type the id of a non active activity."
    elif action == "processing":
      return f"I'm activating <b>{activities}</b> and recalculating the students evaluation. I'll send you a message when I'm done."
    elif action == "end":
      return f"I've finished activating the <b>{activities}</b> activity."


### MENU ACADEMIC STUDENTS  ####################
def menu_stu(lang):
  if lang == "es":
    text = "<b>ESTUDIANTES:</b>\nSelecciona una opción:"
    opt = [
      [
        IKBtn("Ver lista", callback_data="t_menu-stu-view"),
        IKBtn("Agregar", callback_data="t_menu-stu-add"),
      ],
      [
        IKBtn("Modificar", callback_data="t_menu-stu-modify"),
        IKBtn("Eliminar", callback_data="t_menu-stu-delete"),
      ],
      [IKBtn("Atrás", callback_data="t_menu-back")],
    ]
  else:
    text = "<b>STUDENTS:</b>\nSelect an option:"
    opt = [
      [
        IKBtn("View List", callback_data="t_menu-stu-view"),
        IKBtn("Add", callback_data="t_menu-stu-add"),
      ],
      [
        IKBtn("Modify", callback_data="t_menu-stu-modify"),
        IKBtn("Delete", callback_data="t_menu-stu-delete"),
      ],
      [IKBtn("Back", callback_data="t_menu-back")],
    ]
  return (text, opt)


def menu_stu_view(lang, action="menu"):
  if lang == "es":
    if action == "menu":
      text = "<b>VER LISTA DE ESTUDIANTES:</b>\nSelecciona una opción:"
      opt = [
        [IKBtn("Archivo students_format", callback_data="t_menu-stu-view-file")],
        [IKBtn("Estudiantes registrados", callback_data="t_menu-stu-view-reg")],
        [IKBtn("Atrás", callback_data="t_menu-stu")],
      ]
    elif action == "no_elements_registered":
      return "No hay estudiantes registrados."
  else:
    if action == "menu":
      text = "<b>VIEW STUDENTS LIST:</b>\nSelect an option:"
      opt = [
        [IKBtn("students_format file", callback_data="t_menu-stu-view-file")],
        [IKBtn("Registered students", callback_data="t_menu-stu-view-reg")],
        [IKBtn("Back", callback_data="t_menu-stu")],
      ]
    elif action == "no_elements_registered":
      return "No students are registered."
  return (text, opt)


def menu_stu_add(lang):
  if lang == "es":
    return "<b>AGREGAR ESTUDIANTE:</b>\nPara agregar más estudiantes sube un archivo con el nombre <b>add_students_format.csv</b> con el formato de <b>students_format</b>."
  else:
    return "<b>ADD STUDENT:</b>To add more students upload a file with the name <b>add_students_format.csv</b> with the format of <b>students_format</b>."


def menu_stu_modify(lang, action, headers="", data=""):
  if lang == "es":
    Title = "<b>MODIFICAR ESTUDIANTE:</b>\n"
    if action == "cmd":
      return f"{Title}Los campos que puedes modificar son:\n{headers}\n\nPara modificar el nombre de un estudiante escribe el comando:\n<code>/modify_student {lt}email{gt} {lt}campo a modificar{gt} {lt}nuevo contenido{gt}</code>\n\n<b>Ejemplo:</b>\n<code>/modify_student ejemplo@correo.ugr.es first_name David</code>\n(Modifica el nombre del estudiante por David).\n\nPara agregar o modificar el correo de un estudiante, escribe el comando:\n<code>/modify_student {lt}username{gt} {lt}nuevo_email{gt}</code>\n<b>Ejemplo:</b>\n<code>/modify_student David_2020 nuevo@correo.ugr.es</code>\n (Modifica o agrega el nuevo email al estudiante con el username <b>David_2020</b>)."
    elif action == "unregistered_email":
      return f"{Title}El email {data} no se encuentra registrado."
    elif action == "unregistered_user":
      return f"{Title}El username {data} no se encuentra registrado."
    elif action == "column_error":
      return f"{Title}El campo <b>{data}</b> que deseas modificar no es correcto."
    elif action == "success":
      return f"{Title}Se ha modificado el campo {data} con éxito."
  else:
    Title = "<b>MODIFY STUDENT:</b>\n"
    if action == "cmd":
      return f"{Title}The fields you can modify are:\n{headers}\n\nTo change a student's name type the command:\n<code>/modify_student {lt}email{gt} {lt}field to modify{gt} {lt}new content{gt}</code>\n\n<b>Example:</b>\n<code>/modify_student example@correo.ugr.es first_name David</code>\n(modify the student's first name to David).\n\nTo add or modify a student's email, type the command:\n<code>/modify_student {lt}username{gt} {lt}new_email{gt}\n</code><b>Example:</b>\n<code>/modify_student David_2020 new_email@correo.ugr.es</code>\n(Modify or add the new email to the student with the username <b>David_2020</b>)."
    elif action == "unregistered_email":
      return f"{Title}The email {data} is not registered."
    elif action == "unregistered_user":
      return f"{Title}The username {data} is not registered."
    elif action == "column_error":
      return f"{Title}The <b>{data}</b> field you want to modify is not correct."
    elif action == "success":
      return f"{Title}The {data} field has been modified successfully."


def menu_stu_delete(lang):
  if lang == "es":
    return f"<b>ELIMINAR ESTUDIANTE:</b>\nPara eliminar un estudiante escribe el comando\n<code>/delete_student {lt}email{gt}</code>\n\n<b>Ejemplo:</b>\n<code>/delete_student ejemplo@correo.ugr.es</code>"
  else:
    return f"<b>DELETE STUDENT:</b>\nTo delete a student, type command\n<code>/delete_student {lt}email{gt}</code>\n\n<b>Example:</b>\n<code>/delete_student example@correo.ugr.es</code>"


### MENU ACADEMIC REPORTS  ####################
def menu_reports(lang):
  if lang == "es":
    text = "<b>REPORTES:</b>\nSelecciona una opción:"
    opt = [
      [IKBtn("Calificaciones", callback_data="t_menu-reports-grades")],
      [IKBtn("Factor de Riesgo Académico", callback_data="t_menu-reports-ARF")],
      [IKBtn("Meetings", callback_data="t_menu-reports-meetings")],
      [IKBtn("Evaluación docente", callback_data="t_menu-reports-eva_teacher")],
      [IKBtn("Evaluación de recursos", callback_data="t_menu-reports-eva_resources")],
      [IKBtn("Eva. de compañeros", callback_data="t_menu-reports-eva_p2p")],
      [IKBtn("Autoevaluación", callback_data="t_menu-reports-autoeva")],
      [IKBtn("Atrás", callback_data="t_menu-back")],
    ]
  else:
    text = "<b>REPORTS:</b>\nSelect an option:"
    opt = [
      [IKBtn("Grades", callback_data="t_menu-reports-grades")],
      [IKBtn("Academic Risk Factor", callback_data="t_menu-reports-ARF")],
      [IKBtn("Meetings", callback_data="t_menu-reports-meetings")],
      [IKBtn("Teacher Evaluation", callback_data="t_menu-reports-eva_teacher")],
      [IKBtn("Resource Evaluation", callback_data="t_menu-reports-eva_resources")],
      [IKBtn("Peer evaluation", callback_data="t_menu-reports-eva_p2p")],
      [IKBtn("Autoevaluation", callback_data="t_menu-reports-autoeva")],
      [IKBtn("Back", callback_data="t_menu-back")],
    ]
  return (text, opt)


def menu_report_arf(lang):
  if lang == "es":
    text = "<b>REPORTE FACTOR DE RIESGO ACADEMICO:</b>\nSelecciona una opción:"
    opt = [
      [IKBtn("Factor lingüístico", callback_data="t_menu-reports-ARF-ling")],
      [IKBtn("Estudiantes en riesgo", callback_data="t_menu-reports-ARF-risk")],
      [IKBtn("Atrás", callback_data="t_menu-reports")],
    ]
  else:
    text = "<b>ACADEMIC RISK FACTOR REPORT:</b>\nSelect an option:"
    opt = [
      [IKBtn("Linguistic factor", callback_data="t_menu-reports-ARF-ling")],
      [IKBtn("Students at risk", callback_data="t_menu-reports-ARF-risk")],
      [IKBtn("Back", callback_data="t_menu-reports")],
    ]
  return (text, opt)


def menu_report_meeting(lang):
  if lang == "es":
    text = "<b>REPORTE DE MEETINGS:</b>\nSelecciona una opción:"
    opt = [
      [IKBtn("Asistencia", callback_data="t_menu-reports-meetings-att")],
      [IKBtn("Mensajes por meeting", callback_data="t_menu-reports-meetings-meet")],
      [
        IKBtn("Mensajes fuera de meetings", callback_data="t_menu-reports-meetings-out")
      ],
      [IKBtn("General de mensajes", callback_data="t_menu-reports-meetings-general")],
      [IKBtn("Atrás", callback_data="t_menu-reports")],
    ]
  else:
    text = "<b>MEETINGS REPORT:</b>\nSelect an option:"
    opt = [
      [IKBtn("Attendance", callback_data="t_menu-reports-meetings-att")],
      [IKBtn("Messages per meeting", callback_data="t_menu-reports-meetings-meet")],
      [IKBtn("Messages out of meetings", callback_data="t_menu-reports-meetings-out")],
      [IKBtn("General messages", callback_data="t_menu-reports-meetings-general")],
      [IKBtn("Back", callback_data="t_menu-reports")],
    ]
  return (text, opt)


def menu_report_meeting_msgs(lang):
  if lang == "es":
    return "<b>REPORTE DE MENSAJES POR MEETING:</b>\nSelecciona una opción:"
  else:
    return "<b>MESSAGE REPORT PER MEETING:</b>\nSelect an option:"


def report_peer_eva(lang, action, data=False):
  if lang == "es":
    Title = "<b>Reporte de evaluación de compañeros</b>\n\n"
  else:
    Title = "<b>Peer evaluation report</b>"
  if action == "all_students":
    if lang == "es":
      return f"{Title}Estudiantes registrados {data['num_reg_students']}. El {data['pct_evaluators']}% ({data['num_evaluators']}) ha evaluado a sus compañeros."
    else:
      return f"{Title}Registered students {num_reg_students}. The {pct_evaluators}% ({num_evaluators}) have evaluated their peers."
  elif action == "missing":
    if lang == "es":
      return f"{Title}Estudiantes registrados {data['num_reg_students']}. El {data['pct_evaluators']}% ({data['num_evaluators']}) ha evaluado a sus compañeros. A continuación la lista de estudiantes que no han evaluado a sus compañeros.\n\n{data['no_evaluators_names']}"
    else:
      return f"{Title}Registered students {num_reg_students}. The {pct_evaluators}% ({num_evaluators}) have evaluated their peers. Below is the list of students who have not evaluated their peers.\n\n{data['no_evaluators_names']}"
  elif action == "no_evaluation":
    if lang == "es":
      return f"{Title}La evaluación se encuentra cerrada, pero aún no se ha realizado ninguna evaluación."
    else:
      return f"{Title}The evaluation is closed but no evaluation has been done yet."


def report_autoeva(lang, action):
  if lang == "es":
    Title = "<b>Reporte de autoevaluación</b>\n\n"
  else:
    Title = "<b>Autoevaluation report</b>\n\n"
  if action == "no_evalaution":
    if lang == "es":
      return f"{Title}Las evalauciones se encuentran cerradas pero no se ha realizado ninguna autoevalaución."
    else:
      return f"{Title}The evaluations are closed but no autoevaluation has been done."
    if action == "eva_open":
      if lang == "es":
        return f"{Title}Las evaluaciones aún se encuentran abiertas."
      else:
        return f"{Title}Evaluations are still open."


def menu_activate_eva(lang, state):
  if lang == "es":
    if state == 1:
      return f"Las evaluaciones han sido activadas."
    elif state == 0:
      return f"Las evaluaciones han sido desactivadas."
  else:
    if state == 1:
      return f"The evaluations have been activated."
    elif state == 0:
      return f"The evaluations have been deactivated."

      ### Menu: Messages ###


def send_msg_planet(lang):
  if lang == "es":
    return f"<b>ENVIAR MENSAJE A LOS PLANETAS</b>\n\nEscribe el comando <code>/send_message {lt}Mensaje a enviar{gt}</code>\n\n<b>Ejemplo</b>:\n<code>/send_message Se les recuerda que deben realizar la autoevaluación desde el menu Evaluar --> Autoevaluación</code>"
  else:
    return f"<b>SEND MESSAGE TO THE PLANETS</b>\n\nType the command <code>/send_message {lt}Message to send{gt}\n\n<b>Example</b>:\n<code>/send_message You are reminded to realize the autoevaluation from the menu Evaluate --> Autoevaluation</code>"


def send_msg_planet(lang):
  if lang == "es":
    return f"<b>Encuesta privada</b>\n\nEscribe el comando <code>/quiz {lt}¿Pregunta?{gt} {lt}Opción 1, Opción 2, Opción 3...{gt}</code>\n\n<b>Ejemplo</b>:\n<code>/quiz ¿Crees que tú planeta esta funcionando adecuadamente?</code>"
  else:
    return f"<b>SEND MESSAGE TO THE PLANETS</b>\n\nType the command <code>/send_message {lt}Message to send{gt}\n\n<b>Example</b>:\n<code>/send_message You are reminded to realize the autoevaluation from the menu Evaluate --> Autoevaluation</code>"


def meeting(lang, action, meeting_num="", planet=""):
  if lang == "es":
    if action == "active":
      return f"No se puede iniciar otro meeting, actualmente está activo el meeting {meeting_num} en este planeta. Para iniciar otro, primero debes finalizar el actual con el comando:\n\n/end_meeting {meeting_num}"
    elif action == "is_not_a_number":
      return f"El número de meeting que escribiste '{meeting_num}' no es un número."
    elif action == "no_number":
      if meeting_num:
        return f"<b>Meeting {meeting_num} activo.</b>\nPara iniciar o finalizar un meeting se debe escribir el número de meeting."
      else:
        return (
          f"Para iniciar o finalizar un meeting se debe escribir el número de meeting."
        )
    elif action == "finish_no_active":
      return f"Meeting no finalizado. El meeting actualmente activo es meeting {meeting_num}."
    elif action == "none_active":
      return f"No hay ningún meeting activo."
    elif action == "start":
      return f"El meeting {meeting_num} se ha iniciado con éxito."
    elif action == "end":
      return f"El meeting {meeting_num} se ha finalizado con éxito."
    elif action == "error_args":
      return f"Como argumento solo debes escribir el numero de meeting."
    elif action == "sucess":
      return f"Se ha registrado la asistencia y las calificaciones del meeting <b>{meeting_num}</b> en el planeta <b>{planet}</b>."
  else:
    if action == "active":
      return f"Cannot start another meeting, currently meeting {meeting_num} is active on this planet. To start another, first you must end the current one with the command:\n\n/end_meeting {meeting_num}"
    elif action == "is_not_a_number":
      return f"The meeting number you typed '{meeting_num}' is not a number."
    elif action == "no_number":
      if meeting_num:
        return f"<b>Meeting {meeting_num} active.</b>\nTo start or finish a meeting you must type the meeting number."
      else:
        return f"To start or finish a meeting you must type the meeting number."
    elif action == "finish_no_active":
      return f"Meeting not finished. Current active meeting is meeting {meeting_num}."
    elif action == "none_active":
      return f"There is no active meeting."
    elif action == "start":
      return f"The meeting {meeting_num} has been successfully started."
    elif action == "end":
      return f"The meeting {meeting_num} was successfully completed."
    elif action == "error_args":
      return f"As an argument you only have to write the meeting number."
    elif action == "sucess":
      return f"The attendance and grades of the meeting <b>{meeting_num}</b> have been saved on the planet <b>{planet}</b>."

