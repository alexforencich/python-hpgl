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

from __future__ import print_function

def hpgl2svg(argv=None):
    import sys
    from .hpgl import parse_hpgl
    from .hpgl import generate_svg

    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print("Missing input file")
        exit(1)

    hpgl_name = argv[1]
    svg_name = hpgl_name + '.svg'

    if len(argv) > 2:
        svg_name = argv[2]

    print("Opening input HPGL file '%s'" % hpgl_name)
    hpglf = open(hpgl_name, 'r')
    print("Opening output SVG file '%s'" % svg_name)
    imgf = open(svg_name, 'w')

    print("Parsing HPGL")

    paths = parse_hpgl(hpglf)

    print("Writing SVG")

    imgf.write(generate_svg(paths))

    print("Done")

def hprtl2bmp(argv=None):
    import sys
    from .hprtl import parse_hprtl
    from .hprtl import generate_bmp

    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print("Missing input file")
        exit(1)

    rtl_name = argv[1]
    bmp_name = rtl_name + '.bmp'

    if len(argv) > 2:
        bmp_name = argv[2]
    
    print("Opening input HPRTL file '%s'" % rtl_name)
    rtlf = open(rtl_name, 'rb')
    print("Opening output BMP file '%s'" % bmp_name)
    imgf = open(bmp_name, 'wb')

    print("Parsing RTL")

    plane_data = parse_hprtl(rtlf)

    print("Writing BMP")

    imgf.write(generate_bmp(plane_data))

    print("Done")
