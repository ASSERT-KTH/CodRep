for (int i=1; i<=groups.size(); i++)

package org.tigris.scarab.om;

import java.util.Vector;
import org.apache.torque.om.NumberKey;
import org.apache.torque.util.Criteria;

import org.apache.torque.om.UnsecurePersistent;

/** 
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public  class IssueType 
    extends org.tigris.scarab.om.BaseIssueType
    implements UnsecurePersistent
{

    public static final NumberKey ISSUE__PK = new NumberKey("1");
    public static final NumberKey USER_TEMPLATE__PK = new NumberKey("2");
    public static final NumberKey GLOBAL_TEMPLATE__PK = new NumberKey("3");

    /**
     * List of attribute groups associated with this module and issue type.
     */
    public Vector getAttributeGroups(ScarabModule module)
        throws Exception
    {
        Vector groups = null;
        Criteria crit = new Criteria()
            .add(AttributeGroupPeer.MODULE_ID, module.getModuleId())
            .add(AttributeGroupPeer.ISSUE_TYPE_ID, getIssueTypeId())
            .addAscendingOrderByColumn(AttributeGroupPeer.PREFERRED_ORDER);
        groups = AttributeGroupPeer.doSelect(crit);
        return groups;
    }

    /**
     * Gets the sequence where the dedupe screen fits between groups.
     */
    public int getDedupeSequence(ScarabModule module)
        throws Exception
    {
        int sequence = 1;
        Vector groups = getAttributeGroups(module);
        for (int i=1; i<groups.size(); i++)
        {
           int order = ((AttributeGroup)groups.get(i)).getOrder();
           int previousOrder = ((AttributeGroup)groups.get(i-1)).getOrder();
           if (order != previousOrder + 1)
           {
               sequence = order-1;
               break;
           }
        }
        return sequence;
    }
    
}