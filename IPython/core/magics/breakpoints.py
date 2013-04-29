# -*- coding: ISO-8859-1 -*-
import os
import re

import IPython
from IPython.core.magic import Magics, magics_class,\
    line_magic
from IPython.core import magic_arguments
from IPython.utils.path import unquote_filename


class IPyBreakPoint(object):
    def __init__(self, filename, lineno, temporary=False,
                 cond=None, funcname=None):
        self.filename = filename
        self.lineno = int(lineno)
        self.temporary = temporary
        self.cond = cond
        self.funcname = funcname

    def format_pretty(self):
        return (self.filename, str(self.lineno), str(self.temporary),
                self.cond or "", self.funcname or "")

    @classmethod
    def header(cls):
        return ("Filename", "Line number", "Temporary",
                "Condition", "funcname")


def find_funcdefs(filename, funcname):
    """Locate lines in file filename where funcname is defined.

    Will also match lines inside comments that are syntactically function
    definitions
    """
    defs = []
    with open(filename) as src:
        for lineno, row in enumerate(src, 1):
            if re.match("[ \t]*def[ \t]%s[ \t(]" % funcname, row):
                defs.append((lineno, row))
    return defs


@magics_class
class BreakPointMagics(Magics):
    def __init__(self, shell):
        # You must call the parent constructor
        super(BreakPointMagics, self).__init__(shell)
        self.breakpointlist = []

    @magic_arguments.magic_arguments()
    @line_magic
    def bplist(self, line):
        """Magic function for listing breakpoints in breakpoint list
        """
        args = magic_arguments.parse_argstring(self.bplist, line)
        bptxt = [("Number", ) + IPyBreakPoint.header()] +\
                [(str(idx),) + bp.format_pretty()
                 for idx, bp in enumerate(self.breakpointlist, 1)]
        colwids = [max(x) for x in zip(*[[len(x) for x in bp]
                   for bp in bptxt])]
        colfmts = "  ".join(["%%%ds" % wid for wid in colwids])
        print "Breakpoints"
        for bp in bptxt:
            print colfmts % bp

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('bpnum', type=int, default=None,
                              help='Remove bp with number bpnum')
    @line_magic
    def bprm(self, line):
        """Magic function for removing breakpoints from breakpoint list
        """
        args = magic_arguments.parse_argstring(self.bprm, line)
        bpnum = args.bpnum - 1
        if args.bpnum > len(self.breakpointlist):
            print "Error:  bpnum > total number of breakpoints"
            return
        elif args.bpnum <= 0:
            print "Error:  bpnum <= 0"
            return
        del self.breakpointlist[bpnum]

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('filename', type=str, default=None,
                              help='Filename where breakpoint should be set. '
                                   'Can also be a module specificiation.')
    @magic_arguments.argument('linenumber', type=int, nargs="?", default=None,
                              help='Linenumber for break point')
    @magic_arguments.argument('-t', '--temporary', dest="temporary",
                              action='store_true',
                              help='Flag if breakpoint should only be used '
                                   'once')
    @magic_arguments.argument('-c', '--condition', dest="condition", type=str,
                              default=None,
                              help='Boolean condition to evaluate at '
                                   'breakpoint context.')
    @magic_arguments.argument('-f', '--funcname', dest="funcname", type=str,
                              default=None,
                              help='Name of function in file')
    @line_magic
    def bpadd(self, line):
        """Magic function for adding breakpoints to breakpoint list
        """
        args = magic_arguments.parse_argstring(self.bpadd, line)

        filename = os.path.expanduser(unquote_filename(args.filename))
        if os.path.isfile(filename):
            pass
        else:
            filename = IPython.utils.module_paths.find_mod(filename)
        filename = os.path.normpath(os.path.abspath(filename))
        linenumber = args.linenumber
        if linenumber is None and args.funcname is None:
            print("Must specify either line number or function, no"
                  " breakpoint set!")
            return
        if args.funcname:
            funcdefs = find_funcdefs(filename, args.funcname)
            if len(funcdefs) == 1:
                linenumber = funcdefs[0][0]
            elif len(funcdefs) == 0:
                print "Could not find function %r in %r" % (args.funcname,
                                                            filename)
            else:
                print ("Multiple definitions of %r in file %r on lines: %r" %
                       (args.funcname, filename, [x[0] for x in funcdefs]))

        self.breakpointlist.append(IPyBreakPoint(filename, linenumber,
                                                 args.temporary,
                                                 args.condition,
                                                 args.funcname))

