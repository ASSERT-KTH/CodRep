null);

/*******************************************************************************
 * Copyright (c) 2004 Peter Nehrer and Composent, Inc.
 * All rights reserved. This program and the accompanying materials 
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Peter Nehrer - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.example.sdo.editor;

import java.util.MissingResourceException;
import java.util.ResourceBundle;

import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.example.collab.Client;
import org.eclipse.ecf.sdo.DataGraphSharingFactory;
import org.eclipse.ecf.sdo.ISharedDataGraph;
import org.eclipse.ecf.sdo.IUpdateConsumer;
import org.eclipse.ecf.sdo.WaitablePublicationCallback;
import org.eclipse.ecf.sdo.WaitableSubscriptionCallback;
import org.eclipse.ecf.sdo.emf.EMFUpdateProvider;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.osgi.framework.BundleContext;

import commonj.sdo.DataGraph;

/**
 * The main plugin class to be used in the desktop.
 * 
 * @author pnehrer
 */
public class EditorPlugin extends AbstractUIPlugin {
    // The shared instance.
    private static EditorPlugin plugin;

    // Resource bundle.
    private ResourceBundle resourceBundle;

    /**
     * The constructor.
     */
    public EditorPlugin() {
        super();
        plugin = this;
        try {
            resourceBundle = ResourceBundle
                    .getBundle("org.eclipse.ecf.example.sdo.editor.EditorPluginResources");
        } catch (MissingResourceException x) {
            resourceBundle = null;
        }
    }

    /**
     * This method is called upon plug-in activation
     */
    public void start(BundleContext context) throws Exception {
        super.start(context);
    }

    /**
     * This method is called when the plug-in is stopped
     */
    public void stop(BundleContext context) throws Exception {
        super.stop(context);
    }

    /**
     * Returns the shared instance.
     */
    public static EditorPlugin getDefault() {
        return plugin;
    }

    /**
     * Returns the string from the plugin's resource bundle, or 'key' if not
     * found.
     */
    public static String getResourceString(String key) {
        ResourceBundle bundle = EditorPlugin.getDefault().getResourceBundle();
        try {
            return (bundle != null) ? bundle.getString(key) : key;
        } catch (MissingResourceException e) {
            return key;
        }
    }

    /**
     * Returns the plugin's resource bundle,
     */
    public ResourceBundle getResourceBundle() {
        return resourceBundle;
    }

    public void log(Throwable t) {
        if (t instanceof CoreException)
            getLog().log(((CoreException) t).getStatus());
        else
            getLog().log(
                    new Status(Status.ERROR, getBundle().getSymbolicName(), 0,
                            "An unexpected error occurred.", t));
    }

    public synchronized ISharedDataGraph subscribe(String path,
            IUpdateConsumer consumer) throws ECFException {
        Path p = new Path(path);
        ISharedObjectContainer container = getContainer(ResourcesPlugin
                .getWorkspace().getRoot().getProject(p.segment(0)));
        PublishedGraphTracker tracker = getTracker(container);

        ID id = IDFactory.makeStringID(path);
        WaitableSubscriptionCallback mutex = new WaitableSubscriptionCallback();
        ISharedDataGraph result = DataGraphSharingFactory.getDataGraphSharing(
                container, "default").subscribe(id, new EMFUpdateProvider(),
                consumer, mutex);
        ID containerID = null;
        try {
            containerID = mutex.waitForSubscription(5000);
        } catch (InterruptedException e) {
            throw new ECFException(e);
        }

        if (containerID == null)
            throw new ECFException("Subscription timed out.");

        tracker.add(id);
        return result;
    }

    public synchronized ISharedDataGraph publish(String path,
            DataGraph dataGraph, IUpdateConsumer consumer) throws ECFException {
        Path p = new Path(path);
        ISharedObjectContainer container = getContainer(ResourcesPlugin
                .getWorkspace().getRoot().getProject(p.segment(0)));
        PublishedGraphTracker tracker = getTracker(container);

        ID id = IDFactory.makeStringID(path);
        WaitablePublicationCallback mutex = new WaitablePublicationCallback();
        ISharedDataGraph result = DataGraphSharingFactory.getDataGraphSharing(
                container, "default").publish(dataGraph, id,
                new EMFUpdateProvider(), consumer, mutex);
        try {
            if (!mutex.waitForPublication(5000))
                throw new ECFException("Publication timed out.");
        } catch (InterruptedException e) {
            throw new ECFException(e);
        }

        tracker.add(id);
        return result;
    }

    public synchronized boolean isPublished(String path) throws ECFException {
        Path p = new Path(path);
        ISharedObjectContainer container = getContainer(ResourcesPlugin
                .getWorkspace().getRoot().getProject(p.segment(0)));
        PublishedGraphTracker tracker = getTracker(container);
        return tracker.isPublished(IDFactory.makeStringID(path));
    }

    public synchronized void checkConnected(IProject project)
            throws ECFException {
        if (getContainer(project) == null)
            throw new ECFException("Project " + project.getName()
                    + " is not connected.");
    }

    private ISharedObjectContainer getContainer(IProject project)
            throws ECFException {
        return Client.getContainer(project);
    }

    private PublishedGraphTracker getTracker(ISharedObjectContainer container)
            throws ECFException {
        ID id = IDFactory.makeStringID(PublishedGraphTracker.class.getName());
        PublishedGraphTracker tracker = (PublishedGraphTracker) container
                .getSharedObjectManager().getSharedObject(id);
        if (tracker == null) {
            tracker = new PublishedGraphTracker();
            container.getSharedObjectManager().addSharedObject(id, tracker,
                    null, null);
        }

        return tracker;
    }
}
 No newline at end of file