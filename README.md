# DISC

Eines per a generar el DISC. Un llistat de paraules basat en el DIEC per a jocs tipus Scrabble®

## Requeriments

python 3

## Ús

Per a generar les formes flexionades del DISC:
python parsedict.py -i entries.txt -o inflected.txt

On entries.txt són les entrades que volem flexionar i inflected.txt és el resultat amb les formes flexionades.

Nota: encara no tenim codificats tots els models flexius. Per tant, encara no podem generar tot el DISC.

## Proves

Podem fer un control superfícial en tots els models flexius:

python test.py

Això flexiona tots els ./tests/*.test, generant els *.inflected i els compara amb el resultat esperat *.sample

## Més proves

Tenim un llistat reduit d'entrades, test-entries.txt, podem flexionar aquest llistat per a agilitzar les proves:

python parsedict.py -i test-entries.txt -o test-inflected.txt

## Com col·laborar

Podeu revisar que els fitxers tests/*.sample siguin correctes.
Podeu ajudar a codificar els models flexius que falten. Cada model flexiu és defeneix amb un fitxer /models/*.model
Qualsevol altra ajuda és útil.


