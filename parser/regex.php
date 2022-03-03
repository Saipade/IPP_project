<?php

/**
 * File contains regular expressions for character matching
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