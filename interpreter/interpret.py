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

        self.stats = Stats()                            # stats Class attribute

        self.instructionList = []                       # list of instructions

        self.GFrame = []                                # list of global frame variables
        self.LFrame = []                                # list of local frame variables
        self.TFrame = []                                # list of temporary frame variables
        self.frames = []                                # list of local frames

        self.labelList = {}                             # dictionary of labels <labelName> -> line
        self.callStack = []                             # list of line numbers for return instructions 

        self.currentInstruction = None                  # instruction Class object
        self.currentLine = 0                            # current line of input code
        self.instructionCounter = 0                     # instruction counter
    
    def parseArguments(self):
        """
        Parses command line arguments, finds source and input files, fills statsGroups dictionary
        """
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
        while True: # execute exec*X*()
            self.currentInstruction = self.instructionList[self.currentLine]
            exec(f'self.exec{self.currentInstruction.opCode}()')
            self.currentLine += 1
            self.instructionCounter += 1
            if (self.currentLine == len(self.instructionList)):
                break

    '''
    Instruction list
    '''
    def execCREATEFRAME(self):
        self.TFrame = []

    def execPUSHFRAME(self):
        if self.TFrame is None:
            exit(ERR_NOFRAME)
        self.frames.append(self.TFrame)
        self.TFrame = None

    def execPOPFRAME(self):
        if (len(self.frames) == 0):
            exit(ERR_NOFRAME)
        self.TFrame = self.frames.pop()
    
    def execRETURN(self):
        if len(self.callStack) == 0:
            exit(ERR_UNDEFVAR)
        self.currentLine = self.callStack.pop()

            
    def execBREAK(self):
        print(f'Current position: {self.currentLine}\nGlobal frame: {self.GFrame}\nLocal frame: {self.LFrame}\n' \
            f'Temporary frame: {self.TFrame}\nInstruction counter: {self.instructionCounter}')

    def execCLEARS(self):
        self.frames = []

    def execCALL(self):
        try:
            self.currentLine = self.currentInstruction[self.currentLine].args[0]
        except KeyError:
            exit(ERR_SEMAN)

    def execLABEL(self):

    """ 
    def execDEFVAR(self):
    """        


        

def main():

    interpreter = Interpreter()
    interpreter.parseArguments()
    interpreter.constructInstructionList()
    interpreter.executeProgram()
    
if __name__ == "__main__":
    main()

    

"""         


def execLABEL(self):

def execJUMP(self):

def execJUMPIFEQS(self):

def execJUMPIFNEQS(self):

def execJUMPIFEQ(self):

def execJUMPIFNEQ(self):

def execDEFVAR(self):

def execPOPS(self):

def execPUSHS(self):

def execWRITE(self):

def execEXIT(self):
    
def execDPRINT(self):
    
def execNOTS(self):
    
def execINT2CHARS(self):
    
def execSTRI2INTS(self):
    
def execADDS(self):
    
def execSUBS(self):
    
def execMULS(self):
    
def execDIVS(self):
    
def execIDIVS(self):
    
def execLTS(self):
    
def execGTS(self):
    
def execEQS(self):
    
def execANDS(self):
    
def execORS(self):
    
def execMOVE(self):
    
def execINT2CHAR(self):
    
def execSTRLEN(self):
    
def execTYPE(self):
    
def execNOT(self):
    
def execADD(self):
    
def execSUB(self):
    
def execMUL(self):
    
def execIDIV(self):
    
def execLT(self):
    
def execGT(self):
    
def execEQ(self):
    
def execOR(self):
    
def execSTRI2INT(self):
    
def execCONCAT(self):
    
def execGETCHAR(self):
    
def execSETCHAR(self):
    
def execREAD(self):
"""    
