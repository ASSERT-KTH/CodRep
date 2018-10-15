QName name = ((SchemaGrammar.OneSubGroup)substitutionGroupQNames.elementAt(i)).name;


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

import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.validators.common.GrammarResolver;
import org.apache.xerces.validators.common.XMLElementDecl;
import org.apache.xerces.validators.datatype.DatatypeValidator;

import org.xml.sax.SAXException;
import org.apache.xerces.framework.XMLErrorReporter;
import org.apache.xerces.utils.XMLMessages;

import java.lang.ClassCastException;
import java.util.Vector;

/*
 * @version 1.0.  ericye, neilg
 *
  * Modified by neilg, 01/18/01
  * Note:  this class, formerly called equivClassComparator.java, has
  * been renamed to comply with schema CR changes.  It still contains
  * some outmoded terminology--such as use of the term "exemplar", now
  * referred to as the head of the substitution group.  I have
  * changed as much terminology as possible, but I thought future
  * maintainers could deal with simple and not necessarily-ill-named
  * concepts like exemplar.
 */

public class SubstitutionGroupComparator {

    // constants
    private final int TOP_LEVEL_SCOPE = -1;

    // private data members
    private StringPool fStringPool = null;
    private GrammarResolver fGrammarResolver = null;
    private XMLErrorReporter fErrorReporter = null;

    // constructors
    private SubstitutionGroupComparator(){
        // can never be instantiated without passing in a GrammarResolver.
    }
    public  SubstitutionGroupComparator(GrammarResolver grammarResolver, StringPool stringPool, XMLErrorReporter errorReporter){
        fGrammarResolver = grammarResolver;
        fStringPool = stringPool;
        fErrorReporter = errorReporter;
    }

    //public methods
    public boolean isEquivalentTo(QName anElement, QName exemplar) throws Exception{
        if (anElement.localpart==exemplar.localpart && anElement.uri==exemplar.uri ) {
            return true; // they're the same!
        }

        if (fGrammarResolver == null || fStringPool == null) {
            throw new SAXException("Internal error; tried to check an element against a substitutionGroup, but no GrammarResolver is defined");
        }

        // ??? TODO: first try to use
        // sGrammar.getElementDeclAllSubstitutionGroupQNames();
        // which should save lots of time

        int uriIndex = anElement.uri;
        int localpartIndex = anElement.localpart;
        String uri = fStringPool.toString(anElement.uri);
        String localpart = fStringPool.toString(anElement.localpart);

        // In addition to simply trying to find a chain between anElement and exemplar,
        // we need to make sure that no steps in the chain are blocked.
        // That is, at every step, we need to make sure that the element
        // being substituted for will permit being substituted
        // for, and whether the type of the element will permit derivations in
        // instance documents of this sort.
        if(uri==null) {
            return false;
        }
        SchemaGrammar sGrammar = null;
        try {
            sGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uri);
        }
        catch ( ClassCastException ce) {
            //since the return Grammar is not a SchemaGrammar, bail out
            String er = "Grammar with URI " + uri + " is not a schema grammar!";
            Object [] a = {er};
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                    XMLMessages.XML_DOMAIN,
                    XMLMessages.MSG_GENERIC_SCHEMA_ERROR,
                    XMLMessages.SCHEMA_GENERIC_ERROR,
                    a, XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
            return false;
        }
        if(sGrammar == null) {
            return false;
        }

        // this will be the index of anElement
        int elementIndex = sGrammar.getElementDeclIndex(uriIndex, localpartIndex, TOP_LEVEL_SCOPE);
        int anElementIndex = elementIndex;

        String substitutionGroupFullName = sGrammar.getElementDeclSubstitutionGroupAffFullName(elementIndex);
        boolean foundIt = false;
        while (substitutionGroupFullName != null) {
            int commaAt = substitutionGroupFullName.indexOf(",");
            uri = "";
            localpart = substitutionGroupFullName;
            if (  commaAt >= 0  ) {
                if (commaAt > 0 ) {
                    uri = substitutionGroupFullName.substring(0,commaAt);
                }
                localpart = substitutionGroupFullName.substring(commaAt+1);
            }
            if(uri==null) {
                return false;
            }
            try {
                sGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uri);
            }
            catch ( ClassCastException ce) {
                //since the return Grammar is not a SchemaGrammar, bail out
                String er = "Grammar with URI " + uri + " is not a schema grammar!";
                Object [] a = {er};
                fErrorReporter.reportError(fErrorReporter.getLocator(),
                     XMLMessages.XML_DOMAIN,
                     XMLMessages.MSG_GENERIC_SCHEMA_ERROR,
                     XMLMessages.SCHEMA_GENERIC_ERROR,
                     a, XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
                return false;
            }
            if(sGrammar == null) {
                return false;
            }
            uriIndex = fStringPool.addSymbol(uri);
            localpartIndex = fStringPool.addSymbol(localpart);
            elementIndex = sGrammar.getElementDeclIndex(uriIndex, localpartIndex, TOP_LEVEL_SCOPE);
            if (elementIndex == -1) {
                return false;
            }

            if (uriIndex == exemplar.uri && localpartIndex == exemplar.localpart) {
                // time to check for block value on element
                if((sGrammar.getElementDeclBlockSet(elementIndex) & SchemaSymbols.SUBSTITUTION) != 0) {
                    return false;
                }
                foundIt = true;
                break;
            }

            substitutionGroupFullName = sGrammar.getElementDeclSubstitutionGroupAffFullName(elementIndex);

        }

        if (!foundIt) {
            return false;
        }
        // this will contain anElement's complexType information.
        TraverseSchema.ComplexTypeInfo aComplexType = sGrammar.getElementComplexTypeInfo(anElementIndex);
        // elementIndex contains the index of the substitutionGroup head
        int exemplarBlockSet = sGrammar.getElementDeclBlockSet(elementIndex);
        if(aComplexType == null) {
            // check on simpleType case
            XMLElementDecl anElementDecl = new XMLElementDecl();
            sGrammar.getElementDecl(anElementIndex, anElementDecl);
            DatatypeValidator anElementDV = anElementDecl.datatypeValidator;
            XMLElementDecl exemplarDecl = new XMLElementDecl();
            sGrammar.getElementDecl(elementIndex, exemplarDecl);
            DatatypeValidator exemplarDV = exemplarDecl.datatypeValidator;
            return((anElementDV == null) ||
                ((anElementDV == exemplarDV) ||
                ((exemplarBlockSet & SchemaSymbols.RESTRICTION) == 0)));
        }
        // now we have to make sure there are no blocks on the complexTypes that this is based upon
        int anElementDerivationMethod = aComplexType.derivedBy;
        if((anElementDerivationMethod & exemplarBlockSet) != 0) return false;
        // this will contain exemplar's complexType information.
        TraverseSchema.ComplexTypeInfo exemplarComplexType = sGrammar.getElementComplexTypeInfo(elementIndex);
        for(TraverseSchema.ComplexTypeInfo tempType = aComplexType;
                tempType != null && tempType != exemplarComplexType;
                tempType = tempType.baseComplexTypeInfo) {
            if((tempType.blockSet & anElementDerivationMethod) != 0) {
                return false;
            }
        }
        return true;
    }

    /**
     * check whether one element or any element in its substitution group
     * is allowed by a given wildcard uri
     *
     * @param element  the QName of a given element
     * @param wuri     the uri of the wildcard
     * @param wother   whether the uri is from ##other, so wuri is excluded
     *
     * @return whether the element is allowed by the wildcard
     */
    public boolean isAllowedByWildcard(QName element, int wuri, boolean wother) throws Exception{
        // whether the uri is allowed directly by the wildcard
        if (!wother && element.uri == wuri ||
            //wother && element.uri != wuri && element.uri != fStringPool.EMPTY_STRING) { // ??? TODO
            wother && element.uri != wuri) {
            return true;
        }

        if (fGrammarResolver == null || fStringPool == null) {
            throw new SAXException("Internal error; tried to check an element against a substitutionGroup, but no GrammarResolver is defined");
        }

        // get the corresponding grammar
        String uri = fStringPool.toString(element.uri);
        if(uri==null)
            return false;
        SchemaGrammar sGrammar = null;
        try {
            sGrammar = (SchemaGrammar) fGrammarResolver.getGrammar(uri);
        }
        catch ( ClassCastException ce) {
            //since the return Grammar is not a SchemaGrammar, bail out
            String er = "Grammar with URI " + uri + " is not a schema grammar!";
            Object [] a = {er};
            fErrorReporter.reportError(fErrorReporter.getLocator(),
                    XMLMessages.XML_DOMAIN,
                    XMLMessages.MSG_GENERIC_SCHEMA_ERROR,
                    XMLMessages.SCHEMA_GENERIC_ERROR,
                    a, XMLErrorReporter.ERRORTYPE_RECOVERABLE_ERROR);
            return false;
        }
        if(sGrammar == null)
            return false;

        // then get the element decl index for the element
        int elementIndex = sGrammar.getElementDeclIndex(element, TOP_LEVEL_SCOPE);

        // get all elements that can substitute the current element
        Vector substitutionGroupQNames = sGrammar.getElementDeclAllSubstitutionGroupQNames(elementIndex, fGrammarResolver, fStringPool);

        // then check whether there exists one elemet that is allowed by the wildcard
        int size = substitutionGroupQNames == null ? 0 : substitutionGroupQNames.size();
        for (int i = 0; i < size; i++) {
            QName name = ((SchemaGrammar.OneSubGroup)substitutionGroupQNames.get(i)).name;
            if (!wother && name.uri == wuri ||
                //wother && name.uri != wuri && name.uri != fStringPool.EMPTY_STRING) { // ??? TODO
                wother && name.uri != wuri) {
                return true;
            }
        }

        return false;
    }
}