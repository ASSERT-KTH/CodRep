fAttURI[chunk][index] = StringPool.EMPTY_STRING;

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

package org.apache.xerces.framework;

import org.apache.xerces.utils.QName;
import org.apache.xerces.utils.StringPool;

import org.xml.sax.AttributeList;
import org.xml.sax.Locator;
import org.xml.sax.SAXParseException;

/**
 * An instance of this class is used to represent the set of attributes
 * for an element that are either directly specified or provided through
 * a default value in the grammar for the document.   XMLAttrList carries
 * the attributes associated with an element from the scanner up to the
 * application level (via the SAX AtributeList).  Because all the attributes
 * are bundled up together before being presented to the application, we don't
 * have a way to build up an attribute value from pieces, most notably entity
 * references.
 * <p>
 * There is typically one instance of this class for each instance of a
 * parser.  The parser may either use this object to hold the attributes
 * of a single element, calling releaseAttrList() before each new element,
 * or it may use this object to hold the attributes of all of the elements
 * in the document.
 * <p>
 * To start saving a new set of attributes, the startAttrList() method is
 * called, returning a handle for the attribute list.  All addAttr() calls
 * will be added to the set until a call is made to endAttrList().  A handle
 * of -1 is used to indicate that there are no attributes in the set.
 * <p>
 * When an attribute is added to the set, the type of the attribute and an
 * indicator of whether it was specified explicitly or through a default is
 * provided.
 * <p>
 * The attributes in the set may be accessed either through the getFirstAttr()
 * and getNextAttr() iteration interface, or the getAttributeList() method
 * may be used to access the attribute list through the SAX <code>AttributeList</code>
 * interface.
 *
 * @version $Id$
 */
public final class XMLAttrList 
    implements AttributeList {

    //
    // Constants
    //

    // Chunk size constants

    private static final int CHUNK_SHIFT = 5;           // 2^5 = 32
    private static final int CHUNK_SIZE = (1 << CHUNK_SHIFT);
    private static final int CHUNK_MASK = CHUNK_SIZE - 1;
    private static final int INITIAL_CHUNK_COUNT = (1 << (10 - CHUNK_SHIFT));   // 2^10 = 1k

    // Flags (bits)

    private static final int ATTFLAG_SPECIFIED = 1;
    private static final int ATTFLAG_LASTATTR  = 2;

    //
    // Data
    //

    // Instance variables

    private StringPool fStringPool = null;
    private int fCurrentHandle = -1;
    private int fAttributeListHandle = -1;
    private int fAttributeListLength = 0;
    private int fAttrCount = 0;
    private int[][] fAttPrefix = new int[INITIAL_CHUNK_COUNT][];
    private int[][] fAttLocalpart = new int[INITIAL_CHUNK_COUNT][];
    private int[][] fAttName = new int[INITIAL_CHUNK_COUNT][];
    private int[][] fAttURI = new int[INITIAL_CHUNK_COUNT][];
    private int[][] fAttValue = new int[INITIAL_CHUNK_COUNT][];
    private int[][] fAttType = new int[INITIAL_CHUNK_COUNT][];
    private byte[][] fAttFlags = new byte[INITIAL_CHUNK_COUNT][];

    // utility

    private QName fAttributeQName = new QName();

    /**
     * Constructor
     *
     * @param stringPool The string pool instance to use.
     */
    public XMLAttrList(StringPool stringPool) {
        fStringPool = stringPool;
    }

    /**
     * Reset this instance to an "empty" state.
     *
     * @param stringPool The string pool instance to use.
     */
    public void reset(StringPool stringPool) {
        fStringPool = stringPool;
        fCurrentHandle = -1;
        fAttributeListHandle = -1;
        fAttributeListLength = 0;
        fAttrCount = 0;
    }

    public int addAttr(int attrName, int attValue, 
                       int attType, boolean specified, boolean search) throws Exception
    {
        fAttributeQName.setValues(-1, attrName, attrName);
        return addAttr(fAttributeQName, attValue, attType, specified, search);
    }
    /**
     * Add an attribute to the current set.
     *
     * @param attrName The name of the attribute, an index in the string pool.
     * @param attValue The value of the attribute, an index in the string pool.
     * @param attType The type of the attribute, an index in the string pool.
     * @param specified <code>true</code> if the attribute is specified directly; otherwise
     *                  <code>false</code> is the attribute is provided through a default.
     * @param search <code>true</code> if the list should be searched for a duplicate.
     * @return The index of this attribute; or -1 is <code>search</code> was <code>true</code>
     *         and <code>attrName</code> was already present.
     */
    public int addAttr(QName attribute, 
                       int attValue, int attType, 
                       boolean specified, boolean search) throws Exception {

        int chunk;
        int index;
        if (search) {
            chunk = fCurrentHandle >> CHUNK_SHIFT;
            index = fCurrentHandle & CHUNK_MASK;
            for (int attrIndex = fCurrentHandle; attrIndex < fAttrCount; attrIndex++) {
                // REVISIT: Should this be localpart?
                if (fStringPool.equalNames(fAttName[chunk][index], attribute.rawname)) {
                    return -1;
                }
                if (++index == CHUNK_SIZE) {
                    chunk++;
                    index = 0;
                }
            }
        } else {
            chunk = fAttrCount >> CHUNK_SHIFT;
            index = fAttrCount & CHUNK_MASK;
        }
        ensureCapacity(chunk, index);
        fAttPrefix[chunk][index] = attribute.prefix;
        fAttLocalpart[chunk][index] = attribute.localpart;
        fAttName[chunk][index] = attribute.rawname;
        fAttURI[chunk][index] = attribute.uri;
        fAttValue[chunk][index] = attValue;
        fAttType[chunk][index] = attType;
        fAttFlags[chunk][index] = (byte)(specified ? ATTFLAG_SPECIFIED : 0);
        return fAttrCount++;

    } // addAttr(QName,int,int,boolean,boolean):int

    /**
     * Start a new set of attributes.
     *
     * @return The handle for the new set of attributes.
     */
    public int startAttrList() {
        fCurrentHandle = fAttrCount;
        return fCurrentHandle;
    }

    /**
     * Terminate the current set of attributes.
     */
    public void endAttrList() {
        int attrIndex = fAttrCount - 1;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        fAttFlags[chunk][index] |= ATTFLAG_LASTATTR;
        fCurrentHandle = -1;
    }

    /**
     * Get the prefix of the attribute.
     */
    public int getAttrPrefix(int attrIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return -1;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        return fAttPrefix[chunk][index];
    }

    /**
     * Return the localpart of the attribute.
     */
    public int getAttrLocalpart(int attrIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return -1;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        return fAttLocalpart[chunk][index];
    }

    // REVISIT: Should this be renamed "getAttrRawname" to match?
    /**
     * Get the name of the attribute
     *
     * @param attrIndex The index of the attribute.
     * @return The name of the attribute, an index in the string pool.
     */
    public int getAttrName(int attrIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return -1;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        return fAttName[chunk][index];
    }
    
    /** Sets the uri of the attribute. */
    public void setAttrURI(int attrIndex, int uri) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        fAttURI[chunk][index] = uri;
    }

    /** Return the uri of the attribute. */
    public int getAttrURI(int attrIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return -1;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        return fAttURI[chunk][index];
    }

    /**
     * Get the value of the attribute
     *
     * @param attrIndex The index of the attribute.
     * @return The value of the attribute, an index in the string pool.
     */
    public int getAttValue(int attrIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return -1;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        return fAttValue[chunk][index];
    }

    /**
     * Sets the value of the attribute.
     */
    public void setAttValue(int attrIndex, int attrValue) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        fAttValue[chunk][index] = attrValue;
    }

    /** Sets the type of the attribute. */
    public void setAttType(int attrIndex, int attTypeIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        fAttType[chunk][index] = attTypeIndex;
    }

    /**
     * Get the type of the attribute
     *
     * @param attrIndex The index of the attribute.
     * @return The type of the attribute, an index in the string pool.
     */
    public int getAttType(int attrIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return -1;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        return fAttType[chunk][index];
    }

    /**
     * Was the attribute explicitly supplied or was it provided through a default?
     *
     * @param attrIndex The index of the attribute.
     * @return <code>true</code> if the attribute was specified directly; otherwise
     *         <code>false</code> is the attribute was provided through a default.
     */
    public boolean isSpecified(int attrIndex) {
        if (attrIndex < 0 || attrIndex >= fAttrCount)
            return true;
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        return (fAttFlags[chunk][index] & ATTFLAG_SPECIFIED) != 0;
    }

    /**
     * Make the resources of the current attribute list available for reuse.
     *
     * @param The attribute list handle.
     */
    public void releaseAttrList(int attrListHandle) {
        if (attrListHandle == -1)
            return;
        int chunk = attrListHandle >> CHUNK_SHIFT;
        int index = attrListHandle & CHUNK_MASK;
        while (true) {
            boolean last = (fAttFlags[chunk][index] & ATTFLAG_LASTATTR) != 0;
            fAttPrefix[chunk][index] = -1;
            fAttLocalpart[chunk][index] = -1;
            fAttName[chunk][index] = -1;
            fAttURI[chunk][index] = -1;
            if ((fAttFlags[chunk][index] & ATTFLAG_SPECIFIED) != 0)
                fStringPool.releaseString(fAttValue[chunk][index]);
            fAttValue[chunk][index] = -1;
            if (++index == CHUNK_SIZE) {
                chunk++;
                index = 0;
            }
            if (last)
                break;
        }
        int lastIndex = (chunk << CHUNK_SHIFT) + index;
        if (fAttrCount == lastIndex)
            fAttrCount = attrListHandle;
    }

    /** 
     * Get the first attribute in the attribute list.
     *
     * @param attrListHandle The attribute list handle.
     * @return The index of the first attribute in the specified
     *         attribute list or -1 if the handle is invalid.
     */
    public int getFirstAttr(int attrListHandle) {
        if (attrListHandle < 0 || attrListHandle >= fAttrCount) {
            return -1;
        }
        // the first attribute in a list is implemented as
        // the same index of the attribute list handle
        return attrListHandle;
    }

    /**
     * Get the next attribute in the attribute list.
     *
     * @param attrIndex The attribute index.
     * @return The index of the next attribute after <code>attrIndex</code> in
     *         the same attribute list or -1 if there is no next index.
     */
    public int getNextAttr(int attrIndex) {
        if (attrIndex < 0 || attrIndex + 1 >= fAttrCount) {
            return -1;
        }
        int chunk = attrIndex >> CHUNK_SHIFT;
        int index = attrIndex & CHUNK_MASK;
        if ((fAttFlags[chunk][index] & ATTFLAG_LASTATTR) != 0) {
            return -1;
        }
        // attribute lists are implemented in the
        // chunks one after another with the last
        // attribute having a "last" flag set
        return attrIndex + 1;
    }

    /* AttributeList support */

    /**
     * Setup this instance to respond as an <code>AttributeList</code> implementation.
     *
     * @return This instance as an <code>AttributeList</code>.
     */
    public AttributeList getAttributeList(int attrListHandle) {
        fAttributeListHandle = attrListHandle;
        if (fAttributeListHandle == -1)
            fAttributeListLength = 0;
        else {
            int chunk = fAttributeListHandle >> CHUNK_SHIFT;
            int index = fAttributeListHandle & CHUNK_MASK;
            fAttributeListLength = 1;
            while ((fAttFlags[chunk][index] & ATTFLAG_LASTATTR) == 0) {
                if (++index == CHUNK_SIZE) {
                    chunk++;
                    index = 0;
                }
                fAttributeListLength++;
            }
        }
        return this;
    }

    /**
     * Return the number of attributes in this list.
     *
     * <p>The SAX parser may provide attributes in any
     * arbitrary order, regardless of the order in which they were
     * declared or specified.  The number of attributes may be
     * zero.</p>
     *
     * @return The number of attributes in the list.
     */
    public int getLength() {
        return fAttributeListLength;
    }

    /**
     * Return the prefix of an attribute in this list (by position).
     */
    public String getPrefix(int i) {
        if (i < 0 || i >= fAttributeListLength) {
            return null;
        }
        int chunk = (fAttributeListHandle + i) >> CHUNK_SHIFT;
        int index = (fAttributeListHandle + i) & CHUNK_MASK;
        return fStringPool.toString(fAttPrefix[chunk][index]);
    }

    /**
     * Return the local part of an attribute in this list (by position).
     */
    public String getLocalpart(int i) {
        if (i < 0 || i >= fAttributeListLength) {
            return null;
        }
        int chunk = (fAttributeListHandle + i) >> CHUNK_SHIFT;
        int index = (fAttributeListHandle + i) & CHUNK_MASK;
        return fStringPool.toString(fAttLocalpart[chunk][index]);
    }

    /**
     * Return the name of an attribute in this list (by position).
     *
     * <p>The names must be unique: the SAX parser shall not include the
     * same attribute twice.  Attributes without values (those declared
     * #IMPLIED without a value specified in the start tag) will be
     * omitted from the list.</p>
     *
     * <p>If the attribute name has a namespace prefix, the prefix
     * will still be attached.</p>
     *
     * @param i The index of the attribute in the list (starting at 0).
     * @return The name of the indexed attribute, or null
     *         if the index is out of range.
     * @see #getLength
     */
    public String getName(int i) {
        if (i < 0 || i >= fAttributeListLength)
            return null;
        int chunk = (fAttributeListHandle + i) >> CHUNK_SHIFT;
        int index = (fAttributeListHandle + i) & CHUNK_MASK;
        return fStringPool.toString(fAttName[chunk][index]);
    }

    /** Returns the URI of an attribute in this list (by position). */
    public String getURI(int i) {
        if (i < 0 || i >= fAttributeListLength)
            return null;
        int chunk = (fAttributeListHandle + i) >> CHUNK_SHIFT;
        int index = (fAttributeListHandle + i) & CHUNK_MASK;
        return fStringPool.toString(fAttURI[chunk][index]);
    }

    /**
     * Return the type of an attribute in the list (by position).
     *
     * <p>The attribute type is one of the strings "CDATA", "ID",
     * "IDREF", "IDREFS", "NMTOKEN", "NMTOKENS", "ENTITY", "ENTITIES",
     * or "NOTATION" (always in upper case).</p>
     *
     * <p>If the parser has not read a declaration for the attribute,
     * or if the parser does not report attribute types, then it must
     * return the value "CDATA" as stated in the XML 1.0 Recommentation
     * (clause 3.3.3, "Attribute-Value Normalization").</p>
     *
     * <p>For an enumerated attribute that is not a notation, the
     * parser will report the type as "NMTOKEN".</p>
     *
     * @param i The index of the attribute in the list (starting at 0).
     * @return The attribute type as a string, or
     *         null if the index is out of range.
     * @see #getLength
     * @see #getType(java.lang.String)
     */
    public String getType(int i) {
        if (i < 0 || i >= fAttributeListLength)
            return null;
        int chunk = (fAttributeListHandle + i) >> CHUNK_SHIFT;
        int index = (fAttributeListHandle + i) & CHUNK_MASK;
        int attType = fAttType[chunk][index];
        if (attType == fStringPool.addSymbol("ENUMERATION"))
            attType = fStringPool.addSymbol("NMTOKEN");
        return fStringPool.toString(attType);
    }

    /**
     * Return the value of an attribute in the list (by position).
     *
     * <p>If the attribute value is a list of tokens (IDREFS,
     * ENTITIES, or NMTOKENS), the tokens will be concatenated
     * into a single string separated by whitespace.</p>
     *
     * @param i The index of the attribute in the list (starting at 0).
     * @return The attribute value as a string, or
     *         null if the index is out of range.
     * @see #getLength
     * @see #getValue(java.lang.String)
     */
    public String getValue(int i) {
        if (i < 0 || i >= fAttributeListLength)
            return null;
        int chunk = (fAttributeListHandle + i) >> CHUNK_SHIFT;
        int index = (fAttributeListHandle + i) & CHUNK_MASK;
        return fStringPool.toString(fAttValue[chunk][index]);
    }

    /**
     * Return the type of an attribute in the list (by name).
     *
     * <p>The return value is the same as the return value for
     * getType(int).</p>
     *
     * <p>If the attribute name has a namespace prefix in the document,
     * the application must include the prefix here.</p>
     *
     * @param name The name of the attribute.
     * @return The attribute type as a string, or null if no
     *         such attribute exists.
     * @see #getType(int)
     */
    public String getType(String name) {
        int nameIndex = fStringPool.addSymbol(name);
        if (nameIndex == -1)
            return null;
        int chunk = fAttributeListHandle >> CHUNK_SHIFT;
        int index = fAttributeListHandle & CHUNK_MASK;
        for (int i = 0; i < fAttributeListLength; i++) {
            if (fStringPool.equalNames(fAttName[chunk][index], nameIndex)) {
                int attType = fAttType[chunk][index];
                if (attType == fStringPool.addSymbol("ENUMERATION"))
                    attType = fStringPool.addSymbol("NMTOKEN");
                return fStringPool.toString(attType);
            }
            if (++index == CHUNK_SIZE) {
                chunk++;
                index = 0;
            }
        }
        return null;
    }

    /**
     * Return the value of an attribute in the list (by name).
     *
     * <p>The return value is the same as the return value for
     * getValue(int).</p>
     *
     * <p>If the attribute name has a namespace prefix in the document,
     * the application must include the prefix here.</p>
     *
     * @param i The index of the attribute in the list.
     * @return The attribute value as a string, or null if
     *         no such attribute exists.
     * @see #getValue(int)
     */
    public String getValue(String name) {
        int nameIndex = fStringPool.addSymbol(name);
        if (nameIndex == -1)
            return null;
        int chunk = fAttributeListHandle >> CHUNK_SHIFT;
        int index = fAttributeListHandle & CHUNK_MASK;
        for (int i = 0; i < fAttributeListLength; i++) {
            if (fStringPool.equalNames(fAttName[chunk][index], nameIndex))
                return fStringPool.toString(fAttValue[chunk][index]);
            if (++index == CHUNK_SIZE) {
                chunk++;
                index = 0;
            }
        }
        return null;
    }

    //
    // Private methods
    //

    /* Expand our internal data structures as needed. */
    private boolean ensureCapacity(int chunk, int index) {

        try {
            return fAttName[chunk][index] != 0;
        } catch (ArrayIndexOutOfBoundsException ex) {
            int[][] newIntArray = new int[chunk * 2][];
            System.arraycopy(fAttPrefix, 0, newIntArray, 0, chunk);
            fAttPrefix = newIntArray;
            newIntArray = new int[chunk * 2][];
            System.arraycopy(fAttLocalpart, 0, newIntArray, 0, chunk);
            fAttLocalpart = newIntArray;
            newIntArray = new int[chunk * 2][];
            System.arraycopy(fAttName, 0, newIntArray, 0, chunk);
            fAttName = newIntArray;
            newIntArray = new int[chunk * 2][];
            System.arraycopy(fAttURI, 0, newIntArray, 0, chunk);
            fAttURI = newIntArray;
            newIntArray = new int[chunk * 2][];
            System.arraycopy(fAttValue, 0, newIntArray, 0, chunk);
            fAttValue = newIntArray;
            newIntArray = new int[chunk * 2][];
            System.arraycopy(fAttType, 0, newIntArray, 0, chunk);
            fAttType = newIntArray;
            byte[][] newByteArray = new byte[chunk * 2][];
            System.arraycopy(fAttFlags, 0, newByteArray, 0, chunk);
            fAttFlags = newByteArray;
        } catch (NullPointerException ex) {
        }
        fAttPrefix[chunk] = new int[CHUNK_SIZE];
        fAttLocalpart[chunk] = new int[CHUNK_SIZE];
        fAttName[chunk] = new int[CHUNK_SIZE];
        fAttURI[chunk] = new int[CHUNK_SIZE];
        fAttValue[chunk] = new int[CHUNK_SIZE];
        fAttType[chunk] = new int[CHUNK_SIZE];
        fAttFlags[chunk] = new byte[CHUNK_SIZE];
        return true;

    } // ensureCapacity(int,int):boolean

} // class XMLAttrList