import org.columba.mail.folder.headercache.HeaderList;

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
package org.columba.addressbook.facade;

import org.columba.addressbook.model.Contact;
import org.columba.addressbook.model.ContactItem;
import org.columba.addressbook.model.GroupItem;
import org.columba.addressbook.model.HeaderItem;
import org.columba.addressbook.model.HeaderItemList;
import org.columba.addressbook.model.IContact;
import org.columba.addressbook.model.IContactItem;
import org.columba.addressbook.model.IGroupItem;
import org.columba.addressbook.model.IHeaderItem;
import org.columba.addressbook.model.IHeaderItemList;
import org.columba.mail.message.HeaderList;
import org.columba.mail.message.IHeaderList;

/**
 * Builder for creating contact models.
 * 
 * @author fdietz
 */
public class ModelFacade implements IModelFacade {

	/**
	 * @see org.columba.addressbook.facade.IModelFacade#createHeaderItemList()
	 */
	public IHeaderItemList createHeaderItemList() {
		return new HeaderItemList();
	}

	/**
	 * @see org.columba.addressbook.facade.IModelFacade#createHeaderItem()
	 */
	public IHeaderItem createHeaderItem() {
		return new HeaderItem();
	}

	/**
	 * @see org.columba.addressbook.facade.IModelFacade#createContactItem()
	 */
	public IContactItem createContactItem() {
		return new ContactItem();
	}

	/**
	 * @see org.columba.addressbook.facade.IModelFacade#createGroupItem()
	 */
	public IGroupItem createGroupItem() {
		return new GroupItem();
	}

	/**
	 * @see org.columba.addressbook.facade.IModelFacade#createContact()
	 */
	public IContact createContact() {
		return new Contact();
	}

	/**
	 * @see org.columba.addressbook.facade.IModelFacade#createHeaderList()
	 */
	public IHeaderList createHeaderList() {
		return new HeaderList();
	}

}