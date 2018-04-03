minFid.setPrefix(getModule().getCode());

package org.tigris.scarab.util.word;

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

// JDK classes
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Date;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

// Turbine classes
import org.apache.torque.om.NumberKey;
import org.apache.torque.util.Criteria;
import org.apache.commons.util.SequencedHashtable;
import org.apache.commons.util.StringUtils;

// Scarab classes
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.AttributeOption;
import org.tigris.scarab.om.Issue;
import org.tigris.scarab.om.IssuePeer;
import org.tigris.scarab.om.ROptionOptionPeer;
import org.tigris.scarab.om.AttributeValuePeer;
import org.tigris.scarab.om.AttributeValue;
import org.tigris.scarab.om.AttributePeer;
import org.tigris.scarab.om.ActivityPeer;
import org.tigris.scarab.om.TransactionPeer;
import org.tigris.scarab.om.TransactionTypePeer;
import org.tigris.scarab.om.RModuleOptionPeer;
import org.tigris.scarab.om.ScarabUser;
import org.tigris.scarab.services.user.UserManager;

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

    private static final NumberKey ALL_TEXT = new NumberKey("0");

    private static final String PARENT_ID;
    private static final String CHILD_ID;
    private static final String AV_ISSUE_ID;
    private static final String AV_OPTION_ID;
    private static final String AV_USER_ID;
    private static final DateFormat DATETIME_FORMATTER;
    private static final DateFormat DATE_FORMATTER;

    private String searchWords;
    private NumberKey[] textScope;
    private String minId;
    private String maxId;
    private String minDate;
    private String maxDate;
    private int minVotes;
    private String[] createdBy;
    
    private NumberKey stateChangeAttributeId;
    private NumberKey stateChangeFromOptionId;
    private NumberKey stateChangeToOptionId;
    private String stateChangeFromDate;
    private String stateChangeToDate;

    private NumberKey initialSortAttributeId;
    private String initialSortPolarity;
    private int resultsPerPage;
    

    static 
    {
        PARENT_ID = ROptionOptionPeer.OPTION1_ID;
        CHILD_ID = ROptionOptionPeer.OPTION2_ID;

        // column names only
        AV_OPTION_ID = AttributeValuePeer.OPTION_ID.substring(
            AttributeValuePeer.OPTION_ID.indexOf('.')+1);
        AV_ISSUE_ID = AttributeValuePeer.ISSUE_ID.substring(
            AttributeValuePeer.ISSUE_ID.indexOf('.')+1);
        AV_USER_ID = AttributeValuePeer.USER_ID.substring(
            AttributeValuePeer.USER_ID.indexOf('.')+1);

        DATETIME_FORMATTER = new SimpleDateFormat("MM/dd/yy HH:mm");
        DATE_FORMATTER = new SimpleDateFormat("MM/dd/yy");
    }

    public IssueSearch(Issue issue)
        throws Exception
    {
        setTypeId(issue.getTypeId());
        setModuleId(issue.getModuleId());

        List avs = issue.getAttributeValues();
        List newAvs = getAttributeValues();
        for (int i=0; i<avs.size(); i++)
        {
            newAvs.add(avs.get(i));
        }
    }

    public IssueSearch()
    {
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
                textScope[j] = ((Attribute)
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
     * Get the value of createdBy.
     * @return value of createdBy.
     */
    public String[] getCreatedByUserNames() 
    {
        return this.createdBy;
    }
    
    /**
     * Set the value of createdBy.
     * @param v  Value to assign to createdBy.
     */
    public void setCreatedByUserNames(String[] v) 
    {
        if ( v != null && (v.length == 0 || v[0].length() == 0) ) 
        {
            this.createdBy = null;
        }
        else 
        {
            this.createdBy = v;            
        }
    }
    
    /**
     * Get the value of resultsPerPage.
     * @return value of resultsPerPage.
     */
    public int getResultsPerPage() 
    {
        return resultsPerPage;
    }
    
    /**
     * Set the value of resultsPerPage.
     * @param v  Value to assign to resultsPerPage.
     */
    public void setResultsPerPage(int  v) 
    {
        this.resultsPerPage = v;
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
     * Get the value of initialSortAttributeId.
     * @return value of initialSortAttributeId.
     */
    public NumberKey getInitialSortAttributeId() 
    {
        return initialSortAttributeId;
    }
    
    /**
     * Set the value of initialSortAttributeId.
     * @param v  Value to assign to initialSortAttributeId.
     */
    public void setInitialSortAttributeId(NumberKey v) 
    {
        this.initialSortAttributeId = v;
    }
    

    /**
     * Get the value of initialSortPolarity.
     * @return value of initialSortPolarity.
     */
    public String getInitialSortPolarity() 
    {
        String polarity = null;
        if ( initialSortPolarity == null ) 
        {
            polarity = null;
        }
        else if ( DESC.equals(initialSortPolarity) ) 
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
     * Set the value of initialSortPolarity.
     * @param v  Value to assign to initialSortPolarity.
     */
    public void setInitialSortPolarity(String  v) 
    {
        this.initialSortPolarity = v;
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
        SequencedHashtable searchValues = getModuleAttributeValuesMap();
        List searchAttributes = new ArrayList(searchValues.size());

        for ( int i=0; i<searchValues.size(); i++ ) 
        {
            AttributeValue searchValue = 
                (AttributeValue)searchValues.getValue(i);
            if ( (!quickSearchOnly || searchValue.isQuickSearchAttribute())
                 && searchValue instanceof StringAttribute ) 
            {
                searchAttributes.add(searchValue.getAttribute());
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
        SequencedHashtable searchValues = getModuleAttributeValuesMap();
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
                //minFid = new Issue.FederatedId(maxFid.getDomainId(),
                //                               maxFid.getPrefix(), 1);
                crit.add(IssuePeer.ID_DOMAIN, maxFid.getDomain());
                crit.add(IssuePeer.ID_PREFIX, maxFid.getPrefix());
                crit.add(IssuePeer.ID_COUNT, maxFid.getCount(), 
                         Criteria.LESS_EQUAL);
            }
            else if ( maxId == null || maxId.length() == 0 ) 
            {
                minFid = new Issue.FederatedId(minId);
                crit.add(IssuePeer.ID_DOMAIN, minFid.getDomain());
                crit.add(IssuePeer.ID_PREFIX, minFid.getPrefix());
                crit.add(IssuePeer.ID_COUNT, minFid.getCount(), 
                         Criteria.GREATER_EQUAL);

            }
            else 
            {
                minFid = new Issue.FederatedId(minId);
                maxFid = new Issue.FederatedId(maxId);
                // give reasonable defaults if module code was not specified
                if ( minFid.getPrefix() == null ) 
                {
                    minFid.setPrefix(getScarabModule().getCode());
                }
                if ( maxFid.getPrefix() == null ) 
                {
                    maxFid.setPrefix(minFid.getPrefix());
                }
                
                // make sure min id is less than max id and that the character
                // parts are equal otherwise skip the query, there are no 
                // matches
                if ( minFid.getCount() <= maxFid.getCount() 
                     && minFid.getPrefix().equals(maxFid.getPrefix())
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
                    crit.add(IssuePeer.ID_DOMAIN, minFid.getDomain());
                    crit.add(IssuePeer.ID_PREFIX, minFid.getPrefix());
                }
                else 
                {
                    throw new ScarabException("Incompatible issue Ids: " +
                                              minId + " and " + maxId);
                }
            }
        }
    }


    private void addCreatedDateRange(Criteria crit)
        throws ScarabException
    {
        Date minUtilDate = parseDate(getMinDate(), false);
        Date maxUtilDate = parseDate(getMaxDate(), true);
        if ( minUtilDate != null || maxUtilDate != null ) 
        {
            addDateRange(TransactionPeer.CREATED_DATE, 
                         minUtilDate, maxUtilDate, crit);
            crit.addJoin(TransactionPeer.TRANSACTION_ID, 
                         ActivityPeer.TRANSACTION_ID);
            crit.addJoin(ActivityPeer.ISSUE_ID, IssuePeer.ISSUE_ID);
            crit.add(TransactionPeer.TYPE_ID, 
                     TransactionTypePeer.CREATE_ISSUE__PK);
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
    private Date parseDate(String dateString, boolean addTwentyFourHours)
    {
        Date date = null;
        if ( dateString != null ) 
        {
            if ( dateString.indexOf(':') == -1 )
            {
                try
                {
                    date = DATE_FORMATTER.parse(dateString);
                    // add 24 hours to max date so it is inclusive
                    if ( addTwentyFourHours ) 
                    {                
                        date.setTime(date.getTime() + 86399999);
                    }
                }
                catch (Exception ee)
                {
                    // ignore/debug
                    ee.printStackTrace();
                }
            }
            else
            {
                try
                {
                    date = DATETIME_FORMATTER.parse(dateString);
                }
                catch (Exception ee)
                {
                    // ignore/debug
                    ee.printStackTrace();
                }
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
            if ( aval instanceof OptionAttribute 
                 || aval instanceof UserAttribute) 
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
                    if ( aval instanceof OptionAttribute ) 
                    {
                        c2 = buildOptionCriterion(aval);
                    }
                    else 
                    {
                        c2 = buildUserCriterion(aval);
                    }
                    
                    prevCrit.or(c2);
                }
                else
                {
                    Criteria.Criterion c1 = crit.getNewCriterion("av"+index,
                        AV_ISSUE_ID, "av" + index + "." + AV_ISSUE_ID + "=" + 
                        IssuePeer.ISSUE_ID, Criteria.CUSTOM); 
                    crit.addAlias("av"+index, AttributeValuePeer.TABLE_NAME);
                    if ( aval instanceof OptionAttribute ) 
                    {
                        c2 = buildOptionCriterion(aval);
                    }
                    else 
                    {
                        c2 = buildUserCriterion(aval);
                    }
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
        List descendants = aval.getAttributeOption().getDescendants();
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

    /**
     * This method builds a Criterion for a single user attribute value.
     * It is used in the addSelectedAttributes method
     *
     * @param aval an <code>AttributeValue</code> value
     * @return a <code>Criteria.Criterion</code> value
     */
    private Criteria.Criterion buildUserCriterion(AttributeValue aval)
        throws Exception
    {
        Criteria crit = new Criteria();
        String index = aval.getAttributeId().toString();
        Criteria.Criterion criterion = crit.getNewCriterion( 
            "av"+index, AV_USER_ID, aval.getUserId(), Criteria.EQUAL);
        return criterion;
    }

    private void addCreatedByUserIds(Criteria crit)
        throws Exception
    {
        if ( createdBy != null && createdBy.length > 0 ) 
        {
            crit.addJoin(TransactionPeer.TRANSACTION_ID, 
                         ActivityPeer.TRANSACTION_ID);
            crit.addJoin(ActivityPeer.ISSUE_ID, IssuePeer.ISSUE_ID);
            crit.add(TransactionPeer.TYPE_ID, 
                     TransactionTypePeer.CREATE_ISSUE__PK);
            // convert usernames to ids
            List users = UserManager.getUsers(createdBy);
            NumberKey[] ids = new NumberKey[users.size()];
            for ( int i=0; i<users.size(); i++ ) 
            {
                ids[i] = ((ScarabUser)users.get(i)).getUserId();
            }
            
            crit.add(TransactionPeer.CREATED_BY, ids, Criteria.IN);
            // there could be multiple attributes modified during the creation
            // which will lead to duplicates
            crit.setDistinct();
        }
    }

    private NumberKey[] addTextMatches(Criteria crit, List attValues)
        throws Exception
    {
        NumberKey[] matchingIssueIds = null;
        SearchIndex searchIndex = SearchFactory.getInstance(); 
        if ( getSearchWords() != null && getSearchWords().length() != 0 ) 
        {
            searchIndex.addQuery(getTextScope(), getSearchWords());
            matchingIssueIds = searchIndex.getRelatedIssues();    
            if ( matchingIssueIds.length != 0 )
            { 
                crit.addIn(IssuePeer.ISSUE_ID, matchingIssueIds);
            }
        }
        else 
        {
            boolean atLeastOne = false;
            for ( int i=0; i<attValues.size(); i++ ) 
            {
                AttributeValue aval = (AttributeValue)attValues.get(i);
                if ( aval instanceof StringAttribute 
                     && aval.getValue() != null 
                     && aval.getValue().length() != 0 )
                {
                    atLeastOne = true;
                    NumberKey[] id = {aval.getAttributeId()};
                    searchIndex
                        .addQuery(id, aval.getValue());
                }
            }

            if ( atLeastOne ) 
            {
                matchingIssueIds = searchIndex.getRelatedIssues();    
                if ( matchingIssueIds.length != 0 )
                { 
                    crit.addIn(AttributeValuePeer.ISSUE_ID, matchingIssueIds);
                }       
            }
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
                addDateRange(TransactionPeer.CREATED_DATE, 
                             minUtilDate, maxUtilDate, crit);
                crit.addJoin(TransactionPeer.TRANSACTION_ID, 
                             ActivityPeer.TRANSACTION_ID);
            }
        }
    }

    private void addInitialSortCriteria(Criteria crit)
        throws Exception
    {
        NumberKey attId = getInitialSortAttributeId();
        if ( attId != null ) 
        {
            AttributeValue sortAttribute = 
                AttributeValue.getNewInstance(attId, this);
            String sortColumn = null;
            if ( sortAttribute instanceof OptionAttribute ) 
            {            
                // we need to join with the r_module_option table, so first 
                // add the issue columns
                IssuePeer.addSelectColumns(crit);
                crit.addSelectColumn(RModuleOptionPeer.PREFERRED_ORDER);
                crit.add(AttributeValuePeer.ATTRIBUTE_ID, attId );
                crit.addJoin(IssuePeer.ISSUE_ID, AttributeValuePeer.ISSUE_ID);
                crit.addJoin(RModuleOptionPeer.OPTION_ID, 
                             AttributeValuePeer.OPTION_ID);
                crit.addJoin(IssuePeer.MODULE_ID, RModuleOptionPeer.MODULE_ID);
                sortColumn = RModuleOptionPeer.PREFERRED_ORDER;
            }
            else 
            {
                // add the issue columns
                IssuePeer.addSelectColumns(crit);
                // there can be duplicate issues returned because attributes
                // may have multiple values.
                crit.setDistinct();
                crit.addSelectColumn(AttributeValuePeer.VALUE);
                crit.add(AttributeValuePeer.ATTRIBUTE_ID, attId );
                crit.addJoin(IssuePeer.ISSUE_ID, AttributeValuePeer.ISSUE_ID);
                sortColumn = AttributeValuePeer.VALUE;
            }            
            if ( getInitialSortPolarity().equals(ASC)) 
            {
                crit.addAscendingOrderByColumn(sortColumn);
            }
            else 
            {
                crit.addDescendingOrderByColumn(sortColumn);
            }
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
        return getMatchingIssues(-1);
    }

    /**
     * Get a List of Issues that match the criteria given by this
     * SearchIssue's searchWords and the quick search attribute values.
     *
     * @param limitResults an <code>int</code> value
     * @return a <code>List</code> value
     * @exception Exception if an error occurs
     */
    public List getMatchingIssues(int limitResults)
        throws Exception
    {
        // List matchingIssues = null;
        Criteria crit = new Criteria();

        // add option values
        Criteria tempCrit = new Criteria(2)
            .add(AttributeValuePeer.DELETED, false);        
        List attValues = getAttributeValues(tempCrit);
            // remove unset AttributeValues before searching
        removeUnsetValues(attValues);        
        addSelectedAttributes(crit, attValues);

        // search for issues based on text
        NumberKey[] matchingIssueIds = addTextMatches(crit, attValues);

        List matchingIssues = null;
        if ( matchingIssueIds == null || matchingIssueIds.length > 0 ) 
        {            
            addIssueIdRange(crit);
            addCreatedDateRange(crit);
            addMinimumVotes(crit);

            // committed by
            addCreatedByUserIds(crit);
            // state change query
            addStateChangeQuery(crit);
            
            // Add any order by clause
            addInitialSortCriteria(crit);
            
            // get matching issues
            matchingIssues = IssuePeer.doSelect(crit);
            
            // text search can lead to an ordered list according to search 
            // engine's ranking mechanism, so sort the results according to 
            // this list unless another sorting criteria has been specified.
            if ( getInitialSortAttributeId() == null 
                 && matchingIssueIds != null ) 
            {
                matchingIssues = sortByIssueIdList(
                    matchingIssueIds, matchingIssues, limitResults);
            }
            // no sorting
            else
            {
                int maxIssues = matchingIssues.size();
                if ( limitResults > 0 && maxIssues > limitResults )
                {
                    maxIssues = limitResults;
                }
                matchingIssues = matchingIssues.subList(0, maxIssues);
            }
        }
        else 
        {
            matchingIssues = new ArrayList(0);
        }

        return matchingIssues;
    }

    /**
     * Takes a List of Issues and an array of IDs and sorts the Issues in
     * the list to the order given in the ID array
     */
    private List sortByIssueIdList(NumberKey[] ids, List issues, 
                                   int limitResults)
    {
        int maxIssues = issues.size();
        ArrayList sortedIssues = new ArrayList(maxIssues);
        
        // Place issues into a map by id for searching
        Map issueIdMap = new HashMap((int)(1.25*maxIssues+1));
        for ( int i=maxIssues-1; i>=0; i-- ) 
        {
            Issue issue = (Issue)issues.get(i);
            issueIdMap.put( issue.getIssueId(), issue );
        }

        for ( int i=0; i<ids.length  
                  && ( limitResults <= 0 || sortedIssues.size() <= limitResults); i++ ) 
        {
            Object issueObj = issueIdMap.get(ids[i]);
            if (issueObj != null) 
            {
                sortedIssues.add(issueObj);
            }
        }
     
        return sortedIssues;
    }
}