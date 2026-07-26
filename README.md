# disc
Eines per a generar el DISC. Un llistat de paraules basat en el DIEC per a jocs tipus Scrabble®

## Requeriments
python3

## Ús

Per a generar les formes flexionades del DISC:
python3 flexiona.py

Això flexiona els lemes del fitxer entrades.txt i desa les formes flexionades a sortida.txt. Els possibles problemes detectats es desen a problemes.txt

# Models flexius

Els models flexius són regles tipus hunspell. Un fitxer per a cada codi de model flexiu a ./models

# Controls

Per als models verbas el flexionador comprova que:
- El verb model genera les formes esperades.
- Els verbs amb el mateix codi generen el mateix nombre de formes que el verb model.
- Discrepàncies entre les formes úniques generades i les esperades (disponbiles a ./tests)

## Com col·laborar

Podeu revisar el fitxer problemes.txt.
- Formes que ¿SOBREN?: indica formes que sí que es generen però no s'esperen. Si són correctes, cal afegir-les formes al fitxer ./tests. Si són incorrectes cal corregir les regles flexives a ./models
- Formes que ¿FALTEN?: indica formes que no es generen, però que sí s'esperen. Si són correctes, cal corregir les regles flexives a ./models. Si són incorrectes cal suprimir-les del fitxer ./tests

