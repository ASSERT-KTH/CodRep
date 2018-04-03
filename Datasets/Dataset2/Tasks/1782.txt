AbstractMessageFolder child = (AbstractMessageFolder) folder.getChildAt(0);

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.
package org.columba.mail.filter;

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;
import org.columba.mail.folder.virtual.VirtualFolder;


public class SearchItem extends DefaultItem {
    /*
private AdapterNode vFolderNode;
private VirtualFolder vFolder;
private Filter filter;
private AdapterNode searchNode;
*/
    public SearchItem(XmlElement root) {
        super(root);

        /*
this.vFolderNode = node;
this.vFolder = vFolder;

vFolder.setSearchFilter(this);

if (node != null)
        parseNode();
*/
    }

    /*
public VirtualFolder getFolder() {
        return vFolder;
}

protected void parseNode() {
        searchNode = vFolderNode.getChild("search");
        AdapterNode filterNode = searchNode.getChild("filter");

        filter = new Filter(filterNode);

}

public Filter getFilter() {
        return filter;
}

public int getUid() {
        AdapterNode uidNode = searchNode.getChild("uid");
        String uidStr = getTextValue(uidNode);
        Integer iStr = new Integer(uidStr);
        int uid = iStr.intValue();

        return uid;
}

public void setUid(int i) {
        Integer uid = new Integer(i);

        AdapterNode uidNode = searchNode.getChild("uid");

        setTextValue(uidNode, uid.toString());

}

public void setInclude(String s) {
        AdapterNode includeNode = searchNode.getChild("include");
        setTextValue(includeNode, s);
}

public boolean isInclude() {
        AdapterNode includeNode = searchNode.getChild("include");
        String include = getTextValue(includeNode);

        if (include.equals("true"))
                return true;
        else
                return false;
}
*/
    public void addSearchToHistory(VirtualFolder folder) {
        if (folder.getUid() == 106) {
            addSearchToHistory();
        }
    }

    public void addSearchToHistory() {
        /*
//System.out.println("selectedfolder:"+ MainInterface.treeViewer.getSelected().getName());
VirtualFolder folder =
        (VirtualFolder) MainInterface.treeModel.getFolder(106);

if (folder.getChildCount() >= 10)
{
        MessageFolder child = (MessageFolder) folder.getChildAt(0);
        child.removeFromParent();
}

String name = "search result";
VirtualFolder vFolder2 =
        (VirtualFolder) MainInterface.treeModel.addVirtualFolder(folder, name);
Search s = vFolder2.getSearchFilter();
s.setUid(getUid());
s.setInclude((new Boolean(isInclude())).toString());
s.getFilter().getFilterRule().removeAll();
s.getFilter().getFilterRule().setCondition(
        getFilter().getFilterRule().getCondition());
for (int i = 0; i < getFilter().getFilterRule().count(); i++)
{
        FilterCriteria c = getFilter().getFilterRule().getCriteria(i);
        s.getFilter().getFilterRule().addEmptyCriteria();
        FilterCriteria newc = s.getFilter().getFilterRule().getCriteria(i);
        newc.setCriteria(c.getCriteria());
        newc.setHeaderItem(c.getHeaderItem());
        newc.setPattern(c.getPattern());
        newc.setType(c.getType());

        if (i == 0)
        {
                // lets find a good name for our new vfolder

                StringBuffer buf = new StringBuffer();

                if (newc.getType().equalsIgnoreCase("flags"))
                {
                        System.out.println("flags found");

                        buf.append(newc.getType());
                        buf.append(" (");
                        buf.append(newc.getCriteria());
                        buf.append(" ");
                        buf.append(newc.getPattern());
                        buf.append(")");
                }
                else if (newc.getType().equalsIgnoreCase("custom headerfield"))
                {

                        buf.append(newc.getHeaderItem());
                        buf.append(" (");
                        buf.append(newc.getCriteria());
                        buf.append(" ");
                        buf.append(newc.getPattern());
                        buf.append(")");
                }
                else
                {
                        buf.append(newc.getType());
                        buf.append(" (");
                        buf.append(newc.getCriteria());
                        buf.append(" ");
                        buf.append(newc.getPattern());
                        buf.append(")");

                }
                System.out.println("newname:" + buf);

                vFolder2.setName(buf.toString());
                TreeNodeEvent updateEvent2 = new TreeNodeEvent(vFolder2, TreeNodeEvent.UPDATE);
                MainInterface.crossbar.fireTreeNodeChanged(updateEvent2);
        }

}
*/
    }
}