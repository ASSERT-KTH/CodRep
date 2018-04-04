rules.addAttribute("condition", "matchall");

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
//All Rights Reserved.undation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.filter;

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;

public class FilterList extends DefaultItem {
	//private Vector list;
	// private Folder folder;

	public FilterList(XmlElement root) {
		super(root);
	}

	/*
	public FilterList( Folder folder )
	{
	    this.folder = folder;
	    folder.setFilterList( this );
	    list = new Vector();
	
	    FolderItem item = folder.getFolderItem();
	    AdapterNode filterListNode = item.getFilterListNode();
	
	    if ( filterListNode != null )
	    {
	        AdapterNode child;
	        for ( int i=0; i< filterListNode.getChildCount(); i++)
	        {
	            child = (AdapterNode) filterListNode.getChild( i );
	            Filter filter = new Filter( child );
	            filter.setFolder( folder );
	            add( filter );
	        }
	    }
	}
	*/

	public void removeAllElements() {
		getRoot().removeAllElements();
		/*
		list.removeAllElements();
		getFilterListNode().removeChildren();
		*/
	}

	/*
	public void clear()
	{
		
	    if ( list.size() > 0 )
	        list.clear();
	}
	*/

	public static Filter createEmptyFilter() {
		XmlElement filter = new XmlElement("filter");
		filter.addAttribute("description", "new filter");
		filter.addAttribute("enabled","true");
		XmlElement rules = new XmlElement("rules");
		rules.addAttribute("condition", "match_all");
		XmlElement criteria = new XmlElement("criteria");
		criteria.addAttribute("type", "Subject");
		criteria.addAttribute("headerfield", "Subject");
		criteria.addAttribute("criteria", "contains");
		criteria.addAttribute("pattern", "pattern");
		rules.addElement(criteria);
		filter.addElement(rules);

		XmlElement actionList = new XmlElement("actionlist");
		XmlElement action = new XmlElement("action");
		/*
		action.addAttribute(
			"class",
			"org.columba.mail.filter.action.MarkMessageAsReadFilterAction");
		*/
		
		action.addAttribute("type","Mark as Read");
		
		actionList.addElement(action);
		filter.addElement(actionList);

		
		
		//XmlElement.printNode(getRoot(),"");
		
		return new Filter(filter);
		/*
		//AdapterNode filterListNode = getFilterListNode();
		
		AdapterNode node = MailConfig.getFolderConfig().addEmptyFilterNode( getFolder().getNode() );
		Filter filter = new Filter( node );
		
		add( filter );
		
		return filter;
		*/

	}

	public void add(Filter f) {
		getRoot().addElement(f.getRoot());
		
		//list.add(f);
	}

	public int count() {

		return getChildCount();

	}

	public Filter get(int index) {

		Filter filter = new Filter(getRoot().getElement(index));

		return filter;
	}

	public void remove(int index) {
		getRoot().removeElement(index);

	}

}