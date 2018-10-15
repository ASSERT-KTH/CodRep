facets.pattern  = "([a-zA-Z]{1,8})(-[a-zA-Z0-9]{1,8})*";

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2002 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.dv.xs;

import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.dv.XSFacets;
import org.apache.xerces.util.SymbolHash;

/**
 * the factory to create/return built-in schema DVs and create user-defined DVs
 *
 * @author Neeraj Bajaj, Sun Microsystems, inc.
 * @author Sandy Gao, IBM
 *
 * @version $Id$
 */
public class FullDVFactory extends BaseDVFactory {

    static final String URI_SCHEMAFORSCHEMA = "http://www.w3.org/2001/XMLSchema";

    // there are 45 types. 89 is the closest prime number to 45*2=90.
    static SymbolHash fFullTypes = new SymbolHash(89);
    static {
        createBuiltInTypes(fFullTypes);
    }

    /**
     * Get a built-in simple type of the given name
     * REVISIT: its still not decided within the Schema WG how to define the
     *          ur-types and if all simple types should be derived from a
     *          complex type, so as of now we ignore the fact that anySimpleType
     *          is derived from anyType, and pass 'null' as the base of
     *          anySimpleType. It needs to be changed as per the decision taken.
     *
     * @param name  the name of the datatype
     * @return      the datatype validator of the given name
     */
    public XSSimpleType getBuiltInType(String name) {
        return (XSSimpleType)fFullTypes.get(name);
    }

    /**
     * get all built-in simple types, which are stored in a hashtable keyed by
     * the name
     *
     * @return      a hashtable which contains all built-in simple types
     */
    public SymbolHash getBuiltInTypes() {
        return (SymbolHash)fFullTypes.makeClone();
    }

    // create all built-in types
    static void createBuiltInTypes(SymbolHash types) {
        // create base types first
        BaseDVFactory.createBuiltInTypes(types);
        
        // full schema simple type names
        final String DOUBLE            = "double";
        final String DURATION          = "duration";
        final String ENTITY            = "ENTITY";
        final String ENTITIES          = "ENTITIES";
        final String FLOAT             = "float";
        final String HEXBINARY         = "hexBinary";
        final String ID                = "ID";
        final String IDREF             = "IDREF";
        final String IDREFS            = "IDREFS";
        final String NAME              = "Name";
        final String NCNAME            = "NCName";
        final String NMTOKEN           = "NMTOKEN";
        final String NMTOKENS          = "NMTOKENS";
        final String LANGUAGE          = "language";
        final String NORMALIZEDSTRING  = "normalizedString";
        final String NOTATION          = "NOTATION";
        final String QNAME             = "QName";
        final String STRING            = "string";
        final String TOKEN             = "token";

        final XSFacets facets = new XSFacets();

        XSSimpleTypeDecl anySimpleType = XSSimpleTypeDecl.fAnySimpleType;
        XSSimpleTypeDecl stringDV = (XSSimpleTypeDecl)types.get(STRING);

        types.put(FLOAT, new XSSimpleTypeDecl(anySimpleType, FLOAT, XSSimpleTypeDecl.DV_FLOAT, XSSimpleType.ORDERED_TOTAL, true, true, true, true));
        types.put(DOUBLE, new XSSimpleTypeDecl(anySimpleType, DOUBLE, XSSimpleTypeDecl.DV_DOUBLE, XSSimpleType.ORDERED_TOTAL, true, true, true, true));
        types.put(DURATION, new XSSimpleTypeDecl(anySimpleType, DURATION, XSSimpleTypeDecl.DV_DURATION, XSSimpleType.ORDERED_PARTIAL, false, false, false, true));
        types.put(HEXBINARY, new XSSimpleTypeDecl(anySimpleType, HEXBINARY, XSSimpleTypeDecl.DV_HEXBINARY, XSSimpleType.ORDERED_FALSE, false, false, false, true));
        types.put(QNAME, new XSSimpleTypeDecl(anySimpleType, QNAME, XSSimpleTypeDecl.DV_QNAME, XSSimpleType.ORDERED_FALSE, false, false, false, true));
        types.put(NOTATION, new XSSimpleTypeDecl(anySimpleType, NOTATION, XSSimpleTypeDecl.DV_NOTATION, XSSimpleType.ORDERED_FALSE, false, false, false, true));

        facets.whiteSpace =  XSSimpleType.WS_REPLACE;
        XSSimpleTypeDecl normalizedDV = new XSSimpleTypeDecl(stringDV, NORMALIZEDSTRING , URI_SCHEMAFORSCHEMA, (short)0, false);
        normalizedDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0 );
        types.put(NORMALIZEDSTRING, normalizedDV);

        facets.whiteSpace = XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl tokenDV = new XSSimpleTypeDecl(normalizedDV, TOKEN , URI_SCHEMAFORSCHEMA, (short)0, false);
        tokenDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0 );
        types.put(TOKEN, tokenDV);

        facets.whiteSpace = XSSimpleType.WS_COLLAPSE;
        facets.pattern  = "([a-zA-Z]{2}|[iI]-[a-zA-Z]+|[xX]-[a-zA-Z]+)(-[a-zA-Z]+)*";
        XSSimpleTypeDecl languageDV = new XSSimpleTypeDecl(tokenDV, LANGUAGE , URI_SCHEMAFORSCHEMA, (short)0, false);
        languageDV.applyFacets1(facets, (short)(XSSimpleType.FACET_WHITESPACE | XSSimpleType.FACET_PATTERN) ,(short)0);
        types.put(LANGUAGE, languageDV);

        facets.whiteSpace =  XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl nameDV = new XSSimpleTypeDecl(tokenDV, NAME , URI_SCHEMAFORSCHEMA, (short)0, false);
        nameDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0, XSSimpleTypeDecl.SPECIAL_PATTERN_NAME);
        types.put(NAME, nameDV);

        facets.whiteSpace = XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl ncnameDV = new XSSimpleTypeDecl(nameDV, NCNAME , URI_SCHEMAFORSCHEMA, (short)0, false) ;
        ncnameDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0, XSSimpleTypeDecl.SPECIAL_PATTERN_NCNAME);
        types.put(NCNAME, ncnameDV);

        types.put(ID, new XSSimpleTypeDecl(ncnameDV,  ID, XSSimpleTypeDecl.DV_ID, XSSimpleType.ORDERED_FALSE, false, false, false , true));
        XSSimpleTypeDecl idrefDV = new XSSimpleTypeDecl(ncnameDV,  IDREF , XSSimpleTypeDecl.DV_IDREF, XSSimpleType.ORDERED_FALSE, false, false, false, true);
        types.put(IDREF, idrefDV);

        facets.minLength = 1;
        XSSimpleTypeDecl tempDV = new XSSimpleTypeDecl(null, URI_SCHEMAFORSCHEMA, (short)0, idrefDV, true);
        XSSimpleTypeDecl idrefsDV = new XSSimpleTypeDecl(tempDV, IDREFS, URI_SCHEMAFORSCHEMA, (short)0, false);
        idrefsDV.applyFacets1(facets, XSSimpleType.FACET_MINLENGTH, (short)0);
        types.put(IDREFS, idrefsDV);

        XSSimpleTypeDecl entityDV = new XSSimpleTypeDecl(ncnameDV, ENTITY , XSSimpleTypeDecl.DV_ENTITY, XSSimpleType.ORDERED_FALSE, false, false, false, true);
        types.put(ENTITY, entityDV);

        facets.minLength = 1;
        tempDV = new XSSimpleTypeDecl(null, URI_SCHEMAFORSCHEMA, (short)0, entityDV, true);
        XSSimpleTypeDecl entitiesDV = new XSSimpleTypeDecl(tempDV, ENTITIES, URI_SCHEMAFORSCHEMA, (short)0, false);
        entitiesDV.applyFacets1(facets, XSSimpleType.FACET_MINLENGTH, (short)0);
        types.put(ENTITIES, entitiesDV);


        facets.whiteSpace  = XSSimpleType.WS_COLLAPSE;
        XSSimpleTypeDecl nmtokenDV = new XSSimpleTypeDecl(tokenDV, NMTOKEN, URI_SCHEMAFORSCHEMA, (short)0, false);
        nmtokenDV.applyFacets1(facets, XSSimpleType.FACET_WHITESPACE, (short)0, XSSimpleTypeDecl.SPECIAL_PATTERN_NMTOKEN);
        types.put(NMTOKEN, nmtokenDV);

        facets.minLength = 1;
        tempDV = new XSSimpleTypeDecl(null, URI_SCHEMAFORSCHEMA, (short)0, nmtokenDV, true);
        XSSimpleTypeDecl nmtokensDV = new XSSimpleTypeDecl(tempDV, NMTOKENS, URI_SCHEMAFORSCHEMA, (short)0, false);
        nmtokensDV.applyFacets1(facets, XSSimpleType.FACET_MINLENGTH, (short)0);
        types.put(NMTOKENS, nmtokensDV);
    }//createBuiltInTypes(SymbolHash)

}//XFormsDVFactory