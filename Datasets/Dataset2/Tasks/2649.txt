return highest + 1;

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
import java.util.LinkedList;
import java.util.Iterator;
import org.apache.torque.TorqueException;
import org.apache.torque.om.ObjectKey;
import org.apache.torque.om.NumberKey;
import org.apache.torque.om.Persistent;
import org.apache.torque.util.Criteria;

import org.tigris.scarab.services.security.ScarabSecurity;
import org.tigris.scarab.services.cache.ScarabCache;
import org.tigris.scarab.om.Module;
import org.tigris.scarab.om.ModuleManager;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;

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
    private static final String GET_ATTRIBUTES = 
        "getAttributes";
    private static final String GET_R_ATTRIBUTE_ATTRGROUP = 
        "getRAttributeAttributeGroup";
    private static final String GET_ATTRIBUTE_GROUPS = 
        "getAttributeGroups";

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
        NumberKey id = me.getModuleId();
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
        ObjectKey id = getModuleId();
        if ( id != null ) 
        {
            module = ModuleManager.getInstance(id);
        }
        
        return module;
    }


    /**
     * List of Attributes in this group.
     */
    public List getAttributes()
        throws Exception
    {
        List result = null;
        Object obj = ScarabCache.get(this, GET_ATTRIBUTES); 
        if ( obj == null ) 
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
                ObjectKey id = ((RAttributeAttributeGroup)i.next())
                    .getAttributeId();
                result.add(AttributeManager.getInstance(id));
            }
            ScarabCache.put(result, this, GET_ATTRIBUTES);
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
        return highest;
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
        if ( obj == null ) 
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


    public void delete( ScarabUser user )
         throws Exception
    {                
        Module module = getModule();

        if (user.hasPermission(ScarabSecurity.MODULE__EDIT, module))
        {
            // Delete module-attribute mapping
            IssueType issueType = IssueTypeManager
               .getInstance(getIssueTypeId(), false);
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

            // Delete attribute - attribute group mapping
            crit = new Criteria()
                .add(RAttributeAttributeGroupPeer.GROUP_ID, getAttributeGroupId());
            RAttributeAttributeGroupPeer.doDelete(crit);

           // Delete the attribute group
            crit = new Criteria()
                .add(AttributeGroupPeer.ATTRIBUTE_GROUP_ID, getAttributeGroupId());
            AttributeGroupPeer.doDelete(crit);
            List attrGroups = module.getAttributeGroups(getIssueType(), false);
            attrGroups.remove(this);
            attrGroups = module.getAttributeGroups(getIssueType(), true);
            attrGroups.remove(this);
        } 
        else
        {
            throw new ScarabException(ScarabConstants.NO_PERMISSION_MESSAGE);
        }            
    }

    public void addAttribute( Attribute attribute )
         throws Exception
    {                
        IssueType issueType = getIssueType();
        Module module = getModule();

        // add attribute group-attribute mapping
        RAttributeAttributeGroup raag =
            addRAttributeAttributeGroup(attribute);
        raag.save();          

        // add module-attribute groupings
        module.addRModuleAttribute(issueType, attribute);

        // add module-attributeoption mappings
        List options = attribute.getAttributeOptions();
        for (int j=0;j < options.size();j++)
        {
            AttributeOption option = (AttributeOption)options.get(j);
            RModuleOption rmo = module.addRModuleOption(issueType, 
                                                        option);
            rmo.save();

            // add module-attributeoption mappings to template type
            IssueType templateType = IssueTypeManager
                .getInstance(issueType.getTemplateId(), false);
            RModuleOption rmo2 = module.
                 addRModuleOption(templateType, option);
            rmo2.save();
        }
        getAttributes().add(attribute);
    }

    public void deleteAttribute( Attribute attribute, ScarabUser user )
         throws Exception
    {                
        IssueType issueType = getIssueType();
        Module module = getModule();

        // Remove attribute - module mapping
        List rmas = module.getRModuleAttributes(issueType, false,
                                                "data");    
        RModuleAttribute rma = module
            .getRModuleAttribute(attribute, issueType);
        rma.delete(user);
        rmas.remove(rma);

        // Remove attribute - module mapping from template type
        IssueType template = IssueTypeManager.getInstance
                             (issueType.getTemplateId());
        RModuleAttribute rma2 = module
            .getRModuleAttribute(attribute, template);
        rma2.delete(user);
        rmas.remove(rma2);

        // Remove attribute - group mapping
        RAttributeAttributeGroup raag = 
            getRAttributeAttributeGroup(attribute);
        raag.delete(user);

        if (attribute.isOptionAttribute())
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

    private RAttributeAttributeGroup addRAttributeAttributeGroup( Attribute attribute )
         throws Exception
    {                
        RAttributeAttributeGroup raag = new RAttributeAttributeGroup();
        raag.setGroupId(getAttributeGroupId());
        raag.setAttributeId(attribute.getAttributeId());
        raag.setOrder(getAttributes().size() +1 );
        return raag;
    }
}