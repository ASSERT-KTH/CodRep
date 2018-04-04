if (user.hasPermission(ScarabSecurity.MODULE__EDIT, module))

package org.tigris.scarab.om;

import org.apache.torque.om.Persistent;
//import org.apache.fulcrum.template.TemplateContext;
import org.apache.torque.util.Criteria;

import org.tigris.scarab.services.security.ScarabSecurity;
import org.tigris.scarab.services.module.ModuleEntity;
import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;

/** 
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public  class RAttributeAttributeGroup 
    extends org.tigris.scarab.om.BaseRAttributeAttributeGroup
    implements Persistent
{

    /**
     * Delete the record.
     */
    public void delete(ScarabUser user) throws Exception 
    { 
        ModuleEntity module = getAttributeGroup().getModule();

        if (user.hasPermission(ScarabSecurity.ITEM__APPROVE, module))
        {
            Criteria c = new Criteria()
                .add(RAttributeAttributeGroupPeer.GROUP_ID, getGroupId())
                .add(RAttributeAttributeGroupPeer.ATTRIBUTE_ID, getAttributeId());
            RAttributeAttributeGroupPeer.doDelete(c);
        } 
        else
        {
            throw new ScarabException(ScarabConstants.NO_PERMISSION_MESSAGE);
        }            
    }
}