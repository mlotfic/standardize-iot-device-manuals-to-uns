import csv
import json


files = ["01-System Setup & Status.csv", "02-Meter Data (Basic).csv",
         "03-Energy Multi Tariff and Mult.csv", "04-Command Interface.csv",
         "05-HMI.csv", "06-Communications.csv", "07-Inputs & Outputs.csv",
         "08-Relay.csv", "09-Alarms.csv", "10-Files.csv", 
         "11-Diagnostics.csv", "12-Meter Data (Advanced).csv"]

files_ = ["01-System Setup & Status.json", "02-Meter Data (Basic).json",
         "03-Energy Multi Tariff and Mult.json", "04-Command Interface.json",
         "05-HMI.json", "06-Communications.json", "07-Inputs & Outputs.json",
         "08-Relay.json", "09-Alarms.json", "10-Files.json", 
         "11-Diagnostics.json", "12-Meter Data (Advanced).json"]


for i, csv_path in enumerate(files):
    with open(files[i], newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    with open(files_[i], "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=4, ensure_ascii=False)
        print(f"Done. Records written: csv_path {len(rows)}")
