<?php


/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains implementation of CodeFactory class
 */

    /**
     * Factory class for instruction and argument construction
     * Utilizes abstract factory and singleton patterns
     */
    class CodeFactory {

        private static $connection;

        public static function connect() {
            if (!isset(self::$connection))
                self::$connection = new CodeFactory;
            return self::$connection;
        }

        /**
         * Returns array of instruction's arguments
         */
        public function createArguments($opCode, $argumentsStr) : array {
            global $instructionSet;
            $newArguments = array();
            if (count($instructionSet[$opCode]) != count($argumentsStr)) 
                exit(ERR_SYNTAX);
            foreach ($instructionSet[$opCode] as $index => $argumentType) {
                $newArguments[$index] = new $argumentType($argumentsStr[$index]);
            }
            return $newArguments;
        }
        /**
         * Returns new Instruction class object
         */
        public function createInstruction($line, $lineNumber) : Instruction {
            return new Instruction($line, $lineNumber);
        }
    }

?>