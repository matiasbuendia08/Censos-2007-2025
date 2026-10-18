import sys
# Contador privado de visitas (GoatCounter). Cambia el código si registras otro.
GC_CODE = "perutrescensos"
GC = ('\n<!-- Contador de visitas: el panel solo lo ve el dueño en https://' + GC_CODE + '.goatcounter.com -->\n'
      '<script data-goatcounter="https://' + GC_CODE + '.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>')
src=open("/home/claude/web/site/app.html").read()
html='<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
head_end=src.index("</style>")+len("</style>")
html+=src[:head_end]+'\n<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n</head>\n<body>\n'+src[head_end:]+GC+'\n</body>\n</html>\n'
import os; os.makedirs("/home/claude/web/site/docs/data",exist_ok=True)
open("/home/claude/web/site/docs/index.html","w").write(html)
