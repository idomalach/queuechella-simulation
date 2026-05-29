"""Generate Excalidraw elements JSON for the 23-node event diagram from the verified
mock coordinates. Arrows are bound to nodes (startBinding/endBinding + fixedPoint) so
dragging a node in the UI drags its arrows."""
import json, math

R = 75
C_BOOT="#a5d8ff"; C_SVC="#b2f2bb"; C_HUB="#ffc9c9"; C_SPEC="#fff3bf"; C_DAY="#ffd8a8"; C_DEP="#d0bfff"
ST = {C_BOOT:"#1971c2", C_SVC:"#2f9e44", C_HUB:"#c92a2a", C_SPEC:"#f08c00", C_DAY:"#e8590c", C_DEP:"#7048e8"}

NODES = {  # center coords (from verified mock)
 "FG_Arr":(150,160,"FriendsGroup\nArrival",C_BOOT),"Cpl_Arr":(150,380,"Couple\nArrival",C_BOOT),
 "Sgl_Arr":(150,600,"Single\nArrival",C_BOOT),"EndEntry":(390,380,"EndEntry",C_SVC),
 "EndOfStay":(250,1120,"EndOfStay",C_DEP),
 "SS_Main":(720,150,"ShowStart\n@MainStage",C_BOOT),"SE_Main":(940,150,"ShowEnd\n@MainStage",C_SVC),
 "SS_Side":(1180,150,"ShowStart\n@SideStage",C_BOOT),"SE_Side":(1400,150,"ShowEnd\n@SideStage",C_SVC),
 "EarlyExit":(560,300,"EarlyExit\nCheck",C_SPEC),"EndDJ":(560,510,"EndAt\n@DJstage",C_SVC),
 "End_Photo":(940,520,"EndService\n@Photo",C_SVC),"Abandon":(940,730,"AbandonQueue",C_HUB),
 "End_Charge":(1160,730,"EndService\n@Charging",C_SVC),"End_Merch":(940,940,"EndService\n@Merch",C_SVC),
 "End_Body":(720,730,"EndService\n@BodyArt",C_SVC),"BreakEnd":(560,920,"BreakEnd\n@BodyArt",C_SPEC),
 "EndOrder":(1390,520,"EndOrder\n@Food",C_SVC),"EndPrep":(1390,730,"EndPrep\n@Food",C_SVC),
 "EndEat":(1390,940,"EndEating\n@Food",C_SVC),
 "EndOfDay1":(1640,330,"EndOfDay1",C_DAY),"EndOfFestival":(1640,600,"EndOf\nFestival",C_DAY),
 "Day2Resume":(1640,870,"Day2Resume",C_SPEC),
}
SELF=["FG_Arr","Cpl_Arr","Sgl_Arr","EndEntry","EndDJ","End_Photo","End_Charge","End_Merch","End_Body","EndOrder"]
INIT=["FG_Arr","Cpl_Arr","Sgl_Arr","SS_Main","SS_Side","EndOfDay1","EndOfFestival"]
SCHED=[("FG_Arr","EndEntry"),("Cpl_Arr","EndEntry"),("Sgl_Arr","EndEntry"),("EndEntry","EndDJ"),
 ("SS_Main","SE_Main"),("SE_Main","SS_Main"),("SS_Side","SE_Side"),("SE_Side","SS_Side"),("SS_Main","EarlyExit"),
 ("SE_Main","End_Photo"),("SE_Side","End_Photo"),("SE_Main","EndDJ"),("EndDJ","End_Body"),("EndDJ","EndOfStay"),
 ("EarlyExit","End_Photo"),("EarlyExit","EndDJ"),("EndOrder","EndPrep"),("EndPrep","EndEat"),("EndEat","End_Charge"),
 ("End_Charge","EndOrder"),("End_Photo","EndOrder"),("Abandon","EndDJ"),("Abandon","EndOrder"),
 ("End_Body","BreakEnd"),("BreakEnd","End_Body")]
BIDIR=[("End_Photo","End_Charge"),("End_Charge","End_Merch"),("End_Merch","End_Body"),("End_Body","End_Photo"),
 ("End_Photo","Abandon"),("End_Charge","Abandon"),("End_Merch","Abandon"),("End_Body","Abandon")]
ROUTED=[("EndOfDay1",[(1700,18),(40,18),(40,380)],"Cpl_Arr"),("EndOfDay1",[(1715,6),(22,6),(22,600)],"Sgl_Arr"),
 ("EndOfDay1",[(1690,30),(720,30)],"SS_Main"),("EndOfDay1",[(1620,44),(1180,44)],"SS_Side"),
 ("EndOfFestival",[(1745,600),(1745,1205),(360,1205)],"EndOfStay"),("Abandon",[(690,1015),(360,1175)],"EndOfStay"),
 ("End_Merch",[(940,1235),(370,1235)],"EndOfStay"),("EndEat",[(1390,1265),(390,1265)],"EndOfStay"),
 ("Day2Resume",[(1640,1095),(1160,1095)],"End_Charge"),("EndEntry",[(440,730)],"End_Body"),
 ("EndOfDay1",[(1760,330),(1760,870)],"Day2Resume")]

def C(n): return NODES[n][0],NODES[n][1]
def unit(ax,ay,bx,by):
    d=math.hypot(bx-ax,by-ay); return (bx-ax)/d,(by-ay)/d
def perim(n,tx,ty):
    cx,cy=C(n); ux,uy=unit(cx,cy,tx,ty); return cx+ux*R, cy+uy*R
def fp(n,tx,ty):  # fixedPoint on bounding box toward (tx,ty)
    cx,cy=C(n); ux,uy=unit(cx,cy,tx,ty)
    return [round(0.5+0.5*ux,3), round(0.5+0.5*uy,3)]

BLK="#1e1e1e"
els=[{"type":"cameraUpdate","width":2000,"height":1500,"x":-90,"y":-110}]
# title
els.append({"type":"text","id":"title","x":560,"y":-95,"text":"Queuechella - Event Diagram (23 events)","fontSize":30,"strokeColor":BLK})
# legend (black & white: explain the two arrow types, no color groups)
lx,ly=1470,1080
els.append({"type":"text","id":"legt","x":lx,"y":ly-36,"text":"Legend","fontSize":20,"strokeColor":BLK})
# solid scheduling arrow icon
els.append({"type":"arrow","id":"legi1","x":lx,"y":ly+10,"width":56,"height":0,"points":[[0,0],[56,0]],"endArrowhead":"arrow","strokeColor":BLK,"strokeWidth":2})
els.append({"type":"text","id":"legs","x":lx+68,"y":ly,"text":"solid = scheduling edge","fontSize":16,"strokeColor":BLK})
# double-headed icon
els.append({"type":"arrow","id":"legi2","x":lx,"y":ly+44,"width":56,"height":0,"points":[[0,0],[56,0]],"endArrowhead":"arrow","startArrowhead":"arrow","strokeColor":BLK,"strokeWidth":2})
els.append({"type":"text","id":"legd","x":lx+68,"y":ly+34,"text":"double = mutual scheduling","fontSize":16,"strokeColor":BLK})
# zigzag icon
els.append({"type":"arrow","id":"legi3","x":lx,"y":ly+78,"width":56,"height":0,"points":[[0,0],[8,0],[18,9],[28,-9],[38,9],[48,-9],[56,0]],"endArrowhead":"arrow","strokeColor":BLK,"strokeWidth":2})
els.append({"type":"text","id":"legz","x":lx+68,"y":ly+68,"text":"zigzag = init (seed FEL at t=0)","fontSize":16,"strokeColor":BLK})
els.append({"type":"text","id":"legn","x":lx,"y":ly+108,"text":"Shows are entered from their queue by the","fontSize":14,"strokeColor":"#555555"})
els.append({"type":"text","id":"legn2","x":lx,"y":ly+128,"text":"recurring ShowStart cycle (no incoming edge).","fontSize":14,"strokeColor":"#555555"})

# nodes (black & white: white fill, black stroke)
for n,(cx,cy,lbl,fill) in NODES.items():
    els.append({"type":"ellipse","id":f"n_{n}","x":cx-R,"y":cy-R,"width":2*R,"height":2*R,
                "backgroundColor":"#ffffff","fillStyle":"solid","strokeColor":BLK,"strokeWidth":2,
                "label":{"text":lbl,"fontSize":16}})
aid=0
def arrow(s,d,sx,sy,pts,both=False,routed=False,fps=None,fpd=None):
    global aid; aid+=1
    col="#1e1e1e"
    e={"type":"arrow","id":f"a{aid}","x":round(sx),"y":round(sy),
       "points":[[round(px-sx),round(py-sy)] for px,py in pts],
       "endArrowhead":"arrow","strokeColor":col,"strokeWidth":2}
    if both: e["startArrowhead"]="arrow"
    e["startBinding"]={"elementId":f"n_{s}","fixedPoint":fps}
    e["endBinding"]={"elementId":f"n_{d}","fixedPoint":fpd}
    els.append(e)

for s,d in SCHED:
    sx,sy=perim(s,*C(d)); ex,ey=perim(d,*C(s))
    arrow(s,d,sx,sy,[(sx,sy),(ex,ey)],fps=fp(s,*C(d)),fpd=fp(d,*C(s)))
for s,d in BIDIR:
    sx,sy=perim(s,*C(d)); ex,ey=perim(d,*C(s))
    arrow(s,d,sx,sy,[(sx,sy),(ex,ey)],both=True,fps=fp(s,*C(d)),fpd=fp(d,*C(s)))
for s,wps,d in ROUTED:
    sx,sy=perim(s,*wps[0]); ex,ey=perim(d,*wps[-1])
    pts=[(sx,sy)]+wps+[(ex,ey)]
    arrow(s,d,sx,sy,pts,routed=True,fps=fp(s,*wps[0]),fpd=fp(d,*wps[-1]))

# self loops (round arc bulging up; roundness type 2 smooths it)
for n in SELF:
    cx,cy=C(n); aid+=1
    x1,y1=cx-26,cy-R+6
    els.append({"type":"arrow","id":f"slf{aid}","x":round(x1),"y":round(y1),
        "points":[[0,0],[-22,-44],[26,-70],[74,-44],[52,0]],
        "roundness":{"type":2},
        "endArrowhead":"arrow","strokeColor":"#1e1e1e","strokeWidth":2,
        "startBinding":{"elementId":f"n_{n}","fixedPoint":[0.33,0.05]},
        "endBinding":{"elementId":f"n_{n}","fixedPoint":[0.67,0.05]}})

# zigzag init arrows (external -> node left), end bound to node
for n in INIT:
    cx,cy=C(n); aid+=1
    ex,ey=cx-R-4, cy
    x0=cx-R-104
    pts=[[0,0]]
    seq=[0,1,-1,1,-1,1,-1,0]
    for i,s in enumerate(seq):
        pts.append([round(8+ i*12),  round(10*s)])
    pts.append([round(ex-x0),0])
    els.append({"type":"arrow","id":f"zz{aid}","x":round(x0),"y":round(cy),
        "points":pts,"endArrowhead":"arrow","strokeColor":"#1e1e1e","strokeWidth":2,
        "endBinding":{"elementId":f"n_{n}","fixedPoint":[0.02,0.5]}})

print("element count:",len(els))
print("nodes:",sum(1 for e in els if e.get('type')=='ellipse'),
      "arrows:",sum(1 for e in els if e.get('type')=='arrow'))
js=json.dumps(els,separators=(",",":"))
open("/tmp/event_excali.json","w").write(js)
print("bytes:",len(js))
