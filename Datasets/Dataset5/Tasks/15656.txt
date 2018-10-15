package org.apache.xerces.impl.xpath;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2000,2001 The Apache Software Foundation.
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

package org.apache.xerces.impl.v2.xpath;

import org.apache.xerces.util.SymbolTable;
import org.apache.xerces.util.XMLChar;
import org.apache.xerces.xni.NamespaceContext;
import org.apache.xerces.xni.QName;

/**
 * Bare minimum XPath parser.
 *
 * @author Andy Clark, IBM
 * @version $Id$
 */
public class XPath {

    //
    // Constants
    //

    private static final boolean DEBUG_ALL = false;

    private static final boolean DEBUG_XPATH_PARSE = DEBUG_ALL || false;

    private static final boolean DEBUG_ANY = DEBUG_XPATH_PARSE;

    //
    // Data
    //

    /** Expression. */
    protected String fExpression;

    /** Symbol table. */
    protected SymbolTable fSymbolTable;

    /** Location paths. */
    protected LocationPath[] fLocationPaths;

    //
    // Constructors
    //

    /** Constructs an XPath object from the specified expression. */
    public XPath(String xpath, SymbolTable symbolTable,
                 NamespaceContext context)
        throws XPathException {
        fExpression = xpath;
        fSymbolTable = symbolTable;
        parseExpression(context);
    } // <init>(String,SymbolTable,NamespaceContext)

    //
    // Public methods
    //

    /**
     * Returns a representation of all location paths for this XPath.
     * XPath = locationPath ( '|' locationPath)
     */
    public LocationPath[] getLocationPaths() {
        LocationPath[] ret=new LocationPath[fLocationPaths.length];
        for (int i=0;i<fLocationPaths.length;i++){
            ret[i]=(LocationPath)fLocationPaths[i].clone();
        }
        return ret;
    } // getLocationPath(LocationPath)

    /** Returns a representation of the first location path for this XPath. */
    public LocationPath getLocationPath() {
        return (LocationPath)fLocationPaths[0].clone();
    } // getLocationPath(LocationPath)

    //
    // Object methods
    //

    /** Returns a string representation of this object. */
    public String toString() {
        StringBuffer buf=new StringBuffer();
        for (int  i=0;i<fLocationPaths.length;i++){
            if (i>0){
                buf.append("|");
            }
            buf.append(fLocationPaths[i].toString());
        }
        return buf.toString();
    } // toString():String

    //
    // Private methods
    //

    /**
     * This method is implemented by using the XPathExprScanner and
     * examining the list of tokens that it returns.
     */
    private void parseExpression(final NamespaceContext context)
        throws XPathException {

        // tokens
        final XPath.Tokens xtokens = new XPath.Tokens(fSymbolTable);

        // scanner
        XPath.Scanner scanner = new XPath.Scanner(fSymbolTable) {
            protected void addToken(XPath.Tokens tokens, int token)
                throws XPathException {
                if (
                    token == XPath.Tokens.EXPRTOKEN_ATSIGN ||
                    token == XPath.Tokens.EXPRTOKEN_AXISNAME_ATTRIBUTE ||
                    token == XPath.Tokens.EXPRTOKEN_AXISNAME_CHILD ||
                    //token == XPath.Tokens.EXPRTOKEN_AXISNAME_SELF ||
                    token == XPath.Tokens.EXPRTOKEN_DOUBLE_COLON ||
                    //token == XPath.Tokens.EXPRTOKEN_NAMETEST_ANY ||
                    token == XPath.Tokens.EXPRTOKEN_NAMETEST_QNAME ||
                    //token == XPath.Tokens.EXPRTOKEN_NODETYPE_NODE ||
                    token == XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH ||
                    token == XPath.Tokens.EXPRTOKEN_PERIOD ||
                    //added to conform to PR Spec
                    token == XPath.Tokens.EXPRTOKEN_NAMETEST_ANY ||
                    token == XPath.Tokens.EXPRTOKEN_NAMETEST_NAMESPACE ||
                    token == XPath.Tokens.EXPRTOKEN_OPERATOR_DOUBLE_SLASH ||
                    token == XPath.Tokens.EXPRTOKEN_OPERATOR_UNION
                    //
                    ) {
                    super.addToken(tokens, token);
                    return;
                }
                StringBuffer str = new StringBuffer();
                str.append("token not supported: ");
                String tokenName = tokens.getTokenName(token);
                if (tokenName != null) {
                    str.append('"');
                    str.append(tokenName);
                    str.append('"');
                }
                else {
                    str.append('(');
                    str.append(token);
                    str.append(')');
                }
                String message = str.toString();
                throw new XPathException(message);
            }
        };

        int length = fExpression.length();
        /***/
        boolean success = scanner.scanExpr(fSymbolTable,
                                           xtokens, fExpression, 0, length);
        //fTokens.dumpTokens();
        java.util.Vector stepsVector = new java.util.Vector();
        java.util.Vector locationPathsVector= new java.util.Vector();
        int tokenCount = xtokens.getTokenCount();
        boolean firstTokenOfLocationPath=true;

        final String emptySymbol = fSymbolTable.addSymbol("");
        for (int i = 0; i < tokenCount; i++) {
            int token = xtokens.getToken(i);
            boolean isNamespace=false;

            switch (token) {
                case  XPath.Tokens.EXPRTOKEN_OPERATOR_UNION :{
                    if (i == 0) {
                        throw new XPathException("not allowed to have '|' at the beginning of an xpath value");
                    }

                    int size = stepsVector.size();
                    if (size == 0) {
                        throw new XPathException("not allowed to have '||'");
                    }
                    Step[] steps = new Step[size];
                    stepsVector.copyInto(steps);
                    // add location path
                    locationPathsVector.addElement(new LocationPath(steps));
                    //reset stepsVector
                    stepsVector.removeAllElements();
                    firstTokenOfLocationPath=true;
                    break;
                }

                case XPath.Tokens.EXPRTOKEN_AXISNAME_ATTRIBUTE: {
                    // consume "::" token and drop through
                    i++;
                }
                case XPath.Tokens.EXPRTOKEN_ATSIGN: {
                    // consume QName token
                    if (i == tokenCount - 1) {
                        throw new XPathException("missing attribute name");
                    }
                    token = xtokens.getToken(++i);

                    if (token != XPath.Tokens.EXPRTOKEN_NAMETEST_QNAME
                        && token!= XPath.Tokens.EXPRTOKEN_NAMETEST_ANY
                        && token!=  XPath.Tokens.EXPRTOKEN_NAMETEST_NAMESPACE) {
                        throw new XPathException("expected \""+xtokens.getTokenName(XPath.Tokens.EXPRTOKEN_NAMETEST_QNAME)+
                                                 "\" or \""+xtokens.getTokenName( XPath.Tokens.EXPRTOKEN_NAMETEST_ANY)+
                                                 "\" or \""+xtokens.getTokenName( XPath.Tokens.EXPRTOKEN_NAMETEST_NAMESPACE)+
                                                 "\", found "+xtokens.getTokenName(token));
                    }
                    boolean isNamespaceAtt=false;
                    switch (token)
                    {
                        case XPath.Tokens.EXPRTOKEN_NAMETEST_ANY:{
                            Axis axis = new Axis(Axis.ATTRIBUTE);
                            NodeTest nodeTest = new NodeTest(NodeTest.WILDCARD);
                            Step step = new Step(axis, nodeTest);
                            stepsVector.addElement(step);
                            break;
                        }
                        case XPath.Tokens.EXPRTOKEN_NAMETEST_NAMESPACE:{
                            isNamespaceAtt=true;
                    }
                        case XPath.Tokens.EXPRTOKEN_NAMETEST_QNAME:{

                    token = xtokens.getToken(++i);
                    String prefix = xtokens.getTokenString(token);
                    String uri = null;
                    if (context != null && prefix != emptySymbol) {
                        uri = context.getURI(prefix);
                    }
                    if (prefix != emptySymbol && context != null && uri == null) {
                        throw new XPathException("prefix "+prefix+" not bound to namespace URI");
                    }

                            if (isNamespaceAtt)
                            {
                                // build step
                                Axis axis = new Axis(Axis.ATTRIBUTE);
                                NodeTest nodeTest = new NodeTest(prefix, uri);
                                Step step = new Step(axis, nodeTest);
                                stepsVector.addElement(step);
                                break;
                            }

                    token = xtokens.getToken(++i);
                    String localpart = xtokens.getTokenString(token);
                    String rawname = prefix != emptySymbol
                                   ? fSymbolTable.addSymbol(prefix+':'+localpart)
                                   : localpart;

                    // build step
                    Axis axis = new Axis(Axis.ATTRIBUTE);
                    NodeTest nodeTest = new NodeTest(new QName(prefix, localpart, rawname, uri));
                    Step step = new Step(axis, nodeTest);
                    stepsVector.addElement(step);
                    break;
                }
                    }
                    firstTokenOfLocationPath=false;
                    break;
                }
                /***
                case XPath.Tokens.EXPRTOKEN_AXISNAME_SELF: {
                    break;
                }
                /***/
                case XPath.Tokens.EXPRTOKEN_DOUBLE_COLON: {
                    // should never have a bare double colon
                    throw new XPathException("Not allowed to have double colon here");
                }
                /***
                case XPath.Tokens.EXPRTOKEN_NAMETEST_ANY: {
                    break;
                }
                /***/
                case XPath.Tokens.EXPRTOKEN_AXISNAME_CHILD: {

                    // consume "::" token and drop through
                    i++;
                    if (i == tokenCount - 1) {
                        throw new XPathException("expected step following '"
                            +xtokens.getTokenName(XPath.Tokens.EXPRTOKEN_AXISNAME_CHILD)+"::'");
                    }
                    firstTokenOfLocationPath=false;
                    break;
                }
                case XPath.Tokens.EXPRTOKEN_NAMETEST_ANY:{
                    Axis axis = new Axis(Axis.CHILD);
                    NodeTest nodeTest = new NodeTest(NodeTest.WILDCARD);
                    Step step = new Step(axis, nodeTest);
                    stepsVector.addElement(step);
                    firstTokenOfLocationPath=false;
                    break;
                }

                case XPath.Tokens.EXPRTOKEN_NAMETEST_NAMESPACE:{
                    isNamespace=true;
                }
                case XPath.Tokens.EXPRTOKEN_NAMETEST_QNAME: {
                    // consume QName token
                    token = xtokens.getToken(++i);
                    String prefix = xtokens.getTokenString(token);
                    String uri = null;
                    if (context != null && prefix != emptySymbol) {
                        uri = context.getURI(prefix);
                    }
                    if (prefix != emptySymbol && context != null && uri == null) {
                        throw new XPathException("prefix "+prefix+" not bound to namespace URI");
                    }

                    if (isNamespace)
                    {
                        // build step
                        Axis axis = new Axis(Axis.CHILD);
                        NodeTest nodeTest = new NodeTest(prefix, uri);
                        Step step = new Step(axis, nodeTest);
                        stepsVector.addElement(step);
                        break;
                    }

                    token = xtokens.getToken(++i);
                    String localpart = xtokens.getTokenString(token);
                    String rawname = prefix != emptySymbol
                                   ? fSymbolTable.addSymbol(prefix+':'+localpart)
                                   : localpart;

                    // build step
                    Axis axis = new Axis(Axis.CHILD);
                    NodeTest nodeTest = new NodeTest(new QName(prefix, localpart, rawname, uri));
                    Step step = new Step(axis, nodeTest);
                    stepsVector.addElement(step);
                    firstTokenOfLocationPath=false;
                    break;
                }
                /***
                case XPath.Tokens.EXPRTOKEN_NODETYPE_NODE: {
                    break;
                }
                /***/


                case XPath.Tokens.EXPRTOKEN_PERIOD: {
                    // build step
                    Axis axis = new Axis(Axis.SELF);
                    NodeTest nodeTest = new NodeTest(NodeTest.NODE);
                    Step step = new Step(axis, nodeTest);
                    stepsVector.addElement(step);

                    if (firstTokenOfLocationPath && i+1<tokenCount){
                        token=xtokens.getToken(i+1);
                        if (token == XPath.Tokens.EXPRTOKEN_OPERATOR_DOUBLE_SLASH){
                            i++;
                            if (i == tokenCount - 1) {
                                throw new XPathException("expected step following '//'");
                            }
                            if (i+1<tokenCount)	{
                                token=xtokens.getToken(i+1);
                                if (token==XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH)
                                    throw new XPathException("'/' not allowed after '//'");
                            }
                            // build step
                            axis = new Axis(Axis.DESCENDANT);
                            nodeTest = new NodeTest(NodeTest.NODE);
                            step = new Step(axis, nodeTest);
                            stepsVector.addElement(step);
                        }
                    }
                    firstTokenOfLocationPath=false;
                    break;
                }

                case XPath.Tokens.EXPRTOKEN_OPERATOR_DOUBLE_SLASH:{
                    throw new XPathException("'//' only allowed after '.' at the beginning of an xpath");
                }
                case XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH: {
                    if (i == 0) {
                        throw new XPathException("not allowed to have '/' at the beginning of an xpath value");
                    }
                    // keep on truckin'
                    if (firstTokenOfLocationPath) {
                        throw new XPathException("not allowed to select the root");
                    }
                    if (i == tokenCount - 1) {
                        throw new XPathException("expected step following '/'");
                    }
                    firstTokenOfLocationPath=false;
                    break;
                }
                default:
                    firstTokenOfLocationPath=false;
            }
        }

        int size = stepsVector.size();
        if (size == 0) {
            if (locationPathsVector.size()==0)
            throw new XPathException("empty xpath expression");
            else
                throw new XPathException("xpath cannot end with '|'");
        }
        Step[] steps = new Step[size];
        stepsVector.copyInto(steps);
        locationPathsVector.addElement(new LocationPath(steps));

        // save location path
        fLocationPaths=new LocationPath[locationPathsVector.size()];
        locationPathsVector.copyInto(fLocationPaths);


        if (DEBUG_XPATH_PARSE) {
            System.out.println(">>> "+fLocationPaths);
        }

    } // parseExpression(SymbolTable,NamespaceContext)

    //
    // Classes
    //

    // location path information

    /**
     * A location path representation for an XPath expression.
     *
     * @author Andy Clark, IBM
     */
    public static class LocationPath
        implements Cloneable {

        //
        // Data
        //

        /** List of steps. */
        public Step[] steps;

        //
        // Constructors
        //

        /** Creates a location path from a series of steps. */
        public LocationPath(Step[] steps) {
            this.steps = steps;
        } // <init>(Step[])

        /** Copy constructor. */
        protected LocationPath(LocationPath path) {
            steps = new Step[path.steps.length];
            for (int i = 0; i < steps.length; i++) {
                steps[i] = (Step)path.steps[i].clone();
            }
        } // <init>(LocationPath)

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {
            StringBuffer str = new StringBuffer();
            for (int i = 0; i < steps.length; i++) {
                if (i > 0	&& (steps[i-1].axis.type!=Axis.DESCENDANT
                    && steps[i].axis.type!=Axis.DESCENDANT) ){
                    str.append('/');
                }
                str.append(steps[i].toString());
            }
            // DEBUG: This code is just for debugging and should *not*
            //        be left in because it will mess up hashcodes of
            //        serialized versions of this object. -Ac
            if (false) {
                str.append('[');
                String s = super.toString();
                str.append(s.substring(s.indexOf('@')));
                str.append(']');
            }
            return str.toString();
        } // toString():String

        /** Returns a clone of this object. */
        public Object clone() {
            return new LocationPath(this);
        } // clone():Object

    } // class locationPath

    /**
     * A location path step comprised of an axis and node test.
     *
     * @author Andy Clark, IBM
     */
    public static class Step
        implements Cloneable {

        //
        // Data
        //

        /** Axis. */
        public Axis axis;

        /** Node test. */
        public NodeTest nodeTest;

        //
        // Constructors
        //

        /** Constructs a step from an axis and node test. */
        public Step(Axis axis, NodeTest nodeTest) {
            this.axis = axis;
            this.nodeTest = nodeTest;
        } // <init>(Axis,NodeTest)

        /** Copy constructor. */
        protected Step(Step step) {
            axis = (Axis)step.axis.clone();
            nodeTest = (NodeTest)step.nodeTest.clone();
        } // <init>(Step)

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {
            /***
            return axis.toString() + "::" + nodeTest.toString();
            /***/
            if (axis.type == Axis.SELF) {
                return ".";
            }
            if (axis.type == Axis.ATTRIBUTE) {
                return "@" + nodeTest.toString();
            }
            if (axis.type == Axis.CHILD) {
                return nodeTest.toString();
            }
            if (axis.type == Axis.DESCENDANT) {
                return "//";
            }
            return "??? ("+axis.type+')';
            /***/
        } // toString():String

        /** Returns a clone of this object. */
        public Object clone() {
            return new Step(this);
        } // clone():Object

    } // class Step

    /**
     * Axis.
     *
     * @author Andy Clark, IBM
     */
    public static class Axis
        implements Cloneable {

        //
        // Constants
        //

        /** Type: child. */
        public static final short CHILD = 1;

        /** Type: attribute. */
        public static final short ATTRIBUTE = 2;

        /** Type: self. */
        public static final short SELF = 3;


        /** Type: descendant. */
        public static final short DESCENDANT = 4;
        //
        // Data
        //

        /** Axis type. */
        public short type;

        //
        // Constructors
        //

        /** Constructs an axis with the specified type. */
        public Axis(short type) {
            this.type = type;
        } // <init>(short)

        /** Copy constructor. */
        protected Axis(Axis axis) {
            type = axis.type;
        } // <init>(Axis)

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {
            switch (type) {
                case CHILD: return "child";
                case ATTRIBUTE: return "attribute";
                case SELF: return "self";
                case DESCENDANT: return "descendant";
            }
            return "???";
        } // toString():String

        /** Returns a clone of this object. */
        public Object clone() {
            return new Axis(this);
        } // clone():Object

    } // class Axis

    /**
     * Node test.
     *
     * @author Andy Clark, IBM
     */
    public static class NodeTest
        implements Cloneable {

        //
        // Constants
        //

        /** Type: qualified name. */
        public static final short QNAME = 1;

        /** Type: wildcard. */
        public static final short WILDCARD = 2;

        /** Type: node. */
        public static final short NODE = 3;

        /** Type: namespace */
        public static final short NAMESPACE= 4;

        //
        // Data
        //

        /** Node test type. */
        public short type;

        /** Node qualified name. */
        public final QName name = new QName();

        //
        // Constructors
        //

        /** Constructs a node test of type WILDCARD or NODE. */
        public NodeTest(short type) {
            this.type = type;
        } // <init>(int)

        /** Constructs a node test of type QName. */
        public NodeTest(QName name) {
            this.type = QNAME;
            this.name.setValues(name);
        } // <init>(QName)
        /** Constructs a node test of type Namespace. */
        public NodeTest(String prefix, String uri) {
            this.type = NAMESPACE;
            this.name.setValues(prefix, null, null, uri);
        } // <init>(String,String)

        /** Copy constructor. */
        public NodeTest(NodeTest nodeTest) {
            type = nodeTest.type;
            name.setValues(nodeTest.name);
        } // <init>(NodeTest)

        //
        // Object methods
        //

        /** Returns a string representation of this object. */
        public String toString() {

            switch (type) {
                case QNAME: {
                    if (name.prefix.length() !=0) {
                        if (name.uri != null) {
                            return name.prefix+':'+name.localpart;
                        }
                        return "{"+name.uri+'}'+name.prefix+':'+name.localpart;
                    }
                    return name.localpart;
                }
                case NAMESPACE: {
                    if (name.prefix.length() !=0) {
                        if (name.uri != null) {
                            return name.prefix+":*";
                        }
                        return "{"+name.uri+'}'+name.prefix+":*";
                    }
                    return "???:*";
                }
                case WILDCARD: {
                    return "*";
                }
                case NODE: {
                    return "node()";
                }
            }
            return "???";

        } // toString():String

        /** Returns a clone of this object. */
        public Object clone() {
            return new NodeTest(this);
        } // clone():Object

    } // class NodeTest

    // xpath implementation

    // NOTE: The XPath implementation classes are kept internal because
    //       this implementation is just a temporary hack until a better
    //       and/or more appropriate implementation can be written.
    //       keeping the code in separate source files would "muddy" the
    //       CVS directory when it's not needed. -Ac

    /**
     * @author Glenn Marcy, IBM
     * @author Andy Clark, IBM
     *
     * @version $Id$
     */
    private static final class Tokens {

        static final boolean DUMP_TOKENS = false;

        /**
         * [28] ExprToken ::= '(' | ')' | '[' | ']' | '.' | '..' | '@' | ',' | '::'
         *                  | NameTest | NodeType | Operator | FunctionName
         *                  | AxisName | Literal | Number | VariableReference
         */
        public static final int
            EXPRTOKEN_OPEN_PAREN                    =   0,
            EXPRTOKEN_CLOSE_PAREN                   =   1,
            EXPRTOKEN_OPEN_BRACKET                  =   2,
            EXPRTOKEN_CLOSE_BRACKET                 =   3,
            EXPRTOKEN_PERIOD                        =   4,
            EXPRTOKEN_DOUBLE_PERIOD                 =   5,
            EXPRTOKEN_ATSIGN                        =   6,
            EXPRTOKEN_COMMA                         =   7,
            EXPRTOKEN_DOUBLE_COLON                  =   8,
            //
            // [37] NameTest ::= '*' | NCName ':' '*' | QName
            //
            // followed by symbol handle of NCName or QName
            //
            EXPRTOKEN_NAMETEST_ANY                  =   9,
            EXPRTOKEN_NAMETEST_NAMESPACE            =  10,
            EXPRTOKEN_NAMETEST_QNAME                =  11,
            //
            // [38] NodeType ::= 'comment' | 'text' | 'processing-instruction' | 'node'
            //
            EXPRTOKEN_NODETYPE_COMMENT              =  12,
            EXPRTOKEN_NODETYPE_TEXT                 =  13,
            EXPRTOKEN_NODETYPE_PI                   =  14,
            EXPRTOKEN_NODETYPE_NODE                 =  15,
            //
            // [32] Operator ::= OperatorName
            //                 | MultiplyOperator
            //                 | '/' | '//' | '|' | '+' | '-' | '=' | '!=' | '<' | '<=' | '>' | '>='
            // [33] OperatorName ::= 'and' | 'or' | 'mod' | 'div'
            // [34] MultiplyOperator ::= '*'
            //
            EXPRTOKEN_OPERATOR_AND                  =  16,
            EXPRTOKEN_OPERATOR_OR                   =  17,
            EXPRTOKEN_OPERATOR_MOD                  =  18,
            EXPRTOKEN_OPERATOR_DIV                  =  19,
            EXPRTOKEN_OPERATOR_MULT                 =  20,
            EXPRTOKEN_OPERATOR_SLASH                =  21,
            EXPRTOKEN_OPERATOR_DOUBLE_SLASH         =  22,
            EXPRTOKEN_OPERATOR_UNION                =  23,
            EXPRTOKEN_OPERATOR_PLUS                 =  24,
            EXPRTOKEN_OPERATOR_MINUS                =  25,
            EXPRTOKEN_OPERATOR_EQUAL                =  26,
            EXPRTOKEN_OPERATOR_NOT_EQUAL            =  27,
            EXPRTOKEN_OPERATOR_LESS                 =  28,
            EXPRTOKEN_OPERATOR_LESS_EQUAL           =  29,
            EXPRTOKEN_OPERATOR_GREATER              =  30,
            EXPRTOKEN_OPERATOR_GREATER_EQUAL        =  31,

            //EXPRTOKEN_FIRST_OPERATOR                = EXPRTOKEN_OPERATOR_AND,
            //EXPRTOKEN_LAST_OPERATOR                 = EXPRTOKEN_OPERATOR_GREATER_EQUAL,

            //
            // [35] FunctionName ::= QName - NodeType
            //
            // followed by symbol handle
            //
            EXPRTOKEN_FUNCTION_NAME                 =  32,
            //
            // [6] AxisName ::= 'ancestor' | 'ancestor-or-self'
            //                | 'attribute'
            //                | 'child'
            //                | 'descendant' | 'descendant-or-self'
            //                | 'following' | 'following-sibling'
            //                | 'namespace'
            //                | 'parent'
            //                | 'preceding' | 'preceding-sibling'
            //                | 'self'
            //
            EXPRTOKEN_AXISNAME_ANCESTOR             =  33,
            EXPRTOKEN_AXISNAME_ANCESTOR_OR_SELF     =  34,
            EXPRTOKEN_AXISNAME_ATTRIBUTE            =  35,
            EXPRTOKEN_AXISNAME_CHILD                =  36,
            EXPRTOKEN_AXISNAME_DESCENDANT           =  37,
            EXPRTOKEN_AXISNAME_DESCENDANT_OR_SELF   =  38,
            EXPRTOKEN_AXISNAME_FOLLOWING            =  39,
            EXPRTOKEN_AXISNAME_FOLLOWING_SIBLING    =  40,
            EXPRTOKEN_AXISNAME_NAMESPACE            =  41,
            EXPRTOKEN_AXISNAME_PARENT               =  42,
            EXPRTOKEN_AXISNAME_PRECEDING            =  43,
            EXPRTOKEN_AXISNAME_PRECEDING_SIBLING    =  44,
            EXPRTOKEN_AXISNAME_SELF                 =  45,
            //
            // [29] Literal ::= '"' [^"]* '"' | "'" [^']* "'"
            //
            // followed by symbol handle for literal
            //
            EXPRTOKEN_LITERAL                       =  46,
            //
            // [30] Number ::= Digits ('.' Digits?)? | '.' Digits
            // [31] Digits ::= [0-9]+
            //
            // followed by number handle
            //
            EXPRTOKEN_NUMBER                        =  47,
            //
            // [36] VariableReference ::= '$' QName
            //
            // followed by symbol handle for QName
            //
            EXPRTOKEN_VARIABLE_REFERENCE            =  48;

        public static final String[] fgTokenNames = {
            "EXPRTOKEN_OPEN_PAREN",
            "EXPRTOKEN_CLOSE_PAREN",
            "EXPRTOKEN_OPEN_BRACKET",
            "EXPRTOKEN_CLOSE_BRACKET",
            "EXPRTOKEN_PERIOD",
            "EXPRTOKEN_DOUBLE_PERIOD",
            "EXPRTOKEN_ATSIGN",
            "EXPRTOKEN_COMMA",
            "EXPRTOKEN_DOUBLE_COLON",
            "EXPRTOKEN_NAMETEST_ANY",
            "EXPRTOKEN_NAMETEST_NAMESPACE",
            "EXPRTOKEN_NAMETEST_QNAME",
            "EXPRTOKEN_NODETYPE_COMMENT",
            "EXPRTOKEN_NODETYPE_TEXT",
            "EXPRTOKEN_NODETYPE_PI",
            "EXPRTOKEN_NODETYPE_NODE",
            "EXPRTOKEN_OPERATOR_AND",
            "EXPRTOKEN_OPERATOR_OR",
            "EXPRTOKEN_OPERATOR_MOD",
            "EXPRTOKEN_OPERATOR_DIV",
            "EXPRTOKEN_OPERATOR_MULT",
            "EXPRTOKEN_OPERATOR_SLASH",
            "EXPRTOKEN_OPERATOR_DOUBLE_SLASH",
            "EXPRTOKEN_OPERATOR_UNION",
            "EXPRTOKEN_OPERATOR_PLUS",
            "EXPRTOKEN_OPERATOR_MINUS",
            "EXPRTOKEN_OPERATOR_EQUAL",
            "EXPRTOKEN_OPERATOR_NOT_EQUAL",
            "EXPRTOKEN_OPERATOR_LESS",
            "EXPRTOKEN_OPERATOR_LESS_EQUAL",
            "EXPRTOKEN_OPERATOR_GREATER",
            "EXPRTOKEN_OPERATOR_GREATER_EQUAL",
            "EXPRTOKEN_FUNCTION_NAME",
            "EXPRTOKEN_AXISNAME_ANCESTOR",
            "EXPRTOKEN_AXISNAME_ANCESTOR_OR_SELF",
            "EXPRTOKEN_AXISNAME_ATTRIBUTE",
            "EXPRTOKEN_AXISNAME_CHILD",
            "EXPRTOKEN_AXISNAME_DESCENDANT",
            "EXPRTOKEN_AXISNAME_DESCENDANT_OR_SELF",
            "EXPRTOKEN_AXISNAME_FOLLOWING",
            "EXPRTOKEN_AXISNAME_FOLLOWING_SIBLING",
            "EXPRTOKEN_AXISNAME_NAMESPACE",
            "EXPRTOKEN_AXISNAME_PARENT",
            "EXPRTOKEN_AXISNAME_PRECEDING",
            "EXPRTOKEN_AXISNAME_PRECEDING_SIBLING",
            "EXPRTOKEN_AXISNAME_SELF",
            "EXPRTOKEN_LITERAL",
            "EXPRTOKEN_NUMBER",
            "EXPRTOKEN_VARIABLE_REFERENCE"
        };

        /**
         *
         */
        private static final int INITIAL_TOKEN_COUNT = 1 << 8;
        private int[] fTokens = new int[INITIAL_TOKEN_COUNT];
        private int fTokenCount = 0;    // for writing

        private SymbolTable fSymbolTable;

        // REVISIT: Code something better here. -Ac
        private java.util.Hashtable fSymbolMapping = new java.util.Hashtable();

        // REVISIT: Code something better here. -Ac
        private java.util.Hashtable fTokenNames = new java.util.Hashtable();

        //
        // Constructors
        //

        public Tokens(SymbolTable symbolTable) {
            fSymbolTable = symbolTable;
            final String[] symbols = {
                "ancestor",     "ancestor-or-self",     "attribute",
                "child",        "descendant",           "descendant-or-self",
                "following",    "following-sibling",    "namespace",
                "parent",       "preceding",            "preceding-sibling",
                "self",
            };
            for (int i = 0; i < symbols.length; i++) {
                fSymbolMapping.put(fSymbolTable.addSymbol(symbols[i]), new Integer(i));
            }
            fTokenNames.put(new Integer(EXPRTOKEN_OPEN_PAREN), "EXPRTOKEN_OPEN_PAREN");
            fTokenNames.put(new Integer(EXPRTOKEN_CLOSE_PAREN), "EXPRTOKEN_CLOSE_PAREN");
            fTokenNames.put(new Integer(EXPRTOKEN_OPEN_BRACKET), "EXPRTOKEN_OPEN_BRACKET");
            fTokenNames.put(new Integer(EXPRTOKEN_CLOSE_BRACKET), "EXPRTOKEN_CLOSE_BRACKET");
            fTokenNames.put(new Integer(EXPRTOKEN_PERIOD), "EXPRTOKEN_PERIOD");
            fTokenNames.put(new Integer(EXPRTOKEN_DOUBLE_PERIOD), "EXPRTOKEN_DOUBLE_PERIOD");
            fTokenNames.put(new Integer(EXPRTOKEN_ATSIGN), "EXPRTOKEN_ATSIGN");
            fTokenNames.put(new Integer(EXPRTOKEN_COMMA), "EXPRTOKEN_COMMA");
            fTokenNames.put(new Integer(EXPRTOKEN_DOUBLE_COLON), "EXPRTOKEN_DOUBLE_COLON");
            fTokenNames.put(new Integer(EXPRTOKEN_NAMETEST_ANY), "EXPRTOKEN_NAMETEST_ANY");
            fTokenNames.put(new Integer(EXPRTOKEN_NAMETEST_NAMESPACE), "EXPRTOKEN_NAMETEST_NAMESPACE");
            fTokenNames.put(new Integer(EXPRTOKEN_NAMETEST_QNAME), "EXPRTOKEN_NAMETEST_QNAME");
            fTokenNames.put(new Integer(EXPRTOKEN_NODETYPE_COMMENT), "EXPRTOKEN_NODETYPE_COMMENT");
            fTokenNames.put(new Integer(EXPRTOKEN_NODETYPE_TEXT), "EXPRTOKEN_NODETYPE_TEXT");
            fTokenNames.put(new Integer(EXPRTOKEN_NODETYPE_PI), "EXPRTOKEN_NODETYPE_PI");
            fTokenNames.put(new Integer(EXPRTOKEN_NODETYPE_NODE), "EXPRTOKEN_NODETYPE_NODE");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_AND), "EXPRTOKEN_OPERATOR_AND");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_OR), "EXPRTOKEN_OPERATOR_OR");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_MOD), "EXPRTOKEN_OPERATOR_MOD");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_DIV), "EXPRTOKEN_OPERATOR_DIV");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_MULT), "EXPRTOKEN_OPERATOR_MULT");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_SLASH), "EXPRTOKEN_OPERATOR_SLASH");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_DOUBLE_SLASH), "EXPRTOKEN_OPERATOR_DOUBLE_SLASH");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_UNION), "EXPRTOKEN_OPERATOR_UNION");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_PLUS), "EXPRTOKEN_OPERATOR_PLUS");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_MINUS), "EXPRTOKEN_OPERATOR_MINUS");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_EQUAL), "EXPRTOKEN_OPERATOR_EQUAL");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_NOT_EQUAL), "EXPRTOKEN_OPERATOR_NOT_EQUAL");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_LESS), "EXPRTOKEN_OPERATOR_LESS");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_LESS_EQUAL), "EXPRTOKEN_OPERATOR_LESS_EQUAL");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_GREATER), "EXPRTOKEN_OPERATOR_GREATER");
            fTokenNames.put(new Integer(EXPRTOKEN_OPERATOR_GREATER_EQUAL), "EXPRTOKEN_OPERATOR_GREATER_EQUAL");
            fTokenNames.put(new Integer(EXPRTOKEN_FUNCTION_NAME), "EXPRTOKEN_FUNCTION_NAME");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_ANCESTOR), "EXPRTOKEN_AXISNAME_ANCESTOR");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_ANCESTOR_OR_SELF), "EXPRTOKEN_AXISNAME_ANCESTOR_OR_SELF");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_ATTRIBUTE), "EXPRTOKEN_AXISNAME_ATTRIBUTE");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_CHILD), "EXPRTOKEN_AXISNAME_CHILD");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_DESCENDANT), "EXPRTOKEN_AXISNAME_DESCENDANT");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_DESCENDANT_OR_SELF), "EXPRTOKEN_AXISNAME_DESCENDANT_OR_SELF");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_FOLLOWING), "EXPRTOKEN_AXISNAME_FOLLOWING");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_FOLLOWING_SIBLING), "EXPRTOKEN_AXISNAME_FOLLOWING_SIBLING");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_NAMESPACE), "EXPRTOKEN_AXISNAME_NAMESPACE");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_PARENT), "EXPRTOKEN_AXISNAME_PARENT");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_PRECEDING), "EXPRTOKEN_AXISNAME_PRECEDING");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_PRECEDING_SIBLING), "EXPRTOKEN_AXISNAME_PRECEDING_SIBLING");
            fTokenNames.put(new Integer(EXPRTOKEN_AXISNAME_SELF), "EXPRTOKEN_AXISNAME_SELF");
            fTokenNames.put(new Integer(EXPRTOKEN_LITERAL), "EXPRTOKEN_LITERAL");
            fTokenNames.put(new Integer(EXPRTOKEN_NUMBER), "EXPRTOKEN_NUMBER");
            fTokenNames.put(new Integer(EXPRTOKEN_VARIABLE_REFERENCE), "EXPRTOKEN_VARIABLE_REFERENCE");
        }

        //
        // Public methods
        //

        /*** // REVISIT: What is this doing here? -Ac ***
        public int addSymbol(byte[] data, int offset, int length, EncodingMap encoding) {
            //return fSymbolTable.addSymbol(data, offset, length, encoding);
            return fSymbolTable.addSymbol(new String(data, offset, length));
        }
        /***/

        public String getTokenName(int token) {
            if (token < 0 || token >= fgTokenNames.length)
                return null;
            return fgTokenNames[token];
        }

        public String getTokenString(int token) {
            return (String)fTokenNames.get(new Integer(token));
        }

        public void addToken(String tokenStr) {
            Integer tokenInt = (Integer)fTokenNames.get(tokenStr);
            if (tokenInt == null) {
                tokenInt = new Integer(fTokenNames.size());
                fTokenNames.put(tokenInt, tokenStr);
            }
            addToken(tokenInt.intValue());
        }

        public void addToken(int token) {
            try {
                fTokens[fTokenCount] = token;
            } catch (ArrayIndexOutOfBoundsException ex) {
                int[] oldList = fTokens;
                fTokens = new int[fTokenCount << 1];
                System.arraycopy(oldList, 0, fTokens, 0, fTokenCount);
                fTokens[fTokenCount] = token;
            }
            fTokenCount++;
        }
        public int getTokenCount() {
            return fTokenCount;
        }
        public int getToken(int tokenIndex) {
            return fTokens[tokenIndex];
        }
        public void dumpTokens() {
            //if (DUMP_TOKENS) {
                for (int i = 0; i < fTokenCount; i++) {
                    switch (fTokens[i]) {
                    case EXPRTOKEN_OPEN_PAREN:
                        System.out.print("<OPEN_PAREN/>");
                        break;
                    case EXPRTOKEN_CLOSE_PAREN:
                        System.out.print("<CLOSE_PAREN/>");
                        break;
                    case EXPRTOKEN_OPEN_BRACKET:
                        System.out.print("<OPEN_BRACKET/>");
                        break;
                    case EXPRTOKEN_CLOSE_BRACKET:
                        System.out.print("<CLOSE_BRACKET/>");
                        break;
                    case EXPRTOKEN_PERIOD:
                        System.out.print("<PERIOD/>");
                        break;
                    case EXPRTOKEN_DOUBLE_PERIOD:
                        System.out.print("<DOUBLE_PERIOD/>");
                        break;
                    case EXPRTOKEN_ATSIGN:
                        System.out.print("<ATSIGN/>");
                        break;
                    case EXPRTOKEN_COMMA:
                        System.out.print("<COMMA/>");
                        break;
                    case EXPRTOKEN_DOUBLE_COLON:
                        System.out.print("<DOUBLE_COLON/>");
                        break;
                    case EXPRTOKEN_NAMETEST_ANY:
                        System.out.print("<NAMETEST_ANY/>");
                        break;
                    case EXPRTOKEN_NAMETEST_NAMESPACE:
                        System.out.print("<NAMETEST_NAMESPACE");
                        System.out.print(" prefix=\"" + getTokenString(fTokens[++i]) + "\"");
                        System.out.print("/>");
                        break;
                    case EXPRTOKEN_NAMETEST_QNAME:
                        System.out.print("<NAMETEST_QNAME");
                        if (fTokens[++i] != -1)
                            System.out.print(" prefix=\"" + getTokenString(fTokens[i]) + "\"");
                        System.out.print(" localpart=\"" + getTokenString(fTokens[++i]) + "\"");
                        System.out.print("/>");
                        break;
                    case EXPRTOKEN_NODETYPE_COMMENT:
                        System.out.print("<NODETYPE_COMMENT/>");
                        break;
                    case EXPRTOKEN_NODETYPE_TEXT:
                        System.out.print("<NODETYPE_TEXT/>");
                        break;
                    case EXPRTOKEN_NODETYPE_PI:
                        System.out.print("<NODETYPE_PI/>");
                        break;
                    case EXPRTOKEN_NODETYPE_NODE:
                        System.out.print("<NODETYPE_NODE/>");
                        break;
                    case EXPRTOKEN_OPERATOR_AND:
                        System.out.print("<OPERATOR_AND/>");
                        break;
                    case EXPRTOKEN_OPERATOR_OR:
                        System.out.print("<OPERATOR_OR/>");
                        break;
                    case EXPRTOKEN_OPERATOR_MOD:
                        System.out.print("<OPERATOR_MOD/>");
                        break;
                    case EXPRTOKEN_OPERATOR_DIV:
                        System.out.print("<OPERATOR_DIV/>");
                        break;
                    case EXPRTOKEN_OPERATOR_MULT:
                        System.out.print("<OPERATOR_MULT/>");
                        break;
                    case EXPRTOKEN_OPERATOR_SLASH:
                        System.out.print("<OPERATOR_SLASH/>");
                        if (i + 1 < fTokenCount) {
                            System.out.println();
                            System.out.print("  ");
                        }
                        break;
                    case EXPRTOKEN_OPERATOR_DOUBLE_SLASH:
                        System.out.print("<OPERATOR_DOUBLE_SLASH/>");
                        break;
                    case EXPRTOKEN_OPERATOR_UNION:
                        System.out.print("<OPERATOR_UNION/>");
                        break;
                    case EXPRTOKEN_OPERATOR_PLUS:
                        System.out.print("<OPERATOR_PLUS/>");
                        break;
                    case EXPRTOKEN_OPERATOR_MINUS:
                        System.out.print("<OPERATOR_MINUS/>");
                        break;
                    case EXPRTOKEN_OPERATOR_EQUAL:
                        System.out.print("<OPERATOR_EQUAL/>");
                        break;
                    case EXPRTOKEN_OPERATOR_NOT_EQUAL:
                        System.out.print("<OPERATOR_NOT_EQUAL/>");
                        break;
                    case EXPRTOKEN_OPERATOR_LESS:
                        System.out.print("<OPERATOR_LESS/>");
                        break;
                    case EXPRTOKEN_OPERATOR_LESS_EQUAL:
                        System.out.print("<OPERATOR_LESS_EQUAL/>");
                        break;
                    case EXPRTOKEN_OPERATOR_GREATER:
                        System.out.print("<OPERATOR_GREATER/>");
                        break;
                    case EXPRTOKEN_OPERATOR_GREATER_EQUAL:
                        System.out.print("<OPERATOR_GREATER_EQUAL/>");
                        break;
                    case EXPRTOKEN_FUNCTION_NAME:
                        System.out.print("<FUNCTION_NAME");
                        if (fTokens[++i] != -1)
                            System.out.print(" prefix=\"" + getTokenString(fTokens[i]) + "\"");
                        System.out.print(" localpart=\"" + getTokenString(fTokens[++i]) + "\"");
                        System.out.print("/>");
                        break;
                    case EXPRTOKEN_AXISNAME_ANCESTOR:
                        System.out.print("<AXISNAME_ANCESTOR/>");
                        break;
                    case EXPRTOKEN_AXISNAME_ANCESTOR_OR_SELF:
                        System.out.print("<AXISNAME_ANCESTOR_OR_SELF/>");
                        break;
                    case EXPRTOKEN_AXISNAME_ATTRIBUTE:
                        System.out.print("<AXISNAME_ATTRIBUTE/>");
                        break;
                    case EXPRTOKEN_AXISNAME_CHILD:
                        System.out.print("<AXISNAME_CHILD/>");
                        break;
                    case EXPRTOKEN_AXISNAME_DESCENDANT:
                        System.out.print("<AXISNAME_DESCENDANT/>");
                        break;
                    case EXPRTOKEN_AXISNAME_DESCENDANT_OR_SELF:
                        System.out.print("<AXISNAME_DESCENDANT_OR_SELF/>");
                        break;
                    case EXPRTOKEN_AXISNAME_FOLLOWING:
                        System.out.print("<AXISNAME_FOLLOWING/>");
                        break;
                    case EXPRTOKEN_AXISNAME_FOLLOWING_SIBLING:
                        System.out.print("<AXISNAME_FOLLOWING_SIBLING/>");
                        break;
                    case EXPRTOKEN_AXISNAME_NAMESPACE:
                        System.out.print("<AXISNAME_NAMESPACE/>");
                        break;
                    case EXPRTOKEN_AXISNAME_PARENT:
                        System.out.print("<AXISNAME_PARENT/>");
                        break;
                    case EXPRTOKEN_AXISNAME_PRECEDING:
                        System.out.print("<AXISNAME_PRECEDING/>");
                        break;
                    case EXPRTOKEN_AXISNAME_PRECEDING_SIBLING:
                        System.out.print("<AXISNAME_PRECEDING_SIBLING/>");
                        break;
                    case EXPRTOKEN_AXISNAME_SELF:
                        System.out.print("<AXISNAME_SELF/>");
                        break;
                    case EXPRTOKEN_LITERAL:
                        System.out.print("<LITERAL");
                        System.out.print(" value=\"" + getTokenString(fTokens[++i]) + "\"");
                        System.out.print("/>");
                        break;
                    case EXPRTOKEN_NUMBER:
                        System.out.print("<NUMBER");
                        System.out.print(" whole=\"" + getTokenString(fTokens[++i]) + "\"");
                        System.out.print(" part=\"" + getTokenString(fTokens[++i]) + "\"");
                        System.out.print("/>");
                        break;
                    case EXPRTOKEN_VARIABLE_REFERENCE:
                        System.out.print("<VARIABLE_REFERENCE");
                        if (fTokens[++i] != -1)
                            System.out.print(" prefix=\"" + getTokenString(fTokens[i]) + "\"");
                        System.out.print(" localpart=\"" + getTokenString(fTokens[++i]) + "\"");
                        System.out.print("/>");
                        break;
                    default:
                        System.out.println("<???/>");
                    }
                }
                System.out.println();
            //}
        }

    } // class Tokens

    /**
     * @author Glenn Marcy, IBM
     * @author Andy Clark, IBM
     *
     * @version $Id$
     */
    private static class Scanner {

        /**
         * 7-bit ASCII subset
         *
         *  0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
         *  0,  0,  0,  0,  0,  0,  0,  0,  0, HT, LF,  0,  0, CR,  0,  0,  // 0
         *  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  // 1
         * SP,  !,  ",  #,  $,  %,  &,  ',  (,  ),  *,  +,  ,,  -,  .,  /,  // 2
         *  0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  :,  ;,  <,  =,  >,  ?,  // 3
         *  @,  A,  B,  C,  D,  E,  F,  G,  H,  I,  J,  K,  L,  M,  N,  O,  // 4
         *  P,  Q,  R,  S,  T,  U,  V,  W,  X,  Y,  Z,  [,  \,  ],  ^,  _,  // 5
         *  `,  a,  b,  c,  d,  e,  f,  g,  h,  i,  j,  k,  l,  m,  n,  o,  // 6
         *  p,  q,  r,  s,  t,  u,  v,  w,  x,  y,  z,  {,  |,  },  ~, DEL  // 7
         */
        private static final byte
            CHARTYPE_INVALID            =  0,   // invalid XML character
            CHARTYPE_OTHER              =  1,   // not special - one of "#%&;?\^`{}~" or DEL
            CHARTYPE_WHITESPACE         =  2,   // one of "\t\n\r " (0x09, 0x0A, 0x0D, 0x20)
            CHARTYPE_EXCLAMATION        =  3,   // '!' (0x21)
            CHARTYPE_QUOTE              =  4,   // '\"' or '\'' (0x22 and 0x27)
            CHARTYPE_DOLLAR             =  5,   // '$' (0x24)
            CHARTYPE_OPEN_PAREN         =  6,   // '(' (0x28)
            CHARTYPE_CLOSE_PAREN        =  7,   // ')' (0x29)
            CHARTYPE_STAR               =  8,   // '*' (0x2A)
            CHARTYPE_PLUS               =  9,   // '+' (0x2B)
            CHARTYPE_COMMA              = 10,   // ',' (0x2C)
            CHARTYPE_MINUS              = 11,   // '-' (0x2D)
            CHARTYPE_PERIOD             = 12,   // '.' (0x2E)
            CHARTYPE_SLASH              = 13,   // '/' (0x2F)
            CHARTYPE_DIGIT              = 14,   // '0'-'9' (0x30 to 0x39)
            CHARTYPE_COLON              = 15,   // ':' (0x3A)
            CHARTYPE_LESS               = 16,   // '<' (0x3C)
            CHARTYPE_EQUAL              = 17,   // '=' (0x3D)
            CHARTYPE_GREATER            = 18,   // '>' (0x3E)
            CHARTYPE_ATSIGN             = 19,   // '@' (0x40)
            CHARTYPE_LETTER             = 20,   // 'A'-'Z' or 'a'-'z' (0x41 to 0x5A and 0x61 to 0x7A)
            CHARTYPE_OPEN_BRACKET       = 21,   // '[' (0x5B)
            CHARTYPE_CLOSE_BRACKET      = 22,   // ']' (0x5D)
            CHARTYPE_UNDERSCORE         = 23,   // '_' (0x5F)
            CHARTYPE_UNION              = 24,   // '|' (0x7C)
            CHARTYPE_NONASCII           = 25;   // Non-ASCII Unicode codepoint (>= 0x80)

        private static byte[] fASCIICharMap = {
            0,  0,  0,  0,  0,  0,  0,  0,  0,  2,  2,  0,  0,  2,  0,  0,
            0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            2,  3,  4,  1,  5,  1,  1,  4,  6,  7,  8,  9, 10, 11, 12, 13,
           14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 15,  1, 16, 17, 18,  1,
           19, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
           20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 21,  1, 22,  1, 23,
            1, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
           20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20,  1, 24,  1,  1,  1
        };

        /**
         * Symbol literals
         */
        /***
        private static int fgAndSymbol = -1;                // 'and'
        private static int fgOrSymbol = -1;                 // 'or'
        private static int fgModSymbol = -1;                // 'mod'
        private static int fgDivSymbol = -1;                // 'div'

        private static int fgCommentSymbol = -1;            // 'comment'
        private static int fgTextSymbol = -1;               // 'text'
        private static int fgPISymbol = -1;                 // 'processing-instruction'
        private static int fgNodeSymbol = -1;               // 'node'

        private static int fgAncestorSymbol = -1;           // 'ancestor'
        private static int fgAncestorOrSelfSymbol = -1;     // 'ancestor-or-self'
        private static int fgAttributeSymbol = -1;          // 'attribute'
        private static int fgChildSymbol = -1;              // 'child'
        private static int fgDescendantSymbol = -1;         // 'descendant'
        private static int fgDescendantOrSelfSymbol = -1;   // 'descendant-or-self'
        private static int fgFollowingSymbol = -1;          // 'following'
        private static int fgFollowingSiblingSymbol = -1;   // 'following-sibling'
        private static int fgNamespaceSymbol = -1;          // 'namespace'
        private static int fgParentSymbol = -1;             // 'parent'
        private static int fgPrecedingSymbol = -1;          // 'preceding'
        private static int fgPrecedingSiblingSymbol = -1;   // 'preceding-sibling'
        private static int fgSelfSymbol = -1;               // 'self'

        private static SymbolTable fgSymbolTable = new SymbolTable();

        static {
            fgAndSymbol = fgSymbolTable.addSymbol("and");
            fgOrSymbol = fgSymbolTable.addSymbol("or");
            fgModSymbol = fgSymbolTable.addSymbol("mod");
            fgDivSymbol = fgSymbolTable.addSymbol("div");
            fgCommentSymbol = fgSymbolTable.addSymbol("comment");
            fgTextSymbol = fgSymbolTable.addSymbol("text");
            fgPISymbol = fgSymbolTable.addSymbol("processing-instruction");
            fgNodeSymbol = fgSymbolTable.addSymbol("node");
            fgAncestorSymbol = fgSymbolTable.addSymbol("ancestor");
            fgAncestorOrSelfSymbol = fgSymbolTable.addSymbol("ancestor-or-self");
            fgAttributeSymbol = fgSymbolTable.addSymbol("attribute");
            fgChildSymbol = fgSymbolTable.addSymbol("child");
            fgDescendantSymbol = fgSymbolTable.addSymbol("descendant");
            fgDescendantOrSelfSymbol = fgSymbolTable.addSymbol("descendant-or-self");
            fgFollowingSymbol = fgSymbolTable.addSymbol("following");
            fgFollowingSiblingSymbol = fgSymbolTable.addSymbol("following-sibling");
            fgNamespaceSymbol = fgSymbolTable.addSymbol("namespace");
            fgParentSymbol = fgSymbolTable.addSymbol("parent");
            fgPrecedingSymbol = fgSymbolTable.addSymbol("preceding");
            fgPrecedingSiblingSymbol = fgSymbolTable.addSymbol("preceding-sibling");
            fgSelfSymbol = fgSymbolTable.addSymbol("self");
        }
        /***/

        //
        // Data
        //

        /** Symbol table. */
        private SymbolTable fSymbolTable;

        // symbols

        private String fAndSymbol;
        private String fOrSymbol;
        private String fModSymbol;
        private String fDivSymbol;

        private String fCommentSymbol;
        private String fTextSymbol;
        private String fPISymbol;
        private String fNodeSymbol;

        private String fAncestorSymbol;
        private String fAncestorOrSelfSymbol;
        private String fAttributeSymbol;
        private String fChildSymbol;
        private String fDescendantSymbol;
        private String fDescendantOrSelfSymbol;
        private String fFollowingSymbol;
        private String fFollowingSiblingSymbol;
        private String fNamespaceSymbol;
        private String fParentSymbol;
        private String fPrecedingSymbol;
        private String fPrecedingSiblingSymbol;
        private String fSelfSymbol;

        //
        // Constructors
        //

        /** Constructs an XPath expression scanner. */
        public Scanner(SymbolTable symbolTable) {

            // save pool and tokens
            fSymbolTable = symbolTable;

            // create symbols
            fAndSymbol = fSymbolTable.addSymbol("and");
            fOrSymbol = fSymbolTable.addSymbol("or");
            fModSymbol = fSymbolTable.addSymbol("mod");
            fDivSymbol = fSymbolTable.addSymbol("div");
            fCommentSymbol = fSymbolTable.addSymbol("comment");
            fTextSymbol = fSymbolTable.addSymbol("text");
            fPISymbol = fSymbolTable.addSymbol("processing-instruction");
            fNodeSymbol = fSymbolTable.addSymbol("node");
            fAncestorSymbol = fSymbolTable.addSymbol("ancestor");
            fAncestorOrSelfSymbol = fSymbolTable.addSymbol("ancestor-or-self");
            fAttributeSymbol = fSymbolTable.addSymbol("attribute");
            fChildSymbol = fSymbolTable.addSymbol("child");
            fDescendantSymbol = fSymbolTable.addSymbol("descendant");
            fDescendantOrSelfSymbol = fSymbolTable.addSymbol("descendant-or-self");
            fFollowingSymbol = fSymbolTable.addSymbol("following");
            fFollowingSiblingSymbol = fSymbolTable.addSymbol("following-sibling");
            fNamespaceSymbol = fSymbolTable.addSymbol("namespace");
            fParentSymbol = fSymbolTable.addSymbol("parent");
            fPrecedingSymbol = fSymbolTable.addSymbol("preceding");
            fPrecedingSiblingSymbol = fSymbolTable.addSymbol("preceding-sibling");
            fSelfSymbol = fSymbolTable.addSymbol("self");

        } // <init>(SymbolTable)

        /**
         *
         */
        public boolean scanExpr(SymbolTable symbolTable,
                                XPath.Tokens tokens, String data,
                                int currentOffset, int endOffset)
            throws XPathException {

            int nameOffset;
            String nameHandle, prefixHandle;
            boolean starIsMultiplyOperator = false;
            int ch;
            final String emptySymbol = fSymbolTable.addSymbol("");

            /***
            if (XPath.Tokens.DUMP_TOKENS) {
                System.out.println("  <test>");
                System.out.println("    <expression>");
                System.out.println("      " + encoding.createString(data, currentOffset, endOffset - currentOffset));
                System.out.println("    </expression>");
            }
            /***/
            while (true) {
                if (currentOffset == endOffset) {
                    break;
                }
                ch = data.charAt(currentOffset);
                //
                // [39] ExprWhitespace ::= S
                //
                while (ch == ' ' || ch == 0x0A || ch == 0x09 || ch == 0x0D) {
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    ch = data.charAt(currentOffset);
                }
                if (currentOffset == endOffset) {
                    break;
                }
                //
                // [28] ExprToken ::= '(' | ')' | '[' | ']' | '.' | '..' | '@' | ',' | '::'
                //                  | NameTest | NodeType | Operator | FunctionName
                //                  | AxisName | Literal | Number | VariableReference
                //
                byte chartype = (ch >= 0x80) ? CHARTYPE_NONASCII : fASCIICharMap[ch];
                switch (chartype) {
                case CHARTYPE_OPEN_PAREN:       // '('
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_OPEN_PAREN);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_CLOSE_PAREN:      // ')'
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_CLOSE_PAREN);
                    starIsMultiplyOperator = true;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_OPEN_BRACKET:     // '['
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_OPEN_BRACKET);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_CLOSE_BRACKET:    // ']'
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_CLOSE_BRACKET);
                    starIsMultiplyOperator = true;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                //
                // [30] Number ::= Digits ('.' Digits?)? | '.' Digits
                //                                         ^^^^^^^^^^
                //
                case CHARTYPE_PERIOD:           // '.', '..' or '.' Digits
                    if (currentOffset + 1 == endOffset) {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_PERIOD);
                        starIsMultiplyOperator = true;
                        currentOffset++;
                        break;
                    }
                    ch = data.charAt(currentOffset + 1);
                    if (ch == '.') {            // '..'
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_DOUBLE_PERIOD);
                        starIsMultiplyOperator = true;
                        currentOffset += 2;
                    } else if (ch >= '0' && ch <= '9') {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_NUMBER);
                        starIsMultiplyOperator = true;
                        currentOffset = scanNumber(tokens, data, endOffset, currentOffset/*, encoding*/);
                    } else if (ch == '/') {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_PERIOD);
                        starIsMultiplyOperator = true;
                        currentOffset++;
                    } else {                    // '.'
                        throw new XPathException ("Invalid character following '.'");
                    }
                    if (currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_ATSIGN:           // '@'
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_ATSIGN);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_COMMA:            // ','
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_COMMA);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_COLON:            // '::'
                    if (++currentOffset == endOffset) {
                // System.out.println("abort 1a");
                        return false; // REVISIT
                    }
                    ch = data.charAt(currentOffset);
                    if (ch != ':') {
                // System.out.println("abort 1b");
                        return false; // REVISIT
                    }
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_DOUBLE_COLON);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_SLASH:            // '/' and '//'
                    if (++currentOffset == endOffset) {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH);
                        starIsMultiplyOperator = false;
                        break;
                    }
                    ch = data.charAt(currentOffset);
                    if (ch == '/') { // '//'
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_DOUBLE_SLASH);
                        starIsMultiplyOperator = false;
                        if (++currentOffset == endOffset) {
                            break;
                        }
                    } else {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH);
                        starIsMultiplyOperator = false;
                    }
                    break;
                case CHARTYPE_UNION:            // '|'
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_UNION);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_PLUS:             // '+'
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_PLUS);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_MINUS:            // '-'
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_MINUS);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_EQUAL:            // '='
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_EQUAL);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_EXCLAMATION:      // '!='
                    if (++currentOffset == endOffset) {
                // System.out.println("abort 2a");
                        return false; // REVISIT
                    }
                    ch = data.charAt(currentOffset);
                    if (ch != '=') {
                // System.out.println("abort 2b");
                        return false; // REVISIT
                    }
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_NOT_EQUAL);
                    starIsMultiplyOperator = false;
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                case CHARTYPE_LESS: // '<' and '<='
                    if (++currentOffset == endOffset) {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_LESS);
                        starIsMultiplyOperator = false;
                        break;
                    }
                    ch = data.charAt(currentOffset);
                    if (ch == '=') { // '<='
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_LESS_EQUAL);
                        starIsMultiplyOperator = false;
                        if (++currentOffset == endOffset) {
                            break;
                        }
                    } else {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_LESS);
                        starIsMultiplyOperator = false;
                    }
                    break;
                case CHARTYPE_GREATER: // '>' and '>='
                    if (++currentOffset == endOffset) {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_GREATER);
                        starIsMultiplyOperator = false;
                        break;
                    }
                    ch = data.charAt(currentOffset);
                    if (ch == '=') { // '>='
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_GREATER_EQUAL);
                        starIsMultiplyOperator = false;
                        if (++currentOffset == endOffset) {
                            break;
                        }
                    } else {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_GREATER);
                        starIsMultiplyOperator = false;
                    }
                    break;
                //
                // [29] Literal ::= '"' [^"]* '"' | "'" [^']* "'"
                //
                case CHARTYPE_QUOTE:            // '\"' or '\''
                    int qchar = ch;
                    if (++currentOffset == endOffset) {
                // System.out.println("abort 2c");
                        return false; // REVISIT
                    }
                    ch = data.charAt(currentOffset);
                    int litOffset = currentOffset;
                    while (ch != qchar) {
                        if (++currentOffset == endOffset) {
                // System.out.println("abort 2d");
                            return false; // REVISIT
                        }
                        ch = data.charAt(currentOffset);
                    }
                    int litLength = currentOffset - litOffset;
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_LITERAL);
                    starIsMultiplyOperator = true;
                    tokens.addToken(symbolTable.addSymbol(data.substring(litOffset, litOffset + litLength)));
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                //
                // [30] Number ::= Digits ('.' Digits?)? | '.' Digits
                // [31] Digits ::= [0-9]+
                //
                case CHARTYPE_DIGIT:
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_NUMBER);
                    starIsMultiplyOperator = true;
                    currentOffset = scanNumber(tokens, data, endOffset, currentOffset/*, encoding*/);
                    break;
                //
                // [36] VariableReference ::= '$' QName
                //
                case CHARTYPE_DOLLAR:
                    if (++currentOffset == endOffset) {
                // System.out.println("abort 3a");
                        return false; // REVISIT
                    }
                    nameOffset = currentOffset;
                    currentOffset = scanNCName(data, endOffset, currentOffset);
                    if (currentOffset == nameOffset) {
                // System.out.println("abort 3b");
                        return false; // REVISIT
                    }
                    if (currentOffset < endOffset) {
                        ch = data.charAt(currentOffset);
                    }
                    else {
                        ch = -1;
                    }
                    nameHandle = symbolTable.addSymbol(data.substring(nameOffset, currentOffset));
                    if (ch != ':') {
                        prefixHandle = emptySymbol;
                    } else {
                        prefixHandle = nameHandle;
                        if (++currentOffset == endOffset) {
                // System.out.println("abort 4a");
                            return false; // REVISIT
                        }
                        nameOffset = currentOffset;
                        currentOffset = scanNCName(data, endOffset, currentOffset);
                        if (currentOffset == nameOffset) {
                // System.out.println("abort 4b");
                            return false; // REVISIT
                        }
                        if (currentOffset < endOffset) {
                            ch = data.charAt(currentOffset);
                        }
                        else {
                            ch = -1;
                        }
                        nameHandle = symbolTable.addSymbol(data.substring(nameOffset, currentOffset));
                    }
                    addToken(tokens, XPath.Tokens.EXPRTOKEN_VARIABLE_REFERENCE);
                    starIsMultiplyOperator = true;
                    tokens.addToken(prefixHandle);
                    tokens.addToken(nameHandle);
                    break;
                //
                // [37] NameTest ::= '*' | NCName ':' '*' | QName
                // [34] MultiplyOperator ::= '*'
                //
                case CHARTYPE_STAR:             // '*'
                    //
                    // 3.7 Lexical Structure
                    //
                    //  If there is a preceding token and the preceding token is not one of @, ::, (, [, , or
                    //  an Operator, then a * must be recognized as a MultiplyOperator.
                    //
                    // Otherwise, the token must not be recognized as a MultiplyOperator.
                    //
                    if (starIsMultiplyOperator) {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_MULT);
                        starIsMultiplyOperator = false;
                    } else {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_NAMETEST_ANY);
                        starIsMultiplyOperator = true;
                    }
                    if (++currentOffset == endOffset) {
                        break;
                    }
                    break;
                //
                // NCName, QName and non-terminals
                //
                case CHARTYPE_NONASCII: // possibly a valid non-ascii 'Letter' (BaseChar | Ideographic)
                case CHARTYPE_LETTER:
                case CHARTYPE_UNDERSCORE:
                    //
                    // 3.7 Lexical Structure
                    //
                    //  If there is a preceding token and the preceding token is not one of @, ::, (, [, , or
                    //  an Operator, then an NCName must be recognized as an OperatorName.
                    //
                    //  If the character following an NCName (possibly after intervening ExprWhitespace) is (,
                    //  then the token must be recognized as a NodeType or a FunctionName.
                    //
                    //  If the two characters following an NCName (possibly after intervening ExprWhitespace)
                    //  are ::, then the token must be recognized as an AxisName.
                    //
                    //  Otherwise, the token must not be recognized as an OperatorName, a NodeType, a
                    //  FunctionName, or an AxisName.
                    //
                    // [33] OperatorName ::= 'and' | 'or' | 'mod' | 'div'
                    // [38] NodeType ::= 'comment' | 'text' | 'processing-instruction' | 'node'
                    // [35] FunctionName ::= QName - NodeType
                    // [6] AxisName ::= (see above)
                    //
                    // [37] NameTest ::= '*' | NCName ':' '*' | QName
                    // [5] NCName ::= (Letter | '_') (NCNameChar)*
                    // [?] NCNameChar ::= Letter | Digit | '.' | '-' | '_'  (ascii subset of 'NCNameChar')
                    // [?] QName ::= (NCName ':')? NCName
                    // [?] Letter ::= [A-Za-z]                              (ascii subset of 'Letter')
                    // [?] Digit ::= [0-9]                                  (ascii subset of 'Digit')
                    //
                    nameOffset = currentOffset;
                    currentOffset = scanNCName(data, endOffset, currentOffset);
                    if (currentOffset == nameOffset) {
                // System.out.println("abort 4c");
                        return false; // REVISIT
                    }
                    if (currentOffset < endOffset) {
                        ch = data.charAt(currentOffset);
                    }
                    else {
                        ch = -1;
                    }
                    nameHandle = symbolTable.addSymbol(data.substring(nameOffset, currentOffset));
                    boolean isNameTestNCName = false;
                    boolean isAxisName = false;
                    prefixHandle = emptySymbol;
                    if (ch == ':') {
                        if (++currentOffset == endOffset) {
                // System.out.println("abort 5");
                            return false; // REVISIT
                        }
                        ch = data.charAt(currentOffset);
                        if (ch == '*') {
                            if (++currentOffset < endOffset) {
                                ch = data.charAt(currentOffset);
                            }
                            isNameTestNCName = true;
                        } else if (ch == ':') {
                            if (++currentOffset < endOffset) {
                                ch = data.charAt(currentOffset);
                            }
                            isAxisName = true;
                        } else {
                            prefixHandle = nameHandle;
                            nameOffset = currentOffset;
                            currentOffset = scanNCName(data, endOffset, currentOffset);
                            if (currentOffset == nameOffset) {
                // System.out.println("abort 5b");
                                return false; // REVISIT
                            }
                            if (currentOffset < endOffset) {
                                ch = data.charAt(currentOffset);
                            }
                            else {
                                ch = -1;
                            }
                            nameHandle = symbolTable.addSymbol(data.substring(nameOffset, currentOffset));
                        }
                    }
                    //
                    // [39] ExprWhitespace ::= S
                    //
                    while (ch == ' ' || ch == 0x0A || ch == 0x09 || ch == 0x0D) {
                        if (++currentOffset == endOffset) {
                            break;
                        }
                        ch = data.charAt(currentOffset);
                    }
                    //
                    //  If there is a preceding token and the preceding token is not one of @, ::, (, [, , or
                    //  an Operator, then an NCName must be recognized as an OperatorName.
                    //
                    if (starIsMultiplyOperator) {
                        if (nameHandle == fAndSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_AND);
                            starIsMultiplyOperator = false;
                        } else if (nameHandle == fOrSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_OR);
                            starIsMultiplyOperator = false;
                        } else if (nameHandle == fModSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_MOD);
                            starIsMultiplyOperator = false;
                        } else if (nameHandle == fDivSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_OPERATOR_DIV);
                            starIsMultiplyOperator = false;
                        } else {
                // System.out.println("abort 6");
                            return false; // REVISIT
                        }
                        if (isNameTestNCName) {
                // System.out.println("abort 7");
                            return false; // REVISIT - NCName:* where an OperatorName is required
                        } else if (isAxisName) {
                // System.out.println("abort 8");
                            return false; // REVISIT - AxisName:: where an OperatorName is required
                        }
                        break;
                    }
                    //
                    //  If the character following an NCName (possibly after intervening ExprWhitespace) is (,
                    //  then the token must be recognized as a NodeType or a FunctionName.
                    //
                    if (ch == '(' && !isNameTestNCName && !isAxisName) {
                        if (nameHandle == fCommentSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_NODETYPE_COMMENT);
                        } else if (nameHandle == fTextSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_NODETYPE_TEXT);
                        } else if (nameHandle == fPISymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_NODETYPE_PI);
                        } else if (nameHandle == fNodeSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_NODETYPE_NODE);
                        } else {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_FUNCTION_NAME);
                            tokens.addToken(prefixHandle);
                            tokens.addToken(nameHandle);
                        }
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_OPEN_PAREN);
                        starIsMultiplyOperator = false;
                        if (++currentOffset == endOffset) {
                            break;
                        }
                        break;
                    }
                    //
                    //  If the two characters following an NCName (possibly after intervening ExprWhitespace)
                    //  are ::, then the token must be recognized as an AxisName.
                    //
                    if (isAxisName ||
                        (ch == ':' && currentOffset + 1 < endOffset &&
                         data.charAt(currentOffset + 1) == ':')) {
                        if (nameHandle == fAncestorSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_ANCESTOR);
                        } else if (nameHandle == fAncestorOrSelfSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_ANCESTOR_OR_SELF);
                        } else if (nameHandle == fAttributeSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_ATTRIBUTE);
                        } else if (nameHandle == fChildSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_CHILD);
                        } else if (nameHandle == fDescendantSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_DESCENDANT);
                        } else if (nameHandle == fDescendantOrSelfSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_DESCENDANT_OR_SELF);
                        } else if (nameHandle == fFollowingSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_FOLLOWING);
                        } else if (nameHandle == fFollowingSiblingSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_FOLLOWING_SIBLING);
                        } else if (nameHandle == fNamespaceSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_NAMESPACE);
                        } else if (nameHandle == fParentSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_PARENT);
                        } else if (nameHandle == fPrecedingSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_PRECEDING);
                        } else if (nameHandle == fPrecedingSiblingSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_PRECEDING_SIBLING);
                        } else if (nameHandle == fSelfSymbol) {
                            addToken(tokens, XPath.Tokens.EXPRTOKEN_AXISNAME_SELF);
                        } else {
                // System.out.println("abort 9");
                            return false; // REVISIT
                        }
                        if (isNameTestNCName) {
                // System.out.println("abort 10");
                            return false; // REVISIT - "NCName:* ::" where "AxisName ::" is required
                        }
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_DOUBLE_COLON);
                        starIsMultiplyOperator = false;
                        if (!isAxisName) {
                            currentOffset++;
                            if (++currentOffset == endOffset) {
                                break;
                            }
                        }
                        break;
                    }
                    //
                    //  Otherwise, the token must not be recognized as an OperatorName, a NodeType, a
                    //  FunctionName, or an AxisName.
                    //
                    if (isNameTestNCName) {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_NAMETEST_NAMESPACE);
                        starIsMultiplyOperator = true;
                        tokens.addToken(nameHandle);
                    } else {
                        addToken(tokens, XPath.Tokens.EXPRTOKEN_NAMETEST_QNAME);
                        starIsMultiplyOperator = true;
                        tokens.addToken(prefixHandle);
                        tokens.addToken(nameHandle);
                    }
                    break;
                }
            }
            if (XPath.Tokens.DUMP_TOKENS) {
                tokens.dumpTokens();
            }
            return true;
        }
        //
        // [5] NCName ::= (Letter | '_') (NCNameChar)*
        // [6] NCNameChar ::= Letter | Digit | '.' | '-' | '_' | CombiningChar | Extender
        //
        int scanNCName(String data, int endOffset, int currentOffset) {
            int ch = data.charAt(currentOffset);
            if (ch >= 0x80) {
                if (!XMLChar.isNameStart(ch))
                /*** // REVISIT: Make sure this is a negation. ***
                if ((XMLCharacterProperties.fgCharFlags[ch] &
                     XMLCharacterProperties.E_InitialNameCharFlag) == 0)
                /***/
                {
                    return currentOffset;
                }
            }
            else {
                byte chartype = fASCIICharMap[ch];
                if (chartype != CHARTYPE_LETTER && chartype != CHARTYPE_UNDERSCORE) {
                    return currentOffset;
                }
            }
            while (++currentOffset < endOffset) {
                ch = data.charAt(currentOffset);
                if (ch >= 0x80) {
                    if (!XMLChar.isName(ch))
                    /*** // REVISIT: Make sure this is a negation. ***
                    if ((XMLCharacterProperties.fgCharFlags[ch] &
                         XMLCharacterProperties.E_NameCharFlag) == 0)
                    /***/
                    {
                        break;
                    }
                }
                else {
                    byte chartype = fASCIICharMap[ch];
                    if (chartype != CHARTYPE_LETTER && chartype != CHARTYPE_DIGIT &&
                        chartype != CHARTYPE_PERIOD && chartype != CHARTYPE_MINUS &&
                        chartype != CHARTYPE_UNDERSCORE)
                    {
                        break;
                    }
                }
            }
            return currentOffset;
        }
        /*
        void allocateProducer(byte[] data, int offset, int length, EncodingSupport encoding) {
            XPathStringProducer sp = fStringProducers[fStringProducerCount];
            if (sp != null) {
                sp = sp.setState(data, offset, length, encoding);
            } else {
                sp = new XPathStringProducer(data, offset, length, encoding);
            }
            fStringProducers[fStringProducerCount++] = sp;
        }
        void finalizeProducer(byte[] data) {
            fStringProducerCount--;
        }
        private class XPathStringProducer {
            byte[] fData = null;
            int fOffset = -1;
            int fLength = -1;
            String fEncoding = null;
            XPathStringProducer(byte[] data, int offset, int length, EncodingSupport encoding) {
                init(data, offset, length, encoding);
            }
            XPathStringProducer setState(byte[] bytes, int offset, int length, EncodingSupport encoding) {
                init(bytes, offset, length, encoding);
                return this;
            }
            void init(byte[] data, int offset, int length, EncodingSupport encoding) {
                fData = data;
                fOffset = offset;
                fLength = length;
                fEncoding = encoding;
            }
            String getEncoding() {
                return fEncoding;
            }
            void finalizeProducer() {
                // do nothing
            }
            int addSymbol(int offset, int length) {
                return fSymbolTable.addSymbol(fData, offset, length, fEncoding);
            }
        }
        private XPathStringProducer[] fStringProducers = new XPathStringProducer[8];
        private int fStringProducerCount = 0;
        private XPathStringProducer getStringProducer(byte[] data) {
            XPathStringProducer sp = null;
            for (int i = 0; i < fStringProducerCount; i++) {
                if (fStringProducers[i].fData == data) {
                    return fStringProducers[i];
                }
            }
            throw new RuntimeException("No StringProducer");
        }
        */
        //
        // [30] Number ::= Digits ('.' Digits?)? | '.' Digits
        // [31] Digits ::= [0-9]+
        //
        private int scanNumber(XPath.Tokens tokens, String/*byte[]*/ data, int endOffset, int currentOffset/*, EncodingSupport encoding*/) {
            int ch = data.charAt(currentOffset);
            int whole = 0;
            int part = 0;
            while (ch >= '0' && ch <= '9') {
                whole = (whole * 10) + (ch - '0');
                if (++currentOffset == endOffset) {
                    break;
                }
                ch = data.charAt(currentOffset);
            }
            if (ch == '.') {
                if (++currentOffset < endOffset) {
                    int start = currentOffset;
                    ch = data.charAt(currentOffset);
                    while (ch >= '0' && ch <= '9') {
                        part = (part * 10) + (ch - '0');
                        if (++currentOffset == endOffset) {
                            break;
                        }
                        ch = data.charAt(currentOffset);
                    }
                    if (part != 0) {
                        /***
                        part = tokens.addSymbol(data, start, currentOffset - start, encoding);
                        /***/
                        throw new RuntimeException("find a solution!");
                        //part = fStringPool.addSymbol(data.substring(start, currentOffset));
                        /***/
                    }
                }
            }
            tokens.addToken(whole);
            tokens.addToken(part);
            return currentOffset;
        }

        /***
        public static SymbolTable getGlobalTokens() {
            return fgSymbolTable;
        }

        public static void main(String argv[]) {
            try {
                SymbolTable symbols = new SymbolTable(XPathExprScanner.getGlobalTokens());
                XPath.Tokens tokens = new XPath.Tokens(symbols);
                byte[] bytes = new byte[1 << 8]; // 256
                int i = 0;
                if (XPath.Tokens.DUMP_TOKENS) {
                    System.out.println("<output>");
                    System.out.println();
                }
                while (i < argv.length) {
                    String uri = argv[i++];
                    // System.out.println("uri: "+uri);
                    FileInputStream is = new FileInputStream(uri);
                    int lineOffset = 0;
                    int offset = 0;
                    while (true) {
                        int avail = bytes.length - offset;
                        if (avail == 0) {
                            avail = bytes.length;
                            byte[] newBytes = new byte[avail << 1];
                            System.arraycopy(bytes, 0, newBytes, 0, avail);
                            bytes = newBytes;
                        }
                        int result = is.read(bytes, offset, avail);
                        if (result == -1) {
                            bytes[offset] = 0;
                            break;
                        }
                        result += offset;
                        for (int j = offset; j < result; j++) {
                            int ch = bytes[j];
                            if (ch == 0x0A || ch == 0x0D) {
                                if (lineOffset < offset) {
                                    XPathExprScanner.scanExpr(tokens, bytes, lineOffset, offset, UTF8EncodingSupport.getInstance());
                                }
                                while (ch == 0x0A || ch == 0x0D) {
                                    if (++j == result) {
                                        j = result;
                                        break;
                                    }
                                    ch = bytes[j];
                                }
                                lineOffset = offset;
                                if (j == result) {
                                    break;
                                }
                            }
                            bytes[offset++] = (byte)ch;
                        }
                    }
                    is.close();
                }
                if (XPath.Tokens.DUMP_TOKENS) {
                    System.out.println("</output>");
                }
            }
            catch (Exception e) {
                e.printStackTrace();
            }
        }
        /***/

        //
        // Protected methods
        //

        /**
         * This method adds the specified token to the token list. By
         * default, this method allows all tokens. However, subclasses
         * of the XPathExprScanner can override this method in order
         * to disallow certain tokens from being used in the scanned
         * XPath expression. This is a convenient way of allowing only
         * a subset of XPath.
         */
        protected void addToken(XPath.Tokens tokens, int token)
            throws XPathException {
            tokens.addToken(token);
        } // addToken(int)

    } // class Scanner

    /**
     * @author Glenn Marcy, IBM
     * @author Andy Clark, IBM
     *
     * @version $Id$
     */
    /***
    public static class XPathExprParser {

        //
        // Constants
        //

        private static final boolean DUMP_PARSE_TREE = false;

        private static final boolean DEBUG_PUSH_PARSEOPS = false;

        /** Parse Tree operations * /
        public static final int
            PARSEOP_OR                              = -5000,
            PARSEOP_AND                             = -5001,
            PARSEOP_EQUAL                           = -5002,
            PARSEOP_NOT_EQUAL                       = -5003,
            PARSEOP_PLUS                            = -5004,
            PARSEOP_MINUS                           = -5005,
            PARSEOP_MULT                            = -5006,
            PARSEOP_DIV                             = -5007,
            PARSEOP_MOD                             = -5008,
            PARSEOP_LESS                            = -5009,
            PARSEOP_GREATER                         = -5010,
            PARSEOP_LESS_EQUAL                      = -5011,
            PARSEOP_GREATER_EQUAL                   = -5012,
            PARSEOP_NEGATE                          = -5013,
            PARSEOP_UNION                           = -5014,
            PARSEOP_SELECT_ROOT                     = -5015,
            PARSEOP_STEPS                           = -5016,
            PARSEOP_STEP                            = -5017,
            PARSEOP_AXIS_ANCESTOR                   = -5018,
            PARSEOP_AXIS_ANCESTOR_OR_SELF           = -5019,
            PARSEOP_AXIS_ATTRIBUTE                  = -5020,
            PARSEOP_AXIS_CHILD                      = -5021,
            PARSEOP_AXIS_DESCENDANT                 = -5022,
            PARSEOP_AXIS_DESCENDANT_OR_SELF         = -5023,
            PARSEOP_AXIS_FOLLOWING                  = -5024,
            PARSEOP_AXIS_FOLLOWING_SIBLING          = -5025,
            PARSEOP_AXIS_NAMESPACE                  = -5026,
            PARSEOP_AXIS_PARENT                     = -5027,
            PARSEOP_AXIS_PRECEDING                  = -5028,
            PARSEOP_AXIS_PRECEDING_SIBLING          = -5029,
            PARSEOP_AXIS_SELF                       = -5030,
            PARSEOP_NODETEST_ANY                    = -5031,
            PARSEOP_NODETEST_NAMESPACE              = -5032,
            PARSEOP_NODETEST_QNAME                  = -5033,
            PARSEOP_NODETEST_COMMENT                = -5034,
            PARSEOP_NODETEST_TEXT                   = -5035,
            PARSEOP_NODETEST_PI                     = -5036,
            PARSEOP_NODETEST_PI_TARGET              = -5037,
            PARSEOP_NODETEST_NODE                   = -5038,
            PARSEOP_FILTER                          = -5039,
            PARSEOP_PREDICATES                      = -5040,
            PARSEOP_PREDICATE                       = -5041,
            PARSEOP_VARIABLE_REFERENCE              = -5042,
            PARSEOP_GROUPING                        = -5043,
            PARSEOP_LITERAL                         = -5044,
            PARSEOP_NUMBER                          = -5045,
            PARSEOP_FUNCTION                        = -5046,
            PARSEOP_FUNCTION_NAME                   = -5047,
            PARSEOP_FUNCTION_ARGUMENTS              = -5048;

        //
        // Data
        //

        private int fTokenCount = 0;  // for reading
        private int fCurrentToken = 0;  // for reading

        private static final int INITIAL_PARSEOP_COUNT = 1 << 8;
        private int[] fParseTree = new int[INITIAL_PARSEOP_COUNT];
        private int fParseOpCount = 0;    // for writing
        private int fCurrentParseOp = 0;  // for reading

        /** Symbol table. * /
        private SymbolTable fSymbolTable;

        /** Tokens. * /
        private XPath.Tokens fTokens;

        /** Scanner. * /
        private XPathExprScanner fScanner;

        //
        // Constructors
        //

        public XPathExprParser() {
            this(new SymbolTable());
        }

        public XPathExprParser(SymbolTable symbolTable) {
            this(symbolTable, new XPathExprScanner(symbolTable));
        }

        public XPathExprParser(SymbolTable symbolTable, XPathExprScanner scanner) {

            fSymbolTable = symbolTable;
            fScanner = scanner;

        } // <init>(SymbolTable,XPathExprScanner)

        //
        // Public methods
        //

        // init

        public void reset() {
            fParseOpCount = 0;
            fCurrentParseOp = 0;
        }

        // parsing

        public int parseExpr(String data) throws XPathException {
            return parseExpr(data, 0, data.length());
        }

        public int parseExpr(String data, int currentOffset, int endOffset)
            throws XPathException {
            return parseExprOrPattern(data, currentOffset, endOffset, false);
        }

        public int parsePattern(String data, int currentOffset, int endOffset)
            throws XPathException {
            return parseExprOrPattern(data, currentOffset, endOffset, true);
        }

        public int parseExprOrPattern(String data, int currentOffset,
                                      int endOffset, boolean isPattern)
            throws XPathException {
            fTokenCount = 0;

            if (DUMP_PARSE_TREE) {
                System.out.println("  <test>");
                System.out.println("    <expression>");
                System.out.println("      " + data.substring(currentOffset, endOffset));
                System.out.println("    </expression>");
            }
            fTokens = new XPath.Tokens(fSymbolTable);
            fScanner.scanExpr(fTokens, data, currentOffset, endOffset);
            //
            // Build parse tree
            //
            fTokenCount = fTokens.getTokenCount();
            fCurrentToken = 0;
            if (!parseExpr()) {
                // System.out.println("abort 12");
                return -1; // REVISIT
            }
            if (fCurrentToken < fTokenCount) {
                // System.out.println("abort 13");
                return -1; // REVISIT
            }
            if (DUMP_PARSE_TREE) {
                dumpParseTree(fCurrentParseOp, 4);
            }
            if (DUMP_PARSE_TREE) {
                System.out.println("  </test>");
                System.out.println();
            }
            return fCurrentParseOp;
        }

        // parse tree ops

        public int getCurrentParseOp() {
            return fCurrentParseOp;
        }

        public int getParseTreeOp(int handle) {
            return fParseTree[handle];
        }

        public int getParseTreeSubHandle(int handle, int subHandleIndex) {
            return fParseTree[handle - 1 - subHandleIndex];
        }

        public String getParseTreeSymbol(int handle, int subHandleIndex) {
            int symHandle = fParseTree[handle - 1 - subHandleIndex];
            return fTokens.getTokenString(symHandle);
        }

        public int getParseTreeIntValue(int handle, int subHandleIndex) {
            return fParseTree[handle - 1 - subHandleIndex];
        }

        // debugging

        public void dumpParseTree(int rootParseOp, int indent) {
                indentPrint(indent);
                System.out.println("<parse-tree>");
                dumpParseTreeNode(rootParseOp, indent + 2);
                indentPrint(indent);
                System.out.println("</parse-tree>");
        }

        public String getParseOpName(int parseOp) {
            switch (parseOp) {
                case PARSEOP_OR: return "PARSEOP_OR";
                case PARSEOP_AND: return "PARSEOP_AND";
                case PARSEOP_EQUAL: return "PARSEOP_EQUAL";
                case PARSEOP_NOT_EQUAL: return "PARSEOP_NOT_EQUAL";
                case PARSEOP_PLUS: return "PARSEOP_PLUS";
                case PARSEOP_MINUS: return "PARSEOP_MINUS";
                case PARSEOP_MULT: return "PARSEOP_MULT";
                case PARSEOP_DIV: return "PARSEOP_DIV";
                case PARSEOP_MOD: return "PARSEOP_MOD";
                case PARSEOP_LESS: return "PARSEOP_LESS";
                case PARSEOP_GREATER: return "PARSEOP_GREATER";
                case PARSEOP_LESS_EQUAL: return "PARSEOP_LESS_EQUAL";
                case PARSEOP_GREATER_EQUAL: return "PARSEOP_GREATER_EQUAL";
                case PARSEOP_NEGATE: return "PARSEOP_NEGATE";
                case PARSEOP_UNION: return "PARSEOP_UNION";
                case PARSEOP_SELECT_ROOT: return "PARSEOP_SELECT_ROOT";
                case PARSEOP_STEPS: return "PARSEOP_STEPS";
                case PARSEOP_STEP: return "PARSEOP_STEP";
                case PARSEOP_AXIS_ANCESTOR: return "PARSEOP_AXIS_ANCESTOR";
                case PARSEOP_AXIS_ANCESTOR_OR_SELF: return "PARSEOP_AXIS_ANCESTOR_OR_SELF";
                case PARSEOP_AXIS_ATTRIBUTE: return "PARSEOP_AXIS_ATTRIBUTE";
                case PARSEOP_AXIS_CHILD: return "PARSEOP_AXIS_CHILD";
                case PARSEOP_AXIS_DESCENDANT: return "PARSEOP_AXIS_DESCENDANT";
                case PARSEOP_AXIS_DESCENDANT_OR_SELF: return "PARSEOP_AXIS_DESCENDANT_OR_SELF";
                case PARSEOP_AXIS_FOLLOWING: return "PARSEOP_AXIS_FOLLOWING";
                case PARSEOP_AXIS_FOLLOWING_SIBLING: return "PARSEOP_AXIS_FOLLOWING_SIBLING";
                case PARSEOP_AXIS_NAMESPACE: return "PARSEOP_AXIS_NAMESPACE";
                case PARSEOP_AXIS_PARENT: return "PARSEOP_AXIS_PARENT";
                case PARSEOP_AXIS_PRECEDING: return "PARSEOP_AXIS_PRECEDING";
                case PARSEOP_AXIS_PRECEDING_SIBLING: return "PARSEOP_AXIS_PRECEDING_SIBLING";
                case PARSEOP_AXIS_SELF: return "PARSEOP_AXIS_SELF";
                case PARSEOP_NODETEST_ANY: return "PARSEOP_NODETEST_ANY";
                case PARSEOP_NODETEST_NAMESPACE: return "PARSEOP_NODETEST_NAMESPACE";
                case PARSEOP_NODETEST_QNAME: return "PARSEOP_NODETEST_QNAME";
                case PARSEOP_NODETEST_COMMENT: return "PARSEOP_NODETEST_COMMENT";
                case PARSEOP_NODETEST_TEXT: return "PARSEOP_NODETEST_TEXT";
                case PARSEOP_NODETEST_PI: return "PARSEOP_NODETEST_PI";
                case PARSEOP_NODETEST_PI_TARGET: return "PARSEOP_NODETEST_PI_TARGET";
                case PARSEOP_NODETEST_NODE: return "PARSEOP_NODETEST_NODE";
                case PARSEOP_FILTER: return "PARSEOP_FILTER";
                case PARSEOP_PREDICATES: return "PARSEOP_PREDICATES";
                case PARSEOP_PREDICATE: return "PARSEOP_PREDICATE";
                case PARSEOP_VARIABLE_REFERENCE: return "PARSEOP_VARIABLE_REFERENCE";
                case PARSEOP_GROUPING: return "PARSEOP_GROUPING";
                case PARSEOP_LITERAL: return "PARSEOP_LITERAL";
                case PARSEOP_NUMBER: return "PARSEOP_NUMBER";
                case PARSEOP_FUNCTION: return "PARSEOP_FUNCTION";
                case PARSEOP_FUNCTION_NAME: return "PARSEOP_FUNCTION_NAME";
                case PARSEOP_FUNCTION_ARGUMENTS: return "PARSEOP_FUNCTION_ARGUMENTS";
            }
            return "??? ("+parseOp+')';
        }

        //
        // Protected methods
        //

        protected void checkParseOp(int parseOp) throws XPathException {
            // do nothing; all parse ops allowed in the class
        }

        //
        // Private methods
        //

        private void pushParseOp(int parseOp) throws XPathException {
            if (DEBUG_PUSH_PARSEOPS) {
                System.out.println("pushParseOp: "+getParseOpName(parseOp));
            }
            checkParseOp(parseOp);
            try {
                fParseTree[fParseOpCount] = parseOp;
            } catch (ArrayIndexOutOfBoundsException ex) {
                int[] oldList = fParseTree;
                fParseTree = new int[fParseOpCount << 1];
                System.arraycopy(oldList, 0, fParseTree, 0, fParseOpCount);
                fParseTree[fParseOpCount] = parseOp;
            }
            fCurrentParseOp = fParseOpCount++;
        }

        private void pushParseOp2(int parseOp, int arg) throws XPathException {
            if (DEBUG_PUSH_PARSEOPS) {
                System.out.println("pushParseOp2: "+getParseOpName(parseOp)+", "+arg);
            }
            checkParseOp(parseOp);
            try {
                fParseTree[fParseOpCount + 1] = parseOp;
            } catch (ArrayIndexOutOfBoundsException ex) {
                int[] oldList = fParseTree;
                fParseTree = new int[fParseOpCount << 1];
                System.arraycopy(oldList, 0, fParseTree, 0, fParseOpCount);
                fParseTree[fParseOpCount + 1] = parseOp;
            }
            fParseTree[fParseOpCount++] = arg;
            fCurrentParseOp = fParseOpCount++;
        }

        private void pushParseOp3(int parseOp, int arg1, int arg2)
            throws XPathException {
            if (DEBUG_PUSH_PARSEOPS) {
                System.out.println("pushParseOp3: "+getParseOpName(parseOp)+", "+arg1+", "+arg2);
            }
            checkParseOp(parseOp);
            try {
                fParseTree[fParseOpCount + 2] = parseOp;
            } catch (ArrayIndexOutOfBoundsException ex) {
                int[] oldList = fParseTree;
                fParseTree = new int[fParseOpCount << 1];
                System.arraycopy(oldList, 0, fParseTree, 0, fParseOpCount);
                fParseTree[fParseOpCount + 2] = parseOp;
            }
            fParseTree[fParseOpCount++] = arg2;
            fParseTree[fParseOpCount++] = arg1;
            fCurrentParseOp = fParseOpCount++;
        }

        private void indentPrint(int indent) {
            for (int i = 0; i < indent; i++) {
                System.out.print(" ");
            }
        }

        private void dumpParseTreeNode(int parseOp, int indent) {
                switch (fParseTree[parseOp]) {
                case PARSEOP_OR:
                    indentPrint(indent);
                    System.out.println("<or>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</or>");
                    break;
                case PARSEOP_AND:
                    indentPrint(indent);
                    System.out.println("<and>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</and>");
                    break;
                case PARSEOP_EQUAL:
                    indentPrint(indent);
                    System.out.println("<equal>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</equal>");
                    break;
                case PARSEOP_NOT_EQUAL:
                    indentPrint(indent);
                    System.out.println("<not-equal>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</not-equal>");
                    break;
                case PARSEOP_PLUS:
                    indentPrint(indent);
                    System.out.println("<plus>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</plus>");
                    break;
                case PARSEOP_MINUS:
                    indentPrint(indent);
                    System.out.println("<minus>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</minus>");
                    break;
                case PARSEOP_MULT:
                    indentPrint(indent);
                    System.out.println("<mult>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</mult>");
                    break;
                case PARSEOP_DIV:
                    indentPrint(indent);
                    System.out.println("<div>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</div>");
                    break;
                case PARSEOP_MOD:
                    indentPrint(indent);
                    System.out.println("<mod>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</mod>");
                    break;
                case PARSEOP_LESS:
                    indentPrint(indent);
                    System.out.println("<less>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</less>");
                    break;
                case PARSEOP_GREATER:
                    indentPrint(indent);
                    System.out.println("<greater>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</greater>");
                    break;
                case PARSEOP_LESS_EQUAL:
                    indentPrint(indent);
                    System.out.println("<less-equal>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</less-equal>");
                    break;
                case PARSEOP_GREATER_EQUAL:
                    indentPrint(indent);
                    System.out.println("<greater-equal>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</greater-equal>");
                    break;
                case PARSEOP_NEGATE:
                    indentPrint(indent);
                    System.out.println("<negate>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    indentPrint(indent);
                    System.out.println("</negate>");
                    break;
                case PARSEOP_UNION:
                    indentPrint(indent);
                    System.out.println("<union>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</union>");
                    break;
                case PARSEOP_SELECT_ROOT:
                    indentPrint(indent);
                    if (fParseTree[parseOp - 1] == -1) {
                        System.out.println("<select-root/>");
                    } else {
                        System.out.println("<select-root>");
                        dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                        indentPrint(indent);
                        System.out.println("</select-root>");
                    }
                    break;
                case PARSEOP_STEPS:
                    indentPrint(indent);
                    System.out.println("<relative-location-path>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</relative-location-path>");
                    break;
                case PARSEOP_STEP:
                    indentPrint(indent);
                    System.out.println("<step>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</step>");
                    break;
                case PARSEOP_AXIS_ANCESTOR:
                    indentPrint(indent);
                    System.out.println("<axis name=\"ancestor\"/>");
                    break;
                case PARSEOP_AXIS_ANCESTOR_OR_SELF:
                    indentPrint(indent);
                    System.out.println("<axis name=\"ancestor-or-self\"/>");
                    break;
                case PARSEOP_AXIS_ATTRIBUTE:
                    indentPrint(indent);
                    System.out.println("<axis name=\"attribute\"/>");
                    break;
                case PARSEOP_AXIS_CHILD:
                    indentPrint(indent);
                    System.out.println("<axis name=\"child\"/>");
                    break;
                case PARSEOP_AXIS_DESCENDANT:
                    indentPrint(indent);
                    System.out.println("<axis name=\"descendant\"/>");
                    break;
                case PARSEOP_AXIS_DESCENDANT_OR_SELF:
                    indentPrint(indent);
                    System.out.println("<axis name=\"descendant-or-self\"/>");
                    break;
                case PARSEOP_AXIS_FOLLOWING:
                    indentPrint(indent);
                    System.out.println("<axis name=\"following\"/>");
                    break;
                case PARSEOP_AXIS_FOLLOWING_SIBLING:
                    indentPrint(indent);
                    System.out.println("<axis name=\"following-sibling\"/>");
                    break;
                case PARSEOP_AXIS_NAMESPACE:
                    indentPrint(indent);
                    System.out.println("<axis name=\"namespace\"/>");
                    break;
                case PARSEOP_AXIS_PARENT:
                    indentPrint(indent);
                    System.out.println("<axis name=\"parent\"/>");
                    break;
                case PARSEOP_AXIS_PRECEDING:
                    indentPrint(indent);
                    System.out.println("<axis name=\"preceding\"/>");
                    break;
                case PARSEOP_AXIS_PRECEDING_SIBLING:
                    indentPrint(indent);
                    System.out.println("<axis name=\"preceding-sibling\"/>");
                    break;
                case PARSEOP_AXIS_SELF:
                    indentPrint(indent);
                    System.out.println("<axis name=\"self\"/>");
                    break;
                case PARSEOP_NODETEST_ANY:
                    indentPrint(indent);
                    System.out.println("<nodetest type=\"any\"/>");
                    break;
                case PARSEOP_NODETEST_NAMESPACE:
                    indentPrint(indent);
                    System.out.print("<nodetest type=\"namespace\"");
                    System.out.print(" prefix=\"" + fParseTree[parseOp - 1] + "\"");
                    System.out.println("/>");
                    break;
                case PARSEOP_NODETEST_QNAME:
                    indentPrint(indent);
                    System.out.print("<nodetest type=\"qname\"");
                    if (fParseTree[parseOp - 1] != -1) {
                        System.out.print(" prefix=\"" + fParseTree[parseOp - 1] + "\"");
                    }
                    System.out.print(" localpart=\"" + fParseTree[parseOp - 2] + "\"");
                    System.out.println("/>");
                    break;
                case PARSEOP_NODETEST_COMMENT:
                    indentPrint(indent);
                    System.out.println("<nodetest type=\"comment\"/>");
                    break;
                case PARSEOP_NODETEST_TEXT:
                    indentPrint(indent);
                    System.out.println("<nodetest type=\"text\"/>");
                    break;
                case PARSEOP_NODETEST_PI:
                    indentPrint(indent);
                    System.out.println("<nodetest type=\"processing-instruction\"/>");
                    break;
                case PARSEOP_NODETEST_PI_TARGET:
                    indentPrint(indent);
                    System.out.print("<nodetest type=\"processing-instruction\" target=\"");
                    System.out.print(fParseTree[parseOp - 1]);
                    System.out.println("\"/>");
                    break;
                case PARSEOP_NODETEST_NODE:
                    indentPrint(indent);
                    System.out.println("<nodetest type=\"node\"/>");
                    break;
                case PARSEOP_FILTER:
                    indentPrint(indent);
                    System.out.println("<step-with-predicate>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</step-with-predicate>");
                    break;
                case PARSEOP_PREDICATES:
                    indentPrint(indent);
                    System.out.println("<predicates>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</predicates>");
                    break;
                case PARSEOP_PREDICATE:
                    indentPrint(indent);
                    System.out.println("<predicate>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    indentPrint(indent);
                    System.out.println("</predicate>");
                    break;
                case PARSEOP_VARIABLE_REFERENCE:
                    indentPrint(indent);
                    System.out.print("<variable-reference");
                    if (fParseTree[parseOp - 1] != -1) {
                        System.out.print(" prefix=\"" + fParseTree[parseOp - 1] + "\"");
                    }
                    System.out.print(" localpart=\"" + fParseTree[parseOp - 2] + "\"");
                    System.out.println("/>");
                    break;
                case PARSEOP_GROUPING:
                    indentPrint(indent);
                    System.out.println("<grouping>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    indentPrint(indent);
                    System.out.println("</grouping>");
                    break;
                case PARSEOP_LITERAL:
                    indentPrint(indent);
                    System.out.print("<literal");
                    System.out.print(" value=\"" + fParseTree[parseOp - 1] + "\"");
                    System.out.println("/>");
                    break;
                case PARSEOP_NUMBER:
                    indentPrint(indent);
                    System.out.print("<number");
                    System.out.print(" whole=\"" + fParseTree[parseOp - 1] + "\"");
                    System.out.print(" part=\"" + fParseTree[parseOp - 2] + "\"");
                    System.out.println("/>");
                    break;
                case PARSEOP_FUNCTION:
                    indentPrint(indent);
                    System.out.println("<function-call>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    if (fParseTree[parseOp - 2] != -1) {
                        dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    }
                    indentPrint(indent);
                    System.out.println("</function-call>");
                    break;
                case PARSEOP_FUNCTION_NAME:
                    indentPrint(indent);
                    System.out.print("<function-name");
                    if (fParseTree[parseOp - 1] != -1) {
                        System.out.print(" prefix=\"" + fParseTree[parseOp - 1] + "\"");
                    }
                    System.out.print(" localpart=\"" + fParseTree[parseOp - 2] + "\"");
                    System.out.println("/>");
                    break;
                case PARSEOP_FUNCTION_ARGUMENTS:
                    indentPrint(indent);
                    System.out.println("<function-args>");
                    dumpParseTreeNode(fParseTree[parseOp - 1], indent + 2);
                    dumpParseTreeNode(fParseTree[parseOp - 2], indent + 2);
                    indentPrint(indent);
                    System.out.println("</function-args>");
                    break;
                default:
                    throw new RuntimeException("dumpParseTreeNode("+parseOp+")");
                }
        }

        //
        // Package methods
        //

        /**
         * [14] Expr ::= OrExpr
         * /
        boolean parseExpr() throws XPathException {
            return parseOrExpr();
        }

        /**
         * [21] OrExpr ::= AndExpr | OrExpr 'or' AndExpr
         *
         * also: OrExpr ::= (AndExpr 'or')* AndExpr
         * /
        boolean parseOrExpr() throws XPathException {
            if (!parseAndExpr()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_OPERATOR_OR) {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parseAndExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                int right = fCurrentParseOp;
                pushParseOp3(PARSEOP_OR, left, right);
            }
            return true;
        }

        /**
         * [22] AndExpr ::= EqualityExpr | AndExpr 'and' EqualityExpr
         * /
        boolean parseAndExpr() throws XPathException {
            if (!parseEqualityExpr()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_OPERATOR_AND) {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parseEqualityExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                int right = fCurrentParseOp;
                pushParseOp3(PARSEOP_AND, left, right);
            }
            return true;
        }

        /**
         * [23] EqualityExpr ::= RelationalExpr
         *                     | EqualityExpr '=' RelationalExpr
         *                     | EqualityExpr '!=' RelationalExpr
         * /
        boolean parseEqualityExpr() throws XPathException {
            if (!parseRelationalExpr()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                int parseOp;
                if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_EQUAL) {
                    parseOp = PARSEOP_EQUAL;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_NOT_EQUAL) {
                    parseOp = PARSEOP_NOT_EQUAL;
                } else {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parseRelationalExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                int right = fCurrentParseOp;
                pushParseOp3(parseOp, left, right);
            }
            return true;
        }

        /**
         * [24] RelationalExpr ::= AdditiveExpr
         *                       | RelationalExpr '<' AdditiveExpr
         *                       | RelationalExpr '>' AdditiveExpr
         *                       | RelationalExpr '<=' AdditiveExpr
         *                       | RelationalExpr '>=' AdditiveExpr
         * /
        boolean parseRelationalExpr() throws XPathException {
            if (!parseAdditiveExpr()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                int parseOp;
                if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_LESS) {
                    parseOp = PARSEOP_LESS;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_GREATER) {
                    parseOp = PARSEOP_GREATER;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_LESS_EQUAL) {
                    parseOp = PARSEOP_LESS_EQUAL;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_GREATER_EQUAL) {
                    parseOp = PARSEOP_GREATER_EQUAL;
                } else {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parseAdditiveExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                int right = fCurrentParseOp;
                pushParseOp3(parseOp, left, right);
            }
            return true;
        }

        /**
         * [25] AdditiveExpr ::= MultiplicativeExpr
         *                     | AdditiveExpr '+' MultiplicativeExpr
         *                     | AdditiveExpr '-' MultiplicativeExpr
         * /
        boolean parseAdditiveExpr() throws XPathException {
            if (!parseMultiplicativeExpr()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                int parseOp;
                if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_PLUS) {
                    parseOp = PARSEOP_PLUS;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_MINUS) {
                    parseOp = PARSEOP_MINUS;
                } else {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parseMultiplicativeExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                int right = fCurrentParseOp;
                pushParseOp3(parseOp, left, right);
            }
            return true;
        }

        /**
         * [26] MultiplicativeExpr ::= UnaryExpr
         *                           | MultiplicativeExpr MultiplyOperator UnaryExpr
         *                           | MultiplicativeExpr 'div' UnaryExpr
         *                           | MultiplicativeExpr 'mod' UnaryExpr
         * [34] MultiplyOperator ::= '*'
         * /
        boolean parseMultiplicativeExpr() throws XPathException {
            if (!parseUnaryExpr()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                int parseOp;
                if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_MULT) {
                    parseOp = PARSEOP_MULT;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_DIV) {
                    parseOp = PARSEOP_DIV;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_MOD) {
                    parseOp = PARSEOP_MOD;
                } else {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parseUnaryExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                int right = fCurrentParseOp;
                pushParseOp3(parseOp, left, right);
            }
            return true;
        }

        /**
         * [27] UnaryExpr ::= UnionExpr | '-' UnaryExpr
         *
         * Note: "--UnionExpr" == "-(-UnionExpr)"
         * /
        boolean parseUnaryExpr() throws XPathException {
            if (parseUnionExpr()) {
                return true;
            }
            int saveToken = fCurrentToken;
            boolean negate = false;
            while (fCurrentToken < fTokenCount) {
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_OPERATOR_MINUS) {
                    break;
                }
                fCurrentToken++;
                negate = !negate;
            }
            if (fCurrentToken == fTokenCount) {
                fCurrentToken = saveToken;
                return false;
            }
            if (!parseUnionExpr()) {
                fCurrentToken = saveToken;
                return false;
            }
            if (negate) {
                pushParseOp2(PARSEOP_NEGATE, fCurrentParseOp);
            }
            return true;
        }

        /**
         * [18] UnionExpr ::= PathExpr | UnionExpr '|' PathExpr
         * /
        boolean parseUnionExpr() throws XPathException {
            if (!parsePathExpr()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_OPERATOR_UNION) {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parsePathExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                int right = fCurrentParseOp;
                pushParseOp3(PARSEOP_UNION, left, right);
            }
            return true;
        }

        /**
         * [19] PathExpr ::= RelativeLocationPath
         *                 | '/' RelativeLocationPath?
         *                 | '//' RelativeLocationPath
         *                 | PrimaryExpr Predicate*
         *                 | PrimaryExpr Predicate* '/' RelativeLocationPath
         *                 | PrimaryExpr Predicate* '//' RelativeLocationPath
         * /
        boolean parsePathExpr() throws XPathException {
            if (parseRelativeLocationPath()) {
                return true;
            } else {
                if (fCurrentToken == fTokenCount) {
                    return false;
                }
                if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH) {
                    if (++fCurrentToken < fTokenCount && parseRelativeLocationPath()) {
                        pushParseOp2(PARSEOP_SELECT_ROOT, fCurrentParseOp);
                    } else {
                        pushParseOp2(PARSEOP_SELECT_ROOT, -1);
                    }
                    return true;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_DOUBLE_SLASH) {
                    if (++fCurrentToken == fTokenCount) {
                        return false; // REVISIT - backup index
                    }
                    if (!parseRelativeLocationPath()) {
                        return false;
                    }
                    int left = fCurrentParseOp;
                    pushParseOp(PARSEOP_AXIS_DESCENDANT_OR_SELF);
                    int left2 = fCurrentParseOp;
                    pushParseOp(PARSEOP_NODETEST_NODE);
                    pushParseOp3(PARSEOP_STEP, left2, fCurrentParseOp);
                    pushParseOp3(PARSEOP_STEPS, fCurrentParseOp, left);
                    pushParseOp2(PARSEOP_SELECT_ROOT, fCurrentParseOp);
                    return true;
                }
            }
            if (!parsePrimaryExpr()) {
                return false;
            }
            int left = fCurrentParseOp;
            if (parsePredicates()) {
                pushParseOp3(PARSEOP_FILTER, left, fCurrentParseOp);
            }
            if (fCurrentToken == fTokenCount) {
                return true;
            }
            left = fCurrentParseOp;
            if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH) {
                if (++fCurrentToken == fTokenCount) {
                    return false; // REVISIT
                }
                if (!parseRelativeLocationPath()) {
                    return false; // REVISIT
                }
                pushParseOp3(PARSEOP_STEPS, left, fCurrentParseOp);
            } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_DOUBLE_SLASH) {
                if (++fCurrentToken == fTokenCount) {
                    return false;
                }
                if (!parseRelativeLocationPath()) {
                    return false;
                }
                int left2 = fCurrentParseOp;
                pushParseOp(PARSEOP_AXIS_DESCENDANT_OR_SELF);
                int left3 = fCurrentParseOp;
                pushParseOp(PARSEOP_NODETEST_NODE);
                pushParseOp3(PARSEOP_STEP, left3, fCurrentParseOp);
                pushParseOp3(PARSEOP_STEPS, fCurrentParseOp, left2);
                pushParseOp3(PARSEOP_STEPS, left, fCurrentParseOp);
            }
            return true;
        }

        /**
         * [3] RelativeLocationPath ::= Step
         *                            | RelativeLocationPath '/' Step
         *                            | RelativeLocationPath '//' Step
         * /
        boolean parseRelativeLocationPath() throws XPathException {
            if (!parseStep()) {
                return false;
            }
            while (fCurrentToken < fTokenCount) {
                boolean descendantOrSelf;
                if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_SLASH) {
                    descendantOrSelf = false;
                } else if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_OPERATOR_DOUBLE_SLASH) {
                    descendantOrSelf = true;
                } else {
                    break;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                int left = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (!parseStep()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return true;
                }
                if (descendantOrSelf) {
                    int left2 = fCurrentParseOp;
                    pushParseOp(PARSEOP_AXIS_DESCENDANT_OR_SELF);
                    int left3 = fCurrentParseOp;
                    pushParseOp(PARSEOP_NODETEST_NODE);
                    pushParseOp3(PARSEOP_STEP, left3, fCurrentParseOp);
                    pushParseOp3(PARSEOP_STEPS, left, fCurrentParseOp);
                    pushParseOp3(PARSEOP_STEPS, fCurrentParseOp, left2);
                } else {
                    pushParseOp3(PARSEOP_STEPS, left, fCurrentParseOp);
                }
            }
            return true;
        }

        /**
         * [4] Step ::=  (AxisName '::' | '@'?) NodeTest Predicate* | '.' | '..'
         * [6] AxisName ::= 'ancestor' | 'ancestor-or-self'
         *                | 'attribute'
         *                | 'child'
         *                | 'descendant' | 'descendant-or-self'
         *                | 'following' | 'following-sibling'
         *                | 'namespace'
         *                | 'parent'
         *                | 'preceding' | 'preceding-sibling'
         *                | 'self'
         * /
        boolean parseStep() throws XPathException {
            int parseOp;
            int left;
            boolean checkDoubleColon = true;
            int saveToken = fCurrentToken;
            int saveParseOp = fCurrentParseOp;
            if (fCurrentToken == fTokenCount) {
                return false;
            }
            switch (fTokens.getToken(fCurrentToken)) {
            case XPath.Tokens.EXPRTOKEN_PERIOD:
                fCurrentToken++;
                pushParseOp(PARSEOP_AXIS_SELF);
                left = fCurrentParseOp;
                pushParseOp(PARSEOP_NODETEST_NODE);
                pushParseOp3(PARSEOP_STEP, left, fCurrentParseOp);
                return true;
            case XPath.Tokens.EXPRTOKEN_DOUBLE_PERIOD:
                fCurrentToken++;
                pushParseOp(PARSEOP_AXIS_PARENT);
                left = fCurrentParseOp;
                pushParseOp(PARSEOP_NODETEST_NODE);
                pushParseOp3(PARSEOP_STEP, left, fCurrentParseOp);
                return true;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_ANCESTOR:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_ANCESTOR;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_ANCESTOR_OR_SELF:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_ANCESTOR_OR_SELF;
                break;
            case XPath.Tokens.EXPRTOKEN_ATSIGN:
                checkDoubleColon = false;
                // fall through
            case XPath.Tokens.EXPRTOKEN_AXISNAME_ATTRIBUTE:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_ATTRIBUTE;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_DESCENDANT:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_DESCENDANT;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_DESCENDANT_OR_SELF:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_DESCENDANT_OR_SELF;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_FOLLOWING:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_FOLLOWING;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_FOLLOWING_SIBLING:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_FOLLOWING_SIBLING;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_NAMESPACE:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_NAMESPACE;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_PARENT:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_PARENT;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_PRECEDING:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_PRECEDING;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_PRECEDING_SIBLING:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_PRECEDING_SIBLING;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_SELF:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_SELF;
                break;
            case XPath.Tokens.EXPRTOKEN_AXISNAME_CHILD:
                fCurrentToken++;
                parseOp = PARSEOP_AXIS_CHILD;
                break;
            default:
                checkDoubleColon = false;
                parseOp = PARSEOP_AXIS_CHILD;
                break;
            }
            pushParseOp(parseOp);
            left = fCurrentParseOp;
            if (checkDoubleColon) {
                if (fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_DOUBLE_COLON) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                fCurrentToken++;
            }
            if (fCurrentToken == fTokenCount) {
                fCurrentToken = saveToken;
                fCurrentParseOp = saveParseOp;
                return false;
            }
            if (!parseNodeTest()) {
                fCurrentToken = saveToken;
                fCurrentParseOp = saveParseOp;
                return false;
            }
            pushParseOp3(PARSEOP_STEP, left, fCurrentParseOp);
            left = fCurrentParseOp;
            if (parsePredicates()) {
                pushParseOp3(PARSEOP_FILTER, left, fCurrentParseOp);
            }
            return true;
        }

        /**
         * [7] NodeTest ::= '*'
         *                | NCName ':' '*'
         *                | QName
         *                | 'comment' '(' ')'
         *                | 'text' '(' ')'
         *                | 'processing-instruction' '(' Literal? ')'
         *                | 'node' '(' ')'
         * [29] Literal ::= '"' [^"]* '"' | "'" [^']* "'"
         * /
        boolean parseNodeTest() throws XPathException {
            int parseOp;
            int prefix;
            int name;
            if (fCurrentToken == fTokenCount) {
                return false;
            }
            switch (fTokens.getToken(fCurrentToken)) {
            case XPath.Tokens.EXPRTOKEN_NAMETEST_ANY:
                fCurrentToken++;
                pushParseOp(PARSEOP_NODETEST_ANY);
                return true;
            case XPath.Tokens.EXPRTOKEN_NAMETEST_NAMESPACE:
                prefix = fTokens.getToken(++fCurrentToken);
                fCurrentToken++;
                pushParseOp2(PARSEOP_NODETEST_NAMESPACE, prefix);
                return true;
            case XPath.Tokens.EXPRTOKEN_NAMETEST_QNAME:
                prefix = fTokens.getToken(++fCurrentToken);
                name = fTokens.getToken(++fCurrentToken);
                fCurrentToken++;
                pushParseOp3(PARSEOP_NODETEST_QNAME, prefix, name);
                return true;
            case XPath.Tokens.EXPRTOKEN_NODETYPE_COMMENT:
                parseOp = PARSEOP_NODETEST_COMMENT;
                break;
            case XPath.Tokens.EXPRTOKEN_NODETYPE_TEXT:
                parseOp = PARSEOP_NODETEST_TEXT;
                break;
            case XPath.Tokens.EXPRTOKEN_NODETYPE_PI:
                parseOp = PARSEOP_NODETEST_PI;
                break;
            case XPath.Tokens.EXPRTOKEN_NODETYPE_NODE:
                parseOp = PARSEOP_NODETEST_NODE;
                break;
            default:
                return false;
            }
            int saveToken = fCurrentToken;
            int saveParseOp = fCurrentParseOp;
            int left = fCurrentParseOp;
            if (++fCurrentToken == fTokenCount) {
                fCurrentToken = saveToken;
                fCurrentParseOp = saveParseOp;
                return false;
            }
            if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_OPEN_PAREN) {
                fCurrentToken = saveToken;
                fCurrentParseOp = saveParseOp;
                return false;
            }
            if (++fCurrentToken == fTokenCount) {
                fCurrentToken = saveToken;
                fCurrentParseOp = saveParseOp;
                return false;
            }
            if (parseOp == PARSEOP_NODETEST_PI && fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_LITERAL) {
                int target = fTokens.getToken(++fCurrentToken);
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_CLOSE_PAREN) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                fCurrentToken++;
                pushParseOp2(PARSEOP_NODETEST_PI_TARGET, target);
            } else {
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_CLOSE_PAREN) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                fCurrentToken++;
                pushParseOp(parseOp);
            }
            return true;
        }

        /**
         * [8] Predicate ::= '[' PredicateExpr ']'
         * [9] PredicateExpr ::= Expr
         * [4] Step ::= AxisSpecifier NodeTest Predicate* | AbbreviatedStep
         * [20] FilterExpr ::= PrimaryExpr Predicate*
         * /
        boolean parsePredicates() throws XPathException {
            int left = -1;
            boolean found = false;
            while (true) {
                if (fCurrentToken == fTokenCount || fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_OPEN_BRACKET) {
                    return found;
                }
                int saveToken = fCurrentToken;
                int saveParseOp = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount || !parseExpr() ||
                    fCurrentToken == fTokenCount || fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_CLOSE_BRACKET) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return found;
                }
                fCurrentToken++;
                found = true;
                pushParseOp2(PARSEOP_PREDICATE, fCurrentParseOp);
                if (left != -1) {
                    pushParseOp3(PARSEOP_PREDICATES, left, fCurrentParseOp);
                }
                left = fCurrentParseOp;
            }
        }

        /**
         * [15] PrimaryExpr ::= '$' QName
         *                    | '(' Expr ')'
         *                    | '"' [^"]* '"' | "'" [^']* "'"
         *                    | ([0-9]+) ('.' ([0-9]+)?)? | '.' Digits
         *                    | (QName - NodeType) '(' ( Expr ( ',' Expr )* )? ')'
         * /
        boolean parsePrimaryExpr() throws XPathException {
            int prefix;
            int handle;
            int saveToken;
            int saveParseOp;
            if (fCurrentToken == fTokenCount) {
                return false;
            }
            switch (fTokens.getToken(fCurrentToken)) {
            case XPath.Tokens.EXPRTOKEN_VARIABLE_REFERENCE:
                prefix = fTokens.getToken(++fCurrentToken);
                handle = fTokens.getToken(++fCurrentToken); // localpart
                fCurrentToken++;
                pushParseOp3(PARSEOP_VARIABLE_REFERENCE, prefix, handle);
                break;
            case XPath.Tokens.EXPRTOKEN_OPEN_PAREN:
                saveToken = fCurrentToken;
                saveParseOp = fCurrentParseOp;
                if (++fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                if (!parseExpr()) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                if (fCurrentToken == fTokenCount) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_CLOSE_PAREN) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                fCurrentToken++;
                pushParseOp2(PARSEOP_GROUPING, fCurrentParseOp);
                break;
            case XPath.Tokens.EXPRTOKEN_LITERAL:
                handle = fTokens.getToken(++fCurrentToken);
                fCurrentToken++;
                pushParseOp2(PARSEOP_LITERAL, handle);
                break;
            case XPath.Tokens.EXPRTOKEN_NUMBER:
                int whole = fTokens.getToken(++fCurrentToken);
                int part = fTokens.getToken(++fCurrentToken);
                fCurrentToken++;
                pushParseOp3(PARSEOP_NUMBER, whole, part);
                break;
            case XPath.Tokens.EXPRTOKEN_FUNCTION_NAME:
                saveToken = fCurrentToken;
                saveParseOp = fCurrentParseOp;
                prefix = fTokens.getToken(++fCurrentToken);
                handle = fTokens.getToken(++fCurrentToken); // localpart
                fCurrentToken++;
                pushParseOp3(PARSEOP_FUNCTION_NAME, prefix, handle);
                if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_OPEN_PAREN) {
                    fCurrentToken = saveToken;
                    fCurrentParseOp = saveParseOp;
                    return false;
                }
                fCurrentToken++;
                int funcName = fCurrentParseOp;
                int nextArg = -1;
                if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_CLOSE_PAREN) {
                    fCurrentToken++;
                } else {
                    while (true) {
                        if (!parseExpr()) {
                            fCurrentToken = saveToken;
                            fCurrentParseOp = saveParseOp;
                            return false;
                        }
                        if (nextArg != -1) {
                            pushParseOp3(PARSEOP_FUNCTION_ARGUMENTS, nextArg, fCurrentParseOp);
                        }
                        nextArg = fCurrentParseOp;
                        if (fTokens.getToken(fCurrentToken) == XPath.Tokens.EXPRTOKEN_CLOSE_PAREN) {
                            fCurrentToken++;
                            break;
                        }
                        if (fTokens.getToken(fCurrentToken) != XPath.Tokens.EXPRTOKEN_COMMA) {
                            fCurrentToken = saveToken;
                            fCurrentParseOp = saveParseOp;
                            return false;
                        }
                        fCurrentToken++;
                    }
                }
                pushParseOp3(PARSEOP_FUNCTION, funcName, nextArg);
                break;
            default:
                return false;
            }
            return true;
        }

        //
        // MAIN
        //

        public static void main(String argv[]) {
            for (int i = 0; i < argv.length; i++) {
                String expression = argv[i];
                System.out.println("# XPath expression: "+expression);
                XPathExprParser parser = new XPathExprParser();
                try {
                    parser.parseExpr(expression);
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }

    } // class XPathExprParser
    /***/

    //
    // MAIN
    //

    /** Main program entry. */
    public static void main(String[] argv) throws Exception {

        for (int i = 0; i < argv.length; i++) {
            final String expression = argv[i];
            System.out.println("# XPath expression: \""+expression+'"');
            try {
                SymbolTable symbolTable = new SymbolTable();
                XPath xpath = new XPath(expression, symbolTable, null);
                System.out.println("expanded xpath: \""+xpath.toString()+'"');
            }
            catch (XPathException e) {
                System.out.println("error: "+e.getMessage());
            }
        }

    } // main(String[])

} // class XPath