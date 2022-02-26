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
        self.instructionCounter = 0                     # instruction counter
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
            print(xmlInstruction.attrib['order'])
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
            exec(f'self.exec{self.currentInstruction.opCode}()')
            self.stats.updateInsts(self.currentInstruction)
            self.stats.updateHot(self.currentInstruction)
            self.currentLine += 1
            self.instructionCounter += 1
            if (self.currentLine == len(self.instructionList)):
                break

    def __getValues(self, stack=False):
        '''
        Returns variables' values (if there are variables in expression), checks type compatibility
        '''
        if stack is True:
            operand2 = self.dataStack.pop()
            operand1 = self.dataStack.pop()
        else:
            operand1, operand2 = self.currentInstruction.args[1], self.currentInstruction.args[2]
        suffix1, suffix2 = operand1.suffix, operand2.suffix
        if suffix1 == 'GF' or suffix1 == 'LF' or suffix1 == 'TF':
            try:
                exec(f'operand1 = self.{suffix1}rame[{operand1.value}]')
                opType1, opVal1 = operand1
            except KeyError: # undefined variable
                exit(ERR_SEMAN)
        else:
            opType1, opVal1 = suffix1, operand1.value
        if suffix2 == 'GF' or suffix2 == 'LF' or suffix2 == 'TF':
            try:
                exec(f'operand2 = self.{suffix2}rame[{operand2.value}]')
                opType2, opVal2 = operand2
            except KeyError: # undefined variable
                exit(ERR_SEMAN)
        else:
            opType2, opVal2 = suffix2, operand2.value
        if opType1 != opType2 and opVal1 != 'nil' and opVal2 != 'nil':
            exit(ERR_TYPES)
        return opVal1, opVal2

    def __evalExpr(self, op, stack=False):
        operand1, operand2, retval = self.__getValues(stack), None

        if operand1 == 'true' or 'false': operand1 = operand1.capitalize()
        if operand2 == 'true' or 'false': operand2 = operand2.capitalize()

        if operand1 == 'nil' or operand2 == 'nil':
            if op != '==' and op != '!=':
                exit(ERR_TYPES)
            if operand1 == 'nil': operand1 = 'None'
            if operand2 == 'nil': operand2 = 'None'

        exec('retval = operand1 op operand2' )
        if stack is True: self.dataStack.append(retval)
        else: return retval


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
            f'Temporary frame: {self.TFrame}\nInstruction counter: {self.instructionCounter}')

    def execCLEARS(self):
        self.framesStack = []
        self.stats.updateVars(-self.stats.currentVars)

    def execCALL(self):
        try:
            self.currentLine = self.labelList[self.currentInstruction.args[0].value]
            self.callStack.append(self.currentLine+1)
            self.stats.updateVars(len(self.GFrame)+len(self.TFrame)-self.stats.currentVars)
        except KeyError:
            exit(ERR_SEMAN)

    def execLABEL(self):
        '''
        All labels were detected before the code execution. See next method
        '''
        pass
    
    def execL483L(self):
        if self.currentInstruction.args[0].value in self.labelList:
            exit(ERR_SEMAN)
        self.labelList[self.currentInstruction.args[0].value] = self.currentLine + 1

    def execJUMP(self):
        try:
            self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError:
            exit(ERR_SEMAN)

    def execJUMPIFEQS(self):
        try:
            if self.__evalExpr('==', stack=True) == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError:
            exit(ERR_SEMAN)
            
    def execJUMPIFNEQS(self):
        try:
            if self.__evalExpr('!=', stack=True) == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError:
            exit(ERR_SEMAN)
            
    def execJUMPIFEQ(self):
        try:
            if self.__evalExpr('==') == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError:
            exit(ERR_SEMAN)

    def execJUMPIFNEQ(self):
        try:
            if self.__evalExpr('!=') == True:
                self.currentLine = self.labelList[self.currentInstruction.args[0].value]
        except KeyError:
            exit(ERR_SEMAN)
            
    def execDEFVAR(self):
        frame, id = self.currentInstruction.args[0].getData(var=True)
        if frame != 'GF' or frame != 'TF' or frame != 'LF': 
            exit(ERR_SEMAN)
        exec(f'{frame}rame[frame+id] = self.currentInstruction.args[0]')

    def execPOPS(self):
        if len(self.callStack) == 0:
            exit(ERR_UNDEFVAR)
        frame = self.currentInstruction.args[0].suffix
        id = self.currentInstruction.args[0].id
        if frame != 'GF' or frame != 'LF' or frame != 'TF':
            exit(ERR_SEMAN)
        poppedData = self.dataStack.pop()
        exec(f'{frame}rame[id].set(poppedData)')

    def execPUSHS(self):
        if self.currentInstruction.args[0].value is None:
            exit(ERR_UNDEFVAR)
        self.dataStack.append(self.currentInstruction.args[0])

    def execWRITE(self):
        dType, value, toPrint = self.currentInstruction.args[0].getData(var=False), None
        if value == 'nil': toPrint = ''
        else: toPrint = value
        print(toPrint, end='')

    def execEXIT(self):
        pass
    def execDPRINT(self):
        pass
    def execNOTS(self):
        pass
    def execINT2CHARS(self):
        pass
    def execSTRI2INTS(self):
        pass
    def execADDS(self):
        pass
    def execSUBS(self):
        pass
    def execMULS(self):
        pass
    def execDIVS(self):
        pass
    def execIDIVS(self):
        pass
    def execLTS(self):
        pass
    def execGTS(self):
        pass
    def execEQS(self):
        pass
    def execANDS(self):
        pass
    def execORS(self):
        pass
    def execMOVE(self):
        pass
    def execINT2CHAR(self):
        pass
    def execSTRLEN(self):
        pass
    def execTYPE(self):
        pass
    def execNOT(self):
        pass
    def execADD(self):
        pass
    def execSUB(self):
        pass
    def execMUL(self):
        pass
    def execIDIV(self):
        pass
    def execLT(self):
        pass
    def execGT(self):
        pass
    def execEQ(self):
        pass
    def execOR(self):
        pass
    def execSTRI2INT(self):
        pass
    def execCONCAT(self):
        pass
    def execGETCHAR(self):
        pass
    def execSETCHAR(self):
        pass
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

    

"""
"""    
