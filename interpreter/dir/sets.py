__all__ = ['instructionSet', 'help']

# dictionary of instructions and argument types related to them
instructionSet = {
    'CREATEFRAME' : [],
    'PUSHFRAME' : [],
    'POPFRAME' : [],
    'RETURN' : [],
    'BREAK' : [],
    'CLEARS' : [],
    'CALL' : ['Label'],
    'LABEL' : ['Label'],
    'JUMP' : ['Label'],
    'JUMPIFEQS' : ['Label'],
    'JUMPIFNEQS' : ['Label'],
    'JUMPIFEQ' : ['Label', 'Symbol', 'Symbol'],
    'JUMPIFNEQ' : ['Label', 'Symbol', 'Symbol'],
    'DEFVAR' : ['Variable'],
    'POPS' : ['Variable'],
    'PUSHS' : ['Symbol'],
    'WRITE' : ['Symbol'],
    'EXIT' : ['Symbol'],
    'DPRINT' : ['Symbol'],
    'NOTS' : [],
    'INT2CHARS' : [],
    'STRI2INTS' : [],
    'ADDS' : [],
    'SUBS' : [],
    'MULS' : [],
    'DIVS' : [],
    'IDIVS' : [],
    'LTS' : [],
    'GTS' : [],
    'EQS' : [],
    'ANDS' : [],
    'ORS' : [],
    'MOVE' : ['Variable', 'Symbol'],
    'INT2CHAR' : ['Variable', 'Symbol'],
    'STRLEN' : ['Variable', 'Symbol'],
    'TYPE' : ['Variable', 'Symbol'],
    'NOT' :  ['Variable', 'Symbol'],
    'ADD' : ['Variable', 'Symbol', 'Symbol'],
    'SUB' : ['Variable', 'Symbol', 'Symbol'],
    'MUL' : ['Variable', 'Symbol', 'Symbol'],
    'IDIV' : ['Variable', 'Symbol', 'Symbol'],
    'LT' : ['Variable', 'Symbol', 'Symbol'],
    'GT' : ['Variable', 'Symbol', 'Symbol'],
    'EQ' : ['Variable', 'Symbol', 'Symbol'],
    'AND' : ['Variable', 'Symbol', 'Symbol'],
    'OR' : ['Variable', 'Symbol', 'Symbol'],
    'STRI2INT' : ['Variable', 'Symbol', 'Symbol'],
    'CONCAT' : ['Variable', 'Symbol', 'Symbol'],
    'GETCHAR' : ['Variable', 'Symbol', 'Symbol'],
    'SETCHAR' : ['Variable', 'Symbol', 'Symbol'],
    'READ' : ['Variable', 'Type']}

# --help text
help = \
    "Usage: interpret.py [--source=SOURCE_FILE] [--input=INPUT_FILE] [--stats=STATS_FILE] [--insts] [--hot] [--vars]\n" \
    "Arguments:\n\t" \
    "--help shows help message and exits\n\t" \
    "--source=SOURCE_FILE indicates source file\n\t" \
    "--input=INPUT_FILE indicates input file\n\t" \
    "--stats=STATS_FILE indicates stats file\n\t\t" \
    "--insts stats option, counts \"executable\" instructions\n\t\t" \
    "--hot stats option, finds the most used instruction\n\t\t" \
    "--vars stats option, counts maximum number of initialized variables at a time"