return activeDesktop.openAndWait(file);

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
package org.columba.core.desktop;

import java.io.File;
import java.net.URL;

import org.columba.api.desktop.IDesktop;
import org.columba.core.io.DefaultMimeTypeTable;

public class ColumbaDesktop implements IDesktop {

	private static ColumbaDesktop instance = new ColumbaDesktop();
	
	IDesktop activeDesktop;
	
	protected ColumbaDesktop() {
		activeDesktop = new DefaultDesktop();
	}

	public String getMimeType(File file) {
		String mimeType = activeDesktop.getMimeType(file);
		if( mimeType.equals("application/octet-stream")) {
			// Try the built-in mime table
			return DefaultMimeTypeTable.lookup(file);
		} else {
			return mimeType;
		}
	}

	public String getMimeType(String ext) {
		String mimeType = activeDesktop.getMimeType(ext);
		if( mimeType.equals("application/octet-stream")) {
			// Try the built-in mime table
			return DefaultMimeTypeTable.lookup(ext);
		} else {
			return mimeType;
		}
	}

	public boolean supportsOpen() {
		return activeDesktop.supportsOpen();
	}

	public boolean open(File file) {
		return activeDesktop.open(file);
	}

	public boolean openAndWait(File file) {
		return activeDesktop.open(file);
	}

	public boolean supportsBrowse() {
		return activeDesktop.supportsBrowse();
	}

	public void browse(URL url) {
		activeDesktop.browse(url);
	}

	/**
	 * @return Returns the activeDesktop.
	 */
	public IDesktop getActiveDesktop() {
		return activeDesktop;
	}

	/**
	 * @param activeDesktop The activeDesktop to set.
	 */
	public void setActiveDesktop(IDesktop activeDesktop) {
		this.activeDesktop = activeDesktop;
	}

	/**
	 * @return Returns the instance.
	 */
	public static ColumbaDesktop getInstance() {
		return instance;
	}

}