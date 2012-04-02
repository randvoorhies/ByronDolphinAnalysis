#!/usr/bin/env python

import csv
import numpy
import matplotlib.pyplot as plt
import json

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
    DolphinNameObservations[name][observationid]["BehaviourEvents"] = []
    DolphinNameObservations[name][observationid]["BehaviourStates"] = []



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
        DolphinNameObservations[dolphinname][curr_observationid]["BehaviourStates"].append(
            BehaviourStates_OLD[occurence["BehaviourStatesID"]]["BehaviourDescription"])
      except: pass
      try:
        DolphinNameObservations[dolphinname][curr_observationid]["BehaviourEvents"].append(
            BehaviourEvents[occurence["BehaviourEventsID"]]["EventDescription"])
      except: pass


plt.close()
BehaviourMatrices = {}
# Build the "confusion matrix" of dolphin interactions for each behavior type
for behaviourstateid in BehaviourStates_OLD:
  matrix = numpy.zeros((len(DolphinNames), len(DolphinNames)))
  behaviourdescr = BehaviourStates_OLD[behaviourstateid]["BehaviourDescription"]
  for dolphinname in DolphinNameObservations:
    dolphinidx = DolphinNames.index(dolphinname)

    for observationid in DolphinNameObservations[dolphinname]:
      if behaviourdescr in DolphinNameObservations[dolphinname][observationid]["BehaviourStates"]:
        matrix[dolphinidx, dolphinidx] += 1
        for associateddolphinname in DolphinNameObservations[dolphinname][observationid]["Associations"]:
          assc_dolphinidx = DolphinNames.index(associateddolphinname)
          if(dolphinidx > assc_dolphinidx):
            matrix[dolphinidx, assc_dolphinidx] += 1
          else:
            matrix[assc_dolphinidx, dolphinidx] += 1


  matrix = matrix + matrix.transpose()
  matrix[numpy.arange(len(matrix)), numpy.arange(len(matrix))] /=2

  fig = plt.figure()
  plt.clf()
  ax = fig.add_subplot(111)
  #ax.set_aspect(1)
  res = ax.imshow(matrix, cmap=plt.cm.jet, interpolation='nearest')
  (rows, cols) = matrix.shape
  for r in xrange(rows):
    for c in xrange(cols):
        ax.annotate(str(int(matrix[r,c])), xy=(c, r), 
                    horizontalalignment='center',
                    verticalalignment='center')

  plt.xticks(range(0, len(DolphinNames)), DolphinNames, rotation='vertical')
  plt.yticks(range(0, len(DolphinNames)), DolphinNames)
  plt.title(behaviourdescr)
  fig.subplots_adjust(left=.1, bottom=.3)
  plt.savefig(behaviourdescr+'.png', format='png')
 




  BehaviourMatrices[behaviourdescr] = matrix


#plt.show()

# Write the data to a JSON file
f = open('Data.json', 'w')
f.write(json.dumps(DolphinNameObservations, sort_keys=True, indent=4))
f.close()

