import re
from colour import Color
from pyonfx import *

io = Ass("temp_ed.ass")
meta, styles_total, lines = io.get_data()

# def prase_clip(clip):
#     temp = re.match(r".*\( *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\).*",clip)
#     x1,y1,x2,y2 = temp.groups()
#     return ( float(x1), float(y1), float(x2), float(y2) )

# def clip(x1,y1,x2,y2):
#     return "\\clip({},{},{},{})".format(str(x1),str(y1),str(x2),str(y2))

# def clip_transfer(clip, trans):
#     clip = clip[clip.find("(")+1:clip.find(")")]
#     x1,y1,x2,y2 = [float(f) for f in clip.split(",")]
#     for t in trans:
#         if t[0]=="move":
#             x1=x1 + t[1]
#             x2=x2 + t[1]
#             y1=y1 + t[2]
#             y2=y2 + t[2]
#         if t[0]=="zoom":
#             x1-=t[1]
#             x2+=t[1]
#             y1-=t[1]
#             y2+=t[1]
#         if t[0]=="epsilon_zoom":
#             x1 = t[3]*(x1-t[1])+ t[1]
#             x2 = t[3]*(x2-t[1])+ t[1]
#             y1 = t[3]*(y1-t[2])+ t[2]
#             y2 = t[3]*(y2-t[2])+ t[2]
#     return "\\clip({},{},{},{})".format(str(x1),str(y1),str(x2),str(y2))

def move(x,y,movex,movey):
    return "{},{},{},{}".format(str(x),str(y),str(x+movex),str(y+movey))

def add_effect(string , l):
    if "blur" in string or "be" in string:
        l = l[:l.find("{")+1]+string+l[l.find("{")+1:]
    else:
        l = l[:l.find("}")]+string+l[l.find("}"):]
    return l

# def glow(l):
#     l.layer = glow_layer
#     l.actor = l.actor + " glow"
#     # Bỏ cái glow ở trc đi
#     l.text = re.sub(r"\\blur[0-9\.]+","",l.text)
#     l.text = add_effect("{}".format("\\blur7\\alpha&H100&\\c&HFFFFFF&") ,l.text)    
#     io.write_line(l)

def make_ending_kara(line):
    for syl in Utils.all_non_empty(line.syls):
        line.layer = base_layer
        line.comment = False
        line.actor = "fx_ed"

        fadeout_time = root_fade_time
        fadein_time = root_fade_time

        # xu ly moving set
        alignment = line.styleref.alignment

        if alignment >= 5:
            movex = default_move
            movey = default_move
        else:
            movex = default_move
            movey = 0-default_move
        posx = syl.x
        posy = syl.y
        # Tim x-y cho main effect
        try:
            x_main = re.match(r".*\\x([0-9\.\-]+).*",line.raw_text)
            x_main = float(x_main.groups()[0])
            y_main = re.match(r".*\\y([0-9\.\-]+).*",line.raw_text)
            y_main = float(y_main.groups()[0])
        except:
            x_main, y_main = 0,0

        # Leadin Effect
        l = line.copy()
        l.start_time = line.start_time - fadein_time
        l.end_time = line.start_time
        l.dur = l.end_time - l.start_time

        l.text = "{\\blur0.5\\move(%s,%s,%s,%s,0,%d)\\fad(%d,0)}%s" % (
            posx-movex , posy-movey , posx , posy ,
            fadein_time,
            fadein_time/3,
            syl.text,
        )
        io.write_line(l)

        main_l = l

        ##### Main Effect
        l = line.copy()
        l.layer = base_layer + 1 
        l.style = line.style
        l.start_time = line.start_time
        l.end_time = line.end_time
        dur = line.end_time - line.start_time
        l.dur = syl.end_time - syl.start_time
        # get color
        pri_color = syl.styleref.color1
        sec_color = syl.styleref.color2
        outline_color = syl.styleref.color3
        shadow_color = syl.styleref.color4
        l.text = (
            "{\\blur0.5"
            # "\\pos(%s,%s)"
            "\\move(%s,%s,%s,%s,%d,%d)"
            "\\t(%d,%d,%s)\\t(%d,%d,%s)"
            "}%s"
            % (
                posx,
                posy,
                posx + x_main*dur*24/1000/12,
                posy + y_main*dur*24/1000/12,
                0,
                dur,
                syl.start_time,
                syl.start_time+ l.dur / 2,
                "\\1c{}\\3c{}\\fscx120\\fscy120".format(outline_color,pri_color),
                syl.start_time + l.dur / 2,
                syl.end_time,
                "\\1c{}\\3c{}\\fscx100\\fscy100".format(pri_color,outline_color),
                syl.text,
            )
        )
        io.write_line(l)

        posx = posx + x_main*dur*24/1000/12
        posy = posy + y_main*dur*24/1000/12

        main_l = l
        ### Leadout Effect
        l = line.copy()
        l.start_time = line.end_time
        l.end_time = line.end_time + fadeout_time
        l.dur = l.end_time - l.start_time
        movey= 0-movey
        l.text = "{\\blur0.5\\move(%s,%s,%s,%s,0,%d)\\fad(0,%d)}%s" % (
            posx , posy , posx+movex , posy+movey ,
            fadeout_time,
            fadeout_time/3,
            syl.text,
        )
        io.write_line(l)

        main_l = l







def make_ed_viet(line):
    line.layer = base_layer
    line.comment = False
    line.actor = "fx_ed_viet"
    
    fadeout_time = root_fade_time
    fadein_time = root_fade_time

    # xu ly moving set
    alignment = line.styleref.alignment

    if alignment >= 5:
        movex = default_move
        movey = default_move
    else:
        movex = default_move
        movey = 0-default_move
    posx = line.x
    posy = line.y
    # Tim x-y cho main effect
    try:
        x_main = re.match(r".*\\x([0-9\.\-]+).*",line.raw_text)
        x_main = float(x_main.groups()[0])
        y_main = re.match(r".*\\y([0-9\.\-]+).*",line.raw_text)
        y_main = float(y_main.groups()[0])
    except:
        x_main, y_main = 0,0

    # Leadin Effect
    l = line.copy()
    l.start_time = line.start_time - fadein_time
    l.end_time = line.start_time
    l.dur = l.end_time - l.start_time

    l.text = "{\\blur0.5\\move(%s,%s,%s,%s,0,%d)\\fad(%d,0)}%s" % (
        posx-movex , posy-movey , posx , posy ,
        fadein_time,
        fadein_time/3,
        line.text,
    )
    io.write_line(l)

    main_l = l

    ##### Main Effect
    l = line.copy()
    l.layer = base_layer + 1 
    l.style = line.style
    l.start_time = line.start_time
    l.end_time = line.end_time
    dur = line.end_time - line.start_time
    l.dur = line.end_time - line.start_time
    # get color
    pri_color = line.styleref.color1
    sec_color = line.styleref.color2
    outline_color = line.styleref.color3
    shadow_color = line.styleref.color4
    l.text = (
        "{\\blur0.5"
        # "\\pos(%s,%s)"
        "\\move(%s,%s,%s,%s,%d,%d)"
        "}%s"
        % (
            posx,
            posy,
            posx + x_main*dur*24/1000/12,
            posy + y_main*dur*24/1000/12,
            0,
            dur,
            line.text,
        )
    )
    io.write_line(l)

    posx = posx + x_main*dur*24/1000/12
    posy = posy + y_main*dur*24/1000/12

    main_l = l
    ### Leadout Effect
    l = line.copy()
    l.start_time = line.end_time
    l.end_time = line.end_time + fadeout_time
    l.dur = l.end_time - l.start_time
    movey = 0 - movey
    l.text = "{\\blur0.5\\move(%s,%s,%s,%s,0,%d)\\fad(0,%d)}%s" % (
        posx , posy , posx+movex , posy+movey ,
        fadeout_time,
        fadeout_time/3,
        line.text,
    )
    io.write_line(l)

    main_l = l










def sub(line, l):
    # Translation Effect
    l.start_time = line.start_time
    l.end_time = line.end_time
    l.dur = l.end_time - l.start_time

    l.text = "%s" % ( line.text)

    io.write_line(l)

# Get start - end time
time_data = []
for line in lines:
    if line.actor == "ed_romaji":
        clip = {"start_time": line.start_time, "end_time": line.end_time }
        time_data+=[clip]


movex = 0
movey = -20
root_fade_time = 500
glow_layer = 0
base_layer = 1
blend = 7
default_move = 40

for line in lines:
    # Generating lines
    if line.actor == "ed_romaji":
        make_ending_kara(line)
    if line.actor == "ed_viet":
        make_ed_viet(line)

io.save()
io.open_aegisub()
