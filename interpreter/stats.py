from sets import instructionSet
class Stats:

    _instance = None

    def __new__(self):
        '''
        Initiates Stats class object (is a singleton)
        '''
        if not self._instance:
            self._instance = super(Stats, self).__new__(self)
        return self._instance

    def __init__(self):
        self.insts = 0                                      # --insts
        self.hot = 0                                        # --hot
        self.vars = 0                                       # --vars
        self.currentVars = 0                                # counter for current number of initialized variables
        self.statsGroups = {}                               # dictionary of shape <filename> => [statsopt1, statsopt2, ..., statsoptN]

        self.hotInstructions = {}                           # dictionary of shape <instructionOpCode => [useCount, firstAppear]
        for instr in instructionSet:
            self.hotInstructions[instr] = [0, 1]

    def updateInsts(self, instruction):
        if instruction.opCode not in ('LABEL', 'DPRINT', 'BREAK'):
            self.insts += 1

    def updateVars(self, num):
        '''
        Updates number of initialized variables
        '''
        self.currentVars += num
        if self.currentVars > self.vars:
            self.vars = self.currentVars

    def updateHot(self, instruction):
        '''
        Updates "hot" stats for given instruction
        '''
        self.hotInstructions[instruction.opCode][0] += 1
        if self.hotInstructions[instruction.opCode][1] > instruction.order:
            self.hotInstructions[instruction.opCode][1] = instruction.order

    def __findTheHottest(self):
        '''
        Finds the most used instruction, if there are many with the same number of use, finds one that appeared earlier in code.
        Returns order.
        '''
        return list(sorted(list(self.hotInstructions.items()), key=lambda x: (x[1][0], 1/x[1][1]), reverse=True))[0][1][0] # too lon' :(

    def writeStats(self):
        self.hot = self.__findTheHottest()
        print(self.statsGroups)
        for fileName in self.statsGroups:
            if fileName is None:
                continue
            print(fileName)
            file = open(fileName, 'w')
            statsText = ''
            for stat in self.statsGroups[fileName]:
                statsText += f'{getattr(self, stat)}\n'
            file.write(statsText)
            file.close()

    

