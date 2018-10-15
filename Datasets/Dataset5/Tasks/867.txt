dependencies.addElement(currSchemaInfo);

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights
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

package org.apache.xerces.impl.v2;

import org.apache.xerces.impl.v2.datatypes.*;

import org.apache.xerces.impl.XMLErrorReporter;
import org.apache.xerces.parsers.DOMParser;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.parser.XMLEntityResolver;
import org.apache.xerces.xni.parser.XMLInputSource;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.DOMUtil;

import org.w3c.dom.Document;
import org.w3c.dom.Attr;
import org.w3c.dom.Element;

import java.util.Hashtable;
import java.util.Stack;
import java.util.Vector;
import java.io.IOException;

// REVISIT:  needed for the main method
import org.apache.xerces.util.EntityResolverWrapper;
import org.xml.sax.helpers.DefaultHandler;
import java.util.Enumeration;
import java.io.FileReader;
import java.io.IOException;
import org.xml.sax.EntityResolver;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

/**
 * The purpose of this class is to co-ordinate the construction of a
 * grammar object corresponding to a schema.  To do this, it must be
 * prepared to parse several schema documents (for instance if the
 * schema document originally referred to contains <include> or
 * <redefined> information items).  If any of the schemas imports a
 * schema, other grammars may be constructed as a side-effect.
 *
 * @author Neil Graham, IBM
 * @version $Id$
 */

class XSDHandler {

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

    public String EMPTY_STRING;

    //
    //protected data that can be accessable by any traverser
    // stores <notation> decl
    protected Hashtable fNotationRegistry = new Hashtable();

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

    // the presence of an XSDocumentInfo object in this vector means it has
    // been completely traversed; needed to handle mutual <include>s
    // etc.
    private Vector fTraversed = new Vector();

    // the primary XSDocumentInfo we were called to parse
    private XSDocumentInfo fRoot = null;

    // This hashtable's job is to act as a link between the document
    // node at the root of the parsed schema's tree and its
    // XSDocumentInfo object.
    private Hashtable fDoc2XSDocumentMap = new Hashtable();

    // map between <redefine> elements and the XSDocumentInfo
    // objects that correspond to the documents being redefined.
    private Hashtable fRedefine2XSDMap = new Hashtable();

    // these objects store a mapping between the names of redefining
    // groups/attributeGroups and the groups/AttributeGroups which
    // they redefine by restriction (implicitly).  It is up to the
    // Group and AttributeGroup traversers to check these restrictions for
    // validity.
    private Hashtable fRedefinedRestrictedAttributeGroupRegistry = new Hashtable();
    private Hashtable fRedefinedRestrictedGroupRegistry = new Hashtable();

    // the XMLErrorReporter
    private XMLErrorReporter fErrorReporter;

    // the XSAttributeChecker
    private XSAttributeChecker fAttributeChecker;

    // the SubstitutionGroupHandler
    private SubstitutionGroupHandler fSubGroupHandler;

    // the XMLEntityResolver
    private XMLEntityResolver fEntityResolver;

    // the symbol table
    private SymbolTable fSymbolTable;

    // the GrammarResolver
    private XSGrammarResolver fGrammarResolver;

    //************ Traversers **********
    XSDAttributeGroupTraverser fAttributeGroupTraverser;
    XSDAttributeTraverser fAttributeTraverser;
    XSDComplexTypeTraverser fComplexTypeTraverser;
    XSDElementTraverser fElementTraverser;
    XSDGroupTraverser fGroupTraverser;
    XSDKeyrefTraverser fKeyrefTraverser;;
    XSDNotationTraverser fNotationTraverser;
    XSDSimpleTypeTraverser fSimpleTypeTraverser;
    XSDUniqueOrKeyTraverser fUniqueOrKeyTraverser;
    XSDWildcardTraverser fWildCardTraverser;

    DOMParser fSchemaParser;

    // these data members are needed for the deferred traversal
    // of local elements.

    // the initial size of the array to store deferred local elements
    private static final int INIT_STACK_SIZE = 30;
    // the incremental size of the array to store deferred local elements
    private static final int INC_STACK_SIZE  = 10;
    // current position of the array (# of deferred local elements)
    private int fLocalElemStackPos;

    private XSParticleDecl[] fParticle;
    private Element[] fLocalElementDecl;
    private int[] fAllContext;
    private String [][] fLocalElemNamespaceContext;

    // Constructors

    // it should be possible to use the same XSDHandler to parse
    // multiple schema documents; this will allow one to be
    // constructed.
    XSDHandler (XSGrammarResolver gResolver) {
        fGrammarResolver = gResolver;

        // REVISIT: do we use shadowed or synchronized symbol table of
        //          SchemaSymbols.fSymbolTable?
        fSchemaParser = new DOMParser(new SchemaSymbols.SchemaSymbolTable());
        // set ErrorHandler and EntityResolver (doesn't seem that
        // XMLErrorHandler or XMLEntityResolver will work with
        // standard DOMParser...
        //REVISIT: disable deferred dom expansion. there are bugs.
        try {
            fSchemaParser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
        } catch (Exception e) {}

        createTraversers();
    } // end constructor

    // This method initiates the parse of a schema.  It will likely be
    // called from the Validator and it will make the
    // resulting grammar available; it returns a reference to this object just
    // in case.  An ErrorHandler, EntityResolver, GrammarPool and SymbolTable must
    // already have been set; the last thing this method does is reset
    // this object (i.e., clean the registries, etc.).
    SchemaGrammar parseSchema(String schemaNamespace,
                              String schemaHint) {

        // first phase:  construct trees.
        Document schemaRoot = getSchema(schemaNamespace, schemaHint);
        fRoot = constructTrees(schemaRoot);
        if(fRoot == null) {
            // REVISIT:  something went wrong; print error about no schema found
            fElementTraverser.reportGenericSchemaError("Could not locate a schema document!");
            return null;
        }
        fDoc2XSDocumentMap.put(schemaRoot, fRoot);

        // second phase:  fill global registries.
        buildGlobalNameRegistries();

        // third phase:  call traversers
        traverseSchemas();

        // fourth:  handle local element decls
        traverseLocalElements();

        // fifth phase:  handle Keyrefs
//        resolveKeyRefs();

        // sixth phase:  handle derivation constraint checking
        // and UPA, and validate attribute of non-schema namespaces
        fAttributeChecker.checkNonSchemaAttributes(fGrammarResolver);

        // and return.
        return fGrammarResolver.getGrammar(fRoot.fTargetNamespace);
    } // end parseSchema

    // may wish to have setter methods for ErrorHandler,
    // EntityResolver...

    // This method does several things:
    // It constructs an instance of an XSDocumentInfo object using the
    // schemaRoot node.  Then, for each <include>,
    // <redefine>, and <import> children, it attempts to resolve the
    // requested schema document, initiates a DOM parse, and calls
    // itself recursively on that document's root.  It also records in
    // the DependencyMap object what XSDocumentInfo objects its XSDocumentInfo
    // depends on.
    protected XSDocumentInfo constructTrees(Document schemaRoot) {
        if(schemaRoot == null) return null;
        XSDocumentInfo currSchemaInfo = new XSDocumentInfo(schemaRoot, fAttributeChecker, fSymbolTable);
        SchemaGrammar sg = null;
        if((sg = fGrammarResolver.getGrammar(currSchemaInfo.fTargetNamespace)) == null) {
            sg = new SchemaGrammar(fSymbolTable, currSchemaInfo.fTargetNamespace);
            fGrammarResolver.putGrammar(sg);
        }

        Vector dependencies = new Vector();
        dependencies.add(currSchemaInfo);
        Element rootNode = DOMUtil.getRoot(schemaRoot);

        String schemaNamespace=EMPTY_STRING;
        String schemaHint=EMPTY_STRING;
        Document newSchemaRoot = null;
        for (Element child =
             DOMUtil.getFirstChildElement(rootNode);
            child != null;
            child = DOMUtil.getNextSiblingElement(child)) {
            String localName = DOMUtil.getLocalName(child);
            if (localName.equals(SchemaSymbols.ELT_ANNOTATION))
                continue;
            else if (localName.equals(SchemaSymbols.ELT_IMPORT)) {
                // have to handle some validation here too!
                // call XSAttributeChecker to fill in attrs
                Object[] includeAttrs = fAttributeChecker.checkAttributes(child, true, currSchemaInfo);
                schemaHint = (String)includeAttrs[XSAttributeChecker.ATTIDX_SCHEMALOCATION];
                schemaNamespace = (String)includeAttrs[XSAttributeChecker.ATTIDX_NAMESPACE];
                fAttributeChecker.returnAttrArray(includeAttrs, currSchemaInfo);
                newSchemaRoot = getSchema(schemaNamespace, schemaHint);
            }
            else if ((localName.equals(SchemaSymbols.ELT_INCLUDE)) ||
                     (localName.equals(SchemaSymbols.ELT_REDEFINE))) {
                // validation for redefine/include will be the same here; just
                // make sure TNS is right (don't care about redef contents
                // yet).
                Object[] includeAttrs = fAttributeChecker.checkAttributes(child, true, currSchemaInfo);
                schemaHint = (String)includeAttrs[XSAttributeChecker.ATTIDX_SCHEMALOCATION];
                fAttributeChecker.returnAttrArray(includeAttrs, currSchemaInfo);
                newSchemaRoot = getSchema(EMPTY_STRING, schemaHint);
            }
            else {
                // no more possibility of schema references in well-formed
                // schema...
                break;
            }
            XSDocumentInfo newSchemaInfo = constructTrees(newSchemaRoot);
            if (localName.equals(SchemaSymbols.ELT_REDEFINE)) {
                // must record which schema we're redefining so that we can
                // rename the right things later!
                fRedefine2XSDMap.put(child, newSchemaInfo);
            }
            dependencies.addElement(newSchemaInfo);
            fDoc2XSDocumentMap.put(newSchemaRoot, newSchemaInfo);
            newSchemaRoot = null;
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
        while(!schemasToProcess.empty()) {
            XSDocumentInfo currSchemaDoc =
                (XSDocumentInfo)schemasToProcess.pop();
            Document currDoc = currSchemaDoc.fSchemaDoc;
            if(DOMUtil.isHidden(currDoc)) {
                // must have processed this already!
                continue;
            }
            Element currRoot = DOMUtil.getRoot(currDoc);

            // process this schema's global decls
            boolean dependenciesCanOccur = true;
            for(Element globalComp =
                    DOMUtil.getFirstChildElement(currRoot);
                    globalComp != null;
                    globalComp = DOMUtil.getNextSiblingElement(globalComp)){
                // this loop makes sure the <schema> element ordering is
                // also valid.
                if(DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_ANNOTATION)) {
                    //skip it; traverse it later
                    continue;
                } else if(DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_INCLUDE) ||
                        DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_IMPORT)) {
                    if(!dependenciesCanOccur) {
                        // REVISIT:  schema element ordreing violation
                    }
                    // we've dealt with this; mark as traversed
                    DOMUtil.setHidden(globalComp);
                } else if(DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_REDEFINE)) {
                    if(!dependenciesCanOccur) {
                        // REVISIT:  schema element ordreing violation
                    }
                    for(Element redefineComp = DOMUtil.getFirstChildElement(globalComp);
                            redefineComp != null;
                            redefineComp = DOMUtil.getNextSiblingElement(redefineComp)) {
                        String lName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME);
                        if(lName.length() == 0) // an error we'll catch later
                            continue;
                        String qName = currSchemaDoc.fTargetNamespace +","+lName;
                        String componentType = DOMUtil.getLocalName(redefineComp);
                        if(componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                            checkForDuplicateNames(qName, fUnparsedAttributeGroupRegistry, globalComp, currSchemaDoc);
                            // the check will have changed our name;
                            String targetLName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME);
                            // and all we need to do is error-check+rename our kkids:
                            renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_ATTRIBUTEGROUP,
                                lName, targetLName);
                        } else if((componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) ||
                                (componentType.equals(SchemaSymbols.ELT_SIMPLETYPE))) {
                            checkForDuplicateNames(qName, fUnparsedTypeRegistry, globalComp, currSchemaDoc);
                            // the check will have changed our name;
                            String targetLName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME);
                            // and all we need to do is error-check+rename our kkids:
                            if(componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                            renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_COMPLEXTYPE,
                                lName, targetLName);
                            } else { // must be simpleType
                            renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_SIMPLETYPE,
                                lName, targetLName);
                            }
                        } else if(componentType.equals(SchemaSymbols.ELT_GROUP)) {
                            checkForDuplicateNames(qName, fUnparsedGroupRegistry, globalComp, currSchemaDoc);
                            // the check will have changed our name;
                            String targetLName = DOMUtil.getAttrValue(redefineComp, SchemaSymbols.ATT_NAME);
                            // and all we need to do is error-check+rename our kkids:
                            renameRedefiningComponents(currSchemaDoc, redefineComp, SchemaSymbols.ELT_GROUP,
                                lName, targetLName);
                        } else {
                            // REVISIT:  report schema element ordering error
                        }
                    } // end march through <redefine> children
                    // and now set as traversed
                    DOMUtil.setHidden(globalComp);
                } else {
                    dependenciesCanOccur = false;
                    String lName = DOMUtil.getAttrValue(globalComp, SchemaSymbols.ATT_NAME);
                    if(lName.length() == 0) // an error we'll catch later
                        continue;
                    String qName = currSchemaDoc.fTargetNamespace +","+lName;
                    String componentType = DOMUtil.getLocalName(globalComp);
                    if(componentType.equals(SchemaSymbols.ELT_ATTRIBUTE)) {
                        checkForDuplicateNames(qName, fUnparsedAttributeRegistry, globalComp, currSchemaDoc);
                    } else if(componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                        checkForDuplicateNames(qName, fUnparsedAttributeGroupRegistry, globalComp, currSchemaDoc);
                    } else if((componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) ||
                            (componentType.equals(SchemaSymbols.ELT_SIMPLETYPE))) {
                        checkForDuplicateNames(qName, fUnparsedTypeRegistry, globalComp, currSchemaDoc);
                    } else if(componentType.equals(SchemaSymbols.ELT_ELEMENT)) {
                        checkForDuplicateNames(qName, fUnparsedElementRegistry, globalComp, currSchemaDoc);
                    } else if(componentType.equals(SchemaSymbols.ELT_GROUP)) {
                        checkForDuplicateNames(qName, fUnparsedGroupRegistry, globalComp, currSchemaDoc);
                    } else if(componentType.equals(SchemaSymbols.ELT_NOTATION)) {
                        checkForDuplicateNames(qName, fUnparsedNotationRegistry, globalComp, currSchemaDoc);
                    } else {
                        // REVISIT:  report schema element ordering error
                    }
                }
            } // end for

            // now we're done with this one!
            DOMUtil.setHidden(currDoc);
            // now add the schemas this guy depends on
            Vector currSchemaDepends = (Vector)fDependencyMap.get(currSchemaDoc);
            for(int i = 0; i < currSchemaDepends.size(); i++) {
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
        while(!schemasToProcess.empty()) {
            XSDocumentInfo currSchemaDoc =
                (XSDocumentInfo)schemasToProcess.pop();
            Document currDoc = currSchemaDoc.fSchemaDoc;
            SchemaGrammar currSG = fGrammarResolver.getGrammar(currSchemaDoc.fTargetNamespace);
            if(DOMUtil.isHidden(currDoc)) {
                // must have processed this already!
                continue;
            }
            Element currRoot = DOMUtil.getRoot(currDoc);

            // traverse this schema's global decls
            for(Element globalComp =
                    DOMUtil.getFirstVisibleChildElement(currRoot);
                    globalComp != null;
                    globalComp = DOMUtil.getNextVisibleSiblingElement(globalComp)){
                // We'll always want to set this as hidden!
                DOMUtil.setHidden(globalComp);
                String componentType = DOMUtil.getLocalName(globalComp);
                // includes and imports will not show up here!
                if(DOMUtil.getLocalName(globalComp).equals(SchemaSymbols.ELT_REDEFINE)) {
                    for(Element redefinedComp = DOMUtil.getFirstVisibleChildElement(globalComp);
                            redefinedComp != null;
                            redefinedComp = DOMUtil.getNextVisibleSiblingElement(redefinedComp)) {
                        String redefinedComponentType = DOMUtil.getLocalName(redefinedComp);
                        DOMUtil.setHidden(redefinedComp);
                        if(redefinedComponentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                            fAttributeGroupTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        } else if(redefinedComponentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                            fComplexTypeTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        } else if(redefinedComponentType.equals(SchemaSymbols.ELT_GROUP)) {
                            fGroupTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        } else if (redefinedComponentType.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                            fSimpleTypeTraverser.traverseGlobal(redefinedComp, currSchemaDoc, currSG);
                        } else if (redefinedComponentType.equals(SchemaSymbols.ELT_ANNOTATION)) {
                            // REVISIT:  according to 3.13.2 the PSVI needs the parent's attributes;
                            // thus this should be done in buildGlobalNameRegistries not here...
                            fElementTraverser.traverseAnnotationDecl(globalComp, null, true, currSchemaDoc);
                        } else {
                            // We'll have reported an error here already...
                        }
                    } // end march through <redefine> children
                } else if(componentType.equals(SchemaSymbols.ELT_ATTRIBUTE)) {
                    fAttributeTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                } else if(componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
                    fAttributeGroupTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                } else if(componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
                    fComplexTypeTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                } else if(componentType.equals(SchemaSymbols.ELT_ELEMENT)) {
                    fElementTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                } else if(componentType.equals(SchemaSymbols.ELT_GROUP)) {
                    fGroupTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                } else if(componentType.equals(SchemaSymbols.ELT_NOTATION)) {
                    fNotationTraverser.traverse(globalComp, currSchemaDoc, currSG);
                } else if(componentType.equals(SchemaSymbols.ELT_SIMPLETYPE)) {
                    fSimpleTypeTraverser.traverseGlobal(globalComp, currSchemaDoc, currSG);
                } else if(componentType.equals(SchemaSymbols.ELT_ANNOTATION)) {
                    // REVISIT:  according to 3.13.2 the PSVI needs the parent's attributes;
                    // thus this should be done in buildGlobalNameRegistries not here...
                    fElementTraverser.traverseAnnotationDecl(globalComp, null, true, currSchemaDoc);
                } else {
                    // we'll have already reported an error above if we get here.
                }
            } // end for

            // now we're done with this one!
            DOMUtil.setHidden(currDoc);
            // now add the schemas this guy depends on
            Vector currSchemaDepends = (Vector)fDependencyMap.get(currSchemaDoc);
            for(int i = 0; i < currSchemaDepends.size(); i++) {
                schemasToProcess.push(currSchemaDepends.elementAt(i));
            }
        } // while
    } // end traverseSchemas

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
    // this will be an index into an array of Objects of some kind
    // that lives in the Grammar.
    protected Object getGlobalDecl(XSDocumentInfo currSchema,
                                   int declType,
                                   QName declToTraverse) {
        XSDocumentInfo schemaWithDecl = null;
        SchemaGrammar sGrammar = null;
        Element decl = null;

        if (declToTraverse.uri != null &&
            declToTraverse.uri.equals(SchemaSymbols.URI_SCHEMAFORSCHEMA)) {
            sGrammar = SchemaGrammar.SG_SchemaNS;
        } else {
            String declKey = null;
            if (declToTraverse.uri != null) {
                declKey = declToTraverse.uri+","+declToTraverse.localpart;
            } else {
                declKey = ","+declToTraverse.localpart;
            }
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
                // REVISIT: report internal error...
            }
            if (decl != null)
                schemaWithDecl = findXSDocumentForDecl(currSchema, decl);

            if (schemaWithDecl == null) {
                // cannot get to this schema from the one containing the requesting decl
                // REVISIT: report component not found error
                return null;
            }
            sGrammar = fGrammarResolver.getGrammar(schemaWithDecl.fTargetNamespace);
        }

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

        if (retObj != null)
            return retObj;

        if (decl != null) {
            if (DOMUtil.isHidden(decl)) {
                //REVISIT: report an error: circular reference
                fElementTraverser.reportGenericSchemaError("Circular reference detected in schema component named " + declToTraverse.prefix+":"+declToTraverse.localpart);
                return null;
            }

            DOMUtil.setHidden(decl);

            // back up the current SchemaNamespaceSupport, because we need to provide
            // a fresh one to the traverGlobal methods.
            schemaWithDecl.backupNSSupport();

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
                retObj = null;
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
        }

        return retObj;
    } // getGlobalDecl(XSDocumentInfo, int, QName):  Object

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
    } // end resolveKeyRefs

    private Document getSchema(String schemaNamespace,
                               String schemaHint) {
        // contents of this method will depend on the system we adopt for entity resolution--i.e., XMLEntityHandler, EntityHandler, etc.
        XMLInputSource schemaSource=null;
        try {
            schemaSource = fEntityResolver.resolveEntity(schemaNamespace, schemaHint, null);
            if (schemaSource != null) {
                fSchemaParser.reset();
                fSchemaParser.parse(schemaSource);
                return fSchemaParser.getDocument();
            }

        }
        catch (IOException ex) {
            // REVISIT: report an error!
            ex.printStackTrace();
        }

        return null;
    } // getSchema(String, String):  Document

    // initialize all the traversers.
    // this should only need to be called once during the construction
    // of this object; it creates the traversers that will be used to

    // construct schemaGrammars.
    private void createTraversers() {
        fAttributeChecker = new XSAttributeChecker(this);
        fSubGroupHandler = new SubstitutionGroupHandler(fGrammarResolver);
        fAttributeGroupTraverser = new XSDAttributeGroupTraverser(this, fAttributeChecker);
        fAttributeTraverser = new XSDAttributeTraverser(this, fAttributeChecker);
        fComplexTypeTraverser = new XSDComplexTypeTraverser(this, fAttributeChecker);
        fElementTraverser = new XSDElementTraverser(this, fAttributeChecker, fSubGroupHandler);
        fGroupTraverser = new XSDGroupTraverser(this, fAttributeChecker);
        fKeyrefTraverser = new XSDKeyrefTraverser(this, fAttributeChecker);
        fNotationTraverser = new XSDNotationTraverser(this, fAttributeChecker);
        fSimpleTypeTraverser = new XSDSimpleTypeTraverser(this, fAttributeChecker);
        fUniqueOrKeyTraverser = new XSDUniqueOrKeyTraverser(this, fAttributeChecker);
        fWildCardTraverser = new XSDWildcardTraverser(this, fAttributeChecker);
    } // createTraversers()

    // this method clears all the global structs of this object
    // (except those passed in via the constructor).
    protected void reset(XMLErrorReporter errorReporter,
                         XMLEntityResolver entityResolver,
                         SymbolTable symbolTable) {
        fEntityResolver = entityResolver;
        fErrorReporter = errorReporter;
        fSymbolTable = symbolTable;

        EMPTY_STRING = symbolTable.addSymbol("");

        try {
            fSchemaParser.setProperty(SchemaValidator.ERROR_REPORTER, errorReporter);
        } catch (Exception e) {}

        fUnparsedAttributeRegistry.clear();
        fUnparsedAttributeGroupRegistry.clear();
        fUnparsedElementRegistry.clear();
        fUnparsedGroupRegistry.clear();
        fUnparsedIdentityConstraintRegistry.clear();
        fUnparsedNotationRegistry.clear();
        fUnparsedTypeRegistry.clear();

        fXSDocumentInfoRegistry.clear();
        fDependencyMap.clear();
        fTraversed.removeAllElements();
        fDoc2XSDocumentMap.clear();
        fRedefine2XSDMap.clear();
        fRoot = null;

        fLocalElemStackPos = 0;
        fParticle = new XSParticleDecl[INIT_STACK_SIZE];
        fLocalElementDecl = new Element[INIT_STACK_SIZE];
        fAllContext = new int[INIT_STACK_SIZE];
        // err on the small side for num. of local namespaces declared...
        fLocalElemNamespaceContext = new String [INIT_STACK_SIZE][1];

        // reset traversers
        fAttributeChecker.reset(errorReporter, symbolTable);
        fAttributeGroupTraverser.reset(errorReporter, symbolTable);
        fAttributeTraverser.reset(errorReporter, symbolTable);
        fComplexTypeTraverser.reset(errorReporter, symbolTable);
        fElementTraverser.reset(errorReporter, symbolTable);
        fGroupTraverser.reset(errorReporter, symbolTable);
        fKeyrefTraverser.reset(errorReporter, symbolTable);
        fNotationTraverser.reset(errorReporter, symbolTable);
        fSimpleTypeTraverser.reset(errorReporter, symbolTable);
        fUniqueOrKeyTraverser.reset(errorReporter, symbolTable);
        fWildCardTraverser.reset(errorReporter, symbolTable);

    } // reset

    /**
     * Traverse all the deferred local elements. This method should be called
     * by traverseSchemas after we've done with all the global declarations.
     */
    void traverseLocalElements() {
        fElementTraverser.fDeferTraversingLocalElements = false;
        for (int i = 0; i < fLocalElemStackPos; i++) {
            Element currElem = fLocalElementDecl[i];
            XSDocumentInfo currSchema = (XSDocumentInfo)fDoc2XSDocumentMap.get(DOMUtil.getDocument(currElem));
            SchemaGrammar currGrammar = fGrammarResolver.getGrammar(currSchema.fTargetNamespace);
            fElementTraverser.traverseLocal (currElem, currSchema, currGrammar, fAllContext[i]);
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
            String [][] newStackN = new String [fLocalElemStackPos+INC_STACK_SIZE][];
            System.arraycopy(fLocalElemNamespaceContext, 0, newStackN, 0, fLocalElemStackPos);
            fLocalElemNamespaceContext = newStackN;
        }

        fParticle[fLocalElemStackPos] = particle;
        fLocalElementDecl[fLocalElemStackPos] = elmDecl;
        fAllContext[fLocalElemStackPos] = allContextFlags;
        fLocalElemNamespaceContext[fLocalElemStackPos] = schemaDoc.fNamespaceSupport.getEffectiveLocalContext();
    } // end fillInLocalElemInfo(...)

    /** This method makes sure that
     * if this component is being redefined that it lives in the
     * right schema.  It then renames the component correctly.  If it
     * detects a collision--a duplicate definition--then it complains.
     */
    private void checkForDuplicateNames(String qName,
            Hashtable registry, Element currComp,
            XSDocumentInfo currSchema) {
        Object objElem = null;
        if((objElem = registry.get(qName)) == null) {
            // just add it in!
            registry.put(qName, currComp);
        } else {
            Element collidingElem = (Element)objElem;
            XSDocumentInfo redefinedSchema = (XSDocumentInfo)(fRedefine2XSDMap.get(DOMUtil.getParent(collidingElem)));
            if(redefinedSchema == currSchema) { // object comp. okay here
                // now have to do some renaming...
                String newName = qName.substring(qName.lastIndexOf(','));
                currComp.setAttribute(SchemaSymbols.ATT_NAME, newName);
                // and take care of nested redefines by calling recursively:
                checkForDuplicateNames(currSchema.fTargetNamespace+","+newName, registry, currComp, currSchema);
            } else if (redefinedSchema != null) { // we're apparently redefining the wrong schema
                // REVISIT:  error that redefined element in wrong schema
            } else { // we've just got a flat-out collision
                // REVISIT:  report error for duplicate declarations
            }
        }
    } // checkForDuplicateNames(String, Hashtable, Element, XSDocumentInfo):void


    //
    //!!!!!!!!!!!!!!!! IMPLEMENT the following functions !!!!!!!!!!
    //
    //REVISIT: implement namescope support!!!
    protected String resolvePrefixToURI (String prefix) {
        //String uriStr = fStringPool.toString(fNamespacesScope.getNamespaceForPrefix(fStringPool.addSymbol(prefix)));
        //if (uriStr.length() == 0 && prefix.length() > 0) {
            // REVISIT: Localize
            //// REVISIT:  reportGenericSchemaError("prefix : [" + prefix +"] cannot be resolved to a URI");
            //return "";
        //}

        return null;
    }

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
            String processedTypeName = currSchema.fTargetNamespace+","+oldName;
            Element grandKid = DOMUtil.getFirstChildElement(child);
            if (grandKid == null) {
                // fRedefineSucceeded = false;
                // REVISIT: Localize
                // REVISIT:  reportGenericSchemaError("a simpleType child of a <redefine> must have a restriction element as a child");
            } else {
                String grandKidName = grandKid.getLocalName();
                if(grandKidName.equals(SchemaSymbols.ELT_ANNOTATION)) {
                    grandKid = DOMUtil.getNextSiblingElement(grandKid);
                    grandKidName = grandKid.getLocalName();
                }
                if (grandKid == null) {
                    // fRedefineSucceeded = false;
                    // REVISIT: Localize
                    // REVISIT:  reportGenericSchemaError("a simpleType child of a <redefine> must have a restriction element as a child");
                } else if(!grandKidName.equals(SchemaSymbols.ELT_RESTRICTION)) {
                    // fRedefineSucceeded = false;
                    // REVISIT: Localize
                    // REVISIT:  reportGenericSchemaError("a simpleType child of a <redefine> must have a restriction element as a child");
                } else {
                    String derivedBase = grandKid.getAttribute( SchemaSymbols.ATT_BASE );
                    String processedDerivedBase = findQName(derivedBase, currNSMap);
                    if(!processedTypeName.equals(processedDerivedBase)) {
                        // fRedefineSucceeded = false;
                        // REVISIT: Localize
                        // REVISIT:  reportGenericSchemaError("the base attribute of the restriction child of a simpleType child of a redefine must have the same value as the simpleType's type attribute");
                    } else {
                        // now we have to do the renaming...
                        int colonptr = derivedBase.indexOf(":");
                        if ( colonptr > 0)
                            grandKid.setAttribute( SchemaSymbols.ATT_BASE,
                                derivedBase.substring(0,colonptr) + ":" + newName );
                        else
                            grandKid.setAttribute( SchemaSymbols.ATT_BASE, newName );
//                        return true;
                    }
                }
            }
        } else if (componentType.equals(SchemaSymbols.ELT_COMPLEXTYPE)) {
            String processedTypeName = currSchema.fTargetNamespace+","+oldName;
            Element grandKid = DOMUtil.getFirstChildElement(child);
            if (grandKid == null) {
                // fRedefineSucceeded = false;
                // REVISIT: Localize
                // REVISIT:  reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
            } else {
                if(grandKid.getLocalName().equals(SchemaSymbols.ELT_ANNOTATION)) {
                    grandKid = DOMUtil.getNextSiblingElement(grandKid);
                }
                if (grandKid == null) {
                    // fRedefineSucceeded = false;
                    // REVISIT: Localize
                    // REVISIT:  reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
                } else {
                    // have to go one more level down; let another pass worry whether complexType is valid.
                    Element greatGrandKid = DOMUtil.getFirstChildElement(grandKid);
                    if (greatGrandKid == null) {
                        // fRedefineSucceeded = false;
                        // REVISIT: Localize
                        // REVISIT:  reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
                    } else {
                        String greatGrandKidName = greatGrandKid.getLocalName();
                        if(greatGrandKidName.equals(SchemaSymbols.ELT_ANNOTATION)) {
                            greatGrandKid = DOMUtil.getNextSiblingElement(greatGrandKid);
                            greatGrandKidName = greatGrandKid.getLocalName();
                        }
                        if (greatGrandKid == null) {
                            // fRedefineSucceeded = false;
                            // REVISIT: Localize
                            // REVISIT:  reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
                        } else if(!greatGrandKidName.equals(SchemaSymbols.ELT_RESTRICTION) &&
                                !greatGrandKidName.equals(SchemaSymbols.ELT_EXTENSION)) {
                            // fRedefineSucceeded = false;
                            // REVISIT: Localize
                            // REVISIT:  reportGenericSchemaError("a complexType child of a <redefine> must have a restriction or extension element as a grandchild");
                        } else {
                            String derivedBase = greatGrandKid.getAttribute( SchemaSymbols.ATT_BASE );
                            String processedDerivedBase = findQName(derivedBase, currSchema.fNamespaceSupport);
                            if(!processedTypeName.equals(processedDerivedBase)) {
                                // fRedefineSucceeded = false;
                                // REVISIT: Localize
                                // REVISIT:  reportGenericSchemaError("the base attribute of the restriction or extension grandchild of a complexType child of a redefine must have the same value as the complexType's type attribute");
                            } else {
                                // now we have to do the renaming...
                                int colonptr = derivedBase.indexOf(":");
                                if ( colonptr > 0)
                                    greatGrandKid.setAttribute( SchemaSymbols.ATT_BASE,
                                        derivedBase.substring(0,colonptr) + ":" + newName );
                                else
                                    greatGrandKid.setAttribute( SchemaSymbols.ATT_BASE,
                                        newName );
//                                return true;
                            }
                        }
                    }
                }
            }
        } else if (componentType.equals(SchemaSymbols.ELT_ATTRIBUTEGROUP)) {
            String processedBaseName = currSchema.fTargetNamespace+","+oldName;
            int attGroupRefsCount = changeRedefineGroup(processedBaseName, componentType, newName, child, currSchema.fNamespaceSupport);
            if(attGroupRefsCount > 1) {
                // fRedefineSucceeded = false;
                // REVISIT:  localize
                // REVISIT:  reportGenericSchemaError("if an attributeGroup child of a <redefine> element contains an attributeGroup ref'ing itself, it must have exactly 1; this one has " + attGroupRefsCount);
            } else if (attGroupRefsCount == 1) {
//                return true;
            }  else
                fRedefinedRestrictedAttributeGroupRegistry.put(processedBaseName, currSchema.fTargetNamespace+","+newName);
        } else if (componentType.equals(SchemaSymbols.ELT_GROUP)) {
            String processedBaseName = currSchema.fTargetNamespace+","+oldName;
            int groupRefsCount = changeRedefineGroup(processedBaseName, componentType, newName, child, currSchema.fNamespaceSupport);
            if(groupRefsCount > 1) {
                // fRedefineSucceeded = false;
                // REVISIT:  localize
                // REVISIT:  reportGenericSchemaError("if a group child of a <redefine> element contains a group ref'ing itself, it must have exactly 1; this one has " + groupRefsCount);
            } else if (groupRefsCount == 1) {
//                return true;
            }  else {
                fRedefinedRestrictedGroupRegistry.put(processedBaseName, currSchema.fTargetNamespace+","+newName);
            }
        } else {
            // fRedefineSucceeded = false;
            // REVISIT: Localize
            // REVISIT:  reportGenericSchemaError("internal Xerces error; please submit a bug with schema as testcase");
        }
        // if we get here then we must have reported an error and failed somewhere...
//        return false;
    } // renameRedefiningComponents(XSDocumentInfo, Element, String, String, String):void

    // this method takes a name of the form a:b, determines the URI mapped
    // to by a in the current SchemaNamespaceSupport object, and returns this
    // information in the form (nsURI,b) suitable for lookups in the global
    // decl Hashtables.
    private String findQName(String name, SchemaNamespaceSupport currNSMap) {
        int colonPtr = name.indexOf(':');
        String prefix = "";
        if (colonPtr > 0)
            prefix = name.substring(0, colonPtr);
        String uri = currNSMap.getURI(prefix);
        String localpart = (colonPtr == 0)?name:name.substring(colonPtr);
        return uri+","+localpart;
    } // findQName(String, SchemaNamespaceSupport):  String

    // This function looks among the children of curr for an element of type elementSought.
    // If it finds one, it evaluates whether its ref attribute contains a reference
    // to originalQName.  If it does, it returns 1 + the value returned by
    // calls to itself on all other children.  In all other cases it returns 0 plus
    // the sum of the values returned by calls to itself on curr's children.
    // It also resets the value of ref so that it will refer to the renamed type from the schema
    // being redefined.
    private int changeRedefineGroup(String originalQName, String elementSought,
            String newName, Element curr, SchemaNamespaceSupport currNSMap) {
        int result = 0;
        for (Element child = DOMUtil.getFirstChildElement(curr);
                child != null; child = DOMUtil.getNextSiblingElement(child)) {
            String name = child.getLocalName();
            if (!name.equals(elementSought))
                result += changeRedefineGroup(originalQName, elementSought, newName, child, currNSMap);
            else {
                String ref = child.getAttribute( SchemaSymbols.ATT_REF );
                if (ref.length() != 0) {
                    String processedRef = findQName(ref, currNSMap);
                    if(originalQName.equals(processedRef)) {
                        String prefix = "";
                        String localpart = ref;
                        int colonptr = ref.indexOf(":");
                        if ( colonptr > 0) {
                            prefix = ref.substring(0,colonptr);
                            child.setAttribute(SchemaSymbols.ATT_REF, prefix + ":" + newName);
                        } else
                            child.setAttribute(SchemaSymbols.ATT_REF, newName);
                        result++;
                        if(elementSought.equals(SchemaSymbols.ELT_GROUP)) {
                            String minOccurs = child.getAttribute( SchemaSymbols.ATT_MINOCCURS );
                            String maxOccurs = child.getAttribute( SchemaSymbols.ATT_MAXOCCURS );
                            if(!((maxOccurs.length() == 0 || maxOccurs.equals("1"))
                                    && (minOccurs.length() == 0 || minOccurs.equals("1")))) {
                                //REVISIT:  localize
                                // REVISIT:  reportGenericSchemaError("src-redefine.6.1.2:  the group " + ref + " which contains a reference to a group being redefined must have minOccurs = maxOccurs = 1");
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
        Document declDoc = DOMUtil.getDocument(decl);
        Object temp = fDoc2XSDocumentMap.get(declDoc);
        if(temp == null) {
            // something went badly wrong; we don't know this doc?
            return null;
        }
        XSDocumentInfo declDocInfo = (XSDocumentInfo)temp;
        // now look in fDependencyMap to see if this is reachable
        if(((Vector)fDependencyMap.get(currSchema)).contains(declDocInfo)) {
            return declDocInfo;
        }
        // obviously the requesting doc didn't include, redefine or
        // import the one containing decl...
        return null;
    } // findXSDocumentForDecl(XSDocumentInfo, Element):  XSDocumentInfo

    private void setSchemasVisible(XSDocumentInfo startSchema) {
        if(DOMUtil.isHidden(startSchema.fSchemaDoc)) {
            // make it visible
            DOMUtil.setVisible(startSchema.fSchemaDoc);
            Vector dependingSchemas = (Vector)fDependencyMap.get(startSchema);
            for(int i = 0; i < dependingSchemas.size(); i++) {
                setSchemasVisible((XSDocumentInfo)dependingSchemas.elementAt(i));
            }
        }
        // if it's visible already than so must be its children
    } // setSchemasVisible(XSDocumentInfo): void

    /******* only for testing!  ******/
    public static void main (String args[]) throws Exception {
        DefaultHandler handler = new DefaultHandler();
        XSDHandler me = new XSDHandler(new XSGrammarResolver());
        me.reset(new XMLErrorReporter(), new EntityResolverWrapper(new org.apache.xerces.impl.v2.XSDHandler.DummyResolver()), new SymbolTable());
        me.parseSchema(args[0], args[1]);
        Enumeration types = me.fUnparsedTypeRegistry.keys();
        String name = null;
        while(types.hasMoreElements()) {
            name = (String)types.nextElement();
        }
    } // main

    public static class DummyResolver implements EntityResolver {
        public InputSource resolveEntity(String pubId, String sysId) throws SAXException, IOException {
            InputSource toReturn = new InputSource(sysId);
            toReturn.setPublicId(pubId);
            toReturn.setCharacterStream(new FileReader(sysId));
            return toReturn;
        }
    } // dummyResolver*/
} // XSDHandler