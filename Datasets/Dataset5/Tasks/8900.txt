public static void checkIdRefs(Hashtable IDList, Hashtable IDREFList) throws InvalidDatatypeValueException {

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999, 2000 The Apache Software Foundation.  All rights
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

package org.apache.xerces.impl.v2.datatypes;

import java.util.Hashtable;
import java.util.Enumeration;
import java.util.Vector;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.impl.v2.msg.XMLMessages;
import org.apache.xerces.impl.v2.SchemaSymbols;

/**
 * IDREFValidator defines the interface that data type validators must obey.
 * These validators can be supplied by the application writer and may be useful as
 * standalone code as well as plugins to the validator architecture.
 *
 * @author Jeffrey Rodriguez-
 * @author Mark Swinkles - List Validation refactoring
 * @version $Id$
 */
public class IDREFDatatypeValidator extends StringDatatypeValidator {
    private static Object                   fNullValue      = new Object();

    public static final  int                IDREF_VALIDATE  = 0;
    public static final  int                IDREF_CHECKID   = 1;

    public IDREFDatatypeValidator () throws InvalidDatatypeFacetException {
        this( null, null, false ); // Native, No Facets defined, Restriction
    }

    public IDREFDatatypeValidator ( DatatypeValidator base, Hashtable facets,
                                    boolean derivedByList ) throws InvalidDatatypeFacetException {

        // all facets are handled in StringDatatypeValidator
        super (base, facets, derivedByList);

        // list types are handled by ListDatatypeValidator, we do nothing here.
        if ( derivedByList )
            return;

        // the type is NAME by default
        // REVISIT: how to set token type for id/idref derived types
        if (base instanceof IDREFDatatypeValidator)
            setTokenType(((IDREFDatatypeValidator)base).fTokenType);
        else
            setTokenType(SPECIAL_TOKEN_IDREFNAME);
    }

    /**
     * return value of whiteSpace facet
     */
    public short getWSFacet() {
        return COLLAPSE;
    }

    /**
     * Checks that "content" string is valid
     * datatype.
     * If invalid a Datatype validation exception is thrown.
     *
     * @param content A string containing the content to be validated
     * @param derivedBylist
     *                Flag which is true when type
     *                is derived by list otherwise it
     *                it is derived by extension.
     *
     * @exception throws InvalidDatatypeException if the content is
     *                   invalid according to the rules for the validators
     * @exception InvalidDatatypeValueException
     * @see         org.apache.xerces.validators.datatype.InvalidDatatypeValueException
     */
    public Object validate(String content, Object state ) throws InvalidDatatypeValueException{
        StateMessageDatatype message = (StateMessageDatatype) state;
        if (message != null && message.getDatatypeState() == IDREF_CHECKID) {
            Object[] params = (Object[])message.getDatatypeObject();
            checkIdRefs((Hashtable)params[0], (Hashtable)params[1]);
        }
        else {
            // use StringDatatypeValidator to validate content against facets
            super.validate(content, state);

            if ( message != null && message.getDatatypeState() == IDREF_VALIDATE )
                addIdRef( content, (Hashtable)message.getDatatypeObject());
        }

        return null;
    }


    /**
       * Returns a copy of this object.
       */
    public Object clone() throws CloneNotSupportedException {
        throw new CloneNotSupportedException("clone() is not supported in "+this.getClass().getName());
    }

    /** addId. */
    private void addIdRef(String content, Hashtable IDREFList) {
        if ( IDREFList.containsKey( content ) )
            return;

        try {
            IDREFList.put( content, fNullValue );
        }
        catch ( OutOfMemoryError ex ) {
            System.out.println( "Out of Memory: Hashtable of ID's has " + IDREFList.size() + " Elements" );
            ex.printStackTrace();
        }
    } // addId(int):boolean


    private void checkIdRefs(Hashtable IDList, Hashtable IDREFList) throws InvalidDatatypeValueException {
        Enumeration en = IDREFList.keys();

        while ( en.hasMoreElements() ) {
            String key = (String)en.nextElement();
            if ( !IDList.containsKey(key) ) {
                InvalidDatatypeValueException error = new InvalidDatatypeValueException( key );
                
                //REVISIT: handle errors

                //error.setMinorCode(XMLMessages.MSG_ELEMENT_WITH_ID_REQUIRED);
                //error.setMajorCode(XMLMessages.VC_IDREF);
                throw error;
            }
        }
    } // checkIdRefs()
}