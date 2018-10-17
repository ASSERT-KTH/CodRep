c.add(IssueTypePeer.PARENT_ID, 0);

package org.tigris.scarab.om;

import java.util.*;
import com.workingdogs.village.*;
import org.apache.torque.map.*;
import org.apache.torque.pool.DBConnection;
import org.apache.torque.util.Criteria;

// Local classes
import org.tigris.scarab.om.map.*;

/** 
 *  You should add additional methods to this class to meet the
 *  application requirements.  This class will only be generated as
 *  long as it does not already exist in the output directory.
 */
public class IssueTypePeer 
    extends org.tigris.scarab.om.BaseIssueTypePeer
{

    /**
     *  Gets a List of all of the Issue types in the database,
     *  That are not template types.
     */
    public static List getAllIssueTypes()
        throws Exception
    {
        Criteria c = new Criteria();
        c.add(IssueTypePeer.TEMPLATE, 0);
        return doSelect(c);
    }
}