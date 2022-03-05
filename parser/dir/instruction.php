<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * Part: Parser
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains implementation of Insruction class
 */

    include 'regex.php';
    include 'sets.php';
    include 'argument.php';
    include 'factory.php';

    /**
     * Represents any meaningful line of code
     */
    class Instruction {

        private $opCode;                                // operation code attribute
        private $arguments = array();                   // arguments as strings from input line
        private $argFactory;                            // factory for instruction's arguments construction
        private $argumentsA = array();                  // arguments as Argument class objects
        private $order;                                 // order attribute

        public function __construct($line, $lineNumber) {
            $explodedLine = explode(" ", $line);
            $this->opCode = strtoupper($explodedLine[0]);
            $this->checkOpCode();
            $this->arguments = array_slice($explodedLine, 1);
            $this->argFactory = CodeFactory::connect();
            $this->createArgs();
            $this->order = $lineNumber;
        }

        /**
         * Checks if given operation code is valid (is present in instruction set)
         */
        private function checkOpCode() {
            global $instructionSet;
            if (!array_key_exists(strtoupper($this->opCode), $instructionSet))
                exit(ERR_OPCODE);
        }

        /**
         * Uses Argument factory class object to construct array of Arguments
         */
        private function createArgs() {
            $this->argumentsA = $this->argFactory->createArguments($this->opCode, $this->arguments);
        }

        /**
         * Generates XML representation of Instruction
         * 
         * @param DOMdocument $xml DOMdocument
         * @param DOMElement $program root element of DOMdocument
         */
        public function makeXMLInstruction(DOMdocument $xml, DOMElement $program) {
            $instructionXML = $xml->createElement('instruction');
            $instructionXML->setAttribute('order', $this->order);
            $instructionXML->setAttribute('opcode', $this->opCode);
            foreach ($this->argumentsA as $index => $argument) {
                $argXML = $xml->createElement("arg".$index+1, $argument->getValue());
                $argXML->setAttribute('type', $argument->getType());
                $instructionXML->appendChild($argXML);
            }
            $program->appendChild($instructionXML);
        }

        public function getOpCode() {
            return $this->opCode;
        }

        public function getArg($index) {
            return $this->arguments[$index];
        }
        
    }

?>