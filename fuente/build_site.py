"""Arma los datos de la página: site/data/censos.json y site/data/geo.json."""
import json, math, os, re, unicodedata

G = "/tmp/claude-0/-home-claude/1417c317-d5e8-5ec7-b3d0-d63f525322f7/scratchpad/geo/"
OUT = "/home/claude/web/site/data/"
os.makedirs(OUT, exist_ok=True)
D0 = json.load(open("/home/claude/web/data.json"))
M0 = {m["id"]: m for m in D0["meta"]}
PAIRS = ["2007-2017", "2017-2025", "2007-2025"]

CATS = [
 ("Población y hogares", ["POB", "HOG", "URB", "MEN15", "MAY65", "JEFAM", "MIGR5", "NACEXT"]),
 ("Vivienda", ["VOP", "PARNOB", "PARINA", "TECINA", "PISTIE", "HACINA", "HAB1"]),
 ("Infraestructura y servicios básicos", ["SB3RP", "AGUARP", "DESRP", "ELECRP"]),
 ("Conectividad y bienes", ["CELUL", "INTFIJ", "PCLAP", "REFRI", "AUTO", "MOTO"]),
 ("Energía para cocinar", ["COMBCON", "LENA", "GLP"]),
 ("Educación", ["ANALF15", "NOA611", "NOA1216", "ASISTE", "SUPER"]),
 ("Salud e identidad", ["SINSEG", "SIS", "ESSALUD", "SINDNI"]),
 ("Lengua materna", ["LM_QUE", "LM_CAST"]),
 ("Empleo (2007–2017)", ["PEA14", "DES14"]),
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
 "PARNOB": ("Paredes de material noble", "el porcentaje de viviendas con paredes de material noble", 1),
 "PARINA": ("Paredes inadecuadas", "el porcentaje de viviendas con paredes inadecuadas", -1),
 "TECINA": ("Techo inadecuado", "el porcentaje de viviendas con techo inadecuado", -1),
 "PISTIE": ("Piso de tierra", "el porcentaje de viviendas con piso de tierra", -1),
 "HACINA": ("Hacinamiento", "el porcentaje de viviendas hacinadas", -1),
 "HAB1": ("Vivienda de una sola habitación", "el porcentaje de viviendas de una sola habitación", -1),
 "SB3RP": ("Tres servicios básicos (agua, desagüe y luz)", "el porcentaje de viviendas con agua, desagüe y luz por red pública", 1),
 "AGUARP": ("Agua por red pública", "el porcentaje de viviendas con agua por red pública", 1),
 "DESRP": ("Desagüe por red pública", "el porcentaje de viviendas con desagüe por red pública", 1),
 "ELECRP": ("Electricidad por red pública", "el porcentaje de viviendas con electricidad por red pública", 1),
 "CELUL": ("Celular", "el porcentaje de hogares con celular", 1),
 "INTFIJ": ("Internet", "el porcentaje de hogares con internet", 1),
 "PCLAP": ("Computadora, laptop o tablet", "el porcentaje de hogares con computadora, laptop o tablet", 1),
 "REFRI": ("Refrigeradora", "el porcentaje de hogares con refrigeradora", 1),
 "AUTO": ("Auto o camioneta", "el porcentaje de hogares con auto o camioneta", 0),
 "MOTO": ("Motocicleta", "el porcentaje de hogares con motocicleta", 0),
 "COMBCON": ("Cocinan con combustibles contaminantes", "el porcentaje de hogares que cocinan con combustibles contaminantes", -1),
 "LENA": ("Cocinan con leña", "el porcentaje de hogares que cocinan con leña", -1),
 "GLP": ("Cocinan con gas (balón)", "el porcentaje de hogares que cocinan con gas de balón", 1),
 "ANALF15": ("Analfabetismo (15 años a más)", "la tasa de analfabetismo de la población de 15 años a más", -1),
 "NOA611": ("No asisten a la escuela (6 a 11 años)", "el porcentaje de niños de 6 a 11 años que no asiste a la escuela", -1),
 "NOA1216": ("No asisten a la escuela (12 a 16 años)", "el porcentaje de adolescentes de 12 a 16 años que no asiste a la escuela", -1),
 "ASISTE": ("Asiste a un centro educativo (3 años a más)", "el porcentaje de personas de 3 años a más que asiste a un centro educativo", 0),
 "SUPER": ("Con educación superior (3 años a más)", "el porcentaje de personas con educación superior", 1),
 "SINSEG": ("Sin seguro de salud", "el porcentaje de personas sin seguro de salud", -1),
 "SIS": ("Afiliados al SIS", "el porcentaje de personas afiliadas al SIS", 0),
 "ESSALUD": ("Afiliados a EsSalud", "el porcentaje de personas afiliadas a EsSalud", 0),
 "SINDNI": ("Sin DNI", "el porcentaje de personas sin DNI", -1),
 "LM_QUE": ("Lengua materna quechua", "el porcentaje de personas con quechua como lengua materna", 0),
 "LM_CAST": ("Lengua materna castellano", "el porcentaje de personas con castellano como lengua materna", 0),
 "PEA14": ("Tasa de actividad (14 años a más)", "la tasa de actividad de la población de 14 años a más", 0),
 "DES14": ("Tasa de desempleo (14 años a más)", "la tasa de desempleo", -1),
}
CU = {"viviendas particulares con ocupantes presentes": "viviendas", "viviendas con agua por red pública o pilón": "viviendas",
      "hogares": "hogares", "mujeres de 12 años a más": "mujeres"}
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
EMP = "No existe en 2025: el censo no preguntó por empleo."
NOTES = {
 "PARNOB": {"2017-2025": "Misma definición. En 2025 el drywall es una opción aparte."},
 "PARINA": {"2007-2017": SIM07, "2017-2025": "Misma definición; en 2025 el drywall cuenta como material adecuado.", "2007-2025": SIM07},
 "TECINA": {"2007-2017": "No existe en 2007: ese censo no preguntó el material del techo.", "2007-2025": "No existe en 2007: ese censo no preguntó el material del techo.", "2017-2025": "Misma definición; en 2025 el drywall cuenta como material adecuado."},
 "AGUARP": {"2017-2025": "Misma definición. En 2017 el agua del vecino era una opción aparte y no se cuenta."},
 "ELECRP": {"2017-2025": "Similar: en 2017 se preguntó si tenía alumbrado eléctrico por red pública; en 2025, la fuente de energía."},
 "INTFIJ": {"2017-2025": "No comparable: 2017 preguntó por conexión a internet sin separar fijo y móvil; 2025 los separa (aquí, internet fijo).", "2007-2025": "No comparable: 2007 preguntó por conexión a internet; 2025 separa fijo y móvil (aquí, internet fijo)."},
 "PCLAP": {"2007-2017": "No comparable: en 2007 solo se preguntó por computadora.", "2007-2025": "No comparable: en 2007 solo se preguntó por computadora."},
 "AUTO": {"2007-2017": "No existe en 2007.", "2007-2025": "No existe en 2007."},
 "MOTO": {"2007-2017": "No existe en 2007.", "2007-2025": "No existe en 2007."},
 "COMBCON": {"2007-2017": COC07, "2007-2025": COC07, "2017-2025": "Misma definición."},
 "LENA": {"2007-2017": COC07, "2007-2025": COC07},
 "GLP": {"2007-2017": COC07, "2007-2025": COC07},
 "SUPER": {"2007-2017": "No comparable: en 2007 los niveles educativos se clasificaban de otra forma.", "2007-2025": "No comparable: en 2007 los niveles educativos se clasificaban de otra forma.", "2017-2025": "Misma definición."},
 "SINDNI": {"2007-2017": "No comparable: en 2007 solo se preguntó a mayores de 18 años.", "2007-2025": "No comparable: en 2007 solo se preguntó a mayores de 18 años."},
 "LM_QUE": {"2017-2025": "Misma definición, pero en 2025 se puede declarar más de una lengua materna.", "2007-2025": "Misma definición, pero en 2025 se puede declarar más de una lengua materna."},
 "LM_CAST": {"2017-2025": LM2, "2007-2025": LM2},
 "PEA14": {"2017-2025": EMP, "2007-2025": EMP},
 "DES14": {"2017-2025": EMP, "2007-2025": EMP},
 "URB": {"2017-2025": "Misma definición.", "2007-2025": "Misma definición."},
}
EXTRA = {
 "POB": "Población censada, sin la estimación de población omitida. La población total oficial fue 28,220,764 (2007), 31,237,385 (2017) y 34,157,732 (2025).",
 "NACEXT": "En 2007 y 2017 el lugar de nacimiento es donde vivía la madre al nacer; en 2025 se pregunta si nació en otro país.",
 "PEA14": "Conteo directo de los microdatos. En 2017 el INEI publicó una PEA mayor, estimada con modelos (16.5 millones frente a 13.0 millones aquí).",
 "DES14": "Conteo directo de los microdatos. En 2017 el INEI publicó una PEA mayor, estimada con modelos.",
}
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
 "VOP": "Viviendas particulares con ocupantes presentes", "PARNOB": "Paredes de ladrillo o bloque de cemento, o de piedra o sillar con cal o cemento",
 "PARINA": "Paredes de adobe, tapia, quincha, piedra con barro, madera, triplay, calamina, estera u otro material",
 "TECINA": "Techo de calamina o fibrocemento, caña o estera con barro, triplay, estera o carrizo, paja u otro material",
 "PISTIE": "Viviendas con piso de tierra", "HACINA": "Viviendas con más de 3.4 personas por habitación", "HAB1": "Viviendas de una sola habitación",
 "SB3RP": "Viviendas con agua y desagüe por red pública (dentro o fuera de la vivienda) y alumbrado eléctrico por red pública, los tres a la vez",
 "AGUARP": "Agua por red pública, dentro o fuera de la vivienda", "DESRP": "Desagüe por red pública, dentro o fuera de la vivienda",
 "ELECRP": "Alumbrado eléctrico por red pública", "CELUL": "Hogares con al menos un teléfono celular", "INTFIJ": "Hogares con conexión a internet (2025: internet fijo)",
 "PCLAP": "Hogares con computadora, laptop o tablet", "REFRI": "Hogares con refrigeradora o congeladora", "AUTO": "Hogares con automóvil o camioneta",
 "MOTO": "Hogares con motocicleta", "COMBCON": "Hogares que cocinan solo con leña, carbón, bosta u otro combustible contaminante, sin gas ni electricidad",
 "LENA": "Hogares que cocinan con leña", "GLP": "Hogares que cocinan con gas de balón", "ANALF15": "Personas de 15 años a más que no saben leer ni escribir",
 "NOA611": "Niños de 6 a 11 años que no asisten a un centro educativo", "NOA1216": "Adolescentes de 12 a 16 años que no asisten a un centro educativo",
 "ASISTE": "Personas de 3 años a más que asisten a un colegio, instituto o universidad", "SUPER": "Personas de 3 años a más con educación superior, completa o incompleta",
 "SINSEG": "Personas sin ningún seguro de salud", "SIS": "Personas afiliadas al Seguro Integral de Salud", "ESSALUD": "Personas afiliadas a EsSalud",
 "SINDNI": "Personas sin documento nacional de identidad", "LM_QUE": "Personas de 3 años a más cuya lengua materna es el quechua",
 "LM_CAST": "Personas de 3 años a más cuya lengua materna es el castellano", "PEA14": "Población económicamente activa como porcentaje de la población de 14 años a más",
 "DES14": "Desocupados como porcentaje de la población económicamente activa de 14 años a más",
}
meta = []
for cat, ids in CATS:
    for i in ids:
        m = M0[i]
        cu = COUNT_UNIT.get(i) or CU.get(m["den"], "personas")
        meta.append(dict(id=i, cat=cat, label=L[i][0], long=L[i][1], dir=L[i][2], unit=m["unit"], den=m["den"],
                         cu=cu, years=m["years"], cmp=m["cmp"], def_=DEF[i],
                         notes={p: note_for(i, p, m) for p in PAIRS},
                         extra=EXTRA.get(i, "")))

def pick(block, key, idx=None):
    return {i: block[key][i] for i in IDS}

R = D0["regions"]; P = D0["provs"]; DI = D0["dists"]
def norm(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())

old = []
for k in range(len(DI["u"])):
    o = []
    if DI["n07"][k] and norm(DI["n07"][k]) != norm(DI["n"][k]): o.append(f"2007: {DI['n07'][k]}")
    if DI["n17"][k] and norm(DI["n17"][k]) != norm(DI["n"][k]): o.append(f"2017: {DI['n17'][k]}")
    old.append("; ".join(o))

data = dict(
    meta=meta, cats=[c for c, _ in CATS],
    R=dict(names=R["names"], v=pick(R, "v"), n=pick(R, "n")),
    P=dict(u=P["u"], r=P["r"], n=P["n"], v=pick(P, "v"), c=pick(P, "n_")),
    D=dict(u=DI["u"], r=DI["r"], n=DI["n"], old=old,
           e07=[x is not None for x in DI["n07"]], e17=[x is not None for x in DI["n17"]],
           comp={p: [1 if x else 0 for x in DI["comp"][p]] for p in PAIRS},
           v=pick(DI, "v"), c=pick(DI, "n_")),
    alerts={p: D0["alert_summary"][p] for p in PAIRS},
)
s = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
open(OUT + "censos.json", "w").write(s); print("censos.json", round(len(s) / 1e6, 2), "MB")

# ---------- geometría proyectada ----------
lon0, lat0 = -81.4, 0.0
c = math.cos(math.radians(9.2)); S = 41.0
def pt(lo, la): return ((lo - lon0) * c * S + 6, (lat0 - la) * S + 6)
def rings(g): return g["coordinates"] if g["type"] == "Polygon" else [r for p in g["coordinates"] for r in p]
def path(g, dec=1):
    out = []
    for r in rings(g):
        seg = []; last = None
        for p in r:
            x, y = pt(*p[:2]); q = (round(x, dec), round(y, dec))
            if q != last: seg.append(q); last = q
        if len(seg) > 2:
            fmt = (lambda v: f"{v:g}")
            out.append("M" + "L".join(f"{fmt(x)},{fmt(y)}" for x, y in seg) + "Z")
    return "".join(out)
gp = json.load(open(G + "peru_provincial_simple.geojson")); gd = json.load(open(G + "peru_departamental_simple.geojson"))
gdi = json.load(open(G + "peru_distrital_simple.geojson"))
u25 = set(DI["u"])
def merge(pairs):
    out = {}
    for k, d in pairs: out[k] = out.get(k, "") + d   # un código con varios polígonos: se juntan, no se pisan
    return out
geo = dict(
    w=int((-68.6 - lon0) * c * S + 12), h=int((lat0 + 18.4) * S + 12),
    prov=merge((f["properties"]["FIRST_IDPR"], path(f["geometry"])) for f in gp["features"] if f["geometry"]),
    dep=[path(f["geometry"]) for f in gd["features"]],
    dist=merge((f["properties"]["IDDIST"], path(f["geometry"], 2)) for f in gdi["features"] if f["properties"]["IDDIST"] in u25 and f["geometry"]),
)
s = json.dumps(geo, separators=(",", ":"))
open(OUT + "geo.json", "w").write(s); print("geo.json", round(len(s) / 1e6, 2), "MB", len(geo["prov"]), len(geo["dist"]))
