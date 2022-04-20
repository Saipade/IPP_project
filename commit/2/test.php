<?php
    
    /**
     * Subject: IPP - Principles of Programming Languages
     * Part: Tester
     * @author Maksim Tikhonov (xtikho00)
     * 
     * Main file
     */

    include 'tester.php';

    $tester = new Tester();
    $tester->parseArguments();
    $tester->test();
    $tester->constructHTML();

    return TEST_OK;

?>