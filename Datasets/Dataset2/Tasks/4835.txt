Integer id = getModuleId();

package org.tigris.scarab.om;

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



import java.util.List;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Iterator;
import org.apache.torque.TorqueException;
import org.apache.torque.om.ObjectKey;
import org.apache.torque.om.NumberKey;
import org.apache.torque.om.SimpleKey;
import org.apache.torque.om.Persistent;
import org.apache.torque.util.Criteria;

import org.tigris.scarab.services.security.ScarabSecurity;
import org.tigris.scarab.services.cache.ScarabCache;
import org.tigris.scarab.om.Module;
import org.tigris.scarab.om.ModuleManager;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;
import org.tigris.scarab.workflow.WorkflowFactory;

/** 
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public  class AttributeGroup 
    extends org.tigris.scarab.om.BaseAttributeGroup
    implements Persistent
{
    // the following Strings are method names that are used in caching results
    public static final String GET_ATTRIBUTES = 
        "getAttributes";
    private static final String GET_R_ATTRIBUTE_ATTRGROUP = 
        "getRAttributeAttributeGroup";

    public boolean isGlobal()
        throws TorqueException
    {
        return (getModule() == null);
    }

    /**
     * Throws UnsupportedOperationException.  Use
     * <code>getModule()</code> instead.
     *
     * @return a <code>ScarabModule</code> value
     */
    public ScarabModule getScarabModule()
    {
        throw new UnsupportedOperationException(
            "Should use getModule");
    }

    /**
     * Throws UnsupportedOperationException.  Use
     * <code>setModule(Module)</code> instead.
     *
     */
    public void setScarabModule(ScarabModule module)
    {
        throw new UnsupportedOperationException(
            "Should use setModule(Module). Note module cannot be new.");
    }

    /**
     * Use this instead of setScarabModule.  Note: module cannot be new.
     */
    public void setModule(Module me)
        throws TorqueException
    {
        Integer id = me.getModuleId();
        if ( id == null) 
        {
            throw new TorqueException("Modules must be saved prior to " +
                                      "being associated with other objects.");
        }
        setModuleId(id);
    }

    /**
     * Module getter.  Use this method instead of getScarabModule().
     *
     * @return a <code>Module</code> value
     */
    public Module getModule()
        throws TorqueException
    {
        Module module = null;
        ObjectKey id = getPrimaryKey();
        if ( id != null ) 
        {
            module = ModuleManager.getInstance(id);
        }
        
        return module;
    }

    private static org.apache.torque.manager.MethodResultCache
        getMethodResult()
    {
        return AttributeGroupManager.getMethodResult();
    }

    public boolean hasAnyOptionAttributes()
        throws Exception
    {
        boolean result = false;
        for (Iterator i = getAttributes().iterator(); i.hasNext() && !result;) 
        {
            result = ((Attribute)i.next()).isOptionAttribute();
        }
        return result;
    }

    /**
     * List of Attributes in this group.
     */
    public List getAttributes()
        throws Exception
    {
        List result = null;
        Object obj = getMethodResult().get(this, GET_ATTRIBUTES); 
        if (obj == null) 
        {        
            Criteria crit = new Criteria()
                .add(RAttributeAttributeGroupPeer.GROUP_ID, 
                     getAttributeGroupId())
                .addJoin(RAttributeAttributeGroupPeer.ATTRIBUTE_ID, 
                         AttributePeer.ATTRIBUTE_ID)
                .add(AttributePeer.ATTRIBUTE_TYPE_ID, 
                     AttributeTypePeer.USER_TYPE_KEY, Criteria.NOT_EQUAL)
                .add(AttributePeer.DELETED, false)
                .addAscendingOrderByColumn(RAttributeAttributeGroupPeer
                                           .PREFERRED_ORDER);
            List raags = RAttributeAttributeGroupPeer.doSelect(crit);
            result = new LinkedList();
            Iterator i = raags.iterator();
            while (i.hasNext()) 
            {
                Integer id = ((RAttributeAttributeGroup)i.next())
                    .getAttributeId();
                result.add(AttributeManager.getInstance(SimpleKey.keyFor(id)));
            }
            getMethodResult().put(result, this, GET_ATTRIBUTES);
        }
        else 
        {
            result = (List)obj;
        }
        return result;
    }

    /**
     * Retrieves the attribute in this group with the highest preferred order.
     */
    public int getHighestOrderedAttribute ()
        throws Exception
    {
        int highest = 0;
        Criteria crit = new Criteria()
            .add(RAttributeAttributeGroupPeer.GROUP_ID, 
                 getAttributeGroupId())
            .addAscendingOrderByColumn(RAttributeAttributeGroupPeer
                                       .PREFERRED_ORDER);
        List raags = RAttributeAttributeGroupPeer.doSelect(crit);
        if (raags.size() > 0)
        {
            RAttributeAttributeGroup raag = (RAttributeAttributeGroup)
                                             raags.get(raags.size()-1);
            highest = raag.getOrder();
        }
        return highest + 1;
    }
       
    /**
     * Retrieves R_ATTRIBUTE_ATTRIBUTEGROUP mapping object for this group
     * And the given attribute.
     */
    public RAttributeAttributeGroup getRAttributeAttributeGroup
        (Attribute attribute)
        throws Exception
    {
        RAttributeAttributeGroup result = null;
        Object obj = ScarabCache.get(this, GET_R_ATTRIBUTE_ATTRGROUP, 
                                     attribute); 
        if (obj == null) 
        {        
            Criteria crit = new Criteria()
                .add(RAttributeAttributeGroupPeer.GROUP_ID, 
                     getAttributeGroupId())
                .add(RAttributeAttributeGroupPeer.ATTRIBUTE_ID, 
                     attribute.getAttributeId());
            
            result = (RAttributeAttributeGroup)RAttributeAttributeGroupPeer
                .doSelect(crit).get(0);
            ScarabCache.put(result, this, GET_R_ATTRIBUTE_ATTRGROUP, 
                            attribute);
        }
        else 
        {
            result = (RAttributeAttributeGroup)obj;
        }
        return result;
    }


    public void delete(ScarabUser user, Module module)
         throws Exception
    {                
        String permission = null;
        int dupeSequence = 0;
        if (isGlobal())
        {
            permission = (ScarabSecurity.DOMAIN__EDIT);
        }
        else
        {
            permission = (ScarabSecurity.MODULE__CONFIGURE);
        }
        if (user.hasPermission(permission, module))
        {
            IssueType issueType = IssueTypeManager
               .getInstance(SimpleKey.keyFor(getIssueTypeId()), false);
            if (issueType.getLocked())
            { 
                throw new ScarabException("You cannot delete this group, " + 
                                          "because this issue type is locked.");
            }            
            else
            {
                List attrGroups = null;
                if (isGlobal())
                {
                    attrGroups = issueType.getAttributeGroups(false);
                    dupeSequence =  issueType.getDedupeSequence();
                    // Delete issuetype-attribute mapping
                    Criteria crit  = new Criteria()
                        .addJoin(RIssueTypeAttributePeer.ATTRIBUTE_ID,
                                 RAttributeAttributeGroupPeer.ATTRIBUTE_ID)
                        .add(RAttributeAttributeGroupPeer.GROUP_ID,
                                 getAttributeGroupId());
                    List results = RIssueTypeAttributePeer.doSelect(crit);
                    for (int i=0; i<results.size(); i++)
                    {
                         RIssueTypeAttribute ria = (RIssueTypeAttribute)results.get(i);
                         ria.delete(user);
                    }
                }
                else
                {
                    attrGroups = module.getAttributeGroups(getIssueType(), false);
                    dupeSequence =  module.getDedupeSequence(issueType);
                    // Delete module-attribute mapping
                    Criteria crit  = new Criteria()
                        .addJoin(RModuleAttributePeer.ATTRIBUTE_ID,
                                 RAttributeAttributeGroupPeer.ATTRIBUTE_ID)
                        .add(RAttributeAttributeGroupPeer.GROUP_ID,
                                 getAttributeGroupId())
                        .add(RModuleAttributePeer.MODULE_ID,
                                 getModuleId());
                        Criteria.Criterion critIssueType = crit.getNewCriterion(
                                RModuleAttributePeer.ISSUE_TYPE_ID,
                                getIssueTypeId(), Criteria.EQUAL);
                        critIssueType.or(crit.getNewCriterion(
                                RModuleAttributePeer.ISSUE_TYPE_ID,
                                issueType.getTemplateId(), Criteria.EQUAL));
                        crit.and(critIssueType);
                    List results = RModuleAttributePeer.doSelect(crit);
                    for (int i=0; i<results.size(); i++)
                    {
                         RModuleAttribute rma = (RModuleAttribute)results.get(i);
                         rma.delete(user);
                    }
                }

                // Delete attribute - attribute group mapping
                Criteria crit2 = new Criteria()
                    .add(RAttributeAttributeGroupPeer.GROUP_ID, getAttributeGroupId());
                RAttributeAttributeGroupPeer.doDelete(crit2);


                // Delete the attribute group
                int order = getOrder();
                crit2 = new Criteria()
                    .add(AttributeGroupPeer.ATTRIBUTE_GROUP_ID, getAttributeGroupId());
                AttributeGroupPeer.doDelete(crit2);
                attrGroups.remove(this);
                
                // Adjust the orders for the other attribute groups
                for (int i=0; i<attrGroups.size(); i++)
                {
                    AttributeGroup tempGroup = (AttributeGroup)attrGroups.get(i);
                    int tempOrder = tempGroup.getOrder();
                    if (tempGroup.getOrder() > order)
                    { 
                        if (tempOrder == dupeSequence + 1)
                        {
                            tempGroup.setOrder(tempOrder - 2);
                        }
                        else
                        {
                            tempGroup.setOrder(tempOrder - 1);
                        }
                        tempGroup.save();
                    }
                }
                    
            } 
            ScarabCache.clear();
        } 
        else
        {
            throw new ScarabException(ScarabConstants.NO_PERMISSION_MESSAGE);
        }            
    }

    public void addAttribute(Attribute attribute)
         throws Exception
    {                
        IssueType issueType = getIssueType();
        Module module = getModule();

        // add attribute group-attribute mapping
        RAttributeAttributeGroup raag =
            addRAttributeAttributeGroup(attribute);
        raag.save();          
        getAttributes().add(attribute);

        List allOptions = attribute.getAttributeOptions(false);
        // remove duplicate options
        ArrayList options = new ArrayList();
        for (int i=0; i<allOptions.size(); i++)
        {
            AttributeOption option = (AttributeOption)allOptions.get(i);
            if (!options.contains(option))
            {
                options.add(option);
            }
        }

        if (isGlobal())
        {
            // this is a global attribute group
            // add issuetype-attribute groupings
            issueType.addRIssueTypeAttribute(attribute);

            // add issueType-attributeoption mappings
            for (int j=0;j < options.size();j++)
            {
                AttributeOption option = (AttributeOption)options.get(j);
                List roos = option.getROptionOptionsRelatedByOption2Id();
                ROptionOption roo = (ROptionOption)roos.get(0);
                RIssueTypeOption rio = new RIssueTypeOption();
                rio.setIssueTypeId(issueType.getIssueTypeId());
                rio.setOptionId(option.getOptionId());
                rio.setOrder(roo.getPreferredOrder());
                rio.setWeight(roo.getWeight());
                rio.save();
            }
        }
        else
        {
            // add module-attribute groupings
            module.addRModuleAttribute(issueType, attribute);

            // add module-attributeoption mappings
            for (int j=0;j < options.size();j++)
            {
                AttributeOption option = (AttributeOption)options.get(j);
                List roos = option.getROptionOptionsRelatedByOption2Id();
                ROptionOption roo = (ROptionOption)roos.get(0);
                RModuleOption rmo = new RModuleOption();
                rmo.setModuleId(getModuleId());
                rmo.setIssueTypeId(issueType.getIssueTypeId());
                rmo.setOptionId(option.getOptionId());
                rmo.setDisplayValue(option.getName());
                rmo.setOrder(roo.getPreferredOrder());
                rmo.setWeight(roo.getWeight());
                rmo.save();

                // add module-attributeoption mappings to template type
                IssueType templateType = IssueTypeManager
                    .getInstance(issueType.getTemplateId(), false);
                RModuleOption rmo2 = module.
                     addRModuleOption(templateType, option);
                rmo2.save();
            }
        }
        getMethodResult().remove(this, AttributeGroup.GET_ATTRIBUTES);
    }

    public void deleteAttribute(Attribute attribute, ScarabUser user,
                                 Module module)
         throws Exception
    {                
        String permission = null;
        if (isGlobal())
        {
            permission = (ScarabSecurity.DOMAIN__EDIT);
        }
        else
        {
            permission = (ScarabSecurity.MODULE__CONFIGURE);
        }
        if (user.hasPermission(permission, module))
        {
            IssueType issueType = getIssueType();
            IssueType template = IssueTypeManager.getInstance
                                 (issueType.getTemplateId());
            boolean success = true;

            RIssueTypeAttribute ria = issueType.getRIssueTypeAttribute(attribute);
            if (isGlobal())
            {
                // This is a global attribute group
                // Remove attribute - issue type mapping
                List rias = issueType.getRIssueTypeAttributes
                                     (false, AttributePeer.NON_USER);
                ria.delete(user);
                rias.remove(ria);
            }
            else
            {
                // Check if attribute is locked
                if (ria != null && ria.getLocked())
                {
                    success = false;
                    throw new TorqueException(attribute.getName() + "is locked");
                }
                else
                {
                    // Remove attribute - module mapping
                    List rmas = module.getRModuleAttributes(issueType, false,
                                                            AttributePeer.NON_USER);    
                    RModuleAttribute rma = module
                        .getRModuleAttribute(attribute, issueType);
                    rma.delete(user);
                    WorkflowFactory.getInstance().deleteWorkflowsForAttribute
                                                  (attribute, module, issueType);
                    rmas.remove(rma);

                    // Remove attribute - module mapping from template type
                    RModuleAttribute rma2 = module
                                   .getRModuleAttribute(attribute, template);
                    rma2.delete(user);
                    rmas.remove(rma2);
                }
            }

            if (success)
            {
                // Remove attribute - group mapping
                RAttributeAttributeGroup raag = 
                    getRAttributeAttributeGroup(attribute);
                raag.delete(user);

                if (attribute.isOptionAttribute())
                {
                    if (isGlobal())
                    { 
                        // global attributeGroup; remove issuetype-option maps
                        List rios = issueType.getRIssueTypeOptions(attribute);
                        for (int i = 0; i<rios.size();i++)
                        {
                            RIssueTypeOption rio = (RIssueTypeOption)rios.get(i);
                            rio.delete(user, module);
                        }
                    }
                    else
                    {
                        // Remove module-option mapping
                        List rmos = module.getRModuleOptions(attribute, issueType);
                        if (rmos != null)
                        {
                            rmos.addAll(module.getRModuleOptions(attribute, template));
                            for (int j = 0; j<rmos.size();j++)
                            {
                                RModuleOption rmo = (RModuleOption)rmos.get(j);
                                 // rmo's may be inherited by the parent module.
                                 // don't delete unless they are directly associated
                                 // with this module.  Will know by the first one.
                                 if (rmo.getModuleId().equals(module.getModuleId())) 
                                 {
                                     rmo.delete(user);
                                 }
                                 else 
                                 {
                                     break;
                                 } 
                             }
                         }
                     }
                 }
             }
         }
         else
         {
             throw new ScarabException(ScarabConstants.NO_PERMISSION_MESSAGE);
         }            
        getMethodResult().remove(this, AttributeGroup.GET_ATTRIBUTES);
    }

    private RAttributeAttributeGroup addRAttributeAttributeGroup(Attribute attribute)
         throws Exception
    {                
        RAttributeAttributeGroup raag = new RAttributeAttributeGroup();
        raag.setGroupId(getAttributeGroupId());
        raag.setAttributeId(attribute.getAttributeId());
        raag.setOrder(getAttributes().size() +1);
        return raag;
    }

    public AttributeGroup copyGroup()
         throws Exception
    {                
        AttributeGroup newGroup = new AttributeGroup();
        newGroup.setName(getName());
        newGroup.setDescription(getDescription());
        newGroup.setDedupe(getDedupe());
        newGroup.setActive(getActive());
        newGroup.setOrder(getOrder());
        return newGroup;
    }
}