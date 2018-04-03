import org.apache.cactus.*;

/*
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 1999-2001 The Apache Software Foundation.  All rights
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
 * 3. The end-user documentation included with the redistribution, if
 *    any, must include the following acknowlegement:
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowlegement may appear in the software itself,
 *    if and wherever such third-party acknowlegements normally appear.
 *
 * 4. The names "The Jakarta Project", "Struts", and "Apache Software
 *    Foundation" must not be used to endorse or promote products derived
 *    from this software without prior written permission. For written
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache"
 *    nor may "Apache" appear in their names without prior written
 *    permission of the Apache Group.
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
 * individuals on behalf of the Apache Software Foundation.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 *
 */
package org.apache.struts.taglib.logic;

import javax.servlet.*;

import junit.framework.*;
import org.apache.commons.cactus.*;

/**
 * Suite of unit tests for the
 * <code>org.apache.struts.taglib.logic.EqualTag</code> class.
 *
 * @author David Winterfeldt
 */
public class TestEqualTag extends JspTestCase {
    /**
     * Defines the testcase name for JUnit.
     *
     * @param theName the testcase's name.
     */
    public TestEqualTag(String theName) {
        super(theName);
    }

    /**
     * Start the tests.
     *
     * @param theArgs the arguments. Not used
     */
    public static void main(String[] theArgs) {
        junit.awtui.TestRunner.main(new String[] {TestEqualTag.class.getName()});
    }

    /**
     * @return a test suite (<code>TestSuite</code>) that includes all methods
     *         starting with "test"
     */
    public static Test suite() {
        // All methods starting with "test" will be executed in the test suite.
        return new TestSuite(TestEqualTag.class);
    }

    //----- Test initApplication() method --------------------------------------

    /**
     * Verify that two <code>String</code>s match using the <code>EqualTag</code>.
     */
    public void testStringEquals() throws ServletException,  javax.servlet.jsp.JspException {
        EqualTag et = new EqualTag();
        String testStringKey = "testString";
        String testStringValue = "abc";
        
        request.setAttribute(testStringKey, testStringValue);
        et.setPageContext(pageContext);
	et.setName(testStringKey);
	et.setValue(testStringValue);
	
        assertEquals("String equals comparison", true, et.condition(0, 0));
    }

    /**
     * Verify that two <code>String</code>s do not match using the <code>EqualTag</code>.
     */
    public void testStringNotEquals() throws ServletException,  javax.servlet.jsp.JspException {
        EqualTag et = new EqualTag();
        String testStringKey = "testString";
        String testStringValue = "abc";
        String testStringValue1 = "abcd";
        
        request.setAttribute(testStringKey, testStringValue);
        et.setPageContext(pageContext);
	et.setName(testStringKey);
	et.setValue(testStringValue1);
	
        assertEquals("String not equals comparison", false, et.condition(0, 0));
    }

    /**
     * Verify that an <code>Integer</code> and a <code>String</code>
     * match using the <code>EqualTag</code>.
     */
    public void testIntegerEquals() throws ServletException,  javax.servlet.jsp.JspException {
        EqualTag et = new EqualTag();
        String testIntegerKey = "testInteger";
        Integer testIntegerValue = new Integer(21);
        
        request.setAttribute(testIntegerKey, testIntegerValue);
        et.setPageContext(pageContext);
	et.setName(testIntegerKey);
	et.setValue(testIntegerValue.toString());
	
        assertEquals("Integer equals comparison", true, et.condition(0, 0));
    }

    /**
     * Verify that two <code>String</code>s do not match using the <code>EqualTag</code>.
     */
    public void testIntegerNotEquals() throws ServletException,  javax.servlet.jsp.JspException {
        EqualTag et = new EqualTag();
        String testIntegerKey = "testInteger";
        Integer testIntegerValue = new Integer(21);
        Integer testIntegerValue1 = new Integer(testIntegerValue.intValue() + 1);
        
        request.setAttribute(testIntegerKey, testIntegerValue);
        et.setPageContext(pageContext);
	et.setName(testIntegerKey);
	et.setValue(testIntegerValue1.toString());
	
        assertEquals("Integer equals comparison", false, et.condition(0, 0));
    }

}