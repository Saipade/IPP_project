<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * Part: Parser
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains implementation of Parser class
 */

    include 'sets.php';
    /**
     * Parser class, parses args and input, converts it to XML
     */
    class Parser {

        private $code = array();                                                            // array of Instructions
        private $currentLine = 1;                                                           // current line of code
        public $stats;                                                                      // Stats class object
        private $instFactory;                                                               // CodeFactory class object, is required for instruction construction

        public function __construct() {
            $this->stats = Stats::connect();
            $this->instFactory = CodeFactory::connect();
        }

        /**
         * Parses input arguments
         * 
         * @param int $argc number of input arguments
         * @param array $argv array of input arguments
         */
        public function parseArgs() {
            global $argc, $argv, $statsOptions;
            $options = getopt("", ["help"]);                                                // if --help is present
            if (array_key_exists("help", $options)) {
                if ($argc > 2)
                    exit(ERR_PARAM);
                $this->getSomeHelp();
            }
            
            if (count(getopt("", $statsOptions)) == 0)                                      // if any of --stats options were used
                return;
            
            $arguments = array_slice($argv, 1);                                             // cut the first argument (parse.php)
            $tmpArray = array();
            $currentKey = "";
            $statsIsPresent = false;
            foreach ($arguments as $argument) {
                if (preg_match(statsPattern, $argument)) {                                  // if --stats is present
                    if ($statsIsPresent)
                        $this->stats->addToGroups($tmpArray);
                    $currentKey = substr($argument, 8);
                    $tmpArray = array($currentKey => []);                                   // create empty array with filename key
                    $statsIsPresent = true;
                }
                
                elseif (preg_match(statsOptPattern, $argument) && $statsIsPresent == true) {
                    array_push($tmpArray[$currentKey], substr($argument, 2));               // push stats option w/o --
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
            echo "Filter type script (parse.php in PHP 8.1) loads IPPcode22 source code from standard input,\n";
            echo "controls its lexical and syntax correctness and writes XML representation of program to standard output.\n";
            echo "Possible parameters:\n";
            echo "\t--help - don't use with other parameters\n";
            echo "\t--stats=file - will write input code stats to the *file* directiory (use only with some of the following parameters)\n";
            echo "\t--loc - number of lines with instructions\n";
            echo "\t--comments - number of lines with comments\n";
            echo "\t--labels - number of labels\n";
            echo "\t--jumps - number of jumps\n";
            echo "\t--fwjumps - number of forward jumps\n";
            echo "\t--backjumps - number of backward jumps\n";
            echo "\t--badjumps - number of jumps to non-existent labels\n";
            exit(SCAN_OK);
        }

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
                if (($headerIsPresent && preg_match(headerPattern, $line)) || (!$headerIsPresent && !preg_match(headerPattern, $line))) {
                    exit(ERR_HEADER);
                }
                elseif (!$headerIsPresent) {
                    $headerIsPresent = true;
                    continue;
                }
                
                $instruction = $this->instFactory->createInstruction($line, $this->currentLine);
                $this->addInst($instruction);
            }
        }
        
        /**
         * Adds Instruction to $code array, increments line counter
         * 
         * @param Instruction $instruction Instruction object
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

                elseif (!strcmp("RETURN", $instruction->getOpCode()))
                    $this->stats->incJumps();
                                
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