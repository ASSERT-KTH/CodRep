new ListenerList<IConfigListener, ConfigEvent>(IConfigListener.class);

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.ui.internal.config;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResourceChangeEvent;
import org.eclipse.core.resources.IResourceChangeListener;
import org.eclipse.core.resources.IResourceDelta;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.jobs.ILock;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.swt.widgets.Display;
import org.eclipse.wst.xml.vex.core.internal.core.ListenerList;

/**
 * Singleton registry of configuration sources and listeners.
 * 
 * The configuration sources may be accessed by multiple threads, and are
 * protected by a lock. All methods that modify or iterate over config sources
 * do so after acquiring the lock. Callers that wish to perform multiple
 * operations as an atomic transaction must lock and unlock the registry as
 * follows.
 * 
 * <pre>
 * ConfigRegistry reg = ConfigRegistry.getInstance();
 * try {
 * 	reg.lock();
 * 	// make modifications
 * } finally {
 * 	reg.unlock();
 * }
 * </pre>
 * 
 * <p>
 * This class also maintains a list of ConfigListeners. The addConfigListener
 * and removeConfigListener methods must be called from the main UI thread. The
 * fireConfigXXX methods may be called from other threads; this class will
 * ensure the listeners are called on the UI thread.
 */
public class ConfigRegistry {

	/**
	 * Returns the singleton instance of the registry.
	 */
	public static ConfigRegistry getInstance() {
		return instance;
	}

	/**
	 * Add a VexConfiguration to the list of configurations.
	 * 
	 * @param config
	 *            VexConfiguration to be added.
	 */
	public void addConfigSource(ConfigSource config) {
		try {
			this.lock();
			this.configs.add(config);
		} finally {
			this.unlock();
		}
	}

	/**
	 * Adds a ConfigChangeListener to the notification list.
	 * 
	 * @param listener
	 *            Listener to be added.
	 */
	public void addConfigListener(IConfigListener listener) {
		this.configListeners.add(listener);
	}

	/**
	 * Call the configChanged method on all registered ConfigChangeListeners.
	 * The listeners are called from the display thread, even if this method was
	 * called from another thread.
	 * 
	 * @param e
	 *            ConfigEvent to be fired.
	 */
	public void fireConfigChanged(final ConfigEvent e) {
		if (this.isConfigLoaded()) {
			Runnable runnable = new Runnable() {
				public void run() {
					configListeners.fireEvent("configChanged", e); //$NON-NLS-1$
				}
			};

			Display display = Display.getDefault();
			if (display.getThread() == Thread.currentThread()) {
				runnable.run();
			} else {
				display.asyncExec(runnable);
			}
		}
	}

	/**
	 * Call the configLoaded method on all registered ConfigChangeListeners from
	 * the display thread. This method is called from the ConfigLoaderJob
	 * thread.
	 * 
	 * @param e
	 *            ConfigEvent to be fired.
	 */
	public void fireConfigLoaded(final ConfigEvent e) {
		Runnable runnable = new Runnable() {
			public void run() {
				configLoaded = true;
				configListeners.fireEvent("configLoaded", e); //$NON-NLS-1$
			}
		};

		Display.getDefault().asyncExec(runnable);
	}

	/**
	 * Returns an array of all config item factories.
	 */
	public IConfigItemFactory[] getAllConfigItemFactories() {
		return configItemFactories.toArray(new IConfigItemFactory[configItemFactories.size()]);
	}

	/**
	 * Returns an array of all registered ConfigItem objects implementing the
	 * given extension point.
	 * 
	 * @param extensionPoint
	 *            ID of the desired extension point.
	 */
	public List<ConfigItem> getAllConfigItems(String extensionPoint) {
		try {
			this.lock();
			List<ConfigItem> items = new ArrayList<ConfigItem>();
			for (Iterator<ConfigSource> it = this.configs.iterator(); it.hasNext();) {
				ConfigSource config = it.next();
				items.addAll(config.getValidItems(extensionPoint));
			}
			return items;
		} finally {
			this.unlock();
		}
	}

	/**
	 * Returns a list of all registered ConfigSource objects.
	 * 
	 * @return
	 */
	public List<ConfigSource> getAllConfigSources() {
		try {
			this.lock();
			List<ConfigSource> result = new ArrayList<ConfigSource>();
			result.addAll(this.configs);
			return result;
		} finally {
			this.unlock();
		}
	}

	/**
	 * Returns a specific configuration item given an extension point id and the
	 * item's id. Returns null if either the extension point or the item is not
	 * found.
	 * 
	 * @param extensionPoint
	 *            ID of the desired extension point.
	 * @param id
	 *            ID of the desired item.
	 */
	public ConfigItem getConfigItem(String extensionPoint, String id) {
		try {
			this.lock();
			List<ConfigItem> items = this.getAllConfigItems(extensionPoint);
			for (Iterator<ConfigItem> it = items.iterator(); it.hasNext();) {
				ConfigItem item = (ConfigItem) it.next();
				if (item.getUniqueId().equals(id)) {
					return item;
				}
			}
			return null;
		} finally {
			this.unlock();
		}
	}

	/**
	 * Returns the IConfigItemFactory object for the given extension point or
	 * null if none exists.
	 * 
	 * @param extensionPointId
	 *            Extension point ID for which to search.
	 */
	public IConfigItemFactory getConfigItemFactory(String extensionPointId) {
		for (Iterator<IConfigItemFactory> it = configItemFactories.iterator(); it.hasNext();) {
			IConfigItemFactory factory = it.next();
			if (factory.getExtensionPointId().equals(extensionPointId)) {
				return factory;
			}
		}
		return null;
	}

	/**
	 * Returns true if the Vex configuration has been loaded.
	 * 
	 * @see org.eclipse.wst.xml.vex.ui.internal.config.ConfigLoaderJob
	 */
	public boolean isConfigLoaded() {
		return this.configLoaded;
	}

	/**
	 * Locks the registry for modification or iteration over its config sources.
	 */
	public void lock() {
		this.lock.acquire();
	}

	/**
	 * Remove a VexConfiguration from the list of configs.
	 * 
	 * @param config
	 *            VexConfiguration to remove.
	 */
	public void removeConfigSource(ConfigSource config) {
		try {
			this.lock();
			this.configs.remove(config);
		} finally {
			this.unlock();
		}
	}

	/**
	 * Removes a ConfigChangeListener from the notification list.
	 * 
	 * @param listener
	 *            Listener to be removed.
	 */
	public void removeConfigListener(IConfigListener listener) {
		this.configListeners.remove(listener);
	}

	/**
	 * Unlocks the registry.
	 */
	public void unlock() {
		this.lock.release();
	}

	// ======================================================== PRIVATE

	private static ConfigRegistry instance = new ConfigRegistry();

	private ILock lock = Job.getJobManager().newLock();
	private List<ConfigSource> configs = new ArrayList<ConfigSource>();
	private ListenerList<IConfigListener, ConfigEvent> configListeners =
	    new ListenerList<IConfigListener, ConfigEvent>();
	private boolean configLoaded = false;
	private List<IConfigItemFactory> configItemFactories =
		new ArrayList<IConfigItemFactory>();

	/**
	 * Class constructor. All initialization is performed here.
	 */
	private ConfigRegistry() {
		configItemFactories.add(new DoctypeFactory());
		configItemFactories.add(new StyleFactory());
		// TODO do we ever unregister this?
		ResourcesPlugin.getWorkspace().addResourceChangeListener(
				this.resourceChangeListener);
	}

	private IResourceChangeListener resourceChangeListener = new IResourceChangeListener() {

		public void resourceChanged(final IResourceChangeEvent event) {

			// System.out.println("resourceChanged, type is " + event.getType()
			// + ", resource is " + event.getResource());

			if (event.getType() == IResourceChangeEvent.PRE_CLOSE
					|| event.getType() == IResourceChangeEvent.PRE_DELETE) {
				PluginProject pp = PluginProject.get((IProject) event
						.getResource());
				if (pp != null) {
					// System.out.println("  removing project from config registry");
					removeConfigSource(pp);
					fireConfigChanged(new ConfigEvent(this));
				}
			} else if (event.getType() == IResourceChangeEvent.POST_CHANGE) {
				IResourceDelta[] resources = event.getDelta()
						.getAffectedChildren();
				for (int i = 0; i < resources.length; i++) {
					final IResourceDelta delta = resources[i];
					if (delta.getResource() instanceof IProject) {
						final IProject project = (IProject) delta.getResource();

						// System.out.println("Project " + project.getName() +
						// " changed, isOpen is " + project.isOpen());

						PluginProject pluginProject = PluginProject
								.get(project);

						boolean hasPluginProjectNature = false;
						try {
							hasPluginProjectNature = project
									.hasNature(PluginProjectNature.ID);
						} catch (CoreException ex) {
							// yup, sometimes checked exceptions really blow
						}

						if (!project.isOpen() && pluginProject != null) {

							// System.out.println("  closing project: " +
							// project.getName());
							removeConfigSource(pluginProject);
							fireConfigChanged(new ConfigEvent(this));

						} else if (project.isOpen() && pluginProject == null
								&& hasPluginProjectNature) {

							// System.out.println("  newly opened project: " +
							// project.getName() + ", rebuilding");

							// Must be run in another thread, since the
							// workspace is locked here
							Runnable runnable = new Runnable() {
								public void run() {
									PluginProject.load(project);
								}
							};
							Display.getDefault().asyncExec(runnable);
						} else {
							// System.out.println("  no action taken");
						}
					}
				}
			}
		}
	};

}