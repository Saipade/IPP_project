import enum
import xml.etree.ElementTree as ET

from sets import instructionSet
from argument import *
from errorslist import *
import importlib

class Instruction:

    def __init__(self, xmlInstruction):
        '''
        Initializes instruction depending on given xml representation
        '''
        factory = Factory()
        try:
            self.order = int(xmlInstruction.attrib['order'])                # order
            self.opCode = xmlInstruction.attrib['opcode'].upper()           # opcode
        except:
            exit(ERR_STRUCT)
        # number of arguments, opcode, and xml element tag checks
        if self.opCode not in instructionSet or \
        len(instructionSet[self.opCode]) != len(list(xmlInstruction)) or \
        xmlInstruction.tag != 'instruction':
            exit(ERR_STRUCT)
        # sort xml arguments
        xmlInstruction[:] = sorted(xmlInstruction, key=lambda child: child.tag)   
        # dynamically instantiate arguments
        self.args = factory.createArguments(xmlInstruction, self.opCode) # arguments
            
    def __str__(self):
        return f'{self.order}: {self.opCode} {self.args[0]} {self.args[1]} {self.args[2]}'


class Factory:
    '''
    Abstract factory
    '''
    _instance = None

    def __new__(self):
        '''
        Initiates Stats class object (is a singleton)
        '''
        if not self._instance:
            self._instance = super(Factory, self).__new__(self)
        return self._instance

    def createInstruction(self, xmlInstruction):
        return Instruction(xmlInstruction)

    def createArguments(self, xmlInstruction, opCode):
        argument = importlib.import_module('argument')
        args = [None] * 3                              # list of Argument class objects
        for i, arg in enumerate(xmlInstruction):
            if arg.tag != f'arg{i+1}' or i > 2:
                exit(ERR_STRUCT)
            args[i] = getattr(argument, instructionSet[opCode][i])(xmlInstruction.find(f'arg{i+1}'))
        return args