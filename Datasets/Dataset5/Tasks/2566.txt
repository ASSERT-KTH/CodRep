sg = new SchemaGrammar(currSchemaInfo.fTargetNamespace, desc.makeClone());

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

package org.apache.xerces.impl.xs.traversers;

import org.apache.xerces.impl.xs.XSGrammarBucket;
import org.apache.xerces.impl.xs.XSParticleDecl;
import org.apache.xerces.impl.xs.XSElementDecl;
import org.apache.xerces.impl.xs.XSDeclarationPool;
import org.apache.xerces.impl.xs.SchemaNamespaceSupport;
import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.XSComplexTypeDecl;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSMessageFormatter;
import org.apache.xerces.impl.xs.XMLSchemaValidator;
import org.apache.xerces.impl.xs.XSDDescription;
import org.apache.xerces.impl.xs.XMLSchemaException;
import org.apache.xerces.parsers.StandardParserConfiguration;
import org.apache.xerces.impl.Constants;
import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.impl.XMLEntityManager;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLResourceIdentifier;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.parser.XMLConfigurationException;
import org.apache.xerces.xni.parser.XMLEntityResolver;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.xni.grammars.Grammar;
import org.apache.xerces.xni.grammars.XMLGrammarPool;
import org.apache.xerces.util.XMLResourceIdentifierImpl;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.SymbolHash;
import org.apache.xerces.util.DOMUtil;
import org.apache.xerces.xni.XMLLocator;

import org.apache.xerces.impl.xs.dom.DOMParser;
import org.apache.xerces.impl.xs.dom.DOMNodePool;
import org.apache.xerces.impl.xs.dom.ElementNSImpl;
import org.apache.xerces.impl.xs.util.SimpleLocator;
import org.w3c.dom.Document;
import org.w3c.dom.Attr;
import org.w3c.dom.Element;

import org.xml.sax.InputSource;

import java.util.Hashtable;
import java.util.Stack;
import java.util.Vector;
import java.util.StringTokenizer;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.IOException;
import java.io.Reader;

/**
 * The purpose of this class is to co-ordinate the construction of a
 * grammar object corresponding to a schema.  To do this, it must be
 * prepared to parse several schema documents (for instance if the
 * schema document originally referred to contains <include> or
 * <redefined> information items).  If any of the schemas imports a
 * schema, other grammars may be constructed as a side-effect.
 *
 * @author Neil Graham, IBM
 * @author Pavani Mukthipudi, Sun Microsystems
 * @version $Id$
 */
public class XSDHandler {

    /** Property identifier: error handler. */
    protected static final String ERROR_HANDLER =
        Constants.XERCES_PROPERTY_PREFIX + Constants.ERROR_HANDLER_PROPERTY;

    /** Property identifier: JAXP schema source. */
    protected static final String JAXP_SCHEMA_SOURCE =
        Constants.JAXP_PROPERTY_PREFIX + Constants.SCHEMA_SOURCE;

    protected static final boolean DEBUG_NODE_POOL = false;
                              
    // data

    // different sorts of declarations; should make lookup and
    // traverser calling more efficient/less bulky.
    final static int ATTRIBUTE_TYPE          = 1;
    final static int ATTRIBUTEGROUP_TYPE     = 2;
    final static int ELEMENT_TYPE            = 3;
    final static int GROUP_TYPE              = 4;
    final static int IDENTITYCONSTRAINT_TYPE = 5;
    final static int NOTATION_TYPE           = 6;
    final static int TYPEDECL_TYPE           = 7;

    // this string gets appended to redefined names; it's purpose is to be
    // as unlikely as possible to cause collisions.
    public final static String REDEF_IDENTIFIER = "_fn3dktizrknc9pi";

    // please note the difference between SchemaHandler.EMPTY_STRING and
    // SchemaSymbols.EMPTY_STRING:
    //   the one in SchemaHandler is only for namespace binding purpose, it's
    //   used as a legal prefix, and it's added to the current symbol table;
    //   while the one in SchemaSymbols is for general purpose: just empty.
    public String EMPTY_STRING;

    //
    //protected data that can be accessable by any traverser
    // stores <notation> decl
    protected Hashtable fNotationRegistry = new Hashtable();

    protected XSDeclarationPool fDeclPool = null;

    // These tables correspond to the symbol spaces defined in the
    // spec.
    // They are keyed with a QName (that is, String("URI,localpart) and
    // their values are nodes corresponding to the given name's decl.
    // By asking the node for its ownerDocument and looking in
    // XSDocumentInfoRegistry we can easily get the corresponding
    // XSDocumentInfo object.
    private Hashtable fUnparsedAttributeRegistry = new Hashtable();
    private Hashtable fUnparsedAttributeGroupRegistry = new Hashtable();
    private Hashtable fUnparsedElementRegistry = new Hashtable();
    private Hashtable fUnparsedGroupRegistry = new Hashtable();
    private Hashtable fUnparsedIdentityConstraintRegistry = new Hashtable();
    private Hashtable fUnparsedNotationRegistry = new Hashtable();
    private Hashtable fUnparsedTypeRegistry = new Hashtable();
    // this is keyed with a documentNode (or the schemaRoot nodes
    // contained in the XSDocumentInfo objects) and its value is the
    // XSDocumentInfo object corresponding to that document.
    // Basically, the function of this registry is to be a link
    // between the nodes we fetch from calls to the fUnparsed*
    // arrays and the XSDocumentInfos they live in.
    private Hashtable fXSDocumentInfoRegistry = new Hashtable();

    // this hashtable is keyed on by XSDocumentInfo objects.  Its values
    // are Vectors containing the XSDocumentInfo objects <include>d,
    // <import>ed or <redefine>d by the key XSDocumentInfo.
    private Hashtable fDependencyMap = new Hashtable();

    // this hashtable is keyed on by a target namespace.  Its values
    // are Vectors containing namespaces imported by schema documents
    // with the key target namespace.
    // if an imprted schema has absent namespace, the value "null" is stored.
    private Hashtable fImportMap = new Hashtable();
    // all namespaces that imports other namespaces
    // if the importing schema has absent namespace, empty string is stored.
    // (because the key of a hashtable can't be null.)
    private Vector fAllTNSs = new Vector();
    // convinence methods
    private String null2EmptyString(String ns) {
        return ns == null ? EMPTY_STRING : ns;
    }
    private String emptyString2Null(String ns) {
        return ns == EMPTY_STRING ? null : ns;
    }

    // This vector stores strings which are combinations of the
    // publicId and systemId of the inputSource corresponding to a
    // schema document.  This combination is used so that the user's
    // EntityResolver can provide a consistent way of identifying a
    // schema document that is included in multiple other schemas.
    private Hashtable fTraversed = new Hashtable();

    // this hashtable contains a mapping from Document to its systemId
    // this is useful to resolve a uri relative to the referring document
    private Hashtable fDoc2SystemId = new Hashtable();

    // the primary XSDocumentInfo we were called to parse
    private XSDocumentInfo fRoot = null;

    // This hashtable's job is to act as a link between the document
    // node at the root of the parsed schema's tree and its
    // XSDocumentInfo object.
    private Hashtable fDoc2XSDocumentMap = new Hashtable();

    // map between <redefine> elements and the XSDocumentInfo
    // objects that correspond to the documents being redefined.
    private Hashtable fRedefine2XSDMap = new Hashtable();
    
    // map between <redefine> elements and the namespace support
    private Hashtable fRedefine2NSSupport = new Hashtable();

    // these objects store a mapping between the names of redefining
    // groups/attributeGroups and the groups/AttributeGroups which
    // they redefine by restriction (implicitly).  It is up to the
    // Group and AttributeGroup traversers to check these restrictions for
    // validity.
    private Hashtable fRedefinedRestrictedAttributeGroupRegistry = new Hashtable();
    private Hashtable fRedefinedRestrictedGroupRegistry = new Hashtable();

    // a variable storing whether the last schema document
    // processed (by getSchema) was a duplicate.
    private boolean fLastSchemaWasDuplicate;

    // the XMLErrorReporter
    private XMLErrorReporter fErrorReporter;

    // the XSAttributeChecker
    private XSAttributeChecker fAttributeChecker;

    // this class is to make use of the schema location property values.
    // we store the namespace/location pairs in a hashtable (use "" as the
    // namespace of absent namespace). when resolving an entity, we first try
    // to find in the hashtable whether there is a value for that namespace,
    // if so, pass that location value to the user-defined entity resolver.
    protected class LocationResolver {
        // the user-defined entity resolver
        public XMLEntityResolver fExternalResolver = null;
        // namespace/location pairs
        public Hashtable fLocationPairs = new Hashtable();

        public void reset(XMLEntityResolver entityResolver,
                          String sLocation, String nsLocation) {
            fLocationPairs.clear();
            fExternalResolver = entityResolver;

            if (sLocation != null) {
                StringTokenizer t = new StringTokenizer(sLocation, " \n\t\r");
                String namespace, location;
                while (t.hasMoreTokens()) {
                    namespace = t.nextToken ();
                    if (!t.hasMoreTokens()) {
                        break;
                    }
                    location = t.nextToken();
                    fLocationPairs.put(namespace, location);
                }
            }
            if (nsLocation != null) {
                fLocationPairs.put(EMPTY_STRING, nsLocation);
            }
        }

        public XMLInputSource resolveEntity(XSDDescription desc) throws IOException {
            if (fExternalResolver == null)
                return null;

            String loc = null;
            // we consider the schema location properties for import
            if (desc.getContextType() == XSDDescription.CONTEXT_IMPORT ||
                desc.fromInstance()) {
                // use empty string as the key for absent namespace
                String namespace = desc.getTargetNamespace();
                String ns = namespace == null ? EMPTY_STRING : namespace;
                // get the location hint for that namespace
                loc = (String)fLocationPairs.get(ns);
            }

            // if it's not import, or if the target namespace is not set
            // in the schema location properties, use location hint
            if (loc == null) {
                String[] hints = desc.getLocationHints();
                if (hints != null && hints.length > 0)
                    loc = hints[0];
            }

            String expandedLoc = XMLEntityManager.expandSystemId(loc, desc.getBaseSystemId());
            desc.setLiteralSystemId(loc);
            desc.setExpandedSystemId(expandedLoc);
            return fExternalResolver.resolveEntity(desc);
        }
    }

    // the schema location resolver
    private LocationResolver fLocationResolver = new LocationResolver();

    // the symbol table
    private SymbolTable fSymbolTable;

    // the GrammarResolver
    private XSGrammarBucket fGrammarBucket;
    
    // the Grammar description
    private XSDDescription fSchemaGrammarDescription;
    
    // the Grammar Pool
    private XMLGrammarPool fGrammarPool;

    //************ Traversers **********
    XSDAttributeGroupTraverser fAttributeGroupTraverser;
    XSDAttributeTraverser fAttributeTraverser;
    XSDComplexTypeTraverser fComplexTypeTraverser;
    XSDElementTraverser fElementTraverser;
    XSDGroupTraverser fGroupTraverser;
    XSDKeyrefTraverser fKeyrefTraverser;
    XSDNotationTraverser fNotationTraverser;
    XSDSimpleTypeTraverser fSimpleTypeTraverser;
    XSDUniqueOrKeyTraverser fUniqueOrKeyTraverser;
    XSDWildcardTraverser fWildCardTraverser;

    DOMParser fSchemaParser;
    final DOMNodePool fDOMPool = new DOMNodePool();

    // these data members are needed for the deferred traversal
    // of local elements.

    // the initial size of the array to store deferred local elements
    private static final int INIT_STACK_SIZE = 30;
    // the incremental size of the array to store deferred local elements
    private static final int INC_STACK_SIZE  = 10;
    // current position of the array (# of deferred local elements)
    private int fLocalElemStackPos = 0;

    private XSParticleDecl[] fParticle = new XSParticleDecl[INIT_STACK_SIZE];
    private Element[] fLocalElementDecl = new Element[INIT_STACK_SIZE];
    private int[] fAllContext = new int[INIT_STACK_SIZE];
    private String [][] fLocalElemNamespaceContext = new String [INIT_STACK_SIZE][1];

    // these data members are needed for the deferred traversal
    // of keyrefs.

    // the initial size of the array to store deferred keyrefs
    private static final int INIT_KEYREF_STACK = 2;
    // the incremental size of the array to store deferred keyrefs
    private static final int INC_KEYREF_STACK_AMOUNT = 2;
    // current position of the array (# of deferred keyrefs)
    private int fKeyrefStackPos = 0;

    private Element [] fKeyrefs = new Element[INIT_KEYREF_STACK];
    private XSElementDecl [] fKeyrefElems = new XSElementDecl [INIT_KEYREF_STACK];
    private String [][] fKeyrefNamespaceContext = new String[INIT_KEYREF_STACK][1];

    // Constructors

    // it should be possible to use the same XSDHandler to parse
    // multiple schema documents; this will allow one to be
    // constructed.
    public XSDHandler (XSGrammarBucket gBucket) {
        fGrammarBucket = gBucket;

        // Note: don't use SchemaConfiguration internally
        //       we will get stack overflaw because
        //       XMLSchemaValidator will be instantiating XSDHandler...
        fSchemaParser = new DOMParser();
        fSchemaGrammarDescription = new XSDDescription();

        createTraversers();
    } // end constructor

    // This method initiates the parse of a schema.  It will likely be
    // called from the Validator and it will make the
    // resulting grammar available; it returns a reference to this object just
    // in case.  An ErrorHandler, EntityResolver, XSGrammarBucket and SymbolTable must
    // already have been set; the last thing this method does is reset
    // this object (i.e., clean the registries, etc.).
    public SchemaGrammar parseSchema(XSDDescription desc) {
        XMLInputSource schemaSource=null;
        fDOMPool.reset();
        fSchemaParser.setPool(fDOMPool);
        try {
            schemaSource = fLocationResolver.resolveEntity(desc);
        }
        catch (IOException ex) {
            reportSchemaError(DOC_ERROR_CODES[desc.getContextType()],
                              new Object[]{desc.getLocationHints()[0]},
                              null);
        }
        return parseSchema(schemaSource, desc);
    } // end parseSchema

    public SchemaGrammar parseSchema(XMLInputSource is, XSDDescription desc) {

        // first try to find it in the bucket/pool, return if one is found
        SchemaGrammar grammar = findGrammar(desc);
        if (grammar != null)
            return grammar;
        
        // before parsing a schema, need to reset all traversers and
        // clear all registries
        prepare();

        String schemaNamespace = desc.getTargetNamespace();
        // handle empty string URI as null
        if (schemaNamespace != null) {
            schemaNamespace = fSymbolTable.addSymbol(schemaNamespace);
        }
        short referType = desc.getContextType();
        
        // first phase:  construct trees.
        Document schemaRoot = getSchema(schemaNamespace, is,
                                        referType == XSDDescription.CONTEXT_PREPARSE,
                                        referType, null);
        if (schemaRoot == null) {
            // something went wrong right off the hop
            return null;
        }
        fRoot = constructTrees(schemaRoot, is.getSystemId(), desc);
        if (fRoot == null) {
            return null;
        }

        // second phase:  fill global registries.
        buildGlobalNameRegistries();

        // third phase:  call traversers
        traverseSchemas();

        // fourth phase: handle local element decls
        traverseLocalElements();

        // fifth phase:  handle Keyrefs
        resolveKeyRefs();

        // sixth phase:  validate attribute of non-schema namespaces
        // REVISIT: skip this for now. we really don't want to do it.
        //fAttributeChecker.checkNonSchemaAttributes(fGrammarBucket);

        // seventh phase:  store imported grammars
        // for all grammars with <import>s
        for (int i = fAllTNSs.size() - 1; i >= 0; i--) {
            // get its target namespace
            String tns = (String)fAllTNSs.elementAt(i);
            // get all namespaces it imports
            Vector ins = (Vector)fImportMap.get(tns);
            // get the grammar
            SchemaGrammar sg = fGrammarBucket.getGrammar(emptyString2Null(tns));
            if (sg == null)
                continue;
            SchemaGrammar isg;
            // for imported namespace
            int count = 0;
            for (int j = 0; j < ins.size(); j++) {
                // get imported grammar
                isg = fGrammarBucket.getGrammar((String)ins.elementAt(j));
                // reuse the same vector
                if (isg != null)
                    ins.setElementAt(isg, count++);
            }
            ins.setSize(count);
            // set the imported grammars
            sg.setImportedGrammars(ins);
        }

        // and return.
        return fGrammarBucket.getGrammar(schemaNamespace);
    } // end parseSchema

    /**
     * First try to find a grammar in the bucket, if failed, consult the
     * grammar pool. If a grammar is found in the pool, then add it (and all
     * imported ones) into the bucket.
     */
    protected SchemaGrammar findGrammar(XSDDescription desc) {
        SchemaGrammar sg = fGrammarBucket.getGrammar(desc.getTargetNamespace());
        if (sg == null) {
            if (fGrammarPool != null) {
                sg = (SchemaGrammar)fGrammarPool.retrieveGrammar(desc);
                if (sg != null) {
                    // put this grammar into the bucket, along with grammars
                    // imported by it (directly or indirectly)
                    if (!fGrammarBucket.putGrammar(sg, true)) {
                        // REVISIT: a conflict between new grammar(s) and grammars
                        // in the bucket. What to do? A warning? An exception?
                        reportSchemaWarning("GrammarConflict", null, null);
                        sg = null;
                    }
                }
            }
        }
        return sg;
    }
    
    // may wish to have setter methods for ErrorHandler,
    // EntityResolver...

    private static final String[][] NS_ERROR_CODES = {
        {"src-include.2.1", "src-include.2.1"},
        {"src-redefine.3.1", "src-redefine.3.1"},
        {"src-import.3.1", "src-import.3.2"},
        null,
        {"TargetNamespace.1", "TargetNamespace.2"},
        {"TargetNamespace.1", "TargetNamespace.2"},
        {"TargetNamespace.1", "TargetNamespace.2"},
        {"TargetNamespace.1", "TargetNamespace.2"}
    };
    
    private static final String[] ELE_ERROR_CODES = {
        "src-include.1", "src-redefine.2", "src-import.2", "schema_reference.4",
        "schema_reference.4", "schema_reference.4", "schema_reference.4", "schema_reference.4"
    };
    
    // This method does several things:
    // It constructs an instance of an XSDocumentInfo object using the
    // schemaRoot node.  Then, for each <include>,
    // <redefine>, and <import> children, it attempts to resolve the
    // requested schema document, initiates a DOM parse, and calls
    // itself recursively on that document's root.  It also records in
    // the DependencyMap object what XSDocumentInfo objects its XSDocumentInfo
    // depends on.
    // It also makes sure the targetNamespace of the schema it was
    // called to parse is correct.
    protected XSDocumentInfo constructTrees(Document schemaRoot, String locationHint, XSDDescription desc) {
        if (schemaRoot == null) return null;
        String callerTNS = desc.getTargetNamespace();
        short referType = desc.getContextType();
        
        XSDocumentInfo currSchemaInfo = null;
        try {
            currSchemaInfo = new XSDocumentInfo(schemaRoot, fAttributeChecker, fSymbolTable);
        } catch (XMLSchemaException se) {
            reportSchemaError(ELE_ERROR_CODES[referType],
                              new Object[]{locationHint},
                              DOMUtil.getRoot(schemaRoot));
            return null;
        }
        // targetNamespace="" is not valid, issue a warning, and ignore it
        if (currSchemaInfo.fTargetNamespace != null &&
            currSchemaInfo.fTargetNamespace.length() == 0) {
            reportSchemaWarning("EmptyTargetNamespace",
                                new Object[]{locationHint},
                                DOMUtil.getRoot(schemaRoot));
            currSchemaInfo.fTargetNamespace = null;
        }

        if (callerTNS != null) {
            // the second index to the NS_ERROR_CODES array
            // if the caller/expected NS is not absent, we use the first column
            int secondIdx = 0;
            // for include and redefine
            if (referType == XSDDescription.CONTEXT_INCLUDE ||
                referType == XSDDescription.CONTEXT_REDEFINE) {
                // if the referred document has no targetNamespace,
                // it's a chameleon schema
                if (currSchemaInfo.fTargetNamespace == null) {
                    currSchemaInfo.fTargetNamespace = callerTNS;
                    currSchemaInfo.fIsChameleonSchema = true;
                }
                // if the referred document has a target namespace differing
                // from the caller, it's an error
                else if (callerTNS != currSchemaInfo.fTargetNamespace) {
                    reportSchemaError(NS_ERROR_CODES[referType][secondIdx],
                                      new Object [] {callerTNS, currSchemaInfo.fTargetNamespace},
                                      DOMUtil.getRoot(schemaRoot));
                    return null;
                }
            }
            // for preparse, callerTNS is null, so it's not possible;
            // for instance and import, the two NS's must be the same
            else if (callerTNS != currSchemaInfo.fTargetNamespace) {
                reportSchemaError(NS_ERROR_CODES[referType][secondIdx],
                                  new Object [] {callerTNS, currSchemaInfo.fTargetNamespace},
                                  DOMUtil.getRoot(schemaRoot));
                return null;
            }
        }
        // now there is no caller/expected NS, it's an error for the referred
        // document to have a target namespace, unless we are preparsing a schema
        else if (currSchemaInfo.fTargetNamespace != null) {
            // set the target namespace of the description
            if (referType == XSDDescription.CONTEXT_PREPARSE) {
                desc.setTargetNamespace(currSchemaInfo.fTargetNamespace);
                callerTNS = currSchemaInfo.fTargetNamespace;
            }
            else {
                // the second index to the NS_ERROR_CODES array
                // if the caller/expected NS is absent, we use the second column
                int secondIdx = 1;
                reportSchemaError(NS_ERROR_CODES[referType][secondIdx],
                                  new Object [] {callerTNS, currSchemaInfo.fTargetNamespace},
                                  DOMUtil.getRoot(schemaRoot));
                return null;
            }
        }
        // the other cases (callerTNS == currSchemaInfo.fTargetNamespce == null)
        // are valid
        
        // a schema document can always access it's own target namespace
        currSchemaInfo.addAllowedNS(currSchemaInfo.fTargetNamespace);

        SchemaGrammar sg = null;
        
        if (referType != XSDDescription.CONTEXT_INCLUDE &&
            referType != XSDDescription.CONTEXT_REDEFINE) {
            sg = new SchemaGrammar(fSymbolTable, currSchemaInfo.fTargetNamespace, desc.makeClone());
            fGrammarBucket.putGrammar(sg);
        }
            
        fDoc2XSDocumentMap.put(schemaRoot, currSchemaInfo);

        Vector dependencies = new Vector();
        Element rootNode = DOMUtil.getRoot(schemaRoot);

        Document newSchemaRoot = null;
        for (Element child = DOMUtil.getFirstChildElement(rootNode);
            child != null;
            child = DOMUtil.getNextSiblingElement(child)) {
            String schemaNamespace=null;
            String schemaHint=null;
            String localName = DOMUtil.getLocalName(child);
            
            short refType = -1;
            
            if (localName.equals(SchemaSymbols.ELT_ANNOTATION))
                continue;
            else if (localName.equals(SchemaSymbols.ELT_IMPORT)) {
                refType = XSDDescription.CONTEXT_IMPORT;
                // have to handle some validation here too!
                // call XSAttributeChecker to fill in attrs
                Object[] includeAttrs = fAttributeChecker.checkAttributes(child, true, currSchemaInfo);
                schemaHint = (String)includeAttrs[XSAttributeChecker.ATTIDX_SCHEMALOCATION];
                schemaNamespace = (String)includeAttrs[XSAttributeChecker.ATTIDX_NAMESPACE];
                if (schemaNamespace != null)
                    schemaNamespace = fSymbolTable.addSymbol(schemaNamespace);
                // a document can't import another document with the same namespace
                if (schemaNamespace == currSchemaInfo.fTargetNamespace) {
                    reportSchemaError("src-import.1.1", new Object [] {schemaNamespace}, child);
                }
                fAttributeChecker.returnAttrArray(includeAttrs, currSchemaInfo);
                
                // if this namespace has been imported by this document,
                // ignore the <import> statement
                if (currSchemaInfo.isAllowedNS(schemaNamespace))
                    continue;

                // a schema document can access it's imported namespaces
                currSchemaInfo.addAllowedNS(schemaNamespace);
                
                // also record the fact that one namespace imports another one
                // convert null to ""
                String tns = null2EmptyString(currSchemaInfo.fTargetNamespace);
                // get all namespaces imported by this one
                Vector ins = (Vector)fImportMap.get(tns);
                // if no namespace was imported, create new Vector
                if (ins == null) {
                    // record that this one imports other(s)
                    fAllTNSs.addElement(tns);
                    ins = new Vector();
                    fImportMap.put(tns, ins);
                    ins.addElement(schemaNamespace);
                }
                else if (!ins.contains(schemaNamespace)){
                    ins.addElement(schemaNamespace);
                }

                fSchemaGrammarDescription.reset();
                fSchemaGrammarDescription.setContextType(XSDDescription.CONTEXT_IMPORT);
                fSchemaGrammarDescription.setBaseSystemId((String)fDoc2SystemId.get(schemaRoot));
                fSchemaGrammarDescription.setLocationHints(new String[]{schemaHint});
                fSchemaGrammarDescription.setTargetNamespace(schemaNamespace);

                // if a grammar with the same namespace exists (or being
                // built), ignore this one (don't traverse it).
                if (findGrammar(fSchemaGrammarDescription) != null)
                    continue;
                
                newSchemaRoot = getSchema(fSchemaGrammarDescription, false, child);
            }
            else if ((localName.equals(SchemaSymbols.ELT_INCLUDE)) ||
                     (localName.equals(SchemaSymbols.ELT_REDEFINE))) {
                // validation for redefine/include will be the same here; just
                // make sure TNS is right (don't care about redef contents
                // yet).
                Object[] includeAttrs = fAttributeChecker.checkAttributes(child, true, currSchemaInfo);
                schemaHint = (String)includeAttrs[XSAttributeChecker.ATTIDX_SCHEMALOCATION];
                // store the namespace decls of the redefine element
                if (localName.equals(SchemaSymbols.ELT_REDEFINE)) {
                    fRedefine2NSSupport.put(child, new SchemaNamespaceSupport(currSchemaInfo.fNamespaceSupport));
                }
                fAttributeChecker.returnAttrArray(includeAttrs, currSchemaInfo);
                // schemaLocation is required on <include> and <redefine>
                if (schemaHint == null) {
                    reportSchemaError("s4s-att-must-appear", new Object [] {
                                      "<include> or <redefine>", "schemaLocation"},
                                      child);
                }
                // pass the systemId of the current document as the base systemId
                boolean mustResolve = false;
                refType = XSDDescription.CONTEXT_INCLUDE;
                if(localName.equals(SchemaSymbols.ELT_REDEFINE)) {
                    mustResolve = nonAnnotationContent(child);
                    refType = XSDDescription.CONTEXT_REDEFINE;
                }
                fSchemaGrammarDescription.reset();
                fSchemaGrammarDescription.setContextType(refType);
                fSchemaGrammarDescription.setBaseSystemId((String)fDoc2SystemId.get(schemaRoot));
                fSchemaGrammarDescription.setLocationHints(new String[]{schemaHint});
                fSchemaGrammarDescription.setTargetNamespace(callerTNS);
                newSchemaRoot = getSchema(fSchemaGrammarDescription, mustResolve, child);
                schemaNamespace = currSchemaInfo.fTargetNamespace;
            }
            else {
                // no more possibility of schema references in well-formed
                // schema...
                break;
            }

            // If the schema is duplicate, we needn't call constructTrees() again.
            // To handle mutual <include>s
            XSDocumentInfo newSchemaInfo = null;
            if (fLastSchemaWasDuplicate) {
                newSchemaInfo = (XSDocumentInfo)fDoc2XSDocumentMap.get(newSchemaRoot);
            }
            else {
                newSchemaInfo = constructTrees(newSchemaRoot, schemaHint, fSchemaGrammarDescription);
            }

            if (localName.equals(SchemaSymbols.ELT_REDEFINE) &&
                newSchemaInfo != null) {
                // must record which schema we're redefining so that we can
                // rename the right things later!
                fRedefine2XSDMap.put(child, newSchemaInfo);
            }
            if (newSchemaRoot != null) {
                if (newSchemaInfo != null)
                    dependencies.addElement(newSchemaInfo);
                newSchemaRoot = null;
            }
        }
        
        fDependencyMap.put(currSchemaInfo, dependencies);
        return currSchemaInfo;
    } // end constructTrees

    // This method builds registries for all globally-referenceable
    // names.  A registry will be built for each symbol space defined
    // by the spec.  It is also this method's job to rename redefined
    // components, and to record which components redefine others (so
    // that implicit redefinitions of groups and attributeGroups can be handled).
    protected void buildGlobalNameRegistries() {
        /* Starting with fRoot, we examine each child of the schema
         * element.  Skipping all imports and includes, we record the names
         * of all other global components (and children of <redefine>).  We
         * also put <redefine> names in a registry that we look through in
         * case something needs renaming.  Once we're done with a schema we
         * set its Document node to hidden so that we don't try to traverse
         * it again; then we look to its Dependency map entry.  We keep a
         * stack of schemas that we haven't yet finished processing; this
         * is a depth-first traversal.
         */
        Stack schemasToProcess = new Stack();
        schemasToProcess.push(fRoot);
        while (!schemasToProcess.empty()) {
            XSDocumentInfo currSchemaDoc =
            (XSDocumentInfo)schemasToProcess.pop();
            Document currDoc = currSchemaDoc.fSchemaDoc;
            if (DOMUtil.isHidden(currDoc)) {
                // must have processed this already!
                continue;
            }
            Element currRoot = DOMUtil.getRoot(currDoc);

            // process this schema's global decls
            boolean dependenciesCanOccur = true;
            for (Element globalComp =
                 DOMUtil.getFirstChildElement(currRoot);
                globalComp != null;
                globalComp = DOMUtil.getNextSiblingElement(globalComp)) {
                // this loop makes sure the <schema> element ordering is
                // also valid.
                if (DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_ANNOTATION)) {
                    //skip it; traverse it later
                    continue;
                }
                else if (DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_INCLUDE) ||
                         DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_IMPORT)) {
                    if (!dependenciesCanOccur) {
                        reportSchemaError("sch-props-correct.1", new Object [] {DOMUtil.getLocalName(globalComp)}, globalComp);
                    }
                    // we've dealt with this; mark as traversed
                    DOMUtil.setHidden(globalComp);
                }
                else if (DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_REDEFINE)) {
                    if (!dependenciesCanOccur) {
                        reportSchemaError("sch-props-correct.1", new Object [] {DOMUtil.getLocalName(globalComp)}, globalComp);
                    }
                    for (Element redefineComp = DOMUtil.getFirstChildElement(globalComp);
                        redefineComp != null;
                        redefineComp = DOMUtil.getNextSiblingElement(redefineComp)) {
                        String lName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME);
                        if (lName.length() == 0) // an error we'll catch later
                            continue;
                        String qName = currSchemaDoc.fTargetNamespace == null ?
                                       ","+lName:
                                       currSchemaDoc.fTargetNamespace +","+lName;
                        String componentType = DOMUtil.getLocalName(redefineComp);
                        if (componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                            checkForDuplicateNames(qName, fUnparsedAttributeGroupRegistry, redefineComp, currSchemaDoc);
                            // the check will have changed our name;
                            String targetLName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME)+REDEF_IDENTIFIER;
                            // and all we need to do is error-check+rename our kkids:
                            renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_ATTRIBUTEGROUP,
                                                       lName, targetLName);
                        }
                        else if ((componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) ||
                                 (componentType.equals(SchemaSymbols.ELT_SIMPLETYPE))) {
                            checkForDuplicateNames(qName, fUnparsedTypeRegistry, redefineComp, currSchemaDoc);
                            // the check will have changed our name;
                            String targetLName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME) + REDEF_IDENTIFIER;
                            // and all we need to do is error-check+rename our kkids:
                            if (componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                                renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_COMPLEXTYPE,
                                                           lName, targetLName);
                            }
                            else { // must be simpleType
                                renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_SIMPLETYPE,
                                                           lName, targetLName);
                            }
                        }
                        else if (componentType.equals(SchemaSymbols.ELT_GROUP)) {
                            checkForDuplicateNames(qName, fUnparsedGroupRegistry, redefineComp, currSchemaDoc);
                            // the check will have changed our name;
                            String targetLName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME)+REDEF_IDENTIFIER;
                            // and all we need to do is error-check+rename our kids:
                            renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_GROUP,
                                                       lName, targetLName);
                        }
                    } // end march through <redefine> children
                    // and now set as traversed
                    //DOMUtil.setHidden(globalComp);
                }
                else {
                    dependenciesCanOccur = false;
                    String lName = DOMUtil.getAttrValue(globalComp, SchemaSymbols.ATT_NAME);
                    if (lName.length() == 0) // an error we'll catch later
                        continue;
                    String qName = currSchemaDoc.fTargetNamespace == null?
                                   ","+lName:
                                   currSchemaDoc.fTargetNamespace +","+lName;
                    String componentType = DOMUtil.getLocalName(globalComp);
                    if (componentType.equals(SchemaSymbols.ELT_ATTRIBUTE)) {
                        checkForDuplicateNames(qName, fUnparsedAttributeRegistry, globalComp, currSchemaDoc);
                    }
                    else if (componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                        checkForDuplicateNames(qName, fUnparsedAttributeGroupRegistry, globalComp, currSchemaDoc);
                    }
                    else if ((componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) ||
                             (componentType.equals(SchemaSymbols.ELT_SIMPLETYPE))) {
                        checkForDuplicateNames(qName, fUnparsedTypeRegistry, globalComp, currSchemaDoc);
                    }
                    else if (componentType.equals(SchemaSymbols.ELT_ELEMENT)) {
                        checkForDuplicateNames(qName, fUnparsedElementRegistry, globalComp, currSchemaDoc);
                    }
                    else if (componentType.equals(SchemaSymbols.ELT_GROUP)) {
                        checkForDuplicateNames(qName, fUnparsedGroupRegistry, globalComp, currSchemaDoc);
                    }
                    else if (componentType.equals(SchemaSymbols.ELT_NOTATION)) {
                        checkForDuplicateNames(qName, fUnparsedNotationRegistry, globalComp, currSchemaDoc);
                    }
                }
            } // end for

            // now we're done with this one!
            DOMUtil.setHidden(currDoc);
            // now add the schemas this guy depends on
            Vector currSchemaDepends = (Vector)fDependencyMap.get(currSchemaDoc);
            for (int i = 0; i < currSchemaDepends.size(); i++) {
                schemasToProcess.push(currSchemaDepends.elementAt(i));
            }
        } // while
    } // end buildGlobalNameRegistries

    // Beginning at the first schema processing was requested for
    // (fRoot), this method
    // examines each child (global schema information item) of each
    // schema document (and of each <redefine> element)
    // corresponding to an XSDocumentInfo object.  If the
    // readOnly field on that node has not been set, it calls an
    // appropriate traverser to traverse it.  Once all global decls in
    // an XSDocumentInfo object have been traversed, it marks that object
    // as traversed (or hidden) in order to avoid infinite loops.  It completes
    // when it has visited all XSDocumentInfo objects in the
    // DependencyMap and marked them as traversed.
    protected void traverseSchemas() {
        // the process here is very similar to that in
        // buildGlobalRegistries, except we can't set our schemas as
        // hidden for a second time; so make them all visible again
        // first!
        setSchemasVisible(fRoot);
        Stack schemasToProcess = new Stack();
        schemasToProcess.push(fRoot);
        while (!schemasToProcess.empty()) {
            XSDocumentInfo currSchemaDoc =
            (XSDocumentInfo)schemasToProcess.pop();
            Document currDoc = currSchemaDoc.fSchemaDoc;
            SchemaGrammar currSG = fGrammarBucket.getGrammar(currSchemaDoc.fTargetNamespace);
            if (DOMUtil.isHidden(currDoc)) {
                // must have processed this already!
                continue;
            }
            Element currRoot = DOMUtil.getRoot(currDoc);

            // traverse this schema's global decls
            for (Element globalComp =
                 DOMUtil.getFirstVisibleChildElement(currRoot);
                globalComp != null;
                globalComp = DOMUtil.getNextVisibleSiblingElement(globalComp)) {
                // We'll always want to set this as hidden!
                DOMUtil.setHidden(globalComp);
                String componentType = DOMUtil.getLocalName(globalComp);
                // includes and imports will not show up here!
                if (DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_REDEFINE)) {
                    // use the namespace decls for the redefine, instead of for the parent <schema>
                    currSchemaDoc.backupNSSupport((SchemaNamespaceSupport)fRedefine2NSSupport.get(globalComp));
                    for (Element redefinedComp = DOMUtil.getFirstVisibleChildElement(globalComp);
                        redefinedComp != null;
                        redefinedComp = DOMUtil.getNextVisibleSiblingElement(redefinedComp)) {
                        String redefinedComponentType = DOMUtil.getLocalName(redefinedComp);
                        DOMUtil.setHidden(redefinedComp);
                        if (redefinedComponentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                            fAttributeGroupTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        }
                        else if (redefinedComponentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                            fComplexTypeTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        }
                        else if (redefinedComponentType.equals(SchemaSymbols.ELT_GROUP)) {
                            fGroupTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        }
                        else if (redefinedComponentType.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                            fSimpleTypeTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        }
                        else if (redefinedComponentType.equals(SchemaSymbols.ELT_ANNOTATION)) {
                            // REVISIT:  according to 3.13.2 the PSVI needs the parent's attributes;
                            // thus this should be done in buildGlobalNameRegistries not here...
                            fElementTraverser.traverseAnnotationDecl(redefinedComp, null, true, currSchemaDoc);
                        }
                        else {
                            reportSchemaError("src-redefine", new Object [] {componentType}, redefinedComp);
                        }
                    } // end march through <redefine> children
                    currSchemaDoc.restoreNSSupport();
                }
                else if (componentType.equals(SchemaSymbols.ELT_ATTRIBUTE)) {
                    fAttributeTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                }
                else if (componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                    fAttributeGroupTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                }
                else if (componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                    fComplexTypeTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                }
                else if (componentType.equals(SchemaSymbols.ELT_ELEMENT)) {
                    fElementTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                }
                else if (componentType.equals(SchemaSymbols.ELT_GROUP)) {
                    fGroupTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                }
                else if (componentType.equals(SchemaSymbols.ELT_NOTATION)) {
                    fNotationTraverser.traverse(globalComp, currSchemaDoc, currSG);
                }
                else if (componentType.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                    fSimpleTypeTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                }
                else if (componentType.equals(SchemaSymbols.ELT_ANNOTATION)) {
                    // REVISIT:  according to 3.13.2 the PSVI needs the parent's attributes;
                    // thus this should be done in buildGlobalNameRegistries not here...
                    fElementTraverser.traverseAnnotationDecl(globalComp, null, true, currSchemaDoc);
                }
                else {
                    reportSchemaError("sch-props-correct.1", new Object [] {DOMUtil.getLocalName(globalComp)}, globalComp);
                }
            } // end for

            // now we're done with this one!
            DOMUtil.setHidden(currDoc);
            // now add the schemas this guy depends on
            Vector currSchemaDepends = (Vector)fDependencyMap.get(currSchemaDoc);
            for (int i = 0; i < currSchemaDepends.size(); i++) {
                schemasToProcess.push(currSchemaDepends.elementAt(i));
            }
        } // while
    } // end traverseSchemas

    private static final String[] COMP_TYPE = {
        null,               // index 0
        "attribute declaration",
        "attribute group",
        "elment declaration",
        "group",
        "identity constraint",
        "notation",
        "type definition",
    };

    // since it is forbidden for traversers to talk to each other
    // directly (except wen a traverser encounters a local declaration),
    // this provides a generic means for a traverser to call
    // for the traversal of some declaration.  An XSDocumentInfo is
    // required because the XSDocumentInfo that the traverser is traversing
    // may bear no relation to the one the handler is operating on.
    // This method will:
    // 1.  See if a global definition matching declToTraverse exists;
    // 2. if so, determine if there is a path from currSchema to the
    // schema document where declToTraverse lives (i.e., do a lookup
    // in DependencyMap);
    // 3. depending on declType (which will be relevant to step 1 as
    // well), call the appropriate traverser with the appropriate
    // XSDocumentInfo object.
    // This method returns whatever the traverser it called returned;
    // this will be an Object of some kind
    // that lives in the Grammar.
    protected Object getGlobalDecl(XSDocumentInfo currSchema,
                                   int declType,
                                   QName declToTraverse,
                                   Element elmNode) {

        if (DEBUG_NODE_POOL) {
            System.out.println("TRAVERSE_GL: "+declToTraverse.toString());
        }
        // from the schema spec, all built-in types are present in all schemas,
        // so if the requested component is a type, and could be found in the
        // default schema grammar, we should return that type.
        // otherwise (since we would support user-defined schema grammar) we'll
        // use the normal way to get the decl
        if (declToTraverse.uri != null &&
            declToTraverse.uri == SchemaSymbols.URI_SCHEMAFORSCHEMA) {
            if (declType == TYPEDECL_TYPE) {
                Object retObj = SchemaGrammar.SG_SchemaNS.getGlobalTypeDecl(declToTraverse.localpart);
                if (retObj != null)
                    return retObj;
            }
        }

        // now check whether this document can access the requsted namespace
        if (!currSchema.isAllowedNS(declToTraverse.uri)) {
            // cannot get to this schema from the one containing the requesting decl
            reportSchemaError("src-resolve.4", new Object[]{fDoc2SystemId.get(currSchema.fSchemaDoc), declToTraverse.uri}, elmNode);
            return null;
        }

        // check whether there is grammar for the requested namespace
        SchemaGrammar sGrammar = fGrammarBucket.getGrammar(declToTraverse.uri);
        if (sGrammar == null) {
            reportSchemaError("src-resolve", new Object[]{declToTraverse.rawname, COMP_TYPE[declType]}, elmNode);
            return null;
        }

        // if there is such grammar, check whether the requested component is in the grammar
        Object retObj = null;
        switch (declType) {
        case ATTRIBUTE_TYPE :
            retObj = sGrammar.getGlobalAttributeDecl(declToTraverse.localpart);
            break;
        case ATTRIBUTEGROUP_TYPE :
            retObj = sGrammar.getGlobalAttributeGroupDecl(declToTraverse.localpart);
            break;
        case ELEMENT_TYPE :
            retObj = sGrammar.getGlobalElementDecl(declToTraverse.localpart);
            break;
        case GROUP_TYPE :
            retObj = sGrammar.getGlobalGroupDecl(declToTraverse.localpart);
            break;
        case IDENTITYCONSTRAINT_TYPE :
            retObj = sGrammar.getIDConstraintDecl(declToTraverse.localpart);
            break;
        case NOTATION_TYPE :
            retObj = sGrammar.getNotationDecl(declToTraverse.localpart);
            break;
        case TYPEDECL_TYPE :
            retObj = sGrammar.getGlobalTypeDecl(declToTraverse.localpart);
            break;
        }

        // if the component is parsed, return it
        if (retObj != null)
            return retObj;

        XSDocumentInfo schemaWithDecl = null;
        Element decl = null;

        // the component is not parsed, try to find a DOM element for it
        String declKey = declToTraverse.uri == null? ","+declToTraverse.localpart:
                         declToTraverse.uri+","+declToTraverse.localpart;
        switch (declType) {
        case ATTRIBUTE_TYPE :
            decl = (Element)fUnparsedAttributeRegistry.get(declKey);
            break;
        case ATTRIBUTEGROUP_TYPE :
            decl = (Element)fUnparsedAttributeGroupRegistry.get(declKey);
            break;
        case ELEMENT_TYPE :
            decl = (Element)fUnparsedElementRegistry.get(declKey);
            break;
        case GROUP_TYPE :
            decl = (Element)fUnparsedGroupRegistry.get(declKey);
            break;
        case IDENTITYCONSTRAINT_TYPE :
            decl = (Element)fUnparsedIdentityConstraintRegistry.get(declKey);
            break;
        case NOTATION_TYPE :
            decl = (Element)fUnparsedNotationRegistry.get(declKey);
            break;
        case TYPEDECL_TYPE :
            decl = (Element)fUnparsedTypeRegistry.get(declKey);
            break;
        default:
            reportSchemaError("Internal-Error", new Object [] {"XSDHandler asked to locate component of type " + declType + "; it does not recognize this type!"}, elmNode);
        }
        
        // no DOM element found, so the component can't be located
        if (decl == null) {
            reportSchemaError("src-resolve", new Object[]{declToTraverse.rawname, COMP_TYPE[declType]}, elmNode);
            return null;
        }

        // get the schema doc containing the component to be parsed
        // it should always return non-null value, but since null-checking
        // comes for free, let's be safe and check again
        schemaWithDecl = findXSDocumentForDecl(currSchema, decl);
        if (schemaWithDecl == null) {
            // cannot get to this schema from the one containing the requesting decl
            reportSchemaError("src-resolve.4", new Object[]{fDoc2SystemId.get(currSchema.fSchemaDoc), declToTraverse.uri}, elmNode);
            return null;
        }
        // a component is hidden, meaning either it's traversed, or being traversed.
        // but we didn't find it in the grammar, so it's the latter case, and
        // a circular reference. error!
        if (DOMUtil.isHidden(decl)) {
            // decl must not be null if we're here...
            reportSchemaError("st-props-correct.2", new Object [] {declToTraverse.prefix+":"+declToTraverse.localpart}, elmNode);
            return null;
        }

        // hide the element node before traversing it
        DOMUtil.setHidden(decl);

        SchemaNamespaceSupport nsSupport = null;
        // if the parent is <redefine> use the namespace delcs for it.
        Element parent = DOMUtil.getParent(decl);
        if (DOMUtil.getLocalName(parent).equals(SchemaSymbols.ELT_REDEFINE))
            nsSupport = (SchemaNamespaceSupport)fRedefine2NSSupport.get(parent);
        // back up the current SchemaNamespaceSupport, because we need to provide
        // a fresh one to the traverseGlobal methods.
        schemaWithDecl.backupNSSupport(nsSupport);

        // traverse the referenced global component
        switch (declType) {
        case ATTRIBUTE_TYPE :
            retObj = fAttributeTraverser.traverseGlobal(decl, schemaWithDecl, sGrammar);
            break;
        case ATTRIBUTEGROUP_TYPE :
            retObj = fAttributeGroupTraverser.traverseGlobal(decl, schemaWithDecl, sGrammar);
            break;
        case ELEMENT_TYPE :
            retObj = fElementTraverser.traverseGlobal(decl, schemaWithDecl, sGrammar);
            break;
        case GROUP_TYPE :
            retObj = fGroupTraverser.traverseGlobal(decl, schemaWithDecl, sGrammar);
            break;
        case IDENTITYCONSTRAINT_TYPE :
            // identity constraints should have been parsed already...
            // we should never get here
            retObj = null;
            break;
        case NOTATION_TYPE :
            retObj = fNotationTraverser.traverse(decl, schemaWithDecl, sGrammar);
            break;
        case TYPEDECL_TYPE :
            if (DOMUtil.getLocalName(decl).equals(SchemaSymbols.ELT_COMPLEXTYPE))
                retObj = fComplexTypeTraverser.traverseGlobal(decl, schemaWithDecl, sGrammar);
            else
                retObj = fSimpleTypeTraverser.traverseGlobal(decl, schemaWithDecl, sGrammar);
        }

        // restore the previous SchemaNamespaceSupport, so that the caller can get
        // proper namespace binding.
        schemaWithDecl.restoreNSSupport();

        return retObj;
    } // getGlobalDecl(XSDocumentInfo, int, QName):  Object

    // This method determines whether there is a group
    // (attributeGroup) which the given one has redefined by
    // restriction.  If so, it returns it; else it returns null.
    // @param type:  whether what's been redefined is an
    // attributeGroup or a group;
    // @param name:  the QName of the component doing the redefining.
    // @param currSchema:  schema doc in which the redefining component lives.
    // @return:  Object representing decl redefined if present, null
    // otherwise.
    Object getGrpOrAttrGrpRedefinedByRestriction(int type, QName name, XSDocumentInfo currSchema, Element elmNode) {
        String realName = name.uri != null?name.uri+","+name.localpart:
                ","+name.localpart;
        String nameToFind = null;
        switch (type) {
        case ATTRIBUTEGROUP_TYPE:
            nameToFind = (String)fRedefinedRestrictedAttributeGroupRegistry.get(realName);
            break;
        case GROUP_TYPE:
            nameToFind = (String)fRedefinedRestrictedGroupRegistry.get(realName);
            break;
        default:
            return null;
        }
        if (nameToFind == null) return null;
        int commaPos = nameToFind.indexOf(",");
        QName qNameToFind = new QName(EMPTY_STRING, nameToFind.substring(commaPos+1),
            nameToFind.substring(commaPos), (commaPos == 0)? null : nameToFind.substring(0, commaPos));
        Object retObj = getGlobalDecl(currSchema, type, qNameToFind, elmNode);
        if(retObj == null) {
            switch (type) {
            case ATTRIBUTEGROUP_TYPE:
                reportSchemaError("src-redefine.7.2.1", new Object []{name.localpart}, elmNode);
                break;
            case GROUP_TYPE:
                reportSchemaError("src-redefine.6.2.1", new Object []{name.localpart}, elmNode);
                break;
            }
            return null;
        }
        return retObj;
    } // getGrpOrAttrGrpRedefinedByRestriction(int, QName, XSDocumentInfo):  Object

    // Since ID constraints can occur in local elements, unless we
    // wish to completely traverse all our DOM trees looking for ID
    // constraints while we're building our global name registries,
    // which seems terribly inefficient, we need to resolve keyrefs
    // after all parsing is complete.  This we can simply do by running through
    // fIdentityConstraintRegistry and calling traverseKeyRef on all
    // of the KeyRef nodes.  This unfortunately removes this knowledge
    // from the elementTraverser class (which must ignore keyrefs),
    // but there seems to be no efficient way around this...
    protected void resolveKeyRefs() {
        for (int i=0; i<fKeyrefStackPos; i++) {
            Document keyrefDoc = DOMUtil.getDocument(fKeyrefs[i]);
            XSDocumentInfo keyrefSchemaDoc = (XSDocumentInfo)fDoc2XSDocumentMap.get(keyrefDoc);
            keyrefSchemaDoc.fNamespaceSupport.makeGlobal();
            keyrefSchemaDoc.fNamespaceSupport.setEffectiveContext( fKeyrefNamespaceContext[i] );
            SchemaGrammar keyrefGrammar = fGrammarBucket.getGrammar(keyrefSchemaDoc.fTargetNamespace);
            // need to set <keyref> to hidden before traversing it,
            // because it has global scope
            DOMUtil.setHidden(fKeyrefs[i]);
            fKeyrefTraverser.traverse(fKeyrefs[i], fKeyrefElems[i], keyrefSchemaDoc, keyrefGrammar);
        }
    } // end resolveKeyRefs

    // an accessor method.  Just makes sure callers
    // who want the Identity constraint registry vaguely know what they're about.
    protected Hashtable getIDRegistry() {
        return fUnparsedIdentityConstraintRegistry;
    }

    // This method squirrels away <keyref> declarations--along with the element
    // decls and namespace bindings they might find handy.
    protected void storeKeyRef (Element keyrefToStore, XSDocumentInfo schemaDoc,
                                XSElementDecl currElemDecl) {
        String keyrefName = DOMUtil.getAttrValue(keyrefToStore, SchemaSymbols.ATT_NAME);
        if (keyrefName.length() != 0) {
            String keyrefQName = schemaDoc.fTargetNamespace == null?
                                 "," + keyrefName: schemaDoc.fTargetNamespace+","+keyrefName;
            checkForDuplicateNames(keyrefQName, fUnparsedIdentityConstraintRegistry, keyrefToStore, schemaDoc);
        }
        // now set up all the registries we'll need...

        // check array sizes
        if (fKeyrefStackPos == fKeyrefs.length) {
            Element [] elemArray = new Element [fKeyrefStackPos + INC_KEYREF_STACK_AMOUNT];
            System.arraycopy(fKeyrefs, 0, elemArray, 0, fKeyrefStackPos);
            fKeyrefs = elemArray;
            XSElementDecl [] declArray = new XSElementDecl [fKeyrefStackPos + INC_KEYREF_STACK_AMOUNT];
            System.arraycopy(fKeyrefElems, 0, declArray, 0, fKeyrefStackPos);
            fKeyrefElems = declArray;
            String[][] stringArray = new String [fKeyrefStackPos + INC_KEYREF_STACK_AMOUNT][];
            System.arraycopy(fKeyrefNamespaceContext, 0, stringArray, 0, fKeyrefStackPos);
            fKeyrefNamespaceContext = stringArray;
        }
        fKeyrefs[fKeyrefStackPos] = keyrefToStore;
        fKeyrefElems[fKeyrefStackPos] = currElemDecl;
        fKeyrefNamespaceContext[fKeyrefStackPos++] = schemaDoc.fNamespaceSupport.getEffectiveLocalContext();
    } // storeKeyref (Element, XSDocumentInfo, XSElementDecl): void

    private static final String[] DOC_ERROR_CODES = {
        "src-include.0", "src-redefine.0", "src-import.0", "schema_reference.4",
        "schema_reference.4", "schema_reference.4", "schema_reference.4", "schema_reference.4"
    };
    
    // This method is responsible for schema resolution.  If it finds
    // a schema document that the XMLEntityResolver resolves to with
    // the given namespace and hint, it returns it.  It returns true
    // if this is the first time it's seen this document, false
    // otherwise.  schemaDoc is null if and only if no schema document
    // was resolved to.
    private Document getSchema(XSDDescription desc,
                               boolean mustResolve, Element referElement) {
        XMLInputSource schemaSource=null;
        try {
            schemaSource = fLocationResolver.resolveEntity(desc);
        }
        catch (IOException ex) {
            if (mustResolve) {
                reportSchemaError(DOC_ERROR_CODES[desc.getContextType()],
                                  new Object[]{desc.getLocationHints()[0]},
                                  referElement); 
            }
            else {
                reportSchemaWarning(DOC_ERROR_CODES[desc.getContextType()],
                                    new Object[]{desc.getLocationHints()[0]},
                                    referElement);
            }
        }
        return getSchema(desc.getTargetNamespace(), schemaSource, mustResolve, desc.getContextType(), referElement);
    } // getSchema(String, String, String, boolean, short):  Document

    private Document getSchema(String schemaNamespace, XMLInputSource schemaSource,
                               boolean mustResolve, short referType, Element referElement) {

        boolean hasInput = true;
        // contents of this method will depend on the system we adopt for entity resolution--i.e., XMLEntityHandler, EntityHandler, etc.
        Document schemaDoc = null;
        try {
            // when the system id and byte stream and character stream
            // of the input source are all null, it's
            // impossible to find the schema document. so we skip in
            // this case. otherwise we'll receive some NPE or
            // file not found errors. but schemaHint=="" is perfectly
            // legal for import.
            if (schemaSource != null &&
                (schemaSource.getSystemId() != null ||
                 schemaSource.getByteStream() != null ||
                 schemaSource.getCharacterStream() != null)) {

                // When the system id of the input source is used, first try to
                // expand it, and check whether the same document has been
                // parsed before. If so, return the document corresponding to
                // that system id.
                String schemaId = null;
                XSDKey key = null;
                if (schemaSource.getByteStream() == null &&
                    schemaSource.getCharacterStream() == null) {
                    schemaId = XMLEntityManager.expandSystemId(schemaSource.getSystemId(), schemaSource.getBaseSystemId());
                    key = new XSDKey(schemaId, referType, schemaNamespace);
                    if (fTraversed.get(key) != null) {
                        fLastSchemaWasDuplicate = true;
                        return(Document)(fTraversed.get(key));
                    }
                }
                fSchemaParser.reset();
                fSchemaParser.parse(schemaSource);
                schemaDoc = fSchemaParser.getDocument();
                // now we need to store the mapping information from system id
                // to the document. also from the document to the system id.
                if (schemaId != null) {
                    fTraversed.put(key, schemaDoc );
                    fDoc2SystemId.put(schemaDoc, schemaId );
                }
                fLastSchemaWasDuplicate = false;
                return schemaDoc;
            }
            else {
                hasInput = false;
            }
        }
        catch (IOException ex) {
        }
        
        // either an error occured (exception), or empty input source was
        // returned, we need to report an error or a warning
        if (mustResolve) {
            reportSchemaError(DOC_ERROR_CODES[referType],
                              new Object[]{schemaSource.getSystemId()},
                              referElement); 
        }
        else if (hasInput) {
            reportSchemaWarning(DOC_ERROR_CODES[referType],
                                new Object[]{schemaSource.getSystemId()},
                                referElement); 
        }

        fLastSchemaWasDuplicate = false;
        return null;
    } // getSchema(String, XMLInputSource, boolean, boolean): Document

    // initialize all the traversers.
    // this should only need to be called once during the construction
    // of this object; it creates the traversers that will be used to

    // construct schemaGrammars.
    private void createTraversers() {
        fAttributeChecker = new XSAttributeChecker(this);
        fAttributeGroupTraverser = new XSDAttributeGroupTraverser(this, fAttributeChecker);
        fAttributeTraverser = new XSDAttributeTraverser(this, fAttributeChecker);
        fComplexTypeTraverser = new XSDComplexTypeTraverser(this, fAttributeChecker);
        fElementTraverser = new XSDElementTraverser(this, fAttributeChecker);
        fGroupTraverser = new XSDGroupTraverser(this, fAttributeChecker);
        fKeyrefTraverser = new XSDKeyrefTraverser(this, fAttributeChecker);
        fNotationTraverser = new XSDNotationTraverser(this, fAttributeChecker);
        fSimpleTypeTraverser = new XSDSimpleTypeTraverser(this, fAttributeChecker);
        fUniqueOrKeyTraverser = new XSDUniqueOrKeyTraverser(this, fAttributeChecker);
        fWildCardTraverser = new XSDWildcardTraverser(this, fAttributeChecker);
    } // createTraversers()

    // before parsing a schema, need to reset all traversers and
    // clear all registries
    void prepare() {
        fUnparsedAttributeRegistry.clear();
        fUnparsedAttributeGroupRegistry.clear();
        fUnparsedElementRegistry.clear();
        fUnparsedGroupRegistry.clear();
        fUnparsedIdentityConstraintRegistry.clear();
        fUnparsedNotationRegistry.clear();
        fUnparsedTypeRegistry.clear();

        fXSDocumentInfoRegistry.clear();
        fDependencyMap.clear();
        fTraversed.clear();
        fDoc2SystemId.clear();
        fDoc2XSDocumentMap.clear();
        fRedefine2XSDMap.clear();
        fRedefine2NSSupport.clear();
        fAllTNSs.removeAllElements();
        fImportMap.clear();
        fRoot = null;
        fLastSchemaWasDuplicate = false;

        // clear local element stack
        for (int i = 0; i < fLocalElemStackPos; i++) {
            fParticle[i] = null;
            fLocalElementDecl[i] = null;
            fLocalElemNamespaceContext[i] = null;
        }
        fLocalElemStackPos = 0;

        // and do same for keyrefs.
        for (int i = 0; i < fKeyrefStackPos; i++) {
            fKeyrefs[i] = null;
            fKeyrefElems[i] = null;
            fKeyrefNamespaceContext[i] = null;
        }
        fKeyrefStackPos = 0;

        // reset traversers
        fAttributeChecker.reset(fSymbolTable);
        fAttributeGroupTraverser.reset(fSymbolTable);
        fAttributeTraverser.reset(fSymbolTable);
        fComplexTypeTraverser.reset(fSymbolTable);
        fElementTraverser.reset(fSymbolTable);
        fGroupTraverser.reset(fSymbolTable);
        fKeyrefTraverser.reset(fSymbolTable);
        fNotationTraverser.reset(fSymbolTable);
        fSimpleTypeTraverser.reset(fSymbolTable);
        fUniqueOrKeyTraverser.reset(fSymbolTable);
        fWildCardTraverser.reset(fSymbolTable);

        fRedefinedRestrictedAttributeGroupRegistry.clear();
        fRedefinedRestrictedGroupRegistry.clear();
    }
    public void setDeclPool (XSDeclarationPool declPool){
        fDeclPool = declPool;
    }
    // this method reset properties that might change between parses.
    // and process the jaxp schemaSource property
    public void reset(XMLErrorReporter errorReporter,
                      XMLEntityResolver entityResolver,
                      SymbolTable symbolTable,
                      String externalSchemaLocation,
                      String externalNoNSSchemaLocation,
                      XMLGrammarPool grammarPool) {

        fErrorReporter = errorReporter;
        fSymbolTable = symbolTable;
        fGrammarPool = grammarPool;

        EMPTY_STRING = fSymbolTable.addSymbol(SchemaSymbols.EMPTY_STRING);

        fLocationResolver.reset(entityResolver, externalSchemaLocation, externalNoNSSchemaLocation);

        try {
            fSchemaParser.setProperty(ERROR_HANDLER, fErrorReporter.getErrorHandler());
        }
        catch (Exception e) {
        }
        
        //now this part is done in XMLSchemaValidator
        //processJAXPSchemaSource(jaxpSchemaSource, entityResolver);
    } // reset(ErrorReporter, EntityResolver, SymbolTable)

    /**
     * Traverse all the deferred local elements. This method should be called
     * by traverseSchemas after we've done with all the global declarations.
     */
    void traverseLocalElements() {
        fElementTraverser.fDeferTraversingLocalElements = false;

        for (int i = 0; i < fLocalElemStackPos; i++) {
            Element currElem = fLocalElementDecl[i];
            XSDocumentInfo currSchema = (XSDocumentInfo)fDoc2XSDocumentMap.get(DOMUtil.getDocument(currElem));
            SchemaGrammar currGrammar = fGrammarBucket.getGrammar(currSchema.fTargetNamespace);
            fElementTraverser.traverseLocal (fParticle[i], currElem, currSchema, currGrammar, fAllContext[i]);
        }
    }

    // the purpose of this method is to keep up-to-date structures
    // we'll need for the feferred traversal of local elements.
    void fillInLocalElemInfo(Element elmDecl,
                             XSDocumentInfo schemaDoc,
                             int allContextFlags,
                             XSParticleDecl particle) {

        // if the stack is full, increase the size
        if (fParticle.length == fLocalElemStackPos) {
            // increase size
            XSParticleDecl[] newStackP = new XSParticleDecl[fLocalElemStackPos+INC_STACK_SIZE];
            System.arraycopy(fParticle, 0, newStackP, 0, fLocalElemStackPos);
            fParticle = newStackP;
            Element[] newStackE = new Element[fLocalElemStackPos+INC_STACK_SIZE];
            System.arraycopy(fLocalElementDecl, 0, newStackE, 0, fLocalElemStackPos);
            fLocalElementDecl = newStackE;
            int[] newStackI = new int[fLocalElemStackPos+INC_STACK_SIZE];
            System.arraycopy(fAllContext, 0, newStackI, 0, fLocalElemStackPos);
            fAllContext = newStackI;
            String [][] newStackN = new String [fLocalElemStackPos+INC_STACK_SIZE][];
            System.arraycopy(fLocalElemNamespaceContext, 0, newStackN, 0, fLocalElemStackPos);
            fLocalElemNamespaceContext = newStackN;
        }

        fParticle[fLocalElemStackPos] = particle;
        fLocalElementDecl[fLocalElemStackPos] = elmDecl;
        fAllContext[fLocalElemStackPos] = allContextFlags;
        fLocalElemNamespaceContext[fLocalElemStackPos++] = schemaDoc.fNamespaceSupport.getEffectiveLocalContext();
    } // end fillInLocalElemInfo(...)

    /** This method makes sure that
     * if this component is being redefined that it lives in the
     * right schema.  It then renames the component correctly.  If it
     * detects a collision--a duplicate definition--then it complains.
     * Note that redefines must be handled carefully:  if there
     * is a collision, it may be because we're redefining something we know about
     * or because we've found the thing we're redefining.
     */
    void checkForDuplicateNames(String qName,
                                Hashtable registry, Element currComp,
                                XSDocumentInfo currSchema) {
        Object objElem = null;
        // REVISIT:  when we add derivation checking, we'll have to make
        // sure that ID constraint collisions don't necessarily result in error messages.
        if ((objElem = registry.get(qName)) == null) {
            // just add it in!
            registry.put(qName, currComp);
        }
        else {
            Element collidingElem = (Element)objElem;
            if (collidingElem == currComp) return;
            Element elemParent = null;
            XSDocumentInfo redefinedSchema = null;
            // case where we've collided with a redefining element
            // (the parent of the colliding element is a redefine)
            boolean collidedWithRedefine = true;
            if ((DOMUtil.getLocalName((elemParent = DOMUtil.getParent(collidingElem))).equals(SchemaSymbols.ELT_REDEFINE))) {
                redefinedSchema = (XSDocumentInfo)(fRedefine2XSDMap.get(elemParent));
                // case where we're a redefining element.
            }
            else if ((DOMUtil.getLocalName(DOMUtil.getParent(currComp)).equals(SchemaSymbols.ELT_REDEFINE))) {
                redefinedSchema = (XSDocumentInfo)(fDoc2XSDocumentMap.get(DOMUtil.getDocument(collidingElem)));
                collidedWithRedefine = false;
            }
            if (redefinedSchema != null) { //redefinition involved somehow
                String newName = qName.substring(qName.lastIndexOf(',')+1)+REDEF_IDENTIFIER;
                if (redefinedSchema == currSchema) { // object comp. okay here
                    // now have to do some renaming...
                    currComp.setAttribute(SchemaSymbols.ATT_NAME, newName);
                    if (currSchema.fTargetNamespace == null)
                        registry.put(","+newName, currComp);
                    else
                        registry.put(currSchema.fTargetNamespace+","+newName, currComp);
                    // and take care of nested redefines by calling recursively:
                    if (currSchema.fTargetNamespace == null)
                        checkForDuplicateNames(","+newName, registry, currComp, currSchema);
                    else
                        checkForDuplicateNames(currSchema.fTargetNamespace+","+newName, registry, currComp, currSchema);
                }
                else { // we may be redefining the wrong schema
                    if (collidedWithRedefine) {
                        if (currSchema.fTargetNamespace == null)
                            checkForDuplicateNames(","+newName, registry, currComp, currSchema);
                        else
                            checkForDuplicateNames(currSchema.fTargetNamespace+","+newName, registry, currComp, currSchema);
                    }
                    else {
                        // error that redefined element in wrong schema
                        reportSchemaError("src-redefine.1", new Object [] {qName}, currComp);
                    }
                }
            }
            else {
                // we've just got a flat-out collision
                reportSchemaError("sch-props-correct.2", new Object []{qName}, currComp);
            }
        }
    } // checkForDuplicateNames(String, Hashtable, Element, XSDocumentInfo):void

    // the purpose of this method is to take the component of the
    // specified type and rename references to itself so that they
    // refer to the object being redefined.  It takes special care of
    // <group>s and <attributeGroup>s to ensure that information
    // relating to implicit restrictions is preserved for those
    // traversers.
    private void renameRedefiningComponents(XSDocumentInfo currSchema,
                                            Element child, String componentType,
                                            String oldName, String newName) {

        SchemaNamespaceSupport currNSMap = currSchema.fNamespaceSupport;
        if (componentType.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
            Element grandKid = DOMUtil.getFirstChildElement(child);
            if (grandKid == null) {
                reportSchemaError("src-redefine.5", null, child);
            }
            else {
                String grandKidName = grandKid.getLocalName();
                if (grandKidName.equals(SchemaSymbols.ELT_ANNOTATION)) {
                    grandKid = DOMUtil.getNextSiblingElement(grandKid);
                    grandKidName = grandKid.getLocalName();
                }
                if (grandKid == null) {
                    reportSchemaError("src-redefine.5", null, child);
                }
                else if (!grandKidName.equals(SchemaSymbols.ELT_RESTRICTION)) {
                    reportSchemaError("src-redefine.5", null, child);
                }
                else {
                    Object[] attrs = fAttributeChecker.checkAttributes(grandKid, false, currSchema);
                    QName derivedBase = (QName)attrs[XSAttributeChecker.ATTIDX_BASE];
                    if (derivedBase == null ||
                        derivedBase.uri != currSchema.fTargetNamespace ||
                        !derivedBase.localpart.equals(oldName)) {
                        reportSchemaError("src-redefine.5", null, child);
                    }
                    else {
                        // now we have to do the renaming...
                        if (derivedBase.prefix != null && derivedBase.prefix.length() > 0)
                            grandKid.setAttribute( SchemaSymbols.ATT_BASE,
                                                   derivedBase.prefix + ":" + newName );
                        else
                            grandKid.setAttribute( SchemaSymbols.ATT_BASE, newName );
//                        return true;
                    }
                    fAttributeChecker.returnAttrArray(attrs, currSchema);
                }
            }
        }
        else if (componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
            Element grandKid = DOMUtil.getFirstChildElement(child);
            if (grandKid == null) {
                reportSchemaError("src-redefine.5", null, child);
            }
            else {
                if (grandKid.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) {
                    grandKid = DOMUtil.getNextSiblingElement(grandKid);
                }
                if (grandKid == null) {
                    reportSchemaError("src-redefine.5", null, child);
                }
                else {
                    // have to go one more level down; let another pass worry whether complexType is valid.
                    Element greatGrandKid = DOMUtil.getFirstChildElement(grandKid);
                    if (greatGrandKid == null) {
                        reportSchemaError("src-redefine.5", null, grandKid);
                    }
                    else {
                        String greatGrandKidName = greatGrandKid.getLocalName();
                        if (greatGrandKidName.equals(SchemaSymbols.ELT_ANNOTATION)) {
                            greatGrandKid = DOMUtil.getNextSiblingElement(greatGrandKid);
                            greatGrandKidName = greatGrandKid.getLocalName();
                        }
                        if (greatGrandKid == null) {
                            reportSchemaError("src-redefine.5", null, grandKid);
                        }
                        else if (!greatGrandKidName.equals(SchemaSymbols.ELT_RESTRICTION) &&
                                 !greatGrandKidName.equals(SchemaSymbols.ELT_EXTENSION)) {
                            reportSchemaError("src-redefine.5", null, greatGrandKid);
                        }
                        else {
                            Object[] attrs = fAttributeChecker.checkAttributes(greatGrandKid, false, currSchema);
                            QName derivedBase = (QName)attrs[XSAttributeChecker.ATTIDX_BASE];
                            if (derivedBase == null ||
                                derivedBase.uri != currSchema.fTargetNamespace ||
                                !derivedBase.localpart.equals(oldName)) {
                                reportSchemaError("src-redefine.5", null, greatGrandKid);
                            }
                            else {
                                // now we have to do the renaming...
                                if (derivedBase.prefix != null && derivedBase.prefix.length() > 0)
                                    greatGrandKid.setAttribute( SchemaSymbols.ATT_BASE,
                                                                derivedBase.prefix + ":" + newName );
                                else
                                    greatGrandKid.setAttribute( SchemaSymbols.ATT_BASE,
                                                                newName );
//                                return true;
                            }
                        }
                    }
                }
            }
        }
        else if (componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
            String processedBaseName = (currSchema.fTargetNamespace == null)?
                                       ","+oldName:currSchema.fTargetNamespace+","+oldName;
            int attGroupRefsCount = changeRedefineGroup(processedBaseName, componentType, newName, child, currSchema);
            if (attGroupRefsCount > 1) {
                reportSchemaError("src-redefine.7.1", new Object []{new Integer(attGroupRefsCount)}, child);
            }
            else if (attGroupRefsCount == 1) {
//                return true;
            }
            else
                if (currSchema.fTargetNamespace == null)
                fRedefinedRestrictedAttributeGroupRegistry.put(processedBaseName, ","+newName);
            else
                fRedefinedRestrictedAttributeGroupRegistry.put(processedBaseName, currSchema.fTargetNamespace+","+newName);
        }
        else if (componentType.equals(SchemaSymbols.ELT_GROUP)) {
            String processedBaseName = (currSchema.fTargetNamespace == null)?
                                       ","+oldName:currSchema.fTargetNamespace+","+oldName;
            int groupRefsCount = changeRedefineGroup(processedBaseName, componentType, newName, child, currSchema);
            if (groupRefsCount > 1) {
                reportSchemaError("src-redefine.6.1.1", new Object []{new Integer(groupRefsCount)}, child);
            }
            else if (groupRefsCount == 1) {
//                return true;
            }
            else {
                if (currSchema.fTargetNamespace == null)
                    fRedefinedRestrictedGroupRegistry.put(processedBaseName, ","+newName);
                else
                    fRedefinedRestrictedGroupRegistry.put(processedBaseName, currSchema.fTargetNamespace+","+newName);
            }
        }
        else {
            reportSchemaError("Internal-Error", new Object [] {"could not handle this particular <redefine>; please submit your schemas and instance document in a bug report!"}, child);
        }
        // if we get here then we must have reported an error and failed somewhere...
//        return false;
    } // renameRedefiningComponents(XSDocumentInfo, Element, String, String, String):void

    // this method takes a name of the form a:b, determines the URI mapped
    // to by a in the current SchemaNamespaceSupport object, and returns this
    // information in the form (nsURI,b) suitable for lookups in the global
    // decl Hashtables.
    // REVISIT: should have it return QName, instead of String. this would
    //          save lots of string concatenation time. we can use
    //          QName#equals() to compare two QNames, and use QName directly
    //          as a key to the SymbolHash.
    //          And when the DV's are ready to return compiled values from
    //          validate() method, we should just call QNameDV.validate()
    //          in this method.
    private String findQName(String name, XSDocumentInfo schemaDoc) {
        SchemaNamespaceSupport currNSMap = schemaDoc.fNamespaceSupport;
        int colonPtr = name.indexOf(':');
        String prefix = EMPTY_STRING;
        if (colonPtr > 0)
            prefix = name.substring(0, colonPtr);
        String uri = currNSMap.getURI(fSymbolTable.addSymbol(prefix));
        String localpart = (colonPtr == 0)?name:name.substring(colonPtr+1);
        if (prefix == this.EMPTY_STRING && uri == null && schemaDoc.fIsChameleonSchema)
            uri = schemaDoc.fTargetNamespace;
        if (uri == null)
            return ","+localpart;
        return uri+","+localpart;
    } // findQName(String, XSDocumentInfo):  String

    // This function looks among the children of curr for an element of type elementSought.
    // If it finds one, it evaluates whether its ref attribute contains a reference
    // to originalQName.  If it does, it returns 1 + the value returned by
    // calls to itself on all other children.  In all other cases it returns 0 plus
    // the sum of the values returned by calls to itself on curr's children.
    // It also resets the value of ref so that it will refer to the renamed type from the schema
    // being redefined.
    private int changeRedefineGroup(String originalQName, String elementSought,
                                    String newName, Element curr, XSDocumentInfo schemaDoc) {
        SchemaNamespaceSupport currNSMap = schemaDoc.fNamespaceSupport;
        int result = 0;
        for (Element child = DOMUtil.getFirstChildElement(curr);
            child != null; child = DOMUtil.getNextSiblingElement(child)) {
            String name = child.getLocalName();
            if (!name.equals(elementSought))
                result += changeRedefineGroup(originalQName, elementSought, newName, child, schemaDoc);
            else {
                String ref = child.getAttribute( SchemaSymbols.ATT_REF );
                if (ref.length() != 0) {
                    String processedRef = findQName(ref, schemaDoc);
                    if (originalQName.equals(processedRef)) {
                        String prefix = EMPTY_STRING;
                        String localpart = ref;
                        int colonptr = ref.indexOf(":");
                        if (colonptr > 0) {
                            prefix = ref.substring(0,colonptr);
                            child.setAttribute(SchemaSymbols.ATT_REF, prefix + ":" + newName);
                        }
                        else
                            child.setAttribute(SchemaSymbols.ATT_REF, newName);
                        result++;
                        if (elementSought.equals(SchemaSymbols.ELT_GROUP)) {
                            String minOccurs = child.getAttribute( SchemaSymbols.ATT_MINOCCURS );
                            String maxOccurs = child.getAttribute( SchemaSymbols.ATT_MAXOCCURS );
                            if (!((maxOccurs.length() == 0 || maxOccurs.equals("1"))
                                  && (minOccurs.length() == 0 || minOccurs.equals("1")))) {
                                reportSchemaError("src-redefine.6.1.2", new Object [] {ref}, child);
                            }
                        }
                    }
                } // if ref was null some other stage of processing will flag the error
            }
        }
        return result;
    } // changeRedefineGroup

    // this method returns the XSDocumentInfo object that contains the
    // component corresponding to decl.  If components from this
    // document cannot be referred to from those of currSchema, this
    // method returns null; it's up to the caller to throw an error.
    // @param:  currSchema:  the XSDocumentInfo object containing the
    // decl ref'ing us.
    // @param:  decl:  the declaration being ref'd.
    private XSDocumentInfo findXSDocumentForDecl(XSDocumentInfo currSchema,
                                                 Element decl) {

        if (DEBUG_NODE_POOL) {
            System.out.println("DOCUMENT NS:"+ currSchema.fTargetNamespace+" hashcode:"+ ((Object)currSchema.fSchemaDoc).hashCode());
        }
        Document declDoc = DOMUtil.getDocument(decl);
        Object temp = fDoc2XSDocumentMap.get(declDoc);
        if (temp == null) {
            // something went badly wrong; we don't know this doc?
            return null;
        }
        XSDocumentInfo declDocInfo = (XSDocumentInfo)temp;
        return declDocInfo;
        /*********
        Logic here is unnecessary after schema WG's recent decision to allow
        schema components from one document to refer to components of any other,
        so long as there's some include/import/redefine path amongst them.
        If they rver reverse this decision the code's right here though...  - neilg
        // now look in fDependencyMap to see if this is reachable
        if(((Vector)fDependencyMap.get(currSchema)).contains(declDocInfo)) {
            return declDocInfo;
        }
        // obviously the requesting doc didn't include, redefine or
        // import the one containing decl...
        return null;
        **********/
    } // findXSDocumentForDecl(XSDocumentInfo, Element):  XSDocumentInfo

    // returns whether more than <annotation>s occur in children of elem
    private boolean nonAnnotationContent(Element elem) {
        for(Element child = DOMUtil.getFirstChildElement(elem); child != null; child = DOMUtil.getNextSiblingElement(child)) {
            if(!(DOMUtil.getLocalName(child).equals(SchemaSymbols.ELT_ANNOTATION))) return true;
        }
        return false;
    } // nonAnnotationContent(Element):  boolean

    private void setSchemasVisible(XSDocumentInfo startSchema) {
        if (DOMUtil.isHidden(startSchema.fSchemaDoc)) {
            // make it visible
            DOMUtil.setVisible(startSchema.fSchemaDoc);
            Vector dependingSchemas = (Vector)fDependencyMap.get(startSchema);
            for (int i = 0; i < dependingSchemas.size(); i++) {
                setSchemasVisible((XSDocumentInfo)dependingSchemas.elementAt(i));
            }
        }
        // if it's visible already than so must be its children
    } // setSchemasVisible(XSDocumentInfo): void

    private SimpleLocator xl = new SimpleLocator();
    
    /**
     * Extract location information from an Element node, and create a
     * new SimpleLocator object from such information. Returning null means
     * no information can be retrieved from the element.
     */
    public SimpleLocator element2Locator(Element e) {
        if (!(e instanceof ElementNSImpl))
            return null;
        
        SimpleLocator l = new SimpleLocator();
        return element2Locator(e, l) ? l : null;
    }
    
    /**
     * Extract location information from an Element node, store such
     * information in the passed-in SimpleLocator object, then return
     * true. Returning false means can't extract or store such information.
     */
    public boolean element2Locator(Element e, SimpleLocator l) {
        if (!(e instanceof ElementNSImpl) || l == null)
            return false;
            
        ElementNSImpl ele = (ElementNSImpl)e;
        // get system id from document object
        Document doc = ele.getOwnerDocument();
        String sid = (String)fDoc2SystemId.get(doc);
        // line/column numbers are stored in the element node
        int line = ele.getLineNumber();
        int column = ele.getColumnNumber();
        l.setValues(sid, sid, line, column);
        return true;
    }
    
    void reportSchemaError(String key, Object[] args, Element ele) {
        if (element2Locator(ele, xl)) {
            fErrorReporter.reportError(xl, XSMessageFormatter.SCHEMA_DOMAIN,
                                       key, args, XMLErrorReporter.SEVERITY_ERROR);
        }
        else {
            fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                       key, args, XMLErrorReporter.SEVERITY_ERROR);
        }
    }

    void reportSchemaWarning(String key, Object[] args, Element ele) {
        if (element2Locator(ele, xl)) {
            fErrorReporter.reportError(xl, XSMessageFormatter.SCHEMA_DOMAIN,
                                       key, args, XMLErrorReporter.SEVERITY_WARNING);
        }
        else {
            fErrorReporter.reportError(XSMessageFormatter.SCHEMA_DOMAIN,
                                       key, args, XMLErrorReporter.SEVERITY_WARNING);
        }
    }

    // used to identify a reference to a schema document
    // if the same document is referenced twice with the same key, then
    // we only need to parse it once.
    private static class XSDKey {
        String systemId;
        short  referType;
        String referNS;

        XSDKey(String systemId, short referType, String referNS) {
            this.systemId = systemId;
            this.referType = referType;
            this.referNS = referNS;
        }
        
        public int hashCode() {
            if (referType == XSDDescription.CONTEXT_INCLUDE ||
                referType == XSDDescription.CONTEXT_REDEFINE) {
                return systemId.hashCode();
            }
            else {
                return referNS == null ? 0 : referNS.hashCode();
            }
        }

        public boolean equals(Object obj) {
            if (!(obj instanceof XSDKey)) {
                return false;
            }
            XSDKey key = (XSDKey)obj;
            
            // for include and redefine
            if (referType == XSDDescription.CONTEXT_INCLUDE ||
                referType == XSDDescription.CONTEXT_REDEFINE ||
                key.referType == XSDDescription.CONTEXT_INCLUDE ||
                key.referType == XSDDescription.CONTEXT_REDEFINE) {
                // only when the same document is included (or redefined)
                // twice by the same namespace, we consider it a duplicate,
                // and ignore the second one.
                return referType == key.referType &&
                       referNS == key.referNS &&
                       systemId.equals(key.systemId);
            }

            // for import/instance/preparse, as long as the target namespaces
            // are the same, we don't need to parse the document again
            return referNS == key.referNS;
        }
    }
    
} // XSDHandler