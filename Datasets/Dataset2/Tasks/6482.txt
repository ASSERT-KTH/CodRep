ShutdownManager.getInstance().register(this);

//The contents of this file are subject to the Mozilla Public License Version
//1.1
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
//Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.

package org.columba.mail.folder.imap;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import org.columba.core.config.Config;
import org.columba.core.io.StreamCache;
import org.columba.core.shutdown.ShutdownManager;

public class IMAPCache implements Runnable {

	//TODO:add a configuration of the cache size
	
	private StreamCache cache;
	private static IMAPCache instance = new IMAPCache();
	
	protected IMAPCache() {
		File configDir = Config.getInstance().getConfigDirectory();
		cache = new StreamCache(new File(configDir, "imap_cache"));
		
		ShutdownManager.getShutdownManager().register(this);
	}
	
	public static IMAPCache getInstance() {
		return instance;
	}
	
	public InputStream addMimeBody(IMAPFolder folder, Object uid, Integer[] address, InputStream data ) throws IOException {
		return cache.passiveAdd(createMimeBodyKey(folder, uid, address), data);
	}
	
	public InputStream getMimeBody(IMAPFolder folder, Object uid, Integer[] address) {
		return cache.get(createMimeBodyKey(folder, uid, address));
	}
	
	protected String createMimeBodyKey(IMAPFolder folder, Object uid, Integer[] address) {
		return Integer.toString(folder.getUid()) + uid.toString() +  addressToString(address);
	}
	
	protected String addressToString(Integer[] address) {
		String result = address[0].toString();
		for(int i=1; i<address.length; i++) {
			result += "." + address[i];
		}
		
		return result;
	}

	public void run() {
		cache.clear();
	}
}