@version $Id: Issue.java,v 1.4 2001/02/23 03:11:37 jmcnally dead $

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
import org.tigris.scarab.util.*;
import org.apache.turbine.util.*;
import org.apache.turbine.util.db.*;
// import org.tigris.scarab.om.project.peer.*;

import org.tigris.scarab.om.BaseScarabObject;
import org.tigris.scarab.attribute.Attribute;
import org.tigris.scarab.baseom.*;
import org.tigris.scarab.baseom.peer.*;

/**
    This is an object representation of the Issue table.

    @author <a href="mailto:jon@collab.net">Jon S. Stevens</a>
    @version $Id: Issue.java,v 1.3 2001/01/23 22:43:23 jmcnally Exp $
*/
public class Issue extends BaseScarabObject
{
    /** primary table class */
    ScarabIssue scarabIssue;

    /** The attributes that pertain to this module. */
    Vector collScarabAttributes;

    /**
     * Creates a new <code>Issue</code> instance.
     *
     */
    public Issue()
    {
        scarabIssue = new ScarabIssue();
    }

    /**
     * Creates a new <code>Issue</code> instance backed by a 
     * <code>ScarabIssue</code>.
     *
     * @param sm  a <code>ScarabIssue</code> value
     */
    public Issue(ScarabIssue sm)
    {
        scarabIssue = sm;
    }

    /**
     * Creates a new <code>Issue</code> instance backed by a 
     * <code>ScarabIssue</code> with id.
     *
     * @param id an <code>Object</code> value
     */
    public Issue(Object id) throws Exception
    {
        scarabIssue = ScarabIssuePeer.retrieveById(id);
    }

    
    /**
     * Get the value of scarabIssue.
     * @return value of scarabIssue.
     */
    public ScarabIssue getScarabIssue() 
    {
        return scarabIssue;
    }
    
    public Object getId()
    {
        return scarabIssue.getPrimaryKey();
    }

    public void setId(Object id) throws Exception
    {
        scarabIssue.setPrimaryKey(id);
    }
/*
    /**
     * Get the value of issueId.
     * @return value of issueId.
     * /
    public String getIssueId() 
    {
        return scarabIssue.getIssueId();
    }
    
    /**
     * Set the value of issueId.
     * @param v  Value to assign to issueId.
     * /
    public void setIssueId(String  v) 
    {
        scarabIssue.setIssueId(v);
    }
*/    

    public void addAttribute(Attribute attribute) throws Exception
    {
        ScarabIssueAttributeValue sAtt = 
            attribute.getScarabIssueAttributeValue();
        scarabIssue.addScarabIssueAttributeValues(sAtt);
    }

    /**
     * Should contain AttValues for the Issue as well as empty AttValues
     * that are relevant for the module, but have not been set for
     * the issue.
     */
    public HashMap getAllAttributes() throws Exception
    {
        return null;
    }


    public HashMap getAttributes() throws Exception
    {
        Criteria crit = new Criteria(2)
            .add(ScarabIssueAttributeValuePeer.DELETED, false);        
        Vector siaValues = scarabIssue.getScarabIssueAttributeValues(crit);

        HashMap map = new HashMap( (int)(1.25*siaValues.size() + 1) );
        for ( int i=0; i<siaValues.size(); i++ ) 
        {
            Attribute att = Attribute.getInstance(
               (ScarabIssueAttributeValue) siaValues.get(i) );
            String name = att.getName();
            map.put(name.toUpperCase(), att);
        }

        return map;
    }

    public HashMap getModuleAttributes() throws Exception
    {
        Criteria crit = new Criteria(2)
            .add(ScarabRModuleAttributePeer.DELETED, false);        
        Vector moduleAttributes = 
            scarabIssue.getScarabModule().getScarabRModuleAttributes(crit);
        HashMap siaValuesMap = getAttributes();

        HashMap map = new HashMap( (int)(1.25*moduleAttributes.size() + 1) );
try{
        for ( int i=0; i<moduleAttributes.size(); i++ ) 
        {
            Attribute att = Attribute.getInstance(
               (ScarabRModuleAttribute) moduleAttributes.get(i), 
               this.getScarabIssue());
            String key = att.getName().toUpperCase();

            if ( siaValuesMap.containsKey(key) ) 
            {
                map.put( key, siaValuesMap.get(key) );
            }
            else 
            {
                ScarabIssueAttributeValue siav = 
                    new ScarabIssueAttributeValue();
                siav.setScarabAttribute(att.getScarabAttribute());
                siav.setScarabIssue(this.getScarabIssue());
                att.setScarabIssueAttributeValue(siav);
                map.put( key, att ); 
            }             
        }
}catch(Exception e){e.printStackTrace();}
        return map;
    }

    /*
    /**
        get the owner_id of the project
    * /
    public int getOwnerId()
    {
        return scarabIssue.getOwnerId();
    }
    /**
        set the owner_id of the project
    * /
    public void setOwnerId(int id)
    {
        scarabIssue.setOwner(id);
    }
    /**
        get the qa_contact_id of the project
    * /
    public int getQaContactId()
    {
        return scarabIssue.getQaContactId();
    }
    /**
        set the qa_contact_id of the project
    * /
    public void setQaContactId(int id)
    {
        scarabIssue.setQaContactId(id);
    }
    */



    public void save() throws Exception
    {
        scarabIssue.save();        
    }

    public String getQueryKey()
    {
        StringBuffer qs = new StringBuffer("Issue[");
        qs.append(scarabIssue.getPrimaryKey().toString());
        return qs.append("]").toString();
    }

    /**
        calls the doPopulate() method with validation false
    */
    public Issue doPopulate(RunData data)
        throws Exception
    {
        return doPopulate(data, false);
    }

    /**
        populates project based on the existing project data from POST
    */
    public Issue doPopulate(RunData data, boolean validate)
        throws Exception
    {
        String prefix = getQueryKey().toLowerCase();

        if ( scarabIssue.isNew() ) 
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

        if (validate)
        {
        }

        return this;
    }
}




