from asyncore import read
import readline
import xml.etree.ElementTree as ET
import getopt
import sys
import re

from instruction import Instruction
from sets import *
from errorslist import *
from stats import Stats
    
class Interpreter:

    def __init__(self):
        self.xmlTree = None                             # XML tree of input XML code representation
        self.inputFile = sys.stdin                      # text with input for source code interpretation
        self.input = []                                 # input list (for case if there is input file)
        self.orders = []                                # list of orders (no duplicates, all should be positive)

        self.stats = Stats()                            # Stats class attribute

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
        except getopt.GetoptError:
            exit(ERR_PARAM)
        tmpList, sIsPresent, iIsPresent, stIsPresent, xmlFile, statsFile = list(), 0, 0, 0, None, None
        for opt, arg in opts:
            if opt in ('--help'):
                if len(sys.argv) != 2: # --help is present along with other command line options
                    exit(ERR_PARAM)
                print(help)
                exit(INTER_OK)
            elif opt in ('--source'):
                if sIsPresent == 1: # if there is more than 1 source file -> error
                    exit(ERR_PARAM)
                sIsPresent = 1
                xmlFile = arg
            elif opt in ('--input'): # if there is more than 1 input file -> error
                if iIsPresent == 1:
                    exit(ERR_PARAM)
                iIsPresent = 1
                self.inputFile = arg
            elif opt in ('--stats'):
                if stIsPresent > 0:
                    self.stats.statsGroups[statsFile] = tmpList
                else:
                    stIsPresent = 1
                tmpList = list()
                statsFile = arg
            elif opt in ('--insts', '--hot', '--vars') and stIsPresent > 0:
                tmpList.append(opt[2:]) # appends stat name to temporary list, will be added to statsGroups dictionary later
            else:
                exit(ERR_PARAM)
            if stIsPresent == 1:
                self.stats.statsGroups[statsFile] = tmpList
        # no input and no source -> error
        if sIsPresent == 0 and iIsPresent == 0:
            exit(ERR_PARAM)
        self.__readFile(xmlFile)

    def __readFile(self, xmlFile):
        '''
        Reads given files into 2 corresponding interpreter attributes
        '''
        # xmlTree - root XMLElement (program)
        try:
            self.xmlTree = ET.parse(sys.stdin).getroot() if xmlFile is None else ET.parse(xmlFile).getroot()
        except ET.ParseError:
            exit(ERR_FORMAT)
        if self.xmlTree.tag != 'program' or self.xmlTree.get('language') != 'IPPcode22':
            exit(ERR_STRUCT)
        if self.inputFile is not sys.stdin: # read input file into self.input list (if there is input file)
            with open(self.inputFile, 'r') as file:
                self.input = file.read().splitlines()
        # sort instructions by order
        try:
            self.xmlTree[:] = sorted(self.xmlTree, key=lambda child: int(re.search('\d+', child.get('order')).group()))
        except:
            exit(ERR_STRUCT)
        
    def executeProgram(self):
        '''
        Iterates through input code 2 times,
        first - finds all labels,
        second - executes instructions
        '''
        for _, xmlInstruction in enumerate(self.xmlTree):
            self.currentInstruction = Instruction(xmlInstruction)
            if self.currentInstruction.order in self.orders or self.currentInstruction.order < 1:
                exit(ERR_STRUCT)
            self.orders.append(self.currentInstruction.order)
            if self.currentInstruction.opCode == 'LABEL':
                self.execL483L()
            self.currentLine += 1

        self.currentLine = 0
        while True:
            self.currentInstruction = Instruction(self.xmlTree[self.currentLine])
            #print(self.currentInstruction)
            getattr(self, 'exec'+self.currentInstruction.opCode)()
            self.stats.updateInsts(self.currentInstruction)
            self.stats.updateHot(self.currentInstruction)
            self.currentLine += 1
            if (self.currentLine == len(self.xmlTree)):
                break

    def __getValues(self, op, stack=False):
        '''
        Returns variables' values (if there are variables in expression), checks type compatibility
        '''
        if stack is True:
            opType2, opVal2 = self.dataStack.pop()
            opType1, opVal1 = self.dataStack.pop()
        else:
            (opType1, opVal1), (opType2, opVal2) = \
            self.currentInstruction.args[1].getData('suffix', 'id'), self.currentInstruction.args[2].getData('suffix', 'id')
            if opType1 in ('GF', 'LF', 'TF'):
                opType1, opVal1 = self.__findInFrame(opType1, opVal1)
            else:
                opType1, opVal1 = self.currentInstruction.args[1].getData('suffix', 'value')
            if opType2 in ('GF', 'LF', 'TF'):
                opType2, opVal2 = self.__findInFrame(opType2, opVal2)
            else:
                opType2, opVal2 = self.currentInstruction.args[2].getData('suffix', 'value')
        # type compatibility checks
        if op in ('+', '-', '//', '/', '*') and (opType1 != 'int' or opType2 != 'int'):
            exit(ERR_TYPES)
        if op in ('>', '<') and (opType1 != opType2):
            exit(ERR_TYPES)
        if op in ('==', '!=') and ((opType1 != opType2) and (opType1 != 'nil' and opType2 != 'nil')):
            exit(ERR_TYPES)
        if op in ('&&', '||') and (opType1 != 'bool' or opType2 != 'bool'):
            exit(ERR_TYPES)
        if op in ('..') and (opType1 != 'string' or opType2 != 'string'):
            exit(ERR_TYPES)
        if op in ('GC') and (opType1 != 'string' or opType2 != 'int'):
            exit(ERR_TYPES)
        if op in ('ORD'):
            if (opType1 != 'string' or opType2 != 'int'):
                exit(ERR_TYPES)
            if len(opVal1) <= opVal2 or opVal2 < 0:
                exit(ERR_STRING)
                
        return opVal1, opVal2
    
    def __getType(self, op):
        '''
        Returns expression's result type
        '''
        if op in ('==', '!=', '>', '<', '&&', '||'):
            type = 'bool'
        elif op in ('+', '-', '*', '/', '//', 'ORD'):
            type = 'int'
        elif op in ('..', 'GC'):
            type = 'string'
        return type

    def __evalExpr(self, lfunc, op, stack=False):
        '''
        Evaluates given expression
        '''
        operand1, operand2 = self.__getValues(op, stack)
        type = self.__getType(op)
        # if one of operands is either 'nil' or None (None represents nil type)
        try:
            retval = lfunc(operand1, operand2)
        except:
            exit(ERR_VALUE)
        if stack is True: self.dataStack.append((type, retval))
        else: return type, retval

    def __findFrame(self, frame):
        frame =  getattr(self, frame+'rame')
        if frame is None:
            exit(ERR_NOFRAME)
        return frame
        

    def __findInFrame(self, frame, id):
        try:
            type, value = getattr(self, frame+'rame')[id].getData('type', 'value')
        except:
            exit(ERR_NOFRAME)
        return (type, value)

    '''
    Instruction list
    '''
    def execCREATEFRAME(self):
        self.TFrame = {}

    def execPUSHFRAME(self):
        if self.TFrame is None:
            exit(ERR_NOFRAME)
        self.framesStack.append(self.LFrame)
        self.LFrame = self.TFrame
        self.TFrame = None

    def execPOPFRAME(self):
        if self.LFrame is None:
            exit(ERR_NOFRAME)
        if (len(self.framesStack) == 0):
            if (len(self.LFrame) == 0):
                exit(ERR_NOFRAME)
            self.TFrame = self.LFrame
            self.LFrame = {}
            self.stats.updateVars(len(self.TFrame)-self.stats.currentVars)
            return
        self.TFrame = self.LFrame
        self.LFrame = self.framesStack.pop()
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
            self.callStack.append(self.currentLine)
            self.currentLine = self.labelList[self.currentInstruction.args[0].value]
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
            self.__evalExpr(lambda a, b: a == b, '==', stack=True)
            if self.dataStack.pop()[1] is True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)
            
    def execJUMPIFNEQS(self):
        try:
            self.__evalExpr(lambda a, b: a != b, '!=', stack=True)
            if self.dataStack.pop()[1] is True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)
            
    def execJUMPIFEQ(self):
        try:
            if self.__evalExpr(lambda a, b: a == b, '==')[1] == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)

    def execJUMPIFNEQ(self):
        try:
            if self.__evalExpr(lambda a, b: a != b, '!=')[1] == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError: # label does not exist
            exit(ERR_SEMAN)
            
    def execDEFVAR(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        if id in frame: # attempt of variable redefinition
            exit(ERR_SEMAN)
        frame[id] = self.currentInstruction.args[0]

    def execPOPS(self):
        if len(self.dataStack) == 0:
            exit(ERR_UNDEFVAR)
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.dataStack.pop()
        try:
            frame[id].set({'type' : type, 'value' : value})
        except KeyError:
            exit(ERR_UNDECLVAR)

    def execPUSHS(self):
        type, id, value = self.currentInstruction.args[0].getData('suffix', 'id', 'value')
        if type in ('GF', 'LF', 'TF'):
            type, value = self.__findInFrame(type, id)
        self.dataStack.append((type, value))

    def execWRITE(self):
        type, id, toPrint = self.currentInstruction.args[0].getData('suffix', 'id', 'value')
        if id is not None:
            type, toPrint = self.__findInFrame(type, id)
        if type == 'string': # convert all escape sequences 
            toPrint = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), toPrint)
        if type == 'bool': # convert bool2str
            toPrint = str(toPrint).lower()
        if toPrint == 'nil': 
            toPrint = ''
        print(toPrint, end='', file=sys.stdout)

    def execEXIT(self):
        type, id, value = self.currentInstruction.args[0].getData('suffix', 'id', 'value')
        if id is not None:
            type, value = self.__findInFrame(type, id)
        if type != 'int' or int(value) > 49 or int(value) < 0:
            exit(ERR_VALUE)
        self.stats.writeStats()
        exit(value)
        
    def execDPRINT(self):
        type, id, toPrint = self.currentInstruction.args[0].getData('suffix', 'id', 'value')
        if id is not None:
            type, toPrint = self.__findInFrame(type, id)
        print(toPrint, end='', file=sys.stderr)

    def execNOTS(self):
        type, value = self.dataStack.pop()
        if type != 'bool':
            exit(ERR_TYPES)
        self.dataStack.append((type, not value))
        
    def execINT2CHARS(self):
        type, value = self.dataStack.pop()
        if type != 'int': 
            exit(ERR_TYPES)
        if not (0 <= value <= 255):
            exit(ERR_STRING)
        self.dataStack.append(('string', chr(value)))

    def execSTRI2INTS(self):
        self.__evalExpr(lambda a, b : ord(a[b]), 'ORD', stack=True)

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
        self.__evalExpr(lambda a, b : a == b, '==', stack=True)

    def execANDS(self):
        self.__evalExpr(lambda a, b : a and b, '&&', stack=True)

    def execORS(self):
        self.__evalExpr(lambda a, b : a or b, '||', stack=True)

    def execMOVE(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        type, value, id1 = self.currentInstruction.args[1].getData('suffix', 'value', 'id')
        frame = self.__findFrame(frame)
        if type in ('GF', 'LF', 'TF'): # if variable -> find in given frame
            type, value = self.__findInFrame(type, id1)
        try:
            if value is None:
                exit(ERR_UNDEFVAR)
            frame[id].set({'value' : value, 'type' : type})
        except KeyError: 
            exit(ERR_UNDECLVAR)

    def execINT2CHAR(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        type, id1, value = self.currentInstruction.args[1].getData('suffix', 'id', 'value')
        frame = self.__findFrame(frame)
        if type in ('LF', 'GF', 'TF'):
            type, value = self.__findInFrame(type, id1)
        if not (0 <= value <= 1114111): # invalid value 0 <= i <= 0x10ffff
            exit(ERR_STRING)
        value = chr(value)
        frame[id].set({'type' : 'string', 'value' : value})

        
    def execSTRLEN(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        type, id1, value = self.currentInstruction.args[1].getData('suffix', 'id', 'value')
        if type in ('GF', 'LF', 'TF'):
            type, value = self.__findInFrame(type, id1)
        frame = self.__findFrame(frame)
        
        frame[id].set({'type' : type, 'value' : value})

    def execTYPE(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        type, id1 = self.currentInstruction.args[1].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        if type in ('GF', 'LF', 'TF'): # if variable -> find in given frame
            type, _ = self.__findInFrame(type, id1)
        try:
            frame[id].set({'value' : '' if type == 'var' else type, 'type' : 'string'})
        except KeyError:
            exit(ERR_UNDECLVAR)

    def execNOT(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        type, value, id1 = self.currentInstruction.args[1].getData('suffix', 'value', 'id')
        frame = self.__findFrame(frame)
        if type in ('GF', 'LF', 'TF'): # if variable -> find in given frame
            type, value = self.__findInFrame(type, id1)
        if type != 'bool':
            exit(ERR_TYPES)
        try:
            frame[id].set({'value' : not value, 'type' : 'bool'})
        except KeyError: 
            exit(ERR_UNDECLVAR)
        
    def execADD(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a + b, '+')
        frame[id].set({'type' : type, 'value' : value})
        
    def execSUB(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a - b, '-')
        frame[id].set({'type' : type, 'value' : value})
        
    def execMUL(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a * b, '*')
        frame[id].set({'type' : type, 'value' : value})
        
    def execIDIV(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a // b, '//')
        frame[id].set({'type' : type, 'value' : value})
        
    def execLT(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a < b, '<')
        frame[id].set({'type' : type, 'value' : value})

    def execGT(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a > b, '>')
        frame[id].set({'type' : type, 'value' : value})

    def execEQ(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a == b, '==')
        frame[id].set({'type' : type, 'value' : value})

    def execAND(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a and b, '&&')
        frame[id].set({'type' : type, 'value' : value})

    def execOR(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a or b, '||')
        frame[id].set({'type' : type, 'value' : value})

    def execSTRI2INT(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : ord(a[b]), 'ORD', stack=True)
        frame[id].set({'type' : type, 'value' : value})
        
    def execCONCAT(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a + b, '..')
        frame[id].set({'type' : type, 'value' : value})

    def execGETCHAR(self):
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        frame = self.__findFrame(frame)
        type, value = self.__evalExpr(lambda a, b : a[int(b)], 'GC')
        frame[id].set({'type' : type, 'value' : value})

    def execSETCHAR(self):
        frame, id = self.currentInstruction.args[0].getData('frame', 'id')
        type, value = self.__findInFrame(frame, id)
        if type != 'string' or value == '' or value is None:
            exit(ERR_TYPES)
        frame = self.__findFrame(frame)
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
        if self.inputFile is sys.stdin: # read from stdin
            readLine = input()
        else:                           # read from input file
            readLine = self.input[0]
            self.input = self.input[1:]
        frame, id = self.currentInstruction.args[0].getData('suffix', 'id')
        readType = self.currentInstruction.args[1].value
        frame = self.__findFrame(frame)
        if readType == 'int':
            newValue = int(readLine)
            newType = 'int'
        if readType == 'string':
            newValue = str(readLine)
            newType = 'string'
        if readType == 'bool':
            if readLine.lower() == 'true': newValue = True
            elif readLine.lower() == 'false': newValue = False
            else: exit(ERR_TYPES)
            newType = 'bool'
        if readLine == '':
            newValue = 'nil'
            newType = 'nil'
        try:
            frame[id].set({'type' : newType, 'value' : newValue})
        except KeyError:
            exit(ERR_UNDECLVAR)

def main():
    interpreter = Interpreter()
    interpreter.parseArguments()
    interpreter.executeProgram()
    interpreter.stats.writeStats()
    
if __name__ == "__main__":
    main()
