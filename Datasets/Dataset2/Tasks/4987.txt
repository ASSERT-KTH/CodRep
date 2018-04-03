@version $Id: ModifyComponent.java,v 1.7 2001/05/30 01:04:59 jon dead $

package org.tigris.scarab.screens.admin;

/* ================================================================
 * Copyright (c) 2000 Collab.Net.  All rights reserved.
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

// Velocity Stuff 
import org.apache.velocity.*; 
import org.apache.velocity.context.*; 
// Turbine Stuff 
import org.apache.turbine.om.*;
import org.apache.turbine.om.security.*;
import org.apache.turbine.modules.*; 
import org.apache.turbine.modules.screens.*;
import org.apache.turbine.services.velocity.*; 
import org.apache.turbine.util.*; 
// Scarab Stuff
import org.tigris.scarab.om.*;
import org.tigris.scarab.services.module.ModuleEntity;
import org.tigris.scarab.services.module.ModuleManager;
import org.tigris.scarab.screens.base.*;

/**
    This class is responsible for building the Context up
    for the admin,ModifyProject Screen.

    @author <a href="mailto:jon@collab.net">Jon S. Stevens</a>
    @version $Id: ModifyComponent.java,v 1.6 2001/05/21 23:09:12 jon Exp $
*/
public class ModifyComponent extends RequireLoginFirst
{
    /**
        builds up the context for display of variables on the page.
    */
    public void doBuildTemplate( RunData data, Context context ) throws Exception 
    {
        // put the projects list into the context.
        // context.put (ModuleManager.PROJECT_CHANGE_BOX, ModuleManager.getProjectsBox(data, 1));
        // get the project id of the currently selected project.
        ObjectKey project_id = ((ScarabUser)data.getUser())
            .getCurrentModule().getPrimaryKey();
        
        // the list of components
        // context.put ("componentList", ModuleManager.getComponents(project_id));
        // the add section
        // context.put ("compadd", createFromFormData(data));
        // context.put ("compadd_Owner", data.getParameters().getString("compadd_Owner", ""));
        // context.put ("compadd_QaContact", data.getParameters().getString("compadd_QaContact", ""));

        /*
        // get the currently select project information
        ScarabModule sm = ModuleManager.getProject(project_id);
        context.put ("project", sm );
        
        // get the owner username and id
        context.put ("owner", ScarabUser.getUserName(sm.getOwnerId()));
        context.put ("ownerId", new Integer(sm.getOwnerId()).toString());
        // get the qucontact username and id
        context.put ("qaContact", ScarabUser.getUserName(sm.getQaContactId()));
        context.put ("qaContactId", new Integer(sm.getQaContactId()).toString());
        
        // deal with the form data from the new form stuff below
        // only do this if the submit button was clicked
        if (data.getAction().equalsIgnoreCase("admin.AddProject"))
        {
            context.put ("newproject", ModuleManager.getModule(data, false));
            context.put ("newprojectowner", data.getParameters().getString("project_owner", ""));
            context.put ("newprojectqaContact", data.getParameters().getString("project_qacontact", ""));            
        }
        else
        {
            context.put ("newproject", ModuleManager.getEmptyModule());
            context.put ("newprojectowner", "");
            context.put ("newprojectqaContact", "");            
        }
        */
   }
    
    /**
        utility method to create a new component from form data
    */
    private static final ModuleEntity createFromFormData (RunData data)
        throws Exception
    {
        ModuleEntity component = ModuleManager.getInstance();
        component.setName (data.getParameters().getString("compaddname", ""));
        component.setDescription (data.getParameters().getString("compadddescription", ""));
        component.setUrl (data.getParameters().getString("compaddurl", ""));
        return component;
    }
}
/*
        // * deal with components
        
*/