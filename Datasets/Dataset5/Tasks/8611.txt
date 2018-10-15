aValidator = (XSSimpleType)tempAttDecl.getTypeDefinition();

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001, 2002 The Apache Software Foundation.
 * All rights reserved.
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

package org.apache.xerces.impl.xs.identity;

import org.apache.xerces.impl.xs.XSAttributeDecl;
import org.apache.xerces.impl.xs.XSAttributeUseImpl;
import org.apache.xerces.impl.xs.XSAttributeGroupDecl;
import org.apache.xerces.impl.xs.XSElementDecl;
import org.apache.xerces.impl.xs.XSTypeDecl;
import org.apache.xerces.impl.xs.XSComplexTypeDecl;
import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.xs.SchemaGrammar;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xpath.*;
import org.apache.xerces.util.IntStack;
import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.xni.NamespaceContext;
import org.apache.xerces.xni.XNIException;
import org.apache.xerces.xni.QName;
import org.apache.xerces.xni.XMLAttributes;
import org.apache.xerces.xni.XMLString;

/**
 * XPath matcher.
 *
 * @author Andy Clark, IBM
 *
 * @version $Id$
 */
public class XPathMatcher {

    //
    // Constants
    //

    // debugging

    /** Compile to true to debug everything. */
    protected static final boolean DEBUG_ALL = false;

    /** Compile to true to debug method callbacks. */
    protected static final boolean DEBUG_METHODS = false || DEBUG_ALL;

    /** Compile to true to debug important method callbacks. */
    protected static final boolean DEBUG_METHODS2 = false || DEBUG_METHODS || DEBUG_ALL;

    /** Compile to true to debug the <em>really</em> important methods. */
    protected static final boolean DEBUG_METHODS3 = false || DEBUG_METHODS || DEBUG_ALL;

    /** Compile to true to debug match. */
    protected static final boolean DEBUG_MATCH = false || DEBUG_ALL;

    /** Compile to true to debug step index stack. */
    protected static final boolean DEBUG_STACK = false || DEBUG_ALL;

    /** Don't touch this value unless you add more debug constants. */
    protected static final boolean DEBUG_ANY = DEBUG_METHODS ||
                                               DEBUG_METHODS2 ||
                                               DEBUG_METHODS3 ||
                                               DEBUG_MATCH ||
                                               DEBUG_STACK;

    //
    // Data
    //

    /** XPath location path. */
    private XPath.LocationPath[] fLocationPaths;

    /** Application preference to buffer content or not. */
    private boolean fShouldBufferContent;

    /** True if should buffer character content <em>at this time</em>. */
    private boolean fBufferContent;

    /** Buffer to hold match text. */
    private StringBuffer fMatchedBuffer = new StringBuffer();

    /** True if XPath has been matched. */
    private boolean[] fMatched;

    /** The matching string. */
    private String fMatchedString;

    /** Integer stack of step indexes. */
    private IntStack[] fStepIndexes;

    /** Current step. */
    private int[] fCurrentStep;

    /**
     * No match depth. The value of this field will be zero while
     * matching is successful for the given xpath expression.
     */
    private int [] fNoMatchDepth;

    // Xerces 1.x framework

    /** Symbol table. */
    protected SymbolTable fSymbolTable;

    /** Namespace scope. */
    /*** REVISIT:  do we need this?  -NG
    protected NamespaceContext fNamespacesScope;
    */

    // the Identity constraint we're the matcher for.  Only
    // used for selectors!
    protected IdentityConstraint fIDConstraint;

    //
    // Constructors
    //

    /**
     * Constructs an XPath matcher that implements a document fragment
     * handler.
     *
     * @param xpath   The xpath.
     */
    public XPathMatcher(XPath xpath) {
        this(xpath, false, null);
    } // <init>(XPath)

    /**
     * Constructs an XPath matcher that implements a document fragment
     * handler.
     *
     * @param xpath   The xpath.
     * @param shouldBufferContent True if the matcher should buffer the
     *                            matched content.
     * @param idConstraint:  the identity constraint we're matching for;
     *      null unless it's a Selector.
     */
    public XPathMatcher(XPath xpath, boolean shouldBufferContent, IdentityConstraint idConstraint) {
        fLocationPaths = xpath.getLocationPaths();
        fShouldBufferContent = shouldBufferContent;
        fIDConstraint = idConstraint;
        fStepIndexes = new IntStack[fLocationPaths.length];
        for(int i=0; i<fStepIndexes.length; i++) fStepIndexes[i] = new IntStack();
        fCurrentStep = new int[fLocationPaths.length];
        fNoMatchDepth = new int[fLocationPaths.length];
        fMatched = new boolean[fLocationPaths.length];
        if (DEBUG_METHODS) {
            System.out.println(toString()+"#<init>()");
        }
    } // <init>(XPath,boolean)

    //
    // Public methods
    //

    /** Returns true if XPath has been matched. */
    public boolean isMatched() {
        // xpath has been matched if any one of the members of the union have matched.
        for (int i=0; i < fLocationPaths.length; i++)
            if (fMatched[i]) return true;
        return false;
    } // isMatched():boolean

    // returns whether this XPathMatcher was matching a Selector
    public boolean getIsSelector() {
        return (fIDConstraint == null);
    } // end getIsSelector():boolean

    // returns the ID constraint
    public IdentityConstraint getIDConstraint() {
        return fIDConstraint;
    } // end getIDConstraint():IdentityConstraint

    /** Returns the matched string. */
    public String getMatchedString() {
        return fMatchedString;
    } // getMatchedString():String

    //
    // Protected methods
    //

    /**
     * This method is called when the XPath handler matches the
     * XPath expression. Subclasses can override this method to
     * provide default handling upon a match.
     */
    protected void matched(String content, XSSimpleType val, boolean isNil) throws XNIException {
        if (DEBUG_METHODS3) {
            System.out.println(toString()+"#matched(\""+normalize(content)+"\")");
        }
    } // matched(String content, XSSimpleType val)

    //
    // ~XMLDocumentFragmentHandler methods
    //

    /**
     * The start of the document fragment.
     *
     * @param context The namespace scope in effect at the
     *                start of this document fragment.
     *
     * @throws XNIException Thrown by handler to signal an error.
     */
    public void startDocumentFragment(SymbolTable symbolTable)
        throws XNIException {
        if (DEBUG_METHODS) {
            System.out.println(toString()+"#startDocumentFragment("+
                               //"stringPool="+stringPool+','+
                               ")");
        }

        // reset state
        clear();
        for(int i = 0; i < fLocationPaths.length; i++) {
            fStepIndexes[i].clear();
            fCurrentStep[i] = 0;
            fNoMatchDepth[i] = 0;
            fMatched[i]=false;
        }

        // keep values
        /****
        fNamespacesScope = context;
        */
        fSymbolTable = symbolTable;

    } // startDocumentFragment(NamespaceContext)

    /**
     * The start of an element. If the document specifies the start element
     * by using an empty tag, then the startElement method will immediately
     * be followed by the endElement method, with no intervening methods.
     *
     * @param element    The name of the element.
     * @param attributes The element attributes.
     * @param elementDecl: The element declaration for the element
     *
     * @throws SAXException Thrown by handler to signal an error.
     */
    public void startElement(QName element, XMLAttributes attributes,
                             XSElementDecl elementDecl)
        throws XNIException {
        if (DEBUG_METHODS2) {
            System.out.println(toString()+"#startElement("+
                               "element={"+element+"},"+
                               "attributes=..."+attributes+
                               ")");
        }

        for(int i = 0; i < fLocationPaths.length; i++) {
            // push context
            int startStep = fCurrentStep[i];
            fStepIndexes[i].push(startStep);

            // try next xpath, if not matching
            if (fMatched[i] || fNoMatchDepth[i] > 0) {
                fNoMatchDepth[i]++;
                continue;
            }

            if (DEBUG_STACK) {
                System.out.println(toString()+": "+fStepIndexes[i]);
            }

            // consume self::node() steps
            XPath.Step[] steps = fLocationPaths[i].steps;
            while (fCurrentStep[i] < steps.length &&
                    steps[fCurrentStep[i]].axis.type == XPath.Axis.SELF) {
                if (DEBUG_MATCH) {
                    XPath.Step step = steps[fCurrentStep[i]];
                    System.out.println(toString()+" [SELF] MATCHED!");
                }
                fCurrentStep[i]++;
            }
            if (fCurrentStep[i] == steps.length) {
                if (DEBUG_MATCH) {
                    System.out.println(toString()+" XPath MATCHED!");
                }
                fMatched[i] = true;
                int j=0;
                for(; j<i && !fMatched[j]; j++);
                if(j==i)
                    fBufferContent = fShouldBufferContent;
                continue;
            }

            // now if the current step is a descendant step, we let the next
            // step do its thing; if it fails, we reset ourselves
            // to look at this step for next time we're called.
            // so first consume all descendants:
            int descendantStep = fCurrentStep[i];
            while(fCurrentStep[i] < steps.length && steps[fCurrentStep[i]].axis.type == XPath.Axis.DESCENDANT) {
                if (DEBUG_MATCH) {
                    XPath.Step step = steps[fCurrentStep[i]];
                    System.out.println(toString()+" [DESCENDANT] MATCHED!");
                }
                fCurrentStep[i]++;
            }
            if (fCurrentStep[i] == steps.length) {
                if (DEBUG_MATCH) {
                    System.out.println(toString()+" XPath DIDN'T MATCH!");
                }
                fNoMatchDepth[i]++;
                if (DEBUG_MATCH) {
                    System.out.println(toString()+" [CHILD] after NO MATCH");
                }
                continue;
            }

            // match child::... step, if haven't consumed any self::node()
            if ((fCurrentStep[i] == startStep || fCurrentStep[i] > descendantStep) &&
                steps[fCurrentStep[i]].axis.type == XPath.Axis.CHILD) {
                XPath.Step step = steps[fCurrentStep[i]];
                XPath.NodeTest nodeTest = step.nodeTest;
                if (DEBUG_MATCH) {
                    System.out.println(toString()+" [CHILD] before");
                }
                if (nodeTest.type == XPath.NodeTest.QNAME) {
                    if (!nodeTest.name.equals(element)) {
                        if(fCurrentStep[i] > descendantStep) {
                            fCurrentStep[i] = descendantStep;
                            continue;
                        }
                        fNoMatchDepth[i]++;
                        if (DEBUG_MATCH) {
                            System.out.println(toString()+" [CHILD] after NO MATCH");
                        }
                        continue;
                    }
                }
                fCurrentStep[i]++;
                if (DEBUG_MATCH) {
                    System.out.println(toString()+" [CHILD] after MATCHED!");
                }
            }
            if (fCurrentStep[i] == steps.length) {
                fMatched[i] = true;
                int j=0;
                for(; j<i && !fMatched[j]; j++);
                if(j==i)
                    fBufferContent = fShouldBufferContent;
                continue;
            }

            // match attribute::... step
            if (fCurrentStep[i] < steps.length &&
                steps[fCurrentStep[i]].axis.type == XPath.Axis.ATTRIBUTE) {
                if (DEBUG_MATCH) {
                    System.out.println(toString()+" [ATTRIBUTE] before");
                }
                int attrCount = attributes.getLength();
                if (attrCount > 0) {
                    XPath.NodeTest nodeTest = steps[fCurrentStep[i]].nodeTest;
                    QName aname = new QName(); // REVISIT: cache this

                    // Get the list of attributes from the element decl.
                    // REVISIT - is this correct?   This is what was done in xerces-1,
                    // but is it right?
                    XSAttributeGroupDecl attrGrp = null;
                    if (elementDecl != null) {
                        XSTypeDecl type = elementDecl.fType;
                        if (type != null) {
                          if (type.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
                            XSComplexTypeDecl ctype = (XSComplexTypeDecl)type;
                            attrGrp = ctype.getAttrGrp();
                          }
                        }
                    }

                    for (int aindex = 0; aindex < attrCount; aindex++) {
                        attributes.getName(aindex, aname);
                        if (nodeTest.type != XPath.NodeTest.QNAME ||
                            nodeTest.name.equals(aname)) {
                            fCurrentStep[i]++;
                            if (fCurrentStep[i] == steps.length) {
                                fMatched[i] = true;
                                int j=0;
                                for(; j<i && !fMatched[j]; j++);
                                if(j==i) {
                                    String avalue = attributes.getValue(aindex);
                                    fMatchedString = avalue;
                                    // now, we have to go on the hunt for
                                    // datatype validator; not an easy or pleasant task...

                                    XSSimpleType aValidator = null;
                                    if (attrGrp != null) {
                                      XSAttributeUseImpl tempAttUse = attrGrp.getAttributeUse(aname.uri, aname.localpart);
                                      if (tempAttUse != null) {
                                        XSAttributeDecl tempAttDecl = tempAttUse.fAttrDecl;
                                        aValidator = tempAttDecl.fType;
                                      }
                                    }
                                    matched(fMatchedString, aValidator, false);
                                }
                            }
                            break;
                        }
                    }
                }
                if (!fMatched[i]) {
                    if(fCurrentStep[i] > descendantStep) {
                        fCurrentStep[i] = descendantStep;
                        continue;
                    }
                    fNoMatchDepth[i]++;
                    if (DEBUG_MATCH) {
                        System.out.println(toString()+" [ATTRIBUTE] after");
                    }
                    continue;
                }
                if (DEBUG_MATCH) {
                    System.out.println(toString()+" [ATTRIBUTE] after MATCHED!");
                }
            }
        }

    } // startElement(QName,XMLAttrList,int)

    /** Character content. */
    public void characters(XMLString text)
        throws XNIException {
        if (DEBUG_METHODS) {
            System.out.println(toString()+"#characters("+
                               "text="+normalize(text.toString())+
                               ")");
        }

        // collect match content
        // so long as one of our paths is matching, store the content
        for(int i=0; i<fLocationPaths.length; i++)
            if (fBufferContent && fNoMatchDepth[i] == 0) {
                if (!DEBUG_METHODS && DEBUG_METHODS2) {
                    System.out.println(toString()+"#characters("+
                                   "text="+normalize(text.toString())+
                                   ")");
                }
                fMatchedBuffer.append(text);
                break;
            }

    } // characters(char[],int,int)

    /**
     * The end of an element.
     *
     * @param element The name of the element.
     * @param eDecl:  the element declaration
     *
     * @throws SAXException Thrown by handler to signal an error.
     */
    public void endElement(QName element, XSElementDecl eDecl) {
        if (DEBUG_METHODS2) {
            System.out.println(toString()+"#endElement("+
                               "element={"+element+"},"+
                               "ID constraint="+fIDConstraint+
                               ")");
        }
        for(int i = 0; i<fLocationPaths.length; i++) {
            // don't do anything, if not matching
            if (fNoMatchDepth[i] > 0) {
                fNoMatchDepth[i]--;
            }

            // signal match, if appropriate
            else {
                int j=0;
                for(; j<i && !fMatched[j]; j++);
                if (j<i) continue;
                if (fBufferContent) {
                    fBufferContent = false;
                    fMatchedString = fMatchedBuffer.toString();
                    // REVISIT: cache this.
                    // REVISIT:  make sure type's from same schema!
                    // REVISIT:  make sure type is simple!
                    XSSimpleType val=null;

                    if (eDecl!=null) {
                      XSTypeDecl type = eDecl.fType;
                      if (type != null) {
                        if (type.getTypeCategory() == XSTypeDecl.COMPLEX_TYPE) {
                          XSComplexTypeDecl ctype = (XSComplexTypeDecl)type;
                          val = (XSSimpleType)ctype.getSimpleType();
                        }
                        else {
                          val = (XSSimpleType)(type);
                        }
                      }
                    }

                    if(eDecl != null) {
                        matched(fMatchedString, val, (eDecl.getIsNillable()));
                    } else
                        matched(fMatchedString, val, false);

                }
                clear();
            }

            // go back a step
            fCurrentStep[i] = fStepIndexes[i].pop();

            if (DEBUG_STACK) {
                System.out.println(toString()+": "+fStepIndexes[i]);
            }
        }

    } // endElement(QName)

    /**
     * The end of the document fragment.
     *
     * @throws SAXException Thrown by handler to signal an error.
     */
    public void endDocumentFragment() throws XNIException {
        if (DEBUG_METHODS) {
            System.out.println(toString()+"#endDocumentFragment()");
        }
        clear();
    } // endDocumentFragment()

    //
    // Object methods
    //

    /** Returns a string representation of this object. */
    public String toString() {
        /***
        return fLocationPath.toString();
        /***/
        StringBuffer str = new StringBuffer();
        String s = super.toString();
        int index2 = s.lastIndexOf('.');
        if (index2 != -1) {
            s = s.substring(index2 + 1);
        }
        str.append(s);
        for(int i =0;i<fLocationPaths.length; i++) {
            str.append('[');
            XPath.Step[] steps = fLocationPaths[i].steps;
            for (int j = 0; j < steps.length; j++) {
                if (j == fCurrentStep[i]) {
                    str.append('^');
                }
                str.append(steps[i].toString());
                if (j < steps.length - 1) {
                    str.append('/');
                }
            }
            if (fCurrentStep[i] == steps.length) {
                str.append('^');
            }
            str.append(']');
            str.append(',');
        }
        return str.toString();
    } // toString():String

    //
    // Private methods
    //

    /** Clears the match values. */
    private void clear() {
        fBufferContent = false;
        fMatchedBuffer.setLength(0);
        fMatchedString = null;
        for(int i = 0; i<fLocationPaths.length; i++)
            fMatched[i] = false;
    } // clear()

    /** Normalizes text. */
    private String normalize(String s) {
        StringBuffer str = new StringBuffer();
        int length = s.length();
        for (int i = 0; i < length; i++) {
            char c = s.charAt(i);
            switch (c) {
                case '\n': {
                    str.append("\\n");
                    break;
                }
                default: {
                    str.append(c);
                }
            }
        }
        return str.toString();
    } // normalize(String):String

    //
    // MAIN
    //

    // NOTE: The main of this class is here for debugging purposes.
    //       However, javac (JDK 1.1.8) has an internal compiler
    //       error when compiling. Jikes has no problem, though.
    //
    //       If you want to use this main, use Jikes to compile but
    //       *never* check in this code to CVS without commenting it
    //       out. -Ac

    /** Main program. */
    /***
    public static void main(String[] argv) throws XNIException {

        if (DEBUG_ANY) {
            for (int i = 0; i < argv.length; i++) {
                final String expr = argv[i];
                final XPath xpath = new XPath(expr, symbols, null);
                final XPathMatcher matcher = new XPathMatcher(xpath, true);
                org.apache.xerces.parsers.SAXParser parser =
                    new org.apache.xerces.parsers.SAXParser(symbols) {
                    public void startDocument() throws XNIException {
                        matcher.startDocumentFragment(symbols, null);
                    }
                    public void startElement(QName element, XMLAttrList attributes, int handle) throws XNIException {
                        matcher.startElement(element, attributes, handle);
                    }
                    public void characters(char[] ch, int offset, int length) throws XNIException {
                        matcher.characters(ch, offset, length);
                    }
                    public void endElement(QName element) throws XNIException {
                        matcher.endElement(element);
                    }
                    public void endDocument() throws XNIException {
                        matcher.endDocumentFragment();
                    }
                };
                System.out.println("#### argv["+i+"]: \""+expr+"\" -> \""+xpath.toString()+'"');
                final String uri = argv[++i];
                System.out.println("#### argv["+i+"]: "+uri);
                parser.parse(uri);
            }
        }

    } // main(String[])
    /***/

} // class XPathMatcher