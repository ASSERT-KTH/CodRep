public class PopItem extends IncomingItem {

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

/* -*-mode: java; compile-command:"javac PopItem.java -classpath ../"; -*- */
package org.columba.mail.config;

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;


public class PopItem extends DefaultItem {
	
    public static final String DOWNLOAD_LIMIT = "download_limit";
	public static final String ENABLE_DOWNLOAD_LIMIT = "enable_download_limit";
	public static final String EXCLUDE_FROM_CHECKALL = "exclude_from_checkall";
	public static final String OLDER_THAN = "older_than";
	public static final String REMOVE_OLD_FROM_SERVER = "remove_old_from_server";
	public static final String LEAVE_MESSAGES_ON_SERVER = "leave_messages_on_server";

	public PopItem(XmlElement e) {
        super(e);
    }
}