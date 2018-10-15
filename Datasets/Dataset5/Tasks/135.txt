store.put(IXQDTCorePreferences.LANGUAGE_LEVEL, IXQDTCorePreferences.LANGUAGE_NAME_XQUERY_SCRIPTING);

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.internal.core;

import org.eclipse.core.runtime.preferences.AbstractPreferenceInitializer;
import org.eclipse.core.runtime.preferences.DefaultScope;
import org.eclipse.core.runtime.preferences.IEclipsePreferences;
import org.eclipse.wst.xquery.core.IXQDTCorePreferences;
import org.eclipse.wst.xquery.core.XQDTCorePlugin;

public class XQDTPreferenceInitializer extends AbstractPreferenceInitializer {

    public void initializeDefaultPreferences() {
        IEclipsePreferences store = new DefaultScope().getNode(XQDTCorePlugin.PLUGIN_ID);

        store.put(IXQDTCorePreferences.LANGUAGE_LEVEL, IXQDTCorePreferences.LANGUAGE_NAME_XQUERY);
    }

}