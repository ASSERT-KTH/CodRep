System.out.println("ids are " + ids);

package org.tigris.scarab.da;

/* ================================================================
 * Copyright (c) 2000 CollabNet.  All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * 
 * 3. The end-user documentation included with the redistribution, if
 * any, must include the following acknowlegement: "This product includes
 * software developed by CollabNet (http://www.collab.net/)."
 * Alternately, this acknowlegement may appear in the software itself, if
 * and wherever such third-party acknowlegements normally appear.
 * 
 * 4. The hosted project names must not be used to endorse or promote
 * products derived from this software without prior written
 * permission. For written permission, please contact info@collab.net.
 * 
 * 5. Products derived from this software may not use the "Tigris" name
 * nor may "Tigris" appear in their names without prior written
 * permission of CollabNet.
 * 
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL COLLAB.NET OR ITS CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
 * IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * ====================================================================
 * 
 * This software consists of voluntary contributions made by many
 * individuals on behalf of CollabNet.
 */

import java.util.Collection;
import java.util.List;
import java.util.Set;

import org.apache.turbine.Turbine;
import org.tigris.scarab.test.BaseTestCase;

/**
 * Tests the AttributeAccess implementation.
 *
 * @author <a href="mailto:jmcnally@collab.net">John McNally</a>
 */
public class AttributeAccessTest
    extends BaseTestCase
{    
    public void setUp() throws Exception{
        super.setUp();
        Turbine.getConfiguration().setProperty("dataaccess.AttributeAccess.classname","org.tigris.scarab.da.AttributeAccess");
        assertNotNull(Turbine.getConfiguration().getString("dataaccess.AttributeAccess.classname"));
    }
 

 
    public void testRetrieveQueryColumnIDs()
    {
        AttributeAccess aa = DAFactory.getAttributeAccess();
        String userID = "1";
        String listID = "1";
        String moduleID = "5";
        String artifactTypeID = "1";
        List ids = aa.retrieveQueryColumnIDs(userID, listID,
                                             moduleID, artifactTypeID);
       // assertTrue(ids.size()>0);
        // TODO: finish
    }

    /*
     * Make sure delete doesn't break another testcase that needs the data!
     * Better would be to create a new set of data!
     */
    public void OFFtestDeleteQueryColumnIDs()
    {
        AttributeAccess aa = DAFactory.getAttributeAccess();
        String userID = "1";
        String listID = "1";
        String moduleID = "5";
        String artifactTypeID = "1";
        aa.deleteQueryColumnIDs(userID, listID, moduleID, artifactTypeID);
        // TODO: finish
    }

    public void testRetrieveRequiredAttributeIDs()
    {
        AttributeAccess aa = DAFactory.getAttributeAccess();
        String moduleID = "5";
        String[] artifactTypeID = {"1", "3", "5", "7", "9"};
        Set ids;
        for (int i = 0; i < artifactTypeID.length; i++) 
        {
            ids = aa.retrieveRequiredAttributeIDs(moduleID, artifactTypeID[i]);
            assertEquals(getExpectedRequiredSize(artifactTypeID[i]), 
                         ids.size());
        }
    }

    private int getExpectedRequiredSize(String artifactTypeID)

    {
        int expectedSize = 0;
        switch (Integer.parseInt(artifactTypeID))
        {
            case 1: expectedSize = 4;break;
            case 3: expectedSize = 4;break;
            case 5: expectedSize = 2;break;
            case 7: expectedSize = 2;break;
            case 9: expectedSize = 2;break;
        }
        return expectedSize;
    }

    public void testRetrieveQuickSearchAttributeIDs()
    {
        AttributeAccess aa = DAFactory.getAttributeAccess();
        String moduleID = "5";
        String artifactTypeID = "1";
        Set ids = aa.retrieveQuickSearchAttributeIDs(moduleID, artifactTypeID);
        assertEquals (1, ids.size());
    }

    public void testRetrieveActiveAttributeOMs()
    {
        AttributeAccess aa = DAFactory.getAttributeAccess();
        String moduleID = "5";
        boolean isOrdered = false;
        String[] artifactTypeID = {"1", "3", "5", "7", "9"};
        Collection oms;
        for (int i = 0; i < artifactTypeID.length; i++) 
        {
            oms = aa.retrieveActiveAttributeOMs(moduleID, artifactTypeID[i], 
                                             isOrdered);
            assertEquals(getExpectedActiveSize(artifactTypeID[i]), oms.size());
        }
    }

    private int getExpectedActiveSize(String artifactTypeID)

    {
        int expectedSize = 0;
        switch (Integer.parseInt(artifactTypeID))
        {
            // these values include 2 user attributes
            case 1: expectedSize = 12;break;
            case 3: expectedSize = 11;break;
            case 5: expectedSize = 9;break;
            case 7: expectedSize = 9;break;
            case 9: expectedSize = 9;break;
        }
        return expectedSize;
    }

    public void testRetrieveDefaultTextAttributeID()
    {
        AttributeAccess aa = DAFactory.getAttributeAccess();
        String moduleID = "5";
        String artifactTypeID = "1";
        String id = aa.retrieveDefaultTextAttributeID(moduleID, 
                                                      artifactTypeID);
        assertEquals("11", id);
    }

    public void testRetrieveFirstActiveTextAttributeID()
    {
        AttributeAccess aa = DAFactory.getAttributeAccess();
        String moduleID = "5";
        String artifactTypeID = "1";
        String id = aa.retrieveFirstActiveTextAttributeID(moduleID, 
                                                          artifactTypeID);
        assertEquals("11", id);
    }
}