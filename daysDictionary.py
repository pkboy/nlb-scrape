import json
import os
from pathlib import Path
from bs4 import BeautifulSoup

DICT_FILENAME = "daysDictionary.json"
DATA = []

if os.path.isfile(DICT_FILENAME) == False:
  open(DICT_FILENAME, "w").close()
else:
  if os.path. getsize(DICT_FILENAME) > 0:
    with open(DICT_FILENAME, 'r') as f:
      DATA = json.load(f)

def format_day_string(dayStr: str):
  # take away the \uxxxx and replace with spaces, page was utf-8 encoded.
  # doing it the manual way because it looks like human input error so not
  # concerned with the encoding mix up
  dayStr = dayStr.replace(u'\xa0', u' ')
  dayStr = dayStr.replace(u'\u3001', u', ')
  dayStr = dayStr.replace('&', 'and')
  dayStr = dayStr.replace('ys', 'y')
  dayStr = dayStr.replace('y(', 'y (')
  dayStr = dayStr.replace('liday', 'lidays')
  dayStr = dayStr.replace('Everyday', 'Daily')
  return dayStr

def get_day_object(dayStr: str):
  dayStr = format_day_string(dayStr)
  for day in DATA:
    if dayStr == day["serviceDaysString"]:
      return day
  return {
    "dayStart": -1,
    "dayEnd": -1,
    "runOnPublicHoliday": 0,
    "runOnSchoolHoliday": 1,
    "serviceDaysString": dayStr
  }

def build_dict_file():
  path = Path("data/html/")
  for p in path.rglob("*"):
    if p.suffix == ".htm":
      soup = None
      with open(p, "r", encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), "html.parser")

      divs = soup.find_all("div", class_="widget-content")
      ps = divs[1].find_all("p")

      for p in ps:
        if p.text.strip() == "":
          continue
        table = p.find_next_sibling("table")
        if table:
          found = False
          days = p.text.strip()
          days = format_day_string(days)
          
          # check if it is in there
          for serviceDay in DATA:
            if serviceDay["serviceDaysString"].lower() == days.lower():
              found = True
              break
          if not found:
            DATA.append({
              "dayStart": -1,
              "dayEnd": -1,
              "runOnPublicHoliday": 0,
              "runOnSchoolHoliday": 1,
              "serviceDaysString": days
            })
  with open(DICT_FILENAME, 'w') as f:
    json_string = json.dumps(DATA, indent=4)
    f.write(json_string)

# inits the file
build_dict_file()