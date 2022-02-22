<?php

/**
 * Subject: IPP - Principles of Programming Languages
 * @author Maksim Tikhonov (xtikho00)
 * 
 * File contains implementation of Stats class
 */

    include 'sets.php';

    class Stats {

        private static $connection;

        private $groups = array();

        private $loc = 0;                           // --loc
        private $comments = 0;                      // --comments
        private $labels = 0;                        // --labels
        private $jumps = 0;                         // --jumps
        private $fwjumps = 0;                       // --fwjumps
        private $backjumps = 0;                     // --backjumps
        private $badjumps = 0;                      // --badjumps
        
        private $labelIds = array();
        private $jumpDestinations = array();
        
        /**
         * Makes Stats class a singleton
         */
        public static function Connect() {
            if (!isset(self::$connection))
                self::$connection = new Stats;
            return self::$connection;
        }

        /**
         * Pushes array to stats groups array
         * 
         * @param array $group new stats group
         */
        public function addToGroups($group) {
            $this->groups[key($group)] = $group[key($group)];
        }

        public function setInstructions($count) {
            $this->loc = $count - 1;
        }

        public function incComments() {
            $this->comments++;
        }

        public function addLabel($label) {
            if (array_search($label, $this->labelIds)) 
                exit(ERR_SYNTAX);
            array_push($this->labelIds, $label);
        }

        // special case for RETURN instruction; other jumps are handled by addJump method
        public function incJumps() {
            $this->jumps++;
        }

        public function addJump($label) {
            array_push($this->jumpDestinations, $label);
            if (array_search($label, $this->labelIds))
                $this->backjumps++;
        }

        public function setJumpsAndLabels() {
            $returnCnt = $this->jumps; 
            $this->jumps += count($this->jumpDestinations);
            $this->labels = count($this->labelIds);
            foreach ($this->jumpDestinations as $jump) {
                if (!array_search($jump, $this->labelIds)) 
                    $this->badjumps++;
            }
            $this->fwjumps = $this->jumps - $this->badjumps - $this->backjumps - $returnCnt;
        }

        /**
         * Prints all stats groups to corresponding files
         */
        public function writeStats() {
            // check if there are duplicates in files array
            if (count(array_keys($this->groups)) != count(array_unique(array_keys($this->groups))))
                exit(ERR_OUTPUT);

            foreach ($this->groups as $file => $group) {
                $outFile = fopen($file, "w");
                $statsText = "";
                foreach ($group as $option) {
                    $statsText .= $this->{$option}."\n";
                }
                if (!fwrite($outFile, $statsText))
                    exit(ERR_OUTPUT);
                fclose($outFile);
            }
        }

    }

?>