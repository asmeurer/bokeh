from collections import defaultdict

try:
    long
except NameError:
    long = int

numbers = (int, long, float)

class CExpr(object):
    def __new__(cls, *args):
        obj = super(CExpr, cls).__new__(cls)
        obj.args = tuple(args)
        return obj

    def __eq__(self, other):
        return type(self) == type(other) and self.args == other.args

    def __hash__(self):
        return hash(self.args)

    def __add__(self, other):
        return CAdd(self, other)

    __radd__ = __add__

class CAdd(CExpr):
    def __new__(cls, *args):
        # 2*x + y + 3 -> {x: 2, y: 1, None: 3}
        cdict = defaultdict(int)
        for arg in args:
            if isinstance(arg, CVar):
                cdict[arg] += 1
            elif isinstance(arg, CTerm):
                cdict[arg.var] += arg.coeff
            elif isinstance(arg, CAdd):
                for oarg in arg.args:
                    # Every arg of CAdd should be a CTerm or a number
                    if isinstance(oarg, CTerm):
                        coeff, var = oarg.args
                        cdict[var] += coeff
                    elif isinstance(oarg, numbers):
                        cdict[None] += oarg
            elif isinstance(arg, numbers):
                cdict[None] += arg
            else:
                raise TypeError("Don't know how to handle %s in CAdd" % arg)

        newargs = []
        for var in sorted([i for i in cdict if i is not None], key=str):
            coeff = cdict[var]
            newargs.append(CTerm(coeff, var))
        if None in cdict:
            newargs.append(cdict[None])

        if len(newargs) == 1:
            return newargs[0]

        obj = super(CAdd, cls).__new__(cls, *newargs)
        obj.cdict = cdict
        return obj

    def __mul__(self, other):
        # TODO: Add type checking here that other is a number
        return CAdd(*[other*arg for arg in self.args])

    __rmul__ = __mul__

    def __repr__(self):
        return ' + '.join(['%s*%s' % cterm.args if isinstance(cterm, CTerm) else
            str(cterm) for cterm in self.args])

class CVar(CExpr):
    def __init__(self, name):
        self.name = name
        self.args = (name,)

    def __repr__(self):
        return self.name

    def __mul__(self, other):
        # TODO: Add type checking here that other is a number
        return CTerm(other, self)

    __rmul__ = __mul__

class CTerm(CExpr):
    def __init__(self, coeff, var):
        self.var = var
        self.coeff = coeff
        self.args = (coeff, var)

    def __mul__(self, other):
        # TODO: Add type checking here that other is a number
        return CTerm(self.coeff*other, self.var)

    __rmul__ = __mul__

    def __repr__(self):
        return '%s*%s' % (self.coeff, self.var)
