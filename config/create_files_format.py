import pandas as pd
import numpy as np
import re
from datetime import datetime


def create_files(path_files, df, title_table, date=True, mode="w"):
  # print(path_files)
  today = datetime.today()
  date = today.strftime("_%d%m%Y_%H%M%S") if date else ""
  date_text = today.strftime("%B %d, %Y")

  file_name = path_files.split("/")[-1]

  if file_name == "/":
    file_name = file_name[-1]
  else:
    file_name = file_name

  df.index = np.arange(1, len(df) + 1)
  df.fillna("", inplace=True)

  df.to_csv(f"{path_files}{date}.csv", index=0, encoding="UTF-8")
  data_in_html = df.to_html()
  data_in_html = re.sub(
    r"""<table border="1" class="dataframe">""",
    r"""<table id="example" class="table table-striped table-bordered table-hover" style="width:100%">""",
    data_in_html,
  )
  data_in_html = re.sub(r"right", r"center", data_in_html)
  with open(f"{path_files}.html", mode, encoding="utf-8") as file3:
    file3.write(data_in_html)
  data_in_html = re.sub(
    r"<table",
    r"""<!doctype html>
    <html lang="es">
    <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>EDUtrack</title>

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

    <!--datables CSS básico-->
    <link rel="stylesheet" type="text/css" href="datatables/datatables.min.css"/>
    <!--datables estilo bootstrap 4 CSS-->
    <link rel="stylesheet"  type="text/css" href="datatables/DataTables-1.10.18/css/dataTables.bootstrap4.min.css">
    <style>
      body{
        background: #ddd;
          }
      header{
        background:#512DA8;
        }
      table{
        background-color: #fff;

      }
      th{
        background-color:#8CBF42;
      }
      th, td{
      padding: 2px;}
      thead{background-color: #639E0A;
      /*thead{background-color: #8CBF42;*/
      border-bottom: solid 5px #455 color: white;
      }

      tr:nth-child(even){
        background-color: #ddd;
        }
      tr:hover td{
        background-color: #ff9800;
        color: white;
        }
    </style>

    </head>

    <body>
      <header>
          <h4 class="text-center text-light">"""
    + title_table
    + """</h4>
          <h5 class="text-center text-light">"""
    + date_text
    + '''</h5>
      </header>


      <!--Ejemplo tabla con DataTables-->
      <div class="container">
        <div class="row">
          <div class="col-lg-12">
            <div class="table-responsive">
              <table id="example" class="table table-striped table-bordered table-hover"''',
    data_in_html,
  )

  data_in_html = re.sub(
    r"</table>",
    r"""</table>
  </div>
  </div>
  </div>
  </div>

    <!-- jQuery, Popper.js, Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

    <!-- datatables JS -->
    <script type="text/javascript" src="https://cdn.datatables.net/v/bs4/dt-1.10.20/datatables.min.js"></script>

    <script type="text/javascript" >$('#example').DataTable();</script>


    </body>
    </html>""",
    data_in_html,
  )
  html_file = f"{path_files}{date}.html"
  with open(html_file, mode, encoding="utf-8") as file2:
    file2.write(data_in_html)

