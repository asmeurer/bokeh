from collections import defaultdict

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
        # 2*x + y -> {x: 2, y: 1}
        cdict = defaultdict(int)
        for arg in args:
            if isinstance(arg, CVar):
                cdict[arg] += 1
            elif isinstance(arg, CTerm):
                cdict[arg.var] += arg.coeff
            elif isinstance(arg, CAdd):
                for oarg in arg.args:
                    coeff, var = oarg.args
                    cdict[var] += coeff
            else:
                raise TypeError("Don't know how to handle %s in CAdd" % arg)

        newargs = []
        for var in sorted(cdict, key=lambda v: v.name):
            coeff = cdict[var]
            newargs.append(CTerm(coeff, var))

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
        return ' + '.join(['%s*%s' % cterm.args for cterm in self.args])

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
