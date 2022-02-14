<?php

    include 'sets.php';

    class Stats {

        private $loc = 0;                           // --loc
        private $comments = 0;                      // --comments
        private $labels = 0;                        // --labels
        private $jumps = 0;                         // --jumps
        private $fwjumps = 0;                       // --fwjumps
        private $backjumps = 0;                     // --backjumps
        private $badjumps = 0;                      // --badjumps
        
        private $labelIds = array();
        private $jumpDestinations = array();

        private $locEnabled = false;                
        private $commentsEnabled = false;
        private $labelsEnabled = false;
        private $jumpsEnabled = false;
        private $fwjumpsEnabled = false;
        private $backjumpsEnabled = false;
        private $badjumpsEnabled = false;
        
        private $groups = array();
        private $files = array();

        public function enParameters() {
            foreach ($this->groups as $group) {
                foreach ($group as $str) {
                    $this->{$str . "Enabled"} = true;
                }
            }
        }

        public function incInstructions() {
            if ($this->locEnabled)
                $this->loc++;
        }

        public function incComments() {
            if ($this->commentsEnabled)
                $this->comments++;
        }

        public function incLabels() {
            if ($this->labelsEnabled)
                $this->labels++;
        }

        public function incFwJumps() {
            if ($this->fwjumpsEnabled) 
                $this->fwjumps++;
        }

        public function incBackJumps() {
            if ($this->backjumpsEnabled)
                $this->backjumps++;
            
            if ($this->jumpsEnabled) 
                $this->jumps++;
        }

        public function incBadJumps() {
            if ($this->badjumpsEnabled)
                $this->badjumps++;

            if ($this->jumpsEnabled) 
                $this->jumps++;
        }
        
        public function addLabel($label) {
            if (array_search($label, $this->labelIds) == true) 
                return;
            array_push($this->labelIds, $label);
        }

        public function addJump($label) {
            array_push($this->jumpDestinations, $label);
            if (array_search($label, $this->labelIds) == true) {
                $this->backjumps++;

            }
        }

        public function addToGroups($group) {
            array_push($this->groups, $group);
        }

        public function addToFiles($argument) {
            array_push($this->files, substr($argument, 8));
        }

        // debugging reasons -- RM later
        public function echoStats() {
            var_dump($this->groups);
            var_dump($this->files);
        }

        public function writeStats() {
            // check if there are duplicates in files array
            if (count($this->files) != count(array_unique($this->files)))
                exit(ERR_OUTPUT);
            
            for ($i = 0; $i < count($this->files); $i++) {
                $file = fopen($this->files[$i], "w");
                $statsText = "";
                for ($j = 0; $j < count($this->groups[$i]); $j++) {
                    $statsText .= $this->{$this->groups[$i][$j]}."\n";
                }
                if (!fwrite($file, $statsText))
                    exit(ERR_OUTPUT);
                fclose($file);
            }
        }

    }

?>