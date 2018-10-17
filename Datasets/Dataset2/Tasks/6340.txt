@version $Id: Module.java,v 1.4 2001/02/23 03:11:37 jmcnally dead $

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
import java.util.*;

// Turbine
import org.apache.turbine.util.*;
import org.apache.turbine.util.db.*;

import org.tigris.scarab.om.BaseScarabObject;
import org.tigris.scarab.baseom.*;
import org.tigris.scarab.baseom.peer.*;
import org.tigris.scarab.util.*;

/**
    This object wraps a ScarabModule and adds functionality.

    @author <a href="mailto:jmcnally@collab.net">John D. McNally</a>
    @author <a href="mailto:jon@collab.net">Jon S. Stevens</a>
    @version $Id: Module.java,v 1.3 2001/01/23 22:43:23 jmcnally Exp $
*/
public class Module extends BaseScarabObject
{
    /** primary table class */
    ScarabModule scarabModule;

    /** The attributes that pertain to this module. */
    Vector collScarabAttributes;

    /**
     * Creates a new <code>Module</code> instance.
     *
     */
    public Module()
    {
        scarabModule = new ScarabModule();
    }

    /**
     * Creates a new <code>Module</code> instance backed by a 
     * <code>ScarabModule</code>.
     *
     * @param sm  a <code>ScarabModule</code> value
     */
    public Module(ScarabModule sm)
    {
        scarabModule = sm;
    }

    /**
     * Creates a new <code>Module</code> instance backed by a 
     * <code>ScarabModule</code> with id.
     *
     * @param id an <code>Object</code> value
     */
    public Module(Object id) throws Exception
    {
        scarabModule = ScarabModulePeer.retrieveById(id);
    }

    
    /**
     * Get the value of scarabModule.
     * @return value of scarabModule.
     */
    public ScarabModule getScarabModule() 
    {
        return scarabModule;
    }
    
    public Object getId()
    {
        return scarabModule.getPrimaryKey();
    }

    public void setId(Object id) throws Exception
    {
        scarabModule.setPrimaryKey(id);
    }

    /**
        get the name of the project
    */
    public String getName()
    {
        return scarabModule.getName();
    }
    /**
        set the name of the project
    */
    public void setName(String name)
    {
        scarabModule.setName(name);
    }
    /**
        get the Description of the project
    */
    public String getDescription()
    {
        return scarabModule.getDescription();
    }
    /**
        set the Description of the project
    */
    public void setDescription(String desc)
    {
        scarabModule.setDescription(desc);
    }
    /**
        get the url of the project
    */
    public String getUrl()
    {
        return scarabModule.getUrl();
    }
    /**
        set the url of the project
    */
    public void setUrl(String url)
    {
        scarabModule.setUrl(url);
    }
    /**
        get the parent_id of the project
    */
    public int getParentId()
    {
        return scarabModule.getParentId();
    }
    /**
        set the parent_id of the project
    */
    public void setParentId(int id) throws Exception
    {
        scarabModule.setParentId(id);
    }
    /**
        get the owner_id of the project
    */
    public int getOwnerId()
    {
        return scarabModule.getOwnerId();
    }
    /**
        set the owner_id of the project
    */
    public void setOwnerId(int id)
    {
        scarabModule.setOwnerId(id);
    }
    /**
        get the qa_contact_id of the project
    */
    public int getQaContactId()
    {
        return scarabModule.getQaContactId();
    }
    /**
        set the qa_contact_id of the project
    */
    public void setQaContactId(int id)
    {
        scarabModule.setQaContactId(id);
    }




    public void save() throws Exception
    {
        // if new, relate the Module to the user who created it.
        if ( scarabModule.isNew() ) 
        {
            ScarabRModuleUser relation = new ScarabRModuleUser();
            if ( getOwnerId() == NEW_ID ) 
            {
                throw new ScarabException("Can't save a project without" + 
                    "first assigning an owner.");
            }         
            relation.setUserId(getOwnerId());
            relation.setDeleted(false);
            scarabModule.addScarabRModuleUsers(relation);
            
        }

        scarabModule.save();        
    }

    public String getQueryKey()
    {
        StringBuffer qs = new StringBuffer("Module[");
        qs.append(scarabModule.getPrimaryKey().toString());
        return qs.append("]").toString();
    }

    /**
        calls the doPopulate() method with validation false
    */
    public Module doPopulate(RunData data)
        throws Exception
    {
        return doPopulate(data, false);
    }

    /**
        populates project based on the existing project data from POST
    */
    public Module doPopulate(RunData data, boolean validate)
        throws Exception
    {
        String prefix = getQueryKey().toLowerCase();

        if ( scarabModule.isNew() ) 
        {
            int project_id = data.getParameters().getInt(prefix + "id", -1); 
            if (validate)
            {
                if (project_id == -1)
                    throw new Exception ( "Missing project_id!" );
            }
            setId(new Integer(project_id));
            setCreatedBy( ((ScarabUser)data.getUser()).getPrimaryKeyAsInt() );
            setCreatedDate( new Date() );
        }

        String name = data.getParameters().getString(prefix + "name",null);
        String desc = data.getParameters()
            .getString(prefix + "description",null);
        
        if (validate)
        {
            if (! StringUtils.isValid(name))
                throw new Exception ( "Missing project name!" );
            if (! StringUtils.isValid(desc))
                throw new Exception ( "Missing project description!" );
        }

        setName( StringUtils.makeString( name ));
        setDescription( StringUtils.makeString( desc ));
        setUrl( StringUtils.makeString(
            data.getParameters().getString(prefix + "url") ));
        setOwnerId( data.getParameters().getInt(prefix + "ownerid") );
        setQaContactId( data.getParameters()
                        .getInt(prefix + "qacontactid") );
        return this;
    }
}