sortColumn = RModuleOptionPeer.PREFERRED_ORDER;

package org.tigris.scarab.util.word;

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

// JDK classes
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.Iterator;
import java.util.Vector;
import java.util.ArrayList;
import java.util.Date;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.text.ParseException;

import com.workingdogs.village.Record;
import org.apache.torque.TorqueException;
import org.apache.torque.om.NumberKey;
import org.apache.torque.util.Criteria;
import org.apache.commons.collections.SequencedHashMap;
import org.apache.commons.lang.StringUtils;

// Scarab classes
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.AttributeManager;
import org.tigris.scarab.om.AttributeOption;
import org.tigris.scarab.om.AttributeOptionPeer;
import org.tigris.scarab.om.AttachmentTypePeer;
import org.tigris.scarab.om.Issue;
import org.tigris.scarab.om.IssueType;
import org.tigris.scarab.om.IssuePeer;
import org.tigris.scarab.om.ROptionOptionPeer;
import org.tigris.scarab.om.AttributeValuePeer;
import org.tigris.scarab.om.AttributeValue;
import org.tigris.scarab.om.AttributePeer;
import org.tigris.scarab.om.ActivityPeer;
import org.tigris.scarab.om.ActivitySetPeer;
import org.tigris.scarab.om.ActivitySetTypePeer;
import org.tigris.scarab.om.RModuleOptionPeer;
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.om.ScarabUserManager;
import org.tigris.scarab.om.Module;
import org.tigris.scarab.om.MITList;
import org.tigris.scarab.om.MITListItem;

import org.tigris.scarab.util.ScarabConstants;
import org.tigris.scarab.util.ScarabException;
import org.tigris.scarab.attribute.OptionAttribute;
import org.tigris.scarab.attribute.UserAttribute;
import org.tigris.scarab.attribute.StringAttribute;


/** 
 * A utility class to build up and carry out a search for 
 * similar issues.  It subclasses Issue for functionality, it is 
 * not a more specific type of Issue.
 */
public class IssueSearch 
    extends Issue
{
    public static final String ASC = "asc";
    public static final String DESC = "desc";

    public static final String CREATED_BY_KEY = "created_by";
    public static final String ANY_KEY = "any";

    private static final NumberKey ALL_TEXT = new NumberKey("0");

    private static final String PARENT_ID = ROptionOptionPeer.OPTION1_ID;
    private static final String CHILD_ID = ROptionOptionPeer.OPTION2_ID;

    // column names only
    private static final String AV_OPTION_ID = 
        AttributeValuePeer.OPTION_ID.substring(
        AttributeValuePeer.OPTION_ID.indexOf('.')+1);
    private static final String AV_ISSUE_ID = 
        AttributeValuePeer.ISSUE_ID.substring(
        AttributeValuePeer.ISSUE_ID.indexOf('.')+1);
    private static final String AV_USER_ID =
        AttributeValuePeer.USER_ID.substring(
        AttributeValuePeer.USER_ID.indexOf('.')+1);

    private static final String ACTIVITYSETALIAS = "srchcobyactset";
    private static final String USERAVALIAS = "srchuav";
    private static final String ACTIVITYALIAS = "srchcobyact";

    private static final String CREATED_BY = "CREATED_BY";
    private static final String TYPE_ID = "TYPE_ID";
    private static final String ATTRIBUTE_ID = "ATTRIBUTE_ID";
    private static final String USER_ID = "USER_ID";
    private static final String DELETED = "DELETED";

    private static final String ACT_TRAN_ID = 
        ActivityPeer.TRANSACTION_ID.substring(
        ActivityPeer.TRANSACTION_ID.indexOf('.')+1);
    private static final String ACTSET_TRAN_ID = 
        ActivitySetPeer.TRANSACTION_ID.substring(
        ActivitySetPeer.TRANSACTION_ID.indexOf('.')+1);
    private static final String ACTIVITYALIAS_TRANSACTION_ID =
        ACTIVITYALIAS + "." + ACT_TRAN_ID;
    private static final String 
        ACTIVITYALIAS_TRAN_ID__EQUALS__ACTIVITYSETALIAS_TRAN_ID =
        ACTIVITYALIAS_TRANSACTION_ID + "=" + 
        ACTIVITYSETALIAS + "." + ACTSET_TRAN_ID;

    private static final String ACT_ISSUE_ID = 
        ActivityPeer.ISSUE_ID.substring(ActivityPeer.ISSUE_ID.indexOf('.')+1);
    private static final String ACTIVITYALIAS_ISSUE_ID =
        ACTIVITYALIAS + "." + ACT_ISSUE_ID;
    private static final String 
        ACTIVITYALIAS_ISSUE_ID__EQUALS__ISSUEPEER_ISSUE_ID =
        ACTIVITYALIAS_ISSUE_ID + "=" + IssuePeer.ISSUE_ID;

    private static final String ACT_ATTR_ID = 
        ActivityPeer.ATTRIBUTE_ID.substring(
        ActivityPeer.ATTRIBUTE_ID.indexOf('.')+1);
    private static final String AV_ATTR_ID = 
        AttributeValuePeer.ATTRIBUTE_ID.substring(
        AttributeValuePeer.ATTRIBUTE_ID.indexOf('.')+1);
    private static final String ACTIVITYALIAS_ATTRIBUTE_ID =
        ACTIVITYALIAS + "." + ACT_ATTR_ID;
    private static final String 
        ACTIVITYALIAS_ATTR_ID__EQUALS__USERAVALIAS_ATTR_ID =
        ACTIVITYALIAS_ATTRIBUTE_ID + "=" + USERAVALIAS + "." + AV_ATTR_ID;

    private static final String USERAVALIAS_ISSUE_ID =
        USERAVALIAS + "." + AV_ISSUE_ID;
    private static final String 
        USERAVALIAS_ISSUE_ID__EQUALS__ISSUEPEER_ISSUE_ID =
        USERAVALIAS_ISSUE_ID + "=" + IssuePeer.ISSUE_ID;

    private static final String 
        ACTIVITYALIAS_ISSUE_ID__EQUALS__USERAVALIAS_ISSUE_ID =
        ACTIVITYALIAS_ISSUE_ID + "=" + USERAVALIAS + "." + AV_ISSUE_ID;

    private static final String ACT_NEW_USER_ID = 
        ActivityPeer.NEW_USER_ID.substring(
        ActivityPeer.NEW_USER_ID.indexOf('.')+1);
    private static final String ACTIVITYALIAS_NEW_USER_ID =
        ACTIVITYALIAS + "." + ACT_NEW_USER_ID;
    private static final String 
        ACTIVITYALIAS_NEW_USER_ID__EQUALS__USERAVALIAS_USER_ID =
        ACTIVITYALIAS_NEW_USER_ID + "=" + USERAVALIAS + "." + AV_USER_ID;


    private SimpleDateFormat formatter;

    private String searchWords;
    private String commentQuery;
    private NumberKey[] textScope;
    private String minId;
    private String maxId;
    private String minDate;
    private String maxDate;
    private int minVotes;
    
    private NumberKey stateChangeAttributeId;
    private NumberKey stateChangeFromOptionId;
    private NumberKey stateChangeToOptionId;
    private String stateChangeFromDate;
    private String stateChangeToDate;

    private NumberKey sortAttributeId;
    private String sortPolarity;
    private MITList mitList;
     
    static 
    {

    }

    public IssueSearch(Issue issue)
        throws Exception
    {
        this(issue.getModule(), issue.getIssueType());

        Iterator avs = issue.getAttributeValues().iterator();
        List newAvs = getAttributeValues();
        while (avs.hasNext())
        {
            newAvs.add( ((AttributeValue)avs.next()).copy() );
        }
    }

    public IssueSearch(Module module, IssueType issueType)
        throws Exception
    {
        super(module, issueType);
    }

    public IssueSearch(MITList mitList)
        throws Exception
    {
        super();
        if (mitList == null || mitList.size() == 0) 
        {
            throw new IllegalArgumentException("A non-null list with at" +
               " least one item is required.");
        }
        if (mitList.isSingleModuleIssueType()) 
        {
            MITListItem item = mitList.getFirstItem();
            setModuleId(item.getModuleId());
            setTypeId(item.getIssueTypeId());
        }
        else 
        {
            this.mitList = mitList;   
            if (mitList.isSingleModule()) 
            {
                setModule(mitList.getModule());
            }
            if (mitList.isSingleIssueType()) 
            {
                setIssueType(mitList.getIssueType());
            }
        }        
    }


    public boolean isXMITSearch()
    {
        return mitList != null && !mitList.isSingleModuleIssueType();
    }


    public SequencedHashMap getCommonAttributeValuesMap()
        throws Exception
    {
        SequencedHashMap result = null;
        if (isXMITSearch()) 
        {
            result = getMITAttributeValuesMap();
        }
        else 
        {
            result = super.getModuleAttributeValuesMap();
        }
        return result;
    }


    /**
     * AttributeValues that are relevant to the issue's current module.
     * Empty AttributeValues that are relevant for the module, but have 
     * not been set for the issue are included.  The values are ordered
     * according to the module's preference
     */
    private SequencedHashMap getMITAttributeValuesMap() 
        throws Exception
    {
        SequencedHashMap result = null;

        List attributes = null;
        //HashMap siaValuesMap = null;

        attributes = mitList.getCommonAttributes();
        //siaValuesMap = getAttributeValuesMap();
        if (attributes != null) 
        {
            result = new SequencedHashMap((int)(1.25*attributes.size() + 1));
            Iterator i = attributes.iterator();
            while (i.hasNext()) 
            {
                Attribute attribute = (Attribute)i.next();
                String key = attribute.getName().toUpperCase();
                /*
                  if ( siaValuesMap.containsKey(key) ) 
                  {
                  result.put( key, siaValuesMap.get(key) );
                  }
                  else 
                  {
                */
                AttributeValue aval = AttributeValue
                    .getNewInstance(attribute, this);
                addAttributeValue(aval);
                result.put(key, aval);
                //}
            }
        }
        return result;
    }

    public List getUserAttributes()
        throws Exception
    {
        List result = null;
        if (isXMITSearch()) 
        {
            result = mitList.getCommonUserAttributes();
        }
        else 
        {
            result = getModule().getUserAttributes(getIssueType());
        }
        return result;        
    } 

    public List getLeafRModuleOptions(Attribute attribute)
        throws Exception
    {
        List result = null;
        if (isXMITSearch()) 
        {
            result = mitList.getCommonLeafRModuleOptions(attribute);
        }
        else 
        {
            result = getModule()
                .getLeafRModuleOptions(attribute, getIssueType());
        }
        return result;        
    } 

    public List getCommonOptionTree(Attribute attribute)
        throws Exception
    {
        return mitList.getCommonRModuleOptionTree(attribute);
    }

    /**
     * Get the value of searchWords.
     * @return value of searchWords.
     */
    public String getSearchWords() 
    {
        return searchWords;
    }
    
    /**
     * Set the value of searchWords.
     * @param v  Value to assign to searchWords.
     */
    public void setSearchWords(String  v) 
    {
        this.searchWords = v;
    }

    
    /**
     * Get the value of commentQuery.
     * @return value of commentQuery.
     */
    public String getCommentQuery() 
    {
        return commentQuery;
    }
    
    /**
     * Set the value of commentQuery.
     * @param v  Value to assign to commentQuery.
     */
    public void setCommentQuery(String  v) 
    {
        this.commentQuery = v;
    }
    
    /**
     * Get the value of textScope.  if the scope is not set then all
     * text attributes are returned.  if there are no relevant text
     * attributes null will be returned.
     * @return value of textScope.
     */
    public NumberKey[] getTextScope()
        throws Exception
    {
        if ( textScope == null ) 
        {
            setTextScopeToAll();
        }
        else
        {
            for ( int i=textScope.length-1; i>=0; i-- ) 
            {
                if ( textScope[i].equals(ALL_TEXT) ) 
                {
                    setTextScopeToAll();
                    break;
                }       
            }
        }
        return textScope;
    }


    /**
     * Sets the text search scope to all quick search text attributes.
     */
    private void setTextScopeToAll()
        throws Exception
    {
        List textAttributes = getQuickSearchTextAttributeValues();
        if ( textAttributes != null ) 
        {
            textScope = new NumberKey[textAttributes.size()];
            for ( int j=textAttributes.size()-1; j>=0; j-- ) 
            {
                textScope[j] = ((AttributeValue)
                                textAttributes.get(j)).getAttributeId();
            }
        }
    }

    /**
     * Set the value of textScope.
     * @param v  Value to assign to textScope.
     */
    public void setTextScope(NumberKey[]  v) 
    {
        this.textScope = v;
    }


    /**
     * Get the value of minId.
     * @return value of minId.
     */
    public String getMinId() 
    {
        return minId;
    }
    
    /**
     * Set the value of minId.
     * @param v  Value to assign to minId.
     */
    public void setMinId(String  v) 
    {
        if ( v != null && v.length() == 0 ) 
        {
            this.minId = null;
        }
        else 
        {
            this.minId = v;            
        }
    }

    
    /**
     * Get the value of maxId.
     * @return value of maxId.
     */
    public String getMaxId() 
    {
        return maxId;
    }
    
    /**
     * Set the value of maxId.
     * @param v  Value to assign to maxId.
     */
    public void setMaxId(String  v) 
    {
        if ( v != null && v.length() == 0 ) 
        {
            this.maxId = null;
        }
        else 
        {
            this.maxId = v;
        }
    }
    
    
    /**
     * Get the value of minDate.
     * @return value of minDate.
     */
    public String getMinDate() 
    {
        return minDate;
    }
    
    /**
     * Set the value of minDate.
     * @param v  Value to assign to minDate.
     */
    public void setMinDate(String  v) 
    {
        if ( v != null && v.length() == 0 ) 
        {
            this.minDate = null;
        }
        else 
        {
            this.minDate = v;            
        }
    }

    
    /**
     * Get the value of maxDate.
     * @return value of maxDate.
     */
    public String getMaxDate() 
    {
        return maxDate;
    }
    
    /**
     * Set the value of maxDate.
     * @param v  Value to assign to maxDate.
     */
    public void setMaxDate(String  v) 
    {
        if ( v != null && v.length() == 0 ) 
        {
            this.maxDate = null;
        }
        else 
        {
            this.maxDate = v;            
        }
    }
    
    /**
     * Get the value of minVotes.
     * @return value of minVotes.
     */
    public int getMinVotes() 
    {
        return minVotes;
    }
    
    /**
     * Set the value of minVotes.
     * @param v  Value to assign to minVotes.
     */
    public void setMinVotes(int  v) 
    {
        this.minVotes = v;
    }    
        
    /**
     * Get the value of stateChangeAttributeId.
     * @return value of stateChangeAttributeId.
     */
    public NumberKey getStateChangeAttributeId() 
    {
        if ( stateChangeAttributeId == null ) 
        {
            stateChangeAttributeId = AttributePeer.STATUS__PK;
        }
        
        return stateChangeAttributeId;
    }
    
    /**
     * Set the value of stateChangeAttributeId.
     * @param v  Value to assign to stateChangeAttributeId.
     */
    public void setStateChangeAttributeId(NumberKey  v) 
    {
        this.stateChangeAttributeId = v;
    }
    
    
    /**
     * Get the value of stateChangeFromOptionId.
     * @return value of stateChangeFromOptionId.
     */
    public NumberKey getStateChangeFromOptionId() 
    {
        return stateChangeFromOptionId;
    }
    
    /**
     * Set the value of stateChangeFromOptionId.
     * @param v  Value to assign to stateChangeFromOptionId.
     */
    public void setStateChangeFromOptionId(NumberKey  v) 
    {
        this.stateChangeFromOptionId = v;
    }
    
    /**
     * Get the value of stateChangeToOptionId.
     * @return value of stateChangeToOptionId.
     */
    public NumberKey getStateChangeToOptionId() 
    {
        return stateChangeToOptionId;
    }
    
    /**
     * Set the value of stateChangeToOptionId.
     * @param v  Value to assign to stateChangeToOptionId.
     */
    public void setStateChangeToOptionId(NumberKey  v) 
    {
        this.stateChangeToOptionId = v;
    }

    
    /**
     * Get the value of stateChangeFromDate.
     * @return value of stateChangeFromDate.
     */
    public String getStateChangeFromDate() 
    {
        return stateChangeFromDate;
    }
    
    /**
     * Set the value of stateChangeFromDate.
     * @param v  Value to assign to stateChangeFromDate.
     */
    public void setStateChangeFromDate(String  v) 
    {
        if ( v != null && v.length() == 0 ) 
        {
            this.stateChangeFromDate = null;
        }
        else 
        {
            this.stateChangeFromDate = v;
        }
    }
    
    
    /**
     * Get the value of stateChangeToDate.
     * @return value of stateChangeToDate.
     */
    public String getStateChangeToDate() 
    {
        return stateChangeToDate;
    }
    
    /**
     * Set the value of stateChangeToDate.
     * @param v  Value to assign to stateChangeToDate.
     */
    public void setStateChangeToDate(String  v) 
    {
        if ( v != null && v.length() == 0 ) 
        {
            this.stateChangeToDate = null;
        }
        else 
        {
            this.stateChangeToDate = v;
        }
    }
    
    
    /**
     * Get the value of sortAttributeId.
     * @return value of SortAttributeId.
     */
    public NumberKey getSortAttributeId() 
    {
        return sortAttributeId;
    }
    
    /**
     * Set the value of sortAttributeId.
     * @param v  Value to assign to sortAttributeId.
     */
    public void setSortAttributeId(NumberKey v) 
    {
        this.sortAttributeId = v;
    }
    

    /**
     * Get the value of sortPolarity.
     * @return value of sortPolarity.
     */
    public String getSortPolarity() 
    {
        String polarity = null;
        if ( DESC.equals(sortPolarity) ) 
        {
            polarity = DESC;
        }        
        else 
        {
            polarity = ASC;
        }
        return polarity;
    }
    
    /**
     * Set the value of sortPolarity.
     * @param v  Value to assign to sortPolarity.
     */
    public void setSortPolarity(String  v) 
    {
        this.sortPolarity = v;
    }


    private List userIdList;
    private List userSearchCriteriaList;
    /**
     * Describe <code>addUserSearch</code> method here.
     *
     * @param userId a <code>String</code> represention of the PrimaryKey
     * @param searchCriteria a <code>String</code> either a String 
     * representation of an Attribute PrimaryKey, or the Strings "created_by" 
     * "any"
     */
    public void addUserCriteria(String userId, String searchCriteria)
    {
        if (userId == null) 
        {
            throw new IllegalArgumentException("userId cannot be null.");
        }
        if (searchCriteria == null) 
        {
            searchCriteria = ANY_KEY;
        }

        if (userIdList == null) 
        {
            userIdList = new ArrayList(4);
            userSearchCriteriaList = new ArrayList(4);
        }
        
        userIdList.add(userId);
        userSearchCriteriaList.add(searchCriteria);
    }

    public NumberKey getALL_TEXT()
    {
        return ALL_TEXT;
    }

    public List getQuickSearchTextAttributeValues()
        throws Exception
    {
        return getTextAttributeValues(true);
    }

    public List getTextAttributeValues()
        throws Exception
    {
        return getTextAttributeValues(false);
    }

    private List getTextAttributeValues(boolean quickSearchOnly)
        throws Exception
    {
        SequencedHashMap searchValues = getCommonAttributeValuesMap();
        List searchAttributes = new ArrayList(searchValues.size());

        for ( int i=0; i<searchValues.size(); i++ ) 
        {
            AttributeValue searchValue = 
                (AttributeValue)searchValues.getValue(i);
            if ( (!quickSearchOnly || searchValue.isQuickSearchAttribute())
                 && searchValue.getAttribute().isTextAttribute() ) 
            {
                searchAttributes.add(searchValue);
            }
        }

        return searchAttributes;
    }

    /**
     * Returns OptionAttributes which have been marked for Quick search.
     *
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    public List getQuickSearchOptionAttributeValues()
        throws Exception
    {
        return getOptionAttributeValues(true);
    }

    /**
     * Returns OptionAttributes which have been marked for Quick search.
     *
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    public List getOptionAttributeValues()
        throws Exception
    {
        return getOptionAttributeValues(false);
    }


    /**
     * Returns OptionAttributes which have been marked for Quick search.
     *
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    private List getOptionAttributeValues(boolean quickSearchOnly)
        throws Exception
    {
        SequencedHashMap searchValues = getCommonAttributeValuesMap();
        List searchAttributeValues = new ArrayList(searchValues.size());

        for ( int i=0; i<searchValues.size(); i++ ) 
        {
            AttributeValue searchValue = 
                (AttributeValue)searchValues.getValue(i);
            if ( (!quickSearchOnly || searchValue.isQuickSearchAttribute())
                 && searchValue instanceof OptionAttribute ) 
            {
                searchAttributeValues.add(searchValue);
            }
        }

        return searchAttributeValues;
    }


    /**
     * remove unset AttributeValues.
     *
     * @param attValues a <code>List</code> value
     */
    private void removeUnsetValues(List attValues)
    {
        for ( int i=attValues.size()-1; i>=0; i-- ) 
        {
            AttributeValue attVal = (AttributeValue) attValues.get(i);
            if ( attVal.getOptionId() == null && attVal.getValue() == null
                 && attVal.getUserId() == null ) 
            {
                attValues.remove(i);
            }
        }
    }

    private void addMinimumVotes(Criteria crit)
        throws ScarabException
    {
        if ( minVotes > 0 ) 
        {
            crit.addJoin(AttributeValuePeer.ISSUE_ID, IssuePeer.ISSUE_ID)
                .add(AttributeValuePeer.ATTRIBUTE_ID, 
                     AttributePeer.TOTAL_VOTES__PK)
                .add(AttributeValuePeer.NUMERIC_VALUE, minVotes,
                     Criteria.GREATER_EQUAL);
        }
    }

    private void addIssueIdRange(Criteria crit)
        throws ScarabException, Exception
    {
        // check limits to see which ones are present
        // if neither are present, do nothing
        if ( (minId != null && minId.length() != 0)
              || (maxId != null && maxId.length() != 0) ) 
        {
            Issue.FederatedId minFid = null;
            Issue.FederatedId maxFid = null;
            if ( minId == null || minId.length() == 0 ) 
            {
                maxFid = new Issue.FederatedId(maxId);
                setDefaults(null, maxFid);
                if (maxFid.getDomain() != null) 
                {
                    crit.add(IssuePeer.ID_DOMAIN, maxFid.getDomain());
                }
                if (maxFid.getPrefix() != null) 
                {
                    crit.add(IssuePeer.ID_PREFIX, maxFid.getPrefix());
                }
                crit.add(IssuePeer.ID_COUNT, maxFid.getCount(), 
                         Criteria.LESS_EQUAL);
            }
            else if ( maxId == null || maxId.length() == 0 ) 
            {
                minFid = new Issue.FederatedId(minId);
                setDefaults(minFid, null);
                if (minFid.getDomain() != null) 
                {
                    crit.add(IssuePeer.ID_DOMAIN, minFid.getDomain());
                }
                if (minFid.getPrefix() != null) 
                {
                    crit.add(IssuePeer.ID_PREFIX, minFid.getPrefix());
                }
                crit.add(IssuePeer.ID_COUNT, minFid.getCount(), 
                         Criteria.GREATER_EQUAL);
            }
            else 
            {
                minFid = new Issue.FederatedId(minId);
                maxFid = new Issue.FederatedId(maxId);
                setDefaults(minFid, maxFid);
                
                // make sure min id is less than max id and that the character
                // parts are equal otherwise skip the query, there are no 
                // matches
                if ( minFid.getCount() <= maxFid.getCount() 
                     && StringUtils.equals(minFid.getPrefix(), maxFid.getPrefix())
                     && StringUtils
                     .equals( minFid.getDomain(), maxFid.getDomain() ))
                {
                    Criteria.Criterion c1 = crit.getNewCriterion(
                        IssuePeer.ID_COUNT, new Integer(minFid.getCount()), 
                        Criteria.GREATER_EQUAL);
                    c1.and(crit.getNewCriterion(
                        IssuePeer.ID_COUNT, new Integer(maxFid.getCount()), 
                        Criteria.LESS_EQUAL) );
                    crit.add(c1);
                    if (minFid.getDomain() != null) 
                    {
                        crit.add(IssuePeer.ID_DOMAIN, minFid.getDomain());
                    }
                    if (minFid.getPrefix() != null) 
                    {
                        crit.add(IssuePeer.ID_PREFIX, minFid.getPrefix());
                    }
                }
                else 
                {
                    throw new ScarabException("Incompatible issue Ids: " +
                                              minId + " and " + maxId);
                }
            }
        }
    }


    /**
     * give reasonable defaults if module code was not specified
     */
    private void setDefaults(FederatedId minFid, 
                             FederatedId maxFid)
        throws Exception
    {
        Module module = getModule();
        if (module != null) 
        {
            if ( minFid != null && minFid.getDomain() == null ) 
            {
                minFid.setDomain(module.getDomain());
            }
            if ( maxFid != null && maxFid.getDomain() == null ) 
            {
                maxFid.setDomain(module.getDomain());
            }
            if ( minFid != null && minFid.getPrefix() == null ) 
            {
                minFid.setPrefix(module.getCode());
            }            
        }
        if ( maxFid != null && maxFid.getPrefix() == null ) 
        {
            maxFid.setPrefix(minFid.getPrefix());
        }
    }

    private void addCreatedDateRange(Criteria crit)
        throws ScarabException, Exception
    {
        Date minUtilDate = parseDate(getMinDate(), false);
        Date maxUtilDate = parseDate(getMaxDate(), true);
        if ( minUtilDate != null || maxUtilDate != null ) 
        {
            addDateRange(ActivitySetPeer.CREATED_DATE, 
                         minUtilDate, maxUtilDate, crit);
            crit.addJoin(ActivitySetPeer.TRANSACTION_ID, 
                         ActivityPeer.TRANSACTION_ID);
            crit.addJoin(ActivityPeer.ISSUE_ID, IssuePeer.ISSUE_ID);
            crit.add(ActivitySetPeer.TYPE_ID, 
                     ActivitySetTypePeer.CREATE_ISSUE__PK);
            // there could be multiple attributes modified during the creation
            // which will lead to duplicate issue selection, so we need to 
            // specify only unique issues
            crit.setDistinct();
        }
    }


    /**
     * Attempts to parse a String as a Date given in MM/DD/YYYY form or a
     * Date and Time given in 24 hour clock MM/DD/YYYY HH:mm.  Returns null
     * if the String did not contain a suitable format
     *
     * @param dateString a <code>String</code> value
     * @param addTwentyFourHours if no time is given in the date string and
     * this flag is true, then 24 hours - 1 msec will be added to the date.
     * @return a <code>Date</code> value
     */
    public Date parseDate(String dateString, boolean addTwentyFourHours)
        throws ParseException
    {
        Date date = null;
        if ( dateString != null ) 
        {
            if ( dateString.indexOf(':') == -1 )
            {
                String[] patterns = {"MM/dd/yy", "yyyy-MM-dd"};
                date = parseDate(dateString, patterns);
        
                // one last try with the default locale format
                if ( date == null ) 
                {
                    date = DateFormat.getDateInstance().parse(dateString);
                }

                // add 24 hours to max date so it is inclusive
                if ( addTwentyFourHours ) 
                {                
                    date.setTime(date.getTime() + 86399999);
                }
            }
            else
            {
                String[] patterns = {"MM/dd/yy HH:mm", "yyyy-MM-dd HH:mm"};
                date = parseDate(dateString, patterns);
        
                // one last try with the default locale format
                if ( date == null ) 
                {
                    date = DateFormat.getDateTimeInstance().parse(dateString);
                }
            }
        }
        
        return date;
    }

    /**
     * Attempts to parse a String as a Date given in MM/DD/YYYY form or a
     * Date and Time given in 24 hour clock MM/DD/YYYY HH:mm.  Returns null
     * if the String did not contain a suitable format
     *
     * @param dateString a <code>String</code> value
     * @param addTwentyFourHours if no time is given in the date string and
     * this flag is true, then 24 hours - 1 msec will be added to the date.
     * @return a <code>Date</code> value
     */
    private Date parseDate(String s, String[] patterns)
        throws ParseException
    {
        Date date = null;

        if ( s == null ) 
        {
            throw new ParseException("Input string was null", -1);
        }

        if (formatter == null) 
        {
            formatter = new SimpleDateFormat();
        }
        
        for ( int i=0; i<patterns.length; i++) 
        {
            formatter.applyPattern(patterns[i]);
            try
            {
                date = formatter.parse(s);
            }
            catch (ParseException e)
            {
                // ignore
            }
            if ( date != null ) 
            {
                break;
            }
        }
        return date;
    }


    private void addDateRange(String column, Date minUtilDate,
                              Date maxUtilDate, Criteria crit)
        throws ScarabException
    {
        // check limits to see which ones are present
        // if neither are present, do nothing
        if ( minUtilDate != null || maxUtilDate != null ) 
        {
            if ( minUtilDate == null ) 
            {
                crit.add(column, maxUtilDate, Criteria.LESS_THAN);
            }
            else if ( maxUtilDate == null ) 
            {
                crit.add(column, minUtilDate, Criteria.GREATER_EQUAL);
            }
            else 
            {
                // make sure min id is less than max id and that the character
                // parts are equal otherwise skip the query, there are no 
                // matches
                if ( minUtilDate.before(maxUtilDate) )
                {
                    Criteria.Criterion c1 = crit.getNewCriterion(
                        column, minUtilDate,  Criteria.GREATER_EQUAL);
                    c1.and(crit.getNewCriterion(
                        column, maxUtilDate,  Criteria.LESS_EQUAL) );
                    crit.add(c1);
                }
                else 
                {
                    throw new ScarabException("maxDate " + maxUtilDate + 
                        "is before minDate " + minUtilDate);
                }
            }
        }
    }


    /**
     * Returns a List of matching issues.  if no OptionAttributes were
     * found in the input list, criteria is unaltered.
     *
     * @param attValues a <code>List</code> value
     */
    private void addSelectedAttributes(Criteria crit, List attValues)
        throws Exception
    {
        Criteria.Criterion c = null;
        boolean atLeastOne = false;
        HashMap aliasIndices = new HashMap((int)(attValues.size()*1.25));
        for ( int j=0; j<attValues.size(); j++ ) 
        {
            List chainedValues = ((AttributeValue)attValues.get(j))
                .getValueList();
        for ( int i=0; i<chainedValues.size(); i++ ) 
        {
            //pull any chained values out to create a flat list
            AttributeValue aval = (AttributeValue)chainedValues.get(i);
            if ( aval instanceof OptionAttribute )
            {
                // we will add at least one option attribute to the criteria
                atLeastOne = true;
                Criteria.Criterion c2 = null;
                // check if this is a new attribute or another possible value
                String index = aval.getAttributeId().toString();
                if ( aliasIndices.containsKey(index) ) 
                {
                    // this represents another possible value for an attribute
                    // OR it to the other possibilities
                    Criteria.Criterion prevCrit = 
                        (Criteria.Criterion )aliasIndices.get(index);
                    c2 = buildOptionCriterion(aval);
                    prevCrit.or(c2);
                }
                else
                {
                    Criteria.Criterion c1 = crit.getNewCriterion("av"+index,
                        AV_ISSUE_ID, "av" + index + '.' + AV_ISSUE_ID + '=' + 
                        IssuePeer.ISSUE_ID, Criteria.CUSTOM); 
                    crit.addAlias("av"+index, AttributeValuePeer.TABLE_NAME);
                    c2 = buildOptionCriterion(aval);
                    c1.and(c2);
                    aliasIndices.put(index, c2);
                    if ( c == null ) 
                    {
                        c = c1;
                    }
                    else 
                    {
                        c.and(c1);
                    }
                }
            }
        }
        }
        if ( atLeastOne ) 
        {
            crit.add(c);            
        }
    }

    
    /**
     * This method builds a Criterion for a single attribute value.
     * It is used in the addOptionAttributes method
     *
     * @param aval an <code>AttributeValue</code> value
     * @return a <code>Criteria.Criterion</code> value
     */
    private Criteria.Criterion buildOptionCriterion(AttributeValue aval)
        throws Exception
    {
        Criteria crit = new Criteria();
        Criteria.Criterion criterion = null;        
        String index = aval.getAttributeId().toString();
        List descendants = null;
        // it would be a more correct query to separate the descendant
        // options by module and do something like
        // ... (module_id=1 and option_id in (1,2,3)) OR (module_id=5...
        // but we are not checking which options are active here so i
        // don't think the complexity of the query is needed.  might want
        // to revisit, especially the part about ignoring active setting.
        if (isXMITSearch()) 
        {
            descendants = 
                mitList.getDescendantsUnion(aval.getAttributeOption());
        }
        else 
        {
            IssueType issueType = getIssueType();
            descendants = getModule()
                .getRModuleOption(aval.getAttributeOption(), issueType)
                .getDescendants(issueType);
        }
        
        if ( descendants.size() == 0 ) 
        {
            criterion = crit.getNewCriterion( "av"+index, AV_OPTION_ID,
                aval.getOptionId(), Criteria.EQUAL);
        }
        else
        { 
            NumberKey[] ids = new NumberKey[descendants.size()];
            for ( int j=ids.length-1; j>=0; j-- ) 
            {
                ids[j] = ((AttributeOption)descendants.get(j))
                    .getOptionId();
            }
            criterion = crit.getNewCriterion( "av"+index, AV_OPTION_ID,
                                              ids, Criteria.IN);
        }
        
        return criterion;
    }


    private void addUserCriteria(Criteria crit)
    {
        if (userIdList != null) 
        {
            boolean isAnyUserAV = false;
            boolean isAnyCreatedBy = false;
            Iterator iter = userSearchCriteriaList.iterator();
            while (iter.hasNext())
            {
                String userCriteria = (String)iter.next();
               if (CREATED_BY_KEY.equals(userCriteria)) 
               {
                   isAnyCreatedBy = true;
               }
               else if (ANY_KEY.equals(userCriteria)) 
               {
                   isAnyCreatedBy = true;
                   isAnyUserAV = true;
               }               
               else 
               {
                   isAnyUserAV = true;
               }
            }

            for (int i =0; i<userIdList.size(); i++)
            {
               String userId = (String)userIdList.get(i);
               String attrId = (String)userSearchCriteriaList.get(i);

               addUserCriteria(userId, attrId, isAnyCreatedBy, isAnyUserAV, crit);
            }
        }
    }


    public void addUserCriteria(String userId, String attrId, 
        boolean isAnyCreatedBy, boolean isAnyUserAttr, Criteria crit)
    {
        if (attrId == null)
        {
            attrId = ANY_KEY;
        }

        Criteria.Criterion newCrit = null;
        if (attrId.equals(CREATED_BY_KEY) || attrId.equals(ANY_KEY))
        {
            // Build Criteria for created by
            newCrit = crit.getNewCriterion(
                ACTIVITYSETALIAS, CREATED_BY, userId, Criteria.EQUAL);
            newCrit.and( crit.getNewCriterion(
                ACTIVITYSETALIAS, TYPE_ID, 
                ActivitySetTypePeer.CREATE_ISSUE__PK, Criteria.EQUAL) );
            //addJoin(ActivitySetPeer.TRANSACTION_ID, 
            //        ActivityPeer.TRANSACTION_ID)
            newCrit.and( crit.getNewCriterion(
                ACTIVITYALIAS_TRANSACTION_ID,
                ACTIVITYALIAS_TRAN_ID__EQUALS__ACTIVITYSETALIAS_TRAN_ID, 
                Criteria.CUSTOM) );
            //addJoin(ActivityPeer.ISSUE_ID, IssuePeer.ISSUE_ID)
            newCrit.and( crit.getNewCriterion(
                ACTIVITYALIAS_ISSUE_ID,
                ACTIVITYALIAS_ISSUE_ID__EQUALS__ISSUEPEER_ISSUE_ID,
                Criteria.CUSTOM) );

            if (isAnyUserAttr) 
            {
                // this addition improves timing and reduces dupes
                // AND srchact0.ISSUE_ID=srchuav0.ISSUE_ID
                // AND srchact0.ATTRIBUTE_ID=srchuav0.ATTRIBUTE_ID
                newCrit.and( crit.getNewCriterion(
                    ACTIVITYALIAS_ISSUE_ID,
                    ACTIVITYALIAS_ISSUE_ID__EQUALS__USERAVALIAS_ISSUE_ID,
                    Criteria.CUSTOM) );                
                newCrit.and( crit.getNewCriterion(
                    ACTIVITYALIAS_ATTRIBUTE_ID,
                    ACTIVITYALIAS_ATTR_ID__EQUALS__USERAVALIAS_ATTR_ID, 
                        Criteria.CUSTOM) );  
            }

            crit.addAlias(ACTIVITYALIAS, ActivityPeer.TABLE_NAME);
            crit.addAlias(ACTIVITYSETALIAS, ActivitySetPeer.TABLE_NAME);

            if (attrId.equals(ANY_KEY))
            {
                newCrit.or(getUserCriterion(crit, userId, isAnyCreatedBy));
            }   
        }
        else
        {
            // A user attribute was selected to search on 
            newCrit = getUserCriterion(crit, userId, isAnyCreatedBy);
            newCrit.and( crit.getNewCriterion(
                USERAVALIAS, ATTRIBUTE_ID, attrId, Criteria.EQUAL) );
        }

        Criteria.Criterion firstCrit = crit.getCriterion(
            ACTIVITYSETALIAS, CREATED_BY);
        if (firstCrit == null) 
        {
            firstCrit = 
                crit.getCriterion(USERAVALIAS, USER_ID);
        }
        if (firstCrit == null) 
        {            
                crit.and(newCrit);
        }
        else 
        {
            firstCrit.or(newCrit);
        }            
    }


    private Criteria.Criterion getUserCriterion(Criteria crit, String userId, 
                                               boolean isAnyCreatedBy)
    {
        crit.addAlias(USERAVALIAS, AttributeValuePeer.TABLE_NAME);
        
        // Get results of searching across user attributes
        Criteria.Criterion attrCrit = crit.getNewCriterion(
            USERAVALIAS, USER_ID, userId, Criteria.EQUAL);
        attrCrit.and( crit.getNewCriterion(
            USERAVALIAS, DELETED, Boolean.FALSE, Criteria.EQUAL) );
        //addJoin(AttributeValuePeer.ISSUE_ID, IssuePeer.ISSUE_ID)
        attrCrit.and( crit.getNewCriterion(
            USERAVALIAS_ISSUE_ID,
            USERAVALIAS_ISSUE_ID__EQUALS__ISSUEPEER_ISSUE_ID,
            Criteria.CUSTOM) );
        if (isAnyCreatedBy) 
        {
            // the addition of the following improves timing and reduces dupes
            // AND srchuav0.USER_ID = srchact0.NEW_USER_ID
            // AND srchact0.ISSUE_ID=srchuav0.ISSUE_ID
            // AND srchact0.ATTRIBUTE_ID=srchuav0.ATTRIBUTE_ID
            // AND srchact0.TRANSACTION_ID=srchactset0.TRANSACTION_ID
            attrCrit.and( crit.getNewCriterion( ACTIVITYALIAS_NEW_USER_ID,
                ACTIVITYALIAS_NEW_USER_ID__EQUALS__USERAVALIAS_USER_ID, 
                Criteria.CUSTOM) );
            attrCrit.and( crit.getNewCriterion( ACTIVITYALIAS_ISSUE_ID,
                ACTIVITYALIAS_ISSUE_ID__EQUALS__USERAVALIAS_ISSUE_ID,
                Criteria.CUSTOM) );                
            attrCrit.and( crit.getNewCriterion( ACTIVITYALIAS_ATTRIBUTE_ID,
                ACTIVITYALIAS_ATTR_ID__EQUALS__USERAVALIAS_ATTR_ID,
                Criteria.CUSTOM) );                
            attrCrit.and( crit.getNewCriterion( 
                ACTIVITYALIAS_TRANSACTION_ID,
                ACTIVITYALIAS_TRAN_ID__EQUALS__ACTIVITYSETALIAS_TRAN_ID, 
                Criteria.CUSTOM) );
        }

        return attrCrit;
    }


    private NumberKey[] getTextMatches(List attValues)
        throws Exception
    {
        boolean searchCriteriaExists = false;
        NumberKey[] matchingIssueIds = null;
        SearchIndex searchIndex = SearchFactory.getInstance();
        if (searchIndex == null)
        {
            // Check your configuration.
            throw new Exception("No index available to search");
        }
        if ( getSearchWords() != null && getSearchWords().length() != 0 )
        {
            searchIndex.addQuery(getTextScope(), getSearchWords());
            searchCriteriaExists = true;
        }
        else 
        {
            for ( int i=0; i<attValues.size(); i++ ) 
            {
                AttributeValue aval = (AttributeValue)attValues.get(i);
                if ( aval instanceof StringAttribute 
                     && aval.getValue() != null 
                     && aval.getValue().length() != 0 )
                {
                    searchCriteriaExists = true;
                    NumberKey[] id = {aval.getAttributeId()};
                    searchIndex
                        .addQuery(id, aval.getValue());
                }
            }
        }

        // add comment attachments
        commentQuery = getCommentQuery();
        if (commentQuery != null && commentQuery.trim().length() > 0) 
        {
            NumberKey[] id = {AttachmentTypePeer.COMMENT_PK};
            searchIndex.addAttachmentQuery(id, commentQuery);            
            searchCriteriaExists = true;
        }

        if (searchCriteriaExists) 
        {
            matchingIssueIds = searchIndex.getRelatedIssues();    
        }

        return matchingIssueIds;
    }

    private void addStateChangeQuery(Criteria crit)
        throws Exception
    {
        NumberKey oldOptionId = getStateChangeFromOptionId();
        NumberKey newOptionId = getStateChangeToOptionId();
        if ( oldOptionId != null || newOptionId != null )
        {
            if ( oldOptionId == null ) 
            {
                crit.add(ActivityPeer.NEW_OPTION_ID, newOptionId);
            }
            else if ( newOptionId == null ) 
            {
                crit.add(ActivityPeer.OLD_OPTION_ID, oldOptionId);
            }
            else 
            {
                // make sure the old and new options are different, otherwise
                // do not add to criteria.
                if ( !oldOptionId.equals(newOptionId) )
                {
                    Criteria.Criterion c1 = crit.getNewCriterion(
                        ActivityPeer.OLD_OPTION_ID, oldOptionId,  
                        Criteria.EQUAL);
                    c1.and(crit.getNewCriterion(
                        ActivityPeer.NEW_OPTION_ID, newOptionId, 
                        Criteria.EQUAL) );
                    crit.add(c1);
                }
                else 
                {
                    // might want to log user error here
                }
            }
            //crit.add(ActivityPeer.ATTRIBUTE_ID, getStateChangeAttributeId());
            crit.addJoin(IssuePeer.ISSUE_ID, ActivityPeer.ISSUE_ID);

            // add dates, if given
            Date minUtilDate = parseDate(getStateChangeFromDate(), false);
            Date maxUtilDate = parseDate(getStateChangeToDate(), true);
            if ( minUtilDate != null || maxUtilDate != null ) 
            {
                addDateRange(ActivitySetPeer.CREATED_DATE, 
                             minUtilDate, maxUtilDate, crit);
                crit.addJoin(ActivitySetPeer.TRANSACTION_ID, 
                             ActivityPeer.TRANSACTION_ID);
            }
        }
    }

    private NumberKey[] addCoreSearchCriteria(Criteria crit)
        throws Exception
    {
        if (isXMITSearch()) 
        {
            mitList.addToCriteria(crit);
        }
        else 
        {
            crit.add(IssuePeer.MODULE_ID, getModule().getModuleId());
            crit.add(IssuePeer.TYPE_ID, getIssueType().getIssueTypeId());
        }
        crit.add(IssuePeer.DELETED, false);

        // add option values
        Criteria tempCrit = new Criteria(2)
            .add(AttributeValuePeer.DELETED, false);        
        List attValues = getAttributeValues(tempCrit);

        // remove unset AttributeValues before searching
        removeUnsetValues(attValues);        
        addSelectedAttributes(crit, attValues);

        // search for issues based on text
        NumberKey[] matchingIssueIds = getTextMatches(attValues);

        List sortedIssues = null;
        if ( matchingIssueIds == null || matchingIssueIds.length > 0 ) 
        {            
            addIssueIdRange(crit);
            addCreatedDateRange(crit);
            addMinimumVotes(crit);

            // add user values
            addUserCriteria(crit);

            // add text search matches
            addIssuePKsCriteria(crit, matchingIssueIds);

            // state change query
            addStateChangeQuery(crit);
        }
        return matchingIssueIds;
    }

    private void addIssuePKsCriteria(Criteria crit, NumberKey[] ids)
    {
       if (ids != null && ids.length > 0)
       {
           crit.add(IssuePeer.ISSUE_ID, ids, Criteria.IN);
       }     
    }

    /**
     * Get a List of Issues that match the criteria given by this
     * SearchIssue's searchWords and the quick search attribute values.
     *
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    public List getMatchingIssues()
        throws Exception
    {
        Criteria crit = new Criteria();
        NumberKey[] matchingIssueIds = addCoreSearchCriteria(crit);
        List sortedIssues = null;
        // the matchingIssueIds are text search matches.  if length == 0,
        // then no need to search further.  if null then there was no
        // text to search, so continue the search process.
        if ( matchingIssueIds == null || matchingIssueIds.length > 0 ) 
        {            
            // Get matching issues, with sort criteria
            sortedIssues = sortIssues(crit);
        }
        else 
        {
            sortedIssues = new ArrayList(0);
        }

        // Return list as issue ids
        List sortedIssueIds = new ArrayList();
        for (int i=0; i<sortedIssues.size(); i++)
        {
            sortedIssueIds.add(((Issue)sortedIssues.get(i)).getUniqueId());
        }
        return sortedIssueIds;
    }

    public int getIssueCount()
        throws Exception
    {
        int count = 0;
        Criteria crit = new Criteria();
        NumberKey[] matchingIssueIds = addCoreSearchCriteria(crit);
        if ( matchingIssueIds == null || matchingIssueIds.length > 0 ) 
        {
            crit.addSelectColumn("count(DISTINCT " + IssuePeer.ISSUE_ID + ')');
            List records = IssuePeer.doSelectVillageRecords(crit);
            count = ((Record)records.get(0)).getValue(1).asInt();
        }

        return count;
    }

    private List sortIssues(Criteria crit)
        throws Exception
    {
        List matchingIssues = null;
        if (getSortAttributeId() == null)
        {
            //sort by unique id
            matchingIssues = sortByUniqueId(crit);
        }
        else
        {
            //sort by unique id
            matchingIssues = sortByAttribute(crit);
        }
        return matchingIssues;
    }

    /**
     * Sorts on issue unique id (default)
     */
    private List sortByUniqueId(Criteria crit) throws Exception
    {
        if (getSortPolarity().equals("desc"))
        {
            crit.addDescendingOrderByColumn(IssuePeer.ID_COUNT);
        } 
        else
        {
            crit.addAscendingOrderByColumn(IssuePeer.ID_COUNT);
        }
        crit.setDistinct();
        return IssuePeer.doSelect(crit);
    }

    /**
     * Sorts on issue attribute selected by user
     */
    private List sortByAttribute(Criteria crit) throws Exception
    {
        Vector attSet = new Vector();
        Vector attNotSet = new Vector();
        List unSortedIssues = IssuePeer.doSelect(crit);
        List sortedIssues = new ArrayList(unSortedIssues.size());
        NumberKey sortAttrId = getSortAttributeId();
        Attribute att = AttributeManager.getInstance(sortAttrId);

        for (int j=0; j<unSortedIssues.size(); j++)
        {
            Issue issue =  (Issue)unSortedIssues.get(j);
            AttributeValue sortAttVal = (AttributeValue)issue
               .getModuleAttributeValuesMap()
               .get(att.getName().toUpperCase());
            Object sortValue = null;
            if ( sortAttVal instanceof OptionAttribute)
            {
                sortValue = sortAttVal.getAttributeOption();
            }
            else 
            {
                sortValue = sortAttVal.getValue();
            }
            if (sortValue == null)
            {
                attNotSet.add(issue);
            }
            else
            {
                attSet.add(issue.getIssueId());
            }
        } 
        if (attSet.size() > 0)
        {
            String sortColumn = null;  
            Criteria crit2 = new Criteria();
            if ( att.isOptionAttribute())
            {
                crit2.addIn(AttributeValuePeer.ISSUE_ID, attSet);
                crit2.add(AttributeOptionPeer.ATTRIBUTE_ID, sortAttrId);
                crit2.addJoin(AttributeOptionPeer.OPTION_ID,
                              RModuleOptionPeer.OPTION_ID);
                crit2.addJoin(AttributeValuePeer.OPTION_ID,
                              RModuleOptionPeer.OPTION_ID);
                crit2.addJoin(AttributeValuePeer.ISSUE_ID,
                              IssuePeer.ISSUE_ID);
                crit2.addJoin(IssuePeer.MODULE_ID, 
                              RModuleOptionPeer.MODULE_ID);
                crit2.addJoin(IssuePeer.TYPE_ID, 
                              RModuleOptionPeer.ISSUE_TYPE_ID);
                sortColumn = RModuleOptionPeer.WEIGHT;
                crit2.setDistinct();
            }
            else
            {
                crit2.addIn(AttributeValuePeer.ISSUE_ID, attSet);
                crit2.add(AttributeValuePeer.ATTRIBUTE_ID, sortAttrId);
                crit2.addJoin(AttributeValuePeer.ISSUE_ID,
                              IssuePeer.ISSUE_ID);
                crit2.setDistinct();
                sortColumn = AttributeValuePeer.VALUE; 
                }
                if (getSortPolarity().equals("desc"))
                {
                    crit2.addDescendingOrderByColumn(sortColumn);
                }
                else
                {
                    crit2.addAscendingOrderByColumn(sortColumn);
                }
                sortedIssues.addAll(IssuePeer.doSelect(crit2));
           }
           sortedIssues.addAll(attNotSet);
           return sortedIssues;
    }
}