List attGroups = getIssueType().getAttributeGroups(module);

package org.tigris.scarab.om;

import java.util.List;

import org.apache.torque.om.ObjectKey;
import org.apache.torque.om.NumberKey;
import org.apache.torque.om.Persistent;
import org.apache.torque.util.Criteria;
import org.apache.torque.pool.DBConnection;
import org.tigris.scarab.util.ScarabConstants;

import org.tigris.scarab.services.security.ScarabSecurity;
import org.tigris.scarab.util.ScarabException;
import org.tigris.scarab.services.module.ModuleEntity;
import org.tigris.scarab.services.module.ModuleManager;

/** 
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public  class RModuleIssueType 
    extends org.tigris.scarab.om.BaseRModuleIssueType
    implements Persistent
{
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
     * <code>setModule(ModuleEntity)</code> instead.
     *
     */
    public void setScarabModule(ScarabModule module)
    {
        throw new UnsupportedOperationException(
            "Should use setModule(ModuleEntity). Note module cannot be new.");
    }

    /**
     * Use this instead of setScarabModule.  Note: module cannot be new.
     */
    public void setModule(ModuleEntity me)
        throws Exception
    {
        NumberKey id = me.getModuleId();
        if (id == null) 
        {
            throw new ScarabException("Modules must be saved prior to " +
                                      "being associated with other objects.");
        }
        setModuleId(id);
    }

    /**
     * Module getter.  Use this method instead of getScarabModule().
     *
     * @return a <code>ModuleEntity</code> value
     */
    public ModuleEntity getModule()
        throws Exception
    {
        ModuleEntity module = null;
        ObjectKey id = getModuleId();
        if ( id != null ) 
        {
            module = ModuleManager.getInstance(id);
        }
        
        return module;
    }


    /**
     * Checks if user has permission to delete module-issue type mapping.
     */
    public void delete( ScarabUser user )
         throws Exception
    {                
        ModuleEntity module = getModule();

        if (user.hasPermission(ScarabSecurity.MODULE__EDIT, module))
        {
            // Delete attribute groups first
            List attGroups = getIssueType().getAttributeGroups(); 
            for (int j=0; j<attGroups.size(); j++)
            {
                // delete attribute-attribute group map
                AttributeGroup attGroup = 
                              (AttributeGroup)attGroups.get(j);
                attGroup.delete(user);
            }

            Criteria c = new Criteria()
                .add(RModuleIssueTypePeer.MODULE_ID, getModuleId())
                .add(RModuleIssueTypePeer.ISSUE_TYPE_ID, getIssueTypeId());
            RModuleIssueTypePeer.doDelete(c);
            save();
        }
        else
        {
            throw new ScarabException(ScarabConstants.NO_PERMISSION_MESSAGE);
        }            
    }

    /**
     * Gets name to display.
     */
    public String getDisplayText() throws Exception
    {    
        String display = getIssueType().getName();            
        if (super.getDisplayName() != null)
        {
            display = super.getDisplayName();
        }
        return display;
    }
            
    /**
     * Copies object.
     */
    public RModuleIssueType copy()
         throws Exception
    {                
        RModuleIssueType rmit2 = new RModuleIssueType();
        rmit2.setModuleId(getModuleId());
        rmit2.setIssueTypeId(getIssueTypeId());
        rmit2.setActive(getActive());
        rmit2.setDisplay(getDisplay());
        rmit2.setOrder(getOrder());
        rmit2.setHistory(getHistory());
        rmit2.setComments(getComments());
        return rmit2;
    }

    /**
     * Adding to debug a problem with project creation
     */
    public void save(DBConnection dbCon) throws Exception
    {
        // If this object has been modified, then save it to the database.
        if (isModified())
        {
            if (isNew())
            {
                getCategory().debug("[RMIT] Saving new template type: " + 
                                    getModuleId() + "-" + getIssueTypeId());
            }
        }
        super.save(dbCon);
    }
}