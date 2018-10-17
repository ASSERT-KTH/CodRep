attribute = Attribute.getInstance();

package org.tigris.scarab.tools;

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

// Turbine
import org.apache.turbine.om.security.User;
import org.apache.turbine.om.*;
import org.apache.turbine.util.RunData;
import org.apache.turbine.services.intake.IntakeTool;
import org.apache.turbine.services.velocity.TurbineVelocity;
import org.apache.turbine.util.pool.Recyclable;


// Scarab
import org.tigris.scarab.om.*;
import org.tigris.scarab.util.*;
import org.tigris.scarab.util.word.IssueSearch;

/**
 * This class is used by the Scarab API
 */
public class ScarabRequestTool implements ScarabRequestScope,
                                          Recyclable
{
    /** the object containing request specific data */
    private RunData data;

    /**
     * A User object for use within the Scarab API.
     */
    private ScarabUser user = null;

    /**
     * A Issue object for use within the Scarab API.
     */
    private Issue issue = null;

    /**
     * A Attribute object for use within the Scarab API.
     */
    private Attribute attribute = null;

    /**
     * A Module object for use within the Scarab API.
     */
    private Module module = null;

    /**
     * A AttributeOption object for use within the Scarab API.
     */
    private AttributeOption attributeOption = null;
    
    public void init(Object data)
    {
        this.data = (RunData)data;
    }

    /**
     * nulls out the issue and user objects
     */
    public void refresh()
    {
        this.user = null;
        this.issue = null;
    }

    /**
     * Constructor does initialization stuff
     */    
    public ScarabRequestTool()
    {
        //intake = new IntakeSystem();
    }

    /**
     * A Attribute object for use within the Scarab API.
     */
    public void setAttribute (Attribute attribute)
    {
        this.attribute = attribute;
    }

    private IntakeTool getIntakeTool()
    {
        return (IntakeTool)TurbineVelocity.getContext(data)
            .get(ScarabConstants.INTAKE_TOOL);
    }


    /**
     * A Attribute object for use within the Scarab API.
     */
    public void setAttributeOption (AttributeOption option)
    {
        this.attributeOption = option;
    }

    /**
     * A Attribute object for use within the Scarab API.
     */
    public AttributeOption getAttributeOption()
        throws Exception
    {
try{
        if (attributeOption == null)
        {
            String optId = data.getParameters()
                .getString("currentAttributeOption"); 
            if ( optId == null )
            {
                attributeOption = new AttributeOption();                
            }
            else 
            {
                attributeOption = AttributeOptionPeer
                    .retrieveByPK(new NumberKey(optId));
            }
        }
}catch(Exception e){e.printStackTrace();}
        return attributeOption;
    }

    /**
     * A User object for use within the Scarab API.
     */
    public void setUser (ScarabUser user)
    {
        this.user = user;
    }

    /**
     * A User object for use within the Scarab API.
     */
    public ScarabUser getUser()
    {
        if (user == null)
            this.user = (ScarabUser)data.getUser();
        return this.user;
    }

    /**
     * A Attribute object for use within the Scarab API.
     */
    public Attribute getAttribute()
     throws Exception
    {
try{
        if (attribute == null)
        {
            String attId = getIntakeTool()
                .get("Attribute", IntakeTool.DEFAULT_KEY).get("Id").toString();
            if ( attId == null || attId.length() == 0 )
            {
                attribute = Attribute.getNewInstance();
            }
            else 
            {
                attribute = Attribute.getInstance(new NumberKey(attId));
            }
        }        
}catch(Exception e){e.printStackTrace();}
        return attribute;
 
   }
    /**
     * A Module object for use within the Scarab API.
     */
    public void setModule(Module module)
    {
        this.module = module;
    }

    /**
     * Get an Module object. 
     *
     * @return a <code>Module</code> value
     */
    public Module getModule()
     throws Exception
    {
      try{
            String modId = getIntakeTool()
                .get("Module", IntakeTool.DEFAULT_KEY).get("Id").toString();
            if ( modId == null || modId.length() == 0 )
            {
                module = new Module();
            }
            else 
            {
                module = Module.getInstance(new NumberKey(modId));
            }
      }catch(Exception e){e.printStackTrace();}
        return module;
 
   }
    /**
     * Get an RModuleAttribute object. 
     *
     * @return a <code>Module</code> value
     */
    public RModuleAttribute getRModuleAttribute()
        throws Exception
    {
        RModuleAttribute rma = null;
      try{
            ComboKey rModAttId = (ComboKey)getIntakeTool()
                .get("RModuleAttribute", IntakeTool.DEFAULT_KEY)
                .get("Id").getValue();
            if ( rModAttId == null )
            {
                NumberKey attId = (NumberKey)getIntakeTool()
                    .get("Attribute", IntakeTool.DEFAULT_KEY)
                    .get("Id").getValue();
                if ( attId != null && getUser().getCurrentModule() != null )
                {
                    NumberKey[] nka = {attId, 
                        getUser().getCurrentModule().getModuleId()};
                    rma = RModuleAttributePeer.retrieveByPK(new ComboKey(nka));
                }
                else 
                {
                    rma = new RModuleAttribute();
                }
            }
            else 
            {
                rma = RModuleAttributePeer.retrieveByPK(rModAttId);
            }
      }catch(Exception e){e.printStackTrace();}
        return rma;
 
   }

    

    /**
     * Get a specific module by key value.
     *
     * @param key a <code>String</code> value
     * @return a <code>Module</code> value
     */
    public Module getModule(String key) throws Exception
    {
        return ModulePeer.retrieveByPK(new NumberKey(key));
    }


    /**
     * A Issue object for use within the Scarab API.
     */
    public void setIssue(Issue issue)
    {
        this.issue = issue;
    }

    /**
     * Get an Issue object. If it is the first time calling,
     * it will be a new blank issue object.
     *
     * @return a <code>Issue</code> value
     */
    public Issue getIssue()
    {
        if (issue == null)
            this.issue = new Issue();
        return this.issue;
    }

    /**
     * Get a new SearchIssue object. 
     *
     * @return a <code>Issue</code> value
     */
    public Issue getSearch()
        throws Exception
    {
        IssueSearch search = new IssueSearch();
        search.setModule(((ScarabUser)getUser()).getCurrentModule());
        return search;
    }

    /**
     * The id may be a primary key or an issue id.
     *
     * @param key a <code>String</code> value
     * @return a <code>Issue</code> value
     */
    public Issue getIssue(String key)
        throws Exception
    {
        Issue issue = null;
        try
        {
            issue = IssuePeer.retrieveByPK(new NumberKey(key));
        }
        catch (RuntimeException re)
        {
            // was not a primary key, try fid
            Issue.FederatedId fid = new Issue.FederatedId(key);
            if ( fid.getInstance() == null ) 
            {
                // handle null (always null right now)
            }
            issue = Issue.getIssueById(fid);
        }

        return issue;
    }



    // ****************** Recyclable implementation ************************

    private boolean disposed;

    /**
     * Recycles the object for a new client. Recycle methods with
     * parameters must be added to implementing object and they will be
     * automatically called by pool implementations when the object is
     * taken from the pool for a new client. The parameters must
     * correspond to the parameters of the constructors of the object.
     * For new objects, constructors can call their corresponding recycle
     * methods whenever applicable.
     * The recycle methods must call their super.
     */
    public void recycle()
    {
        disposed = false;
    }

    /**
     * Disposes the object after use. The method is called
     * when the object is returned to its pool.
     * The dispose method must call its super.
     */
    public void dispose()
    {
        data = null;
        user = null;
        issue = null;
        attribute = null;

        disposed = true;
    }

    /**
     * Checks whether the recyclable has been disposed.
     * @return true, if the recyclable is disposed.
     */
    public boolean isDisposed()
    {
        return disposed;
    }


}


