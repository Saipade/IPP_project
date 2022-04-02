<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * Part: Parser
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains some regular expression patterns
 */

    define("statsPattern", "/^(--stats=)(.+)$/");
    define("statsOptPattern", "/^--(loc|comments|labels|jumps|fwjumps|backjumps|badjumps)$/");
    define("headerPattern", "/^(.IPPcode22)$/i");
    define("commentPattern", "/#.*/");
    define("varPattern", "/^[[:alpha:]_$&%\-*!?][[:alnum:]_$&%\-*!?]*$/");
    define("lablePattern", "/^[[:alpha:]_$&%\-*!?][[:alnum:]_$&%\-*!?]*$/"); // same as varPattern
    define("intPattern", "/^([-+]?[0-9]+|nil)$/");
    define("boolPattern", "/^(true|false)$/");
    define("nilPattern", "/^(nil)$/");
    define("stringPattern", "/^(\\\\\d\d\d|(?!\#|\\\\).)*$/u");
    define("typePattern", "/^(int|string|bool|float)$/");
    define("jumpPattern", "/^((JUMP)(.*)|CALL)$/");

?>