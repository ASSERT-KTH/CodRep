DOMConfiguration config = core.getDomConfig();

/*
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 2001 The Apache Software Foundation.  All rights
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written
 *    permission, please contact apache\@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation, and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.ibm.com .  For more information
 * on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

/**
 * $Id$
 *
 * This program is a straight port of xerces/c/tests/ThreadTest.cpp
 * No particular effort has been made to make it more java-like (who cares
 * besides a few biggots? ;-)
 *
 * @author Andy Heninger, IBM (C++ version)
 * @author Arnaud  Le Hors, IBM
 */

package thread;

import org.w3c.dom.*;
import org.xml.sax.*;

import org.apache.xerces.dom.CoreDocumentImpl;
import org.apache.xerces.dom3.DOMConfiguration;
import org.apache.xerces.parsers.SAXParser;
import org.apache.xerces.parsers.DOMParser;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.StringReader;

public class Test {


//------------------------------------------------------------------------------
//
//  struct InFileInfo   One of these structs will be set up for each file listed
//                      on the command line.  Once set, the data is unchanging
//                      and can safely be referenced by the test threads without
//                      use of synchronization.
//
//------------------------------------------------------------------------------
class InFileInfo
{
    public String fileName;
    public String fileContent; // If doing an in-memory parse, this field points
                             //   to an allocated string containing the entire file
                             //   contents.  Otherwise it's 0.
    int     checkSum;        // The XML checksum.  Set up by the main thread for
                             //   each file before the worker threads are started.
}

//------------------------------------------------------------------------------
//
//  struct runInfo     Holds the info extracted from the command line.
//                     There is only one of these, and it is static, and
//                     unchanging once the command line has been parsed.
//                     During the test, the threads will access this info without
//                     any synchronization.
//
//------------------------------------------------------------------------------
final int MAXINFILES = 25;
class RunInfo
{
    boolean     quiet;
    boolean     verbose;
    int         numThreads;
    boolean     validating;
    boolean     dom;
    boolean     reuseParser;
    boolean     inMemory;
    boolean     dumpOnErr;
    int         totalTime;
    int         numInputFiles;
    InFileInfo  files[] = new InFileInfo[MAXINFILES];
}


//------------------------------------------------------------------------------
//
//  struct threadInfo  Holds information specific to an individual thread.
//                     One of these is set up for each thread in the test.
//                     The main program monitors the threads by looking
//                     at the status stored in these structs.
//
//------------------------------------------------------------------------------
class ThreadInfo
{
    boolean    fHeartBeat;      // Set true by the thread each time it finishes
                                //   parsing a file.
    int        fParses;         // Number of parses completed.
    int        fThreadNum;      // Identifying number for this thread.

    ThreadInfo() {
        fHeartBeat = false;
        fParses = 0;
        fThreadNum = -1;
    }
}


//
//------------------------------------------------------------------------------
//
//  Global Data
//
//------------------------------------------------------------------------------
RunInfo         gRunInfo = new RunInfo();
ThreadInfo      gThreadInfo[];



//------------------------------------------------------------------------------
//
//  class ThreadParser   Bundles together a SAX parser and the SAX handlers
//                       and contains the API that the rest of this test
//                       program uses for creating parsers and doing parsing.
//
//                       Multiple instances of this class can operate concurrently
//                       in different threads.
//
//-------------------------------------------------------------------------------
class ThreadParser extends HandlerBase
{
    private int           fCheckSum;
    private SAXParser     fSAXParser;
    private DOMParser     fDOMParser;


    // Not really public,
    //  These are the SAX call-back functions
    //  that this class implements.
    public void characters(char chars[], int start, int length) {
        addToCheckSum(chars, start, length);}
    public void ignorableWhitespace(char chars[], int start, int length) {
        addToCheckSum(chars, start, length);}

    public void warning(SAXParseException ex)     {
        System.err.print("*** Warning "+
                         ex.getMessage());}

    public void error(SAXParseException ex)       {
        System.err.print("*** Error "+
                         ex.getMessage());}

    public void fatalError(SAXParseException ex)  {
        System.err.print("***** Fatal error "+
                         ex.getMessage());}

//
//  ThreadParser constructor.  Invoked by the threads of the test program
//                              to create parsers.
//
ThreadParser()
{
    if (gRunInfo.dom) {
        // Set up to use a DOM parser
        fDOMParser = new org.apache.xerces.parsers.DOMParser();
        try {
            fDOMParser.setFeature( "http://xml.org/sax/features/validation", 
                                   gRunInfo.validating);
        }
        catch (Exception e) {}
        fDOMParser.setErrorHandler(this);
    }
    else
    {
        // Set up to use a SAX parser.
        fSAXParser = new org.apache.xerces.parsers.SAXParser();
        try {
            fSAXParser.setFeature( "http://xml.org/sax/features/validation", 
                                   gRunInfo.validating);
        }
        catch (Exception e) {}
        fSAXParser.setDocumentHandler(this);
        fSAXParser.setErrorHandler(this);
    }

}

//------------------------------------------------------------------------
//
//  parse   - This is the method that is invoked by the rest of
//            the test program to actually parse an XML file.
//
// @param fileNum is an index into the gRunInfo.files array.
// @return the XML checksum, or 0 if a parse error occured.
//
//------------------------------------------------------------------------
int parse(int fileNum)
{
    InputSource mbis = null;
    InFileInfo  fInfo = gRunInfo.files[fileNum];

    fCheckSum = 0;

    if (gRunInfo.inMemory) {
        mbis = new InputSource(new StringReader(fInfo.fileContent));
    }

    try
    {
        if (gRunInfo.dom) {
            // Do a DOM parse
            if (gRunInfo.inMemory)
                fDOMParser.parse(mbis);
            else
                fDOMParser.parse(fInfo.fileName);
            Document doc = fDOMParser.getDocument();
            domCheckSum(doc);
            CoreDocumentImpl core = (CoreDocumentImpl) doc;
            DOMConfiguration config = core.getConfig();
            config.setParameter("validate", Boolean.TRUE);
            core.normalizeDocument();

        }
        else
        {
            // Do a SAX parse
            if (gRunInfo.inMemory)
                fSAXParser.parse(mbis);
            else
                fSAXParser.parse(fInfo.fileName);
        }
    }

    catch (SAXException e)
    {
        String exceptionMessage = e.getMessage();
        System.err.println(" during parsing: " + fInfo.fileName +
                           " Exception message is: " + exceptionMessage);
    }
    catch (IOException e)
    {
        String exceptionMessage = e.getMessage();
        System.err.println(" during parsing: " + fInfo.fileName +
                           " Exception message is: " + exceptionMessage);
    }

    return fCheckSum;
}


//
//  addToCheckSum - private function, used within ThreadParser in
//                  computing the checksum of the XML file.
//
private void addToCheckSum(char chars[], int start, int len)
{
    // String with character count.
    int i;
    for (i=start; i<len; i++)
        fCheckSum = fCheckSum*5 + chars[i];
}

//
//  addToCheckSum - private function, used within ThreadParser in
//                  computing the checksum of the XML file.
//
private void addToCheckSum(String chars)
{
    int i;
    int len = chars.length();
    for (i=0; i<len; i++)
        fCheckSum = fCheckSum*5 + chars.charAt(i);
}



//
// startElement - our SAX handler callback function for element starts.
//                update the document checksum with the element name
//                and any attribute names and values.
//
public void startElement(String name, AttributeList attributes)
{
    addToCheckSum(name);

    int n = attributes.getLength();
    int i;
    for (i=0; i<n; i++)
    {
        String attNam = attributes.getName(i);
        addToCheckSum(attNam);
        String attVal = attributes.getValue(i);
        addToCheckSum(attVal);
    }
}


//
// domCheckSum  -  Compute the check sum for a DOM node.
//                 Works recursively - initially called with a document node.
//
public void domCheckSum(Node node)
{
    String        s;
    Node          child;
    NamedNodeMap  attributes;

    switch (node.getNodeType() )
    {
    case Node.ELEMENT_NODE:
        {
            s = node.getNodeName();   // the element name

            attributes = node.getAttributes();  // Element's attributes
            int numAttributes = attributes.getLength();
            int i;
            for (i=0; i<numAttributes; i++)
                domCheckSum(attributes.item(i));

            addToCheckSum(s);  // Content and Children
            for (child=node.getFirstChild(); child!=null; child=child.getNextSibling())
                domCheckSum(child);

            break;
        }


    case Node.ATTRIBUTE_NODE:
        {
            s = node.getNodeName();  // The attribute name
            addToCheckSum(s);
            s = node.getNodeValue();  // The attribute value
            if (s != null)
                addToCheckSum(s);
            break;
        }


    case Node.TEXT_NODE:
    case Node.CDATA_SECTION_NODE:
        {
            s = node.getNodeValue();
            addToCheckSum(s);
            break;
        }

    case Node.ENTITY_REFERENCE_NODE:
    case Node.DOCUMENT_NODE:
        {
            // For entity references and the document, nothing is dirctly
            //  added to the checksum, but we do want to process the chidren nodes.
            //
            for (child=node.getFirstChild(); child!=null; child=child.getNextSibling())
                domCheckSum(child);
            break;
        }
    }
}


//
// Recompute the checksum.  Meaningful only for DOM, will tell us whether
//  a failure is transient, or whether the DOM data is permanently corrupted.
//  for DOM, re-walk the tree.
//  for SAX, can't do, just return previous value.
//
public int reCheck()
{
    if (gRunInfo.dom) {
        fCheckSum = 0;
        Document doc = fDOMParser.getDocument();
        domCheckSum(doc);
    }
    return fCheckSum;
}

//
// domPrint  -  Dump the contents of a DOM document.
//              For debugging failures, when all else fails.
//
public void domPrint()
{
    System.out.println("Begin DOMPrint ...");
    if (gRunInfo.dom)
        domPrint(fDOMParser.getDocument());
    System.out.println("End DOMPrint");
}

//
// domPrint  -  Dump the contents of a DOM node.
//              For debugging failures, when all else fails.
//                 Works recursively - initially called with a document node.
//
void domPrint(Node node)
{

    String        s;
    Node          child;
    NamedNodeMap  attributes;

    switch (node.getNodeType() )
    {
    case Node.ELEMENT_NODE:
        {
            System.out.print("<");
            System.out.print(node.getNodeName());   // the element name

            attributes = node.getAttributes();  // Element's attributes
            int numAttributes = attributes.getLength();
            int i;
            for (i=0; i<numAttributes; i++) {
                domPrint(attributes.item(i));
            }
            System.out.print(">");

            for (child=node.getFirstChild(); child!=null; child=child.getNextSibling())
                domPrint(child);

            System.out.print("</");
            System.out.print(node.getNodeName());
            System.out.print(">");
            break;
        }


    case Node.ATTRIBUTE_NODE:
        {
            System.out.print(" ");
            System.out.print(node.getNodeName());   // The attribute name
            System.out.print("= \"");
            System.out.print(node.getNodeValue());  // The attribute value
            System.out.print("\"");
            break;
        }


    case Node.TEXT_NODE:
    case Node.CDATA_SECTION_NODE:
        {
            System.out.print(node.getNodeValue());
            break;
        }

    case Node.ENTITY_REFERENCE_NODE:
    case Node.DOCUMENT_NODE:
        {
            // For entity references and the document, nothing is dirctly
            //  printed, but we do want to process the chidren nodes.
            //
            for (child=node.getFirstChild(); child!=null; child=child.getNextSibling())
                domPrint(child);
            break;
        }
    }
}

} // class ThreadParser


//----------------------------------------------------------------------
//
//   parseCommandLine   Read through the command line, and save all
//                      of the options in the gRunInfo struct.
//
//                      Display the usage message if the command line
//                      is no good.
//
//                      Probably ought to be a member function of RunInfo.
//
//----------------------------------------------------------------------

void parseCommandLine(String argv[])
{
    gRunInfo.quiet = false;               // Set up defaults for run.
    gRunInfo.verbose = false;
    gRunInfo.numThreads = 2;
    gRunInfo.validating = false;
    gRunInfo.dom = false;
    gRunInfo.reuseParser = false;
    gRunInfo.inMemory = false;
    gRunInfo.dumpOnErr = false;
    gRunInfo.totalTime = 0;
    gRunInfo.numInputFiles = 0;

    try             // Use exceptions for command line syntax errors.
    {
        int argnum = 0;
        int argc = argv.length;
        while (argnum < argc)
        {
            if (argv[argnum].equals("-quiet"))
                gRunInfo.quiet = true;
            else if (argv[argnum].equals("-verbose"))
                gRunInfo.verbose = true;
            else if (argv[argnum].equals("-v"))
                gRunInfo.validating = true;
            else if (argv[argnum].equals("-dom"))
                gRunInfo.dom = true;
            else if (argv[argnum].equals("-reuse"))
                gRunInfo.reuseParser = true;
            else if (argv[argnum].equals("-dump"))
                gRunInfo.dumpOnErr = true;
            else if (argv[argnum].equals("-mem"))
                gRunInfo.inMemory = true;
            else if (argv[argnum].equals("-threads"))
            {
                ++argnum;
                if (argnum >= argc)
                    throw new Exception();
                try {
                    gRunInfo.numThreads = Integer.parseInt(argv[argnum]);
                }
                catch (NumberFormatException e) {
                    throw new Exception();
                }
                if (gRunInfo.numThreads < 0)
                    throw new Exception();
            }
            else if (argv[argnum].equals("-time"))
            {
                ++argnum;
                if (argnum >= argc)
                    throw new Exception();
                try {
                    gRunInfo.totalTime = Integer.parseInt(argv[argnum]);
                }
                catch (NumberFormatException e) {
                    throw new Exception();
                }
                if (gRunInfo.totalTime < 1)
                    throw new Exception();
            }
            else  if (argv[argnum].charAt(0) == '-')
            {
                System.err.println("Unrecognized command line option. Scanning"
                                   + " \"" + argv[argnum] + "\"");
                throw new Exception();
            }
            else
            {
                gRunInfo.numInputFiles++;
                if (gRunInfo.numInputFiles >= MAXINFILES)
                {
                    System.err.println("Too many input files. Limit is "
                                       + MAXINFILES);
                    throw new Exception();
                }
                gRunInfo.files[gRunInfo.numInputFiles-1] = new InFileInfo();
                gRunInfo.files[gRunInfo.numInputFiles-1].fileName = argv[argnum];
            }
            argnum++;
        }

        // We've made it through the command line.
        //  Verify that at least one input file to be parsed was specified.
        if (gRunInfo.numInputFiles == 0)
        {
            System.err.println("No input XML file specified on command line.");
            throw new Exception();
        };


    }
    catch (Exception e)
    {
        System.err.print("usage: java thread.Test [-v] [-threads nnn] [-time nnn] [-quiet] [-verbose] xmlfile...\n" +
            "     -v             Use validating parser.  Non-validating is default. \n" +
            "     -dom           Use a DOM parser.  Default is SAX. \n" +
            "     -quiet         Suppress periodic status display. \n" +
            "     -verbose       Display extra messages. \n" +
            "     -reuse         Retain and reuse parser.  Default creates new for each parse.\n" +
            "     -threads nnn   Number of threads.  Default is 2. \n" +
            "     -time nnn      Total time to run, in seconds.  Default is forever.\n" +
            "     -dump          Dump DOM tree on error.\n" +
            "     -mem           Read files into memory once only, and parse them from there.\n"
            );
        System.exit(1);
    }
}


//---------------------------------------------------------------------------
//
//   ReadFilesIntoMemory   For use when parsing from memory rather than
//                          reading the files each time, here is the code that
//                          reads the files into local memory buffers.
//
//                          This function is only called once, from the main
//                          thread, before all of the worker threads are started.
//
//---------------------------------------------------------------------------
void ReadFilesIntoMemory()
{
    int     fileNum;
    InputStreamReader fileF;
    char chars[] = new char[1024];
    StringBuffer buf = new StringBuffer();

    if (gRunInfo.inMemory)
    {
        for (fileNum = 0; fileNum <gRunInfo.numInputFiles; fileNum++)
        {
            InFileInfo fInfo = gRunInfo.files[fileNum];
            buf.setLength(0);
            try {
                FileInputStream in = new FileInputStream( fInfo.fileName );
                fileF = new InputStreamReader(in);
                int len = 0;
                while ((len = fileF.read(chars, 0, chars.length)) > 0) {
                    buf.append(chars, 0, len);
                }
                fInfo.fileContent = buf.toString();
                fileF.close();
            }
            catch (FileNotFoundException e) {
                System.err.print("File not found: \"" +
                                 fInfo.fileName + "\".");
                System.exit(-1);
            }
            catch (IOException e) {
                System.err.println("Error reading file \"" +
                                   fInfo.fileName + "\".");
                System.exit(-1);
            }
        }
    }
}



//----------------------------------------------------------------------
//
//  threadMain   The main function for each of the swarm of test threads.
//               Run in an infinite loop, parsing each of the documents
//               given on the command line in turn.
//
//               There is no return from this fuction, and no graceful
//               thread termination.  Threads are stuck running here
//               until the OS shuts them down as a consequence of the
//               main thread of the process (which never calls this
//               function) exiting.
//
//----------------------------------------------------------------------


class thread extends Thread {

    ThreadInfo thInfo;

    thread (ThreadInfo param) {
        thInfo = param;
    }

    public void run()
{
    ThreadParser thParser = null;

    if (gRunInfo.verbose)
        System.out.println("Thread " + thInfo.fThreadNum + ": starting");

    int docNum = gRunInfo.numInputFiles;

    //
    // Each time through this loop, one file will be parsed and its checksum
    // computed and compared with the precomputed value for that file.
    //
    while (true)
    {

        if (thParser == null)
            thParser = new ThreadParser();

        docNum++;

        if (docNum >= gRunInfo.numInputFiles)
            docNum = 0;

        InFileInfo fInfo = gRunInfo.files[docNum];

        if (gRunInfo.verbose )
            System.out.println("Thread " + thInfo.fThreadNum +
                               ": starting file " + fInfo.fileName);


        int checkSum = 0;
        checkSum = thParser.parse(docNum);

        if (checkSum != gRunInfo.files[docNum].checkSum)
        {
            System.err.println("\nThread " + thInfo.fThreadNum +
                               ": Parse Check sum error on file  \"" +
                               fInfo.fileName + "\".  Expected " +
                               fInfo.checkSum + ",  got " + checkSum);

            // Revisit - let the loop continue to run?
            int secondTryCheckSum = thParser.reCheck();
            System.err.println("   Retry checksum is " + secondTryCheckSum);
            if (gRunInfo.dumpOnErr)
                thParser.domPrint();
            System.out.flush();
            System.exit(-1);
        }

        if (gRunInfo.reuseParser == false)
        {
            thParser = null;
        }


        thInfo.fHeartBeat = true;
        thInfo.fParses++;
    }
} // run():void

} // class thread


//----------------------------------------------------------------------
//
//   main
//
//----------------------------------------------------------------------

void run(String argv[])
{
    parseCommandLine(argv);

    //
    // If we will be parsing from memory, read each of the input files
    //  into memory now.
    //
    ReadFilesIntoMemory();


    //
    // While we are still single threaded, parse each of the documents
    //  once, to check for errors, and to note the checksum.
    // Blow off the rest of the test if there are errors.
    //
    ThreadParser mainParser = new ThreadParser();
    int     n;
    boolean errors = false;
    int     cksum;


    for (n = 0; n < gRunInfo.numInputFiles; n++)
    {
        String fileName = gRunInfo.files[n].fileName;
        if (gRunInfo.verbose)
            System.out.print(fileName + " checksum is ");

        cksum = mainParser.parse(n);

        if (cksum == 0)
        {
            System.err.println("An error occured while initially parsing" +
                               fileName);
            errors = true;
        }

        gRunInfo.files[n].checkSum = cksum;
        if (gRunInfo.verbose )
            System.out.println(cksum);
        if (gRunInfo.dumpOnErr && errors)
            mainParser.domPrint();

    }
    if (errors)
        System.exit(1);

    //
    //  Fire off the requested number of parallel threads
    //

    if (gRunInfo.numThreads == 0)
        return;

    gThreadInfo = new ThreadInfo[gRunInfo.numThreads];

    int threadNum;
    for (threadNum=0; threadNum < gRunInfo.numThreads; threadNum++)
    {
        gThreadInfo[threadNum] = new ThreadInfo();
        gThreadInfo[threadNum].fThreadNum = threadNum;
        thread t = new thread(gThreadInfo[threadNum]);
        t.start();
    }

    //
    //  Loop, watching the heartbeat of the worker threads.
    //    Each second, display "+" when all threads have completed a parse
    //                 display "." if some thread hasn't since previous "+"
    //

    long startTime = System.currentTimeMillis();
    long elapsedSeconds = 0;
    while (gRunInfo.totalTime == 0 || gRunInfo.totalTime > elapsedSeconds)
    {
        try {
            Thread.sleep(1000);
        }
        catch (InterruptedException e) {
            // nobody would dare!! :-)
        }
        if (gRunInfo.quiet == false && gRunInfo.verbose == false)
        {
            char c = '+';
            for (threadNum=0; threadNum < gRunInfo.numThreads; threadNum++)
            {
                if (gThreadInfo[threadNum].fHeartBeat == false)
                {
                    c = '.';
                    break;
                }
            }
            System.out.print(c);
            System.out.flush();
            if (c == '+')
                for (threadNum=0; threadNum < gRunInfo.numThreads; threadNum++)
                    gThreadInfo[threadNum].fHeartBeat = false;
        }
        elapsedSeconds = (System.currentTimeMillis() - startTime) / 1000;
    };

    //
    //  Time's up, we are done.  (We only get here if this was a timed run)
    //  Tally up the total number of parses completed by each of the threads.
    //  To Do:  Run the main thread at higher priority, so that the worker threads
    //    won't make much progress while we are adding up the results.
    //
    double totalParsesCompleted = 0;
    for (threadNum=0; threadNum < gRunInfo.numThreads; threadNum++)
    {
        totalParsesCompleted += gThreadInfo[threadNum].fParses;
        // printf("%f   ", totalParsesCompleted);
    }

    double parsesPerMinute =
        totalParsesCompleted / (((double)gRunInfo.totalTime) / ((double)60));
    System.out.println("\n" + parsesPerMinute + " parses per minute.");

    //  The threads are still running; we just return
    //   and leave it to the operating sytem to kill them.
    //
    System.exit(0);
}

static public void main(String argv[]) {
    Test test = new Test();
    test.run(argv);
}

} // class Test