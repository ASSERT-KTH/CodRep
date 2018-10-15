System.out.println("XSD adapter [" + Thread.currentThread().getName()

/*******************************************************************************
 * Copyright (c) 2005 - 2009 itemis AG (http://www.itemis.eu) and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 *******************************************************************************/

package org.eclipse.xtend.typesystem.xsd.ui;

import org.eclipse.core.resources.IProject;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.eclipse.xtend.shared.ui.MetamodelContributor;
import org.eclipse.xtend.shared.ui.core.metamodel.MetamodelContributorRegistry;
import org.osgi.framework.BundleContext;

/**
 * The activator class controls the plug-in life cycle
 * 
 * @author Moritz Eysholdt - Initial contribution and API
 */
public class XSDToolsPlugin extends AbstractUIPlugin {

//	public static class XsdLogger extends SimpleLog {
//
//		private static final long serialVersionUID = 1L;
//
//		public XsdLogger(String name) {
//			super(name);
//			setLevel(LOG_LEVEL_ALL);
//		}
//
//		protected void write(StringBuffer buffer) {
//			traceLog(buffer.toString());
//		}
//
//	}

	// The shared instance
	private static XSDToolsPlugin plugin;

	// The plug-in ID
	public static final String PLUGIN_ID = "org.eclipse.xtend.typesystem.xsd.ui";
	public static boolean trace = false;

//	static {
//		String value = Platform.getDebugOption(PLUGIN_ID + "/trace");
//		if (value != null && value.equals("true")) {
//			trace = true;
//		}
//		XSDLog.setLogFactory(new XSDLogFactory() {
//			public Log getLog(Class<?> clazz) {
//				return new XsdLogger(clazz.getName());
//			}
//		});
//	}

	/**
	 * Returns the shared instance
	 * 
	 * @return the shared instance
	 */
	public static XSDToolsPlugin getDefault() {
		if (plugin == null)
			traceLog("Access to XSDToolsPlugin before the plugin has been initialized!");
		return plugin;
	}

	public static boolean isXSDProject(IProject proj) {
		IJavaProject jp = JavaCore.create(proj);
		if (jp == null)
			return false;
		for (MetamodelContributor c : MetamodelContributorRegistry
				.getActiveMetamodelContributors(jp))
			if (c instanceof XSDMetamodelContributor)
				return true;
		return false;
	}

	public static void traceLog(String msg) {
		if (trace)
			System.out.println("oAW-XSD[" + Thread.currentThread().getName()
					+ "]: " + msg);
	}

	private XSDBuilderConfigurator builderConfigurator = new XSDBuilderConfigurator();

	private XSDMetamodelStore store = new XSDMetamodelStore();

	public XSDToolsPlugin() {
		plugin = this;
	}

	public XSDMetamodelStore getXSDStore() {
		return store;
	}

	public void start(BundleContext context) throws Exception {
		super.start(context);
		traceLog(getClass().getName() + " started");
		builderConfigurator = new XSDBuilderConfigurator();
		store = new XSDMetamodelStore();
		builderConfigurator.start();
	}

	public void stop(BundleContext context) throws Exception {
		builderConfigurator.stop();
		plugin = null;
		super.stop(context);
		traceLog(getClass().getName() + " stopped");
	}

}