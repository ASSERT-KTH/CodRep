IGroupModelPartial groupPartial = new GroupModelPartial(folder.getId(), group

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

import java.util.Iterator;
import java.util.Map;

import org.columba.addressbook.folder.IContactFolder;

public class ContactModelFactory {

	public static IGroupModelPartial createGroupPartial(IGroupModel group,
			IContactFolder folder) {
		if (group == null)
			throw new IllegalArgumentException("group == null");
		if (folder == null)
			throw new IllegalArgumentException("folder == null");

		IGroupModelPartial groupPartial = new GroupPartial(folder.getId(), group
				.getName(), group.getDescription());

		// retrieve list of all group members
		String[] members = group.getMembers();
		Map<String, IContactModelPartial> map = folder
				.getContactItemMap(members);

		Iterator<IContactModelPartial> it = map.values().iterator();
		while (it.hasNext()) {
			IContactModelPartial partial = it.next();

			groupPartial.addContact(partial);
		}
		
		return groupPartial;
	}

	public static IContactModelPartial createContactModelPartial(
			IContactModel model, String id) {
		if (model == null)
			throw new IllegalArgumentException("model == null");
		if (id == null)
			throw new IllegalArgumentException("id == null");

		String sortString = model.getSortString();

		// @author: fdietz
		// This is a workaround. Generally, the contact dialog editor
		// should ensure that all necessary fields are available
		// 

		// fall-back to formatted name
		if (sortString == null || sortString.length() == 0)
			sortString = model.getFormattedName();

		// fall-back to email address
		if (sortString == null || sortString.length() == 0)
			sortString = model.getPreferredEmail();

		IContactModelPartial item = new ContactModelPartial(id, sortString,
				model.getGivenName(), model.getFamilyName(), model
						.getPreferredEmail(), model.getHomePage());

		return item;
	}
}