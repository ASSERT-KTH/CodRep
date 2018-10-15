for (int index = info.insertAt; index < info.childCount-1; index++)

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
import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringPool;
import org.apache.xerces.validators.schema.SubstitutionGroupComparator;
import org.apache.xerces.validators.schema.SchemaGrammar;

/**
 * MixedContentModel is a derivative of the abstract content model base
 * class that handles the special case of mixed model elements. If an element
 * is mixed model, it has PCDATA as its first possible content, followed
 * by an alternation of the possible children. The children cannot have any
 * numeration or order, so it must look like this:
 * <pre>
 *   &lt;!ELEMENT Foo ((#PCDATA|a|b|c|)*)&gt;
 * </pre>
 * So, all we have to do is to keep an array of the possible children and
 * validate by just looking up each child being validated by looking it up
 * in the list.
 *
 * @version $Id$
 */
public class MixedContentModel 
    implements XMLContentModel {


    //
    // Data
    //
    
    /** The count of possible children that we have to deal with. */
    private int fCount;

    /** The list of possible children that we have to accept. */
    private QName fChildren[];

    /** The type of the children to support ANY. */
    private int fChildrenType[];

    /* this is the SubstitutionGroupComparator object */
    private SubstitutionGroupComparator comparator = null;
    
    /** 
     * True if mixed content model is ordered. DTD mixed content models
     * are <em>always</em> unordered.
     */
    private boolean fOrdered;

    /** Boolean to allow DTDs to validate even with namespace support. */
    private boolean fDTD;

    //
    // Constructors
    //

    /**
     * Constructs a mixed content model.
     *
     * @param count The child count.
     * @param childList The list of allowed children.
     *
     * @exception CMException Thrown if content model can't be built.
     */
    public MixedContentModel(QName childList[],
                             int childListType[],
                             int offset, int length) throws CMException {
        this(childList, childListType, offset, length, false, false);
    }

    /**
     * Constructs a mixed content model.
     *
     * @param count The child count.
     * @param childList The list of allowed children.
     * @param ordered True if content must be ordered.
     *
     * @exception CMException Thrown if content model can't be built.
     */
    public MixedContentModel(QName childList[],
                             int childListType[],
                             int offset, int length,
                             boolean ordered) throws CMException {
        this(childList, childListType, offset, length, ordered, false);
    }

    /**
     * Constructs a mixed content model.
     *
     * @param count The child count.
     * @param childList The list of allowed children.
     * @param ordered True if content must be ordered.
     *
     * @exception CMException Thrown if content model can't be built.
     */
    public MixedContentModel(QName childList[],
                             int childListType[],
                             int offset, int length,
                             boolean ordered,
                             boolean dtd) throws CMException {

        // Make our own copy now, which is exactly the right size
        fCount = length;
        fChildren = new QName[fCount];
        fChildrenType = new int[fCount];
        for (int i = 0; i < fCount; i++) {
            fChildren[i] = new QName(childList[offset + i]);
            fChildrenType[i] = childListType[offset + i];
        }
        fOrdered = ordered;

        fDTD = dtd;

    } // <init>(QName[],int[],int,int,boolean,boolean)
    
    // Unique Particle Attribution
    public void checkUniqueParticleAttribution(SchemaGrammar gram) {
        // rename back
        for (int i = 0; i < fCount; i++)
            fChildren[i].uri = gram.getContentSpecOrgUri(fChildren[i].uri);

        // for mixed content model, it's only a sequence
        // UPA checking is not necessary
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
    public int validateContent(QName children[], int offset, int length) 
        throws Exception {
        
        // must match order
        if (fOrdered) {
            int inIndex = 0;
            for (int outIndex = 0; outIndex < length; outIndex++) {

                // ignore mixed text
                final QName curChild = children[offset + outIndex];
                if (curChild.localpart == -1) {
                    continue;
                }

                // element must match
                int type = fChildrenType[inIndex];
                if (type == XMLContentSpec.CONTENTSPECNODE_LEAF) {
                    if (fDTD) {
                        if (fChildren[inIndex].rawname != children[offset + outIndex].rawname) {
                            return outIndex;
                        }
                    }
                    else {
                        if (fChildren[inIndex].uri != children[offset + outIndex].uri &&
                            fChildren[inIndex].localpart != children[offset + outIndex].localpart) {
                            return outIndex;
                        }
                    }
                }
                else if (type == XMLContentSpec.CONTENTSPECNODE_ANY) {
                }
                else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_NS) {
                    if (children[outIndex].uri != fChildren[inIndex].uri) {
                        return outIndex;
                    }
                }
                else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_OTHER) {
                    if (fChildren[inIndex].uri == children[outIndex].uri) {
                        return outIndex;
                    }
                }
                
                // advance index
                inIndex++;
            }
        }

        // can appear in any order
        else {
            for (int outIndex = 0; outIndex < length; outIndex++)
            {
                // Get the current child out of the source index
                final QName curChild = children[offset + outIndex];
    
                // If its PCDATA, then we just accept that
                if (curChild.localpart == -1)
                    continue;
    
                // And try to find it in our list
                int inIndex = 0;
                for (; inIndex < fCount; inIndex++)
                {
                    int type = fChildrenType[inIndex];
                    if (type == XMLContentSpec.CONTENTSPECNODE_LEAF) {
                        if (fDTD) {
                            if (curChild.rawname == fChildren[inIndex].rawname) {
                                break;
                            }
                        }
                        else {
                            if (curChild.uri == fChildren[inIndex].uri &&
                                curChild.localpart == fChildren[inIndex].localpart)
                                break;
                        }
                    }
                    else if (type == XMLContentSpec.CONTENTSPECNODE_ANY) {
                            break;
                    }
                    else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_NS) {
                        if (children[outIndex].uri == fChildren[inIndex].uri) {
                            break;
                        }
                    }
                    else if (type == XMLContentSpec.CONTENTSPECNODE_ANY_OTHER) {
                        if (fChildren[inIndex].uri != children[outIndex].uri) {
                            break;
                        }
                    }
                    // REVISIT: What about checking for multiple ANY matches?
                    //          The content model ambiguity *could* be checked
                    //          by the caller before constructing the mixed
                    //          content model.
                }

                // We did not find this one, so the validation failed
                if (inIndex == fCount)
                    return outIndex;
            }
        }

        // Everything seems to be in order, so return success
        return -1;

    }

    public int validateContentSpecial(QName children[], int offset, int length) throws Exception{
         //TO DO here. cause Mixed Content is only for DTD, Schema is kind of different.
            return validateContent(children,offset, length);
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
    public int whatCanGoHere(boolean                    fullyValid
                            , InsertableElementsInfo    info) throws Exception
    {
        //
        //  For this one, having the empty slot at the insertion point is 
        //  a problem. So lets compress the array down. We know that it has
        //  to have at least the empty slot at the insertion point.
        //
        for (int index = info.insertAt; index < info.childCount; index++)
            info.curChildren[index] = info.curChildren[index+1];
        info.childCount--;

        //
        //  Check the validity of the existing contents. If this is less than
        //  the insert at point, then return failure index right now
        //
        final int failedIndex = validateContent(info.curChildren, 0, info.childCount);
        if ((failedIndex != -1) && (failedIndex < info.insertAt))
            return failedIndex;

        //
        //  Set any stuff we can know right off the bat for all cases. Mixed
        //  models can always hold PCData. And, since its always a repetition
        //  of a bunch of choice nodes, its always valid EOC.
        //
        info.canHoldPCData = true;
        info.isValidEOC = true;

        //
        //  Set the results count member and then see if we need to reallocate
        //  the outgoing arrays.
        //
        info.resultsCount = fCount;

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
        //  If the fully valid parameter is set, then whether any child can
        //  go here is dependent upon the content model having been valid all
        //  the way to the end. If its not, nothing we put here is going to
        //  make it happy. If it was ok, then nothing we put here is ever going
        //  make it bad.
        //
        //  So set up a boolean that can be used to set every possible child's
        //  insertable status below.
        //
        boolean bStatus = true;
        if (fullyValid && (failedIndex < info.childCount))
            bStatus = false;

        //
        //  Fill in the possible children array, from our array. And set the
        //  boolean flag for each one to true because any of them can go
        //  anywhere.
        //
        for (int index = 0; index < fCount; index++)
        {
            info.possibleChildren[index].setValues(fChildren[index]);
            info.results[index] = bStatus;
        }

        return -1;
    }


    public ContentLeafNameTypeVector getContentLeafNameTypeVector() {
        return null;
    }


} // class MixedContentModel