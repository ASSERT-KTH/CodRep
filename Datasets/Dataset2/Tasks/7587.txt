@version $Id: MoveIssue.java,v 1.9 2001/09/04 22:02:08 elicia dead $

package org.tigris.scarab.actions;

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

import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

// Turbine Stuff 
import org.apache.turbine.TemplateAction;
import org.apache.turbine.RunData;
import org.apache.turbine.TemplateContext;
import org.apache.turbine.modules.ContextAdapter;

import org.apache.torque.om.NumberKey; 
import org.apache.torque.util.Criteria;

// Scarab Stuff
import org.tigris.scarab.services.module.ModuleEntity;
import org.tigris.scarab.om.Issue;
import org.tigris.scarab.om.IssuePeer;
import org.tigris.scarab.om.Attachment;
import org.tigris.scarab.om.AttachmentPeer;
import org.tigris.scarab.om.RModuleAttribute;
import org.tigris.scarab.om.RModuleAttributePeer;
import org.tigris.scarab.om.RModuleOption;
import org.tigris.scarab.om.RModuleOptionPeer;
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.AttributePeer;
import org.tigris.scarab.om.AttributeValue;
import org.tigris.scarab.om.Transaction;
import org.tigris.scarab.om.Activity;
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.om.ScarabModule;
import org.tigris.scarab.om.ScarabModulePeer;
import org.tigris.scarab.attribute.OptionAttribute;


/**
    This class is responsible for moving/copying an issue from one module to another.
    ScarabIssueAttributeValue
    @author <a href="mailto:elicia@collab.net">Elicia David</a>
    @version $Id: MoveIssue.java,v 1.8 2001/08/31 01:48:55 jmcnally Exp $
*/
public class MoveIssue extends TemplateAction
{

    public void doMapattributes( RunData data, TemplateContext context )
        throws Exception
    {
        String issueId = data.getParameters().getString("id");
        String moduleId = data.getParameters().getString("module_id");
        String selectAction = data.getParameters().getString("select_action");
        Issue issue = (Issue)IssuePeer.retrieveByPK(new NumberKey(issueId));
        
        List matchingAttributes = getList(issue, moduleId, "matching");
        List orphanAttributes = getList(issue, moduleId, "orphan");
        
        data.getParameters().add("issue_id", issueId); 
        data.getParameters().add("new_module_id", moduleId); 
        context.put("orphanAttributes", orphanAttributes);
        context.put("matchingAttributes", matchingAttributes);
        context.put("select_action", selectAction);
        setTarget(data, "secure,MoveIssue2.vm");            
    }


    public void doSaveissue( RunData data, TemplateContext context )
        throws Exception
    {
        String issueId = data.getParameters().getString("id");
        String newModuleId = data.getParameters().getString("module_id");
        String selectAction = data.getParameters().getString("select_action");

        Issue issue = (Issue)IssuePeer.retrieveByPK(new NumberKey(issueId));
        ModuleEntity oldModule = issue.getScarabModule();
        ScarabUser user = (ScarabUser)data.getUser();

        NumberKey newIssueId;
        Issue newIssue;
        StringBuffer descBuf = null;
        ModuleEntity newModule;
        Attachment attachment = new Attachment();

        List matchingAttributes = getList(issue, newModuleId, "matching");
        List orphanAttributes = getList(issue, newModuleId, "orphan");

        // Save transaction record
        Transaction transaction = new Transaction();
        transaction.create(user, null);

        // Move issue to other module
        if (selectAction.equals("move"))
        {
            newIssue = issue;
            newIssue.setModuleId(new NumberKey(newModuleId)); 
            newIssue.setModifiedBy(user.getUserId());
            newIssue.save();
            newModule = newIssue.getScarabModule();
 
            // Delete non-matching attributes.
            for (int i=0;i<orphanAttributes.size();i++)
            {
               AttributeValue attVal = (AttributeValue) orphanAttributes.get(i);
               attVal.setDeleted(true);
               attVal.save();
            }
            descBuf = new StringBuffer(" moved from ");
            descBuf.append(oldModule.getName()).append(" to ");
            descBuf.append(newModule.getName());
        } 

        // Copy issue to other module
        else
        {
            newIssue = new Issue();
            newIssue.setCreatedBy(user.getUserId());
            newIssue.setModifiedBy(user.getUserId());
            newIssue.setModuleId(new NumberKey(newModuleId));
            newIssue.save();
            newModule = newIssue.getScarabModule();

            // Copy over attributes
            for (int i=0;i<matchingAttributes.size();i++)
            {
               AttributeValue attVal = (AttributeValue) matchingAttributes
                                                        .get(i);
               AttributeValue newAttVal = attVal.copy();
               newAttVal.setIssueId(newIssue.getIssueId());
               newAttVal.startTransaction(transaction);
               newAttVal.save();
            }
            descBuf = new StringBuffer(" copied from issue ");
            descBuf.append(issue.getUniqueId());
            descBuf.append(" in module ").append(oldModule.getName());
        }


        if (!orphanAttributes.isEmpty())
        {
            // Save comment
            StringBuffer dataBuf = new StringBuffer("removed " + 
                                                    "irrelevant attribute(s): ");
            for (int i=0;i<orphanAttributes.size();i++)
            {
               AttributeValue attVal = (AttributeValue) orphanAttributes.get(i);
               dataBuf.append(attVal.getAttribute().getName());
               dataBuf.append("=").append(attVal.getAttributeOption().getName());
               if (i < orphanAttributes.size()-1 )
               {
                  dataBuf.append(",");
               } 
            }
            attachment.setDataAsString(dataBuf.toString());
            context.put("deletedAttributes", dataBuf.toString());
        }
        else
        {
            attachment.setDataAsString("all attributes were copied.");
        }
            
        attachment.setName("Moved Issue Note");
        attachment.setTextFields(user, newIssue, Attachment.MODIFICATION__PK);
        attachment.save();

        // Update transaction
        transaction.setAttachment(attachment);
        transaction.save();

        // Save activity record
        String desc = descBuf.toString();
        Activity activity = new Activity();
        Attribute zeroAttribute = (Attribute) AttributePeer
                                  .retrieveByPK(new NumberKey("0"));
        activity.create(newIssue, zeroAttribute, desc, transaction, 
                        null, null, oldModule.getName(), newModule.getName());

        context.put("action", selectAction);
        context.put("oldModule", oldModule.getName());
        context.put("newModule", newModule.getName());
        transaction.sendEmail(new ContextAdapter(context), newIssue, 
                              "issue " +  newIssue.getIssueId() + desc,
                              "email/MoveIssue.vm");

        data.getParameters().add("id", newIssue.getIssueId().toString()); 
        setTarget(data, "ViewIssue.vm");            

    }

    private List getList( Issue issue, String moduleId, String listToReturn )
          throws Exception
    {
        AttributeValue aval = null;
        String value = null;
        List matchingAttributes = new ArrayList();
        List orphanAttributes = new ArrayList();
        List returnList = null;
        ScarabModule module = (ScarabModule)ScarabModulePeer
                              .retrieveByPK(new NumberKey(moduleId));

        HashMap setMap = issue.getAttributeValuesMap();
        Iterator iter = setMap.keySet().iterator();
        while ( iter.hasNext() ) 
        {
            aval = (AttributeValue)setMap.get(iter.next());
            RModuleAttribute modAttr = module.
                                       getRModuleAttribute(aval.getAttribute());
            
            // If this attribute is not active for the destination module,
            // Add to orphanAttributes list
            if (!modAttr.getActive()) 
            {
                 orphanAttributes.add(aval);
            } 
            else
            {
                // If attribute is an option attribute,
                // Check if attribute option is active for destination module.
                if ( aval instanceof OptionAttribute ) 
                {
                    Criteria crit2 = new Criteria(1)
                        .add(RModuleOptionPeer.ACTIVE, true);
                    RModuleOption modOpt = (RModuleOption)RModuleOptionPeer
                                            .doSelect(crit2).get(0);
                    if (modOpt.getActive())
                    {
                        matchingAttributes.add(aval);
                    } 
                    else
                    {
                        orphanAttributes.add(aval);
                    }
                }
                else
                {
                    matchingAttributes.add(aval);
                }
            }
        }

        //Return requested list
        if ( listToReturn.equals("matching") )
        {
            returnList = matchingAttributes;
        }
        else
        {
            returnList = orphanAttributes;
        }
        return returnList;
    }
        
} 