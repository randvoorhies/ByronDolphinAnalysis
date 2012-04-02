#!/usr/bin/env python

import csv

def readdb(filename):
  reader = csv.reader(open(filename, 'rb'), delimiter=',', quotechar='"')
  table = {}
  headers = []
  for row in reader:
    if len(headers) == 0:
      headers = row
    else:
      entry = {}
      for columnIdx in range(1, len(row)):
        entry[headers[columnIdx]] = row[columnIdx]
      table[row[0]] = entry
  return table


Dolphins = readdb('Dolphins')

DolphinNames = ["Windex", "PASS", "Alison", "NANCY", "492", "SCALLOP",
                "Trike", "Scooter", "Ianthe", "CHOP SUEY", "Feather",
                "dallas", "MORNING DUE", "2LiveCrew", "cousin"]

# Make a reverse lookup table so we can get dolphin IDs by name
DolphinNameIds = {name : -1 for name in DolphinNames}
for dolphinid in Dolphins:
  name = Dolphins[dolphinid]["Name"] 
  if name in DolphinNames:
    if DolphinNameIds[name] != -1:
      print "Duplicate Name/ID found for ", name
    else:
      DolphinNameIds[name] = dolphinid


# Grab all dolphin observations between 2009 and 2011
DolphinObservations = readdb('DolphinObservations')
DolphinNameObservations = {name : {} for name in DolphinNames}
for observationid in DolphinObservations:
  entry = DolphinObservations[observationid]

  # Filter out all observations out of our date range
  year = -1
  try: year = int(entry['StartTime'].split(' ')[0].split('/')[-1])
  except: continue
  if year < 2009 or year > 2011: continue

  # Create a new observation entry
  dolphinid = entry["DolphinID"]
  if dolphinid in DolphinNameIds.values():
    name = Dolphins[dolphinid]["Name"]
    DolphinNameObservations[name][observationid] = entry
    DolphinNameObservations[name][observationid]["Associations"]    = []
    DolphinNameObservations[name][observationid]["BehaviourEvents"] = set()
    DolphinNameObservations[name][observationid]["BehaviourStates"] = set()



# Find all of the associated dolphins for each observation
Associations = readdb('Associations')
for associationid in Associations:
  curr_dolphinid = Associations[associationid]["AssociatedDolphinID"]
  if not curr_dolphinid in Dolphins.keys(): continue
  curr_name = Dolphins[curr_dolphinid]["Name"]
  if curr_name in DolphinNames:
    curr_observationid = Associations[associationid]["ObservationID"]
    for dolphinname in DolphinNameObservations:
      if curr_observationid in DolphinNameObservations[dolphinname].keys():
        DolphinNameObservations[dolphinname][curr_observationid]["Associations"].append(curr_name)



# Find all of the behaviours for each observation
BehaviourStates_OLD = readdb('BehaviourStates_OLD')
BehaviourEvents     = readdb('BehaviourEvents')
Occurences          = readdb('Occurences')
for occurenceid in Occurences:
  occurence = Occurences[occurenceid]
  curr_observationid = occurence["ObservationID"]
  for dolphinname in DolphinNameObservations:
    if curr_observationid in DolphinNameObservations[dolphinname]:
      try:
        DolphinNameObservations[dolphinname][curr_observationid]["BehaviourStates"].add(
            BehaviourStates_OLD[occurence["BehaviourStatesID"]]["BehaviourDescription"])
      except: pass
      try:
        DolphinNameObservations[dolphinname][curr_observationid]["BehaviourEvents"].add(
            BehaviourEvents[occurence["BehaviourEventsID"]]["EventDescription"])
      except: pass





