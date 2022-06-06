import os
import json
from pathlib import Path 

path = Path("data/json")
for p in path.rglob("*"):
  if p.suffix == ".json":
    with open(p, "r") as f:
      data = json.load(f)
      numOfTimetables = len(data["timetables"])
      if numOfTimetables > 0:
        
        print(data["routeId"] + " " + data["routeName"])
        print("Number of timetables: {numOfTimetables}".format( numOfTimetables = numOfTimetables ))
        for table in data["timetables"]:
          print(table["days"])
