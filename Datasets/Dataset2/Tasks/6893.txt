handler = PluginManager.getInstance().getExtensionHandler(

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

package org.columba.mail.folder;

import java.util.Enumeration;
import java.util.LinkedList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.columba.api.exception.PluginHandlerNotFoundException;
import org.columba.api.plugin.ExtensionMetadata;
import org.columba.api.plugin.IExtension;
import org.columba.api.plugin.IExtensionHandler;
import org.columba.core.plugin.PluginManager;
import org.columba.mail.config.IFolderItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.plugin.IExtensionHandlerKeys;

/**
 * Factory for creating subfolders. Implemented as a singelton. Use
 * {@link #getInstance()}.
 * 
 * @author Timo Stich <tstich@users.sourceforge.net>
 */
public class FolderFactory {
	// Groups are separated by at least one WS character
	private static final Pattern groupPattern = Pattern
			.compile("([^\\s]+)\\s*");

	private static FolderFactory instance;

	private IExtensionHandler handler;

	// parent directory for mail folders
	// for example: ".columba/mail/"
	private String path = MailConfig.getInstance().getConfigDirectory()
			.getPath();

	protected FolderFactory() throws PluginHandlerNotFoundException {
		// Get the handler
		handler = PluginManager.getInstance().getHandler(
				IExtensionHandlerKeys.ORG_COLUMBA_MAIL_FOLDER);

	}

	/**
	 * Singleton - pattern
	 * 
	 * @return the instance of the factory
	 */
	public static FolderFactory getInstance() {
		if (instance == null) {
			try {
				instance = new FolderFactory();
			} catch (PluginHandlerNotFoundException phnfe) {
				throw new RuntimeException(phnfe);
			}
		}
		return instance;
	}

	/**
	 * Gets a list of all possible child foldertypes.
	 * 
	 * @param parent
	 * @return a list that contains Strings of foldertypes
	 */
	public List getPossibleChilds(IMailFolder parent) {
		List list = new LinkedList();

		// which parents are possible ?
		IFolderItem item = parent.getConfiguration();
		String parentType = item.get("type");

		// the group of the given parent
		String parentGroup = getGroup(parentType);

		// iterate through all foldertypes to find suitable ones
		Enumeration e = handler.getExtensionEnumeration();
		while (e.hasMoreElements()) {
			IExtension extension = (IExtension) e.nextElement();
			ExtensionMetadata metadata = (ExtensionMetadata) extension.getMetadata();
			String possibleParents = metadata.getAttribute("possible_parents");
			String id = metadata.getId();

			if (possibleParents != null) {
				Matcher matcher = groupPattern.matcher(possibleParents);

				while (matcher.find()) {
					if (matcher.group(1).equals(parentGroup)
							|| matcher.group(1).equals("all")) {
						list.add(id);
					}
				}
			}
		}

		return list;
	}

	/**
	 * Creates the default child for the given parent.
	 * 
	 * @param parent
	 *            the parent folder
	 * @return the childfolder
	 * @throws Exception
	 */
	public IMailFolder createDefaultChild(IMailFolder parent, String name)
			throws FolderCreationException {
		List possibleChilds = getPossibleChilds(parent);

		if (possibleChilds.size() > 0) {
			String childType = (String) possibleChilds.get(0);
			return createChild(parent, name, childType);
		} else {
			return null;
		}
	}

	/**
	 * Creates a subfolder for the given folder with the given type.
	 * 
	 * @param parent
	 *            the parentfolder
	 * @param childType
	 *            the type of the child (e.g. CachedMHFolder )
	 * @return the childfolder
	 * @throws Exception
	 */
	public IMailFolder createChild(IMailFolder parent, String name,
			String childType) throws FolderCreationException {
		IMailFolder child;
		try {
			IExtension extension = handler.getExtension(childType);

			child = (IMailFolder) extension.instanciateExtension(new Object[] {
					name, childType, path });

			// Add child to parent
			parent.addSubfolder(child);
		} catch (Exception e) {
			throw new FolderCreationException(e);
		}
		return child;
	}

	public String getGroup(String parentType) {
		// iterate through all foldertypes to find suitable ones
		Enumeration e = handler.getExtensionEnumeration();
		while (e.hasMoreElements()) {
			IExtension extension = (IExtension) e.nextElement();
			ExtensionMetadata metadata = (ExtensionMetadata) extension.getMetadata();
			String id = metadata.getId();
			String group = metadata.getAttribute("group");

			if (id.equals(parentType))
				return group;
		}

		return null;

	}
}