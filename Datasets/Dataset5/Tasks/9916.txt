fElementRecurseComplex.clear();


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
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */
package org.apache.xerces.validators.schema;

import  org.apache.xerces.framework.XMLErrorReporter;
import  org.apache.xerces.validators.common.Grammar;
import  org.apache.xerces.validators.common.GrammarResolver;
import  org.apache.xerces.validators.common.GrammarResolverImpl;
import  org.apache.xerces.validators.common.XMLElementDecl;
import  org.apache.xerces.validators.common.XMLAttributeDecl;
import  org.apache.xerces.validators.schema.SchemaSymbols;
import  org.apache.xerces.validators.schema.XUtil;
import  org.apache.xerces.validators.datatype.DatatypeValidator;
import  org.apache.xerces.validators.datatype.DatatypeValidatorRegistry;
import  org.apache.xerces.validators.datatype.InvalidDatatypeValueException;
import  org.apache.xerces.utils.StringPool;
import  org.w3c.dom.Element;

//REVISIT: for now, import everything in the DOM package
import  org.w3c.dom.*;
import java.util.*;
import java.net.URL;
import java.net.MalformedURLException;

//Unit Test 
import  org.apache.xerces.parsers.DOMParser;
import  org.apache.xerces.validators.common.XMLValidator;
import  org.apache.xerces.validators.datatype.*;

import  org.apache.xerces.validators.datatype.DatatypeValidator;
import  org.apache.xerces.validators.datatype.InvalidDatatypeValueException;
import  org.apache.xerces.framework.XMLContentSpec;
import  org.apache.xerces.utils.QName;
import  org.apache.xerces.utils.NamespacesScope;
import  org.apache.xerces.parsers.SAXParser;
import  org.apache.xerces.framework.XMLParser;
import  org.apache.xerces.framework.XMLDocumentScanner;

import  org.xml.sax.InputSource;
import  org.xml.sax.SAXParseException;
import  org.xml.sax.EntityResolver;
import  org.xml.sax.ErrorHandler;
import  org.xml.sax.SAXException;
import  java.io.IOException;
import  org.w3c.dom.Document;
import  org.apache.xml.serialize.OutputFormat;
import  org.apache.xml.serialize.XMLSerializer;
import  org.apache.xerces.validators.schema.SchemaSymbols;




/**
 * Instances of this class get delegated to Traverse the Schema and
 * to populate the Grammar internal representation by
 * instances of Grammar objects.
 * Traverse a Schema Grammar:
     * As of April 07, 2000 the following is the
     * XML Representation of Schemas and Schema components,
     * Chapter 4 of W3C Working Draft.
     * <schema 
     *   attributeFormDefault = qualified | unqualified 
     *   blockDefault = #all or (possibly empty) subset of {equivClass, extension, restriction} 
     *   elementFormDefault = qualified | unqualified 
     *   finalDefault = #all or (possibly empty) subset of {extension, restriction} 
     *   id = ID 
     *   targetNamespace = uriReference 
     *   version = string>
     *   Content: ((include | import | annotation)* , ((simpleType | complexType | element | group | attribute | attributeGroup | notation) , annotation*)+)
     * </schema>
     * 
     * 
     * <attribute 
     *   form = qualified | unqualified 
     *   id = ID 
     *   name = NCName 
     *   ref = QName 
     *   type = QName 
     *   use = default | fixed | optional | prohibited | required 
     *   value = string>
     *   Content: (annotation? , simpleType?)
     * </>
     * 
     * <element 
     *   abstract = boolean 
     *   block = #all or (possibly empty) subset of {equivClass, extension, restriction} 
     *   default = string 
     *   equivClass = QName 
     *   final = #all or (possibly empty) subset of {extension, restriction} 
     *   fixed = string 
     *   form = qualified | unqualified 
     *   id = ID 
     *   maxOccurs = string 
     *   minOccurs = nonNegativeInteger 
     *   name = NCName 
     *   nullable = boolean 
     *   ref = QName 
     *   type = QName>
     *   Content: (annotation? , (simpleType | complexType)? , (unique | key | keyref)*)
     * </>
     * 
     * 
     * <complexType 
     *   abstract = boolean 
     *   base = QName 
     *   block = #all or (possibly empty) subset of {extension, restriction} 
     *   content = elementOnly | empty | mixed | textOnly 
     *   derivedBy = extension | restriction 
     *   final = #all or (possibly empty) subset of {extension, restriction} 
     *   id = ID 
     *   name = NCName>
     *   Content: (annotation? , (((minExclusive | minInclusive | maxExclusive | maxInclusive | precision | scale | length | minLength | maxLength | encoding | period | duration | enumeration | pattern)* | (element | group | all | choice | sequence | any)*) , ((attribute | attributeGroup)* , anyAttribute?)))
     * </>
     * 
     * 
     * <attributeGroup 
     *   id = ID 
     *   name = NCName
     *   ref = QName>
     *   Content: (annotation?, (attribute|attributeGroup), anyAttribute?)
     * </>
     * 
     * <anyAttribute 
     *   id = ID 
     *   namespace = ##any | ##other | ##local | list of {uri, ##targetNamespace}>
     *   Content: (annotation?)
     * </anyAttribute>
     * 
     * <group 
     *   id = ID 
     *   maxOccurs = string 
     *   minOccurs = nonNegativeInteger 
     *   name = NCName 
     *   ref = QName>
     *   Content: (annotation? , (element | group | all | choice | sequence | any)*)
     * </>
     * 
     * <all 
     *   id = ID 
     *   maxOccurs = string 
     *   minOccurs = nonNegativeInteger>
     *   Content: (annotation? , (element | group | choice | sequence | any)*)
     * </all>
     * 
     * <choice 
     *   id = ID 
     *   maxOccurs = string 
     *   minOccurs = nonNegativeInteger>
     *   Content: (annotation? , (element | group | choice | sequence | any)*)
     * </choice>
     * 
     * <sequence 
     *   id = ID 
     *   maxOccurs = string 
     *   minOccurs = nonNegativeInteger>
     *   Content: (annotation? , (element | group | choice | sequence | any)*)
     * </sequence>
     * 
     * 
     * <any 
     *   id = ID 
     *   maxOccurs = string 
     *   minOccurs = nonNegativeInteger 
     *   namespace = ##any | ##other | ##local | list of {uri, ##targetNamespace} 
     *   processContents = lax | skip | strict>
     *   Content: (annotation?)
     * </any>
     * 
     * <unique 
     *   id = ID 
     *   name = NCName>
     *   Content: (annotation? , (selector , field+))
     * </unique>
     * 
     * <key 
     *   id = ID 
     *   name = NCName>
     *   Content: (annotation? , (selector , field+))
     * </key>
     * 
     * <keyref 
     *   id = ID 
     *   name = NCName 
     *   refer = QName>
     *   Content: (annotation? , (selector , field+))
     * </keyref>
     * 
     * <selector>
     *   Content: XPathExprApprox : An XPath expression 
     * </selector>
     * 
     * <field>
     *   Content: XPathExprApprox : An XPath expression 
     * </field>
     * 
     * 
     * <notation 
     *   id = ID 
     *   name = NCName 
     *   public = A public identifier, per ISO 8879 
     *   system = uriReference>
     *   Content: (annotation?)
     * </notation>
     * 
     * <annotation>
     *   Content: (appinfo | documentation)*
     * </annotation>
     * 
     * <include 
     *   id = ID 
     *   schemaLocation = uriReference>
     *   Content: (annotation?)
     * </include>
     * 
     * <import 
     *   id = ID 
     *   namespace = uriReference 
     *   schemaLocation = uriReference>
     *   Content: (annotation?)
     * </import>
     * 
     * <simpleType
     *   abstract = boolean 
     *   base = QName 
     *   derivedBy = | list | restriction  : restriction
     *   id = ID 
     *   name = NCName>
     *   Content: ( annotation? , ( minExclusive | minInclusive | maxExclusive | maxInclusive | precision | scale | length | minLength | maxLength | encoding | period | duration | enumeration | pattern )* )
     * </simpleType>
     * 
     * <length
     *   id = ID 
     *   value = nonNegativeInteger>
     *   Content: ( annotation? )
     * </length>
     * 
     * <minLength
     *   id = ID 
     *   value = nonNegativeInteger>
     *   Content: ( annotation? )
     * </minLength>
     * 
     * <maxLength
     *   id = ID 
     *   value = nonNegativeInteger>
     *   Content: ( annotation? )
     * </maxLength>
     * 
     * 
     * <pattern
     *   id = ID 
     *   value = string>
     *   Content: ( annotation? )
     * </pattern>
     * 
     * 
     * <enumeration
     *   id = ID 
     *   value = string>
     *   Content: ( annotation? )
     * </enumeration>
     * 
     * <maxInclusive
     *   id = ID 
     *   value = string>
     *   Content: ( annotation? )
     * </maxInclusive>
     * 
     * <maxExclusive
     *   id = ID 
     *   value = string>
     *   Content: ( annotation? )
     * </maxExclusive>
     * 
     * <minInclusive
     *   id = ID 
     *   value = string>
     *   Content: ( annotation? )
     * </minInclusive>
     * 
     * 
     * <minExclusive
     *   id = ID 
     *   value = string>
     *   Content: ( annotation? )
     * </minExclusive>
     * 
     * <precision
     *   id = ID 
     *   value = nonNegativeInteger>
     *   Content: ( annotation? )
     * </precision>
     * 
     * <scale
     *   id = ID 
     *   value = nonNegativeInteger>
     *   Content: ( annotation? )
     * </scale>
     * 
     * <encoding
     *   id = ID 
     *   value = | hex | base64 >
     *   Content: ( annotation? )
     * </encoding>
     * 
     * 
     * <duration
     *   id = ID 
     *   value = timeDuration>
     *   Content: ( annotation? )
     * </duration>
     * 
     * <period
     *   id = ID 
     *   value = timeDuration>
     *   Content: ( annotation? )
     * </period>
     * 
 * 
 * @author Jeffrey Rodriguez
 *         Eric Ye
 * @see                  org.apache.xerces.validators.common.Grammar
 *
 * @version $Id$
 */

public class TraverseSchema implements 
                            NamespacesScope.NamespacesHandler{

    
    //CONSTANTS
    private static final int TOP_LEVEL_SCOPE = -1;

    //debuggin
    private static boolean DEBUGGING = false;

    //private data members


    private XMLErrorReporter    fErrorReporter = null;
    private StringPool          fStringPool    = null;

    private GrammarResolver fGrammarResolver = null;
    private SchemaGrammar fSchemaGrammar = null;

    private Element fSchemaRootElement;

    private DatatypeValidatorRegistry fDatatypeRegistry =
                                             DatatypeValidatorRegistry.getDatatypeRegistry();
    private Hashtable fComplexTypeRegistry = new Hashtable();
    private Hashtable fAttributeDeclRegistry = new Hashtable();

    private Vector fIncludeLocations = new Vector();
    private Vector fImportLocations = new Vector();


    private int fAnonTypeCount =0;
    private int fScopeCount=0;
    private int fCurrentScope=TOP_LEVEL_SCOPE;
    private int fSimpleTypeAnonCount = 0;
    private Stack fCurrentTypeNameStack = new Stack();
    private Hashtable fElementRecurseComplex = new Hashtable();

    private boolean fDefaultQualified = false;
    private int fTargetNSURI;
    private String fTargetNSURIString = "";
    private NamespacesScope fNamespacesScope = null;
    private String fCurrentSchemaURL = "";

    private XMLAttributeDecl fTempAttributeDecl = new XMLAttributeDecl();

    // REVISIT: maybe need to be moved into SchemaGrammar class
    public class ComplexTypeInfo {
        public String typeName;
        
        public DatatypeValidator baseDataTypeValidator;
        public ComplexTypeInfo baseComplexTypeInfo;
        public int derivedBy;
        public int blockSet;
        public int finalSet;

        public int scopeDefined = -1;

        public int contentType;
        public int contentSpecHandle = -1;
        public int templateElementIndex = -1;
        public int attlistHead = -1;
        public DatatypeValidator datatypeValidator;
    }


    //REVISIT: verify the URI.
    public final static String SchemaForSchemaURI = "http://www.w3.org/TR-1/Schema";

    private TraverseSchema( ) {
        // new TraverseSchema() is forbidden;
    }


    public void setGrammarResolver(GrammarResolver grammarResolver){
        fGrammarResolver = grammarResolver;
    }
    public void startNamespaceDeclScope(int prefix, int uri){
        //TO DO
    }
    public void endNamespaceDeclScope(int prefix){
        //TO DO, do we need to do anything here?
    }

    

    private String resolvePrefixToURI (String prefix) throws Exception  {
        String uriStr = fStringPool.toString(fNamespacesScope.getNamespaceForPrefix(fStringPool.addSymbol(prefix)));
        if (uriStr == null) {
            reportGenericSchemaError("prefix : [" + prefix +"] can not be resolved to a URI");
        }
        return uriStr;
    }

    public  TraverseSchema(Element root, StringPool stringPool, 
                           SchemaGrammar schemaGrammar, 
                           GrammarResolver grammarResolver,
                           XMLErrorReporter errorReporter,
                           String schemaURL
                           ) throws Exception {
        fErrorReporter = errorReporter;
        fCurrentSchemaURL = schemaURL;
        doTraverseSchema(root, stringPool, schemaGrammar, grammarResolver);
    }

    public  TraverseSchema(Element root, StringPool stringPool, 
                           SchemaGrammar schemaGrammar, 
                           GrammarResolver grammarResolver
                           ) throws Exception {
        doTraverseSchema(root, stringPool, schemaGrammar, grammarResolver);
    }

    public  void doTraverseSchema(Element root, StringPool stringPool, 
                           SchemaGrammar schemaGrammar, 
                           GrammarResolver grammarResolver) throws Exception {

        fNamespacesScope = new NamespacesScope(this);
        
        fSchemaRootElement = root;
        fStringPool = stringPool;
        fSchemaGrammar = schemaGrammar;
        fGrammarResolver = grammarResolver;

        if (root == null) { 
            // REVISIT: Anything to do?
            return;
        }

        //Retrieve the targetnamespace URI information
        fTargetNSURIString = root.getAttribute(SchemaSymbols.ATT_TARGETNAMESPACE);
        if (fTargetNSURIString==null) {
            fTargetNSURIString="";
        }
        fTargetNSURI = fStringPool.addSymbol(fTargetNSURIString);

        if (fGrammarResolver == null) {
            reportGenericSchemaError("Internal error: don't have a GrammarResolver for TraverseSchema");
        }
        else{
            fSchemaGrammar.setComplexTypeRegistry(fComplexTypeRegistry);
            fSchemaGrammar.setDatatypeRegistry(fDatatypeRegistry);
            fSchemaGrammar.setAttributeDeclRegistry(fAttributeDeclRegistry);
            fGrammarResolver.putGrammar(fTargetNSURIString, fSchemaGrammar);
        }
        


        // Retrived the Namespace mapping from the schema element.
        NamedNodeMap schemaEltAttrs = root.getAttributes();
        int i = 0;
        Attr sattr = null;

        boolean seenXMLNS = false;                                        
        while ((sattr = (Attr)schemaEltAttrs.item(i++)) != null) {
            String attName = sattr.getName();
            if (attName.startsWith("xmlns:")) {
                String attValue = sattr.getValue();
                String prefix = attName.substring(attName.indexOf(":")+1);
                fNamespacesScope.setNamespaceForPrefix( fStringPool.addSymbol(prefix),
                                                        fStringPool.addSymbol(attValue) );
            }
            if (attName.equals("xmlns")) {

                String attValue = sattr.getValue();
                fNamespacesScope.setNamespaceForPrefix( fStringPool.addSymbol(""),
                                                        fStringPool.addSymbol(attValue) );
                seenXMLNS = true;
            }

        }
        if (!seenXMLNS && fTargetNSURIString.length() == 0 ) {
            fNamespacesScope.setNamespaceForPrefix( fStringPool.addSymbol(""),
                                                    fStringPool.addSymbol("") );
        }

        fDefaultQualified = 
            root.getAttribute(SchemaSymbols.ATT_ELEMENTFORMDEFAULT).equals(SchemaSymbols.ATTVAL_QUALIFIED);

        //fScopeCount++;
        fCurrentScope = -1;


        checkTopLevelDuplicateNames(root);

        //extract all top-level attribute, attributeGroup, and group Decls and put them in the 3 hasn table in the SchemaGrammar.
        extractTopLevel3Components(root);

        for (Element child = XUtil.getFirstChildElement(root); child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getNodeName();

            if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) {
                traverseAnnotationDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_SIMPLETYPE )) {
                traverseSimpleTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_COMPLEXTYPE )) {
                traverseComplexTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ELEMENT )) { 
                traverseElementDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                //traverseAttributeGroupDecl(child);
            } else if (name.equals( SchemaSymbols.ELT_ATTRIBUTE ) ) {
                //traverseAttributeDecl( child );
            } else if (name.equals( SchemaSymbols.ELT_WILDCARD) ) {
                traverseWildcardDecl( child);
            } else if (name.equals(SchemaSymbols.ELT_GROUP) && child.getAttribute(SchemaSymbols.ATT_REF).equals("")) {
                //traverseGroupDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_NOTATION)) {
                ; //TO DO
            }
            else if (name.equals(SchemaSymbols.ELT_INCLUDE)) {
                traverseInclude(child); 
            }
            else if (name.equals(SchemaSymbols.ELT_IMPORT)) {
                traverseImport(child); 
            }
        } // for each child node

    } // traverseSchema(Element)

    private void checkTopLevelDuplicateNames(Element root) {
        //TO DO : !!!
    }

    private void extractTopLevel3Components(Element root){
        
        for (Element child = XUtil.getFirstChildElement(root); child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getNodeName();

            if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                fSchemaGrammar.topLevelAttrGrpDecls.put(name, child);
            } else if (name.equals( SchemaSymbols.ELT_ATTRIBUTE ) ) {
                fSchemaGrammar.topLevelAttrDecls.put(name, child);
            } else if (name.equals(SchemaSymbols.ELT_GROUP) && child.getAttribute(SchemaSymbols.ATT_REF).equals("")) {
                fSchemaGrammar.topLevelGroupDecls.put(name, child);
            } 
        } // for each child node
    }

    /**
     * Expands a system id and returns the system id as a URL, if
     * it can be expanded. A return value of null means that the
     * identifier is already expanded. An exception thrown
     * indicates a failure to expand the id.
     *
     * @param systemId The systemId to be expanded.
     *
     * @return Returns the URL object representing the expanded system
     *         identifier. A null value indicates that the given
     *         system identifier is already expanded.
     *
     */
    private String expandSystemId(String systemId, String currentSystemId) throws Exception{
     String id = systemId;

     // check for bad parameters id
     if (id == null || id.length() == 0) {
         return systemId;
     }

     // if id already expanded, return
     try {
         URL url = new URL(id);
         if (url != null) {
             return systemId;
         }
     }
     catch (MalformedURLException e) {
         // continue on...
     }

     // normalize id
     id = fixURI(id);

     // normalize base
     URL base = null;
     URL url = null;
     try {
         if (currentSystemId == null) {
             String dir;
             try {
                 dir = fixURI(System.getProperty("user.dir"));
             }
             catch (SecurityException se) {
                 dir = "";
             }
             if (!dir.endsWith("/")) {
                 dir = dir + "/";
             }
             base = new URL("file", "", dir);
         }
         else {
             base = new URL(currentSystemId);
         }

         // expand id
         url = new URL(base, id);
     }
     catch (Exception e) {
         // let it go through
     }
     if (url == null) {
         return systemId;
     }
     return url.toString();
    }
    /**
     * Fixes a platform dependent filename to standard URI form.
     *
     * @param str The string to fix.
     *
     * @return Returns the fixed URI string.
     */
    private static String fixURI(String str) {

        // handle platform dependent strings
        str = str.replace(java.io.File.separatorChar, '/');

        // Windows fix
        if (str.length() >= 2) {
            char ch1 = str.charAt(1);
            if (ch1 == ':') {
                char ch0 = Character.toUpperCase(str.charAt(0));
                if (ch0 >= 'A' && ch0 <= 'Z') {
                    str = "/" + str;
                }
            }
        }

        // done
        return str;
    }


    private void traverseInclude(Element includeDecl) throws Exception {

        //TO DO: !!!!! location needs to be resolved first.

        String location = includeDecl.getAttribute(SchemaSymbols.ATT_SCHEMALOCATION);
        location = expandSystemId(location, fCurrentSchemaURL);

        if (fIncludeLocations.contains((Object)location)) {
            return;
        }
        fIncludeLocations.addElement((Object)location);

        DOMParser parser = new DOMParser() {
            public void ignorableWhitespace(char ch[], int start, int length) {}
            public void ignorableWhitespace(int dataIdx) {}
        };
        parser.setEntityResolver( new Resolver() );
        parser.setErrorHandler(  new ErrorHandler() );

        try {
            parser.setFeature("http://xml.org/sax/features/validation", false);
            parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
        }catch(  org.xml.sax.SAXNotRecognizedException e ) {
            e.printStackTrace();
        }catch( org.xml.sax.SAXNotSupportedException e ) {
            e.printStackTrace();
        }

        try {
            parser.parse( location);
        }catch( IOException e ) {
            e.printStackTrace();
        }catch( SAXException e ) {
            //e.printStackTrace();
        }

        Document     document   = parser.getDocument(); //Our Grammar
        Element root = null;
        if (document != null) {
            root = document.getDocumentElement();
        }

        if (root != null) {
            String targetNSURI = root.getAttribute(SchemaSymbols.ATT_TARGETNAMESPACE);
            if (targetNSURI.length() > 0 && !targetNSURI.equals(fTargetNSURIString) ) {
                reportGenericSchemaError("included schema '"+location+"' has a different targetNameSpace '"
                                         +targetNSURI+"'");
            }
            else {
                boolean saveDefaultQualified = fDefaultQualified;
                int saveScope = fCurrentScope;
                String savedSchemaURL = fCurrentSchemaURL;
                fCurrentSchemaURL = location;
                traverseIncludedSchema(root);
                fCurrentSchemaURL = savedSchemaURL;
                fCurrentScope = saveScope;
                fDefaultQualified = saveDefaultQualified;
            }

        }

    }

    private void traverseIncludedSchema(Element root) throws Exception {
        // Retrived the Namespace mapping from the schema element.
        NamedNodeMap schemaEltAttrs = root.getAttributes();
        int i = 0;
        Attr sattr = null;

        boolean seenXMLNS = false;                                        
        while ((sattr = (Attr)schemaEltAttrs.item(i++)) != null) {
            String attName = sattr.getName();
            if (attName.startsWith("xmlns:")) {
                String attValue = sattr.getValue();
                String prefix = attName.substring(attName.indexOf(":")+1);
                fNamespacesScope.setNamespaceForPrefix( fStringPool.addSymbol(prefix),
                                                        fStringPool.addSymbol(attValue) );
            }
            if (attName.equals("xmlns")) {

                String attValue = sattr.getValue();
                fNamespacesScope.setNamespaceForPrefix( fStringPool.addSymbol(""),
                                                        fStringPool.addSymbol(attValue) );
                seenXMLNS = true;
            }

        }
        if (!seenXMLNS && fTargetNSURIString.length() == 0 ) {
            fNamespacesScope.setNamespaceForPrefix( fStringPool.addSymbol(""),
                                                    fStringPool.addSymbol("") );
        }

        fDefaultQualified = 
            root.getAttribute(SchemaSymbols.ATT_ELEMENTFORMDEFAULT).equals(SchemaSymbols.ATTVAL_QUALIFIED);

        //fScopeCount++;
        fCurrentScope = -1;


        checkTopLevelDuplicateNames(root);

        //extract all top-level attribute, attributeGroup, and group Decls and put them in the 3 hasn table in the SchemaGrammar.
        extractTopLevel3Components(root);

        for (Element child = XUtil.getFirstChildElement(root); child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getNodeName();

            if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) {
                traverseAnnotationDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_SIMPLETYPE )) {
                traverseSimpleTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_COMPLEXTYPE )) {
                traverseComplexTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ELEMENT )) { 
                traverseElementDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                //traverseAttributeGroupDecl(child);
            } else if (name.equals( SchemaSymbols.ELT_ATTRIBUTE ) ) {
                //traverseAttributeDecl( child );
            } else if (name.equals( SchemaSymbols.ELT_WILDCARD) ) {
                traverseWildcardDecl( child);
            } else if (name.equals(SchemaSymbols.ELT_GROUP) && child.getAttribute(SchemaSymbols.ATT_REF).equals("")) {
                //traverseGroupDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_NOTATION)) {
                ; //TO DO
            }
            else if (name.equals(SchemaSymbols.ELT_INCLUDE)) {
                traverseInclude(child); 
            }
            else if (name.equals(SchemaSymbols.ELT_IMPORT)) {
                traverseImport(child); 
            }
        } // for each child node

    }

    private void traverseImport(Element importDecl)  throws Exception {
        String location = importDecl.getAttribute(SchemaSymbols.ATT_SCHEMALOCATION);
        location = expandSystemId(location, fCurrentSchemaURL);


        String namespaceString = importDecl.getAttribute(SchemaSymbols.ATT_NAMESPACE);
        SchemaGrammar importedGrammar = new SchemaGrammar();
        if (fGrammarResolver.getGrammar(namespaceString) != null) {
            importedGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(namespaceString);
        }

        if (fImportLocations.contains((Object)location)) {
            return;
        }
        fImportLocations.addElement((Object)location);

        DOMParser parser = new DOMParser() {
            public void ignorableWhitespace(char ch[], int start, int length) {}
            public void ignorableWhitespace(int dataIdx) {}
        };
        parser.setEntityResolver( new Resolver() );
        parser.setErrorHandler(  new ErrorHandler() );

        try {
            parser.setFeature("http://xml.org/sax/features/validation", false);
            parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
        }catch(  org.xml.sax.SAXNotRecognizedException e ) {
            e.printStackTrace();
        }catch( org.xml.sax.SAXNotSupportedException e ) {
            e.printStackTrace();
        }

        try {
            parser.parse( location);
        }catch( IOException e ) {
            e.printStackTrace();
        }catch( SAXException e ) {
            e.printStackTrace();
        }

        Document     document   = parser.getDocument(); //Our Grammar
        Element root = null;
        if (document != null) {
            root = document.getDocumentElement();
        }

        if (root != null) {
            String targetNSURI = root.getAttribute(SchemaSymbols.ATT_TARGETNAMESPACE);
            if (!targetNSURI.equals(namespaceString) ) {
                reportGenericSchemaError("included schema '"+location+"' has a different targetNameSpace '"
                                         +targetNSURI+"' from what is declared '"+namespaceString+"'.");
            }
            else
                new TraverseSchema(root, fStringPool, importedGrammar, fGrammarResolver, fErrorReporter, location);
        }
    }

/**
     * No-op - Traverse Annotation Declaration
     * 
     * @param comment
     */
    private void traverseAnnotationDecl(Element comment) {
        //TO DO
        return ;
    }

    /**
     * Traverse SimpleType declaration:
     * <simpleType
     *         abstract = boolean 
     *         base = QName 
     *         derivedBy = | list | restriction  : restriction
     *         id = ID 
     *         name = NCName>
     *         Content: ( annotation? , ( minExclusive | minInclusive | maxExclusive | maxInclusive | precision | scale | length | minLength | maxLength | encoding | period | duration | enumeration | pattern )* )
     *       </simpleType>
     * 
     * @param simpleTypeDecl
     * @return 
     */
    private int traverseSimpleTypeDecl( Element simpleTypeDecl ) throws Exception {
        
        String varietyProperty       =  simpleTypeDecl.getAttribute( SchemaSymbols.ATT_DERIVEDBY );
        if (varietyProperty.length() == 0) {
            varietyProperty = SchemaSymbols.ATTVAL_RESTRICTION;
        }
        String nameProperty          =  simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME );
        String baseTypeQNameProperty =  simpleTypeDecl.getAttribute( SchemaSymbols.ATT_BASE );
        String abstractProperty      =  simpleTypeDecl.getAttribute( SchemaSymbols.ATT_ABSTRACT );

        int     newSimpleTypeName    = -1;


        if ( nameProperty.equals("")) { // anonymous simpleType
            newSimpleTypeName = fStringPool.addSymbol(
                               "http://www.apache.org/xml/xerces/internalDatatype"+fSimpleTypeAnonCount++ );   
            } else 
            newSimpleTypeName       = fStringPool.addSymbol( nameProperty );


        int               basetype;
        DatatypeValidator baseValidator = null;

        if( baseTypeQNameProperty!= null ) {
            basetype      = fStringPool.addSymbol( baseTypeQNameProperty );
            baseValidator = fDatatypeRegistry.getDatatypeValidator( baseTypeQNameProperty );
            if (baseValidator == null) {
                reportSchemaError(SchemaMessageProvider.UnknownBaseDatatype,
                new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_BASE ),
                                                  simpleTypeDecl.getAttribute(SchemaSymbols.ATT_NAME) });
                return -1;
                }
        }
        // Any Children if so then check Content otherwise bail out

        Element   content   = XUtil.getFirstChildElement( simpleTypeDecl );
        int       numFacets = 0; 
        Hashtable facetData = null;

        if( content != null ) {

            //Content follows: ( annotation? , facets* )

            //annotation ? ( 0 or 1 )
            if( content.getNodeName().equals( SchemaSymbols.ELT_ANNOTATION ) ){
                traverseAnnotationDecl( content );   
                content                    = XUtil.getNextSiblingElement(content);
            } 

            //TODO: If content is annotation again should raise validation error
            // if( content.getNodeName().equal( SchemaSymbols.ELT_ANNOTATIO ) {
            //   throw ValidationException(); }
            //

            //facets    * ( 0 or more )

            
            int numEnumerationLiterals = 0;
            facetData        = new Hashtable();
            Vector enumData            = new Vector();

            while (content != null) {
                if (content.getNodeType() == Node.ELEMENT_NODE) {
                    Element facetElt = (Element) content;
                    numFacets++;
                    if (facetElt.getNodeName().equals(SchemaSymbols.ELT_ENUMERATION)) {
                        numEnumerationLiterals++;
                        String enumVal = facetElt.getAttribute(SchemaSymbols.ATT_VALUE);
                        enumData.addElement(enumVal);
                        //Enumerations can have annotations ? ( 0 | 1 )
                        Element enumContent =  XUtil.getFirstChildElement( facetElt );
                        if( enumContent != null && enumContent != null && enumContent.getNodeName().equals( SchemaSymbols.ELT_ANNOTATION ) ){
                            traverseAnnotationDecl( content );   
                         } 
                        //TODO: If enumContent is encounter  again should raise validation error
                        //  enumContent.getNextSibling();
                        // if( enumContent.getNodeName().equal( SchemaSymbols.ELT_ANNOTATIO ) {
                        //   throw ValidationException(); }
                        //
                    } else {
                    facetData.put(facetElt.getNodeName(),facetElt.getAttribute( SchemaSymbols.ATT_VALUE ));
                    }
                }
                //content = (Element) content.getNextSibling();
                content = XUtil.getNextSiblingElement(content);
            }
            if (numEnumerationLiterals > 0) {
               facetData.put(SchemaSymbols.ELT_ENUMERATION, enumData);
            }
        }

        // create & register validator for "generated" type if it doesn't exist
        try {
            DatatypeValidator newValidator = (DatatypeValidator) baseValidator.getClass().newInstance();
           if (numFacets > 0)
               newValidator.setFacets(facetData, varietyProperty );
           fDatatypeRegistry.addValidator(fStringPool.toString(newSimpleTypeName),newValidator);
           } catch (Exception e) {
               //e.printStackTrace(System.err);
               reportSchemaError(SchemaMessageProvider.DatatypeError,new Object [] { e.getMessage() });
           }
        return newSimpleTypeName;
    }


    /**
     * Traverse ComplexType Declaration.
     *  
     *       <complexType 
     *         abstract = boolean 
     *         base = QName 
     *         block = #all or (possibly empty) subset of {extension, restriction} 
     *         content = elementOnly | empty | mixed | textOnly 
     *         derivedBy = extension | restriction 
     *         final = #all or (possibly empty) subset of {extension, restriction} 
     *         id = ID 
     *         name = NCName>
     *          Content: (annotation? , (((minExclusive | minInclusive | maxExclusive
     *                    | maxInclusive | precision | scale | length | minLength 
     *                    | maxLength | encoding | period | duration | enumeration 
     *                    | pattern)* | (element | group | all | choice | sequence | any)*) , 
     *                    ((attribute | attributeGroup)* , anyAttribute?)))
     *        </complexType>
     * @param complexTypeDecl
     * @return 
     */
    
    //REVISIT: TO DO, base and derivation ???
    private int traverseComplexTypeDecl( Element complexTypeDecl ) throws Exception{ 
        int complexTypeAbstract  = fStringPool.addSymbol(
                                                        complexTypeDecl.getAttribute( SchemaSymbols.ATT_ABSTRACT ));
        String isAbstract = complexTypeDecl.getAttribute( SchemaSymbols.ATT_ABSTRACT );

        int complexTypeBase      = fStringPool.addSymbol(
                                                        complexTypeDecl.getAttribute( SchemaSymbols.ATT_BASE ));
        String base = complexTypeDecl.getAttribute(SchemaSymbols.ATT_BASE);

        int complexTypeBlock     = fStringPool.addSymbol(
                                                        complexTypeDecl.getAttribute( SchemaSymbols.ATT_BLOCK ));
        String blockSet = complexTypeDecl.getAttribute( SchemaSymbols.ATT_BLOCK );

        int complexTypeContent   = fStringPool.addSymbol(
                                                        complexTypeDecl.getAttribute( SchemaSymbols.ATT_CONTENT ));
        String content = complexTypeDecl.getAttribute(SchemaSymbols.ATT_CONTENT);

        int complexTypeDerivedBy =  fStringPool.addSymbol(
                                                         complexTypeDecl.getAttribute( SchemaSymbols.ATT_DERIVEDBY ));
        String derivedBy = complexTypeDecl.getAttribute( SchemaSymbols.ATT_DERIVEDBY );

        int complexTypeFinal     =  fStringPool.addSymbol(
                                                         complexTypeDecl.getAttribute( SchemaSymbols.ATT_FINAL ));
        String finalSet = complexTypeDecl.getAttribute( SchemaSymbols.ATT_FINAL );

        int complexTypeID        = fStringPool.addSymbol(
                                                        complexTypeDecl.getAttribute( SchemaSymbols.ATTVAL_ID ));
        String typeId = complexTypeDecl.getAttribute( SchemaSymbols.ATTVAL_ID );

        int complexTypeName      =  fStringPool.addSymbol(
                                                         complexTypeDecl.getAttribute( SchemaSymbols.ATT_NAME ));
        String typeName = complexTypeDecl.getAttribute(SchemaSymbols.ATT_NAME); 
        boolean isNamedType = false;

        if ( DEBUGGING )
            System.out.println("traversing complex Type : " + typeName +","+base+","+content+".");

        if (typeName.equals("")) { // gensym a unique name
            //typeName = "http://www.apache.org/xml/xerces/internalType"+fTypeCount++;
            typeName = "#"+fAnonTypeCount++;
        }
        else {
            fCurrentTypeNameStack.push(typeName);
            isNamedType = true;
        }

        int scopeDefined = fScopeCount++;
        int previousScope = fCurrentScope;
        fCurrentScope = scopeDefined;

        Element child = null;
        int contentSpecType = -1;
        int csnType = 0;
        int left = -2;
        int right = -2;

        ComplexTypeInfo baseTypeInfo = null;  //if base is a complexType;
        DatatypeValidator baseTypeValidator = null; //if base is a simple type or a complex type derived from a simpleType
        DatatypeValidator simpleTypeValidator = null;
        int baseTypeSymbol = -1;
        String fullBaseName = "";
        boolean baseIsSimpleSimple = false;
        boolean baseIsComplexSimple = false;
        boolean derivedByRestriction = true;
        boolean derivedByExtension = false;
        int baseContentSpecHandle = -1;
        Element baseTypeNode = null;


        //int parsedderivedBy = parseComplexDerivedBy(derivedBy);
        //handle the inhreitance here. 
        if (base.length()>0) {

            //first check if derivedBy is present
            if (derivedBy.length() == 0) {
                reportGenericSchemaError("derivedBy must be present when base is present in " 
                                         +SchemaSymbols.ELT_COMPLEXTYPE
                                         +" "+ typeName);
            }
            else {
                if (derivedBy.equals(SchemaSymbols.ATTVAL_EXTENSION)) {
                    derivedByRestriction = false;
                }
                
                String prefix = "";
                String localpart = base;
                int colonptr = base.indexOf(":");
                if ( colonptr > 0) {
                    prefix = base.substring(0,colonptr);
                    localpart = base.substring(colonptr+1);
                }
                int localpartIndex = fStringPool.addSymbol(localpart);
                String typeURI = resolvePrefixToURI(prefix);
                
                // check if the base type is from the same Schema;
                if (!typeURI.equals(fTargetNSURIString) && !typeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) ) {
                    baseTypeInfo = getTypeInfoFromNS(typeURI, localpart);
                    if (baseTypeInfo == null) {
                        baseTypeValidator = getTypeValidatorFromNS(typeURI, localpart);
                        if (baseTypeValidator == null) {
                            //TO DO: report error here;
                            System.out.println("Counld not find base type " +localpart 
                                               + " in schema " + typeURI);
                        }
                        else{
                            baseIsSimpleSimple = true;
                        }
                    }
                }
                else {
                
                    fullBaseName = typeURI+","+localpart;
                    
                    // assume the base is a complexType and try to locate the base type first
                    baseTypeInfo = (ComplexTypeInfo) fComplexTypeRegistry.get(fullBaseName);

                    // if not found, 2 possibilities: 1: ComplexType in question has not been compiled yet;
                    //                                2: base is SimpleTYpe;
                    if (baseTypeInfo == null) {
                        baseTypeValidator = fDatatypeRegistry.getDatatypeValidator(localpart);
                        if (baseTypeValidator == null) {
                            baseTypeNode = getTopLevelComponentByName(SchemaSymbols.ELT_COMPLEXTYPE,localpart);
                            if (baseTypeNode != null) {
                                baseTypeSymbol = traverseComplexTypeDecl( baseTypeNode );
                                baseTypeInfo = (ComplexTypeInfo)
                                fComplexTypeRegistry.get(fStringPool.toString(baseTypeSymbol)); //REVISIT: should it be fullBaseName;
                            }
                            else {
                                baseTypeNode = getTopLevelComponentByName(SchemaSymbols.ELT_SIMPLETYPE, localpart);
                                if (baseTypeNode != null) {
                                    baseTypeSymbol = traverseSimpleTypeDecl( baseTypeNode );
                                    simpleTypeValidator = baseTypeValidator = fDatatypeRegistry.getDatatypeValidator(localpart);
                                    if (simpleTypeValidator == null) {
                                        //TO DO: signal error here.
                                    }

                                    baseIsSimpleSimple = true;
                                }
                                else {
                                    reportGenericSchemaError("Base type could not be found : " + base);
                                }
                            }
                        }
                        else {
                            simpleTypeValidator = baseTypeValidator;
                            baseIsSimpleSimple = true;
                        }
                    }
                }
                        //Schema Spec : 5.11: Complex Type Definition Properties Correct : 2
                if (baseIsSimpleSimple && derivedByRestriction) {
                    reportGenericSchemaError("base is a simpledType, can't derive by restriction in " + typeName); 
                }

                //if  the base is a complexType
                if (baseTypeInfo != null ) {

                    //Schema Spec : 5.11: Derivation Valid ( Extension ) 1.1.1
                    //              5.11: Derivation Valid ( Restriction, Complex ) 1.2.1
                    if (derivedByRestriction) {
                        //REVISIT: check base Type's finalset does not include "restriction"
                    }
                    else {
                        //REVISIT: check base Type's finalset doest not include "extension"
                    }

                    if ( baseTypeInfo.contentSpecHandle > -1) {
                        if (derivedByRestriction) {
                            //REVISIT: !!! really hairy staff to check the particle derivation OK in 5.10
                            checkParticleDerivationOK(complexTypeDecl, baseTypeNode);
                        }
                        baseContentSpecHandle = baseTypeInfo.contentSpecHandle;
                    }
                    else if ( baseTypeInfo.datatypeValidator != null ) {
                        baseTypeValidator = baseTypeInfo.datatypeValidator;
                        baseIsComplexSimple = true;
                    }
                }

                //Schema Spec : 5.11: Derivation Valid ( Extension ) 1.1.1
                if (baseIsComplexSimple && !derivedByRestriction ) {
                    reportGenericSchemaError("base is ComplexSimple, can't derive by extension in " + typeName);
                }


            } // END of if (derivedBy.length() == 0) {} else {}
        } // END of if (base.length() > 0) {}

        // skip refinement and annotations
        child = null;

        if (baseIsComplexSimple) {

            contentSpecType = XMLElementDecl.TYPE_SIMPLE;
            
            int numEnumerationLiterals = 0;
            int numFacets = 0;
            Hashtable facetData        = new Hashtable();
            Vector enumData            = new Vector();

            for (child = XUtil.getFirstChildElement(complexTypeDecl);
                 child != null && (child.getNodeName().equals(SchemaSymbols.ELT_MINEXCLUSIVE) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_MININCLUSIVE) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_MAXEXCLUSIVE) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_MAXINCLUSIVE) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_PRECISION) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_SCALE) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_LENGTH) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_MINLENGTH) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_MAXLENGTH) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_ENCODING) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_PERIOD) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_DURATION) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_ENUMERATION) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_PATTERN) ||
                                   child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION));
                 child = XUtil.getNextSiblingElement(child)) 
            {
                if ( child.getNodeType() == Node.ELEMENT_NODE ) {
                    Element facetElt = (Element) child;
                    numFacets++;
                    if (facetElt.getNodeName().equals(SchemaSymbols.ELT_ENUMERATION)) {
                        numEnumerationLiterals++;
                        enumData.addElement(facetElt.getAttribute(SchemaSymbols.ATT_VALUE));
                        //Enumerations can have annotations ? ( 0 | 1 )
                        Element enumContent =  XUtil.getFirstChildElement( facetElt );
                        if( enumContent != null && enumContent.getNodeName().equals( SchemaSymbols.ELT_ANNOTATION ) ){
                            traverseAnnotationDecl( child );   
                        }
                        // TO DO: if Jeff check in new changes to TraverseSimpleType, copy them over
                    } else {
                        facetData.put(facetElt.getNodeName(),facetElt.getAttribute( SchemaSymbols.ATT_VALUE ));
                    }
                }
            }
            if (numEnumerationLiterals > 0) {
                facetData.put(SchemaSymbols.ELT_ENUMERATION, enumData);
            }

            // overide the facets of the baseTypeValidator
            if (numFacets > 0)
                baseTypeValidator.setFacets(facetData, derivedBy );

            // now we are ready with our own simpleTypeValidator
            simpleTypeValidator = baseTypeValidator;

            if (child != null) {
                reportGenericSchemaError("Invalid Schema Document");
            }
        }

            // if content = textonly, base is a datatype
        if (content.equals(SchemaSymbols.ATTVAL_TEXTONLY)) {
            //TO DO
            if (base.length() == 0) {
                simpleTypeValidator = baseTypeValidator = fDatatypeRegistry.getDatatypeValidator(SchemaSymbols.ATTVAL_STRING);
            }
            else if (fDatatypeRegistry.getDatatypeValidator(base) == null) // must be datatype
                        reportSchemaError(SchemaMessageProvider.NotADatatype,
                                          new Object [] { base }); //REVISIT check forward refs
            //handle datatypes
            contentSpecType = XMLElementDecl.TYPE_SIMPLE;
            /****
            left = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                 fStringPool.addSymbol(base),
                                                 -1, false);
            /****/                                                 

        } 
        else {   
            if (!baseIsComplexSimple) {
                contentSpecType = XMLElementDecl.TYPE_CHILDREN;
            }
            csnType = XMLContentSpec.CONTENTSPECNODE_SEQ;
            boolean mixedContent = false;
            //REVISIT: is the default content " elementOnly"
            boolean elementContent = true;
            boolean textContent = false;
            boolean emptyContent = false;
            left = -2;
            right = -2;
            boolean hadContent = false;

            if (content.equals(SchemaSymbols.ATTVAL_EMPTY)) {
                contentSpecType = XMLElementDecl.TYPE_EMPTY;
                emptyContent = true;
                elementContent = false;
                left = -1; // no contentSpecNode needed
            } else if (content.equals(SchemaSymbols.ATTVAL_MIXED) ) {
                contentSpecType = XMLElementDecl.TYPE_MIXED;
                mixedContent = true;
                elementContent = false;
                csnType = XMLContentSpec.CONTENTSPECNODE_CHOICE;
            } else if (content.equals(SchemaSymbols.ATTVAL_ELEMENTONLY) || content.equals("")) {
                elementContent = true;
            } else if (content.equals(SchemaSymbols.ATTVAL_TEXTONLY)) {
                textContent = true;
                elementContent = false;
            }

            if (mixedContent) {
                // add #PCDATA leaf

                left = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                         -1, // -1 means "#PCDATA" is name
                                                         -1, false);
                csnType = XMLContentSpec.CONTENTSPECNODE_CHOICE;
            }

            boolean seeOtherParticle = false;                
            boolean seeAll = false;

            for (child = XUtil.getFirstChildElement(complexTypeDecl);
                 child != null;
                 child = XUtil.getNextSiblingElement(child)) {

                int index = -2;  // to save the particle's contentSpec handle 
                hadContent = true;

                boolean seeParticle = false;

                String childName = child.getNodeName();

                if (childName.equals(SchemaSymbols.ELT_ELEMENT)) {
                    if (mixedContent || elementContent) {
                        if ( DEBUGGING )
                            System.out.println(" child element name " + child.getAttribute(SchemaSymbols.ATT_NAME));

                        QName eltQName = traverseElementDecl(child);
                        index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                                   eltQName.localpart,
                                                                   eltQName.uri, 
                                                                   false);
                        seeParticle = true;
                        seeOtherParticle = true;

                    } 
                    else {
                        reportSchemaError(SchemaMessageProvider.EltRefOnlyInMixedElemOnly, null);
                    }

                } 
                else if (childName.equals(SchemaSymbols.ELT_GROUP)) {
                    index = traverseGroupDecl(child);
                    seeParticle = true;
                    seeOtherParticle = true;
                } 
                else if (childName.equals(SchemaSymbols.ELT_ALL)) {
                    index = traverseAll(child);
                    seeParticle = true;
                    seeAll = true;
                  
                } 
                else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                    index = traverseChoice(child);
                    seeParticle = true;
                    seeOtherParticle = true;                  
                } 
                else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                    index = traverseSequence(child);
                    seeParticle = true;
                    seeOtherParticle = true;                  
                } 
                else if (childName.equals(SchemaSymbols.ELT_ATTRIBUTE) ||
                           childName.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                    break; // attr processing is done later on in this method
                } 
                else if (childName.equals(SchemaSymbols.ELT_ANY)) {
                    contentSpecType = fStringPool.addSymbol("ANY");
                    left = -1;
                } 
                else { // datatype qual   
                    if (base.equals(""))
                        reportSchemaError(SchemaMessageProvider.DatatypeWithType, null);
                    else
                        reportSchemaError(SchemaMessageProvider.DatatypeQualUnsupported,
                                          new Object [] { childName });
                }

                // if base is complextype with simpleType content, can't have any particle children at all.
                if (baseIsComplexSimple && seeParticle) {
                    reportGenericSchemaError("In complexType "+typeName+", base type is complextype with simpleType content, can't have any particle children at all");
                    hadContent = false;
                    left = index = -2;
                    contentSpecType = XMLElementDecl.TYPE_SIMPLE;
                    break;
                }

                // check the minOccurs and maxOccurs of the particle, and fix the  
                // contentspec accordingly
                if (seeParticle) {
                    index = expandContentModel(index, child);
                } //end of if (seeParticle)

                if (seeAll && seeOtherParticle) {
                    reportGenericSchemaError ( " 'All' group needs to be the only child in Complextype : " + typeName);
                }

                if (seeAll) {
                    //TO DO:
                    //check the minOccurs = 1 and maxOccurs = 1  
                }

                if (left == -2) {
                    left = index;
                } else if (right == -2) {
                    right = index;
                } else {
                    left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);
                    right = index;
                }
            } //end looping through the children

            if (hadContent && right != -2)
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);

            if (mixedContent && hadContent) {
                // set occurrence count
                left = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE,
                                                     left, -1, false);
            }
        }

        // if derived by extension and base complextype has a content model, 
        // compose the final content model by concatenating the base and the 
        // current in sequence.
        if (!derivedByRestriction && baseContentSpecHandle > -1 ) {
            left = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_SEQ, 
                                                 baseContentSpecHandle,
                                                 left,
                                                 false);
        }

        // REVISIT: this is when sees a topelevel <complexType name="abc">attrs*</complexType>
        if (content.length() == 0 && base.length() == 0 && left == -2) {
            contentSpecType = XMLElementDecl.TYPE_ANY;
        }

        if ( DEBUGGING )
            System.out.println("!!!!!>>>>>" + typeName+", "+ baseTypeInfo + ", " 
                               + baseContentSpecHandle +", " + left +", "+scopeDefined);

        ComplexTypeInfo typeInfo = new ComplexTypeInfo();
        typeInfo.baseComplexTypeInfo = baseTypeInfo;
        typeInfo.baseDataTypeValidator = baseTypeValidator;
        int derivedByInt = -1;
        if (derivedBy.length() > 0) {
            derivedByInt = parseComplexDerivedBy(derivedBy);
        }
        typeInfo.derivedBy = derivedByInt;
        typeInfo.scopeDefined = scopeDefined; 
        typeInfo.contentSpecHandle = left;
        typeInfo.contentType = contentSpecType;
        typeInfo.datatypeValidator = simpleTypeValidator;
        typeInfo.blockSet = parseBlockSet(complexTypeDecl.getAttribute(SchemaSymbols.ATT_BLOCK));
        typeInfo.finalSet = parseFinalSet(complexTypeDecl.getAttribute(SchemaSymbols.ATT_FINAL));

        //add a template element to the grammar element decl pool.
        int typeNameIndex = fStringPool.addSymbol(typeName);
        int templateElementNameIndex = fStringPool.addSymbol("$"+typeName);

        typeInfo.templateElementIndex = 
            fSchemaGrammar.addElementDecl(new QName(-1, templateElementNameIndex,typeNameIndex,fTargetNSURI),
                                          (fTargetNSURI==-1) ? -1 : fCurrentScope, scopeDefined,
                                            contentSpecType, left, 
                                          -1, simpleTypeValidator);
        typeInfo.attlistHead = fSchemaGrammar.getFirstAttributeDeclIndex(typeInfo.templateElementIndex);


        // (attribute | attrGroupRef)*
        for (child = XUtil.getFirstChildElement(complexTypeDecl);
             child != null;
             child = XUtil.getNextSiblingElement(child)) {

            String childName = child.getNodeName();

            if (childName.equals(SchemaSymbols.ELT_ATTRIBUTE)) {
                if ((baseIsComplexSimple||baseIsSimpleSimple) && derivedByRestriction) {
                    reportGenericSchemaError("In complexType "+typeName+", base type has simpleType content and derivation method is 'restriction', can't have any attribute children at all");
                    break;
                }
                traverseAttributeDecl(child, typeInfo);
            } 
            else if ( childName.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ) { 
                if ((baseIsComplexSimple||baseIsSimpleSimple) && derivedByRestriction) {
                    reportGenericSchemaError("In complexType "+typeName+", base type has simpleType content and derivation method is 'restriction', can't have any attribute children at all");
                    break;
                }
                traverseAttributeGroupDecl(child,typeInfo);
            }
        }
        typeInfo.attlistHead = fSchemaGrammar.getFirstAttributeDeclIndex(typeInfo.templateElementIndex);

        // merge in base type's attribute decls
        if (baseTypeInfo != null && baseTypeInfo.attlistHead > -1 ) {
            int attDefIndex = baseTypeInfo.attlistHead;
            while ( attDefIndex > -1 ) {
                fSchemaGrammar.getAttributeDecl(attDefIndex, fTempAttributeDecl);
                attDefIndex = fSchemaGrammar.getNextAttributeDeclIndex(attDefIndex);
                // if found a duplicate, if it is derived by restriction. then skip the one from the base type
                if (fSchemaGrammar.getAttributeDeclIndex(typeInfo.templateElementIndex, fTempAttributeDecl.name) > -1) {
                    if (derivedByRestriction) {
                        continue;
                    }
                }
                //REVISIT:
                // int enumeration = ????
                fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                          fTempAttributeDecl.name, fTempAttributeDecl.type, 
                                          -1, fTempAttributeDecl.defaultType, 
                                          fTempAttributeDecl.defaultValue, fTempAttributeDecl.datatypeValidator);
            }
        }

        if (!typeName.startsWith("#")) {
            typeName = fTargetNSURIString + "," + typeName;
        }
        fComplexTypeRegistry.put(typeName,typeInfo);

        // before exit the complex type definition, restore the scope, mainly for nested Anonymous Types
        fCurrentScope = previousScope;
        if (isNamedType) {
            fCurrentTypeNameStack.pop();
            checkRecursingComplexType();
            fCurrentTypeNameStack.clear();
        }

        typeNameIndex = fStringPool.addSymbol(typeName);
        return typeNameIndex;


    } // end of method: traverseComplexTypeDecl

    private void checkRecursingComplexType() throws Exception {
        if ( fCurrentTypeNameStack.empty() ) {
            if (! fElementRecurseComplex.isEmpty() ) {
                Enumeration e = fElementRecurseComplex.keys();
                while( e.hasMoreElements() ) {
                    String nameThenScope = (String) e.nextElement();
                    String typeName = (String) fElementRecurseComplex.get(nameThenScope);
                    int comma = nameThenScope.indexOf(",");
                    String eltName = nameThenScope.substring(0, comma);
                    int enclosingScope = Integer.parseInt(nameThenScope.substring(comma+1));
                    ComplexTypeInfo typeInfo = 
                        (ComplexTypeInfo) fComplexTypeRegistry.get(fTargetNSURIString+","+typeName);
                    if (typeInfo==null) {
                        throw new Exception ( "Internal Error in void checkRecursingComplexType(). " );
                    }
                    else {
                        int nameIndex = fStringPool.addSymbol(eltName);
                        int elementIndex = fSchemaGrammar.addElementDecl(new QName(-1, nameIndex, nameIndex, -1), 
                                                                         enclosingScope, typeInfo.scopeDefined, 
                                                                         typeInfo.contentType, 
                                                                         typeInfo.contentSpecHandle, 
                                                                         typeInfo.attlistHead, 
                                                                         typeInfo.datatypeValidator);
                        fSchemaGrammar.setElementComplexTypeInfo(elementIndex, typeInfo);
                    }

                }
            }
        }
    }

    private void checkParticleDerivationOK(Element derivedTypeNode, Element baseTypeNode) {
        //TO DO: !!!
    }

    private int expandContentModel ( int index, Element particle) throws Exception {
        
        String minOccurs = particle.getAttribute(SchemaSymbols.ATT_MINOCCURS);
        String maxOccurs = particle.getAttribute(SchemaSymbols.ATT_MAXOCCURS);    

        int min=1, max=1;

        if (minOccurs.equals("")) {
            minOccurs = "1";
        }
        if (maxOccurs.equals("") ){
            if ( minOccurs.equals("0")) {
                maxOccurs = "1";
            }
            else {
                maxOccurs = minOccurs;
            }
        }


        int leafIndex = index;
        //REVISIT: !!! minoccurs, maxoccurs.
        if (minOccurs.equals("1")&& maxOccurs.equals("1")) {

        }
        else if (minOccurs.equals("0")&& maxOccurs.equals("1")) {
            //zero or one
            index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE,
                                                   index,
                                                   -1,
                                                   false);
        }
        else if (minOccurs.equals("0")&& maxOccurs.equals("unbounded")) {
            //zero or more
            index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE,
                                                   index,
                                                   -1,
                                                   false);
        }
        else if (minOccurs.equals("1")&& maxOccurs.equals("unbounded")) {
            //one or more
            index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE,
                                                   index,
                                                   -1,
                                                   false);
        }
        else if (maxOccurs.equals("unbounded") ) {
            // >=2 or more
            try {
                min = Integer.parseInt(minOccurs);
            }
            catch (Exception e) {
                reportSchemaError(SchemaMessageProvider.GenericError,
                                  new Object [] { "illegal value for minOccurs : '" +e.getMessage()+ "' " });
            }
            if (min<2) {
                //REVISIT: report Error here
            }

            // => a,a,..,a+
            index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE,
                   index,
                   -1,
                   false);

            for (int i=0; i < (min-1); i++) {
                index = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_SEQ,
                                                      index,
                                                      leafIndex,
                                                      false);
            }

        }
        else {
            // {n,m} => a,a,a,...(a),(a),...
            try {
                min = Integer.parseInt(minOccurs);
                max = Integer.parseInt(maxOccurs);
            }
            catch (Exception e){
                reportSchemaError(SchemaMessageProvider.GenericError,
                                  new Object [] { "illegal value for minOccurs or maxOccurs : '" +e.getMessage()+ "' "});
            }
            for (int i=0; i<(min-1); i++) {
                index = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_SEQ,
                                                      index,
                                                      leafIndex,
                                                      false);

            }
            if (max>min ) {
                int optional = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE,
                                                             leafIndex,
                                                             -1,
                                                             false);
                for (int i=0; i < (max-min); i++) {
                    index = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_SEQ,
                                                          index,
                                                          optional,
                                                          false);
                }
            }
        }

        return index;
    }

    /**
     * Traverses Schema attribute declaration.
     *   
     *       <attribute 
     *         form = qualified | unqualified 
     *         id = ID 
     *         name = NCName 
     *         ref = QName 
     *         type = QName 
     *         use = default | fixed | optional | prohibited | required 
     *         value = string>
     *         Content: (annotation? , simpleType?)
     *       <attribute/>
     * 
     * @param attributeDecl
     * @return 
     * @exception Exception
     */
    private int traverseAttributeDecl( Element attrDecl, ComplexTypeInfo typeInfo ) throws Exception {
        int attributeForm  =  fStringPool.addSymbol(
                                                   attrDecl.getAttribute( SchemaSymbols.ATT_FORM ));

        int attributeID    =  fStringPool.addSymbol(
                                                   attrDecl.getAttribute( SchemaSymbols.ATTVAL_ID ));

        int attributeName  =  fStringPool.addSymbol(
                                                   attrDecl.getAttribute( SchemaSymbols.ATT_NAME ));

        int attributeRef   =  fStringPool.addSymbol(
                                                   attrDecl.getAttribute( SchemaSymbols.ATT_REF ));

        int attributeType  =  fStringPool.addSymbol(
                                                   attrDecl.getAttribute( SchemaSymbols.ATT_TYPE ));

        int attributeUse   =  fStringPool.addSymbol(
                                                   attrDecl.getAttribute( SchemaSymbols.ATT_USE ));

        int attributeValue =  fStringPool.addSymbol(
                                                   attrDecl.getAttribute( SchemaSymbols.ATT_VALUE ));

        String attNameStr = attrDecl.getAttribute(SchemaSymbols.ATT_NAME);
        // attribute name
        int attName = fStringPool.addSymbol(attNameStr);
        // form attribute
        String isQName = attrDecl.getAttribute(SchemaSymbols.ATT_EQUIVCLASS);

        DatatypeValidator dv = null;
        // attribute type
        int attType = -1;
        boolean attIsList = false;
        int dataTypeSymbol = -1;

        String ref = attrDecl.getAttribute(SchemaSymbols.ATT_REF); 
        String datatype = attrDecl.getAttribute(SchemaSymbols.ATT_TYPE);

        if (!ref.equals("")) {
            if (XUtil.getFirstChildElement(attrDecl) != null)
                reportSchemaError(SchemaMessageProvider.NoContentForRef, null);
            String prefix = "";
            String localpart = ref;
            int colonptr = ref.indexOf(":");
            if ( colonptr > 0) {
                prefix = ref.substring(0,colonptr);
                localpart = ref.substring(colonptr+1);
            }
            String uriStr = resolvePrefixToURI(prefix);

            if (!uriStr.equals(fTargetNSURIString)) {
                addAttributeDeclFromAnotherSchema(localpart, uriStr, typeInfo);

                return -1;
                // TO DO
                // REVISIT: different NS, not supported yet.
                //reportGenericSchemaError("Feature not supported: see an attribute from different NS");
            }

            Element referredAttribute = getTopLevelComponentByName(SchemaSymbols.ELT_ATTRIBUTE,localpart);
            if (referredAttribute != null) {
                traverseAttributeDecl(referredAttribute, typeInfo);
            }
            else {
                reportGenericSchemaError ( "Couldn't find top level attribute " + ref);
            }
            return -1;
        }

        if (datatype.equals("")) {
            Element child = XUtil.getFirstChildElement(attrDecl);

            while (child != null && !child.getNodeName().equals(SchemaSymbols.ELT_SIMPLETYPE))
                child = XUtil.getNextSiblingElement(child);
            if (child != null && child.getNodeName().equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                attType = XMLAttributeDecl.TYPE_SIMPLE;
                dataTypeSymbol = traverseSimpleTypeDecl(child);
            } 
            else {
                attType = XMLAttributeDecl.TYPE_SIMPLE;
                dataTypeSymbol = fStringPool.addSymbol("string");
            }

        } else {

            String prefix = "";
            String localpart = datatype;
            int colonptr = datatype.indexOf(":");
            if ( colonptr > 0) {
                prefix = datatype.substring(0,colonptr);
                localpart = datatype.substring(colonptr+1);
            }
            String typeURI = resolvePrefixToURI(prefix);
            dataTypeSymbol = fStringPool.addSymbol(localpart);

            if ( typeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) ) {
                if (localpart.equals("ID")) {
                    attType = XMLAttributeDecl.TYPE_ID;
                } else if (localpart.equals("IDREF")) {
                    attType = XMLAttributeDecl.TYPE_IDREF;
                } else if (localpart.equals("IDREFS")) {
                    attType = XMLAttributeDecl.TYPE_IDREF;
                    attIsList = true;
                } else if (localpart.equals("ENTITY")) {
                    attType = XMLAttributeDecl.TYPE_ENTITY;
                } else if (localpart.equals("ENTITIES")) {
                    attType = XMLAttributeDecl.TYPE_ENTITY;
                    attIsList = true;
                } else if (localpart.equals("NMTOKEN")) {
                    attType = XMLAttributeDecl.TYPE_NMTOKEN;
                } else if (localpart.equals("NMTOKENS")) {
                    attType = XMLAttributeDecl.TYPE_NMTOKEN;
                    attIsList = true;
                } else if (localpart.equals(SchemaSymbols.ELT_NOTATION)) {
                    attType = XMLAttributeDecl.TYPE_NOTATION;
                }
                else {
                    attType = XMLAttributeDecl.TYPE_SIMPLE;
                }
            }
            else { // REVISIT: Danger: assuming all other ATTR types are datatypes
                //REVISIT check against list of validators to ensure valid type name

                // check if the type is from the same Schema
                if (!typeURI.equals(fTargetNSURIString) ) {
                    dv = getTypeValidatorFromNS(typeURI, localpart);
                    if (dv == null) {
                        //TO DO: report error here;
                        System.out.println("Counld not find base type " +localpart 
                                           + " in schema " + typeURI);
                    }
                }
                else {
                        dv = fDatatypeRegistry.getDatatypeValidator(localpart);
                }

                attType = XMLAttributeDecl.TYPE_SIMPLE;
            }

        }

        // attribute default type
        int attDefaultType = -1;
        int attDefaultValue = -1;

        String use = attrDecl.getAttribute(SchemaSymbols.ATT_USE);
        boolean required = use.equals(SchemaSymbols.ATTVAL_REQUIRED);

        //if (attType == XMLAttributeDecl.TYPE_SIMPLE ) {
        if(dv==null)
            dv = fDatatypeRegistry.getDatatypeValidator(fStringPool.toString(dataTypeSymbol));
        //}

        if (dv == null) {
            reportGenericSchemaError("null validator for datatype : " 
                                     + fStringPool.toString(dataTypeSymbol));
        }

        if (required) {
            attDefaultType = XMLAttributeDecl.DEFAULT_TYPE_REQUIRED;
        } else {
            if (use.equals(SchemaSymbols.ATTVAL_FIXED)) {
                String fixed = attrDecl.getAttribute(SchemaSymbols.ATT_VALUE);
                if (!fixed.equals("")) {
                    attDefaultType = XMLAttributeDecl.DEFAULT_TYPE_FIXED;
                    attDefaultValue = fStringPool.addString(fixed);
                } 
            }
            else if (use.equals(SchemaSymbols.ATTVAL_DEFAULT)) {
                // attribute default value
                String defaultValue = attrDecl.getAttribute(SchemaSymbols.ATT_VALUE);
                if (!defaultValue.equals("")) {
                    attDefaultType = XMLAttributeDecl.DEFAULT_TYPE_DEFAULT;
                    attDefaultValue = fStringPool.addString(defaultValue);
                } 
            }
            else if (use.equals(SchemaSymbols.ATTVAL_PROHIBITED)) {
                
                attDefaultType = fStringPool.addSymbol("#PROHIBITED");
                attDefaultValue = fStringPool.addString("");
            }
            else {
                attDefaultType = XMLAttributeDecl.DEFAULT_TYPE_IMPLIED;
            }       // check default value is valid for the datatype.

            if (attType == XMLAttributeDecl.TYPE_SIMPLE && attDefaultValue != -1) {
                try { 
                    // REVISIT - integrate w/ error handling
                    dv = fDatatypeRegistry.getDatatypeValidator(datatype);
                    if (dv != null) 
                        //REVISIT
                        dv.validate(fStringPool.toString(attDefaultValue));
                    else
                        reportSchemaError(SchemaMessageProvider.NoValidatorFor,
                                          new Object [] { datatype });
                } /*catch (InvalidDatatypeValueException idve) {
                    reportSchemaError(SchemaMessageProvider.IncorrectDefaultType,
                                      new Object [] { attrDecl.getAttribute(SchemaSymbols.ATT_NAME), idve.getMessage() });
                } */catch (Exception e) {
                    e.printStackTrace();
                    System.out.println("Internal error in attribute datatype validation");
                }
            }
        }

        int uriIndex = -1;
        if ( isQName.equals(SchemaSymbols.ATTVAL_QUALIFIED)||
             fDefaultQualified || isTopLevel(attrDecl) ) {
            uriIndex = fTargetNSURI;
        }

        QName attQName = new QName(-1,attName,attName,uriIndex);
        if ( DEBUGGING )
            System.out.println(" the dataType Validator for " + fStringPool.toString(attName) + " is " + dv);

        //put the top-levels in the attribute decl registry.
        if (isTopLevel(attrDecl)) {
            fTempAttributeDecl.datatypeValidator = dv;
            fTempAttributeDecl.name.setValues(attQName);
            fTempAttributeDecl.type = attType;
            fTempAttributeDecl.defaultType = attDefaultType;
            if (attDefaultValue != -1 ) {
                fTempAttributeDecl.defaultValue = new String(fStringPool.toString(attDefaultValue));
            }
            fAttributeDeclRegistry.put(attNameStr, new XMLAttributeDecl(fTempAttributeDecl));
        }

        // add attribute to attr decl pool in fSchemaGrammar, 
        fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                  attQName, attType, 
                                  dataTypeSymbol, attDefaultType, 
                                  fStringPool.toString( attDefaultValue), dv);
        return -1;
    } // end of method traverseAttribute

    private int addAttributeDeclFromAnotherSchema( String name, String uriStr, ComplexTypeInfo typeInfo) throws Exception {
        SchemaGrammar aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uriStr);
        if (uriStr == null || ! (aGrammar instanceof SchemaGrammar) ) {
            reportGenericSchemaError("!!Schema not found : " + uriStr);
            return -1;
        }

        Hashtable attrRegistry = aGrammar.getAttirubteDeclRegistry();
        if (attrRegistry == null) {
            reportGenericSchemaError("no attribute was defined in schema : " + uriStr);
            return -1;
        }

        XMLAttributeDecl tempAttrDecl = (XMLAttributeDecl) attrRegistry.get(name);

        if (tempAttrDecl == null) {
            reportGenericSchemaError( "no attribute named \"" + name 
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }


        fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                  tempAttrDecl.name, tempAttrDecl.type,
                                  -1, tempAttrDecl.defaultType,
                                  tempAttrDecl.defaultValue, 
                                  tempAttrDecl.datatypeValidator);


        return 0;
    }
    /*
    * 
    * <attributeGroup 
    *   id = ID 
    *   name = NCName
    *   ref = QName>
    *   Content: (annotation?, (attribute|attributeGroup), anyAttribute?)
    * </>
    * 
    */
    private int traverseAttributeGroupDecl( Element attrGrpDecl, ComplexTypeInfo typeInfo ) throws Exception {
        // attribute name
        int attGrpName = fStringPool.addSymbol(attrGrpDecl.getAttribute(SchemaSymbols.ATT_NAME));
        
        String ref = attrGrpDecl.getAttribute(SchemaSymbols.ATT_REF); 

        // attribute type
        int attType = -1;
        int enumeration = -1;

        if (!ref.equals("")) {
            if (XUtil.getFirstChildElement(attrGrpDecl) != null)
                reportSchemaError(SchemaMessageProvider.NoContentForRef, null);
            String prefix = "";
            String localpart = ref;
            int colonptr = ref.indexOf(":");
            if ( colonptr > 0) {
                prefix = ref.substring(0,colonptr);
                localpart = ref.substring(colonptr+1);
            }
            String uriStr = resolvePrefixToURI(prefix);
            if (!uriStr.equals(fTargetNSURIString)) {
                
                traverseAttributeGroupDeclFromAnotherSchema(localpart, uriStr, typeInfo);

                return -1;
                // TO DO 
                // REVISIST: different NS, not supported yet.
                //reportGenericSchemaError("Feature not supported: see an attribute from different NS");
            }
            Element referredAttrGrp = getTopLevelComponentByName(SchemaSymbols.ELT_ATTRIBUTEGROUP,localpart);
            if (referredAttrGrp != null) {
                traverseAttributeGroupDecl(referredAttrGrp, typeInfo);
            }
            else {
                reportGenericSchemaError ( "Couldn't find top level attributegroup " + ref);
            }
            return -1;
        }

        for ( Element child = XUtil.getFirstChildElement(attrGrpDecl); 
             child != null ; child = XUtil.getNextSiblingElement(child)) {
       
            if ( child.getNodeName().equals(SchemaSymbols.ELT_ATTRIBUTE) ){
                traverseAttributeDecl(child, typeInfo);
            }
            else if ( child.getNodeName().equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ) {
                traverseAttributeGroupDecl(child, typeInfo);
            }
            else if (child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION) ) {
                // REVISIT: what about appInfo
            }
        }
        return -1;
    } // end of method traverseAttributeGroup
    
    private int traverseAttributeGroupDeclFromAnotherSchema( String attGrpName , String uriStr, ComplexTypeInfo typeInfo ) throws Exception {
        
        SchemaGrammar aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uriStr);
        if (uriStr == null || ! (aGrammar instanceof SchemaGrammar) ) {
            reportGenericSchemaError("!!Schema not found : " + uriStr);
            return -1;
        }
        // attribute name
        Element attGrpDecl = (Element) aGrammar.topLevelAttrGrpDecls.get((Object)attGrpName);
        if (attGrpDecl == null) {
            reportGenericSchemaError( "no attribute group named \"" + attGrpName 
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }

        // attribute type
        int attType = -1;
        int enumeration = -1;


        for ( Element child = XUtil.getFirstChildElement(attGrpDecl); 
             child != null ; child = XUtil.getNextSiblingElement(child)) {

            //child attribute couldn't be a top-level attribute DEFINITION, 
            if ( child.getNodeName().equals(SchemaSymbols.ELT_ATTRIBUTE) ){
                String childAttName = child.getAttribute(SchemaSymbols.ATT_NAME);
                if ( childAttName.length() > 0 ) {
                    Hashtable attDeclRegistry = aGrammar.getAttirubteDeclRegistry();
                    if (attDeclRegistry != null) {
                        if (attDeclRegistry.get((Object)childAttName) != null ){
                            addAttributeDeclFromAnotherSchema(childAttName, uriStr, typeInfo);
                            return -1;
                        }
                    }       
                }
                else 
                    traverseAttributeDecl(child, typeInfo);
            }
            else if ( child.getNodeName().equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ) {
                traverseAttributeGroupDecl(child, typeInfo);
            }
            else if (child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION) ) {
                // REVISIT: what about appInfo
            }
        }
        return -1;
    } // end of method traverseAttributeGroupFromAnotherSchema
    

    /**
     * Traverse element declaration:
     *  <element
     *         abstract = boolean
     *         block = #all or (possibly empty) subset of {equivClass, extension, restriction}
     *         default = string
     *         equivClass = QName
     *         final = #all or (possibly empty) subset of {extension, restriction}
     *         fixed = string
     *         form = qualified | unqualified
     *         id = ID
     *         maxOccurs = string
     *         minOccurs = nonNegativeInteger
     *         name = NCName
     *         nullable = boolean
     *         ref = QName
     *         type = QName>
     *   Content: (annotation? , (simpleType | complexType)? , (unique | key | keyref)*)
     *   </element>
     * 
     * 
     *       The following are identity-constraint definitions
     *        <unique 
     *         id = ID 
     *         name = NCName>
     *         Content: (annotation? , (selector , field+))
     *       </unique>
     *       
     *       <key 
     *         id = ID 
     *         name = NCName>
     *         Content: (annotation? , (selector , field+))
     *       </key>
     *       
     *       <keyref 
     *         id = ID 
     *         name = NCName 
     *         refer = QName>
     *         Content: (annotation? , (selector , field+))
     *       </keyref>
     *       
     *       <selector>
     *         Content: XPathExprApprox : An XPath expression 
     *       </selector>
     *       
     *       <field>
     *         Content: XPathExprApprox : An XPath expression 
     *       </field>
     *       
     * 
     * @param elementDecl
     * @return 
     * @exception Exception
     */
    private QName traverseElementDecl(Element elementDecl) throws Exception {
        int elementBlock      =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_BLOCK ) );

        int elementDefault    =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_DEFAULT ));

        int elementEquivClass =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_EQUIVCLASS ));

        int elementFinal      =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_FINAL ));

        int elementFixed      =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_FIXED ));

        int elementForm       =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_FORM ));

        int elementID          =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATTVAL_ID ));

        int elementMaxOccurs   =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_MAXOCCURS ));

        int elementMinOccurs  =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_MINOCCURS ));

        int elemenName        =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_NAME ));

        int elementNullable   =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_NULLABLE ));

        int elementRef        =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_REF ));

        int elementType       =  fStringPool.addSymbol(
            elementDecl.getAttribute( SchemaSymbols.ATT_TYPE ));

        int contentSpecType      = -1;
        int contentSpecNodeIndex = -1;
        int typeNameIndex = -1;
        int scopeDefined = -2; //signal a error if -2 gets gets through 
                                //cause scope can never be -2.
        DatatypeValidator dv = null;



        String name = elementDecl.getAttribute(SchemaSymbols.ATT_NAME);

        if ( DEBUGGING )
            System.out.println("traversing element decl : " + name );

        String ref = elementDecl.getAttribute(SchemaSymbols.ATT_REF);
        String type = elementDecl.getAttribute(SchemaSymbols.ATT_TYPE);
        String minOccurs = elementDecl.getAttribute(SchemaSymbols.ATT_MINOCCURS);
        String maxOccurs = elementDecl.getAttribute(SchemaSymbols.ATT_MAXOCCURS);
        String dflt = elementDecl.getAttribute(SchemaSymbols.ATT_DEFAULT);
        String fixed = elementDecl.getAttribute(SchemaSymbols.ATT_FIXED);
        String equivClass = elementDecl.getAttribute(SchemaSymbols.ATT_EQUIVCLASS);
        // form attribute
        String isQName = elementDecl.getAttribute(SchemaSymbols.ATT_EQUIVCLASS);

        String fromAnotherSchema = null;

        if (isTopLevel(elementDecl)) {
        
            int nameIndex = fStringPool.addSymbol(name);
            int eltKey = fSchemaGrammar.getElementDeclIndex(nameIndex,TOP_LEVEL_SCOPE);
            if (eltKey > -1 ) {
                return new QName(-1,nameIndex,nameIndex,fTargetNSURI);
            }
        }

        int attrCount = 0;
        if (!ref.equals("")) attrCount++;
        if (!type.equals("")) attrCount++;
                //REVISIT top level check for ref & archref
        if (attrCount > 1)
            reportSchemaError(SchemaMessageProvider.OneOfTypeRefArchRef, null);

        if (!ref.equals("")) {
            if (XUtil.getFirstChildElement(elementDecl) != null)
                reportSchemaError(SchemaMessageProvider.NoContentForRef, null);
            String prefix = "";
            String localpart = ref;
            int colonptr = ref.indexOf(":");
            if ( colonptr > 0) {
                prefix = ref.substring(0,colonptr);
                localpart = ref.substring(colonptr+1);
            }
            int localpartIndex = fStringPool.addSymbol(localpart);
            String uriString = resolvePrefixToURI(prefix);
            QName eltName = new QName(  fStringPool.addSymbol(prefix),
                                      localpartIndex,
                                      fStringPool.addSymbol(ref),
                                      fStringPool.addSymbol(uriString) );

            //if from another schema, just return the element QName
            if (! uriString.equals(fTargetNSURIString) ) {
                return eltName;
            }

            int elementIndex = fSchemaGrammar.getElementDeclIndex(localpartIndex, TOP_LEVEL_SCOPE);
            //if not found, traverse the top level element that if referenced

            if (elementIndex == -1 ) {
                Element targetElement = getTopLevelComponentByName(SchemaSymbols.ELT_ELEMENT,localpart);
                if (targetElement == null ) {
                    reportGenericSchemaError("Element " + localpart + " not found in the Schema");
                    //REVISIT, for now, the QName anyway
                    return eltName;
                    //return new QName(-1,fStringPool.addSymbol(localpart), -1, fStringPool.addSymbol(uriString));
                }
                else {
                    // do nothing here, other wise would cause infinite loop for 
                    //   <element name="recur"><complexType><element ref="recur"> ...
                    //eltName= traverseElementDecl(targetElement);
                }
            }
            return eltName;
        }
                
        Element equivClassElementDecl = null;
        if ( equivClass.length() > 0 ) {
            equivClassElementDecl = getTopLevelComponentByName(SchemaSymbols.ELT_ELEMENT, getLocalPart(equivClass));
            if (equivClassElementDecl == null) {
                reportGenericSchemaError("Equivclass affiliation element "
                                         +equivClass
                                         +" in element declaration " 
                                         +name);  
            }
        }
        
        ComplexTypeInfo typeInfo = new ComplexTypeInfo();

        // element has a single child element, either a datatype or a type, null if primitive
        Element child = XUtil.getFirstChildElement(elementDecl);
        
        while (child != null && child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION))
            child = XUtil.getNextSiblingElement(child);
        
        boolean haveAnonType = false;

        if (child != null) {
            
            String childName = child.getNodeName();
            
            if (childName.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                if (child.getAttribute(SchemaSymbols.ATT_NAME).length() > 0) {
                    reportGenericSchemaError("anoymous complexType error element '" + name +"' has a name attribute"); 
                }
                else 
                    typeNameIndex = traverseComplexTypeDecl(child);
                if (typeNameIndex != -1 ) {
                    typeInfo = (ComplexTypeInfo)
                        fComplexTypeRegistry.get(fStringPool.toString(typeNameIndex));
                }
                else {
                    reportGenericSchemaError("traverse complexType error in element '" + name +"'"); 
                }
                
                haveAnonType = true;
            } 
            else if (childName.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                //   TO DO:  the Default and fixed attribute handling should be here.                
                if (child.getAttribute(SchemaSymbols.ATT_NAME).length() > 0) {
                    reportGenericSchemaError("anoymous complexType error element '" + name +"' has a name attribute"); 
                }
                else 
                    typeNameIndex = traverseSimpleTypeDecl(child);
                if (typeNameIndex != -1) {
                    dv = fDatatypeRegistry.getDatatypeValidator(fStringPool.toString(typeNameIndex));
                }
                else {
                    reportGenericSchemaError("traverse simpleType error in element '" + name +"'"); 
                }

                haveAnonType = true;
            } else if (type.equals("")) { // "ur-typed" leaf
                contentSpecType = XMLElementDecl.TYPE_ANY;
                    //REVISIT: is this right?
                //contentSpecType = fStringPool.addSymbol("UR_TYPE");
                // set occurrence count
                contentSpecNodeIndex = -1;
            } else {
                System.out.println("unhandled case in TraverseElementDecl");
            }
        } 

        if (haveAnonType && (type.length()>0)) {
            reportGenericSchemaError( "can have type when have a annoymous type" );
        }
        // type specified as an attribute and no child is type decl.
        else if (!type.equals("")) { 
            if (equivClassElementDecl != null) {
                checkEquivClassOK(elementDecl, equivClassElementDecl); 
            }
            String prefix = "";
            String localpart = type;
            int colonptr = type.indexOf(":");
            if ( colonptr > 0) {
                prefix = type.substring(0,colonptr);
                localpart = type.substring(colonptr+1);
            }
            String typeURI = resolvePrefixToURI(prefix);
            
            // check if the type is from the same Schema
            if (!typeURI.equals(fTargetNSURIString) && !typeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA)) {
                fromAnotherSchema = typeURI;
                typeInfo = getTypeInfoFromNS(typeURI, localpart);
                if (typeInfo == null) {
                    dv = getTypeValidatorFromNS(typeURI, localpart);
                    if (dv == null) {
                        //TO DO: report error here;
                        System.out.println("Counld not find base type " +localpart 
                                           + " in schema " + typeURI);
                    }
                }
            }
            else {
                typeInfo = (ComplexTypeInfo) fComplexTypeRegistry.get(typeURI+","+localpart);
                if (typeInfo == null) {
                    dv = fDatatypeRegistry.getDatatypeValidator(localpart);
                    if (dv == null) {
                        Element topleveltype = getTopLevelComponentByName(SchemaSymbols.ELT_COMPLEXTYPE,localpart);
                        if (topleveltype != null) {
                            if (fCurrentTypeNameStack.search((Object)localpart) > - 1) {
                                //then we found a recursive element using complexType.
                                // REVISIT: this will be broken when recursing happens between 2 schemas
                                fElementRecurseComplex.put(name+","+fCurrentScope, localpart);
                                return new QName(-1, fStringPool.addSymbol(name), fStringPool.addSymbol(name), -1);
                            }
                            else {
                                typeNameIndex = traverseComplexTypeDecl( topleveltype );
                                typeInfo = (ComplexTypeInfo)
                                    fComplexTypeRegistry.get(fStringPool.toString(typeNameIndex));
                            }
                        }
                        else {
                            topleveltype = getTopLevelComponentByName(SchemaSymbols.ELT_SIMPLETYPE, localpart);
                            if (topleveltype != null) {
                                typeNameIndex = traverseSimpleTypeDecl( topleveltype );
                                dv = fDatatypeRegistry.getDatatypeValidator(localpart);
                                //   TO DO:  the Default and fixed attribute handling should be here.
                            }
                            else {
                                reportGenericSchemaError("type not found : " + localpart);
                            }

                        }

                    }
                }
            }
   
        } 
        else if (haveAnonType){
            if (equivClassElementDecl != null ) {
                checkEquivClassOK(elementDecl, equivClassElementDecl); 
            }

        }
        // this element is ur-type
        else {
            // if there is equivClass affiliation, then grab its type and stick it to this element
            if (equivClassElementDecl != null) {
                int equivClassElementDeclIndex = 
                    fSchemaGrammar.getElementDeclIndex(getLocalPartIndex(equivClass),TOP_LEVEL_SCOPE);
                if ( equivClassElementDeclIndex == -1) {
                    traverseElementDecl(equivClassElementDecl);
                    equivClassElementDeclIndex = 
                        fSchemaGrammar.getElementDeclIndex(getLocalPartIndex(equivClass),TOP_LEVEL_SCOPE);
                }
                ComplexTypeInfo equivClassEltType = fSchemaGrammar.getElementComplexTypeInfo( equivClassElementDeclIndex );
            }
        }

        if (typeInfo == null && dv==null) {
            reportGenericSchemaError ("untyped element : " + name );
        }
        // if element belongs to a compelx type
        if (typeInfo!=null) {
            contentSpecNodeIndex = typeInfo.contentSpecHandle;
            contentSpecType = typeInfo.contentType;
            scopeDefined = typeInfo.scopeDefined;
            dv = typeInfo.datatypeValidator;
        }
        
        // if element belongs to a simple type
        if (dv!=null) {
            contentSpecType = XMLElementDecl.TYPE_SIMPLE;
        }

        
        //
        // Create element decl
        //

        int elementNameIndex     = fStringPool.addSymbol(name);
        int localpartIndex = elementNameIndex;
        int uriIndex = -1;
        int enclosingScope = fCurrentScope;

        if ( isQName.equals(SchemaSymbols.ATTVAL_QUALIFIED)||
             fDefaultQualified || isTopLevel(elementDecl) ) {
            uriIndex = fTargetNSURI;
            enclosingScope = TOP_LEVEL_SCOPE;
        }

        //There can never be two elements with the same name in the same scope.
        if (fSchemaGrammar.getElementDeclIndex(localpartIndex, enclosingScope) > -1) {
            reportGenericSchemaError("duplicate element decl in the same scope : " + 
                              fStringPool.toString(localpartIndex));
        }

        QName eltQName = new QName(-1,localpartIndex,elementNameIndex,uriIndex);
        
        // add element decl to pool
        
        int attrListHead = -1 ;

        // copy up attribute decls from type object
        if (typeInfo != null) {
            attrListHead = typeInfo.attlistHead;
        }
        int elementIndex = fSchemaGrammar.addElementDecl(eltQName, enclosingScope, scopeDefined, 
                                                         contentSpecType, contentSpecNodeIndex, 
                                                         attrListHead, dv);
        if ( DEBUGGING ) {
            /***/
            System.out.println("########elementIndex:"+elementIndex+" "+elementDecl.getAttribute(SchemaSymbols.ATT_NAME)
                               +" eltType:"+name+" contentSpecType:"+contentSpecType+
                               " SpecNodeIndex:"+ contentSpecNodeIndex +" enclosingScope: " +enclosingScope +
                               " scopeDefined: " +scopeDefined);
             /***/
        }

        if (typeInfo != null) {
            fSchemaGrammar.setElementComplexTypeInfo(elementIndex, typeInfo);
        }
        else {
            fSchemaGrammar.setElementComplexTypeInfo(elementIndex, typeInfo);

            // REVISIT: should we report error from here?
        }

        // mark element if its type belongs to different Schema.
        fSchemaGrammar.setElementFromAnotherSchemaURI(elementIndex, fromAnotherSchema);

        
        return eltQName;

    }// end of method traverseElementDecl(Element)


    int getLocalPartIndex(String fullName){
        int colonAt = fullName.indexOf(":"); 
        String localpart = fullName;
        if (  colonAt > -1 ) {
            localpart = fullName.substring(colonAt+1);
        }
        return fStringPool.addSymbol(localpart);
    }
    
    String getLocalPart(String fullName){
        int colonAt = fullName.indexOf(":"); 
        String localpart = fullName;
        if (  colonAt > -1 ) {
            localpart = fullName.substring(colonAt+1);
        }
        return localpart;
    }
    
    private void checkEquivClassOK(Element elementDecl, Element equivClassElementDecl){
        //TO DO!!
    }
    
    private Element getTopLevelComponentByName(String componentCategory, String name) throws Exception {
        Element child = XUtil.getFirstChildElement(fSchemaRootElement);

        if (child == null) {
            return null;
        }

        while (child != null ){
            if ( child.getNodeName().equals(componentCategory)) {
                if (child.getAttribute(SchemaSymbols.ATT_NAME).equals(name)) {
                    return child;
                }
            }
            child = XUtil.getNextSiblingElement(child);
        }

        return null;
    }

    private boolean isTopLevel(Element component) {
        //REVISIT, is this the right way to check ?
        /****
        if (component.getParentNode() == fSchemaRootElement ) {
            return true;
        }
        /****/
        if (component.getParentNode().getNodeName().endsWith(SchemaSymbols.ELT_SCHEMA) ) {
            return true;
        }
        return false;
    }
    
    DatatypeValidator getTypeValidatorFromNS(String newSchemaURI, String localpart){
        Grammar grammar = fGrammarResolver.getGrammar(newSchemaURI);
        if (grammar != null && grammar instanceof SchemaGrammar) {
            SchemaGrammar sGrammar = (SchemaGrammar) grammar;
            DatatypeValidator dv = (DatatypeValidator) fSchemaGrammar.getDatatypeRegistry().getDatatypeValidator(localpart);
            return dv;
        }
        else {
            //TO DO: report internal erro here
            System.out.println("could not resolver URI : " + newSchemaURI + " to a SchemaGrammar in getTypeValidatorFromNS");
        }
        return null;
    }

    ComplexTypeInfo getTypeInfoFromNS(String newSchemaURI, String localpart){
        Grammar grammar = fGrammarResolver.getGrammar(newSchemaURI);
        if (grammar != null && grammar instanceof SchemaGrammar) {
            SchemaGrammar sGrammar = (SchemaGrammar) grammar;
            ComplexTypeInfo typeInfo = (ComplexTypeInfo) fSchemaGrammar.getComplexTypeRegistry().get(newSchemaURI+","+localpart);
            return typeInfo;
        }
        else {
            //TO DO: report internal erro here
            System.out.println("could not resolver URI : " + newSchemaURI + " to a SchemaGrammar in getTypeInfoFromNS");
        }
        return null;
    }
    /**
     * Traverse attributeGroup Declaration
     * 
     *   <attributeGroup
     *         id = ID
     *         ref = QName>
     *         Content: (annotation?)
     *      </>
     * 
     * @param elementDecl
     * @exception Exception
     */
    /*private int traverseAttributeGroupDecl( Element attributeGroupDecl ) throws Exception {
        int attributeGroupID         =  fStringPool.addSymbol(
                                                             attributeGroupDecl.getAttribute( SchemaSymbols.ATTVAL_ID ));

        int attributeGroupName      =  fStringPool.addSymbol(
                                                            attributeGroupDecl.getAttribute( SchemaSymbols.ATT_NAME ));

        return -1;
    }*/


    /**
     * Traverse Group Declaration.
     * 
     * <group 
     *         id = ID 
     *         maxOccurs = string 
     *         minOccurs = nonNegativeInteger 
     *         name = NCName 
     *         ref = QName>
     *   Content: (annotation? , (element | group | all | choice | sequence | any)*)
     * <group/>
     * 
     * @param elementDecl
     * @return 
     * @exception Exception
     */
    private int traverseGroupDecl( Element groupDecl ) throws Exception {
        int groupID         =  fStringPool.addSymbol(
            groupDecl.getAttribute( SchemaSymbols.ATTVAL_ID ));

        int groupMaxOccurs  =  fStringPool.addSymbol(
            groupDecl.getAttribute( SchemaSymbols.ATT_MAXOCCURS ));
        int groupMinOccurs  =  fStringPool.addSymbol(
            groupDecl.getAttribute( SchemaSymbols.ATT_MINOCCURS ));

        //int groupName      =  fStringPool.addSymbol(
            //groupDecl.getAttribute( SchemaSymbols.ATT_NAME ));

        int grouRef        =  fStringPool.addSymbol(
            groupDecl.getAttribute( SchemaSymbols.ATT_REF ));

        String groupName = groupDecl.getAttribute(SchemaSymbols.ATT_NAME);
        String ref = groupDecl.getAttribute(SchemaSymbols.ATT_REF);

        if (!ref.equals("")) {
            if (XUtil.getFirstChildElement(groupDecl) != null)
                reportSchemaError(SchemaMessageProvider.NoContentForRef, null);
            String prefix = "";
            String localpart = ref;
            int colonptr = ref.indexOf(":");
            if ( colonptr > 0) {
                prefix = ref.substring(0,colonptr);
                localpart = ref.substring(colonptr+1);
            }
            int localpartIndex = fStringPool.addSymbol(localpart);
            
            String uriStr = resolvePrefixToURI(prefix);
            if (!uriStr.equals(fTargetNSURIString)) {
                return traverseGroupDeclFromAnotherSchema(localpart, uriStr);
            }

            int contentSpecIndex = -1;
            Element referredGroup = getTopLevelComponentByName(SchemaSymbols.ELT_GROUP,localpart);
            if (referredGroup == null) {
                reportGenericSchemaError("Group " + localpart + " not found in the Schema");
                //REVISIT, this should be some custom Exception
                throw new Exception("Group " + localpart + " not found in the Schema");
            }
            else {
                contentSpecIndex = traverseGroupDecl(referredGroup);
            }
            
            return contentSpecIndex;
        }

        boolean traverseElt = true; 
        if (fCurrentScope == TOP_LEVEL_SCOPE) {
            traverseElt = false;
        }

        Element child = XUtil.getFirstChildElement(groupDecl);
        while (child != null && child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION))
            child = XUtil.getNextSiblingElement(child);

        int contentSpecType = 0;
        int csnType = 0;
        int allChildren[] = null;
        int allChildCount = 0;

        csnType = XMLContentSpec.CONTENTSPECNODE_SEQ;
        contentSpecType = XMLElementDecl.TYPE_CHILDREN;
        
        int left = -2;
        int right = -2;
        boolean hadContent = false;
        boolean seeAll = false;
        boolean seeParticle = false;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            int index = -2;
            hadContent = true;

            boolean illegalChild = false;

            String childName = child.getNodeName();
            if (childName.equals(SchemaSymbols.ELT_ELEMENT)) {
                QName eltQName = traverseElementDecl(child);
                index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                       eltQName.localpart,
                                                       eltQName.uri, 
                                                       false);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_GROUP)) {
                index = traverseGroupDecl(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_ALL)) {
                index = traverseAll(child);
                //seeParticle = true;
                seeAll = true;
            } 
            else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                index = traverseChoice(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                index = traverseSequence(child);
                seeParticle = true;

            } 
            else {
                illegalChild = true;
                reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                                  new Object [] { "group", childName });
            }
            
            if ( ! illegalChild ) {
                index = expandContentModel( index, child);
            }

            if (seeParticle && seeAll) {
                reportSchemaError( SchemaMessageProvider.GroupContentRestricted,
                                   new Object [] { "'all' needs to be 'the' only Child", childName});
            }

            if (left == -2) {
                left = index;
            } else if (right == -2) {
                right = index;
            } else {
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);
                right = index;
            }
        }
        if (hadContent && right != -2)
            left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);


        return left;
    }

    private int traverseGroupDeclFromAnotherSchema( String groupName , String uriStr ) throws Exception {
        
        SchemaGrammar aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uriStr);
        if (uriStr == null || ! (aGrammar instanceof SchemaGrammar) ) {
            reportGenericSchemaError("!!Schema not found : " + uriStr);
            return -1;
        }
        
        Element groupDecl = (Element) aGrammar.topLevelGroupDecls.get((Object)groupName);
        if (groupDecl == null) {
            reportGenericSchemaError( "no group named \"" + groupName 
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }

        boolean traverseElt = true; 
        if (fCurrentScope == TOP_LEVEL_SCOPE) {
            traverseElt = false;
        }

        Element child = XUtil.getFirstChildElement(groupDecl);
        while (child != null && child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION))
            child = XUtil.getNextSiblingElement(child);

        int contentSpecType = 0;
        int csnType = 0;
        int allChildren[] = null;
        int allChildCount = 0;

        csnType = XMLContentSpec.CONTENTSPECNODE_SEQ;
        contentSpecType = XMLElementDecl.TYPE_CHILDREN;
        
        int left = -2;
        int right = -2;
        boolean hadContent = false;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            int index = -2;
            hadContent = true;

            boolean seeParticle = false;
            String childName = child.getNodeName();
            int childNameIndex = fStringPool.addSymbol(childName);
            String formAttrVal = child.getAttribute(SchemaSymbols.ATT_FORM);
            if (childName.equals(SchemaSymbols.ELT_ELEMENT)) {
                QName eltQName = traverseElementDecl(child); 
                index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                       eltQName.localpart,
                                                       eltQName.uri, 
                                                       false);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_GROUP)) {
                index = traverseGroupDecl(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_ALL)) {
                index = traverseAll(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                index = traverseChoice(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                index = traverseSequence(child);
                seeParticle = true;

            } 
            else {
                reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                                  new Object [] { "group", childName });
            }

            if (seeParticle) {
                index = expandContentModel( index, child);
            }
            if (left == -2) {
                left = index;
            } else if (right == -2) {
                right = index;
            } else {
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);
                right = index;
            }
        }
        if (hadContent && right != -2)
            left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);


        return left;


    } // end of method traverseGroupDeclFromAnotherSchema
    
    /**
    *
    * Traverse the Sequence declaration
    * 
    * <sequence 
    *   id = ID 
    *   maxOccurs = string 
    *   minOccurs = nonNegativeInteger>
    *   Content: (annotation? , (element | group | choice | sequence | any)*)
    * </sequence>
    * 
    **/
    int traverseSequence (Element sequenceDecl) throws Exception {
            
        Element child = XUtil.getFirstChildElement(sequenceDecl);
        while (child != null && child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION))
            child = XUtil.getNextSiblingElement(child);

        int contentSpecType = 0;
        int csnType = 0;

        csnType = XMLContentSpec.CONTENTSPECNODE_SEQ;
        contentSpecType = XMLElementDecl.TYPE_CHILDREN;

        int left = -2;
        int right = -2;
        boolean hadContent = false;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            int index = -2;
            hadContent = true;

            boolean seeParticle = false;
            String childName = child.getNodeName();
            if (childName.equals(SchemaSymbols.ELT_ELEMENT)) {
                QName eltQName = traverseElementDecl(child);
                index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                       eltQName.localpart,
                                                       eltQName.uri, 
                                                       false);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_GROUP)) {
                index = traverseGroupDecl(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                index = traverseChoice(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                index = traverseSequence(child);
                seeParticle = true;

            } 
            else {
                reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                                  new Object [] { "group", childName });
            }

            if (seeParticle) {
                index = expandContentModel( index, child);
            }
            if (left == -2) {
                left = index;
            } else if (right == -2) {
                right = index;
            } else {
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);
                right = index;
            }
        }

        if (hadContent && right != -2)
            left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);

        return left;
    }
    
    /**
    *
    * Traverse the Sequence declaration
    * 
    * <choice
    *   id = ID 
    *   maxOccurs = string 
    *   minOccurs = nonNegativeInteger>
    *   Content: (annotation? , (element | group | choice | sequence | any)*)
    * </choice>
    * 
    **/
    int traverseChoice (Element choiceDecl) throws Exception {
            
        // REVISIT: traverseChoice, traverseSequence can be combined
        Element child = XUtil.getFirstChildElement(choiceDecl);
        while (child != null && child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION))
            child = XUtil.getNextSiblingElement(child);

        int contentSpecType = 0;
        int csnType = 0;

        csnType = XMLContentSpec.CONTENTSPECNODE_CHOICE;
        contentSpecType = XMLElementDecl.TYPE_CHILDREN;

        int left = -2;
        int right = -2;
        boolean hadContent = false;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            int index = -2;
            hadContent = true;

            boolean seeParticle = false;
            String childName = child.getNodeName();
            if (childName.equals(SchemaSymbols.ELT_ELEMENT)) {
                QName eltQName = traverseElementDecl(child);
                index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                       eltQName.localpart,
                                                       eltQName.uri, 
                                                       false);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_GROUP)) {
                index = traverseGroupDecl(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                index = traverseChoice(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                index = traverseSequence(child);
                seeParticle = true;

            } 
            else {
                reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                                  new Object [] { "group", childName });
            }

            if (seeParticle) {
                index = expandContentModel( index, child);
            }
            if (left == -2) {
                left = index;
            } else if (right == -2) {
                right = index;
            } else {
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);
                right = index;
            }
        }

        if (hadContent && right != -2)
            left = fSchemaGrammar.addContentSpecNode(csnType, left, right, false);

        return left;
    }
    

   /**
    * 
    * Traverse the "All" declaration
    *
    * <all 
    *   id = ID 
    *   maxOccurs = string 
    *   minOccurs = nonNegativeInteger>
    *   Content: (annotation? , (element | group | choice | sequence | any)*)
    * </all>
    *   
    **/

    int traverseAll( Element allDecl) throws Exception {


        Element child = XUtil.getFirstChildElement(allDecl);

        while (child != null && child.getNodeName().equals(SchemaSymbols.ELT_ANNOTATION))
            child = XUtil.getNextSiblingElement(child);

        int allChildren[] = null;
        int allChildCount = 0;

        int left = -2;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {

            int index = -2;
            boolean seeParticle = false;

            String childName = child.getNodeName();

            if (childName.equals(SchemaSymbols.ELT_ELEMENT)) {
                QName eltQName = traverseElementDecl(child);
                index = fSchemaGrammar.addContentSpecNode( XMLContentSpec.CONTENTSPECNODE_LEAF,
                                                       eltQName.localpart,
                                                       eltQName.uri, 
                                                       false);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_GROUP)) {
                index = traverseGroupDecl(child);
                seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
                    index = traverseChoice(child);
                    seeParticle = true;

            } 
            else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
                index = traverseSequence(child);
                seeParticle = true;

            } 
            else {
                reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                                  new Object [] { "group", childName });
            }

            if (seeParticle) {
                index = expandContentModel( index, child);
            }
            try {
                allChildren[allChildCount] = index;
            }
            catch (NullPointerException ne) {
                allChildren = new int[32];
                allChildren[allChildCount] = index;
            }
            catch (ArrayIndexOutOfBoundsException ae) {
                int[] newArray = new int[allChildren.length*2];
                System.arraycopy(allChildren, 0, newArray, 0, allChildren.length);
                allChildren[allChildCount] = index;
            }
            allChildCount++;
        }
        left = buildAllModel(allChildren,allChildCount);

        return left;
    }
    
    /** builds the all content model */
    private int buildAllModel(int children[], int count) throws Exception {

        // build all model
        if (count > 1) {

            // create and initialize singletons
            XMLContentSpec choice = new XMLContentSpec();

            choice.type = XMLContentSpec.CONTENTSPECNODE_CHOICE;
            choice.value = -1;
            choice.otherValue = -1;

            int[] exactChildren = new int[count];
            System.arraycopy(children,0,exactChildren,0,count);
            // build all model
            sort(exactChildren, 0, count);
            int index = buildAllModel(exactChildren, 0, choice);

            return index;
        }

        if (count > 0) {
            return children[0];
        }

        return -1;
    }

    /** Builds the all model. */
    private int buildAllModel(int src[], int offset,
                              XMLContentSpec choice) throws Exception {

        // swap last two places
        if (src.length - offset == 2) {
            int seqIndex = createSeq(src);
            if (choice.value == -1) {
                choice.value = seqIndex;
            }
            else {
                if (choice.otherValue != -1) {
                    choice.value = fSchemaGrammar.addContentSpecNode(choice.type, choice.value, choice.otherValue, false);
                }
                choice.otherValue = seqIndex;
            }
            swap(src, offset, offset + 1);
            seqIndex = createSeq(src);
            if (choice.value == -1) {
                choice.value = seqIndex;
            }
            else {
                if (choice.otherValue != -1) {
                    choice.value = fSchemaGrammar.addContentSpecNode(choice.type, choice.value, choice.otherValue, false);
                }
                choice.otherValue = seqIndex;
            }
            return fSchemaGrammar.addContentSpecNode(choice.type, choice.value, choice.otherValue, false);
        }

        // recurse
        for (int i = offset; i < src.length - 1; i++) {
            choice.value = buildAllModel(src, offset + 1, choice);
            choice.otherValue = -1;
            sort(src, offset, src.length - offset);
            shift(src, offset, i + 1);
        }

        int choiceIndex = buildAllModel(src, offset + 1, choice);
        sort(src, offset, src.length - offset);

        return choiceIndex;

    } // buildAllModel(int[],int,ContentSpecNode,ContentSpecNode):int

    /** Creates a sequence. */
    private int createSeq(int src[]) throws Exception {

        int left = src[0];
        int right = src[1];

        for (int i = 2; i < src.length; i++) {
            left = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_SEQ,
                                                       left, right, false);
            right = src[i];
        }

        return fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_SEQ,
                                                   left, right, false);

    } // createSeq(int[]):int

    /** Shifts a value into position. */
    private void shift(int src[], int pos, int offset) {

        int temp = src[offset];
        for (int i = offset; i > pos; i--) {
            src[i] = src[i - 1];
        }
        src[pos] = temp;

    } // shift(int[],int,int)

    /** Simple sort. */
    private void sort(int src[], final int offset, final int length) {

        for (int i = offset; i < offset + length - 1; i++) {
            int lowest = i;
            for (int j = i + 1; j < offset + length; j++) {
                if (src[j] < src[lowest]) {
                    lowest = j;
                }
            }
            if (lowest != i) {
                int temp = src[i];
                src[i] = src[lowest];
                src[lowest] = temp;
            }
        }

    } // sort(int[],int,int)

    /** Swaps two values. */
    private void swap(int src[], int i, int j) {

        int temp = src[i];
        src[i] = src[j];
        src[j] = temp;

    } // swap(int[],int,int)

    /**
     * Traverse Wildcard declaration
     * 
     * <any 
     *   id = ID 
     *   maxOccurs = string 
     *   minOccurs = nonNegativeInteger 
     *   namespace = ##any | ##other | ##local | list of {uri, ##targetNamespace} 
     *   processContents = lax | skip | strict>
     *   Content: (annotation?)
     * </any>
     * @param elementDecl
     * @return 
     * @exception Exception
     */
    private int traverseWildcardDecl( Element wildcardDecl ) throws Exception {
        int wildcardID         =  fStringPool.addSymbol(
                                                       wildcardDecl.getAttribute( SchemaSymbols.ATTVAL_ID ));

        int wildcardMaxOccurs  =  fStringPool.addSymbol(
                                                       wildcardDecl.getAttribute( SchemaSymbols.ATT_MAXOCCURS ));

        int wildcardMinOccurs  =  fStringPool.addSymbol(
                                                       wildcardDecl.getAttribute( SchemaSymbols.ATT_MINOCCURS ));

        int wildcardNamespace  =  fStringPool.addSymbol(
                                                       wildcardDecl.getAttribute( SchemaSymbols.ATT_NAMESPACE ));

        int wildcardProcessContents =  fStringPool.addSymbol(
                                                            wildcardDecl.getAttribute( SchemaSymbols.ATT_PROCESSCONTENTS ));


        int wildcardContent =  fStringPool.addSymbol(
                                                    wildcardDecl.getAttribute( SchemaSymbols.ATT_CONTENT ));


        return -1;
    }
    
    

    // utilities from Tom Watson's SchemaParser class
    // TO DO: Need to make this more conformant with Schema int type parsing

    private int parseInt (String intString) throws Exception
    {
            if ( intString.equals("*") ) {
                    return SchemaSymbols.INFINITY;
            } else {
                    return Integer.parseInt (intString);
            }
    }

    private int parseSimpleDerivedBy (String derivedByString) throws Exception
    {
            if ( derivedByString.equals (SchemaSymbols.ATTVAL_LIST) ) {
                    return SchemaSymbols.LIST;
            } 
            else if ( derivedByString.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                    return SchemaSymbols.RESTRICTION;
            }  
            else {
                    reportGenericSchemaError ("SimpleType: Invalid value for 'derivedBy'");
                    return -1;
            }
    }

    private int parseComplexDerivedBy (String derivedByString)  throws Exception
    {
            if ( derivedByString.equals (SchemaSymbols.ATTVAL_EXTENSION) ) {
                    return SchemaSymbols.EXTENSION;
            } 
            else if ( derivedByString.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                    return SchemaSymbols.RESTRICTION;
            } 
            else {
                    reportGenericSchemaError ( "ComplexType: Invalid value for 'derivedBy'" );
                    return -1;
            }
    }

    private int parseSimpleFinal (String finalString) throws Exception
    {
            if ( finalString.equals (SchemaSymbols.ATTVAL_POUNDALL) ) {
                    return SchemaSymbols.ENUMERATION+SchemaSymbols.RESTRICTION+SchemaSymbols.LIST+SchemaSymbols.REPRODUCTION;
            } else {
                    int enumerate = 0;
                    int restrict = 0;
                    int list = 0;
                    int reproduce = 0;

                    StringTokenizer t = new StringTokenizer (finalString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                            reportGenericSchemaError ("restriction in set twice");
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_LIST) ) {
                                    if ( list == 0 ) {
                                            list = SchemaSymbols.LIST;
                                    } else {
                                            reportGenericSchemaError ("list in set twice");
                                    }
                            }
                            else {
                                reportGenericSchemaError (  "Invalid value (" + 
                                                            finalString +
                                                            ")" );
                            }
                    }

                    return enumerate+restrict+list+reproduce;
            }
    }

    private int parseComplexContent (String contentString)  throws Exception
    {
            if ( contentString.equals (SchemaSymbols.ATTVAL_EMPTY) ) {
                    return XMLElementDecl.TYPE_EMPTY;
            } else if ( contentString.equals (SchemaSymbols.ATTVAL_ELEMENTONLY) ) {
                    return XMLElementDecl.TYPE_CHILDREN;
            } else if ( contentString.equals (SchemaSymbols.ATTVAL_TEXTONLY) ) {
                    return XMLElementDecl.TYPE_SIMPLE;
            } else if ( contentString.equals (SchemaSymbols.ATTVAL_MIXED) ) {
                    return XMLElementDecl.TYPE_MIXED;
            } else {
                    reportGenericSchemaError ( "Invalid value for content" );
                    return -1;
            }
    }

    private int parseDerivationSet (String finalString)  throws Exception
    {
            if ( finalString.equals ("#all") ) {
                    return SchemaSymbols.EXTENSION+SchemaSymbols.RESTRICTION+SchemaSymbols.REPRODUCTION;
            } else {
                    int extend = 0;
                    int restrict = 0;
                    int reproduce = 0;

                    StringTokenizer t = new StringTokenizer (finalString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ATTVAL_EXTENSION) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EXTENSION;
                                    } else {
                                            reportGenericSchemaError ( "extension already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                            reportGenericSchemaError ( "restriction already in set" );
                                    }
                            } else {
                                    reportGenericSchemaError ( "Invalid final value (" + finalString + ")" );
                            }
                    }

                    return extend+restrict+reproduce;
            }
    }

    private int parseBlockSet (String finalString)  throws Exception
    {
            if ( finalString.equals ("#all") ) {
                    return SchemaSymbols.EQUIVCLASS+SchemaSymbols.EXTENSION+SchemaSymbols.LIST+SchemaSymbols.RESTRICTION+SchemaSymbols.REPRODUCTION;
            } else {
                    int extend = 0;
                    int restrict = 0;
                    int reproduce = 0;

                    StringTokenizer t = new StringTokenizer (finalString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ATTVAL_EQUIVCLASS) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EQUIVCLASS;
                                    } else {
                                            reportGenericSchemaError ( "'equivClass' already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_EXTENSION) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EXTENSION;
                                    } else {
                                            reportGenericSchemaError ( "extension already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_LIST) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.LIST;
                                    } else {
                                            reportGenericSchemaError ( "'list' already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                            reportGenericSchemaError ( "restriction already in set" );
                                    }
                            } else {
                                    reportGenericSchemaError ( "Invalid final value (" + finalString + ")" );
                            }
                    }

                    return extend+restrict+reproduce;
            }
    }

    private int parseFinalSet (String finalString)  throws Exception
    {
            if ( finalString.equals ("#all") ) {
                    return SchemaSymbols.EQUIVCLASS+SchemaSymbols.EXTENSION+SchemaSymbols.LIST+SchemaSymbols.RESTRICTION+SchemaSymbols.REPRODUCTION;
            } else {
                    int extend = 0;
                    int restrict = 0;
                    int reproduce = 0;

                    StringTokenizer t = new StringTokenizer (finalString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ATTVAL_EQUIVCLASS) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EQUIVCLASS;
                                    } else {
                                            reportGenericSchemaError ( "'equivClass' already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_EXTENSION) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EXTENSION;
                                    } else {
                                            reportGenericSchemaError ( "extension already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_LIST) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.LIST;
                                    } else {
                                            reportGenericSchemaError ( "'list' already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                            reportGenericSchemaError ( "restriction already in set" );
                                    }
                            } else {
                                    reportGenericSchemaError ( "Invalid final value (" + finalString + ")" );
                            }
                    }

                    return extend+restrict+reproduce;
            }
    }

    private void reportGenericSchemaError (String error) throws Exception {
        if (fErrorReporter == null) {
            System.err.println("__TraverseSchemaError__ : " + error);       
        }
        else {
            reportSchemaError (SchemaMessageProvider.GenericError, new Object[] { error });
        }        
    }


    private void reportSchemaError(int major, Object args[]) throws Exception {
        if (fErrorReporter == null) {
            System.out.println("__TraverseSchemaError__ : " + SchemaMessageProvider.fgMessageKeys[major]);
            for (int i=0; i< args.length ; i++) {
                System.out.println((String)args[i]);    
            }
        }
        else {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       SchemaMessageProvider.SCHEMA_DOMAIN,
                                       major,
                                       SchemaMessageProvider.MSG_NONE,
                                       args,
                                       XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
        }
    }

    //Unit Test here
    public static void main(String args[] ) {

        if( args.length != 1 ) {
            System.out.println( "Error: Usage java TraverseSchema yourFile.xsd" );
            System.exit(0);
        }

        DOMParser parser = new DOMParser() {
            public void ignorableWhitespace(char ch[], int start, int length) {}
            public void ignorableWhitespace(int dataIdx) {}
        };
        parser.setEntityResolver( new Resolver() );
        parser.setErrorHandler(  new ErrorHandler() );

        try {
        parser.setFeature("http://xml.org/sax/features/validation", false);
        parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
        }catch(  org.xml.sax.SAXNotRecognizedException e ) {
            e.printStackTrace();
        }catch( org.xml.sax.SAXNotSupportedException e ) {
            e.printStackTrace();
        }

        try {
        parser.parse( args[0]);
        }catch( IOException e ) {
            e.printStackTrace();
        }catch( SAXException e ) {
            e.printStackTrace();
        }

        Document     document   = parser.getDocument(); //Our Grammar

        OutputFormat    format  = new OutputFormat( document );
        java.io.StringWriter outWriter = new java.io.StringWriter();
        XMLSerializer    serial = new XMLSerializer( outWriter,format);

        TraverseSchema tst = null;
        try {
            Element root   = document.getDocumentElement();// This is what we pass to TraverserSchema
            //serial.serialize( root );
            //System.out.println(outWriter.toString());

            tst = new TraverseSchema( root, new StringPool(), new SchemaGrammar(), (GrammarResolver) new GrammarResolverImpl() );
            }
            catch (Exception e) {
                e.printStackTrace(System.err);
            }
            
            parser.getDocument();
    }

    static class Resolver implements EntityResolver {
        private static final String SYSTEM[] = {
            "http://www.w3.org/TR/2000/WD-xmlschema-1-20000407/structures.dtd",
            "http://www.w3.org/TR/2000/WD-xmlschema-1-20000407/datatypes.dtd",
            "http://www.w3.org/TR/2000/WD-xmlschema-1-20000407/versionInfo.ent",
        };
        private static final String PATH[] = {
            "structures.dtd",
            "datatypes.dtd",
            "versionInfo.ent",
        };

        public InputSource resolveEntity(String publicId, String systemId)
        throws IOException {

            // looking for the schema DTDs?
            for (int i = 0; i < SYSTEM.length; i++) {
                if (systemId.equals(SYSTEM[i])) {
                    InputSource source = new InputSource(getClass().getResourceAsStream(PATH[i]));
                    source.setPublicId(publicId);
                    source.setSystemId(systemId);
                    return source;
                }
            }

            // use default resolution
            return null;

        } // resolveEntity(String,String):InputSource

    } // class Resolver

    static class ErrorHandler implements org.xml.sax.ErrorHandler {

        /** Warning. */
        public void warning(SAXParseException ex) {
            System.err.println("[Warning] "+
                               getLocationString(ex)+": "+
                               ex.getMessage());
        }

        /** Error. */
        public void error(SAXParseException ex) {
            System.err.println("[Error] "+
                               getLocationString(ex)+": "+
                               ex.getMessage());
        }

        /** Fatal error. */
        public void fatalError(SAXParseException ex) throws SAXException {
            System.err.println("[Fatal Error] "+
                               getLocationString(ex)+": "+
                               ex.getMessage());
            throw ex;
        }

        //
        // Private methods
        //

        /** Returns a string of the location. */
        private String getLocationString(SAXParseException ex) {
            StringBuffer str = new StringBuffer();

            String systemId_ = ex.getSystemId();
            if (systemId_ != null) {
                int index = systemId_.lastIndexOf('/');
                if (index != -1)
                    systemId_ = systemId_.substring(index + 1);
                str.append(systemId_);
            }
            str.append(':');
            str.append(ex.getLineNumber());
            str.append(':');
            str.append(ex.getColumnNumber());

            return str.toString();

        } // getLocationString(SAXParseException):String
    }


}




