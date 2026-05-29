"""Minimal native Excalidraw scene from my simplified element list.
Drops every field Excalidraw's import restore() back-fills, to shrink the payload.
Reads simplified JSON argv[1] -> writes native scene argv[2]."""
import json, sys
simple = json.load(open(sys.argv[1]))
native=[]; bound={}
def ri(v): return int(round(v))
for e in simple:
    typ=e.get("type")
    if typ=="cameraUpdate": continue
    if typ=="text":
        w=max(len(l) for l in e["text"].split("\n"))*e.get("fontSize",16)*0.6
        h=len(e["text"].split("\n"))*e.get("fontSize",16)*1.25
        native.append({"id":e["id"],"type":"text","x":ri(e["x"]),"y":ri(e["y"]),
            "width":ri(w),"height":ri(h),"text":e["text"],"fontSize":e.get("fontSize",16),
            "strokeColor":e.get("strokeColor","#1e1e1e"),"textAlign":"left","verticalAlign":"top"})
    elif typ in ("ellipse","rectangle","diamond"):
        el={"id":e["id"],"type":typ,"x":ri(e["x"]),"y":ri(e["y"]),"width":ri(e["width"]),
            "height":ri(e["height"]),"backgroundColor":e.get("backgroundColor","transparent"),
            "fillStyle":"solid","strokeColor":e.get("strokeColor","#1e1e1e")}
        native.append(el)
        if "label" in e:
            tid=f"t_{e['id']}"; cx=e["x"]+e["width"]/2; cy=e["y"]+e["height"]/2
            txt=e["label"]["text"]; fs=e["label"].get("fontSize",16)
            w=max(len(l) for l in txt.split("\n"))*fs*0.6; h=len(txt.split("\n"))*fs*1.25
            native.append({"id":tid,"type":"text","x":ri(cx-w/2),"y":ri(cy-h/2),"width":ri(w),
                "height":ri(h),"text":txt,"fontSize":fs,"textAlign":"center",
                "verticalAlign":"middle","containerId":e["id"]})
            bound.setdefault(e["id"],[]).append({"type":"text","id":tid})
for e in simple:
    if e.get("type")!="arrow": continue
    sb=e.get("startBinding"); eb=e.get("endBinding")
    same=sb and eb and sb["elementId"]==eb["elementId"]
    a={"id":e["id"],"type":"arrow","x":ri(e["x"]),"y":ri(e["y"]),
       "points":[[ri(px),ri(py)] for px,py in e["points"]],
       "endArrowhead":e.get("endArrowhead","arrow"),"strokeColor":e.get("strokeColor","#1e1e1e")}
    xs=[p[0] for p in a["points"]]; ys=[p[1] for p in a["points"]]
    a["width"]=max(xs)-min(xs); a["height"]=max(ys)-min(ys)
    if e.get("startArrowhead"): a["startArrowhead"]=e["startArrowhead"]
    if e.get("roundness"): a["roundness"]=e["roundness"]
    if sb and not same:
        a["startBinding"]={"elementId":sb["elementId"],"focus":0,"gap":4}
        bound.setdefault(sb["elementId"],[]).append({"type":"arrow","id":e["id"]})
    if eb and not same:
        a["endBinding"]={"elementId":eb["elementId"],"focus":0,"gap":4}
        bound.setdefault(eb["elementId"],[]).append({"type":"arrow","id":e["id"]})
    native.append(a)
for el in native:
    if el["id"] in bound: el["boundElements"]=bound[el["id"]]
scene={"type":"excalidraw","version":2,"source":"https://excalidraw.com","elements":native,
       "appState":{"viewBackgroundColor":"#ffffff"},"files":{}}
out=json.dumps(scene,separators=(",",":"))
open(sys.argv[2],"w").write(out); print("bytes:",len(out),"elements:",len(native))
