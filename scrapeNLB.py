import json
import requests
import os
from operator import itemgetter
from bs4 import BeautifulSoup
import re
import time
import daysDictionary


def scrapeNlbRoute(route_id: str, route_name: str):
  cached_item = False
  WEBSITE_BASE_URL = "https://www.nlb.com.hk/route/detail/"
  s = requests.Session()
  # change to English
  # change to Traditional CHinese / Simplified Chinese with zh / cn respectively
  s.get("https://www.nlb.com.hk/language/set/en")
  soup = None

  DATA_DIR = "data/"
  HTML_DIR = DATA_DIR + "html/"
  JSON_DIR = DATA_DIR + "json/"
  
  if not os.path.isdir(HTML_DIR):
      os.makedirs(HTML_DIR)
  
  if not os.path.isdir(JSON_DIR):
      os.makedirs(JSON_DIR)
  
  print("Processing route: {route_id} - {route_name}".format(route_id=route_id, route_name=route_name))
  filename = route_id + "_" + route_name.replace(" ", "").replace(">", "-To-")

  # Download html
  if os.path.isfile(HTML_DIR + filename + ".htm") == False:
    page = s.get(WEBSITE_BASE_URL + route_id)
    with open(HTML_DIR + filename + ".htm", "wb", encoding="utf-8") as f:
      f.write(page.content)
    soup = BeautifulSoup(page.content, "html.parser")
  else:
    cached_item = True
    with open(HTML_DIR + filename + ".htm", "r", encoding="utf-8") as f:
      soup = BeautifulSoup(f.read(), "html.parser")

  divs = soup.find_all("div", class_="widget-content")
  
  origin = route_name.split(">")[0].strip()
  destination = route_name.split(">")[1].strip()

  #print(divs[1])
  ps = divs[1].find_all("p")
  data = { 
    "routeCode" : route_id, 
    "routeName" : route_name, 
    "origin": origin, 
    "destination": destination, 
    "departures" : [], 
    "remarks" : []
  }

  for p in ps:
    if p.text.strip() == "":
      continue
    timetable_data = { "serviceTimes" : [] }
    table = p.find_next_sibling("table")
    if table:
      days = p.text.strip()
      dayObj = daysDictionary.get_day_object(days)
      # print(dayObj)
      # see if this day exists in our days -> dictionary
      # dictionary will have to be manually updated.
      timetable_data = { **dayObj, **timetable_data }
      # timetable_data["days"] = p.text.strip()
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
        # remark is used instead of note in the data
        is_time_first = False
        row_items = []
        for i in range(0, len(tds)):
          text = str.strip(tds[i].text)
          if text:
            match = re.match(r"^[0-2][0-9]:[0-5][0-9]$", text)
            if match:
              if i == 0:
                is_time_first = True
              row_items.append(text)
            else:
              row_items.append(text)
        if not is_time_first:
          row_items.reverse()
        
        # so now the first item will be a time.
        curr_item = { "time": "", "remark": "" }
        for i in range(0, len(row_items)):
          if i == 0:
            curr_item["time"] = row_items[i]
          else:
            match = re.match(r"^[0-2][0-9]:[0-5][0-9]$", row_items[i])
            if match:
              timetable.append(curr_item)
              curr_item = { "time": row_items[i], "remark": "" }
            else:
              #print(curr_item)
              if curr_item["remark"]:
                curr_item["remark"] = curr_item["remark"] + " " + row_items[i]
              else:
                curr_item["remark"] = row_items[i]
        timetable.append(curr_item)
      # sort timetable
      sorted_timetable = sorted(timetable, key=itemgetter("time"))
      timetable_data["serviceTimes"] = sorted_timetable
      data["departures"].append(timetable_data)
    else:
      if str.strip(p.text):
        # the last few lines are supposed to be remarks
        # code is the first string before space
        firstSpaceIndex = 0
        try:
          firstSpaceIndex = p.text.index(" ")
        except:
          pass
        code = p.text[:firstSpaceIndex]
        remark = str.strip(p.text[firstSpaceIndex:])
        data["remarks"].append({ "code" : code, "remark" : remark })

  routes_obj = { "routes": [ data ]}

  json_timetable = json.dumps(routes_obj, indent=4, ensure_ascii=True)
  with open(JSON_DIR + filename + ".json", "w", encoding="utf-8") as f:
    f.write(json_timetable)

  return cached_item

def getNlbTimetables():
  API_ROUTE_LIST = "https://rt.data.gov.hk/v1/transport/nlb/route.php?action=list"

  ROUTE_LIST = "route.list.json"

  routes = []

  if os.path.isfile(ROUTE_LIST) == False:
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
    cached_item = scrapeNlbRoute(route["routeId"], route["routeName"])
    if not cached_item:
      time.sleep(2)

getNlbTimetables()