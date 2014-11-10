__author__ = "Dusan (Ph4r05) Klinec"
__copyright__ = "Copyright (C) 2014 Dusan (ph4r05) Klinec"
__license__ = "Apache License, Version 2.0"
__version__ = "1.0"

class Visitor(object):

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __getattr__(self, name):
        if not name.startswith('visit_'):
            raise AttributeError('name must start with visit_ but was {}'.format(name))

        def f(element):
            if self.verbose:
                msg = 'unimplemented call to {}; ignoring ({})'
                print(msg.format(name, element))
            return True
        return f

    # visitor.visit_PackageStatement(self)
    # visitor.visit_ImportStatement(self)
    # visitor.visit_OptionStatement(self)
    # visitor.visit_FieldDirective(self)
    # visitor.visit_FieldType(self)
    # visitor.visit_FieldDefinition(self)
    # visitor.visit_EnumFieldDefinition(self)
    # visitor.visit_EnumDefinition(self)
    # visitor.visit_MessageDefinition(self)
    # visitor.visit_MessageExtension(self)
    # visitor.visit_MethodDefinition(self)
    # visitor.visit_ServiceDefinition(self)
    # visitor.visit_ExtensionsDirective(self)
    # visitor.visit_Literal(self)
    # visitor.visit_Name(self)
    # visitor.visit_Proto(self)

# Lexical unit - contains lexspan and linespan for later analysis.
class LU(object):
    def __init__(self, p, idx):
        self.p = p
        self.idx = idx
        self.pval = p[idx]
        self.lexspan = p.lexspan(idx)
        self.linespan = p.linespan(idx)

        # If string is in the value (raw value) and start and stop lexspan is the same, add real span
        # obtained by string length.
        if isinstance(self.pval, str) \
                and self.lexspan != None \
                and self.lexspan[0] == self.lexspan[1] \
                and self.lexspan[0] != 0:
            self.lexspan = tuple([self.lexspan[0], self.lexspan[0] + len(self.pval)])
        super(LU, self).__init__()

    @staticmethod
    def i(p, idx):
        if isinstance(p[idx], LU): return p[idx]
        if isinstance(p[idx], str): return LU(p, idx)
        return p[idx]

    def describe(self):
        return "LU(%s,%s)" % (self.pval,  self.lexspan)

    def __str__(self):
        return self.pval

    def __repr__(self):
        return self.describe()

    def accept(self, visitor):
        pass

    def __iter__(self):
        for x in self.pval:
            yield x

# Base node
class SourceElement(object):
    '''
    A SourceElement is the base class for all elements that occur in a Protocol Buffers
    file parsed by plyproto.
    '''
    def __init__(self, linespan=[], lexspan=[], p=None):
        super(SourceElement, self).__init__()
        self._fields = [] # ['linespan', 'lexspan']
        self.linespan = linespan
        self.lexspan = lexspan
        self.p = p

    def __repr__(self):
        equals = ("{0}={1!r}".format(k, getattr(self, k))
                  for k in self._fields)
        args = ", ".join(equals)
        return "{0}({1})".format(self.__class__.__name__, args)

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def setLexData(self, linespan, lexspan):
        self.linespan = linespan
        self.lexspan = lexspan

    def setLexObj(self, p):
        self.p = p

    def accept(self, visitor):
        pass

class PackageStatement(SourceElement):
    def __init__(self, name, linespan=None, lexspan=None, p=None):
        super(PackageStatement, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name']
        self.name = name

    def accept(self, visitor):
        visitor.visit_PackageStatement(self)

class ImportStatement(SourceElement):
    def __init__(self, name, linespan=None, lexspan=None, p=None):
        super(ImportStatement, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name']
        self.name = name

    def accept(self, visitor):
        visitor.visit_ImportStatement(self)

class OptionStatement(SourceElement):
    def __init__(self, name, value, linespan=None, lexspan=None, p=None):
        super(OptionStatement, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'value']
        self.name = name
        self.value = value

    def accept(self, visitor):
        visitor.visit_OptionStatement(self)

class FieldDirective(SourceElement):
    def __init__(self, name, value, linespan=None, lexspan=None, p=None):
        super(FieldDirective, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'value']
        self.name = name
        self.value = value

    def accept(self, visitor):
        visitor.visit_FieldDirective(self)

class FieldType(SourceElement):
    def __init__(self, name, linespan=None, lexspan=None, p=None):
        super(FieldType, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name']
        self.name = name

    def accept(self, visitor):
        visitor.visit_FieldType(self)

class FieldDefinition(SourceElement):
    def __init__(self, field_modifier, ftype, name, fieldId, fieldDirective, linespan=None, lexspan=None, p=None):
        super(FieldDefinition, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['field_modifier', 'ftype', 'name', 'fieldId', 'fieldDirective']
        self.name = name
        self.field_modifier = field_modifier
        self.ftype = ftype
        self.fieldId = fieldId
        self.fieldDirective = fieldDirective

    def accept(self, visitor):
        visitor.visit_FieldDefinition(self)

class EnumFieldDefinition(SourceElement):
    def __init__(self, name, fieldId, linespan=None, lexspan=None, p=None):
        super(EnumFieldDefinition, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'fieldId']
        self.name = name
        self.fieldId = fieldId

    def accept(self, visitor):
        visitor.visit_EnumFieldDefinition(self)

class EnumDefinition(SourceElement):
    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(EnumDefinition, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_EnumDefinition(self):
            for s in self.body:
                s.accept(visitor)

class MessageDefinition(SourceElement):
    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(MessageDefinition, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_MessageDefinition(self):
            for s in self.body:
                s.accept(visitor)

class MessageExtension(SourceElement):
    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(MessageExtension, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_MessageExtension(self):
            for s in self.body:
                s.accept(visitor)

class MethodDefinition(SourceElement):
    def __init__(self, name, name2, name3, linespan=None, lexspan=None, p=None):
        super(MethodDefinition, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'name2', 'name3']
        self.name = name
        self.name2 = name2
        self.name3 = name3

    def accept(self, visitor):
        visitor.visit_MethodDefinition(self)

class ServiceDefinition(SourceElement):
    def __init__(self, name, body, linespan=None, lexspan=None, p=None):
        super(ServiceDefinition, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['name', 'body']
        self.name = name
        self.body = body

    def accept(self, visitor):
        if visitor.visit_ServiceDefinition(self):
            for s in self.body:
                s.accept(visitor)

class ExtensionsMax(SourceElement):
    pass

class ExtensionsDirective(SourceElement):
    def __init__(self, fromVal, toVal, linespan=None, lexspan=None, p=None):
        super(ExtensionsDirective, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['fromVal', 'toVal']
        self.fromVal = fromVal
        self.toVal = toVal

    def accept(self, visitor):
        visitor.visit_ExtensionsDirective(self)

class Literal(SourceElement):

    def __init__(self, value, linespan=None, lexspan=None, p=None):
        super(Literal, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['value']
        self.value = value

    def accept(self, visitor):
        visitor.visit_Literal(self)

class Name(SourceElement):

    def __init__(self, value, linespan=None, lexspan=None, p=None):
        super(Name, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['value']
        self.value = value
        self.deriveLex()

    def append_name(self, name):
        try:
            self.value = self.value + '.' + name.value
        except:
            self.value = self.value + '.' + name

    def deriveLex(self):
        if hasattr(self.value, "lexspan"):
            self.lexspan = self.value.lexspan
            self.linespan = self.value.linespan
        else:
            return

    def accept(self, visitor):
        visitor.visit_Name(self)

class DotName(Name):
    elements = []
    def __init__(self, elements, linespan=None, lexspan=None, p=None):
        super(DotName, self).__init__('.'.join([str(x) for x in elements]), linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['elements']
        self.elements = elements
        self.deriveLex()

    def deriveLex(self):
        if isinstance(self.elements, list) and len(self.elements)>0:
            self.lexspan = (min([x.lexspan[0] for x in self.elements if x.lexspan[0] != 0]), max([x.lexspan[1] for x in self.elements if x.lexspan[1] != 0]))
            self.linespan = (min([x.linespan[0] for x in self.elements if x.linespan[0] != 0]), max([x.linespan[1] for x in self.elements if x.linespan[1] != 0]))
        elif hasattr(self.elements, "lexspan"):
            self.lexspan = self.elements.lexspan
            self.linespan = self.elements.linespan
        else:
            return

    def accept(self, visitor):
        visitor.visit_DotName(self)

class ProtoFile(SourceElement):

    def __init__(self, pkg, body, linespan=None, lexspan=None, p=None):
        super(ProtoFile, self).__init__(linespan=linespan, lexspan=lexspan, p=p)
        self._fields += ['pkg', 'body']
        self.pkg = pkg
        self.body = body

    def accept(self, visitor):
        if visitor.visit_Proto(self):
            for s in self.body:
                s.accept(visitor)
