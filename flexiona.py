import os
import sys
import re
from collections import Counter

def carregar_models(directori_models):
    """
    Llegeix tots els fitxers .model del directori especificat i els desa en memòria.
    Retorna un diccionari amb les regles i el lema de referència si existeix.
    """
    models = {}
    
    if not os.path.isdir(directori_models):
        print(f"Error: El directori '{directori_models}' no existeix.", file=sys.stderr)
        return models

    for nom_fitxer in os.listdir(directori_models):
        if nom_fitxer.endswith('.model'):
            codi_model = nom_fitxer.split('.')[0]
            ruta_completa = os.path.join(directori_models, nom_fitxer)
            regles = []
            lema_model = None
            
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                for num_linia, linia in enumerate(f, 1):
                    linia_raw = linia.strip()
                    if not linia_raw:
                        continue
                    
                    # Captura del lema de referència a la primera línia (ex: # 66 envejar)
                    if num_linia == 1 and linia_raw.startswith('#'):
                        parts_capçalera = linia_raw.lstrip('#').strip().split()
                        if len(parts_capçalera) >= 2:
                            lema_model = parts_capçalera[1]
                        continue
                    
                    # Ignorem altres comentaris que no siguin de regles
                    if linia_raw.startswith('#'):
                        continue
                    
                    parts = linia_raw.split('#', 1)
                    if len(parts) < 2:
                        continue
                    
                    forma_esperada = parts[1].strip() # Paraula de control
                    camps_regla = parts[0].strip().split()
                    
                    if len(camps_regla) >= 4:
                        elidir = camps_regla[0]
                        afix = camps_regla[1]
                        condicio = camps_regla[2]
                        infogramatical = camps_regla[3]
                        
                        regles.append({
                            'elidir': '' if elidir == '0' else elidir,
                            'afix': '' if afix == '0' else afix,
                            'condicio': condicio,
                            'gramatica': infogramatical,
                            'esperada': forma_esperada,
                            'num_linia': num_linia
                        })
            
            models[codi_model] = {
                'lema_model': lema_model,
                'regles': regles
            }
            
    return models

def validar_condicio_hunspell(lema_base, condicio):
    """
    Avalua si un lema compleix la condició de la regla hunspell.
    Suporta tant expressions regulars (ex: [^sn]ar) com caràcters o sufixos simples.
    """
    if condicio == '.':
        return True
        
    try:
        if re.search(condicio + '$', lema_base):
            return True
        return False
    except re.error:
        return lema_base.endswith(condicio)

def aplicar_regla_hunspell(lema, regla):
    """
    Aplica una regla d'afix sobre un lema.
    Tant la condició com l'elisió actuen com a expressions regulars independents.
    """
    condicio_raw = regla['condicio']
    elidir_raw = regla['elidir']
    afix = regla['afix']
    
    # Gestió de lemes amb clítics/reflexius (-se)
    es_reflexiu = False
    lema_base = lema
    if lema.endswith('-se'):
        es_reflexiu = True
        lema_base = lema[:-3]

    # Funció interna per traduir la teva sintaxi [opcio1|opcio2] a la de regex (opcio1|opcio2)
    def preparar_regex(cadena_patro):
        if '[' in cadena_patro and '|' in cadena_patro and ']' in cadena_patro:
            return cadena_patro.replace('[', '(').replace(']', ')')
        return cadena_patro

    # 1. Validem primer la condició general (sobre el lema sencer)
    condicio_regex = preparar_regex(condicio_raw)
    if not validar_condicio_hunspell(lema_base, condicio_regex):
        return None

    # 2. Si es compleix la condició, mirem si podem aplicar l'elisió al final
    if elidir_raw:
        try:
            elidir_regex = preparar_regex(elidir_raw)
            patro_final = elidir_regex + '$'
            
            # Comprovem si el final del lema lliga amb la regex d'elisió
            if re.search(patro_final, lema_base):
                # Substituïm el fragment que coincideix amb la regex final per l'afix
                res = re.sub(patro_final, afix, lema_base)
                return res + '-se' if es_reflexiu else res
            else:
                # Si el lema complia la condició però no té el final a elidir, no s'aplica
                return None
        except re.error:
            # Fallback segur per si la regex estigués mal escrita al fitxer
            if lema_base.endswith(elidir_raw):
                res = lema_base[:-len(elidir_raw)] + afix
                return res + '-se' if es_reflexiu else res
            return None
    else:
        # Si no hi ha res a elidir, simplement enganxem l'afix
        res = lema_base + afix
        return res + '-se' if es_reflexiu else res
        
def validar_models_verbals(models):
    """
    Verifica que per als models 1-199 la flexió del lema propi del model 
    coincideixi exactament amb la forma esperada indicada a cada regla.
    Retorna una tupla: (errors_verbals, formes_per_model)
    """
    errors_verbals = []
    formes_per_model = {}
    
    for codi_model, dada in models.items():
        if codi_model.isdigit():
            num_model = int(codi_model)
            if 1 <= num_model <= 199:
                lema_ref = dada['lema_model']
                if not lema_ref:
                    errors_verbals.append((codi_model, 1, "Falta la capçalera amb el lema del model", "-", "-"))
                    continue
                
                comptador_formes_model = 0
                for regla in dada['regles']:
                    esperat_raw = regla['esperada']
                    es_alternativa = esperat_raw.startswith("ALT:")
                    
                    esperat = esperat_raw[4:].strip() if es_alternativa else esperat_raw
                    generat = aplicar_regla_hunspell(lema_ref, regla)
                    
                    if generat is None:
                        if es_alternativa:
                            continue
                        else:
                            errors_verbals.append((
                                codi_model,
                                regla['num_linia'],
                                lema_ref,
                                "[NO S'APLICA REGLA]",
                                esperat
                            ))
                    else:
                        comptador_formes_model += 1
                        if generat != esperat:
                            errors_verbals.append((
                                codi_model,
                                regla['num_linia'],
                                lema_ref,
                                generat,
                                esperat
                            ))
                
                formes_per_model[codi_model] = comptador_formes_model
                        
    return errors_verbals, formes_per_model

def validar_tests_verbals(models, directori_tests="./tests"):
    """
    Verifica els models verbals (1-199) contra els seus fitxers .test de referència.
    """
    incidencies_tests = []
    
    if not os.path.isdir(directori_tests):
        return incidencies_tests

    for codi_model, dada in models.items():
        if codi_model.isdigit():
            num_model = int(codi_model)
            if 1 <= num_model <= 199:
                fitxer_test = os.path.join(directori_tests, f"{codi_model}.test")
                
                if os.path.isfile(fitxer_test):
                    lema_ref = dada['lema_model']
                    if not lema_ref:
                        continue
                    
                    with open(fitxer_test, 'r', encoding='utf-8') as f_test:
                        esperades_test = set(line.strip() for line in f_test if line.strip() and not line.strip().startswith('#'))
                    
                    generades_model = set()
                    for regla in dada['regles']:
                        forma = aplicar_regla_hunspell(lema_ref, regla)
                        if forma:
                            generades_model.add(forma)
                    
                    falten = esperades_test - generades_model
                    sobren = generades_model - esperades_test
                    
                    if falten or sobren:
                        incidencies_tests.append({
                            'model': codi_model,
                            'lema': lema_ref,
                            'falten': sorted(list(falten)),
                            'sobren': sorted(list(sobren))
                        })
                        
    return incidencies_tests

def processar_diccionari(fitxer_entrades, directori_models, fitxer_sortida, fitxer_problemes, directori_tests="./tests"):
    """
    Llegeix les entrades, aplica els models, executa totes les validacions
    i genera un informe complet d'incidències a 'problemes.txt'.
    """
    print("Carregant models en memòria...")
    models = carregar_models(directori_models)
    
    print("Verificant integritat dels models verbals (1-199)...")
    errors_verbals, formes_per_model = validar_models_verbals(models)
    
    print("Verificant models verbals contra fitxers .test...")
    incidencies_tests = validar_tests_verbals(models, directori_tests)
    
    built_lines = 0
    models_no_trobats = Counter()
    anomalies_formes = []
    anomalies_paritat_verbal = []

    print("Processant entrades i generant flexions...")
    with open(fitxer_entrades, 'r', encoding='utf-8') as f_in, \
         open(fitxer_sortida, 'w', encoding='utf-8') as f_out:
             
        for num_linia, linia in enumerate(f_in, 1):
            linia = linia.strip()
            if (not linia or linia.startswith('#')):
                continue
                
            camps = linia.split('|')
            if len(camps) < 3:
                continue
                
            lema = camps[0]
            categoria = camps[1]
            codi_model = camps[2]
            
            lema_net = lema
            if lema.endswith("-se") and categoria == 'v.':
                lema_net = lema[:-3]
            elif (lema.endswith("’s") or lema.endswith("'s")) and categoria == 'v.':
                lema_net = lema[:-2]
            
            if codi_model in models:
                regles = models[codi_model]['regles']
                formes_generades = 0
                
                for regla in regles:
                    forma_flexionada = aplicar_regla_hunspell(lema_net, regla)
                    
                    if forma_flexionada is not None:
                        f_out.write(f"{forma_flexionada}|{lema}|{categoria}|{codi_model}|{regla['gramatica']}\n")
                        built_lines += 1
                        formes_generades += 1
                
                if codi_model.isdigit():
                    num_model = int(codi_model)
                    if 1 <= num_model <= 199:
                        esperades_model = formes_per_model.get(codi_model, 0)
                        if (formes_generades != esperades_model and not(num_model == 74 and lema.endswith("ànyer") and esperades_model-formes_generades == 1)):
                            anomalies_paritat_verbal.append((lema, codi_model, formes_generades, esperades_model, num_linia))
                
                if codi_model.isdigit():
                    num_model = int(codi_model)
                    
                    if 200 <= num_model <= 224:
                        if formes_generades != 2:
                            anomalies_formes.append((lema, codi_model, formes_generades, 2, num_linia))
                            
                    elif 225 <= num_model <= 299:
                        if formes_generades != 3:
                            anomalies_formes.append((lema, codi_model, formes_generades, 3, num_linia))
                    
                    elif (313 <= num_model <= 317) or num_model == 380:
                        if formes_generades != 5:
                            anomalies_formes.append((lema, codi_model, formes_generades, 5, num_linia))

                    elif num_model == 324 or num_model == 391:
                        if formes_generades != 6:
                            anomalies_formes.append((lema, codi_model, formes_generades, 6, num_linia))

                    elif 300 <= num_model <= 399:
                        if formes_generades != 4:
                            anomalies_formes.append((lema, codi_model, formes_generades, 4, num_linia))
                    else:
                    	if formes_generades == 0:
                    	    anomalies_formes.append((lema, codi_model, formes_generades, "X", num_linia))
            else:
                models_no_trobats[codi_model] += 1

    print("-" * 50)
    print(f"Procés completat correctament. S'han generat {built_lines} formes flexionades a '{fitxer_sortida}'.")
    
    with open(fitxer_problemes, 'w', encoding='utf-8') as f_prob:
        f_prob.write("==================================================\n")
        f_prob.write("INFORME D'INCIDÈNCIES I ANOMALIES DE FLEXIÓ\n")
        f_prob.write("==================================================\n\n")
        
        f_prob.write("1. DISCREPÀNCIES AMB FITXERS DE TEST (RANG 1-199)\n")
        f_prob.write("--------------------------------------------------\n")
        if incidencies_tests:
            f_prob.write(f"S'han trobat {len(incidencies_tests)} models verbals que no coincideixen amb el seu fitxer .test:\n\n")
            for inc in incidencies_tests:
                f_prob.write(f"MODEL {inc['model']} (Lema: '{inc['lema']}'):\n")
                if inc['falten']:
                    f_prob.write(f"  - Formes que ¿FALTEN? ({len(inc['falten'])}): {', '.join(inc['falten'])}\n")
                if inc['sobren']:
                    f_prob.write(f"  - Formes que ¿SOBREN? ({len(inc['sobren'])}): {', '.join(inc['sobren'])}\n")
                f_prob.write("\n")
        else:
            f_prob.write("Tots els models verbals amb fitxer .test generen exactament les formes esperades.\n")
            
        f_prob.write("\n\n")

        f_prob.write("2. DISCREPÀNCIES INTERNES EN MODELS VERBALS (RANG 1-199)\n")
        f_prob.write("--------------------------------------------------\n")
        if errors_verbals:
            f_prob.write(f"S'han trobat {len(errors_verbals)} errors de generació en les regles dels propis models verbals:\n\n")
            f_prob.write("MODEL\tLÍNIA\tLEMA REF.\tFORMA GENERADA\tFORMA ESPERADA\n")
            for mod, n_lin, lema_ref, gen, esp in errors_verbals:
                f_prob.write(f"{mod}\t{n_lin}\t{lema_ref}\t{gen}\t\t{esp}\n")
        else:
            f_prob.write("Tots els models verbals (1-199) generen exactament les formes esperades per línia de regla.\n")
        
        f_prob.write("\n\n")

        f_prob.write("2b. INCOMPLIMENT DE PARITAT AMB EL LEMA MODEL (RANG 1-199)\n")
        f_prob.write("--------------------------------------------------\n")
        if anomalies_paritat_verbal:
            f_prob.write(f"S'han trobat {len(anomalies_paritat_verbal)} lemes que generen un nombre de formes diferent al seu model de referència:\n\n")
            f_prob.write("LÍNIA\tLEMA\tMODEL\tFORMES GENERADES\tESPERADES (MODEL)\n")
            for lema, model, generades, esperades, n_lin in anomalies_paritat_verbal:
                f_prob.write(f"{n_lin}\t{lema}\t{model}\t{generades}\t\t\t{esperades}\n")
        else:
            f_prob.write("Tots els lemes verbals generen el memo nombre de formes que el seu model de referència.\n")

        f_prob.write("\n\n")

        f_prob.write("3. INCOMPLIMENT DE QUANTITAT DE FORMES DE CORD (RANGS 200-399)\n")
        f_prob.write("--------------------------------------------------\n")
        if anomalies_formes:
            f_prob.write(f"S'han trobat {len(anomalies_formes)} lemes com un nombre de formes inesperat:\n\n")
            f_prob.write("LÍNIA\tLEMA\tMODEL\tFORMES GENERADES\tESPERADES\n")
            for lema, model, generades, esperades, n_lin in anomalies_formes:
                f_prob.write(f"{n_lin}\t{lema}\t{model}\t{generades}\t\t\t{esperades}\n")
        else:
            f_prob.write("Tots els lemes dels rangs 200-299 i 300-399 compleixen les condicions de formes generades.\n")
        
        f_prob.write("\n\n")
        
        f_prob.write("4. MODELS MANCANTS (ORDENAT PER AFECTACIÓ)\n")
        f_prob.write("--------------------------------------------------\n")
        if models_no_trobats:
            f_prob.write(f"Total de codis de model diferents sense implementar: {len(models_no_trobats)}\n\n")
            f_prob.write("MODEL\tENTRADES AFECTADES\n")
            for model, quantitat in models_no_trobats.most_common():
                f_prob.write(f"{model}\t{quantitat}\n")
        else:
            f_prob.write("Tots els models requerits estan implementats correctament.\n")

    print(f"S'ha generat/actualitzat l'informe detallat a '{fitxer_problemes}'.")

if __name__ == "__main__":
    FITXER_ENTRADES = "entrades.txt"
    DIRECTORI_MODELS = "./models"
    DIRECTORI_TESTS = "./tests"
    FITXER_SORTIDA = "sortida.txt"
    FITXER_PROBLEMES = "problemes.txt"
    
    processar_diccionari(
        FITXER_ENTRADES, 
        DIRECTORI_MODELS, 
        FITXER_SORTIDA, 
        FITXER_PROBLEMES, 
        DIRECTORI_TESTS
    )
