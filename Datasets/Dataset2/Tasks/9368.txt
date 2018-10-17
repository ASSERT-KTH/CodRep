cat = Category.getInstance(org.tigris.scarab.util.xml.XMLImport.class);

package org.tigris.scarab.util.xml;

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
import java.util.Hashtable;
import java.util.ArrayList;
import java.util.Enumeration;

import org.apache.log4j.Category;
import org.tigris.scarab.om.DependType;
import org.tigris.scarab.om.Depend;

import org.apache.torque.om.NumberKey;

/**
 * @author <a href="mailto:kevin.minshull@bitonic.com">Kevin Minshull</a>
 * @author <a href="mailto:richard.han@bitonic.com">Richard Han</a>
 */
public class DependencyTree
{
    private Hashtable issueDependTree;
    private Hashtable moduleDependTree;
    private Hashtable issueIdTable;
    private Hashtable validationTree;
    private Category cat;
    
    public DependencyTree () 
    {
        moduleDependTree = new Hashtable();
        issueDependTree = new Hashtable();
        issueIdTable = new Hashtable();
        cat = Category.getInstance(org.tigris.scarab.util.xml.DBImport.class);
    }
    
    public void addModuleDependency(NumberKey childModuleId, NumberKey parentModuleId)
    {
        moduleDependTree.put(childModuleId, parentModuleId);
    }
    
    public NumberKey getModuleDependency(NumberKey childModuleId)
    {
        return (NumberKey)moduleDependTree.get(childModuleId);
    }
    
    public void addIssueDependency(String xmlIssueId, DependencyNode dependencyNode) 
    {
        if (issueDependTree.containsKey(xmlIssueId)) 
        {
            ((ArrayList)issueDependTree.get(xmlIssueId)).add(dependencyNode);
        } 
        else 
        {
            ArrayList al = new ArrayList();
            al.add(dependencyNode);
            issueDependTree.put(xmlIssueId, al);
        }
    }
    
    public void addIssueId(String xmlIssueId, NumberKey dbIssueId) 
    {
        issueIdTable.put(xmlIssueId, dbIssueId);
    }
    
    public String getIssueXmlId(NumberKey dbIssueId)
    {
        Enumeration xmlIdList = issueIdTable.keys();
        while(xmlIdList.hasMoreElements())
        {
            String xmlId = (String)xmlIdList.nextElement();
            if(xmlId != null )
            {
                NumberKey issueId = getIssueId(xmlId);
                if(issueId.equals(dbIssueId))
                {
                    return xmlId;
                }
            }
        }
        return null;
    }
    
    public ArrayList getIssueDependencies(String xmlIssueId) 
    {
        return (ArrayList)issueDependTree.get(xmlIssueId);
    }
    
    public NumberKey getIssueId(String xmlIssueId)
    {
        return (NumberKey) issueIdTable.get(xmlIssueId);
    }
    
    public boolean isIssueDependencyValid(DependencyNode node)
    {
        Enumeration xmlIdList = issueDependTree.keys();
        while(xmlIdList.hasMoreElements())
        {
            String xmlId = (String)xmlIdList.nextElement();
            if(xmlId.equals(node.getParentOrChildId()))
            {
                return(isDependTypesMatch(xmlId,node.getIssueId(), node.getDependType()));
            }
        }
        return false;
    }
    
    private boolean isDependTypesMatch(String xmlId1, String xmlId2, DependType dependType)
    {
        ArrayList dependencies = getIssueDependencies(xmlId1);
        for(int i = 0; i < dependencies.size(); i++)
        {
            DependencyNode node = (DependencyNode)dependencies.get(i);
            
            if(node != null && node.getParentOrChildId().equals(xmlId2))
            {
                return node.getDependType().getName().equals(dependType.getName());
            }
        }
        return false;
    }
    
    public boolean isIssueDependencyResolved(String xmlIssueId)
    {
        ArrayList dependencyList = (ArrayList) getIssueDependencies(xmlIssueId);
        if(dependencyList == null)
        {
            return true;
        }
        for(int i = 0; i < dependencyList.size(); i++)
        {
            DependencyNode node = (DependencyNode) dependencyList.get(i);
            if(!node.isResolved())
            {
                return false;
            }
        }
        return true;
    }
    
    public boolean isModuleDependencyValid(NumberKey parentModuleId)
    {
        Enumeration childModuleIdList = moduleDependTree.keys();
        while(childModuleIdList.hasMoreElements())
        {
            NumberKey childModuleId = (NumberKey) childModuleIdList.nextElement();
            if(childModuleId.equals(parentModuleId))
            { 
                return true;
            }
        }
        return false;
    }
    
    public ArrayList getInvalidIssueDependencies()
    {
        ArrayList invalidList = new ArrayList();
        Enumeration xmlIdList = issueDependTree.keys();
        while(xmlIdList.hasMoreElements())
        {
            String xmlIssueId = (String) xmlIdList.nextElement();
            ArrayList dependencyList = getIssueDependencies(xmlIssueId);
            for(int i = 0; i < dependencyList.size(); i++)
            {
                DependencyNode node = (DependencyNode)dependencyList.get(i);
                if(node != null)
                {
                    String dependencyXmlId = node.getParentOrChildId();
                    if(!isIssueDependencyValid(node))
                    {
                        invalidList.add(node);
                    }
                }
            }
        }
        return invalidList;
    }
    
    public ArrayList getUnresolvedDependencyIssues()
    {
        ArrayList unresolvedList = new ArrayList();
        Enumeration xmlIdList = issueDependTree.keys();
        while(xmlIdList.hasMoreElements())
        {
            String xmlIssueId = (String) xmlIdList.nextElement();
            if(!isIssueDependencyResolved(xmlIssueId))
            {
                unresolvedList.add(xmlIssueId);
            }
        }
        return unresolvedList;
    }
    
    public boolean isAllIssueDependencyResolved()
    {
        return (getUnresolvedDependencyIssues().size() == 0 );
    }
    
    public void resolveIssueDependencies() throws Exception
    {
        if(!isAllIssueDependencyResolved())
        {
            cat.debug("resolving remaining issue dependencies ...");
            
            ArrayList unresolvedIssueList = getUnresolvedDependencyIssues();
            
            for(int i = 0; i < unresolvedIssueList.size(); i++)
            {
                String unresolvedIssueId = (String)unresolvedIssueList.get(i);
                ArrayList unresolvedDependencies = getIssueDependencies(unresolvedIssueId);
                for(int j = 0; j < unresolvedDependencies.size(); j++)
                {
                    DependencyNode node = (DependencyNode)unresolvedDependencies.get(j);
                    Depend depend = Depend.getInstance();
                    depend.setDependType(node.getDependType());
//                    if(node.getNodeType().equals(DependencyNode.NODE_TYPE_CHILD))
//                    {
//                        depend.setObserverId(getIssueId(node.getParentOrChildId()));
//                        depend.setObservedId(getIssueId(unresolvedIssueId));
//                        depend.save();
//                    }
//we only need to insert the same depend relationship ONCE
                    if (node.getNodeType().equals(DependencyNode.NODE_TYPE_PARENT))
                    {
                        depend.setObserverId(getIssueId(unresolvedIssueId));
                        depend.setObservedId(getIssueId(node.getParentOrChildId()));
                        depend.save();
                    }
                }
            }
        }
    }  
    
    public ArrayList getInvalidModuleDependencies()
    {
        ArrayList invalidList = new ArrayList();
        Enumeration childModuleIdList = moduleDependTree.keys();
        while(childModuleIdList.hasMoreElements())
        {
            NumberKey childModuleId = (NumberKey) childModuleIdList.nextElement();
            NumberKey parentModuleId = getModuleDependency(childModuleId);
            if(!isModuleDependencyValid(parentModuleId))
            {
                invalidList.add(childModuleId);
            }
        }
        return invalidList;
    }
    
    public String getInvalidIssueDependencyInfo()
    {
        StringBuffer info = new StringBuffer();
        ArrayList dependencies = getInvalidIssueDependencies();
        for(int i = 0; i < dependencies.size(); i++)
        {
            int errorNo = i + 1;
            DependencyNode node = (DependencyNode) dependencies.get(i);
            info.append("<validation error " + errorNo + "> issue: " + node.getIssueId() + " has either an unknown depend issue: " 
                            + node.getParentOrChildId() + " or their depend types don't match" 
                       + " Or their parent/child doesn't match\n");
        }
        return info.toString();
    }
    
    public String getInvalidModuleDependencyInfo()
    {
        StringBuffer info = new StringBuffer();
        ArrayList dependencies = getInvalidModuleDependencies();
        for(int i = 0; i < dependencies.size(); i++)
        {
            NumberKey childModuleId = (NumberKey) dependencies.get(i);
            info.append("<validation error> module: " + childModuleId + " has an unresolved parent module: " + getModuleDependency(childModuleId) + "\n");
        }
        
        return info.toString();
    }
    
    public boolean isAllIssueDependencyValid()
    {
        return (getInvalidIssueDependencies().size() == 0 );
    }
    
    public boolean isAllModuleDependencyValid()
    {
        return (getInvalidModuleDependencies().size() == 0 );
    }
    
    public boolean isIssueResolvedYet(String xmlIssueId)
    {
        if(getIssueId(xmlIssueId) != null)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
}