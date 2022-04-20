<?php

    /**
     * Subject: IPP - Principles of Programming Languages
     * Part: Tester
     * @author Maksim Tikhonov (xtikho00)
     * 
     * File contains auxiliary variables (more of a constants tbh)
     */

    // array of possible options
    define('options', ["help", "directory:", "recursive", "parse-script:", "int-script:", 
    "parse-only", "int-only", "jexampath:", "noclean"]);

    // help message
    define("help", "Usage: test.php [--directory=PATH] [--recursive] [--parse-script=FILE] [--int-script=FILE] [--parse-only] [--int-only] [--jexampath=PATH] [--noclean]
Options:
    \t--help prints help message
    \t--directory=PATH path to the tests directory
    \t--recursive if enabled, makes script recursively iterate through all subfolders
    \t--parse-script=FILE path to the parser script
    \t--int-script=FILE path to interpreter script
    \t--parse-only if enabled, tests only parser
    \t--int-only if enabled, tests only interpreter
    \t--jexampath=PATH path to the directory with jexamxml.jar file
    \t--noclean if enabled, test script won't clean auxilary file\n");
    
?>