import org.eclipse.ecf.internal.ui.deprecated.ChatPreferencePage;

/*******************************************************************************
 * Copyright (c) 2004, 2007 Remy Suen, Composent, Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.ui;

import org.eclipse.core.runtime.preferences.AbstractPreferenceInitializer;
import org.eclipse.ecf.ui.ChatPreferencePage;

public class UIPreferenceInitializer extends AbstractPreferenceInitializer {

	public void initializeDefaultPreferences() {
		Activator.getDefault().getPreferenceStore().setDefault(
				ChatPreferencePage.PREF_BROWSER_FOR_CHAT,
				ChatPreferencePage.VIEW);
	}

}