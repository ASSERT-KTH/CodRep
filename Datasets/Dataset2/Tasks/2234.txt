Map siaValuesMap = getAttributeValuesMap();

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
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.Iterator;
import java.util.Vector;
import java.util.ArrayList;
import java.util.Date;
import java.util.Collections;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.text.ParseException;

import com.workingdogs.village.Record;
import org.apache.torque.Torque;
import org.apache.torque.adapter.DB;
import org.apache.torque.om.NumberKey;
import org.apache.torque.om.ComboKey;
import org.apache.torque.om.ObjectKey;
import org.apache.torque.util.Criteria;
import org.apache.torque.util.BasePeer;
import org.apache.torque.TorqueException;
import org.apache.commons.collections.SequencedHashMap;
import org.apache.commons.collections.LRUMap;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.lang.ObjectUtils;
import org.apache.log4j.Logger;

// Scarab classes
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.AttributeManager;
import org.tigris.scarab.om.AttributeOptionPeer;
import org.tigris.scarab.om.AttachmentTypePeer;
import org.tigris.scarab.om.Issue;
import org.tigris.scarab.om.IssueType;
import org.tigris.scarab.om.IssuePeer;
import org.tigris.scarab.om.AttributeValuePeer;
import org.tigris.scarab.om.AttributeValue;
import org.tigris.scarab.om.AttributePeer;
import org.tigris.scarab.om.ActivityPeer;
import org.tigris.scarab.om.ActivitySetPeer;
import org.tigris.scarab.om.ActivitySetTypePeer;
import org.tigris.scarab.om.RModuleOptionPeer;
import org.tigris.scarab.om.RModuleOption;
import org.tigris.scarab.om.RModuleIssueType;
import org.tigris.scarab.om.RModuleIssueTypeManager;
import org.tigris.scarab.om.Module;
import org.tigris.scarab.om.ModuleManager;
import org.tigris.scarab.om.MITList;
import org.tigris.scarab.om.MITListItem;
import org.tigris.scarab.om.RModuleUserAttribute;

import org.tigris.scarab.util.ScarabException;
import org.tigris.scarab.attribute.OptionAttribute;
import org.tigris.scarab.attribute.StringAttribute;
import org.tigris.scarab.util.Log;


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
    private static final String CREATED_DATE = "CREATED_DATE";
    private static final String TYPE_ID = "TYPE_ID";
    private static final String ATTRIBUTE_ID = "ATTRIBUTE_ID";
    private static final String USER_ID = "USER_ID";
    private static final String DELETED = "DELETED";
    private static final String AND = " AND ";
    private static final String OR = " OR ";
    private static final String INNER_JOIN = " INNER JOIN ";
    private static final String ON = " ON (";
    private static final String IN = " IN (";
    private static final String IS_NULL = " IS NULL";

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
    private static final String END_DATE = 
        ActivityPeer.END_DATE.substring(
        ActivityPeer.END_DATE.indexOf('.')+1);

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

    private static String WHERE = " WHERE ";
    private static String FROM = " FROM ";
    private static String ORDER_BY = " ORDER BY ";
    private static String BASE_OPTION_SORT_LEFT_JOIN = 
        " LEFT OUTER JOIN SCARAB_R_MODULE_OPTION sortRMO ON " + 
        "(SCARAB_ISSUE.MODULE_ID=sortRMO.MODULE_ID AND SCARAB_ISSUE.TYPE_ID=" +
        "sortRMO.ISSUE_TYPE_ID AND sortRMO.OPTION_ID=";

    private static int NO_ATTRIBUTE_SORT = -1;

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

    private List userIdList;
    private List userSearchCriteriaList;
    private List lastUsedAVList;
    private boolean modified;

    private int lastTotalIssueCount = -1;
    private List lastMatchingIssueIds = null;
    private List lastQueryResults = null;

    // the attribute columns that will be shown
    private List issueListAttributeColumns;

    // used to cache a few modules and issuetypes to make listing
    // a result set faster.
    private LRUMap moduleMap = new LRUMap(20);
    private LRUMap rmitMap = new LRUMap(20);
    
     
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

    /**
     * List of attributes to show with each issue.
     *
     * @param rmuas a <code>List</code> of RModuleUserAttribute objects
     */
    public void setIssueListAttributeColumns(List rmuas)
    {
        //FIXME! implement logic to determine if a new search is required.
        issueListAttributeColumns = rmuas;
    }

    public List getIssueListAttributeColumns()
    {
        return issueListAttributeColumns;
    }

    public List getUserIdList()
    {
        return userIdList;
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

        List attributes = mitList.getCommonAttributes();
        HashMap siaValuesMap = getAttributeValuesMap();
        if (attributes != null) 
        {
            result = new SequencedHashMap((int)(1.25*attributes.size() + 1));
            Iterator i = attributes.iterator();
            while (i.hasNext()) 
            {
                Attribute attribute = (Attribute)i.next();
                String key = attribute.getName().toUpperCase();
                if ( siaValuesMap.containsKey(key) ) 
                {
                    result.put( key, siaValuesMap.get(key) );
                }
                else 
                {
                    AttributeValue aval = AttributeValue
                        .getNewInstance(attribute, this);
                    addAttributeValue(aval);
                    result.put(key, aval);
                }
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
        if (!ObjectUtils.equals(v, this.searchWords)) 
        {
            modified = true;
            this.searchWords = v;
        }
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
        if (!ObjectUtils.equals(v, this.commentQuery)) 
        {
            modified = true;
            this.commentQuery = v;
        }
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
            textScope = getTextScopeForAll();
        }
        else
        {
            for ( int i=textScope.length-1; i>=0; i-- ) 
            {
                if ( textScope[i].equals(ALL_TEXT) ) 
                {
                    textScope = getTextScopeForAll();
                    break;
                }       
            }
        }
        return textScope;
    }


    /**
     * Sets the text search scope to all quick search text attributes.
     */
    private NumberKey[] getTextScopeForAll()
        throws Exception
    {
        NumberKey[] textScope = null;
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
        return textScope;
    }

    /**
     * Set the value of textScope.
     * @param v  Value to assign to textScope.
     */
    public void setTextScope(NumberKey[]  v) 
        throws Exception
    {
        if (v != null) 
        {
            for ( int i=v.length-1; i>=0; i-- ) 
            {
                if ( v[i].equals(ALL_TEXT) ) 
                {
                    v = getTextScopeForAll();
                    break;
                }       
            }
        }

        // note previous block may have made v == null though its not likely
        // (don't replace the if with an else)
        if (v == null) 
        {
            modified |= this.textScope != null;
            this.textScope = null;
        }
        else if (this.textScope != null && this.textScope.length == v.length)
        {
            for ( int i=v.length-1; i>=0; i-- ) 
            {
                if ( !v[i].equals(this.textScope[i]) ) 
                {
                    modified = true;
                    this.textScope = v;            
                    break;
                }       
            }
        }
        else 
        {
            modified = true;
            this.textScope = v;            
        }
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
            v = null;
        }
        if (!ObjectUtils.equals(v, this.minId)) 
        {
            modified = true;
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
            v = null;
        }
        if (!ObjectUtils.equals(v, this.maxId)) 
        {
            modified = true;
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
            v = null;
        }
        if (!ObjectUtils.equals(v, this.minDate)) 
        {
            modified = true;
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
            v = null;
        }
        if (!ObjectUtils.equals(v, this.maxDate)) 
        {
            modified = true;
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
        if (v != this.minVotes) 
        {
            modified = true;
            this.minVotes = v;
        }
    }    


    /**
     * Get the value of stateChangeAttributeId.
     * @return value of stateChangeAttributeId.
     */
    public NumberKey getStateChangeAttributeId() 
    {
        if ( stateChangeAttributeId == null ) 
        {
            return AttributePeer.STATUS__PK;
        }
        return stateChangeAttributeId;
    }
    
    /**
     * Set the value of stateChangeAttributeId.
     * @param v  Value to assign to stateChangeAttributeId.
     */
    public void setStateChangeAttributeId(NumberKey  v) 
    {
        if (!ObjectUtils.equals(v, this.stateChangeAttributeId)) 
        {
            modified = true;
            this.stateChangeAttributeId = v;
        }
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
        if (!ObjectUtils.equals(v, this.stateChangeFromOptionId)) 
        {
            modified = true;
            this.stateChangeFromOptionId = v;
        }
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
        if (!ObjectUtils.equals(v, this.stateChangeToOptionId)) 
        {
            modified = true;
            this.stateChangeToOptionId = v;
        }
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
            v = null;
        }
        if (!ObjectUtils.equals(v, this.stateChangeFromDate)) 
        {
            modified = true;
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
            v = null;
        }
        if (!ObjectUtils.equals(v, this.stateChangeToDate)) 
        {
            modified = true;
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
        if (!ObjectUtils.equals(v, this.sortAttributeId)) 
        {
            modified = true;
            this.sortAttributeId = v;
        }
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
        if (!ObjectUtils.equals(v, this.sortPolarity)) 
        {
            modified = true;
            this.sortPolarity = v;
        }
    }

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
        boolean newCriteria = true;
        for (int i=userIdList.size()-1; i>=0; i--) 
        {
            if (userId.equals(userIdList.get(i)) &&
                searchCriteria.equals(userSearchCriteriaList.get(i))) 
            {
                newCriteria = false;
                break;
            }
        }
        
        if (newCriteria) 
        {
            modified = true;
            userIdList.add(userId);
            userSearchCriteriaList.add(searchCriteria);            
        }
    }

    private boolean isAVListModified()
        throws TorqueException
    {
        boolean result = false;
        if (lastUsedAVList == null) 
        {
            result = true;
        }
        else 
        {
            List avList = getAttributeValues();
            int max = avList.size();
            if (lastUsedAVList.size() == max) 
            {
                for (int i=0; i<max; i++) 
                {
                    AttributeValue a1 = (AttributeValue)avList.get(i);
                    AttributeValue a2 = (AttributeValue)lastUsedAVList.get(i);
                    if ( !ObjectUtils.equals(a1.getOptionId(), a2.getOptionId())
                         || !ObjectUtils.equals(a1.getUserId(), a2.getUserId())
                         //|| a1.getNumericValue() != a2.getNumericValue()
                         || !ObjectUtils.equals(a1.getValue(), a2.getValue()))
                    {
                        result = true;
                    }
                }
            }
            else 
            {
                result = true;
            }
        }        
        return result;
    }

    /**
     * 
     *
     * @return a <code>boolean</code> value
     */
    private void checkModified()
        throws TorqueException
    {
        if (modified || isAVListModified()) 
        {
            modified = false;
            lastTotalIssueCount = -1;
            lastMatchingIssueIds = null;
            lastQueryResults = null;
        }
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
    private List removeUnsetValues(List attValues)
    {
        int size = attValues.size();
        List setAVs = new ArrayList(size);
        for ( int i=0; i<size; i++ ) 
        {
            AttributeValue attVal = (AttributeValue) attValues.get(i);
            if ( attVal.getOptionId() != null || attVal.getValue() != null
                 || attVal.getUserId() != null ) 
            {
                setAVs.add(attVal);
            }
        }
        return setAVs;
    }

    private void addMinimumVotes(Criteria crit)
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

    private void addAnd(StringBuffer sb)
    {
        if (sb.length() > 0) 
        {
            sb.append(AND);
        }
    }

    private void addIssueIdRange(StringBuffer where)
        throws ScarabException, Exception
    {
        // check limits to see which ones are present
        // if neither are present, do nothing
        if ( (minId != null && minId.length() != 0)
              || (maxId != null && maxId.length() != 0) ) 
        {
            StringBuffer sb = new StringBuffer();
            String domain = null;
            String prefix = null;
            Issue.FederatedId minFid = null;
            Issue.FederatedId maxFid = null;
            if ( minId == null || minId.length() == 0 ) 
            {
                maxFid = new Issue.FederatedId(maxId);
                setDefaults(null, maxFid);
                addAnd(sb);
                sb.append(IssuePeer.ID_COUNT).append("<=")
                    .append(maxFid.getCount());
                domain = maxFid.getDomain();
                prefix = maxFid.getPrefix();
            }
            else if ( maxId == null || maxId.length() == 0 ) 
            {
                minFid = new Issue.FederatedId(minId);
                setDefaults(minFid, null);
                addAnd(sb);
                sb.append(IssuePeer.ID_COUNT).append(">=")
                    .append(minFid.getCount());
                domain = minFid.getDomain();
                prefix = minFid.getPrefix();
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
                    addAnd(sb);
                    sb.append(IssuePeer.ID_COUNT).append(">=")
                        .append(minFid.getCount()).append(AND)
                        .append(IssuePeer.ID_COUNT).append("<=")
                        .append(maxFid.getCount());
                    domain = minFid.getDomain();
                    prefix = minFid.getPrefix();
                }
                else 
                {
                    throw new ScarabException("Incompatible issue Ids: " +
                                              minId + " and " + maxId);
                }
            }
            if (domain != null) 
            {
                sb.append(AND).append(IssuePeer.ID_DOMAIN).append("='")
                    .append(domain).append('\'');
            }
            if (prefix != null) 
            {
                sb.append(AND).append(IssuePeer.ID_PREFIX).append("='")
                    .append(prefix).append('\'');
            }
            where.append(AND).append(sb);
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
            if (minFid == null) 
            {
                maxFid.setPrefix(module.getCode());                
            }
            else 
            {
                maxFid.setPrefix(minFid.getPrefix());        
            }
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
     * @param s a <code>String</code> value
     * @param patterns if no time is given in the date string and
     * this flag is true, then 24 hours - 1 msec will be added to the date.
     * @return a <code>Date</code> value
     * @throws ParseException if input String is null
     */
    private Date parseDate(String s, String[] patterns)
        throws ParseException
    {
        /* FIXME: the contract for this method is strange
           it is returning a null value when encountering a ParseException,
           and throwing a ParseException when having a wrong input*/
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
                              Date maxUtilDate, StringBuffer sb)
        throws Exception
    {
        // check limits to see which ones are present
        // if neither are present, do nothing
        if ( minUtilDate != null || maxUtilDate != null ) 
        {
            DB adapter = Torque.getDB(Torque.getDefaultDB());
            if ( minUtilDate == null ) 
            {
                sb.append(column).append('<')
                    .append(adapter.getDateString(maxUtilDate));
            }
            else if ( maxUtilDate == null ) 
            {
                sb.append(column).append(">=")
                    .append(adapter.getDateString(minUtilDate));
            }
            else 
            {
                // make sure min id is less than max id and that the character
                // parts are equal otherwise skip the query, there are no 
                // matches
                if ( minUtilDate.before(maxUtilDate) )
                {
                    sb.append(column).append(">=")
                        .append(adapter.getDateString(minUtilDate));
                    sb.append(AND);
                    sb.append(column).append('<')
                        .append(adapter.getDateString(maxUtilDate));
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
    private void addSelectedAttributes(StringBuffer fromClause,  
                                       List attValues)
        throws Exception
    {
        Map attrMap = new HashMap((int)(attValues.size()*1.25));
        for ( int j=0; j<attValues.size(); j++ ) 
        {
            AttributeValue multiAV = (AttributeValue)attValues.get(j);
            if ( multiAV instanceof OptionAttribute )
            {
                NumberKey index = multiAV.getAttributeId();
                List options = (List)attrMap.get(index);
                if (options == null) 
                {
                    options = new ArrayList();
                    attrMap.put(index, options);
                }
                
                //pull any chained values out to create a flat list
                List chainedValues = multiAV.getValueList();
                for ( int i=0; i<chainedValues.size(); i++ ) 
                {
                    AttributeValue aval = (AttributeValue)chainedValues.get(i);
                    buildOptionList(options, aval);
                }
            }
        }

        for (Iterator i=attrMap.entrySet().iterator(); i.hasNext();) 
        {
            Map.Entry entry = (Map.Entry)i.next();
            String alias = "av" + entry.getKey();
            List options = (List)entry.getValue();
            String c2 = null;
            if ( options.size() == 1 ) 
            {
                c2 = alias + '.' + AV_OPTION_ID + '=' 
                    + options.get(0);
            }
            else
            { 
                c2 = alias + '.' + AV_OPTION_ID + " IN ("
                    + StringUtils.join(options.iterator(), ",") + ')';
            }
        
            String joinClause = " INNER JOIN " + AttributeValuePeer.TABLE_NAME
                + ' ' + alias + " ON (" + 
                alias + '.' + AV_ISSUE_ID + '=' + IssuePeer.ISSUE_ID + 
                AND + c2 + AND + 
                alias + '.' + "DELETED=0" + ')';
            // might want to add redundant av2.ISSUE_ID=av5.ISSUE_ID. might
            // not be necessary with sql92 join format?
            fromClause.append(joinClause);
        }
    }


    /**
     * This method builds a Criterion for a single attribute value.
     * It is used in the addOptionAttributes method
     *
     * @param aval an <code>AttributeValue</code> value
     * @return a <code>Criteria.Criterion</code> value
     */
    private void buildOptionList(List options, AttributeValue aval)
        throws Exception
    {
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
            options.add(aval.getOptionId());
        }
        else
        { 
            for (Iterator i=descendants.iterator(); i.hasNext();) 
            {
                options.add( ((RModuleOption)i.next())
                    .getOptionId() );
            }
        }
    }

    private void addUserAndCreatedDateCriteria(StringBuffer from, 
                                               StringBuffer where)
        throws Exception
    {
        String dateRangeSql = null;
        if (getMinDate() != null || getMaxDate() != null) 
        {
            StringBuffer sbdate = new StringBuffer();
            Date minUtilDate = parseDate(getMinDate(), false);
            Date maxUtilDate = parseDate(getMaxDate(), true);
            addDateRange(ACTIVITYSETALIAS + '.' + CREATED_DATE, 
                         minUtilDate, maxUtilDate, sbdate);
            dateRangeSql = sbdate.toString(); 
        }                
        
        if (userIdList == null)
        {
            if (dateRangeSql != null) 
            {
                // just dates
                from.append(INNER_JOIN + ActivityPeer.TABLE_NAME + ' ' +
                    ACTIVITYALIAS + " ON ("
                    + ACTIVITYALIAS_ISSUE_ID__EQUALS__ISSUEPEER_ISSUE_ID)
                    .append(')' + INNER_JOIN + ActivitySetPeer.TABLE_NAME + 
                    ' ' + ACTIVITYSETALIAS + " ON (" +
                    ACTIVITYALIAS_TRAN_ID__EQUALS__ACTIVITYSETALIAS_TRAN_ID
                    + AND + ACTIVITYSETALIAS + '.' + TYPE_ID + '=' +
                    ActivitySetTypePeer.CREATE_ISSUE__PK)
                    .append(AND).append(dateRangeSql)
                    .append(')');
            }
        }
        else
        {
            List anyUsers = null;
            List creatorUsers = null;
            Map attrUsers = null;
            List attrUserAttrs = null;
            int maxUsers = userIdList.size();
            for (int i =0; i<maxUsers; i++)
            {
                String userId = (String)userIdList.get(i);
                String attrId = (String)userSearchCriteriaList.get(i);
                if (attrId == null || ANY_KEY.equals(attrId)) 
                {
                    if (anyUsers == null) 
                    {
                        anyUsers = new ArrayList(maxUsers);
                    }
                    anyUsers.add(userId);
                }               
                else if (CREATED_BY_KEY.equals(attrId)) 
                {
                    if (creatorUsers == null) 
                    {
                        creatorUsers = new ArrayList(maxUsers);
                    }
                    creatorUsers.add(userId);
                }
                else 
                {
                    // using a map here seems like overkill, but it
                    // makes the logic easier
                    if (attrUsers == null) 
                    {
                        attrUsers = new HashMap(maxUsers);
                    }
                    List userIds = (List)attrUsers.get(attrId);
                    if (userIds == null) 
                    {
                        userIds = new ArrayList(maxUsers);
                        attrUsers.put(attrId, userIds);
                    }
                    userIds.add(userId);
                }
            }

            String fromClause = INNER_JOIN + ActivityPeer.TABLE_NAME + ' ' +
                ACTIVITYALIAS + " ON ("
                + ACTIVITYALIAS_ISSUE_ID__EQUALS__ISSUEPEER_ISSUE_ID;

            StringBuffer attrCrit = null;
            if (anyUsers != null) 
            {
                attrCrit = new StringBuffer();
                attrCrit.append('(');
                addUserActivityFragment(attrCrit, anyUsers);
                attrCrit.append(')');
            }
            
            if (attrUsers != null) 
            {
                for (Iterator i = attrUsers.entrySet().iterator(); i.hasNext();)
                {
                    if (attrCrit == null) 
                    {
                        attrCrit = new StringBuffer();
                    }
                    else 
                    {
                        attrCrit.append(OR);
                    }
                
                    Map.Entry entry = (Map.Entry)i.next();
                    String attrId = (String)entry.getKey();
                    List userIds = (List)entry.getValue();
                    attrCrit.append('(');
                    addUserActivityFragment(attrCrit, userIds);
                    attrCrit.append( AND +
                        ACTIVITYALIAS + '.' + ATTRIBUTE_ID + '=' + attrId );
                    attrCrit.append(')');
                }
            }

            boolean isAddActivitySet = anyUsers != null || creatorUsers != null
                || dateRangeSql != null;
            String whereClause = null;
            if (isAddActivitySet)
            {
                if (attrCrit != null) 
                {
                    whereClause = '(' + attrCrit.toString() + ')';
                }

                fromClause += ')' + INNER_JOIN + ActivitySetPeer.TABLE_NAME + 
                    ' ' + ACTIVITYSETALIAS + " ON (" +
                    ACTIVITYALIAS_TRAN_ID__EQUALS__ACTIVITYSETALIAS_TRAN_ID;
 
                if (anyUsers != null || creatorUsers != null)
                {
                    List anyAndCreators = new ArrayList(maxUsers);
                    if (anyUsers != null) 
                    {
                        anyAndCreators.addAll(anyUsers);
                    }
                    if (creatorUsers != null) 
                    {
                        anyAndCreators.addAll(creatorUsers);
                    }
                
                    // we can add this to the join condition, if created-only
                    // query otherwise it needs to go in the where clause
                    String createdBySqlFragment = 
                        ACTIVITYSETALIAS + '.' + TYPE_ID + '=' +
                        ActivitySetTypePeer.CREATE_ISSUE__PK + AND +
                        ACTIVITYSETALIAS + '.' + CREATED_BY;
                    if (anyAndCreators.size() == 1) 
                    {
                        createdBySqlFragment += 
                            '=' + anyAndCreators.get(0).toString();
                    }
                    else 
                    {
                        createdBySqlFragment += IN + 
                            StringUtils.join(anyAndCreators.iterator(), ",") 
                            + ')';
                    }
                
                    if (anyUsers != null || attrUsers != null) 
                    {
                        fromClause += ')'; 
                        whereClause = '(' + whereClause + OR + 
                            createdBySqlFragment + ')';
                        if (dateRangeSql != null) 
                        {
                            System.out.println("Date range: " + dateRangeSql);
                            whereClause += AND + dateRangeSql;
                        }
                    }
                    else 
                    {
                        fromClause += AND + createdBySqlFragment;
                        if (dateRangeSql != null) 
                        {
                            fromClause += AND + dateRangeSql;
                        }
                        fromClause += ')'; 
                    }
                }
                else // dateRangeSql will not be null
                {
                    fromClause += ACTIVITYSETALIAS + '.' + TYPE_ID + '=' +
                        ActivitySetTypePeer.CREATE_ISSUE__PK
                        + AND + dateRangeSql + ')'; 
                }                
            }
            else
            {
                if (attrCrit == null) 
                {
                    fromClause += ')';
                }
                else 
                {
                    fromClause += AND + '(' + attrCrit + "))";
                }
            }

            from.append(fromClause);
            if (whereClause != null) 
            {
                where.append(AND).append(whereClause);
            }
        }
    }

    private void addUserActivityFragment(StringBuffer sb, List userIds)
    {
        sb.append(ACTIVITYALIAS + '.' + END_DATE + 
                  IS_NULL + AND + ACTIVITYALIAS_NEW_USER_ID );
        if (userIds.size() == 1) 
        {
            sb.append('=').append(userIds.get(0));
        }
        else 
        {
            sb.append( IN + 
                       StringUtils.join(userIds.iterator(), ",") + ')' );
        }
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
        String commentQuery = getCommentQuery();
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

    private void addStateChangeQuery(StringBuffer from)
        throws Exception
    {
        NumberKey oldOptionId = getStateChangeFromOptionId();
        NumberKey newOptionId = getStateChangeToOptionId();
        if ( oldOptionId != null || newOptionId != null )
        {
            from.append(INNER_JOIN + ActivityPeer.TABLE_NAME + ON +
                        ActivityPeer.ISSUE_ID + '=' + IssuePeer.ISSUE_ID);

            if ( oldOptionId == null ) 
            {
                from.append(AND).append(ActivityPeer.NEW_OPTION_ID).append('=')
                    .append(newOptionId);
            }
            else if ( newOptionId == null ) 
            {
                from.append(AND).append(ActivityPeer.OLD_OPTION_ID).append('=')
                    .append(oldOptionId);
            }
            // make sure the old and new options are different, otherwise
            // do not add to criteria.
            else if ( !oldOptionId.equals(newOptionId) )
            {
                from.append(AND).append(ActivityPeer.NEW_OPTION_ID)
                    .append('=').append(newOptionId);
                from.append(AND).append(ActivityPeer.OLD_OPTION_ID)
                    .append('=').append(oldOptionId);
            }
            else 
            {
                // might want to log user error here
            }
            from.append(')');

            // add dates, if given
            Date minUtilDate = parseDate(getStateChangeFromDate(), false);
            Date maxUtilDate = parseDate(getStateChangeToDate(), true);
            if ( minUtilDate != null || maxUtilDate != null ) 
            {
                from.append( INNER_JOIN + ActivitySetPeer.TABLE_NAME + ON +
                             ActivitySetPeer.TRANSACTION_ID + '=' +
                             ActivityPeer.TRANSACTION_ID);
                from.append(AND);

                addDateRange(ActivitySetPeer.CREATED_DATE, 
                             minUtilDate, maxUtilDate, from);
                
                from.append(')');
            }
        }
    }

    private NumberKey[] addCoreSearchCriteria(StringBuffer fromClause, 
                                              StringBuffer whereClause)
        throws Exception
    {
        if (isXMITSearch()) 
        {
            Criteria crit = new Criteria();
            mitList.addToCriteria(crit);
            String sql = crit.toString();
            int wherePos = sql.indexOf(" WHERE ");
            whereClause.append(sql.substring(wherePos + 7));
        }
        else 
        {
            whereClause.append(IssuePeer.MODULE_ID).append('=')
                .append(getModule().getModuleId());
            whereClause.append(AND).append(IssuePeer.TYPE_ID).append('=')
                .append(getIssueType().getIssueTypeId());
        }
        whereClause.append(AND).append(IssuePeer.DELETED).append("=0");

        // add option values
        lastUsedAVList = getAttributeValues();

        // remove unset AttributeValues before searching
        List setAttValues = removeUnsetValues(lastUsedAVList);        
        addSelectedAttributes(fromClause, setAttValues);

        // search for issues based on text
        NumberKey[] matchingIssueIds = getTextMatches(setAttValues);

        if ( matchingIssueIds == null || matchingIssueIds.length > 0 )
        {
            addIssueIdRange(whereClause);
            //addMinimumVotes(whereClause);

            // add user values
            addUserAndCreatedDateCriteria(fromClause, whereClause);

            // add text search matches
            addIssuePKsCriteria(whereClause, matchingIssueIds);

            // state change query
            addStateChangeQuery(fromClause);
        }
        return matchingIssueIds;
    }

    private void addIssuePKsCriteria(StringBuffer sb, NumberKey[] ids)
    {
       if (ids != null && ids.length > 0)
       {
           sb.append(AND).append(IssuePeer.ISSUE_ID).append(IN)
               .append(StringUtils.join(ids, ",")).append(')');
       }     
    }

    /**
     * Get a List of Issues that match the criteria given by this
     * SearchIssue's searchWords and the quick search attribute values.
     *
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    public List getQueryResults()
        throws Exception
    {
        checkModified();
        if (lastQueryResults == null) 
        {
            List rows = null;
            StringBuffer from = new StringBuffer();
            StringBuffer where = new StringBuffer();
            NumberKey[] matchingIssueIds = addCoreSearchCriteria(from, where);
            // the matchingIssueIds are text search matches.  if length == 0,
            // then no need to search further.  if null then there was no
            // text to search, so continue the search process.
            if ( matchingIssueIds == null || matchingIssueIds.length > 0 ) 
            {            
                // Get matching issues, with sort criteria
                StringBuffer sql = new StringBuffer(255);
                sql.append("select DISTINCT ")
                    .append(IssuePeer.ISSUE_ID).append(',')
                    .append(IssuePeer.MODULE_ID).append(',')
                    .append(IssuePeer.TYPE_ID).append(',')
                    .append(IssuePeer.ID_PREFIX).append(',')
                    .append(IssuePeer.ID_COUNT);

                lastQueryResults = sortResults(sql, from, where);
            }
            else 
            {
                lastQueryResults = new ArrayList(0);
            }            
        }
        
        return lastQueryResults;
    }


    public int getIssueCount()
        throws Exception
    {
        checkModified();
        int count = 0;
        if (lastTotalIssueCount >= 0) 
        {
            count = lastTotalIssueCount;
        }
        else 
        {
            Criteria crit = new Criteria();
            StringBuffer from = new StringBuffer();
            StringBuffer where = new StringBuffer();
            NumberKey[] matchingIssueIds = addCoreSearchCriteria(from, where);
            if ( matchingIssueIds == null || matchingIssueIds.length > 0 ) 
            {
                String sql = 
                    "SELECT count(DISTINCT " + IssuePeer.ISSUE_ID + ") FROM " +
                    IssuePeer.TABLE_NAME;
                if (from.length() > 0) 
                {
                    sql += ' ' + from.toString();
                }
                if (where.length() > 0) 
                {
                    sql += WHERE + where.toString();
                }

                List records = BasePeer.executeQuery(sql);
                count = ((Record)records.get(0)).getValue(1).asInt();
            }
            lastTotalIssueCount = count;
        }

        return count;
    }

    private List sortResults(StringBuffer select, 
                             StringBuffer from, StringBuffer where)
        throws Exception
    {
        List matchingIssues = null;
        NumberKey sortAttrId = getSortAttributeId();

        // add the attribute value columns that will be shown in the list.
        // these are joined using a left outer join, so the additional
        // columns do not affect the results of the search (no additional
        // criteria are added to the where clause.)  Criteria object does
        // not provide support for outer joins, so we will need to manipulate
        // the query manually
        StringBuffer sb = new StringBuffer(select.length() + 500);
        sb.append(select);
        // use this to track already added aliases, need to use a better method
        String fromString = from.toString();

        String sortColumn = null;
        int sortAttrPos = NO_ATTRIBUTE_SORT;
        StringBuffer outerJoin = null;
        int valueListSize = -1;
        List rmuas = getIssueListAttributeColumns();
        if (rmuas != null) 
        {
            valueListSize = rmuas.size();
            outerJoin = new StringBuffer(10 * valueListSize + 20);
            StringBuffer selectColumns = new StringBuffer(20 * valueListSize);

            int count = 0;
            for (Iterator i = rmuas.iterator(); i.hasNext(); count++) 
            {
                RModuleUserAttribute rmua = (RModuleUserAttribute)i.next();
                // locate the sort attribute position so we can move any 
                // unset results to the end of the list.
                NumberKey attrPK = rmua.getAttributeId();
                if (attrPK.equals(sortAttrId)) 
                {
                    sortAttrPos = count;
                }
                String id = attrPK.toString();
                String alias = "av" + id;
                // add column to SELECT column clause
                selectColumns.append(',').append(alias).append(".VALUE");
                // if no criteria was specified for a displayed attribute
                // add it as an outer join
                if (fromString.indexOf(alias) < 0)
                {
                    outerJoin.append(
                        " LEFT OUTER JOIN SCARAB_ISSUE_ATTRIBUTE_VALUE ")
                        .append(alias).append(" ON (SCARAB_ISSUE.ISSUE_ID=")
                        .append(alias).append(".ISSUE_ID AND ").append(alias)
                        .append(".DELETED=0 AND ").append(alias)
                        .append(".ATTRIBUTE_ID=").append(id).append(')');
                }
            }

            // we need add more sql for attribute/option sorting
            if (sortAttrId != null) 
            {
                String sortId = sortAttrId.toString();
                Attribute att = AttributeManager.getInstance(sortAttrId);
                if ( att.isOptionAttribute())
                {
                    // add the sort column
                    sortColumn = "sortRMO.PREFERRED_ORDER";
                    selectColumns.append(',').append(sortColumn);
                    // join the RMO table to the AttributeValue alias we are sorting
                    outerJoin.append(BASE_OPTION_SORT_LEFT_JOIN).append("av")
                        .append(sortId).append(".OPTION_ID)");
                }
                else 
                {
                    sortColumn = "av" + sortId + ".VALUE";
                }
            }
            // add attribute columns for the table
            sb.append(selectColumns);
        }

        sb.append(FROM).append(IssuePeer.TABLE_NAME);
        if (from.length() > 0) 
        {
            sb.append(' ').append(fromString);
        }
        if (outerJoin != null) 
        {
            // add left outer join
            sb.append(outerJoin);    
        }
        if (where.length() > 0) 
        {
            sb.append(WHERE).append(where);
        }

        // add order by clause
        if (sortColumn == null) 
        {
            sb.append(ORDER_BY).append(IssuePeer.ID_PREFIX);
            if (getSortPolarity().equals("desc"))
            {
                sb.append(" DESC");
            }
            else
            {
                sb.append(" ASC");
            }
            sb.append(',').append(IssuePeer.ID_COUNT);
            if (getSortPolarity().equals("desc"))
            {
                sb.append(" DESC");
            }
            else
            {
                sb.append(" ASC");
            }
        }
        else 
        {
            sb.append(ORDER_BY).append(sortColumn);
            if (getSortPolarity().equals("desc"))
            {
                sb.append(" DESC");
            }
            else
            {
                sb.append(" ASC");
            }
            // add pk sort so that rows can be combined easily
            sb.append(',').append(IssuePeer.ISSUE_ID).append(" ASC");
        }
        
        Logger torqueLog = Log.get("org.apache.torque");
        if (torqueLog.isDebugEnabled()) 
        {
            torqueLog.debug("Search sql: " + sb.toString());
        }
                
        // return a List of QueryResult objects
        return buildQueryResults(BasePeer.executeQuery(sb.toString()),
                                 sortAttrPos, valueListSize);
    }

    
    /**
     * provides common code for use by the sortByUniqueId and sortByAttribute
     * methods.  Assembles a list of Record objects into a list of QueryResults.
     *
     * @param records a <code>List</code> value
     * @param sortAttrPos an <code>int</code> value
     * @param valueListSize an <code>int</code> value
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    private List buildQueryResults(List records, int sortAttrPos, 
                                   int valueListSize)
        throws Exception
    {
        List queryResults = new ArrayList(records.size());
        // if we are sorting on an attribute column and some records have
        // null (non-existent) values for that attribute we separate them
        // for presentation at the end of the list.  Otherwise for certain
        // polarity they will be shown first.
        List heldRows = null;
        if (sortAttrPos >= 0) 
        {
            heldRows = new ArrayList();
        }
        
        String prevPk = null;
        QueryResult qr = null;
        for (Iterator i = records.iterator(); i.hasNext();) 
        {
            Record rec = (Record)i.next();
            String pk = rec.getValue(1).asString();
            // each attribute can result in a different Record object.  We have
            // sorted on the pk column in addition to any other sort, so that
            // all attributes for a given issue will be grouped.  The following
            // code maps these multiple Records into a single QueryResult per
            // issue
            if (pk.equals(prevPk)) 
            {
                if (valueListSize > 0) 
                {
                    List values = qr.getAttributeValues();
                    for (int j=0; j < valueListSize; j++) 
                    {
                        String s = rec.getValue(j+6).asString();
                        // it's possible that multiple Records could have the
                        // same value for a given attribute, but we do not want
                        // to add the same value many times, so we check for
                        // this possibility below.  See the code in the else
                        // block about 10 lines down to see how the values lists
                        // are arranged to allow for multiple values.
                        List prevValues = (List)values.get(j);
                        boolean newValue = true;
                        for (int k=0; k<prevValues.size(); k++) 
                        {
                            if (ObjectUtils.equals(prevValues.get(k), s)) 
                            {
                                newValue = false;
                                break;
                            }
                        }                    
                        if (newValue) 
                        {
                            prevValues.add(s);
                        }
                    }
                }
            }
            else 
            {
                // the current Record is a new issue
                prevPk = pk;
                qr = new QueryResult(this);
                qr.setIssueId(pk);
                qr.setModuleId(rec.getValue(2).asIntegerObj());
                qr.setIssueTypeId(rec.getValue(3).asIntegerObj());
                qr.setIdPrefix(rec.getValue(4).asString());
                qr.setIdCount(rec.getValue(5).asString());
                boolean holdRow = false;
                if (valueListSize > 0) 
                {
                    List values = new ArrayList(valueListSize);
                    for (int j = 0; j < valueListSize; j++) 
                    {
                        String s = rec.getValue(j+6).asString();
                        // check if we are sorting on this value and hold the
                        // result to the end of the list, if the value is null.
                        if (j == sortAttrPos && s == null) 
                        {
                            holdRow = true;
                        }

                        // some attributes can be multivalued, so store a list
                        // for each attribute containing the values
                        ArrayList multiVal = new ArrayList(2);
                        multiVal.add(s);
                        values.add(multiVal);
                    }
                    qr.setAttributeValues(values);
                }
                if (holdRow) 
                {
                    heldRows.add(qr);
                }
                else 
                {
                    queryResults.add(qr);
                }
            }
        }
            
        if (heldRows != null) 
        {
            queryResults.addAll(heldRows);
        }

        return queryResults;
    }

    /**
     * Used by QueryResult to avoid multiple db hits in the event caching
     * is not being used application-wide.  It is used if the IssueList.vm
     * template is printing the module names next to each issue id.
     * As this IssueSearch object is short-lived, use of a simple Map based
     * cache is ok, need to re-examine if the lifespan is increased.
     *
     * @param id an <code>Integer</code> value
     * @return a <code>Module</code> value
     * @exception TorqueException if an error occurs
     */
    Module getModule(Integer id)
        throws TorqueException
    {
        Module module = (Module)moduleMap.get(id);
        if (module == null)
        {
            module = ModuleManager.getInstance(new NumberKey(id.intValue()));
            moduleMap.put(id, module);
        }
        return module;
    }
    
    /**
     * Used by QueryResult to avoid multiple db hits in the event caching
     * is not being used application-wide.  It is used if the IssueList.vm
     * template is printing the issue type names next to each issue id.
     * As this IssueSearch object is short-lived, use of a simple Map based
     * cache is ok, need to re-examine if the lifespan is increased.
     *
     * @param moduleId an <code>Integer</code> value
     * @param issueTypeId an <code>Integer</code> value
     * @return a <code>RModuleIssueType</code> value
     * @exception TorqueException if an error occurs
     */
    RModuleIssueType getRModuleIssueType(Integer moduleId, Integer issueTypeId)
        throws TorqueException
    {
        NumberKey[] nks = {new NumberKey(moduleId.intValue()), 
                           new NumberKey(issueTypeId.intValue())};
        ObjectKey key = new ComboKey(nks);
        RModuleIssueType rmit = (RModuleIssueType)rmitMap.get(key);
        if (rmit == null)
        {
            rmit = RModuleIssueTypeManager.getInstance(key);
            rmitMap.put(key, rmit);
        }
        return rmit;
    }
}
