int value = fStringPool.addString(child.getFirstChild().getFirstChild().getNodeValue());

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

package org.apache.xerces.validators.schema;

import org.apache.xerces.framework.XMLAttrList;
import org.apache.xerces.framework.XMLContentSpecNode;
import org.apache.xerces.framework.XMLErrorReporter;
import org.apache.xerces.framework.XMLValidator;
import org.apache.xerces.readers.XMLEntityHandler;
import org.apache.xerces.utils.ChunkyCharArray;
import org.apache.xerces.utils.NamespacesScope;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.utils.XMLCharacterProperties;
import org.apache.xerces.utils.XMLMessages;
import org.apache.xerces.utils.ImplementationMessages;

import org.xml.sax.Locator;
import org.xml.sax.InputSource;
import org.xml.sax.SAXParseException;

import java.util.StringTokenizer;
import java.util.Stack;

// for schema
import org.apache.xerces.validators.dtd.XMLContentModel;
import org.apache.xerces.validators.dtd.SimpleContentModel;
import org.apache.xerces.validators.dtd.MixedContentModel;
import org.apache.xerces.validators.dtd.DFAContentModel;
import org.apache.xerces.validators.dtd.CMException;
import org.apache.xerces.validators.dtd.CMNode;
import org.apache.xerces.validators.dtd.CMLeaf;
import org.apache.xerces.validators.dtd.CMUniOp;
import org.apache.xerces.validators.dtd.CMBinOp;
import org.apache.xerces.validators.dtd.InsertableElementsInfo;
import org.apache.xerces.validators.dtd.EntityPool;
import org.apache.xerces.validators.dtd.ElementDeclPool;
import org.apache.xerces.dom.DocumentImpl;
import org.apache.xerces.dom.DocumentTypeImpl;
import org.apache.xerces.parsers.DOMParser;
import org.w3c.dom.Document;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.EntityResolver;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import java.io.IOException;
import java.util.Hashtable;
import java.util.Vector; // REVISIT remove
import org.apache.xerces.validators.datatype.DatatypeValidator;
import org.apache.xerces.validators.datatype.InvalidDatatypeValueException;
import org.apache.xerces.validators.datatype.IllegalFacetException;
import org.apache.xerces.validators.datatype.IllegalFacetValueException;
import org.apache.xerces.validators.datatype.UnknownFacetException;
import org.apache.xerces.validators.datatype.BooleanValidator;
import org.apache.xerces.validators.datatype.IntegerValidator;
import org.apache.xerces.validators.datatype.StringValidator;
import org.apache.xerces.validators.datatype.FloatValidator;
import org.apache.xerces.validators.datatype.DoubleValidator;
import org.apache.xerces.validators.datatype.DecimalValidator;
import org.apache.xerces.msg.SchemaMessages;

/**
 * XSchemaValidator is an <font color="red"><b>experimental</b></font> implementation
 * of a validator for the W3C Schema Language.  All of its implementation is subject
 * to change.
 */
public class XSchemaValidator implements XMLValidator {
    //
    // Debugging options
    //
    private static final boolean PRINT_EXCEPTION_STACK_TRACE = false;
    private static final boolean DEBUG_PRINT_ATTRIBUTES = false;
    private static final boolean DEBUG_PRINT_CONTENT = false;
    private static final boolean DEBUG_PAREN_DEPTH = false;
    private static final boolean DEBUG_MARKUP_DEPTH = false;
    //
    //
    //
    private boolean fValidationEnabled = false;
    private boolean fDynamicValidation = false;
    private boolean fValidationEnabledByDynamic = false;
    private boolean fDynamicDisabledByValidation = false;
    private boolean fValidating = false;
    private boolean fWarningOnDuplicateAttDef = false;
    private boolean fWarningOnUndeclaredElements = false;
    private EntityPool fEntityPool = null;
    private ElementDeclPool fElementDeclPool = null;
    private int fStandaloneReader = -1;
    private int[] fElementTypeStack = new int[8];
    private int[] fContentSpecTypeStack = new int[8];
    private int[] fElementChildCount = new int[8];
    private int[][] fElementChildren = new int[8][];
    private int fElementDepth = -1;
    private NamespacesScope fNamespacesScope = null;
    private boolean fNamespacesEnabled = false;
    private int fRootElementType = -1;
    private int fAttrIndex = -1;
    //
    private XMLErrorReporter fErrorReporter = null;
    private XMLEntityHandler fEntityHandler = null;
    private StringPool fStringPool = null;
    private boolean fBufferDatatype = false;
    private StringBuffer fDatatypeBuffer = new StringBuffer();
    private DatatypeValidatorRegistry fDatatypeRegistry = new DatatypeValidatorRegistry();
    private int fTypeCount = 0;
    private int fGroupCount = 0;
    private int fModelGroupCount = 0;
    private int fAttributeGroupCount = 0;
    private Hashtable fForwardRefs = new Hashtable(); // REVISIT w/ more efficient structure later
    private Hashtable fAttrGroupUses = new Hashtable();

    // constants

    private static final String ELT_COMMENT = "comment";
    private static final String ELT_DATATYPEDECL = "datatype";
    private static final String ELT_ARCHETYPEDECL = "archetype";
    private static final String ELT_ELEMENTDECL = "element";
    private static final String ELT_GROUP = "group";
    private static final String ELT_ATTRGROUPDECL = "attrGroup";
    private static final String ELT_ATTRGROUPREF = "attrGroupRef";
    private static final String ELT_MODELGROUPDECL = "modelGroup";
    private static final String ELT_MODELGROUPREF = "modelGroupRef";
    private static final String ELT_TEXTENTITYDECL = "textEntity";
    private static final String ELT_EXTERNALENTITYDECL = "externalEntity";
    private static final String ELT_UNPARSEDENTITYDECL = "unparsedEntity";
    private static final String ELT_NOTATIONDECL = "notation";
    private static final String ELT_REFINES = "refines";
    private static final String ELT_ATTRIBUTEDECL = "attribute";
    private static final String ATT_NAME = "name";
    private static final String ATT_CONTENT = "content";
    private static final String ATT_MODEL = "model";
    private static final String ATT_ORDER = "order";
    private static final String ATT_TYPE = "type";
    private static final String ATT_DEFAULT = "default";
    private static final String ATT_FIXED = "fixed";
    private static final String ATT_COLLECTION = "collection";
    private static final String ATT_REF = "ref";
    private static final String ATT_ARCHREF = "archRef";
    private static final String ATT_SCHEMAABBREV = "schemaAbbrev";
    private static final String ATT_SCHEMANAME = "schemaName";
    private static final String ATT_MINOCCURS = "minOccurs";
    private static final String ATT_MAXOCCURS = "maxOccurs";
    private static final String ATT_EXPORT = "export";
    private static final String ATTVAL_ANY = "any";
    private static final String ATTVAL_MIXED = "mixed";
    private static final String ATTVAL_EMPTY = "empty";
    private static final String ATTVAL_CHOICE = "choice";
    private static final String ATTVAL_SEQ = "seq";
    private static final String ATTVAL_ALL = "all";
    private static final String ATTVAL_ELEMONLY = "elemOnly";
    private static final String ATTVAL_TEXTONLY = "textOnly";

    private Document fSchemaDocument;

    //
    //
    //
    public XSchemaValidator(StringPool stringPool, XMLErrorReporter errorReporter, XMLEntityHandler entityHandler) {
        fEntityPool = new EntityPool(stringPool, errorReporter, true);
        fElementDeclPool = new ElementDeclPool(stringPool, errorReporter);
        fErrorReporter = errorReporter;
        fEntityHandler = entityHandler;
        fStringPool = stringPool;
        fDatatypeRegistry.initializeRegistry();
    }
    //
    //
    //
    public void reset(StringPool stringPool, XMLErrorReporter errorReporter, XMLEntityHandler entityHandler) throws Exception {
        fEntityPool.reset(stringPool);
        fValidating = fValidationEnabled;
        fElementDeclPool.reset(stringPool);
        fRootElementType = -1;
        fAttrIndex = -1;
        fStandaloneReader = -1;
        fElementDepth = -1;
        fErrorReporter = errorReporter;
        fEntityHandler = entityHandler;
        fStringPool = stringPool;

        fSchemaDocument = null;
    }

    /** @deprecated */
    public Document getSchemaDocument() {
        return fSchemaDocument;
    }

    //
    // Turning on validation/dynamic turns on validation if it is off, and this
    // is remembered.  Turning off validation DISABLES validation/dynamic if it
    // is on.  Turning off validation/dynamic DOES NOT turn off validation if it
    // was explicitly turned on, only if it was turned on BECAUSE OF the call to
    // turn validation/dynamic on.  Turning on validation will REENABLE and turn
    // validation/dynamic back on if it was disabled by a call that turned off
    // validation while validation/dynamic was enabled.
    //
    public void setValidationEnabled(boolean flag) {
        fValidationEnabled = flag;
        fValidationEnabledByDynamic = false;
        if (fValidationEnabled) {
            if (fDynamicDisabledByValidation) {
                fDynamicValidation = true;
                fDynamicDisabledByValidation = false;
            }
        } else if (fDynamicValidation) {
            fDynamicValidation = false;
            fDynamicDisabledByValidation = true;
        }
        fValidating = fValidationEnabled;
    }
    public boolean getValidationEnabled() {
        return fValidationEnabled;
    }
    public void setDynamicValidationEnabled(boolean flag) {
        fDynamicValidation = flag;
        fDynamicDisabledByValidation = false;
        if (fDynamicValidation) {
            if (!fValidationEnabled) {
                fValidationEnabledByDynamic = true;
                fValidationEnabled = true;
            }
        } else if (fValidationEnabledByDynamic) {
            fValidationEnabled = false;
            fValidationEnabledByDynamic = false;
        }
    }
    public boolean getDynamicValidationEnabled() {
        return fDynamicValidation;
    }
    public void setNamespacesEnabled(boolean flag) {
        fNamespacesEnabled = flag;
    }
    public boolean getNamespacesEnabled() {
        return fNamespacesEnabled;
    }
    public void setWarningOnDuplicateAttDef(boolean flag) {
        fWarningOnDuplicateAttDef = flag;
    }
    public boolean getWarningOnDuplicateAttDef() {
        return fWarningOnDuplicateAttDef;
    }
    public void setWarningOnUndeclaredElements(boolean flag) {
        fWarningOnUndeclaredElements = flag;
    }
    public boolean getWarningOnUndeclaredElements() {
        return fWarningOnUndeclaredElements;
    }
    private boolean usingStandaloneReader() {
        return fStandaloneReader == -1 || fEntityHandler.getReaderId() == fStandaloneReader;
    }
    private boolean invalidStandaloneAttDef(int elementTypeIndex, int attrNameIndex) {
        if (fStandaloneReader == -1)
            return false;
        if (elementTypeIndex == -1) // we are normalizing a default att value...  this ok?
            return false;
        int attDefIndex = fElementDeclPool.getAttDef(elementTypeIndex, attrNameIndex);
        return fElementDeclPool.getAttDefIsExternal(attDefIndex);
    }
    //
    // Validator interface
    //
    public boolean notationDeclared(int notationNameIndex) {
        return fEntityPool.lookupNotation(notationNameIndex) != -1;
    }
    protected void addRequiredNotation(int notationName, Locator locator, int majorCode, int minorCode, Object[] args) throws Exception {
        fEntityPool.addRequiredNotation(notationName, locator, majorCode, minorCode, args);
    }
    public void characters(char[] chars, int offset, int length) throws Exception {
        if (fValidating) {
            charDataInContent();
            if (fBufferDatatype)
                fDatatypeBuffer.append(chars, offset, length);
        }
    }
    public void characters(int stringIndex) throws Exception {
        if (fValidating) {
            charDataInContent();
            if (fBufferDatatype)
                fDatatypeBuffer.append(fStringPool.toString(stringIndex));
        }
    }
    public void ignorableWhitespace(char[] chars, int offset, int length) throws Exception {
        if (fStandaloneReader != -1 && fValidating) {
            int elementIndex = getElement(peekElementType());
            if (fElementDeclPool.getElementDeclIsExternal(elementIndex)) {
                reportRecoverableXMLError(XMLMessages.MSG_WHITE_SPACE_IN_ELEMENT_CONTENT_WHEN_STANDALONE,
                                            XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION);
            }
        }
    }
    public void ignorableWhitespace(int stringIndex) throws Exception {
        if (fStandaloneReader != -1 && fValidating) {
            int elementIndex = getElement(peekElementType());
            if (fElementDeclPool.getElementDeclIsExternal(elementIndex)) {
                reportRecoverableXMLError(XMLMessages.MSG_WHITE_SPACE_IN_ELEMENT_CONTENT_WHEN_STANDALONE,
                                            XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION);
            }
        }
    }
    public int getElement(int elementTypeIndex) {
        int elementIndex = fElementDeclPool.getElement(elementTypeIndex);
        return elementIndex;
    }
    public int getElementType(int elementIndex) throws Exception {
        int name = fElementDeclPool.getElementType(elementIndex);
        return name;
    }
    public int getContentSpecType(int elementIndex) {
        int contentspecType = fElementDeclPool.getContentSpecType(elementIndex);
        return contentspecType;
    }
    public int getContentSpec(int elementIndex) {
        int contentspec = fElementDeclPool.getContentSpec(elementIndex);
        return contentspec;
    }
    public String getContentSpecAsString(int elementIndex) {
        String contentspec = fElementDeclPool.getContentSpecAsString(elementIndex);
        return contentspec;
    }
    public void getContentSpecNode(int contentSpecIndex, XMLContentSpecNode csn) {
        fElementDeclPool.getContentSpecNode(contentSpecIndex, csn);
    }
    public int getAttName(int attDefIndex) {
        int attName = fElementDeclPool.getAttName(attDefIndex);
        return attName;
    }
    public int getAttValue(int attDefIndex) {
        int attValue = fElementDeclPool.getAttValue(attDefIndex);
        return attValue;
    }
    public int lookupEntity(int entityNameIndex) {
        int entityIndex = fEntityPool.lookupEntity(entityNameIndex);
        return entityIndex;
    }
    public boolean externalReferenceInContent(int entityIndex) throws Exception {
        boolean external = fEntityPool.isExternalEntity(entityIndex);
        if (fStandaloneReader != -1 && fValidating) {
            if (external) {
                reportRecoverableXMLError(XMLMessages.MSG_EXTERNAL_ENTITY_NOT_PERMITTED,
                                          XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                          fEntityPool.getEntityName(entityIndex));
            } else if (fEntityPool.getEntityDeclIsExternal(entityIndex)) {
                reportRecoverableXMLError(XMLMessages.MSG_REFERENCE_TO_EXTERNALLY_DECLARED_ENTITY_WHEN_STANDALONE,
                                          XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                          fEntityPool.getEntityName(entityIndex));
            }
        }
        return external;
    }
    public int valueOfReferenceInAttValue(int entityIndex) throws Exception {
        if (fStandaloneReader != -1 && fValidating && fEntityPool.getEntityDeclIsExternal(entityIndex)) {
            reportRecoverableXMLError(XMLMessages.MSG_REFERENCE_TO_EXTERNALLY_DECLARED_ENTITY_WHEN_STANDALONE,
                                      XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                      fEntityPool.getEntityName(entityIndex));
        }
        int entityValue = fEntityPool.getEntityValue(entityIndex);
        return entityValue;
    }
    public boolean isExternalEntity(int entityIndex) {
        boolean external = fEntityPool.isExternalEntity(entityIndex);
        return external;
    }
    public boolean isUnparsedEntity(int entityIndex) {
        boolean external = fEntityPool.isUnparsedEntity(entityIndex);
        return external;
    }
    public int getEntityName(int entityIndex) {
        int name = fEntityPool.getEntityName(entityIndex);
        return name;
    }
    public int getEntityValue(int entityIndex) {
        int value = fEntityPool.getEntityValue(entityIndex);
        return value;
    }
    public String getPublicIdOfEntity(int entityIndex) {
        int publicId = fEntityPool.getPublicId(entityIndex);
        return fStringPool.toString(publicId);
    }
    public int getPublicIdIndexOfEntity(int entityIndex) {
        int publicId = fEntityPool.getPublicId(entityIndex);
        return publicId;
    }
    public String getSystemIdOfEntity(int entityIndex) {
        int systemId = fEntityPool.getSystemId(entityIndex);
        return fStringPool.toString(systemId);
    }
    public int getSystemIdIndexOfEntity(int entityIndex) {
        int systemId = fEntityPool.getSystemId(entityIndex);
        return systemId;
    }
    public int getNotationName(int entityIndex) {
        int name = fEntityPool.getNotationName(entityIndex);
        return name;
    }
    public int lookupParameterEntity(int peNameIndex) throws Exception {
        throw new RuntimeException("cannot happen 26"); // not called
    }
    public boolean isExternalParameterEntity(int peIndex) {
        throw new RuntimeException("cannot happen 27"); // not called
    }
    public int getParameterEntityValue(int peIndex) {
        throw new RuntimeException("cannot happen 28"); // not called
    }
    public String getPublicIdOfParameterEntity(int peIndex) {
        throw new RuntimeException("cannot happen 29"); // not called
    }
    public String getSystemIdOfParameterEntity(int peIndex) {
        throw new RuntimeException("cannot happen 30"); // not called
    }
    public void rootElementSpecified(int rootElementType) throws Exception {
        if (fValidating) {
            fRootElementType = rootElementType; // REVISIT - how does schema do this?
            if (fRootElementType != -1 && rootElementType != fRootElementType) {
                reportRecoverableXMLError(XMLMessages.MSG_ROOT_ELEMENT_TYPE,
                                            XMLMessages.VC_ROOT_ELEMENT_TYPE,
                                            fRootElementType, rootElementType);
            }
        }
    }
    public boolean attributeSpecified(int elementTypeIndex, XMLAttrList attrList, int attrNameIndex, Locator attrNameLocator, int attValueIndex) throws Exception {
        int attDefIndex = fElementDeclPool.getAttDef(elementTypeIndex, attrNameIndex);
        if (attDefIndex == -1) {
            if (fValidating) {
                // REVISIT - cache the elem/attr tuple so that we only give
                //  this error once for each unique occurrence
                Object[] args = { fStringPool.toString(elementTypeIndex),
                                  fStringPool.toString(attrNameIndex) };
                fErrorReporter.reportError(attrNameLocator,
                                           XMLMessages.XML_DOMAIN,
                                           XMLMessages.MSG_ATTRIBUTE_NOT_DECLARED,
                                           XMLMessages.VC_ATTRIBUTE_VALUE_TYPE,
                                           args,
                                           XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
            }
            int attType = fStringPool.addSymbol("CDATA");
            if (fAttrIndex == -1)
                fAttrIndex = attrList.startAttrList();
            return attrList.addAttr(attrNameIndex, attValueIndex, attType, true, true) != -1;
        }
        int attType = fElementDeclPool.getAttType(attDefIndex);
        if (attType != fStringPool.addSymbol("CDATA")) {
            int enumIndex = fElementDeclPool.getEnumeration(attDefIndex);
            attValueIndex = normalizeAttributeValue(elementTypeIndex, attrNameIndex, attValueIndex, attType, enumIndex);
        }
        if (fAttrIndex == -1)
            fAttrIndex = attrList.startAttrList();
        return attrList.addAttr(attrNameIndex, attValueIndex, attType, true, true) != -1;
    }
    public boolean startElement(int elementTypeIndex, XMLAttrList attrList) throws Exception {
        int attrIndex = fAttrIndex;
        fAttrIndex = -1;
        int elementIndex = fElementDeclPool.getElement(elementTypeIndex);
        int contentSpecType = (elementIndex == -1) ? -1 : fElementDeclPool.getContentSpecType(elementIndex);
        if (contentSpecType == -1 && fValidating) {
            reportRecoverableXMLError(XMLMessages.MSG_ELEMENT_NOT_DECLARED,
                                      XMLMessages.VC_ELEMENT_VALID,
                                      elementTypeIndex);
        }
        if (elementIndex != -1) {
            attrIndex = fElementDeclPool.addDefaultAttributes(elementIndex, attrList, attrIndex, fValidating, fStandaloneReader != -1);
        }
        checkAttributes(elementIndex, attrList, attrIndex);
        if (fValidating && contentSpecType == fStringPool.addSymbol("DATATYPE")) {
            fBufferDatatype = true;
            fDatatypeBuffer.setLength(0);
        }
        pushElement(elementTypeIndex, contentSpecType);
        return contentSpecType == fStringPool.addSymbol("CHILDREN");
    }
    public boolean endElement(int elementTypeIndex) throws Exception {
        if (fValidating) {
            int elementIndex = fElementDeclPool.getElement(elementTypeIndex);
            if (elementIndex != -1 && fElementDeclPool.getContentSpecType(elementIndex) != -1) {
                int childCount = peekChildCount();
                int result = checkContent(elementIndex, childCount, peekChildren());
                if (result != -1) {
                    int majorCode = result != childCount ? XMLMessages.MSG_CONTENT_INVALID : XMLMessages.MSG_CONTENT_INCOMPLETE;
                    reportRecoverableXMLError(majorCode,
                                              0,
                                              fStringPool.toString(elementTypeIndex),
                                              fElementDeclPool.getContentSpecAsString(elementIndex));
                }
            }
            fBufferDatatype = false;
        }
        popElement();
        return peekContentSpecType() == fStringPool.addSymbol("CHILDREN");
    }
    private int normalizeAttributeValue(int elementTypeIndex, int attrNameIndex, int attValueIndex, int attType, int enumIndex) throws Exception {
        //
        // Normalize attribute based upon attribute type...
        //
        String attValue = fStringPool.toString(attValueIndex);
        if (attType == fStringPool.addSymbol("ID")) {
            String newAttValue = attValue.trim();
            if (fValidating) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
                if (newAttValue != attValue && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
                if (!XMLCharacterProperties.validName(newAttValue)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ID_INVALID,
                                              XMLMessages.VC_ID,
                                              fStringPool.toString(attrNameIndex), newAttValue);
                }
                //
                // ID - check that the id value is unique within the document (V_TAG8)
                //
                if (elementTypeIndex != -1 && !fElementDeclPool.addId(attValueIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ID_NOT_UNIQUE,
                                              XMLMessages.VC_ID,
                                              fStringPool.toString(attrNameIndex), newAttValue);
                }
            } else if (newAttValue != attValue) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
            }
        } else if (attType == fStringPool.addSymbol("IDREF")) {
            String newAttValue = attValue.trim();
            if (fValidating) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
                if (newAttValue != attValue && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
                if (!XMLCharacterProperties.validName(newAttValue)) {
                    reportRecoverableXMLError(XMLMessages.MSG_IDREF_INVALID,
                                              XMLMessages.VC_IDREF,
                                              fStringPool.toString(attrNameIndex), newAttValue);
                }
                //
                // IDREF - remember the id value
                //
                if (elementTypeIndex != -1)
                    fElementDeclPool.addIdRef(attValueIndex);
            } else if (newAttValue != attValue) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
            }
        } else if (attType == fStringPool.addSymbol("IDREFS")) {
            StringTokenizer tokenizer = new StringTokenizer(attValue);
            StringBuffer sb = new StringBuffer(attValue.length());
            boolean ok = true;
            if (tokenizer.hasMoreTokens()) {
                while (true) {
                    String idName = tokenizer.nextToken();
                    if (fValidating) {
                        if (!XMLCharacterProperties.validName(idName)) {
                            ok = false;
                        }
                        //
                        // IDREFS - remember the id values
                        //
                        if (elementTypeIndex != -1)
                            fElementDeclPool.addIdRef(fStringPool.addSymbol(idName));
                    }
                    sb.append(idName);
                    if (!tokenizer.hasMoreTokens())
                        break;
                    sb.append(' ');
                }
            }
            String newAttValue = sb.toString();
            if (fValidating && (!ok || newAttValue.length() == 0)) {
                reportRecoverableXMLError(XMLMessages.MSG_IDREFS_INVALID,
                                          XMLMessages.VC_IDREF,
                                          fStringPool.toString(attrNameIndex), newAttValue);
            }
            if (!newAttValue.equals(attValue)) {
                attValueIndex = fStringPool.addString(newAttValue);
                if (fValidating && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
            }
        } else if (attType == fStringPool.addSymbol("ENTITY")) {
            String newAttValue = attValue.trim();
            if (fValidating) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
                if (newAttValue != attValue && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
                //
                // ENTITY - check that the value is an unparsed entity name (V_TAGa)
                //
                int entity = fEntityPool.lookupEntity(attValueIndex);
                if (entity == -1 || !fEntityPool.isUnparsedEntity(entity)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ENTITY_INVALID,
                                              XMLMessages.VC_ENTITY_NAME,
                                              fStringPool.toString(attrNameIndex), newAttValue);
                }
            } else if (newAttValue != attValue) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
            }
        } else if (attType == fStringPool.addSymbol("ENTITIES")) {
            StringTokenizer tokenizer = new StringTokenizer(attValue);
            StringBuffer sb = new StringBuffer(attValue.length());
            boolean ok = true;
            if (tokenizer.hasMoreTokens()) {
                while (true) {
                    String entityName = tokenizer.nextToken();
                    //
                    // ENTITIES - check that each value is an unparsed entity name (V_TAGa)
                    //
                    if (fValidating) {
                        int entity = fEntityPool.lookupEntity(fStringPool.addSymbol(entityName));
                        if (entity == -1 || !fEntityPool.isUnparsedEntity(entity)) {
                            ok = false;
                        }
                    }
                    sb.append(entityName);
                    if (!tokenizer.hasMoreTokens())
                        break;
                    sb.append(' ');
                }
            }
            String newAttValue = sb.toString();
            if (fValidating && (!ok || newAttValue.length() == 0)) {
                reportRecoverableXMLError(XMLMessages.MSG_ENTITIES_INVALID,
                                          XMLMessages.VC_ENTITY_NAME,
                                          fStringPool.toString(attrNameIndex), newAttValue);
            }
            if (!newAttValue.equals(attValue)) {
                attValueIndex = fStringPool.addString(newAttValue);
                if (fValidating && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
            }
        } else if (attType == fStringPool.addSymbol("NMTOKEN")) {
            String newAttValue = attValue.trim();
            if (fValidating) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
                if (newAttValue != attValue && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
                if (!XMLCharacterProperties.validNmtoken(newAttValue)) {
                    reportRecoverableXMLError(XMLMessages.MSG_NMTOKEN_INVALID,
                                              XMLMessages.VC_NAME_TOKEN,
                                              fStringPool.toString(attrNameIndex), newAttValue);
                }
            } else if (newAttValue != attValue) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
            }
        } else if (attType == fStringPool.addSymbol("NMTOKENS")) {
            StringTokenizer tokenizer = new StringTokenizer(attValue);
            StringBuffer sb = new StringBuffer(attValue.length());
            boolean ok = true;
            if (tokenizer.hasMoreTokens()) {
                while (true) {
                    String nmtoken = tokenizer.nextToken();
                    if (fValidating && !XMLCharacterProperties.validNmtoken(nmtoken)) {
                        ok = false;
                    }
                    sb.append(nmtoken);
                    if (!tokenizer.hasMoreTokens())
                        break;
                    sb.append(' ');
                }
            }
            String newAttValue = sb.toString();
            if (fValidating && (!ok || newAttValue.length() == 0)) {
                reportRecoverableXMLError(XMLMessages.MSG_NMTOKENS_INVALID,
                                          XMLMessages.VC_NAME_TOKEN,
                                          fStringPool.toString(attrNameIndex), newAttValue);
            }
            if (!newAttValue.equals(attValue)) {
                attValueIndex = fStringPool.addString(newAttValue);
                if (fValidating && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
            }
        } else if (attType == fStringPool.addSymbol("NOTATION") ||
                   attType == fStringPool.addSymbol("ENUMERATION")) {
            String newAttValue = attValue.trim();
            if (fValidating) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
                if (newAttValue != attValue && invalidStandaloneAttDef(elementTypeIndex, attrNameIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTVALUE_CHANGED_DURING_NORMALIZATION_WHEN_STANDALONE,
                                              XMLMessages.VC_STANDALONE_DOCUMENT_DECLARATION,
                                              fStringPool.toString(attrNameIndex), attValue, newAttValue);
                }
                //
                // NOTATION - check that the value is in the AttDef enumeration (V_TAGo)
                // ENUMERATION - check that value is in the AttDef enumeration (V_TAG9)
                //
                if (!fStringPool.stringInList(enumIndex, attValueIndex)) {
                    reportRecoverableXMLError(XMLMessages.MSG_ATTRIBUTE_VALUE_NOT_IN_LIST,
                                              attType == fStringPool.addSymbol("NOTATION") ?
                                               XMLMessages.VC_NOTATION_ATTRIBUTES :
                                               XMLMessages.VC_ENUMERATION,
                                              fStringPool.toString(attrNameIndex),
                                              newAttValue, fStringPool.stringListAsString(enumIndex));
                }
            } else if (newAttValue != attValue) {
                // REVISIT - can we release the old string?
                attValueIndex = fStringPool.addSymbol(newAttValue);
            }
        } else if (attType == fStringPool.addSymbol("DATATYPE")) {
            try { // REVISIT - integrate w/ error handling
                String type = fStringPool.toString(enumIndex);
                DatatypeValidator v = fDatatypeRegistry.getValidatorFor(type);
                if (v != null)
                    v.validate(attValue);
                else
                    reportSchemaError(SchemaMessageProvider.NoValidatorFor,
									  new Object [] { type });
            } catch (InvalidDatatypeValueException idve) {
				reportSchemaError(SchemaMessageProvider.IncorrectDatatype,
								  new Object [] { idve.getMessage() });
            } catch (Exception e) {
                e.printStackTrace();
                System.out.println("Internal error in attribute datatype validation");
            }
        } else {
            throw new RuntimeException("cannot happen 1");
        }
        return attValueIndex;
    }
    //
    // element stack
    //
    private void pushElement(int elementTypeIndex, int contentSpecType) {
        if (fElementDepth >= 0) {
            int[] children = fElementChildren[fElementDepth];
            int childCount = fElementChildCount[fElementDepth];
            if (children == null) {
                children = fElementChildren[fElementDepth] = new int[8];
                childCount = 0; // should really assert this...
            } else if (childCount == children.length) {
                int[] newChildren = new int[childCount * 2];
                System.arraycopy(children, 0, newChildren, 0, childCount);
                children = fElementChildren[fElementDepth] = newChildren;
            }
            children[childCount++] = elementTypeIndex;
            fElementChildCount[fElementDepth] = childCount;
        }
        fElementDepth++;
        if (fElementDepth == fElementTypeStack.length) {
            int[] newStack = new int[fElementDepth * 2];
            System.arraycopy(fElementTypeStack, 0, newStack, 0, fElementDepth);
            fElementTypeStack = newStack;
            newStack = new int[fElementDepth * 2];
            System.arraycopy(fContentSpecTypeStack, 0, newStack, 0, fElementDepth);
            fContentSpecTypeStack = newStack;
            newStack = new int[fElementDepth * 2];
            System.arraycopy(fElementChildCount, 0, newStack, 0, fElementDepth);
            fElementChildCount = newStack;
            int[][] newContentStack = new int[fElementDepth * 2][];
            System.arraycopy(fElementChildren, 0, newContentStack, 0, fElementDepth);
            fElementChildren = newContentStack;
        }
        fElementTypeStack[fElementDepth] = elementTypeIndex;
        fContentSpecTypeStack[fElementDepth] = contentSpecType;
        fElementChildCount[fElementDepth] = 0;
    }
    private void charDataInContent() {
        int[] children = fElementChildren[fElementDepth];
        int childCount = fElementChildCount[fElementDepth];
        if (children == null) {
            children = fElementChildren[fElementDepth] = new int[8];
            childCount = 0; // should really assert this...
        } else if (childCount == children.length) {
            int[] newChildren = new int[childCount * 2];
            System.arraycopy(children, 0, newChildren, 0, childCount);
            children = fElementChildren[fElementDepth] = newChildren;
        }
        children[childCount++] = -1;
        fElementChildCount[fElementDepth] = childCount;
    }
    private int peekElementType() {
        return fElementTypeStack[fElementDepth];
    }
    private int peekContentSpecType() {
        if (fElementDepth < 0) return -1;
        return fContentSpecTypeStack[fElementDepth];
    }
    private int peekChildCount() {
        return fElementChildCount[fElementDepth];
    }
    private int[] peekChildren() {
        return fElementChildren[fElementDepth];
    }
    private void popElement() throws Exception {
        if (fElementDepth < 0)
            throw new RuntimeException("Element stack underflow");
        if (--fElementDepth < 0) {
            //
            // Check after document is fully parsed
            // (1) check that there was an element with a matching id for every
            //   IDREF and IDREFS attr (V_IDREF0)
            //
            if (fValidating)
                checkIDRefNames();
        }
    }

    /**
     * Check that the attributes for an element are valid.
     * <p>
     * This method is called as a convenience. The scanner will do any required
     * checks for well-formedness on the attributes, as well as fill out any
     * defaulted ones. However, if the validator has any other constraints or
     * semantics it must enforce, it can use this API to do so.
     * <p>
     * The scanner provides the element index (within the decl pool, i.e. not the
     * name index which is within the string pool), and the index of the first
     * attribute within the attribute pool that holds the attributes of the element.
     * By this time, all defaulted attributes are present and all fixed values have
     * been confirmed. For most validators, this will be a no-op.
     *
     * @param elementIndex The index within the <code>ElementDeclPool</code> of
     *                     this element.
     * @param firstAttrIndex The index within the <code>AttrPool</code> of the
     *                       first attribute of this element, or -1 if there are
     *                       no attributes.
     *
     * @exception Exception Thrown on error.
     */
    private void checkAttributes(int elementIndex, XMLAttrList attrList, int attrIndex) throws Exception
    {
        if (DEBUG_PRINT_ATTRIBUTES) {
            int elementTypeIndex = fElementDeclPool.getElementType(elementIndex);
            String elementType = fStringPool.toString(elementTypeIndex);
            System.out.print("checkAttributes: <" + elementType);
            if (attrIndex != -1) {
                int index = attrList.getFirstAttr(attrIndex);
                while (index != -1) {
                    int attNameIndex = attrList.getAttrName(index);
                    if (attNameIndex != -1) {
                        int adIndex = fElementDeclPool.getAttDef(elementTypeIndex, attNameIndex);
                        if (adIndex != -1)
                            System.out.println(fStringPool.toString(getAttName(adIndex))+" "+
                                               fElementDeclPool.getAttType(adIndex)+" "+
                                               fElementDeclPool.getEnumeration(adIndex));
                        else
                            System.out.println("Missing adIndex for "+fStringPool.toString(attNameIndex));
                    } else
                        System.out.println("Missing attNameIndex");
                    System.out.print(" " + fStringPool.toString(attrList.getAttrName(index)) + "=\"" +
                            fStringPool.toString(attrList.getAttValue(index)) + "\"");
                    index = attrList.getNextAttr(index);
                }
            }
            System.out.println(">");
        }
    }

    /**
     * Check that the content of an element is valid.
     * <p>
     * This is the method of primary concern to the validator. This method is called
     * upon the scanner reaching the end tag of an element. At that time, the
     * element's children must be structurally validated, so it calls this method.
     * The index of the element being checked (in the decl pool), is provided as
     * well as an array of element name indexes of the children. The validator must
     * confirm that this element can have these children in this order.
     * <p>
     * This can also be called to do 'what if' testing of content models just to see
     * if they would be valid.
     * <p>
     * Note that the element index is an index into the element decl pool, whereas
     * the children indexes are name indexes, i.e. into the string pool.
     * <p>
     * A value of -1 in the children array indicates a PCDATA node. All other
     * indexes will be positive and represent child elements. The count can be
     * zero, since some elements have the EMPTY content model and that must be
     * confirmed.
     *
     * @param elementIndex The index within the <code>ElementDeclPool</code> of this
     *                     element.
     * @param childCount The number of entries in the <code>children</code> array.
     * @param children The children of this element.  Each integer is an index within
     *                 the <code>StringPool</code> of the child element name.  An index
     *                 of -1 is used to indicate an occurrence of non-whitespace character
     *                 data.
     *
     * @return The value -1 if fully valid, else the 0 based index of the child
     *         that first failed. If the value returned is equal to the number
     *         of children, then additional content is required to reach a valid
     *         ending state.
     *
     * @exception Exception Thrown on error.
     */
    public int checkContent(int     elementIndex
                            , int   childCount
                            , int[] children) throws Exception
    {
        // Get the element name index from the element
        final int elementTypeIndex = fElementDeclPool.getElementType(elementIndex);

        if (DEBUG_PRINT_CONTENT)
        {
            String strTmp = fStringPool.toString(elementTypeIndex);
            System.out.println
            (
                "Name: "
                + strTmp
                + ", Count: "
                + childCount
                + ", ContentSpec: "
                + fElementDeclPool.getContentSpecAsString(elementIndex)
            );
            for (int index = 0; index < childCount && index < 10; index++) {
                if (index == 0) System.out.print("  (");
                String childName = (children[index] == -1) ? "#PCDATA" : fStringPool.toString(children[index]);
                if (index + 1 == childCount)
                    System.out.println(childName + ")");
                else if (index + 1 == 10)
                    System.out.println(childName + ",...)");
                else
                    System.out.print(childName + ",");
            }
        }

        // Get out the content spec for this element
        final int contentSpec = fElementDeclPool.getContentSpecType(elementIndex);

        //
        //  Deal with the possible types of content. We try to optimized here
        //  by dealing specially with content models that don't require the
        //  full DFA treatment.
        //
        if (contentSpec == fStringPool.addSymbol("EMPTY"))
        {
            //
            //  If the child count is greater than zero, then this is
            //  an error right off the bat at index 0.
            //
            if (childCount != 0)
                return 0;
        }
         else if (contentSpec == fStringPool.addSymbol("ANY"))
        {
            //
            //  This one is open game so we don't pass any judgement on it
            //  at all. Its assumed to fine since it can hold anything.
            //
        }
         else if (contentSpec == fStringPool.addSymbol("MIXED")
              ||  contentSpec == fStringPool.addSymbol("CHILDREN"))
        {
            // Get the content model for this element, faulting it in if needed
            XMLContentModel cmElem = null;
            try
            {
                cmElem = getContentModel(elementIndex);
                return cmElem.validateContent(childCount, children);
            }

            catch(CMException excToCatch)
            {
                int majorCode = excToCatch.getErrorCode();
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                                           ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                           majorCode,
                                           0,
                                           null,
                                           XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
            }
        }
         else if (contentSpec == -1)
        {
            Object[] args = { fStringPool.toString(elementTypeIndex) };
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       XMLMessages.XML_DOMAIN,
                                       XMLMessages.MSG_ELEMENT_NOT_DECLARED,
                                       XMLMessages.VC_ELEMENT_VALID,
                                       args,
                                       XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
        }
         else if (contentSpec == fStringPool.addSymbol("DATATYPE"))
        {

            XMLContentModel cmElem = null;
            try {
                cmElem = getContentModel(elementIndex);
                return cmElem.validateContent(1, new int[] { fStringPool.addString(fDatatypeBuffer.toString()) });
            } catch (CMException cme) {
                System.out.println("Internal Error in datatype validation");
            } catch (InvalidDatatypeValueException idve) {
                reportSchemaError(SchemaMessageProvider.DatatypeError,
                                  new Object [] { idve.getMessage() });
            }
/*
            boolean DEBUG_DATATYPES = false;
            if (DEBUG_DATATYPES) {
                System.out.println("Checking content of datatype");
                String strTmp = fStringPool.toString(elementTypeIndex);
                int contentSpecIndex = fElementDeclPool.getContentSpec(elementIndex);
                XMLContentSpecNode csn = new XMLContentSpecNode();
                fElementDeclPool.getContentSpecNode(contentSpecIndex, csn);
                String contentSpecString = fStringPool.toString(csn.value);
                System.out.println
                (
                    "Name: "
                    + strTmp
                    + ", Count: "
                    + childCount
                    + ", ContentSpec: "
                    + contentSpecString
                );
                for (int index = 0; index < childCount && index < 10; index++) {
                    if (index == 0) System.out.print("  (");
                    String childName = (children[index] == -1) ? "#PCDATA" : fStringPool.toString(children[index]);
                    if (index + 1 == childCount)
                        System.out.println(childName + ")");
                    else if (index + 1 == 10)
                        System.out.println(childName + ",...)");
                    else
                        System.out.print(childName + ",");
                }
            }
            try { // REVISIT - integrate w/ error handling
                int contentSpecIndex = fElementDeclPool.getContentSpec(elementIndex);
                XMLContentSpecNode csn = new XMLContentSpecNode();
                fElementDeclPool.getContentSpecNode(contentSpecIndex, csn);
                String type = fStringPool.toString(csn.value);
                DatatypeValidator v = fDatatypeRegistry.getValidatorFor(type);
                if (v != null)
                    v.validate(fDatatypeBuffer.toString());
                else
                    System.out.println("No validator for datatype "+type);
            } catch (InvalidDatatypeValueException idve) {
                System.out.println("Incorrect datatype: "+idve.getMessage());
            } catch (Exception e) {
                e.printStackTrace();
                System.out.println("Internal error in datatype validation");
            }
 */
        }
         else
        {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                       ImplementationMessages.VAL_CST,
                                       0,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        }

        // We succeeded
        return -1;
    }

    /**
     * Check that all ID references were to ID attributes present in the document.
     * <p>
     * This method is a convenience call that allows the validator to do any id ref
     * checks above and beyond those done by the scanner. The scanner does the checks
     * specificied in the XML spec, i.e. that ID refs refer to ids which were
     * eventually defined somewhere in the document.
     * <p>
     * If the validator is for a Schema perhaps, which defines id semantics beyond
     * those of the XML specificiation, this is where that extra checking would be
     * done. For most validators, this is a no-op.
     *
     * @exception Exception Thrown on error.
     */
    public void checkIDRefNames() throws Exception
    {
        fElementDeclPool.checkIdRefs();
    }

    /**
     * Returns information about which elements can be placed at a particular point
     * in the passed element's content model.
     * <p>
     * Note that the incoming content model to test must be valid at least up to
     * the insertion point. If not, then -1 will be returned and the info object
     * will not have been filled in.
     * <p>
     * If, on return, the info.isValidEOC flag is set, then the 'insert after'
     * elemement is a valid end of content, i.e. nothing needs to be inserted
     * after it to make the parent element's content model valid.
     *
     * @param elementIndex The index within the <code>ElementDeclPool</code> of the
     *                     element which is being querying.
     * @param fullyValid Only return elements that can be inserted and still
     *                   maintain the validity of subsequent elements past the
     *                   insertion point (if any).  If the insertion point is at
     *                   the end, and this is true, then only elements that can
     *                   be legal final states will be returned.
     * @param info An object that contains the required input data for the method,
     *             and which will contain the output information if successful.
     *
     * @return The value -1 if fully valid, else the 0 based index of the child
     *         that first failed before the insertion point. If the value
     *         returned is equal to the number of children, then the specified
     *         children are valid but additional content is required to reach a
     *         valid ending state.
     *
     * @exception Exception Thrown on error.
     *
     * @see InsertableElementsInfo
     */
    public int whatCanGoHere(int                        elementIndex
                            , boolean                   fullyValid
                            , InsertableElementsInfo    info) throws Exception
    {
        //
        //  Do some basic sanity checking on the info packet. First, make sure
        //  that insertAt is not greater than the child count. It can be equal,
        //  which means to get appendable elements, but not greater. Or, if
        //  the current children array is null, that's bad too.
        //
        //  Since the current children array must have a blank spot for where
        //  the insert is going to be, the child count must always be at least
        //  one.
        //
        //  Make sure that the child count is not larger than the current children
        //  array. It can be equal, which means get appendable elements, but not
        //  greater.
        //
        if ((info.insertAt > info.childCount)
        ||  (info.curChildren == null)
        ||  (info.childCount < 1)
        ||  (info.childCount > info.curChildren.length))
        {
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                       ImplementationMessages.VAL_WCGHI,
                                       0,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        }

        int retVal = 0;
        try
        {
            // Get the content model for this element
            final XMLContentModel cmElem = getContentModel(elementIndex);

            // And delegate this call to it
            retVal = cmElem.whatCanGoHere(fullyValid, info);
        }

        catch(CMException excToCatch)
        {
            // REVISIT - Translate caught error to the public error handler interface
            int majorCode = excToCatch.getErrorCode();
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                                       ImplementationMessages.XERCES_IMPLEMENTATION_DOMAIN,
                                       majorCode,
                                       0,
                                       null,
                                       XMLErrorReporter.ERRORTYPE_FATAL_ERROR);
        }
        return retVal;
    }


    // -----------------------------------------------------------------------
    //  Private methods
    // -----------------------------------------------------------------------

    //
    //  When the element has a 'CHILDREN' model, this method is called to
    //  create the content model object. It looks for some special case simple
    //  models and creates SimpleContentModel objects for those. For the rest
    //  it creates the standard DFA style model.
    //
    private final XMLContentModel createChildModel(int elementIndex) throws CMException
    {
        //
        //  Get the content spec node for the element we are working on.
        //  This will tell us what kind of node it is, which tells us what
        //  kind of model we will try to create.
        //
        XMLContentSpecNode specNode = new XMLContentSpecNode();
        int contentSpecIndex = fElementDeclPool.getContentSpec(elementIndex);
        fElementDeclPool.getContentSpecNode(contentSpecIndex, specNode);

        //
        //  Check that the left value is not -1, since any content model
        //  with PCDATA should be MIXED, so we should not have gotten here.
        //
        if (specNode.value == -1)
            throw new CMException(ImplementationMessages.VAL_NPCD);

        if (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_LEAF)
        {
            //
            //  Its a single leaf, so its an 'a' type of content model, i.e.
            //  just one instance of one element. That one is definitely a
            //  simple content model.
            //
            return new SimpleContentModel(specNode.value, -1, specNode.type);
        }
         else if ((specNode.type == XMLContentSpecNode.CONTENTSPECNODE_CHOICE)
              ||  (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_SEQ))
        {
            //
            //  Lets see if both of the children are leafs. If so, then it
            //  it has to be a simple content model
            //
            XMLContentSpecNode specLeft = new XMLContentSpecNode();
            XMLContentSpecNode specRight = new XMLContentSpecNode();
            fElementDeclPool.getContentSpecNode(specNode.value, specLeft);
            fElementDeclPool.getContentSpecNode(specNode.otherValue, specRight);

            if ((specLeft.type == XMLContentSpecNode.CONTENTSPECNODE_LEAF)
            &&  (specRight.type == XMLContentSpecNode.CONTENTSPECNODE_LEAF))
            {
                //
                //  Its a simple choice or sequence, so we can do a simple
                //  content model for it.
                //
                return new SimpleContentModel
                (
                    specLeft.value
                    , specRight.value
                    , specNode.type
                );
            }
        }
         else if ((specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE)
              ||  (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE)
              ||  (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ONE_OR_MORE))
        {
            //
            //  Its a repetition, so see if its one child is a leaf. If so
            //  its a repetition of a single element, so we can do a simple
            //  content model for that.
            //
            XMLContentSpecNode specLeft = new XMLContentSpecNode();
            fElementDeclPool.getContentSpecNode(specNode.value, specLeft);

            if (specLeft.type == XMLContentSpecNode.CONTENTSPECNODE_LEAF)
            {
                //
                //  It is, so we can create a simple content model here that
                //  will check for this repetition. We pass -1 for the unused
                //  right node.
                //
                return new SimpleContentModel(specLeft.value, -1, specNode.type);
            }
        }
         else
        {
            throw new CMException(ImplementationMessages.VAL_CST);
        }

        //
        //  Its not a simple content model, so here we have to create a DFA
        //  for this element. So we create a DFAContentModel object. He
        //  encapsulates all of the work to create the DFA.
        //
        fLeafCount = 0;
        fEpsilonIndex = fStringPool.addSymbol("<<CMNODE_EPSILON>>");
        CMNode cmn = buildSyntaxTree(contentSpecIndex, specNode);
        return new DFAContentModel
        (
            fStringPool
            , cmn
            , fLeafCount
        );
    }


    //
    //  This method will handle the querying of the content model for a
    //  particular element. If the element does not have a content model, then
    //  it will be created.
    //
    public XMLContentModel getContentModel(int elementIndex) throws CMException
    {
        // See if a content model already exists first
        XMLContentModel cmRet = fElementDeclPool.getContentModel(elementIndex);

        // If we have one, just return that. Otherwise, gotta create one
        if (cmRet != null)
            return cmRet;

        // Get the type of content this element has
        final int contentSpec = fElementDeclPool.getContentSpecType(elementIndex);

        // And create the content model according to the spec type
        if (contentSpec == fStringPool.addSymbol("MIXED"))
        {
            //
            //  Just create a mixel content model object. This type of
            //  content model is optimized for mixed content validation.
            //
            XMLContentSpecNode specNode = new XMLContentSpecNode();
            int contentSpecIndex = fElementDeclPool.getContentSpec(elementIndex);
            makeContentList(contentSpecIndex, specNode);
            cmRet = new MixedContentModel(fCount, fContentList);
        }
         else if (contentSpec == fStringPool.addSymbol("CHILDREN"))
        {
            //
            //  This method will create an optimal model for the complexity
            //  of the element's defined model. If its simple, it will create
            //  a SimpleContentModel object. If its a simple list, it will
            //  create a SimpleListContentModel object. If its complex, it
            //  will create a DFAContentModel object.
            //
            cmRet = createChildModel(elementIndex);
        }
         else if (contentSpec == fStringPool.addSymbol("DATATYPE")) {
            cmRet = new DatatypeContentModel(fDatatypeRegistry, fElementDeclPool, fStringPool, elementIndex);
        }
         else
        {
            throw new CMException(ImplementationMessages.VAL_CST);
        }

        // Add the new model to the content model for this element
        fElementDeclPool.setContentModel(elementIndex, cmRet);

        return cmRet;
    }
    //
    //  This method will build our syntax tree by recursively going though
    //  the element's content model and creating new CMNode type node for
    //  the model, and rewriting '?' and '+' nodes along the way.
    //
    //  On final return, the head node of the syntax tree will be returned.
    //  This top node will be a sequence node with the left side being the
    //  rewritten content, and the right side being a special end of content
    //  node.
    //
    //  We also count the non-epsilon leaf nodes, which is an important value
    //  that is used in a number of places later.
    //
    private int fLeafCount = 0;
    private int fEpsilonIndex = -1;
    private final CMNode
    buildSyntaxTree(int startNode, XMLContentSpecNode specNode) throws CMException
    {
        // We will build a node at this level for the new tree
        CMNode nodeRet = null;
        getContentSpecNode(startNode, specNode);

        //
        //  If this node is a leaf, then its an easy one. We just add it
        //  to the tree.
        //
        if (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_LEAF)
        {
            //
            //  Create a new leaf node, and pass it the current leaf count,
            //  which is its DFA state position. Bump the leaf count after
            //  storing it. This makes the positions zero based since we
            //  store first and then increment.
            //
            nodeRet = new CMLeaf(specNode.type, specNode.value, fLeafCount++);
        }
         else
        {
            //
            //  Its not a leaf, so we have to recurse its left and maybe right
            //  nodes. Save both values before we recurse and trash the node.
            //
            final int leftNode = specNode.value;
            final int rightNode = specNode.otherValue;

            if ((specNode.type == XMLContentSpecNode.CONTENTSPECNODE_CHOICE)
            ||  (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_SEQ))
            {
                //
                //  Recurse on both children, and return a binary op node
                //  with the two created sub nodes as its children. The node
                //  type is the same type as the source.
                //

                nodeRet = new CMBinOp
                (
                    specNode.type
                    , buildSyntaxTree(leftNode, specNode)
                    , buildSyntaxTree(rightNode, specNode)
                );
            }
             else if (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE)
            {
                nodeRet = new CMUniOp
                (
                    specNode.type
                    , buildSyntaxTree(leftNode, specNode)
                );
            }
             else if (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE)
            {
                // Convert to (x|epsilon)
                nodeRet = new CMBinOp
                (
                    XMLContentSpecNode.CONTENTSPECNODE_CHOICE
                    , buildSyntaxTree(leftNode, specNode)
                    , new CMLeaf(XMLContentSpecNode.CONTENTSPECNODE_LEAF, fEpsilonIndex)
                );
            }
             else if (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ONE_OR_MORE)
            {
                // Convert to (x,x*)
                nodeRet = new CMBinOp
                (
                    XMLContentSpecNode.CONTENTSPECNODE_SEQ
                    , buildSyntaxTree(leftNode, specNode)
                    , new CMUniOp
                      (
                        XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE
                        , buildSyntaxTree(leftNode, specNode)
                      )
                );
            }
             else
            {
                throw new CMException(ImplementationMessages.VAL_CST);
            }
        }

        // And return our new node for this level
        return nodeRet;
    }

    private int fCount = 0;
    private int[] fContentList = new int[64];
    private final void makeContentList(int startNode, XMLContentSpecNode specNode) throws CMException {
        //
        //  Ok, we need to build up an array of the possible children
        //  under this element. The mixed content model can only be a
        //  repeated series of alternations with no numeration or ordering.
        //  So we call a local recursive method to iterate the tree and
        //  build up the array.
        //
        //  So we get the content spec of the element, which gives us the
        //  starting node. Everything else kicks off from there. We pass
        //  along a content node for each iteration to use so that it does
        //  not have to create and trash lots of objects.
        //
        while (true)
        {
            fCount = 0;

            try
            {
                fCount = buildContentList
                (
                    startNode
                    , 0
                    , specNode
                );
            }

            catch(IndexOutOfBoundsException excToCatch)
            {
                //
                //  Expand the array and try it again. Yes, this is
                //  piggy, but the odds of it ever actually happening
                //  are slim to none.
                //
                fContentList = new int[fContentList.length * 2];
                fCount = 0;
                continue;
            }

            // We survived, so break out
            break;
        }
    }
    private final int buildContentList( int                     startNode
                                        , int                   count
                                        , XMLContentSpecNode    specNode) throws CMException
    {
        // Get the content spec for the passed start node
        fElementDeclPool.getContentSpecNode(startNode, specNode);

        // If this node is a leaf, then add it to our list and return.
        if (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_LEAF)
        {
            fContentList[count++] = specNode.value;
            return count;
        }

        //
        //  Its not a leaf, so we have to recurse its left and maybe right
        //  nodes. Save both values before we recurse and trash the node.
        //
        final int leftNode = specNode.value;
        final int rightNode = specNode.otherValue;

        if ((specNode.type == XMLContentSpecNode.CONTENTSPECNODE_CHOICE)
        ||  (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_SEQ))
        {
            //
            //  Recurse on the left and right nodes of this guy, making sure
            //  to keep the count correct.
            //
            count = buildContentList(leftNode, count, specNode);
            count = buildContentList(rightNode, count, specNode);
        }
         else if ((specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE)
              ||  (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE)
              ||  (specNode.type == XMLContentSpecNode.CONTENTSPECNODE_ONE_OR_MORE))
        {
            // Just do the left node on this one
            count = buildContentList(leftNode, count, specNode);
        }
         else
        {
            throw new CMException(ImplementationMessages.VAL_CST);
        }

        // And return our accumlated new count
        return count;
    }
    //
    //
    //
    protected void reportRecoverableXMLError(int majorCode, int minorCode) throws Exception {
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   null,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
    }
    protected void reportRecoverableXMLError(int majorCode, int minorCode, int stringIndex1) throws Exception {
        Object[] args = { fStringPool.toString(stringIndex1) };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
    }
    protected void reportRecoverableXMLError(int majorCode, int minorCode, String string1) throws Exception {
        Object[] args = { string1 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
    }
    protected void reportRecoverableXMLError(int majorCode, int minorCode, int stringIndex1, int stringIndex2) throws Exception {
        Object[] args = { fStringPool.toString(stringIndex1), fStringPool.toString(stringIndex2) };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
    }
    protected void reportRecoverableXMLError(int majorCode, int minorCode, String string1, String string2) throws Exception {
        Object[] args = { string1, string2 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
    }
    protected void reportRecoverableXMLError(int majorCode, int minorCode, String string1, String string2, String string3) throws Exception {
        Object[] args = { string1, string2, string3 };
        fErrorReporter.reportError(fErrorReporter.getLocator(),
                                   XMLMessages.XML_DOMAIN,
                                   majorCode,
                                   minorCode,
                                   args,
                                   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
    }

    // content spec node types

    /** Occurrence count: [0, n]. */
    private static final int CONTENTSPECNODE_ZERO_TO_N = XMLContentSpecNode.CONTENTSPECNODE_SEQ + 1;

    /** Occurrence count: [m, n]. */
    private static final int CONTENTSPECNODE_M_TO_N = CONTENTSPECNODE_ZERO_TO_N + 1;

    /** Occurrence count: [m, *). */
    private static final int CONTENTSPECNODE_M_OR_MORE = CONTENTSPECNODE_M_TO_N + 1;

    private DOMParser fSchemaParser = null;

    public void loadSchema(String uri) {

        // get URI to schema file
        //String uri = getSchemaURI(data);
        //if (uri == null) {
        //    System.err.println("error: malformed href pseudo-attribute ("+data+')');
        //    return;
        //}

        // resolve schema file relative to *this* file
        String systemId = fEntityHandler.expandSystemId(uri);

        // create parser for schema
        if (fSchemaParser == null) {
            fSchemaParser = new DOMParser() {
                public void ignorableWhitespace(char ch[], int start, int length) {}
                public void ignorableWhitespace(int dataIdx) {}
            };
            fSchemaParser.setEntityResolver(new Resolver());
            fSchemaParser.setErrorHandler(new ErrorHandler());
        }

        // parser schema file
        try {

            fSchemaParser.setFeature("http://xml.org/sax/features/validation", true);
            fSchemaParser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", false);
            fSchemaParser.parse(systemId);
        }
        catch (SAXException se) {
            se.getException().printStackTrace();
            System.err.println("error parsing schema file");
            System.exit(1);
        }
        catch (Exception e) {
            e.printStackTrace();
            System.err.println("error parsing schema file");
            System.exit(1);
        }
        fSchemaDocument = fSchemaParser.getDocument();
        if (fSchemaDocument == null) {
            System.err.println("error: couldn't load schema file!");
            return;
        }

        // traverse schema
        try {
            Element root = fSchemaDocument.getDocumentElement();
            traverseSchema(root);
        }
        catch (Exception e) {
            e.printStackTrace(System.err);
            System.exit(1);
        }
    }

    private void traverseSchema(Element root) throws Exception {
        // is there anything to do?
        if (root == null) {
            return;
        }

        // run through children
        for (Element child = XUtil.getFirstChildElement(root);
             child != null;
             child = XUtil.getNextSiblingElement(child)) {
            //System.out.println("child: "+child.getNodeName()+' '+child.getAttribute(ATT_NAME));

            //
            // Element type
            //

            String name = child.getNodeName();
			if (name.equals(ELT_COMMENT)) {
				traverseComment(child);
            } else if (name.equals(ELT_DATATYPEDECL)) {
				traverseDatatypeDecl(child);
            } else if (name.equals(ELT_ARCHETYPEDECL)) {
				traverseTypeDecl(child);
			} else if (name.equals(ELT_ELEMENTDECL)) { // && child.getAttribute(ATT_REF).equals("")) {
				traverseElementDecl(child);
			} else if (name.equals(ELT_ATTRGROUPDECL)) {
				traverseAttrGroup(child);
			} else if (name.equals(ELT_MODELGROUPDECL)) {
				traverseModelGroup(child);
			}

            //
            // Entities
            //

            else if (name.equals(ELT_TEXTENTITYDECL) ||
                     name.equals(ELT_EXTERNALENTITYDECL) ||
                     name.equals(ELT_UNPARSEDENTITYDECL)) {

                int entityName = fStringPool.addSymbol(child.getAttribute(ATT_NAME));

                if (name.equals(ELT_TEXTENTITYDECL)) {
                    int value = fStringPool.addString(child.getFirstChild().getNodeValue());
                    fEntityPool.addEntityDecl(entityName, value, -1, -1, -1, -1, true);
                }
                else {
                    int publicId = fStringPool.addString(child.getAttribute("public"));
                    int systemId = fStringPool.addString(child.getAttribute("system"));

                    if (name.equals(ELT_EXTERNALENTITYDECL)) {
                        fEntityPool.addEntityDecl(entityName, -1, -1, publicId, systemId, -1, true);
                    }
                    else {
                        int notationName = fStringPool.addSymbol(child.getAttribute("notation"));
                        fEntityPool.addEntityDecl(entityName, -1, -1, publicId, systemId, notationName, true);
                    }
                }
            }

            //
            // Notation
            //

            else if (name.equals(ELT_NOTATIONDECL)) {

                int notationName = fStringPool.addSymbol(child.getAttribute(ATT_NAME));
                int publicId = fStringPool.addString(child.getAttribute("public"));
                int systemId = fStringPool.addString(child.getAttribute("system"));
                fEntityPool.addNotationDecl(notationName, publicId, systemId, true);
            }

        } // for each child node

        cleanupForwardReferences();
    } // traverseSchema(Element)

    /**
     * this method is going to be needed to handle any elementDecl derived constructs which
     * need to copy back attributes that haven't been declared yet.
     * right now that's just attributeGroups and types -- grrr.
     */
    private void cleanupForwardReferences() {
        for (java.util.Enumeration keys = fForwardRefs.keys(); keys.hasMoreElements();) {
            Object k = keys.nextElement();
            int ik = ((Integer) k).intValue();
            cleanupForwardReferencesTo(ik);
        }
    }

    private void cleanupForwardReferencesTo(int r) {
        Vector referrers = (Vector) fForwardRefs.get(new Integer(r));
        if (referrers == null) return;
//        System.out.println("referee "+r+" csnIndex= "+getContentSpec(getElement(r)));
        for (int i = 0; i < referrers.size(); i++) {
            int ref = ((Integer) referrers.elementAt(i)).intValue();
//            System.out.println("referrer "+referrers.elementAt(i)+ " csnIndex = "+getContentSpec(getElement(((Integer)referrers.elementAt(i)).intValue())));
//            System.out.println("copying from "+fStringPool.toString(r)+" to "+fStringPool.toString(ref));
            fElementDeclPool.copyAtts(r, ((Integer) referrers.elementAt(i)).intValue());
//            try {
//                fElementDeclPool.fixupDeclaredElements(ref, r);
//            } catch (Exception e) {
//                System.out.println("Error while cleaning up");
//            }
//            cleanupForwardReferencesTo(ref);
        }
    }

	private void traverseComment(Element comment) {
        return; // do nothing
	}

	private int traverseTypeDecl(Element typeDecl) throws Exception {
		String typeName = typeDecl.getAttribute(ATT_NAME);
		String content = typeDecl.getAttribute(ATT_CONTENT);
		String model = typeDecl.getAttribute(ATT_MODEL);
		String order = typeDecl.getAttribute(ATT_ORDER);
		String type = typeDecl.getAttribute(ATT_TYPE);
		String deflt = typeDecl.getAttribute(ATT_DEFAULT);
		String fixed = typeDecl.getAttribute(ATT_FIXED);
		String schemaAbbrev = typeDecl.getAttribute(ATT_SCHEMAABBREV);
		String schemaName = typeDecl.getAttribute(ATT_SCHEMANAME);
		
		if (typeName.equals("")) { // gensym a unique name
		    typeName = "http://www.apache.org/xml/xerces/internalType"+fTypeCount++;
		}
		
		// integrity checks
		if (type.equals("")) {
		    if (!schemaAbbrev.equals(""))
				reportSchemaError(SchemaMessageProvider.AttMissingType,
							new Object [] { "schemaAbbrev" });
		    if (!schemaName.equals(""))
				reportSchemaError(SchemaMessageProvider.AttMissingType,
							new Object [] { "schemaName" });
		    if (!deflt.equals(""))
				reportSchemaError(SchemaMessageProvider.AttMissingType,
							new Object [] { "default" });
		    if (!fixed.equals(""))
				reportSchemaError(SchemaMessageProvider.AttMissingType,
							new Object [] { "fixed" });
		} else {
            if (fDatatypeRegistry.getValidatorFor(type) != null) // must be datatype
				reportSchemaError(SchemaMessageProvider.NotADatatype,
								  new Object [] { type }); //REVISIT check forward refs
            if (!content.equals(ATTVAL_TEXTONLY)) //REVISIT: check if attribute was specified, if not, set
				reportSchemaError(SchemaMessageProvider.TextOnlyContentWithType, null);
		    // REVISIT handle datatypes
		}
		
		Element child = XUtil.getFirstChildElement(typeDecl);
		Element refines = null;

		// skip the refines
		if (child != null && child.getNodeName().equals(ELT_REFINES)) {
			reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
							  new Object [] { "Refinement" });
			refines = child;
			child = XUtil.getNextSiblingElement(child);
		}
		
		int contentSpecType = 0;
		int csnType = 0;
        boolean mixedContent = false;
        boolean elementContent = false;
        boolean textContent = false;
        boolean buildAll = false;
        int allChildren[] = null;
        int allChildCount = 0;
		int left = -2;
		int right = -2;
		boolean hadContent = false;
		
        if (order.equals(ATTVAL_CHOICE)) {
			csnType = XMLContentSpecNode.CONTENTSPECNODE_CHOICE;
			contentSpecType = fStringPool.addSymbol("CHILDREN");
		} else if (order.equals(ATTVAL_SEQ)) {
			csnType = XMLContentSpecNode.CONTENTSPECNODE_SEQ;
			contentSpecType = fStringPool.addSymbol("CHILDREN");
		} else if (order.equals(ATTVAL_ALL)) {
            buildAll = true;
            allChildren = new int[((org.apache.xerces.dom.NodeImpl)typeDecl).getLength()];
            allChildCount = 0;
		}

		if (content.equals(ATTVAL_EMPTY)) {
			contentSpecType = fStringPool.addSymbol("EMPTY");
			left = -1; // no contentSpecNode needed
		} else if (content.equals(ATTVAL_ANY)) {
			contentSpecType = fStringPool.addSymbol("ANY");
			left = -1; // no contentSpecNode needed
		} else if (content.equals(ATTVAL_MIXED)) {
		    contentSpecType = fStringPool.addSymbol("MIXED");
		    mixedContent = true;
		    csnType = XMLContentSpecNode.CONTENTSPECNODE_CHOICE;
		} else if (content.equals(ATTVAL_ELEMONLY)) {
            elementContent = true;
		} else if (content.equals(ATTVAL_TEXTONLY)) {
            textContent = true;
        }

        if (mixedContent) {
    	    // add #PCDATA leaf
            left = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_LEAF,
					      							   -1, // -1 means "#PCDATA" is name
													   -1, false);
        }

        Vector uses = new Vector();
		for (;
			 child != null;
			 child = XUtil.getNextSiblingElement(child)) {
			int index = -2;
            hadContent = true;
			String childName = child.getNodeName();
			if (childName.equals(ELT_ELEMENTDECL)) {
			    if (child.getAttribute(ATT_REF).equals("")) { // elt decl
			        if (elementContent)   //REVISIT: no support for nested type declarations
						reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
										  new Object [] { "Nesting element declarations" });
        			else
						reportSchemaError(SchemaMessageProvider.NestedOnlyInElemOnly, null);
    			} else if (mixedContent || elementContent) { // elt ref
    			    index = traverseElementRef(child);
    			} else {
					reportSchemaError(SchemaMessageProvider.EltRefOnlyInMixedElemOnly, null);
    			}
			} else if (childName.equals(ELT_GROUP)) {
			    if (elementContent && !buildAll) {
    			    int groupNameIndex = traverseGroup(child);
	    			index = getContentSpec(getElement(groupNameIndex));
				} else if (!elementContent)
					reportSchemaError(SchemaMessageProvider.OnlyInEltContent,
									  new Object [] { "group" });
			    else // buildAll
					reportSchemaError(SchemaMessageProvider.OrderIsAll,
									  new Object [] { "group" } );
			} else if (childName.equals(ELT_MODELGROUPREF)) {
			    if (elementContent && !buildAll) {
    				int modelGroupNameIndex = traverseModelGroup(child);
	    			index = getContentSpec(getElement(modelGroupNameIndex));
		    		if (index == -1)
						reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
										  new Object [] { "Forward reference to model group" });
				    index = expandContentModel(index, child);
				} else if (!elementContent)
					reportSchemaError(SchemaMessageProvider.OnlyInEltContent,
									  new Object [] { "modelGroupRef" });
				else // buildAll
					reportSchemaError(SchemaMessageProvider.OrderIsAll,
									  new Object [] { "modelGroupRef" });
			} else if (childName.equals(ELT_ATTRIBUTEDECL) || childName.equals(ELT_ATTRGROUPREF)) {
			    break; // attr processing is done below
			} else { // datatype qual
			    if (type.equals(""))
					reportSchemaError(SchemaMessageProvider.DatatypeWithType, null);
			    else
					reportSchemaError(SchemaMessageProvider.DatatypeQualUnsupported,
									  new Object [] { childName });
			}
            uses.addElement(new Integer(index));
			if (buildAll) {
			    allChildren[allChildCount++] = index;
			} else if (left == -2) {
				left = index;
			} else if (right == -2) {
				right = index;
			} else {
   				left = fElementDeclPool.addContentSpecNode(csnType, left, right, false);
    			right = index;
   			}
		}
		if (buildAll) {
		    left = buildAllModel(allChildren,allChildCount);
		} else {
		    if (hadContent && right != -2)
       		    left = fElementDeclPool.addContentSpecNode(csnType, left, right, false);
		
    		if (mixedContent && hadContent) {
	    		// set occurrence count
		    	left = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE,
													   left, -1, false);
	    	}
		}
		
		// stick in ElementDeclPool as a hack
		int typeNameIndex = fStringPool.addSymbol(typeName); //REVISIT namespace clashes possible
		int typeIndex = fElementDeclPool.addElementDecl(typeNameIndex, contentSpecType, left, false);

        for (int x = 0; x < uses.size(); x++)
            addUse(typeNameIndex, (Integer)uses.elementAt(x));

		// (attribute | attrGroupRef)*
		for (;
			 child != null;
			 child = XUtil.getNextSiblingElement(child)) {
			String childName = child.getNodeName();
			if (childName.equals(ELT_ATTRIBUTEDECL)) {
				traverseAttributeDecl(child, typeIndex);
			} else if (childName.equals(ELT_ATTRGROUPREF)) {
    			int index = traverseAttrGroupRef(child);
    			if (getContentSpec(getElement(index)) == -1) {
					reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
									  new Object [] { "Forward References to attrGroup" });
    			    Vector v = null;
    			    Integer i = new Integer(index);
    			    if ((v = (Vector) fForwardRefs.get(i)) == null)
    			        v = new Vector();
                    v.addElement(new Integer(typeNameIndex));
    			    fForwardRefs.put(i,v);
                    addUse(typeNameIndex, index);
    			} else
        			fElementDeclPool.copyAtts(index, typeNameIndex);
			}
		}
		
        return typeNameIndex;
	}

	private int traverseGroup(Element groupDecl) throws Exception {
		String groupName = groupDecl.getAttribute(ATT_NAME);
		String collection = groupDecl.getAttribute(ATT_COLLECTION);
		String order = groupDecl.getAttribute(ATT_ORDER);
		
		if (groupName.equals("")) { // gensym a unique name
		    groupName = "http://www.apache.org/xml/xerces/internalGroup"+fGroupCount++;
		}
		
		Element child = XUtil.getFirstChildElement(groupDecl);

		int contentSpecType = 0;
		int csnType = 0;
        boolean buildAll = false;
        int allChildren[] = null;
        int allChildCount = 0;
		
		if (order.equals(ATTVAL_CHOICE)) {
			csnType = XMLContentSpecNode.CONTENTSPECNODE_CHOICE;
			contentSpecType = fStringPool.addSymbol("CHILDREN");
		} else if (order.equals(ATTVAL_SEQ)) {
			csnType = XMLContentSpecNode.CONTENTSPECNODE_SEQ;
			contentSpecType = fStringPool.addSymbol("CHILDREN");
		} else if (order.equals(ATTVAL_ALL)) {
            buildAll = true;
            allChildren = new int[((org.apache.xerces.dom.NodeImpl)groupDecl).getLength()];
            allChildCount = 0;
		}
		int left = -2;
		int right = -2;
		boolean hadContent = false;
		int groupIndices[] = new int [((org.apache.xerces.dom.NodeImpl)groupDecl).getLength()];
		int numGroups = 0;

		for (;
			 child != null;
			 child = XUtil.getNextSiblingElement(child)) {
			int index = -2;
            hadContent = true;
			String childName = child.getNodeName();
			if (childName.equals(ELT_ELEMENTDECL)) {
			    if (child.getAttribute(ATT_REF).equals(""))
					reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
									  new Object [] { "Nesting element declarations" });
			    else
    			    index = traverseElementRef(child);
			} else if (childName.equals(ELT_GROUP)) {
			    if (!buildAll) {
    			    int groupNameIndex = traverseGroup(child);
	    			groupIndices[numGroups++] = groupNameIndex;
		    		index = getContentSpec(getElement(groupNameIndex));
		    	} else
					reportSchemaError(SchemaMessageProvider.OrderIsAll,
									  new Object [] { "group" } );
			} else if (childName.equals(ELT_MODELGROUPREF)) {
			    if (!buildAll) {
                    int modelGroupNameIndex = traverseModelGroupRef(child);
                    index = getContentSpec(getElement(modelGroupNameIndex));
                    index = expandContentModel(index, child);
                } else
					reportSchemaError(SchemaMessageProvider.OrderIsAll,
									  new Object [] { "modelGroupRef" });
			} else {
				reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
								  new Object [] { "group", childName });
			}
			if (buildAll) {
			    allChildren[allChildCount++] = index;
			} else if (left == -2) {
				left = index;
			} else if (right == -2) {
				right = index;
			} else {
   				left = fElementDeclPool.addContentSpecNode(csnType, left, right, false);
    			right = index;
   			}
		}
		if (buildAll) {
		    left = buildAllModel(allChildren,allChildCount);
		} else {
			if (hadContent && right != -2)
				left = fElementDeclPool.addContentSpecNode(csnType, left, right, false);
		}
		left = expandContentModel(left, groupDecl);
	
		// stick in ElementDeclPool as a hack
		int groupNameIndex = fStringPool.addSymbol(groupName); //REVISIT namespace clashes possible
		int groupIndex = fElementDeclPool.addElementDecl(groupNameIndex, contentSpecType, left, false);

        return groupNameIndex;
	}

	private int traverseModelGroup(Element modelGroupDecl) throws Exception {
		String modelGroupName = modelGroupDecl.getAttribute(ATT_NAME);
		String order = modelGroupDecl.getAttribute(ATT_ORDER);
		
		if (modelGroupName.equals("")) { // gensym a unique name
		    modelGroupName = "http://www.apache.org/xml/xerces/internalModelGroup"+fModelGroupCount++;
		}
		
		Element child = XUtil.getFirstChildElement(modelGroupDecl);

		int contentSpecType = 0;
		int csnType = 0;
        boolean buildAll = false;
        int allChildren[] = null;
        int allChildCount = 0;
		
		if (order.equals(ATTVAL_CHOICE)) {
			csnType = XMLContentSpecNode.CONTENTSPECNODE_CHOICE;
			contentSpecType = fStringPool.addSymbol("CHILDREN");
		} else if (order.equals(ATTVAL_SEQ)) {
			csnType = XMLContentSpecNode.CONTENTSPECNODE_SEQ;
			contentSpecType = fStringPool.addSymbol("CHILDREN");
		} else if (order.equals(ATTVAL_ALL)) {
			buildAll = true;
            allChildren = new int[((org.apache.xerces.dom.NodeImpl)modelGroupDecl).getLength()];
            allChildCount = 0;
		}
		int left = -2;
		int right = -2;
		boolean hadContent = false;

		for (;
			 child != null;
			 child = XUtil.getNextSiblingElement(child)) {
			int index = -2;
            hadContent = true;
			String childName = child.getNodeName();
			if (childName.equals(ELT_ELEMENTDECL)) {
			    if (child.getAttribute(ATT_REF).equals(""))
					reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
									  new Object [] { "Nesting element declarations" });
			    else {
    			    index = traverseElementRef(child);
                }
			} else if (childName.equals(ELT_GROUP)) {
			    int groupNameIndex = traverseGroup(child);
				index = getContentSpec(getElement(groupNameIndex));
			} else if (childName.equals(ELT_MODELGROUPREF)) {
                int modelGroupNameIndex = traverseModelGroupRef(child);
                index = getContentSpec(getElement(modelGroupNameIndex));
                index = expandContentModel(index, child);
			} else {
				reportSchemaError(SchemaMessageProvider.GroupContentRestricted,
								  new Object [] { "modelGroup", childName });
			}
			if (buildAll) {
			    allChildren[allChildCount++] = index;
			} else if (left == -2) {
				left = index;
			} else if (right == -2) {
				right = index;
			} else {
   				left = fElementDeclPool.addContentSpecNode(csnType, left, right, false);
    			right = index;
   			}
		}
		if (buildAll) {
		    left = buildAllModel(allChildren,allChildCount);
		} else {
			if (hadContent && right != -2)
				left = fElementDeclPool.addContentSpecNode(csnType, left, right, false);
		}

		left = expandContentModel(left, modelGroupDecl);

		// stick in ElementDeclPool as a hack
		int modelGroupNameIndex = fStringPool.addSymbol(modelGroupName); //REVISIT namespace clashes possible
		int modelGroupIndex = fElementDeclPool.addElementDecl(modelGroupNameIndex, contentSpecType, left, false);

        return modelGroupNameIndex;
	}

	private int traverseModelGroupRef(Element modelGroupRef) {
	    String name = modelGroupRef.getAttribute(ATT_NAME);
	    int index = fStringPool.addSymbol(name);
//	    if (getContentSpec(getElement(index)) == -1) fElementDeclPool.setContentSpec(index, -2);
        return index;
	}

	public int traverseDatatypeDecl(Element datatypeDecl) {
		int newTypeName = fStringPool.addSymbol(datatypeDecl.getAttribute(ATT_NAME));
		int export = fStringPool.addSymbol(datatypeDecl.getAttribute(ATT_EXPORT));

		Element datatypeChild = XUtil.getFirstChildElement(datatypeDecl);
		int basetype = fStringPool.addSymbol(datatypeChild.getNodeName());
		// check that base type is defined
		//REVISIT: how do we do the extension mechanism? hardwired type name?
		DatatypeValidator baseValidator = fDatatypeRegistry.getValidatorFor(datatypeChild.getAttribute(ATT_NAME));
		if (baseValidator == null) {
			reportSchemaError(SchemaMessageProvider.UnknownBaseDatatype,
							  new Object [] { datatypeChild.getAttribute(ATT_NAME), datatypeDecl.getAttribute(ATT_NAME) });
			return -1;
		}

		// build facet list
		int numFacets = 0;
		int numEnumerationLiterals = 0;
		Hashtable facetData = new Hashtable();
		Vector enumData = new Vector();

		Node facet = datatypeChild.getNextSibling();
		while (facet != null) {
			if (facet.getNodeType() == Node.ELEMENT_NODE) {
				numFacets++;
				if (facet.getNodeName().equals(DatatypeValidator.ENUMERATION)) {
					Node literal = XUtil.getFirstChildElement(facet);
					while (literal != null) {
						numEnumerationLiterals++;
						enumData.addElement(literal.getFirstChild().getNodeValue());
						literal = XUtil.getNextSiblingElement(literal);
					}
				} else {
					facetData.put(facet.getNodeName(),facet.getFirstChild().getNodeValue());
				}
			}
			facet = facet.getNextSibling();
		}
		if (numEnumerationLiterals > 0) {
			facetData.put(DatatypeValidator.ENUMERATION, enumData);
		}

		// create & register validator for "generated" type if it doesn't exist
		try {
			DatatypeValidator newValidator = (DatatypeValidator) baseValidator.getClass().newInstance();
			if (numFacets > 0)
				newValidator.setFacets(facetData);
			fDatatypeRegistry.addValidator(fStringPool.toString(newTypeName),newValidator);
		} catch (Exception e) {
			reportSchemaError(SchemaMessageProvider.DatatypeError,
							  new Object [] { e.getMessage() });
		}
        return -1;
	}

	private int traverseElementDecl(Element elementDecl) throws Exception {
		int contentSpecType      = -1;
		int contentSpecNodeIndex = -1;
        int typeNameIndex = -1;

		String name = elementDecl.getAttribute(ATT_NAME);
		String ref = elementDecl.getAttribute(ATT_REF);
		String archRef = elementDecl.getAttribute(ATT_ARCHREF);
		String type = elementDecl.getAttribute(ATT_TYPE);
		String schemaAbbrev = elementDecl.getAttribute(ATT_SCHEMAABBREV);
		String schemaName = elementDecl.getAttribute(ATT_SCHEMANAME);
		String minOccurs = elementDecl.getAttribute(ATT_MINOCCURS);
		String maxOccurs = elementDecl.getAttribute(ATT_MAXOCCURS);
		String export = elementDecl.getAttribute(ATT_EXPORT);

        int attrCount = 0;
		if (!ref.equals("")) attrCount++;
		if (!type.equals("")) attrCount++;
		if (!archRef.equals("")) attrCount++;
		//REVISIT top level check for ref & archref
		if (attrCount > 1)
			reportSchemaError(SchemaMessageProvider.OneOfTypeRefArchRef, null);
		
		if (!ref.equals("") || !archRef.equals("")) {
		    if (XUtil.getFirstChildElement(elementDecl) != null)
				reportSchemaError(SchemaMessageProvider.NoContentForRef, null);
		   	int typeName = (!ref.equals("")) ? fStringPool.addSymbol(ref) : fStringPool.addSymbol(archRef);
		   	contentSpecNodeIndex = getContentSpec(getElement(typeName));
		   	contentSpecType = getContentSpecType(getElement(typeName));

		   	int elementNameIndex = fStringPool.addSymbol(name);
            int elementIndex = -1;

		   	if (contentSpecNodeIndex == -1) {
		   	    contentSpecType = XMLContentSpecNode.CONTENTSPECNODE_LEAF;
            	contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_LEAF,
	        							                                   elementNameIndex, -1, false);
                fElementDeclPool.addElementDecl(elementNameIndex, contentSpecType, contentSpecNodeIndex, true);
				reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
								  new Object [] { "Forward references to archetypes" });
    			Vector v = null;
    			Integer i = new Integer(typeName);
    			if ((v = (Vector) fForwardRefs.get(i)) == null)
    			     v = new Vector();
                v.addElement(new Integer(elementNameIndex));
    			fForwardRefs.put(i,v);
    			addUse(elementNameIndex, typeName);
		   	} else {
                fElementDeclPool.addElementDecl(elementNameIndex, contentSpecType, contentSpecNodeIndex, true);
                // copy up attribute decls from type object
                fElementDeclPool.copyAtts(typeName, elementNameIndex);
            }
		    return elementNameIndex;
		}
		
		// element has a single child element, either a datatype or a type, null if primitive
		Element content = XUtil.getFirstChildElement(elementDecl);

		if (content != null) {
			String contentName = content.getNodeName();
			if (contentName.equals(ELT_ARCHETYPEDECL)) {
				typeNameIndex = traverseTypeDecl(content);
				contentSpecNodeIndex = getContentSpec(getElement(typeNameIndex));
				contentSpecType = getContentSpecType(getElement(typeNameIndex));
			} else if (contentName.equals(ELT_DATATYPEDECL)) {
				reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
								  new Object [] { "Nesting datatype declarations" });
				// contentSpecNodeIndex = traverseDatatypeDecl(content);
				// contentSpecType = fStringPool.addSymbol("DATATYPE");
			} else if (!type.equals("")) { // datatype
				contentSpecType = fStringPool.addSymbol("DATATYPE");

				// set content spec node index to leaf
				contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_LEAF,
																		   fStringPool.addSymbol(content.getAttribute(ATT_NAME)),
																		   -1, false);
				// set occurrance count
				contentSpecNodeIndex = expandContentModel(contentSpecNodeIndex, content);
			} else if (type.equals("")) { // "untyped" leaf
			    // untyped leaf element decl
	    		contentSpecType = fStringPool.addSymbol("CHILDREN");

    			// add leaf
				int leftIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_LEAF,
																	fStringPool.addSymbol(content.getAttribute(ATT_NAME)),
																	-1, false);

    			// set occurrence count
	    		contentSpecNodeIndex = expandContentModel(contentSpecNodeIndex, content);
			} else {
				System.out.println("unhandled case in element decl code");
			}
		} else if (!type.equals("")) { // type specified in attribute, not content
			contentSpecType = fStringPool.addSymbol("DATATYPE");

			// set content spec node index to leaf
			contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_LEAF,
																	   fStringPool.addSymbol(type),
																	   -1, false);
			// set occurrance count
			contentSpecNodeIndex = expandContentModel(contentSpecNodeIndex, elementDecl);
		}

		//
		// Create element decl
		//

		int elementNameIndex     = fStringPool.addSymbol(elementDecl.getAttribute(ATT_NAME));

		// add element decl to pool
		int elementIndex = fElementDeclPool.addElementDecl(elementNameIndex, contentSpecType, contentSpecNodeIndex, true);
//        System.out.println("elementIndex:"+elementIndex+" "+elementDecl.getAttribute(ATT_NAME)+" eltType:"+elementName+" contentSpecType:"+contentSpecType+
//                           " SpecNodeIndex:"+ contentSpecNodeIndex);

        // copy up attribute decls from type object
        fElementDeclPool.copyAtts(typeNameIndex, elementNameIndex);

        return elementNameIndex;
	}

    private int traverseElementRef(Element elementRef) {
        String elementName = elementRef.getAttribute(ATT_REF);
        int elementTypeIndex = fStringPool.addSymbol(elementName);
        int contentSpecNodeIndex = 0;
        try {
        	contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_LEAF,
	    							                                   elementTypeIndex, -1, false);
            contentSpecNodeIndex = expandContentModel(contentSpecNodeIndex, elementRef);
        } catch (Exception e) {
            //REVISIT: integrate w/ error handling
            e.printStackTrace();
        }
        return contentSpecNodeIndex;
    }

	//REVISIT: elementIndex API is ugly
	private void traverseAttributeDecl(Element attrDecl, int elementIndex) throws Exception {
		// attribute name
		int attName = fStringPool.addSymbol(attrDecl.getAttribute(ATT_NAME));

		// attribute type
		int attType = -1;
		int enumeration = -1;
		String datatype = attrDecl.getAttribute(ATT_TYPE);
		if (datatype.equals("")) {
			attType = fStringPool.addSymbol("CDATA");
		} else {
			if (datatype.equals("string")) {
				attType = fStringPool.addSymbol("CDATA");
			} else if (datatype.equals("ID")) {
				attType = fStringPool.addSymbol("ID");
			} else if (datatype.equals("IDREF")) {
				attType = fStringPool.addSymbol("IDREF");
			} else if (datatype.equals("IDREFS")) {
				attType = fStringPool.addSymbol("IDREFS");
			} else if (datatype.equals("ENTITY")) {
				attType = fStringPool.addSymbol("ENTITY");
			} else if (datatype.equals("ENTITIES")) {
				attType = fStringPool.addSymbol("ENTITIES");
			} else if (datatype.equals("NMTOKEN")) {
				Element e = XUtil.getFirstChildElement(attrDecl, "enumeration");
				if (e == null) {
					attType = fStringPool.addSymbol("NMTOKEN");
				} else {
					attType = fStringPool.addSymbol("ENUMERATION");
					enumeration = fStringPool.startStringList();
					for (Element literal = XUtil.getFirstChildElement(e, "literal");
						 literal != null;
						 literal = XUtil.getNextSiblingElement(literal, "literal")) {
			    		int stringIndex = fStringPool.addSymbol(literal.getFirstChild().getNodeValue());
						fStringPool.addStringToList(enumeration, stringIndex);
					}
					fStringPool.finishStringList(enumeration);
				}
			} else if (datatype.equals("NMTOKENS")) {
				attType = fStringPool.addSymbol("NMTOKENS");
			} else if (datatype.equals(ELT_NOTATIONDECL)) {
				attType = fStringPool.addSymbol("NOTATION");
			} else { // REVISIT: Danger: assuming all other ATTR types are datatypes
				//REVISIT check against list of validators to ensure valid type name
				attType = fStringPool.addSymbol("DATATYPE");
				enumeration = fStringPool.addSymbol(datatype);
			}
		}

		// attribute default type
		int attDefaultType = -1;
		int attDefaultValue = -1;
		boolean required = attrDecl.getAttribute("required").equals("true");
		if (required) {
			attDefaultType = fStringPool.addSymbol("#REQUIRED");
		} else {
			String fixed = attrDecl.getAttribute(ATT_FIXED);
			if (!fixed.equals("")) {
				attDefaultType = fStringPool.addSymbol("#FIXED");
				attDefaultValue = fStringPool.addString(fixed);
			} else {
				// attribute default value
				String defaultValue = attrDecl.getAttribute(ATT_DEFAULT);
				if (!defaultValue.equals("")) {
					attDefaultType = fStringPool.addSymbol("");
					attDefaultValue = fStringPool.addString(defaultValue);
				} else {
					attDefaultType = fStringPool.addSymbol("#IMPLIED");
				}
			}
			if (attType == fStringPool.addSymbol("DATATYPE") && attDefaultValue != -1) {
        		try { // REVISIT - integrate w/ error handling
                    String type = fStringPool.toString(enumeration);
                    DatatypeValidator v = fDatatypeRegistry.getValidatorFor(type);
                    if (v != null)
                        v.validate(fStringPool.toString(attDefaultValue));
                    else
						reportSchemaError(SchemaMessageProvider.NoValidatorFor,
										  new Object [] { type });
                } catch (InvalidDatatypeValueException idve) {
					reportSchemaError(SchemaMessageProvider.IncorrectDefaultType,
									  new Object [] { attrDecl.getAttribute(ATT_NAME), idve.getMessage() });
                } catch (Exception e) {
                    e.printStackTrace();
                    System.out.println("Internal error in attribute datatype validation");
                }
            }
		}

		// add attribute to element decl pool
		fElementDeclPool.addAttDef(elementIndex, attName, attType, enumeration, attDefaultType, attDefaultValue, true, true, true);
	}

	private int traverseAttrGroup(Element attrGroupDecl) throws Exception {

		String attrGroupName = attrGroupDecl.getAttribute(ATT_NAME);
		
		if (attrGroupName.equals("")) { // gensym a unique name
		    attrGroupName = "http://www.apache.org/xml/xerces/internalGroup"+fGroupCount++;
		}
		
		Element child = XUtil.getFirstChildElement(attrGroupDecl);

		int groupIndices[] = new int [((org.apache.xerces.dom.NodeImpl)attrGroupDecl).getLength()];
		int numGroups = 0;

		for (;
			 child != null;
			 child = XUtil.getNextSiblingElement(child)) {
			String childName = child.getNodeName();
			if (childName.equals(ELT_ATTRGROUPREF)) {
			    groupIndices[numGroups++] = traverseAttrGroupRef(child);
			    if (getContentSpec(getElement(groupIndices[numGroups-1])) == -1) {
					reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
									  new Object [] { "Forward reference to AttrGroup" });
			    }
			} else if (childName.equals(ELT_ATTRIBUTEDECL)) {
                continue;
   			} else {
				reportSchemaError(SchemaMessageProvider.IllegalAttContent,
								  new Object [] { childName });
   			}
		}
	
		// stick in ElementDeclPool as a hack
		int attrGroupNameIndex = fStringPool.addSymbol(attrGroupName); //REVISIT namespace clashes possible
		int attrGroupIndex = fElementDeclPool.addElementDecl(attrGroupNameIndex, 0, 0, false);
//        System.out.println("elementIndex:"+groupIndex+" "+groupName+" eltType:"+groupNameIndex+" SpecType:"+contentSpecType+
//                           " SpecNodeIndex:"+ left);

		// (attribute | attrGroupRef)*
		for (child = XUtil.getFirstChildElement(attrGroupDecl);  // start from the beginning to just do attrs
			 child != null;
			 child = XUtil.getNextSiblingElement(child)) {
			String childName = child.getNodeName();
			if (childName.equals(ELT_ATTRIBUTEDECL)) {
				traverseAttributeDecl(child, attrGroupIndex);
			} else if (childName.equals(ELT_ATTRGROUPDECL)) {
    			int index = traverseAttrGroupRef(child);
    			if (getContentSpec(getElement(index)) == -1) {
					reportSchemaError(SchemaMessageProvider.FeatureUnsupported,
									  new Object [] { "Forward reference to AttrGroup" });
    			    Vector v = null;
    			    Integer i = new Integer(index);
    			    if ((v = (Vector) fForwardRefs.get(i)) == null)
    			        v = new Vector();
                    v.addElement(new Integer(attrGroupNameIndex));
    			    fForwardRefs.put(i,v);
    			    addUse(attrGroupNameIndex, index);
    			} else
    			    groupIndices[numGroups++] = getContentSpec(getElement(index));
			}
		}
		
        // copy up attribute decls from nested groups
		for (int i = 0; i < numGroups; i++) {
            fElementDeclPool.copyAtts(groupIndices[i], attrGroupNameIndex);
        }

        return attrGroupNameIndex;
	}

	private int traverseAttrGroupRef(Element attrGroupRef) {
	    String name = attrGroupRef.getAttribute(ATT_NAME);
	    int index = fStringPool.addSymbol(name);
        return index;
	}
	
	private void addUse(int def, int use) {
        addUse(def, new Integer(use));
	}

	private void addUse(int def, Integer use) {
        Vector v = (Vector) fAttrGroupUses.get(new Integer(def));
        if (v == null) v = new Vector();
    		 v.addElement(use);
	}

    /** builds the all content model */
    private int buildAllModel(int children[], int count) throws Exception {

        // build all model
        if (count > 1) {

            // create and initialize singletons
            XMLContentSpecNode choice = new XMLContentSpecNode();

            choice.type = XMLContentSpecNode.CONTENTSPECNODE_CHOICE;
            choice.value = -1;
            choice.otherValue = -1;

            // build all model
            sort(children, 0, count);
            int index = buildAllModel(children, 0, choice);

            return index;
        }

        if (count > 0) {
            return children[0];
        }

        return -1;
    }

    /** Builds the all model. */
    private int buildAllModel(int src[], int offset,
                              XMLContentSpecNode choice) throws Exception {

        // swap last two places
        if (src.length - offset == 2) {
            int seqIndex = createSeq(src);
            if (choice.value == -1) {
                choice.value = seqIndex;
            }
            else {
                if (choice.otherValue != -1) {
                    choice.value = fElementDeclPool.addContentSpecNode(choice.type, choice.value, choice.otherValue, false);
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
                    choice.value = fElementDeclPool.addContentSpecNode(choice.type, choice.value, choice.otherValue, false);
                }
                choice.otherValue = seqIndex;
            }
            return fElementDeclPool.addContentSpecNode(choice.type, choice.value, choice.otherValue, false);
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
            left = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                       left, right, false);
            right = src[i];
        }

        return fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
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

    /***
    private void print(int indexes[], int offset, boolean mark) {

        for (int i = 0; i < indexes.length; i++) {
            System.out.print(offset==i?'.':' ');
            System.out.print(indexes[i]);
        }
        if (mark) {
            System.out.print(" *");
        }
        System.out.println();

    } // print(int[],int,boolean)
    /***/

    /** Builds the children content model. */
/*    private int buildChildrenModel(Element model, int type) throws Exception {

        // is there anything to do?
        if (model == null) {
            return -1;
        }

        // fill parent node
        int parentValue = -1;
        int parentOtherValue = -1;

        // build content model bottom-up
        int index = -1;
        for (Element child = XUtil.getFirstChildElement(model);
             child != null;
             child = XUtil.getNextSiblingElement(child)) {

            //
            // leaf
            //

            String childName = child.getNodeName();
            if (childName.equals("elementTypeRef")) {

                // add element name to symbol table
                String elementType = child.getAttribute(ATT_NAME);
                int elementTypeIndex = fStringPool.addSymbol(elementType);

                // create leaf node
                index = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_LEAF,
                                                            elementTypeIndex, -1, false);

                // set occurrence count
                index = expandContentModel(index, child);

            }

            //
            // all
            //

            else if (childName.equals(ATTVAL_ALL)) {

                index = buildAllModel(child);

            }

            //
            // choice or sequence
            //

            else {
                int childType = childName.equals(ATTVAL_CHOICE)
                              ? XMLContentSpecNode.CONTENTSPECNODE_CHOICE
                              : XMLContentSpecNode.CONTENTSPECNODE_SEQ;
                index = buildChildrenModel(child, childType);
            }

            // add to parent node
            if (parentValue == -1) {
                parentValue = index;
            }
            else if (parentOtherValue == -1) {
                parentOtherValue = index;
            }
            else {
                parentValue = fElementDeclPool.addContentSpecNode(type, parentValue, parentOtherValue, false);
                parentOtherValue = index;
            }

        } // for all children

        // set model type
        index = fElementDeclPool.addContentSpecNode(type, parentValue, parentOtherValue, false);

        // set occurrence count
        index = expandContentModel(index, model);

        // return last content spec node
        return index;

    } // buildChildrenModel(Element,int):int
*/
    private int expandContentModel(int contentSpecNodeIndex, Element element) throws Exception {

        // set occurrence count
        int occurs = getOccurrenceCount(element);
        int m = 1, n = 1;
        if (!isSimpleOccurrenceCount(occurs)) {
            try { m = Integer.parseInt(element.getAttribute(ATT_MINOCCURS)); }
            catch (NumberFormatException e) {
				reportSchemaError(SchemaMessageProvider.ValueNotInteger,
								  new Object [] { ATT_MINOCCURS });
			}
            try { n = Integer.parseInt(element.getAttribute(ATT_MAXOCCURS)); }
            catch (NumberFormatException e) {
				reportSchemaError(SchemaMessageProvider.ValueNotInteger,
								  new Object [] { ATT_MAXOCCURS });
			}
        }

		switch (occurs) {

            //
            // +
            //

            case XMLContentSpecNode.CONTENTSPECNODE_ONE_OR_MORE: {
                //System.out.println("occurs = +");
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_ONE_OR_MORE,
                                                            contentSpecNodeIndex, -1, false);
                break;
            }

            //
            // *
            //

            case XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE: {
                //System.out.println("occurs = *");
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE,
                                                            contentSpecNodeIndex, -1, false);
                break;
            }

            //
            // ?
            //

            case XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE: {
                //System.out.println("occurs = ?");
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE,
                                                            contentSpecNodeIndex, -1, false);
                break;
            }

            //
            // M -> *
            //

            case CONTENTSPECNODE_M_OR_MORE: {
                //System.out.println("occurs = "+m+" -> *");

                // create sequence node
                int value = contentSpecNodeIndex;
                int otherValue = -1;

                // add required number
                for (int i = 1; i < m; i++) {
                    if (otherValue != -1) {
                        value = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                                    value, otherValue, false);
                    }
                    otherValue = contentSpecNodeIndex;
                }

                // create optional content model node
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE,
                                                            contentSpecNodeIndex, -1, false);

                // add optional part
                if (otherValue != -1) {
                    value = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                                value, otherValue, false);
                }
                otherValue = contentSpecNodeIndex;

                // set expanded content model index
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                            value, otherValue, false);
                break;
            }

            //
            // M -> N
            //

            case CONTENTSPECNODE_M_TO_N: {
                //System.out.println("occurs = "+m+" -> "+n);

                // create sequence node
                int value = contentSpecNodeIndex;
                int otherValue = -1;

                // add required number
                for (int i = 1; i < m; i++) {
                    if (otherValue != -1) {
                        value = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                                    value, otherValue, false);
                    }
                    otherValue = contentSpecNodeIndex;
                }

                // create optional content model node
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE,
                                                            contentSpecNodeIndex, -1, false);

                // add optional number
                for (int i = n; i > m; i--) {
                    if (otherValue != -1) {
                        value = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                                        value, otherValue, false);
                    }
                    otherValue = contentSpecNodeIndex;
                }

                // set expanded content model index
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                            value, otherValue, false);
                break;
            }

            //
            // 0 -> N
            //

            case CONTENTSPECNODE_ZERO_TO_N: {
                //System.out.println("occurs = 0 -> "+n);

                // create optional content model node
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE,
                                                            contentSpecNodeIndex, -1, false);

                int value = contentSpecNodeIndex;
                int otherValue = -1;

                // add optional number
                for (int i = 1; i < n; i++) {
                    if (otherValue != -1) {
                        value = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                                    value, otherValue, false);
                    }
                    otherValue = contentSpecNodeIndex;
                }

                // set expanded content model index
                contentSpecNodeIndex = fElementDeclPool.addContentSpecNode(XMLContentSpecNode.CONTENTSPECNODE_SEQ,
                                                            value, otherValue, false);
                break;
            }

        } // switch

        //System.out.println("content = "+getContentSpecNodeAsString(contentSpecNodeIndex));
        return contentSpecNodeIndex;

    } // expandContentModel(int,int,int,int):int

    private boolean isSimpleOccurrenceCount(int occurs) {
        return occurs == -1 ||
               occurs == XMLContentSpecNode.CONTENTSPECNODE_ONE_OR_MORE ||
               occurs == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE ||
               occurs == XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE;
    }

    private int getOccurrenceCount(Element element) {

        String minOccur = element.getAttribute(ATT_MINOCCURS);
        String maxOccur = element.getAttribute(ATT_MAXOCCURS);

        if (minOccur.equals("0")) {
            if (maxOccur.equals("1") || maxOccur.length() == 0) {
                return XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_ONE;
            }
            else if (maxOccur.equals("*")) {
                return XMLContentSpecNode.CONTENTSPECNODE_ZERO_OR_MORE;
            }
            else {
                return CONTENTSPECNODE_ZERO_TO_N;
            }
        }
        else if (minOccur.equals("1") || minOccur.length() == 0) {
            if (maxOccur.equals("*")) {
                return XMLContentSpecNode.CONTENTSPECNODE_ONE_OR_MORE;
            }
            else if (!maxOccur.equals("1") && maxOccur.length() > 0) {
                return CONTENTSPECNODE_M_TO_N;
            }
        }
        else {
            if (maxOccur.equals("*")) {
                return CONTENTSPECNODE_M_OR_MORE;
            }
            else {
                return CONTENTSPECNODE_M_TO_N;
            }
        }

        // exactly one
        return -1;
    }

	private void reportSchemaError(int major, Object args[]) {
	    try {
    		fErrorReporter.reportError(fErrorReporter.getLocator(),
	    							   SchemaMessageProvider.SCHEMA_DOMAIN,
		    						   major,
			    					   SchemaMessageProvider.MSG_NONE,
				    				   args,
					    			   XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
		} catch (Exception e) {
		    e.printStackTrace();
		}
	}

    //
    // Classes
    //

    static class Resolver implements EntityResolver {

        private static final String SYSTEM[] = {
            "http://www.w3.org/XML/Group/1999/09/23-xmlschema/structures/structures.dtd",
            "http://www.w3.org/XML/Group/1999/09/23-xmlschema/datatypes/datatypes.dtd",
            };
        private static final String PATH[] = {
            "structures.dtd",
            "datatypes.dtd",
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

    class DatatypeValidatorRegistry {
        Hashtable fRegistry = new Hashtable();

        String integerSubtypeTable[][] = {
            { "non-negative-integer", DatatypeValidator.MININCLUSIVE , "0"},
            { "postive-integer", DatatypeValidator.MININCLUSIVE, "1"},
            { "non-positive-integer", DatatypeValidator.MAXINCLUSIVE, "0"},
            { "negative-integer", DatatypeValidator.MAXINCLUSIVE, "-1"}
        };

        void initializeRegistry() {
            Hashtable facets = null;
            fRegistry.put("boolean", new BooleanValidator());
            DatatypeValidator integerValidator = new IntegerValidator();
            fRegistry.put("integer", integerValidator);
            fRegistry.put("string", new StringValidator());
            fRegistry.put("decimal", new DecimalValidator());
            fRegistry.put("float", new FloatValidator());
            fRegistry.put("double", new DoubleValidator());
            //REVISIT - enable the below
            //fRegistry.put("binary", new BinaryValidator());
            //fRegistry.put("date", new DateValidator());
            //fRegistry.put("timePeriod", new TimePeriodValidator());
            //fRegistry.put("time", new TimeValidator());
            //fRegistry.put("uri", new URIValidator());

            DatatypeValidator v = null;
            for (int i = 0; i < integerSubtypeTable.length; i++) {
                v = new IntegerValidator();
                facets = new Hashtable();
                facets.put(integerSubtypeTable[i][1],integerSubtypeTable[i][2]);
                v.setBasetype(integerValidator);
                try {
                    v.setFacets(facets);
                } catch (IllegalFacetException ife) {
                    System.out.println("Internal error initializing registry - Illegal facet: "+integerSubtypeTable[i][0]);
                } catch (IllegalFacetValueException ifve) {
                    System.out.println("Internal error initializing registry - Illegal facet value: "+integerSubtypeTable[i][0]);
                } catch (UnknownFacetException ufe) {
                    System.out.println("Internal error initializing registry - Unknown facet: "+integerSubtypeTable[i][0]);
                }
                fRegistry.put(integerSubtypeTable[0], v);
            }
        }

        DatatypeValidator getValidatorFor(String type) {
            return (DatatypeValidator) fRegistry.get(type);
        }

        void addValidator(String name, DatatypeValidator v) {
            fRegistry.put(name,v);
        }
    }
}