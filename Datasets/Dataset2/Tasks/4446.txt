import org.apache.commons.util.SequencedHashtable;

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

// Turbine classes
import org.apache.torque.om.NumberKey;
import org.apache.torque.util.Criteria;
import org.apache.turbine.util.SequencedHashtable;

// Scarab classes
import org.tigris.scarab.om.Attribute;
import org.tigris.scarab.om.AttributeOption;
import org.tigris.scarab.om.Issue;
import org.tigris.scarab.om.IssuePeer;
import org.tigris.scarab.om.ROptionOptionPeer;
import org.tigris.scarab.om.AttributeValuePeer;
import org.tigris.scarab.om.AttributeValue;

import org.tigris.scarab.attribute.OptionAttribute;
import org.tigris.scarab.attribute.StringAttribute;

/** 
 * A utility class to build up and carry out a search for 
 * similar issues.  It subclasses Issue for functionality, it is 
 * not a more specific type of Issue.
 */
public class IssueSearch 
    extends Issue
{
    private String searchWords;
    private NumberKey[] textScope;
    private int resultsPerPage;

    private static final NumberKey ALL_TEXT = new NumberKey("0");
    private static final String PARENT_ID;
    private static final String CHILD_ID;
    private static final String AV_ISSUE_ID;
    private static final String AV_OPTION_ID;

    static 
    {
        PARENT_ID = ROptionOptionPeer.OPTION1_ID;
        CHILD_ID = ROptionOptionPeer.OPTION2_ID;

        // column names only
        AV_OPTION_ID = AttributeValuePeer.OPTION_ID.substring(
            AttributeValuePeer.OPTION_ID.indexOf('.')+1);
        AV_ISSUE_ID = AttributeValuePeer.ISSUE_ID.substring(
            AttributeValuePeer.ISSUE_ID.indexOf('.')+1);

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
        List textAttributes = getQuickSearchTextAttributes();
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
     * Get the value of resultsPerPage.
     * @return value of resultsPerPage.
     */
    public int getResultsPerPage() 
    {
        if ( resultsPerPage == 0) 
        {
            resultsPerPage = -1;
        }
        
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


    public NumberKey getALL_TEXT()
    {
        return ALL_TEXT;
    }

    public List getQuickSearchTextAttributes()
        throws Exception
    {
        SequencedHashtable searchValues = getModuleAttributeValuesMap();
        List searchAttributes = new ArrayList(searchValues.size());

        for ( int i=0; i<searchValues.size(); i++ ) 
        {
            AttributeValue searchValue = 
                (AttributeValue)searchValues.getValue(i);
            if ( searchValue.isQuickSearchAttribute() &&                  
                 searchValue instanceof StringAttribute ) 
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
        List allValues = getOptionAttributeValues();
        List searchAttributeValues = new ArrayList(allValues.size());

        for ( int i=0; i<allValues.size(); i++ ) 
        {
            AttributeValue searchValue = 
                (AttributeValue)allValues.get(i);
            if ( searchValue.isQuickSearchAttribute()  ) 
            {
                searchAttributeValues.add(searchValue);
            }
        }

        return searchAttributeValues;
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
        SequencedHashtable searchValues = getModuleAttributeValuesMap();
        List searchAttributeValues = new ArrayList(searchValues.size());

        for ( int i=0; i<searchValues.size(); i++ ) 
        {
            AttributeValue searchValue = 
                (AttributeValue)searchValues.getValue(i);
            if ( searchValue instanceof OptionAttribute ) 
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


    /**
     * Returns a List of matching issues.  if no OptionAttributes were
     * found in the input list null is returned.
     *
     * @param attValues a <code>List</code> value
     */
    private List searchOnOptionAttributes(List attValues, 
                                          NumberKey[] validIssueIds)
        throws Exception
    {
        Criteria crit = new Criteria();
        Criteria.Criterion c = null;
        boolean atLeastOne = false;
        for ( int i=0; i<attValues.size(); i++ ) 
        {
            AttributeValue aval = (AttributeValue)attValues.get(i);
            if ( aval instanceof OptionAttribute ) 
            {
                atLeastOne = true;
                Criteria.Criterion c1 = crit.getNewCriterion("av" + i,
                    AV_ISSUE_ID, "av" + i + "." + AV_ISSUE_ID + "=" + 
                    IssuePeer.ISSUE_ID, Criteria.CUSTOM); 
                crit.addAlias("av" + i, AttributeValuePeer.TABLE_NAME);
                List descendants = aval.getAttributeOption().getDescendants();
                if ( descendants.size() == 0 ) 
                {
                    c1.and(crit.getNewCriterion( "av" + i, AV_OPTION_ID,
                        aval.getOptionId(), Criteria.EQUAL));
                }
                else
                { 
                    NumberKey[] ids = new NumberKey[descendants.size()];
                    for ( int j=ids.length-1; j>=0; j-- ) 
                    {
                        ids[j] = ((AttributeOption)descendants.get(j))
                            .getOptionId();
                    }
                    c1.and(crit.getNewCriterion( "av" + i, AV_OPTION_ID,
                        ids, Criteria.IN));
                }                
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

        if ( atLeastOne ) 
        {
            crit.add(c);
            if ( validIssueIds != null && validIssueIds.length != 0 ) 
            {
                crit.addIn(AttributeValuePeer.ISSUE_ID, validIssueIds);
            }
            
            return IssuePeer.doSelect(crit);
        }
        else 
        {
            return null;
        }
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
        List matchingIssues = null;
        
        // search for issues based on text
        NumberKey[] matchingIssueIds = null;      
        if ( getSearchWords() != null && getSearchWords().length() != 0 ) 
        {
            SearchIndex searchIndex = SearchFactory.getInstance();
            searchIndex.addQuery(getSearchWords());
            searchIndex.setAttributeIds(getTextScope());
            matchingIssueIds = searchIndex.getRelatedIssues();      
        }

        Criteria crit = new Criteria(2)
            .add(AttributeValuePeer.DELETED, false);        
        List attValues = getAttributeValues(crit);
        // remove unset AttributeValues before searching
        removeUnsetValues(attValues);
        // get matching issues according to option values
        List optionMatchingIssues = 
            searchOnOptionAttributes(attValues, matchingIssueIds);

        
        // only have text search
        if ( optionMatchingIssues == null && matchingIssueIds != null
             && matchingIssueIds.length != 0 ) 
        {
            crit = new Criteria()
                .addIn(IssuePeer.ISSUE_ID, matchingIssueIds);
            List textMatchingIssues = IssuePeer.doSelect(crit);

            matchingIssues = 
                sortByIssueIdList(matchingIssueIds, textMatchingIssues, 
                                  limitResults);
        }
        // options only
        else if ( optionMatchingIssues != null && matchingIssueIds == null )
        {
            int maxIssues = optionMatchingIssues.size();
            if ( limitResults >= 0 && maxIssues > limitResults )
            {
                maxIssues = limitResults;
            }
            matchingIssues = new ArrayList(maxIssues);
        
            for (int i=0; i<maxIssues; i++)
            {
                matchingIssues.add(optionMatchingIssues.get(i));
            }
        }
        // text and options
        else if ( optionMatchingIssues != null && matchingIssueIds != null )
        {            
            matchingIssues = 
                sortByIssueIdList(matchingIssueIds, optionMatchingIssues, 
                                  limitResults);
        }
            
        return matchingIssues;
    }

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
                  || sortedIssues.size() == limitResults; i++ ) 
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