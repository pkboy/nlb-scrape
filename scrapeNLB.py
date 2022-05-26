from cgitb import text
import json
import requests
from os import path
from operator import itemgetter
from bs4 import BeautifulSoup
import re
import time


def scrapeNlbRoute(route_id: str, route_name: str):
  WEBSITE_BASE_URL = "https://www.nlb.com.hk/route/detail/"
  s = requests.Session()
  # change to English
  # change to Traditional CHinese / Simplified Chinese with zh / cn respectively
  s.get("https://www.nlb.com.hk/language/set/en")
  soup = None

  print("Processing route: {route_id} - {route_name}".format(route_id=route_id, route_name=route_name))
  filename = "data/" + route_id + "_" + route_name.replace(" ", "").replace(">", "-To-")

  if path.isfile(filename + ".htm") == False:
    page = s.get(WEBSITE_BASE_URL + route_id)
    with open(filename + ".htm", "wb") as f:
      f.write(page.content)
    soup = BeautifulSoup(page.content, "html.parser")
  else:
    with open(filename + ".htm", "r") as f:
      soup = BeautifulSoup(f.read(), "html.parser")

  divs = soup.find_all("div", class_="widget-content")
  #print(divs[1])
  ps = divs[1].find_all("p")
  data = { "routeId" : route_id, "routeName" : route_name, "timetables" : [], "notes" : [] }
  for p in ps:
    timetable_data = { "days" : "", "timetable" : [] }
    table = p.find_next_sibling("table")
    if table:
      timetable_data["days"] = p.text.replace('\u00a0', ' ')
      timetable = []
      trs = table.find_all("tr")
      for tr in trs:
        tds = tr.find_all("td")
        # for tds, if the td is *not* a time, then it is a note.
        # this note applies to the time that comes *after* the td.
        # ok maybe not because some timetables have the note *before* the td.
        # so maybe if the first td is a time, then the note follows.
        # if the first item is a note / blank, then the note precedes
        # some rows have multiple blanks as well.

        # check if note is in front or behind.
        is_time_first = False
        row_items = []
        for i in range(0, len(tds)):
          text = str.strip(tds[i].text)
          if text:
            match = re.match(r'^[0-2][0-9]:[0-5][0-9]$', text)
            if match:
              if i == 0:
                is_time_first = True
              row_items.append(text)
            else:
              row_items.append(text)
        if not is_time_first:
          row_items.reverse()
        
        # so now the first item will be a time.
        curr_item = { "time": "", "note": "" }
        for i in range(0, len(row_items)):
          if i == 0:
            curr_item["time"] = row_items[i]
          else:
            match = re.match(r'^[0-2][0-9]:[0-5][0-9]$', row_items[i])
            if match:
              timetable.append(curr_item)
              curr_item = { "time": row_items[i], "note": "" }
            else:
              if curr_item["note"]:
                curr_item["note"] = curr_item["note"] + " " + row_items[i]
              else:
                curr_item["note"] = row_items[i]
        timetable.append(curr_item)
      # sort timetable
      sorted_timetable = sorted(timetable, key=itemgetter("time"))
      timetable_data["timetable"] = sorted_timetable
      data["timetables"].append(timetable_data)
    else:
      if str.strip(p.text):
        data["notes"].append(p.text)

  json_timetable = json.dumps(data, indent=4)
  with open(filename + '.json', 'w') as f:
    f.write(json_timetable)
    

  # 2nd widget-content div
  # p > parent item (Mon to Saturday)
  #   table > 
  #    dict ( "note", "time" )
  # last p > meaning of note.

  return

def getNlbTimetables():
  API_ROUTE_LIST = "https://rt.data.gov.hk/v1/transport/nlb/route.php?action=list"

  ROUTE_LIST = "route.list.json"

  routes = []

  if path.isfile(ROUTE_LIST) == False:
    download = requests.get(API_ROUTE_LIST)
    data = json.loads(download.content.decode("utf-8-sig"))
    with open(ROUTE_LIST, "wb") as f:
      f.write(download.content)
    for route in data["routes"]:
      routes.append({ "routeId" : route["routeId"], "routeName" : route["routeName_e"]  })
  else:
    with open(ROUTE_LIST, "r") as f:
      data = json.load(f)
      for route in data["routes"]:
        routes.append({ "routeId" : route["routeId"], "routeName" : route["routeName_e"]  })
  
  for route in routes:
    scrapeNlbRoute(route["routeId"], route["routeName"])
    #time.sleep(2)
  #scrapeNlbRoute(routes[1]["routeId"], routes[1]["routeName"])

getNlbTimetables()