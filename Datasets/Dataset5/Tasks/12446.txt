import org.eclipse.wst.xquery.set.core.ISETPreferenceConstants;

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
package org.eclipse.wst.xquery.set.internal.ui.preferences;

import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.wst.xquery.set.internal.core.preferences.ISETPreferenceConstants;
import org.eclipse.wst.xquery.set.ui.SETUIPlugin;

public class PreferenceConstants {

    // ===============
    // preference keys
    // ===============

    // build paths
    public static final String BUILD_PATH_HANDLER_DIR = "org.eclipse.wst.xquery.set.preferences.buildpath.handler"; //$NON-NLS-1$
    public static final String BUILD_PATH_LIBRARY_DIR = "org.eclipse.wst.xquery.set.preferences.buildpath.library"; //$NON-NLS-1$
    public static final String BUILD_PATH_EXTERNAL_DIR = "org.eclipse.wst.xquery.set.preferences.buildpath.external"; //$NON-NLS-1$

    // template paths
    public static final String TEMPLATES_ROOT_DIR = "org.eclipse.wst.xquery.set.preferences.templates.root"; //$NON-NLS-1$
    public static final String TEMPLATES_PROJECTS_DIR = "org.eclipse.wst.xquery.set.preferences.templates.projects"; //$NON-NLS-1$
    public static final String TEMPLATES_DEFAULT_PROJECT_DIR = "org.eclipse.wst.xquery.set.preferences.templates.projects.default"; //$NON-NLS-1$
    public static final String TEMPLATES_MODULES_DIR = "org.eclipse.wst.xquery.set.preferences.templates.modules"; //$NON-NLS-1$
    public static final String TEMPLATES_MODULES_DEFAULT_MODULE_HANDLER = "org.eclipse.wst.xquery.set.preferences.templates.modules.default.handler"; //$NON-NLS-1$
    public static final String TEMPLATES_MODULES_DEFAULT_ERROR_LIBRARY = "org.eclipse.wst.xquery.set.preferences.templates.modules.default.error"; //$NON-NLS-1$
    public static final String TEMPLATES_MODULES_NEW_MODULE_HANDLER = "org.eclipse.wst.xquery.set.preferences.templates.modules.new.handler"; //$NON-NLS-1$
    public static final String TEMPLATES_MODULES_NEW_MODULE_LIBRARY = "org.eclipse.wst.xquery.set.preferences.templates.modules.new.library"; //$NON-NLS-1$
    public static final String TEMPLATES_CONFIG_DIR = "org.eclipse.wst.xquery.set.preferences.templates.config"; //$NON-NLS-1$
    public static final String TEMPLATES_CONFIG_SAUSALITO_XML = "org.eclipse.wst.xquery.set.preferences.templates.config.sausalito"; //$NON-NLS-1$

    // template replacement fields

    // =================
    // preference values
    // =================

    // build paths
    public static final String DEF_VAL_BUILD_PATH_HANDLER_DIR = ISETPreferenceConstants.DIR_NAME_HANDLER;
    public static final String DEF_VAL_BUILD_PATH_LIBRARY_DIR = ISETPreferenceConstants.DIR_NAME_LIBRARY;
    public static final String DEF_VAL_BUILD_PATH_EXTERNAL_DIR = ISETPreferenceConstants.DIR_NAME_EXTERNAL;

    // template paths
    public static final String DEF_VAL_TEMPLATES_ROOT_DIR = "templates"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_PROJECTS_DIR = "projects"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_DEFAULT_PROJECT_DIR = "default"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_MODULES_DIR = "modules"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_MODULES_DEFAULT_MODULE_HANDLER = "default_module_handler.xq"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_MODULES_DEFAULT_ERROR_LIBRARY = "default_error_library.xq"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_MODULES_NEW_MODULE_HANDLER = "new_module_handler.xq"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_MODULES_NEW_MODULE_LIBRARY = "new_module_library.xq"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_CONFIG_DIR = "config"; //$NON-NLS-1$
    public static final String DEF_VAL_TEMPLATES_CONFIG_SAUSALITO_XML = "sausalito.xml"; //$NON-NLS-1$

    // template replacement fields
    public static final String TEMPLATES_MODULES_VAR_ERROR_NAMESPACE = "ERROR_NAMESPACE"; //$NON-NLS-1$
    public static final String TEMPLATES_MODULES_VAR_DEFAULT_NAMESPACE = "DEFAULT_NAMESPACE"; //$NON-NLS-1$
    public static final String TEMPLATES_MODULES_VAR_MODULE_NAME = "MODULE_NAME"; //$NON-NLS-1$
    public static final String TEMPLATES_CONFIG_VAR_PROJECT_URI = "PROJECT_URI"; //$NON-NLS-1$

    public static IPreferenceStore getPreferenceStore() {
        return SETUIPlugin.getDefault().getPreferenceStore();
    }

    public static void initializeDefaultValues() {
        IPreferenceStore store = getPreferenceStore();

        store.setDefault(BUILD_PATH_HANDLER_DIR, DEF_VAL_BUILD_PATH_HANDLER_DIR);
        store.setDefault(BUILD_PATH_LIBRARY_DIR, DEF_VAL_BUILD_PATH_LIBRARY_DIR);
        store.setDefault(BUILD_PATH_EXTERNAL_DIR, DEF_VAL_BUILD_PATH_EXTERNAL_DIR);

        store.setDefault(TEMPLATES_ROOT_DIR, DEF_VAL_TEMPLATES_ROOT_DIR);
        store.setDefault(TEMPLATES_PROJECTS_DIR, DEF_VAL_TEMPLATES_PROJECTS_DIR);
        store.setDefault(TEMPLATES_DEFAULT_PROJECT_DIR, DEF_VAL_TEMPLATES_DEFAULT_PROJECT_DIR);
        store.setDefault(TEMPLATES_MODULES_DIR, DEF_VAL_TEMPLATES_MODULES_DIR);
        store.setDefault(TEMPLATES_MODULES_DEFAULT_MODULE_HANDLER, DEF_VAL_TEMPLATES_MODULES_DEFAULT_MODULE_HANDLER);
        store.setDefault(TEMPLATES_MODULES_DEFAULT_ERROR_LIBRARY, DEF_VAL_TEMPLATES_MODULES_DEFAULT_ERROR_LIBRARY);
        store.setDefault(TEMPLATES_MODULES_NEW_MODULE_HANDLER, DEF_VAL_TEMPLATES_MODULES_NEW_MODULE_HANDLER);
        store.setDefault(TEMPLATES_MODULES_NEW_MODULE_LIBRARY, DEF_VAL_TEMPLATES_MODULES_NEW_MODULE_LIBRARY);
        store.setDefault(TEMPLATES_CONFIG_DIR, DEF_VAL_TEMPLATES_CONFIG_DIR);
        store.setDefault(TEMPLATES_CONFIG_SAUSALITO_XML, DEF_VAL_TEMPLATES_CONFIG_SAUSALITO_XML);
    }
}