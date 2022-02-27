from sre_constants import NOT_LITERAL
import xml.etree.ElementTree as ET
import getopt
import sys
from pathlib import Path
import re
from xml.sax.saxutils import XMLFilterBase

from instruction import Instruction
from sets import *
from errorslist import *
from stats import Stats
    
class Interpreter:

    def __init__(self):
        self.xmlTree = None                             # XML tree of input XML code representation
        self.inputText = None                           # text with input for source code interpretation

        self.stats = Stats()                            # Stats class attribute

        self.instructionList = []                       # list of instructions

        self.GFrame = {}                                # dictionary of global frame variables of shape <varID> -> Argument class object
        self.LFrame = {}                                # dictionary on top of framesStack of shape <varID> -> Argument class object
        self.TFrame = None                              # dictionary of temporary frame variables of shape <varID> -> Argument class object
        self.framesStack = []                           # list of local frames

        self.labelList = {}                             # dictionary of labels <labelName> -> line
        self.callStack = []                             # list of line numbers for return instructions 

        self.currentInstruction = None                  # Instruction class object
        self.currentLine = 0                            # current line of input code
        self.dataStack = []                             # list of shape [[type, value], [type, value], ..]
    
    def parseArguments(self):
        ''' 
        Parses command line arguments, finds source and input files, fills statsGroups dictionary
        ''' 
        try:
            opts, _ = getopt.getopt(sys.argv[1:], '', ['help', 'source=', 'input=', 'stats=', 'insts', 'hot', 'vars'])
        except getopt.GetoptError as err:
            print(err)
            exit(ERR_PARAM)
        statsGroups, tmpList, sIsPresent, iIsPresent, stIsPresent, xmlFile, inputFile, statsFile = {}, list(), 0, 0, 0, None, None, None
        for opt, arg in opts:
            if opt in ('--help'):
                if len(sys.argv) != 2:
                    exit(ERR_PARAM)
                print(help)
                exit(INTER_OK)
            elif opt in ('--source'):
                if sIsPresent == 1:
                    exit(ERR_PARAM)
                sIsPresent = 1
                xmlFile = arg
            elif opt in ('--input'):
                if iIsPresent == 1:
                    exit(ERR_PARAM)
                iIsPresent = 1
                inputFile = arg
            elif opt in ('--stats'):
                if stIsPresent > 0:
                    self.stats.statsGroups[statsFile] = tmpList
                else:
                    stIsPresent = 1
                tmpList = list()
                statsFile = arg
            elif opt in ('--insts', '--hot', '--vars') and stIsPresent > 0:
                tmpList.append(opt[2:])
            else:
                exit(ERR_PARAM)
            self.stats.statsGroups[statsFile] = tmpList
        # no input and no source => error
        if sIsPresent == 0 and iIsPresent == 0:
            exit(ERR_PARAM)
            
        self.__readFiles(xmlFile, inputFile)

    def __readFiles(self, xmlFile, inputFile):
        '''
        Reads given files into 2 corresponding interpreter attributes
        '''
        # xmlTree -- root XMLElement, 
        self.xmlTree = ET.parse(sys.stdin).getroot() if xmlFile is None else ET.parse(xmlFile).getroot()
        if self.xmlTree.tag != 'program':
            exit(ERR_FORMAT)
        # sort instructions by order
        self.xmlTree[:] = sorted(self.xmlTree, key=lambda child: int(re.search('\d+', child.get('order')).group()))
        # inputText -- list<string>
        self.inputText = sys.stdin.readlines() if inputFile is None else Path(inputFile).read_text().split('\n')
        
    def constructInstructionList(self):
        for _, xmlInstruction in enumerate(self.xmlTree):
            self.instructionList.append(Instruction(xmlInstruction))
        for instruction in self.instructionList:
            print(f'order: {instruction.order}, {instruction.opCode} {instruction.args[0]} {instruction.args[1]} {instruction.args[2]} ')

    def executeProgram(self):
        '''
        Iterates through input code 2 times,
        first -- finds all labels,
        second -- executes instructions from instruction list
        '''
        while True: # find all labels
            self.currentInstruction = self.instructionList[self.currentLine]
            if self.currentInstruction.opCode == "LABEL":
                self.execL483L()
            self.currentLine += 1
            if (self.currentLine == len(self.instructionList)):
                break
            
        self.currentLine = 0
        print(self.labelList)
        while True: # execute __exec*X*()
            self.currentInstruction = self.instructionList[self.currentLine]
            print(self.currentInstruction.order, self.currentInstruction.opCode)
            getattr(self, 'exec'+self.currentInstruction.opCode)()
            self.stats.updateInsts(self.currentInstruction)
            self.stats.updateHot(self.currentInstruction)
            self.currentLine += 1
            if (self.currentLine == len(self.instructionList)):
                break

    def __getValues(self, stack=False):
        '''
        Returns variables' values (if there are variables in expression), checks type compatibility
        '''
        if stack is True:
            opType1, opVal1 = self.dataStack.pop()
            opType2, opVal2 = self.dataStack.pop()
        else:
            opType1, opVal1, opType2, opVal2 = \
            self.currentInstruction.args[1].getData('suffix', 'id'), self.currentInstruction.args[2].getData('suffix', 'id')
        if opType1 in ('GF', 'LF', 'TF'):
            opType1, opVal1 = self.__findInFrame(opType1, opVal1)
        else:
            opType1, opVal1 = self.currentInstruction.args[1].getData('suffix', 'value')
        if opType2 in ('GF', 'LF', 'TF'):
            opType2, opVal2 = self.__findInFrame(opType2, opVal2)
        else:
            opType2, opVal2 = self.currentInstruction.args[2].getData('suffix', 'value')
        if opType1 != opType2 and opVal1 != 'nil' and opVal2 != 'nil':
            exit(ERR_TYPES)
        return opVal1, opVal2, opType1

    def __evalExpr(self, lexp, op, stack=False):
        '''
        Evaluates given expression
        '''
        operand1, operand2, type = self.__getValues(stack)
        
        if operand1 in ('true', 'false'): operand1 = operand1.capitalize()
        if operand2 in ('true', 'false'): operand2 = operand2.capitalize()
        if operand1 == 'nil' or operand2 == 'nil':
            if op not in ('==', '!='):
                exit(ERR_TYPES)
            if operand1 == 'nil': operand1 = None
            if operand2 == 'nil': operand2 = None

        retval = lexp(operand1, operand2)
        if stack is True: self.dataStack.append(type, retval)
        else: return retval

    def __str2bool(self, str1, str2):
        for str in [str1, str2]:
            if str == 'true': str = True
            else: str = False
        return str1, str2

    def __findInFrame(self, frame, id):
        try:
            type, value = getattr(self, frame+'rame')[id].getData('suffix', 'value')
        except KeyError:
            exit(ERR_UNDECLVAR)
        return type, value

    '''
    Instruction list
    '''
    def execCREATEFRAME(self):
        self.TFrame = {}

    def execPUSHFRAME(self):
        if self.TFrame is None:
            exit(ERR_NOFRAME)
        self.framesStack.append(self.TFrame)
        self.LFrame = self.TFrame
        self.TFrame = None

    def execPOPFRAME(self):
        if (len(self.framesStack) == 0):
            exit(ERR_NOFRAME)
        self.TFrame = self.framesStack.pop()
        self.stats.updateVars(len(self.GFrame)+len(self.TFrame)+len(self.LFrame)-self.stats.currentVars)
    
    def execRETURN(self):
        if len(self.callStack) == 0:
            exit(ERR_UNDEFVAR)
        self.currentLine = self.callStack.pop()

    def execBREAK(self):
        print(f'Current position: {self.currentLine}\nGlobal frame: {self.GFrame}\nLocal frame: {self.LFrame}\n' \
            f'Temporary frame: {self.TFrame}\nInstruction counter: {self.stats.insts}', file=sys.stderr)

    def execCLEARS(self):
        self.dataStack = []

    def execCALL(self):
        try:
            self.currentLine = self.labelList[self.currentInstruction.args[0].value]
            self.callStack.append(self.currentLine+1)
            self.stats.updateVars(len(self.GFrame)+len(self.TFrame)-self.stats.currentVars)
        except KeyError: # label does not exist
            exit(ERR_SEMAN)

    def execLABEL(self):
        '''
        All labels were detected before the code execution. See next method
        '''
        pass
    
    def execL483L(self):
        if self.currentInstruction.args[0].value in self.labelList:
            exit(ERR_SEMAN)
        self.labelList[self.currentInstruction.args[0].value] = self.currentLine

    def execJUMP(self):
        try:
            self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)

    def execJUMPIFEQS(self):
        try:
            if self.__evalExpr(lambda a, b: a == b, '==', stack=True) == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)
            
    def execJUMPIFNEQS(self):
        try:
            if self.__evalExpr(lambda a, b: a != b, '!=', stack=True) == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)
            
    def execJUMPIFEQ(self):
        try:
            if self.__evalExpr(lambda a, b: a == b, '==',) == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)

    def execJUMPIFNEQ(self):
        try:
            if self.__evalExpr(lambda a, b: a != b, '!=',) == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)
            
    def execDEFVAR(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = getattr(self, frame+'rame')
        if id in frame: # attempt of variable redefinition
            exit(ERR_SEMAN)
        frame[id] = self.currentInstruction.args[0]

    def execPOPS(self):
        if len(self.callStack) == 0:
            exit(ERR_UNDEFVAR)
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        if frame != 'GF' and frame != 'LF' and frame != 'TF':
            exit(ERR_SEMAN)
        type, value = self.dataStack.pop()
        frame = getattr(self, (frame+'rame'))[id].set({'suffix' : type, 'value' : value})

    def execPUSHS(self):
        if self.currentInstruction.args[0].value is None:
            exit(ERR_UNDEFVAR)
        type, value = self.currentInstruction.args[0].getData('type', 'value')
        if type == 'var': 
            exit(ERR_UNDEFVAR)
        self.dataStack.append((type, value))

    def execWRITE(self):
        value, toPrint = self.currentInstruction.args[0].getData('value'), None
        if value == 'nil': toPrint = ''
        else: toPrint = value
        print(toPrint, end='')

    def execEXIT(self):
        _type, value = self.currentInstruction.args[0].getData('suffix', 'value')
        if _type != 'int' or int(value) > 49 or int(value) < 0:
            exit(ERR_VALUE)
        self.stats.writeStats()
        exit(int(value))
        
    def execDPRINT(self):
        toPrint = self.currentInstruction.args[0].getData('value')
        if toPrint == 'nil':
            toPrint = ''
        print(toPrint, end='', file=sys.stderr)

    def execNOTS(self):
        type, value = self.dataStack.pop()
        if type != 'bool' or value not in ('true', 'false'):
            exit(ERR_TYPES)
        value, _ = self.__str2bool(value, _)
        self.dataStack.append(type, value)
        
    def execINT2CHARS(self):
        type, value = self.dataStack.pop()
        if type != 'int': exit(ERR_TYPES)
        if 0 <= (int(value)) <= 256: exit(ERR_STRING)
        self.dataStack.append('string', chr(int(value)))

    def execSTRI2INTS(self):
        type, value = self.dataStack.pop()

    def execADDS(self):
        self.__evalExpr(lambda a, b : a + b, '+', stack=True)

    def execSUBS(self):
        self.__evalExpr(lambda a, b : a - b, '-', stack=True)

    def execMULS(self):
        self.__evalExpr(lambda a, b : a * b, '*', stack=True)

    def execDIVS(self):
        self.__evalExpr(lambda a, b : a / b, '/', stack=True)
        
    def execIDIVS(self):
        self.__evalExpr(lambda a, b : a // b, '//', stack=True)
        
    def execLTS(self):
        self.__evalExpr(lambda a, b : a < b, '<', stack=True)

    def execGTS(self):
        self.__evalExpr(lambda a, b : a > b, '>', stack=True)

    def execEQS(self):
        self.__evalExpr(lambda a, b : a > b, '==', stack=True)

    def execANDS(self):
        self.__evalExpr(lambda a, b : a and b, '&&', stack=True)

    def execORS(self):
        self.__evalExpr(lambda a, b : a or b, '||', stack=True)

    def execMOVE(self):
        var = self.currentInstruction.args[0]
        type, value, id = self.currentInstruction.args[1].getData('suffix', 'value', 'id')
        frame = getattr(self, var.suffix+'rame')
        if type in ('GF', 'LF', 'TF'): # if variable -> find in given frame
            type, value = self.__findInFrame(type, id)
        try:
            if value is None:
                exit(ERR_UNDEFVAR)
            frame[var.id].set({'value' : value, 'type' : type})
        except KeyError: 
            exit(ERR_UNDECLVAR)

    def execINT2CHAR(self):
        pass
    def execSTRLEN(self):
        pass
    def execTYPE(self):
        var = self.currentInstruction.args[0]
        type, id = self.currentInstruction.args[1].getData('suffix', 'id')
        frame = getattr(self, var.suffix+'rame')
        if type in ('GF', 'LF', 'TF'): # if variable -> find in given frame
            type, _ = self.__findInFrame(type, id)
        try:
            frame[var.id].set({'value' : '' if type == 'var' else type, 'type' : 'string'})
        except KeyError:
            exit(ERR_UNDECLVAR)

    def execNOT(self):
        var = self.currentInstruction.args[0]
        type, value, id = self.currentInstruction.args[1].getData('suffix', 'value', 'id')
        frame = getattr(self, var.suffix+'rame')
        if type in ('GF', 'LF', 'TF'): # if variable -> find in given frame
            type, value = self.__findInFrame(type, id)
        if type != 'bool':
            exit(ERR_TYPES)
        value, _ = self.__str2bool(value, _)
        try:
            frame[var.id].set({'value' : not value, 'type' : 'bool'})
        except KeyError: 
            exit(ERR_UNDECLVAR)
        
    def execADD(self):
        self.__evalExpr(lambda a, b : a + b, '+')
        
    def execSUB(self):
        self.__evalExpr(lambda a, b : a - b, '-')
        
    def execMUL(self):
        self.__evalExpr(lambda a, b : a * b, '*')
        
    def execIDIV(self):
        self.__evalExpr(lambda a, b : a / b, '/')
        
    def execLT(self):
        self.__evalExpr(lambda a, b : a < b, '<')

    def execGT(self):
        self.__evalExpr(lambda a, b : a > b, '>')

    def execEQ(self):
        self.__evalExpr(lambda a, b : a == b, '==')

    def execAND(self):
        self.__evalExpr(lambda a, b : a and b, '&&')

    def execOR(self):
        self.__evalExpr(lambda a, b : a or b, '||')

    def execSTRI2INT(self):
        pass
    def execCONCAT(self):
        self.__evalExpr(lambda a, b : a + b, '..')

    def execGETCHAR(self):
        self.__evalExpr(lambda a, b : a[int(b)], 'GC')

    def execSETCHAR(self):
        frame, id = self.currentInstruction.args[0].getData('frame', 'id')
        type, value = self.__findInFrame(frame, id)
        if type != 'string' or value == '' or value is None:
            exit(ERR_TYPES)
        frame = getattr(self, frame+'rame')
        type1, id1, value1 = self.currentInstruction.args[1].getData('suffix', 'id', 'value')
        type2, id2, value2 = self.currentInstruction.args[2].getData('suffix', 'id', 'value')
        if id1 is not None: # if symb1 (int) is variable
            type1, value1 = self.__findInFrame(type1, id1)
        if type1 != 'int':
            exit(ERR_TYPES)
        if not (0 <= value1 < len(value)):
            exit(ERR_STRING)
        if id2 is not None: # if symb2 (string) is variable
            type2, value2 = self.__findInFrame(type2, id2)
        if type2 != 'string':
            exit(ERR_TYPES)
        if value2 == '' or value2 is None:
            exit(ERR_STRING)
        frame[id].set({'value' : value[:value1] + value2[0] + value[value1+1:]})

    def execREAD(self):
        pass


        

def main():

    interpreter = Interpreter()
    interpreter.parseArguments()
    interpreter.constructInstructionList()
    interpreter.executeProgram()
    #interpreter.stats.
    
if __name__ == "__main__":
    main()
