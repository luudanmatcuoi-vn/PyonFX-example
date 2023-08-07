import re
from colour import Color
from pyonfx import *

io = Ass("test op 2.ass")
meta, styles_total, lines = io.get_data()

def split_lines_to_syl(line, l):
    for syl in Utils.all_non_empty(line.syls):
        temp = re.match(r".*\\pos\(([0-9\.]+),([0-9\.]+)\).*",line.raw_text)
        try:
            x, y = temp.groups()
            deltax = l.center - float(x)
            deltay = l.middle - float(y)
            print(deltax, deltay)
        except:
            deltax = 0
            deltay = 0

        # Main Effect
        l.layer = 1
        l.actor = "syl_line"

        l.start_time = line.start_time
        l.end_time = line.start_time + syl.end_time
        l.dur = l.end_time - l.start_time

        l.text = (
            "{\\an5\\pos(%.3f,%.3f)}"
            "%s"
            % (
                syl.center - deltax,
                syl.middle - deltay,
                syl.text,
            )
        )
        io.write_line(l)

def prase_clip(clip):
    temp = re.match(r".*\( *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\).*",clip)
    x1,y1,x2,y2 = temp.groups()
    return ( float(x1), float(y1), float(x2), float(y2) )

def clip(x1,y1,x2,y2):
    return "\\clip({},{},{},{})".format(str(x1),str(y1),str(x2),str(y2))

def clip_transfer(clip, trans):
    clip = clip[clip.find("(")+1:clip.find(")")]
    x1,y1,x2,y2 = [float(f) for f in clip.split(",")]
    for t in trans:
        if t[0]=="move":
            x1=x1 + t[1]
            x2=x2 + t[1]
            y1=y1 + t[2]
            y2=y2 + t[2]
        if t[0]=="zoom":
            x1-=t[1]
            x2+=t[1]
            y1-=t[1]
            y2+=t[1]
        if t[0]=="epsilon_zoom":
            x1 = t[3]*(x1-t[1])+ t[1]
            x2 = t[3]*(x2-t[1])+ t[1]
            y1 = t[3]*(y1-t[2])+ t[2]
            y2 = t[3]*(y2-t[2])+ t[2]
    return "\\clip({},{},{},{})".format(str(x1),str(y1),str(x2),str(y2))

def move(x,y,movex,movey):
    return "{},{},{},{}".format(str(x),str(y),str(x+movex),str(y+movey))

def add_effect(string , l):
    if "blur" in string or "be" in string:
        l = l[:l.find("{")+1]+string+l[l.find("{")+1:]
    else:
        l = l[:l.find("}")]+string+l[l.find("}"):]
    return l

def glow(l):
    l.layer = glow_layer
    l.actor = l.actor + " glow"
    # Bỏ cái glow ở trc đi
    l.text = re.sub(r"\\blur[0-9\.]+","",l.text)
    l.text = add_effect("{}".format("\\blur7\\alpha&H100&\\c&HFFFFFF&") ,l.text)    
    io.write_line(l)

def make_clip(l, layer, effect, color = "\\c&H000000&"):
    l.layer = layer
    l.text = add_effect(effect ,l.text)
    if "\\c&H" in l.text:
        l.text = re.sub(r"\\c&H[0-9ABCDEF]{6}&", "\\c" + color ,l.text )
    else:
        l.text = add_effect("\\c"+color , l.text)

    if "\\fad" in l.text:
        temp = re.match(r".*\\fad\( *([0-9\.]+) *\, *([0-9\.]+) *\).*",l.text)
        inn , out = temp.groups()
        if int(inn)!= 0:
            l.text = add_effect("\\alpha&H20&\\t({},{},\\alpha&H00&)".format(str(inn),str(int(inn)+1)) ,l.text)

        if int(out)!= 0:
            l.text = add_effect("\\alpha&H00&\\t({},{},\\alpha&H20&)".format(str(out),str(int(out)+1)) ,l.text)

    io.write_line(l)

def color_trans(string):
    if "#" in string:
        string = "&H"+string[5:7]+string[3:5]+string[1:3]+"&"
    else:
        string = "#"+string[6:8]+string[4:6]+string[2:4]
    return string

def make_clip_layers( l ,clip):
    l.actor = l.actor + " clip"
    l.style = l.style + " clip"
    color_1 = Color(color_trans("&HC131F2&"))
    # color_2 = Color("#180419")
    color_2 = Color(color_trans("&HC131F2&"))
    color_2.luminance = 0
    color_list = [ color_trans(g.hex_l)  for g in list(color_2.range_to(color_1, blend))]
    if "\\move" in l.text:
        temp = re.match(r".*\\move\( *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\).*",l.text)
        m_x1 , m_y1, m_x2, m_y2 , t1 , t2 = temp.groups()
        movex_local = float(m_x2) - float(m_x1)
        movey_local = float(m_y2) - float(m_y1)
        if int( movex_local + movex + movey_local + movey ) == 0:
            clip = clip_transfer(clip,[["move",movex,movey]])
        for blur in range(0-blend//2,blend//2+1):
            make_clip(l.copy(), l.layer+blend//2+1+blur, "{}\\t({},{},{})".format(clip_transfer(clip,[["zoom",blend-blur]]) ,t1,t2, clip_transfer(clip,[["zoom",blend-blur],["move",movex_local,movey_local]]) )  , color_list[blend//2+blur])
    else:
        for blur in range(0-blend//2+1,blend//2 ):
            make_clip(l.copy(), l.layer+blend//2+1+blur, "{}".format(clip_transfer(clip,[["zoom",blend-blur]]) ) , color_list[blend//2+blur])


def make_op_kara(line):
    for syl in Utils.all_non_empty(line.syls):
        line.layer = base_layer
        line.comment = False
        line.actor = "fx"

        # Xu ly fade time 
        fade_id = [i for i in range(len(time_data)) if time_data[i]["start_time"] == line.start_time][0]
        try:
            leadin_time = abs(time_data[fade_id]["start_time"]-time_data[fade_id-1]["end_time"])
        except:
            leadin_time = 1000000000000
        try:
            leadout_time = abs(time_data[fade_id]["end_time"]-time_data[fade_id+1]["start_time"])
        except:
            leadout_time = 1000000000000
        fadein_time = min(root_fade_time,leadin_time/2)
        fadeout_time = min(root_fade_time,leadout_time/2)

        # Find Clip
        clip = [c["clip"] for c in clip_data if c["start_time"] == line.start_time and  c["text"] == syl.text ][0]

        l = line.copy()
        # Leadin Effect
        l.start_time = line.start_time - fadein_time
        l.end_time = line.start_time
        l.dur = l.end_time - l.start_time

        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)\\fad(%d,0)}%s" % (
            syl.center,
            syl.middle,
            fadein_time,
            syl.text,
        )
        io.write_line(l)

        main_l = l

        # Glow
        glow(main_l.copy())

        # Clip Leadin Effect
        make_clip_layers(main_l.copy(), clip)

        ##### Main Effect
        l = line.copy()
        l.layer = base_layer + 1 
        l.style = line.style
        l.start_time = line.start_time
        l.end_time = line.start_time + (syl.start_time + syl.end_time)/2
        l.dur = syl.end_time - syl.start_time
        l.text = (
            "{\\an5\\blur0.5"
            "\\move(%s,%d,%d)"
            "}%s"
            % (
                move( syl.center, syl.middle, movex, movey),
                syl.start_time,
                l.dur / 2 + syl.start_time,
                syl.text,
            )
        )
        io.write_line(l)

        main_l = l

        # Glow
        glow(main_l.copy())

        # # Clip Main Effect
        make_clip_layers(main_l.copy(), clip)



        ##### Second Main Effect
        l = line.copy()
        l.layer = base_layer + 1
        l.comment  = False
        l.style = line.style
        l.start_time = line.start_time + (syl.start_time + syl.end_time)/2
        l.end_time = line.end_time
        l.dur = syl.end_time - syl.start_time
        l.text = (
            "{\\an5\\blur0.5"
            "\\move(%s,%d,%d)"
            "}%s"
            % (
                move( syl.center+movex, syl.middle+movey, 0-movex, 0-movey),
                0,
                l.dur/2,
                syl.text,
            )
        )
        io.write_line(l)

        main_l = l

        # Glow
        glow(main_l.copy())

        # Clip Second Main Effect
        make_clip_layers(main_l.copy(), clip)

        ### Leadout Effect
        l = line.copy()
        l.start_time = line.end_time
        l.end_time = line.end_time + fadeout_time
        l.dur = l.end_time - l.start_time

        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)\\fad(0,%d)}%s" % (
            syl.center,
            syl.middle,
            fadeout_time,
            syl.text,
        )
        io.write_line(l)

        main_l = l

        # Glow
        glow(main_l.copy())

        # Clip Leadin Effect
        make_clip_layers(main_l.copy(), clip)













def make_op_viet_effect(line):
    for syl in Utils.all_non_empty(line.syls):
        line.layer = base_layer
        line.comment = False
        line.actor = "viet_op_fx"
        # Xu ly fade time 
        fade_id = [i for i in range(len(time_data)) if time_data[i]["start_time"] == line.start_time][0]
        try:
            leadin_time = abs(time_data[fade_id]["start_time"]-time_data[fade_id-1]["end_time"])
        except:
            leadin_time = 1000000000000
        try:
            leadout_time = abs(time_data[fade_id]["end_time"]-time_data[fade_id+1]["start_time"])
        except:
            leadout_time = 1000000000000
        fadein_time = min(root_fade_time,leadin_time/2)
        fadeout_time = min(root_fade_time,leadout_time/2)

        # Find Clip
        clip = [c["clip"] for c in clip_data if c["start_time"] == line.start_time and  c["text"] == syl.text ][0]


        l = line.copy()
        # Leadin Effect
        l.start_time = line.start_time - fadein_time
        l.end_time = line.start_time
        l.dur = l.end_time - l.start_time

        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)\\fad(%d,0)}%s" % (
            syl.center,
            syl.middle,
            fadein_time,
            syl.text,
        )
        io.write_line(l)

        main_l = l

        # Glow
        glow(main_l.copy())

        # Clip Leadin Effect
        make_clip_layers(main_l.copy(), clip)


        ##### Main Effect
        l = line.copy()
        l.start_time = line.start_time
        l.end_time = line.end_time

        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)}%s" % (
            syl.center,
            syl.middle,
            syl.text,
        )
        io.write_line(l)

        main_l = l

        # Glow
        glow(main_l.copy())

        make_clip_layers(main_l.copy(), clip)



        l = line.copy()
        # OUT Effect
        l.start_time = line.end_time
        l.end_time = line.end_time + fadeout_time
        l.dur = l.end_time - l.start_time

        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)\\fad(0,%d)}%s" % (
            syl.center,
            syl.middle,
            fadeout_time,
            syl.text,
        )
        io.write_line(l)










def sub(line, l):
    # Translation Effect
    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    l.text = "%s" % ( line.text)

    io.write_line(l)

# Get clip data
clip_data = []
for line in lines:
    if line.actor == "syl_line":
        try:
            clip = re.findall(r"\\[i]{0,1}clip\([0-9\.,]+\)",line.raw_text)[0]
            clip = clip.replace("i","")
        except:
            clip = "\\clip(0,0,0,0)"
        clip = {"start_time": line.start_time, "clip": clip , "text": line.text }
        clip_data+=[clip]

# Get start - end time
time_data = []
for line in lines:
    if line.actor == "op_viet":
        clip = {"start_time": line.start_time, "end_time": line.end_time }
        time_data+=[clip]


movex = 0
movey = -20
root_fade_time = 500
glow_layer = 0
base_layer = 1
blend = 7

for line in lines:
    # Generating lines
    if not any([line.actor == "syl_line" for line in lines]):
        if line.actor == "line_need_split":
            split_lines_to_syl(line, line.copy())
    else:
        if line.actor == "line_need_split":
            make_op_kara(line)
        if line.actor == "op_viet":
            make_op_viet_effect(line)

io.save()
io.open_aegisub()
