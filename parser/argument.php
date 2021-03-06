<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * Part: Parser
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains implementations of Argument abstract class, all subclasses of it 
 * and implementation of Factory method class designed for argument construction
 */

    /**
     * Abstract class for all nonterminal symbols used as intructions' arguments
     */
    abstract class Argument {

        protected $type;                            // type attribute
        protected $value;                           // string value

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
                    $this->value = $id[0] . "@" . $id[1];
                    return;
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
                    global $stringReplacements;
                    $this->type = "string";
                    $id[1] = strtr($id[1], $stringReplacements);            // replace bad characters with XML escape sequence (see sets.php)
                    break;

                default:
                    exit(ERR_SYNTAX);
            }
            $this->value = $id[1];
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
            if (!preg_match(typePattern, $id)) 
                exit(ERR_SYNTAX);
            $this->type = "type";
            $this->value = $id;
        }

    }

?>