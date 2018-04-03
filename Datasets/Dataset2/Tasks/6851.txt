@version $Id: ModuleManager.java,v 1.10 2001/05/14 21:43:55 jon dead $

package org.tigris.scarab.om;

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

// JDK
import java.math.*;
import java.util.*;

// Scarab

// Turbine
import org.apache.turbine.om.security.*;
import org.apache.turbine.om.*;
import org.apache.turbine.util.*;
import org.apache.turbine.util.db.*;
import org.apache.turbine.util.template.*;
import org.apache.turbine.services.security.*;

/**
    This class contains code for dealing with Modules.

    @author <a href="mailto:jon@collab.net">Jon S. Stevens</a>
    @version $Id: ModuleManager.java,v 1.9 2001/05/01 00:03:37 jmcnally Exp $
*/
public class ModuleManager
{
    public static final String USER_SELECTED_MODULE = "scarab.user.selected.module";
    public static final String CURRENT_PROJECT = "cur_project_id";
    public static final String PROJECT_CHANGE_BOX = "project_change_box";
    
    public ModuleManager()
    {
    }

    /* *
        This is a utility method to quickly get the list of modules associated
        to a user.
    * /
    public static Vector getProjects(ObjectKey visitorid)
        throws Exception
    {
        Criteria crit = new Criteria();
        crit.addJoin (ModulePeer.MODULE_ID, RModuleUserPeer.MODULE_ID);
        crit.add (RModuleUserPeer.USER_ID, visitorid);
        return ModulePeer.doSelect(crit);
    }
    */

    /**
        gets a single project
        @return null on error
    */
    public static Module getProject(ObjectKey project_id) throws Exception
    {
        Module project = null;
        try
        {
            Criteria criteria = new Criteria();
            criteria.add(ModulePeer.MODULE_ID, project_id);
            // get the Project object
            Vector projectVec = ModulePeer.doSelect(criteria);
            if (projectVec.size() == 1)
                project = (Module)projectVec.elementAt(0);
        }
        catch (Exception e)
        {
        }
        return project;    
    }
    
    /* *
        This method will pull all of the projects associated to a user
        out of the database and then format them into a SelectorBox which
        you can just stick into the context.
        <p>
        It will attempt to get the visitorid from data.getUser(). If the visitorid
        does not exist, it will return null.
        <p>
        It will attempt to get the USER_SELECTED_MODULE from data.getUser().getTemp()
        in order to auto mark the "selected" option.
    * /
    public static SelectorBox getProjectsBox(RunData data, int size)
        throws Exception
    {
        ObjectKey visitorid = ((org.apache.turbine.om.security.TurbineUser)
                         data.getUser()).getPrimaryKey();
        if (visitorid == null)
            return null;
        
        String selectedModule = data.getParameters()
            .getString(CURRENT_PROJECT, "1");

        // get a list of the projects associated to the user.
        Vector result = getProjects(visitorid);
        Object[] names = new Object[result.size()];
        Object[] values = new Object[result.size()];
        boolean[] selected = new boolean[result.size()];
        int i = 0;
        // build up the Object[]'s
        for (Enumeration e = result.elements();e.hasMoreElements(); )
        {
            Module sm = (Module) e.nextElement();
            names[i] = sm.getPrimaryKey();
            values[i] = sm.getName();

            if (selectedModule != null
                && sm.getPrimaryKey().equals(selectedModule) )
            {
                selected[i++] = true;
            }
            else 
            {
                selected[i++] = false;       
            }
        }
        // store the first project as the "default" project
        if ( selectedModule == null && names.length > 0 )
            data.getParameters().add(CURRENT_PROJECT, (String)names[0]);
        return new SelectorBox(PROJECT_CHANGE_BOX, names, values, size, selected);
    }
    */
    /**
        give me a list of components that match the parent project id
    */
    public static Vector getComponents(ObjectKey parent_project_id)
        throws Exception
    {
        Criteria crit = new Criteria();
        crit.add (ModulePeer.PARENT_ID, parent_project_id);
        return ModulePeer.doSelect(crit);
    }
    /**
        create a new ScarabModule based on form input.
        
        it will optionally try to validate the data. if there is an error, it will
        throw an exception.
    */
    public static Module getModule(RunData data, boolean validate)
        throws Exception
    {
        String project_id = data.getParameters().getString("project_id", null);
        String name = data.getParameters().getString("project_name",null);
        String desc = data.getParameters().getString("project_description",null);

        Module sm = new Module();
        sm.setPrimaryKey(project_id);
        sm.setName( StringUtils.makeString( name ));
        sm.setDescription( StringUtils.makeString( desc ));
        sm.setUrl( StringUtils.makeString(data.getParameters().getString("project_url") ));
        if (validate)
        {
            if (project_id == null)
                throw new Exception ( "Missing project_id!" );
            if (! StringUtils.isValid(name))
                throw new Exception ( "Missing project name!" );
            if (! StringUtils.isValid(desc))
                throw new Exception ( "Missing project description!" );

            User project_owner = TurbineSecurity.getUser(
                data.getParameters().getString("project_owner", ""));
            User project_qacontact = TurbineSecurity.getUser(
                data.getParameters().getString("project_qacontact", ""));
            
            if (project_owner == null)
                throw new Exception ("Could not find a registered user for the project owner!");
            if (project_qacontact == null )
                throw new Exception ("Could not find a registered user for the project qa contact!");

            sm.setOwnerId((NumberKey)((ScarabUser)project_owner).getPrimaryKey() );
            sm.setQaContactId((NumberKey)((ScarabUser)
                                project_qacontact).getPrimaryKey() );
        }
        return sm;
    }
    /**
        returns an empty module
    */
    public static Module getEmptyModule()
    {
        Module sm = new Module();
        sm.setName("");
        sm.setDescription("");
        sm.setUrl("");
        return sm;
    }
    
    /**
        check for a duplicate project name
    */
    public static void checkForDuplicateProject(Module module)
        throws Exception
    {
        Criteria crit = new Criteria();
        crit.add (ModulePeer.MODULE_NAME, module.getName());
        crit.setSingleRecord(true);
        Vector result = ModulePeer.doSelect(crit);
        if (result.size() > 0)
            throw new Exception ("Project: " + module.getName() + 
            " already exists. Please choose another name!" );        
    }
    
    /* *
        create a new project. it will throw an exception with the
        error message in it which you can catch.
    * /
    public static void createNewProject(RunData data)
        throws Exception
    {
        // get a populated ScarabModule and do validation
        Module module = getModule(data, true);
        
        // check to see if we have a duplicate name!
        checkForDuplicateProject(module);
        
        // create the new module
        ModulePeer.doInsert(module);

        // you are related to a new project
        Criteria crit = new Criteria(4)
            .add (RModuleUserPeer.MODULE_ID, module.getPrimaryKey())
            .add (RModuleUserPeer.USER_ID, 
                  ((org.apache.turbine.om.security.TurbineUser)
                   data.getUser()).getPrimaryKey());
        RModuleUserPeer.doInsert(crit);
    }
    */

}