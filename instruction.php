<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains classes for code representation
 */

    include 'regex.php';
    include 'sets.php';

    /**
     * Represents every meaningful line of code
     */
    class Instruction {

        private $opCode;                            // operation code attribute
        private $arguments = array();               // arguments (string -> Argument's subclasses)
        private $argumentsA = array();              //
        private $order;                             // order attribute

        public function __construct($line, $lineNumber) {
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
                // see instructionSet array; creates objects of arguments according to given operation code and refills $arguments array
                // e.g. for 'JUMPIFNEQ' operation code 3 objects will be created -- of Label, Symbol and Symbol classes
                $this->argumentsA[$index] = new $argumentType($this->arguments[$index]);
            }    
        }

        /**
         * Generates XML representation of Instruction
         * 
         * @param DOMdocument $xml DOMdocument
         * @param DOMElement $program root element of DOMdocument
         */
        public function makeXMLInstruction(DOMdocument $xml, DOMElement $program) {
            $instructionXML = $xml->createElement('Instruction');
            $instructionXML->setAttribute('order', $this->order);
            $instructionXML->setAttribute('opcode', $this->opCode);
            for ($i = 0; $i < count($this->arguments); $i++) {
                $argXML = $xml->createElement("arg".$i+1, $this->argumentsA[$i]->getValue());
                $argXML->setAttribute('type', $this->argumentsA[$i]->getType());
                $instructionXML->appendChild($argXML);
            }
            $program->appendChild($instructionXML);
        }
        
    }

    /**
     * Abstract class for all nonterminal symbols used as intructions' arguments
     */
    abstract class Argument {

        private $type;                            // type attribute
        private $value;                           // string value

        abstract public function __construct($id);

        public function getType() {
            return $this->type;
        }

        public function getValue() {
            return $this->value;
        }
        
    }

    /**
     * Class representing <var> nonterminal
     */
    class Variable extends Argument {

        public function __construct($id) {
            $id = explode("@", $id, 2);
            if (!preg_match(varPattern, $id[1]))
                exit(ERR_SYNTAX);
            $this->type = "var";
            $this->value = $id[0] . "@" . $id[1];
        }

    }

    /**
     * Class representing <symb> nonterminal; can be either constant or variable
     */
    class Symbol extends Argument {

        public function __construct($id) {
            $id = explode("@", $id, 2);
            switch ($id[0]) {
                // variable
                case "TF":
                case "GF":
                case "LF":
                    if (!preg_match(varPattern, $id[1]))
                        exit(ERR_SYNTAX);
                    $this->type = "var";
                    break;
                // const int
                case "int":
                    if (!preg_match(intPattern, $id[1]))
                        exit(ERR_SYNTAX);
                    $this->type = "int";
                    break;
                // const bool
                case "bool":
                    if (!preg_match(boolPattern, $id[1]))
                        exit(ERR_SYNTAX);
                    $this->type = "bool";
                    break;
                // const nil
                case "nil":
                    if (!preg_match(nilPattern, $id[1]))
                        exit(ERR_SYNTAX);
                    $this->type = "nil";
                    break;
                // const string
                case "string":
                    if (!preg_match(stringPattern, $id[1]))
                        exit(ERR_SYNTAX);
                    $this->type = "string";
                    break;

                default:
                    exit(ERR_SYNTAX);
            }
            $this->value = $id[0] . "@" . $id[1];
        }

    }

    /**
     * Class representing <label> nonterminal
     */
    class Label extends Argument {

        public function __construct($id) {
            if (!preg_match(lablePattern, $id))
                exit(ERR_SYNTAX);
            $this->type = "label";
            $this->value = $id;
        }

    }

    /**
     * Class representing <type> nonterminal -- used only by READ instruction
     */
    class Type extends Argument {

        public function __construct($id) {
            if (!preg_match(typePattern, $id)) {
                echo $id;
                exit(ERR_SYNTAX);
            }
            $this->type = "type";
            $this->value = $id;
        }

    }

?>