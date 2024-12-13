import string
import sys
import random
import argparse

H = False
O = False
R = {
    'True': '(()==())',
    'False': '(()==[])',
}
V = "__RSV"
B = "__B"
E = [
    'None', 'and', 'as', 'assert', 'break', 'class', 'continue',
    'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
    'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not',
    'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
]
I = [
    'abs', 'dict', 'help', 'min', 'setattr', 'all', 'dir', 'hex', 'next', 'slice',
    'any', 'divmod', 'id', 'object', 'sorted', 'ascii', 'enumerate', 'input', 'oct', 
    'staticmethod', 'bin', 'eval', 'int', 'open', 'str', 'bool', 'exec', 'isinstance',
    'ord', 'sum', 'bytearray', 'filter', 'issubclass', 'pow', 'super', 'bytes', 
    'float', 'iter', 'print', 'tuple', 'callable', 'format', 'len', 'property', 'type',
    'chr', 'frozenset', 'list', 'range', 'vars', 'classmethod', 'getattr', 'locals', 
    'repr', 'zip', 'compile', 'globals', 'map', 'reversed', '__import__', 'complex', 
    'hasattr', 'max', 'round', 'delattr', 'hash', 'memoryview', 'set'
]
P = [';', ':', '=', '+', '-', '*', '%', '^', '<<', '>>', '|', '^', '/', ',', '{', '}', '[', ']']

class A:
    def __init__(self):
        self.H = {}
        self.V = {}

    def H_V(self):
        return ";".join("{}={}".format(self.H[k], self.V[self.H[k]]) for k in sorted(self.H, key=lambda x: len(self.H[x]))) + "\n"

    def A_V(self, k, v):
        if k in self.H:
            return self.H[k]
        if len(v) < (len(self.V) + 1) + 2:
            return v
        n = '_' * (len(self.V) + 1)
        self.V[n] = v
        self.H[k] = n
        return n

    def N(self, n, a=False):
        if int(n) < 0:
            return "(~([]==())*{})".format(self.N(abs(int(n))))
        n = str(n)
        if n in self.H:
            return self.V[self.H[n]]
        if n == '0':
            return '((()==[])+(()==[]))'
        elif n == '1':
            return '((()==())+(()==[]))'
        else:
            if ('0' not in self.H):
                self.A_V('0', '((()==[])+(()==[]))')
                self.A_V('1', '({0}**{0})'.format(self.H['0']))
            b = bin(int(n))[2:]
            s = 0
            o = ''
            while b != '':
                if b[-1] == '1':
                    if s == 0:
                        o += self.N(1)
                    elif str(1 << s) in self.H:
                        o += self.H[str(1 << s)]
                    elif str(s) in self.H:
                        o += '({}<<{})'.format(self.H['1'], self.H[str(s)])
                    else:
                        bm = self.N(str(1 << (s - 1)), True)
                        o += '({}<<{})'.format(bm, self.N('1'))
                    o += '+'
                b = b[:-1]
                s += 1
            o = "({})".format(o[:-1]) if b.count('1') != 1 else o[:-1]
            return self.A_V(n, o) if a else o

    def S(self, s, a=False, f=False):
        if H or f:
            r = "'{}'".format("".join("\\x{:02x}".format(ord(c)) for c in s))
        else:
            b = "[{}]".format(",".join([self.N(ord(c)) for c in s]))
            r = "str(''.join(chr({0}) for {0} in {1}))".format(V, b)
        return self.A_V(s, r) if a else r

    def C(self, c, a=True):
        if c.split()[0] in ['import', 'from']:
            return c
        p = c
        for i in P:
            p = p.replace(i, " {} ".format(i))
        p = p.replace('(', "( ").replace(')', ' )')
        r = ''
        q = ''
        l = False
        for s in p.split():
            if s[0] == '#':
                if R:
                    return
                l = True
            if l:
                r += s + ' '
                continue
            if (q == '') and (s[0] in ["\"", "\'"]):
                q = s + ' '
                continue
            if q != '':
                if (s.find(q[0]) != -1):
                    q += s[:s.find(q[0]) + 1]
                    r += self.S(q[1:-1])
                    q = ''
                else:
                    q += s + ' '
                continue
            if s in E:
                r += " {} ".format(s)
                continue
            if s in P:
                r += s
                continue
            if s in R:
                r += R[s]
                continue
            if s.isdigit():
                r += self.N(int(s))
                continue
            n = ""
            for ch in s:
                if ch in string.ascii_letters + '_':
                    n += ch
                elif n:
                    if n[0] in string.digits:
                        n = ""
            if n in I:
                if O:
                    if B not in self.H:
                        self.A_V(B, self.S('builtins'))
                    e = self.A_V(n, self.S(n))
                    r += "getattr(__import__({}), {})".format(self.H[B], e)
                    r += s[len(n):]
                else:
                    r += s
                continue
            if (n != "") and (n not in E) and (n not in I):
                if n not in self.V:
                    self.V[n] = '_' * (len(self.V) + 1)
                r += self.V[n] + s[len(n):]
                continue
            r += s
        i = ""
        j = 0
        while c[j] in ['\t', ' ']:
            i += c[j]
            j += 1
        r = i + r.strip()
        return self.H_V() + r if a and (len(self.H) > 0) else r

    def L(self, c):
        s = -1
        x = []
        for i, ch in enumerate(c):
            if (ch in ['\'', '\"']) and (c[i - 1] != '\\'):
                if s == -1:
                    s = i
                elif ch == c[s]:
                    x.append(c[s: i + 1])
                    s = -1
        v = {}
        for s in x:
            v[s] = self.A_V(s, self.S(s[1:-1]))
        for s in v:
            c = c.replace(s, v[s])
        r = ""
        for l in c.split('\n'):
            if not l:
                continue
            r += self.C(l, False) + "\n"
        return self.H_V() + r

def M():
    i = input("اسم الملف المراد تشفيره: ")
    o = input("اسم الملف لحفظ الكود المشفر (مع الامتداد .py): ")
    if not o.endswith('.py'):
        o += '.py'
    with open(i, 'r') as f:
        l = f.read()
    ob = A()
    r = ob.L(l)
    with open(o, 'w') as f:
        f.write(r)
    print(f"تم حفظ الكود المشفر في الملف: {o}")

if __name__ == "__main__":
    M()
