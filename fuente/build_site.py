import os as _os; HERE = _os.path.dirname(_os.path.abspath(__file__)).replace('\\', '/')
"""Arma los datos de la página: site/data/censos.json y site/data/geo.json."""
import json, math, os, re, unicodedata

G = HERE + "/../geo/"
OUT = HERE + "/out/data/"
os.makedirs(OUT, exist_ok=True)
D0 = json.load(open(HERE + "/data.json", encoding="utf-8"))
M0 = {m["id"]: m for m in D0["meta"]}
PAIRS = ["2007-2017", "2017-2025", "2007-2025"]

# Materiales adecuados = reverso exacto del inadecuado: las categorías de material suman el total de viviendas
# ocupadas en los tres censos (sin "no sabe"), así que adecuado = VOP - inadecuado.
REV = {"PARADE": "PARINA", "TECADE": "TECINA", "PISADE": "PISTIE"}
for blk, nk in (("regions", "n"), ("provs", "n_"), ("dists", "n_")):
    B = D0[blk]
    for new, old in REV.items():
        B["v"][new] = []; B[nk][new] = []
        for vop_v, bad in zip(B["v"]["VOP"], B[nk][old]):
            n = [None if (t is None or b is None) else t - b for t, b in zip(vop_v, bad)]
            B[nk][new].append(n)
            B["v"][new].append([None if (x is None or not t) else round(100 * x / t, 1) for x, t in zip(n, vop_v)])
for new, old in REV.items():
    M0[new] = dict(M0[old], id=new)

# Educación (edu.json, de build_edu.py): no asisten de 6 a 16 años = 6-11 + 12-16, con el lector eligiendo las edades
# (bloque K, cada edad con su propio denominador). Los totales por edad van como series ocultas para las brechas.
E = json.load(open(HERE + "/edu.json", encoding="utf-8"))
def add3(a, b): return [None if (x is None or y is None) else x + y for x, y in zip(a, b)]
HID = ["P15", "P611", "P1216", "P616"]
for blk, nk, lev in (("regions", "n", "R"), ("provs", "n_", "P"), ("dists", "n_", "D")):
    B, e = D0[blk], E[lev]
    e["P616"] = [add3(a, b) for a, b in zip(e["P611"], e["P1216"])]
    num = [add3(a, b) for a, b in zip(e["NOA611"], e["NOA1216"])]
    B[nk]["NOA616"] = num
    B["v"]["NOA616"] = [[None if (x is None or not t) else round(100 * x / t, 1) for x, t in zip(n, d)] for n, d in zip(num, e["P616"])]
    for h in HID: B["v"][h] = e[h]; B[nk][h] = e[h]
M0["NOA616"] = dict(M0["NOA611"], id="NOA616", den="población de 6 a 16 años")
AGES = [("611", "NOA611", "P611", "6 a 11 años", "niños", "niños de 6 a 11 años"),
        ("1216", "NOA1216", "P1216", "12 a 16 años", "adolescentes", "adolescentes de 12 a 16 años")]
K_EDU = {"NOA616": dict(
    cats=[dict(id=c, label=lab, note="", years=[2007, 2017, 2025], den=d, cu=cu,
               lab=f"No asisten a la escuela ({lab})", long=f"el porcentaje de {who} que no asiste a la escuela",
               dentxt=f"población de {lab}", def_=f"{who[0].upper() + who[1:]} que no asisten a un centro educativo")
          for c, _, d, lab, cu, who in AGES],
    **{"def": ["611", "1216"], "den": "P616", "byage": True},
    **{lev: {c: E[lev][i] for c, i, *_ in AGES} for lev in ("R", "P", "D")})}

CATS = [
 ("Población y hogares", ["POB", "HOG", "URB", "MEN15", "MAY65", "JEFAM", "MIGR5", "NACEXT"]),
 ("Vivienda", ["VOP", "PARADE", "TECADE", "PISADE", "HACINA", "HAB1"]),
 ("Infraestructura y servicios básicos", ["SB3RP", "AGUARP", "DESRP", "ELECRP"]),
 ("Conectividad y bienes", ["CELUL", "INTFIJ", "PCLAP", "REFRI", "AUTO", "MOTO"]),
 ("Energía para cocinar", ["COMBCON", "LENA", "GLP"]),
 ("Educación", ["ANALF15", "NOA616", "ASISTE", "SUPER"]),
 ("Salud e identidad", ["SINSEG", "SIS", "ESSALUD", "SINDNI"]),
 ("Lengua materna", ["LM_QUE", "LM_CAST"]),
]
# etiqueta, título largo (para frases), dirección (+1 subir es mejora, -1 bajar es mejora, 0 neutro)
L = {
 "POB": ("Población censada", "la población censada", 0),
 "HOG": ("Hogares", "el número de hogares", 0),
 "URB": ("Población urbana", "el porcentaje de población urbana", 0),
 "MEN15": ("Menores de 15 años", "el porcentaje de menores de 15 años", 0),
 "MAY65": ("65 años a más", "el porcentaje de personas de 65 años a más", 0),
 "JEFAM": ("Hogares con jefa de hogar", "el porcentaje de hogares con jefa de hogar", 0),
 "MIGR5": ("Vivía en otro distrito o país hace 5 años", "el porcentaje de personas que vivía en otro distrito o país cinco años antes", 0),
 "NACEXT": ("Nacidos en otro país", "el porcentaje de personas nacidas en otro país", 0),
 "VOP": ("Viviendas ocupadas", "el número de viviendas ocupadas", 0),
 "PARADE": ("Paredes adecuadas", "el porcentaje de viviendas con paredes de material adecuado", 1),
 "TECADE": ("Techos adecuados", "el porcentaje de viviendas con techo de concreto armado", 1),
 "PISADE": ("Pisos adecuados", "el porcentaje de viviendas con piso adecuado", 1),

 "HACINA": ("Hacinamiento", "el porcentaje de viviendas hacinadas", -1),
 "HAB1": ("Vivienda de una sola habitación", "el porcentaje de viviendas de una sola habitación", -1),
 "SB3RP": ("Tres servicios básicos (agua, desagüe y luz)", "el porcentaje de viviendas con agua, desagüe y luz por red pública", 1),
 "AGUARP": ("Agua por red pública", "el porcentaje de viviendas con agua por red pública", 1),
 "DESRP": ("Desagüe por red pública", "el porcentaje de viviendas con desagüe por red pública", 1),
 "ELECRP": ("Electricidad por red pública", "el porcentaje de viviendas con electricidad por red pública", 1),
 "CELUL": ("Celular", "el porcentaje de hogares con celular", 1),
 "INTFIJ": ("Internet en el hogar", "el porcentaje de hogares con internet", 1),
 "PCLAP": ("Computadora, laptop o tablet", "el porcentaje de hogares con computadora, laptop o tablet", 1),
 "REFRI": ("Refrigeradora", "el porcentaje de hogares con refrigeradora", 1),
 "AUTO": ("Auto o camioneta", "el porcentaje de hogares con auto o camioneta", 0),
 "MOTO": ("Motocicleta", "el porcentaje de hogares con motocicleta", 0),
 "COMBCON": ("Cocinan con combustibles contaminantes", "el porcentaje de hogares que cocinan con combustibles contaminantes", -1),
 "LENA": ("Cocinan con leña", "el porcentaje de hogares que cocinan con leña", -1),
 "GLP": ("Cocinan con gas (balón)", "el porcentaje de hogares que cocinan con gas de balón", 1),
 "ANALF15": ("Analfabetismo (15 años a más)", "la tasa de analfabetismo de la población de 15 años a más", -1),
 "NOA616": ("No asisten a la escuela (6 a 16 años)", "el porcentaje de niños y adolescentes de 6 a 16 años que no asiste a la escuela", -1),
 "ASISTE": ("Asiste a un centro educativo (3 años a más)", "el porcentaje de personas de 3 años a más que asiste a un centro educativo", 0),
 "SUPER": ("Con educación superior (3 años a más)", "el porcentaje de personas con educación superior", 1),
 "SINSEG": ("Sin seguro de salud", "el porcentaje de personas sin seguro de salud", -1),
 "SIS": ("Afiliados al SIS", "el porcentaje de personas afiliadas al SIS", 0),
 "ESSALUD": ("Afiliados a EsSalud", "el porcentaje de personas afiliadas a EsSalud", 0),
 "SINDNI": ("Sin ningún documento de identidad", "el porcentaje de personas sin ningún documento de identidad", -1),
 "LM_QUE": ("Lengua materna quechua", "el porcentaje de personas con quechua como lengua materna", 0),
 "LM_CAST": ("Lengua materna castellano", "el porcentaje de personas con castellano como lengua materna", 0),
}
CU = {"viviendas particulares con ocupantes presentes": "viviendas", "viviendas con agua por red pública o pilón": "viviendas",
      "hogares": "hogares", "mujeres de 12 años a más": "mujeres", "población de 6 a 16 años": "niños y adolescentes"}
COUNT_UNIT = {"POB": "personas", "HOG": "hogares", "VOP": "viviendas"}
IDS = [i for _, l in CATS for i in l]

def clean(t):
    t = t or ""
    if t.startswith("="): t = "Misma definición" + t[1:]
    elif t.startswith("≈"): t = "Similar" + t[1:]
    elif t.startswith("X"): t = "No existe" + t[1:]
    return t.replace("( ", "(").strip()

SIM07 = "Similar: en 2007 no existía la opción triplay/calamina."
COC07 = "No comparable: en 2007 se preguntó solo por la energía principal para cocinar; desde 2017, por todas las que usa el hogar."
LM2 = "No comparable: en 2025 se puede declarar más de una lengua materna y el castellano sube por las respuestas múltiples."
NOTES = {
 "PARADE": {"2007-2017": "Misma definición: los materiales adecuados (ladrillo o bloque, piedra o sillar con cal o cemento) son opciones en los tres censos.", "2017-2025": "Misma definición. En 2025 el drywall, que aparece como opción aparte, cuenta como adecuado (0.2% de las viviendas).", "2007-2025": "Misma definición. En 2025 el drywall, que aparece como opción aparte, cuenta como adecuado (0.2% de las viviendas)."},
 "TECADE": {"2007-2017": "No existe en 2007: ese censo no preguntó el material del techo.", "2007-2025": "No existe en 2007: ese censo no preguntó el material del techo.", "2017-2025": "Misma definición."},
 "PISADE": {"2007-2017": "Misma definición.", "2017-2025": "Misma definición.", "2007-2025": "Misma definición."},
 "AGUARP": {"2007-2017": "Misma definición. El agua del vecino es una opción aparte y no se cuenta.", "2017-2025": "Misma definición. En 2017 el agua del vecino era una opción aparte y no se cuenta; en 2025 la pregunta va en dos pasos (red pública y luego dentro o fuera de la vivienda).", "2007-2025": "Misma definición. En 2025 la pregunta va en dos pasos (red pública y luego dentro o fuera de la vivienda)."},
 "DESRP": {"2007-2017": "Misma definición.", "2017-2025": "Misma definición. 2025 dice 'dentro del lote o terreno' donde 2017 decía 'dentro de la edificación'.", "2007-2025": "Misma definición. 2025 dice 'dentro del lote o terreno' donde 2007 decía 'dentro de la edificación'."},
 "ELECRP": {"2007-2017": "Misma definición: la misma pregunta en ambos censos.", "2017-2025": "Similar: 2007 y 2017 preguntaron si la vivienda tenía alumbrado eléctrico por red pública (sí o no); 2025 pregunta de dónde proviene principalmente la energía eléctrica (red pública, panel solar, generador u otro).", "2007-2025": "Similar: 2007 y 2017 preguntaron si la vivienda tenía alumbrado eléctrico por red pública (sí o no); 2025 pregunta de dónde proviene principalmente la energía eléctrica (red pública, panel solar, generador u otro)."},
 "SB3RP": {"2007-2017": "Misma definición.", "2017-2025": "Similar: agua y desagüe tienen la misma definición; la luz cambió de pregunta (2007 y 2017: alumbrado eléctrico por red pública, sí o no; 2025: fuente principal de energía eléctrica, red pública).", "2007-2025": "Similar: agua y desagüe tienen la misma definición; la luz cambió de pregunta (2007 y 2017: alumbrado eléctrico por red pública, sí o no; 2025: fuente principal de energía eléctrica, red pública)."},
 "INTFIJ": {"2007-2017": "Misma definición.", "2017-2025": "Similar: 2007 y 2017 preguntaron si el hogar tenía conexión a internet, sin separar fijo y móvil; 2025 pregunta por internet fijo y por internet móvil por separado, y aquí se suman (el hogar tiene uno u otro). Parte del salto puede deberse al cambio de pregunta: en 2017 algunos hogares con solo datos en el celular pudieron responder que no.", "2007-2025": "Similar: 2007 y 2017 preguntaron si el hogar tenía conexión a internet, sin separar fijo y móvil; 2025 pregunta por internet fijo y por internet móvil por separado, y aquí se suman (el hogar tiene uno u otro). Parte del salto puede deberse al cambio de pregunta: en 2017 algunos hogares con solo datos en el celular pudieron responder que no."},
 "PCLAP": {"2007-2017": "No comparable: en 2007 solo se preguntó por computadora.", "2007-2025": "No comparable: en 2007 solo se preguntó por computadora."},
 "AUTO": {"2007-2017": "No existe en 2007.", "2007-2025": "No existe en 2007."},
 "MOTO": {"2007-2017": "No existe en 2007.", "2007-2025": "No existe en 2007."},
 "COMBCON": {"2007-2017": COC07, "2007-2025": COC07, "2017-2025": "Misma definición."},
 "LENA": {"2007-2017": COC07, "2007-2025": COC07},
 "GLP": {"2007-2017": COC07, "2007-2025": COC07},
 "SUPER": {"2007-2017": "No comparable: en 2007 los niveles educativos se clasificaban de otra forma.", "2007-2025": "No comparable: en 2007 los niveles educativos se clasificaban de otra forma.", "2017-2025": "Misma definición."},
 "SINDNI": {"2007-2017": "No comparable: en 2007 solo se preguntó por el DNI a mayores de 18 años, sin preguntar por otros documentos.", "2007-2025": "No comparable: en 2007 solo se preguntó por el DNI a mayores de 18 años, sin preguntar por otros documentos.", "2017-2025": "Misma definición. En 2025 se agrega el permiso temporal de permanencia, que tienen solo extranjeros."},
 "LM_QUE": {"2017-2025": "Misma definición, pero en 2025 se puede declarar más de una lengua materna.", "2007-2025": "Misma definición, pero en 2025 se puede declarar más de una lengua materna."},
 "LM_CAST": {"2017-2025": LM2, "2007-2025": LM2},
 "URB": {"2017-2025": "Misma definición.", "2007-2025": "Misma definición."},
}
EXTRA = {
 "POB": "Población censada, sin la estimación de población omitida. La población total oficial fue 28,220,764 (2007), 31,237,385 (2017) y 34,157,732 (2025).",
 "NACEXT": "En 2007 y 2017 el lugar de nacimiento es donde vivía la madre al nacer; en 2025 se pregunta si nació en otro país.",
}
CMP = {"INTFIJ": {"2007-2017": True, "2017-2025": True, "2007-2025": True}}
def note_for(i, p, m):
    if i in NOTES and p in NOTES[i]: return NOTES[i][p]
    if m["cmp"][p]: return "Similar." if clean({"2007-2017": m["n1707"], "2017-2025": m["n1725"], "2007-2025": m["n0725"]}[p]).startswith("Similar") else "Misma definición."
    y = [int(x) for x in p.split("-")]
    miss = [x for x in y if x not in m["years"]]
    return f"No existe en {miss[0]}." if miss else "No comparable: la pregunta cambió."
DEF = {
 "POB": "Población censada", "HOG": "Hogares en viviendas particulares con ocupantes presentes", "URB": "Población que vive en área urbana, según la definición del censo",
 "MEN15": "Población de 0 a 14 años", "MAY65": "Población de 65 años a más", "JEFAM": "Hogares cuya jefa de hogar es mujer",
 "MIGR5": "Personas de 5 años a más que vivían en otro distrito o país cinco años antes del censo", "NACEXT": "Personas nacidas en otro país",
 "VOP": "Viviendas particulares con ocupantes presentes el día del censo (no incluye viviendas desocupadas ni colectivas)",
 "PARADE": "Viviendas cuyas paredes exteriores son de ladrillo o bloque de cemento, o de piedra o sillar con cal o cemento (en 2025 también drywall). Se consideran no adecuadas, por su vulnerabilidad ante sismos y lluvias, las de adobe, tapia, quincha, piedra con barro, madera, triplay, calamina, estera u otro material",
 "TECADE": "Viviendas con techo de concreto armado. Se consideran no adecuados la madera, las tejas, las planchas de calamina o fibrocemento, la caña o estera con torta de barro, el triplay, la estera o el carrizo, la paja u hojas de palmera, el drywall y otros materiales",
 "PISADE": "Viviendas con piso de parquet o madera pulida, láminas asfálticas o vinílicos, o losetas, terrazos o cerámicos (agrupación del INEI). No incluye cemento, madera en entablado, tierra ni otros materiales",
 "HACINA": "Viviendas con más de 3.4 personas por habitación (sin contar baño, cocina ni pasadizos), el umbral de hacinamiento del INEI", "HAB1": "Viviendas que tienen una sola habitación en total",
 "SB3RP": "Viviendas con agua por red pública, desagüe por red pública y electricidad por red pública, los tres a la vez. Agua y desagüe cuentan dentro de la vivienda o fuera de ella pero dentro de la edificación o del lote",
 "AGUARP": "Viviendas con agua por red pública, dentro de la vivienda o fuera de ella pero dentro de la edificación (2025: dentro del lote o terreno). No incluye pilón de uso público, camión cisterna, pozo, río ni vecino",
 "DESRP": "Viviendas con servicio higiénico conectado a la red pública de desagüe, dentro de la vivienda o fuera de ella pero dentro de la edificación (2025: dentro del lote o terreno). No incluye pozo séptico, letrina ni pozo ciego",
 "ELECRP": "Viviendas con electricidad por red pública (2007 y 2017: alumbrado eléctrico por red pública; 2025: la red pública es la fuente principal de energía eléctrica)", "CELUL": "Hogares con al menos un teléfono celular", "INTFIJ": "Hogares con conexión a internet (2007 y 2017: conexión a internet; 2025: internet fijo o móvil)",
 "PCLAP": "Hogares con computadora, laptop o tablet", "REFRI": "Hogares con refrigeradora o congeladora", "AUTO": "Hogares con automóvil o camioneta",
 "MOTO": "Hogares con motocicleta", "COMBCON": "Hogares que cocinan solo con leña, carbón, bosta u otro combustible contaminante, sin gas ni electricidad",
 "LENA": "Hogares que cocinan con leña", "GLP": "Hogares que cocinan con gas de balón", "ANALF15": "Personas de 15 años a más que no saben leer ni escribir",
 "NOA616": "Niños y adolescentes de 6 a 16 años que no asisten a un centro educativo. Se pueden ver por separado los de 6 a 11 años (edad de primaria) y los de 12 a 16 años (edad de secundaria)",
 "ASISTE": "Personas de 3 años a más que asisten a un colegio, instituto o universidad", "SUPER": "Personas de 3 años a más con educación superior, completa o incompleta",
 "SINSEG": "Personas sin ningún seguro de salud", "SIS": "Personas afiliadas al Seguro Integral de Salud", "ESSALUD": "Personas afiliadas a EsSalud",
 "SINDNI": "Personas que no tienen DNI ni ningún otro documento (partida de nacimiento, carné de extranjería o permiso temporal). No cuenta a los extranjeros, que no pueden tener DNI, ni a quienes respondieron que no recuerdan o no saben qué documento tienen (2.7 millones en 2025), una respuesta ambigua", "LM_QUE": "Personas de 3 años a más cuya lengua materna es el quechua",
 "LM_CAST": "Personas de 3 años a más cuya lengua materna es el castellano",
}
# Frase de "lo que falta": (texto, id del total). Solo indicadores con meta clara y total en la página.
GAP = {
 "PARADE": ("aún no tenían paredes adecuadas", "VOP"), "TECADE": ("aún no tenían techo de concreto", "VOP"), "PISADE": ("aún no tenían piso adecuado", "VOP"),
 "HACINA": ("aún estaban hacinadas", "VOP"), "SB3RP": ("aún no tenían los tres servicios básicos", "VOP"),
 "AGUARP": ("aún no tenían agua por red pública", "VOP"), "DESRP": ("aún no tenían desagüe por red pública", "VOP"), "ELECRP": ("aún no tenían electricidad por red pública", "VOP"),
 "CELUL": ("aún no tenían celular", "HOG"), "INTFIJ": ("aún no tenían internet", "HOG"), "PCLAP": ("aún no tenían computadora, laptop ni tablet", "HOG"),
 "REFRI": ("aún no tenían refrigeradora", "HOG"), "COMBCON": ("aún cocinaban solo con combustibles contaminantes", "HOG"), "LENA": ("aún cocinaban con leña", "HOG"),
 "SINSEG": ("aún no tenían seguro de salud", "POB"), "SINDNI": ("aún no tenían ningún documento de identidad", "POB"),
 "ANALF15": ("aún no sabían leer ni escribir", "P15"), "NOA616": ("aún no asistían a la escuela", "P616"),
}
meta = []
for cat, ids in CATS:
    for i in ids:
        m = M0[i]
        cu = COUNT_UNIT.get(i) or CU.get(m["den"], "personas")
        meta.append(dict(id=i, cat=cat, label=L[i][0], long=L[i][1], dir=L[i][2], unit=m["unit"], den=m["den"],
                         cu=cu, years=m["years"], cmp=CMP.get(i, m["cmp"]), def_=DEF[i],
                         notes={p: note_for(i, p, m) for p in PAIRS},
                         extra=EXTRA.get(i, ""), **({"gap": GAP[i][0], "dk": GAP[i][1]} if i in GAP else {})))

def pick(block, key, idx=None):
    return {i: block[key][i] for i in IDS + HID}

R = D0["regions"]; P = D0["provs"]; DI = D0["dists"]
def norm(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())

old = []
for k in range(len(DI["u"])):
    o = []
    if DI["n07"][k] and norm(DI["n07"][k]) != norm(DI["n"][k]): o.append(f"2007: {DI['n07'][k]}")
    if DI["n17"][k] and norm(DI["n17"][k]) != norm(DI["n"][k]): o.append(f"2017: {DI['n17'][k]}")
    old.append("; ".join(o))

# ---------- comparabilidad por distrito ----------
# Antes: si en una provincia se creaba un distrito, toda la provincia quedaba sin comparar.
# Ahora solo quedan fuera, en cada par de censos: el distrito nuevo, su distrito de origen (ley de creación,
# distritos_origen.tsv) y, por prudencia, los distritos de esa provincia que perdieron más de 30% de su población.
import csv
U = DI["u"]; IX = {u: k for k, u in enumerate(U)}; NAME = dict(zip(U, DI["n"]))
POBV = DI["v"]["POB"]; e07 = [x is not None for x in DI["n07"]]; e17 = [x is not None for x in DI["n17"]]
period = {}   # distrito nuevo -> periodo en que aparece
for k, u in enumerate(U):
    if not e07[k] and e17[k]: period[u] = "2007-2017"
    elif not e17[k]: period[u] = "2017-2025"
origin = {}   # distrito nuevo -> [distritos de origen]
for row in csv.DictReader(open(HERE + "/distritos_origen.tsv", encoding="utf-8"), delimiter="\t"):
    if row["ubigeo_nuevo"] in period and row["ubigeos_origen"]:
        origin[row["ubigeo_nuevo"]] = [x.strip() for x in row["ubigeos_origen"].split(",") if x.strip() in IX]
origin.setdefault("050104", []).append("050101")   # Carmen Alto: en la base 2007 va dentro del distrito Ayacucho
EXTRA_07 = {"120606": "Recibió la zona en límite Mazamari–Pangoa que el censo 2007 registró aparte.",
            "100603": "Cedió el centro poblado Margarita al distrito Irazola (Ucayali) en 2015."}
SUB = {"2007-2017": ["2007-2017"], "2017-2025": ["2017-2025"], "2007-2025": ["2007-2017", "2017-2025"]}
YI = {"2007": 0, "2017": 1, "2025": 2}
comp, why = {}, {}
for p in PAIRS:
    a, b = YI[p[:4]], YI[p[5:]]
    c = [1] * len(U); w = [""] * len(U)
    for sub in SUB[p]:
        news = [u for u, per in period.items() if per == sub]
        kids = {}
        for nu in news:
            for o in origin.get(nu, []): kids.setdefault(o, []).append(NAME[nu])
        for o, ns in kids.items():
            k = IX[o]; c[k] = 0
            lst = ns[0] if len(ns) == 1 else ", ".join(ns[:-1]) + " y " + ns[-1]
            txt = f"De este distrito {'salió' if len(ns) == 1 else 'salieron'} {lst} entre {sub.replace('-', ' y ')}"
            w[k] = (w[k] + "; " if w[k] else "") + txt
        for pr in {u[:4] for u in news}:   # distritos de la provincia con caída fuerte de población
            sa, sb = YI[sub[:4]], YI[sub[5:]]
            for k, u in enumerate(U):
                if u[:4] != pr or not c[k] or u in period and period[u] in SUB[p]: continue
                x0, x1 = POBV[k][sa], POBV[k][sb]
                if x0 and x1 is not None and x1 < 0.7 * x0:
                    c[k] = 0; w[k] = f"Perdió {round(100 * (1 - x1 / x0))}% de su población entre {sub.replace('-', ' y ')}, en una provincia donde se crearon distritos: pudo ceder territorio"
    if a == 0:
        for u, t in EXTRA_07.items(): k = IX[u]; c[k] = 0; w[k] = (w[k] + "; " if w[k] else "") + t
        k = IX["010201"]; c[k] = 0; w[k] = "En 2007 este código era el distrito La Peca, que incluía la ciudad de Bagua; en 2008 se separaron Bagua y La Peca"
    for u, per in period.items():
        if per in SUB[p] or (a == 0 and per == "2007-2017"): c[IX[u]] = 0
    comp[p] = c; why[p] = w
    old_n = sum(1 for x in DI["comp"][p] if not x); new_n = sum(1 for k, x in enumerate(c) if not x and not (u := U[k]) in period)
    print(p, "distritos sin comparar antes:", old_n, "ahora (sin contar los nuevos):", new_n)

data = dict(
    meta=meta, cats=[c for c, _ in CATS],
    R=dict(names=R["names"], v=pick(R, "v"), n=pick(R, "n")),
    P=dict(u=P["u"], r=P["r"], n=P["n"], v=pick(P, "v"), c=pick(P, "n_")),
    D=dict(u=DI["u"], r=DI["r"], n=DI["n"], old=old,
           e07=[x is not None for x in DI["n07"]], e17=[x is not None for x in DI["n17"]],
           comp=comp, why=why,
           v=pick(DI, "v"), c=pick(DI, "n_")),
    alerts={p: D0["alert_summary"][p] for p in PAIRS},
    K=K_EDU,
)
s = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
open(OUT + "censos.json", "w", encoding="utf-8").write(s); print("censos.json", round(len(s) / 1e6, 2), "MB")


