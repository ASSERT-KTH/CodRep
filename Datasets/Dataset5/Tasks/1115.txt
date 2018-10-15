referredAttrDecl.defaultValue = fixedStr;

/* 
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000,2001 The Apache Software Foundation.  
 * All rights reserved.
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
import  org.apache.xerces.validators.schema.identity.Field;
import  org.apache.xerces.validators.schema.identity.IdentityConstraint;
import  org.apache.xerces.validators.schema.identity.Key;
import  org.apache.xerces.validators.schema.identity.KeyRef;
import  org.apache.xerces.validators.schema.identity.Selector;
import  org.apache.xerces.validators.schema.identity.Unique;
import  org.apache.xerces.validators.schema.identity.XPath;
import  org.apache.xerces.validators.schema.identity.XPathException;
import  org.apache.xerces.validators.datatype.DatatypeValidator;
import  org.apache.xerces.validators.datatype.DatatypeValidatorFactoryImpl;
import  org.apache.xerces.validators.datatype.IDDatatypeValidator;
import  org.apache.xerces.validators.datatype.NOTATIONDatatypeValidator;
import  org.apache.xerces.validators.datatype.StringDatatypeValidator;  
import  org.apache.xerces.validators.datatype.ListDatatypeValidator;
import  org.apache.xerces.validators.datatype.UnionDatatypeValidator; 
import  org.apache.xerces.validators.datatype.InvalidDatatypeValueException;
import  org.apache.xerces.utils.StringPool;
import  org.w3c.dom.Element;

import java.io.IOException;
import java.util.*;
import java.net.URL;
import java.net.MalformedURLException;

//REVISIT: for now, import everything in the DOM package
import  org.w3c.dom.*;

//Unit Test 
import  org.apache.xerces.parsers.DOMParser;
import  org.apache.xerces.validators.common.XMLValidator;
import  org.apache.xerces.validators.datatype.DatatypeValidator.*;
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
import  org.w3c.dom.Document;
/** Don't check the following code in because it creates a dependency on
    the serializer, preventing to package the parser without the serializer.
import  org.apache.xml.serialize.OutputFormat;
import  org.apache.xml.serialize.XMLSerializer;
**/
import  org.apache.xerces.validators.schema.SchemaSymbols;

/**
 * Instances of this class get delegated to Traverse the Schema and
 * to populate the Grammar internal representation by
 * instances of Grammar objects.
 * Traverse a Schema Grammar:
 * 
 * @author Eric Ye, IBM
 * @author Jeffrey Rodriguez, IBM
 * @author Andy Clark, IBM
 *  
 * @see org.apache.xerces.validators.common.Grammar
 *
 * @version $Id$
 */
public class TraverseSchema implements 
                            NamespacesScope.NamespacesHandler{

    
    //CONSTANTS
    private static final int TOP_LEVEL_SCOPE = -1;

    /** Identity constraint keywords. */
    private static final String[][] IDENTITY_CONSTRAINTS = {
        { SchemaSymbols.URI_SCHEMAFORSCHEMA, SchemaSymbols.ELT_UNIQUE },
        { SchemaSymbols.URI_SCHEMAFORSCHEMA, SchemaSymbols.ELT_KEY }, 
        { SchemaSymbols.URI_SCHEMAFORSCHEMA, SchemaSymbols.ELT_KEYREF },
    };
    private static final String redefIdentifier = "_redefined";

    // Flags for handleOccurrences to indicate any special
    // restrictions on minOccurs and maxOccurs relating to "all".
    //    NOT_ALL_CONTEXT    - not processing an <all>
    //    PROCESSING_ALL     - processing an <element> in an <all>
    //    GROUP_REF_WITH_ALL - processing <group> reference that contained <all>
    //    CHILD_OF_GROUP     - processing a child of a model group definition
    private static final int NOT_ALL_CONTEXT    = 0;
    private static final int PROCESSING_ALL     = 1;
    private static final int GROUP_REF_WITH_ALL = 2;
    private static final int CHILD_OF_GROUP     = 4;

    //debugging
    private static final boolean DEBUGGING = false;

    /** Compile to true to debug identity constraints. */
    private static final boolean DEBUG_IDENTITY_CONSTRAINTS = false;
    
    /** 
     * Compile to true to debug datatype validator lookup for
     * identity constraint support.
     */
    private static final boolean DEBUG_IC_DATATYPES = false;

    //private data members

    private boolean fFullConstraintChecking = false;

    private XMLErrorReporter    fErrorReporter = null;
    private StringPool          fStringPool    = null;

    private GrammarResolver fGrammarResolver = null;
    private SchemaGrammar fSchemaGrammar = null;

    private Element fSchemaRootElement;
    // this is always set to refer to the root of the linked list containing the root info of schemas under redefinition.
    private SchemaInfo fSchemaInfoListRoot = null;
    private SchemaInfo fCurrentSchemaInfo = null;
    private boolean fRedefineSucceeded;

    private DatatypeValidatorFactoryImpl fDatatypeRegistry = null;

    private Hashtable fComplexTypeRegistry = new Hashtable();
    private Hashtable fAttributeDeclRegistry = new Hashtable();
    
    // stores the names of groups that we've traversed so we can avoid multiple traversals
    // qualified group names are keys and their contentSpecIndexes are values.  
    private Hashtable fGroupNameRegistry = new Hashtable();
    // this Hashtable keeps track of whether a given redefined group does so by restriction.
    private Hashtable fRestrictedRedefinedGroupRegistry = new Hashtable();

    // stores "final" values of simpleTypes--no clean way to integrate this into the existing datatype validation structure...
    private Hashtable fSimpleTypeFinalRegistry = new Hashtable();

    // stores <notation> decl
    private Hashtable fNotationRegistry = new Hashtable();

    private Vector fIncludeLocations = new Vector();
    private Vector fImportLocations = new Vector();
    private Hashtable fRedefineLocations = new Hashtable();
    private Vector fTraversedRedefineElements = new Vector();
    // Hashtable associating attributeGroups within a <redefine> which
    // restrict attributeGroups in the original schema with the
    // new name for those groups in the modified redefined schema.  
    private Hashtable fRedefineAttributeGroupMap = null;

    // simpleType data
    private Hashtable fFacetData = new Hashtable(10);
    private Stack fSimpleTypeNameStack = new Stack();
    private String fListName = "";


    private int fAnonTypeCount =0;
    private int fScopeCount=0;
    private int fCurrentScope=TOP_LEVEL_SCOPE;
    private int fSimpleTypeAnonCount = 0;
    private Stack fCurrentTypeNameStack = new Stack();
    private Stack fCurrentGroupNameStack = new Stack();
    private Hashtable fElementRecurseComplex = new Hashtable();

    private boolean fElementDefaultQualified = false;
    private boolean fAttributeDefaultQualified = false;
    private int fBlockDefault = 0;
    private int fFinalDefault = 0;

    private int fTargetNSURI;
    private String fTargetNSURIString = "";
    private NamespacesScope fNamespacesScope = null;
    private String fCurrentSchemaURL = "";

    private XMLAttributeDecl fTempAttributeDecl = new XMLAttributeDecl();
    private XMLAttributeDecl fTemp2AttributeDecl = new XMLAttributeDecl();
    private XMLElementDecl fTempElementDecl = new XMLElementDecl();
    private XMLElementDecl fTempElementDecl2 = new XMLElementDecl();
    private XMLContentSpec tempContentSpec1 = new XMLContentSpec();
    private XMLContentSpec tempContentSpec2 = new XMLContentSpec();

    private EntityResolver  fEntityResolver = null;
    private SubstitutionGroupComparator fSComp = null;
    
    private Hashtable fIdentityConstraints = new Hashtable();
    // Yet one more data structure; this one associates
    // <unique> and <key> QNames with their corresponding objects,
    // so that <keyRef>s can find them.
    private Hashtable fIdentityConstraintNames = new Hashtable();
    
    // General Attribute Checking
    private GeneralAttrCheck fGeneralAttrCheck = null;
    private int fXsiURI;

   // REVISIT: maybe need to be moved into SchemaGrammar class
    public class ComplexTypeInfo {
        public String typeName;
        
        public DatatypeValidator baseDataTypeValidator;
        public ComplexTypeInfo baseComplexTypeInfo;

        public int derivedBy = 0;
        public int blockSet = 0;
        public int finalSet = 0;

        public int miscFlags=0;

        public int scopeDefined = -1;

        public int contentType;
        public int contentSpecHandle = -1;
        public int templateElementIndex = -1;
        public int attlistHead = -1;
        public DatatypeValidator datatypeValidator;

        public boolean isAbstractType() {
           return ((miscFlags & CT_IS_ABSTRACT)!=0);
        }
        public boolean containsAttrTypeID () {
           return ((miscFlags & CT_CONTAINS_ATTR_TYPE_ID)!=0);
        }
        public boolean declSeen () {
           return ((miscFlags & CT_DECL_SEEN)!=0);
        }

        public void setIsAbstractType() {
           miscFlags |= CT_IS_ABSTRACT;
        }
        public void setContainsAttrTypeID() {
           miscFlags |= CT_CONTAINS_ATTR_TYPE_ID;
        }
        public void setDeclSeen() {
           miscFlags |= CT_DECL_SEEN;               
        }
          
    }
    private static final int CT_IS_ABSTRACT=1;
    private static final int CT_CONTAINS_ATTR_TYPE_ID=2;
    private static final int CT_DECL_SEEN=4;    // indicates that the declaration was 
                                                // traversed as opposed to processed due 
                                                // to a forward reference

    private class ComplexTypeRecoverableError extends Exception {
        ComplexTypeRecoverableError() {super();}
        ComplexTypeRecoverableError(String s) {super(s);}
    }

    private class ParticleRecoverableError extends Exception {
        ParticleRecoverableError(String s) {super(s);}
    }

    //REVISIT: verify the URI.
    public final static String SchemaForSchemaURI = "http://www.w3.org/TR-1/Schema";

    private TraverseSchema( ) {
        // new TraverseSchema() is forbidden;
    }

    public void setFullConstraintCheckingEnabled() {
        fFullConstraintChecking = true;
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

    public boolean particleEmptiable(int contentSpecIndex) {

       if (!fFullConstraintChecking) {
           return true;
       }
       if (minEffectiveTotalRange(contentSpecIndex)==0) 
         return true;
       else
         return false;
    }

    public int minEffectiveTotalRange(int contentSpecIndex) {

       fSchemaGrammar.getContentSpec(contentSpecIndex, tempContentSpec1);
       int type = tempContentSpec1.type;
       if (type == XMLContentSpec.CONTENTSPECNODE_SEQ ||
           type == XMLContentSpec.CONTENTSPECNODE_ALL) {
          return minEffectiveTotalRangeSeq(contentSpecIndex);
       }
       else if (type == XMLContentSpec.CONTENTSPECNODE_CHOICE) {
          return minEffectiveTotalRangeChoice(contentSpecIndex); 
       }
       else {
          return(fSchemaGrammar.getContentSpecMinOccurs(contentSpecIndex));
       }
       
    }
    
    private int minEffectiveTotalRangeSeq(int csIndex) {

       fSchemaGrammar.getContentSpec(csIndex, tempContentSpec1);
       int type = tempContentSpec1.type;
       int left = tempContentSpec1.value;
       int right = tempContentSpec1.otherValue;
       int min = fSchemaGrammar.getContentSpecMinOccurs(csIndex);

       int result;
       if (right == -2)
          result = min * minEffectiveTotalRange(left);
       else
          result = min * (minEffectiveTotalRange(left) + minEffectiveTotalRange(right));
       return result;

    }
    private int minEffectiveTotalRangeChoice(int csIndex) {

       fSchemaGrammar.getContentSpec(csIndex, tempContentSpec1);
       int type = tempContentSpec1.type;
       int left = tempContentSpec1.value;
       int right = tempContentSpec1.otherValue;
       int min = fSchemaGrammar.getContentSpecMinOccurs(csIndex);

       int result;
       if (right == -2)
          result = min * minEffectiveTotalRange(left);
       else {
          int minLeft = minEffectiveTotalRange(left);
          int minRight = minEffectiveTotalRange(right);
          result = min * ((minLeft < minRight)?minLeft:minRight);
       }
       return result;
    }

    public int maxEffectiveTotalRange(int contentSpecIndex) {

       fSchemaGrammar.getContentSpec(contentSpecIndex, tempContentSpec1);
       int type = tempContentSpec1.type;
       if (type == XMLContentSpec.CONTENTSPECNODE_SEQ ||
           type == XMLContentSpec.CONTENTSPECNODE_ALL) {
          return maxEffectiveTotalRangeSeq(contentSpecIndex);
       }
       else if (type == XMLContentSpec.CONTENTSPECNODE_CHOICE) {
          return maxEffectiveTotalRangeChoice(contentSpecIndex); 
       }
       else {
          return(fSchemaGrammar.getContentSpecMaxOccurs(contentSpecIndex));
       }
       
    }
    
    private int maxEffectiveTotalRangeSeq(int csIndex) {

       fSchemaGrammar.getContentSpec(csIndex, tempContentSpec1);
       int type = tempContentSpec1.type;
       int left = tempContentSpec1.value;
       int right = tempContentSpec1.otherValue;
       int max = fSchemaGrammar.getContentSpecMaxOccurs(csIndex);

       if (max == SchemaSymbols.OCCURRENCE_UNBOUNDED) 
         return SchemaSymbols.OCCURRENCE_UNBOUNDED;

       int maxLeft = maxEffectiveTotalRange(left);
       if (right == -2) {
         if (maxLeft == SchemaSymbols.OCCURRENCE_UNBOUNDED) 
           return SchemaSymbols.OCCURRENCE_UNBOUNDED;
         else 
           return max * maxLeft;
       }
       else {
         int maxRight = maxEffectiveTotalRange(right);
         if (maxLeft == SchemaSymbols.OCCURRENCE_UNBOUNDED ||
            maxRight == SchemaSymbols.OCCURRENCE_UNBOUNDED) 
           return SchemaSymbols.OCCURRENCE_UNBOUNDED;
         else
           return max * (maxLeft + maxRight); 
       }
    }
          
    private int maxEffectiveTotalRangeChoice(int csIndex) {

       fSchemaGrammar.getContentSpec(csIndex, tempContentSpec1);
       int type = tempContentSpec1.type;
       int left = tempContentSpec1.value;
       int right = tempContentSpec1.otherValue;
       int max = fSchemaGrammar.getContentSpecMaxOccurs(csIndex);

       if (max == SchemaSymbols.OCCURRENCE_UNBOUNDED) 
         return SchemaSymbols.OCCURRENCE_UNBOUNDED;

       int maxLeft = maxEffectiveTotalRange(left);
       if (right == -2) {
         if (maxLeft == SchemaSymbols.OCCURRENCE_UNBOUNDED) 
           return SchemaSymbols.OCCURRENCE_UNBOUNDED;
         else 
           return max * maxLeft;
       }
       else {
         int maxRight = maxEffectiveTotalRange(right);
         if (maxLeft == SchemaSymbols.OCCURRENCE_UNBOUNDED ||
            maxRight == SchemaSymbols.OCCURRENCE_UNBOUNDED) 
           return SchemaSymbols.OCCURRENCE_UNBOUNDED;
         else
           return max * ((maxLeft > maxRight)?maxLeft:maxRight);
       }
    }


    private String resolvePrefixToURI (String prefix) throws Exception  {
        String uriStr = fStringPool.toString(fNamespacesScope.getNamespaceForPrefix(fStringPool.addSymbol(prefix)));
        if (uriStr.length() == 0 && prefix.length() > 0) {
            // REVISIT: Localize
            reportGenericSchemaError("prefix : [" + prefix +"] cannot be resolved to a URI");
            return "";
        }

        //REVISIT, !!!! a hack: needs to be updated later, cause now we only use localpart to key build-in datatype.
        if ( prefix.length()==0 && uriStr.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) 
             && fTargetNSURIString.length() == 0) {
            uriStr = "";
        }

        return uriStr;
    }

    public  TraverseSchema(Element root, StringPool stringPool, 
                           SchemaGrammar schemaGrammar, 
                           GrammarResolver grammarResolver,
                           XMLErrorReporter errorReporter,
                           String schemaURL,
                   EntityResolver entityResolver,
                           boolean fullChecking
                           ) throws Exception {
        fErrorReporter = errorReporter;
        fCurrentSchemaURL = schemaURL;
        fFullConstraintChecking = fullChecking;
    fEntityResolver = entityResolver;
        doTraverseSchema(root, stringPool, schemaGrammar, grammarResolver);
    }

    public  TraverseSchema(Element root, StringPool stringPool, 
                           SchemaGrammar schemaGrammar, 
                           GrammarResolver grammarResolver,
                           XMLErrorReporter errorReporter,
                           String schemaURL, 
                           boolean fullChecking
                           ) throws Exception {
        fErrorReporter = errorReporter;
        fCurrentSchemaURL = schemaURL;
        fFullConstraintChecking = fullChecking;
        doTraverseSchema(root, stringPool, schemaGrammar, grammarResolver);
    }

    public  TraverseSchema(Element root, StringPool stringPool, 
                           SchemaGrammar schemaGrammar, 
                           GrammarResolver grammarResolver, 
                           boolean fullChecking
                           ) throws Exception {
        fFullConstraintChecking = fullChecking;
        doTraverseSchema(root, stringPool, schemaGrammar, grammarResolver);
    }

    public  void doTraverseSchema(Element root, StringPool stringPool, 
                           SchemaGrammar schemaGrammar, 
                           GrammarResolver grammarResolver) throws Exception {

        fNamespacesScope = new NamespacesScope(this);
        
        fSchemaRootElement = root;
        fStringPool = stringPool;
        fSchemaGrammar = schemaGrammar;
        if (fFullConstraintChecking) {
          fSchemaGrammar.setDeferContentSpecExpansion();                           
          fSchemaGrammar.setCheckUniqueParticleAttribution();
        }

        fGrammarResolver = grammarResolver;
        fDatatypeRegistry = (DatatypeValidatorFactoryImpl) fGrammarResolver.getDatatypeRegistry();
        
        //Expand to registry type to contain all primitive datatype
        fDatatypeRegistry.expandRegistryToFullSchemaSet(); 

        // General Attribute Checking
        fGeneralAttrCheck = new GeneralAttrCheck(fErrorReporter);
        fXsiURI = fStringPool.addSymbol(SchemaSymbols.URI_XSI);

        if (root == null) { 
            // REVISIT: Anything to do?
            return;
        }

        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_GLOBAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(root, scope);

        //Make sure namespace binding is defaulted
        String rootPrefix = root.getPrefix();
        if( rootPrefix == null || rootPrefix.length() == 0 ){
            String xmlns = root.getAttribute("xmlns");
            if( xmlns.length() == 0 )
                root.setAttribute("xmlns", SchemaSymbols.URI_SCHEMAFORSCHEMA );
        }

        //Retrieve the targetNamespace URI information
        fTargetNSURIString = getTargetNamespaceString(root);
        fTargetNSURI = fStringPool.addSymbol(fTargetNSURIString);

        if (fGrammarResolver == null) {
            // REVISIT: Localize
            reportGenericSchemaError("Internal error: don't have a GrammarResolver for TraverseSchema");
        }
        else{
            // for complex type registry, attribute decl registry and 
            // namespace mapping, needs to check whether the passed in 
            // Grammar was a newly instantiated one.
            if (fSchemaGrammar.getComplexTypeRegistry() == null ) {
                fSchemaGrammar.setComplexTypeRegistry(fComplexTypeRegistry);
            }
            else {
                fComplexTypeRegistry = fSchemaGrammar.getComplexTypeRegistry();
            }

            if (fSchemaGrammar.getAttributeDeclRegistry() == null ) {
                fSchemaGrammar.setAttributeDeclRegistry(fAttributeDeclRegistry);
            }
            else {
                fAttributeDeclRegistry = fSchemaGrammar.getAttributeDeclRegistry();
            }

            if (fSchemaGrammar.getNamespacesScope() == null ) {
                fSchemaGrammar.setNamespacesScope(fNamespacesScope);
            }
            else {
                fNamespacesScope = fSchemaGrammar.getNamespacesScope();
            }

            fSchemaGrammar.setDatatypeRegistry(fDatatypeRegistry);
            fSchemaGrammar.setTargetNamespaceURI(fTargetNSURIString);
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

        fElementDefaultQualified = 
            root.getAttribute(SchemaSymbols.ATT_ELEMENTFORMDEFAULT).equals(SchemaSymbols.ATTVAL_QUALIFIED);
        fAttributeDefaultQualified = 
            root.getAttribute(SchemaSymbols.ATT_ATTRIBUTEFORMDEFAULT).equals(SchemaSymbols.ATTVAL_QUALIFIED);
        Attr blockAttr = root.getAttributeNode(SchemaSymbols.ATT_BLOCKDEFAULT);
        if (blockAttr == null) 
            fBlockDefault = 0;
        else
            fBlockDefault = 
                parseBlockSet(blockAttr.getValue());
        Attr finalAttr = root.getAttributeNode(SchemaSymbols.ATT_FINALDEFAULT);
        if (finalAttr == null) 
            fFinalDefault = 0;
        else
            fFinalDefault = 
                parseFinalSet(finalAttr.getValue());
        
        //REVISIT, really sticky when noTargetNamesapce, for now, we assume everyting is in the same name space);
        if (fTargetNSURI == StringPool.EMPTY_STRING) {
            //fElementDefaultQualified = true;
            //fAttributeDefaultQualified = true;
        }


        //fScopeCount++;
        fCurrentScope = -1;


        //extract all top-level attribute, attributeGroup, and group Decls and put them in the 3 hasn table in the SchemaGrammar.
        extractTopLevel3Components(root);

        // process <redefine>, <include> and <import> info items.
        Element child = XUtil.getFirstChildElement(root); 
        for (; child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getLocalName();
            if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) {
                traverseAnnotationDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_INCLUDE)) {
                fNamespacesScope.increaseDepth();
                traverseInclude(child); 
                fNamespacesScope.decreaseDepth();
            } else if (name.equals(SchemaSymbols.ELT_IMPORT)) {
                traverseImport(child); 
            } else if (name.equals(SchemaSymbols.ELT_REDEFINE)) {
                fRedefineSucceeded = true; // presume worked until proven failed.
                fNamespacesScope.increaseDepth();
                traverseRedefine(child); 
                fNamespacesScope.decreaseDepth();
            } else
                break;
        }

        // child refers to the first info item which is not <annotation> or 
        // one of the schema inclusion/importation declarations.
        for (; child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getLocalName();
            if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) {
                traverseAnnotationDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_SIMPLETYPE )) {
                traverseSimpleTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_COMPLEXTYPE )) {
                traverseComplexTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ELEMENT )) { 
                traverseElementDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                traverseAttributeGroupDecl(child, null, null);
            } else if (name.equals( SchemaSymbols.ELT_ATTRIBUTE ) ) {
                traverseAttributeDecl( child, null, false );
            } else if (name.equals(SchemaSymbols.ELT_GROUP)) {
                traverseGroupDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_NOTATION)) {
                traverseNotationDecl(child); //TO DO
            } else {
                // REVISIT: Localize
                reportGenericSchemaError("error in content of <schema> element information item");
            }
        } // for each child node

        // handle identity constraints
        // we must traverse <key>s and <unique>s before we tackel<keyref>s,
        // since all have global scope and may be declared anywhere in the schema.  
        Enumeration elementIndexes = fIdentityConstraints.keys();
        while (elementIndexes.hasMoreElements()) {
            Integer elementIndexObj = (Integer)elementIndexes.nextElement();
            if (DEBUG_IC_DATATYPES) {
                System.out.println("<ICD>: traversing identity constraints for element: "+elementIndexObj);
            }
            Vector identityConstraints = (Vector)fIdentityConstraints.get(elementIndexObj);
            if (identityConstraints != null) {
                int elementIndex = elementIndexObj.intValue();
                traverseIdentityNameConstraintsFor(elementIndex, identityConstraints);
            }
        }
        elementIndexes = fIdentityConstraints.keys();
        while (elementIndexes.hasMoreElements()) {
            Integer elementIndexObj = (Integer)elementIndexes.nextElement();
            if (DEBUG_IC_DATATYPES) {
                System.out.println("<ICD>: traversing identity constraints for element: "+elementIndexObj);
            }
            Vector identityConstraints = (Vector)fIdentityConstraints.get(elementIndexObj);
            if (identityConstraints != null) {
                int elementIndex = elementIndexObj.intValue();
                traverseIdentityRefConstraintsFor(elementIndex, identityConstraints);
            }
        }

        // General Attribute Checking
        fGeneralAttrCheck = null;

    } // traverseSchema(Element)


    private void extractTopLevel3Components(Element root) throws Exception {
        
        for (Element child = XUtil.getFirstChildElement(root); child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getLocalName();
            String compName = child.getAttribute(SchemaSymbols.ATT_NAME);
            if (name.equals(SchemaSymbols.ELT_ELEMENT)) {
                // Check if the element has already been declared
                if (fSchemaGrammar.topLevelElemDecls.get(compName) != null) {
                   reportGenericSchemaError("sch-props-correct: Duplicate declaration for an element " +
                                             compName);
                }
                else {                
                    fSchemaGrammar.topLevelElemDecls.put(compName, child);
                }
            }
            else if (name.equals(SchemaSymbols.ELT_SIMPLETYPE) ||
                     name.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                 // Check for dublicate declaration
                if (fSchemaGrammar.topLevelTypeDecls.get(compName) != null) {
                   reportGenericSchemaError("sch-props-correct: Duplicate declaration for a type " +
                                             compName);
                }
                else {                
                    fSchemaGrammar.topLevelTypeDecls.put(compName, child);
                }
            }
            else if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                 // Check for dublicate declaration
                if (fSchemaGrammar.topLevelAttrGrpDecls.get(compName) != null) {
                   reportGenericSchemaError("sch-props-correct: Duplicate declaration for an attribute group " +
                                             compName);
                }
                else {                
                fSchemaGrammar.topLevelAttrGrpDecls.put(compName, child);
                }
            } else if (name.equals( SchemaSymbols.ELT_ATTRIBUTE ) ) {
                // Check for dublicate declaration
                if (fSchemaGrammar.topLevelAttrGrpDecls.get(compName) != null) {
                   reportGenericSchemaError("sch-props-correct: Duplicate declaration for an attribute " +
                                             compName);
                }
                else {                
                    fSchemaGrammar.topLevelAttrGrpDecls.put(compName, child);
                }
            } else if ( name.equals(SchemaSymbols.ELT_GROUP) ) {
                // Check if the group has already been declared
                if (fSchemaGrammar.topLevelGroupDecls.get(compName) != null){ 
                   reportGenericSchemaError("sch-props-correct: Duplicate declaration for a group " +
                                             compName);
                }
                else {                
                fSchemaGrammar.topLevelGroupDecls.put(compName, child);
                }
            } else if ( name.equals(SchemaSymbols.ELT_NOTATION) ) {
                // Check for dublicate declaration
                if (fSchemaGrammar.topLevelNotationDecls.get(compName) != null) {
                   reportGenericSchemaError("sch-props-correct: Duplicate declaration for a notation " +
                                             compName);
                }
                else {                
                fSchemaGrammar.topLevelNotationDecls.put(compName, child);
            }
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

        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_GLOBAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(includeDecl, scope);
        checkContent(includeDecl, XUtil.getFirstChildElement(includeDecl), true);

        Attr locationAttr = includeDecl.getAttributeNode(SchemaSymbols.ATT_SCHEMALOCATION);
        if (locationAttr == null) {
            // REVISIT: Localize
            reportGenericSchemaError("a schemaLocation attribute must be specified on an <include> element");
            return;
        }
        String location = locationAttr.getValue();
        
        // expand it before passing it to the parser
        InputSource source = null;
        if (fEntityResolver != null) {
            source = fEntityResolver.resolveEntity("", location);
        }
        if (source == null) {
            location = expandSystemId(location, fCurrentSchemaURL);
            source = new InputSource(location);
        }
        else {
            // create a string for uniqueness of this included schema in fIncludeLocations
            if (source.getPublicId () != null)
                location = source.getPublicId ();

            location += (',' + source.getSystemId ());
        }

        if (fIncludeLocations.contains((Object)location)) {
            return;
        }
        fIncludeLocations.addElement((Object)location);

        DOMParser parser = new IgnoreWhitespaceParser();
        parser.setEntityResolver( new Resolver() );
        parser.setErrorHandler(  new ErrorHandler() 
            {
                public void fatalError(SAXParseException ex) throws SAXException {
                    StringBuffer str = new StringBuffer(); 
                    String systemId_ = ex.getSystemId();
                    if (systemId_ != null) {
                        int index = systemId_.lastIndexOf('/');
                        if (index != -1)
                            systemId_ = systemId_.substring(index + 1);
                        str.append(systemId_);
                    }
                    str.append(':').append(ex.getLineNumber()).append(':').append(ex.getColumnNumber());
                    String message = ex.getMessage();
                    if(message.toLowerCase().trim().endsWith("not found.")) {
                        System.err.println("[Warning] "+
                               str.toString()+": "+ message);
                    } else { // do standard thing
                        System.err.println("[Fatal Error] "+
                               str.toString()+":"+message);
                        throw ex;
                    }
                }
            });

        try {
            parser.setFeature("http://xml.org/sax/features/validation", false);
            parser.setFeature("http://xml.org/sax/features/namespaces", true);
            parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
        }catch(  org.xml.sax.SAXNotRecognizedException e ) {
            e.printStackTrace();
        }catch( org.xml.sax.SAXNotSupportedException e ) {
            e.printStackTrace();
        }

        try {
            parser.parse( source );
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
            String targetNSURI = getTargetNamespaceString(root);
            if (targetNSURI.length() > 0 && !targetNSURI.equals(fTargetNSURIString) ) {
                // REVISIT: Localize
                reportGenericSchemaError("included schema '"+location+"' has a different targetNameSpace '"
                                         +targetNSURI+"'");
            }
            else {
                // We not creating another TraverseSchema object to compile
                // the included schema file, because the scope count, anon-type count
                // should not be reset for a included schema, this can be fixed by saving 
                // the counters in the Schema Grammar, 
                if (fSchemaInfoListRoot == null) {
                    fSchemaInfoListRoot = new SchemaInfo(fElementDefaultQualified, fAttributeDefaultQualified, 
                        fBlockDefault, fFinalDefault,
                        fCurrentScope, fCurrentSchemaURL, fSchemaRootElement, null, null);
                    fCurrentSchemaInfo = fSchemaInfoListRoot;
                }
                fSchemaRootElement = root;
                fCurrentSchemaURL = location;
                traverseIncludedSchemaHeader(root);
                // and now we'd better save this stuff!  
                fCurrentSchemaInfo = new SchemaInfo(fElementDefaultQualified, fAttributeDefaultQualified, 
                        fBlockDefault, fFinalDefault, 
                        fCurrentScope, fCurrentSchemaURL, fSchemaRootElement, fCurrentSchemaInfo.getNext(), fCurrentSchemaInfo);
                (fCurrentSchemaInfo.getPrev()).setNext(fCurrentSchemaInfo);
                traverseIncludedSchema(root);
                // there must always be a previous element!
                fCurrentSchemaInfo = fCurrentSchemaInfo.getPrev();
                fCurrentSchemaInfo.restore();
            }

        }

    }

    private void traverseIncludedSchemaHeader(Element root) throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_GLOBAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(root, scope);

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

        fElementDefaultQualified = 
            root.getAttribute(SchemaSymbols.ATT_ELEMENTFORMDEFAULT).equals(SchemaSymbols.ATTVAL_QUALIFIED);
        fAttributeDefaultQualified = 
            root.getAttribute(SchemaSymbols.ATT_ATTRIBUTEFORMDEFAULT).equals(SchemaSymbols.ATTVAL_QUALIFIED);
        Attr blockAttr = root.getAttributeNode(SchemaSymbols.ATT_BLOCKDEFAULT);
        if (blockAttr == null) 
            fBlockDefault = 0;
        else
            fBlockDefault = 
                parseBlockSet(blockAttr.getValue());
        Attr finalAttr = root.getAttributeNode(SchemaSymbols.ATT_FINALDEFAULT);
        if (finalAttr == null) 
            fFinalDefault = 0;
        else
            fFinalDefault = 
                parseFinalSet(finalAttr.getValue());
        
        //REVISIT, really sticky when noTargetNamesapce, for now, we assume everyting is in the same name space);
        if (fTargetNSURI == StringPool.EMPTY_STRING) {
            fElementDefaultQualified = true;
            //fAttributeDefaultQualified = true;
        }

        //fScopeCount++;
        fCurrentScope = -1;
    } // traverseIncludedSchemaHeader 

    private void traverseIncludedSchema(Element root) throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_GLOBAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(root, scope);

        //extract all top-level attribute, attributeGroup, and group Decls and put them in the 3 hasn table in the SchemaGrammar.
        extractTopLevel3Components(root);

        // handle <redefine>, <include> and <import> elements.
        Element child = XUtil.getFirstChildElement(root); 
        for (; child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getLocalName();

            if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) {
                traverseAnnotationDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_INCLUDE)) {
                fNamespacesScope.increaseDepth();
                traverseInclude(child); 
                fNamespacesScope.decreaseDepth();
            } else if (name.equals(SchemaSymbols.ELT_IMPORT)) {
                traverseImport(child); 
            } else if (name.equals(SchemaSymbols.ELT_REDEFINE)) {
                fRedefineSucceeded = true; // presume worked until proven failed.
                fNamespacesScope.increaseDepth();
                traverseRedefine(child); 
                fNamespacesScope.decreaseDepth();
            } else
                break;
        }

        // handle the rest of the schema elements.
        for (; child != null;
            child = XUtil.getNextSiblingElement(child)) {

            String name = child.getLocalName();

            if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) {
                traverseAnnotationDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_SIMPLETYPE )) {
                traverseSimpleTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_COMPLEXTYPE )) {
                traverseComplexTypeDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ELEMENT )) { 
                traverseElementDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                if(fRedefineAttributeGroupMap != null) {
                    String dName = child.getAttribute(SchemaSymbols.ATT_NAME);
                    String bName = (String)fRedefineAttributeGroupMap.get(dName);
                    if(bName != null) {
                        child.setAttribute(SchemaSymbols.ATT_NAME, bName);
                        // Now we reuse this location in the array to store info we'll need for validation...  
                        ComplexTypeInfo typeInfo = new ComplexTypeInfo();
                        int templateElementNameIndex = fStringPool.addSymbol("$"+bName);
                        int typeNameIndex = fStringPool.addSymbol("%"+bName);
                        typeInfo.scopeDefined = -2;
                        typeInfo.contentSpecHandle = -1;
                        typeInfo.contentType = XMLElementDecl.TYPE_SIMPLE;
                        typeInfo.datatypeValidator = null;
                        typeInfo.templateElementIndex = fSchemaGrammar.addElementDecl(
                            new QName(-1, templateElementNameIndex,typeNameIndex,fTargetNSURI),
                            (fTargetNSURI==StringPool.EMPTY_STRING) ? StringPool.EMPTY_STRING : -2, typeInfo.scopeDefined,
                            typeInfo.contentType, 
                            typeInfo.contentSpecHandle, -1, typeInfo.datatypeValidator);

                        Vector anyAttDecls = new Vector();
                        // need to determine how to initialize these babies; then
                        // on the <redefine> traversing end, try
                        // and cast the hash value into the right form;
                        // failure indicates nothing to redefine; success
                        // means we can feed checkAttribute... what it needs...
                        traverseAttributeGroupDecl(child, typeInfo, anyAttDecls);
                        typeInfo.attlistHead = fSchemaGrammar.getFirstAttributeDeclIndex(
                                typeInfo.templateElementIndex);
                        fRedefineAttributeGroupMap.put(dName, new Object []{typeInfo, fSchemaGrammar, anyAttDecls});
                        continue;
                    }
                }
                traverseAttributeGroupDecl(child, null, null);
            } else if (name.equals( SchemaSymbols.ELT_ATTRIBUTE ) ) {
                traverseAttributeDecl( child, null , false);
            } else if (name.equals(SchemaSymbols.ELT_GROUP)) {
                String dName = child.getAttribute(SchemaSymbols.ATT_NAME);
                if(fGroupNameRegistry.get(fTargetNSURIString + ","+dName) == null) {
                    // we've been renamed already
                    traverseGroupDecl(child);
                    continue;
                }
                // if we're here: must have been a restriction.
                // we have yet to be renamed.
                try {
                    Integer i = (Integer)fGroupNameRegistry.get(fTargetNSURIString + ","+dName);
                } catch (ClassCastException c) {
                    String s = (String)fGroupNameRegistry.get(fTargetNSURIString + ","+dName);
                    if (s == null) continue; // must have seen this already--somehow...
                };
                String bName = (String)fGroupNameRegistry.get(fTargetNSURIString +"," + dName);
                if(bName != null) {
                    child.setAttribute(SchemaSymbols.ATT_NAME, bName);
                    // Now we reuse this location in the array to store info we'll need for validation...  
                    // note that traverseGroupDecl will happily do that for us!
                }
                traverseGroupDecl(child);
            } else if (name.equals(SchemaSymbols.ELT_NOTATION)) {
                traverseNotationDecl(child); 
            } else {
                // REVISIT: Localize
                reportGenericSchemaError("error in content of included <schema> element information item");
            }
        } // for each child node

    }

    // This method's job is to open a redefined schema and store away its root element, defaultElementQualified and other
    // such info, in order that it can be available when redefinition actually takes place.  
    // It assumes that it will be called from the schema doing the redefining, and it assumes
    // that the other schema's info has already been saved, putting the info it finds into the
    // SchemaInfoList element that is passed in.  
    private void openRedefinedSchema(Element redefineDecl, SchemaInfo store) throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_GLOBAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(redefineDecl, scope);

        Attr locationAttr = redefineDecl.getAttributeNode(SchemaSymbols.ATT_SCHEMALOCATION);
        if (locationAttr == null) {
            // REVISIT: Localize
            fRedefineSucceeded = false;
            reportGenericSchemaError("a schemaLocation attribute must be specified on a <redefine> element");
            return;
        }
        String location = locationAttr.getValue();
        
        // expand it before passing it to the parser
        InputSource source = null;
        if (fEntityResolver != null) {
            source = fEntityResolver.resolveEntity("", location);
        }

        if (source == null) {
            location = expandSystemId(location, fCurrentSchemaURL);
            source = new InputSource(location);
        }
        else {
            // Make sure we don't redefine the same schema twice; it's allowed 
            // but the specs encourage us to avoid it.  
            if (source.getPublicId () != null)
                location = source.getPublicId ();

            // make sure we're not redefining ourselves!
            if(source.getSystemId().equals(fCurrentSchemaURL)) {
                // REVISIT:  localize
                reportGenericSchemaError("src-redefine.2:  a schema cannot redefine itself");
                fRedefineSucceeded = false;
                return;
            }
            location += (',' + source.getSystemId ());
        }
        if (fRedefineLocations.get((Object)location) != null) {
            // then we'd better make sure we're directed at that schema...
            fCurrentSchemaInfo = (SchemaInfo)(fRedefineLocations.get((Object)location));
            fCurrentSchemaInfo.restore();
            return;
        }

        DOMParser parser = new IgnoreWhitespaceParser();
        parser.setEntityResolver( new Resolver() );
        parser.setErrorHandler(  new ErrorHandler() );

        try {
            parser.setFeature("http://xml.org/sax/features/validation", false);
            parser.setFeature("http://xml.org/sax/features/namespaces", true);
            parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
        }catch(  org.xml.sax.SAXNotRecognizedException e ) {
            e.printStackTrace();
        }catch( org.xml.sax.SAXNotSupportedException e ) {
            e.printStackTrace();
        }

        try {
            parser.parse( source );
        }catch( IOException e ) {
            e.printStackTrace();
        }catch( SAXException e ) {
            //e.printStackTrace();
        }

        Document     document   = parser.getDocument(); //Our Grammar to be redefined
        Element root = null;
        if (document != null) {
            root = document.getDocumentElement();
        }

        if (root == null) { // nothing to be redefined, so just continue; specs disallow an error here. 
            fRedefineSucceeded = false;
            return; 
        }

        // now if root isn't null, it'll contain the root of the schema we need to redefine.  
        // We do this in two phases:  first, we look through the children of
        // redefineDecl.  Each one will correspond to an element of the
        // redefined schema that we need to redefine.  To do this, we rename the
        // element of the redefined schema, and rework the base or ref tag of
        // the kid we're working on to refer to the renamed group or derive the
        // renamed type.  Once we've done this, we actually go through the
        // schema being redefined and convert it to a grammar.  Only then do we
        // run through redefineDecl's kids and put them in the grammar.  
        //
        // This approach is kosher with the specs.  It does raise interesting
        // questions about error reporting, and perhaps also about grammar
        // access, but it is comparatively efficient (we need make at most
        // only 2 traversals of any given information item) and moreover 
        // we can use existing code to build the grammar structures once the
        // first pass is out of the way, so this should be quite robust.  

        // check to see if the targetNameSpace is right
        String redefinedTargetNSURIString = getTargetNamespaceString(root);
        if (redefinedTargetNSURIString.length() > 0 && !redefinedTargetNSURIString.equals(fTargetNSURIString) ) {
            // REVISIT: Localize
            fRedefineSucceeded = false;
            reportGenericSchemaError("redefined schema '"+location+"' has a different targetNameSpace '"
                                     +redefinedTargetNSURIString+"' from the original schema");
        }
        else {
            // targetNamespace is right, so let's do the renaming...
            // and let's keep in mind that the targetNamespace of the redefined
            // elements is that of the redefined schema!  
            fSchemaRootElement = root;
            fCurrentSchemaURL = location;
            // get default form xmlns bindings et al. 
            traverseIncludedSchemaHeader(root);
            // and then save them...
            store.setNext(new SchemaInfo(fElementDefaultQualified, fAttributeDefaultQualified, 
                    fBlockDefault, fFinalDefault, 
                    fCurrentScope, fCurrentSchemaURL, fSchemaRootElement, null, store));
            (store.getNext()).setPrev(store);
            fCurrentSchemaInfo = store.getNext();
            fRedefineLocations.put((Object)location, store.getNext());
        } // end if
    } // end openRedefinedSchema

    /****
     * <redefine
       *        schemaLocation = uriReference 
       *        {any attributes with non-schema namespace . . .}>
       *        Content: (annotation | (
     *            attributeGroup | complexType | group | simpleType))* 
     *    </redefine> 
     */
    private void traverseRedefine(Element redefineDecl) throws Exception {

        // initialize storage areas...
        fRedefineAttributeGroupMap = new Hashtable();

        // only case in which need to save contents is when fSchemaInfoListRoot is null; otherwise we'll have
        // done this already one way or another.  
        if (fSchemaInfoListRoot == null) {
            fSchemaInfoListRoot = new SchemaInfo(fElementDefaultQualified, fAttributeDefaultQualified, 
                    fBlockDefault, fFinalDefault, 
                    fCurrentScope, fCurrentSchemaURL, fSchemaRootElement, null, null);
            openRedefinedSchema(redefineDecl, fSchemaInfoListRoot);
            if(!fRedefineSucceeded)
                return;
            fCurrentSchemaInfo = fSchemaInfoListRoot.getNext();
		    renameRedefinedComponents(redefineDecl,fSchemaInfoListRoot.getNext().getRoot(), fSchemaInfoListRoot.getNext());
        } else {
            // may have a chain here; need to be wary!  
            SchemaInfo curr = fSchemaInfoListRoot;
            for(; curr.getNext() != null; curr = curr.getNext());
            fCurrentSchemaInfo = curr;
            fCurrentSchemaInfo.restore();
            openRedefinedSchema(redefineDecl, fCurrentSchemaInfo);
            if(!fRedefineSucceeded)
                return;
		    renameRedefinedComponents(redefineDecl,fCurrentSchemaInfo.getRoot(), fCurrentSchemaInfo);
        }
        // Now we have to march through our nicely-renamed schemas from the 
        // bottom up.  When we do these traversals other <redefine>'s may
        // perhaps be encountered; we leave recursion to sort this out.  

        traverseIncludedSchema(fSchemaRootElement);
        // and last but not least:  traverse our own <redefine>--the one all
        // this labour has been expended upon.  
        for (Element child = XUtil.getFirstChildElement(redefineDecl); child != null;
           		child = XUtil.getNextSiblingElement(child)) { 
           	String name = child.getLocalName();

			// annotations can occur anywhere in <redefine>s!
           	if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) {
               	traverseAnnotationDecl(child);
           	} else if (name.equals(SchemaSymbols.ELT_SIMPLETYPE )) {
               	traverseSimpleTypeDecl(child);
           	} else if (name.equals(SchemaSymbols.ELT_COMPLEXTYPE )) {
               	traverseComplexTypeDecl(child);
           	} else if (name.equals(SchemaSymbols.ELT_GROUP)) {
                String dName = child.getAttribute(SchemaSymbols.ATT_NAME);
                if(fGroupNameRegistry.get(fTargetNSURIString +","+ dName) == null || 
                        ((fRestrictedRedefinedGroupRegistry.get(fTargetNSURIString+","+dName) != null) &&
                        !((Boolean)fRestrictedRedefinedGroupRegistry.get(fTargetNSURIString+","+dName)).booleanValue())) { // extension!
               	    traverseGroupDecl(child);
                    continue;
                } 
               	traverseGroupDecl(child);
                Integer bCSIndexObj = null;
                try {
                    bCSIndexObj = (Integer)fGroupNameRegistry.get(fTargetNSURIString +","+ dName+redefIdentifier);
                } catch(ClassCastException c) {
                    // if it's still a String, then we mustn't have found a corresponding attributeGroup in the redefined schema.
                    // REVISIT:  localize
                    reportGenericSchemaError("src-redefine.6.2:  a <group> within a <redefine> must either have a ref to a <group> with the same name or must restrict such an <group>");
                    continue;
                }
                if(bCSIndexObj != null) { // we have something!
                    int bCSIndex = bCSIndexObj.intValue();
                    Integer dCSIndexObj;
                    try {
                        dCSIndexObj = (Integer)fGroupNameRegistry.get(fTargetNSURIString+","+dName);
                    } catch (ClassCastException c) {
                        continue;
                    }
                    if(dCSIndexObj == null) // something went wrong...
                        continue;
                    int dCSIndex = dCSIndexObj.intValue();
                    try {
                      checkParticleDerivationOK(dCSIndex, -1, bCSIndex, -1, null);
                    }
                    catch (ParticleRecoverableError e) {
                      reportGenericSchemaError(e.getMessage());
                    }
                } else
                    // REVISIT:  localize
                    reportGenericSchemaError("src-redefine.6.2:  a <group> within a <redefine> must either have a ref to a <group> with the same name or must restrict such an <group>");
           	} else if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                if(fRedefineAttributeGroupMap != null) {
                    String dName = child.getAttribute(SchemaSymbols.ATT_NAME);
                    Object [] bAttGrpStore = null;
                    try {
                        bAttGrpStore = (Object [])fRedefineAttributeGroupMap.get(dName);
                    } catch(ClassCastException c) {
                        // if it's still a String, then we mustn't have found a corresponding attributeGroup in the redefined schema.
                        // REVISIT:  localize
                        reportGenericSchemaError("src-redefine.7.2:  an <attributeGroup> within a <redefine> must either have a ref to an <attributeGroup> with the same name or must restrict such an <attributeGroup>");
                        continue;
                    }
                    if(bAttGrpStore != null) { // we have something!
                        ComplexTypeInfo bTypeInfo = (ComplexTypeInfo)bAttGrpStore[0];
                        SchemaGrammar bSchemaGrammar = (SchemaGrammar)bAttGrpStore[1];
                        Vector bAnyAttDecls = (Vector)bAttGrpStore[2];
                        XMLAttributeDecl bAnyAttDecl =  
                            (bAnyAttDecls.size()>0 )? (XMLAttributeDecl)bAnyAttDecls.elementAt(0):null;
                        ComplexTypeInfo dTypeInfo = new ComplexTypeInfo();
                        int templateElementNameIndex = fStringPool.addSymbol("$"+dName);
                        int dTypeNameIndex = fStringPool.addSymbol("%"+dName);
                        dTypeInfo.scopeDefined = -2;
                        dTypeInfo.contentSpecHandle = -1;
                        dTypeInfo.contentType = XMLElementDecl.TYPE_SIMPLE;
                        dTypeInfo.datatypeValidator = null;
                        dTypeInfo.templateElementIndex = fSchemaGrammar.addElementDecl(
                            new QName(-1, templateElementNameIndex,dTypeNameIndex,fTargetNSURI),
                            (fTargetNSURI==StringPool.EMPTY_STRING) ? StringPool.EMPTY_STRING : -2, dTypeInfo.scopeDefined,
                            dTypeInfo.contentType, 
                            dTypeInfo.contentSpecHandle, -1, dTypeInfo.datatypeValidator);

                        Vector dAnyAttDecls = new Vector();
                        XMLAttributeDecl dAnyAttDecl =  
                            (dAnyAttDecls.size()>0 )? (XMLAttributeDecl)dAnyAttDecls.elementAt(0):null;
                        traverseAttributeGroupDecl(child, dTypeInfo, dAnyAttDecls);
                        dTypeInfo.attlistHead = fSchemaGrammar.getFirstAttributeDeclIndex(
                                dTypeInfo.templateElementIndex);
                        try {
                            checkAttributesDerivationOKRestriction(dTypeInfo.attlistHead,fSchemaGrammar,
                                dAnyAttDecl,bTypeInfo.attlistHead,bSchemaGrammar,bAnyAttDecl); 
                        }
                        catch (ComplexTypeRecoverableError e) {
                            String message = e.getMessage();
                            reportGenericSchemaError("src-redefine.7.2:  redefinition failed because of " + message);
                        }
                        continue;
                    }
                }
               	traverseAttributeGroupDecl(child, null, null);
			} // no else; error reported in the previous traversal
       	} //for

        // and restore the original globals
        fCurrentSchemaInfo = fCurrentSchemaInfo.getPrev();
        fCurrentSchemaInfo.restore();
    } // traverseRedefine

	// the purpose of this method is twofold:  1.  To find and appropriately modify all information items
	// in redefinedSchema with names that are redefined by children of
	// redefineDecl.  2.  To make sure the redefine element represented by
	// redefineDecl is valid as far as content goes and with regard to
	// properly referencing components to be redefined.  No traversing is done here!
    // This method also takes actions to find and, if necessary, modify the names
    // of elements in <redefine>'s in the schema that's being redefined.  
	private void renameRedefinedComponents(Element redefineDecl, Element schemaToRedefine, SchemaInfo currSchemaInfo) throws Exception {
		for (Element child = XUtil.getFirstChildElement(redefineDecl);
				child != null;
				child = XUtil.getNextSiblingElement(child)) {
            String name = child.getLocalName();
            if (name.equals(SchemaSymbols.ELT_ANNOTATION) ) 
                continue;
            else if (name.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
            	String typeName = child.getAttribute( SchemaSymbols.ATT_NAME );
                if(fTraversedRedefineElements.contains(typeName))
                    continue;
                if(validateRedefineNameChange(SchemaSymbols.ELT_SIMPLETYPE, typeName, typeName+redefIdentifier, child)) {
					fixRedefinedSchema(SchemaSymbols.ELT_SIMPLETYPE, 
						typeName, typeName+redefIdentifier, 
						schemaToRedefine, currSchemaInfo);
				}
			} else if (name.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
            	String typeName = child.getAttribute( SchemaSymbols.ATT_NAME );
                if(fTraversedRedefineElements.contains(typeName))
                    continue;
                if(validateRedefineNameChange(SchemaSymbols.ELT_COMPLEXTYPE, typeName, typeName+redefIdentifier, child)) {
				    fixRedefinedSchema(SchemaSymbols.ELT_COMPLEXTYPE, 
					    typeName, typeName+redefIdentifier, 
					    schemaToRedefine, currSchemaInfo);
				}
            } else if (name.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
				String baseName = child.getAttribute( SchemaSymbols.ATT_NAME );
                if(fTraversedRedefineElements.contains(baseName))
                    continue;
                if(validateRedefineNameChange(SchemaSymbols.ELT_ATTRIBUTEGROUP, baseName, baseName+redefIdentifier, child)) {
					fixRedefinedSchema(SchemaSymbols.ELT_ATTRIBUTEGROUP, 
						baseName, baseName+redefIdentifier, 
						schemaToRedefine, currSchemaInfo);
                }
            } else if (name.equals(SchemaSymbols.ELT_GROUP)) {
				String baseName = child.getAttribute( SchemaSymbols.ATT_NAME );
                if(fTraversedRedefineElements.contains(baseName))
                    continue;
                if(validateRedefineNameChange(SchemaSymbols.ELT_GROUP, baseName, baseName+redefIdentifier, child)) {
					fixRedefinedSchema(SchemaSymbols.ELT_GROUP, 
						baseName, baseName+redefIdentifier, 
						schemaToRedefine, currSchemaInfo);
				} 
			} else {
                fRedefineSucceeded = false;
            	// REVISIT: Localize
            	reportGenericSchemaError("invalid top-level content for <redefine>");
				return;
			} 
		} // for 
	} // renameRedefinedComponents

	// This function looks among the children of curr for an element of type elementSought.  
	// If it finds one, it evaluates whether its ref attribute contains a reference
	// to originalName.  If it does, it returns 1 + the value returned by
	// calls to itself on all other children.  In all other cases it returns 0 plus 
	// the sum of the values returned by calls to itself on curr's children.
	// It also resets the value of ref so that it will refer to the renamed type from the schema
	// being redefined.
	private int changeRedefineGroup(QName originalName, String elementSought, String newName, Element curr) throws Exception {
		int result = 0;
		for (Element child = XUtil.getFirstChildElement(curr);
				child != null; child = XUtil.getNextSiblingElement(child)) {
            String name = child.getLocalName();
            if (!name.equals(elementSought)) 
				result += changeRedefineGroup(originalName, elementSought, newName, child);
			else {
				String ref = child.getAttribute( SchemaSymbols.ATT_REF );
				if (!ref.equals("")) {
            		String prefix = "";
            		String localpart = ref;
            		int colonptr = ref.indexOf(":");
            		if ( colonptr > 0) {
                		prefix = ref.substring(0,colonptr);
                		localpart = ref.substring(colonptr+1);
            		}
            		String uriStr = resolvePrefixToURI(prefix);
					if(originalName.equals(new QName(-1, fStringPool.addSymbol(localpart), fStringPool.addSymbol(localpart), fStringPool.addSymbol(uriStr)))) {
                        if(prefix.equals(""))
						    child.setAttribute(SchemaSymbols.ATT_REF, newName);
                        else 
						    child.setAttribute(SchemaSymbols.ATT_REF, prefix + ":" + newName);
						result++;
                        if(elementSought.equals(SchemaSymbols.ELT_GROUP)) {
				            String minOccurs = child.getAttribute( SchemaSymbols.ATT_MINOCCURS );
				            String maxOccurs = child.getAttribute( SchemaSymbols.ATT_MAXOCCURS );
                            if(!((maxOccurs.length() == 0 || maxOccurs.equals("1")) 
                                    && (minOccurs.length() == 0 || minOccurs.equals("1")))) {
                                //REVISIT:  localize
                                reportGenericSchemaError("src-redefine.6.1.2:  the group " + ref + " which contains a reference to a group being redefined must have minOccurs = maxOccurs = 1");
                            } 
                        }
					}
				} // if ref was null some other stage of processing will flag the error 
			}
		}
		return result;
	} // changeRedefineGroup

	// This simple function looks for the first occurrence of an eltLocalname
	// schema information item and appropriately changes the value of
	// its name or type attribute from oldName to newName.  
	// Root contains the root of the schema being operated upon.  
    // If it turns out that what we're looking for is in a <redefine> though, then we
    // just rename it--and it's reference--to be the same and wait until
    // renameRedefineDecls can get its hands on it and do it properly.  
	private void fixRedefinedSchema(String eltLocalname, String oldName, String newName, Element schemaToRedefine,
                SchemaInfo currSchema) throws Exception {

		boolean foundIt = false;
		for (Element child = XUtil.getFirstChildElement(schemaToRedefine);
				child != null;
				child = XUtil.getNextSiblingElement(child)) {
            String name = child.getLocalName();
            if(name.equals(SchemaSymbols.ELT_REDEFINE)) { // need to search the redefine decl...
		        for (Element redefChild = XUtil.getFirstChildElement(child);
				        redefChild != null;
				        redefChild = XUtil.getNextSiblingElement(redefChild)) {
                    String redefName = redefChild.getLocalName();
                    if (redefName.equals(eltLocalname) ) {
            	        String infoItemName = redefChild.getAttribute( SchemaSymbols.ATT_NAME );
				        if(!infoItemName.equals(oldName)) 
					        continue;
				        else { // found it!
					        foundIt = true;
                            openRedefinedSchema(child, currSchema);
                            if(!fRedefineSucceeded)
                                return;
                            if (validateRedefineNameChange(eltLocalname, oldName, newName+redefIdentifier, redefChild) &&
                                    (currSchema.getNext() != null))
	                            fixRedefinedSchema(eltLocalname, oldName, newName+redefIdentifier, fSchemaRootElement, currSchema.getNext());
            		        redefChild.setAttribute( SchemaSymbols.ATT_NAME, newName );
                            // and we now know we will traverse this, so set fTraversedRedefineElements appropriately...
                            fTraversedRedefineElements.addElement(newName);
                            currSchema.restore();
                            fCurrentSchemaInfo = currSchema;
                            break;
				        }
			        }
		        } //for 
                if (foundIt) break;
            }
            else if (name.equals(eltLocalname) ) {
            	String infoItemName = child.getAttribute( SchemaSymbols.ATT_NAME );
				if(!infoItemName.equals(oldName)) 
					continue;
				else { // found it!
					foundIt = true;
            		child.setAttribute( SchemaSymbols.ATT_NAME, newName );
                    break;
				}
			}
		} //for
		if(!foundIt) {
            fRedefineSucceeded = false;
            // REVISIT: localize
            reportGenericSchemaError("could not find a declaration in the schema to be redefined corresponding to " + oldName);
        }
	} // end fixRedefinedSchema

    // this method returns true if the redefine component is valid, and if
    // it was possible to revise it correctly.  The definition of
    // correctly will depend on whether renameRedefineDecls
    // or fixRedefineSchema is the caller.
    // this method also prepends a prefix onto newName if necessary; newName will never contain one. 
    private boolean validateRedefineNameChange(String eltLocalname, String oldName, String newName, Element child) throws Exception {
        if (eltLocalname.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
			QName processedTypeName = new QName(-1, fStringPool.addSymbol(oldName), fStringPool.addSymbol(oldName), fTargetNSURI);
			Element grandKid = XUtil.getFirstChildElement(child);
			if (grandKid == null) {
                fRedefineSucceeded = false;
            	// REVISIT: Localize
            	reportGenericSchemaError("a simpleType child of a <redefine> must have a restriction element as a child");
            } else {
                String grandKidName = grandKid.getLocalName();
				if(grandKidName.equals(SchemaSymbols.ELT_ANNOTATION)) {
				    grandKid = XUtil.getNextSiblingElement(grandKid);
               	    grandKidName = grandKid.getLocalName();
                }
			    if (grandKid == null) {
                    fRedefineSucceeded = false;
            	    // REVISIT: Localize
            	    reportGenericSchemaError("a simpleType child of a <redefine> must have a restriction element as a child");
                } else if(!grandKidName.equals(SchemaSymbols.ELT_RESTRICTION)) {
                    fRedefineSucceeded = false;
            		// REVISIT: Localize
            		reportGenericSchemaError("a simpleType child of a <redefine> must have a restriction element as a child");
                } else {
            		String derivedBase = grandKid.getAttribute( SchemaSymbols.ATT_BASE );
					QName processedDerivedBase = parseBase(derivedBase);
					if(!processedTypeName.equals(processedDerivedBase)) {
                        fRedefineSucceeded = false;
            			// REVISIT: Localize
            			reportGenericSchemaError("the base attribute of the restriction child of a simpleType child of a redefine must have the same value as the simpleType's type attribute");
                    } else {
						// now we have to do the renaming...
                        String prefix = "";
                        int colonptr = derivedBase.indexOf(":");
                        if ( colonptr > 0) 
                            prefix = derivedBase.substring(0,colonptr) + ":";
            			grandKid.setAttribute( SchemaSymbols.ATT_BASE, prefix + newName );
                        return true;
					}
				}
			}
		} else if (eltLocalname.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
			QName processedTypeName = new QName(-1, fStringPool.addSymbol(oldName), fStringPool.addSymbol(oldName), fTargetNSURI);
			Element grandKid = XUtil.getFirstChildElement(child);
			if (grandKid == null) {
                fRedefineSucceeded = false;
           		// REVISIT: Localize
           		reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
            } else {
                if(grandKid.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) {
		            grandKid = XUtil.getNextSiblingElement(grandKid);
                }
		        if (grandKid == null) {
                    fRedefineSucceeded = false;
            	    // REVISIT: Localize
            	    reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
                } else {
				    // have to go one more level down; let another pass worry whether complexType is valid.
				    Element greatGrandKid = XUtil.getFirstChildElement(grandKid);
				    if (greatGrandKid == null) {
                        fRedefineSucceeded = false;
            		    // REVISIT: Localize
            		    reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
                    } else {
            		    String greatGrandKidName = greatGrandKid.getLocalName();
				        if(greatGrandKidName.equals(SchemaSymbols.ELT_ANNOTATION)) {
			                greatGrandKid = XUtil.getNextSiblingElement(greatGrandKid);
                            greatGrandKidName = greatGrandKid.getLocalName();
                        }
			            if (greatGrandKid == null) {
                            fRedefineSucceeded = false;
                            // REVISIT: Localize
            	            reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
					    } else if(!greatGrandKidName.equals(SchemaSymbols.ELT_RESTRICTION) && 
							    !greatGrandKidName.equals(SchemaSymbols.ELT_EXTENSION)) {
                            fRedefineSucceeded = false;
            			    // REVISIT: Localize
            			    reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
					    } else {
            			    String derivedBase = greatGrandKid.getAttribute( SchemaSymbols.ATT_BASE );
						    QName processedDerivedBase = parseBase(derivedBase);
						    if(!processedTypeName.equals(processedDerivedBase)) {
                                fRedefineSucceeded = false;
            				    // REVISIT: Localize
            				    reportGenericSchemaError("the base attribute of the restriction or extension grandchild of a complexType child of a redefine must have the same value as the complexType's type attribute");
						    } else {
							    // now we have to do the renaming...
                                String prefix = "";
                                int colonptr = derivedBase.indexOf(":");
                                if ( colonptr > 0) 
                                    prefix = derivedBase.substring(0,colonptr) + ":";
            				    greatGrandKid.setAttribute( SchemaSymbols.ATT_BASE, prefix + newName );
                                return true;
						    }
                        }
					}
				}
			}
        } else if (eltLocalname.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
			QName processedBaseName = new QName(-1, fStringPool.addSymbol(oldName), fStringPool.addSymbol(oldName), fTargetNSURI);
			int attGroupRefsCount = changeRedefineGroup(processedBaseName, eltLocalname, newName, child);
			if(attGroupRefsCount > 1) {
                fRedefineSucceeded = false;
				// REVISIT:  localize
				reportGenericSchemaError("if an attributeGroup child of a <redefine> element contains an attributeGroup ref'ing itself, it must have exactly 1; this one has " + attGroupRefsCount);
			} else if (attGroupRefsCount == 1) {
                return true;
			}  else
                fRedefineAttributeGroupMap.put(oldName, newName);
        } else if (eltLocalname.equals(SchemaSymbols.ELT_GROUP)) {
			QName processedBaseName = new QName(-1, fStringPool.addSymbol(oldName), fStringPool.addSymbol(oldName), fTargetNSURI);
			int groupRefsCount = changeRedefineGroup(processedBaseName, eltLocalname, newName, child);
            if(!fRedefineSucceeded) {
                fRestrictedRedefinedGroupRegistry.put(fTargetNSURIString+","+oldName, new Boolean(false)); 
            }
			if(groupRefsCount > 1) {
                fRedefineSucceeded = false;
                fRestrictedRedefinedGroupRegistry.put(fTargetNSURIString+","+oldName, new Boolean(false)); 
				// REVISIT:  localize
				reportGenericSchemaError("if a group child of a <redefine> element contains a group ref'ing itself, it must have exactly 1; this one has " + groupRefsCount);
			} else if (groupRefsCount == 1) {
                fRestrictedRedefinedGroupRegistry.put(fTargetNSURIString+","+oldName, new Boolean(false)); 
                return true;
			}  else {
                fGroupNameRegistry.put(fTargetNSURIString + "," + oldName, newName);
                fRestrictedRedefinedGroupRegistry.put(fTargetNSURIString+","+oldName, new Boolean(true)); 
            }
		} else {
            fRedefineSucceeded = false;
           	// REVISIT: Localize
           	reportGenericSchemaError("internal Xerces error; please submit a bug with schema as testcase");
		} 
        // if we get here then we must have reported an error and failed somewhere...
        return false;
    } // validateRedefineNameChange

    private void traverseImport(Element importDecl)  throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_GLOBAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(importDecl, scope);
        checkContent(importDecl, XUtil.getFirstChildElement(importDecl), true);

        String location = importDecl.getAttribute(SchemaSymbols.ATT_SCHEMALOCATION);
        // expand it before passing it to the parser
        InputSource source = null;
        if (fEntityResolver != null) {
            source = fEntityResolver.resolveEntity("", location);
        }
        if (source == null) {
            location = expandSystemId(location, fCurrentSchemaURL);
            source = new InputSource(location);
        }
         else {
             // create a string for uniqueness of this imported schema in fImportLocations
             if (source.getPublicId () != null)
                 location = source.getPublicId ();

             location += (',' + source.getSystemId ());
         }

         if (fImportLocations.contains((Object)location)) {
             return;
         }
         fImportLocations.addElement((Object)location);

         String namespaceString = importDecl.getAttribute(SchemaSymbols.ATT_NAMESPACE);
         SchemaGrammar importedGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(namespaceString);

         if (importedGrammar == null) {
             importedGrammar = new SchemaGrammar();
         }

         DOMParser parser = new IgnoreWhitespaceParser();
         parser.setEntityResolver( new Resolver() );
         parser.setErrorHandler(  new ErrorHandler() 
            {
                public void fatalError(SAXParseException ex) throws SAXException {
                    StringBuffer str = new StringBuffer(); 
                    String systemId_ = ex.getSystemId();
                    if (systemId_ != null) {
                        int index = systemId_.lastIndexOf('/');
                        if (index != -1)
                            systemId_ = systemId_.substring(index + 1);
                        str.append(systemId_);
                    }
                    str.append(':').append(ex.getLineNumber()).append(':').append(ex.getColumnNumber());
                    String message = ex.getMessage();
                    if(message.toLowerCase().trim().endsWith("not found.")) {
                        System.err.println("[Warning] "+
                               str.toString()+": "+ message);
                    } else { // do standard thing
                        System.err.println("[Fatal Error] "+
                               str.toString()+":"+message);
                        throw ex;
                    }
                }
            });

         try {
             parser.setFeature("http://xml.org/sax/features/validation", false);
             parser.setFeature("http://xml.org/sax/features/namespaces", true);
             parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
         }catch(  org.xml.sax.SAXNotRecognizedException e ) {
             e.printStackTrace();
         }catch( org.xml.sax.SAXNotSupportedException e ) {
             e.printStackTrace();
         }

         try {
             parser.parse( source );
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
             String targetNSURI = getTargetNamespaceString(root);
             if (!targetNSURI.equals(namespaceString) ) {
                 // REVISIT: Localize
                 reportGenericSchemaError("imported schema '"+location+"' has a different targetNameSpace '"
                                          +targetNSURI+"' from what is declared '"+namespaceString+"'.");
             }
             else {
                 TraverseSchema impSchema = new TraverseSchema(root, fStringPool, importedGrammar, fGrammarResolver, fErrorReporter, location, fEntityResolver, fFullConstraintChecking);
                 Enumeration ics = impSchema.fIdentityConstraints.keys();
                 while(ics.hasMoreElements()) {
                    Object icsKey = ics.nextElement();
                    fIdentityConstraints.put(icsKey, impSchema.fIdentityConstraints.get(icsKey));
                }
                 Enumeration icNames = impSchema.fIdentityConstraintNames.keys();
                 while(icNames.hasMoreElements()) {
                    String icsNameKey = (String)icNames.nextElement();
                    fIdentityConstraintNames.put(icsNameKey, impSchema.fIdentityConstraintNames.get(icsNameKey));
                }
            }
         }
         else {
             reportGenericSchemaError("Could not get the doc root for imported Schema file: "+location);
         }
    }

    // utility method for finding the targetNamespace (and flagging errors if they occur)
    private String getTargetNamespaceString( Element root) throws Exception {
        String targetNSURI = "";
        Attr targetNSAttr = root.getAttributeNode(SchemaSymbols.ATT_TARGETNAMESPACE);
        if(targetNSAttr != null) {
            targetNSURI=targetNSAttr.getValue();
            if(targetNSURI.length() == 0) {
                // REVISIT:  localize
                reportGenericSchemaError("sch-prop-correct.1:  \"\" is not a legal value for the targetNamespace attribute; the attribute must either be absent or contain a nonempty value");
            }
        }
        return targetNSURI;
    } // end getTargetNamespaceString(Element)

    /**
    * <annotation>(<appinfo> | <documentation>)*</annotation>
    * 
    * @param annotationDecl:  the DOM node corresponding to the <annotation> info item
    */
    private void traverseAnnotationDecl(Element annotationDecl) throws Exception {

        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(annotationDecl, scope);

        for(Element child = XUtil.getFirstChildElement(annotationDecl); child != null;
                 child = XUtil.getNextSiblingElement(child)) {
            String name = child.getLocalName();
            if(!((name.equals(SchemaSymbols.ELT_APPINFO)) ||
                    (name.equals(SchemaSymbols.ELT_DOCUMENTATION)))) {
                // REVISIT: Localize
                reportGenericSchemaError("an <annotation> can only contain <appinfo> and <documentation> elements");
            }

            // General Attribute Checking
            attrValues = fGeneralAttrCheck.checkAttributes(child, scope);
        }
    }


    //
    // Evaluates content of Annotation if present.
    //
    // @param: elm - top element
    // @param: content - content must be annotation? or some other simple content
    // @param: isEmpty: -- true if the content allowed is (annotation?) only
    //                     false if must have some element (with possible preceding <annotation?>)
    // 
    //REVISIT: this function should be used in all traverse* methods!
   private Element checkContent( Element elm, Element content, boolean isEmpty ) throws Exception {
       //isEmpty = true-> means content can be null!
       if ( content == null) {
           if (!isEmpty) {
               reportSchemaError(SchemaMessageProvider.ContentError,
                                 new Object [] { elm.getAttribute( SchemaSymbols.ATT_NAME )});
           }
           return null;
       }
       if (content.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) {
		   traverseAnnotationDecl( content );   
		   content = XUtil.getNextSiblingElement(content);
		   if (content == null ) {   //must be followed by <simpleType?>
			   if (!isEmpty) {
				   reportSchemaError(SchemaMessageProvider.ContentError,
									 new Object [] { elm.getAttribute( SchemaSymbols.ATT_NAME )});
			   }
			   return null;
		   }
		   if (content.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) {
			   reportSchemaError(SchemaMessageProvider.AnnotationError,
								 new Object [] { elm.getAttribute( SchemaSymbols.ATT_NAME )});
			   return null;
		   }
		   //return null if expected only annotation?, else returns updated content
	   }
       return content;  
   }

   
   //@param: elm - top element
   //@param: baseTypeStr - type (base/itemType/memberTypes)
   //@param: baseRefContext:  whether the caller is using this type as a base for restriction, union or list
   //return DatatypeValidator available for the baseTypeStr, null if not found or disallowed.
   // also throws an error if the base type won't allow itself to be used in this context.
   //REVISIT: this function should be used in some|all traverse* methods!
   private DatatypeValidator findDTValidator (Element elm, String baseTypeStr, int baseRefContext )  throws Exception{
        int baseType      = fStringPool.addSymbol( baseTypeStr );
        String prefix = "";
        DatatypeValidator baseValidator = null;
        String localpart = baseTypeStr;
        int colonptr = baseTypeStr.indexOf(":");
        if ( colonptr > 0) {
            prefix = baseTypeStr.substring(0,colonptr);
            localpart = baseTypeStr.substring(colonptr+1);
        }
        String uri = resolvePrefixToURI(prefix);
        baseValidator = getDatatypeValidator(uri, localpart);
        if (baseValidator == null) {
            Element baseTypeNode = getTopLevelComponentByName(SchemaSymbols.ELT_SIMPLETYPE, localpart);
            if (baseTypeNode != null) {
                traverseSimpleTypeDecl( baseTypeNode ); 
                
                baseValidator = getDatatypeValidator(uri, localpart);
            }
        }
        Integer finalValue;
        if ( baseValidator == null ) {
            reportSchemaError(SchemaMessageProvider.UnknownBaseDatatype,
                              new Object [] { elm.getAttribute( SchemaSymbols.ATT_BASE ),
                                  elm.getAttribute(SchemaSymbols.ATT_NAME)});
        } else {
            finalValue = (uri.equals("")?
                    ((Integer)fSimpleTypeFinalRegistry.get(localpart)):
                    ((Integer)fSimpleTypeFinalRegistry.get(uri + "," +localpart)));
            if((finalValue != null) &&
                    ((finalValue.intValue() & baseRefContext) != 0)) {
                //REVISIT:  localize
                reportGenericSchemaError("the base type " + baseTypeStr + " does not allow itself to be used as the base for a restriction and/or as a type in a list and/or union");
                return baseValidator;
            }
        }
       return baseValidator;
    }

    private void checkEnumerationRequiredNotation(String name, String type) throws Exception{
        String localpart = type;
        int colonptr = type.indexOf(":");
        if ( colonptr > 0) {
            localpart = type.substring(colonptr+1);
        }
        if (localpart.equals("NOTATION")) {        
          reportGenericSchemaError("[enumeration-required-notation] It is an error for NOTATION to be used "+
                                "directly in a schema in element/attribute '"+name+"'"); 
        }

    }

   // @used in traverseSimpleType
   // on return we need to pop the last simpleType name from 
   // the name stack
    private int resetSimpleTypeNameStack(int returnValue){
       if (!fSimpleTypeNameStack.empty()) {
           fSimpleTypeNameStack.pop();
       }
       return returnValue;
    }

    // @used in traverseSimpleType
    // report an error cos-list-of-atomic and reset the last name of the list datatype we traversing
    private void reportCosListOfAtomic () throws Exception{  
       reportGenericSchemaError("cos-list-of-atomic: The itemType must have a {variety} of atomic or union (in which case all the {member type definitions} must be atomic)");
       fListName="";
    }

    // @used in traverseSimpleType
    // find if union datatype validator has list datatype member.
    private boolean isListDatatype (DatatypeValidator validator){
       if (validator instanceof UnionDatatypeValidator) {
              Vector temp = ((UnionDatatypeValidator)validator).getBaseValidators();
              for (int i=0;i<temp.size();i++) {
                   if (temp.elementAt(i) instanceof ListDatatypeValidator) {
                       return true;
                   }
                   if (temp.elementAt(i) instanceof UnionDatatypeValidator) {
                       if (isListDatatype((DatatypeValidator)temp.elementAt(i))) {
                           return true;
                       }
                   }
              }
       }
       return false;
    }

    
   
   /**
     * Traverse SimpleType declaration:
     * <simpleType
     *         final = #all | list of (restriction, union or list)
     *         id = ID 
     *         name = NCName>
     *         Content: (annotation? , ((list | restriction | union)))
     *       </simpleType>
     * traverse <list>|<restriction>|<union>
     * 
     * @param simpleTypeDecl
     * @return 
     */
    private int traverseSimpleTypeDecl( Element simpleTypeDecl ) throws Exception {
                
        // General Attribute Checking
        int scope = isTopLevel(simpleTypeDecl)?
                    GeneralAttrCheck.ELE_CONTEXT_GLOBAL:
                    GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(simpleTypeDecl, scope);

        String nameProperty          =  simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME );
        String qualifiedName = nameProperty;


        //---------------------------------------------------
        // set qualified name
        //---------------------------------------------------
        if ( nameProperty.length() == 0) { // anonymous simpleType
            qualifiedName = "#S#"+(fSimpleTypeAnonCount++);
            fStringPool.addSymbol(qualifiedName);   
        }
        else {
            if (fTargetNSURIString.length () != 0) {
                qualifiedName = fTargetNSURIString+","+qualifiedName;
            }
            fStringPool.addSymbol( nameProperty );        
        }

        //----------------------------------------------------------------------
        //check if we have already traversed the same simpleType decl
        //----------------------------------------------------------------------        
        if (fDatatypeRegistry.getDatatypeValidator(qualifiedName)!=null) {
            return resetSimpleTypeNameStack(fStringPool.addSymbol(qualifiedName));
        }
        else {
           if (fSimpleTypeNameStack.search(qualifiedName) != -1 ){
               // cos-no-circular-unions && no circular definitions
               reportGenericSchemaError("cos-no-circular-unions: no circular definitions are allowed for an element '"+ nameProperty+"'");
               return resetSimpleTypeNameStack(-1);
           }
        }
        

        //----------------------------------------------------------
        // update _final_ registry
        //----------------------------------------------------------
        Attr finalAttr = simpleTypeDecl.getAttributeNode(SchemaSymbols.ATT_FINAL);
        int finalProperty = 0;
        if(finalAttr != null) 
            finalProperty = parseFinalSet(finalAttr.getValue());
        else
            finalProperty = parseFinalSet(null);

        // if we have a nonzero final , store it in the hash...
        if(finalProperty != 0) 
            fSimpleTypeFinalRegistry.put(qualifiedName, new Integer(finalProperty));


        // -------------------------------
        // remember name being traversed to 
        // avoid circular definitions in union
        // -------------------------------
        fSimpleTypeNameStack.push(qualifiedName);
        

        //----------------------------------------------------------------------
        //annotation?,(list|restriction|union)
        //----------------------------------------------------------------------
        Element content = XUtil.getFirstChildElement(simpleTypeDecl);
        content = checkContent(simpleTypeDecl, content, false);
        if (content == null) {
            return resetSimpleTypeNameStack(-1);
        }

        // General Attribute Checking
        scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable contentAttrs = fGeneralAttrCheck.checkAttributes(content, scope);

        //----------------------------------------------------------------------
        //use content.getLocalName for the cases there "xsd:" is a prefix, ei. "xsd:list"
        //----------------------------------------------------------------------
        String varietyProperty = content.getLocalName();
        String baseTypeQNameProperty = null;
        Vector dTValidators = null;
        int size = 0;  
        StringTokenizer unionMembers = null;
        boolean list = false;
        boolean union = false;
        boolean restriction = false;
        int numOfTypes = 0; //list/restriction = 1, union = "+"
        
        if (varietyProperty.equals(SchemaSymbols.ELT_LIST)) { //traverse List
           baseTypeQNameProperty =  content.getAttribute( SchemaSymbols.ATT_ITEMTYPE );
           list = true;
           if (fListName.length() != 0) { // parent is <list> datatype
                    reportCosListOfAtomic();
                    return resetSimpleTypeNameStack(-1);
           }
           else {
                fListName = qualifiedName;
           }
        }
        else if (varietyProperty.equals(SchemaSymbols.ELT_RESTRICTION)) { //traverse Restriction
            baseTypeQNameProperty =  content.getAttribute( SchemaSymbols.ATT_BASE );
            restriction= true;
        }
        else if (varietyProperty.equals(SchemaSymbols.ELT_UNION)) { //traverse union
            union = true;
            baseTypeQNameProperty = content.getAttribute( SchemaSymbols.ATT_MEMBERTYPES);
            if (baseTypeQNameProperty.length() != 0) {
                unionMembers = new StringTokenizer( baseTypeQNameProperty );
                size = unionMembers.countTokens();
            }
            else {
                size = 1; //at least one must be seen as <simpleType> decl
            }
            dTValidators = new Vector (size, 2); 
        }
        else {
             reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
                       new Object [] { varietyProperty });
                       return -1;
        }
        if(XUtil.getNextSiblingElement(content) != null) {
            // REVISIT: Localize
            reportGenericSchemaError("error in content of simpleType");
        }

        int typeNameIndex;
        DatatypeValidator baseValidator = null;
        
        if ( baseTypeQNameProperty.length() == 0 ) { 
            //---------------------------
            //must 'see' <simpleType>
            //---------------------------

            //content = {annotation?,simpleType?...}
            content = XUtil.getFirstChildElement(content);
            
            //check content (annotation?, ...)
            content = checkContent(simpleTypeDecl, content, false);
            if (content == null) {
                return resetSimpleTypeNameStack(-1);
            }
            if (content.getLocalName().equals( SchemaSymbols.ELT_SIMPLETYPE )) { 
              typeNameIndex = traverseSimpleTypeDecl(content); 
              if (typeNameIndex!=-1) {
                  baseValidator=fDatatypeRegistry.getDatatypeValidator(fStringPool.toString(typeNameIndex));
                  if (baseValidator !=null && union) {  
                      dTValidators.addElement((DatatypeValidator)baseValidator);
                  }
              }
              if ( typeNameIndex == -1 || baseValidator == null) {
                  reportSchemaError(SchemaMessageProvider.UnknownBaseDatatype,
                                        new Object [] { content.getAttribute( SchemaSymbols.ATT_BASE ),
                                            content.getAttribute(SchemaSymbols.ATT_NAME) });
                      return resetSimpleTypeNameStack(-1);
              }
            }
            else {
                 reportSchemaError(SchemaMessageProvider.ListUnionRestrictionError,
                        new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME )});
                 return resetSimpleTypeNameStack(-1);
            }
        } //end - must see simpleType?
        else { 
            //-----------------------------
            //base was provided - get proper validator. 
            //-----------------------------
            numOfTypes = 1;
            if (union) {
                numOfTypes= size;
            }
            //--------------------------------------------------------------------
            // this loop is also where we need to find out whether the type being used as
            // a base (or itemType or whatever) allows such things.
            //--------------------------------------------------------------------
            int baseRefContext = (restriction? SchemaSymbols.RESTRICTION:0);
            baseRefContext = baseRefContext | (union? SchemaSymbols.UNION:0);
            baseRefContext = baseRefContext | (list ? SchemaSymbols.LIST:0);
            for (int i=0; i<numOfTypes; i++) {  //find all validators
                if (union) {
                    baseTypeQNameProperty = unionMembers.nextToken();
                }
                baseValidator = findDTValidator ( simpleTypeDecl, baseTypeQNameProperty, baseRefContext);
                if ( baseValidator == null) {
                    return resetSimpleTypeNameStack(-1);
                }
                // ------------------------------
                // (variety is list)cos-list-of-atomic
                // ------------------------------
                if (fListName.length() != 0 ) {
                    if (baseValidator instanceof ListDatatypeValidator) {                   
                        reportCosListOfAtomic();
                        return resetSimpleTypeNameStack(-1);
                    }
                    //-----------------------------------------------------
                    // if baseValidator is of type (union) need to look
                    // at Union validators to make sure that List is not one of them
                    //-----------------------------------------------------
                    if (isListDatatype(baseValidator)) {
                        reportCosListOfAtomic();
                        return resetSimpleTypeNameStack(-1);

                    }
                    
                }
                if (union) {
                    dTValidators.addElement((DatatypeValidator)baseValidator); //add validator to structure
                }
                //REVISIT: Should we raise exception here?
                // if baseValidator.isInstanceOf(LIST) and UNION
                if ( list && (baseValidator instanceof UnionDatatypeValidator)) {
                    reportSchemaError(SchemaMessageProvider.UnknownBaseDatatype,
                                      new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_BASE ),
                                          simpleTypeDecl.getAttribute(SchemaSymbols.ATT_NAME)});
                    return -1;
                }
            }
        } //end - base is available
        
        
        // ------------------------------------------
        // move to next child 
        // <base==empty)->[simpleType]->[facets]  OR
        // <base!=empty)->[facets]
        // ------------------------------------------
        if (baseTypeQNameProperty.length() == 0) {  
            content = XUtil.getNextSiblingElement( content );
        }
        else { 
            content = XUtil.getFirstChildElement(content);
        }
        
        // ------------------------------------------
        //get more types for union if any
        // ------------------------------------------
        if (union) {
            int index=size;
            if (baseTypeQNameProperty.length() != 0 ) {
                content = checkContent(simpleTypeDecl, content, true);
            }
            while (content!=null) {
                typeNameIndex = traverseSimpleTypeDecl(content);   
                if (typeNameIndex!=-1) {
                    baseValidator=fDatatypeRegistry.getDatatypeValidator(fStringPool.toString(typeNameIndex));
                    if (baseValidator != null) {
                        if (fListName.length() != 0 && baseValidator instanceof ListDatatypeValidator) {
                            reportCosListOfAtomic();
                            return resetSimpleTypeNameStack(-1);
                        }
                        dTValidators.addElement((DatatypeValidator)baseValidator);
                    }
                }
                if ( baseValidator == null || typeNameIndex == -1) {
                     reportSchemaError(SchemaMessageProvider.UnknownBaseDatatype,
                                      new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_BASE ),
                                          simpleTypeDecl.getAttribute(SchemaSymbols.ATT_NAME)});
                    return (-1);
                }
                content   = XUtil.getNextSiblingElement( content );
            }
        } // end - traverse Union
        
        
        if (fListName.length() != 0) {
            // reset fListName, meaning that we are done with
            // traversing <list> and its itemType resolves to atomic value
            if (fListName.equals(qualifiedName)) {
                fListName = "";
            }
        }
              
        int numFacets=0;
        fFacetData.clear();
        if (restriction && content != null) {
            short flags = 0; // flag facets that have fixed="true"
            int numEnumerationLiterals = 0;
            Vector enumData  = new Vector();
            content = checkContent(simpleTypeDecl, content , true);
            StringBuffer pattern = null;
            String facet;
            while (content != null) { 
                if (content.getNodeType() == Node.ELEMENT_NODE) {
                        // General Attribute Checking
                        contentAttrs = fGeneralAttrCheck.checkAttributes(content, scope);
                        numFacets++;
                        facet =content.getLocalName(); 
                        if (facet.equals(SchemaSymbols.ELT_ENUMERATION)) {
                            numEnumerationLiterals++;
                            String enumVal = content.getAttribute(SchemaSymbols.ATT_VALUE);
                            String localName;
                            if (baseValidator instanceof NOTATIONDatatypeValidator) {
                                String prefix = "";
                                String localpart = enumVal;
                                int colonptr = enumVal.indexOf(":");
                                if ( colonptr > 0) {
                                        prefix = enumVal.substring(0,colonptr);
                                        localpart = enumVal.substring(colonptr+1);
                                }
                                String uriStr = (prefix.length() != 0)?resolvePrefixToURI(prefix):fTargetNSURIString;
                                nameProperty=uriStr + ":" + localpart;
                                localName = (String)fNotationRegistry.get(nameProperty);
                                if(localName == null){
                                       localName = traverseNotationFromAnotherSchema( localpart, uriStr);
                                       if (localName == null) {
                                            reportGenericSchemaError("Notation '" + localpart + 
                                                                    "' not found in the grammar "+ uriStr); 
                                                                    
                                       }
                                }
                                enumVal=nameProperty;
                            }
                            enumData.addElement(enumVal);
                            checkContent(simpleTypeDecl, XUtil.getFirstChildElement( content ), true);
                        }
                        else if (facet.equals(SchemaSymbols.ELT_ANNOTATION) || facet.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                                  reportSchemaError(SchemaMessageProvider.ListUnionRestrictionError,
                                  new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME )});
                        }         
                        else if (facet.equals(SchemaSymbols.ELT_PATTERN)) {
                            if (pattern == null) {                                
                                pattern = new StringBuffer (content.getAttribute( SchemaSymbols.ATT_VALUE ));
                            }
                            else { 
                                // ---------------------------------------------
                                //datatypes: 5.2.4 pattern: src-multiple-pattern 
                                // ---------------------------------------------
                                pattern.append("|");
                                pattern.append(content.getAttribute( SchemaSymbols.ATT_VALUE ));
                                checkContent(simpleTypeDecl, XUtil.getFirstChildElement( content ), true);
                            }
                        }
                        else {
                            if ( fFacetData.containsKey(facet) )
                                reportSchemaError(SchemaMessageProvider.DatatypeError,
                                                  new Object [] {"The facet '" + facet + "' is defined more than once."} );
                             fFacetData.put(facet,content.getAttribute( SchemaSymbols.ATT_VALUE ));
                             
                             if (content.getAttribute( SchemaSymbols.ATT_FIXED).equals("true") ||
                                 content.getAttribute( SchemaSymbols.ATT_FIXED).equals("1")){
                                 // --------------------------------------------
                                 // set fixed facet flags
                                 // length - must remain const through derivation
                                 // thus we don't care if it fixed
                                 // --------------------------------------------
                                  if ( facet.equals(SchemaSymbols.ELT_MINLENGTH) ) {
                                      flags |= DatatypeValidator.FACET_MINLENGTH;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_MAXLENGTH)) {
                                      flags |= DatatypeValidator.FACET_MAXLENGTH;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_MAXEXCLUSIVE)) {
                                      flags |= DatatypeValidator.FACET_MAXEXCLUSIVE;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_MAXINCLUSIVE)) {
                                      flags |= DatatypeValidator.FACET_MAXINCLUSIVE;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_MINEXCLUSIVE)) {
                                      flags |= DatatypeValidator.FACET_MINEXCLUSIVE;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_MININCLUSIVE)) {
                                      flags |= DatatypeValidator.FACET_MININCLUSIVE;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_TOTALDIGITS)) {
                                      flags |= DatatypeValidator.FACET_TOTALDIGITS;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_FRACTIONDIGITS)) {
                                      flags |= DatatypeValidator.FACET_FRACTIONDIGITS;
                                  }
                                  else if (facet.equals(SchemaSymbols.ELT_WHITESPACE) &&
                                           baseValidator instanceof StringDatatypeValidator) {
                                      flags |= DatatypeValidator.FACET_WHITESPACE;
                                  }
                              }
                             checkContent(simpleTypeDecl, XUtil.getFirstChildElement( content ), true);
                        }
                }
                    content = XUtil.getNextSiblingElement(content);
            }
            if (numEnumerationLiterals > 0) {
                  fFacetData.put(SchemaSymbols.ELT_ENUMERATION, enumData);
            }
            if (pattern !=null) {
                fFacetData.put(SchemaSymbols.ELT_PATTERN, pattern.toString());
            }
            if (flags != 0) {
                fFacetData.put(DatatypeValidator.FACET_FIXED, new Short(flags));
            }
        }

        
        else if (list && content!=null) { 
            // report error - must not have any children!
            if (baseTypeQNameProperty.length() != 0) {
                content = checkContent(simpleTypeDecl, content, true);
                if (content!=null) {
                    reportSchemaError(SchemaMessageProvider.ListUnionRestrictionError,
                                      new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME )});
            }
            }
            else {
                reportSchemaError(SchemaMessageProvider.ListUnionRestrictionError,
                        new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME )});
                //REVISIT: should we return?
            }
        }
        else if (union && content!=null) { 
            //report error - must not have any children!
             if (baseTypeQNameProperty.length() != 0) {
                content = checkContent(simpleTypeDecl, content, true);
                if (content!=null) {
                    reportSchemaError(SchemaMessageProvider.ListUnionRestrictionError,
                                            new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME )});
                }
            }
            else {
                reportSchemaError(SchemaMessageProvider.ListUnionRestrictionError,
                        new Object [] { simpleTypeDecl.getAttribute( SchemaSymbols.ATT_NAME )});
                //REVISIT: should we return?
            }
        }
     
        // ----------------------------------------------------------------------
        // create & register validator for "generated" type if it doesn't exist 
        // ----------------------------------------------------------------------
        try { 
           DatatypeValidator newValidator =
                 fDatatypeRegistry.getDatatypeValidator( qualifiedName );

           if( newValidator == null ) { // not previously registered
               if (list) {
                    fDatatypeRegistry.createDatatypeValidator( qualifiedName, baseValidator, 
                                                               fFacetData,true);
               }
               else if (restriction) {
                   fDatatypeRegistry.createDatatypeValidator( qualifiedName, baseValidator,
                                                               fFacetData,false);
               }
               else { //union
                   fDatatypeRegistry.createDatatypeValidator( qualifiedName, dTValidators);
               }
                           
           }
            
           } catch (Exception e) {
               reportSchemaError(SchemaMessageProvider.DatatypeError,new Object [] { e.getMessage() });
           }
        return resetSimpleTypeNameStack(fStringPool.addSymbol(qualifiedName));
     }


    /*
    * <any 
    *   id = ID 
    *   maxOccurs = string 
    *   minOccurs = nonNegativeInteger 
    *   namespace = (##any | ##other) | List of (anyURI | (##targetNamespace | ##local))
    *   processContents = lax | skip | strict>
    *   Content: (annotation?)
    * </any>
    */
    private int traverseAny(Element child) throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(child, scope);

        Element annotation = checkContent( child, XUtil.getFirstChildElement(child), true );
        if(annotation != null ) {
            // REVISIT: Localize
            reportGenericSchemaError("<any> elements can contain at most one <annotation> element in their children");
        }
        int anyIndex = -1;
        String namespace = child.getAttribute(SchemaSymbols.ATT_NAMESPACE).trim();
        String processContents = child.getAttribute("processContents").trim();

        int processContentsAny = XMLContentSpec.CONTENTSPECNODE_ANY;
        int processContentsAnyOther = XMLContentSpec.CONTENTSPECNODE_ANY_OTHER;
        int processContentsAnyLocal = XMLContentSpec.CONTENTSPECNODE_ANY_NS;

        if (processContents.length() > 0 && !processContents.equals("strict")) {
            if (processContents.equals("lax")) {
                processContentsAny = XMLContentSpec.CONTENTSPECNODE_ANY_LAX;
                processContentsAnyOther = XMLContentSpec.CONTENTSPECNODE_ANY_OTHER_LAX;
                processContentsAnyLocal = XMLContentSpec.CONTENTSPECNODE_ANY_NS_LAX;
            }
            else if (processContents.equals("skip")) {
                processContentsAny = XMLContentSpec.CONTENTSPECNODE_ANY_SKIP;
                processContentsAnyOther = XMLContentSpec.CONTENTSPECNODE_ANY_OTHER_SKIP;
                processContentsAnyLocal = XMLContentSpec.CONTENTSPECNODE_ANY_NS_SKIP;
            }
        }

        if (namespace.length() == 0 || namespace.equals("##any")) {
            anyIndex = fSchemaGrammar.addContentSpecNode(processContentsAny, -1, StringPool.EMPTY_STRING, false);
        }
        else if (namespace.equals("##other")) {
			String uri = fTargetNSURIString;
            int uriIndex = fStringPool.addSymbol(uri);
            anyIndex = fSchemaGrammar.addContentSpecNode(processContentsAnyOther, -1, uriIndex, false);
        }
        else if (namespace.length() > 0) {
            int uriIndex, leafIndex, choiceIndex;

            StringTokenizer tokenizer = new StringTokenizer(namespace);
                String token = tokenizer.nextToken();
            if (token.equals(SchemaSymbols.ATTVAL_TWOPOUNDLOCAL)) {
                choiceIndex = fSchemaGrammar.addContentSpecNode(processContentsAnyLocal, -1, StringPool.EMPTY_STRING, false);
            } else {
                if (token.equals("##targetNamespace"))
			        token = fTargetNSURIString;
                uriIndex = fStringPool.addSymbol(token);
                choiceIndex = fSchemaGrammar.addContentSpecNode(processContentsAnyLocal, -1, uriIndex, false);
            }

            while (tokenizer.hasMoreElements()) {
                token = tokenizer.nextToken();
                if (token.equals(SchemaSymbols.ATTVAL_TWOPOUNDLOCAL)) {
                    leafIndex = fSchemaGrammar.addContentSpecNode(processContentsAnyLocal, -1, StringPool.EMPTY_STRING, false);
                } else {
                    if (token.equals("##targetNamespace"))
                        token = fTargetNSURIString;
                    uriIndex = fStringPool.addSymbol(token);
                    leafIndex = fSchemaGrammar.addContentSpecNode(processContentsAnyLocal, -1, uriIndex, false);
                }

                choiceIndex = fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_CHOICE, choiceIndex, leafIndex, false);
            }
            anyIndex = choiceIndex;
        }
        else {
            // REVISIT: Localize
            reportGenericSchemaError("Empty namespace attribute for any element");
        }

        return anyIndex;
    }


    public DatatypeValidator getDatatypeValidator(String uri, String localpart) {

        DatatypeValidator dv = null;

        if (uri.length()==0 || uri.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA)) {
            dv = fDatatypeRegistry.getDatatypeValidator( localpart );
        }
        else {
            dv = fDatatypeRegistry.getDatatypeValidator( uri+","+localpart );
        }

        return dv;
    }

    /*
    * <anyAttribute 
    *   id = ID 
    *   namespace = ##any | ##other | ##local | list of {uri, ##targetNamespace}>
    *   Content: (annotation?)
    * </anyAttribute>
    */
    private XMLAttributeDecl traverseAnyAttribute(Element anyAttributeDecl) throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(anyAttributeDecl, scope);

        Element annotation = checkContent( anyAttributeDecl, XUtil.getFirstChildElement(anyAttributeDecl), true );
        if(annotation != null ) {
            // REVISIT: Localize
            reportGenericSchemaError("<anyAttribute> elements can contain at most one <annotation> element in their children");
        }
        XMLAttributeDecl anyAttDecl = new XMLAttributeDecl();
        String processContents = anyAttributeDecl.getAttribute(SchemaSymbols.ATT_PROCESSCONTENTS).trim();
        String namespace = anyAttributeDecl.getAttribute(SchemaSymbols.ATT_NAMESPACE).trim();
        // simplify!  NG
        //String curTargetUri = anyAttributeDecl.getOwnerDocument().getDocumentElement().getAttribute("targetNamespace");
        String curTargetUri = fTargetNSURIString;

        if ( namespace.length() == 0 || namespace.equals(SchemaSymbols.ATTVAL_TWOPOUNDANY) ) {
            anyAttDecl.type = XMLAttributeDecl.TYPE_ANY_ANY;
        } 
        else if (namespace.equals(SchemaSymbols.ATTVAL_TWOPOUNDOTHER)) {
            anyAttDecl.type = XMLAttributeDecl.TYPE_ANY_OTHER;
            anyAttDecl.name.uri = fStringPool.addSymbol(curTargetUri);
        }
        else if (namespace.length() > 0){
            anyAttDecl.type = XMLAttributeDecl.TYPE_ANY_LIST;

            StringTokenizer tokenizer = new StringTokenizer(namespace);
            int aStringList = fStringPool.startStringList();
            Vector tokens = new Vector();
            int tokenStr;
            while (tokenizer.hasMoreElements()) {
                String token = tokenizer.nextToken();
                if (token.equals(SchemaSymbols.ATTVAL_TWOPOUNDLOCAL)) {
                    tokenStr = fStringPool.EMPTY_STRING;
                } else {
                    if (token.equals(SchemaSymbols.ATTVAL_TWOPOUNDTARGETNS))
                    token = curTargetUri;
                    tokenStr = fStringPool.addSymbol(token);
                }
                if (!fStringPool.addStringToList(aStringList, tokenStr)){
                    reportGenericSchemaError("Internal StringPool error when reading the "+
                                             "namespace attribute for anyattribute declaration");
                }
            }
            fStringPool.finishStringList(aStringList);

            anyAttDecl.enumeration = aStringList;
        }
        else {
            // REVISIT: Localize
            reportGenericSchemaError("Empty namespace attribute for anyattribute declaration");
        }

        // default processContents is "strict";
        if (processContents.equals(SchemaSymbols.ATTVAL_SKIP)){
            anyAttDecl.defaultType |= XMLAttributeDecl.PROCESSCONTENTS_SKIP;
        }
        else if (processContents.equals(SchemaSymbols.ATTVAL_LAX)) {
            anyAttDecl.defaultType |= XMLAttributeDecl.PROCESSCONTENTS_LAX;
        }
        else {
            anyAttDecl.defaultType |= XMLAttributeDecl.PROCESSCONTENTS_STRICT;
        }

        return anyAttDecl; 
    }

    // Schema Component Constraint: Attribute Wildcard Intersection
    // For a wildcard's {namespace constraint} value to be the intensional intersection of two other such values (call them O1 and O2): the appropriate case among the following must be true:
    // 1 If O1 and O2 are the same value, then that value must be the value.
    // 2 If either O1 or O2 is any, then the other must be the value.
    // 3 If either O1 or O2 is a pair of not and a namespace name and the other is a set of (namespace names or ·absent·), then that set, minus the negated namespace name if it was in the set, must be the value.
    // 4 If both O1 and O2 are sets of (namespace names or ·absent·), then the intersection of those sets must be the value.
    // 5 If the two are negations of different namespace names, then the intersection is not expressible.
    // In the case where there are more than two values, the intensional intersection is determined by identifying the intensional intersection of two of the values as above, then the intensional intersection of that value with the third (providing the first intersection was expressible), and so on as required.
    private XMLAttributeDecl AWildCardIntersection(XMLAttributeDecl oneAny, XMLAttributeDecl anotherAny) {
        // if either one is not expressible, the result is still not expressible
        if (oneAny.type == -1) {
            return oneAny;
        }
        if (anotherAny.type == -1) {
            return anotherAny;
        }

        // 1 If O1 and O2 are the same value, then that value must be the value.
        // this one is dealt with in different branches

        // 2 If either O1 or O2 is any, then the other must be the value.
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_ANY) {
            return anotherAny;
        }
        if (anotherAny.type == XMLAttributeDecl.TYPE_ANY_ANY) {
            return oneAny;
        }

        // 3 If either O1 or O2 is a pair of not and a namespace name and the other is a set of (namespace names or ·absent·), then that set, minus the negated namespace name if it was in the set, must be the value.
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_OTHER &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_LIST ||
            oneAny.type == XMLAttributeDecl.TYPE_ANY_LIST &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_OTHER) {
            XMLAttributeDecl anyList, anyOther;
            if (oneAny.type == XMLAttributeDecl.TYPE_ANY_LIST) {
                anyList = oneAny;
                anyOther = anotherAny;
            } else {
                anyList = anotherAny;
                anyOther = oneAny;
                }

            int[] uriList = fStringPool.stringListAsIntArray(anyList.enumeration);
            if (elementInSet(anyOther.name.uri, uriList)) {
                    int newList = fStringPool.startStringList();
                for (int i=0; i< uriList.length; i++) {
                    if (uriList[i] != anyOther.name.uri ) {
                        fStringPool.addStringToList(newList, uriList[i]);
                        }
                    }
                    fStringPool.finishStringList(newList);
                anyList.enumeration = newList;
                }

            return anyList;
        }

        // 4 If both O1 and O2 are sets of (namespace names or ·absent·), then the intersection of those sets must be the value.
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_LIST &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_LIST) {
            int[] result = intersect2sets(fStringPool.stringListAsIntArray(oneAny.enumeration),
                                          fStringPool.stringListAsIntArray(anotherAny.enumeration));
            int newList = fStringPool.startStringList();
            for (int i=0; i<result.length; i++) {
                fStringPool.addStringToList(newList, result[i]);
            }
            fStringPool.finishStringList(newList);
            oneAny.enumeration = newList;
                return oneAny;
            }

        // 5 If the two are negations of different namespace names, then the intersection is not expressible.
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_OTHER &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_OTHER) {
            if (oneAny.name.uri == anotherAny.name.uri) {
                return oneAny;
            } else {
                oneAny.type = -1;
                return oneAny;
            }
        }

        // should never go there;
                    return oneAny;
                }

    // Schema Component Constraint: Attribute Wildcard Union
    // For a wildcard's {namespace constraint} value to be the intensional union of two other such values (call them O1 and O2): the appropriate case among the following must be true:
    // 1 If O1 and O2 are the same value, then that value must be the value.
    // 2 If either O1 or O2 is any, then any must be the value.
    // 3 If both O1 and O2 are sets of (namespace names or ·absent·), then the union of those sets must be the value.
    // 4 If the two are negations of different namespace names, then any must be the value.
    // 5 If either O1 or O2 is a pair of not and a namespace name and the other is a set of (namespace names or ·absent·), then The appropriate case among the following must be true:
    // 5.1 If the set includes the negated namespace name, then any must be the value.
    // 5.2 If the set does not include the negated namespace name, then whichever of O1 or O2 is a pair of not and a namespace name must be the value.
    // In the case where there are more than two values, the intensional union is determined by identifying the intensional union of two of the values as above, then the intensional union of that value with the third, and so on as required.
    private XMLAttributeDecl AWildCardUnion(XMLAttributeDecl oneAny, XMLAttributeDecl anotherAny) {
        // if either one is not expressible, the result is still not expressible
        if (oneAny.type == -1) {
                    return oneAny;
                }
        if (anotherAny.type == -1) {
            return anotherAny;
            }

        // 1 If O1 and O2 are the same value, then that value must be the value.
        // this one is dealt with in different branches

        // 2 If either O1 or O2 is any, then any must be the value.
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_ANY) {
                return oneAny;
            }
        if (anotherAny.type == XMLAttributeDecl.TYPE_ANY_ANY) {
            return anotherAny;
        }

        // 3 If both O1 and O2 are sets of (namespace names or ·absent·), then the union of those sets must be the value.
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_LIST &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_LIST) {
            int[] result = union2sets(fStringPool.stringListAsIntArray(oneAny.enumeration),
                                               fStringPool.stringListAsIntArray(anotherAny.enumeration));
                int newList = fStringPool.startStringList();
                for (int i=0; i<result.length; i++) {
                    fStringPool.addStringToList(newList, result[i]);
                }
                fStringPool.finishStringList(newList);
                oneAny.enumeration = newList;
                return oneAny;
            }

        // 4 If the two are negations of different namespace names, then any must be the value.
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_OTHER &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_OTHER) {
            if (oneAny.name.uri == anotherAny.name.uri) {
                return oneAny;
            } else {
                oneAny.type = XMLAttributeDecl.TYPE_ANY_ANY;
                return oneAny;
            }
        }

        // 5 If either O1 or O2 is a pair of not and a namespace name and the other is a set of (namespace names or ·absent·), then The appropriate case among the following must be true:
        if (oneAny.type == XMLAttributeDecl.TYPE_ANY_OTHER &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_LIST ||
            oneAny.type == XMLAttributeDecl.TYPE_ANY_LIST &&
            anotherAny.type == XMLAttributeDecl.TYPE_ANY_OTHER) {
            XMLAttributeDecl anyList, anyOther;
            if (oneAny.type == XMLAttributeDecl.TYPE_ANY_LIST) {
                anyList = oneAny;
                anyOther = anotherAny;
            } else {
                anyList = anotherAny;
                anyOther = oneAny;
        }
            // 5.1 If the set includes the negated namespace name, then any must be the value.
            if (elementInSet(anyOther.name.uri,
                             fStringPool.stringListAsIntArray(anyList.enumeration))) {
                anyOther.type = XMLAttributeDecl.TYPE_ANY_ANY;
            }
            // 5.2 If the set does not include the negated namespace name, then whichever of O1 or O2 is a pair of not and a namespace name must be the value.

            return anyOther;
        }

        // should never go there;
        return oneAny;
    }

    // Schema Component Constraint: Wildcard Subset
    // For a namespace constraint (call it sub) to be an intensional subset of another namespace constraint (call it super) one of the following must be true:
    // 1 super must be any.
    // 2 All of the following must be true:
    // 2.1 sub must be a pair of not and a namespace name or ·absent·.
    // 2.2 super must be a pair of not and the same value.
    // 3 All of the following must be true:
    // 3.1 sub must be a set whose members are either namespace names or ·absent·.
    // 3.2 One of the following must be true:
    // 3.2.1 super must be the same set or a superset thereof.
    // 3.2.2 super must be a pair of not and a namespace name or ·absent· and that value must not be in sub's set.
    private boolean AWildCardSubset(XMLAttributeDecl subAny, XMLAttributeDecl superAny) {
        // if either one is not expressible, it can't be a subset
        if (subAny.type == -1 || superAny.type == -1)
            return false;

        // 1 super must be any.
        if (superAny.type == XMLAttributeDecl.TYPE_ANY_ANY)
            return true;

        // 2 All of the following must be true:
        // 2.1 sub must be a pair of not and a namespace name or ·absent·.
        if (subAny.type == XMLAttributeDecl.TYPE_ANY_OTHER) {
            // 2.2 super must be a pair of not and the same value.
            if (superAny.type == XMLAttributeDecl.TYPE_ANY_OTHER &&
                subAny.name.uri == superAny.name.uri) {
                return true;
            }
        }

        // 3 All of the following must be true:
        // 3.1 sub must be a set whose members are either namespace names or ·absent·.
        if (subAny.type == XMLAttributeDecl.TYPE_ANY_LIST) {
        // 3.2 One of the following must be true:
            // 3.2.1 super must be the same set or a superset thereof.
            if (superAny.type == XMLAttributeDecl.TYPE_ANY_LIST &&
                subset2sets(fStringPool.stringListAsIntArray(subAny.enumeration),
                            fStringPool.stringListAsIntArray(superAny.enumeration))) {
                return true;
            }

            // 3.2.2 super must be a pair of not and a namespace name or ·absent· and that value must not be in sub's set.
            if (superAny.type == XMLAttributeDecl.TYPE_ANY_OTHER &&
                !elementInSet(superAny.name.uri, fStringPool.stringListAsIntArray(superAny.enumeration))) {
                return true;
            }
        }

        return false;
    }

    // Validation Rule: Wildcard allows Namespace Name
    // For a value which is either a namespace name or ·absent· to be ·valid· with respect to a wildcard constraint (the value of a {namespace constraint}) one of the following must be true:
    // 1 The constraint must be any.
    // 2 All of the following must be true:
    // 2.1 The constraint is a pair of not and a namespace name or ·absent· ([Definition:]  call this the namespace test).
    // 2.2 The value must not be identical to the ·namespace test·.
    // 2.3 The value must not be ·absent·.
    // 3 The constraint is a set, and the value is identical to one of the members of the set.
    private boolean AWildCardAllowsNameSpace(XMLAttributeDecl wildcard, String uri) {
        // if the constrain is not expressible, then nothing is allowed
        if (wildcard.type == -1)
            return false;

        // 1 The constraint must be any.
        if (wildcard.type == XMLAttributeDecl.TYPE_ANY_ANY)
            return true;

        int uriStr = fStringPool.addString(uri);

        // 2 All of the following must be true:
        // 2.1 The constraint is a pair of not and a namespace name or ·absent· ([Definition:]  call this the namespace test).
        if (wildcard.type == XMLAttributeDecl.TYPE_ANY_OTHER) {
            // 2.2 The value must not be identical to the ·namespace test·.
            // 2.3 The value must not be ·absent·.
            if (uriStr != wildcard.name.uri && uriStr != StringPool.EMPTY_STRING)
                return true;
        }

        // 3 The constraint is a set, and the value is identical to one of the members of the set.
        if (wildcard.type == XMLAttributeDecl.TYPE_ANY_LIST) {
            if (elementInSet(uriStr, fStringPool.stringListAsIntArray(wildcard.enumeration)))
                return true;
        }

        return false;
    }

    private boolean isAWildCard(XMLAttributeDecl a) {
        if (a.type == XMLAttributeDecl.TYPE_ANY_ANY
            ||a.type == XMLAttributeDecl.TYPE_ANY_LIST
            ||a.type == XMLAttributeDecl.TYPE_ANY_OTHER )
            return true;
        else
            return false;
    }

    int[] intersect2sets(int[] one, int[] theOther){
        int[] result = new int[(one.length>theOther.length?one.length:theOther.length)];

        // simple implemention, 
        int count = 0;
        for (int i=0; i<one.length; i++) {
            if (elementInSet(one[i], theOther))
                    result[count++] = one[i];
                }

        int[] result2 = new int[count];
        System.arraycopy(result, 0, result2, 0, count);

        return result2;
    }

    int[] union2sets(int[] one, int[] theOther){
        int[] result1 = new int[one.length];

        // simple implemention,
        int count = 0;
        for (int i=0; i<one.length; i++) {
            if (!elementInSet(one[i], theOther))
                result1[count++] = one[i];
        }

        int[] result2 = new int[count+theOther.length];
        System.arraycopy(result1, 0, result2, 0, count);
        System.arraycopy(theOther, 0, result2, count, theOther.length);

        return result2;
    }

    boolean subset2sets(int[] subSet, int[] superSet){
        for (int i=0; i<subSet.length; i++) {
            if (!elementInSet(subSet[i], superSet))
                return false;
        }

        return true;
    }

    boolean elementInSet(int ele, int[] set){
        boolean found = false;
        for (int i=0; i<set.length && !found; i++) {
            if (ele==set[i])
                found = true;
        }

        return found;
    }

    // wrapper traverseComplexTypeDecl method
    private int traverseComplexTypeDecl( Element complexTypeDecl ) throws Exception { 
        return traverseComplexTypeDecl (complexTypeDecl, false);
    }

    /**
     * Traverse ComplexType Declaration - Rec Implementation.
     *  
     *       <complexType 
     *         abstract = boolean 
     *         block = #all or (possibly empty) subset of {extension, restriction} 
     *         final = #all or (possibly empty) subset of {extension, restriction} 
     *         id = ID 
     *         mixed = boolean : false
     *         name = NCName>
     *         Content: (annotation? , (simpleContent | complexContent | 
     *                    ( (group | all | choice | sequence)? , 
     *                    ( (attribute | attributeGroup)* , anyAttribute?))))  
     *       </complexType>
     * @param complexTypeDecl
     * @param forwardRef
     * @return 
     */
    
    private int traverseComplexTypeDecl( Element complexTypeDecl, boolean forwardRef) 
            throws Exception {
        
        // General Attribute Checking
        int scope = isTopLevel(complexTypeDecl)?
                    GeneralAttrCheck.ELE_CONTEXT_GLOBAL:
                    GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(complexTypeDecl, scope);

        // ------------------------------------------------------------------
        // Get the attributes of the type
        // ------------------------------------------------------------------
        String isAbstract = complexTypeDecl.getAttribute( SchemaSymbols.ATT_ABSTRACT );
        String blockSet = null;
        Attr blockAttr = complexTypeDecl.getAttributeNode( SchemaSymbols.ATT_BLOCK );
        if (blockAttr != null)
            blockSet = blockAttr.getValue();
        String finalSet = null;
        Attr finalAttr = complexTypeDecl.getAttributeNode( SchemaSymbols.ATT_FINAL );
        if (finalAttr != null)
            finalSet = finalAttr.getValue();
        String typeId = complexTypeDecl.getAttribute( SchemaSymbols.ATTVAL_ID );
        String typeName = complexTypeDecl.getAttribute(SchemaSymbols.ATT_NAME); 
        String mixed = complexTypeDecl.getAttribute(SchemaSymbols.ATT_MIXED);
        boolean isNamedType = false;

        // ------------------------------------------------------------------
        // Generate a type name, if one wasn't specified
        // ------------------------------------------------------------------
        if (typeName.equals("")) { // gensym a unique name
            typeName = genAnonTypeName(complexTypeDecl);
        }

        if ( DEBUGGING )
            System.out.println("traversing complex Type : " + typeName); 

        fCurrentTypeNameStack.push(typeName);

        int typeNameIndex = fStringPool.addSymbol(typeName);

       
        // ------------------------------------------------------------------
        // Check if the type has already been registered
        // ------------------------------------------------------------------
        if (isTopLevel(complexTypeDecl)) {
        
            String fullName = fTargetNSURIString+","+typeName;
            ComplexTypeInfo temp = (ComplexTypeInfo) fComplexTypeRegistry.get(fullName);
            if (temp != null ) {
                // check for duplicate declarations
                if (!forwardRef)  {
                   if (temp.declSeen()) 
                      reportGenericSchemaError("sch-props-correct: Duplicate declaration for complexType " +
                                                typeName);
                   else 
                      temp.setDeclSeen();
                   
                }
                return fStringPool.addSymbol(fullName);
            }
            else {
              // check if the type is the name of a simple type                
              if (getDatatypeValidator(fTargetNSURIString,typeName)!=null)
                reportGenericSchemaError("sch-props-correct: Duplicate type declaration - type is " +
                                                typeName);
                  
            }
        }

        int scopeDefined = fScopeCount++;
        int previousScope = fCurrentScope;
        fCurrentScope = scopeDefined;

        Element child = null;
        ComplexTypeInfo typeInfo = new ComplexTypeInfo();

        try {

          // ------------------------------------------------------------------
          // First, handle any ANNOTATION declaration and get next child
          // ------------------------------------------------------------------
          child = checkContent(complexTypeDecl,XUtil.getFirstChildElement(complexTypeDecl),
                               true);

          // ------------------------------------------------------------------
          // Process the content of the complex type declaration
          // ------------------------------------------------------------------
          if (child==null) {
              //
              // EMPTY complexType with complexContent 
              //
              processComplexContent(typeNameIndex, child, typeInfo, null, false);
          }
          else {
              String childName = child.getLocalName();
              int index = -2;

              if (childName.equals(SchemaSymbols.ELT_SIMPLECONTENT)) {
                  //
                  // SIMPLE CONTENT element
                  //
                  traverseSimpleContentDecl(typeNameIndex, child, typeInfo);
                  if (XUtil.getNextSiblingElement(child) != null) 
                     throw new ComplexTypeRecoverableError(
                      "Invalid child following the simpleContent child in the complexType");
              }
              else if (childName.equals(SchemaSymbols.ELT_COMPLEXCONTENT)) {
                  //
                  // COMPLEX CONTENT element
                  //
                  traverseComplexContentDecl(typeNameIndex, child, typeInfo,   
                        mixed.equals(SchemaSymbols.ATTVAL_TRUE) ? true:false);
                  if (XUtil.getNextSiblingElement(child) != null) 
                     throw new ComplexTypeRecoverableError(
                      "Invalid child following the complexContent child in the complexType");
              }
              else {
                  // 
                  // We must have ....
                  // GROUP, ALL, SEQUENCE or CHOICE, followed by optional attributes
                  // Note that it's possible that only attributes are specified.
                  //
                  processComplexContent(typeNameIndex, child, typeInfo, null, 
                        mixed.equals(SchemaSymbols.ATTVAL_TRUE) ? true:false);
       
              }
          }
          typeInfo.blockSet = parseBlockSet(blockSet); 
          // make sure block's value was absent, #all or in {extension, restriction}
          if( (blockSet != null ) && !blockSet.equals("") &&
                (!blockSet.equals(SchemaSymbols.ATTVAL_POUNDALL) &&
                (((typeInfo.blockSet & SchemaSymbols.RESTRICTION) == 0) && 
                ((typeInfo.blockSet & SchemaSymbols.EXTENSION) == 0))))  
            throw new ComplexTypeRecoverableError("The values of the 'block' attribute of a complexType must be either #all or a list of 'restriction' and 'extension'; " + blockSet + " was found");

          typeInfo.finalSet = parseFinalSet(finalSet); 
          // make sure final's value was absent, #all or in {extension, restriction}
          if( (finalSet != null ) && !finalSet.equals("") &&
                (!finalSet.equals(SchemaSymbols.ATTVAL_POUNDALL) &&
                (((typeInfo.finalSet & SchemaSymbols.RESTRICTION) == 0) && 
                ((typeInfo.finalSet & SchemaSymbols.EXTENSION) == 0))))  
            throw new ComplexTypeRecoverableError("The values of the 'final' attribute of a complexType must be either #all or a list of 'restriction' and 'extension'; " + finalSet + " was found");

        }
        catch (ComplexTypeRecoverableError e) {
           String message = e.getMessage();
           handleComplexTypeError(message,typeNameIndex,typeInfo);
        }
                
            
        // ------------------------------------------------------------------
        // Finish the setup of the typeInfo and register the type
        // ------------------------------------------------------------------
        typeInfo.scopeDefined = scopeDefined; 
        if (isAbstract.equals(SchemaSymbols.ATTVAL_TRUE)) 
          typeInfo.setIsAbstractType();  
        if (!forwardRef)
          typeInfo.setDeclSeen();
        typeName = fTargetNSURIString + "," + typeName;
        typeInfo.typeName = new String(typeName);

        if ( DEBUGGING )
            System.out.println(">>>add complex Type to Registry: " + typeName +
                               " baseDTValidator=" + typeInfo.baseDataTypeValidator +
                               " baseCTInfo=" + typeInfo.baseComplexTypeInfo + 
                               " derivedBy=" + typeInfo.derivedBy + 
                             " contentType=" + typeInfo.contentType +
                               " contentSpecHandle=" + typeInfo.contentSpecHandle + 
                               " datatypeValidator=" + typeInfo.datatypeValidator);

        fComplexTypeRegistry.put(typeName,typeInfo);

        // ------------------------------------------------------------------
        // Before exiting, restore the scope, mainly for nested anonymous types
        // ------------------------------------------------------------------
        fCurrentScope = previousScope;
        fCurrentTypeNameStack.pop();
        checkRecursingComplexType();

        //set template element's typeInfo
        fSchemaGrammar.setElementComplexTypeInfo(typeInfo.templateElementIndex, typeInfo);

        typeNameIndex = fStringPool.addSymbol(typeName);
        return typeNameIndex;

    } // end traverseComplexTypeDecl

      
    /**
     * Traverse SimpleContent Declaration                          
     *  
     *       <simpleContent 
     *         id = ID 
     *         {any attributes with non-schema namespace...}>
     *
     *         Content: (annotation? , (restriction | extension)) 
     *       </simpleContent>
     *
     *       <restriction
     *         base = QNAME
     *         id = ID           
     *         {any attributes with non-schema namespace...}>
     *
     *         Content: (annotation?,(simpleType?, (minExclusive|minInclusive|maxExclusive
     *                    | maxInclusive | totalDigits | fractionDigits | length | minLength
     *                    | maxLength | encoding | period | duration | enumeration 
     *                    | pattern | whiteSpace)*) ? ,  
     *                    ((attribute | attributeGroup)* , anyAttribute?))
     *       </restriction>
     *
     *       <extension
     *         base = QNAME
     *         id = ID           
     *         {any attributes with non-schema namespace...}>
     *         Content: (annotation? , ((attribute | attributeGroup)* , anyAttribute?))
     *       </extension>
     *
     * @param typeNameIndex
     * @param simpleContentTypeDecl
     * @param typeInfo                   
     * @return 
     */
    
    private void traverseSimpleContentDecl(int typeNameIndex,
               Element simpleContentDecl, ComplexTypeInfo typeInfo) 
               throws Exception {

        
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(simpleContentDecl, scope);

        String typeName = fStringPool.toString(typeNameIndex);

        // -----------------------------------------------------------------------
        // Get attributes.   
        // -----------------------------------------------------------------------
        String simpleContentTypeId = simpleContentDecl.getAttribute(SchemaSymbols.ATTVAL_ID);

        // -----------------------------------------------------------------------
        // Set the content type to be simple, and initialize content spec handle
        // -----------------------------------------------------------------------
        typeInfo.contentType = XMLElementDecl.TYPE_SIMPLE;
        typeInfo.contentSpecHandle = -1;

        Element simpleContent = checkContent(simpleContentDecl,
                                     XUtil.getFirstChildElement(simpleContentDecl),false);
        
        // If there are no children, return
        if (simpleContent==null) {
          throw new ComplexTypeRecoverableError();
        }

        // General Attribute Checking
        attrValues = fGeneralAttrCheck.checkAttributes(simpleContent, scope);

        // -----------------------------------------------------------------------
        // The content should be either "restriction" or "extension"
        // -----------------------------------------------------------------------
        String simpleContentName = simpleContent.getLocalName();
        if (simpleContentName.equals(SchemaSymbols.ELT_RESTRICTION))
          typeInfo.derivedBy = SchemaSymbols.RESTRICTION;
        else if (simpleContentName.equals(SchemaSymbols.ELT_EXTENSION))
          typeInfo.derivedBy = SchemaSymbols.EXTENSION;
        else {
          
          throw new ComplexTypeRecoverableError(
                     "The content of the simpleContent element is invalid.  The " +
                     "content must be RESTRICTION or EXTENSION");
        }

        // -----------------------------------------------------------------------
        // Get the attributes of the restriction/extension element
        // -----------------------------------------------------------------------
        String base = simpleContent.getAttribute(SchemaSymbols.ATT_BASE);
        String typeId = simpleContent.getAttribute(SchemaSymbols.ATTVAL_ID);


        // -----------------------------------------------------------------------
        // Skip over any annotations in the restriction or extension elements
        // -----------------------------------------------------------------------
        Element content = checkContent(simpleContent,
                              XUtil.getFirstChildElement(simpleContent),true); 

        // -----------------------------------------------------------------------
        // Handle the base type name 
        // -----------------------------------------------------------------------
        if (base.length() == 0)  {
          throw new ComplexTypeRecoverableError(
                  "The BASE attribute must be specified for the " +
                  "RESTRICTION or EXTENSION element"); 
        }

        QName baseQName = parseBase(base);
        // check if we're extending a simpleType which has a "final" setting which precludes this
        Integer finalValue = (baseQName.uri == StringPool.EMPTY_STRING?
                ((Integer)fSimpleTypeFinalRegistry.get(fStringPool.toString(baseQName.localpart))):
                ((Integer)fSimpleTypeFinalRegistry.get(fStringPool.toString(baseQName.uri) + "," +fStringPool.toString(baseQName.localpart))));
        if(finalValue != null && 
                (finalValue.intValue() == typeInfo.derivedBy)) 
            throw new ComplexTypeRecoverableError(
                  "The simpleType " + base + " that " + typeName + " uses has a value of \"final\" which does not permit extension");

        processBaseTypeInfo(baseQName,typeInfo);
       
        // check that the base isn't a complex type with complex content
        if (typeInfo.baseComplexTypeInfo != null)  {
             if (typeInfo.baseComplexTypeInfo.contentType != XMLElementDecl.TYPE_SIMPLE) {
                 throw new ComplexTypeRecoverableError(
                 "The type '"+ base +"' specified as the " + 
                 "base in the simpleContent element must not have complexContent");
             }
        }
           
        // -----------------------------------------------------------------------
        // Process the content of the derivation
        // -----------------------------------------------------------------------
        Element attrNode = null;
        //
        // RESTRICTION
        //
        if (typeInfo.derivedBy==SchemaSymbols.RESTRICTION) {
            //
            //Schema Spec : Complex Type Definition Properties Correct : 2
            //
            if (typeInfo.baseDataTypeValidator != null) {
                throw new ComplexTypeRecoverableError(
                 "ct-props-correct.2: The type '" + base +"' is a simple type.  It cannot be used in a "+
                 "derivation by RESTRICTION for a complexType");
            }
            else {
               typeInfo.baseDataTypeValidator = typeInfo.baseComplexTypeInfo.datatypeValidator;
            }

            //
            // Check that the base's final set does not include RESTRICTION
            //
            if((typeInfo.baseComplexTypeInfo.finalSet & SchemaSymbols.RESTRICTION) != 0) {
               throw new ComplexTypeRecoverableError("Derivation by restriction is forbidden by either the base type " + base + " or the schema");
            }
               

            // -----------------------------------------------------------------------
            // There may be a simple type definition in the restriction element
            // The data type validator will be based on it, if specified          
            // -----------------------------------------------------------------------
            if (content.getLocalName().equals(SchemaSymbols.ELT_SIMPLETYPE )) { 
                int simpleTypeNameIndex = traverseSimpleTypeDecl(content); 
                if (simpleTypeNameIndex!=-1) {
                    DatatypeValidator dv=fDatatypeRegistry.getDatatypeValidator(
                       fStringPool.toString(simpleTypeNameIndex));
                    
                  //check that this datatype validator is validly derived from the base
                  //according to derivation-ok-restriction 5.1.1
                  if (!checkSimpleTypeDerivationOK(dv,typeInfo.baseDataTypeValidator)) {
                    throw new ComplexTypeRecoverableError("derivation-ok-restriction.5.1.1:  The content type is not a valid restriction of the content type of the base"); 
                  }
                  typeInfo.baseDataTypeValidator = dv;
                  content = XUtil.getNextSiblingElement(content);
                }
                else {
                  throw new ComplexTypeRecoverableError();
                }
            }

 
            //
            // Build up facet information
            //
            int numEnumerationLiterals = 0;
            int numFacets = 0;
            Hashtable facetData        = new Hashtable();
            Vector enumData            = new Vector();
            Element child;

             // General Attribute Checking
            scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
            Hashtable contentAttrs;

            //REVISIT: there is a better way to do this, 
            for (child = content;
                 child != null && (child.getLocalName().equals(SchemaSymbols.ELT_MINEXCLUSIVE) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_MININCLUSIVE) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_MAXEXCLUSIVE) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_MAXINCLUSIVE) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_TOTALDIGITS) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_FRACTIONDIGITS) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_LENGTH) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_MINLENGTH) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_MAXLENGTH) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_PERIOD) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_DURATION) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_ENUMERATION) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_PATTERN) ||
                           child.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION));
                 child = XUtil.getNextSiblingElement(child)) 
            {
                if ( child.getNodeType() == Node.ELEMENT_NODE ) {
                    Element facetElt = (Element) child;
                    // General Attribute Checking
                    contentAttrs = fGeneralAttrCheck.checkAttributes(facetElt, scope);
                    numFacets++;
                    if (facetElt.getLocalName().equals(SchemaSymbols.ELT_ENUMERATION)) {
                        numEnumerationLiterals++;
                        enumData.addElement(facetElt.getAttribute(SchemaSymbols.ATT_VALUE));
                        //Enumerations can have annotations ? ( 0 | 1 )
                        Element enumContent =  XUtil.getFirstChildElement( facetElt );
                        if( enumContent != null && 
                            enumContent.getLocalName().equals
                                  ( SchemaSymbols.ELT_ANNOTATION )){
                            traverseAnnotationDecl( child );   
                        }
                        // TO DO: if Jeff check in new changes to TraverseSimpleType, copy them over
                    } 
                    else {
                        facetData.put(facetElt.getLocalName(),
                              facetElt.getAttribute( SchemaSymbols.ATT_VALUE ));
                    }
                }
            } // end of for loop thru facets

            if (numEnumerationLiterals > 0) {
                facetData.put(SchemaSymbols.ELT_ENUMERATION, enumData);
            }

            //
            // If there were facets, create a new data type validator, otherwise 
            // the data type validator is from the base
            //
            if (numFacets > 0) {
              try{
                typeInfo.datatypeValidator = fDatatypeRegistry.createDatatypeValidator(
                                      typeName,
                                      typeInfo.baseDataTypeValidator, facetData, false);
              } catch (Exception e) {
                throw new ComplexTypeRecoverableError(e.getMessage());
              }

            }
            else
                typeInfo.datatypeValidator = 
                             typeInfo.baseDataTypeValidator;

            if (child != null) {
               //
               // Check that we have attributes
               //
               if (!isAttrOrAttrGroup(child)) {
                  throw new ComplexTypeRecoverableError(
                     "Invalid child in the RESTRICTION element of simpleContent");
               }
               else
                  attrNode = child;
            }
            
        } // end RESTRICTION

        //
        // EXTENSION
        //
        else {
            if (typeInfo.baseComplexTypeInfo != null) {
               typeInfo.baseDataTypeValidator = typeInfo.baseComplexTypeInfo.datatypeValidator;
              //
              // Check that the base's final set does not include EXTENSION
              //
              if((typeInfo.baseComplexTypeInfo.finalSet & 
                   SchemaSymbols.EXTENSION) != 0) {
                 throw new ComplexTypeRecoverableError("Derivation by extension is forbidden by either the base type " + base + " or the schema");
              }
            }

            typeInfo.datatypeValidator = typeInfo.baseDataTypeValidator;

            //
            // Look for attributes 
            //
            if (content != null)  {
               //
               // Check that we have attributes
               //
               if (!isAttrOrAttrGroup(content)) {
                   throw new ComplexTypeRecoverableError(
                             "Only annotations and attributes are allowed in the " +
                             "content of an EXTENSION element for a complexType with simpleContent"); 
               }
               else {
                   attrNode = content;
               }
            }
              
        }

        // -----------------------------------------------------------------------
        // add a template element to the grammar element decl pool for the type
        // -----------------------------------------------------------------------
        int templateElementNameIndex = fStringPool.addSymbol("$"+typeName);

        typeInfo.templateElementIndex = fSchemaGrammar.addElementDecl(
             new QName(-1, templateElementNameIndex,typeNameIndex,fTargetNSURI),
             (fTargetNSURI==StringPool.EMPTY_STRING) ? StringPool.EMPTY_STRING : fCurrentScope, typeInfo.scopeDefined,
             typeInfo.contentType, 
             typeInfo.contentSpecHandle, -1, typeInfo.datatypeValidator);
        typeInfo.attlistHead = fSchemaGrammar.getFirstAttributeDeclIndex(
                                typeInfo.templateElementIndex);

        // -----------------------------------------------------------------------
        // Process attributes                                          
        // -----------------------------------------------------------------------
        processAttributes(attrNode,baseQName,typeInfo);

        if (XUtil.getNextSiblingElement(simpleContent) != null) 
            throw new ComplexTypeRecoverableError(
               "Invalid child following the RESTRICTION or EXTENSION element in the " +
               "complex type definition");

    }  // end traverseSimpleContentDecl

    /**
     * Traverse complexContent Declaration                          
     *  
     *       <complexContent 
     *         id = ID 
     *         mixed = boolean 
     *         {any attributes with non-schema namespace...}>
     *
     *         Content: (annotation? , (restriction | extension)) 
     *       </complexContent>
     *
     *       <restriction
     *         base = QNAME
     *         id = ID           
     *         {any attributes with non-schema namespace...}>
     *
     *         Content: (annotation? , (group | all | choice | sequence)?, 
     *                  ((attribute | attributeGroup)* , anyAttribute?))
     *       </restriction>
     *
     *       <extension
     *         base = QNAME
     *         id = ID           
     *         {any attributes with non-schema namespace...}>
     *         Content: (annotation? , (group | all | choice | sequence)?, 
     *                  ((attribute | attributeGroup)* , anyAttribute?))
     *       </extension>
     *
     * @param typeNameIndex
     * @param simpleContentTypeDecl
     * @param typeInfo                   
     * @param mixedOnComplexTypeDecl                   
     * @return 
     */
    
    private void traverseComplexContentDecl(int typeNameIndex,  
               Element complexContentDecl, ComplexTypeInfo typeInfo, 
               boolean mixedOnComplexTypeDecl) throws Exception { 

         // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(complexContentDecl, scope);

        String typeName = fStringPool.toString(typeNameIndex);

        // -----------------------------------------------------------------------
        // Get the attributes                                                      
        // -----------------------------------------------------------------------
        String typeId = complexContentDecl.getAttribute(SchemaSymbols.ATTVAL_ID);
        String mixed = complexContentDecl.getAttribute(SchemaSymbols.ATT_MIXED);
        
        // -----------------------------------------------------------------------
        // Determine whether the content is mixed, or element-only
        // Setting here overrides any setting on the complex type decl
        // -----------------------------------------------------------------------
        boolean isMixed = mixedOnComplexTypeDecl;
        if (mixed.equals(SchemaSymbols.ATTVAL_TRUE))
           isMixed = true;
        else if (mixed.equals(SchemaSymbols.ATTVAL_FALSE))
           isMixed = false;
        
        // -----------------------------------------------------------------------
        // Since the type must have complex content, set the simple type validators 
        // to null
        // -----------------------------------------------------------------------
        typeInfo.datatypeValidator = null;
        typeInfo.baseDataTypeValidator = null;

        Element complexContent = checkContent(complexContentDecl,
                                 XUtil.getFirstChildElement(complexContentDecl),false);
        
        // If there are no children, return
        if (complexContent==null) {
           throw new ComplexTypeRecoverableError();
        }

        // -----------------------------------------------------------------------
        // The content should be either "restriction" or "extension"
        // -----------------------------------------------------------------------
        String complexContentName = complexContent.getLocalName();
        if (complexContentName.equals(SchemaSymbols.ELT_RESTRICTION))
          typeInfo.derivedBy = SchemaSymbols.RESTRICTION;
        else if (complexContentName.equals(SchemaSymbols.ELT_EXTENSION))
          typeInfo.derivedBy = SchemaSymbols.EXTENSION;
        else {
           throw new ComplexTypeRecoverableError(
                     "The content of the complexContent element is invalid. " +
                     "The content must be RESTRICTION or EXTENSION");
        }

        // Get the attributes of the restriction/extension element
        String base = complexContent.getAttribute(SchemaSymbols.ATT_BASE);
        String complexContentTypeId=complexContent.getAttribute(SchemaSymbols.ATTVAL_ID);


        // Skip over any annotations in the restriction or extension elements
        Element content = checkContent(complexContent,
                              XUtil.getFirstChildElement(complexContent),true); 

        // -----------------------------------------------------------------------
        // Handle the base type name 
        // -----------------------------------------------------------------------
        if (base.length() == 0)  {
           throw new ComplexTypeRecoverableError(
                  "The BASE attribute must be specified for the " +
                  "RESTRICTION or EXTENSION element"); 
        }

        QName baseQName = parseBase(base);

        // -------------------------------------------------------------
        // check if the base is "anyType"                       
        // -------------------------------------------------------------
        String baseTypeURI = fStringPool.toString(baseQName.uri);
        String baseLocalName = fStringPool.toString(baseQName.localpart);
        if (!(baseTypeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) &&
            baseLocalName.equals("anyType"))) {

            processBaseTypeInfo(baseQName,typeInfo);
       
            //Check that the base is a complex type                                  
            if (typeInfo.baseComplexTypeInfo == null)  {
                 throw new ComplexTypeRecoverableError(
                   "The base type specified in the complexContent element must be a complexType");
            }
        }

        // -----------------------------------------------------------------------
        // Process the elements that make up the content
        // -----------------------------------------------------------------------
        processComplexContent(typeNameIndex,content,typeInfo,baseQName,isMixed);

        if (XUtil.getNextSiblingElement(complexContent) != null) 
            throw new ComplexTypeRecoverableError(
               "Invalid child following the RESTRICTION or EXTENSION element in the " +
               "complex type definition");

    }  // end traverseComplexContentDecl


    /**
     * Handle complexType error                                            
     *  
     * @param message 
     * @param typeNameIndex 
     * @param typeInfo 
     * @return 
     */
    private void handleComplexTypeError(String message, int typeNameIndex,  
                                        ComplexTypeInfo typeInfo) throws Exception {

        String typeName = fStringPool.toString(typeNameIndex);
        if (message != null) {
          if (typeName.startsWith("#")) 
            reportGenericSchemaError("Anonymous complexType: " + message);
          else
            reportGenericSchemaError("ComplexType '" + typeName + "': " + message);
        }

        //
        //  Mock up the typeInfo structure so that there won't be problems during     
        //  validation      
        //
        typeInfo.contentType = XMLElementDecl.TYPE_ANY;  // this should match anything
        typeInfo.contentSpecHandle = -1;
        typeInfo.derivedBy = 0;
        typeInfo.datatypeValidator = null;
        typeInfo.attlistHead = -1;

        int templateElementNameIndex = fStringPool.addSymbol("$"+typeName);
        typeInfo.templateElementIndex = fSchemaGrammar.addElementDecl(
            new QName(-1, templateElementNameIndex,typeNameIndex,fTargetNSURI),
            (fTargetNSURI==StringPool.EMPTY_STRING) ? StringPool.EMPTY_STRING : fCurrentScope, typeInfo.scopeDefined,
            typeInfo.contentType, 
            typeInfo.contentSpecHandle, -1, typeInfo.datatypeValidator);
        return;
    }

    /**
     * Generate a name for an anonymous type                        
     *  
     * @param Element
     * @return String
     */
    private String genAnonTypeName(Element complexTypeDecl) throws Exception {

        String typeName; 

        // If the anonymous type is not nested within another type, we can 
        // simply assign the type a numbered name
        //
        if (fCurrentTypeNameStack.empty()) 
            typeName = "#"+fAnonTypeCount++;
          
        // Otherwise, we must generate a name that can be looked up later 
        // Do this by concatenating outer type names with the name of the parent
        // element
        else {
            String parentName = ((Element)complexTypeDecl.getParentNode()).getAttribute(
                                SchemaSymbols.ATT_NAME);
            typeName = parentName + "_AnonType";
            int index=fCurrentTypeNameStack.size() -1; 
	    for (int i = index; i > -1; i--) {
               String parentType = (String)fCurrentTypeNameStack.elementAt(i); 
               typeName = parentType + "_" + typeName;
               if (!(parentType.startsWith("#"))) 
                  break;
            }
            typeName = "#" + typeName;
        }
           
        return typeName;
    }
    /**
     * Parse base string                                            
     *  
     * @param base
     * @return QName
     */
    private QName parseBase(String base) throws Exception {

        String prefix = "";
        String localpart = base;
        int colonptr = base.indexOf(":");
        if ( colonptr > 0) {
            prefix = base.substring(0,colonptr);
            localpart = base.substring(colonptr+1);
        }

        int nameIndex = fStringPool.addSymbol(base);
        int prefixIndex = fStringPool.addSymbol(prefix);
        int localpartIndex = fStringPool.addSymbol(localpart);
        int URIindex = fStringPool.addSymbol(resolvePrefixToURI(prefix));
        return new QName(prefixIndex,localpartIndex,nameIndex,URIindex);
    }
    
    /**
     * Check if base is from another schema                         
     *  
     * @param baseName
     * @return boolean
     */
    private boolean baseFromAnotherSchema(QName baseName) throws Exception {

        String typeURI = fStringPool.toString(baseName.uri);
        if ( ! typeURI.equals(fTargetNSURIString) 
             && ! typeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) 
             && typeURI.length() != 0 ) 
             //REVISIT, !!!! a hack: for schema that has no 
             //target namespace, e.g. personal-schema.xml
          return true;
        else
          return false;
                                        
    }
    
    /**
     * Process "base" information for a complexType
     *  
     * @param baseTypeInfo        
     * @param baseName
     * @param typeInfo
     * @return 
     */
    
    private void processBaseTypeInfo(QName baseName, ComplexTypeInfo typeInfo) throws Exception {

        ComplexTypeInfo baseComplexTypeInfo = null;
        DatatypeValidator baseDTValidator = null;
        
        String typeURI = fStringPool.toString(baseName.uri);
        String localpart = fStringPool.toString(baseName.localpart);
        String base = fStringPool.toString(baseName.rawname);


        // -------------------------------------------------------------
        // check if the base type is from another schema 
        // -------------------------------------------------------------
        if (baseFromAnotherSchema(baseName)) {
            baseComplexTypeInfo = getTypeInfoFromNS(typeURI, localpart);
            if (baseComplexTypeInfo == null) {
                baseDTValidator = getTypeValidatorFromNS(typeURI, localpart);
                if (baseDTValidator == null) {
                    throw new ComplexTypeRecoverableError(
                       "Could not find base type " +localpart 
                       + " in schema " + typeURI);
                }
            }
        }

        // -------------------------------------------------------------
        // type must be from same schema
        // -------------------------------------------------------------
        else {
            String fullBaseName = typeURI+","+localpart;

            // assume the base is a complexType and try to locate the base type first
            baseComplexTypeInfo= (ComplexTypeInfo) fComplexTypeRegistry.get(fullBaseName);

            // if not found, 2 possibilities: 
            //           1: ComplexType in question has not been compiled yet;
            //           2: base is SimpleTYpe;
            if (baseComplexTypeInfo == null) {
                baseDTValidator = getDatatypeValidator(typeURI, localpart);

                if (baseDTValidator == null) {
                    int baseTypeSymbol;
                    Element baseTypeNode = getTopLevelComponentByName(
                                   SchemaSymbols.ELT_COMPLEXTYPE,localpart);
                    if (baseTypeNode != null) {
                        // Before traversing the base, make sure we're not already 
                        // doing so.. 
                        // ct-props-correct 3
                        if (fCurrentTypeNameStack.search((Object)localpart) > - 1) {
                            throw new ComplexTypeRecoverableError(
                                 "ct-props-correct.3:  Recursive type definition");
                        }
                        
                        baseTypeSymbol = traverseComplexTypeDecl( baseTypeNode, true );
                        baseComplexTypeInfo = (ComplexTypeInfo)
                        fComplexTypeRegistry.get(fStringPool.toString(baseTypeSymbol)); 
                        //REVISIT: should it be fullBaseName;
                    }
                    else {
                        baseTypeNode = getTopLevelComponentByName(
                                   SchemaSymbols.ELT_SIMPLETYPE, localpart);
                        if (baseTypeNode != null) {
                            baseTypeSymbol = traverseSimpleTypeDecl( baseTypeNode );
                            baseDTValidator = getDatatypeValidator(typeURI, localpart);
                            if (baseDTValidator == null)  {
                                        //TO DO: signal error here.
                            }
                        }
                        else {
                            throw new ComplexTypeRecoverableError(
                                 "Base type could not be found : " + base);
                        }
                    }
                }
            }
        } // end else (type must be from same schema)

        typeInfo.baseComplexTypeInfo = baseComplexTypeInfo;
        typeInfo.baseDataTypeValidator = baseDTValidator;


    } // end processBaseTypeInfo

    /**
     * Process content which is complex                             
     *  
     *     (group | all | choice | sequence) ? , 
     *     ((attribute | attributeGroup)* , anyAttribute?))
     *
     * @param typeNameIndex
     * @param complexContentChild
     * @param typeInfo                   
     * @return 
     */
    
    private void processComplexContent(int typeNameIndex,
               Element complexContentChild, ComplexTypeInfo typeInfo, QName baseName,
               boolean isMixed) throws Exception {

       Element attrNode = null;
       int index=-2;
       String typeName = fStringPool.toString(typeNameIndex);

       if (complexContentChild != null) {
           // -------------------------------------------------------------
           // GROUP, ALL, SEQUENCE or CHOICE, followed by attributes, if specified.
           // Note that it's possible that only attributes are specified.
           // -------------------------------------------------------------


          String childName = complexContentChild.getLocalName();

          if (childName.equals(SchemaSymbols.ELT_GROUP)) {
               int groupIndex = traverseGroupDecl(complexContentChild); 

               index = handleOccurrences(groupIndex,
                                complexContentChild,
                                hasAllContent(groupIndex) ? GROUP_REF_WITH_ALL :
                                                            NOT_ALL_CONTEXT);
               attrNode = XUtil.getNextSiblingElement(complexContentChild);
           }
           else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
               index = handleOccurrences(traverseSequence(complexContentChild), 
                                         complexContentChild);
               attrNode = XUtil.getNextSiblingElement(complexContentChild);
           }
           else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
               index = handleOccurrences(traverseChoice(complexContentChild), 
                                          complexContentChild);
               attrNode = XUtil.getNextSiblingElement(complexContentChild);
           }
           else if (childName.equals(SchemaSymbols.ELT_ALL)) {
               index = handleOccurrences(traverseAll(complexContentChild), 
                                         complexContentChild, PROCESSING_ALL);
               attrNode = XUtil.getNextSiblingElement(complexContentChild);
           }
           else if (isAttrOrAttrGroup(complexContentChild)) {
               // reset the contentType
               typeInfo.contentType = XMLElementDecl.TYPE_ANY;
               attrNode = complexContentChild;
           }
           else {
               throw new ComplexTypeRecoverableError(
                "Invalid child '"+ childName +"' in the complex type");               
           }
       }
     
       typeInfo.contentSpecHandle = index;

       // -----------------------------------------------------------------------
       // Merge in information from base, if it exists           
       // -----------------------------------------------------------------------
       if (typeInfo.baseComplexTypeInfo != null) {
           int baseContentSpecHandle = typeInfo.baseComplexTypeInfo.contentSpecHandle;

           //-------------------------------------------------------------
           // RESTRICTION
           //-------------------------------------------------------------
           if (typeInfo.derivedBy == SchemaSymbols.RESTRICTION) {
              // check to see if the baseType permits derivation by restriction
              if((typeInfo.baseComplexTypeInfo.finalSet & SchemaSymbols.RESTRICTION) != 0)
                    throw new ComplexTypeRecoverableError("Derivation by restriction is forbidden by either the base type " + fStringPool.toString(baseName.localpart) + " or the schema");
               
              // if the content is EMPTY, check that the base is correct 
              // according to derivation-ok-restriction 5.2
              if (typeInfo.contentSpecHandle==-2) {
                 if (!(typeInfo.baseComplexTypeInfo.contentType==XMLElementDecl.TYPE_EMPTY ||
                     particleEmptiable(baseContentSpecHandle))) {
                    throw new ComplexTypeRecoverableError("derivation-ok-restrictoin.5.2 Content type of complexType is EMPTY but base is not EMPTY or does not have a particle which is emptiable");
                 }
              }
                      
              //
              // The hairy derivation by restriction particle constraints
              // derivation-ok-restriction 5.3
              //
              else {
                
                try {
                  checkParticleDerivationOK(typeInfo.contentSpecHandle,fCurrentScope,
                       baseContentSpecHandle,typeInfo.baseComplexTypeInfo.scopeDefined,
                      typeInfo.baseComplexTypeInfo);
                }
                catch (ParticleRecoverableError e) {
                   String message = e.getMessage();
                   throw new ComplexTypeRecoverableError(message);
                }
              }
           }
           //-------------------------------------------------------------
           // EXTENSION
           //-------------------------------------------------------------
           else {
               // check to see if the baseType permits derivation by extension
               if((typeInfo.baseComplexTypeInfo.finalSet & SchemaSymbols.EXTENSION) != 0)
                    throw new ComplexTypeRecoverableError("cos-ct-extends.1.1: Derivation by extension is forbidden by either the base type " + fStringPool.toString(baseName.localpart) + " or the schema");
               
               //
               // Check if the contentType of the base is consistent with the new type
               // cos-ct-extends.1.4.2.2 
               if (typeInfo.baseComplexTypeInfo.contentType != XMLElementDecl.TYPE_EMPTY) {
                  if (((typeInfo.baseComplexTypeInfo.contentType == XMLElementDecl.TYPE_CHILDREN) && 
                       isMixed) ||
                      ((typeInfo.baseComplexTypeInfo.contentType == XMLElementDecl.TYPE_MIXED_COMPLEX) &&
                      !isMixed)) {
                    throw new ComplexTypeRecoverableError("cos-ct-extends.1.4.2.2.2.1: The content type of the base type " + 
                    fStringPool.toString(baseName.localpart) + " and derived type " + 
                    typeName + " must both be mixed or element-only");
                  }

               }

               //
               // Compose the final content model by concatenating the base and the 
               // current in sequence
               //
               if (baseFromAnotherSchema(baseName)) {
                   String baseSchemaURI = fStringPool.toString(baseName.uri);
                   SchemaGrammar aGrammar= (SchemaGrammar) fGrammarResolver.getGrammar(
                                    baseSchemaURI);
                   baseContentSpecHandle = importContentSpec(aGrammar, baseContentSpecHandle);
               }
               if (typeInfo.contentSpecHandle == -2) {
                   typeInfo.contentSpecHandle = baseContentSpecHandle;
               }
               else if (baseContentSpecHandle > -1) {
                   if (typeInfo.contentSpecHandle > -1 &&
                       (hasAllContent(typeInfo.contentSpecHandle) ||
                        hasAllContent(baseContentSpecHandle))) {
                       throw new ComplexTypeRecoverableError("cos-all-limited:  An \"all\" model group that is part of a complex type definition must constitute the entire {content type} of the definition.");
                   }

                   typeInfo.contentSpecHandle = 
                   fSchemaGrammar.addContentSpecNode(XMLContentSpec.CONTENTSPECNODE_SEQ, 
                                                     baseContentSpecHandle,
                                                     typeInfo.contentSpecHandle,
                                                     false);
               } 

               //
               // Check that there is a particle in the final content 
               // cos-ct-extends.1.4.2.1
               // LM - commented out until I get a clarification from HT
               //
               if (typeInfo.contentSpecHandle <0) {
                    throw new ComplexTypeRecoverableError("cos-ct-extends.1.4.2.1: The content of a type derived by EXTENSION must contain a particle");
               }
           }
       }
       else {
           typeInfo.derivedBy = 0;
       }

       // -------------------------------------------------------------
       // Set the content type                                                     
       // -------------------------------------------------------------
       if (isMixed) {

           // if there are no children, detect an error                   
           // See the definition of content type in Structures 3.4.1

           if (typeInfo.contentSpecHandle == -2) {

             throw new ComplexTypeRecoverableError("Type '" + typeName + "': The content of a mixed complexType must not be empty");
           }

           else
             typeInfo.contentType = XMLElementDecl.TYPE_MIXED_COMPLEX;
       }
       else if (typeInfo.contentSpecHandle == -2)
           typeInfo.contentType = XMLElementDecl.TYPE_EMPTY;
       else
           typeInfo.contentType = XMLElementDecl.TYPE_CHILDREN;


       // -------------------------------------------------------------
       // add a template element to the grammar element decl pool.
       // -------------------------------------------------------------
       int templateElementNameIndex = fStringPool.addSymbol("$"+typeName);

       typeInfo.templateElementIndex = fSchemaGrammar.addElementDecl(
            new QName(-1, templateElementNameIndex,typeNameIndex,fTargetNSURI),
            (fTargetNSURI==StringPool.EMPTY_STRING) ? StringPool.EMPTY_STRING : fCurrentScope, typeInfo.scopeDefined,
            typeInfo.contentType, 
            typeInfo.contentSpecHandle, -1, typeInfo.datatypeValidator);
       typeInfo.attlistHead = fSchemaGrammar.getFirstAttributeDeclIndex(
                               typeInfo.templateElementIndex);

       // -------------------------------------------------------------
       // Now, check attributes and handle
       // -------------------------------------------------------------
       if (attrNode !=null) {
           if (!isAttrOrAttrGroup(attrNode)) {
              throw new ComplexTypeRecoverableError(
                  "Invalid child "+ attrNode.getLocalName() + " in the complexType or complexContent");
           }
           else
              processAttributes(attrNode,baseName,typeInfo);
       }
       else if (typeInfo.baseComplexTypeInfo != null)
           processAttributes(null,baseName,typeInfo);


    } // end processComplexContent

    /**
     * Process attributes of a complex type                              
     *  
     * @param attrNode
     * @param typeInfo                   
     * @return 
     */
    
    private void processAttributes(Element attrNode, QName baseName,            
               ComplexTypeInfo typeInfo) throws Exception {


        XMLAttributeDecl attWildcard = null;
        Vector anyAttDecls = new Vector();

        Element child;
        for (child = attrNode;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {

            String childName = child.getLocalName();

            if (childName.equals(SchemaSymbols.ELT_ATTRIBUTE)) {
                traverseAttributeDecl(child, typeInfo, false);
            } 
            else if ( childName.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ) { 
                traverseAttributeGroupDecl(child,typeInfo,anyAttDecls);

            }
            else if ( childName.equals(SchemaSymbols.ELT_ANYATTRIBUTE) ) { 
                attWildcard = traverseAnyAttribute(child);
            }
            else {
                throw new ComplexTypeRecoverableError( "Invalid child among the children of the complexType definition");
            }
        }

        if (attWildcard != null) {
            XMLAttributeDecl fromGroup = null;
            final int count = anyAttDecls.size();
            if ( count > 0) {
                fromGroup = (XMLAttributeDecl) anyAttDecls.elementAt(0);
                for (int i=1; i<count; i++) {
                    fromGroup = AWildCardIntersection(
                                fromGroup,(XMLAttributeDecl)anyAttDecls.elementAt(i));
                }
            }
            if (fromGroup != null) {
                int saveProcessContents = attWildcard.defaultType;
                attWildcard = AWildCardIntersection(attWildcard, fromGroup);
                attWildcard.defaultType = saveProcessContents;
            }
        }
        else {
            //REVISIT: unclear in the Scheme Structures 4.3.3 what to do in this case
            if (anyAttDecls.size()>0) {
                attWildcard = (XMLAttributeDecl)anyAttDecls.elementAt(0);
            }
        }
        //
        // merge in base type's attribute decls
        //
        XMLAttributeDecl baseAttWildcard = null;
        ComplexTypeInfo baseTypeInfo = typeInfo.baseComplexTypeInfo;

        SchemaGrammar aGrammar=null;
        if (baseTypeInfo != null && baseTypeInfo.attlistHead > -1 ) {
            int attDefIndex = baseTypeInfo.attlistHead;
            aGrammar = fSchemaGrammar;
            String baseTypeSchemaURI = baseFromAnotherSchema(baseName)? 
                           fStringPool.toString(baseName.uri):null;
            if (baseTypeSchemaURI != null) {
                aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(baseTypeSchemaURI);
            }
            if (aGrammar == null) {
                //reportGenericSchemaError("In complexType "+typeName+", can NOT find the grammar "+
                  //                       "with targetNamespace" + baseTypeSchemaURI+
                    //                     "for the base type");
            }
            else
            while ( attDefIndex > -1 ) {
                fTempAttributeDecl.clear();
                aGrammar.getAttributeDecl(attDefIndex, fTempAttributeDecl);
                if (fTempAttributeDecl.type == XMLAttributeDecl.TYPE_ANY_ANY 
                    ||fTempAttributeDecl.type == XMLAttributeDecl.TYPE_ANY_LIST
                    ||fTempAttributeDecl.type == XMLAttributeDecl.TYPE_ANY_OTHER ) {
                    if (attWildcard == null) {
                        baseAttWildcard = fTempAttributeDecl;
                    }
                    attDefIndex = aGrammar.getNextAttributeDeclIndex(attDefIndex);
                    continue;
                }
                // if found a duplicate, if it is derived by restriction,
                // then skip the one from the base type
                
                int temp = fSchemaGrammar.getAttributeDeclIndex(typeInfo.templateElementIndex, fTempAttributeDecl.name);
                if ( temp > -1) {
                  if (typeInfo.derivedBy==SchemaSymbols.EXTENSION) {
                    reportGenericSchemaError("Attribute that appeared in the base should nnot appear in a derivation by extension");

                  }
                  else {
                    attDefIndex = fSchemaGrammar.getNextAttributeDeclIndex(attDefIndex);
                    continue;
                  }
                }

                fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                          fTempAttributeDecl.name, fTempAttributeDecl.type, 
                                          fTempAttributeDecl.enumeration, fTempAttributeDecl.defaultType, 
                                          fTempAttributeDecl.defaultValue, 
                                          fTempAttributeDecl.datatypeValidator,
                                          fTempAttributeDecl.list);
                attDefIndex = aGrammar.getNextAttributeDeclIndex(attDefIndex);
            }
        }

        // att wildcard will inserted after all attributes were processed
        if (attWildcard != null) {
            if (attWildcard.type != -1) {
                fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                          attWildcard.name, attWildcard.type, 
                                          attWildcard.enumeration, attWildcard.defaultType, 
                                          attWildcard.defaultValue, 
                                          attWildcard.datatypeValidator,
                                          attWildcard.list);
            }
            else {
                //REVISIT: unclear in Schema spec if should report error here.
                reportGenericSchemaError("The intensional intersection for {attribute wildcard}s must be expressible");
            }
        }
        else if (baseAttWildcard != null) {
            fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                      baseAttWildcard.name, baseAttWildcard.type, 
                                      baseAttWildcard.enumeration, baseAttWildcard.defaultType, 
                                      baseAttWildcard.defaultValue, 
                                      baseAttWildcard.datatypeValidator,
                                      baseAttWildcard.list);
        }

        typeInfo.attlistHead = fSchemaGrammar.getFirstAttributeDeclIndex
                                              (typeInfo.templateElementIndex);

        // For derivation by restriction, ensure that the resulting attribute list 
        // satisfies the constraints in derivation-ok-restriction 2,3,4
        if ((typeInfo.derivedBy==SchemaSymbols.RESTRICTION) && 
            (typeInfo.attlistHead>-1 && baseTypeInfo != null)) {
           checkAttributesDerivationOKRestriction(typeInfo.attlistHead,fSchemaGrammar,
               attWildcard,baseTypeInfo.attlistHead,aGrammar,baseAttWildcard);
        }
        
    } // end processAttributes

    // Check that the attributes of a type derived by restriction satisfy the 
    // constraints of derivation-ok-restriction

    private void checkAttributesDerivationOKRestriction(int dAttListHead, SchemaGrammar dGrammar, XMLAttributeDecl dAttWildCard, int bAttListHead, SchemaGrammar bGrammar, XMLAttributeDecl bAttWildCard) throws ComplexTypeRecoverableError {

       int attDefIndex = dAttListHead;

       if (bAttListHead < 0) {
          throw new ComplexTypeRecoverableError("derivation-ok-restriction.2:  Base type definition does not have any attributes"); 
       }
          
       // Loop thru the attributes
       while ( attDefIndex > -1 ) {
          fTempAttributeDecl.clear();
          dGrammar.getAttributeDecl(attDefIndex, fTempAttributeDecl);
          if (isAWildCard(fTempAttributeDecl)) {
             attDefIndex = dGrammar.getNextAttributeDeclIndex(attDefIndex);
             continue;
          }
          int bAttDefIndex = bGrammar.findAttributeDecl(bAttListHead, fTempAttributeDecl.name);
          if (bAttDefIndex > -1) {
             fTemp2AttributeDecl.clear();
             bGrammar.getAttributeDecl(bAttDefIndex, fTemp2AttributeDecl);

             // derivation-ok-restriction.  Constraint 2.1.1
             if ((fTemp2AttributeDecl.defaultType & 
                   XMLAttributeDecl.DEFAULT_TYPE_REQUIRED) > 0 &&
                (fTempAttributeDecl.defaultType & 
                   XMLAttributeDecl.DEFAULT_TYPE_REQUIRED) <= 0) {
               throw new ComplexTypeRecoverableError("derivation-ok-restriction.2.1.1:  Attribute '" + fStringPool.toString(fTempAttributeDecl.name.localpart) + "' in derivation has an inconsistent REQUIRED setting to that of attribute in base");
             }
             
             //
             // derivation-ok-restriction.  Constraint 2.1.2
             // 
             if (!(checkSimpleTypeDerivationOK(
                  fTempAttributeDecl.datatypeValidator,
                  fTemp2AttributeDecl.datatypeValidator))) {
               throw new ComplexTypeRecoverableError("derivation-ok-restriction.2.1.2:  Type of attribute '" + fStringPool.toString(fTempAttributeDecl.name.localpart) + "' in derivation must be a restriction of type of attribute in base");
             }

             //
             // derivation-ok-restriction.  Constraint 2.1.3
             // 
             if ((fTemp2AttributeDecl.defaultType & 
                   XMLAttributeDecl.DEFAULT_TYPE_FIXED) > 0) {

               if (!((fTempAttributeDecl.defaultType & 
                   XMLAttributeDecl.DEFAULT_TYPE_FIXED) > 0) ||
                   !fTempAttributeDecl.defaultValue.equals(fTemp2AttributeDecl.defaultValue)) {
                  
                  throw new ComplexTypeRecoverableError("derivation-ok-restriction.2.1.3:  Attribute '" + fStringPool.toString(fTempAttributeDecl.name.localpart) + "' is either not fixed, or is not fixed with the same value as the attribute in the base");
               }
             }
                    
          }
         else {
             //
             // derivation-ok-restriction.  Constraint 2.2
             // 
             if ((bAttWildCard==null) ||
              !AWildCardAllowsNameSpace(bAttWildCard, dGrammar.getTargetNamespaceURI())) {
                throw new ComplexTypeRecoverableError("derivation-ok-restriction.2.2:  Attribute '" + fStringPool.toString(fTempAttributeDecl.name.localpart) + "' has a target namespace which is not valid with respect to a base type definition's wildcard or, the base does not contain a wildcard");
               
             }
         }
         attDefIndex = dGrammar.getNextAttributeDeclIndex(attDefIndex);
             
       }

       // derivation-ok-restriction.  Constraint 4
       if (dAttWildCard!=null) {
          if (bAttWildCard==null) {
            throw new ComplexTypeRecoverableError("derivation-ok-restriction.4.1: An attribute wildcard is present in the derived type, but not the base"); 
          }
                
          if (!AWildCardSubset(dAttWildCard,bAttWildCard)) {
            throw new ComplexTypeRecoverableError("derivation-ok-restriction.4.2: The attribute wildcard in the derived type is not a valid subset of that in the base");

          }
       }
    }
        
    private boolean isAttrOrAttrGroup(Element e) 
    {
        String elementName = e.getLocalName();

        if (elementName.equals(SchemaSymbols.ELT_ATTRIBUTE) ||
            elementName.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ||
            elementName.equals(SchemaSymbols.ELT_ANYATTRIBUTE))
          return true;
        else
          return false;
    }

    private void checkRecursingComplexType() throws Exception {
        if ( fCurrentTypeNameStack.empty() ) {
            if (! fElementRecurseComplex.isEmpty() ) {
                Enumeration e = fElementRecurseComplex.keys();
                while( e.hasMoreElements() ) {
                    QName nameThenScope = (QName) e.nextElement();
                    String typeName = (String) fElementRecurseComplex.get(nameThenScope);

                    int eltUriIndex = nameThenScope.uri;
                    int eltNameIndex = nameThenScope.localpart;
                    int enclosingScope = nameThenScope.prefix;
                    ComplexTypeInfo typeInfo = 
                        (ComplexTypeInfo) fComplexTypeRegistry.get(fTargetNSURIString+","+typeName);
                    if (typeInfo==null) {
                        throw new Exception ( "Internal Error in void checkRecursingComplexType(). " );
                    }
                    else {
                        int elementIndex = fSchemaGrammar.addElementDecl(new QName(-1, eltNameIndex, eltNameIndex, eltUriIndex), 
                                                                         enclosingScope, typeInfo.scopeDefined, 
                                                                         typeInfo.contentType, 
                                                                         typeInfo.contentSpecHandle, 
                                                                         typeInfo.attlistHead, 
                                                                         typeInfo.datatypeValidator);
                        fSchemaGrammar.setElementComplexTypeInfo(elementIndex, typeInfo);
                    }

                }
                fElementRecurseComplex.clear();
            }
        }
    }

    // Check that the particle defined by the derived ct tree is a valid restriction of 
    // that specified by baseContentSpecIndex.   derivedScope and baseScope are the 
    // scopes of the particles, respectively.  bInfo is supplied when the base particle
    // is from a base type definition, and may be null - it helps determine other scopes
    // that elements should be looked up in. 

    private void checkParticleDerivationOK(int derivedContentSpecIndex, int derivedScope, int baseContentSpecIndex, int baseScope, ComplexTypeInfo bInfo) throws Exception {
        

       // Only do this if full checking is enabled
       if (!fFullConstraintChecking) 
           return;

       // Check for pointless occurrences of all, choice, sequence.  The result is the 
       // contentspec which is not pointless.   If the result is a non-pointless 
       // group, Vector is filled  in with the children of interest
       int csIndex1 = derivedContentSpecIndex;
       fSchemaGrammar.getContentSpec(csIndex1, tempContentSpec1);
       int csIndex2 = baseContentSpecIndex; 
       fSchemaGrammar.getContentSpec(csIndex2, tempContentSpec2);

       Vector tempVector1 = new Vector();
       Vector tempVector2 = new Vector();

       if (tempContentSpec1.type == XMLContentSpec.CONTENTSPECNODE_SEQ ||
           tempContentSpec1.type == XMLContentSpec.CONTENTSPECNODE_CHOICE || 
           tempContentSpec1.type == XMLContentSpec.CONTENTSPECNODE_ALL) {
         csIndex1 = checkForPointlessOccurrences(csIndex1,tempVector1);
       }
       if (tempContentSpec2.type == XMLContentSpec.CONTENTSPECNODE_SEQ ||
           tempContentSpec2.type == XMLContentSpec.CONTENTSPECNODE_CHOICE || 
           tempContentSpec2.type == XMLContentSpec.CONTENTSPECNODE_ALL) {
         csIndex2 = checkForPointlessOccurrences(csIndex2,tempVector2);
       }
         
       fSchemaGrammar.getContentSpec(csIndex1, tempContentSpec1);
       fSchemaGrammar.getContentSpec(csIndex2, tempContentSpec2);

       switch (tempContentSpec1.type & 0x0f) {
         case XMLContentSpec.CONTENTSPECNODE_LEAF: 
         {
            switch (tempContentSpec2.type & 0x0f) {

              // Elt:Elt NameAndTypeOK
              case XMLContentSpec.CONTENTSPECNODE_LEAF: 
              {
                 checkNameAndTypeOK(csIndex1, derivedScope, csIndex2, baseScope, bInfo);
                 return;
              }
              
              // Elt:Any NSCompat
              case XMLContentSpec.CONTENTSPECNODE_ANY:
              case XMLContentSpec.CONTENTSPECNODE_ANY_OTHER:
              case XMLContentSpec.CONTENTSPECNODE_ANY_NS:
              {
                 checkNSCompat(csIndex1, derivedScope, csIndex2);
                 return;
              }

              // Elt:All RecurseAsIfGroup 
              case XMLContentSpec.CONTENTSPECNODE_CHOICE:
              case XMLContentSpec.CONTENTSPECNODE_SEQ:
              case XMLContentSpec.CONTENTSPECNODE_ALL:
              {
                 checkRecurseAsIfGroup(csIndex1, derivedScope, csIndex2, tempVector2, baseScope, bInfo);
                 return;
              }

              default:
              { 
           	throw new ParticleRecoverableError("internal Xerces error"); 
              }
            }
         }

         case XMLContentSpec.CONTENTSPECNODE_ANY: 
         case XMLContentSpec.CONTENTSPECNODE_ANY_OTHER:
         case XMLContentSpec.CONTENTSPECNODE_ANY_NS:
         {
            switch (tempContentSpec2.type & 0x0f) {

              // Any:Any NSSubset
              case XMLContentSpec.CONTENTSPECNODE_ANY:
              case XMLContentSpec.CONTENTSPECNODE_ANY_OTHER:
              case XMLContentSpec.CONTENTSPECNODE_ANY_NS:
              {
                 checkNSSubset(csIndex1, csIndex2);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_CHOICE:
              case XMLContentSpec.CONTENTSPECNODE_SEQ:
              case XMLContentSpec.CONTENTSPECNODE_ALL:
              case XMLContentSpec.CONTENTSPECNODE_LEAF:
              {
                 throw new ParticleRecoverableError("cos-particle-restrict: Forbidden restriction: Any: Choice,Seq,All,Elt");
              }

              default:
              { 
           	throw new ParticleRecoverableError("internal Xerces error"); 
              }
            }
         }

         case XMLContentSpec.CONTENTSPECNODE_ALL: 
         {
            switch (tempContentSpec2.type & 0x0f) {

              // All:Any NSRecurseCheckCardinality
              case XMLContentSpec.CONTENTSPECNODE_ANY:
              case XMLContentSpec.CONTENTSPECNODE_ANY_OTHER:
              case XMLContentSpec.CONTENTSPECNODE_ANY_NS:
              {
                 checkNSRecurseCheckCardinality(csIndex1, tempVector1, derivedScope, csIndex2);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_ALL:
              {
                 checkRecurse(csIndex1, tempVector1, derivedScope, csIndex2, tempVector2, baseScope, bInfo);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_CHOICE:
              case XMLContentSpec.CONTENTSPECNODE_SEQ:
              case XMLContentSpec.CONTENTSPECNODE_LEAF:
              {
                 throw new ParticleRecoverableError("cos-particle-restrict: Forbidden restriction: All:Choice,Seq,Elt");
              }

              default:
              { 
           	throw new ParticleRecoverableError("internal Xerces error"); 
              }
            }
         }

         case XMLContentSpec.CONTENTSPECNODE_CHOICE: 
         {
            switch (tempContentSpec2.type & 0x0f) {

              // Choice:Any NSRecurseCheckCardinality
              case XMLContentSpec.CONTENTSPECNODE_ANY:
              case XMLContentSpec.CONTENTSPECNODE_ANY_OTHER:
              case XMLContentSpec.CONTENTSPECNODE_ANY_NS:
              {
                 checkNSRecurseCheckCardinality(csIndex1, tempVector1, derivedScope, csIndex2);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_CHOICE:
              {
                 checkRecurseLax(csIndex1, tempVector1, derivedScope, csIndex2, tempVector2, baseScope, bInfo);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_ALL:
              case XMLContentSpec.CONTENTSPECNODE_SEQ:
              case XMLContentSpec.CONTENTSPECNODE_LEAF:
              {
                 throw new ParticleRecoverableError("cos-particle-restrict: Forbidden restriction: Choice:All,Seq,Leaf");
              }

              default:
              { 
           	throw new ParticleRecoverableError("internal Xerces error"); 
              }
            }
         }


         case XMLContentSpec.CONTENTSPECNODE_SEQ: 
         {
            switch (tempContentSpec2.type & 0x0f) {

              // Choice:Any NSRecurseCheckCardinality
              case XMLContentSpec.CONTENTSPECNODE_ANY:
              case XMLContentSpec.CONTENTSPECNODE_ANY_OTHER:
              case XMLContentSpec.CONTENTSPECNODE_ANY_NS:
              {
                 checkNSRecurseCheckCardinality(csIndex1, tempVector1, derivedScope, csIndex2);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_ALL:
              {
                 checkRecurseUnordered(csIndex1, tempVector1, derivedScope, csIndex2, tempVector2, baseScope, bInfo);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_SEQ:
              {
                 checkRecurse(csIndex1, tempVector1, derivedScope, csIndex2, tempVector2, baseScope, bInfo);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_CHOICE:
              {
                 checkMapAndSum(csIndex1, tempVector1, derivedScope, csIndex2, tempVector2, baseScope, bInfo);
                 return;
              }

              case XMLContentSpec.CONTENTSPECNODE_LEAF:
              {
                throw new ParticleRecoverableError("cos-particle-restrict: Forbidden restriction: Seq:Elt");
              }

              default:
              { 
           	throw new ParticleRecoverableError("internal Xerces error"); 
              }
            }
         }

       }

    }

    private int checkForPointlessOccurrences(int csIndex, Vector tempVector)  { 

       // Note:  instead of using a Vector, we should use a growable array of int. 
       // To be cleaned up in release 1.4.1. (LM)

       fSchemaGrammar.getContentSpec(csIndex, tempContentSpec1);
       
       if (tempContentSpec1.otherValue == -2) {
         gatherChildren(tempContentSpec1.type,tempContentSpec1.value,tempVector);
         if (tempVector.size() == 1) {
           Integer returnVal = (Integer)(tempVector.elementAt(0));
           return returnVal.intValue();
         }
       }

       int type = tempContentSpec1.type;
       int value = tempContentSpec1.value;
       int otherValue = tempContentSpec1.otherValue;

       gatherChildren(type,value, tempVector);
       gatherChildren(type,otherValue, tempVector);

       
       return csIndex;
    }


    private void gatherChildren(int parentType, int csIndex, Vector tempVector) {
       
       fSchemaGrammar.getContentSpec(csIndex, tempContentSpec1);
       int min = fSchemaGrammar.getContentSpecMinOccurs(csIndex);
       int max = fSchemaGrammar.getContentSpecMaxOccurs(csIndex);
       int left = tempContentSpec1.value;
       int right = tempContentSpec1.otherValue;
       int type = tempContentSpec1.type;

       if (type == XMLContentSpec.CONTENTSPECNODE_LEAF ||
           (type & 0x0f) == XMLContentSpec.CONTENTSPECNODE_ANY ||
           (type & 0x0f) == XMLContentSpec.CONTENTSPECNODE_ANY_NS  ||
           (type & 0x0f) == XMLContentSpec.CONTENTSPECNODE_ANY_OTHER ) {
          tempVector.addElement(new Integer(csIndex));
       }
       else if (! (min==1 && max==1)) {
          tempVector.addElement(new Integer(csIndex)); 
       }
       else if (right == -2) {
          gatherChildren(type,left,tempVector);
       }
       else if (parentType == type) {
          gatherChildren(type,left,tempVector);
          gatherChildren(type,right,tempVector);
       }
       else {
          tempVector.addElement(new Integer(csIndex));
       }
          
    }
       

    private void checkNameAndTypeOK(int csIndex1, int derivedScope, int csIndex2, int baseScope, ComplexTypeInfo bInfo) throws Exception {

      fSchemaGrammar.getContentSpec(csIndex1, tempContentSpec1);
      fSchemaGrammar.getContentSpec(csIndex2, tempContentSpec2);
 
    
      int localpart1 = tempContentSpec1.value;
      int uri1 = tempContentSpec1.otherValue;
      int localpart2 = tempContentSpec2.value;
      int uri2 = tempContentSpec2.otherValue;

      int min1 = fSchemaGrammar.getContentSpecMinOccurs(csIndex1);
      int max1 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex1);
      int min2 = fSchemaGrammar.getContentSpecMinOccurs(csIndex2);
      int max2 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex2);

      //start the checking...
      if (!(localpart1==localpart2 && uri1==uri2)) {

        // we have non-matching names.   Check substitution groups.
        if (fSComp == null) 
           fSComp = new SubstitutionGroupComparator(fGrammarResolver,fStringPool,fErrorReporter);
        if (!checkSubstitutionGroups(localpart1,uri1,localpart2,uri2)) 
          throw new ParticleRecoverableError("rcase-nameAndTypeOK.1:  Element name/uri in restriction does not match that of corresponding base element");
      }
 
      if (!checkOccurrenceRange(min1,max1,min2,max2)) {
        throw new ParticleRecoverableError("rcase-nameAndTypeOK.3:  Element occurrence range not a restriction of base element's range: element is " +  fStringPool.toString(localpart1));
      }

      SchemaGrammar aGrammar = fSchemaGrammar;

      // get the element decl indices for the remainder...
      String schemaURI = fStringPool.toString(uri1);
      if ( !schemaURI.equals(fTargetNSURIString)
            && schemaURI.length() != 0 ) 
         aGrammar= (SchemaGrammar) fGrammarResolver.getGrammar(schemaURI);

      int eltndx1 =  findElement(derivedScope, localpart1, aGrammar, null);
      if (eltndx1 < 0) 
         return;
         
      int eltndx2 = findElement(baseScope, localpart2, aGrammar, bInfo);
      if (eltndx2 < 0) 
         return;
       
      int miscFlags1 = ((SchemaGrammar) aGrammar).getElementDeclMiscFlags(eltndx1);
      int miscFlags2 = ((SchemaGrammar) aGrammar).getElementDeclMiscFlags(eltndx2);
      boolean element1IsNillable = (miscFlags1 & SchemaSymbols.NILLABLE) !=0;
      boolean element2IsNillable = (miscFlags2 & SchemaSymbols.NILLABLE) !=0;
      boolean element2IsFixed = (miscFlags2 & SchemaSymbols.FIXED) !=0;
      boolean element1IsFixed = (miscFlags1 & SchemaSymbols.FIXED) !=0;
      String element1Value = aGrammar.getElementDefaultValue(eltndx1);
      String element2Value = aGrammar.getElementDefaultValue(eltndx2);
      
      if (! (element2IsNillable || !element1IsNillable)) {
        throw new ParticleRecoverableError("rcase-nameAndTypeOK.2:  Element " +fStringPool.toString(localpart1) + " is nillable in the restriction but not the base");
      }

      if (! (element2Value == null || !element2IsFixed ||  
             (element1IsFixed && element1Value.equals(element2Value)))) {
        throw new ParticleRecoverableError("rcase-nameAndTypeOK.4:  Element " +fStringPool.toString(localpart1) + " is either not fixed, or is not fixed with the same value as in the base");
      }

      // check disallowed substitutions 
      int blockSet1 = ((SchemaGrammar) aGrammar).getElementDeclBlockSet(eltndx1);
      int blockSet2 = ((SchemaGrammar) aGrammar).getElementDeclBlockSet(eltndx2);
      if (((blockSet1 & blockSet2)!=blockSet2) || 
            (blockSet1==0 && blockSet2!=0))
        throw new ParticleRecoverableError("rcase-nameAndTypeOK.6:  Element " +fStringPool.toString(localpart1) + "'s disallowed subsitutions are not a superset of those of the base element's");


      // Need element decls for the remainder of the checks
      aGrammar.getElementDecl(eltndx1, fTempElementDecl); 
      aGrammar.getElementDecl(eltndx2, fTempElementDecl2); 
         
      // check identity constraints 
      checkIDConstraintRestriction(fTempElementDecl, fTempElementDecl2, aGrammar, localpart1, localpart2);

      // check that the derived element's type is derived from the base's. - TO BE DONE
      checkTypesOK(fTempElementDecl,fTempElementDecl2,eltndx1,eltndx2,aGrammar,fStringPool.toString(localpart1));
  
    }

    private void checkTypesOK(XMLElementDecl derived, XMLElementDecl base, int dndx, int bndx, SchemaGrammar aGrammar, String elementName) throws Exception {
      
      ComplexTypeInfo tempType=((SchemaGrammar)aGrammar).getElementComplexTypeInfo(dndx); 
      if (derived.type == XMLElementDecl.TYPE_SIMPLE ) {
 
        if (base.type != XMLElementDecl.TYPE_SIMPLE) 
            throw new ParticleRecoverableError("rcase-nameAndTypeOK.6:  Derived element " + elementName + " has a type that does not derive from that of the base");

        if (tempType == null) {
         if (!(checkSimpleTypeDerivationOK(derived.datatypeValidator,
               base.datatypeValidator))) 
              throw new ParticleRecoverableError("rcase-nameAndTypeOK.6:  Derived element " + elementName + " has a type that does not derives from that of the base");
         return;
        }
      }
      
      ComplexTypeInfo bType=((SchemaGrammar)aGrammar).getElementComplexTypeInfo(bndx); 
      for(; tempType != null; tempType = tempType.baseComplexTypeInfo) {
        if (tempType.derivedBy != SchemaSymbols.RESTRICTION) {
          throw new ParticleRecoverableError("rcase-nameAndTypeOK.6:  Derived element " + elementName + " has a type that does not derives from that of the base");
        }
        if (tempType.typeName.equals(bType.typeName))
          break; 
      }
      if(tempType == null) {
        throw new ParticleRecoverableError("rcase-nameAndTypeOK.6:  Derived element " + elementName + " has a type that does not derives from that of the base");
      }
    }

    private void checkIDConstraintRestriction(XMLElementDecl derivedElemDecl, XMLElementDecl baseElemDecl, 
                SchemaGrammar grammar, int derivedElemName, int baseElemName) throws Exception {
        // this method throws no errors if the ID constraints on
        // the derived element are a logical subset of those on the
        // base element--that is, those that are present are
        // identical to ones in the base element.  
        Vector derivedUnique = derivedElemDecl.unique;
        Vector baseUnique = baseElemDecl.unique;
        if(derivedUnique.size() > baseUnique.size()) {
            throw new ParticleRecoverableError("rcase-nameAndTypeOK.5:  derived element " + 
                    fStringPool.toString(derivedElemName) + 
                    " has fewer <unique> Identity Constraints than the base element"+
                    fStringPool.toString(baseElemName));
        } else {
            boolean found = true;
            for(int i=0; i<derivedUnique.size() && found; i++) {
                Unique id = (Unique)derivedUnique.elementAt(i);
                found = false;
                for(int j=0; j<baseUnique.size(); j++) {
                    if(id.equals((Unique)baseUnique.elementAt(j))) {
                        found = true;
                        break;
                    }
                }
            }
            if(!found) {
                throw new ParticleRecoverableError("rcase-nameAndTypeOK.5:  derived element " + 
                    fStringPool.toString(derivedElemName) + 
                    " has a <unique> Identity Constraint that does not appear on the base element"+
                    fStringPool.toString(baseElemName));
            }
        }

        Vector derivedKey = derivedElemDecl.key;
        Vector baseKey = baseElemDecl.key;
        if(derivedKey.size() > baseKey.size()) {
            throw new ParticleRecoverableError("rcase-nameAndTypeOK.5:  derived element " + 
                    fStringPool.toString(derivedElemName) + 
                    " has fewer <key> Identity Constraints than the base element"+
                    fStringPool.toString(baseElemName));
        } else {
            boolean found = true;
            for(int i=0; i<derivedKey.size() && found; i++) {
                Key id = (Key)derivedKey.elementAt(i);
                found = false;
                for(int j=0; j<baseKey.size(); j++) {
                    if(id.equals((Key)baseKey.elementAt(j))) {
                        found = true;
                        break;
                    }
                }
            }
            if(!found) {
                throw new ParticleRecoverableError("rcase-nameAndTypeOK.5:  derived element " + 
                    fStringPool.toString(derivedElemName) + 
                    " has a <key> Identity Constraint that does not appear on the base element"+
                    fStringPool.toString(baseElemName));
            }
        }

        Vector derivedKeyRef = derivedElemDecl.keyRef;
        Vector baseKeyRef = baseElemDecl.keyRef;
        if(derivedKeyRef.size() > baseKeyRef.size()) {
            throw new ParticleRecoverableError("rcase-nameAndTypeOK.5:  derived element " + 
                    fStringPool.toString(derivedElemName) + 
                    " has fewer <keyref> Identity Constraints than the base element"+
                    fStringPool.toString(baseElemName));
        } else {
            boolean found = true;
            for(int i=0; i<derivedKeyRef.size() && found; i++) {
                KeyRef id = (KeyRef)derivedKeyRef.elementAt(i);
                found = false;
                for(int j=0; j<baseKeyRef.size(); j++) {
                    if(id.equals((KeyRef)baseKeyRef.elementAt(j))) {
                        found = true;
                        break;
                    }
                }
            }
            if(!found) {
                throw new ParticleRecoverableError("rcase-nameAndTypeOK.5:  derived element " + 
                    fStringPool.toString(derivedElemName) + 
                    " has a <keyref> Identity Constraint that does not appear on the base element"+
                    fStringPool.toString(baseElemName));
            }
        }
    } // checkIDConstraintRestriction

    private boolean checkSubstitutionGroups(int local1, int uri1, int local2, int uri2) 
throws Exception {

       // check if either name is in the other's substitution group
       QName name1 = new QName(-1,local1,local1,uri1);
       QName name2 = new QName(-1,local2,local2,uri2);

       if (fSComp.isEquivalentTo(name1,name2) ||
           fSComp.isEquivalentTo(name2,name1)) 
         return true;
       else
         return false;

    }
    private boolean checkOccurrenceRange(int min1, int max1, int min2, int max2) {

      if ((min1 >= min2) && 
          ((max2==SchemaSymbols.OCCURRENCE_UNBOUNDED) || (max1!=SchemaSymbols.OCCURRENCE_UNBOUNDED && max1<=max2))) 
        return true;
      else
        return false;
    }

    private int findElement(int scope, int nameIndex, SchemaGrammar gr, ComplexTypeInfo bInfo) {

      // check for element at given scope first
      int elementDeclIndex = gr.getElementDeclIndex(nameIndex,scope);

      // if not found, check at global scope
      if (elementDeclIndex == -1) {
         elementDeclIndex = gr.getElementDeclIndex(nameIndex, -1);
        
         // if still not found, and base is specified, look it up there
         if (elementDeclIndex == -1 && bInfo != null) {
            ComplexTypeInfo baseInfo = bInfo;
            while (baseInfo != null) {
                elementDeclIndex = gr.getElementDeclIndex(nameIndex,baseInfo.scopeDefined);
                if (elementDeclIndex > -1) 
                   break;
                baseInfo = baseInfo.baseComplexTypeInfo;
            }
         }

      }
      return elementDeclIndex;
    }

    private void checkNSCompat(int csIndex1, int derivedScope, int csIndex2) throws Exception { 

      int min1 = fSchemaGrammar.getContentSpecMinOccurs(csIndex1);
      int max1 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex1);
      int min2 = fSchemaGrammar.getContentSpecMinOccurs(csIndex2);
      int max2 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex2);

      // check Occurrence ranges
      if (!checkOccurrenceRange(min1,max1,min2,max2)) {
        throw new ParticleRecoverableError("rcase-NSCompat.2:  Element occurrence range not a restriction of base any element's range");
      }

      
      fSchemaGrammar.getContentSpec(csIndex1, tempContentSpec1);
      int uri = tempContentSpec1.otherValue;

      // check wildcard subset
      if (!wildcardEltAllowsNamespace(csIndex2, uri)) 
        throw new ParticleRecoverableError("rcase-NSCompat.1:  Element's namespace not allowed by wildcard in base");

    }

    private boolean wildcardEltAllowsNamespace(int wildcardNode, int uriIndex) {

      fSchemaGrammar.getContentSpec(wildcardNode, tempContentSpec1);
      if ((tempContentSpec1.type & 0x0f) == XMLContentSpec.CONTENTSPECNODE_ANY) 
        return true;

      if ((tempContentSpec1.type & 0x0f)==XMLContentSpec.CONTENTSPECNODE_ANY_NS) {
        if (uriIndex == tempContentSpec1.otherValue) 
           return true; 
      }
      else { // must be ANY_OTHER 
        if (uriIndex != tempContentSpec1.otherValue && uriIndex != StringPool.EMPTY_STRING)
            return true;
      }

      return false;
    }
       

    private void checkNSSubset(int csIndex1, int csIndex2) throws Exception {
      int min1 = fSchemaGrammar.getContentSpecMinOccurs(csIndex1);
      int max1 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex1);
      int min2 = fSchemaGrammar.getContentSpecMinOccurs(csIndex2);
      int max2 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex2);

      // check Occurrence ranges
      if (!checkOccurrenceRange(min1,max1,min2,max2)) {
        throw new ParticleRecoverableError("rcase-NSSubset.2:  Wildcard's occurrence range not a restriction of base wildcard's range");
      }

      if (!wildcardEltSubset(csIndex1, csIndex2)) 
         throw new ParticleRecoverableError("rcase-NSSubset.1:  Wildcard is not a subset of corresponding wildcard in base");


    }

    private boolean wildcardEltSubset(int wildcardNode, int wildcardBaseNode) {

      fSchemaGrammar.getContentSpec(wildcardNode, tempContentSpec1);
      fSchemaGrammar.getContentSpec(wildcardBaseNode, tempContentSpec2);

      if ((tempContentSpec2.type & 0x0f) == XMLContentSpec.CONTENTSPECNODE_ANY) 
        return true;

      if ((tempContentSpec1.type & 0x0f)==XMLContentSpec.CONTENTSPECNODE_ANY_OTHER) {
        if ((tempContentSpec2.type & 0x0f)==XMLContentSpec.CONTENTSPECNODE_ANY_OTHER &&
            tempContentSpec1.otherValue == tempContentSpec2.otherValue) 
           return true; 
      }

      if ((tempContentSpec1.type & 0x0f)==XMLContentSpec.CONTENTSPECNODE_ANY_NS) {
        if ((tempContentSpec2.type & 0x0f)==XMLContentSpec.CONTENTSPECNODE_ANY_NS &&
            tempContentSpec1.otherValue == tempContentSpec2.otherValue) 
           return true; 

        if ((tempContentSpec2.type & 0x0f)==XMLContentSpec.CONTENTSPECNODE_ANY_OTHER &&
            tempContentSpec1.otherValue != tempContentSpec2.otherValue) 
           return true; 

      }

      return false;
    }

    private void checkRecurseAsIfGroup(int csIndex1, int derivedScope, int csIndex2, Vector tempVector2, int baseScope, ComplexTypeInfo bInfo) throws Exception {

      fSchemaGrammar.getContentSpec(csIndex2, tempContentSpec2);
     
       //  Treat the element as if it were in a group of the same type as csindex2
      int indexOfGrp=fSchemaGrammar.addContentSpecNode(tempContentSpec2.type, 
                             csIndex1,-2, false);
      Vector tmpVector = new Vector();
      tmpVector.addElement(new Integer(csIndex1));

      
      if (tempContentSpec2.type == XMLContentSpec.CONTENTSPECNODE_ALL || 
          tempContentSpec2.type == XMLContentSpec.CONTENTSPECNODE_SEQ) 
         checkRecurse(indexOfGrp, tmpVector, derivedScope, csIndex2, 
                      tempVector2, baseScope, bInfo);
      else
         checkRecurseLax(indexOfGrp, tmpVector, derivedScope, csIndex2, 
                         tempVector2, baseScope, bInfo);
       
      tmpVector = null;
    }

    private void checkNSRecurseCheckCardinality(int csIndex1, Vector tempVector1, int derivedScope, int csIndex2) throws Exception {

      // Implement total range check 
      int min1 = minEffectiveTotalRange(csIndex1);
      int max1 = maxEffectiveTotalRange(csIndex1);

      int min2 = fSchemaGrammar.getContentSpecMinOccurs(csIndex2);
      int max2 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex2);

      // check Occurrence ranges
      if (!checkOccurrenceRange(min1,max1,min2,max2)) {
        throw new ParticleRecoverableError("rcase-NSSubset.2:  Wildcard's occurrence range not a restriction of base wildcard's range");
      }

      if (!wildcardEltSubset(csIndex1, csIndex2)) 
         throw new ParticleRecoverableError("rcase-NSSubset.1:  Wildcard is not a subset of corresponding wildcard in base");
      // Check that each member of the group is a valid restriction of the wildcard
      int count = tempVector1.size();
      for (int i = 0; i < count; i++) {
         Integer particle1 = (Integer)tempVector1.elementAt(i);
         checkParticleDerivationOK(particle1.intValue(),derivedScope,csIndex2,-1,null);
      }
      
    }

    private void checkRecurse(int csIndex1, Vector tempVector1, int derivedScope, int csIndex2, Vector tempVector2, int baseScope, ComplexTypeInfo bInfo) throws Exception {
 
      int min1 = fSchemaGrammar.getContentSpecMinOccurs(csIndex1);
      int max1 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex1);
      int min2 = fSchemaGrammar.getContentSpecMinOccurs(csIndex2);
      int max2 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex2);

      // check Occurrence ranges
      if (!checkOccurrenceRange(min1,max1,min2,max2)) {
        throw new ParticleRecoverableError("rcase-Recurse.1:  Occurrence range of group is not a valid restriction of occurence range of base group");
      }

      int count1= tempVector1.size();
      int count2= tempVector2.size();
 
      int current = 0; 
      label: for (int i = 0; i<count1; i++) {

        Integer particle1 = (Integer)tempVector1.elementAt(i);
        for (int j = current; j<count2; j++) {
           Integer particle2 = (Integer)tempVector2.elementAt(j);
           current +=1;
           try {
             checkParticleDerivationOK(particle1.intValue(),derivedScope, 
                particle2.intValue(), baseScope, bInfo);
             continue label;
           }
           catch (ParticleRecoverableError e) {
             if (!particleEmptiable(particle2.intValue()))
                throw new ParticleRecoverableError("rcase-Recurse.2:  There is not a complete functional mapping between the particles");
           }
        }
        throw new ParticleRecoverableError("rcase-Recurse.2:  There is not a complete functional mapping between the particles");
      }
      
      // Now, see if there are some elements in the base we didn't match up
      for (int j=current; j < count2; j++) {
        Integer particle2 = (Integer)tempVector2.elementAt(j);
        if (!particleEmptiable(particle2.intValue())) {
          throw new ParticleRecoverableError("rcase-Recurse.2:  There is not a complete functional mapping between the particles");
        }
      }
      
    }

    private void checkRecurseUnordered(int csIndex1, Vector tempVector1, int derivedScope, int csIndex2, Vector tempVector2, int baseScope, ComplexTypeInfo bInfo) throws Exception {
      int min1 = fSchemaGrammar.getContentSpecMinOccurs(csIndex1);
      int max1 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex1);
      int min2 = fSchemaGrammar.getContentSpecMinOccurs(csIndex2);
      int max2 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex2);

      // check Occurrence ranges
      if (!checkOccurrenceRange(min1,max1,min2,max2)) {
        throw new ParticleRecoverableError("rcase-RecurseUnordered.1:  Occurrence range of group is not a valid restriction of occurence range of base group");
      }

      int count1= tempVector1.size();
      int count2 = tempVector2.size();

      boolean foundIt[] = new boolean[count2];

      label: for (int i = 0; i<count1; i++) {

        Integer particle1 = (Integer)tempVector1.elementAt(i);
        for (int j = 0; j<count2; j++) {
           Integer particle2 = (Integer)tempVector2.elementAt(j);
           try {
             checkParticleDerivationOK(particle1.intValue(),derivedScope, 
                particle2.intValue(), baseScope, bInfo);
             if (foundIt[j]) 
	        throw new ParticleRecoverableError("rcase-RecurseUnordered.2:  There is not a complete functional mapping between the particles");
             else
                foundIt[j]=true;
             
             continue label;
           }
           catch (ParticleRecoverableError e) {
           }
        }
        // didn't find a match.  Detect an error
	throw new ParticleRecoverableError("rcase-RecurseUnordered.2:  There is not a complete functional mapping between the particles");
      }

    }

    private void checkRecurseLax(int csIndex1, Vector tempVector1, int derivedScope, int csIndex2, Vector tempVector2, int baseScope, ComplexTypeInfo bInfo) throws Exception {

      int min1 = fSchemaGrammar.getContentSpecMinOccurs(csIndex1);
      int max1 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex1);
      int min2 = fSchemaGrammar.getContentSpecMinOccurs(csIndex2);
      int max2 = fSchemaGrammar.getContentSpecMaxOccurs(csIndex2);

      // check Occurrence ranges
      if (!checkOccurrenceRange(min1,max1,min2,max2)) {
        throw new ParticleRecoverableError("rcase-RecurseLax.1:  Occurrence range of group is not a valid restriction of occurence range of base group");
      }

      int count1= tempVector1.size();
      int count2 = tempVector2.size();

      int current = 0;
      label: for (int i = 0; i<count1; i++) {

        Integer particle1 = (Integer)tempVector1.elementAt(i);
        for (int j = current; j<count2; j++) {
           Integer particle2 = (Integer)tempVector2.elementAt(j);
           current +=1;
           try {
             checkParticleDerivationOK(particle1.intValue(),derivedScope, 
                particle2.intValue(), baseScope, bInfo);
             continue label;
           }
           catch (ParticleRecoverableError e) {
           }
        }
        // didn't find a match.  Detect an error
	throw new ParticleRecoverableError("rcase-Recurse.2:  There is not a complete functional mapping between the particles");

      }

    }

    private void checkMapAndSum(int csIndex1, Vector tempVector1, int derivedScope, int csIndex2, Vector tempVector2, int baseScope, ComplexTypeInfo bInfo) throws Exception {

      // See if the sequence group particle is a valid restriction of one of the particles 
      // of the choice
      // This isn't what the spec says, but I can't make heads or tails of the 
      // algorithm in structures

      int count2 = tempVector2.size();
      boolean foundit = false; 
      for (int i=0; i<count2; i++) {
         Integer particle = (Integer)tempVector2.elementAt(i);
         fSchemaGrammar.getContentSpec(particle.intValue(),tempContentSpec1);
         if (tempContentSpec1.type == XMLContentSpec.CONTENTSPECNODE_SEQ)
         try {
           checkParticleDerivationOK(csIndex1,derivedScope,particle.intValue(),
               baseScope, bInfo);
           foundit = true;
           break;
         }
         catch (ParticleRecoverableError e) {
         }
      }

      if (!foundit) 
	throw new ParticleRecoverableError("rcase-MapAndSum:  There is not a complete functional mapping between the particles");
    }

    private int importContentSpec(SchemaGrammar aGrammar, int contentSpecHead ) throws Exception {
        XMLContentSpec ctsp = new XMLContentSpec();
        aGrammar.getContentSpec(contentSpecHead, ctsp);
        int left = -1;
        int right = -1;
        if ( ctsp.type == ctsp.CONTENTSPECNODE_LEAF 
             || (ctsp.type & 0x0f) == ctsp.CONTENTSPECNODE_ANY
             || (ctsp.type & 0x0f) == ctsp.CONTENTSPECNODE_ANY_NS
             || (ctsp.type & 0x0f) == ctsp.CONTENTSPECNODE_ANY_OTHER ) {
            return fSchemaGrammar.addContentSpecNode(ctsp.type, ctsp.value, ctsp.otherValue, false);
        }
		else if (ctsp.type == -1) 
			// case where type being extended has no content
			return -2;
        else {
            if ( ctsp.value == -1 ) {
                left = -1;
            }
            else {
                left = importContentSpec(aGrammar, ctsp.value);
            }
            
            if ( ctsp.otherValue == -1 ) {
                right = -1;
            }
            else {
                right = importContentSpec(aGrammar, ctsp.otherValue);
            }
            return fSchemaGrammar.addContentSpecNode(ctsp.type, left, right, false);
        
        }
    }

    private int handleOccurrences(int index,
                                  Element particle) throws Exception {
        // Pass through, indicating we're not processing an <all>
        return handleOccurrences(index, particle, NOT_ALL_CONTEXT);
    }

    // Checks constraints for minOccurs, maxOccurs and expands content model 
    // accordingly
    private int handleOccurrences(int index, Element particle,
                                  int allContextFlags) throws Exception {
        
        // if index is invalid, return
        if (index < 0) 
          return index;
        
        String minOccurs =
                    particle.getAttribute(SchemaSymbols.ATT_MINOCCURS).trim();
        String maxOccurs =
                    particle.getAttribute(SchemaSymbols.ATT_MAXOCCURS).trim();    
        boolean processingAll   = ((allContextFlags & PROCESSING_ALL) != 0);
        boolean groupRefWithAll = ((allContextFlags & GROUP_REF_WITH_ALL) != 0);
        boolean isGroupChild    = ((allContextFlags & CHILD_OF_GROUP) != 0);

        // Neither minOccurs nor maxOccurs may be specified
        // for the child of a model group definition.
        if (isGroupChild && (!minOccurs.equals("") || !maxOccurs.equals(""))) {
            reportSchemaError(SchemaMessageProvider.MinMaxOnGroupChild, null);
            minOccurs = (maxOccurs = "1");
        }

        // If minOccurs=maxOccurs=0, no component is specified
        if(minOccurs.equals("0") && maxOccurs.equals("0")){
            return -2;
        }

        int min=1, max=1;

        if (minOccurs.equals("")) {
            minOccurs = "1";
        }
        if (maxOccurs.equals("")) {
            maxOccurs = "1";
        }

        // For the elements referenced in an <all>, minOccurs attribute 
        // must be zero or one, and maxOccurs attribute must be one.
        if (processingAll || groupRefWithAll) {
            if ((groupRefWithAll || !minOccurs.equals("0")) &&
                 !minOccurs.equals("1")) {
                int minMsg = processingAll ?
                             SchemaMessageProvider.BadMinMaxForAll :
                             SchemaMessageProvider.BadMinMaxForGroupWithAll;
                reportSchemaError(minMsg, new Object [] { "minOccurs",
                                                          minOccurs });
                minOccurs = "1";
            }

            if (!maxOccurs.equals("1")) {
                int maxMsg = processingAll ?
                             SchemaMessageProvider.BadMinMaxForAll :
                             SchemaMessageProvider.BadMinMaxForGroupWithAll;
                reportSchemaError(maxMsg, new Object [] { "maxOccurs",
                                                          maxOccurs });
                maxOccurs = "1";
            }
        }

        try {
            min = Integer.parseInt(minOccurs);
        }
        catch (Exception e){
            reportSchemaError(SchemaMessageProvider.GenericError,
                              new Object [] { "illegal value for minOccurs or maxOccurs : '" +e.getMessage()+ "' "});
        }

        if (maxOccurs.equals("unbounded")) {
           max = SchemaSymbols.OCCURRENCE_UNBOUNDED;
        }
        else {
           try {
               max = Integer.parseInt(maxOccurs);
           }
           catch (Exception e){
               reportSchemaError(SchemaMessageProvider.GenericError,
                                new Object [] { "illegal value for minOccurs or maxOccurs : '" +e.getMessage()+ "' "});
           }

           // Check that minOccurs isn't greater than maxOccurs.
           // p-props-correct 2.1
           if (min > max) {
               reportGenericSchemaError("p-props-correct:2.1 Value of minOccurs '" + minOccurs + "' must not be greater than value of maxOccurs '" + maxOccurs +"'");
           }

           if (max < 1) {
               reportGenericSchemaError("p-props-correct:2.2 Value of maxOccurs " + maxOccurs + " is invalid.  It must be greater than or equal to 1");
           }
        }

        if (fSchemaGrammar.getDeferContentSpecExpansion()) {
          fSchemaGrammar.setContentSpecMinOccurs(index,min);
          fSchemaGrammar.setContentSpecMaxOccurs(index,max);
          return index;
        }
        else {
          return fSchemaGrammar.expandContentModel(index,min,max);
        }

    }


    /**
     * Traverses Schema attribute declaration.
     *   
     *       <attribute 
     *         default = string
     *         fixed = string
     *         form = (qualified | unqualified)
     *         id = ID 
     *         name = NCName 
     *         ref = QName 
     *         type = QName 
     *         use = (optional | prohibited | required) : optional
     *         {any attributes with non-schema namespace ...}>
     *         Content: (annotation? , simpleType?)
     *       <attribute/>
     * 
     * @param attributeDecl: the declaration of the attribute under 
	 * 		consideration
	 * @param typeInfo: Contains the index of the element to which 
	 * 		the attribute declaration is attached.
	 * @param referredTo:  true iff traverseAttributeDecl was called because 
	 *		of encountering a ``ref''property (used
	 *		to suppress error-reporting).
     * @return 0 if the attribute schema is validated successfully, otherwise -1
     * @exception Exception
     */
    private int traverseAttributeDecl( Element attrDecl, ComplexTypeInfo typeInfo, boolean referredTo ) throws Exception {

        // General Attribute Checking
        int scope = isTopLevel(attrDecl)?
                    GeneralAttrCheck.ELE_CONTEXT_GLOBAL:
                    GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(attrDecl, scope);

        ////// Get declared fields of the attribute
        String defaultStr   = attrDecl.getAttribute(SchemaSymbols.ATT_DEFAULT);
        String fixedStr     = attrDecl.getAttribute(SchemaSymbols.ATT_FIXED);
        String formStr      = attrDecl.getAttribute(SchemaSymbols.ATT_FORM);//form attribute
        String attNameStr    = attrDecl.getAttribute(SchemaSymbols.ATT_NAME);
        String refStr       = attrDecl.getAttribute(SchemaSymbols.ATT_REF);
        String datatypeStr  = attrDecl.getAttribute(SchemaSymbols.ATT_TYPE);
        String useStr       = attrDecl.getAttribute(SchemaSymbols.ATT_USE);
        Element simpleTypeChild = findAttributeSimpleType(attrDecl);

        Attr defaultAtt   = attrDecl.getAttributeNode(SchemaSymbols.ATT_DEFAULT);
        Attr fixedAtt     = attrDecl.getAttributeNode(SchemaSymbols.ATT_FIXED);
        Attr formAtt      = attrDecl.getAttributeNode(SchemaSymbols.ATT_FORM);
        Attr attNameAtt    = attrDecl.getAttributeNode(SchemaSymbols.ATT_NAME);
        Attr refAtt       = attrDecl.getAttributeNode(SchemaSymbols.ATT_REF);
        Attr datatypeAtt  = attrDecl.getAttributeNode(SchemaSymbols.ATT_TYPE);
        Attr useAtt       = attrDecl.getAttributeNode(SchemaSymbols.ATT_USE);
        
        checkEnumerationRequiredNotation(attNameStr, datatypeStr);
        
        ////// define attribute declaration Schema components
        int attName;        // attribute name indexed in the string pool
        int uriIndex;       // indexed for target namespace uri
        QName attQName;     // QName combining attName and uriIndex
		
        // attribute type
        int attType;
        boolean attIsList    = false;
        int dataTypeSymbol   = -1;
        String localpart = null;

        // validator
        DatatypeValidator dv;
        boolean dvIsDerivedFromID = false;

        // value constraints and use type
        int attValueAndUseType = 0;
        int attValueConstraint = -1;   // indexed value in a string pool

        ////// Check W3C's PR-Structure 3.2.3
        // --- Constraints on XML Representations of Attribute Declarations
        boolean isAttrTopLevel = isTopLevel(attrDecl);
        boolean isOptional = false;
        boolean isProhibited = false;
        boolean isRequired = false;

        StringBuffer errorContext = new StringBuffer(30);
        errorContext.append(" -- ");
        if(typeInfo == null) {
            errorContext.append("(global attribute) ");
		}
        else if(typeInfo.typeName == null) {
            errorContext.append("(local attribute) ");
        }
        else {
            errorContext.append("(attribute) ").append(typeInfo.typeName).append("/");
        }
        errorContext.append(attNameStr).append(' ').append(refStr);

        if(useStr.equals("") || useStr.equals(SchemaSymbols.ATTVAL_OPTIONAL)) {
            attValueAndUseType |= XMLAttributeDecl.USE_TYPE_OPTIONAL;
            isOptional = true;
        }
        else if(useStr.equals(SchemaSymbols.ATTVAL_PROHIBITED)) {
            attValueAndUseType |= XMLAttributeDecl.USE_TYPE_PROHIBITED;
            isProhibited = true;
        }
        else if(useStr.equals(SchemaSymbols.ATTVAL_REQUIRED)) {
            attValueAndUseType |= XMLAttributeDecl.USE_TYPE_REQUIRED;
            isRequired = true;
        }
        else {
            reportGenericSchemaError("An attribute cannot declare \"" +
                SchemaSymbols.ATT_USE + "\" as \"" + useStr + "\"" + errorContext);
        }

        if(defaultAtt != null && fixedAtt != null) {
            reportGenericSchemaError("src-attribute.1: \"" + SchemaSymbols.ATT_DEFAULT +
                "\" and \"" + SchemaSymbols.ATT_FIXED +
                "\" cannot be both present" + errorContext);
        }
        else if(defaultAtt != null && !isOptional) {
            reportGenericSchemaError("src-attribute.2: If both \"" + SchemaSymbols.ATT_DEFAULT +
                "\" and \"" + SchemaSymbols.ATT_USE + "\" " +
                "are present for an attribute declaration, \"" +
                SchemaSymbols.ATT_USE + "\" can only be \"" +
                SchemaSymbols.ATTVAL_OPTIONAL + "\", not \"" + useStr + "\"." + errorContext);
        }

        if(!isAttrTopLevel) {
            if((refAtt == null) == (attNameAtt == null)) {
                reportGenericSchemaError("src-attribute.3.1: When the attribute's parent is not <schema> , one of \"" +
                    SchemaSymbols.ATT_REF + "\" and \""  + SchemaSymbols.ATT_NAME +
                    "\" should be declared, but not both."+ errorContext);
                return -1;
            }
            else if((refAtt != null) && (simpleTypeChild != null || formAtt != null || datatypeAtt != null)) {
                reportGenericSchemaError("src-attribute.3.2: When the attribute's parent is not <schema> and \"" +
                    SchemaSymbols.ATT_REF + "\" is present, " +
                    "all of <" + SchemaSymbols.ELT_SIMPLETYPE + ">, " +
                    SchemaSymbols.ATT_FORM + " and "  + SchemaSymbols.ATT_TYPE +
                    " must be absent."+ errorContext);
            }
        }

        if(datatypeAtt != null && simpleTypeChild != null) {
            reportGenericSchemaError("src-attribute.4: \"" + SchemaSymbols.ATT_TYPE + "\" and <" +
                SchemaSymbols.ELT_SIMPLETYPE + "> cannot both be present"+ errorContext);
        }

        ////// Check W3C's PR-Structure 3.2.2
        // --- XML Representation of Attribute Declaration Schema Components

        // check case-dependent attribute declaration schema components
        if (isAttrTopLevel) {
            //// global attributes
            // set name component
            attName  = fStringPool.addSymbol(attNameStr);
            if(fTargetNSURIString.length() == 0) {
                uriIndex = StringPool.EMPTY_STRING;
            }
            else {
                uriIndex = fTargetNSURI;
            }
            
            // attQName = new QName(-1,attName,attName,uriIndex);
            // Above line replaced by following 2 to work around a JIT problem.
            attQName = new QName();
            attQName.setValues(-1,attName,attName,uriIndex);

        }
        else if(refAtt == null) {
            //// local attributes
            // set name component
            attName  = fStringPool.addSymbol(attNameStr);
            if((formStr.length() > 0 && formStr.equals(SchemaSymbols.ATTVAL_QUALIFIED)) ||
                (formStr.length() == 0 && fAttributeDefaultQualified)) {
                uriIndex = fTargetNSURI;
            }
            else {
                uriIndex = StringPool.EMPTY_STRING;
            }
            // attQName = new QName(-1,attName,attName,uriIndex);
            // Above line replaced by following 2 to work around a JIT problem.
            attQName = new QName();
            attQName.setValues(-1,attName,attName,uriIndex);
        }
        else {
            //// locally referenced global attributes
            String prefix;
            int colonptr = refStr.indexOf(":");
            if ( colonptr > 0) {
                prefix = refStr.substring(0,colonptr);
                localpart = refStr.substring(colonptr+1);
            }
            else {
                prefix = "";
                localpart = refStr;
            }

            String uriStr = resolvePrefixToURI(prefix);

            if (!uriStr.equals(fTargetNSURIString)) {
                addAttributeDeclFromAnotherSchema(localpart, uriStr, typeInfo);
                return 0;
            }

            Element referredAttribute = getTopLevelComponentByName(SchemaSymbols.ELT_ATTRIBUTE,localpart);
            if (referredAttribute != null) { 
					// don't need to traverse ref'd attribute if we're global; just make sure it's there...
               	 	traverseAttributeDecl(referredAttribute, typeInfo, true);

                Attr referFixedAttr = referredAttribute.getAttributeNode(SchemaSymbols.ATT_FIXED);
                String referFixed = referFixedAttr == null ? null : referFixedAttr.getValue();
                if (referFixed != null && (defaultAtt != null || fixedAtt != null && !referFixed.equals(fixedStr))) {
                    reportGenericSchemaError("au-props-correct.2: If the {attribute declaration} has a fixed {value constraint}, then if the attribute use itself has a {value constraint}, it must also be fixed and its value must match that of the {attribute declaration}'s {value constraint}" + errorContext);
                }

                // this nasty hack needed to ``override'' the
                // global attribute with "use" and "fixed" on the ref'ing attribute
                if(!isOptional || fixedStr.length() > 0) {
					int referredAttName = fStringPool.addSymbol(referredAttribute.getAttribute(SchemaSymbols.ATT_NAME));
                    uriIndex = StringPool.EMPTY_STRING;
        			if ( fTargetNSURIString.length() > 0) {
                    	uriIndex = fTargetNSURI;
        			}
        			QName referredAttQName = new QName(-1,referredAttName,referredAttName,uriIndex);

	                	int tempIndex = fSchemaGrammar.getAttributeDeclIndex(typeInfo.templateElementIndex, referredAttQName);
						XMLAttributeDecl referredAttrDecl = new XMLAttributeDecl();
						fSchemaGrammar.getAttributeDecl(tempIndex, referredAttrDecl);

                    boolean updated = false;

                    int useDigits =   XMLAttributeDecl.USE_TYPE_OPTIONAL |
                                      XMLAttributeDecl.USE_TYPE_PROHIBITED |
                                      XMLAttributeDecl.USE_TYPE_REQUIRED;

                    int valueDigits = XMLAttributeDecl.VALUE_CONSTRAINT_DEFAULT |
                                      XMLAttributeDecl.VALUE_CONSTRAINT_FIXED;

                    if(!isOptional &&
                       (referredAttrDecl.defaultType & useDigits) !=
                       (attValueAndUseType & useDigits))
                    {
                        if(referredAttrDecl.defaultType != XMLAttributeDecl.USE_TYPE_PROHIBITED) {
                            referredAttrDecl.defaultType |= useDigits;
                            referredAttrDecl.defaultType ^= useDigits; // clear the use
                        referredAttrDecl.defaultType |= (attValueAndUseType & useDigits);
                        updated = true;
					}
					}

                    if(fixedStr.length() > 0) {
                        if((referredAttrDecl.defaultType & XMLAttributeDecl.VALUE_CONSTRAINT_FIXED) == 0) {
                            referredAttrDecl.defaultType |= valueDigits;
                            referredAttrDecl.defaultType ^= valueDigits; // clear the value
                            referredAttrDecl.defaultType |= XMLAttributeDecl.VALUE_CONSTRAINT_FIXED;
                            referredAttrDecl.defaultValue = fStringPool.toString(attValueConstraint);
                            updated = true;
					}
			}

                    if(updated) {
                        fSchemaGrammar.setAttributeDecl(typeInfo.templateElementIndex, tempIndex, referredAttrDecl);
                    }
                }
			}
            else if (fAttributeDeclRegistry.get(localpart) != null) {
                    addAttributeDeclFromAnotherSchema(localpart, uriStr, typeInfo);
                }
            else {
                    // REVISIT: Localize
                reportGenericSchemaError ( "Couldn't find top level attribute " + refStr + errorContext);
            }
            return 0;
            }

        if (uriIndex == fXsiURI) {
            reportGenericSchemaError("no-xsi: The {target namespace} of an attribute declaration must not match " + SchemaSymbols.URI_XSI + errorContext);
        }

        // validation of attribute type is same for each case of declaration
            if (simpleTypeChild != null) { 
                attType        = XMLAttributeDecl.TYPE_SIMPLE;
                dataTypeSymbol = traverseSimpleTypeDecl(simpleTypeChild);
                localpart = fStringPool.toString(dataTypeSymbol);
            dv = fDatatypeRegistry.getDatatypeValidator(localpart);
        }
        else if (datatypeStr.length() != 0) {
            dataTypeSymbol = fStringPool.addSymbol(datatypeStr);
            String prefix;
            int  colonptr = datatypeStr.indexOf(":");
            if ( colonptr > 0) {
                prefix = datatypeStr.substring(0,colonptr);
                localpart = datatypeStr.substring(colonptr+1);
            }
            else {
                prefix = "";
                localpart = datatypeStr;
            }
            String typeURI = resolvePrefixToURI(prefix);

            if ( typeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA) 
                 || typeURI.length()==0) {

                dv = getDatatypeValidator("", localpart);

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
                    if (dv == null && typeURI.length() == 0) {
                        Element topleveltype = getTopLevelComponentByName(SchemaSymbols.ELT_SIMPLETYPE, localpart);
                        if (topleveltype != null) {
                            traverseSimpleTypeDecl( topleveltype );
                            dv = getDatatypeValidator(typeURI, localpart);
                        }else if (!referredTo) {
                            // REVISIT: Localize
                            reportGenericSchemaError("simpleType not found : " + "("+typeURI+":"+localpart+")"+ errorContext);
                        }
                    }
                }
            } else { //isn't of the schema for schemas namespace...
                attType = XMLAttributeDecl.TYPE_SIMPLE;
                // check if the type is from the same Schema

                dv = getDatatypeValidator(typeURI, localpart);
                if (dv == null && typeURI.equals(fTargetNSURIString) ) {
                    Element topleveltype = getTopLevelComponentByName(SchemaSymbols.ELT_SIMPLETYPE, localpart);
                    if (topleveltype != null) {
                        traverseSimpleTypeDecl( topleveltype );
                        dv = getDatatypeValidator(typeURI, localpart);
                    }else if (!referredTo) {
                        // REVISIT: Localize
                        reportGenericSchemaError("simpleType not found : " + "("+typeURI+":"+ localpart+")"+ errorContext);
                    }
                }
            }
				} 
				else {
            attType        = XMLAttributeDecl.TYPE_SIMPLE;
            localpart      = "string";
            dataTypeSymbol = fStringPool.addSymbol(localpart);
            dv = fDatatypeRegistry.getDatatypeValidator(localpart);
        } // if(...Type)

        // validation of data constraint is same for each case of declaration
        if(defaultStr.length() > 0) {
            attValueAndUseType |= XMLAttributeDecl.VALUE_CONSTRAINT_DEFAULT;
            attValueConstraint = fStringPool.addString(defaultStr);
			}
        else if(fixedStr.length() > 0) {
            attValueAndUseType |= XMLAttributeDecl.VALUE_CONSTRAINT_FIXED;
            attValueConstraint = fStringPool.addString(fixedStr);
		}

        ////// Check W3C's PR-Structure 3.2.6
        // --- Constraints on Attribute Declaration Schema Components
        // check default value is valid for the datatype.  
        if (attType == XMLAttributeDecl.TYPE_SIMPLE && attValueConstraint != -1) {
            try { 
                if (dv != null) {
                    if(defaultStr.length() > 0) {
                    //REVISIT
                        dv.validate(defaultStr, null);
                    }
                    else {
                        dv.validate(fixedStr, null);
                    }
                }
                else if (!referredTo)
                    reportSchemaError(SchemaMessageProvider.NoValidatorFor,
                            new Object [] { datatypeStr });
            } catch (InvalidDatatypeValueException idve) {
				if (!referredTo) 
                	reportSchemaError(SchemaMessageProvider.IncorrectDefaultType,
                        new Object [] { attrDecl.getAttribute(SchemaSymbols.ATT_NAME), idve.getMessage() });    //a-props-correct.2
            } catch (Exception e) {
                e.printStackTrace();
                System.out.println("Internal error in attribute datatype validation");
            }
        }

        // check the coexistence of ID and value constraint
        dvIsDerivedFromID = 
          ((dv != null) && dv instanceof IDDatatypeValidator);
        if (dvIsDerivedFromID && attValueConstraint != -1)
        {
            reportGenericSchemaError("a-props-correct.3: If type definition is or is derived from ID ," +
                "there must not be a value constraint" + errorContext);
        }

        if (attNameStr.equals("xmlns")) {
            reportGenericSchemaError("no-xmlns: The {name} of an attribute declaration must not match 'xmlns'" + errorContext);
        }

        ////// every contraints were matched.  Now register the attribute declaration
        //put the top-levels in the attribute decl registry.
        if (isAttrTopLevel) {
            fTempAttributeDecl.datatypeValidator = dv;
            fTempAttributeDecl.name.setValues(attQName);
            fTempAttributeDecl.type = attType;
            fTempAttributeDecl.defaultType = attValueAndUseType;
            fTempAttributeDecl.list = attIsList;
            if (attValueConstraint != -1 ) {
                fTempAttributeDecl.defaultValue = fStringPool.toString(attValueConstraint);
            }
            fAttributeDeclRegistry.put(attNameStr, new XMLAttributeDecl(fTempAttributeDecl));
        }

        // add attribute to attr decl pool in fSchemaGrammar, 
        if (typeInfo != null) {
            
            // check that there aren't duplicate attributes
            int temp = fSchemaGrammar.getAttributeDeclIndex(typeInfo.templateElementIndex, attQName);
            if (temp > -1) {
              reportGenericSchemaError("ct-props-correct.4:  Duplicate attribute " + 
              fStringPool.toString(attQName.rawname) + " in type definition");
            }
              
            // check that there aren't multiple attributes with type derived from ID
            if (dvIsDerivedFromID) {
               if (typeInfo.containsAttrTypeID())  {
                 reportGenericSchemaError("ct-props-correct.5: More than one attribute derived from type ID cannot appear in the same complex type definition.");
               }
               typeInfo.setContainsAttrTypeID();
            }

            fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                      attQName, attType, 
                                      dataTypeSymbol, attValueAndUseType,
                                      fStringPool.toString( attValueConstraint), dv, attIsList);
        }

        return 0;
    } // end of method traverseAttribute

    private int addAttributeDeclFromAnotherSchema( String name, String uriStr, ComplexTypeInfo typeInfo) throws Exception {
        SchemaGrammar aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uriStr);
        if (uriStr == null || ! (aGrammar instanceof SchemaGrammar) ) {
            // REVISIT: Localize
            reportGenericSchemaError( "no attribute named \"" + name
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }

        Hashtable attrRegistry = aGrammar.getAttributeDeclRegistry();
        if (attrRegistry == null) {
            // REVISIT: Localize
            reportGenericSchemaError( "no attribute named \"" + name
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }

        XMLAttributeDecl tempAttrDecl = (XMLAttributeDecl) attrRegistry.get(name);

        if (tempAttrDecl == null) {
            // REVISIT: Localize
            reportGenericSchemaError( "no attribute named \"" + name 
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }


        if (typeInfo!= null) {

            // check that there aren't duplicate attributes
            int temp = fSchemaGrammar.getAttributeDeclIndex(typeInfo.templateElementIndex, tempAttrDecl.name);
            if (temp > -1) {
              reportGenericSchemaError("ct-props-correct.4:  Duplicate attribute " + 
              fStringPool.toString(tempAttrDecl.name.rawname) + " in type definition");
            }

            // check that there aren't multiple attributes with type derived from ID
            if (tempAttrDecl.datatypeValidator != null && 
                tempAttrDecl.datatypeValidator instanceof IDDatatypeValidator) {
               if (typeInfo.containsAttrTypeID())  {
                 reportGenericSchemaError("ct-props-correct.5: More than one attribute derived from type ID cannot appear in the same complex type definition");
               }
               typeInfo.setContainsAttrTypeID();
            }

            fSchemaGrammar.addAttDef( typeInfo.templateElementIndex, 
                                      tempAttrDecl.name, tempAttrDecl.type,
                                      -1, tempAttrDecl.defaultType,
                                      tempAttrDecl.defaultValue, 
                                      tempAttrDecl.datatypeValidator, 
                                      tempAttrDecl.list);
        }


        return 0;
    }

    /*
    * 
    * <attributeGroup 
    *   id = ID 
    *   name = NCName
    *   ref = QName>
    *   Content: (annotation?, (attribute|attributeGroup)*, anyAttribute?)
    * </>
    * 
    */
    private int traverseAttributeGroupDecl( Element attrGrpDecl, ComplexTypeInfo typeInfo, Vector anyAttDecls ) throws Exception {
        // General Attribute Checking
        int scope = isTopLevel(attrGrpDecl)?
                    GeneralAttrCheck.ELE_CONTEXT_GLOBAL:
                    GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(attrGrpDecl, scope);

        // attributeGroup name
        String attGrpNameStr = attrGrpDecl.getAttribute(SchemaSymbols.ATT_NAME);
        int attGrpName = fStringPool.addSymbol(attGrpNameStr);
        
        String ref = attrGrpDecl.getAttribute(SchemaSymbols.ATT_REF); 
		Element child = checkContent( attrGrpDecl, XUtil.getFirstChildElement(attrGrpDecl), true );

        if (!ref.equals("")) {
			if(isTopLevel(attrGrpDecl)) 
				// REVISIT:  localize 
   	    	    reportGenericSchemaError ( "An attributeGroup with \"ref\" present must not have <schema> or <redefine> as its parent");
			if(!attGrpNameStr.equals(""))
				// REVISIT:  localize 
   	    	    reportGenericSchemaError ( "attributeGroup " + attGrpNameStr + " cannot refer to another attributeGroup, but it refers to " + ref);
            if (XUtil.getFirstChildElement(attrGrpDecl) != null ||
                attrGrpDecl.getNodeValue() != null)
				// REVISIT:  localize
   	    	    reportGenericSchemaError ( "An attributeGroup with \"ref\" present must be empty");
            
            String prefix = "";
            String localpart = ref;
            int colonptr = ref.indexOf(":");
            if ( colonptr > 0) {
                prefix = ref.substring(0,colonptr);
                localpart = ref.substring(colonptr+1);
            }
            String uriStr = resolvePrefixToURI(prefix);
            if (!uriStr.equals(fTargetNSURIString)) {
                
                traverseAttributeGroupDeclFromAnotherSchema(localpart, uriStr, typeInfo, anyAttDecls);

                return -1;
                // TO DO 
                // REVISIST: different NS, not supported yet.
                // REVISIT: Localize
                //reportGenericSchemaError("Feature not supported: see an attribute from different NS");
            } else {
                Element parent = (Element)attrGrpDecl.getParentNode();
                if (parent.getLocalName().equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) &&
                    parent.getAttribute(SchemaSymbols.ATT_NAME).equals(localpart)) {
                    if (!((Element)parent.getParentNode()).getLocalName().equals(SchemaSymbols.ELT_REDEFINE)) {
                        reportGenericSchemaError("src-attribute_group.3: Circular group reference is disallowed outside <redefine> -- "+ref);
            }
                    return -1;
                }
            }

			if(typeInfo != null) { 
 				// only do this if we're traversing because we were ref'd here; when we come 
				// upon this decl by itself we're just validating.
            	Element referredAttrGrp = getTopLevelComponentByName(SchemaSymbols.ELT_ATTRIBUTEGROUP,localpart);
            	if (referredAttrGrp != null) {
                	traverseAttributeGroupDecl(referredAttrGrp, typeInfo, anyAttDecls);
            	}
            	else {
                	// REVISIT: Localize
                	reportGenericSchemaError ( "Couldn't find top level attributeGroup " + ref);
            	}
 				return -1;
			}
        } else if (attGrpNameStr.equals(""))
				// REVISIT:  localize 
                reportGenericSchemaError ( "an attributeGroup must have a name or a ref attribute present");

        for (; 
             child != null ; child = XUtil.getNextSiblingElement(child)) {
       
            if ( child.getLocalName().equals(SchemaSymbols.ELT_ATTRIBUTE) ){
                traverseAttributeDecl(child, typeInfo, false);
            }
            else if ( child.getLocalName().equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ) {
//				if(typeInfo != null)
 					// only do this if we're traversing because we were ref'd here; when we come 
					// upon this decl by itself we're just validating.
                	traverseAttributeGroupDecl(child, typeInfo,anyAttDecls);
            }
            else 
				break;
        }
		if (child != null) {
			if ( child.getLocalName().equals(SchemaSymbols.ELT_ANYATTRIBUTE) ) {
                if (anyAttDecls != null) { 
                     anyAttDecls.addElement(traverseAnyAttribute(child));
                }
				if (XUtil.getNextSiblingElement(child) != null) 
					// REVISIT:  localize
                	reportGenericSchemaError ( "src-attribute_group.0: The content of an attributeGroup declaration must match (annotation?, ((attribute | attributeGroup)*, anyAttribute?))");
				return -1;
			}
			else 
				// REVISIT:  localize
                reportGenericSchemaError ( "src-attribute_group.0: The content of an attributeGroup declaration must match (annotation?, ((attribute | attributeGroup)*, anyAttribute?))");
		}
        return -1;
    } // end of method traverseAttributeGroup
    
    private int traverseAttributeGroupDeclFromAnotherSchema( String attGrpName , String uriStr, 
                                                             ComplexTypeInfo typeInfo,
                                                             Vector anyAttDecls ) throws Exception {
        
        SchemaGrammar aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uriStr);
        if (uriStr == null || aGrammar == null || ! (aGrammar instanceof SchemaGrammar) ) {
            // REVISIT: Localize
            reportGenericSchemaError("!!Schema not found in #traverseAttributeGroupDeclFromAnotherSchema, schema uri : " + uriStr);
            return -1;
        }
        // attribute name
        Element attGrpDecl = (Element) aGrammar.topLevelAttrGrpDecls.get((Object)attGrpName);
        if (attGrpDecl == null) {
            // REVISIT: Localize
            reportGenericSchemaError( "no attribute group named \"" + attGrpName 
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }
        
        NamespacesScope saveNSMapping = fNamespacesScope;
        int saveTargetNSUri = fTargetNSURI;
        fTargetNSURI = fStringPool.addSymbol(aGrammar.getTargetNamespaceURI());
        fNamespacesScope = aGrammar.getNamespacesScope();

        // attribute type
        int attType = -1;
        int enumeration = -1;


        Element child = checkContent(attGrpDecl, XUtil.getFirstChildElement(attGrpDecl), true); 
        for (; 
             child != null ; child = XUtil.getNextSiblingElement(child)) {

            //child attribute couldn't be a top-level attribute DEFINITION, 
            if ( child.getLocalName().equals(SchemaSymbols.ELT_ATTRIBUTE) ){
                String childAttName = child.getAttribute(SchemaSymbols.ATT_NAME);
                if ( childAttName.length() > 0 ) {
                    Hashtable attDeclRegistry = aGrammar.getAttributeDeclRegistry();
                    if (attDeclRegistry != null) {
                        if (attDeclRegistry.get((Object)childAttName) != null ){
                            addAttributeDeclFromAnotherSchema(childAttName, uriStr, typeInfo);
                            return -1;
                        }
                    }       
                }
                else 
                    traverseAttributeDecl(child, typeInfo, false);
            }
            else if ( child.getLocalName().equals(SchemaSymbols.ELT_ATTRIBUTEGROUP) ) {
                traverseAttributeGroupDecl(child, typeInfo, anyAttDecls);
            }
            else if ( child.getLocalName().equals(SchemaSymbols.ELT_ANYATTRIBUTE) ) {
                anyAttDecls.addElement(traverseAnyAttribute(child));
                break;
            }
            else {
                // REVISIT: Localize
                reportGenericSchemaError("Invalid content for attributeGroup");
            }
        }

        fNamespacesScope = saveNSMapping;
        fTargetNSURI = saveTargetNSUri;
        if(child != null) {
            // REVISIT: Localize
            reportGenericSchemaError("Invalid content for attributeGroup");
        }
        return -1;
    } // end of method traverseAttributeGroupFromAnotherSchema
    
	// This simple method takes an attribute declaration as a parameter and
	// returns null if there is no simpleType defined or the simpleType
	// declaration if one exists.  It also throws an error if more than one
	// <annotation> or <simpleType> group is present.
	private Element findAttributeSimpleType(Element attrDecl) throws Exception {
		Element child = checkContent(attrDecl, XUtil.getFirstChildElement(attrDecl), true);
        // if there is only a annotatoin, then no simpleType
	   	if (child == null)
	   		return null;
        // if the current one is not simpleType, or there are more elements,
        // report an error
		if (!child.getLocalName().equals(SchemaSymbols.ELT_SIMPLETYPE) ||
            XUtil.getNextSiblingElement(child) != null)
    		//REVISIT: localize
		    reportGenericSchemaError("src-attribute.0: the content must match (annotation?, (simpleType?)) -- attribute declaration '"+
                                     attrDecl.getAttribute(SchemaSymbols.ATT_NAME)+"'");
		if (child.getLocalName().equals(SchemaSymbols.ELT_SIMPLETYPE))
			return child;
	   		return null;
	} // end findAttributeSimpleType

    /**
     * Traverse element declaration:
     *  <element
     *         abstract = boolean
     *         block = #all or (possibly empty) subset of {substitutionGroup, extension, restriction}
     *         default = string
     *         substitutionGroup = QName
     *         final = #all or (possibly empty) subset of {extension, restriction}
     *         fixed = string
     *         form = qualified | unqualified
     *         id = ID
     *         maxOccurs = string
     *         minOccurs = nonNegativeInteger
     *         name = NCName
     *         nillable = boolean
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

        // General Attribute Checking
        int scope = isTopLevel(elementDecl)?
                    GeneralAttrCheck.ELE_CONTEXT_GLOBAL:
                    GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(elementDecl, scope);

        int contentSpecType      = -1;
        int contentSpecNodeIndex = -1;
        int typeNameIndex = -1;
        int scopeDefined = -2; //signal a error if -2 gets gets through 
                                //cause scope can never be -2.
        DatatypeValidator dv = null;

        String abstractStr = elementDecl.getAttribute(SchemaSymbols.ATT_ABSTRACT);
        String blockStr = elementDecl.getAttribute(SchemaSymbols.ATT_BLOCK);
        String defaultStr = elementDecl.getAttribute(SchemaSymbols.ATT_DEFAULT);
        String finalStr = elementDecl.getAttribute(SchemaSymbols.ATT_FINAL);
        String fixedStr = elementDecl.getAttribute(SchemaSymbols.ATT_FIXED);
        String formStr = elementDecl.getAttribute(SchemaSymbols.ATT_FORM);
        String maxOccursStr = elementDecl.getAttribute(SchemaSymbols.ATT_MAXOCCURS);
        String minOccursStr = elementDecl.getAttribute(SchemaSymbols.ATT_MINOCCURS);
        String nameStr = elementDecl.getAttribute(SchemaSymbols.ATT_NAME);
        String nillableStr = elementDecl.getAttribute(SchemaSymbols.ATT_NILLABLE);
        String refStr = elementDecl.getAttribute(SchemaSymbols.ATT_REF);
        String substitutionGroupStr = elementDecl.getAttribute(SchemaSymbols.ATT_SUBSTITUTIONGROUP);
        String typeStr = elementDecl.getAttribute(SchemaSymbols.ATT_TYPE);
        
        checkEnumerationRequiredNotation(nameStr, typeStr);
        
        if ( DEBUGGING )
            System.out.println("traversing element decl : " + nameStr );

        Attr abstractAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_ABSTRACT);
        Attr blockAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_BLOCK);
        Attr defaultAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_DEFAULT);
        Attr finalAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_FINAL);
        Attr fixedAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_FIXED);
        Attr formAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_FORM);
        Attr maxOccursAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_MAXOCCURS);
        Attr minOccursAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_MINOCCURS);
        Attr nameAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_NAME);
        Attr nillableAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_NILLABLE);
        Attr refAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_REF);
        Attr substitutionGroupAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_SUBSTITUTIONGROUP);
        Attr typeAtt = elementDecl.getAttributeNode(SchemaSymbols.ATT_TYPE);

		if(defaultAtt != null && fixedAtt != null)
			// REVISIT:  localize
			reportGenericSchemaError("src-element.1: an element cannot have both \"fixed\" and \"default\" present at the same time");

        String fromAnotherSchema = null;

        if (isTopLevel(elementDecl)) {
			if(nameAtt == null)
				// REVISIT:  localize
                reportGenericSchemaError("globally-declared element must have a name");
			else if (refAtt != null)
				// REVISIT:  localize
                reportGenericSchemaError("globally-declared element " + nameStr + " cannot have a ref attribute");
        
            int nameIndex = fStringPool.addSymbol(nameStr);
            int eltKey = fSchemaGrammar.getElementDeclIndex(fTargetNSURI, nameIndex,TOP_LEVEL_SCOPE);
            if (eltKey > -1 ) {
                return new QName(-1,nameIndex,nameIndex,fTargetNSURI);
            }
        }
        
        // parse out 'block', 'final', 'nillable', 'abstract'
        if (blockAtt == null)
            blockStr = null;
        int blockSet = parseBlockSet(blockStr);
        if( (blockStr != null) && !blockStr.equals("") &&
                (!blockStr.equals(SchemaSymbols.ATTVAL_POUNDALL) &&
                (((blockSet & SchemaSymbols.RESTRICTION) == 0) && 
                (((blockSet & SchemaSymbols.EXTENSION) == 0) &&
                ((blockSet & SchemaSymbols.SUBSTITUTION) == 0)))))  
            reportGenericSchemaError("The values of the 'block' attribute of an element must be either #all or a list of 'substitution', 'restriction' and 'extension'; " + blockStr + " was found");
        if (finalAtt == null)
            finalStr = null;
        int finalSet = parseFinalSet(finalStr);
        if( (finalStr != null) && !finalStr.equals("") &&
                (!finalStr.equals(SchemaSymbols.ATTVAL_POUNDALL) &&
                (((finalSet & SchemaSymbols.RESTRICTION) == 0) && 
                ((finalSet & SchemaSymbols.EXTENSION) == 0))))  
            reportGenericSchemaError("The values of the 'final' attribute of an element must be either #all or a list of 'restriction' and 'extension'; " + finalStr + " was found");
        boolean isNillable = nillableStr.equals(SchemaSymbols.ATTVAL_TRUE)? true:false;
        boolean isAbstract = abstractStr.equals(SchemaSymbols.ATTVAL_TRUE)? true:false;
        int elementMiscFlags = 0;
        if (isNillable) {
            elementMiscFlags += SchemaSymbols.NILLABLE;
        }
        if (isAbstract) {
            elementMiscFlags += SchemaSymbols.ABSTRACT;
        }
        // make the property of the element's value being fixed also appear in elementMiscFlags
        if(fixedAtt != null)
            elementMiscFlags += SchemaSymbols.FIXED;

        //if this is a reference to a global element
        if (refAtt != null) {
            //REVISIT top level check for ref 
        	if (abstractAtt != null || blockAtt != null || defaultAtt != null ||
                finalAtt != null || fixedAtt != null || formAtt != null ||
                nillableAtt != null || substitutionGroupAtt != null || typeAtt != null)
            	reportSchemaError(SchemaMessageProvider.BadAttWithRef, null);   //src-element.2.2
			if (nameAtt != null)
                // REVISIT: Localize
                reportGenericSchemaError("src-element.2.1: element " + nameStr + " cannot also have a ref attribute");

            Element child = XUtil.getFirstChildElement(elementDecl);
        	if(child != null && child.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) {
            	if (XUtil.getNextSiblingElement(child) != null) 
                	reportSchemaError(SchemaMessageProvider.NoContentForRef, null);
				else
					traverseAnnotationDecl(child);
			}
			else if (child != null) 
                reportSchemaError(SchemaMessageProvider.NoContentForRef, null);
            String prefix = "";
            String localpart = refStr;
            int colonptr = refStr.indexOf(":");
            if ( colonptr > 0) {
                prefix = refStr.substring(0,colonptr);
                localpart = refStr.substring(colonptr+1);
            }
            int localpartIndex = fStringPool.addSymbol(localpart);
            String uriString = resolvePrefixToURI(prefix);
            QName eltName = new QName(prefix != null ? fStringPool.addSymbol(prefix) : -1,
                                      localpartIndex,
                                      fStringPool.addSymbol(refStr),
                                      uriString != null ? fStringPool.addSymbol(uriString) : StringPool.EMPTY_STRING);

            //if from another schema, just return the element QName
            if (! uriString.equals(fTargetNSURIString) ) {
                return eltName;
            }

            int elementIndex = fSchemaGrammar.getElementDeclIndex(eltName, TOP_LEVEL_SCOPE);
            //if not found, traverse the top level element that if referenced

            if (elementIndex == -1 ) {
                Element targetElement = getTopLevelComponentByName(SchemaSymbols.ELT_ELEMENT,localpart);
                if (targetElement == null ) {
                    // REVISIT: Localize
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
        } else if (nameAtt == null)
            // REVISIT: Localize
            reportGenericSchemaError("src-element.2.1: a local element must have a name or a ref attribute present");

                
        // Handle the substitutionGroup
        Element substitutionGroupElementDecl = null;
        int substitutionGroupElementDeclIndex = -1;
        boolean noErrorSoFar = true;
        String substitutionGroupUri = null;
        String substitutionGroupLocalpart = null;
        String substitutionGroupFullName = null;
        ComplexTypeInfo substitutionGroupEltTypeInfo = null;
        DatatypeValidator substitutionGroupEltDV = null;
        SchemaGrammar subGrammar = fSchemaGrammar;

        if ( substitutionGroupStr.length() > 0 ) {
            if(refAtt != null)
                // REVISIT: Localize
                reportGenericSchemaError("a local element cannot have a substitutionGroup");
            substitutionGroupUri =  resolvePrefixToURI(getPrefix(substitutionGroupStr));
            substitutionGroupLocalpart = getLocalPart(substitutionGroupStr);
            substitutionGroupFullName = substitutionGroupUri+","+substitutionGroupLocalpart;
           
            if ( !substitutionGroupUri.equals(fTargetNSURIString) ) {  
                Grammar grammar = fGrammarResolver.getGrammar(substitutionGroupUri);
                if (grammar != null && grammar instanceof SchemaGrammar) {
                    subGrammar = (SchemaGrammar) grammar;
                    substitutionGroupElementDeclIndex = subGrammar.getElementDeclIndex(fStringPool.addSymbol(substitutionGroupUri), 
                                                              fStringPool.addSymbol(substitutionGroupLocalpart), 
                                                              TOP_LEVEL_SCOPE);
                    if (substitutionGroupElementDeclIndex<=-1) {
                        // REVISIT:  localize
                        noErrorSoFar = false;
                        reportGenericSchemaError("couldn't find substitutionGroup " + substitutionGroupLocalpart + " referenced by element " + nameStr 
                                         + " in the SchemaGrammar "+substitutionGroupUri);

                    } else {
                        substitutionGroupEltTypeInfo = getElementDeclTypeInfoFromNS(substitutionGroupUri, substitutionGroupLocalpart);
                        if (substitutionGroupEltTypeInfo == null) {
                            substitutionGroupEltDV = getElementDeclTypeValidatorFromNS(substitutionGroupUri, substitutionGroupLocalpart);
                            if (substitutionGroupEltDV == null) {
                                //TO DO: report error here;
                                noErrorSoFar = false;
                                reportGenericSchemaError("Could not find type for element '" +substitutionGroupLocalpart 
                                                 + "' in schema '" + substitutionGroupUri+"'");
                            }
                        }
                    }
                } else {
                    // REVISIT:  locallize
                    noErrorSoFar = false;
                    reportGenericSchemaError("couldn't find a schema grammar with target namespace " + substitutionGroupUri);
                }
            }
            else {
                substitutionGroupElementDecl = getTopLevelComponentByName(SchemaSymbols.ELT_ELEMENT, substitutionGroupLocalpart);
                if (substitutionGroupElementDecl == null) {
                    substitutionGroupElementDeclIndex = 
                        fSchemaGrammar.getElementDeclIndex(fTargetNSURI, getLocalPartIndex(substitutionGroupStr),TOP_LEVEL_SCOPE);
                    if ( substitutionGroupElementDeclIndex == -1) {
                        noErrorSoFar = false;
                        // REVISIT: Localize
                        reportGenericSchemaError("unable to locate substitutionGroup affiliation element "
                                                  +substitutionGroupStr
                                                  +" in element declaration " 
                                                  +nameStr);
                    }
                }
                else {
                    substitutionGroupElementDeclIndex = 
                        fSchemaGrammar.getElementDeclIndex(fTargetNSURI, getLocalPartIndex(substitutionGroupStr),TOP_LEVEL_SCOPE);

                    if ( substitutionGroupElementDeclIndex == -1) {
                        traverseElementDecl(substitutionGroupElementDecl);
                        substitutionGroupElementDeclIndex = 
                            fSchemaGrammar.getElementDeclIndex(fTargetNSURI, getLocalPartIndex(substitutionGroupStr),TOP_LEVEL_SCOPE);
                    }
                }

                if (substitutionGroupElementDeclIndex != -1) {
                    substitutionGroupEltTypeInfo = fSchemaGrammar.getElementComplexTypeInfo( substitutionGroupElementDeclIndex );
                    if (substitutionGroupEltTypeInfo == null) {
                        fSchemaGrammar.getElementDecl(substitutionGroupElementDeclIndex, fTempElementDecl);
                        substitutionGroupEltDV = fTempElementDecl.datatypeValidator;
                        if (substitutionGroupEltDV == null) {
                            //TO DO: report error here;
                            noErrorSoFar = false;
                            reportGenericSchemaError("Could not find type for element '" +substitutionGroupLocalpart 
                                                     + "' in schema '" + substitutionGroupUri+"'");
                        }
                    }
                }
            }
 
        }
        

        //
        // resolving the type for this element right here
        //

        ComplexTypeInfo typeInfo = null;

        // element has a single child element, either a datatype or a type, null if primitive
        Element child = XUtil.getFirstChildElement(elementDecl);
        
        if(child != null && child.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) {
			traverseAnnotationDecl(child);
            child = XUtil.getNextSiblingElement(child);
		}
        if(child != null && child.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) 
            // REVISIT: Localize
            reportGenericSchemaError("element declarations can contain at most one annotation Element Information Item");
        
        boolean haveAnonType = false;

        // Handle Anonymous type if there is one
        if (child != null) {
            
            String childName = child.getLocalName();
            
            if (childName.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                if (child.getAttribute(SchemaSymbols.ATT_NAME).length() > 0) {
                    noErrorSoFar = false;
                    // REVISIT: Localize
                    reportGenericSchemaError("anonymous complexType in element '" + nameStr +"' has a name attribute");
                }

                else {
                    // Determine what the type name will be 
                    String anonTypeName = genAnonTypeName(child);
                    if (fCurrentTypeNameStack.search((Object)anonTypeName) > - 1) {
                        // A recursing element using an anonymous type

                        int uriInd = StringPool.EMPTY_STRING;
                        if ( formStr.equals(SchemaSymbols.ATTVAL_QUALIFIED)||
                             fElementDefaultQualified) {
                             uriInd = fTargetNSURI;
                        }
                        int nameIndex = fStringPool.addSymbol(nameStr);
                        QName tempQName = new QName(fCurrentScope, nameIndex, nameIndex, uriInd);
                        fElementRecurseComplex.put(tempQName, anonTypeName);
                        return new QName(-1, nameIndex, nameIndex, uriInd);

                    }
                    else {
                        typeNameIndex = traverseComplexTypeDecl(child);
                        if (typeNameIndex != -1 ) {
                            typeInfo = (ComplexTypeInfo)
                                fComplexTypeRegistry.get(fStringPool.toString(typeNameIndex));
                        }
                        else {
                            noErrorSoFar = false;
                            // REVISIT: Localize
                            reportGenericSchemaError("traverse complexType error in element '" + nameStr +"'");
                        }
                    }
                }

                haveAnonType = true;
            	child = XUtil.getNextSiblingElement(child);
            } 
            else if (childName.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                if (child.getAttribute(SchemaSymbols.ATT_NAME).length() > 0) {
                    noErrorSoFar = false;
                    // REVISIT: Localize
                    reportGenericSchemaError("anonymous simpleType in element '" + nameStr +"' has a name attribute");
                }
                else 
                    typeNameIndex = traverseSimpleTypeDecl(child);
                if (typeNameIndex != -1) {
                    dv = fDatatypeRegistry.getDatatypeValidator(fStringPool.toString(typeNameIndex));
                }
                else {
                    noErrorSoFar = false;
                    // REVISIT: Localize
                    reportGenericSchemaError("traverse simpleType error in element '" + nameStr +"'");
                }
                contentSpecType = XMLElementDecl.TYPE_SIMPLE; 
                haveAnonType = true;
            	child = XUtil.getNextSiblingElement(child);
            } else if (typeAtt == null) { // "ur-typed" leaf
                contentSpecType = XMLElementDecl.TYPE_ANY;
                    //REVISIT: is this right?
                //contentSpecType = fStringPool.addSymbol("UR_TYPE");
                // set occurrence count
                contentSpecNodeIndex = -1;
            } 
			// see if there's something here; it had better be key, keyref or unique.
			if (child != null) 
            	childName = child.getLocalName();
			while ((child != null) && ((childName.equals(SchemaSymbols.ELT_KEY))
					|| (childName.equals(SchemaSymbols.ELT_KEYREF)) 
					|| (childName.equals(SchemaSymbols.ELT_UNIQUE)))) {
            	child = XUtil.getNextSiblingElement(child);
                if (child != null) {
                    childName = child.getLocalName();
                }
			}
			if (child != null) {
               	// REVISIT: Localize
            	noErrorSoFar = false;
                reportGenericSchemaError("src-element.0: the content of an element information item must match (annotation?, (simpleType | complexType)?, (unique | key | keyref)*)");
			}
        } 

        // handle type="" here
        if (haveAnonType && (typeAtt != null)) {
            noErrorSoFar = false;
            // REVISIT: Localize
            reportGenericSchemaError( "src-element.3: Element '"+ nameStr +
                                      "' have both a type attribute and a annoymous type child" );
        }
        // type specified as an attribute and no child is type decl.
        else if (typeAtt != null) {
            String prefix = "";
            String localpart = typeStr;
            int colonptr = typeStr.indexOf(":");
            if ( colonptr > 0) {
                prefix = typeStr.substring(0,colonptr);
                localpart = typeStr.substring(colonptr+1);
            }
            String typeURI = resolvePrefixToURI(prefix);
            
            // check if the type is from the same Schema
            if ( !typeURI.equals(fTargetNSURIString) 
                 && !typeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA)
                 && typeURI.length() != 0) {  // REVISIT, only needed because of resolvePrifixToURI.
                fromAnotherSchema = typeURI;
                typeInfo = getTypeInfoFromNS(typeURI, localpart);
                if (typeInfo == null) {
                    dv = getTypeValidatorFromNS(typeURI, localpart);
                    if (dv == null) {
                        //TO DO: report error here;
                        noErrorSoFar = false;
                        reportGenericSchemaError("Could not find type " +localpart 
                                           + " in schema " + typeURI);
                    }
                }
            }
            else {
                typeInfo = (ComplexTypeInfo) fComplexTypeRegistry.get(typeURI+","+localpart);
                if (typeInfo == null) {
                    dv = getDatatypeValidator(typeURI, localpart);
                    if (dv == null )
                    if (typeURI.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA)
                        && !fTargetNSURIString.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA)) 
                    {
                        noErrorSoFar = false;
                        // REVISIT: Localize
                        reportGenericSchemaError("type not found : " + typeURI+":"+localpart);
                    }
                    else {
                        Element topleveltype = getTopLevelComponentByName(SchemaSymbols.ELT_COMPLEXTYPE,localpart);
                        if (topleveltype != null) {
                            if (fCurrentTypeNameStack.search((Object)localpart) > - 1) {
                                //then we found a recursive element using complexType.
                                // REVISIT: this will be broken when recursing happens between 2 schemas
                                int uriInd = StringPool.EMPTY_STRING;
                                if ( formStr.equals(SchemaSymbols.ATTVAL_QUALIFIED)||
                                     fElementDefaultQualified) {
                                    uriInd = fTargetNSURI;
                                }
                                int nameIndex = fStringPool.addSymbol(nameStr);
                                QName tempQName = new QName(fCurrentScope, nameIndex, nameIndex, uriInd);
                                fElementRecurseComplex.put(tempQName, localpart);
                                return new QName(-1, nameIndex, nameIndex, uriInd);
                            }
                            else {
                                typeNameIndex = traverseComplexTypeDecl( topleveltype, true );
                                typeInfo = (ComplexTypeInfo)
                                    fComplexTypeRegistry.get(fStringPool.toString(typeNameIndex));
                            }
                        }
                        else {
                            topleveltype = getTopLevelComponentByName(SchemaSymbols.ELT_SIMPLETYPE, localpart);
                            if (topleveltype != null) {
                                typeNameIndex = traverseSimpleTypeDecl( topleveltype );
                                dv = getDatatypeValidator(typeURI, localpart);
                            }
                            else {
                                noErrorSoFar = false;
                                // REVISIT: Localize
                                reportGenericSchemaError("type not found : " + typeURI+":"+localpart);
                            }

                        }

                    }
                }
            }
   
        } 
        // now we need to make sure that our substitution (if any)
        // is valid, now that we have all the requisite type-related info.
        if(substitutionGroupStr.length() > 0) {
            checkSubstitutionGroupOK(elementDecl, substitutionGroupElementDecl, noErrorSoFar, substitutionGroupElementDeclIndex, subGrammar, typeInfo, substitutionGroupEltTypeInfo, dv, substitutionGroupEltDV); 
        }
        
        // this element is ur-type, check its substitutionGroup affiliation.
        // if there is substitutionGroup affiliation and not type definition found for this element, 
        // then grab substitutionGroup affiliation's type and give it to this element
        if ( noErrorSoFar && typeInfo == null && dv == null ) {
			typeInfo = substitutionGroupEltTypeInfo;
			dv = substitutionGroupEltDV;
        }

        if (typeInfo == null && dv==null) {
            if (noErrorSoFar) {
                // Actually this Element's type definition is ur-type;
                contentSpecType = XMLElementDecl.TYPE_ANY;
                // REVISIT, need to wait till we have wildcards implementation.
                // ADD attribute wildcards here
            }
            else {
                noErrorSoFar = false;
                // REVISIT: Localize
                reportGenericSchemaError ("untyped element : " + nameStr );
            }
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
            if (typeInfo == null) {
                fromAnotherSchema = null; // not to switch schema in this case
            }
        }

        // Now we can handle validation etc. of default and fixed attributes, 
        // since we finally have all the type information.
        if(fixedAtt != null) defaultStr = fixedStr;
        if(!defaultStr.equals("")) {
            if(typeInfo != null && 
                    (typeInfo.contentType != XMLElementDecl.TYPE_MIXED_SIMPLE &&
                     typeInfo.contentType != XMLElementDecl.TYPE_MIXED_COMPLEX &&
                    typeInfo.contentType != XMLElementDecl.TYPE_SIMPLE)) {
                // REVISIT: Localize
                reportGenericSchemaError ("e-props-correct.2.1: element " + nameStr + " has a fixed or default value and must have a mixed or simple content model");
            }
            if(typeInfo != null &&
               (typeInfo.contentType == XMLElementDecl.TYPE_MIXED_SIMPLE ||
                typeInfo.contentType == XMLElementDecl.TYPE_MIXED_COMPLEX)) {
                if (!particleEmptiable(typeInfo.contentSpecHandle))
                    reportGenericSchemaError ("e-props-correct.2.2.2: for element " + nameStr + ", the {content type} is mixed, then the {content type}'s particle must be emptiable");
            }

            try {
                if(dv == null) { // in this case validate according to xs:string
                    new StringDatatypeValidator().validate(defaultStr, null);
                } else {
                    dv.validate(defaultStr, null);
                }
            } catch (InvalidDatatypeValueException ide) {
                reportGenericSchemaError ("e-props-correct.2: invalid fixed or default value '" + defaultStr + "' in element " + nameStr);
            }
        }

        if (!defaultStr.equals("") &&
            dv != null && dv instanceof IDDatatypeValidator) {
            reportGenericSchemaError ("e-props-correct.4: If the {type definition} or {type definition}'s {content type} is or is derived from ID then there must not be a {value constraint} -- element " + nameStr);
        }

        //
        // Create element decl
        //

        int elementNameIndex     = fStringPool.addSymbol(nameStr);
        int localpartIndex = elementNameIndex;
        int uriIndex = StringPool.EMPTY_STRING;
        int enclosingScope = fCurrentScope;

        //refer to 4.3.2 in "XML Schema Part 1: Structures"
        if ( isTopLevel(elementDecl)) {
            uriIndex = fTargetNSURI;
            enclosingScope = TOP_LEVEL_SCOPE;
        }
        else if ( !formStr.equals(SchemaSymbols.ATTVAL_UNQUALIFIED) &&
                	(( formStr.equals(SchemaSymbols.ATTVAL_QUALIFIED)||
                   		fElementDefaultQualified ))) {
            
            uriIndex = fTargetNSURI;
        }
        //There can never be two elements with the same name and different type in the same scope.
        int existSuchElementIndex = fSchemaGrammar.getElementDeclIndex(uriIndex, localpartIndex, enclosingScope);
        if ( existSuchElementIndex > -1) {
            fSchemaGrammar.getElementDecl(existSuchElementIndex, fTempElementDecl);
            DatatypeValidator edv = fTempElementDecl.datatypeValidator;
            ComplexTypeInfo eTypeInfo = fSchemaGrammar.getElementComplexTypeInfo(existSuchElementIndex);
            if ( ((eTypeInfo != null)&&(eTypeInfo!=typeInfo))
                 || ((edv != null)&&(edv != dv)) )  {
                noErrorSoFar = false;
                // REVISIT: Localize
                reportGenericSchemaError("duplicate element decl in the same scope : " + 
                                         fStringPool.toString(localpartIndex));

            }
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
            System.out.println("########elementIndex:"+elementIndex+" ("+fStringPool.toString(eltQName.uri)+","
                               + fStringPool.toString(eltQName.localpart) + ")"+
                               " eltType:"+typeStr+" contentSpecType:"+contentSpecType+
                               " SpecNodeIndex:"+ contentSpecNodeIndex +" enclosingScope: " +enclosingScope +
                               " scopeDefined: " +scopeDefined+"\n");
             /***/
        }

        fSchemaGrammar.setElementComplexTypeInfo(elementIndex, typeInfo); 
        // REVISIT: should we report error if typeInfo was null?

        // mark element if its type belongs to different Schema.
        fSchemaGrammar.setElementFromAnotherSchemaURI(elementIndex, fromAnotherSchema);

        // set BlockSet, FinalSet, Nillable and Abstract for this element decl
        fSchemaGrammar.setElementDeclBlockSet(elementIndex, blockSet);
        fSchemaGrammar.setElementDeclFinalSet(elementIndex, finalSet);
        fSchemaGrammar.setElementDeclMiscFlags(elementIndex, elementMiscFlags);
        fSchemaGrammar.setElementDefault(elementIndex, defaultStr);

        // setSubstitutionGroupElementFullName
        fSchemaGrammar.setElementDeclSubstitutionGroupElementFullName(elementIndex, substitutionGroupFullName);

        //
        // key/keyref/unique processing
        //

        Element ic = XUtil.getFirstChildElementNS(elementDecl, IDENTITY_CONSTRAINTS);
        if (ic != null) {
            Integer elementIndexObj = new Integer(elementIndex);
            Vector identityConstraints = (Vector)fIdentityConstraints.get(elementIndexObj);
            if (identityConstraints == null) {
                identityConstraints = new Vector();
                fIdentityConstraints.put(elementIndexObj, identityConstraints);
            }
            while (ic != null) {
                if (DEBUG_IC_DATATYPES) {
                    System.out.println("<ICD>: adding ic for later traversal: "+ic);
                }
                identityConstraints.addElement(ic);
                ic = XUtil.getNextSiblingElementNS(ic, IDENTITY_CONSTRAINTS);
            }
        }
        
        return eltQName;

    }// end of method traverseElementDecl(Element)

    private void traverseIdentityNameConstraintsFor(int elementIndex,
                                                Vector identityConstraints)
        throws Exception {

        // iterate over identity constraints for this element
        int size = identityConstraints != null ? identityConstraints.size() : 0;
        if (size > 0) {
            // REVISIT: Use cached copy. -Ac
            XMLElementDecl edecl = new XMLElementDecl();
            fSchemaGrammar.getElementDecl(elementIndex, edecl);
            for (int i = 0; i < size; i++) {
                Element ic = (Element)identityConstraints.elementAt(i);
                String icName = ic.getLocalName();
                if ( icName.equals(SchemaSymbols.ELT_KEY) ) { 
                    traverseKey(ic, edecl);
                }
                else if ( icName.equals(SchemaSymbols.ELT_UNIQUE) ) {
                    traverseUnique(ic, edecl);
                }
                fSchemaGrammar.setElementDecl(elementIndex, edecl);

            } // loop over vector elements

        } // if size > 0

    } // traverseIdentityNameConstraints(Vector)

    private void traverseIdentityRefConstraintsFor(int elementIndex,
                                                Vector identityConstraints)
        throws Exception {

        // iterate over identity constraints for this element
        int size = identityConstraints != null ? identityConstraints.size() : 0;
        if (size > 0) {
            // REVISIT: Use cached copy. -Ac
            XMLElementDecl edecl = new XMLElementDecl();
            fSchemaGrammar.getElementDecl(elementIndex, edecl);
            for (int i = 0; i < size; i++) {
                Element ic = (Element)identityConstraints.elementAt(i);
                String icName = ic.getLocalName();
                if ( icName.equals(SchemaSymbols.ELT_KEYREF) ) {
                    traverseKeyRef(ic, edecl);
                }
                fSchemaGrammar.setElementDecl(elementIndex, edecl);

            } // loop over vector elements

        } // if size > 0

    } // traverseIdentityRefConstraints(Vector)

    private void traverseUnique(Element uElem, XMLElementDecl eDecl) 
        throws Exception {

        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(uElem, scope);

        // create identity constraint
        String uName = uElem.getAttribute(SchemaSymbols.ATT_NAME);
        if (DEBUG_IDENTITY_CONSTRAINTS) {
            System.out.println("<IC>: traverseUnique(\""+uElem.getNodeName()+"\") ["+uName+']');
        }
        String eName = getElementNameFor(uElem);
        Unique unique = new Unique(uName, eName);
        fIdentityConstraintNames.put(fTargetNSURIString+","+uName, unique);

        // get selector and fields
        traverseIdentityConstraint(unique, uElem);

        // add to element decl
        eDecl.unique.addElement(unique);

    } // traverseUnique(Element,XMLElementDecl)

    private void traverseKey(Element kElem, XMLElementDecl eDecl)
        throws Exception {

        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(kElem, scope);

        // create identity constraint
        String kName = kElem.getAttribute(SchemaSymbols.ATT_NAME);
        if (DEBUG_IDENTITY_CONSTRAINTS) {
            System.out.println("<IC>: traverseKey(\""+kElem.getNodeName()+"\") ["+kName+']');
        }
        String eName = getElementNameFor(kElem);
        Key key = new Key(kName, eName);
        fIdentityConstraintNames.put(fTargetNSURIString+","+kName, key);

        // get selector and fields
        traverseIdentityConstraint(key, kElem);

        // add to element decl
        eDecl.key.addElement(key);

    } // traverseKey(Element,XMLElementDecl)

    private void traverseKeyRef(Element krElem, XMLElementDecl eDecl) 
        throws Exception {

        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(krElem, scope);

        // create identity constraint
        String krName = krElem.getAttribute(SchemaSymbols.ATT_NAME);
        String kName = krElem.getAttribute(SchemaSymbols.ATT_REFER);
        if (DEBUG_IDENTITY_CONSTRAINTS) {
            System.out.println("<IC>: traverseKeyRef(\""+krElem.getNodeName()+"\") ["+krName+','+kName+']');
        }

        // verify that key reference "refer" attribute is valid
        String prefix = "";
        String localpart = kName;
        int colonptr = kName.indexOf(":");
        if ( colonptr > 0) {
            prefix = kName.substring(0,colonptr);
            localpart = kName.substring(colonptr+1);
        }
        String uriStr = resolvePrefixToURI(prefix);
        IdentityConstraint kId = (IdentityConstraint)fIdentityConstraintNames.get(uriStr+","+localpart); 
        if (kId== null) {
            reportSchemaError(SchemaMessageProvider.KeyRefReferNotFound,
                              new Object[]{krName,kName});
            return;
        }
        
        String eName = getElementNameFor(krElem);
        KeyRef keyRef = new KeyRef(krName, kId, eName);

        // add to element decl
        traverseIdentityConstraint(keyRef, krElem);

        // add key reference to element decl
        eDecl.keyRef.addElement(keyRef);

    } // traverseKeyRef(Element,XMLElementDecl)

    private void traverseIdentityConstraint(IdentityConstraint ic, 
                                            Element icElem) throws Exception {
        
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(icElem, scope);

        // check for <annotation> and get selector
        Element sElem = XUtil.getFirstChildElement(icElem);
        sElem = checkContent( icElem, sElem, false);
        // General Attribute Checking
        attrValues = fGeneralAttrCheck.checkAttributes(sElem, scope);

        if(!sElem.getLocalName().equals(SchemaSymbols.ELT_SELECTOR)) {
            // REVISIT: localize
            reportGenericSchemaError("The content of an identity constraint must match (annotation?, selector, field+)");
        }
        // and make sure <selector>'s content is fine:
        checkContent(icElem, XUtil.getFirstChildElement(sElem), true);

        String sText = sElem.getAttribute(SchemaSymbols.ATT_XPATH);
        sText = sText.trim();
        Selector.XPath sXpath = null;
        try {
            // REVISIT: Must get ruling from XML Schema working group
            //          regarding whether steps in the XPath must be
            //          fully qualified if the grammar has a target
            //          namespace. -Ac
            //          RESOLUTION: Yes.
            sXpath = new Selector.XPath(sText, fStringPool, 
                                        fNamespacesScope);
            Selector selector = new Selector(sXpath, ic);
            if (DEBUG_IDENTITY_CONSTRAINTS) {
                System.out.println("<IC>:   selector: "+selector);
            }
            ic.setSelector(selector);
        }
        catch (XPathException e) {
            // REVISIT: Add error message.
            reportGenericSchemaError(e.getMessage());
            return;
        }

        // get fields
        Element fElem = XUtil.getNextSiblingElement(sElem);

        while (fElem != null) {
            // General Attribute Checking
            attrValues = fGeneralAttrCheck.checkAttributes(fElem, scope);

            if(!fElem.getLocalName().equals(SchemaSymbols.ELT_FIELD))
                // REVISIT: localize
                reportGenericSchemaError("The content of an identity constraint must match (annotation?, selector, field+)");
            // and make sure <field>'s content is fine:
            checkContent(icElem, XUtil.getFirstChildElement(fElem), true);
            String fText = fElem.getAttribute(SchemaSymbols.ATT_XPATH);
            fText = fText.trim();
            try {
                // REVISIT: Must get ruling from XML Schema working group
                //          regarding whether steps in the XPath must be
                //          fully qualified if the grammar has a target
                //          namespace. -Ac
                //          RESOLUTION: Yes.
                Field.XPath fXpath = new Field.XPath(fText, fStringPool, 
                                                     fNamespacesScope);
                // REVISIT: Get datatype validator. -Ac
                // cannot statically determine type of field; not just because of descendant/union
                // but because of <any> and <anyAttribute>.  - NG
                // DatatypeValidator validator = getDatatypeValidatorFor(parent, sXpath, fXpath);
                // if (DEBUG_IC_DATATYPES) {
                //  System.out.println("<ICD>: datatype validator: "+validator);
                // }
                // must find DatatypeValidator in the Validator...
                Field field = new Field(fXpath, ic);
                if (DEBUG_IDENTITY_CONSTRAINTS) {
                    System.out.println("<IC>:   field:    "+field);
                }
                ic.addField(field);
            }
            catch (XPathException e) {
                // REVISIT: Add error message.
                reportGenericSchemaError(e.getMessage());
                return;
            }
            fElem = XUtil.getNextSiblingElement(fElem);
        }

    } // traverseIdentityConstraint(IdentityConstraint,Element)

    /* This code is no longer used because datatypes can't be found statically for ID constraints.
    private DatatypeValidator getDatatypeValidatorFor(Element element, 
                                                      Selector.XPath sxpath, 
                                                      Field.XPath fxpath)
        throws Exception {

        // variables
        String ename = element.getAttribute("name");
        if (DEBUG_IC_DATATYPES) {
            System.out.println("<ICD>: XMLValidator#getDatatypeValidatorFor("+
                               ename+','+sxpath+','+fxpath+')');
        }
        int localpart = fStringPool.addSymbol(ename);
        String targetNamespace = fSchemaRootElement.getAttribute("targetNamespace");
        int uri = fStringPool.addSymbol(targetNamespace);
        int edeclIndex = fSchemaGrammar.getElementDeclIndex(uri, localpart, 
                                                            Grammar.TOP_LEVEL_SCOPE);

        // walk selector
        XPath.LocationPath spath = sxpath.getLocationPath();
        XPath.Step[] ssteps = spath.steps;
        for (int i = 0; i < ssteps.length; i++) {
            XPath.Step step = ssteps[i];
            XPath.Axis axis = step.axis;
            XPath.NodeTest nodeTest = step.nodeTest;
            switch (axis.type) {
                case XPath.Axis.ATTRIBUTE: {
                    // REVISIT: Add message. -Ac
                    reportGenericSchemaError("not allowed to select attribute");
                    return null;
                }
                case XPath.Axis.CHILD: {
                    int index = fSchemaGrammar.getElementDeclIndex(nodeTest.name, edeclIndex);
                    if (index == -1) {
                        index = fSchemaGrammar.getElementDeclIndex(nodeTest.name, Grammar.TOP_LEVEL_SCOPE);
                    }
                    if (index == -1) {
                        // REVISIT: Add message. -Ac
                        reportGenericSchemaError("no such element \""+fStringPool.toString(nodeTest.name.rawname)+'"');
                        return null;
                    }
                    edeclIndex = index;
                    break;
                }
                case XPath.Axis.SELF: {
                    // no-op
                    break;
                }
                default: {
                    // REVISIT: Add message. -Ac
                    reportGenericSchemaError("invalid selector axis");
                    return null;
                }
            }
        }

        // walk field
        XPath.LocationPath fpath = fxpath.getLocationPath();
        XPath.Step[] fsteps = fpath.steps;
        for (int i = 0; i < fsteps.length; i++) {
            XPath.Step step = fsteps[i];
            XPath.Axis axis = step.axis;
            XPath.NodeTest nodeTest = step.nodeTest;
            switch (axis.type) {
                case XPath.Axis.ATTRIBUTE: {
                    if (i != fsteps.length - 1) {
                        // REVISIT: Add message. -Ac
                        reportGenericSchemaError("attribute must be last step");
                        return null;
                    }
                    // look up validator
                    int adeclIndex = fSchemaGrammar.getAttributeDeclIndex(edeclIndex, nodeTest.name);
                    if (adeclIndex == -1) {
                        // REVISIT: Add message. -Ac
                        reportGenericSchemaError("no such attribute \""+fStringPool.toString(nodeTest.name.rawname)+'"');
                    }
                    XMLAttributeDecl adecl = new XMLAttributeDecl();
                    fSchemaGrammar.getAttributeDecl(adeclIndex, adecl);
                    DatatypeValidator validator = adecl.datatypeValidator;
                    return validator;
                }
                case XPath.Axis.CHILD: {
                    int index = fSchemaGrammar.getElementDeclIndex(nodeTest.name, edeclIndex);
                    if (index == -1) {
                        index = fSchemaGrammar.getElementDeclIndex(nodeTest.name, Grammar.TOP_LEVEL_SCOPE);
                    }
                    if (index == -1) {
                        // REVISIT: Add message. -Ac
                        reportGenericSchemaError("no such element \""+fStringPool.toString(nodeTest.name.rawname)+'"');
                        return null;
                    }
                    edeclIndex = index;
                    if (i < fsteps.length - 1) {
                        break;
                    }
                    // NOTE: Let fall through to self case so that we
                    //       avoid duplicating code. -Ac
                }
                case XPath.Axis.SELF: {
                    // look up validator, if needed
                    if (i == fsteps.length - 1) {
                        XMLElementDecl edecl = new XMLElementDecl();
                        fSchemaGrammar.getElementDecl(edeclIndex, edecl);
                        if (edecl.type != XMLElementDecl.TYPE_SIMPLE) {
                            // REVISIT: Add message. -Ac
                            reportGenericSchemaError("selected element is not of simple type");
                            return null;
                        }
                        DatatypeValidator validator = edecl.datatypeValidator;
                        if (validator == null) validator = new StringDatatypeValidator();
                        return validator;
                    }
                    break;
                }
                default: {
                    // REVISIT: Add message. -Ac
                    reportGenericSchemaError("invalid selector axis");
                    return null;
                }
            }
        }

        // no validator!
        // REVISIT: Add message. -Ac
        reportGenericSchemaError("No datatype validator for field "+fxpath+
                                 " of element "+ename);
        return null;

    } // getDatatypeValidatorFor(XPath):DatatypeValidator
    */ // back in to live code...

    private String getElementNameFor(Element icnode) {
        Element enode = (Element)icnode.getParentNode();
        String ename = enode.getAttribute("name");
        if (ename.length() == 0) {
            ename = enode.getAttribute("ref");
        }
        return ename;
    } // getElementNameFor(Element):String

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
    
    int getPrefixIndex(String fullName){
        int colonAt = fullName.indexOf(":"); 
        String prefix = "";
        if (  colonAt > -1 ) {
            prefix = fullName.substring(0,colonAt);
        }
        return fStringPool.addSymbol(prefix);
    }

    String getPrefix(String fullName){
        int colonAt = fullName.indexOf(":"); 
        String prefix = "";
        if (  colonAt > -1 ) {
            prefix = fullName.substring(0,colonAt);
        }
        return prefix;
    }
    
    private void checkSubstitutionGroupOK(Element elementDecl, Element substitutionGroupElementDecl, 
            boolean noErrorSoFar, int substitutionGroupElementDeclIndex, SchemaGrammar substitutionGroupGrammar, ComplexTypeInfo typeInfo, 
            ComplexTypeInfo substitutionGroupEltTypeInfo, DatatypeValidator dv, 
            DatatypeValidator substitutionGroupEltDV)  throws Exception {
        // here we must do two things:
        // 1.  Make sure there actually *is* a relation between the types of
        // the element being nominated and the element doing the nominating;
        // (see PR 3.3.6 point #3 in the first tableau, for instance; this
        // and the corresponding tableaux from 3.4.6 and 3.14.6 rule out the nominated
        // element having an anonymous type declaration.
        // 2.  Make sure the nominated element allows itself to be nominated by
        // an element with the given type-relation.
        // Note:  we assume that (complex|simple)Type processing checks
        // whether the type in question allows itself to
        // be modified as this element desires.  

        // Check for type relationship;
        // that is, make sure that the type we're deriving has some relationship
        // to substitutionGroupElt's type.
        if (typeInfo != null) {
            int derivationMethod = typeInfo.derivedBy;
            if(typeInfo.baseComplexTypeInfo == null) {
                if (typeInfo.baseDataTypeValidator != null) { // take care of complexType based on simpleType case...
                    DatatypeValidator dTemp = typeInfo.baseDataTypeValidator; 
                    for(; dTemp != null; dTemp = dTemp.getBaseValidator()) {
                        // WARNING!!!  This uses comparison by reference andTemp is thus inherently suspect!
                        if(dTemp == substitutionGroupEltDV) break;
                    }
                    if (dTemp == null) {
                        if(substitutionGroupEltDV instanceof UnionDatatypeValidator) {
                            // dv must derive from one of its members...
                            Vector subUnionMemberDV = ((UnionDatatypeValidator)substitutionGroupEltDV).getBaseValidators();
                            int subUnionSize = subUnionMemberDV.size();
                            boolean found = false;
                            for (int i=0; i<subUnionSize && !found; i++) {
                                DatatypeValidator dTempSub = (DatatypeValidator)subUnionMemberDV.elementAt(i); 
                                DatatypeValidator dTempOrig = typeInfo.baseDataTypeValidator; 
                                for(; dTempOrig != null; dTempOrig = dTempOrig.getBaseValidator()) {
                                    // WARNING!!!  This uses comparison by reference andTemp is thus inherently suspect!
                                    if(dTempSub == dTempOrig) {
                                        found = true;
                                        break;
                                    }
                                }
                            }
                            if(!found) {
                                // REVISIT:  localize
                                reportGenericSchemaError("Element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) + " has a type which does not derive from the type of the element at the head of the substitution group");
                                noErrorSoFar = false;
                            }
                        } else {
                            // REVISIT:  localize
                            reportGenericSchemaError("Element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) + " has a type which does not derive from the type of the element at the head of the substitution group");
                            noErrorSoFar = false;
                        }
                    } else { // now let's see if substitutionGroup element allows this:
                        if((derivationMethod & substitutionGroupGrammar.getElementDeclFinalSet(substitutionGroupElementDeclIndex)) != 0) {
                            noErrorSoFar = false;
                            // REVISIT:  localize
                            reportGenericSchemaError("element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) 
                                + " cannot be part of the substitution group headed by " 
                                + substitutionGroupElementDecl.getAttribute(SchemaSymbols.ATT_NAME));
                        } 
                    }
                } else {
                    // REVISIT:  localize
                    reportGenericSchemaError("Element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) + " which is part of a substitution must have a type which derives from the type of the element at the head of the substitution group");
                    noErrorSoFar = false;
                }
            } else {
                String eltBaseName = typeInfo.baseComplexTypeInfo.typeName;
                ComplexTypeInfo subTypeInfo = substitutionGroupEltTypeInfo;
                for (; subTypeInfo != null && !subTypeInfo.typeName.equals(eltBaseName); subTypeInfo = subTypeInfo.baseComplexTypeInfo);
                if (subTypeInfo == null) { // then this type isn't in the chain...
                    // REVISIT:  localize
                    reportGenericSchemaError("Element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) + " has a type whose base is " + eltBaseName + "; this basetype does not derive from the type of the element at the head of the substitution group");
                    noErrorSoFar = false;
                } else { // type is fine; does substitutionElement allow this?
                    if((derivationMethod & substitutionGroupGrammar.getElementDeclFinalSet(substitutionGroupElementDeclIndex)) != 0) {
                        noErrorSoFar = false;
                        // REVISIT:  localize
                        reportGenericSchemaError("element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) 
                            + " cannot be part of the substitution group headed by " 
                            + substitutionGroupElementDecl.getAttribute(SchemaSymbols.ATT_NAME));
                    } 
                }
            } 
        } else if (dv != null) { // do simpleType case...
            // first, check for type relation.
            if (!(checkSimpleTypeDerivationOK(dv,substitutionGroupEltDV))) {
               // REVISIT:  localize
               reportGenericSchemaError("Element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) + " has a type which does not derive from the type of the element at the head of the substitution group");
               noErrorSoFar = false;
            }
            else { // now let's see if substitutionGroup element allows this:
                if((SchemaSymbols.RESTRICTION & substitutionGroupGrammar.getElementDeclFinalSet(substitutionGroupElementDeclIndex)) != 0) {
                    noErrorSoFar = false;
                    // REVISIT:  localize
                    reportGenericSchemaError("element " + elementDecl.getAttribute(SchemaSymbols.ATT_NAME) 
                        + " cannot be part of the substitution group headed by " 
                        + substitutionGroupElementDecl.getAttribute(SchemaSymbols.ATT_NAME));
                } 
            } 
        } 
    }
    
    //
    // A utility method to check whether a particular datatypevalidator d, was validly 
    // derived from another datatypevalidator, b
    // 
    private boolean checkSimpleTypeDerivationOK(DatatypeValidator d, DatatypeValidator b) {
       DatatypeValidator dTemp = d; 
       for(; dTemp != null; dTemp = dTemp.getBaseValidator()) {
           // WARNING!!!  This uses comparison by reference andTemp is thus inherently suspect!
           if(dTemp == b) break;
       }
       if (dTemp == null) {
           // now if b is a union, then we can
           // derive from it if we derive from any of its members' types.  
           if(b instanceof UnionDatatypeValidator) {
               // d must derive from one of its members...
               Vector subUnionMemberDV = ((UnionDatatypeValidator)b).getBaseValidators();
               int subUnionSize = subUnionMemberDV.size();
               boolean found = false;
               for (int i=0; i<subUnionSize && !found; i++) {
                   DatatypeValidator dTempSub = (DatatypeValidator)subUnionMemberDV.elementAt(i); 
                   DatatypeValidator dTempOrig = d; 
                   for(; dTempOrig != null; dTempOrig = dTempOrig.getBaseValidator()) {
                       // WARNING!!!  This uses comparison by reference andTemp is thus inherently suspect!
                       if(dTempSub == dTempOrig) {
                           found = true;
                           break;
                       }
                   }
               }
               if(!found) {
                  return false;
               }
           } else {
               return false;         
           }
       } 

    return true;
    }

    // this originally-simple method is much -complicated by the fact that, when we're 
    // redefining something, we've not only got to look at the space of the thing
    // we're redefining but at the original schema too.
    // The idea is to start from the top, then go down through
    // our list of schemas until we find what we aant.  
    // This should not often be necessary, because we've processed
    // all redefined schemas, but three are conditions in which
    // not all elements so redefined may have been promoted to
    // the topmost level.  
    private Element getTopLevelComponentByName(String componentCategory, String name) throws Exception {
        Element child = null;
        SchemaInfo curr = fSchemaInfoListRoot; 
        for (; curr != null || curr == fSchemaInfoListRoot; curr = curr.getNext()) {
            if (curr != null) curr.restore();
            if ( componentCategory.equals(SchemaSymbols.ELT_GROUP) ) {
                child = (Element) fSchemaGrammar.topLevelGroupDecls.get(name);
            }
            else if ( componentCategory.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP ) ) {
                child = (Element) fSchemaGrammar.topLevelAttrGrpDecls.get(name);
            }
            else if ( componentCategory.equals(SchemaSymbols.ELT_ATTRIBUTE ) ) {
                child = (Element) fSchemaGrammar.topLevelAttrDecls.get(name);
            }

            if (child != null ) {
                break;
            }
            
            child = XUtil.getFirstChildElement(fSchemaRootElement);

            if (child == null) {
                continue;
            }

            while (child != null ){
                if ( child.getLocalName().equals(componentCategory)) {
                    if (child.getAttribute(SchemaSymbols.ATT_NAME).equals(name)) {
                        break;
                    }
                } else if (fRedefineSucceeded && child.getLocalName().equals(SchemaSymbols.ELT_REDEFINE)) {
                    Element gChild = XUtil.getFirstChildElement(child);
                    while (gChild != null ){
                        if (gChild.getLocalName().equals(componentCategory)) {
                            if (gChild.getAttribute(SchemaSymbols.ATT_NAME).equals(name)) {
                                break;
                            }
                        }
                        gChild = XUtil.getNextSiblingElement(gChild);
                    }
                    if (gChild != null) {
                        child = gChild;
                        break;
                    }
                }
                child = XUtil.getNextSiblingElement(child);
            }
            if (child != null || fSchemaInfoListRoot == null) break;
        }
        // have to reset fSchemaInfoList
        if(curr != null) 
            curr.restore();
        else
            if (fSchemaInfoListRoot != null) 
                fSchemaInfoListRoot.restore();
        return child;
    }

    private boolean isTopLevel(Element component) {
        String parentName = component.getParentNode().getLocalName();
		return (parentName.endsWith(SchemaSymbols.ELT_SCHEMA))
		    || (parentName.endsWith(SchemaSymbols.ELT_REDEFINE)) ; 
    }
    
    DatatypeValidator getTypeValidatorFromNS(String newSchemaURI, String localpart) throws Exception {
        // The following impl is for the case where every Schema Grammar has its own instance of DatatypeRegistry.
        // Now that we have only one DataTypeRegistry used by all schemas. this is not needed.
        /*****
        Grammar grammar = fGrammarResolver.getGrammar(newSchemaURI);
        if (grammar != null && grammar instanceof SchemaGrammar) {
            SchemaGrammar sGrammar = (SchemaGrammar) grammar;
            DatatypeValidator dv = (DatatypeValidator) fSchemaGrammar.getDatatypeRegistry().getDatatypeValidator(localpart);
            return dv;
        }
        else {
            reportGenericSchemaError("could not resolve URI : " + newSchemaURI + " to a SchemaGrammar in getTypeValidatorFromNS");
        }
        return null;
        /*****/
        return getDatatypeValidator(newSchemaURI, localpart);
    }

    ComplexTypeInfo getTypeInfoFromNS(String newSchemaURI, String localpart) throws Exception {
        Grammar grammar = fGrammarResolver.getGrammar(newSchemaURI);
        if (grammar != null && grammar instanceof SchemaGrammar) {
            SchemaGrammar sGrammar = (SchemaGrammar) grammar;
            ComplexTypeInfo typeInfo = (ComplexTypeInfo) sGrammar.getComplexTypeRegistry().get(newSchemaURI+","+localpart);
            return typeInfo;
        }
        else {
            reportGenericSchemaError("could not resolve URI : " + newSchemaURI + " to a SchemaGrammar in getTypeInfoFromNS");
        }
        return null;
    }
    
    DatatypeValidator getElementDeclTypeValidatorFromNS(String newSchemaURI, String localpart) throws Exception {
        Grammar grammar = fGrammarResolver.getGrammar(newSchemaURI);
        if (grammar != null && grammar instanceof SchemaGrammar) {
            SchemaGrammar sGrammar = (SchemaGrammar) grammar;
            int eltIndex = sGrammar.getElementDeclIndex(fStringPool.addSymbol(newSchemaURI), 
                                                        fStringPool.addSymbol(localpart), 
                                                        TOP_LEVEL_SCOPE);

            DatatypeValidator dv = null;
            if (eltIndex>-1) {
                sGrammar.getElementDecl(eltIndex, fTempElementDecl);
                dv = fTempElementDecl.datatypeValidator;
            }
            else {
                reportGenericSchemaError("could not find global element : '" + localpart 
                                         + " in the SchemaGrammar "+newSchemaURI);
            }
            return dv;
        }
        else {
            reportGenericSchemaError("could not resolve URI : " + newSchemaURI
                                      + " to a SchemaGrammar in getELementDeclTypeValidatorFromNS");
        }
        return null;
    }

    ComplexTypeInfo getElementDeclTypeInfoFromNS(String newSchemaURI, String localpart) throws Exception {
        Grammar grammar = fGrammarResolver.getGrammar(newSchemaURI);
        if (grammar != null && grammar instanceof SchemaGrammar) {
            SchemaGrammar sGrammar = (SchemaGrammar) grammar;
            int eltIndex = sGrammar.getElementDeclIndex(fStringPool.addSymbol(newSchemaURI), 
                                                              fStringPool.addSymbol(localpart), 
                                                              TOP_LEVEL_SCOPE);
            ComplexTypeInfo typeInfo = null;
            if (eltIndex>-1) {
                 typeInfo = sGrammar.getElementComplexTypeInfo(eltIndex);
            }
            else {
                reportGenericSchemaError("could not find global element : '" + localpart 
                                         + " in the SchemaGrammar "+newSchemaURI);

            }
            return typeInfo;
        }
        else {
            reportGenericSchemaError("could not resolve URI : " + newSchemaURI 
                                     + " to a SchemaGrammar in getElementDeclTypeInfoFromNS");
        }
        return null;
    }



    /**
     * Traverses notation declaration 
     * and saves it in a registry.
     * Notations are stored in registry with the following
     * key: "uri:localname"
     * 
     * @param notation child <notation>
     * @return  local name of notation
     * @exception Exception
     */
    private String traverseNotationDecl( Element notation ) throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(notation, scope);

        String name = notation.getAttribute(SchemaSymbols.ATT_NAME);
        String qualifiedName =name;
        if (fTargetNSURIString.length () != 0) {
            qualifiedName = fTargetNSURIString+":"+name;
        }
        if (fNotationRegistry.get(qualifiedName)!=null) {
            return name;
        }
        String publicId = notation.getAttribute(SchemaSymbols.ATT_PUBLIC);
        String systemId = notation.getAttribute(SchemaSymbols.ATT_SYSTEM);
        if (publicId.length() == 0 && systemId.length() == 0) {
            //REVISIT: update error messages
            reportGenericSchemaError("<notation> declaration is invalid");
        }
        if (name.equals("")) {
            //REVISIT: update error messages
            reportGenericSchemaError("<notation> declaration does not have a name");

        }
        
        fNotationRegistry.put(qualifiedName, name);

        //we don't really care if something inside <notation> is wrong..
        checkContent( notation, XUtil.getFirstChildElement(notation), true );
        
        //REVISIT: wait for DOM L3 APIs to pass info to application
        //REVISIT: SAX2 does not support notations. API should be changed.
        return name;
    }
    
    /**
     * This methods will traverse notation from current schema,
     * as well as from included or imported schemas
     * 
     * @param notationName
     *               localName of notation
     * @param uriStr uriStr for schema grammar
     * @return  return local name for Notation (if found), otherwise
     *         return empty string;
     * @exception Exception
     */
    private String traverseNotationFromAnotherSchema( String notationName , String uriStr ) throws Exception {
        
        SchemaGrammar aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uriStr);
        if (uriStr == null || aGrammar==null ||! (aGrammar instanceof SchemaGrammar) ) {
            // REVISIT: Localize
            reportGenericSchemaError("!!Schema not found in #traverseNotationDeclFromAnotherSchema, "+
                                     "schema uri: " + uriStr
                                     +", groupName: " + notationName);
            return "";
        }


        String savedNSURIString = fTargetNSURIString;
        fTargetNSURIString = fStringPool.toString(fStringPool.addSymbol(aGrammar.getTargetNamespaceURI()));
        if (DEBUGGING) {
            System.out.println("[traverseFromAnotherSchema]: " + fTargetNSURIString);
        }

        String qualifiedName = fTargetNSURIString + ":" + notationName;
        String localName = (String)fNotationRegistry.get(qualifiedName);

        if(localName != null ) 	// we've already traversed this notation
            return localName;

        //notation decl has not been traversed yet
        Element notationDecl = (Element) aGrammar.topLevelNotationDecls.get((Object)notationName);
        if (notationDecl == null) {
            // REVISIT: Localize
            reportGenericSchemaError( "no notation named \"" + notationName 
                                      + "\" was defined in schema : " + uriStr);
            return "";
        }

        localName = traverseNotationDecl(notationDecl);
        fTargetNSURIString = savedNSURIString;
        return localName;

    } // end of method traverseNotationFromAnotherSchema


    /**
     * Traverse Group Declaration.
     * 
     * <group 
     *         id = ID 
     *         maxOccurs = string 
     *         minOccurs = nonNegativeInteger 
     *         name = NCName 
     *         ref = QName>
     *   Content: (annotation? , (all | choice | sequence)?)
     * <group/>
     * 
     * @param elementDecl
     * @return 
     * @exception Exception
     */
    private int traverseGroupDecl( Element groupDecl ) throws Exception {

        // General Attribute Checking
        int scope = isTopLevel(groupDecl)?
                    GeneralAttrCheck.ELE_CONTEXT_GLOBAL:
                    GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(groupDecl, scope);

        String groupName = groupDecl.getAttribute(SchemaSymbols.ATT_NAME);
        String ref = groupDecl.getAttribute(SchemaSymbols.ATT_REF);
		Element child = checkContent( groupDecl, XUtil.getFirstChildElement(groupDecl), true );

        if (!ref.equals("")) {
            if (isTopLevel(groupDecl)) 
                // REVISIT:  localize 
                reportGenericSchemaError ( "A group with \"ref\" present must not have <schema> or <redefine> as its parent");
            if (!groupName.equals(""))
                // REVISIT:  localize 
                reportGenericSchemaError ( "group " + groupName + " cannot refer to another group, but it refers to " + ref);

            // there should be no children for <group ref="...">
            if (XUtil.getFirstChildElement(groupDecl)!=null) 
                reportGenericSchemaError ( "A group with \"ref\" present must not have children");
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
            Object contentSpecHolder = fGroupNameRegistry.get(uriStr + "," + localpart);
            if(contentSpecHolder != null ) {	// we may have already traversed this group
                boolean fail = false;
                int contentSpecHolderIndex = 0;
                try {
                    contentSpecHolderIndex = ((Integer)contentSpecHolder).intValue();
                } catch (ClassCastException c) {
                    fail = true;
                }
                if(!fail) {
		            return contentSpecHolderIndex;
                }
            }

            // Check if we are in the middle of traversing this group (i.e. circular references)
            if (fCurrentGroupNameStack.search((Object)localpart) > - 1) {
                reportGenericSchemaError("mg-props-correct: Circular definition for group " + localpart); 
                return -2;
            }

            int contentSpecIndex = -1;
            Element referredGroup = getTopLevelComponentByName(SchemaSymbols.ELT_GROUP,localpart);
            if (referredGroup == null) {
                // REVISIT: Localize
                reportGenericSchemaError("Group " + localpart + " not found in the Schema");
                //REVISIT, this should be some custom Exception
                //throw new RuntimeException("Group " + localpart + " not found in the Schema");
            }
            else {
                contentSpecIndex = traverseGroupDecl(referredGroup);
            }
            
            return contentSpecIndex;
        } else if (groupName.equals(""))
            // REVISIT: Localize
            reportGenericSchemaError("a <group> must have a name or a ref present");
		String qualifiedGroupName = fTargetNSURIString + "," + groupName;
		Object contentSpecHolder = fGroupNameRegistry.get(qualifiedGroupName);
        if(contentSpecHolder != null ) {	// we may have already traversed this group
            boolean fail = false;
            int contentSpecHolderIndex = 0;
            try {
                contentSpecHolderIndex = ((Integer)contentSpecHolder).intValue();
            } catch (ClassCastException c) {
                fail = true;
            }
            if(!fail) {
		        return contentSpecHolderIndex;
            }
        }

	// if we're here then we're traversing a top-level group that we've never seen before.
        // Push the group name onto a stack, so that we can check for circular groups
        fCurrentGroupNameStack.push(groupName);

        // Save the scope and set the current scope to -1 
        int savedScope = fCurrentScope;
        fCurrentScope = -1;

        int index = -2;

        boolean illegalChild = false;
		String childName = 
        	(child != null) ? child.getLocalName() : "";

        if (childName.equals(SchemaSymbols.ELT_ALL)) {
            index = traverseAll(child);
        } 
        else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
            index = traverseChoice(child);
        } 
        else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
            index = traverseSequence(child);
        } 
        else if (!childName.equals("") || (child != null && XUtil.getNextSiblingElement(child) != null)) {
            illegalChild = true;
            reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                              new Object [] { "group", childName });
        }

        //Must have all or choice or sequence child.
        if (child == null) {
            reportGenericSchemaError("Named group must contain an 'all', 'choice' or 'sequence' child");
        }
        else if (XUtil.getNextSiblingElement(child) != null) {
            illegalChild = true;
            reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                              new Object [] { "group", childName });
        }
        if ( ! illegalChild && child != null) {
            index = handleOccurrences(index, child, CHILD_OF_GROUP);
        }

	contentSpecHolder = new Integer(index);
        fCurrentGroupNameStack.pop();
        fCurrentScope = savedScope;
	fGroupNameRegistry.put(qualifiedGroupName, contentSpecHolder);
        return index;
    }

    private int traverseGroupDeclFromAnotherSchema( String groupName , String uriStr ) throws Exception {
        
        SchemaGrammar aGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uriStr);
        if (uriStr == null || aGrammar==null ||! (aGrammar instanceof SchemaGrammar) ) {
            // REVISIT: Localize
            reportGenericSchemaError("!!Schema not found in #traverseGroupDeclFromAnotherSchema, "+
                                     "schema uri: " + uriStr
                                     +", groupName: " + groupName);
            return -1;
        }


        Element groupDecl = (Element) aGrammar.topLevelGroupDecls.get((Object)groupName);
        if (groupDecl == null) {
            // REVISIT: Localize
            reportGenericSchemaError( "no group named \"" + groupName 
                                      + "\" was defined in schema : " + uriStr);
            return -1;
        }

        NamespacesScope saveNSMapping = fNamespacesScope;
        int saveTargetNSUri = fTargetNSURI;
        fTargetNSURI = fStringPool.addSymbol(aGrammar.getTargetNamespaceURI());
        fNamespacesScope = aGrammar.getNamespacesScope();

	Element child = checkContent( groupDecl, XUtil.getFirstChildElement(groupDecl), true );

	String qualifiedGroupName = fTargetNSURIString + "," + groupName;
	Object contentSpecHolder = fGroupNameRegistry.get(qualifiedGroupName);
    if(contentSpecHolder != null ) {	// we may have already traversed this group
        boolean fail = false;
        int contentSpecHolderIndex  = 0;
        try {
            contentSpecHolderIndex = ((Integer)contentSpecHolder).intValue();
        } catch (ClassCastException c) {
            fail = true;
        }
        if(!fail) {
            return contentSpecHolderIndex;
        }
    }

        // ------------------------------------
	// if we're here then we're traversing a top-level group that we've never seen before.

        int index = -2;

        boolean illegalChild = false;
	String childName = (child != null) ? child.getLocalName() : "";
        if (childName.equals(SchemaSymbols.ELT_ALL)) {
            index = traverseAll(child);
        } 
        else if (childName.equals(SchemaSymbols.ELT_CHOICE)) {
            index = traverseChoice(child);
        } 
        else if (childName.equals(SchemaSymbols.ELT_SEQUENCE)) {
            index = traverseSequence(child);
        } 
        else if (!childName.equals("") || (child != null && XUtil.getNextSiblingElement(child) != null)) {
            illegalChild = true;
            reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
                              new Object [] { "group", childName });
        }
        if ( ! illegalChild && child != null) {
            index = handleOccurrences( index, child);
        }

	contentSpecHolder = new Integer(index);
	fGroupNameRegistry.put(qualifiedGroupName, contentSpecHolder);
	fNamespacesScope = saveNSMapping;
	fTargetNSURI = saveTargetNSUri;
        return index;


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
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(sequenceDecl, scope);
            
        Element child = checkContent(sequenceDecl, XUtil.getFirstChildElement(sequenceDecl), true);

        int csnType = XMLContentSpec.CONTENTSPECNODE_SEQ;

        int left = -2;
        int right = -2;
        boolean hadContent = false;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            int index = -2;

            boolean seeParticle = false;
            String childName = child.getLocalName();
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

                // A content type of all can only appear
                // as the content type of a complex type definition.
                if (hasAllContent(index)) {
                    reportSchemaError(SchemaMessageProvider.AllContentLimited,
                                      new Object [] { "sequence" });
                    continue;
                }

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
            else if (childName.equals(SchemaSymbols.ELT_ANY)) {
                index = traverseAny(child);
                seeParticle = true;
            } 
            else {
                reportSchemaError(
                             SchemaMessageProvider.SeqChoiceContentRestricted,
                             new Object [] { "sequence", childName });
                continue;
            }

            if (index != -2)
                hadContent = true;

            if (seeParticle) {
                index = handleOccurrences( index, child);
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

        if (hadContent) {
            if (right != -2 || fSchemaGrammar.getDeferContentSpecExpansion())
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right,
                                                         false);
        }

        return left;
    }
    
    /**
    *
    * Traverse the Choice declaration
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
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(choiceDecl, scope);
            
        // REVISIT: traverseChoice, traverseSequence can be combined
        Element child = checkContent(choiceDecl, XUtil.getFirstChildElement(choiceDecl), true);

        int csnType = XMLContentSpec.CONTENTSPECNODE_CHOICE;

        int left = -2;
        int right = -2;
        boolean hadContent = false;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            int index = -2;

            boolean seeParticle = false;
            String childName = child.getLocalName();
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

                // A model group whose {compositor} is "all" can only appear
                // as the {content type} of a complex type definition.
                if (hasAllContent(index)) {
                    reportSchemaError(SchemaMessageProvider.AllContentLimited,
                                      new Object [] { "choice" });
                    continue;
                }

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
            else if (childName.equals(SchemaSymbols.ELT_ANY)) {
                index = traverseAny(child);
                seeParticle = true;
            } 
            else {
                reportSchemaError(
                              SchemaMessageProvider.SeqChoiceContentRestricted,
                              new Object [] { "choice", childName });
                continue;
            }

            if (index != -2)
                hadContent = true;

            if (seeParticle) {
                index = handleOccurrences( index, child);
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


        if (hadContent) {
            if (right != -2 || fSchemaGrammar.getDeferContentSpecExpansion())
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right,
                                                         false);
        }
        return left;
    }
    

   /**
    *
    * Traverse the "All" declaration
    *
    * <all
    *   id = ID
    *   maxOccurs = 1 : 1
    *   minOccurs = (0 | 1) : 1>
    *   Content: (annotation? , element*)
    * </all>
    **/

    int traverseAll(Element allDecl) throws Exception {
        // General Attribute Checking
        int scope = GeneralAttrCheck.ELE_CONTEXT_LOCAL;
        Hashtable attrValues = fGeneralAttrCheck.checkAttributes(allDecl, scope);

        Element child = checkContent(allDecl,
                                     XUtil.getFirstChildElement(allDecl), true);

        int csnType = XMLContentSpec.CONTENTSPECNODE_ALL;

        int left = -2;
        int right = -2;
        boolean hadContent = false;

        for (;
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            int index = -2;

            String childName = child.getLocalName();

            // Only elements are allowed in <all>
            if (childName.equals(SchemaSymbols.ELT_ELEMENT)) {
                QName eltQName = traverseElementDecl(child);
                index = fSchemaGrammar.addContentSpecNode(
                                           XMLContentSpec.CONTENTSPECNODE_LEAF,
                                           eltQName.localpart,
                                           eltQName.uri, 
                                           false);

                index = handleOccurrences(index, child, PROCESSING_ALL);
            } 
            else {
                reportSchemaError(SchemaMessageProvider.AllContentRestricted,
                                  new Object [] { childName });
                continue;
            }

            hadContent = true;

            if (left == -2) { 
                left = index;
            } else if (right == -2) {
                right = index;
            } else {
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right,
                                                         false);
                right = index;
            }
        }

        if (hadContent) {
            if (right != -2 || fSchemaGrammar.getDeferContentSpecExpansion())
                left = fSchemaGrammar.addContentSpecNode(csnType, left, right,
                                                         false);
        }

        return left;
    }

    // Determines whether a content spec tree represents an "all" content model
    private boolean hasAllContent(int contentSpecIndex) {
        // If the content is not empty, is the top node ALL?
        if (contentSpecIndex > -1) {
            XMLContentSpec content = new XMLContentSpec();
            fSchemaGrammar.getContentSpec(contentSpecIndex, content);

            // An ALL node could be optional, so we have to be prepared
            // to look one level below a ZERO_OR_ONE node for an ALL.
            if (content.type == XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE) {
                fSchemaGrammar.getContentSpec(content.value, content);
            }

            return (content.type == XMLContentSpec.CONTENTSPECNODE_ALL);
        }

        return false;
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
    
       
    private int parseSimpleFinal (String finalString) throws Exception
    {
            if ( finalString.equals (SchemaSymbols.ATTVAL_POUNDALL) ) {
                    return SchemaSymbols.ENUMERATION+SchemaSymbols.RESTRICTION+SchemaSymbols.LIST;
            } else {
                    int enumerate = 0;
                    int restrict = 0;
                    int list = 0;

                    StringTokenizer t = new StringTokenizer (finalString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ("restriction in set twice");
                                    }
                            } else if ( token.equals (SchemaSymbols.ELT_LIST) ) {
                                    if ( list == 0 ) {
                                            list = SchemaSymbols.LIST;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ("list in set twice");
                                    }
                            }
                            else {
                                // REVISIT: Localize
                                reportGenericSchemaError (  "Invalid value (" + 
                                                            finalString +
                                                            ")" );
                            }
                    }

                    return enumerate+list;
            }
    }


    private int parseDerivationSet (String finalString)  throws Exception
    {
            if ( finalString.equals (SchemaSymbols.ATTVAL_POUNDALL) ) {
                    return SchemaSymbols.EXTENSION+SchemaSymbols.RESTRICTION;
            } else {
                    int extend = 0;
                    int restrict = 0;

                    StringTokenizer t = new StringTokenizer (finalString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ATTVAL_EXTENSION) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EXTENSION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "extension already in set" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "restriction already in set" );
                                    }
                            } else {
                                // REVISIT: Localize
                                    reportGenericSchemaError ( "Invalid final value (" + finalString + ")" );
                            }
                    }

                    return extend+restrict;
            }
    }

    private int parseBlockSet (String blockString)  throws Exception
    {
            if( blockString == null) 
                return fBlockDefault;
            else if ( blockString.equals (SchemaSymbols.ATTVAL_POUNDALL) ) {
                    return SchemaSymbols.SUBSTITUTION+SchemaSymbols.EXTENSION+SchemaSymbols.RESTRICTION;
            } else {
                    int extend = 0;
                    int restrict = 0;
                    int substitute = 0;

                    StringTokenizer t = new StringTokenizer (blockString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ATTVAL_SUBSTITUTION) ) {
                                    if ( substitute == 0 ) {
                                            substitute = SchemaSymbols.SUBSTITUTION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "The value 'substitution' already in the list" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_EXTENSION) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EXTENSION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "The value 'extension' is already in the list" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "The value 'restriction' is already in the list" );
                                    }
                            } else {
                                // REVISIT: Localize
                                    reportGenericSchemaError ( "Invalid block value (" + blockString + ")" );
                            }
                    }

                    int defaultVal = extend+restrict+substitute;
                    return (defaultVal == 0 ? fBlockDefault : defaultVal);
            }
    }

    private int parseFinalSet (String finalString)  throws Exception
    {
            if( finalString == null) {
                return fFinalDefault;
            }
            else if ( finalString.equals (SchemaSymbols.ATTVAL_POUNDALL) ) {
                    return SchemaSymbols.EXTENSION+SchemaSymbols.LIST+SchemaSymbols.RESTRICTION+SchemaSymbols.UNION;
            } else {
                    int extend = 0;
                    int restrict = 0;
                    int list = 0;
                    int union = 0;

                    StringTokenizer t = new StringTokenizer (finalString, " ");
                    while (t.hasMoreTokens()) {
                            String token = t.nextToken ();

                            if ( token.equals (SchemaSymbols.ELT_UNION) ) {
                                    if ( union == 0 ) {
                                            union = SchemaSymbols.UNION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "The value 'union' is already in the list" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_EXTENSION) ) {
                                    if ( extend == 0 ) {
                                            extend = SchemaSymbols.EXTENSION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "The value 'extension' is already in the list" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ELT_LIST) ) {
                                    if ( list == 0 ) {
                                            list = SchemaSymbols.LIST;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "The value 'list' is already in the list" );
                                    }
                            } else if ( token.equals (SchemaSymbols.ATTVAL_RESTRICTION) ) {
                                    if ( restrict == 0 ) {
                                            restrict = SchemaSymbols.RESTRICTION;
                                    } else {
                                        // REVISIT: Localize
                                            reportGenericSchemaError ( "The value 'restriction' is already in the list" );
                                    }
                            } else {
                                // REVISIT: Localize
                                    reportGenericSchemaError ( "Invalid final value (" + finalString + ")" );
                            }
                    }

                    int defaultVal = extend+restrict+list+union;
                    return (defaultVal == 0 ? fFinalDefault : defaultVal);
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

    /** Don't check the following code in because it creates a dependency on
        the serializer, preventing to package the parser without the serializer
    //Unit Test here
    public static void main(String args[] ) {

        if( args.length != 1 ) {
            System.out.println( "Error: Usage java TraverseSchema yourFile.xsd" );
            System.exit(0);
        }

        DOMParser parser = new IgnoreWhitespaceParser();
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
    **/

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

    static class IgnoreWhitespaceParser
        extends DOMParser {
        public void ignorableWhitespace(char ch[], int start, int length) {}
        public void ignorableWhitespace(int dataIdx) {}
    } // class IgnoreWhitespaceParser

    // When in a <redefine>, type definitions being used (and indeed 
    // refs to <group>'s and <attributeGroup>'s) may refer to info 
    // items either in the schema being redefined, in the <redefine>, 
    // or else in the schema doing the redefining.  Because of this 
    // latter we have to be prepared sometimes to look for our type 
    // definitions outside the schema stored in fSchemaRootElement.  
    // This simple class does this; it's just a linked list that 
    // lets us look at the <schema>'s on the queue; note also that this 
    // should provide us with a mechanism to handle nested <redefine>'s.  
    // It's also a handy way of saving schema info when importing/including; saves some code.
    public class SchemaInfo {
        private Element saveRoot;
        private SchemaInfo nextRoot;
        private SchemaInfo prevRoot;
        private String savedSchemaURL = fCurrentSchemaURL;
        private boolean saveElementDefaultQualified = fElementDefaultQualified;
        private boolean saveAttributeDefaultQualified = fAttributeDefaultQualified;
        private int saveScope = fCurrentScope;
        private int saveBlockDefault = fBlockDefault;
        private int saveFinalDefault = fFinalDefault;

        public SchemaInfo ( boolean saveElementDefaultQualified, boolean saveAttributeDefaultQualified,
                int saveBlockDefault, int saveFinalDefault, 
                int saveScope, String savedSchemaURL, Element saveRoot, SchemaInfo nextRoot, SchemaInfo prevRoot) {
            this.saveElementDefaultQualified = saveElementDefaultQualified;
            this.saveAttributeDefaultQualified = saveAttributeDefaultQualified;
            this.saveBlockDefault = saveBlockDefault;
            this.saveFinalDefault = saveFinalDefault;
            this.saveScope  = saveScope ;
            this.savedSchemaURL = savedSchemaURL;
            this.saveRoot  = saveRoot ;
            this.nextRoot = nextRoot;
            this.prevRoot = prevRoot;
        }
        public void setNext (SchemaInfo next) {
            nextRoot = next;
        }
        public SchemaInfo getNext () {
            return nextRoot;
        }
        public void setPrev (SchemaInfo prev) {
            prevRoot = prev;
        }
        public String getCurrentSchemaURL() { return savedSchemaURL; }
        public SchemaInfo getPrev () {
            return prevRoot;
        }
        public Element getRoot() { return saveRoot; }
        // NOTE:  this has side-effects!!!
        public void restore() {
            fCurrentSchemaURL = savedSchemaURL;
            fCurrentScope = saveScope;
            fElementDefaultQualified = saveElementDefaultQualified;
            fAttributeDefaultQualified = saveAttributeDefaultQualified;
            fBlockDefault = saveBlockDefault;
            fFinalDefault = saveFinalDefault;
            fSchemaRootElement = saveRoot; 
        }
    } // class SchemaInfo

} // class TraverseSchema