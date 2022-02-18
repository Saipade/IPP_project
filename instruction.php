<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains implementation of Insruction class
 */

    include 'regex.php';
    include 'sets.php';
    include 'argument.php';

    /**
     * Represents any meaningful line of code
     */
    class Instruction {

        private $opCode;                            // operation code attribute
        private $arguments = array();               // arguments as strings from input line
        private $argumentsA = array();              // arguments as objects (transformed from string form)
        private $order;                             // order attribute
        private $argFactory;                        // object for argument creation

        public function __construct($line, $lineNumber) {
            $this->argFactory = new ArgumentFactory();
            $explodedLine = explode(" ", $line);
            $this->opCode = strtoupper($explodedLine[0]);
            $this->arguments = array_slice($explodedLine, 1);
            $this->order = $lineNumber;
            $this->checkOpCode();
            $this->createArgs();
        }

        /**
         * Checks if given operation code is valid (is present in instruction set)
         */
        private function checkOpCode() {
            global $instructionSet;
            if (!array_key_exists(strtoupper($this->opCode), $instructionSet)){
                exit(ERR_OPCODE);
            }
        }

        /**
         * Checks if number of input arguments is corresponding to exprected number;
         * then creates objects of Argument's subclasses corresponding to instruction's ones
         */
        private function createArgs() {
            global $instructionSet;
            if (count($instructionSet[$this->opCode]) != count($this->arguments)) 
                exit(ERR_SYNTAX);

            foreach ($instructionSet[$this->opCode] as $index => $argumentType) {
                // see instructionSet array; creates objects of arguments according to given operation code and fills $argumentsA array
                // e.g. for 'JUMPIFNEQ' operation code 3 objects will be created -- of Label, Symbol and Symbol classes
                $this->argumentsA[$index] = $this->argFactory->createArgument($argumentType, $this->arguments[$index]);
            }    
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
            for ($i = 0; $i < count($this->arguments); $i++) {
                $argXML = $xml->createElement("arg".$i+1, $this->argumentsA[$i]->getValue());
                $argXML->setAttribute('type', $this->argumentsA[$i]->getType());
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