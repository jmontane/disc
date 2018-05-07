#!/usr/bin/python3

import sys
import getopt
import re
import os
import unicodedata

def load_models():

  models = {}
  for file in os.listdir("./models"):
    if file.endswith(".model"):
      modelId = os.path.splitext(file)[0]
      #models.append(number)
      model = load_model(modelId)
      models[modelId] = model

  return models

def load_model(modelId):
  model =[]
  # Obrim el fitxer del model sol·licitat
  #print("Carreguem el model flexiu: " + modelId)
  file = open("./models/" + modelId + ".model", 'rt', encoding="utf-8")

  for line in file:
    # Normalitzem les dades
    line = unicodedata.normalize('NFC',line)

    # Expressió regular que captura la 1a línia:
    #   # 26 cantar
    n = re.match("^# [0-9]+ [^ ]+$",line)

    # Expressió regular que captura les línies que defineixen el model flexiu:
    #   r r ar VMN00000 # cantar
    m = re.match("^([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+) # ([^ ]+)$",line)
 
    # Si tenim una línia de flexió...
    if m:
      remove = m.group(1)
      if remove == "0":
        remove = "$"
      else:
        remove = remove + "$"

      add = m.group(2)
      if add == "0":
        add = ""

      condition = "^.*" + m.group(3) + "$"
      grammar = m.group(4)
      comment = m.group(5)

      # ...desem els 4 camps en un array, i ho afegit al model
      model.append([remove,add,condition,grammar])
    # Si tenim la 1a lína del model
    #elif n:
      

  # Tanquem el fitxer
  file.close

  # Retornem el model carregat en un array.
  return model


def inflection(fields, models):
  lemma = fields[0]
  pos = fields[1]
  modelId = fields[2]
  reference = fields[3]
  
  inflectedforms = []

  # En cas de tenir un verb pronominal, suprimim el pronom del lema abans de flexionar-lo
  if ((pos == "v." or pos == "v") and re.match(".*'s$|.*-se$",lemma)):
     lemma = re.sub ("'s$|-se$","",lemma)

  # Variable de control
  flag = 0

  if modelId not in models:
    print("Manca el model: " + modelId)
    return 1

  # Recorrem totes les regles del model flexiu  
  for element in models[modelId]:
    remove = element[0]
    add = element[1]
    condition = element[2]
    grammar = element[3]
    
    # Apliquem les regles on es compleixi la condició
    if re.match(condition,lemma):
      # Si apliquem alguna regla marquem la bandera de control
      flag = 1
      inflected = re.sub(remove, add, lemma)
      # Generem la forma flexionada corresponent 
      inflectedforms.append(inflected + "|" + pos  + "|" + modelId  + "|" + grammar  + "|" + reference)


  # Si flag == 0 vol dir que no hem aplicat cap regla i el model no encaixa amb l'entrada, cal revisar-ho
  if flag == 0:
    print("Error: reviseu el model flexiu assignat a l'entrada «" + lemma +"»" + pos + " " + modelId + " " + grammar)
    return 1

  return inflectedforms

def parsedictfile(inputfile, outputfile):

  # Obrim el fitxer amb les entrades
  disc = open(inputfile, 'rt', encoding="utf-8")
  discout = open(outputfile, 'w', encoding="utf-8")

  myEntries = []
  myModels = {}

  myModels = load_models()

  for entry in disc:
    # Normalitzem les dades
    entry = unicodedata.normalize('NFC', entry)
    entry = entry.rstrip()

    # Fem una petita comprovació que la línia compleix algun dels 2 formats següents:
    #   entrada|categoria|model flexiu
    #   entrada|categoria|model flexiu|referència
    # En aquest cas, és una entrada del diccionari, la processem
    if re.match("^[^#]+\|.+\|[0-9]+(\|.+)?$", entry):
      myFields = []
      myFields = entry.split("|")

      if len(myFields) == 3:
        myFields.append(myFields[0])
 
      # Generem les formes flexionades de l'entrada
      inflected = []
      inflected = inflection(myFields, myModels)
      # Escrivim les formes flexionades al fitxer de sortida, si n'hi ha
      if inflected == 1:
        print("Cal revisar això: "+ entry);
      else:
        for element in inflected:
          discout.write(element+'\n')



    # Si la línia no comença amb #, cal revisar-la
    elif not re.match("^[ \t]*#.*$", entry):
      print("Cal revisar aquesta línia: ",entry)

  # Tanquem els fitxers  
  disc.close()
  discout.close()


def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print('parsedict.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('parsedict.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   # print("El fitxer d'entrada és: " + inputfile)
   # print("El fitxer de sortida és: " + outputfile)

   parsedictfile(inputfile, outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])
