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
    drawn = False
    cur_pen = 1
    cur_x = 0
    cur_y = 0
    cur_cr_x = cur_x
    cur_cr_y = cur_y

    # page_size = (8900, 7350)  # letter (landscape)
    # page_size = (7350, 8900)  # letter (portrait)
    page_size = (10660, 7995)  # 7470

    p1 = (0, 0)
    p2 = page_size

    scale = (1, 1)
    offset = (0, 0)

    std_font = 48
    alt_font = 48
    cur_font = 48

    char_rel_width = 0.0075
    char_rel_height = 0.015

    char_abs_width = 0
    char_abs_height = 0

    char_size_rel = False

    pen_width = 40*0.35
    stroke_weight = 0

    label_term = '\x03'
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
            if not drawn:
                # draw point
                paths.append((cur_pen, pen_width, [(cur_x, cur_y, 0, 0)]))
        elif cmd == 'PD':
            # pen down
            pen_down = True
            drawn = False
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
            char_size_rel = True

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
            char_size_rel = False

            char_rel_width = 0.0075
            char_rel_height = 0.015

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
        elif cmd == 'SC':
            # scale
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            t = 0
            s = s.split(',')
            if len(s) == 0:
                scale = (1, 1)
                offset = (0, 0)
            else:
                if len(s) > 4:
                    t = int(s[4])
                if t == 1:
                    # isotropic scaling
                    xmin, xmax, ymin, ymax = (float(x) for x in s[0:4])
                    if len(s) > 5:
                        left = min(max(float(s[5])/100, 0), 1)
                        bottom = min(max(float(s[6])/100, 0), 1)
                    else:
                        left = 0.5
                        bottom = 0.5
                    xfactor = (p2[0] - p1[0]) / (xmax - xmin)
                    yfactor = (p2[1] - p1[1]) / (ymax - ymin)
                    if xfactor < yfactor:
                        # fill in x, align in y
                        scale = (xfactor, xfactor)
                        diff = p2[1] - p1[1] - (ymax - ymin) * scale
                        offset = (p1[0] - xmin, p1[1] - ymin + diff*bottom)
                    else:
                        # fill in y, align in x
                        scale = (yfactor, yfactor)
                        diff = p2[0] - p1[0] - (xmax - xmin) * scale
                        offset = (p1[0] - xmin + diff*left, p1[1] - ymin)
                elif t == 2:
                    # point factor
                    # (xmin, ymin) -> p1
                    xmin, xfactor, ymin, yfactor = (float(x) for x in s[0:4])
                    scale = (xfactor, yfactor)
                    offset = (p1[0] - xmin, p1[1] - ymin)
                else:
                    # anisotropic scaling
                    # (xmin, ymin) -> p1, (xmax, ymax) -> p2
                    xmin, xmax, ymin, ymax = (float(x) for x in s[0:4])
                    xfactor = (p2[0] - p1[0]) / (xmax - xmin)
                    yfactor = (p2[1] - p1[1]) / (ymax - ymin)
                    scale = (xfactor, yfactor)
                    offset = (p1[0] - xmin, p1[1] - ymin)
        elif cmd == 'PA':
            # plot absolute

            c = ''
            pts = [(cur_x, cur_y)]

            while c != ';':
                s = ''
                c = glf.read(1)
                if c == ';':
                    # switch to absolute plotting
                    break
                while c == '-' or '0' <= c <= '9':
                    s += c
                    c = glf.read(1)

                # cur_x = int(s)
                cur_x = (int(s)+offset[0])*scale[0]

                s = ''
                c = glf.read(1)
                while c == '-' or '0' <= c <= '9':
                    s += c
                    c = glf.read(1)

                # cur_y = int(s)
                cur_y = (int(s)+offset[1])*scale[1]

                cur_cr_x = cur_x
                cur_cr_y = cur_y

                pts.append((cur_x, cur_y))

            if pen_down:
                paths.append((cur_pen, pen_width, pts))
                drawn = True
        elif cmd == 'LB':
            # label

            c = glf.read(1)

            if char_size_rel:
                char_width = char_rel_width * (p2[0]-p1[0])
                char_height = char_rel_height * (p2[1]-p1[1])
            else:
                char_width = char_abs_width
                char_height = char_abs_height

            while label_term_print or c != label_term:
                if c == '\x08':
                    cur_x -= char_width * 3/2
                elif c == '\r':
                    cur_x = cur_cr_x
                    cur_y = cur_cr_y
                elif c == '\n':
                    cur_cr_y -= char_height * 2
                    cur_x = cur_cr_x
                    cur_y = cur_cr_y
                elif c < ' ':
                    pass
                else:
                    labels.append((cur_x, cur_y, char_width, char_height, cur_pen, cur_font, c))
                    drawn = True
                    cur_x += char_width * 3/2
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
            cur_cr_x = cur_x
            cur_cr_y = cur_y

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.015

            label_term = '\x03'
            label_term_print = False
        elif cmd == 'IN':
            # init
            pen_down = False
            cur_pen = 1
            cur_x = 0
            cur_y = 0
            cur_cr_x = cur_x
            cur_cr_y = cur_y

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.015

            label_term = '\x03'
            label_term_print = False
        elif cmd == 'IP':
            # input P1 and P2 (absolute)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            s = [float(x) for x in s.split(',')]
            if len(s) == 2:
                # set p1, move p2 to keep same x,y offset
                d = tuple(map(lambda i, j: i - j, p2, p1))
                p1 = (s[0], s[1])
                p2 = tuple(map(lambda i, j: i + j, p1, d))
            elif len(s) == 4:
                # set p1 and p2
                p1 = (s[0], s[1])
                p2 = (s[2], s[3])
        elif cmd == 'IR':
            # input P1 and P2 (relative)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            s = [float(x)/100 for x in s.split(',')]
            if len(s) == 2:
                # set p1, move p2 to keep same x,y offset
                d = tuple(map(lambda i, j: i - j, p2, p1))
                p1 = (s[0]*page_size[0], s[1]*page_size[1])
                p2 = tuple(map(lambda i, j: i + j, p1, d))
            elif len(s) == 4:
                # set p1 and p2
                p1 = (s[0]*page_size[0], s[1]*page_size[1])
                p2 = (s[2]*page_size[0], s[3]*page_size[1])
        elif cmd == 'OP':
            # output P1 and P2 - ignored
            pass
        else:
            raise Exception("Unknown HPGL command (%s)" % cmd)

    # render text
    for lb in labels:
        x, y, cw, ch, pen, font, c = lb
        if stroke_weight < 9999:
            pw = 0.1 * min(ch, 1.5*cw) * 1.13**stroke_weight
        else:
            pw = pen_width
        if c in stick_font:
            chr_paths = stick_font[c]
            for pts in chr_paths:
                path = []
                for p in pts:
                    path.append((p[0]/4*cw+x, p[1]/8*cw+y))
                paths.append((pen, pw, path))

    # determine size
    max_x = 0
    max_y = 0

    for path in paths:
        pen, width, pts = path
        for p in pts:
            max_x = max(p[0], max_x)
            max_y = max(p[1], max_y)

    max_x = round(max_x+0.5)
    max_y = round(max_y+0.5)

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
            svg += '<rect x="%0.1f" y="%0.1f" width="%.3f" height="%.3f" fill="%s" />\n' % (pts[0][0], pts[0][1], width, width, pen_color)
        else:
            svg += '<path fill="none" stroke="%s" stroke-width="%.3f" d="M' % (pen_color, width)
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
