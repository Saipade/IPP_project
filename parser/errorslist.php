<?php 

/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * Files contains macros for errors
 */

    define("SCAN_OK", 0);                       // no error
    define("ERR_PARAM", 10);                    // script parameter error
    define("ERR_INPUT", 11);                    // read error
    define("ERR_OUTPUT", 12);                   // write error
    define("ERR_HEADER", 21);                   // header is missing
    define("ERR_OPCODE", 22);                   // invalid operation code
    define("ERR_SYNTAX", 23);                   // lexical or syntax error
    define("ERR_INTERNAL", 99);                 // internal error

?>