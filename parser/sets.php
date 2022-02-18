<?php 

/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains auxiliary arrays
 */

    // array of all IPPcode22 instructions with their arguments
    $instructionSet = array(
        'CREATEFRAME' => [],
        'PUSHFRAME' => [],
        'POPFRAME' => [],
        'RETURN' => [],
        'BREAK' => [],
        'CALL' => ['Label'],
        'LABEL' => ['Label'],
        'JUMP' => ['Label'],
        'JUMPIFEQ' => ['Label', 'Symbol', 'Symbol'],
        'JUMPIFNEQ' => ['Label', 'Symbol', 'Symbol'],
        'DEFVAR' => ['Variable'],
        'POPS' => ['Variable'],
        'PUSHS' => ['Symbol'],
        'WRITE' => ['Symbol'],
        'EXIT' => ['Symbol'],
        'DPRINT' => ['Symbol'],
        'MOVE' => ['Variable', 'Symbol'],
        'INT2CHAR' => ['Variable', 'Symbol'],
        'STRLEN' => ['Variable', 'Symbol'],
        'TYPE' => ['Variable', 'Symbol'],
        'NOT' =>  ['Variable', 'Symbol'],
        'ADD' => ['Variable', 'Symbol', 'Symbol'],
        'SUB' => ['Variable', 'Symbol', 'Symbol'],
        'MUL' => ['Variable', 'Symbol', 'Symbol'],
        'IDIV' => ['Variable', 'Symbol', 'Symbol'],
        'LT' => ['Variable', 'Symbol', 'Symbol'],
        'GT' => ['Variable', 'Symbol', 'Symbol'],
        'EQ' => ['Variable', 'Symbol', 'Symbol'],
        'AND' => ['Variable', 'Symbol', 'Symbol'],
        'OR' => ['Variable', 'Symbol', 'Symbol'],
        'STRI2INT' => ['Variable', 'Symbol', 'Symbol'],
        'CONCAT' => ['Variable', 'Symbol', 'Symbol'],
        'GETCHAR' => ['Variable', 'Symbol', 'Symbol'],
        'SETCHAR' => ['Variable', 'Symbol', 'Symbol'],
        'READ' => ['Variable', 'Type'],
    );

    // array of possible stats options
    $statsOptions = array(                      
        "stats:",
        "loc",
        "comments",
        "labels",
        "jumps",
        "fwjumps",
        "backjumps",
        "badjumps",
    );

?>