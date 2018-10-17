@version $Id: ConfigureIssueList.java,v 1.5 2001/08/14 22:25:32 elicia dead $

package org.tigris.scarab.actions;

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


// Turbine Stuff 
import org.apache.turbine.TemplateContext;
import org.apache.turbine.RunData;

import org.apache.torque.om.NumberKey;
import org.apache.turbine.tool.IntakeTool;
import org.apache.turbine.services.intake.model.Group;
import org.apache.turbine.services.intake.model.Field;

// Scarab Stuff
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.RModuleUserAttribute;
import org.tigris.scarab.om.RModuleUserAttributePeer;
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.om.ScarabUserImplPeer;
import org.tigris.scarab.om.ScarabModulePeer;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.services.module.ModuleEntity;
import org.tigris.scarab.actions.base.RequireLoginFirstAction;

/**
    This class is responsible for the user configuration of the issue list.
    @author <a href="mailto:elicia@collab.net">Elicia David</a>
    @version $Id: ConfigureIssueList.java,v 1.4 2001/08/09 07:59:52 jon Exp $
*/
public class ConfigureIssueList extends RequireLoginFirstAction
{

    public void doSelectattributes( RunData data, TemplateContext context )
        throws Exception
    {
        IntakeTool intake = (IntakeTool)context
            .get(ScarabConstants.INTAKE_TOOL);
        String userId = data.getParameters().getString("user_id");
        String moduleId = data.getParameters().getString("module_id");
        ModuleEntity module = (ModuleEntity) ScarabModulePeer
                        .retrieveByPK(new NumberKey(moduleId));
        ScarabUser user = (ScarabUser) ScarabUserImplPeer
                          .retrieveByPK(new NumberKey(userId));
        RModuleUserAttribute mua = null;

        Attribute[] activeAttributes  = module.getActiveAttributes();
        for (int i=0; i < activeAttributes.length; i++)
        {
            Attribute attribute = (Attribute)activeAttributes[i];
            NumberKey attributeId =  attribute.getAttributeId();
            String queryKey = moduleId + ":" + userId + ":" 
                              + attribute.getAttributeId().toString();
            Group group = intake.get("RModuleUserAttribute", queryKey, false);

            // If the user selected the attribute, add or update the record.
            if (group.get("Selected").toString().equals("true"))
            {
                mua = user.getModuleUserAttribute
                         (new NumberKey(moduleId), attributeId);
                Field order = group.get("Order");
                order.setProperty(mua);
                mua.save();
            }
            // Otherwise, if user un-selected it, delete record.
            else
            {
                try
                {
                    mua = RModuleUserAttributePeer
                          .retrieveByPK(new NumberKey(moduleId), 
                          new NumberKey(userId), new NumberKey(attributeId));
                    mua.delete();
                }
                catch (Exception e)
                {
                    // ignored
                }
             }
        }

        String template = data.getParameters()
            .getString(ScarabConstants.NEXT_TEMPLATE);
        setTemplate(data, template);            
    }

    /**
        This manages clicking the cancel button
    */
    public void doCancel( RunData data, TemplateContext context ) throws Exception
    {
        data.setMessage("Changes were not saved!");
    }

    /**
        does nothing.
    */
    public void doPerform( RunData data, TemplateContext context ) throws Exception
    {
        doCancel(data, context);
    }
}