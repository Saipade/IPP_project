from ctypes import sizeof
import xml.etree.ElementTree as ET
import argparse
import getopt
import sys
import operator
import re
import fileinput
import inspect
from xml.sax.saxutils import XMLFilterBase

from sets import *
from errorslist import *
from stats import Stats
    
class Interpreter:

    def __init__(self):
        self.stats = Stats()
    
    def parseArguments(self):
        """
        Parses command line arguments, finds source, input and stats files, fills statsGroups dictionary
        """
        try:
            opts, _ = getopt.getopt(sys.argv[1:], '', ['help', 'source=', 'input=', 'stats=', 'insts', 'hot', 'vars'])
        except getopt.GetoptError as err:
            print(err)
            exit(ERR_PARAM)
        statsGroups, tmpList, sCount, iCount, stCount, xmlFile, inputFile, statsFile = {}, list(), 0, 0, 0, "", "", ""
        for opt, arg in opts:
            if opt in ('--help'):
                if len(sys.argv) != 2:
                    exit(ERR_PARAM)
                print(help)
                exit(INTER_OK)
            elif opt in ('--source'):
                if sCount == 1:
                    exit(ERR_PARAM)
                sCount = 1
                xmlFile = arg
            elif opt in ('--input'):
                if iCount == 1:
                    exit(ERR_PARAM)
                iCount = 1
                inputFile = arg
            elif opt in ('--stats'):
                if stCount > 0:
                    statsGroups[statsFile] = tmpList
                tmpList = list()
                statsFile = arg
                stCount += 1
            elif opt in ('--insts', '--hot', '--vars') and stCount > 0:
                tmpList.append(opt[2:])
            else:
                exit(ERR_PARAM)
            statsGroups[statsFile] = tmpList
        
        if sCount == 0 and iCount == 0:
            exit(ERR_PARAM)
        

                


        


def main():

    interpreter = Interpreter()
    interpreter.parseArguments()
    

    

if __name__ == "__main__":
    main()