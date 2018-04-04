import org.apache.torque.om.Persistent;

package org.tigris.scarab.om;


import org.apache.turbine.services.db.om.Persistent;

/** 
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public  class Query 
    extends org.tigris.scarab.om.BaseQuery
    implements Persistent
{
    /**
     * A new Query object
     */
    public static Query getInstance() 
    {
        return new Query();
    }

}