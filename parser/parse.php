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

    $parser = new Parser();

    $parser->parseArgs();
    $parser->parseCode();

    $parser->makeupStats();
    
    $parser->stats->writeStats();

    $xml = new DomDocument('1.0', 'UTF-8');
    $xml->formatOutput = true;
    $program = $xml->createElement('program');
    $program->setAttribute('language', 'IPPcode22');
    $xml->appendChild($program);
    $parser->convertToXML($xml, $program);

    $xml = $xml->saveXML();
    echo $xml;

    return SCAN_OK;

?>