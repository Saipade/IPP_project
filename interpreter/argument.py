import xml.etree.ElementTree as ET

from errorslist import *

class Argument: 

    def __init__(self, xmlArgument):
        '''

        '''
        self.type = None                                # xml type
        self.suffix = None                              # text before @
        self.value = None                               # text after @ if constant or value of variable if variable
        self.id = None                                  # text after @ if variable
        
        if xmlArgument is None:
            exit(ERR_SEMAN)
        self.type = xmlArgument.attrib['type']
        if self.type == 'var': # variable
            self.suffix, self.id = str.split(xmlArgument.text, "@")
        elif self.type == 'type' or self.type == 'label': # type or label
            self.value = xmlArgument.text
        else: # constant
            self.suffix, self.value = self.type, xmlArgument.text

    def __str__(self):
        return f'{"" if self.suffix is None else self.suffix}{"" if self.value is None else self.value}'

class Label(Argument):

    def __str__(self):
        return f'{"" if self.value is None else self.value}'

class Symbol(Argument):

    def set(self, type=None, value=None):
        if self.type == 'var':
            self.type = type if type is not None else self.type
            self.value = value if value is not None else self.value
        else:
            exit(ERR_TYPES)

    def getData(self, var=True):
        if var == True: # return frame@id
            return self.suffix, self.id
        else:           # return type@value
            return self.suffix, self.value

    def __str__(self):
        return f'{"" if self.suffix is None else self.suffix}{"" if self.value is None else self.value}'

class Variable(Argument):
    
    def set(self, type=None, value=None):
        self.type = type if type is not None else self.type
        self.value = value if value is not None else self.value

    def getData(self, var=True):
        if var == True: # return frame@id
            return self.suffix, self.id
        else:           # return type@value
            return self.suffix, self.value

    def __str__(self):
        return f'{self.suffix}{self.id}'

class Type(Argument):

    def __init__(self, xmlArgument):
        self.type = None                                # xml type
        self.suffix = None                              # text before @
        self.value = None                               # text after @ if constant or value of variable if variable
        self.id = None                                  # text after @ if variable
        
        if xmlArgument is None:
            exit(ERR_SEMAN)
        self.type = xmlArgument.attrib['type']
        if self.type != 'type':
            exit(ERR_SEMAN)
        self.id = xmlArgument.text

    def __str__(self):
        return f'{self.value}'