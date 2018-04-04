@version $Id: Approval.java,v 1.12 2002/02/08 18:18:20 jmcnally Exp $

package org.tigris.scarab.actions.admin;

/* ================================================================
 * Copyright (c) 2000-2002 CollabNet.  All rights reserved.
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
import org.apache.fulcrum.template.DefaultTemplateContext;
import org.apache.torque.om.NumberKey; 
import org.apache.turbine.TemplateAction;
import org.apache.turbine.TemplateContext;
import org.apache.turbine.modules.ContextAdapter;
import org.apache.turbine.RunData;
import org.apache.turbine.Turbine;
import org.apache.turbine.ParameterParser;

// Scarab Stuff
import org.tigris.scarab.om.Query;
import org.tigris.scarab.om.QueryPeer;
import org.tigris.scarab.om.Transaction;
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.om.ScarabUserImplPeer;
import org.tigris.scarab.om.ScarabUserImplPeer;
import org.tigris.scarab.services.module.ModuleEntity;
import org.tigris.scarab.om.Issue;
import org.tigris.scarab.om.IssuePeer;
import org.tigris.scarab.om.IssueTemplateInfo;
import org.tigris.scarab.om.IssueTemplateInfoPeer;
import org.tigris.scarab.tools.Email;
import org.tigris.scarab.attribute.OptionAttribute;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;
import org.tigris.scarab.tools.ScarabRequestTool;

/**
    This class is responsible for edit issue forms.
    ScarabIssueAttributeValue
    @author <a href="mailto:elicia@collab.net">Elicia David</a>
    @version $Id: Approval.java,v 1.11 2002/02/08 00:12:31 jmcnally Exp $
*/
public class Approval extends TemplateAction
{

    public void doSubmit( RunData data, TemplateContext context )
        throws Exception
    {
        ScarabRequestTool scarabR = (ScarabRequestTool)context
            .get(ScarabConstants.SCARAB_REQUEST_TOOL);
        ScarabUser user = (ScarabUser)data.getUser();
        ModuleEntity module = scarabR.getCurrentModule();
        String globalComment = data.getParameters().getString("global_comment");
       
        ParameterParser params = data.getParameters();
        Object[] keys = params.getKeys();
        String key;
        String action = null;
        String actionWord = null;
        String artifact = null;
        String artifactName = null;
        String comment = null;
        ScarabUser toUser = null;
        String userId;

        for (int i =0; i<keys.length; i++)
        {
            action="none";
            key = keys[i].toString();
            if (key.startsWith("query_id_"))
            {
               String queryId = key.substring(9);
               Query query = (Query) QueryPeer
                                     .retrieveByPK(new NumberKey(queryId));

               action = params.getString("query_action_" + queryId);
               comment = params.getString("query_comment_" + queryId);

               userId = params.getString("query_user_" + queryId);
               toUser = (ScarabUser) ScarabUserImplPeer
                                     .retrieveByPK(new NumberKey(userId));
               artifact = "query";
               artifactName = query.getName();

               if (action.equals("reject"))
               {
                   try
                   {
                       query.approve(user, false);
                   }
                   catch (ScarabException e)
                   {
                       data.setMessage(e.getMessage());
                   }
                   actionWord = "rejected";
               } 
               else if (action.equals("approve"))
               {
                   try
                   {
                       query.approve(user, true);
                   }
                   catch(ScarabException e)
                   {
                       data.setMessage(e.getMessage());
                   }
                   actionWord = "approved";
               }

            }
            else if (key.startsWith("template_id_"))
            {
               String templateId = key.substring(12);
               IssueTemplateInfo info = (IssueTemplateInfo) IssueTemplateInfoPeer
                                     .retrieveByPK(new NumberKey(templateId));

               action = params.getString("template_action_" + templateId);
               comment = params.getString("template_comment_" + templateId);

               userId = params.getString("template_user_" + templateId);
               toUser = (ScarabUser) ScarabUserImplPeer
                                     .retrieveByPK(new NumberKey(userId));
               artifact = "issue entry template";
               artifactName = info.getName();

               if (action.equals("reject"))
               {
                   try
                   {
                       info.approve(user, false);
                   }
                   catch(ScarabException e)
                   {
                       data.setMessage(e.getMessage());
                   }
                   actionWord = "rejected";
               } 
               else if (action.equals("Approve"))
               {
                   try
                   {
                       info.approve(user, true);
                   }
                   catch(ScarabException e)
                   {
                       data.setMessage(e.getMessage());
                   }
                   actionWord = "approved";
               }
            }

            if (!action.equals("none"))
            {
                // send email
                StringBuffer bodyBuf = new StringBuffer("The user ");
                bodyBuf.append(user.getUserName());
                bodyBuf.append(" has just ").append(actionWord);
                bodyBuf.append(" your ").append(artifact).append(" '");
                bodyBuf.append(artifactName).append("'.");

                // add data to context for email template
                context.put("body", bodyBuf.toString());
                context.put("comment", comment);
                context.put("globalComment", globalComment);

                String subject = "Scarab " + artifact + " " + actionWord;
                String template = Turbine.getConfiguration().
                    getString("scarab.email.approval.template",
                              "email/Approval.vm");
                Email.sendEmail(new ContextAdapter(context), module, null, 
				toUser, subject, template);
            }
        }

        String template = data.getParameters()
            .getString(ScarabConstants.NEXT_TEMPLATE);
        setTarget(data, template);            
    }
}