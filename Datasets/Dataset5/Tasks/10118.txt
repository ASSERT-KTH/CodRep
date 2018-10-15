parserConfiguration = (XMLParserConfiguration)ObjectFactory.newInstance(parserName, cl, true);

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2002 The Apache Software Foundation.  All rights
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
 *    permission, please contact apache@apache.org.
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
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package xni;

import org.apache.xerces.parsers.XMLGrammarPreparser;
import org.apache.xerces.parsers.StandardParserConfiguration;
import org.apache.xerces.util.ObjectFactory;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLGrammarPoolImpl;
import org.apache.xerces.impl.Constants;

import org.apache.xerces.xni.grammars.XMLGrammarDescription;
import org.apache.xerces.xni.grammars.Grammar;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.parser.XMLParserConfiguration;

import java.util.Vector;

/**
 * This sample program illustrates how to use Xerces2's grammar
 * preparsing and caching functionality.  It permits either DTD or
 * Schema grammars to be parsed, and then allows instance documents to
 * be validated with them.  
 * <p> Note that, for access to a grammar's contents (via Xerces's
 * Schema Component model interfaces), slightly different methods need
 * to be used.  Nonetheless, this should go some way to indicating how
 * grammar preparsing and caching can be coupled in Xerces to achieve 
 * better performance.  It's also hoped this sample shows the way
 * towards combining this functionality in a DOM or SAX context.  
 *
 * @author Neil Graham, IBM
 * @version $Id$
 */
public class XMLGrammarBuilder {

    //
    // Constants
    //

    // property IDs:

    /** Property identifier: symbol table. */
    public static final String SYMBOL_TABLE =
        Constants.XERCES_PROPERTY_PREFIX + Constants.SYMBOL_TABLE_PROPERTY;

    /** Property identifier: grammar pool. */
    public static final String GRAMMAR_POOL =
        Constants.XERCES_PROPERTY_PREFIX + Constants.XMLGRAMMAR_POOL_PROPERTY;

    // feature ids

    /** Namespaces feature id (http://xml.org/sax/features/namespaces). */
    protected static final String NAMESPACES_FEATURE_ID = "http://xml.org/sax/features/namespaces";

    /** Validation feature id (http://xml.org/sax/features/validation). */
    protected static final String VALIDATION_FEATURE_ID = "http://xml.org/sax/features/validation";

    /** Schema validation feature id (http://apache.org/xml/features/validation/schema). */
    protected static final String SCHEMA_VALIDATION_FEATURE_ID = "http://apache.org/xml/features/validation/schema";

    /** Schema full checking feature id (http://apache.org/xml/features/validation/schema-full-checking). */
    protected static final String SCHEMA_FULL_CHECKING_FEATURE_ID = "http://apache.org/xml/features/validation/schema-full-checking";

    // a larg(ish) prime to use for a symbol table to be shared
    // among
    // potentially man parsers.  Start one as close to 2K (20
    // times larger than normal) and see what happens...
    public static final int BIG_PRIME = 2039;

    // default settings

    /** Default Schema full checking support (false). */
    protected static final boolean DEFAULT_SCHEMA_FULL_CHECKING = false;

    //
    // MAIN
    //

    /** Main program entry point. */
    public static void main(String argv[]) {

        // too few parameters
        if (argv.length < 2) {
            printUsage();
            System.exit(1);
        }

        XMLParserConfiguration parserConfiguration = null;
        String arg = null;
        int i = 0;

        arg = argv[i];
        if (arg.equals("-p")) {
            // get parser name
            i++;
            String parserName = argv[i];

            // create parser
            try {
                ClassLoader cl = ObjectFactory.findClassLoader();
                parserConfiguration = (XMLParserConfiguration)ObjectFactory.newInstance(parserName, cl);
            }
            catch (Exception e) {
                parserConfiguration = null;
                System.err.println("error: Unable to instantiate parser configuration ("+parserName+")");
            }
            i++;
        }
        arg = argv[i];
        // process -d
        Vector externalDTDs = null; 
        if (arg.equals("-d")) {
            externalDTDs= new Vector();
            i++;
            while (i < argv.length && !(arg = argv[i]).startsWith("-")) {
                externalDTDs.addElement(arg);
                i++;
            }
            // has to be at least one dTD or schema , and there has to be other parameters
            if (externalDTDs.size() == 0) {
                printUsage();
                System.exit(1);
            }
        }

        // process -f/F
        Vector schemas = null;
        boolean schemaFullChecking = DEFAULT_SCHEMA_FULL_CHECKING;
        if(i < argv.length) {
            arg = argv[i];
            if (arg.equals("-f")) {
                schemaFullChecking = true;
                i++;
                arg = argv[i];
            } else if (arg.equals("-F")) {
                schemaFullChecking = false;
                i++;
                arg = argv[i];
            } 
            if (arg.equals("-a")) {
                if(externalDTDs != null) {
                    printUsage();
                    System.exit(1);
                }

                // process -a: schema files

                schemas= new Vector();
                i++;
                while (i < argv.length && !(arg = argv[i]).startsWith("-")) {
                    schemas.addElement(arg);
                    i++;
                }

                // has to be at least one dTD or schema , and there has to be other parameters
                if (schemas.size() == 0) {
                    printUsage();
                    System.exit(1);
                }
            }

        }
        // process -i: instance files, if any
        Vector ifiles = null;
        if (i < argv.length) {
            if (!arg.equals("-i")) {
                printUsage();
                System.exit(1);
            }

            i++;
            ifiles = new Vector();
            while (i < argv.length && !(arg = argv[i]).startsWith("-")) {
                ifiles.addElement(arg);
                i++;
            }

            // has to be at least one instance file, and there has to be no more
            // parameters
            if (ifiles.size() == 0 || i != argv.length) {
                printUsage();
                System.exit(1);
            }
        }

        // now we have all our arguments.  We only
        // need to parse the DTD's/schemas, put them
        // in a grammar pool, possibly instantiate an 
        // appropriate configuration, and we're on our way.

        SymbolTable sym = new SymbolTable(BIG_PRIME);
        XMLGrammarPreparser preparser = new XMLGrammarPreparser(sym);
        XMLGrammarPoolImpl grammarPool = new XMLGrammarPoolImpl();
        boolean isDTD = false;
        if(externalDTDs != null) {
            preparser.registerPreparser(XMLGrammarDescription.XML_DTD, null);
            isDTD = true;
        } else if(schemas != null) {
            preparser.registerPreparser(XMLGrammarDescription.XML_SCHEMA, null);
            isDTD = false;
        } else {
            System.err.println("No schema or DTD specified!");
            System.exit(1);
        }
        preparser.setProperty(GRAMMAR_POOL, grammarPool);
        preparser.setFeature(NAMESPACES_FEATURE_ID, true);
        preparser.setFeature(VALIDATION_FEATURE_ID, true);
        // note we can set schema features just in case...
        preparser.setFeature(SCHEMA_VALIDATION_FEATURE_ID, true);
        preparser.setFeature(SCHEMA_FULL_CHECKING_FEATURE_ID, schemaFullChecking);
        // parse the grammar...

        try {
            if(isDTD) {
                for (i = 0; i < externalDTDs.size(); i++) {
                    Grammar g = preparser.preparseGrammar(XMLGrammarDescription.XML_DTD, stringToXIS((String)externalDTDs.elementAt(i)));
                    // we don't really care about g; grammarPool will take care of everything.
                }
            } else { // must be schemas!
                for (i = 0; i < schemas.size(); i++) {
                    Grammar g = preparser.preparseGrammar(XMLGrammarDescription.XML_SCHEMA, stringToXIS((String)schemas.elementAt(i)));
                    // we don't really care about g; grammarPool will take care of everything.
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
        // Now we have a grammar pool and a SymbolTable; just
        // build a configuration and we're on our way!
        if(parserConfiguration == null) {
            parserConfiguration = new StandardParserConfiguration(sym, grammarPool);
        } else {
            // set GrammarPool and SymbolTable...
            parserConfiguration.setProperty(SYMBOL_TABLE, sym);
            parserConfiguration.setProperty(GRAMMAR_POOL, grammarPool);
        }
        // now must reset features, unfortunately:
        try{
            parserConfiguration.setFeature(NAMESPACES_FEATURE_ID, true);
            parserConfiguration.setFeature(VALIDATION_FEATURE_ID, true);
            // now we can still do schema features just in case, 
            // so long as it's our configuraiton......
            parserConfiguration.setFeature(SCHEMA_VALIDATION_FEATURE_ID, true);
            parserConfiguration.setFeature(SCHEMA_FULL_CHECKING_FEATURE_ID, schemaFullChecking);
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
        // then for each instance file, try to validate it
        if (ifiles != null) {
            try {
                for (i = 0; i < ifiles.size(); i++) {
                    parserConfiguration.parse(stringToXIS((String)ifiles.elementAt(i)));
                }
            } catch (Exception e) {
                e.printStackTrace();
                System.exit(1);
            }
        }

    } // main(String[])

    //
    // Private static methods
    //

    /** Prints the usage. */
    private static void printUsage() {

        System.err.println("usage: java xni.XMLGrammarBuilder [-p config_file] -d uri ... | [-f|-F] -a uri ... [-i uri ...]");
        System.err.println();

        System.err.println("options:");
        System.err.println("  -p config_file:   configuration to use for instance validation");
        System.err.println("  -d    grammars to preparse are DTD esxternal subsets");
        System.err.println("  -f  | -F    Turn on/off Schema full checking (default "+ 
                (DEFAULT_SCHEMA_FULL_CHECKING ? "on" : "off"));
        System.err.println("  -a uri ...  Provide a list of schema documents.");
        System.err.println("  -i uri ...  Provide a list of instalce documents to validate.");
        System.err.println();
        System.err.println("Both -d and -a cannot be specified!");

    } // printUsage()

    private static XMLInputSource stringToXIS(String uri) {
        return new XMLInputSource(null, uri, null);
    }
} // class XMLGrammarBuilder
