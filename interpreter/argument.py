import xml.etree.ElementTree as ET

from errorslist import *

class Argument: 

    def __init__(self, xmlArgument):
        '''

        '''
        self.type = None                                # xml type, will be changed to data type for variables
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

class Label(Argument):

    def __str__(self):
        return f'{self.value}'

class Symbol(Argument):

    def set(self, attrDict):
        for key in attrDict:
            setattr(self, key, attrDict[key])

    def getData(self, *retvalsSTR):
        retvals = [getattr(self, attr) for attr in retvalsSTR]
        return retvals

    def __str__(self):
        return f'{self.type}:{self.suffix}{self.id}:{self.value}'

class Variable(Argument):

    def set(self, attrDict):
        for key in attrDict:
            setattr(self, key, attrDict[key])

    def getData(self, *retvalsSTR):
        retvals = [getattr(self, attr) for attr in retvalsSTR]
        return retvals

    def __str__(self):
        return f'{self.type}:{self.suffix}{self.id}:{self.value}'

class Type(Argument):

    def __str__(self):
        return f'{self.value}'