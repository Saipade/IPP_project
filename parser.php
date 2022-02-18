<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains implementation of Parser class
 */

    class Parser {

        public function __construct($stats) {
            $this->stats = $stats;
        }

        /**
         * Parses input arguments
         * 
         * @param argc number of input arguments
         * @param argv array of input arguments
         */
        public function parseArgs($argc, $argv) {
            global $statsOptions;
            $options = getopt("", ["help"]);                                                // if --help is present
            if (array_key_exists("help", $options)) {
                if ($argc > 2) {
                    fputs(STDERR, "--help should be the only parameter\n");
                    exit(ERR_PARAM);
                }
                $this->getSomeHelp();
            }
            
            if (count(getopt("", $statsOptions)) == 0)                                      // if any of --stats options were used
                return;

            $arguments = array_slice($argv, 1);                                             // cut the first argument (parse.php)
            $tmpArray = array();
            $statsIsPresent = false;
            for ($i = 0; $i < count($arguments); $i++) {
                
                if (preg_match(statsPattern, $arguments[$i])) {                             // if --stats is present
                    if ($statsIsPresent) {
                        $this->stats->addToGroups($tmpArray);
                    }
                    $tmpArray = array();                                                    // stats for each stats group in $statsGroups
                    $statsIsPresent = true;                                                 // files for each stats group in $statsFiles
                    $this->stats->addToFiles($arguments[$i]);
                }

                else if ((!strcmp($arguments[$i], "--loc")                                  // if any other valid parameter 
                || !strcmp($arguments[$i], "--comments") || !strcmp($arguments[$i], "--labels") 
                || !strcmp($arguments[$i], "--jumps") || !strcmp($arguments[$i], "--fwjumps") 
                || !strcmp($arguments[$i], "--backjumps") || !strcmp($arguments[$i], "--badjumps")) && $statsIsPresent == true) {
                    array_push($tmpArray, substr($arguments[$i], 2));                       // push parameter w/o --
                }

                else {                                                                      // no --stats before params or any unrecognized parameter
                    exit(ERR_PARAM);
                }

            }
            $this->stats->addToGroups($tmpArray);
        }

        /**
         * Prints help text to standard output
         */
        private function getSomeHelp() {
            fputs(STDOUT, "Filter type script (parse.php in PHP 8.1) loads IPPcode22 source code from standard input,\n");
            fputs(STDOUT, "controls its lexical and syntax correctness and writes XML representation of program to standard output.\n");
            fputs(STDOUT, "Possible parameters:\n");
            fputs(STDOUT, "\t--help - don't use with other parameters\n");
            fputs(STDOUT, "\t--stats=file - will write input code stats to the *file* directiory (use only with some of the following parameters)\n");
            fputs(STDOUT, "\t--loc - number of lines with instructions\n");
            fputs(STDOUT, "\t--comments - number of lines with comments\n");
            fputs(STDOUT, "\t--labels - number of labels\n");
            fputs(STDOUT, "\t--jumps - number of jumps\n");
            fputs(STDOUT, "\t--fwjumps - number of forward jumps\n");
            fputs(STDOUT, "\t--backjumps - number of backward jumps\n");
            fputs(STDOUT, "\t--badjumps - number of jumps to non-existent labels\n");
            exit(SCAN_OK);
        }

        private $code = array();                                                            // array of Instructions
        private $currentLine = 1;                                                           // current line of code

        /**
         * Parses input code, fills $code array with Instructions
         */
        public function parseCode() {
            $headerIsPresent = false;
            while ($line = fgets(STDIN)) {
                // remove all comments and trim
                $line = trim(preg_replace(commentPattern, "", $line, count: $count));
                if ($count > 0)
                    $this->stats->incComments();
                // empty line
                if (strlen($line) == 0) 
                    continue;
                // header is missing or is written twice
                if (($headerIsPresent && preg_match(headerPattern, $line)) || (!$headerIsPresent && !preg_match(headerPattern, $line))) 
                    exit(ERR_HEADER);
                elseif (!$headerIsPresent) {
                    $headerIsPresent = true;
                    continue;
                }
                
                $instruction = new Instruction($line, $this->currentLine);
                $this->addInst($instruction);
            }
        }
        
        /**
         * Adds Instruction to $code array, increments line counter
         * 
         * @param instruction Instruction object
         */
        private function addInst($instruction) {
            array_push($this->code, $instruction);
            $this->currentLine++;
        }
        
        /**
         * Counts labels, all types of jumps according to $code array
         */
        public function makeupStats() {
            $this->stats->setInstructions($this->currentLine);
            foreach ($this->code as $instruction) {
                if (preg_match(jumpPattern, $instruction->getOpCode())) 
                    $this->stats->addJump($instruction->getArg(0));
                
                elseif ($instruction->getOpCode() == "LABEL") 
                    $this->stats->addLabel($instruction->getArg(0));
                
            }
            $this->stats->setJumpsAndLabels();
        }

        /**
         * Creates all Instruction elements based on $code array
         * 
         * @param DOMdocument $xml XML document
         * @param DOMElement $program root element of DOMdocument
         */
        public function convertToXML(DOMdocument $xml, DOMElement $program) {
            foreach($this->code as $instruction)
                $instruction->makeXMLInstruction($xml, $program);
        }

    }

?>