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
            $this->parseScript = "./parse.php";
            $this->intScript = "./interpret.py";
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
                    if (!is_file($file) or !is_readable($file))
                        exit(ERR_INPUT);    
                    $this->parseScript = $file;
                }
                elseif (!strcmp($argument, 'int-script')) {
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
            if ($this->recursive)
                $this->directories = $this->locateDirectories($this->directory);
        }

        /**
         * Recursive search function for --recursive case
         */
        private function locateDirectories($directory) {
            $tmp = [];
            foreach (glob("{$directory}"."/*", GLOB_ONLYDIR) as $dir) {
                $tmp = array_merge($this->locateDirectories($dir), $tmp);
                array_push($tmp, $dir);
            }
            return $tmp;     
        }

        /**
         * Locates all files in given directories, converts $this->directories to assiciative array of shape "dir_path => 
         */
        private function locateFiles() {
            foreach ($this->directories as $index => $dir) {
                $this->directories[$dir] = glob("{$dir}/*.src");
                unset($this->directories[$index]);
            }
            // remove path to file and .src at the end
            foreach ($this->directories as $key => $array) {
                foreach ($array as $id => $testFile) {
                    $match = "";
                    preg_match("/[a-zA-Z0-9,_@]+\.src$/", $testFile, $match);
                    $match = substr($match[0], 0, -4);
                    $this->directories[$key][$id] = $match;
                }
            }
        }

        public function test() {
            if ($this->noclean and !file_exists("noclean-output"))
                mkdir("noclean-output/");
            else {
                $file = "temp.tmp";
            }
            foreach ($this->directories as $key => $array) {
                foreach ($array as $index => $fileName) {
                    // Get test files' content
                    // array key + file name = path to file
                    $testName = $key . "/" . $fileName;
                    if ($this->noclean) {
                        $file = "noclean-output/" . substr(preg_replace("/\//", "-", $testName), 2) . ".tmp";
                    }
                    // .out file's content
                    $expOutput = file_get_contents("$testName.out");    
                    // .rc file's content
                    $expError = file_get_contents("$testName.rc");      
                    
                    // Execute scripts on tests
                    if ($this->parseOnly) { // --parse-only
                        exec("php \"$this->parseScript\" < \"$testName\".src > \"$file\"", $output, $error);
                    }

                    elseif ($this->intOnly) { // --int-only
                        exec("python3 \"$this->intScript\" --source=\"$testName\".src --input=\"$testName\".in > \"$file\"", $output, $error);
                    }

                    else { // both  
                        exec("php8.1 \"$this->parseScript\" < \"$testName\".src > \"$file\"", $output, $error);
                        $output = implode("\n", $output);
                        if ($error != 0) { // parsing error occured
                            array_push($this->testResults, new TestResult($expOutput, $output, intval($expError), $error, "failed"));
                            $this->testsFailedCounter++;
                            continue;
                        }
                        $file1 = "noclean-output/" . preg_replace("/\//", "-", $testName) . "-int.tmp";
                        exec("python3.8 \"$this->intScript\" --source=\"$file\" --input=\"$testName\".in > \"$file1\"", $output, $error);
                    }
                    
                    // Create test result and push it to array
                    $output = implode("\n", $output);
                    $result = new TestResult($expOutput, $output, intval($expError), $error);
                    if ($this->parseOnly) {
                        $result->compare($this->jexampath, $file, "{$testName}.out", modes::PARSE);
                    }

                    else {
                        $result->compare($this->jexampath, $file, "{$testName}.out", modes::OTHER);
                    }

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
                $title = "Only interpreter is being tested";
            elseif ($this->parseOnly)
                $title = "Only parser is being tested";
            else 
                $title = "Both interpreter and parser are being tested";
            $this->resultHTML .= '<!DOCTYPE html>
<html lang="en">
<head>
&#9<meta charset="utf-8">
&#9<title>Test results</title>
&#9<link rel="stylesheet" href="css/style.css">
</head>
<body>
&#9<header id="header">
&#9&#9<div class="content">
&#9&#9<h1>' . date("h:i - d.m.Y") . '</h1>
&#9&#9<h1>Success rate: ' . round($this->testsPassedCounter/($this->testsFailedCounter+$this->testsPassedCounter)*100) . '%</h1>
&#9&#9<h1>' . $title . '</h1>
&#9&#9<h1>' . $this->testsPassedCounter . '/' . $this->testsFailedCounter + $this->testsPassedCounter . ' tests passed</h1>
&#9&#9</div>
&#9</header>
';
        }

        private function addHTMLBody() {
            $this->resultHTML .= '<main>
<section id="results">
<div class="content">';
            $counter = 1;
            foreach ($this->testResults as $testResult) {
                $this->resultHTML .= $testResult->getHTMLBlock($counter);
                $counter++;
            }
            $this->resultHTML .= '</div>
</section>
</main>
<footer id="footer">
<div class="content">
<span>This script was written by <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley">Maksim Tikhonov</a></span>
</div>
</footer&>
</body>
</html>
';
        }

        public function printHTML() {
            echo $this->resultHTML;
        }

    }

?>