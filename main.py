#!/usr/bin/env python3
"""Procedural midnight greenhouse illustration; standard library only."""
import math
import os
import struct
import zlib

W = H = 512


class Canvas:
    def __init__(self):
        self.p = bytearray(W * H * 3)

    def blend(self, x, y, color, a=1.0):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H and a > 0:
            i = (y * W + x) * 3
            for k in range(3):
                self.p[i + k] = max(0, min(255, int(self.p[i + k] * (1-a) + color[k] * a)))

    def disk(self, cx, cy, r, color, alpha=1.0, soft=0.0):
        x0, x1 = max(0, int(cx-r-1)), min(W, int(cx+r+2))
        y0, y1 = max(0, int(cy-r-1)), min(H, int(cy+r+2))
        for y in range(y0, y1):
            for x in range(x0, x1):
                d = math.hypot(x+.5-cx, y+.5-cy)
                if d <= r:
                    a = alpha
                    if soft and d > r-soft:
                        a *= (r-d)/soft
                    self.blend(x, y, color, a)

    def oval(self, cx, cy, rx, ry, color, alpha=1.0):
        for y in range(max(0, int(cy-ry-1)), min(H, int(cy+ry+2))):
            for x in range(max(0, int(cx-rx-1)), min(W, int(cx+rx+2))):
                d=((x+.5-cx)/rx)**2+((y+.5-cy)/ry)**2
                if d <= 1:
                    self.blend(x,y,color,alpha*min(1.0,(1-d)*14))

    def poly(self, pts, color, alpha=1.0):
        miny=max(0,int(min(y for x,y in pts))); maxy=min(H-1,int(max(y for x,y in pts))+1)
        for y in range(miny,maxy+1):
            scan=y+.5; xs=[]
            for i,(x1,y1) in enumerate(pts):
                x2,y2=pts[(i+1)%len(pts)]
                if (y1<=scan<y2) or (y2<=scan<y1): xs.append(x1+(scan-y1)*(x2-x1)/(y2-y1))
            xs.sort()
            for j in range(0,len(xs)-1,2):
                for x in range(max(0,int(xs[j])),min(W,int(xs[j+1])+1)):
                    self.blend(x,y,color,alpha)

    def line(self, a, b, width, color, alpha=1.0):
        x1,y1=a; x2,y2=b
        n=max(1,int(math.hypot(x2-x1,y2-y1)*1.3))
        for i in range(n+1): self.disk(x1+(x2-x1)*i/n,y1+(y2-y1)*i/n,width/2,color,alpha)


def png_bytes(rgb):
    raw=b''.join(b'\0'+bytes(rgb[y*W*3:(y+1)*W*3]) for y in range(H))
    def chunk(tag,data):
        body=tag+data
        return struct.pack('>I',len(data))+body+struct.pack('>I',zlib.crc32(body)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',W,H,8,2,0,0,0))+
            chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))


def render():
    c=Canvas()
    # Deep greenhouse night: quiet vertical falloff with a pool of teal behind the subject.
    for y in range(H):
        for x in range(W):
            u=((x-258)/370)**2+((y-220)/390)**2
            glow=max(0,1-u)
            n=max(0,1-((x-256)/250)**2)*max(0,1-((y-245)/300)**2)
            c.blend(x,y,(int(5+9*glow+7*n),int(12+20*glow+20*n),int(37+28*glow+19*n)))
    # Soft aureole, built from broad low-opacity discs for a luminous but graphic edge.
    for r,a,col in [(118,.035,(34,145,221)),(91,.05,(35,180,235)),(73,.065,(63,204,255)),(61,.09,(113,225,255))]:
        c.disk(250,196,r,col,a)
    c.disk(250,196,56,(157,236,255),.16)
    # Glasshouse ribs recede into darkness, with a fine turquoise edge.
    for pts in [[(28,0),(42,0),(111,278),(101,291)],[(470,0),(484,0),(398,287),(387,278)],[(140,0),(145,0),(183,175),(178,176)],[(367,0),(372,0),(329,175),(324,174)]]:
        c.poly(pts,(14,54,72),.65)
        c.line(pts[0],pts[1],2,(46,116,126),.42)
    c.line((17,278),(495,278),3,(19,91,103),.22)
    c.line((35,286),(475,286),1,(51,133,133),.4)
    # Slender stems and leaves frame the bloom without crowding it.
    c.line((286,484),(258,320),7,(12,80,67))
    c.line((258,390),(205,350),5,(13,91,71))
    c.line((267,426),(324,387),5,(14,100,74))
    c.poly([(216,357),(174,337),(198,373),(235,379)],(17,125,86))
    c.poly([(298,407),(339,369),(330,414),(282,433)],(17,125,86))
    c.line((190,354),(224,373),2,(82,190,124),.8)
    c.line((328,391),(294,418),2,(82,190,124),.8)
    # Oversized crimson flower, radiating curved-looking pointed petals.
    cx,cy=258,339
    petals=[((0,-8),(-42,-76),(-27,-133),(2,-94),(21,-44)),
            ((-5,-8),(-82,-48),(-116,-100),(-59,-86),(-12,-42)),
            ((-8,-3),(-114,-24),(-155,-64),(-94,-62),(-18,-28)),
            ((3,-8),(45,-78),(33,-136),(8,-96),(-15,-42)),
            ((7,-7),(88,-49),(126,-103),(62,-86),(16,-39)),
            ((10,-2),(120,-20),(163,-61),(100,-59),(19,-27))]
    colors=[(195,19,55),(231,27,66),(171,12,49),(214,18,58),(242,35,72),(184,13,49)]
    for p,col in zip(petals,colors):
        c.poly([(cx+x,cy+y) for x,y in p],col)
    # Petal highlight strokes and dark folded bases give the bloom depth.
    for a,b in [((257,329),(245,230)),((250,330),(170,255)),((248,335),(110,283)),((262,329),(273,226)),((269,330),(346,252)),((270,336),(378,282))]:
        c.line(a,b,4,(255,91,103),.72)
    c.disk(cx,cy-3,25,(111,11,43))
    c.disk(cx,cy-5,17,(246,81,59))
    for i in range(11):
        ang=i*math.tau/11
        c.line((cx+math.cos(ang)*5,cy-5+math.sin(ang)*5),(cx+math.cos(ang)*19,cy-5+math.sin(ang)*19),2,(255,200,99),.9)
        c.disk(cx+math.cos(ang)*21,cy-5+math.sin(ang)*21,2.2,(255,216,121))
    # Moth body and antennae, centered against its clean luminous halo.
    c.line((246,152),(224,128),2,(107,221,255),.9)
    c.line((254,152),(276,127),2,(107,221,255),.9)
    c.disk(223,126,2,(190,246,255)); c.disk(277,125,2,(190,246,255))
    # Wing outlines are jewel-blue leaded glass, with facets separated by dark seams.
    wings=[[(247,176),(222,151),(183,115),(142,91),(135,116),(147,143),(179,166),(218,182)],
           [(247,183),(217,188),(181,185),(148,194),(169,214),(205,219),(239,205)],
           [(257,176),(282,151),(321,115),(362,91),(369,116),(357,143),(325,166),(286,182)],
           [(257,183),(287,188),(323,185),(356,194),(335,214),(299,219),(265,205)]]
    glass=[(10,109,201),(16,160,226),(20,112,191),(17,151,216)]
    for p,col in zip(wings,glass):
        c.poly(p,(4,26,62))
        # inset colored pane
        q=[(sum(x for x,y in p)/len(p)+(x-sum(xx for xx,yy in p)/len(p))*.88,
            sum(y for x,y in p)/len(p)+(y-sum(yy for xx,yy in p)/len(p))*.88) for x,y in p]
        c.poly(q,col)
        c.line(p[0],p[1],3,(89,221,255),.9)
        for i in range(1,len(p)-1):
            c.line(p[0],p[i+1],2,(60,193,247),.86)
        # glass glints
        c.line(p[0],p[1],1.5,(190,249,255),.88)
    # Distinctive scalloped wing tips and bright rim catchlights.
    for x,y in [(137,106),(149,143),(170,201),(366,106),(354,143),(333,201)]:
        c.disk(x,y,4,(44,179,247),.8)
        c.disk(x-1,y-1,1.4,(194,246,255))
    c.line((245,169),(245,196),5,(8,31,72))
    c.line((245,169),(245,196),2.5,(111,225,255))
    c.line((255,169),(255,196),5,(8,31,72))
    c.line((255,169),(255,196),2.5,(111,225,255))
    c.disk(250,166,7,(11,36,82)); c.disk(250,165,4,(204,248,255))
    # A few suspended dew jewels and fine glints.
    for x,y,r in [(98,170,5),(407,160,6),(118,247,3),(390,237,4),(306,76,3),(79,310,3),(426,328,4)]:
        c.disk(x,y,r+2,(62,198,237),.16)
        c.disk(x,y,r,(31,139,188),.86)
        c.disk(x-1,y-2,max(1,r*.3),(207,250,255),.95)
    # Foreground shadow and subtle greenhouse floor reflections.
    c.oval(271,482,107,13,(2,8,25),.6)
    c.line((111,475),(394,475),1,(39,98,108),.35)
    c.line((150,490),(355,490),1,(29,77,94),.28)
    return png_bytes(c.p)


def main():
    outdir=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
    os.makedirs(outdir,exist_ok=True)
    path=os.path.join(outdir,'entry.png')
    data=render()
    with open(path,'wb') as f: f.write(data)


if __name__=='__main__': main()
