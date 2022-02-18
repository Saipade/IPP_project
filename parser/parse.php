<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * Main file
 */

    include 'errorslist.php';
    include 'parser.php';
    include 'instruction.php';
    include 'stats.php';
    
    ini_set('display_errors', 'stderr');

    $stats = new Stats();
    $parser = new Parser($stats);

    $parser->parseArgs($argc, $argv);
    $parser->parseCode();

    $parser->makeupStats();
    $parser->stats->writeStats();

    $xml = new DomDocument('1.0', 'UTF-8');
    $xml->formatOutput = true;
    $program = $xml->createElement('program');
    $program->setAttribute('language', 'IPPcode22');
    $xml->appendChild($program);
    $parser->convertToXML($xml, $program);

    $formattedXML = $xml->saveXML();
    echo $formattedXML;

?>