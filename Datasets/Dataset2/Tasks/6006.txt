static final Integer MULTIPLE_KEY = new Integer(0);

package org.tigris.scarab.om;

/* ================================================================
 * Copyright (c) 2000-2003 CollabNet.  All rights reserved.
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

import org.apache.commons.lang.ObjectUtils;
import org.apache.torque.om.Persistent;
import org.tigris.scarab.util.word.IssueSearch;

/** 
 * A module and an issue type.  Wildcards are possible, so that a single
 * MITListItem could represent all the issue types in a module.  A single
 * issue type in all modules (that have it defined).  Or all modules and
 * issue types.
 */
public  class MITListItem 
    extends org.tigris.scarab.om.BaseMITListItem
    implements Persistent
{
    private static final Integer MULTIPLE_KEY = new Integer(0);

    /**
     * The number of active issues of the this issue type within the module.
     *
     * @param user a <code>ScarabUser</code> value used to determine if
     * a count should be given.  
     * @return an <code>int</code> the number of issues entered for the 
     * module unless the user does not have permission to
     * search for issues in the given module, then a value of 0 
     * will be returned.
     * @exception Exception if an error occurs
     */
    public int getIssueCount(ScarabUser user)
        throws Exception
    {
        IssueSearch is = new IssueSearch(getModule(), getIssueType(), user);
        return is.getIssueCount();
    }

    public boolean isSingleModuleIssueType()
    {
        boolean single = true;
        if (MULTIPLE_KEY.equals(getModuleId()) 
            || MULTIPLE_KEY.equals(getIssueTypeId())) 
        {
            single = false;
        }
        return single;
    }

    public boolean isSingleModule()
    {
        return !MULTIPLE_KEY.equals(getModuleId());
    }

    public boolean isSingleIssueType()
    {
        return !MULTIPLE_KEY.equals(getIssueTypeId());
    }

    public boolean isUseCurrentModule()
    {
        return getModuleId() == null;
    }

    public boolean isUseCurrentIssueType()
    {
        return getIssueTypeId() == null;
    }

    public String getQueryKey()
    {
        String key = super.getQueryKey();
        if (key == null || key.length() == 0) 
        {
            StringBuffer sb = new StringBuffer();
            if (getModuleId() != null) 
            {
                sb.append(getModuleId());
            }
            sb.append(':');
            if (getIssueTypeId() != null) 
            {
                sb.append(getIssueTypeId());
            }
            key = sb.toString();
        }
        return key;
    }

    public int hashCode()
    {
        int hashCode = 10;
        if (getModuleId() != null) 
        {
            hashCode += getModuleId().hashCode();
        }
        if (getIssueTypeId() != null) 
        {
            hashCode += getIssueTypeId().hashCode();
        }
        return hashCode;
    }

    public boolean equals(Object obj)
    {
        boolean isEqual = false;
        if (obj instanceof MITListItem) 
        {
            MITListItem item = (MITListItem)obj;
            isEqual = ObjectUtils.equals(this.getModuleId(), item.getModuleId());
            isEqual &= ObjectUtils.equals(this.getIssueTypeId(), 
                                          item.getIssueTypeId());
        }
        return isEqual;
    }

    public String toString()
    {
        StringBuffer sb = new StringBuffer(50);
        sb.append('{').append(super.toString()).append('(');
        if (getModuleId() != null) 
        {
            sb.append(getModuleId());
        }
        sb.append(':');
        if (getIssueTypeId() != null) 
        {
            sb.append(getIssueTypeId());
        }
        sb.append(")}");

        return sb.toString();
    }
}