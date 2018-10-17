public class GroupPartial extends HeaderItemPartial implements IGroupModelPartial {

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.addressbook.model;

import java.util.List;
import java.util.Vector;

/**
 * @author fdietz
 * 
 */
public class GroupPartial extends HeaderItemPartial implements IGroupPartial {

	private List<IContactModelPartial> list = new Vector<IContactModelPartial>();
	
	/**
	 * 
	 */
	public GroupPartial() {
		super(false);
	}

	/**
	 * @param group
	 */
	public GroupPartial(String id) {
		super(id, false);

	}

	public GroupPartial(String id, String name, String description) {
		this(id);

		this.name = name;
		this.description = description;

	}

	public List<IContactModelPartial> retrieveContacts() {
		return list;
	}

	public void addContact(IContactModelPartial modelPartial) {
		if ( modelPartial == null ) throw new IllegalArgumentException("modelPartial == null");
		
		list.add(modelPartial);
	}

	public void removeContact(IContactModelPartial modelPartial) {
		if ( modelPartial == null ) throw new IllegalArgumentException("modelPartial == null");
		
		list.remove(modelPartial);
	}

	public int getContactCount() {
		return list.size();
	}

}