#!/usr/bin/python3

import sys
import getopt
import re
import os
import unicodedata
import subprocess
import filecmp

def build_tests():

  for file in os.listdir("./models"):
    if file.endswith(".model"):
      modelId = os.path.splitext(file)[0]
      build_test(modelId)
      run_test(modelId)
      if not filecmp.cmp("./tests/"+modelId+".inflected","./tests/"+modelId+".sample"):
        print("Les formes flexionades del model " + modelId + " no coincideixen")
      else:
        print("El fitxer " + modelId + ".inflected sembla correcte")
      #  print("No podem crear el test del model: " + modelId)

  return 0

def build_test(modelId):

  # Obrim el fitxer del model sol·licitat
  print("Realitzem el test del model flexiu: " + modelId)
  modelfile = open("./models/" + modelId + ".model", 'rt', encoding="utf-8")
  testfile = open("./tests/"+ modelId + ".test", 'w', encoding="utf-8")

  for line in modelfile:
    # Normalitzem les dades
    line = unicodedata.normalize('NFC',line).rstrip();

    # Expressió regular que captura la 1a línia:
    #   # 26 cantar
    n = re.match("^# ([0-9]+) ([^ ]+)$",line)

    if n:
      model = n.group(1)
      if model != modelId:
        print("!!! Hi ha una discrepància en el model: " + modelId + "!!!")
      sample = n. group(2)
      testfile.write(sample + "|test|" + model + '\n')

  # Tanquem els fitxers
  modelfile.close
  testfile.close

  return 0

def run_test(modelId):

  subprocess.run(["python3", "./parsedict.py", "-i", "./tests/" + modelId + ".test", "-o", "./tests/" + modelId + ".inflected"])
  return 0


build_tests()
