import xml.etree.ElementTree as ET

from sets import instructionSet
from argument import Argument
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
        
        if xmlInstruction.tag != 'instruction':
            exit(ERR_STRUCT)
        self.order = int(xmlInstruction.attrib['order']) if int(xmlInstruction.attrib['order']) > 0 else exit(ERR_STRUCT)
        self.opCode = xmlInstruction.attrib['opcode'].upper() if xmlInstruction.attrib['opcode'].upper() in instructionSet else exit(ERR_STRUCT)
        for i, arg in enumerate(xmlInstruction):
            if arg.tag != f'arg{i+1}' or i > 2:
                exit(ERR_STRUCT)
            # dynamic argument instantiation
            self.args[i] = getattr(argument, instructionSet[self.opCode][i])(xmlInstruction.find(f'arg{i+1}'))