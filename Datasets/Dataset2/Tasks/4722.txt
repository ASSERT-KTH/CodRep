import org.columba.addressbook.config.AdapterNode;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.filter;

import java.util.Vector;

import org.columba.core.config.AdapterNode;
import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;

public class FilterRule extends DefaultItem {

	// Condition
	public final static int MATCH_ALL = 0;
	public final static int MATCH_ANY = 1;

	// list of FilterCriteria
	private Vector list;

	// condition: match all (AND) = 0, match any (OR) = 1
	private AdapterNode conditionNode;

	public FilterRule(XmlElement root) {
		super(root);

		list = new Vector();

	}

	public void addEmptyCriteria() {
		XmlElement criteria = new XmlElement("criteria");
		criteria.addAttribute("type", "Subject");
		criteria.addAttribute("criteria", "contains");
		criteria.addAttribute("pattern", "pattern");

		getRoot().addElement(criteria);
		/*
		AdapterNode n =
			MailConfig.getFolderConfig().addEmptyFilterCriteria(getRootNode());
		FilterCriteria criteria = new FilterCriteria(n, getDocument());
		
		list.add(criteria);
		*/
	}

	public void remove(int index) {
		getRoot().removeElement(index);
		/*
		if ((index >= 0) && (index < list.size())) {
			list.remove(index);
		
			int result = -1;
		
			for (int i = 0; i < getRootNode().getChildCount(); i++) {
				AdapterNode child = (AdapterNode) getRootNode().getChildAt(i);
				String name = child.getName();
		
				if (name.equals("filtercriteria"))
					result++;
		
				if (result == index) {
					child.remove();
					break;
				}
			}
		
			//AdapterNode child = getRootNode().getChildAt(index);
		
		}
		*/
	}

	public void removeAll() {
		/*
		for (int i = 0; i < count(); i++) {
			remove(0);
		}
		*/
		getRoot().removeAllElements();
	}

	public void removeLast() {
		/*
		int index = list.size() - 1;
		
		remove(index);
		*/

		getRoot().removeElement(getRoot().count() - 1);

	}

	public FilterCriteria get(int index) {
		return new FilterCriteria(getRoot().getElement(index));
	}

	public int count() {
		return getRoot().count();
	}

	public String getCondition() {
		return getRoot().getAttribute("condition");
		/*
		if (conditionNode == null) {
			System.out.println(
				"---------------------------> failure: conditionNode == null !");
		
			return new String("matchany");
		} else
			return getTextValue(conditionNode);
		*/
	}

	public void setCondition(String s) {
		getRoot().addAttribute("condition", s);
		/*
		setTextValue(conditionNode, s);
		*/
	}

	/*
	public FilterCriteria getCriteria(int index) {
		return (FilterCriteria) list.get(index);
	}
	*/

	public int getConditionInt() {
		//System.out.println("condigtion: "+ condition );

		if (getCondition().equals("matchall"))
			return MATCH_ALL;
		if (getCondition().equals("matchany"))
			return MATCH_ANY;
		return -1;
	}

}