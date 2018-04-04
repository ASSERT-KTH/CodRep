config.setInitParameter("application", "org.apache.struts.webapp.example.ApplicationResources");

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
package org.apache.struts.action;

import javax.servlet.ServletException;
import junit.framework.Test;
import junit.framework.TestSuite;

import org.apache.cactus.ServletTestCase;
import org.apache.struts.util.MessageResources;

/**
 * Suite of unit tests for the
 * <code>org.apache.struts.action.ActionServlet</code> class.
 */
public class TestActionServlet extends ServletTestCase
{
    /**
     * Defines the testcase name for JUnit.
     *
     * @param theName the testcase's name.
     */
    public TestActionServlet(String theName)
    {
        super(theName);
    }

    /**
     * Start the tests.
     *
     * @param theArgs the arguments. Not used
     */
    public static void main(String[] theArgs)
    {
        junit.awtui.TestRunner.main(new String[] {TestActionServlet.class.getName()});
    }

    /**
     * @return a test suite (<code>TestSuite</code>) that includes all methods
     *         starting with "test"
     */
    public static Test suite()
    {
        // All methods starting with "test" will be executed in the test suite.
        return new TestSuite(TestActionServlet.class);
    }


    // ----------------------------- initInternal() and destroyInternal() tests


    /**
     * Verify that we can initialize and destroy our internal message
     * resources object.
     */
    public void testInitDestroyInternal() {

        ActionServlet servlet = new ActionServlet();
        try {
            servlet.initInternal();
        } catch (ServletException e) {
            fail("initInternal() threw exception: " + e);
        }
        assertTrue("internal was initialized",
                   servlet.getInternal() != null);
        assertTrue("internal of correct type",
                   servlet.getInternal() instanceof MessageResources);
        servlet.destroyInternal();
        assertTrue("internal was destroyed",
                   servlet.getInternal() == null);

    }



    //----- Test initApplication() method --------------------------------------

    /**
     * Verify that nothing happens if no "application" property is defined in
     * the servlet configuration.
     */
    /*
    public void testInitApplicationNull() throws ServletException
    {
        ActionServlet servlet = new ActionServlet();
        servlet.init(config);        

        // Test the initApplication() method
        servlet.initApplication();

        // As no "application" object is found in the servlet config, no
        // attribute should be set in the context
        assertTrue(config.getServletContext().getAttribute(Action.MESSAGES_KEY) == null);
    }
    */

    /**
     * Verify that eveything is fine when only a "application" parameter is
     * defined in the servlet configuration.
     */
    /*
    public void testInitApplicationOk1() throws ServletException
    {
        // initialize config
        config.setInitParameter("application", "org.apache.struts.example.ApplicationResources");

        ActionServlet servlet = new ActionServlet();
        servlet.init(config);        

        // Test the initApplication() method
        servlet.initApplication();

        assertTrue(servlet.application != null);
        assertTrue(servlet.application.getReturnNull() == true);

        assertTrue(config.getServletContext().getAttribute(Action.MESSAGES_KEY) != null);
        assertEquals(servlet.application, config.getServletContext().getAttribute(Action.MESSAGES_KEY));

    }
    */

    // [...]
}