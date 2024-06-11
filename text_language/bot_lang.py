def config_files_send_document(lang, elements):
  if lang == "es":
    return f"files/guides/ES/{elements}_format.csv"

  else:
    return f"files/guides/EN/{elements}_format.csv"


def no_username(lang):
  if lang == "es":
    return "Me di cuenta que no tienes un username/alias registrado en tu cuenta de Telegram. Para utilizar EDUtrack debes configurar un username/alias. Ve a ajustes en tu cuenta de Telegram y edita tu perfil para asignar un username/alias. Cuando lo tengas escribe el comando /start."
  else:
    return "I noticed that you don't have a username registered in your Telegram account. To use EDUtrack you must set up a username or alias. In Telegram, go to settings account and edit your profile to assign a username. When you have it, type the command /start."
