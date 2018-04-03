public final static String SELECTED_BROWSER = "selected_browser";

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
package org.columba.mail.config;

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;

/**
 * User interface specific options, including configuration settings for
 * the tree view, the message list and the message preview component.
 * 
 * @author fdietz
 */

// 
// options.xml
//
//<options>
// <gui>
//  <messageviewer inline_attachments="false">
//   <smilies enabled="true" />
//   <quote color="0" enabled="true" />
//  </messageviewer>
//  <tree>
//   <sorting sorted="true" ascending="true" comparator="alphabetic" />
//  </tree>
// </gui>
// <html prefer="true" />
// <markasread delay="2" enabled="true" />
// <headerviewer style="0" headerfields="Subject Date Reply-To From To Cc Bcc" />
//</options>

public class OptionsItem extends DefaultItem {

	public final static String MESSAGEVIEWER = "gui/messageviewer";
	
	public final static String MESSAGEVIEWER_SMILIES = "gui/messageviewer/smilies";
	
	public final static String MESSAGEVIEWER_QUOTE = "gui/messageviewer/quote";
	
	public final static String TREE = "gui/tree";
	
	public final static String TREE_SORTING = "gui/tree/sorting";
	
	public final static String ENABLED_BOOL = "enabled";
	
	public final static String DISABLE_BOOL = "disable";
	
	public final static String SORTED_BOOL = "sorted";
	
	public final static String ASCENDING_BOOL = "ascending";
	
	public final static String COMPARATOR = "comparator";
	
	public final static String HTML = "html";
	
	public final static String PREFER_BOOL = "prefer";
	
	public final static String MARKASREAD = "markasread";
	
	public final static String DELAY_INT = "delay";
	
	public final static String HEADERVIEWER = "headerviewer";
	
	public final static String STYLE_INT = "style";
	
	public final static String HEADERFIELDS = "headerfields";
	
	public final static String INLINE_ATTACHMENTS_BOOL = "inline_attachments";
	
	public final static String USE_SYSTEM_DEFAULT_BROWSER = "use_system_default_browser";
	
	/**
	 * @param root
	 */
	public OptionsItem(XmlElement root) {
		super(root);
	}

}