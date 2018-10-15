public static final String ATT_CONTAINER_TYPE_NAME = "containerFactoryName";

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.internal.ui.wizards;

import org.eclipse.ecf.internal.ui.Activator;

public interface IWizardRegistryConstants {

	public static final String ATT_ID = "id";

	public static final String ATT_NAME = "name";

	public static final String ATT_CLASS = "class";

	public static final String ATT_DESCRIPTION = "description";

	public static final String ATT_ICON = "icon";

	public static final String ATT_DESCRIPTION_IMAGE = "descriptionImage";

	public static final String ELEMENT_WIZARD = "wizard";

	public static final String ELEMENT_CATEGORY = "category";

	public static final String ATT_PARENT_CATEGORY = "parentCategory";

	public static final String CONFIGURE_EPOINT = "configurationWizards";

	public static final String CONNECT_EPOINT = "connectWizards";
	
	public static final String CONFIGURE_EPOINT_ID = Activator.PLUGIN_ID + "." + CONFIGURE_EPOINT;
	
	public static final String CONNECT_EPOINT_ID = Activator.PLUGIN_ID + "." + CONNECT_EPOINT;
	
	public static final String PRIMARY_WIZARD = "primaryWizard";
	
	public static final String HAS_PAGES = "hasPages";
	
	public static final String CAN_FINISH_EARLY = "canFinishEarly";

	public static final String HELP_HREF = "helpHref";
	
	public static final String ATT_CONTAINER_TYPE_NAME = "containerTypeName";
	

}