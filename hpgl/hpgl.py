"""

Copyright (c) 2015 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from .fonts import stick_font

def parse_hpgl(gl_file):
    """Convert HP Graphics Language (HPGL) to list of paths"""

    border = 10

    pen_down = False
    cur_pen = 1
    cur_x = 0
    cur_y = 0
    cto_x = 0 # text offset
    cto_y = 0

    std_font = 48
    alt_font = 48
    cur_font = 48

    char_rel_width = 0.0075
    char_rel_height = 0.0075

    char_abs_width = 0
    char_abs_height = 0

    pen_width = 1
    stroke_weight = 0

    label_term = chr(3)
    label_term_print = False

    paths = []
    labels = []

    if type(gl_file) == str:
        glf = open(gl_file, 'r')
    else:
        glf = gl_file

    while True:
        c = glf.read(1)
        while c == ';' or c == ' ' or c == '\r' or c == '\n':
            c = glf.read(1)
        cmd = c + glf.read(1)
        cmd = cmd.upper()

        if len(cmd) < 2:
            break

        if cmd == 'PU':
            # pen up
            pen_down = False
        elif cmd == 'PD':
            # pen down
            pen_down = True
        elif cmd == 'SP':
            # select pen
            c = glf.read(1)
            if c == ';':
                continue
            cur_pen = int(c)
        elif cmd == 'LT':
            pass
        elif cmd == 'SA':
            # select alternate
            cur_font = alt_font
        elif cmd == 'SS':
            # select standard
            cur_font = std_font
        elif cmd == 'SR':
            # specify relative character sizes
            s = ''
            c = glf.read(1)
            while c != ',':
                s += c
                c = glf.read(1)
            char_rel_width = float(s)/100.0
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            char_rel_height = float(s)/100.0
        elif cmd == 'SI':
            # specify absolute character sizes
            s = ''
            c = glf.read(1)
            while c != ',':
                s += c
                c = glf.read(1)
            char_abs_width = float(s)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            char_abs_height = float(s)
        elif cmd == 'PA':
            # plot absolute

            c = ''
            pts = [(cur_x, cur_y, cto_x, cto_y)]

            while c != ';':
                s = ''
                c = glf.read(1)
                if c == ';':
                    cur_x = 0
                    cur_y = 0
                    cto_x = 0
                    cto_y = 0
                    pts.append((0,0,0,0))
                    break
                while c == '-' or ord(c) >= 48 and ord(c) <= 57:
                    s += c
                    c = glf.read(1)

                cur_x = int(s)

                s = ''
                c = glf.read(1)
                while c == '-' or ord(c) >= 48 and ord(c) <= 57:
                    s += c
                    c = glf.read(1)

                cur_y = int(s)

                cto_x = 0
                cto_y = 0

                pts.append((cur_x, cur_y, 0, 0))

            if pen_down:
                paths.append((cur_pen, pen_width, pts))
        elif cmd == 'LB':
            # label

            c = glf.read(1)
            x = cur_x
            y = cur_y
            tx = cto_x
            ty = cto_y
            while label_term_print or c != label_term:
                if ord(c) == 8:
                    cto_x -= char_rel_width * 3/2
                elif ord(c) == 10:
                    cto_x = tx
                    cto_y -= char_rel_height * 2
                elif ord(c) < 32:
                    pass
                else:
                    labels.append((cur_x, cur_y, cto_x, cto_y, char_rel_width, char_rel_height, cur_pen, cur_font, c))
                    cto_x += char_rel_width * 3/2
                    if c == label_term:
                        break
                c = glf.read(1)
        elif cmd == 'DI':
            # absolute direction
            s = ''
            c = glf.read(1)
            if c == ';':
                #run = 1
                #rise = 0
                continue
            while c != ',':
                s += c
                c = glf.read(1)
            #run = float(s)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            #rise = float(s)
        elif cmd == 'DF':
            # defaults
            pen_down = False
            cur_pen = 1
            cur_x = 0
            cur_y = 0
            cto_x = 0
            cto_y = 0

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.0075

            label_term = chr(3)
            label_term_print = False
        elif cmd == 'IN':
            # init
            pen_down = False
            cur_pen = 1
            cur_x = 0
            cur_y = 0
            cto_x = 0
            cto_y = 0

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.0075

            label_term = chr(3)
            label_term_print = False
        elif cmd == 'OP':
            # output P1 and P2 - ignored
            pass
        else:
            raise Exception("Unknown HPGL command (%s)" % cmd)

    # determine size
    max_x = 0
    max_y = 0

    # max extent of vector graphics
    for path in paths:
        pen, width, pts = path
        for p in pts:
            max_x = max(p[0], max_x)
            max_y = max(p[1], max_y)

    # max extent of text
    for lb in labels:
        max_x = max(lb[0]/(1-(lb[2]+lb[4])), max_x)
        max_y = max(lb[1]/(1-(lb[3]+lb[5])), max_y)

    max_x = round(max_x+0.5)
    max_y = round(max_y+0.5)

    # add text offsets
    paths2 = []
    for path in paths:
        pen, width, pts = path
        pts2 = []
        for p in pts:
            pts2.append((p[0] + p[2]*max_x, p[1] + p[3]*max_y))
        paths2.append((pen, width, pts2))
    paths = paths2

    # render text
    for lb in labels:
        x, y, tx, ty, cw, ch, pen, font, c = lb
        width = cw*max_x
        height = ch*max_y
        x += tx*max_x
        y += ty*max_y
        if stroke_weight < 9999:
            pw = 0.1 * min(height, 1.5*width) * 1.13**stroke_weight
        else:
            pw = pen_width
        if c in stick_font:
            chr_paths = stick_font[c]
            for pts in chr_paths:
                path = []
                for p in pts:
                    path.append((p[0]/4*width+x, p[1]/8*height+y))
                paths.append((pen, pw, path))

    max_x += border*2
    max_y += border*2

    # flip y axis and shift
    paths2 = []
    for path in paths:
        pen, width, pts = path
        pts2 = []
        for p in pts:
            pts2.append((p[0]+border, max_y-p[1]-border))
        paths2.append((pen, width, pts2))

    return paths2, max_x, max_y

def generate_svg(paths):
    """Generate SVG from list of paths"""

    paths, max_x, max_y = paths

    pen_colors = ['none', 'black', 'blue', 'green', 'yellow', 'red', 'magenta', 'cyan']

    svg = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    svg += '<!-- Created with python-hpgl (http://github.com/alexforencich/python-hpgl/) -->\n'
    svg += '<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg" version="1.1">\n' % (max_x, max_y)
    svg += '<style>path {fill: none; stroke-linecap: round; stroke-linejoin: round;}</style>\n'

    for path in paths:
        pen, width, pts = path
        pen_color = pen_colors[pen]
        if len(pts) == 1:
            svg += '<rect x="%0.1f" y="%0.1f" width="%d" height="%d" fill="%s" />\n' % (pts[0][0], pts[0][1], width, width, pen_color)
        else:
            svg += '<path fill="none" stroke="%s" stroke-width="%d" d="M' % (pen_color, width)
            first = True
            for p in pts:
                if not first:
                    svg += ' L'
                svg += '%0.1f,%0.1f' % p
                first = False
            svg += '" />\n'

    svg += '</svg>\n'

    return svg

def hpgl2svg(gl_file):
    """Convert HP Graphics Language (HPGL) to SVG"""

    return generate_svg(parse_hpgl(gl_file))
