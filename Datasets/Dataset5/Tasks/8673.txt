public void checkUniqueParticleAttribution(SchemaGrammar gram) throws Exception;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000 The Apache Software Foundation.  All rights 
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

package org.apache.xerces.validators.common;

import org.apache.xerces.utils.QName;
import org.apache.xerces.validators.schema.SubstitutionGroupComparator;
import org.apache.xerces.validators.schema.SchemaGrammar;

/**
 * ContentModel is an interface that can be used by your own custom validators
 * to plug in various types of content models. It is used internally as well
 * for the same purposes.
 * <p>
 * Since there are a number of optimizations that can be used for simple or
 * special content models, this class provides the interface via which all of
 * the various content model types are managed. So the validation handler
 * class has a list of things derived from this class. It finds the one for
 * the desired element, then asks it to validate the element contents.
 * <p>
 * The validation interface from the scanner to the validation handle provides
 * a child count and an array of element name indices into the string pool.
 * So it is assumed that those same parameters will be passed to the content
 * model to be validated. Therefore the validateContent() method accepts
 * this standard view of the elements to be validated.
 *
 * @author  Dean Roddey, Eric Ye
 * @version $Id$
 */
public interface XMLContentModel {

    /**
     * Check that the specified content is valid according to this
     * content model. This method can also be called to do 'what if' 
     * testing of content models just to see if they would be valid.
     * <p>
     * A value of -1 in the children array indicates a PCDATA node. All other 
     * indexes will be positive and represent child elements. The count can be
     * zero, since some elements have the EMPTY content model and that must be 
     * confirmed.
     *
     * @param children The children of this element.  Each integer is an index within
     *                 the <code>StringPool</code> of the child element name.  An index
     *                 of -1 is used to indicate an occurrence of non-whitespace character
     *                 data.
     * @param offset Offset into the array where the children starts.
     * @param length The number of entries in the <code>children</code> array.
     *
     * @return The value -1 if fully valid, else the 0 based index of the child
     *         that first failed. If the value returned is equal to the number
     *         of children, then the specified children are valid but additional
     *         content is required to reach a valid ending state.
     *
     * @exception Exception Thrown on error.
     */
    public int validateContent(QName children[], int offset, int length) throws Exception;

    /**
     * This method is different from "validateContent" in that it will try to use
     * the SubstitutionGroupComparator to match children against the content model.
     * <p>
     * A value of -1 in the children array indicates a PCDATA node. All other 
     * indexes will be positive and represent child elements. The count can be
     * zero, since some elements have the EMPTY content model and that must be 
     * confirmed.
     *
     * @param children The children of this element.  Each integer is an index within
     *                 the <code>StringPool</code> of the child element name.  An index
     *                 of -1 is used to indicate an occurrence of non-whitespace character
     *                 data.
     * @param offset Offset into the array where the children starts.
     * @param length The number of entries in the <code>children</code> array.
     *
     * @return The value -1 if fully valid, else the 0 based index of the child
     *         that first failed. If the value returned is equal to the number
     *         of children, then the specified children are valid but additional
     *         content is required to reach a valid ending state.
     *
     * @exception Exception Thrown on error.
     */
    public int validateContentSpecial(QName children[], int offset, int length) throws Exception;

    /**
     * The setter method to pass in the SubstitutionGroupComparator.
     *
     * @param comparator a SubstitutionGroupComparator object.
     * @return 
     * @exception 
     */
    public void setSubstitutionGroupComparator(SubstitutionGroupComparator comparator);// should really use a Comparator interface

    /**
     * Returns information about which elements can be placed at a particular point
     * in the passed element's content model.
     * <p>
     * Note that the incoming content model to test must be valid at least up to
     * the insertion point. If not, then -1 will be returned and the info object
     * will not have been filled in.
     * <p>
     * If, on return, the info.isValidEOC flag is set, then the 'insert after'
     * element is a valid end of content. In other words, nothing needs to be
     * inserted after it to make the parent element's content model valid.
     *
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
     * @see InsertableElementsInfo
     */
    public int whatCanGoHere(boolean fullyValid, 
                             InsertableElementsInfo info) throws Exception;

    public ContentLeafNameTypeVector getContentLeafNameTypeVector() ;

    // each kind of content model needs to provide a way to validate
    // Unique Particle Attribution
    public void checkUniqueParticleAttribution(SchemaGrammar gram);
} // interface XMLContentModel