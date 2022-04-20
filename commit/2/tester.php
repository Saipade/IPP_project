<?php

    /**
     * Subject: IPP - Principles of Programming Languages
     * Part: Tester
     * @author Maksim Tikhonov (xtikho00)
     * 
     * File contains implementation of Tester class
     */

    include 'sets.php';
    include 'errorslist.php';
    include 'testresult.php';

    /**
     * Tester class, parses command line arguments and tests 
     */
    class Tester {
        
        private $directory;                     // tests directory
        private $recursive;                     // recursive flag
        private $parseScript;                   // parser script file
        private $intScript;                     // interpreter script file
        private $parseOnly;                     // parse-only flag
        private $intOnly;                       // int-only flag
        private $jexampath;                     // jaxampath directory
        private $noclean;                       // noclean flag

        private $testsPassedCounter;
        private $testsFailedCounter;

        private $directories;                   // all directories tests are in

        private $resultHTML;

        private $testResults;                   // array of TestResult objects

        public function __construct() {
            $this->directory = ".";
            $this->recursive = false;
            $this->parseScript = ".";
            $this->intScript = ".";
            $this->parseOnly = false;
            $this->intOnly = false;
            $this->jexampath = "/pub/courses/ipp/jexamxml/";
            $this->noclean = false;

            $this->testsPassedCounter = 0;
            $this->testsFailedCounter = 0;

            $this->directories = [];
            
            $this->resultHTML = "";

            $this->testResults = [];
        }

        public function parseArguments() {
            global $argc;
            $arguments = getopt("", options);
            if ($argc != count($arguments)+1)
                exit(ERR_PARAM);
            foreach ($arguments as $argument => $file) {
                if (!strcmp($argument, 'help')) {
                    if ($argc != 2)
                        exit(ERR_PARAM);
                    echo help;
                    exit(TEST_OK);
                }
                elseif (!strcmp($argument, 'directory')) {
                    if ($this->directory != '.')
                        exit(ERR_PARAM);
                    if (!is_dir($file) or !is_readable($file))
                        exit(ERR_INPUT);
                    $this->directory = $file;
                    array_push($this->directories, $file);
                }
                elseif (!strcmp($argument, 'recursive')) {
                    if ($this->recursive == true)
                        exit(ERR_PARAM);
                    $this->recursive = true;
                }
                elseif (!strcmp($argument, 'parse-script')) {
                    if ($this->parseScript != '.') 
                        exit(ERR_PARAM);
                    if (!is_file($file) or !is_readable($file))
                        exit(ERR_INPUT);    
                    $this->parseScript = $file;
                }
                elseif (!strcmp($argument, 'int-script')) {
                    if ($this->intScript != '.')
                        exit(ERR_PARAM);
                    if (!is_file($file) or !is_readable($file))
                        exit(ERR_INPUT);    
                    $this->intScript = $file;
                }
                elseif (!strcmp($argument, 'parse-only')) {
                    if ($this->parseOnly == true) 
                        exit(ERR_PARAM);
                    $this->parseOnly = true;
                }
                elseif (!strcmp($argument, 'int-only')) {
                    if ($this->intOnly == true)
                        exit(ERR_PARAM);
                    $this->intOnly = true;
                }
                elseif (!strcmp($argument, 'jexampath')) {
                    if ($this->jexampath != "/pub/courses/ipp/jexamxml/")
                        exit(ERR_PARAM);
                    if (!is_dir($file) or !is_readable($file))
                        exit(ERR_INPUT);
                    $this->jexampath = $file;
                }
                elseif (!strcmp($argument, 'noclean')) {
                    if ($this->noclean == true)
                        exit(ERR_PARAM);
                    $this->noclean = true;
                }
            }
            $this->checkArguments($arguments);
            if ($this->recursive)
                $this->directories = $this->locateDirectories($this->directory);
            $this->locateFiles();

        }

        /**
         * Checks all arguments for consistency
         */
        private function checkArguments($arguments) {
            if ($this->parseOnly and 
            (array_key_exists("int-only", $arguments) or array_key_exists("int-script", $arguments)))
                exit(ERR_PARAM);
            if ($this->intOnly and 
            (array_key_exists("parse-only", $arguments) or array_key_exists("parse-script", $arguments) or array_key_exists("jexampath", $arguments)))
                exit(ERR_PARAM);
        }

        /**
         * Recursive search function for --recursive case
         */
        private function locateDirectories($directory) {
            $array = glob("{$directory}/*", GLOB_ONLYDIR);
            foreach ($array as $key => $directory) 
                $array[$key] = preg_replace("/\/\//", "/", $directory);
            return $array;
        }

        /**
         * Locates all files in given directories
         */
        private function locateFiles() {

            foreach ($this->directories as $index => $dir) {
                $this->directories[$dir] = glob("{$dir}/*.src");
                unset($this->directories[$index]);
            }
            // remove path to file and .src at the end
            foreach ($this->directories as $key => $array) {
                if (count($array) == 0) {
                    unset($this->directories[$key]);
                    continue;
                }
                foreach ($array as $id => $testFile) {
                    $match = "";
                    preg_match("/[a-zA-Z0-9,_@]+\.src$/", $testFile, $match);
                    $match = substr($match[0], 0, -4);
                    $this->directories[$key][$id] = $match;
                }
            }
        }

        public function test() {
            /* Create output directory (noclean option) or create temporary file */
            foreach ($this->directories as $key => $array) {
                foreach ($array as $index => $fileName) {
                    var_dump($key. '/' . $fileName);
                }
            }
            if ($this->noclean and !file_exists("output"))
                mkdir("output");
            else             
                $file = tempnam("output", "sorrow");
            foreach ($this->directories as $key => $array) {
                foreach ($array as $index => $fileName) {
                    /* Get test files" content */
                    if ($this->noclean) {
                        $file = fopen("output/" . preg_replace("/\//", "-", $key) . "-" . $fileName . ".out", "w+");
                    }
                    $testName = $key . "/" . $fileName;
                    if (file_exists("{$testName}.out"))
                        $refOut = file_get_contents("{$testName}.out");  // .out file"s content
                    else 
                        $refOut = "";
                    if (file_exists("{$testName}.rc"))
                        $refErr = file_get_contents("{$testName}.rc");   // .rc file"s content
                    else
                        $refErr = 0;
                    /* Execute scripts on tests */
                    if ($this->parseOnly) { // --parse-only
                        var_dump("php {$this->parseScript} < {$testName}.src > {$file}");
                        exec("php8.1 {$this->parseScript} < {$testName}.src > {$file}", $output, $error);
                    }
                    elseif ($this->intOnly) { // --int-only
                        exec("python3 {$this->intScript} --source={$testName}.src --input={$testName}.in > {$file}", $output, $error);
                    } 
                    else { // both
                        exec("php {$this->parseScript} < {$testName}.src > {$file}", $output, $error);
                        if ($error != 0) { // parsing error occured
                            array_push($this->testResults, new TestResult($refOut, $output, $refErr, $error, "failed"));
                            $this->testsFailedCounter++;
                            continue;
                        }
                        $file = fopen("output/" . preg_replace("/\//", "-", $key) . "-" . $fileName . "-int.out", "w+");
                        exec("python3 {$this->intScript} --source={$file} --input={$testName}.in > {$file}", $output, $error);
                    }
                    /* Create test result and push it to array */
                    $result = new TestResult($refOut, $output, $refErr, $error);
                    if ($this->parseOnly)
                        $result->compare($this->jexampath, $file, "{$testName}.out", modes::PARSE);
                    else
                        $result->compare($this->jexampath, $file, "{$testName}.out", modes::OTHER);
                    if ($result->getResult() == "passed")
                        $this->testsPassedCounter++;
                    else 
                        $this->testsFailedCounter++;
                    array_push($this->testResults, $result);
                }
            }
            unlink($file);
        }

        public function constructHTML() {
            $this->addHTMLHeader();
            $this->addHTMLBody();
        }

        private function addHTMLHeader() {
            $title = "";
            if ($this->intOnly)
                $title = "Only interpreter are being tested";
            elseif ($this->parseOnly)
                $title = "Only parser are being tested";
            else 
                $title = "Both interpreter and parser are being tested";
            $this->resultHTML .= '&lt!DOCTYPE html&gt
&lthtml lang="en"&gt
&lthead&gt
&ltmeta charset="utf-8"&gt
&lttitle&gtTest results&lt/title&gt
&ltlink rel="stylesheet" href="css/style.css"&gt
&lt/head&gt
&ltbody&gt
&ltheader id="header"&gt
&ltdiv class="content"&gt
&lth1&gt' . date("h:i - d.m.Y") . '&lt/h1&gt
&lth1&gtSuccess rate: ' . round($this->testsPassedCounter%($this->testsFailedCounter+$this->testsPassedCounter)*100) . '%&lt/h1&gt
&lth1&gt' . $title . '&lt/h1&gt
&lth1&gt' . $this->testsPassedCounter . '/' . $this->testsFailedCounter + $this->testsPassedCounter . ' tests passed&lt/h1&gt
&lt/div&gt
&lt/header&gt
';
        }

        private function addHTMLBody() {
            $this->resultHTML .= '&ltmain&gt
&ltsection id="results"&gt
&ltdiv class="content"&gt';
            $counter = 1;
            foreach ($this->testResults as $testResult) {
                $this->resultHTML .= $testResult->getHTMLBlock($counter);
                $counter++;
            }
            $this->resultHTML .= '&lt/div&gt
&lt/section&gt
&lt/main&gt
&ltfooter id="footer"&gt
&ltdiv class="content"&gt
&ltspan&gtThis script was written by &lta href="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley"&gtMaksim Tikhonov&lt/a&gt&lt/span&gt
&lt/div&gt
&lt/footer&gt
&lt/body&gt
&lt/html&gt
';
        }

    }

?>