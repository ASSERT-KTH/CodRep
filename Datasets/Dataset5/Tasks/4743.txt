for (int index = info.insertAt; index < info.childCount-1; index++) {

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

import org.apache.xerces.framework.XMLContentSpec;
import org.apache.xerces.utils.ImplementationMessages;
import org.apache.xerces.utils.QName;
import org.apache.xerces.validators.schema.SchemaGrammar;

import org.apache.xerces.validators.schema.SubstitutionGroupComparator;

/**
 * SimpleContentModel is a derivative of the abstract content model base
 * class that handles a small set of simple content models that are just
 * way overkill to give the DFA treatment.
 * <p>
 * This class handles the following scenarios:
 * <ul>
 * <li> a
 * <li> a?
 * <li> a*
 * <li> a+
 * <li> a,b
 * <li> a|b
 * </ul>
 * <p>
 * These all involve a unary operation with one element type, or a binary
 * operation with two elements. These are very simple and can be checked
 * in a simple way without a DFA and without the overhead of setting up a
 * DFA for such a simple check.
 *
 * @version $Id$
 */
public class SimpleContentModel 
    implements XMLContentModel {

    //
    // Data
    //

    /**
     * The element decl pool indices of the first (and optional second)
     * child node. The operation code tells us whether the second child
     * is used or not.
     */
    private QName fFirstChild = new QName();

    /**
     * The element decl pool indices of the first (and optional second)
     * child node. The operation code tells us whether the second child
     * is used or not.
     */
    private QName fSecondChild = new QName();

    /**
     * The operation that this object represents. Since this class only
     * does simple contents, there is only ever a single operation
     * involved (i.e. the children of the operation are always one or
     * two leafs.) This is one of the XMLDTDParams.CONTENTSPECNODE_XXX values.
     */
    private int fOp;

    /** Boolean to allow DTDs to validate even with namespace support. */
    private boolean fDTD;

    /* this is the SubstitutionGroupComparator object */
    private SubstitutionGroupComparator comparator = null;
    
    //
    // Constructors
    //

    /**
     * Constructs a simple content model.
     *
     * @param firstChildIndex The first child index
     * @parma secondChildIndex The second child index.
     * @param cmOp The content model operator.
     *
     * @see XMLContentSpec
     */
    public SimpleContentModel(QName firstChild, QName secondChild, int cmOp) {
        this(firstChild, secondChild, cmOp, false);
    }

    /**
     * Constructs a simple content model.
     *
     * @param firstChildIndex The first child index
     * @parma secondChildIndex The second child index.
     * @param cmOp The content model operator.
     *
     * @see XMLContentSpec
     */
    public SimpleContentModel(QName firstChild, QName secondChild, 
                              int cmOp, boolean dtd) {
        //
        //  Store away the children and operation. This is all we need to
        //  do the content model check.
        //
        //  The operation is one of the ContentSpecNode.NODE_XXX values!
        //
        fFirstChild.setValues(firstChild);
        if (secondChild != null) {
            fSecondChild.setValues(secondChild);
        }
        else {
            fSecondChild.clear();
        }
        fOp = cmOp;
        fDTD = dtd;
    }

    // Unique Particle Attribution
    public void checkUniqueParticleAttribution(SchemaGrammar gram) throws Exception {
        // rename back
        fFirstChild.uri = gram.getContentSpecOrgUri(fFirstChild.uri);
        fSecondChild.uri = gram.getContentSpecOrgUri(fSecondChild.uri);

        // only possible violation is when it's a choice
        if (fOp == XMLContentSpec.CONTENTSPECNODE_CHOICE &&
            ElementWildcard.conflict(XMLContentSpec.CONTENTSPECNODE_LEAF,
                                     fFirstChild.localpart, fFirstChild.uri,
                                     XMLContentSpec.CONTENTSPECNODE_LEAF,
                                     fSecondChild.localpart, fSecondChild.uri,
                                     comparator)) {
        }
    }
    // Unique Particle Attribution

    //
    // XMLContentModel methods
    //
    
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
    public int validateContent(QName children[], int offset, int length) throws Exception {

        //
        //  According to the type of operation, we do the correct type of
        //  content check.
        //
        switch(fOp)
        {
            case XMLContentSpec.CONTENTSPECNODE_LEAF :
                // If there is not a child, then report an error at index 0
                if (length == 0)
                    return 0;

                // If the 0th child is not the right kind, report an error at 0
                if (fDTD) {
                    if (children[offset].rawname != fFirstChild.rawname) {
                        return 0;
                    }
                }
                else {
                    if (children[offset].uri != fFirstChild.uri || 
                        children[offset].localpart != fFirstChild.localpart)
                        return 0;
                }

                // If more than one child, report an error at index 1
                if (length > 1)
                    return 1;
                break;

            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE :
                //
                //  If there is one child, make sure its the right type. If not,
                //  then its an error at index 0.
                //
                if (length == 1) {
                    if (fDTD) {
                        if (children[offset].rawname != fFirstChild.rawname) {
                            return 0;
                        }
                    }
                    else {
                        if (children[offset].uri != fFirstChild.uri || 
                         children[offset].localpart != fFirstChild.localpart)
                        return 0;
                    }
                }

                //
                //  If the child count is greater than one, then obviously
                //  bad, so report an error at index 1.
                //
                if (length > 1)
                    return 1;
                break;

            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE :
                //
                //  If the child count is zero, that's fine. If its more than
                //  zero, then make sure that all children are of the element
                //  type that we stored. If not, report the index of the first
                //  failed one.
                //
                if (length > 0)
                {
                    if (fDTD) {
                        for (int index = 0; index < length; index++) {
                            if (children[offset + index].rawname != fFirstChild.rawname) {
                                return index;
                            }
                        }
                    }
                    else {
                        for (int index = 0; index < length; index++)
                        {
                            if (children[offset + index].uri != fFirstChild.uri || 
                                children[offset + index].localpart != fFirstChild.localpart)
                                return index;
                        }
                    }
                }
                break;

            case XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE :
                //
                //  If the child count is zero, that's an error so report
                //  an error at index 0.
                //
                if (length == 0)
                    return 0;

                //
                //  Otherwise we have to check them all to make sure that they
                //  are of the correct child type. If not, then report the index
                //  of the first one that is not.
                //
                if (fDTD) {
                    for (int index = 0; index < length; index++) {
                        if (children[offset + index].rawname != fFirstChild.rawname) {
                            return index;
                        }
                    }
                }
                else {
                    for (int index = 0; index < length; index++)
                    {
                        if (children[offset + index].uri != fFirstChild.uri || 
                            children[offset + index].localpart != fFirstChild.localpart)
                            return index;
                    }
                }
                break;

            case XMLContentSpec.CONTENTSPECNODE_CHOICE :
                //
                //  There must be one and only one child, so if the element count
                //  is zero, return an error at index 0.
                //
                if (length == 0)
                    return 0;

                // If the zeroth element isn't one of our choices, error at 0
                if (fDTD) {
                    if ((children[offset].rawname != fFirstChild.rawname) &&
                        (children[offset].rawname != fSecondChild.rawname)) {
                        return 0;
                    }
                }
                else {
                    if ((children[offset].uri != fFirstChild.uri || children[offset].localpart != fFirstChild.localpart) &&
                        (children[offset].uri != fSecondChild.uri || children[offset].localpart != fSecondChild.localpart))
                        return 0;
                }

                // If there is more than one element, then an error at 1
                if (length > 1)
                    return 1;
                break;

            case XMLContentSpec.CONTENTSPECNODE_SEQ :
                //
                //  There must be two children and they must be the two values
                //  we stored, in the stored order.
                //
                if (length == 2) {
                    if (fDTD) {
                        if (children[offset].rawname != fFirstChild.rawname) {
                            return 0;
                        }
                        if (children[offset + 1].rawname != fSecondChild.rawname) {
                            return 1;
                        }
                    }
                    else {
                        if (children[offset].uri != fFirstChild.uri || children[offset].localpart != fFirstChild.localpart)
                            return 0;

                        if (children[offset + 1].uri != fSecondChild.uri || children[offset + 1].localpart != fSecondChild.localpart)
                            return 1;
                    }
                }
                else {
                    if (length > 2) {
                        return 2;
                    }

                    return length;
                }

                break;

            default :
                throw new CMException(ImplementationMessages.VAL_CST);
        }

        // We survived, so return success status
        return -1;
    }
    
    public int validateContentSpecial(QName children[], int offset, int length) throws Exception{

        if (comparator==null) {
            return validateContent(children,offset, length);
        }
        //
        //  According to the type of operation, we do the correct type of
        //  content check.
        //
        switch(fOp)
        {
            case XMLContentSpec.CONTENTSPECNODE_LEAF :
                // If there is not a child, then report an error at index 0
                if (length == 0)
                    return 0;

                // If the 0th child is not the right kind, report an error at 0
                if (children[offset].uri != fFirstChild.uri || 
                    children[offset].localpart != fFirstChild.localpart)
                    if (!comparator.isEquivalentTo(children[offset], fFirstChild)) 
                        return 0;

                // If more than one child, report an error at index 1
                if (length > 1)
                    return 1;
                break;

            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE :
                //
                //  If there is one child, make sure its the right type. If not,
                //  then its an error at index 0.
                //
                if (length == 1 && 
                    (children[offset].uri != fFirstChild.uri || 
                     children[offset].localpart != fFirstChild.localpart))
                    if (!comparator.isEquivalentTo(children[offset], fFirstChild)) 
                        return 0;

                //
                //  If the child count is greater than one, then obviously
                //  bad, so report an error at index 1.
                //
                if (length > 1)
                    return 1;
                break;

            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE :
                //
                //  If the child count is zero, that's fine. If its more than
                //  zero, then make sure that all children are of the element
                //  type that we stored. If not, report the index of the first
                //  failed one.
                //
                if (length > 0)
                {
                    for (int index = 0; index < length; index++)
                    {
                        if (children[offset + index].uri != fFirstChild.uri || 
                            children[offset + index].localpart != fFirstChild.localpart)
                            if (!comparator.isEquivalentTo(children[offset+index], fFirstChild)) 
                                return index;
                    }
                }
                break;

            case XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE :
                //
                //  If the child count is zero, that's an error so report
                //  an error at index 0.
                //
                if (length == 0)
                    return 0;

                //
                //  Otherwise we have to check them all to make sure that they
                //  are of the correct child type. If not, then report the index
                //  of the first one that is not.
                //
                for (int index = 0; index < length; index++)
                {
                    if (children[offset + index].uri != fFirstChild.uri || 
                        children[offset + index].localpart != fFirstChild.localpart)
                        if (!comparator.isEquivalentTo(children[offset+index], fFirstChild)) 
                            return index;
                }
                break;

            case XMLContentSpec.CONTENTSPECNODE_CHOICE :
                //
                //  There must be one and only one child, so if the element count
                //  is zero, return an error at index 0.
                //
                if (length == 0)
                    return 0;

                // If the zeroth element isn't one of our choices, error at 0
                if ((children[offset].uri != fFirstChild.uri || children[offset].localpart != fFirstChild.localpart) &&
                    (children[offset].uri != fSecondChild.uri || children[offset].localpart != fSecondChild.localpart))
                    if (   !comparator.isEquivalentTo(children[offset], fFirstChild) 
                        && !comparator.isEquivalentTo(children[offset], fSecondChild) ) 
                        return 0;

                // If there is more than one element, then an error at 1
                if (length > 1)
                    return 1;
                break;

            case XMLContentSpec.CONTENTSPECNODE_SEQ :
                //
                //  There must be two children and they must be the two values
                //  we stored, in the stored order.
                //
                if (length == 2) {
                    if (children[offset].uri != fFirstChild.uri || children[offset].localpart != fFirstChild.localpart)
                        if (!comparator.isEquivalentTo(children[offset], fFirstChild)) 
                            return 0;

                    if (children[offset + 1].uri != fSecondChild.uri || children[offset + 1].localpart != fSecondChild.localpart)
                        if (!comparator.isEquivalentTo(children[offset+1], fSecondChild)) 
                            return 1;
                }
                else {
                    if (length > 2) {
                        return 2;
                    }

                    return length;
                }

                break;

            default :
                throw new CMException(ImplementationMessages.VAL_CST);
        }

        // We survived, so return success status
        return -1;
    }

    public void setSubstitutionGroupComparator(SubstitutionGroupComparator comparator) {
        this.comparator = comparator;
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
    public int whatCanGoHere(boolean fullyValid, InsertableElementsInfo info) 
        throws Exception {

        //
        //  For this one, having the empty slot at the insertion point is 
        //  a problem. So lets compress the array down. We know that it has
        //  to have at least the empty slot at the insertion point.
        //
        for (int index = info.insertAt; index < info.childCount; index++) {
            info.curChildren[index].setValues(info.curChildren[index+1]);
        }
        info.childCount--;
        
        //
        //  Check the validity of the existing contents. If this is less than
        //  the insert at point, then return failure index right now
        //
        final int failedIndex = validateContent(info.curChildren, 0, info.childCount);
        if ((failedIndex != -1) && (failedIndex < info.insertAt))
            return failedIndex;

        // Set any stuff we can know right off the bat for all cases
        info.canHoldPCData = false;

        // See how many children we can possibly report
        if ((fOp == XMLContentSpec.CONTENTSPECNODE_LEAF)
        ||  (fOp == XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE)
        ||  (fOp == XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE)
        ||  (fOp == XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE))
        {
            info.resultsCount = 1;
        }
         else if ((fOp == XMLContentSpec.CONTENTSPECNODE_CHOICE)
              ||  (fOp == XMLContentSpec.CONTENTSPECNODE_SEQ))
        {
            info.resultsCount = 2;
        }
         else
        {
            throw new CMException(ImplementationMessages.VAL_CST);
        }

        //
        //  If the outgoing arrays are too small or null, create new ones. These
        //  have to be at least the size of the results count.
        //
        if ((info.results == null) || (info.results.length < info.resultsCount))
            info.results = new boolean[info.resultsCount];

        if ((info.possibleChildren == null)
        ||  (info.possibleChildren.length < info.resultsCount))
        {
            info.possibleChildren = new QName[info.resultsCount];
            for (int i = 0; i < info.possibleChildren.length; i++) {
                info.possibleChildren[i] = new QName();
            }
        }

        //
        //  Fill in the possible children array, and set all of the associated
        //  results entries to defaults of false.
        //
        info.possibleChildren[0].setValues(fFirstChild);
        info.results[0] = false;
        if (info.resultsCount == 2)
        {
            info.possibleChildren[1].setValues(fSecondChild);
            info.results[1] = false;
        }

        //
        //  Set some defaults so that it does not have to be done redundantly
        //  below in each case.
        //
        info.isValidEOC = false;

        //
        //  Now, for each spec type, lets do the grunt work required. Each of
        //  them is pretty simple, its just making sure of corner cases.
        //
        //  We know its valid up to the insert point at least and we know that
        //  the insert point is never past the number of children, so this releaves
        //  a lot of checking below.
        //
        switch(fOp)
        {
            case XMLContentSpec.CONTENTSPECNODE_LEAF :
            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_ONE :
                //
                //  If there are no current children, then insert at has to be
                //  zero, so we can have the one leaf element inserted here.
                //
                if (info.childCount == 0)
                {
                    info.results[0] = true;
                }
                 else if (info.childCount > 0)
                {
                    //
                    //  If the child count is greater than zero, then inserting
                    //  anything cannot be fully valid. But, if not fully valid
                    //  checking, it is ok as long as inserting at zero.
                    //
                    if (!fullyValid && (info.insertAt == 0))
                        info.results[0] = true;
                }

                if (fOp == XMLContentSpec.CONTENTSPECNODE_LEAF)
                {
                    // If the insert point is 1, then EOC is valid there
                    if (info.insertAt == 0)
                        info.isValidEOC = true;
                }
                 else
                {
                    // Its zero or one, so EOC is valid in either case
                    info.isValidEOC = true;
                }
                break;

            case XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE :
            case XMLContentSpec.CONTENTSPECNODE_ONE_OR_MORE :
                //
                //  The one child is always possible to insert, regardless of
                //  where. The fully valid flag never comes into play since it
                //  cannot become invalid by inserting any number of new
                //  instances of the one element.
                //
                info.results[0] = true;

                //
                //  Its zero/one or more, so EOC is valid in either case but only
                //  after the 0th index for one or more.
                //
                if ((fOp == XMLContentSpec.CONTENTSPECNODE_ZERO_OR_MORE)
                ||  (info.insertAt > 0))
                {
                    info.isValidEOC = true;
                }
                break;

            case XMLContentSpec.CONTENTSPECNODE_CHOICE :
                //
                //  If the insert point is zero, then either of the two children
                //  can be inserted, unless fully valid is set and there are
                //  already any children.
                //
                if (info.insertAt == 0)
                {
                    if (!fullyValid && (info.childCount == 0))
                    {
                        info.results[0] = true;
                        info.results[1] = true;
                    }
                }

                // EOC is only valid at the end
                if (info.insertAt == 1)
                    info.isValidEOC = true;
                break;

            case XMLContentSpec.CONTENTSPECNODE_SEQ :
                //
                //  If the insert at is 0, then the first one valid. Else its
                //  the second one.
                //
                if (info.insertAt == 0)
                {
                    //
                    //  If fully valid check, then if there are two children,
                    //  it cannot be valid. If there is one child, it must be
                    //  equal to the second child of the pattern since it will
                    //  get pushed up (which means it was a pattern like (x|x)
                    //  which is kinda wierd.)
                    //
                    if (fullyValid)
                    {
                        if (info.childCount == 1)
                            info.results[0] = info.curChildren[0].uri == fSecondChild.uri &&
                                              info.curChildren[0].localpart == fSecondChild.localpart;
                    }
                     else
                    {
                        info.results[0] = true;
                    }
                }
                 else if (info.insertAt == 1)
                {
                    // If fully valid, then there cannot be two existing children
                    if (!fullyValid || (info.childCount == 1))
                        info.results[1] = true;
                }

                // EOC is only valid at the end
                if (info.insertAt == 2)
                    info.isValidEOC = true;
                break;

            default :
                throw new CMException(ImplementationMessages.VAL_CST);
        }

        // We survived, so return success status
        return -1;
    }

    public ContentLeafNameTypeVector getContentLeafNameTypeVector() {
          return null;
    }
} // class SimpleContentModel