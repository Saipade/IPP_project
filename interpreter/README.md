# Implementation documentation for the 2. task of IPP subject 2021/2022
## Author: Maksim Tikhonov

## Login: xtikho00

---

# Interpreter

## Brief description

**interpret.py** script interprets input XML representation of **IPPcode22** either from `stdin` or from a file given by `--source=` command line parameter. Input for the `READ` function is given by `--input=` parameter. The output strings given by "writing" functions of **IPPcode22** are printed either to `stdout` (`WRITE`) or to `stderr` (`DPRINT`, `BREAK`). 

All interpreter scripts are designed in OOP manner. All the remarkable details of the implementation just as registered extensions are listed and described below. 

## Details

### Interpreter class

`Interpreter class` encapsulates all required data and methods for code interpretation. Such as XML tree of code (`xml.etree.ElementTree` library was used), input file pointer; dictionaries for global, local and temporary frames; frame stack, which is essential for `PUSHFRAME`, `CREATEFRAME` and `POPFRAME` operations; data stack for correct implementation of stack related instructions, line counter. It also has instances of `Stats` and `Factory` classes, the former for statistics, the latter for the object instantiation of `Instruction` and `Argument` classes.

### Input code interpretation

As soon as command line arguments are parsed and all required parameters (such as input XML tree, pointer to the file with inputs, and stats options) are set the interpreter starts code execution: firstly, it runs through the entire input code in search for label identifiers and inconsistency among `order` parameters. Then, after the labels dictionary of shape {\<labelname\> => line} is created, interpreter starts executing the code in `while True` loop (instruction to be executed is decided by `current line` parameter, which can be changed by **jumps** or incremented by 1 at the end of each of the loop's iterations). Each instruction in XML document corresponds to a signle `Instruction` class object, the code is being executied by functions with names like "exec\*X\*", where X is a **IPPcode22** function that is being processed; all corresponding functions are called by `getattr` with an argument of the current instruction's operation code.

### Arithmetic and logical operations

All aritmetic and logical operations are implemented in corresponding `Interpreter class` methods (e.g. `MUL`, `ORS`), most of them were implemented with the help of lambda functions that were passed to `__evalExpr` method which evaluates given expression and checks for type compatibility.

### Extensions

#### STACK

Stack related instructions were implemented in the same way as were normal ones (one instruction - one `Interpreter`'s "exec\*X\*" method). The main and the most obvious difference from normal instruction is the fact that these ones are using **data stack**, which contains Python's tuples of form "(`data type`, `value`)". Each time stack instruction is executed, interpreter pops highest data pairs from the top of the stack, evaluates given expression, and pushes the result back to the top.

#### STATI

All the statistics are encapsulated inside the `Stats` class and are calculated during the code execeution: each time data frame is changed the `updateVars` method is called for the sake of actualisation of counter of currently initialised variables, each time the new instruction is called `updateInsts` and `updateHot` methods are called for the actualisation of counter of executed instructions and counters of "hot" instructions.

At the end of enterpretation all the statistics that were specified in command line arguments will be printed into the given files.

#### NVI

As were mentioned before, each script is designed in the OOP manner. For the purpose of adding separation between object's usage and object's creation the **dependency injection** was utilised via creating instance inside other object -- the **abstract factory**. It has methods for both `Instruction` class and `Argument` class instantiations. Also the **inheritence** was used to avoid code duplication (classes `Variable`, `Type`, `Symbol` and `Label` are all subclasses of `Argument` class)

# Tester

## Brief description

**test.php** script automatically tests **parse.php** or/and **interpret.py** scripts and generates HTML file with results of individual tests.

## Details

### Recursive location of test files

As soon as all command line arguments were processed by `getopt` function, tester starts the location of files. If `--recursive` option is present it recursively locates all subfolders of given by argument `--directory=` folder, the result of this operation -- array of paths (array of single element in case of absense of `--recursive`) is then transformed into associative array of form "[folder path] => [test_name1, test_name_2, ...]" 

### Testing

After array with files' paths is ready it is passed to  `test` method. This method will first create temporary file (or "noclean-output" folder in case of `--noclean`) iterate through all test files and will execute code given by **test_name_N.src** file. After the execution the instance of `TestResult` class is being constructed which then compares (either by `diff` or by `jexam`) the test result with reference test result given by **test_name_N.out** file.

### HTML

HTML header shows what parts of the project are being tested and global statistics on test results, all individual tests are listed in centered blocks. It is also necessary to hover over `Output/Expected output` in order to see results. 

### Extensions

No extensions are registered