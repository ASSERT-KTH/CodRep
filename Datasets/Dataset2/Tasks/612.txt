@version $Id: DeleteComponent.java,v 1.9 2001/10/24 22:54:56 jon dead $

package org.tigris.scarab.actions.admin;

/* ================================================================
 * Copyright (c) 2000-2001 CollabNet.  All rights reserved.
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
 * software developed by Collab.Net <http://www.Collab.Net/>."
 * Alternately, this acknowlegement may appear in the software itself, if
 * and wherever such third-party acknowlegements normally appear.
 * 
 * 4. The hosted project names must not be used to endorse or promote
 * products derived from this software without prior written
 * permission. For written permission, please contact info@collab.net.
 * 
 * 5. Products derived from this software may not use the "Tigris" or 
 * "Scarab" names nor may "Tigris" or "Scarab" appear in their names without 
 * prior written permission of Collab.Net.
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
 * individuals on behalf of Collab.Net.
 */ 

// Turbine Stuff
import org.apache.turbine.TemplateContext;
import org.apache.turbine.RunData;
import org.apache.torque.util.Criteria;

// Scarab Stuff
import org.tigris.scarab.om.ScarabModulePeer;
import org.tigris.scarab.actions.base.RequireLoginFirstAction;

/**
    This class will attempt to delete a component. Right now, it is
    hard coded to only work on the ModifyProject.vm template. Need
    to figure out how to make it better re-usable. Not a major issue
    right now though. :-(
        
    @author <a href="mailto:jon@collab.net">Jon S. Stevens</a>
    @version $Id: DeleteComponent.java,v 1.8 2001/08/02 07:11:37 jon Exp $
*/
public class DeleteComponent extends RequireLoginFirstAction
{
    /**
        This manages clicking the Delete button
    */
    public void doDelete( RunData data, TemplateContext context ) throws Exception
    {
        try
        {
            // get the id
            int component_id = data.getParameters().getInt("component_id", -1);
            // validate the data
            if (component_id == -1)
            {
                data.setMessage("Invalid component id");
                return;
            }
            // build the criteria
            Criteria crit = new Criteria();
            crit.add(ScarabModulePeer.MODULE_ID, component_id);
            // do the delete
            ScarabModulePeer.doDelete(crit);
            data.setMessage("Component Deletion Successful!");
        }
        catch (Exception e)
        {
            // display the error message
            data.setMessage(e.getMessage());
        }
    }
    /**
        The form on the admin,ModifyProject page has a doModify
        button. Don't do anything if it is clicked. We only want
        the doDelete button.
    */
    public void doModify( RunData data, TemplateContext context ) throws Exception
    {
    }
    /**
        does nothing.
    */
    public void doPerform( RunData data, TemplateContext context ) throws Exception
    {
    }
}