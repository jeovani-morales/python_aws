from telegram import InlineKeyboardButton as IKButton
import config.config_file as cfg

lt = "&lt;"
gt = "&gt;"


def welcome(user, context, action="short"):
  bot_username = context.bot.username
  
  if user.language == "es":
    if action == "long":
      #return f"Bienvenido a EDUtrack <b>{username}</b>,tu correo demo es correo_{user_id}@demo.com, te acompañare durante el curso para hacerte más participe en la asignatura.\n\nEscribe el símbolo <b>'/'</b> y te mostrare los comandos que puedes utilizar para que trabajemos juntos. Aquí tienes una breve explicación de cada uno.\n\n/menu\nTe mostraré el menú con las opciones activas que pordrás utilizar.\n\n/change_language\nTe ayudaré a cambiar el idioma en que te muestro los contenidos. Las opciones actuales son Inglés y Español.\n\n/help\nPodrás descargar el manual de usuario."
      # Te mostraré los comandos que puedes utilizar y la descripción de cada apartado del menú. También podrás acceder al manual de usuario.'
      return f"""Welcome to EDUtrack <b>{bot_username}</b>,your demo email is mail_{user._id}@demo.com. With EDUTrack_Demo you will be able to interact with EDUTrack from the student and teacher perspective. Type the /menu command to access the student menu. Select the Be a Teacher option to change your profile. "
    
Bienvenido a EDUtrack <b>{bot_username}</b>,tu correo demo es mail_{user._id}@demo.com. Con EDUTrack_Demo podrás interactuar con EDUTrack desde la perspectiva de estuidante y de docente. Escribe el comando /menu para acceder al menú de estudiante. Selecciona la opción de Ser Docente para cambiar de perfil."""
    if action == "short":
      return f"Escribe el comando /menu para ver las opciones."

  else:
    if action == "long":
      #return f"Welcome to EDUtrack {bot_username}. I will guide you during the course so that you can be more active in this subject.\nType character <b> '/' </b> and I will show you the commands you can use to work together. Here's a brief explanation of each one.\n\n/menu\nI'll show you the menu with the active options you can use.\n\n/change_language\nI will help you change the language in which I show you the contents. The current options are English and Spanish.\n\n/help\nYou can download the user manual."
      return f"""Welcome to EDUtrack <b>{bot_username}</b>,your demo email is mail_{user._id}@demo.com. With EDUTrack_Demo you will be able to interact with EDUTrack from the student and teacher perspective. Type the /menu command to access the student menu. Select the Be a Teacher option to change your profile. "
    
    Bienvenido a EDUtrack <b>{bot_username}</b>,tu correo demo es mail_{user._id}@demo.com. Con EDUTrack_Demo podrás interactuar con EDUTrack desde la perspectiva de estuidante y de docente. Escribe el comando /menu para acceder al menú de estudiante. Selecciona la opción de Ser Docente para cambiar de perfil."""
    if action == "short":
      return ("Type /menu command to see active conversations.",)

    # I'll show you the commands you can use and the description of each menu item. You will also be able to access the user manual."


def not_config_files_set(lang, context):
  bot_name = context.bot.first_name
  if lang == "es":
    return f"<b>EDUtrack {bot_name}</b> está en modo configuración y por ello aún no está activo. Espera instrucciones de tu profesor/a."
  else:
    return f"<b>EDUtrack {bot_name}</b> is in configuration mode and therefore is not active yet. Wait for instructions of your teacher."


def check_email(lang, action, email=""):
  if lang == "es":
    Title = f"<b>VERIFICACIÓN POR EMAIL:</b>\n"
    if action == "registration":
      return f"{Title}Para verificar que eres estudiante de la asignatura <b>{cfg.subject_data['name']}</b> y registrar tu usario de Telegram en la base de datos escribe el comando:\n\n<code>/check_email {lt}correo UGR{gt}</code>\n\nSi no lo sabes/recuerdas, contacta con tu profesor/a.\n\n<b>Ejemplo</b>:\n<code>/check_email nombre@correo.ugr.es</code>"
    elif action == "no_args":
      return f"{Title}Debes escribir tu correo después del comando.\n\n<b>Ejemplo</b>:\n/check_email nombre@correo.ugr.es"
    elif action == "many_args":
      return f"{Title}{email} no es un email correcto, no debe llevar espacios.\n\n<b>Ejemplo:</b>\n<code>/check_email nombre@correo.ugr.espacios</code>"
    elif action == "not_found":
      return f"{Title}El email <b>{email}</b> no se encuentra en la base de datos. Por favor revisa si lo escribiste correctamente o comunícate con tu profesor/a."
    elif action == "exists_email":
      return f"{Title}Ya tengo registrado el email <b>{email}</b> en mi base de datos. No es necesario registrarlo de nuevo. Si el email es el tuyo y no tienes acceso al comando /menu contacta a tu profesor/a."
    elif action == "registered_user":
      return f"Tu usuario ya se encuentra registrado con el email {email}\nSi no es tu correo por favor contacta con tu profesor/a."
    elif action == "success":
      return (
        f"{Title}He registrado con éxito el email {email} a tu usuario de Telegram."
      )

  else:
    Title = f"<b>EMAIL VERIFICATION:</b>\n"
    if action == "registration":
      return f"{Title}To verify that you are a student of <b>{cfg.subject_data['name']}</b> course and to register your Telegram alias in the database, type the command:\n\n<code>/check_email {lt}UGR email{gt}</code>\n\nIf you don't know/remember it, contact with your teacher.\n\n*Example*:\n<code>/check_email nickname@correo.ugr.es</code>"
    elif action == "no_args":
      return f"{Title}You must write your email after the command.\n\n<b>Example</b>:\n/check_email nickname@correo.ugr.es"
    elif action == "many_args":
      return f"{Title}{email} is not a correct email, it must not contain spaces.\n\n<b>Example:</b>\n<code>/check_email nickname@correo.ugr.es</code>"
    elif action == "not_found":
      return f"{Title}The email <b>{email}</b> is not in the database. Please check if you typed it correctly or contact your teacher."
    elif action == "exists_email":
      return f"{Title}I have already registered the email {email} in my database. It is not necessary to register it again. If the email is yours and you do not have access to the /menu command, contact your teacher."
    elif action == "registered_user":
      return f"{Title}Your user is already registered with the email {email}\nIf this is not your email, please contact your teacher."
    elif action == "success":
      return f"{Title}I have successfully registered the email {email} to your Telegram user."


def example_commands(lang, command):
  if lang == "es":
    if command == "check_email":
      return f"\n\n<b>Ejemplo</b>:\n<code>/check_email nombre@correo.ugr.es</code>"


## MENUS ####################
def main_menu(lang):
  if lang == "es":
    text = "<b>MENU ESTUDIANTE</b>\nSelecciona una opción:"
    opt = [
      [IKButton("Mi Calificación", callback_data="s_menu-grade")],
      [
        IKButton("Opinar", callback_data="s_menu-opn"),
        IKButton("Evaluar", callback_data="s_menu-eva"),
      ],
      [IKButton("Sugerencia", callback_data="s_menu-suggestion")],
      [IKButton("Cambiar Idioma", callback_data="s_menu-change_language")],
      [IKButton("Ser Docente", callback_data="s_menu-change_profile")],
    ]
  else:
    text = "<b>STUDENT MENU</b>\nSelect an option:"
    opt = [
      [IKButton("My grades", callback_data="s_menu-grade")],
      [
        IKButton("Opinion", callback_data="s_menu-opn"),
        IKButton("Evaluate", callback_data="s_menu-eva"),
      ],
      [IKButton("Suggestion", callback_data="s_menu-suggestion")],
      [IKButton("Change Language", callback_data="s_menu-change_language")],
      [IKButton("Be a Teacher", callback_data="s_menu-change_profile")],

    ]
  return (text, opt)


def my_grade(lang, action, week, stu_data="", note=""):
  if lang == "es":
    Title = f"<b>MI CALIFICACIÓN - SEMANA {week}:</b>\n\n"
    if action == "grades":
      return f"{Title}Tu factor de riesgo académico es: <b>{stu_data['linguistic']}</b>.\nTu calificación actual es: <b>{stu_data['actual_grade']}</b>\nTu calificación máxima posible es: <b>{stu_data['max_possible_grade']}</b> \n\nA continuación te muestro cada actividad que se ha evaluado hasta este momento y su calificación:{stu_data['activities']}\n\nRecuerda que la calificación actual es con base a las actividades realizadas y calificadas hasta este momento, conforme realices  más actividades tu nota ira mejorando.\n"
    elif action == "no_active":
      return f"{Title}Actualmente no existen actividades calificadas.\n\nTu factor de riesgo académico es: <b>Ninguno</b>.\nTu máxima calificación posible es: <b>10</b>"
    elif action == "no_email":
      return f"{Title}La base de datos aún no tiene registrado tu email. Ponte en contacto con tu profesor/a."
  else:
    Title = f"<b>MY GRADE WEEK {week}</b>\n\n"
    if action == "grades":
      return f"{Title}Your academic risk factor is <b>{stu_data['linguistic']}</b>.\nYour actual grade is: <b>{stu_data['actual_grade']}</b>\nYour highest possible grade is: <b>{stu_data['max_possible_grade']}</b>\n\nBelow I show you each activity that has been evaluated so far and its grade:{stu_data['activities']}\n\nRemember that the current grade is based on the activities completed and graded up to this point, as you do more activities your grade will improve."
    elif action == "no_active":
      return f"{Title}There are currently no qualified activities.\n\nYour academic risk factor is: <b>None</b>.\nYour highest possible grade is: <b>10</b>."
    elif action == "no_email":
      return (
        f"{Title}The database has not yet registered your email. Contact your teacher."
      )


def menu_opinion(lang):
  if lang == "es":
    text = f"<b>OPINAR</b>\nSelecciona una opción:"
    opt = [
      [IKButton("Práctica Docente", callback_data="s_menu-opn-tp")],
      [IKButton("Colaboración entre compañeros", callback_data="s_menu-opn-coll")],
      [IKButton("Recursos/materiales", callback_data="s_menu-opn-rsrcs")],
      [IKButton("Tu planeta", callback_data="s_menu-opn-planet")],
      [IKButton("Regresar", callback_data="s_menu-back")],
    ]
  else:
    text = "<b>OPINION</b>\nSelect an option:"
    opt = [
      [IKButton("Teaching Practice", callback_data="s_menu-opn-tp")],
      [IKButton("Peer Collaboration", callback_data="s_menu-opn-coll")],
      [IKButton("Resources/materials", callback_data="s_menu-opn-rsrcs")],
      [IKButton("Your planet", callback_data="s_menu-opn-planet")],
      [IKButton("Back", callback_data="s_menu-back")],
    ]
  return (text, opt)


def menu_opn_tea_practice(lang):
  if lang == "es":
    text = "<b>OPINION DE LA PRACTICA DOCENTE</b>\nSelecciona una categoría para ver los criterios:"
    opt = [
      [IKButton("Docente", callback_data="s_menu-opn-tp-teacher")],
      [IKButton("Contenidos", callback_data="s_menu-opn-tp-content")],
      [IKButton("Meetings", callback_data="s_menu-opn-tp-meet")],
      [IKButton("Regresar", callback_data="s_menu-opn")],
    ]
  else:
    text = "<b>TEACHING PRACTICE OPINION</b>\nSelect a category to see the criteria:"
    opt = [
      [IKButton("Teacher", callback_data="s_menu-opn-tp-teacher")],
      [IKButton("Contents", callback_data="s_menu-opn-tp-content")],
      [IKButton("Meetings", callback_data="s_menu-opn-tp-meet")],
      [IKButton("Back", callback_data="s_menu-opn")],
    ]
  return (text, opt)


def opn_tea_practice(lang, action, week, criterion=""):
  if lang == "es":
    Title = f"<b>OPINION SOBRE LA PRACTICA DOCENTE\nSEMANA {week}</b>\n\n"
    if action == "criterion":
      return f"{Title}¿Cuál es tu opinión sobre el criterio <b>{criterion}</b> en la práctica docente según tu experiencia de esta semana en la asignatura?"
    elif action == "text_after_save":
      return (
        f"{Title}Se ha guardado correctamente tu opinión.\n\nSelecciona una opción."
      )
    elif action == "no_criteria":
      return f"{Title}No hay criterios que evaluar o ya los has evaluado todos esta semana. Regresa en otro momento o la siguiente semana."
    elif action == "choice_criterion":
      return f"{Title}Selecciona un criterio para evaluarlo."
    elif action == "success":
      return f"Se ha guardado correctamente tu evaluación."
  else:
    Title = f"<b>TEACHING PRACTICE OPINION\nWEEK {week}</b>\n\n"
    if action == "criterion":
      return f"{Title}What is your opinion about criterion <b>{criterion}</b> in the teaching practice according to your experience of this week in the subject?"
    elif action == "text_after_save":
      return f"{Title}Your opinion has been saved correctly.\n\nSelect an option:"
    elif action == "no_criteria":
      return f"{Title}There are no criteria to evaluate or you've already evaluated them all this week. Come back at another time or the next week."
    elif action == "choice_criterion":
      return f"{Title}Selecciona un criterio para evaluarlo."
    elif action == "success":
      return f"Your evaluation has been saved correctly."


### MENU opn_collaboration
def opn_collaboration(lang, action, week, classmate=""):
  if lang == "es":
    Title = f"<b>OPINION SOBRE LA COLABORACION ENTRE COMPAÑEROS\nSEMANA {week}</b>\n"
    if action == "choice":
      return f"{Title}Selecciona una opción."
    elif action == "scale":
      return f"{Title}¿Cómo consideras que ha sido la colaboración de tu compañero/a <b>{classmate['name']}</b> con el username <b>{classmate['username']}</b> en las tareas y actividades de tu planeta durante esta semana?."
    elif action == "no_classmates":
      return f"No hay compañeros de equipo que evaluar o ya has evaluado a todos en esta semana. Regresa en otro momento o la siguiente semana."
    elif action == "success":
      return f"Se ha guardado correctamente tu evaluación."
  else:
    Title = f"<b>PEER COLLABORATION OPINION</b>\n"
    if action == "choice":
      return f"{Title}Select an option:"
    elif action == "scale":
      return f"<b>PEER COLLABORATION OPINION\nWEEK {week}</b>\n\nHow do you consider the collaboration of your teammate <b>{classmate['name']}</b> with the username <b>{classmate['username']}</b> in the tasks and activities of your planet during this week?"
    elif action == "no_classmates":
      return f"There are no teammates to evaluate or you have already evaluated everyone this week. Come back at another time or the next week."
    elif action == "success":
      return f"Your evaluation has been saved correctly."

  return (text, opt)


## MENU - OPINION - RESOURCES
def opn_resources(lang, action, resource=""):
  if lang == "es":
    Title = f"<b>OPINION SOBRE LOS RECURSOS</b>\n"
    if action == "section":
      return f"{Title}Selecciona una sección para ver sus recursos.\n<b>Nota FC_ML Son recursos de Flipped Classrom y M-Learning.</b>"
    elif action == "rsrc":
      return f"{Title}Selecciona una opción:"
    elif action == "scale":
      return f"{Title}¿Como consideras el recurso/material <b>{resource}</b>?."
    elif action == "no_resources":
      return f"{Title}Actualmente no hay más recursos que evaluar en esta seccion. Selecciona otra sección."
    elif action == "no_section":
      return f"{Title}Actualmente no hay más recursos que evaluar. Regresa en otro momento o la siguiente semana."
    elif action == "success":
      return f"{Title}Se ha guardado correctamente tu opinión."

  else:
    Title = f"<b>RESOURCES OPINION</b>\n"
    if action == "section":
      return f"{Title}Select a section to view its resources.\n<b>Note: FC_ML are resources of Flipped Classrom and M-Learning.</b>"
    elif action == "rsrc":
      return f"{Title}Select an option:"
    elif action == "scale":
      return f"{Title}How do you consider the resource/material <b>{resource}</b>?"
    elif action == "no_resources":
      return f"{Title}There are currently no more resources to evaluate in this section. Select another section."
    elif action == "no_section":
      return f"{Title}Currently there are no more resources to evaluate. Come back at another time or the next week."
    elif action == "success":
      return f"{Title}Your opinion has been saved correctly."


## MENU - OPINION - TEACHER - MEETINGS
def opn_tea_meeting(lang, action, meeting=""):
  if lang == "es":
    Title = f"<b>OPINIÓN SOBRE LA COMUNICACIÓN VIRTUAL CON EL DOCENTE</b>\n"
    if action == "text_meeting":
      return f"{Title}Selecciona una meeting."
    elif action == "no_meetings":
      return f"{Title}Aún no se ha realizado ninguna meeting ó ya has evaluado las meetings hasta la fecha. Regresa después."
    elif action == "scale":
      return f"{Title}¿Como consideras que fue la actuación de tu profesor/a en la <b>meeting {meeting}</b>?."
    elif action == "success":
      return f"Se ha guardado correctamente tu evaluación."

  else:
    Title = f"<b>OPINION OF THE VIRTUAL COMMUNICATION WITH THE TEACHER</b>\n"
    if action == "text_meeting":
      return f"{Title}Select a meeting."
    elif action == "no_meetings":
      return f"{Title}No meeting has been taken place yet or you have already evaluated all meetings to date. Come back later."
    elif action == "scale":
      return f"{Title}How do you think the teacher's performance was in the <b>meeting {meeting}</b>?"
    elif action == "success":
      return f"Your evaluation has been saved correctly."


def opn_planet(lang, action, planet=""):
  if lang == "es":
    Title = "<b>Opinión de tu planeta</b>\n\n"
    if action == "no_planet":
      return (
        f"{Title}Aún no te tengo registrado en un planeta. Pregunta a tu profesor/a."
      )
    elif action == "already":
      return f"{Title}Ya has evaluado a tu planeta esta semana. Regresa la siguiente semana para opinar nuevamente."
    elif action == "scale":
      return f"{Title}¿Cuál es tu opinión sobre el funcionamiento de tú planeta {planet} esta semana?"
  else:
    Title = "<b>Opinion of your planet</b>\n\n"
    if action == "no_planet":
      return f"{Title}I haven't registered you on a planet yet. Ask your teacher."
    elif action == "already":
      return f"{Title}You have already evaluated your planet this week. Come back next week to give your opinion again."
    elif action == "scale":
      return f"{Title}What is your opinion about the functioning of your planet {planet} this week?"


## MENU EVALUATE
# CAMBIAR POR ACTIVE_EVALUATE
def evaluate(lang, action):
  if lang == "es":
    if action == "not_available":
      return f"<b>EVALUAR</b>\nPor el momento esta función no se encuentra disponible. Solicita información a tu profesor/a."
  else:
    if action == "not_available":
      return f"<b>EVALUATE</b>\nAt the moment this function is not available. Ask your teacher for information."


def menu_evaluate(lang):
  if lang == "es":
    text = "<b>EVALUAR</b>\nSelecciona una opción:"
    opt = [
      [IKButton("Autoevaluación", callback_data="s_menu-eva-auto")],
      [IKButton("Colaboración entre compañeros", callback_data="s_menu-eva-coll")],
      [IKButton("Docente", callback_data="s_menu-eva-teacher")],
      [IKButton("Regresar", callback_data="s_menu-back")],
    ]
  else:
    text = "<b>EVALUATE</b>\nSelect an option:"
    opt = [
      [IKButton("Self-Evaluation", callback_data="s_menu-eva-auto")],
      [IKButton("Peer Collaboration", callback_data="s_menu-eva-coll")],
      [IKButton("Teacher", callback_data="s_menu-eva-teacher")],
      [IKButton("Back", callback_data="s_menu-back")],
    ]
  return (text, opt)


def eva_autoevaluation(language, action, question="", next_=""):
  if language == "es":
    Title = "<b>AUTOEVALUACION</b>\n\n"
    if action == "init":
      text = f"{Title}A continuación se te presentaran 5 preguntas.\n\nDeberás responder SI o NO de forma honesta.\n"
      opt = [
        [IKButton("Iniciar Autoevaluación", callback_data="s_menu-eva-auto-init")],
        [IKButton("Regresar", callback_data="s_menu-eva")],
      ]
    elif action == "continue":
      text = f"{Title}Ya has respondido algunas preguntas, así que continuemos con tu autoevaluación.\n"
      opt = [
        [
          IKButton("Continuar Autoevaluación", callback_data="s_menu-eva-auto-continue")
        ],
        [IKButton("Regresar", callback_data="s_menu-eva")],
      ]
    elif action == "question":
      if question == "Q1":
        text = f"{Title}1.- ¿Tienes un plan de estudio específico a seguir en esta asignatura?"
      elif question == "Q2":
        text = (
          f"{Title}2.- En caso de tener una planificación, ¿la usas con frecuencia?"
        )
      elif question == "Q3":
        text = f"{Title}3.- ¿Esta asignatura te frustra de alguna forma?"
      elif question == "Q4":
        text = (
          f"{Title}4.- ¿Consideras que estudias con responsabilidad en esta asignatura?"
        )
      elif question == "Q5":
        text = f"{Title}5.- En todos los temas se ha proporcionado una bibliografía asociada, ¿la has consultado?"
      opt = [
        [IKButton("SI", callback_data=f"s_menu-eva-auto-{question}-1")],
        [IKButton("NO", callback_data=f"s_menu-eva-auto-{question}-0")],
      ]
      return (text, opt)
    elif action == "response":
      if question == "RQ1":
        text = "<b>PLAN DE ESTUDIO</b>\n\nLa manera en que se planifica y organiza el tiempo es una cuestión de hábitos, y determina, en gran medida el aprovechamiento del tiempo y, por tanto, el rendimiento académico."
      elif question == "RQ2":
        text = "<b>CREA HABITOS</b>\n\nSigue tu horario hasta que hayas adquirido el hábito de estudio/trabajo. Estudiando seis días a la semana, el mismo número de horas y a la misma hora facilita la aparición y consolidación del hábito."
      elif question == "RQ3":
        text = "<b>EVITA LA FRUSTRACIÓN</b>\n\nMantener altos niveles de atención y concentración requiere a veces mucho esfuerzo. Vigila tu tolerancia a la frustración. Si pretendes hacerlo todo de golpe, es probable que no lo logres."
      elif question == "RQ4":
        text = "<b>EVITA PROCRASTINAR</b>\n\nRechaza el hábito de la procrastinación: “dejarlo para después”. Todos procrastinamos nuestras responsabilidades de vez en cuando. La clave está en saber qué cosas “dejamos para luego”, cómo y por qué."
      elif question == "RQ5":
        text = "<b>LEER LA BIBLIOGRAFIA</b>\n\nLa lectura de la bibliografía asociada, es el paso imprescindible para comprender el contenido y extraer las ideas principales del texto. Lo que supone también aprender y utilizar con propiedad los términos específicos de la materia."
      opt = [[IKButton("Continuar", callback_data=f"s_menu-eva-auto-{next_}")]]
      return (text, opt)
    elif action == "success":
      return f"{Title}Ya has realizado la autoevaluación."
    return (text, opt)
  else:
    Title = "<b>SELF-EVALUATION</b>\n\n"
    if action == "init":
      text = f"{Title}You will then be asked 5 questions.\n\nYou must answer YES or NO honestly.\n"
      opt = [
        [IKButton("Start Self-Evaluation", callback_data="s_menu-eva-auto-init")],
        [IKButton("Back", callback_data="s_menu-eva")],
      ]
    elif action == "continue":
      text = f"{Title}You've already answered a few questions, so let's get on with your self-evaluation.\n"
      opt = [
        [
          IKButton("Continue Self-Evaluation", callback_data="s_menu-eva-auto-continue")
        ],
        [IKButton("Back", callback_data="s_menu-eva")],
      ]
    elif action == "question":
      if question == "Q1":
        text = (
          f"{Title}1.- Do you have a specific study plan to follow in this subject?"
        )
      elif question == "Q2":
        text = f"{Title}2.- If you have a plan, do you use it regularly?"
      elif question == "Q3":
        text = f"{Title}3.- Does this course frustrate you in any way?"
      elif question == "Q4":
        text = f"{Title}4.- Do you think you study responsibly in this course?"
      elif question == "Q5":
        text = f"{Title}5.- In all subjects an associated bibliography has been provided, have you consulted it?"
      opt = [
        [IKButton("YES", callback_data=f"s_menu-eva-auto-{question}-1")],
        [IKButton("NO", callback_data=f"s_menu-eva-auto-{question}-0")],
      ]
    elif action == "response":
      if question == "RQ1":
        text = "<b>STUDY PLAN</b>\n\nThe way time is planned and organized is a matter of habits, and determines to a large extent the use of time and, therefore, academic performance."
      elif question == "RQ2":
        text = "<b>CREATE HABITS</b>\n\nFollow your schedule until you have acquired the habit of study/work. By studying six days a week, the same number of hours at the same time facilitates the emergence and consolidation of the habit."
      elif question == "RQ3":
        text = "<b>AVOID FRUSTRATION</b>\n\nMaintaining high levels of attention and concentration sometimes requires a lot of effort. Watch your tolerance for frustration. If you intend to do it all at once, you probably won't make it."
      elif question == "RQ4":
        text = "<b>AVOID PROCRASTINATING</b>\n\nReject the habit of procrastination: 'Leave it for later'. We all postpone our responsibilities from time to time. The key is to know what we 'leave for later', how and why."
      elif question == "RQ5":
        text = "<b>READ THE BIBLIOGRAPHY</b>\n\nThe reading of the associated bibliography is the essential step to understand the content and extract the main ideas of the text. This also implies learning and using the specific terms of the subject."
      opt = [[IKButton("NEXT", callback_data=f"s_menu-eva-auto-{next_}")]]
      return (text, opt)
    elif action == "success":
      return f"{Title}You've already done the self-evaluation."

    return (text, opt)


def eva_collaboration(language, action, classmate=""):
  if language == "es":
    if action == "choice":
      return f"<b>EVALUACION SOBRE LA COLABORACION ENTRE COMPAÑEROS</b>\n\nSelecciona una opción:"
    if action == "no_planet":
      return f"<b>EVALUACION SOBRE LA COLABORACION ENTRE COMPAÑEROS</b>\nAún no estás registrado en ningún planeta."
    elif action == "scale":
      return f"<b>EVALUACION SOBRE LA COLABORACION ENTRE COMPAÑEROS</b>\n\n¿Cómo consideras que ha sido la colaboración de tu compañero/a <b>{classmate['name']}</b> con el username <b>{classmate['username']}</b> en las tareas de tu planeta en general?."
    elif action == "no_classmates":
      return f"<b>EVALUACION SOBRE LA COLABORACION ENTRE COMPAÑEROS:</b>\n\nNo hay compañeros de equipo que evaluar o ya has evaluado a todos."
    elif action == "success":
      return f"<b>EVALUACION SOBRE LA COLABORACION ENTRE COMPAÑEROS:</b>\n\nSe ha guardado correctamente tu evaluación.\n\nSelecciona una opción."

  else:
    if action == "choice":
      return f"<b>PEER COLLABORATION EVALUATION</b>\n\nSelect an option:"
    if action == "no_planet":
      return f"<b>PEER COLLABORATION EVALUATION</b>\nYou're not registered in any planet yet."
    elif action == "scale":
      return f"<b>PEER COLLABORATION EVALUATION</b>\n\nHow do you think your team-mate <b>{classmate['name']}</b> with the username <b>{classmate['username']}</b>, has collaborated in the tasks of your planet in general?."
    elif action == "no_classmates":
      return f"<b>PEER COLLABORATION EVALUATION</b>\n\nThere are no team-mates to evaluate or you have already evaluated everyone this week. Come back at another time or the next week."
    elif action == "success":
      return f"<b>PEER COLLABORATION EVALUATION</b>\n\nYour evaluation has been saved correctly.\n\nSelect an option:"


def eva_teacher(language, action):
  if language == "es":
    if action == "sucess":
      return "<b>EVALUACION DOCENTE</b>\n\nYa has evaluado al docente."
    if action == "scale":
      return "<b>EVALUACION DOCENTE</b>\n\n¿Cómo consideras que fue la comunicación con tu <b>profesor/a</b> durante los meetings."


def suggestion(lang, action):
  if lang == "es":
    if action == "text":
      return f"<b>SUGERENCIA:</b>\nEn esta sección podras sugerir ideas que mejoren este bot o también que quieras proponer para la asignatura. Puede ser integrar alguna funcionalidad o proponer alguna mejora de mi funcionamiento.\n\nEscribe el comando /suggestion {lt}tu sugerencia{gt}\n\nEjemplo:\n/suggestion Creo que se podría mejorar el funcionamieno si..."
    elif action == "empty":
      return f"<b>SUGERENCIA:</b>\nLo siento la sugerencia no puede estar vacía.\n\nEscribe el comando /suggestion {lt}tu sugerencia{gt}\n\nEjemplo:\n/suggestion Creo que se podría mejorar el funcionamieno si..."
    elif action == "save":
      return f"<b>SUGERENCIA:</b>\nSe ha guardado tu sugerencia con exito."
  else:
    if action == "text":
      return f"<b>SUGGESTION:</b>\nIn this section you can suggest ideas that improve this bot or also that you want to propose for the course. It can be to integrate some functionality or to propose some improvement of my operation\n\nType the command /suggestion {lt}your suggestion{gt}\n\nExample:\n/suggestion I think that this course could be improved if..."
    elif action == "empty":
      return f"<b>SUGGESTION:</b>\nI'm sorry the suggestion can't be empty.\n\nType the command /suggestion {lt}your suggestion{gt}\n\nExample:\n/suggestion I think that this course could be improved if..."
    elif action == "save":
      return f"<b>SUGGESTION:</b>\nYour suggestion has been successfully saved."
