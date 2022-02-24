import xml.etree.ElementTree as ET

from sets import instructionSet
from argument import Argument
from errorslist import *

class Instruction: 

    def __init__(self, xmlInstruction):
        '''
        Initializes instruction depending on given xml representation
        '''
        self.order = 0
        self.opCode = ""
        self.args = [None] * 3
        
        if xmlInstruction.tag != 'instruction':
            exit(ERR_STRUCT)
        self.order = int(xmlInstruction.attrib['order']) if int(xmlInstruction.attrib['order']) > 0 else exit(ERR_STRUCT)
        self.opCode = xmlInstruction.attrib['opcode'] if xmlInstruction.attrib['opcode'].upper() in instructionSet else exit(ERR_STRUCT)
        for i, arg in enumerate(xmlInstruction):
            if arg.tag != f'arg{i+1}' or i > 2:
                exit(ERR_STRUCT)
            self.args[i] = Argument(xmlInstruction.find(f'arg{i+1}'))

    def getOpCodeNOrder(self):
        return self.opCode, self.order
        