<?php

    /**
     * Subject: IPP - Principles of Programming Languages
     * Part: Tester
     * @author Maksim Tikhonov (xtikho00)
     * 
     * File contains implementation of TestResult class
     */
    
    interface modes {
        const PARSE = true;
        const OTHER = false;
    }
    
    class TestResult {

        private $testPath;

        private $testExpOut;            // .out
        private $testExpErr;            // .rc        
        private $testErr;               // error code result
        private $testOut;               // output result

        private $verdict;               // evaluation of test

        /**
         * @param string $expOut reference output
         * @param string $out given output
         * @param int $expErr reference error
         * @param int $err given error
         * 
         */
        public function __construct($expOut="", $out="", $expErr=0, $err=0, $verdict='passed') {
            $this->testExpOut = $expOut;
            $this->testOut = $out;
            $this->testExpErr = $expErr;
            $this->testErr = $err;
            $this->verdict = $verdict;
        }
        
        /**
         * Does testing depending on $mode
         * @param string $jexamPath path to A7Soft JExamXML file
         * @param string $file path to temporary file (or not temporary)
         * @param string $outputFile path to reference output
         * @param bool $mode mode (true - parse-only, false - not). see modes interface
         * 
         */
        public function compare($jexamlPath, $file, $outputFile, $mode) {
            $this->testPath = substr($outputFile, 0, -4);
            $this->testOut = file_get_contents($file);
            /* Compare return codes and outputs, return either 'passed' or 'failed' */
            if (empty($this->testOut) and empty($this->testExpOut)) {
                if ($this->testExpErr == $this->testErr)
                    $this->verdict = 'passed';
                else 
                    $this->verdict = 'failed';
                return;
            }
            if (intval($this->testExpErr) == $this->testErr) {
                if (empty($this->testOut) and empty($this->testExpOut)) {
                    $this->verdict = 'passed';
                }
                else {
                    switch ($mode) {
                        case modes::PARSE: // parse-only
                            $jexam = $jexamlPath . '/jexamxml.jar';
                            exec("java -jar \"$jexam\" \"$file\" \"$outputFile\"", $diff, $error);
                        break;
                        case modes::OTHER:
                            exec("diff \"$file\" \"$outputFile\" 2>/dev/null", $diff, $error);
                            $diff = implode("\n", $diff);
                            $error = empty($diff);
                        break;
                    }
                    if ($error) 
                        $this->verdict = 'passed';
                    else 
                        $this->verdict = 'failed';
                }
            }
            else {
                $this->verdict = 'failed';
            }
        }

        public function getHTMLBlock($counter) {
            return '<div class="result">
<div>
<div class="info">
<h1>' . $counter . '</h1>
<p>...' . $this->testPath . '</p>
<div class="tooltip">Output
<pre class="tooltiptext">' . $this->testOut . '</pre>
</div>
<div class="tooltip">Expected output
<pre class="tooltiptext">' . $this->testExpOut . '</pre>
</div>
<p>Error code: ' . $this->testErr . '</p>
<p>Expected error code: ' . $this->testExpErr . '</p>
</div>
</div>
<div>
<h1 class="' . $this->verdict . '">' . ucfirst($this->verdict) . '</h1>
</div>
</div>
';
        } 

        public function getResult() {
            return $this->verdict;
        }

    }

?>