new File(configDirectory, "options.xml");

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
package org.columba.mail.config;

import java.io.File;

import org.columba.core.config.DefaultConfig;
import org.columba.core.config.DefaultXmlConfig;
import org.columba.core.xml.XmlElement;

/**
 * @author frd
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class MailConfig extends DefaultConfig {

	public static final String MODULE_NAME = "mail";

	private static File accountFile;
	private static File accountTemplateFile;

	private static File folderFile;
	private static File mainFrameOptionsFile;
	private static File popManageOptionsFile;
	private static File composerOptionsFile;

	//private static File filterActionFile;
	//private static File localFilterFile;
	//private static File remoteFilterFile;

	/**
	 * @see java.lang.Object#Object()
	 */
	public MailConfig() {

		File configDirectory = createConfigDir(MODULE_NAME);

		accountFile = new File(configDirectory, "account.xml");
		registerPlugin(
			accountFile.getName(),
			new AccountXmlConfig(accountFile));

		accountTemplateFile = new File("account_template.xml");
		registerTemplatePlugin(
			accountTemplateFile.getName(),
			new AccountTemplateXmlConfig(accountTemplateFile));

		folderFile = new File(configDirectory, "tree.xml");
		registerPlugin(folderFile.getName(), new FolderXmlConfig(folderFile));

		mainFrameOptionsFile =
			new File(configDirectory, "mainframeoptions.xml");
		registerPlugin(
			mainFrameOptionsFile.getName(),
			new MainFrameOptionsXmlConfig(mainFrameOptionsFile));

		/*
		popManageOptionsFile =
			new File(configDirectory, "popmanageoptions.xml");
		registerPlugin(
			popManageOptionsFile.getName(),
			new PopManageOptionsXmlConfig(popManageOptionsFile));
		*/
		
		composerOptionsFile = new File(configDirectory, "composeroptions.xml");
		registerPlugin(
			composerOptionsFile.getName(),
			new ComposerOptionsXmlConfig(composerOptionsFile));

		/*
		filterActionFile = new File(configDirectory, "filter_actions.xml");
		registerPlugin(
			filterActionFile.getName(),
			new FilterActionXmlConfig(filterActionFile));
		*/

		/*
		localFilterFile = new File(configDirectory, "filter_local.xml");
		registerPlugin(
			localFilterFile.getName(),
			new LocalFilterXmlConfig(localFilterFile));
		remoteFilterFile = new File(configDirectory, "filter_remote.xml");
		registerPlugin(
			remoteFilterFile.getName(),
			new LocalFilterXmlConfig(remoteFilterFile));
		*/

	}

	/**
	 * Method registerPlugin.
	 * @param id
	 * @param plugin
	 */
	protected static void registerPlugin(String id, DefaultXmlConfig plugin) {
		DefaultConfig.registerPlugin(MODULE_NAME, id, plugin);
	}

	protected static void registerTemplatePlugin(
		String id,
		DefaultXmlConfig plugin) {
		DefaultConfig.registerTemplatePlugin(MODULE_NAME, id, plugin);
	}

	/**
	 * Method getPlugin.
	 * @param id
	 * @return DefaultXmlConfig
	 */
	protected static DefaultXmlConfig getPlugin(String id) {
		return DefaultConfig.getPlugin(MODULE_NAME, id);
	}

	protected static DefaultXmlConfig getTemplatePlugin(String id) {
		return DefaultConfig.getTemplatePlugin(MODULE_NAME, id);
	}

	/**
	 * Method getAccountList.
	 * @return AccountList
	 */
	public static AccountList getAccountList() {
		return getAccountConfig().getAccountList();
	}

	public static AccountTemplateXmlConfig getAccountTemplateConfig() {
		return (AccountTemplateXmlConfig) getTemplatePlugin(
			accountTemplateFile.getName());
	}

	public static XmlElement get(String name) {
		DefaultXmlConfig xml = getPlugin(name + ".xml");
		return xml.getRoot();
	}

	/**
	 * Method getAccountConfig.
	 * @return AccountXmlConfig
	 */
	public static AccountXmlConfig getAccountConfig() {
		//return accountConfig;

		return (AccountXmlConfig) getPlugin(accountFile.getName());
	}

	/*
	public static FilterActionXmlConfig getFilterActionConfig() {
		return (FilterActionXmlConfig) getPlugin(filterActionFile.getName());
	}
	*/
	/*
	public static LocalFilterXmlConfig getLocalFilterConfig() {
		return (LocalFilterXmlConfig) getPlugin(localFilterFile.getName());
	}
	public static RemoteFilterXmlConfig getRemoteFilterConfig() {
		return (RemoteFilterXmlConfig) getPlugin(remoteFilterFile.getName());
	}
	*/

	/**
	 * Method getFolderConfig.
	 * @return FolderXmlConfig
	 */
	public static FolderXmlConfig getFolderConfig() {
		//return folderConfig;

		return (FolderXmlConfig) getPlugin(folderFile.getName());
	}

	/**
	 * Method getMainFrameOptionsConfig.
	 * @return MainFrameOptionsXmlConfig
	 */
	public static MainFrameOptionsXmlConfig getMainFrameOptionsConfig() {
		//return mainFrameOptionsConfig;
		return (MainFrameOptionsXmlConfig) getPlugin(
			mainFrameOptionsFile.getName());
	}

	

	/**
	 * Method getComposerOptionsConfig.
	 * @return ComposerOptionsXmlConfig
	 */
	public static ComposerOptionsXmlConfig getComposerOptionsConfig() {
		//return composerOptionsConfig;

		return (ComposerOptionsXmlConfig) getPlugin(
			composerOptionsFile.getName());
	}

}