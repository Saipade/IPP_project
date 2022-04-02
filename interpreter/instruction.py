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
        argument = importlib.import_module('argument')
        self.order = 0                                      # order
        self.opCode = ""                                    # operation code
        self.args = [None] * 3                              # list of Argument class objects
        
        try:
            self.order = int(xmlInstruction.attrib['order'])
            self.opCode = xmlInstruction.attrib['opcode'].upper()
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
        for i, arg in enumerate(xmlInstruction):
            if arg.tag != f'arg{i+1}' or i > 2:
                exit(ERR_STRUCT)
            self.args[i] = getattr(argument, instructionSet[self.opCode][i])(xmlInstruction.find(f'arg{i+1}'))
            

    def __str__(self):
        return f'{self.order}: {self.opCode} {self.args[0]} {self.args[1]} {self.args[2]}'