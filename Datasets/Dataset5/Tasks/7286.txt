protected final PrintWriter fOut = new PrintWriter(System.out);

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

package jaxp;

import java.io.PrintWriter;
import java.util.Vector;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamReader;
import javax.xml.transform.Source;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.sax.SAXSource;
import javax.xml.transform.stax.StAXSource;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.w3c.dom.Document;
import org.xml.sax.ErrorHandler;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.SAXNotRecognizedException;
import org.xml.sax.SAXNotSupportedException;
import org.xml.sax.SAXParseException;
import org.xml.sax.XMLReader;
import org.xml.sax.helpers.XMLReaderFactory;

/**
 * <p>A sample demonstrating how to use the JAXP 1.4 Validation API
 * to create a validator and use the validator to validate input
 * from SAX, DOM, StAX or a stream. The output of this program shows 
 * the time spent executing the Validator.validate(Source) method.</p>
 * 
 * <p>This class is useful as a "poor-man's" performance tester to
 * compare the speed of various JAXP 1.4 validators with different
 * input sources. However, it is important to note that the first 
 * validation time of a validator will include both VM class load time 
 * and validator initialization that would not be present in subsequent
 * validations with the same document. Also note that when the source for
 * validation is SAX, StAX or a stream, the validation time will also 
 * include the time to parse the document, whereas the DOM validation is
 * completely in memory.</p>
 * 
 * <p><strong>Note:</strong> The results produced by this program
 * should never be accepted as true performance measurements.</p>
 *
 * @author Michael Glavassevich, IBM
 *
 * @version $Id$
 */
public class SourceValidator 
    implements ErrorHandler {
    
    //
    // Constants
    //

    // feature ids
    
    /** Schema full checking feature id (http://apache.org/xml/features/validation/schema-full-checking). */
    protected static final String SCHEMA_FULL_CHECKING_FEATURE_ID = "http://apache.org/xml/features/validation/schema-full-checking";
    
    /** Honour all schema locations feature id (http://apache.org/xml/features/honour-all-schemaLocations). */
    protected static final String HONOUR_ALL_SCHEMA_LOCATIONS_ID = "http://apache.org/xml/features/honour-all-schemaLocations";
    
    /** Validate schema annotations feature id (http://apache.org/xml/features/validate-annotations) */
    protected static final String VALIDATE_ANNOTATIONS_ID = "http://apache.org/xml/features/validate-annotations";
    
    /** Generate synthetic schema annotations feature id (http://apache.org/xml/features/generate-synthetic-annotations). */
    protected static final String GENERATE_SYNTHETIC_ANNOTATIONS_ID = "http://apache.org/xml/features/generate-synthetic-annotations";
    
    // property ids
    
    /** StAX support for reporting line and column numbers property id (javax.xml.stream.isSupportingLocationCoordinates). */
    protected static final String IS_SUPPORTING_LOCATION_COORDINATES = "javax.xml.stream.isSupportingLocationCoordinates";
    
    // default settings
    
    /** Default schema language (http://www.w3.org/2001/XMLSchema). */
    protected static final String DEFAULT_SCHEMA_LANGUAGE = XMLConstants.W3C_XML_SCHEMA_NS_URI;
    
    /** Default repetition (1). */
    protected static final int DEFAULT_REPETITION = 1;
    
    /** Default validation source. */
    protected static final String DEFAULT_VALIDATION_SOURCE = "sax";
    
    /** Default schema full checking support (false). */
    protected static final boolean DEFAULT_SCHEMA_FULL_CHECKING = false;
    
    /** Default honour all schema locations (false). */
    protected static final boolean DEFAULT_HONOUR_ALL_SCHEMA_LOCATIONS = false;
    
    /** Default validate schema annotations (false). */
    protected static final boolean DEFAULT_VALIDATE_ANNOTATIONS = false;
    
    /** Default generate synthetic schema annotations (false). */
    protected static final boolean DEFAULT_GENERATE_SYNTHETIC_ANNOTATIONS = false;
    
    /** Default memory usage report (false). */
    protected static final boolean DEFAULT_MEMORY_USAGE = false;
    
    //
    // Data
    //
    
    protected PrintWriter fOut = new PrintWriter(System.out);

    //
    // Constructors
    //

    /** Default constructor. */
    public SourceValidator() {
    } // <init>()
    
    //
    // Public methods
    //
    
    public void validate(Validator validator, 
            Source source, String systemId,
            int repetitions, boolean memoryUsage) {
        try {
            long timeBefore = System.currentTimeMillis();
            long memoryBefore = Runtime.getRuntime().freeMemory();
            for (int j = 0; j < repetitions; ++j) {
                validator.validate(source);
            }
            long memoryAfter = Runtime.getRuntime().freeMemory();
            long timeAfter = System.currentTimeMillis();

            long time = timeAfter - timeBefore;
            long memory = memoryUsage
                        ? memoryBefore - memoryAfter : Long.MIN_VALUE;
            printResults(fOut, systemId, time, memory, repetitions);
        }
        catch (SAXParseException e) {
            // ignore
        }
        catch (Exception e) {
            System.err.println("error: Parse error occurred - "+e.getMessage());
            Exception se = e;
            if (e instanceof SAXException) {
                se = ((SAXException)e).getException();
            }
            if (se != null)
              se.printStackTrace(System.err);
            else
              e.printStackTrace(System.err);

        }
    } // validate(Validator,Source,String,int,boolean)
    
    public void validate(Validator validator, 
            XMLInputFactory xif, String systemId,
            int repetitions, boolean memoryUsage) {
        try {
            Source source = new StreamSource(systemId);
            long timeBefore = System.currentTimeMillis();
            long memoryBefore = Runtime.getRuntime().freeMemory();
            for (int j = 0; j < repetitions; ++j) {
                XMLStreamReader reader = xif.createXMLStreamReader(source);
                validator.validate(new StAXSource(reader));
                reader.close();
            }
            long memoryAfter = Runtime.getRuntime().freeMemory();
            long timeAfter = System.currentTimeMillis();

            long time = timeAfter - timeBefore;
            long memory = memoryUsage
                        ? memoryBefore - memoryAfter : Long.MIN_VALUE;
            printResults(fOut, systemId, time, memory, repetitions);
        }
        catch (SAXParseException e) {
            // ignore
        }
        catch (Exception e) {
            System.err.println("error: Parse error occurred - "+e.getMessage());
            Exception se = e;
            if (e instanceof SAXException) {
                se = ((SAXException)e).getException();
            }
            if (se != null)
              se.printStackTrace(System.err);
            else
              e.printStackTrace(System.err);

        }
    } // validate(Validator,XMLInputFactory,String,int,boolean)
    
    /** Prints the results. */
    public void printResults(PrintWriter out, String uri, long time,
                             long memory, int repetition) {
        
        // filename.xml: 631 ms
        out.print(uri);
        out.print(": ");
        if (repetition == 1) {
            out.print(time);
        }
        else {
            out.print(time);
            out.print('/');
            out.print(repetition);
            out.print('=');
            out.print(((float)time)/repetition);
        }
        out.print(" ms");
        if (memory != Long.MIN_VALUE) {
            out.print(", ");
            out.print(memory);
            out.print(" bytes");
        }
        out.println();
        out.flush();

    } // printResults(PrintWriter,String,long,long,int)
    
    //
    // ErrorHandler methods
    //

    /** Warning. */
    public void warning(SAXParseException ex) throws SAXException {
        printError("Warning", ex);
    } // warning(SAXParseException)

    /** Error. */
    public void error(SAXParseException ex) throws SAXException {
        printError("Error", ex);
    } // error(SAXParseException)

    /** Fatal error. */
    public void fatalError(SAXParseException ex) throws SAXException {
        printError("Fatal Error", ex);
        throw ex;
    } // fatalError(SAXParseException)
    
    //
    // Protected methods
    //
    
    /** Prints the error message. */
    protected void printError(String type, SAXParseException ex) {

        System.err.print("[");
        System.err.print(type);
        System.err.print("] ");
        String systemId = ex.getSystemId();
        if (systemId != null) {
            int index = systemId.lastIndexOf('/');
            if (index != -1)
                systemId = systemId.substring(index + 1);
            System.err.print(systemId);
        }
        System.err.print(':');
        System.err.print(ex.getLineNumber());
        System.err.print(':');
        System.err.print(ex.getColumnNumber());
        System.err.print(": ");
        System.err.print(ex.getMessage());
        System.err.println();
        System.err.flush();

    } // printError(String,SAXParseException)
    
    //
    // MAIN
    //

    /** Main program entry point. */
    public static void main (String [] argv) {
        
        // is there anything to do?
        if (argv.length == 0) {
            printUsage();
            System.exit(1);
        }
        
        // variables
        Vector schemas = null;
        Vector instances = null;
        String schemaLanguage = DEFAULT_SCHEMA_LANGUAGE;
        int repetition = DEFAULT_REPETITION;
        String validationSource = DEFAULT_VALIDATION_SOURCE;
        boolean schemaFullChecking = DEFAULT_SCHEMA_FULL_CHECKING;
        boolean honourAllSchemaLocations = DEFAULT_HONOUR_ALL_SCHEMA_LOCATIONS;
        boolean validateAnnotations = DEFAULT_VALIDATE_ANNOTATIONS;
        boolean generateSyntheticAnnotations = DEFAULT_GENERATE_SYNTHETIC_ANNOTATIONS;
        boolean memoryUsage = DEFAULT_MEMORY_USAGE;
        
        // process arguments
        for (int i = 0; i < argv.length; ++i) {
            String arg = argv[i];
            if (arg.startsWith("-")) {
                String option = arg.substring(1);
                if (option.equals("l")) {
                    // get schema language name
                    if (++i == argv.length) {
                        System.err.println("error: Missing argument to -l option.");
                    }
                    else {
                        schemaLanguage = argv[i];
                    }
                    continue;
                }
                if (option.equals("x")) {
                    if (++i == argv.length) {
                        System.err.println("error: Missing argument to -x option.");
                        continue;
                    }
                    String number = argv[i];
                    try {
                        int value = Integer.parseInt(number);
                        if (value < 1) {
                            System.err.println("error: Repetition must be at least 1.");
                            continue;
                        }
                        repetition = value;
                    }
                    catch (NumberFormatException e) {
                        System.err.println("error: invalid number ("+number+").");
                    }
                    continue;
                }
                if (arg.equals("-a")) {
                    // process -a: schema documents
                    if (schemas == null) {
                        schemas = new Vector();
                    }
                    while (i + 1 < argv.length && !(arg = argv[i + 1]).startsWith("-")) {
                        schemas.add(arg);
                        ++i;
                    }
                    continue;
                }
                if (arg.equals("-i")) {
                    // process -i: instance documents
                    if (instances == null) {
                        instances = new Vector();
                    }
                    while (i + 1 < argv.length && !(arg = argv[i + 1]).startsWith("-")) {
                        instances.add(arg);
                        ++i;
                    }
                    continue;
                }
                if (arg.equals("-vs")) {
                    if (i + 1 < argv.length && !(arg = argv[i + 1]).startsWith("-")) {
                        if (arg.equals("sax") || arg.equals("dom") || arg.equals("stax") || arg.equals("stream")) {
                            validationSource = arg;
                        }
                        else {
                            System.err.println("error: unknown source type ("+arg+").");
                        }
                    }
                    continue;
                }
                if (option.equalsIgnoreCase("f")) {
                    schemaFullChecking = option.equals("f");
                    continue;
                }
                if (option.equalsIgnoreCase("hs")) {
                    honourAllSchemaLocations = option.equals("hs");
                    continue;
                }
                if (option.equalsIgnoreCase("va")) {
                    validateAnnotations = option.equals("va");
                    continue;
                }
                if (option.equalsIgnoreCase("ga")) {
                    generateSyntheticAnnotations = option.equals("ga");
                    continue;
                }
                if (option.equalsIgnoreCase("m")) {
                    memoryUsage = option.equals("m");
                    continue;
                }
                if (option.equals("h")) {
                    printUsage();
                    continue;
                }
                System.err.println("error: unknown option ("+option+").");
                continue;
            }
        }
        
        try {
            // Create new instance of SourceValidator.
            SourceValidator sourceValidator = new SourceValidator();
            
            // Create SchemaFactory and configure
            SchemaFactory factory = SchemaFactory.newInstance(schemaLanguage);
            factory.setErrorHandler(sourceValidator);
            
            try {
                factory.setFeature(SCHEMA_FULL_CHECKING_FEATURE_ID, schemaFullChecking);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: SchemaFactory does not recognize feature ("+SCHEMA_FULL_CHECKING_FEATURE_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: SchemaFactory does not support feature ("+SCHEMA_FULL_CHECKING_FEATURE_ID+")");
            }
            try {
                factory.setFeature(HONOUR_ALL_SCHEMA_LOCATIONS_ID, honourAllSchemaLocations);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: SchemaFactory does not recognize feature ("+HONOUR_ALL_SCHEMA_LOCATIONS_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: SchemaFactory does not support feature ("+HONOUR_ALL_SCHEMA_LOCATIONS_ID+")");
            }
            try {
                factory.setFeature(VALIDATE_ANNOTATIONS_ID, validateAnnotations);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: SchemaFactory does not recognize feature ("+VALIDATE_ANNOTATIONS_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: SchemaFactory does not support feature ("+VALIDATE_ANNOTATIONS_ID+")");
            }
            try {
                factory.setFeature(GENERATE_SYNTHETIC_ANNOTATIONS_ID, generateSyntheticAnnotations);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: SchemaFactory does not recognize feature ("+GENERATE_SYNTHETIC_ANNOTATIONS_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: SchemaFactory does not support feature ("+GENERATE_SYNTHETIC_ANNOTATIONS_ID+")");
            }
            
            // Build Schema from sources
            Schema schema;
            if (schemas != null && schemas.size() > 0) {
                final int length = schemas.size();
                StreamSource[] sources = new StreamSource[length];
                for (int j = 0; j < length; ++j) {
                    sources[j] = new StreamSource((String) schemas.elementAt(j));
                }
                schema = factory.newSchema(sources);
            }
            else {
                schema = factory.newSchema();
            }
            
            // Setup validator and input source.
            Validator validator = schema.newValidator();
            validator.setErrorHandler(sourceValidator);
            
            try {
                validator.setFeature(SCHEMA_FULL_CHECKING_FEATURE_ID, schemaFullChecking);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Validator does not recognize feature ("+SCHEMA_FULL_CHECKING_FEATURE_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Validator does not support feature ("+SCHEMA_FULL_CHECKING_FEATURE_ID+")");
            }
            try {
                validator.setFeature(HONOUR_ALL_SCHEMA_LOCATIONS_ID, honourAllSchemaLocations);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Validator does not recognize feature ("+HONOUR_ALL_SCHEMA_LOCATIONS_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Validator does not support feature ("+HONOUR_ALL_SCHEMA_LOCATIONS_ID+")");
            }
            try {
                validator.setFeature(VALIDATE_ANNOTATIONS_ID, validateAnnotations);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Validator does not recognize feature ("+VALIDATE_ANNOTATIONS_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Validator does not support feature ("+VALIDATE_ANNOTATIONS_ID+")");
            }
            try {
                validator.setFeature(GENERATE_SYNTHETIC_ANNOTATIONS_ID, generateSyntheticAnnotations);
            }
            catch (SAXNotRecognizedException e) {
                System.err.println("warning: Validator does not recognize feature ("+GENERATE_SYNTHETIC_ANNOTATIONS_ID+")");
            }
            catch (SAXNotSupportedException e) {
                System.err.println("warning: Validator does not support feature ("+GENERATE_SYNTHETIC_ANNOTATIONS_ID+")");
            }

            // Validate instance documents
            if (instances != null && instances.size() > 0) {
                final int length = instances.size();
                if (validationSource.equals("sax")) {
                    // SAXSource
                    XMLReader reader = XMLReaderFactory.createXMLReader();
                    reader.setErrorHandler(sourceValidator);
                    for (int j = 0; j < length; ++j) {
                        String systemId = (String) instances.elementAt(j);
                        SAXSource source = new SAXSource(reader, new InputSource(systemId));
                        sourceValidator.validate(validator, source, systemId, repetition, memoryUsage);
                    }
                }
                else if (validationSource.equals("dom")) {
                    // DOMSource
                    DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
                    dbf.setNamespaceAware(true);
                    DocumentBuilder db = dbf.newDocumentBuilder();
                    db.setErrorHandler(sourceValidator);
                    for (int j = 0; j < length; ++j) {
                        String systemId = (String) instances.elementAt(j);
                        Document doc = db.parse(systemId);
                        DOMSource source = new DOMSource(doc);
                        source.setSystemId(systemId);
                        sourceValidator.validate(validator, source, systemId, repetition, memoryUsage);
                    }
                }
                else if (validationSource.equals("stax")) {
                    // StAXSource
                    XMLInputFactory xif = XMLInputFactory.newInstance();
                    try {
                        // Enable reporting of column and line numbers in XMLStreamReaders which support it.
                        xif.setProperty(IS_SUPPORTING_LOCATION_COORDINATES, Boolean.TRUE);
                    }
                    catch (IllegalArgumentException e) {}
                    for (int j = 0; j < length; ++j) {
                        String systemId = (String) instances.elementAt(j);
                        sourceValidator.validate(validator, xif, systemId, repetition, memoryUsage);
                    }
                }
                else {
                    // StreamSource
                    for (int j = 0; j < length; ++j) {
                        String systemId = (String) instances.elementAt(j);
                        StreamSource source = new StreamSource(systemId);
                        sourceValidator.validate(validator, source, systemId, repetition, memoryUsage);
                    }
                }
            }
        }
        catch (SAXParseException e) {
            // ignore
        }
        catch (Exception e) {
            System.err.println("error: Parse error occurred - "+e.getMessage());
            if (e instanceof SAXException) {
                Exception nested = ((SAXException)e).getException();
                if (nested != null) {
                    e = nested;
                } 
            }
            e.printStackTrace(System.err);
        }
    } // main(String[])
    
    //
    // Private static methods
    //
    
    /** Prints the usage. */
    private static void printUsage() {
        
        System.err.println("usage: java jaxp.SourceValidator (options) ...");
        System.err.println();
        
        System.err.println("options:");
        System.err.println("  -l name     Select schema language by name.");
        System.err.println("  -x number   Select number of repetitions.");
        System.err.println("  -a uri ...  Provide a list of schema documents");
        System.err.println("  -i uri ...  Provide a list of instance documents to validate");
        System.err.println("  -vs source  Select validation source (sax|dom|stax|stream)");
        System.err.println("  -f  | -F    Turn on/off Schema full checking.");
        System.err.println("              NOTE: Not supported by all schema factories and validators.");
        System.err.println("  -hs | -HS   Turn on/off honouring of all schema locations.");
        System.err.println("              NOTE: Not supported by all schema factories and validators.");
        System.err.println("  -va | -VA   Turn on/off validation of schema annotations.");
        System.err.println("              NOTE: Not supported by all schema factories and validators.");
        System.err.println("  -ga | -GA   Turn on/off generation of synthetic schema annotations.");
        System.err.println("              NOTE: Not supported by all schema factories and validators.");
        System.err.println("  -m  | -M    Turn on/off memory usage report");
        System.err.println("  -h          This help screen.");
        
        System.err.println();
        System.err.println("defaults:");
        System.err.println("  Schema language:                 " + DEFAULT_SCHEMA_LANGUAGE);
        System.err.println("  Repetition:                      " + DEFAULT_REPETITION);
        System.err.println("  Validation source:               " + DEFAULT_VALIDATION_SOURCE);
        System.err.print("  Schema full checking:            ");
        System.err.println(DEFAULT_SCHEMA_FULL_CHECKING ? "on" : "off");
        System.err.print("  Honour all schema locations:     ");
        System.err.println(DEFAULT_HONOUR_ALL_SCHEMA_LOCATIONS ? "on" : "off");
        System.err.print("  Validate annotations:            ");
        System.err.println(DEFAULT_VALIDATE_ANNOTATIONS ? "on" : "off");
        System.err.print("  Generate synthetic annotations:  ");
        System.err.println(DEFAULT_GENERATE_SYNTHETIC_ANNOTATIONS ? "on" : "off");
        System.err.print("  Memory:                          ");
        System.err.println(DEFAULT_MEMORY_USAGE ? "on" : "off");
        
        System.err.println();
        System.err.println("notes:");
        System.err.println("  The speed and memory results from this program should NOT be used as the");
        System.err.println("  basis of parser performance comparison! Real analytical methods should be");
        System.err.println("  used. For better results, perform multiple document validations within the");
        System.err.println("  same virtual machine to remove class loading from parse time and memory usage.");
        
    } // printUsage()

} // class SourceValidator