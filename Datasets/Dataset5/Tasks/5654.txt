static final String Javadoc_NotFound = "Javadoc_NotFound";

/*******************************************************************************
 * Copyright (c) 2007 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.internal.presence.bot.kosmos;

import java.util.MissingResourceException;
import java.util.ResourceBundle;

public class CustomMessages {
	
	static final String No_Operation_Privileges = "No_Operation_Privileges";
	static final String Learn_Failure = "Learn_Failure";
	static final String Learn_Reply = "Learn_Reply";
	static final String Learn_Conflict = "Learn_Conflict";
	static final String Learn_Update = "Learn_Update";
	static final String Learn_Remove = "Learn_Remove";

	static final String Bug = "Bug";
	static final String Bug_Reply = "Bug_Reply";

	static final String BugContent = "BugContent";
	static final String BugContent_Reply = "BugContent_Reply";

	static final String Javadoc_NotFound = "Javadoc_notFound";
	static final String Javadoc_ResultsUnknown = "Javadoc_ResultsUnknown";

	static final String NewsgroupSearch = "NewsgroupSearch";
	static final String NewsgroupSearch_Reply = "NewsgroupSearch_Reply";

	static final String Google = "Google";
	static final String Google_Reply = "Google_Reply";

	static final String Wiki = "Wiki";
	static final String Wiki_Reply = "Wiki_Reply";

	static final String EclipseHelp = "EclipseHelp";
	static final String EclipseHelp_Reply = "EclipseHelp_Reply";

	private static final String RESOURCE_BUNDLE = "org.eclipse.ecf.internal.presence.bot.kosmos.custom"; //$NON-NLS-1$

	private final static ResourceBundle BUNDLE = ResourceBundle
			.getBundle(RESOURCE_BUNDLE);

	/**
	 * A private constructor to prevent instantiation.
	 */
	private CustomMessages() {
		// do nothing
	}

	public static String getString(String key) {
		try {
			return BUNDLE.getString(key);
		} catch (MissingResourceException e) {
			return "!" + key + "!";
		}
	}

	public static ResourceBundle getResourceBundle() {
		return BUNDLE;
	}

}