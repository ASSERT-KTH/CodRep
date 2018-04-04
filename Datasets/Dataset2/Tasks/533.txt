issue = IssueManager.getIssueById(id);

package org.tigris.scarab.tools;

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

import java.text.DateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Iterator;
import java.util.Locale;
import java.util.Hashtable;
import java.util.HashMap;
import java.util.TimeZone;
import java.util.Arrays;

// Turbine
import org.apache.turbine.RunData;
import org.apache.turbine.Turbine;
import org.apache.turbine.tool.IntakeTool;
import org.apache.torque.om.NumberKey;
import org.apache.torque.om.ObjectKey;
import org.apache.torque.om.ComboKey;
import org.apache.fulcrum.localization.Localization;
import org.apache.fulcrum.intake.Intake;
import org.apache.fulcrum.intake.model.Group;
import org.apache.fulcrum.intake.model.Field;
import org.apache.fulcrum.pool.RecyclableSupport;
import org.apache.fulcrum.util.parser.StringValueParser;
import org.apache.fulcrum.util.parser.ValueParser;
import org.apache.commons.collections.SequencedHashMap;
import org.apache.commons.lang.StringUtils;

// Scarab
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.om.ScarabUserManager;
import org.tigris.scarab.om.Issue;
import org.tigris.scarab.om.IssueManager;
import org.tigris.scarab.om.IssueType;
import org.tigris.scarab.om.IssueTypeManager;
import org.tigris.scarab.om.Query;
import org.tigris.scarab.om.QueryManager;
import org.tigris.scarab.om.QueryPeer;
import org.tigris.scarab.om.IssueTemplateInfo;
import org.tigris.scarab.om.IssueTemplateInfoManager;
import org.tigris.scarab.om.IssueTemplateInfoPeer;
import org.tigris.scarab.om.Depend;
import org.tigris.scarab.om.DependManager;
import org.tigris.scarab.om.ScopePeer;
import org.tigris.scarab.om.FrequencyPeer;
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.AttributePeer;
import org.tigris.scarab.om.AttributeManager;
import org.tigris.scarab.om.AttributeGroup;
import org.tigris.scarab.om.AttributeGroupManager;
import org.tigris.scarab.om.Attachment;
import org.tigris.scarab.om.AttachmentManager;
import org.tigris.scarab.om.AttributeOption;
import org.tigris.scarab.om.ROptionOption;
import org.tigris.scarab.om.AttributeOptionManager;
import org.tigris.scarab.om.RModuleAttribute;
import org.tigris.scarab.om.RModuleAttributeManager;
import org.tigris.scarab.om.RModuleIssueType;
import org.tigris.scarab.om.AttributeValue;
import org.tigris.scarab.om.ParentChildAttributeOption;
import org.tigris.scarab.om.Module;
import org.tigris.scarab.om.ModuleManager;
import org.tigris.scarab.om.MITList;
import org.tigris.scarab.om.MITListManager;
import org.tigris.scarab.reports.ReportBridge;
import org.tigris.scarab.om.ReportManager;
import org.tigris.scarab.om.ActivitySet;
import org.tigris.scarab.om.ActivitySetTypePeer;
import org.tigris.scarab.om.Activity;
import org.tigris.scarab.om.AttachmentTypePeer;
import org.tigris.scarab.tools.SecurityAdminTool;
import org.tigris.scarab.services.cache.ScarabCache;
import org.tigris.scarab.util.Log;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;  
import org.tigris.scarab.util.SnippetRenderer;  
import org.tigris.scarab.util.SimpleSkipFiltering;  
import org.tigris.scarab.util.word.IssueSearch;
import org.tigris.scarab.util.word.SearchIndex;
import org.tigris.scarab.util.word.QueryResult;
import org.tigris.scarab.tools.ScarabLocalizationTool;

/**
 * This class is used by the Scarab API
 */
public class ScarabRequestTool
    extends RecyclableSupport
    implements ScarabRequestScope
{
    private static final String TIME_ZONE =
        Turbine.getConfiguration().getString("scarab.timezone");

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
     * The <code>Alert!</code> message for this request.
     */
    private Object alert = null;

    /**
     * A Attribute object for use within the Scarab API.
     */
    private Attribute attribute = null;

    /**
     * A Attachment object for use within the Scarab API.
     */
    private Attachment attachment = null;

    /**
     * A Depend object for use within the Scarab API.
     */
    private Depend depend = null;

    /**
     * A Query object for use within the Scarab API.
     */
    private Query query = null;

    /**
     * An IssueTemplateInfo object for use within the Scarab API.
     */
    private IssueTemplateInfo templateInfo = null;

    /**
     * An IssueType object for use within the Scarab API.
     */
    private IssueType issueType = null;

    /**
     * An AttributeGroup object
     */
    private AttributeGroup group = null;

    /**
     * The issue that is currently being entered.
     */
    private Issue reportingIssue = null;

    /**
     * A Module object
     */
    private Module module = null;

    /**
     * A AttributeOption object for use within the Scarab API.
     */
    private AttributeOption attributeOption = null;

    /**
     * A ROptionOption
     */
    private ROptionOption roo = null;

    /**
     * A ParentChildAttributeOption
     */
    private ParentChildAttributeOption pcao = null;

    /**
     * IssueSearch object for performing queries
     */
    private IssueSearch issueSearch = null;
    
    /**
     * A list of Issues
     */
    private List issueList;
    
    /**
     * A ReportGenerator
     */
    private ReportBridge reportGenerator = null;
    
    private int nbrPages = 0;
    private int prevPage = 0;
    private int nextPage = 0;

    /* messages usually set in actions */
    private Object confirmMessage;
    private Object infoMessage;
    private Object alertMessage;

    /** The time zone that will be used when formatting dates */
    private final TimeZone timezone;
    
    /**
     * Constructor does initialization stuff
     */    
    public ScarabRequestTool()
    {
        TimeZone tmpTimeZone = null;
        if (TIME_ZONE != null) 
        {
            tmpTimeZone = TimeZone.getTimeZone(TIME_ZONE);
        }        
        timezone = tmpTimeZone;
    }

    /**
     * This method expects to get a RunData object
     */
    public void init(Object data)
    {
        this.data = (RunData)data;
    }

    /**
     * nulls out the issue and user objects
     */
    public void refresh()
    {
        user = null;
        issue = null;
        attribute = null;
        attachment = null;
        depend = null;
        query = null;
        templateInfo = null;
        issueType = null;
        group = null;
        reportingIssue = null;
        module = null;
        attributeOption = null;
        roo = null;
        pcao = null;
        issueSearch = null;
        issueList = null;
        reportGenerator = null;
        nbrPages = 0;
        prevPage = 0;
        nextPage = 0;
        confirmMessage = null;
        infoMessage = null;
        alertMessage = null;
    }

    /**
     * Sets the <code>Alert!</code> message for this request.
     *
     * @param message The alert message to set.
     */
    public void setAlert(Object message)
    {
        this.alert = message;
    }

    /**
     * Retrieves any <code>Alert!</code> message which has been set.
     *
     * @return The alert message.
     */
    public Object getAlert()
    {
        return alert;
    }

    /**
     * A Attachment object for use within the Scarab API
     */
    public void setAttachment(Attachment attachment)
    {
        this.attachment = attachment;
    }

    /**
     * A Attribute object for use within the Scarab API.
     */
    public void setAttribute (Attribute attribute)
    {
        this.attribute = attribute;
    }

    /**
     * A Depend object for use within the Scarab API.
     */
    public void setDepend (Depend depend)
    {
        this.depend = depend;
    }

    /**
     * A Query object for use within the Scarab API.
     */
    public void setQuery (Query query)
    {
        this.query = query;
    }

    /**
     * Get the intake tool.
     */
    private IntakeTool getIntakeTool()
    {
        return (IntakeTool)org.apache.turbine.modules.Module.getTemplateContext(data)
            .get(ScarabConstants.INTAKE_TOOL);
    }

    /**
     * Gets an instance of a ROptionOption from this tool.
     * if it is null it will return a new instance of an 
     * empty ROptionOption and set it within this tool.
     */
    public ROptionOption getROptionOption()
    {
        if (roo == null)
        {
            roo = ROptionOption.getInstance();
        }
        return roo;
    }

    /**
     * Sets an instance of a ROptionOption
     */
    public void setROptionOption(ROptionOption roo)
    {
        this.roo = roo;
    }


    /**
     * A IssueTemplateInfo object for use within the Scarab API.
     */
    public void setIssueTemplateInfo (IssueTemplateInfo templateInfo)
    {
        this.templateInfo = templateInfo;
    }

    /**
     * A IssueType object for use within the Scarab API.
     */
    public void setIssueType (IssueType issuetype)
    {
        this.issueType = issueType;
    }


    /**
     * Gets an instance of a ParentChildAttributeOption from this tool.
     * if it is null it will return a new instance of an 
     * empty ParentChildAttributeOption and set it within this tool.
     */
    public ParentChildAttributeOption getParentChildAttributeOption()
    {
        if (pcao == null)
        {
            pcao = ParentChildAttributeOption.getInstance();
        }
        return pcao;
    }

    /**
     * Sets an instance of a ParentChildAttributeOption
     */
    public void setParentChildAttributeOption(ParentChildAttributeOption roo)
    {
        this.pcao = pcao;
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
            String optId = getIntakeTool()
                .get("AttributeOption", IntakeTool.DEFAULT_KEY)
                .get("OptionId").toString();
            if ( optId == null || optId.length() == 0 )
            {
                attributeOption = AttributeOption.getInstance();
            }
            else 
            {
                attributeOption = AttributeOptionManager
                    .getInstance(new NumberKey(optId));
            }
        }
}catch(Exception e){e.printStackTrace();}
        return attributeOption;
    }

    /**
     * @see org.tigris.scarab.tools.ScarabRequestScope#setUser(ScarabUser)
     */
    public void setUser (ScarabUser user)
    {
        this.user = user;
    }

    /**
     * @see org.tigris.scarab.tools.ScarabRequestScope#getUser()
     */
    public ScarabUser getUser()
    {
        return this.user;
    }

    /**
     * Return a specific User by ID from within the system.
     * You can pass in either a NumberKey or something that
     * will resolve to a String object as id.toString() is 
     * called on everything that isn't a NumberKey.
     */
    public ScarabUser getUser(Object id)
     throws Exception
    {
        if (id == null)
        {
            return null;
        }
        ScarabUser su = null;
        try
        {
            ObjectKey pk = null;
            if (id instanceof NumberKey)
            {
                pk = (ObjectKey) id;
            }
            else
            {
                pk = new NumberKey(id.toString());
            }
            su = ScarabUserManager.getInstance(pk);
        }
        catch (Exception e)
        {
            // Logged at debug level, as a null user is interpreted 
            // as an invalid user id
            Log.get().debug("User with user id "+ id +" could not be found,", e);
        }
        return su;
    }

    /**
     * Return a specific User by username.
     */
    public ScarabUser getUserByUserName(String username)
     throws Exception
    {
        ScarabUser su = null;
        try
        {
            su = ScarabUserManager.getInstance(username, getIssue().getModule().getDomain());
        }
        catch (Exception e)
        {
            // Logged at debug level, as a null user is interpreted 
            // as an invalid username
            Log.get().debug("User, "+username+" could not be found,", e);
        }
        return su;
    }

    /**
     * A Attribute object for use within the Scarab API.
     */
    public Attribute getAttribute()
     throws Exception
    {
        try
        {
            if (attribute == null)
            {
                String attId = getIntakeTool()
                    .get("Attribute", IntakeTool.DEFAULT_KEY)
                    .get("Id").toString();
                if ( attId == null || attId.length() == 0 )
                {
                    attId = data.getParameters().getString("attId");
                    if ( attId == null || attId.length() == 0 )
                    { 
                        attribute = AttributeManager.getInstance();
                    }
                    else 
                    {
                        attribute = AttributeManager.getInstance(new NumberKey(attId));
                    }
                }
                else 
                {
                    attribute = AttributeManager.getInstance(new NumberKey(attId));
                }
            }
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return attribute;
    }

    /**
     * A Attribute object for use within the Scarab API.
     */
    public Attribute getAttribute(NumberKey pk)
     throws Exception
    {
        Attribute attr = null;
        try
        {
           attr = AttributeManager.getInstance(pk);
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        this.attribute = attr;
        return attr;
    }

    /**
     * A Attribute object for use within the Scarab API.
     */
    public AttributeOption getAttributeOption(NumberKey pk)
     throws Exception
    {
        try
        {
           attributeOption = AttributeOptionManager.getInstance(pk);
        }
        catch(Exception e){e.printStackTrace();}
        return attributeOption;
    }

    public AttributeOption getAttributeOption(String key)
         throws Exception
    {
        return getAttributeOption(new NumberKey(key));
    }    

    /**
     * First attempts to get the RModuleUserAttributes from the user.
     * If it is empty, then it will try to get the defaults from the module.
     * If anything fails, it will return an empty list.
     */
    public List getRModuleUserAttributes()
    {
        ScarabUser user = (ScarabUser)data.getUser();
        List result = null;
        try
        {
            Module module = getCurrentModule();
            IssueType issueType = getCurrentIssueType();
            MITList currentList = user.getCurrentMITList();
            if (currentList != null)
            {
                if (currentList.isSingleModuleIssueType()) 
                {
                    module = currentList.getModule();
                    issueType = currentList.getIssueType();
                }
                else 
                {
                    result = currentList.getCommonRModuleUserAttributes();
                }                
            }

            if (result == null)
            {
                result = user.getRModuleUserAttributes(module, issueType);
                if (result.isEmpty())
                {
                    result = module.getDefaultRModuleUserAttributes(issueType);
                }
            }
        }
        catch (Exception e)
        {
            Log.get().error("Could not get list attributes", e);
        }
        if (result == null)
        {
            result = new ArrayList();
        }
        return result;
    }
    

    public List getValidIssueListAttributes()
    {
        ScarabUser user = (ScarabUser)data.getUser();
        List result = null;
        try
        {
            MITList currentList = user.getCurrentMITList();
            if (currentList != null)
            {
                result = currentList.getCommonAttributes();
            }
            else 
            {
                Module module = getCurrentModule();
                IssueType issueType = getCurrentIssueType();
                List rmas = module.getRModuleAttributes(issueType, true);
                if (rmas != null) 
                {
                    result = new ArrayList(rmas.size());
                    Iterator i = rmas.iterator();
                    while (i.hasNext()) 
                    {
                        result.add( ((RModuleAttribute)i.next()).getAttribute() );
                    }
                }
            }
        }
        catch (Exception e)
        {
            Log.get().error("Could not get list attributes", e);
        }
        if (result == null)
        {
            result = new ArrayList();
        }
        return result;
    }

    /**
     * A Query object for use within the Scarab API.
     */
    public Query getQuery()
     throws Exception
    {
        try
        {
            if (query == null)
            {
                String queryId = data.getParameters()
                    .getString("queryId"); 
                if ( queryId == null || queryId.length() == 0 )
                {
                    query = Query.getInstance();
                }
                else 
                {
                    query = QueryManager
                        .getInstance(new NumberKey(queryId), false);
                }
            }        
        }        
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return query;
    }

    /**
     * A IssueTemplateInfo object for use within the Scarab API.
     */
    public IssueTemplateInfo getIssueTemplateInfo()
     throws Exception
    {
        try
        {
            if (templateInfo == null)
            {
                String templateId = data.getParameters()
                    .getString("templateId"); 

                if ( templateId == null || templateId.length() == 0 )
                {
                    templateInfo = IssueTemplateInfo.getInstance();
                }
                else 
                {
                    templateInfo = IssueTemplateInfoManager
                        .getInstance(new NumberKey(templateId), false);
                }
            }        
        }        
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return templateInfo;
    }

    /**
     * An Enter issue template.
     */
    public Issue getIssueTemplate()
     throws Exception
    {
        Issue template = null;
        String templateId = data.getParameters()
            .getString("templateId"); 
        try
        {
            if ( templateId == null || templateId.length() == 0 )
            {
                template = getCurrentModule().getNewIssue(getIssueType(
                                   getCurrentIssueType().getTemplateId().toString()));
            }
            else 
            {
                template = IssueManager
                    .getInstance(new NumberKey(templateId), false);
            }
        }        
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return template;
    }

    /**
     * An Enter issue template.
     */
    public Issue getIssueTemplate(String templateId)
     throws Exception
    {
        Issue template = null;
        try
        {
            if ( templateId == null || templateId.length() == 0 )
            {
                ScarabLocalizationTool l10n = getLocalizationTool();
                setAlertMessage(l10n.get("NoTemplateId"));
            }
            else 
            {
                template = IssueManager
                    .getInstance(new NumberKey(templateId), false);
            }
        }        
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return template;
    }

    /**
     * A Depend object for use within the Scarab API.
     */
    public Depend getDepend()
     throws Exception
    {
        try
        {
            if (depend == null)
            {
                String dependId = getIntakeTool()
                    .get("Depend", IntakeTool.DEFAULT_KEY).get("Id").toString();
                if ( dependId == null || dependId.length() == 0 )
                {
                    depend = DependManager.getInstance();
                }
                else 
                {
                    depend = DependManager
                        .getInstance(new NumberKey(dependId), false);
                }
            }        
        }        
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return depend;
    }

    /**
     * Get reason for modification.
     */
    public String getActivityReason(ActivitySet activitySet, Activity activity)
     throws Exception
    {
        ScarabLocalizationTool l10n = getLocalizationTool();
        String reason = null;
        Attachment attachment = activitySet.getAttachment();
        if (attachment != null)
        {
             String data = attachment.getData();
             // Reason is the attachment entered for this transaction
             if (data != null && data.length() > 0)
             {
                reason = data;
             }
             else
             {
                reason = l10n.get("NotProvided");
             }
         } 
         // No reasons given for initial issue entry
         else if (activitySet.getTypeId().equals(ActivitySetTypePeer.CREATE_ISSUE__PK))
         {
             reason = l10n.get("InitialEntry");
         }
         else
         {
             reason = l10n.get("NotProvided");
         }
         return reason;
    }
            
        
    /**
     * A Attachment object for use within the Scarab API.
     */
    public Attachment getAttachment()
     throws Exception
    {
try{
        if (attachment == null)
        {
            Group att = getIntakeTool()
                .get("Attachment", IntakeTool.DEFAULT_KEY, false);
            if ( att != null ) 
            {            
                String attId =  att.get("Id").toString();
                if ( attId == null || attId.length() == 0 )
                {
                    attachment = new Attachment();
                }
                else 
                {
                    attachment = AttachmentManager
                        .getInstance(new NumberKey(attId), false);
                }
            }
            else 
            {
                attachment = new Attachment();
            }
        }        
}catch(Exception e){e.printStackTrace(); throw e;}
        return attachment;
    }

    /**
     * A AttributeGroup object for use within the Scarab API.
     */
    public AttributeGroup getAttributeGroup()
     throws Exception
    {
           AttributeGroup group = null;
try{
            String attGroupId = getIntakeTool()
                .get("AttributeGroup", IntakeTool.DEFAULT_KEY)
                .get("AttributeGroupId").toString();
            if ( attGroupId == null || attGroupId.length() == 0 )
            {
                group = new AttributeGroup();
            }
            else 
            {
                group = AttributeGroupManager
                    .getInstance(new NumberKey(attGroupId), false);
            }
}catch(Exception e){e.printStackTrace();}
        return group;
 
   }
    /**
     * Get a AttributeGroup object.
     */
    public AttributeGroup getAttributeGroup(String key)
    {
        AttributeGroup group = null;
        try
        {
            group = AttributeGroupManager
                .getInstance(new NumberKey(key), false);
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return group;
    }

    /**
     * Get a specific issue type by key value. Returns null if
     * the Issue Type could not be found
     *
     * @param key a <code>String</code> value
     * @return a <code>IssueType</code> value
     */
    public IssueType getIssueType(String key)
    {
        IssueType issueType = null;
        try
        {
            issueType = IssueTypeManager
                .getInstance(new NumberKey(key), false);
        }
        catch (Exception e)
        {
        }
        return issueType;
    }

    /**
     * Get an issue type object.
     */
    public IssueType getIssueType()
        throws Exception
    {
        if ( issueType == null ) 
        {
            String key = data.getParameters()
                .getString("issuetypeid");
            if ( key == null ) 
            {
                // get new issue type
                issueType = new IssueType();
            }
            else 
            {
                try
                {
                    issueType = IssueTypeManager
                        .getInstance(new NumberKey(key), false);
                }
                catch (Exception e)
                {
                    e.printStackTrace();
                }
            }
        }
        return issueType;
    }


    /**
     * Gets a new instance of AttributeValue
     */
    public AttributeValue getNewAttributeValue(Attribute attribute, Issue issue)
        throws Exception
    {
        
        return AttributeValue.getNewInstance(attribute.getAttributeId(),issue);
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
                Module currentModule = getCurrentModule();
                if ( attId != null && currentModule != null )
                {
                    NumberKey[] nka = {attId, currentModule.getModuleId()};
                    rma = RModuleAttributeManager
                        .getInstance(new ComboKey(nka), false);
                }
                else 
                {
                    rma = new RModuleAttribute();
                }
            }
            else 
            {
                rma = RModuleAttributeManager.getInstance(rModAttId, false);
            }
      }catch(Exception e){e.printStackTrace();}
        return rma;
    }

    /**
     * A AttributeGroup object for use within the Scarab API.
     */
    public void setAttributeGroup(AttributeGroup group)
    {
        this.group = group;
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
            module = ModuleManager.getInstance();
        }
        else 
        {
            module = ModuleManager.getInstance(new NumberKey(modId));
        }
      }catch(Exception e){e.printStackTrace();}
       return module;
    }

    /**
     * Get a specific module by key value. Returns null if
     * the Module could not be found
     *
     * @param key a <code>String</code> value
     * @return a <code>Module</code> value
     */
    public Module getModule(String key)
    {
        Module me = null;
        if ( key != null && key.length() > 0 ) 
        {
            try
            {
                me = ModuleManager.getInstance(new NumberKey(key));
            }
            catch (Exception e)
            {
                Log.get().info("[ScarabRequestTool] Unable to retrieve Module: " +
                         key, e);
            }
        }
        return me;
    }

    /**
     * Gets the Module associated with the information
     * passed around in the query string. Returns null if
     * the Module could not be found.
     */
    public Module getCurrentModule()
    {
        ScarabUser user = (ScarabUser)data.getUser();
        Module currentModule = null;
        if (user != null) 
        {
            currentModule = user.getCurrentModule();            
        }

        return currentModule;
    }

    /**
     * Gets the IssueType associated with the information
     * passed around in the query string.
     */
    public IssueType getCurrentIssueType() throws Exception
    {
        ScarabUser user = (ScarabUser)data.getUser();
        IssueType currentIssueType = null;
        if (user != null) 
        {
             currentIssueType = user.getCurrentIssueType();            
        }
        return currentIssueType;
    }

    public void setCurrentIssueType(IssueType type)
    {
        ScarabUser user = (ScarabUser)data.getUser();
        if (user != null) 
        {
            user.setCurrentIssueType(type);
        }        
    }

    public RModuleIssueType getCurrentRModuleIssueType()
    {
        RModuleIssueType rmit = null;
        try
        {
            rmit = ((ScarabUser)data.getUser()).getCurrentRModuleIssueType();
        }
        catch (Exception e)
        {
            Log.get().debug("getCurrentRModuleIssueType: ", e);
        }
        return rmit;
    }

    /**
     * Looks at the current RModuleIssueType and if it is null,
     * returns the users homepage. If it is not null, and is 
     * dedupe, returns Wizard1...else Wizard3.
     */
    public String getNextEntryTemplate()
    {
        ScarabLocalizationTool l10n = getLocalizationTool();
        RModuleIssueType rmit = null;
        String nextTemplate = null;
        try
        {
            rmit = getCurrentRModuleIssueType();
            if (rmit == null)
            {
                nextTemplate = ((ScarabUser)data.getUser()).getHomePage();
                setAlertMessage(l10n.get("ModuleIssueTypeRequiredToEnterIssue"));
            }
            else if (rmit.getDedupe())
            {
                nextTemplate = "entry,Wizard1.vm";
            }
            else
            {
                nextTemplate = "entry,Wizard3.vm";
            }
        }
        catch (Exception e)
        {
            // system would be messed up, if we are here.  Punt
            nextTemplate = "Index.vm";
            String msg = "CannotDetermineIssueEntryTemplate";
            setAlertMessage(l10n.get(msg));
            Log.get().error(msg, e);
        }
        return nextTemplate;
    }

    /**
     * Returns name of current template
     */
    public String getCurrentTemplate()
    {
        return data.getTarget().replace('/',',');
    }

    /**
     * The issue that is currently being entered.
     *
     * @return an <code>Issue</code> value
     */
    public Issue getReportingIssue()
        throws Exception
    {
        if ( reportingIssue == null ) 
        {
            String key = data.getParameters()
                .getString(ScarabConstants.REPORTING_ISSUE);
            if ( key == null ) 
            {
                getNewReportingIssue();
            }
            else 
            {
                reportingIssue = ((ScarabUser)data.getUser())
                    .getReportingIssue(key);

                // if reportingIssue is still null, the parameter must have
                // been stale, just get a new issue
                if ( reportingIssue == null ) 
                {
                    getNewReportingIssue();                    
                }
            }
        }
        return reportingIssue;
    }

    private void getNewReportingIssue()
        throws Exception
    {
        reportingIssue = getCurrentModule().getNewIssue(getCurrentIssueType());
        String key = ((ScarabUser)data.getUser())
            .setReportingIssue(reportingIssue);
        data.getParameters().add(ScarabConstants.REPORTING_ISSUE, key);
    }

    public void setReportingIssue(Issue issue)
    {
        reportingIssue = issue;
    }

    /**
     * Sets the current Module
     */
    public void setCurrentModule(Module me)
    {
        ScarabUser user = (ScarabUser)data.getUser();
        if (user != null) 
        {
            user.setCurrentModule(me);
        }        
    }

    /**
     * A Issue object for use within the Scarab API.
     */
    public void setIssue(Issue issue)
    {
        this.issue = issue;
    }

    /**
     * Get an Issue object from unique id.
     * If first time calling, returns a new blank issue object.
     *
     * @return a <code>Issue</code> value
     */
    public Issue getIssue()
        throws Exception
    {
        if (issue == null)
        {
            String issueId = null;
            Group issueGroup = getIntakeTool()
                .get("Issue", IntakeTool.DEFAULT_KEY, false);
            if ( issueGroup != null ) 
            {            
                issueId =  issueGroup.get("Id").toString();
            }
            else
            {
                issueId = data.getParameters().getString("id");
            }
            if ( issueId == null || issueId.length() == 0 )
            {
                issue = getCurrentModule()
                    .getNewIssue(getCurrentIssueType());
            }
            else 
            {
                issue = getIssue(issueId);
            }
        }
        return issue;
    }

    /**
     * The id may only be the issue's primary key.
     *
     * @param key a <code>String</code> value
     * @return a <code>Issue</code> value
     */
    public Issue getIssueByPk(String key)
    {
        Issue issue = null;
        try
        {
            issue = IssueManager.getInstance(new NumberKey(key));
        }
        catch (Exception e)
        {
            ScarabLocalizationTool l10n = getLocalizationTool();
            setAlertMessage(l10n.get("InvalidIssueId"));
        }
        return issue;
    }

    /**
     * Takes unique id, and returns issue.
     * if the issue is not valid, then it returns null.
     */
    public Issue getIssue(String id)
    {
        ScarabLocalizationTool l10n = getLocalizationTool();
        Issue issue = null;
        if (id == null || id.length() == 0)
        {
            setInfoMessage(l10n.get("EnterId"));
        }
        else
        {
            try
            {
                char firstChar = id.charAt(0);
                if ('0' <= firstChar && firstChar <= '9') 
                {
                    id = getCurrentModule().getCode() + id;
                }
                issue = Issue.getIssueById(id);

                if (issue.getDeleted())
                {
                    setAlertMessage(l10n.get("InvalidId"));
                    issue = null;
                }
            }        
            catch (Exception e)
            {
                setAlertMessage(l10n.get("InvalidId"));
            }
        }
        return issue;
    }

    /**
     * Get a list of Issue objects.
     *
     * @return a <code>Issue</code> value
     */
    public List getIssues()
        throws Exception
    {
        List issues = null;

        Group issueGroup = getIntakeTool()
            .get("Issue", IntakeTool.DEFAULT_KEY, false);
        if ( issueGroup != null ) 
        {            
            NumberKey[] issueIds =  (NumberKey[])
                issueGroup.get("Ids").getValue();
            if ( issueIds != null )
            {
                issues = getIssues(Arrays.asList(issueIds));
            }
        }
        else 
        {
            String[] issue_ids = data.getParameters().getStrings("issue_ids");
            if (issue_ids != null)
            {
                issues = getIssues(Arrays.asList(issue_ids));
            }
        }
        if (issues == null)
        {
            issues = Collections.EMPTY_LIST;
        }
        return issues;
    }

    /**
     * Get a list of Issue objects from a list of issue ids.  The list
     * can contain Strings or NumberKeys, but all ids must be of the same type
     * (String or NumberKey).
     *
     * @param issueIds a <code>List</code> value
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    public List getIssues(List issueIds)
        throws Exception
    {
        List issues = null;
        StringBuffer invalidIds = null; 
        if (issueIds == null || issueIds.isEmpty()) 
        {
            issues = Collections.EMPTY_LIST;
        }
        else 
        {
            if (issueIds.get(0) instanceof String) 
            {
                issues = new ArrayList(issueIds.size());
                Iterator i = issueIds.iterator();
                while (i.hasNext()) 
                {
                    String id = (String)i.next();
                    Issue issue = getIssue(id);
                    if (issue == null)
                    {
                        if (invalidIds == null) 
                        {
                            invalidIds = new StringBuffer(id);
                        }
                        else 
                        {
                            invalidIds.append(' ').append(id);
                        }                        
                    }
                    else
                    {
                        issues.add(issue);   
                    } 
                }
                if (invalidIds != null) 
                {                
                    setAlertMessage( getLocalizationTool()
                        .format("SomeIssueIdsNotValid", invalidIds.toString()));
                }
            }
            else if (issueIds.get(0) instanceof NumberKey)
            {
                issues = new ArrayList(issueIds.size());
                Iterator i = issueIds.iterator();
                while (i.hasNext()) 
                {
                    Issue issue = IssueManager.getInstance((NumberKey)i.next());
                    if (issue == null) 
                    {
                        setAlertMessage(getLocalizationTool()
                                        .get("SomeIssuePKsNotValid"));
                    }
                    else 
                    {
                        issues.add(issue);   
                    }                    
                }
            }
            else 
            {
                throw new IllegalArgumentException(
                    "issue ids must be Strings or NumberKeys, not " + 
                    issueIds.get(0).getClass().getName());
            }
        }        
        return issues;
    }
        

    /**
     * Get all scopes.
     */
    public List getScopes()
        throws Exception
    {
        return ScopePeer.getAllScopes();
    }

    /**
     * Get all frequencies.
     */
    public List getFrequencies()
        throws Exception
    {
        return FrequencyPeer.getFrequencies();
    }

    /**
     * Generates link to Issue List page, re-running stored query.
     */
    public String getExecuteLink(String link, Query query)
    {
        // query.getValue() begins with a &
        link = link 
            + "/template/IssueList.vm?action=Search&eventSubmit_doSearch=Search" 
            + "&resultsperpage=25&pagenum=1" + query.getValue();

        NumberKey listId = query.getListId();
        if (listId != null) 
        {
            link += '&' + ScarabConstants.CURRENT_MITLIST_ID + '=' + listId;
        }
        else 
        {
            link += '&' + ScarabConstants.REMOVE_CURRENT_MITLIST_QKEY + "=true";
        }
        return link;
     }

    /**
     * Generates link to the Query Detail page.
     */
    public String getEditLink(String link, Query query)
    {
        // query.getValue() begins with a &
        link = link + "/template/EditQuery.vm?queryId=" + query.getQueryId()
                    + query.getValue();

        NumberKey listId = query.getListId();
        if (listId != null) 
        {
            link += '&' + ScarabConstants.CURRENT_MITLIST_ID + '=' + listId;
        }
        else 
        {
            link += '&' + ScarabConstants.REMOVE_CURRENT_MITLIST_QKEY + "=true";
        }
        return link;
    }

    public Intake getConditionalIntake(String parameter)
        throws Exception
    {
        Intake intake = null;
        String param = data.getParameters().getString(parameter);
        if ( param == null ) 
        {            
            intake = getIntakeTool();
        }
        else 
        {
            intake = new Intake();
            StringValueParser parser = new StringValueParser();
            parser.parse(param, '&', '=', true);
            intake.init(parser);
        }

        return intake;
    }

    /**
     * Get a new IssueSearch object. 
     *
     * @return a <code>Issue</code> value
     */
    public IssueSearch getNewSearch()
        throws Exception
    {
        if (issueSearch == null) 
        {
            MITList mitList = ((ScarabUser)data.getUser()).getCurrentMITList();
            if (mitList == null)
            {
                IssueType it = getCurrentIssueType();
                Module cum = getCurrentModule();
                issueSearch = new IssueSearch(cum, it);
            }
            else 
            {
                issueSearch = new IssueSearch(mitList);
            }
        }
        return issueSearch; 
    }

    /**
     * Get an IssueSearch object based on a query string.
     *
     * @return a <code>Issue</code> value
     */
    public IssueSearch getPopulatedSearch(String query)
        throws Exception
    {
        IssueSearch search = getNewSearch();
        ScarabLocalizationTool l10n = getLocalizationTool();
        search.setIssueListAttributeColumns(getRModuleUserAttributes());

        List queryResults = new ArrayList();
        boolean searchSuccess = true;
        Intake intake = null;

        if (query == null)
        {
            setInfoMessage(l10n.get("EnterQuery"));
            searchSuccess = false;
        }
        else
        {
           intake = parseQuery(query);
           searchSuccess = intake.isAllValid();
        }

        if (searchSuccess)
        {
            // If they have entered users to search on, add them to the search
            StringValueParser parser = new StringValueParser();
            parser.parse(query, '&', '=', true);
            String[] userList = parser.getStrings("user_list");
            if ( userList != null && userList.length > 0)
            {
                for (int i =0; i<userList.length; i++)
                {
                    String userId = userList[i];
                    String attrId = parser.getString("user_attr_" + userId);
                    search.addUserCriteria(userId, attrId);
                }
            }

            // Set intake properties
            Group searchGroup = intake.get("SearchIssue", 
                                           search.getQueryKey() );

            Field minDate = searchGroup.get("MinDate");
            if (minDate != null && minDate.toString().length() > 0)
            { 
               searchSuccess =  checkDate(search, minDate.toString());
            }
            Field maxDate = searchGroup.get("MaxDate");
            if (maxDate != null && minDate.toString().length() > 0)
            { 
                searchSuccess = checkDate(search, minDate.toString());
            }
            Field stateChangeFromDate = searchGroup.get("StateChangeFromDate");
            if (stateChangeFromDate != null 
                && stateChangeFromDate.toString().length() > 0)
            { 
                searchSuccess = checkDate(search, stateChangeFromDate.toString());
            }
            Field stateChangeToDate = searchGroup.get("StateChangeToDate");
            if (stateChangeToDate != null 
                && stateChangeToDate.toString().length() > 0)
            { 
                searchSuccess = checkDate(search, stateChangeToDate.toString());
            }
            if (!searchSuccess)
            {
                setAlertMessage(l10n.get("DateFormatPrompt"));
             }
            searchGroup.setProperties(search);

            // Set attribute values to search on
            SequencedHashMap avMap = search.getCommonAttributeValuesMap();
            Iterator i = avMap.iterator();
            while (i.hasNext()) 
            {
                AttributeValue aval = (AttributeValue)avMap.get(i.next());
                Group group = intake.get("AttributeValue", aval.getQueryKey());
                if ( group != null ) 
                {
                    group.setProperties(aval);
                }                
            }
            
            // If user is sorting on an attribute, set sort criteria
            // Do not use intake, since intake parsed from query is not the same
            // As intake passed from the form
            String sortColumn = data.getParameters().getString("sortColumn");
            if (sortColumn != null && sortColumn.length() > 0 
                && StringUtils.isNumeric(sortColumn))
            {
                search.setSortAttributeId(new NumberKey(sortColumn));
            }
            String sortPolarity = data.getParameters().getString("sortPolarity");
            if (sortPolarity != null && sortPolarity.length() > 0)
            {
                search.setSortPolarity(sortPolarity);
            }
        }
        return search;
    }

    /**
     * Get an IssueSearch object based on current query string.
     *
     * @return a <code>Issue</code> value
     */
    public IssueSearch getPopulatedSearch()
        throws Exception
    {
        String currentQueryString = ((ScarabUser)data.getUser()).getMostRecentQuery();
        return getPopulatedSearch(currentQueryString);
    }

    /**
     * Parses query into intake values.
    */
    public Intake parseQuery(String query)
        throws Exception
    {
        Intake intake = new Intake();
        StringValueParser parser = new StringValueParser();
        parser.parse(query, '&', '=', true);
        intake.init(parser);
        return intake;
    }


    /**
     * Performs search on current query (which is stored in user session).
    */
    public List getCurrentSearchResults()
    {
        List matchingIssueIds = null;
        try 
        {
            matchingIssueIds = getUnprotectedCurrentSearchResults();
        }
        catch (Exception e)
        {
            matchingIssueIds = Collections.EMPTY_LIST;
            setAlertMessage(getLocalizationTool()
                .format("ErrorProcessingQuery", e.getMessage()));
            Log.get().info("Error processing a query", e);
        }
        
        return matchingIssueIds;
    }

    /**
     * Caches the result of getUncachedCurrentSearchResults for the remainder
     * of the request.
     */
    private List getUnprotectedCurrentSearchResults()
        throws Exception
    {
        // normally we would use "this" as the first arg to ScarabCache.get,
        // but SRT is not serializable.  Might want to change the interface,
        // but getSearchResults wraps an IssueSearch so we can get around it
        // that way
        IssueSearch search = getNewSearch();
        List results = null;
        Object obj = 
            ScarabCache.get(search, "getUnprotectedCurrentSearchResults"); 
        if ( obj == null ) 
        {       
            results = getUncachedCurrentSearchResults();
            ScarabCache
                .put(results, search, "getUnprotectedCurrentSearchResults");
        }
        else 
        {
            results = (List)obj;
        }
        return results;
    }

    /**
     * Performs search on current query (which is stored in user session).
     */
    private List getUncachedCurrentSearchResults()
        throws Exception
    {
        ScarabLocalizationTool l10n = getLocalizationTool();
        ScarabUser user = (ScarabUser)data.getUser();
        String currentQueryString = user.getMostRecentQuery();
        IssueSearch search = getPopulatedSearch(currentQueryString);
        List queryResults = null;

        // Do search
        try
        {
            queryResults = search.getQueryResults();
            if (queryResults == null || queryResults.size() <= 0)
            {
                setInfoMessage(l10n.get("NoMatchingIssues"));
            }            
        }
        catch (ScarabException e)
        {
            String queryError = e.getMessage();
            if (queryError.startsWith(SearchIndex.PARSE_ERROR)) 
            {
                Log.get().info(queryError);
                setAlertMessage( new SimpleSkipFiltering(
                    l10n.format("QueryParserError", 
                        new SnippetRenderer(data, "TextQueryHelp.vm")) ) );
            }
            else 
            {
                throw e;
            }
        }
        return queryResults;
    }

    public int getCurrentSearchResultsSize()
    {
        int result = 0;
        String[] prevNextList = data.getParameters().getStrings("issueList");
        if (prevNextList == null) 
        {
            result = getCurrentSearchResults().size();
        }
        else 
        {
            result = Integer.parseInt(prevNextList[1]);
        }
        return result;
    }

    /**
     * Returns index of issue's position in current issue list.
    */
    public int getIssuePosInList()
        throws Exception, ScarabException
    {
        int issuePos = -1;
        String[] prevNextList = data.getParameters().getStrings("issueList");
        if (prevNextList != null) 
        {
            String id = getIssue().getUniqueId();
            int listOffset = Math.max(0, Integer.parseInt(prevNextList[0]));
            for (int i=2; i<prevNextList.length; i++)
            {
                if (prevNextList[i].equals(id)) 
                {
                    issuePos = listOffset + i - 1;
                    break;
                }
            }        
        }

        if (issuePos == -1) 
        {
            List srchResults = getCurrentSearchResults();
            Issue issue = getIssue();
            for (int i = 0; i<srchResults.size(); i++)
            {
                if (srchResults.get(i).equals(issue.getUniqueId()))
                {
                    issuePos = i + 1;
                    break;
                }
            }
        }
        return (issuePos == -1) ? 0 : issuePos;
    }

    /**
     * Returns next issue id in list.
    */
    public String getNextIssue()
        throws Exception, ScarabException
    {
        String nextIssueId = null;
        String[] prevNextList = data.getParameters().getStrings("issueList");
        if (prevNextList != null) 
        {
            String id = getIssue().getUniqueId();
            for (int i=2; i<prevNextList.length-1; i++)
            {
                if (prevNextList[i].equals(id)) 
                {
                    nextIssueId = prevNextList[i+1];
                    break;
                }
            }
        }

        if (nextIssueId == null) 
        {
            int issuePos = getIssuePosInList();
            List idList = getCurrentSearchResults();
            if (issuePos < idList.size())
            {
                nextIssueId = ((QueryResult)idList.get(issuePos)).getUniqueId().toString();
            }
            resetIssueIdList(idList, issuePos);
        }
        return nextIssueId;
    }

    /**
     * Returns previous issue id in list.
    */
    public String getPrevIssue()
        throws Exception, ScarabException
    {
        String prevIssueId = null;
        String[] prevNextList = data.getParameters().getStrings("issueList");
        if (prevNextList != null) 
        {
            String id = getIssue().getUniqueId();
            for (int i=3; i<prevNextList.length; i++)
            {
                if (prevNextList[i].equals(id)) 
                {
                    prevIssueId = prevNextList[i-1];
                    break;
                }
            }
        }

        if (prevIssueId == null) 
        {
            int issuePos = getIssuePosInList();
            if (issuePos > 1)
            {
                List idList = getCurrentSearchResults();
                prevIssueId = idList.get(issuePos - 2).toString();
                resetIssueIdList(idList, issuePos);
            }
        }
        return prevIssueId;
    }

    private void resetIssueIdList(List idList, int pos)
    {
        ValueParser pp = data.getParameters();
        pp.remove("issueList");
        Integer min = new Integer(pos-5);
        Iterator prevNextList = getGlobalTool()
            .subset(idList, min, new Integer(pos+10)).iterator();
        pp.add("issueList", min.toString());
        pp.add("issueList", idList.size());        
        while (prevNextList.hasNext()) 
        {
            pp.add("issueList", ((QueryResult)prevNextList.next()).getUniqueId().toString());
        }
    }

    /**
     * Attempts to parse a date passed in the query page.
    */
    private boolean checkDate(IssueSearch search, String date)
        throws Exception
    {
        boolean success = true;
        try
        {
            search.parseDate(date, false);
        }
        catch (Exception e)
        {
            success = false;
        }
        return success;
    }


    /**
     * Convert paths with slashes to commas.
     */
    public String convertPath(String path)
        throws Exception
    {
            return path.replace('/',',');
    }

    /**
     * Returns all issue templates that are global, 
     * Plus those that are personal and created by logged-in user.
    */
    public List getIssueTemplates()
        throws Exception
    {
        String sortColumn = data.getParameters().getString("sortColumn");
        String sortPolarity = data.getParameters().getString("sortPolarity");
        if (sortColumn == null)
        {
            sortColumn = "name";
        }
        if (sortPolarity == null)
        {
            sortPolarity = "asc";
        }
        return IssueTemplateInfoPeer.getAllTemplates(getCurrentModule(),
               getCurrentIssueType(), (ScarabUser)data.getUser(), 
               sortColumn, sortPolarity);
    }

    /**
     * Returns queries that are personal and created by logged-in user.
    */
    public List getPrivateQueries()
        throws Exception
    {
        return QueryPeer.getQueries(getCurrentModule(),
               getCurrentIssueType(), (ScarabUser)data.getUser(), 
               "name", "asc", "private");
    }

    /**
     * Returns all queries that are global.
    */
    public List getGlobalQueries()
        throws Exception
    {
        return QueryPeer.getQueries(getCurrentModule(),
               getCurrentIssueType(), (ScarabUser)data.getUser(), 
               "name", "asc", "global");
    }

    /**
     * Returns all queries that are global, 
     * Plus those that are personal and created by logged-in user.
    */
    public List getQueries()
        throws Exception
    {
        String sortColumn = data.getParameters().getString("sortColumn");
        String sortPolarity = data.getParameters().getString("sortPolarity");
        if (sortColumn == null)
        {
            sortColumn = "avail";
        }
        if (sortPolarity == null)
        {
            sortPolarity = "desc";
        }
        return QueryPeer.getQueries(getCurrentModule(),
               getCurrentIssueType(), (ScarabUser)data.getUser(), 
               sortColumn, sortPolarity, "all");
    }

    /**
     * a report helper class
     */
    public ReportBridge getReport()
        throws Exception
    {
        if ( reportGenerator == null ) 
        {
            String key = data.getParameters()
                .getString(ScarabConstants.CURRENT_REPORT);
            ValueParser parameters = data.getParameters();
            String id = parameters.getString("report_id");
            if ( id == null || id.length() == 0 ) 
            {
                if ( key == null ) 
                {
                    reportGenerator = getNewReport();
                }
                else 
                {
                    reportGenerator = ((ScarabUser)data.getUser())
                        .getCurrentReport(key);
                    
                    // if reportingIssue is still null, the parameter must have
                    // been stale, just get a new issue
                    if ( reportGenerator == null ) 
                    {
                        reportGenerator = getNewReport();                    
                    }
                }                
            }
            else 
            {
                reportGenerator = new ReportBridge(
                    ReportManager.getInstance(new NumberKey(id), false));
                key = ((ScarabUser)data.getUser())
                    .setCurrentReport(reportGenerator);
                data.getParameters()
                    .remove(ScarabConstants.CURRENT_REPORT);
                data.getParameters()
                    .add(ScarabConstants.CURRENT_REPORT, key);
            }
        }

        return reportGenerator;
    }

    private ReportBridge getNewReport()
        throws Exception
    {
        ScarabUser user = (ScarabUser)data.getUser();
        org.tigris.scarab.om.Report om  = new org.tigris.scarab.om.Report();
        ReportBridge report = new ReportBridge(om);
        report.setGeneratedBy(user);

        MITList mitList = user.getCurrentMITList();
        if (mitList == null) 
        {
            report.setModule(getCurrentModule());
            report.setIssueType(getCurrentIssueType());
        }
        else 
        {
            report.setMITList(mitList);
        }
        
        String key = ((ScarabUser)data.getUser()).setCurrentReport(report);
        data.getParameters().add(ScarabConstants.CURRENT_REPORT, key);

        return report;
    }

    public void setReport(ReportBridge report)
    {
        this.reportGenerator = report;
    }
    
    /*
    private static String getReportQueryString(ValueParser params) 
    {
        StringBuffer query = new StringBuffer();
        Object[] keys =  params.getKeys();
        for (int i =0; i<keys.length; i++)
        {
            String key = keys[i].toString();
            if ( key.startsWith("rep") || key.startsWith("intake")
                 || key.startsWith("ofg") )
            {
                String[] values = params.getStrings(key);
                for (int j=0; j<values.length; j++)
                {
                    query.append('&').append(key);
                    query.append('=').append(values[j]);
                }
            }
         }
         return query.toString();
    }
    */


    /**
     * Return all users for module and issue type.
     */
    public List getUsers(Module module, IssueType issueType)
        throws Exception
    {
        List users = new ArrayList();
        ScarabUser[] userArray = module
            .getUsers(module.getUserPermissions(issueType));
        for (int i=0;i<userArray.length;i++)
        {
            users.add(userArray[i]);
        }
        return sortUsers(users);
    }
        
    /**
     * Return all users for current module and issue type.
     */
    public List getUsers() throws Exception
    {
        Module module = getCurrentModule();  
        IssueType issueType = getCurrentIssueType();  
        return getUsers(module, issueType);
    }

    /**
     * Return results of user search.
     */
    public List getUserSearchResults()  throws Exception
    {
        ScarabLocalizationTool l10n = getLocalizationTool();
        String searchString = data.getParameters()
               .getString("searchString"); 
        String searchField = data.getParameters()
               .getString("searchField"); 
        Module module = getCurrentModule();  
        if (searchField == null)
        {
            setInfoMessage(l10n.get("SearchFieldPrompt"));
            return null ;
        }
        
        String firstName = null;
        String lastName = null;
        String email = null;
        if (searchField.equals("First Name"))
        {
            firstName = searchString;
        }
        else if (searchField.equals("Last Name"))
        {
            lastName = searchString;
        }
        else
        {
            email = searchString;
        }

        return sortUsers(module.getUsers(firstName, lastName, null, email, 
                               getCurrentIssueType()));
    }

    /**
     * Return results of attribute search.
     */
    public List getAttributeSearchResults()  throws Exception
    {
        ScarabLocalizationTool l10n = getLocalizationTool();
        String searchString = data.getParameters()
               .getString("searchString"); 
        String searchField = data.getParameters()
               .getString("searchField"); 
        if (searchField == null)
        {
            setInfoMessage(l10n.get("SearchFieldPrompt"));
            return null ;
        }
        
        String name = null;
        String description = null;
        if (searchField.equals("Name") || searchField.equals("Any"))
        {
            name = searchString;
        }
        if (searchField.equals("Description") || searchField.equals("Any"))
        {
            description = searchString;
        }

        return sortAttributes(AttributePeer
            .getFilteredAttributes(name, description, searchField));
    }

    /**
     * Sort users on name or email.
     */
    public List sortUsers(List userList)  throws Exception
    {
        final String sortColumn = data.getParameters().getString("sortColumn");
        final String sortPolarity = data.getParameters().getString("sortPolarity");
        final int polarity = ("desc".equals(sortPolarity)) ? -1 : 1;   
        Comparator c = new Comparator() 
        {
            public int compare(Object o1, Object o2) 
            {
                int i = 0;
                if (sortColumn != null && sortColumn.equals("email"))
                {
                    i =  polarity * ((ScarabUser)o1).getEmail()
                         .compareTo(((ScarabUser)o2).getEmail());
                }
                else
                {
                    i =  polarity * ((ScarabUser)o1).getName()
                         .compareTo(((ScarabUser)o2).getName());
                }
                return i;
             }
        };
        Collections.sort(userList, c);
        return userList;
    }


    /**
     * Sort attributes on name or description.
     */
    public List sortAttributes(List attList)  throws Exception
    {
        final String sortColumn = data.getParameters().getString("sortColumn");
        final String sortPolarity = data.getParameters().getString("sortPolarity");
        final int polarity = ("desc".equals(sortPolarity)) ? -1 : 1;   
        Comparator c = new Comparator() 
        {
            public int compare(Object o1, Object o2) 
            {
                int i = 0;
                if (sortColumn != null && sortColumn.equals("name"))
                {
                    i =  polarity * ((Attribute)o1).getName()
                         .compareTo(((Attribute)o2).getName());
                }
                else
                {
                    i =  polarity * ((Attribute)o1).getDescription()
                         .compareTo(((Attribute)o2).getDescription());
                }
                return i;
             }
        };
        Collections.sort(attList, c);
        return attList;
    }

    /**
     * Return a subset of the passed-in list.
     * 
     * @param nbrItmsPerPage negative value returns full list
     */
    public List getPaginatedList( List fullList, int pgNbr, int nbrItmsPerPage)
    {
        List pageResults = null;
        try 
        {
            if (nbrItmsPerPage < 0) 
            {
                pageResults = fullList;
            }
            else 
            {
                this.nbrPages =  (int)Math.ceil((float)fullList.size() 
                                                / nbrItmsPerPage);
                this.nextPage = pgNbr + 1;
                this.prevPage = pgNbr - 1;
                pageResults = fullList.subList ((pgNbr - 1) * nbrItmsPerPage, 
                    Math.min(pgNbr * nbrItmsPerPage, fullList.size()));
            }
        }
        catch(Exception e)
        {
            Log.get().error("", e);
        }
        return pageResults;
    }

    /**
     * Set the value of issueList.
     * @param v  Value to assign to issueList.
     */
    public void setIssueList(List  v) 
    {
        this.issueList = v;
    }
    
    /**
     * Return the number of paginated pages.
     *
     */
    public int getNbrPages()
    {
        return nbrPages;
    }

    /**
     * Return the next page in the paginated list.
     *
     */
    public int getNextPage()
    {
        if (nextPage <= nbrPages)
        {
            return nextPage;
        }
        else
        {
            return 0;
        }       
    }

    /**
     * Return the previous page in the paginated list.
     *
     */
    public int getPrevPage()
    {
        return prevPage;
    }

    /**
     * This is used to get the format for a date in the 
     * Locale sent by the browser.
     */
    public DateFormat getDateFormat()
    {
        Locale locale = Localization.getLocale(data.getRequest());
        DateFormat df = DateFormat
            .getDateTimeInstance(DateFormat.MEDIUM, DateFormat.LONG, locale);
        if (timezone != null) 
        {
            df.setTimeZone(timezone);
        }
        return df;

        // We may want to eventually format the date other than default, 
        // this is how you would do it.
        //SimpleDateFormat sdf = new SimpleDateFormat(
        //    "yyyy/MM/dd hh:mm:ss a z", locale);
        //return (DateFormat) sdf;
    }

    /**
     * This is used to get the format for a date in the 
     * Locale sent by the browser.
     */
    public Calendar getCalendar()
    {
        Locale locale = Localization.getLocale(data.getRequest());
        Calendar cal = Calendar
            .getInstance(locale);
        if (timezone != null) 
        {
            cal.setTimeZone(timezone);
        }
        return cal;
    }

    /**
     * Determine if the user currently interacting with the scarab
     * application has a permission within the user's currently
     * selected module.
     *
     * @param permission a <code>String</code> permission value, which should
     * be a constant in this interface.
     * @return true if the permission exists for the user within the
     * current module, false otherwise
     */
    public boolean hasPermission(String permission)
    {
        boolean hasPermission = false;
        try
        {
            Module module = getCurrentModule();
            hasPermission = hasPermission(permission, module);
        }
        catch (Exception e)
        {
            hasPermission = false;
            Log.get().error("Permission check failed on:" + permission, e);
        }
        return hasPermission;
    }

    /**
     * Determine if the user currently interacting with the scarab
     * application has a permission within a module.
     *
     * @param permission a <code>String</code> permission value, which should
     * be a constant in this interface.
     * @param module a <code>Module</code> value
     * @return true if the permission exists for the user within the
     * given module, false otherwise
     */
    public boolean hasPermission(String permission, Module module)
    {
        boolean hasPermission = false;
        try
        {
            hasPermission = ((ScarabUser)data.getUser())
                .hasPermission(permission, module);
        }
        catch (Exception e)
        {
            hasPermission = false;
            Log.get().error("Permission check failed on:" + permission, e);
        }
        return hasPermission;
    }

    /* The map of associated users used on AssignIssue
     * When we first go to the screen, reset the map
     * To the currently assigned users for each issue
     */
    public void resetAssociatedUsers() throws Exception
    {
        HashMap assoUsers = new HashMap();
        List issueList = getIssues();
        if (issueList != null)
        {
            for (int i=0; i<issueList.size(); i++)
            {
                Issue issue = (Issue)issueList.get(i);
                assoUsers.put(issue.getIssueId(), issue.getAssociatedUsers());
            }
            ((ScarabUser)data.getUser()).setAssociatedUsersMap(assoUsers);
        }
    }

    public List getAssignIssuesList()
        throws Exception
    {        
        List issues = null;
        HashMap userMap = ((ScarabUser)data.getUser()).getAssociatedUsersMap();
        if (userMap != null && userMap.size() > 0)
        {
            issues = new ArrayList();
            Iterator iter = userMap.keySet().iterator();
            while (iter.hasNext()) 
            {
                issues.add(IssueManager.getInstance((NumberKey)iter.next()));
            }
        }
        return issues;
    }

    /**
     * When a user searches for other users (in the ManageUserSearch.vm
     * template for example), the result of this search is stored into
     * the temporary data for that user. This previous result can be 
     * retrieved by this method.
     *
     * FIXME: shouldn't this be stored into the cache instead of the
     * temporary data of the user?
     *
     * @return The list of users of the last user-search.
     */
    public List getGlobalUserSearch() 
    {
        List users = (List) data.getUser().getTemp("userList");
        if (users == null) 
        {
            users = new ArrayList();
        }
        return users;
    }
    
    /**
     * Store the search result of other users for later use. The 
     * result is stored into the temporary data of the current user.
     *
     * FIXME: use the cache instead?
     *
     * @param users The list of users that is a result of a query.
     */
    public void setGlobalUserSearch(List users) 
    {
        data.getUser().setTemp("userList", users);
    }
    
    /**
     * Return the parameter used for the user-search (like in the
     * ManageUserSearch.vm template for example) returned by the
     * getGlobalUserSearch() method. These parameters are stored
     * into the temporary data of the current user.
     *
     * FIXME: use the cache instead?
     *
     * @param name The name of the parameter
     * @return The value of the parameter used in the search for users.
     */
    public String getGlobalUserSearchParam(String name) 
    {
        Hashtable params = (Hashtable) data.getUser().getTemp("userListParams");
        
        if (params == null) 
        {
            return "";
        }

        return (String) params.get(name);
    }
    
    /**
     * Set the parameters used to retrieved the users in the List given
     * to the setGlobalUserSearch(List) method. These parameters can be
     * retrieved by the getGlobalUserSearchParam(String) for later use.
     *
     * FIXME: use the cache instead?
     *
     * @param name The name of the parameter
     * @param value The value of the parameter
     */
    public void setGlobalUserSearchParam(String name, String value) 
    {
        Hashtable params = (Hashtable) data.getUser().getTemp("userListParams");
        if (params == null) 
        {
            params = new Hashtable();
        }

        if ((name != null) && (value != null))
        {
            params.put(name, value);
        }
        data.getUser().setTemp("userListParams", params);
    }

    public boolean hasItemsToApprove()
    {
        try
        {
            SecurityAdminTool sat = (SecurityAdminTool)org.apache.turbine.modules.Module.getTemplateContext(data)
                .get(ScarabConstants.SECURITY_ADMIN_TOOL);
            if (getCurrentModule().getUnapprovedQueries().isEmpty() &&
                getCurrentModule().getUnapprovedTemplates().isEmpty() &&
                sat.getPendingGroupUserRoles(getCurrentModule()).isEmpty())
            {
                return false;
            }
        }
        catch (Exception e)
        {
            Log.get().debug("Error: ", e);
        }
        return true;
    }

    public MITList getMITList(List issues)
        throws Exception
    {
        return MITListManager
            .getInstanceFromIssueList(issues, (ScarabUser)data.getUser());
    }

    /**
     * Gets a list of Attributes or the user type that are in common
     * between the issues in the given list.
     *
     * @param issues a <code>List</code> value
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    public List getUserAttributes(List issues)
        throws Exception
    {        
        List attributes = null;
        if (issues == null || issues.isEmpty()) 
        {
            attributes = Collections.EMPTY_LIST;
            Log.get().warn("ScarabRequestTool.getUserAttributes issue list was"
                     + (issues == null ? " null" : " empty")) ;
        }
        else 
        {
            attributes = getMITList(issues).getCommonUserAttributes();
        }
        
        return attributes;
    }


    // --------------------
    // template timing methods
    private long startTime;
    private long lapTime;

    /**
     * Should be called near the beginning of a template or wherever timing
     * should start.
     */
    public void startTimer()
    {
        startTime = System.currentTimeMillis();
        lapTime = startTime;
    }

    /**
     * Useful when performance tuning.  Usage is to call
     * <pre><code>
     * $scarabR.startTimer()
     * ...
     * $scarabR.reportTimer("foo")
     * ...
     * $scarabR.reportTimer("bar")
     *
     * or
     *
     * $scarabG.log( $scarabR.reportTimer("bar") )
     * </code></pre>
     *
     * The labels are useful when output is directed to a log file, it can 
     * be "", if the output is written as part of the response.
     */
    public String reportTimer(String mesg)
    {
        long endTime = System.currentTimeMillis();
        String s = mesg + ".  Time for " + data.getTarget() + ": Lap/Split= "
            + (endTime-lapTime) + "ms; Cumulative= " + 
            (endTime-startTime) + "ms";
        lapTime = endTime;
        return s;
    }

    /**
     * Helper method to retrieve the ScarabLocalizationTool from the Context
     */
    private ScarabLocalizationTool getLocalizationTool()
    {
        return (ScarabLocalizationTool)org.apache.turbine.modules.Module
            .getTemplateContext(data).get(ScarabConstants.LOCALIZATION_TOOL);
    }

    /**
     * Helper method to retrieve the ScarabGlobalTool from the Context
     */
    private ScarabGlobalTool getGlobalTool()
    {
        return (ScarabGlobalTool)org.apache.turbine.modules.Module
            .getTemplateContext(data).get(ScarabConstants.SCARAB_GLOBAL_TOOL);
    }

    /**
     * Get any confirmation message usually set in the action.
     * @return value of confirmMessage.
     */
    public Object getConfirmMessage() 
    {
        return confirmMessage;
    }
    
    /**
     * Set confirmation message.
     * @param v  Value to assign to confirmMessage.
     */
    public void setConfirmMessage(Object  v) 
    {
        this.confirmMessage = v;
    }

    /**
     * Get any informational message usually set in the action.
     * @return value of infoMessage.
     */
    public Object getInfoMessage() 
    {
        return infoMessage;
    }
    
    /**
     * Set informational message.
     * @param v  Value to assign to infoMessage.
     */
    public void setInfoMessage(Object  v) 
    {
        this.infoMessage = v;
    }

    /**
     * Get any alert message usually set in the action.
     * @return value of alertMessage.
     */
    public Object getAlertMessage() 
    {
        return alertMessage;
    }
    
    /**
     * Set alert message.
     * @param v  Value to assign to alertMessage.
     */
    public void setAlertMessage(Object  v) 
    {
        this.alertMessage = v;
    }
    
    // ****************** Recyclable implementation ************************

    /**
     * Disposes the object after use. The method is called when the
     * object is returned to its pool.  The dispose method must call
     * its super.
     */
    public void dispose()
    {
        super.dispose();
        data = null;
        refresh();
    }
}
