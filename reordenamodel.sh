import sys


def obtenir_clau_ordenacio(linea):
    camps = linea.strip().split()

    # Si la línia no té el format esperat (ex. capçaleres o comentaris inicials),
    # la mantenim a l'inici del fitxer.
    if len(camps) < 4 or not camps[3].startswith("VM"):
        return (0, 0, 0)

    etiqueta = camps[3]

    # 1. Determinació del grup principal segons la quarta columna (etiqueta VM)
    if etiqueta.startswith("VMN000"):
        grup = 1
    elif etiqueta.startswith("VMG000"):
        grup = 2
    elif etiqueta.startswith("VMP"):
        grup = 3
    elif etiqueta.startswith("VMIP"):
        grup = 4
    elif etiqueta.startswith("VMII"):
        grup = 5
    elif etiqueta.startswith("VMIS"):
        grup = 6
    elif etiqueta.startswith("VMIF"):
        grup = 7
    elif etiqueta.startswith("VMIC"):
        grup = 8
    elif etiqueta.startswith("VMSP"):
        grup = 9
    elif etiqueta.startswith("VMSI"):
        grup = 10
    elif etiqueta.startswith("VMM"):
        grup = 11
    else:
        grup = 12

    # Extraiem caràcters per posició (índex 0 de Python = posició 1 humana)
    pos5 = etiqueta[4] if len(etiqueta) > 4 else ""  # Posició 5: Persona (1, 2, 3)
    pos6 = etiqueta[5] if len(etiqueta) > 5 else ""  # Posició 6: Nombre (S, P)
    pos7 = etiqueta[6] if len(etiqueta) > 6 else ""  # Posició 7: Gènere (M, F)

    # 2. Criteris d'ordenació secundària dins de cada grup
    if grup == 3:  # Per a VMP (Participis)
        # Posició 6: S (1) primer que P (2)
        ordre_pos6 = 1 if pos6 == "S" else (2 if pos6 == "P" else 3)
        # Posició 7: M (1) primer que F (2)
        ordre_pos7 = 1 if pos7 == "M" else (2 if pos7 == "F" else 3)
        sub1, sub2 = ordre_pos6, ordre_pos7
    else:  # Per a la resta de grups
        # Posició 5: 1, 2, 3
        ordre_pos5 = int(pos5) if pos5 in "123" else 0
        # Posició 6: S (1) primer que P (2)
        ordre_pos6 = 1 if pos6 == "S" else (2 if pos6 == "P" else 3)
        sub1, sub2 = ordre_pos5, ordre_pos6

    return (grup, sub1, sub2)


def main():
    if len(sys.argv) < 2:
        print("Ús: python ordenar_verbs.py <ruta_del_fitxer>")
        sys.exit(1)

    ruta_fitxer = sys.argv[1]

    # Llegir el fitxer en UTF-8 i ignorar línies en blanc
    with open(ruta_fitxer, "r", encoding="utf-8") as f:
        linees = [linea.rstrip("\r\n") for linea in f if linea.strip()]

    # Reordenar les línies
    linees_ordenades = sorted(linees, key=obtenir_clau_ordenacio)

    # Reescriure el fitxer original en UTF-8 amb les línies ordenades
    with open(ruta_fitxer, "w", encoding="utf-8") as f:
        for linea in linees_ordenades:
            f.write(linea + "\n")

    print(
        f"Fitxer '{ruta_fitxer}' reordenat i desat amb èxit ({len(linees_ordenades)} línies)."
    )


if __name__ == "__main__":
    main()
