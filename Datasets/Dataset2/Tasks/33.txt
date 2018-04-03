return AttributePeer.doSelect(crit);

package org.tigris.scarab.om;

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



import java.util.List;
import org.apache.torque.om.UnsecurePersistent;
import org.apache.torque.util.Criteria;

import org.tigris.scarab.security.ScarabSecurity;
import org.tigris.scarab.security.SecurityFactory;
import org.tigris.scarab.services.module.ModuleEntity;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;

/** 
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public  class AttributeGroup 
    extends org.tigris.scarab.om.BaseAttributeGroup
    implements UnsecurePersistent
{

    /**
     * List of attributes in this group.
     */
    public List getAttributes()
        throws Exception
    {
        Criteria crit = new Criteria()
            .add(RAttributeAttributeGroupPeer.GROUP_ID, getAttributeGroupId())
            .addJoin(RAttributeAttributeGroupPeer.ATTRIBUTE_ID, 
                                                  AttributePeer.ATTRIBUTE_ID)
            .addAscendingOrderByColumn(RAttributeAttributeGroupPeer
                                       .PREFERRED_ORDER);
        return (List) AttributePeer.doSelect(crit);
    }

    /**
     * FIXME: Should use ModuleManager.  Use this instead of setScarabModule.
     */
    public void setModule(ModuleEntity me)
        throws Exception
    {
        super.setScarabModule((ScarabModule)me);
    }

    /**
     * Module getter.  Use this method instead of getScarabModule().
     *
     * @return a <code>ModuleEntity</code> value
     */
    public ModuleEntity getModule()
        throws Exception
    {
        return getScarabModule();
    }

    /**
     * Retrieves R_ATTRIBUTE_ATTRIBUTEGROUP mapping object for this group
     * And the given attribute.
     */
    public RAttributeAttributeGroup getRAttributeAttributeGroup
        (Attribute attribute)
        throws Exception
    {
        RAttributeAttributeGroup ras = null;
        Criteria crit = new Criteria()
            .add(RAttributeAttributeGroupPeer.GROUP_ID, getAttributeGroupId())
            .add(RAttributeAttributeGroupPeer.ATTRIBUTE_ID, 
                 attribute.getAttributeId());
        
         ras = (RAttributeAttributeGroup)RAttributeAttributeGroupPeer
                                         .doSelect(crit).get(0);
         return ras;
    }

    public void delete( ScarabUser user )
         throws Exception
    {                
        ModuleEntity module = getModule();
        ScarabSecurity security = SecurityFactory.getInstance();

        if (security.hasPermission(ScarabSecurity.MODULE__EDIT,
                                   user, module))
        {
            // Delete module-attribute mapping
            Criteria c  = new Criteria()
                .addJoin(RModuleAttributePeer.ATTRIBUTE_ID,
                         RAttributeAttributeGroupPeer.ATTRIBUTE_ID)
                .add(RAttributeAttributeGroupPeer.GROUP_ID,
                         getAttributeGroupId());
                 List results = RModuleAttributePeer.doSelect(c);
            for (int i=0; i<results.size(); i++)
            {
                 RModuleAttribute rma = (RModuleAttribute)results.get(i);
                 rma.delete(user);
            }

            // Delete attribute - attribute group mapping
            c = new Criteria()
                .add(RAttributeAttributeGroupPeer.GROUP_ID, getAttributeGroupId());
            RAttributeAttributeGroupPeer.doDelete(c);

           // Delete the attribute group
            c = new Criteria()
                .add(AttributeGroupPeer.ATTRIBUTE_GROUP_ID, getAttributeGroupId());
            AttributeGroupPeer.doDelete(c);
        } 
        else
        {
            throw new ScarabException(ScarabConstants.NO_PERMISSION_MESSAGE);
        }            
    }

}