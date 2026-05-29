"""Mock of the Queuechella event diagram (v2) — verify layout before Excalidraw."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np

R = 78
C_BOOT="#a5d8ff"; C_SVC="#b2f2bb"; C_HUB="#ffc9c9"; C_SPEC="#fff3bf"; C_DAY="#ffd8a8"; C_DEP="#d0bfff"

NODES = {
 "FG_Arr":   (150,160,"FriendsGroup\nArrival",C_BOOT),
 "Cpl_Arr":  (150,380,"Couple\nArrival",C_BOOT),
 "Sgl_Arr":  (150,600,"Single\nArrival",C_BOOT),
 "EndEntry": (390,380,"EndEntry",C_SVC),
 "EndOfStay":(250,1120,"EndOfStay",C_DEP),
 "SS_Main":  (720,150,"ShowStart\n@MainStage",C_BOOT),
 "SE_Main":  (940,150,"ShowEnd\n@MainStage",C_SVC),
 "SS_Side":  (1180,150,"ShowStart\n@SideStage",C_BOOT),
 "SE_Side":  (1400,150,"ShowEnd\n@SideStage",C_SVC),
 "EarlyExit":(560,300,"EarlyExit\nCheck",C_SPEC),
 "EndDJ":    (560,510,"EndAt\n@DJstage",C_SVC),
 "End_Photo":(940,520,"EndService\n@Photo",C_SVC),
 "Abandon":  (940,730,"Abandon\nQueue",C_HUB),
 "End_Charge":(1160,730,"EndService\n@Charging",C_SVC),
 "End_Merch":(940,940,"EndService\n@Merch",C_SVC),
 "End_Body": (720,730,"EndService\n@BodyArt",C_SVC),
 "BreakEnd": (560,920,"BreakEnd\n@BodyArt",C_SPEC),
 "EndOrder": (1390,520,"EndOrder\n@Food",C_SVC),
 "EndPrep":  (1390,730,"EndPrep\n@Food",C_SVC),
 "EndEat":   (1390,940,"EndEating\n@Food",C_SVC),
 "EndOfDay1":     (1640,330,"EndOfDay1",C_DAY),
 "EndOfFestival": (1640,600,"EndOf\nFestival",C_DAY),
 "Day2Resume":    (1640,870,"Day2\nResume",C_SPEC),
}
SELF=["FG_Arr","Cpl_Arr","Sgl_Arr","EndEntry","EndDJ","End_Photo","End_Charge","End_Merch","End_Body","EndOrder"]
INIT=["FG_Arr","Cpl_Arr","Sgl_Arr","SS_Main","SS_Side","EndOfDay1","EndOfFestival"]
SCHED=[
 ("FG_Arr","EndEntry"),("Cpl_Arr","EndEntry"),("Sgl_Arr","EndEntry"),
 ("EndEntry","EndDJ"),
 ("SS_Main","SE_Main"),("SE_Main","SS_Main"),("SS_Side","SE_Side"),("SE_Side","SS_Side"),
 ("SS_Main","EarlyExit"),
 ("SE_Main","End_Photo"),("SE_Side","End_Photo"),("SE_Main","EndDJ"),
 ("EndDJ","End_Body"),("EndDJ","EndOfStay"),
 ("EarlyExit","End_Photo"),("EarlyExit","EndDJ"),
 ("EndOrder","EndPrep"),("EndPrep","EndEat"),("EndEat","End_Charge"),
 ("End_Charge","EndOrder"),("End_Photo","EndOrder"),
 ("Abandon","EndDJ"),("Abandon","EndOrder"),
 ("End_Body","BreakEnd"),("BreakEnd","End_Body"),
]
BIDIR=[
 ("End_Photo","End_Charge"),("End_Charge","End_Merch"),("End_Merch","End_Body"),("End_Body","End_Photo"),
 ("End_Photo","Abandon"),("End_Charge","Abandon"),("End_Merch","Abandon"),("End_Body","Abandon"),
]
ROUTED=[
 ("EndOfDay1",[(1700,18),(40,18),(40,380)],"Cpl_Arr"),
 ("EndOfDay1",[(1715,6),(22,6),(22,600)],"Sgl_Arr"),
 ("EndOfDay1",[(1690,30),(720,30)],"SS_Main"),
 ("EndOfDay1",[(1620,44),(1180,44)],"SS_Side"),
 ("EndOfFestival",[(1745,600),(1745,1205),(360,1205)],"EndOfStay"),
 ("Abandon",[(690,1015),(360,1175)],"EndOfStay"),
 ("End_Merch",[(940,1235),(370,1235)],"EndOfStay"),
 ("EndEat",[(1390,1265),(390,1265)],"EndOfStay"),
 ("Day2Resume",[(1640,1095),(1160,1095)],"End_Charge"),
 ("EndEntry",[(440,730)],"End_Body"),
 ("EndOfDay1",[(1760,330),(1760,870)],"Day2Resume"),
]
def perim(a,b):
    ax,ay=NODES[a][0],NODES[a][1]
    bx,by=b if isinstance(b,tuple) else (NODES[b][0],NODES[b][1])
    d=np.hypot(bx-ax,by-ay); return (ax+(bx-ax)/d*R, ay+(by-ay)/d*R)
def seg_dist(p,a,b):
    p,a,b=map(np.array,(p,a,b)); ab=b-a
    t=np.clip(np.dot(p-a,ab)/np.dot(ab,ab),0,1); return np.hypot(*(p-(a+t*ab)))
violations=[]
def check(a_pt,b_pt,ends):
    for nid,(cx,cy,_,_) in NODES.items():
        if nid in ends: continue
        if seg_dist((cx,cy),a_pt,b_pt)<R+12: violations.append((tuple(sorted(ends)),nid))
# node-node overlap check
ids=list(NODES)
for i in range(len(ids)):
    for j in range(i+1,len(ids)):
        a,b=ids[i],ids[j]; d=np.hypot(NODES[a][0]-NODES[b][0],NODES[a][1]-NODES[b][1])
        if d<2*R+14: violations.append(("OVERLAP",a,b,round(d)))
for s,d in SCHED+BIDIR: check(perim(s,d),perim(d,s),{s,d})
for s,wps,d in ROUTED:
    pts=[perim(s,wps[0])]+wps+[perim(d,wps[-1])]
    for i in range(len(pts)-1): check(pts[i],pts[i+1],{s,d})
# render
fig,ax=plt.subplots(figsize=(19,15))
for nid,(cx,cy,lbl,fill) in NODES.items():
    ax.add_patch(Circle((cx,cy),R,facecolor=fill,edgecolor="#1e1e1e",lw=2,zorder=3))
    ax.text(cx,cy,lbl,ha="center",va="center",fontsize=10,zorder=4)
def arrow(a_pt,b_pt,both=False,color="#1e1e1e"):
    ax.add_patch(FancyArrowPatch(a_pt,b_pt,arrowstyle="<|-|>" if both else "-|>",
        mutation_scale=16,lw=1.6,color=color,zorder=2,shrinkA=0,shrinkB=0))
for s,d in SCHED: arrow(perim(s,d),perim(d,s))
for s,d in BIDIR: arrow(perim(s,d),perim(d,s),both=True,color="#c92a2a")
for s,wps,d in ROUTED:
    pts=[perim(s,wps[0])]+wps+[perim(d,wps[-1])]; xs,ys=zip(*pts)
    ax.plot(xs,ys,color="#7048e8",lw=1.6,zorder=2); arrow(pts[-2],pts[-1],color="#7048e8")
for nid in SELF:
    cx,cy,_,_=NODES[nid]
    ax.add_patch(FancyArrowPatch((cx-25,cy-R+4),(cx+25,cy-R+4),connectionstyle="arc3,rad=2.2",
        arrowstyle="-|>",mutation_scale=12,lw=1.4,color="#1e1e1e",zorder=2))
for nid in INIT:
    cx,cy,_,_=NODES[nid]; x0=cx-R-95; xs=np.linspace(x0,cx-R-6,9)
    ys=cy+8*np.array([0,1,-1,1,-1,1,-1,1,0]); ax.plot(xs,ys,color="#e8590c",lw=2,zorder=2)
    arrow((xs[-2],ys[-2]),(cx-R-2,cy),color="#e8590c")
ax.set_xlim(-60,1820); ax.set_ylim(-20,1300); ax.invert_yaxis(); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout(); plt.savefig("/tmp/event_layout_mock.png",dpi=80,bbox_inches="tight")
print("VIOLATIONS:",len(violations))
for v in violations: print("  ",v)
