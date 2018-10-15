private boolean expandEntityRef = true;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 1999-2000, Pierpaolo
 * Fumagalli <mailto:pier@betaversion.org>, http://www.apache.org.
 * For more information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package javax.xml.parsers;

import java.io.InputStream;
import java.io.IOException;
import java.io.File;
import java.io.FileInputStream;

import java.util.Properties;
import java.io.BufferedReader;
import java.io.InputStreamReader;

/**
 * The <code>DocumentBuilderFactory</code> defines a factory API that enables
 * applications to configure and obtain a parser to parse XML documents into
 * a DOM Document tree.
 * <br>
 * <br>
 * <b>ATTENTION:</b> THIS IMPLEMENTATION OF THE "JAVAX.XML.PARSER" CLASSES
 *   IS NOT THE OFFICIAL REFERENCE IMPLEMENTATION OF THE JAVA SPECIFICATION
 *   REQUEST 5 FOUND AT
 *   <a href="http://java.sun.com/aboutJava/communityprocess/jsr/jsr_005_xml.html">
 *   http://java.sun.com/aboutJava/communityprocess/jsr/jsr_005_xml.html
 *   </a><br>
 *   THIS IMPLEMENTATION IS CONFORMANT TO THE "JAVA API FOR XML PARSING"
 *   SPECIFICATION VERSION 1.1 PUBLIC REVIEW 1 BY JAMES DUNCAN DAVIDSON
 *   PUBLISHED BY SUN MICROSYSTEMS ON NOV. 2, 2000 AND FOUND AT
 *   <a href="http://java.sun.com/xml">http://java.sun.com/xml</a>
 * <br>
 * <br>
 * <b>THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
 * EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * @author <a href="pier@betaversion.org">Pierpaolo Fumagalli</a>
 * @author Copyright &copy; 2000 The Apache Software Foundation.
 * @version 1.0 CVS $Revision$ $Date$
 */
public abstract class DocumentBuilderFactory {
    /** The default property name according to the JAXP spec */
    private static final String defaultPropName =
        "javax.xml.parsers.DocumentBuilderFactory";

    private boolean validating = false;
    private boolean namespaceAware = false;
    private boolean whitespace = false;
    private boolean expandEntityRef = false;
    private boolean ignoreComments = false;
    private boolean coalescing = false;
    
    protected DocumentBuilderFactory () {
    
    }

    /**
     * Obtain a new instance of a
     * <code>DocumentBuilderFactory</code>. This static method creates
     * a new factory instance based on a System property setting or
     * uses the platform default if no property has been defined.<p>
     *
     * The system property that controls which Factory implementation
     * to create is named
     * &quot;javax.xml.parsers.DocumentBuilderFactory&quot;. This
     * property names a class that is a concrete subclass of this
     * abstract class. If no property is defined, a platform default
     * will be used.<p>
     *
     * Once an application has obtained a reference to a
     * <code>DocumentBuilderFactory</code> it can use the factory to
     * configure and obtain parser instances.
     *
     * @exception FactoryConfigurationError if the implementation is not
     * available or cannot be instantiated.
     */    
    
    public static DocumentBuilderFactory newInstance() {
	String factoryImplName = findFactory(defaultPropName,
					     "org.apache.xerces.jaxp.DocumentBuilderFactoryImpl");
	// the default can be removed after services are tested well enough

        if (factoryImplName == null) {
            throw new FactoryConfigurationError(
                "No default implementation found");
        }

        DocumentBuilderFactory factoryImpl;
        try {
            Class clazz = Class.forName(factoryImplName);
            factoryImpl = (DocumentBuilderFactory)clazz.newInstance();
        } catch  (ClassNotFoundException cnfe) {
	    throw new FactoryConfigurationError(cnfe);
	} catch (IllegalAccessException iae) {
	    throw new FactoryConfigurationError(iae);
	} catch (InstantiationException ie) {
	    throw new FactoryConfigurationError(ie);
	}
        return factoryImpl;
    }
    
    /**
     * Creates a new instance of a DocumentBuilder using the
     * currently configured parameters.
     *
     * @exception ParserConfigurationException if a DocumentBuilder
     * cannot be created which satisfies the configuration requested
     */
    
    public abstract DocumentBuilder newDocumentBuilder()
        throws ParserConfigurationException;
    
    
    /**
     * Specifies that the parser produced by this code will
     * provide support for XML namespaces.
     */
    
    public void setNamespaceAware(boolean awareness) {
        this.namespaceAware = awareness;
    }

    /**
     * Specifies that the parser produced by this code will
     * validate documents as they are parsed.
     */
    
    public void setValidating(boolean validating) {
        this.validating = validating;
    }

    /**
     * Specifies that the parser produced by this code will
     * ignore "ignorable whitespace" ONLY when the document is validated as 
     * they are parsed.
     */
    
    public void setIgnoringElementContentWhitespace(boolean whitespace) {
        this.whitespace = whitespace;
    }

    /**
     * Specifies that the parser produced by this code will
     * expand entity reference nodes.
     */
    
    public void setExpandEntityReferences(boolean expandEntityRef) {
        this.expandEntityRef = expandEntityRef;
    }

    /**
     * Specifies that the parser produced by this code will
     * ignore comments.
     */
    
    public void setIgnoringComments(boolean ignoreComments) {
        this.ignoreComments = ignoreComments;
    }

    /**
     * Specifies that the parser produced by this code will
     * convert CDATA nodes to Text nodes and append it to the 
     * adjacent (if any) text node.
     */
    
    public void setCoalescing(boolean coalescing) {
        this.coalescing = coalescing;
    }

    /**
     * Indicates whether or not the factory is configured to produce
     * parsers which are namespace aware.
     */
    
    public boolean isNamespaceAware() {
        return namespaceAware;
    }

    /**
     * Indicates whether or not the factory is configured to produce
     * parsers which validate the XML content during parse.
     */
    
    public boolean isValidating() {
        return validating;
    }

    /**
     * Indicates whether or not the factory is configured to produce
     * parsers which ignore "ignorable whitespace" when validated in the XML 
     * content during parse.
     */
    
    public boolean isIgnoringElementContentWhitespace() {
        return whitespace;
    }

    /**
     * Indicates whether or not the factory is configured to produce
     * parsers which expand entity reference nodes.
     */
    
    public boolean isExpandEntityReferences() {
        return expandEntityRef;
    }

    /**
     * Indicates whether or not the factory is configured to produce
     * parsers which ignores comments.
     */
    
    public boolean isIgnoringComments() {
        return ignoreComments;
    }

    /**
     * Indicates whether or not the factory is configured to produce
     * parsers which converts CDATA nodes to Text nodes and appends it to
     * the adjacent (if any) Text node.
     */
    
    public boolean isCoalescing() {
        return coalescing;
    }

    /**
     * Allows the user to set specific attributes on the underlying 
     * implementation.
     * @param name The name of the attribute.
     * @param value The value of the attribute.
     * @exception IllegalArgumentException thrown if the underlying 
     * implementation doesn't recognize the attribute.
     */
    public abstract void setAttribute(String name, Object value) 
    			throws IllegalArgumentException;

    /**
     * Allows the user to retrieve specific attributes on the underlying 
     * implementation.
     * @param name The name of the attribute.
     * @return value The value of the attribute.
     * @exception IllegalArgumentException thrown if the underlying 
     * implementation doesn't recognize the attribute.
     */
    public abstract Object getAttribute(String name)
    			throws IllegalArgumentException;
    
    // -------------------- private methods --------------------
    // This code is duplicated in all factories.
    // Keep it in sync or move it to a common place 
    // Because it's small probably it's easier to keep it here
    /** Avoid reading all the files when the findFactory
	method is called the second time ( cache the result of
	finding the default impl )
    */
    private static String foundFactory=null;

    /** Temp debug code - this will be removed after we test everything
     */
    private static final boolean debug=
	System.getProperty( "jaxp.debug" ) != null;

    /** Private implementation method - will find the implementation
	class in the specified order.
	@param factoryId   Name of the factory interface
	@param xmlProperties Name of the properties file based on JAVA/lib
	@param defaultFactory Default implementation, if nothing else is found
    */
    private static String findFactory(String factoryId, 
				      String defaultFactory)
    {
	// Use the system property first
	try {
	    String systemProp =
                System.getProperty( factoryId );
	    if( systemProp!=null) {
		if( debug ) 
		    System.err.println("JAXP: found system property" +
				       systemProp );
		return systemProp;
	    }
	    
	}catch (SecurityException se) {
	}

	if( foundFactory!=null)
	    return foundFactory;
	
	// try to read from $java.home/lib/xml.properties
	try {
	    String javah=System.getProperty( "java.home" );
	    String configFile = javah + File.separator +
		"lib" + File.separator + "jaxp.properties";
	    File f=new File( configFile );
	    if( f.exists()) {
		Properties props=new Properties();
		props.load( new FileInputStream(f));
		foundFactory=props.getProperty( factoryId );
		if( debug )
		    System.err.println("JAXP: found java.home property " +
				       foundFactory );
		if(foundFactory!=null )
		    return foundFactory;
	    }
	} catch(Exception ex ) {
	    if( debug ) ex.printStackTrace();
	}

	String serviceId = "META-INF/services/" + factoryId;
	// try to find services in CLASSPATH
	try {
	    ClassLoader cl=DocumentBuilderFactory.class.getClassLoader();
	    InputStream is=null;
	    if( cl == null ) {
		is=ClassLoader.getSystemResourceAsStream( serviceId );
	    } else {
		is=cl.getResourceAsStream( serviceId );
	    }
	    
	    if( is!=null ) {
		if( debug )
		    System.err.println("JAXP: found  " +
				       serviceId);
		BufferedReader rd=new BufferedReader( new
		    InputStreamReader(is));
		
		foundFactory=rd.readLine();
		rd.close();

		if( debug )
		    System.err.println("JAXP: loaded from services: " +
				       foundFactory );
		if( foundFactory != null &&
		    !  "".equals( foundFactory) ) {
		    return foundFactory;
		}
	    }
	} catch( Exception ex ) {
	    if( debug ) ex.printStackTrace();
	}

	return defaultFactory;
    }

}