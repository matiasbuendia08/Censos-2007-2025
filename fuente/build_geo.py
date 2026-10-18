"""Arma data/geo.json: distritos, provincias y regiones (disueltas desde los distritos)."""
import json, math, sys
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union

SRC, CENSOS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
D = json.load(open(CENSOS, encoding="utf-8"))
reg_of = dict(zip(D["D"]["u"], D["D"]["r"]))          # ubigeo 2025 -> región
reg_of_prov = dict(zip(D["P"]["u"], D["P"]["r"]))

lon0, lat0 = -81.4, 0.0
c = math.cos(math.radians(9.2)); S = 41.0
def pt(lo, la): return ((lo - lon0) * c * S + 6, (lat0 - la) * S + 6)

def clean(g, min_area=1e-6, min_hole=1e-5):
    """Quita astillas y agujeros diminutos que deja la disolución."""
    polys = [g] if isinstance(g, Polygon) else list(getattr(g, "geoms", []))
    out = []
    for p in polys:
        if not isinstance(p, Polygon) or p.area < min_area: continue
        out.append(Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area > min_hole]))
    return MultiPolygon(out) if len(out) > 1 else out[0]

def path(g, dec=1):
    out = []
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    for p in polys:
        for r in [p.exterior] + list(p.interiors):
            seg = []; last = None
            for lo, la in r.coords:
                x, y = pt(lo, la); q = (round(x, dec), round(y, dec))
                if q != last: seg.append(q); last = q
            if len(seg) > 2:
                out.append("M" + "L".join(f"{x:g},{y:g}" for x, y in seg) + "Z")
    return "".join(out)

g = json.load(open(SRC, encoding="utf-8"))
dist = {}
for f in g["features"]:
    u = f["properties"]["UBIGEO"]
    if not f["geometry"]: continue
    s = shape(f["geometry"]).buffer(0)
    dist[u] = unary_union([dist[u], s]) if u in dist else s

missing = sorted(set(reg_of) - set(dist))
extra = sorted(set(dist) - set(reg_of))
print("distritos con polígono:", len(set(dist) & set(reg_of)), "sin polígono:", len(missing), "sobran:", extra)

prov = {}
for u, s in dist.items(): prov.setdefault(u[:4], []).append(s)
prov = {k: clean(unary_union(v).buffer(0)) for k, v in prov.items()}
print("provincias:", len(prov), "faltan:", sorted(set(D["P"]["u"]) - set(prov)))

reg = {}
for u, s in dist.items():
    r = reg_of.get(u) or reg_of_prov.get(u[:4])
    reg.setdefault(r, []).append(s)
reg = {k: clean(unary_union(v).buffer(0)) for k, v in reg.items()}
print("regiones:", len(reg), sorted(reg))

geo = dict(
    w=int((-68.6 - lon0) * c * S + 12), h=int((lat0 + 18.4) * S + 12),
    reg={k: path(v) for k, v in reg.items()},
    prov={k: path(v) for k, v in prov.items()},
    dist={k: path(v, 2) for k, v in dist.items() if k in reg_of},
)
geo["dep"] = list(geo["reg"].values())   # contorno de regiones para el mapa nacional
s = json.dumps(geo, separators=(",", ":"))
open(OUT, "w", encoding="utf-8").write(s)
print("geo.json", round(len(s) / 1e6, 2), "MB")
print("sin polígono:", missing)
