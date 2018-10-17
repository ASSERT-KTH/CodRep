public void add(Object uid, IContactItem contactItem) {

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

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * @author fdietz
 *
 */
public class ContactItemMap {

	private Map map;
	
	public ContactItemMap() {
		map = new HashMap();
	}
	
	
	public void add(Object uid, ContactItem contactItem) {
		map.put(uid, contactItem);
	}
	
	public ContactItem get(Object uid) {
		return (ContactItem) map.get(uid);
	}
	
	public void remove(Object uid) {
		
		map.remove(uid);
	}
	
	public boolean exists(Object uid) {
		if ( map.containsKey(uid)) return true;
		
		return false;
	}
	
	public int count() {
		return map.size();
	}
	
	public Iterator iterator() {
		Iterator it = map.values().iterator();
		
		return it;
	}
	
	public void clear() {
		map.clear();
	}
}