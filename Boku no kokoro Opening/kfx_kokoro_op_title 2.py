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

# def prase_clip(clip):
#     temp = re.match(r".*\( *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\).*",clip)
#     x1,y1,x2,y2 = temp.groups()
#     return ( float(x1), float(y1), float(x2), float(y2) )

# def clip(x1,y1,x2,y2):
#     return "\\clip({},{},{},{})".format(str(x1),str(y1),str(x2),str(y2))

def clip_transfer(clip, trans):
    # clip = clip[clip.find("(")+1:clip.find(")")]
    # clip = re.findall(r"[0-9\.]+",clip)
    tempclip = []
    while True:
        # print(clip)
        tea = re.findall(r"[0-9\.]+ [0-9\.]+",clip)
        if len(tea)!=0:
            tea = tea[0]
            tempclip +=[[float(g) for g in tea.split(" ")]]
            clip = clip.replace(tea,"")
        else:
            break
    clip = tempclip
    # print(clip)
    forcus_point = [sum([a[0] for a in clip ])/len(clip) , sum([a[1] for a in clip ])/len(clip)  ]
    # print(forcus_point)
    # x1,y1,x2,y2 = [float(f) for f in clip.split(",")]
    for t in trans:
        # if t[0]=="move":
        #     x1=x1 + t[1]
        #     x2=x2 + t[1]
        #     y1=y1 + t[2]
        #     y2=y2 + t[2]
        if t[0]=="zoom":
            if clip[0][0] == 0:
                clip[0][0] = 1
            ratio = (clip[0][0]+t[1])/clip[0][0]
            pre_clip = [ [ (clip[gb][0]-forcus_point[0])*ratio+forcus_point[0] , (clip[gb][1]-forcus_point[1])*ratio+forcus_point[1] ] for gb in range(len(clip))]

            ratio = (clip[0][0]+t[1]-3)/clip[0][0]
            res_clip = [ [ (clip[gb][0]-forcus_point[0])*ratio+forcus_point[0] , (clip[gb][1]-forcus_point[1])*ratio+forcus_point[1] ] for gb in range(len(clip))]
            res_clip.reverse()

            def pra_clip(cl):
                rs = "m {} {} l ".format(cl[0][0],cl[0][1])
                cl = cl[1:]
                rs = rs + " ".join([str(ka[0])+ " "+ str(ka[1]) for ka in cl]) 
                return rs
        # if t[0]=="epsilon_zoom":
        #     x1 = t[3]*(x1-t[1])+ t[1]
        #     x2 = t[3]*(x2-t[1])+ t[1]
        #     y1 = t[3]*(y1-t[2])+ t[2]
        #     y2 = t[3]*(y2-t[2])+ t[2]
    return "\\clip(1,{} {})".format( pra_clip(pre_clip) , pra_clip(res_clip) )

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

    if "clip" in l.text:
        l.text = re.sub(r"\\i{0,1}clip\([^\)]+\)","",l.text)
        
    l.text = add_effect(effect ,l.text)
    if "\\c&H" in l.text:
        l.text = re.sub(r"\\c&H[0-9ABCDEF]{6}&", "\\c" + color ,l.text )
    else:
        l.text = add_effect("\\c"+color , l.text)

    if "\\fad" in l.text:
        temp = re.match(r".*\\fad\( *([0-9\.]+) *\, *([0-9\.]+) *\).*",l.text)
        inn , out = temp.groups()
        # if int(inn)!= 0:
            # l.text = add_effect("\\alpha&HFF&\\t({},{},\\alpha&H00&)".format(str(inn),str(int(inn)+1)) ,l.text)

        # if int(out)!= 0:
            # l.text = add_effect("\\alpha&H00&\\t({},{},\\alpha&HFF&)".format(str(out),str(int(out)+1)) ,l.text)

    io.write_line(l)

def color_trans(string):
    if "#" in string:
        string = "&H"+string[5:7]+string[3:5]+string[1:3]+"&"
    else:
        string = "#"+string[6:8]+string[4:6]+string[2:4]
    return string

def make_clip_layers( l ,clip):
    global bodem
    l.actor = l.actor + " clip"
    l.actor = str(bodem).zfill(4)+"|"+re.sub(r".*\|","",l.actor)
    bodem+=1
    l.style = l.style + " clip"
    color_1 = Color(color_trans("&HC131F2&"))
    # color_2 = Color("#180419")
    color_2 = Color(color_trans("&HC131F2&"))
    color_2.luminance = 0
    color_list = [ color_trans(g.hex_l)  for g in list(color_2.range_to(color_1, blend))]

    # if "\\move" in l.text:
    #     temp = re.match(r".*\\move\( *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\, *([0-9\.]+) *\).*",l.text)
    #     m_x1 , m_y1, m_x2, m_y2 , t1 , t2 = temp.groups()
    #     movex_local = float(m_x2) - float(m_x1)
    #     movey_local = float(m_y2) - float(m_y1)
    #     if int( movex_local + movex + movey_local + movey ) == 0:
    #         clip = clip_transfer(clip,[["move",movex,movey]])
    #     for blur in range(0-blend//2,blend//2+1):
    #         make_clip(l.copy(), l.layer+blend//2+1+blur, "{}\\t({},{},{})".format(clip_transfer(clip,[["zoom",blend-blur]]) ,t1,t2, clip_transfer(clip,[["zoom",blend-blur],["move",movex_local,movey_local]]) )  , color_list[blend//2+blur])
    # else:




    # for blur in range(0-blend//2+1,blend//2 ):
    #     # print(blur)
    #     # print('a')
    make_clip(l.copy(), 2, clip , "&HC131F2&")

bodem = 1
def make_op_kara(line):
    global bodem
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
        l.actor = str(bodem).zfill(4)+"|"+re.sub(r".*\|","",l.actor)
        bodem+=1
        l.start_time = line.start_time - fadein_time
        l.end_time = line.start_time
        l.dur = l.end_time - l.start_time

        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)\\fad(%d,0)}%s" % (
            syl.center,
            syl.middle,
            fadein_time,
            syl.text,
        )
        l.text = add_effect(clip.replace("\\clip","\\iclip") ,l.text)   
        io.write_line(l)

        main_l = l

        # # Glow
        # glow(main_l.copy())

        # Clip Leadin Effect
        make_clip_layers(main_l.copy(), clip)




        ##### Main Effect
        l = line.copy()
        l.actor = str(bodem).zfill(4)+"|"+re.sub(r".*\|","",l.actor)
        bodem+=1
        l.layer = base_layer + 1 
        l.style = line.style
        l.start_time = line.start_time
        # l.end_time = line.start_time + (syl.start_time + syl.end_time)/2
        l.end_time = line.end_time
        l.dur = syl.end_time - syl.start_time
        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)}%s" % (
            syl.center,
            syl.middle,
            syl.text,
        )
        l.text = add_effect(clip.replace("\\clip","\\iclip") ,l.text)   

        io.write_line(l)

        main_l = l

        # # Glow
        # glow(main_l.copy())

        # # Clip Main Effect
        make_clip_layers(main_l.copy(), clip)



        # ##### Second Main Effect
        # l = line.copy()
        # l.layer = base_layer + 1
        # l.comment  = False
        # l.style = line.style
        # l.start_time = line.start_time + (syl.start_time + syl.end_time)/2
        # l.end_time = line.end_time
        # l.dur = syl.end_time - syl.start_time
        # l.text = (
        #     "{\\an5\\blur0.5"
        #     "\\move(%s,%d,%d)"
        #     "}%s"
        #     % (
        #         move( syl.center+movex, syl.middle+movey, 0-movex, 0-movey),
        #         0,
        #         l.dur/2,
        #         syl.text,
        #     )
        # )
        # io.write_line(l)

        # main_l = l

        # # # Glow
        # # glow(main_l.copy())

        # # Clip Second Main Effect
        # make_clip_layers(main_l.copy(), clip)

        ### Leadout Effect
        l = line.copy()
        l.actor = str(bodem).zfill(4)+"|"+re.sub(r".*\|","",l.actor)
        bodem+=1
        l.start_time = line.end_time
        l.end_time = line.end_time + fadeout_time
        l.dur = l.end_time - l.start_time

        l.text = "{\\an5\\blur0.5\\pos(%.3f,%.3f)\\fad(0,%d)}%s" % (
            syl.center,
            syl.middle,
            fadeout_time,
            syl.text,
        )
        l.text = add_effect(clip.replace("\\clip","\\iclip") ,l.text)   
        io.write_line(l)

        main_l = l

        # # Glow
        # glow(main_l.copy())

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

        # # Glow
        # glow(main_l.copy())

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

        # # Glow
        # glow(main_l.copy())

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
            clip = clip.replace("\\i","\\")
        except:
            clip = "\\clip(0,0,0,0)"
        clip = {"start_time": line.start_time, "clip": clip , "text": line.text }
        clip_data+=[clip]
# print(clip_data)

# Get start - end time
time_data = []
for line in lines:
    if line.style == "OP vie" and line.comment:
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
        if line.style == "OP Romaji":
            make_op_kara(line)
        if line.style == "OP vie":
            make_op_viet_effect(line)

io.save()
io.open_aegisub()
