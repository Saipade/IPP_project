import xml.etree.ElementTree as ET

from errorslist import *


class Argument:
    '''
    Class representing both instruction argument and variables in any of memory frames
    '''
    type = None                                # xml type, will be changed to data type for variables
    suffix = None                              # text before @
    value = None                               # text after @ if constant or value of variable if variable
    id = None                                  # text after @ if variable

class Label(Argument):
    '''
    Subclass representing labels 
    '''
    def __init__(self, xmlArgument):
        if xmlArgument is None:
            exit(ERR_STRUCT)
        self.type = xmlArgument.attrib['type']
        if self.type != 'label':
            exit(ERR_TYPES)
        self.value = xmlArgument.text

    def __str__(self):
        return f'{self.value}'

class Symbol(Argument):
    '''
    Subclass representing symbol (can be either constantor variable)
    '''
    def __init__(self, xmlArgument):
        if xmlArgument is None:
            exit(ERR_STRUCT)
        self.type = xmlArgument.attrib['type']
        if self.type == 'var': # variable
            self.suffix, self.id = xmlArgument.text.split('@')
            self.value = None
        elif self.type == 'string':
            self.suffix, self.value = self.type, xmlArgument.text
        elif self.type == 'int':
            self.suffix, self.value = self.type, int(xmlArgument.text)
        elif self.type == 'nil':
            self.suffix, self.value = self.type, xmlArgument.text
        elif self.type == 'bool':
            self.suffix = self.type
            if xmlArgument.text == 'true': self.value = True
            if xmlArgument.text == 'false': self.value = False
        else: 
            exit(ERR_TYPES)

    def set(self, attrDict):
        for key in attrDict:
            setattr(self, key, attrDict[key])

    def getData(self, *retvalsSTR):
        retvals = [getattr(self, attr) for attr in retvalsSTR]
        return retvals

    def __str__(self):
        return f'{self.suffix}@{self.id}:{self.type}@{self.value}'

class Variable(Argument):
    '''
    Subclass representing variable
    '''
    def __init__(self, xmlArgument):
        if xmlArgument is None:
            exit(ERR_STRUCT)
        self.type = xmlArgument.attrib['type']
        if self.type != 'var':
            exit(ERR_TYPES)
        self.suffix, self.id = xmlArgument.text.split('@')
        self.value = None

    def set(self, attrDict):
        for key in attrDict:
            setattr(self, key, attrDict[key])

    def getData(self, *retvalsSTR):
        retvals = [getattr(self, attr) for attr in retvalsSTR]
        return retvals

    def __str__(self):
        return f'{self.suffix}@{self.id}:{self.type}@{self.value}'

class Type(Argument):
    '''
    Subclass representing 'type' type of constants
    '''
    def __init__(self, xmlArgument):
        if xmlArgument is None:
            exit(ERR_STRUCT)
        self.type = xmlArgument.attrib['type']
        if self.type != 'type':
            exit(ERR_TYPES)
        self.value = xmlArgument.text

    def __str__(self):
        return f'{self.value}'