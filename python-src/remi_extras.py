# -*- coding: utf-8 -*-
"""
Extra widgets, routines etc. to work with REMI

    https://github.com/rawpython/remi


@author: Martinus Werts
"""

from remi.gui import TextInput

class LineWriterBox(TextInput):
    def __init__(self, *args,
                 initlines = [],
                 maxlines = 50,
                 reverse_out = False,
                 **kwargs):
        # kwargs override
        kwargs.update(single_line = False)
        super().__init__(*args, **kwargs)
        self.style['resize']='none'
        # I would like the textarea to autoscroll
        # the following CSS hack does not work
        # self.style['scrollTop']=self.style['scrollHeight']
        # for now just use inverted writeln (new lines added to top)
        self.maxlines = maxlines
        self.reverse_out = reverse_out
        self.lines = []
        for line in initlines:
            self.writeln(line)
            
    def writeln(self, line):
        self.lines.append(line)
        while len(self.lines) > self.maxlines:
            self.lines.pop(0)
        outstr = ''
        if self.reverse_out:
            outlines = self.lines[-1::-1]
        else:
            outlines = self.lines
        for line in outlines:
            outstr += line+'\n'
        self.set_text(outstr)
        
    

