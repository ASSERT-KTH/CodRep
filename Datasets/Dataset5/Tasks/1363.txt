private static final boolean[] TEST_RESULTS = new boolean[] {

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package xinclude;

import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.LineNumberReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.io.Reader;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.StringTokenizer;

import org.apache.xerces.parsers.XIncludeParserConfiguration;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.parser.XMLErrorHandler;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLParseException;
import org.apache.xerces.xni.parser.XMLParserConfiguration;

import xni.Writer;

/**
 * Tests for XInclude implementation.
 * Use -f option to see the error message log
 * @author Peter McCracken, IBM
 */
public class Test implements XMLErrorHandler {
    /** Namespaces feature id (http://xml.org/sax/features/namespaces). */
    protected static final String NAMESPACES_FEATURE_ID =
        "http://xml.org/sax/features/namespaces";

    /** Validation feature id (http://xml.org/sax/features/validation). */
    protected static final String VALIDATION_FEATURE_ID =
        "http://xml.org/sax/features/validation";

    /** Schema validation feature id (http://apache.org/xml/features/validation/schema). */
    protected static final String SCHEMA_VALIDATION_FEATURE_ID =
        "http://apache.org/xml/features/validation/schema";

    /** Schema full checking feature id (http://apache.org/xml/features/validation/schema-full-checking). */
    protected static final String SCHEMA_FULL_CHECKING_FEATURE_ID =
        "http://apache.org/xml/features/validation/schema-full-checking";

    /** Property identifier: error handler. */
    protected static final String ERROR_HANDLER =
        "http://apache.org/xml/properties/internal/error-handler";

    // this array contains whether the test number NN (contained in file testNN.xml)
    // is meant to be a pass or fail test
    // true means the test should pass
    private static final int NUM_TESTS = 41;
    private static boolean[] TEST_RESULTS = new boolean[] {
        // one value for each test
        true, true, true, true, true, true, false, true, false, true, // 10
        false, false, false, false, true, true, true, false, true, true, // 20
        true, false, true, false, false, false, true, true, false, true, // 30
        true, false, true, true, true, true, true, true, false, false, // 40
        true, };
    
    private String fOutputDirectory = "tests/xinclude/output";

    public static void main(String[] args) {
        Test tester = new Test();
        boolean testsSpecified = false;
        for (int i = 0; i < args.length; i++) {
            if (args[i].charAt(0) == '-' && args[i].length() > 1) {
                switch (args[i].charAt(1)) {
                    case 'g' :
                        tester.fGenerate = true;
                        if (args.length > i + 1
                            && args[i + 1].charAt(0) != '-') {
                            try {
                                Integer.parseInt(args[i + 1]);
                                // if it parses as an integer, we'll assume it's a test number
                                tester.setLogFile(System.err);
                            }
                            catch (NumberFormatException e) {
                                tester.fOutputDirectory = args[++i];
                            }
                        }
                        break;
                    case 'h' :
                        printUsage();
                        return;
                    case 'f' :
                        if (args.length > i + 1
                            && args[i + 1].charAt(0) != '-') {
                            try {
                                Integer.parseInt(args[i + 1]);
                                // if it parses as an integer, we'll assume it's a test number
                                tester.setLogFile(System.err);
                            }
                            catch (NumberFormatException e) {
                                // if it doesn't parse as an integer,
                                // we assume it's the log file name
                                try {
                                    tester.setLogFile(
                                        new PrintStream(
                                            new FileOutputStream(args[++i])));
                                }
                                catch (IOException ioe) {
                                    System.err.println(
                                        "Couldn't open log file: " + args[i]);
                                }
                            }
                        }
                        else {
                            tester.setLogFile(System.err);
                        }
                        break;
                    default :
                        System.err.println("Unrecognized option: " + args[i]);
                }
            }
            else {
                testsSpecified = true;
                tester.addTest(Integer.parseInt(args[i]));
            }
        }

        if (!testsSpecified) {
            for (int i = 1; i <= NUM_TESTS; i++) {
                tester.addTest(i);
            }
        }
        
        // Create output directory if it does not already exist.
        if (tester.fGenerate) {
            File outputDir = new File(tester.fOutputDirectory);
            if (!outputDir.exists()) {
                outputDir.mkdirs();
            }
        }
        tester.runTests();
    }

    private final PrintStream DEFAULT_LOG_STREAM =
        new PrintStream(new OutputStream() {
        public void write(int b) throws IOException {
        }
    });

    private Writer fWriter;
    private String fResults;
    private PrintWriter fOutputWriter;
    private int[] fTests = new int[NUM_TESTS];
    private int fNumTests = 0;
    public boolean fGenerate;
    public PrintStream fLogStream;

    public Test() throws XNIException {
        XMLParserConfiguration parserConfig = new XIncludeParserConfiguration();
        parserConfig.setFeature(NAMESPACES_FEATURE_ID, true);
        parserConfig.setFeature(SCHEMA_VALIDATION_FEATURE_ID, true);
        parserConfig.setFeature(SCHEMA_FULL_CHECKING_FEATURE_ID, true);
        fWriter = new Writer(parserConfig);

        // this has to be done AFTER fWriter is created
        parserConfig.setProperty(ERROR_HANDLER, this);

        fGenerate = false;

        // squelch output by default
        fLogStream = DEFAULT_LOG_STREAM;
    }

    public void addTest(int t) {
        fTests[fNumTests++] = t;
    }

    public void setLogFile(PrintStream stream) {
        fLogStream = stream;
    }

    public void runTests() {
        int totalFailures = 0;

        for (int i = 0; i < fNumTests; i++) {
            if (!runTest(fTests[i])) {
                totalFailures++;
            }
        }

        if (fLogStream != null && fLogStream != System.err) {
            fLogStream.close();
        }

        if (totalFailures == 0) {
            System.out.println("All XInclude Tests Passed");
        }
        else {
            System.err.println(
                "Total failures for XInclude: "
                    + totalFailures
                    + "/"
                    + fNumTests);
            printDetailsMessage();
            System.exit(1);
        }
    }

    private static final String XML_EXTENSION = ".xml";
    private static final String TXT_EXTENSION = ".txt";

    private boolean runTest(int testnum) {
        String testname = "tests/xinclude/tests/test";
        String outputFilename = fOutputDirectory + "/test";
        String expectedOutputFilename = "tests/xinclude/output/test";
        if (testnum < 10) {
            testname += "0" + testnum;
            outputFilename += "0" + testnum;
            expectedOutputFilename += "0" + testnum;
        }
        else {
            testname += testnum;
            outputFilename += testnum;
            expectedOutputFilename += testnum;
        }
        testname += XML_EXTENSION;
        // we output to an .xml file if we expect success,
        // or a .txt file if we expect failure
        if (TEST_RESULTS[testnum - 1]) {
            outputFilename += XML_EXTENSION;
            expectedOutputFilename += XML_EXTENSION;
        }
        else {
            outputFilename += TXT_EXTENSION;
            expectedOutputFilename += TXT_EXTENSION;
        }

        boolean passed = true;
        StringBuffer buffer = null;
        try {
            fLogStream.println("TEST: " + testname);
            java.io.Writer myWriter = new StringWriter();
            buffer = ((StringWriter)myWriter).getBuffer();
            fOutputWriter = new PrintWriter(myWriter);
            fWriter.setOutput(myWriter);
            fWriter.parse(new XMLInputSource(null, testname, null));
        }
        catch (XNIException e) {
            passed = false;
        }
        catch (IOException e) {
            fLogStream.println("Unexpected IO problem: " + e);
            fLogStream.println("Result: FAIL");
            return false;
        }

        fResults = stripUserDir(buffer);
        return processTestResults(
            passed,
            TEST_RESULTS[testnum - 1],
            outputFilename,
            expectedOutputFilename);
    }

    private boolean processTestResults(
        boolean passed,
        boolean expectedPass,
        String outputFilename,
        String expectedOutputFile) {
        if (fGenerate) {
            try {
                fLogStream.println("Generated: " + outputFilename);
                PrintWriter outputFile =
                    new PrintWriter(new FileWriter(outputFilename));
                outputFile.print(fResults);
                outputFile.close();
            }
            catch (IOException e) {
                fLogStream.println(
                    "IOException generating results: " + e.getMessage());
                return false;
            }
            return true;
        }

        try {
            if (passed == expectedPass) {
                if (compareOutput(new FileReader(expectedOutputFile),
                    new StringReader(fResults))) {
                    fLogStream.println("Result: PASS");
                    return true;
                }
                else {
                    fLogStream.println("Result: FAIL");
                    return false;
                }
            }
            else {
                compareOutput(new FileReader(expectedOutputFile),
                                    new StringReader(fResults));
                fLogStream.println(fResults);
                fLogStream.println("Result: FAIL");
                return false;
            }
        }
        catch (IOException e) {
            fLogStream.println(
                "Unexpected IO problem attempting to verify results: " + e);
            fLogStream.println("Result: FAIL");
            return false;
        }
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.parser.XMLErrorHandler#error(java.lang.String, java.lang.String, org.apache.xerces.xni.parser.XMLParseException)
     */
    public void error(String domain, String key, XMLParseException exception)
        throws XNIException {
        printError("Error", exception);
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.parser.XMLErrorHandler#fatalError(java.lang.String, java.lang.String, org.apache.xerces.xni.parser.XMLParseException)
     */
    public void fatalError(
        String domain,
        String key,
        XMLParseException exception)
        throws XNIException {
        printError("Fatal Error", exception);
    }

    /* (non-Javadoc)
     * @see org.apache.xerces.xni.parser.XMLErrorHandler#warning(java.lang.String, java.lang.String, org.apache.xerces.xni.parser.XMLParseException)
     */
    public void warning(String domain, String key, XMLParseException exception)
        throws XNIException {
        printError("Warning", exception);
    }

    private static void printUsage() {
        System.out.println("java xinclude.Test [OPTIONS] [TESTS]");
        System.out.println("OPTIONS:");
        System.out.println("  -f [file] :      Specifies a log file to print detailed error messages to.");
        System.out.println("                   Omitting the FILE parameter makes messages print to ");
        System.out.println("                   standard error. If this option is absent, the messages");
        System.out.println("                   will not be output.");
        System.out.println("");
        System.out.println("  -g [directory] : Generates the expected output files in the ");
        System.out.println("                   given directory if specified, otherwise the files");
        System.out.println("                   are written to the expected output directory.");
        System.out.println("                   Only use this option without a target when the output ");
        System.out.println("                   is sure to be correct. The previous expected output files ");
        System.out.println("                   will be overwritten.");
        System.out.println("");
        System.out.println("  -h :             Prints this help message and exits.");
        System.out.println("TESTS:");
        System.out.println(
            "  A whitespace separated list of tests to run, specified by test number.");
        System.out.println("  If this is absent, all tests will be run.");
    }

    private void printDetailsMessage() {
        if (fLogStream != DEFAULT_LOG_STREAM) {
            System.err.println("See log output for details");
        }
        else {
            System.err.println("Re-run with -f option to get details.");
        }
    }

    /** Prints the error message. */
    protected void printError(String type, XMLParseException ex) {
        fOutputWriter.print("[");
        fOutputWriter.print(type);
        fOutputWriter.print("] ");
        String systemId = ex.getExpandedSystemId();
        if (systemId != null) {
            int index = systemId.lastIndexOf('/');
            if (index != -1)
                systemId = systemId.substring(index + 1);
            fOutputWriter.print(systemId);
        }
        fOutputWriter.print(':');
        fOutputWriter.print(ex.getLineNumber());
        fOutputWriter.print(':');
        fOutputWriter.print(ex.getColumnNumber());
        /*
         * The String returned by getMessage() is not stable across JDKs, so we
         * don't print it.  Unfortunately, there doesn't seem to be a way to get
         * the underlying type of exception (like FileNotFoundException) so
         * we just don't print anything.
        fOutputWriter.print(": ");
        fOutputWriter.print(ex.getMessage());
        */
        fOutputWriter.println();
        fOutputWriter.flush();
    } // printError(String,XMLParseException)

    protected boolean compareOutput(Reader expected, Reader actual)
        throws IOException {
        LineNumberReader expectedOutput = new LineNumberReader(expected);
        LineNumberReader actualOutput = new LineNumberReader(actual);

        while (expectedOutput.ready() && actualOutput.ready()) {
            String expectedLine = expectedOutput.readLine();
            String actualLine = actualOutput.readLine();
            if (!expectedLine.equals(actualLine)) {
                fLogStream.println(
                    "Mismatch on line: " + expectedOutput.getLineNumber());
                fLogStream.println("Expected: " + expectedLine);
                fLogStream.println("  Actual: " + actualLine);
                return false;
            }
        }
        if (expectedOutput.ready() && !actualOutput.ready()) {
            String expectedLine = expectedOutput.readLine();
            if (expectedLine != null) {
                fLogStream.println(
                    "Actual output contains fewer lines than expected output.");
                fLogStream.println(
                    "Line "
                        + expectedOutput.getLineNumber()
                        + ": "
                        + expectedLine);
                fLogStream.println("Above line has no match in actual output.");
                return false;
            }
        }
        else if (!expectedOutput.ready() && actualOutput.ready()) {
            String actualLine = actualOutput.readLine();
            if (actualLine != null) {
                fLogStream.println(
                    "Actual output contains more lines than expected output.");
                fLogStream.println(
                    "Line " + actualOutput.getLineNumber() + ": " + actualLine);
                fLogStream.println(
                    "Above line has no match in expected output.");
                return false;
            }
        }

        expectedOutput.close();
        actualOutput.close();
        return true;
    }

    private String stripUserDir(StringBuffer buf) {
        String userDir = System.getProperty("user.dir");
        String userURI = "file://";
        if (userDir.charAt(0) != '/') {
            userURI += "/";
        }
        userURI += userDir.replace('\\', '/');
        String str = getPathWithoutEscapes(buf.toString());

        int start = 0, end = 0;
        // strip ones in URI form
        while ((start = str.indexOf(userURI, start)) != -1) {
            end = start + userURI.length();
            // we add one, to get rid of the '/' after the user directory path
            str = str.substring(0, start) + str.substring(end+1);
        }

        while ((start = str.indexOf(userDir, start)) != -1) {
            end = start + userDir.length();
            // we add one, to get rid of the '/' after the user directory path
            str = str.substring(0, start) + str.substring(end+1);
        }
        return str;
    }
    
    private static String getPathWithoutEscapes(String origPath) {
        if (origPath != null && origPath.length() != 0 && origPath.indexOf('%') != -1) {
            // Locate the escape characters
            StringTokenizer tokenizer = new StringTokenizer(origPath, "%");
            StringBuffer result = new StringBuffer(origPath.length());
            int size = tokenizer.countTokens();
            result.append(tokenizer.nextToken());
            for(int i = 1; i < size; ++i) {
                String token = tokenizer.nextToken();
                // Decode the 2 digit hexadecimal number following % in '%nn'
                result.append((char)Integer.valueOf(token.substring(0, 2), 16).intValue());
                result.append(token.substring(2));
            }
            return result.toString();
        }
        return origPath;
    }
}
 No newline at end of file