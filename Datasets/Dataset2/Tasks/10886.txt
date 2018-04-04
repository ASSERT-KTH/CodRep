+ "&resultsperpage=25&pagenum=1" + getValue();

package org.tigris.scarab.om;

import java.util.Vector;
import org.apache.torque.util.Criteria;
import org.apache.torque.om.Persistent;

/** 
 * You should add additional methods to this class to meet the
 * application requirements.  This class will only be generated as
 * long as it does not already exist in the output directory.
 */
public class Query 
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

    /**
     * Generates link to Issue List page, re-running stored query.
     */
    public String getExecuteLink(String link) 
    {
       return link 
          + "/template/IssueList.vm?action=Search&eventSubmit_doSearch=Search" 
          + getValue();
    }

    /**
     * Generates link to the Query Detail page.
     */
    public String getEditLink(String link) 
    {
        return link + "/template/secure,EditQuery.vm?queryId=" + getQueryId()
                    + getValue();
    }

    /**
     * Returns list of all query types.
     */
    public Vector getAllQueryTypes() throws Exception
    {
        return QueryTypePeer.doSelect(new Criteria());
    }
}