if (!path.startsWith("/"))buf.append("/"); //$NON-NLS-1$ //$NON-NLS-2$

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.discovery.ui;

import java.net.URI;
import java.net.URL;
import java.util.Arrays;
import java.util.List;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.discovery.IServiceInfo;
import org.eclipse.ecf.discovery.IServiceProperties;
import org.eclipse.ecf.discovery.identity.IServiceID;
import org.eclipse.ecf.discovery.ui.views.IServiceAccessHandler;
import org.eclipse.ecf.internal.discovery.ui.Activator;
import org.eclipse.ecf.internal.discovery.ui.Messages;
import org.eclipse.jface.action.*;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.browser.IWorkbenchBrowserSupport;

/**
 * This is a service access handler for handling the http/http service.  The associated properties
 * for this service are documented at <a href="http://www.dns-sd.org/ServiceTypes.html">http://www.dns-sd.org/ServiceTypes.html</a>.
 */
public class UrlServiceAccessHandler implements IServiceAccessHandler {

	private static final String RFC2782_PATH = "path"; //$NON-NLS-1$
	//private static final String RFC2782_USERNAME = "u"; //$NON-NLS-1$
	//private static final String RFC2782_PASSWORD = "p"; //$NON-NLS-1$
	static final IContributionItem[] EMPTY_CONTRIBUTION = {};

	public UrlServiceAccessHandler() {
		// nothing to do
	}

	public IContributionItem[] getContributionsForService(IServiceInfo serviceInfo) {
		IServiceID serviceID = serviceInfo.getServiceID();
		List serviceTypes = Arrays.asList(serviceID.getServiceTypeID().getServices());
		String protocol = null;
		if (serviceTypes.size() == 1 && serviceTypes.contains("http")) //$NON-NLS-1$
			protocol = "http"; //$NON-NLS-1$
		else if (serviceTypes.size() == 1 && serviceTypes.contains("https")) //$NON-NLS-1$
			protocol = "https"; //$NON-NLS-1$
		else if (serviceTypes.size() == 1 && serviceTypes.contains("ftp")) //$NON-NLS-1$
			protocol = "ftp"; //$NON-NLS-1$
		if (protocol == null)
			return EMPTY_CONTRIBUTION;
		URI location = serviceInfo.getLocation();
		StringBuffer buf = new StringBuffer(protocol);
		buf.append("://").append(location.getHost()); //$NON-NLS-1$
		if (location.getPort() != -1)
			buf.append(":").append(location.getPort()); //$NON-NLS-1$ 
		IServiceProperties svcProps = serviceInfo.getServiceProperties();
		final String path = svcProps.getPropertyString(RFC2782_PATH);
		if (path != null) {
			if (path.startsWith("/"))buf.append("/"); //$NON-NLS-1$ //$NON-NLS-2$
			buf.append(path);
		}
		final String urlString = buf.toString();
		//final String username = svcProps.getPropertyString(RFC2782_USERNAME);
		//final String password = svcProps.getPropertyString(RFC2782_PASSWORD);
		Action action = new Action() {
			public void run() {
				openBrowser(urlString);
			}
		};
		action.setText(NLS.bind(Messages.HttpServiceAccessHandler_MENU_TEXT, urlString));
		return new IContributionItem[] {new ActionContributionItem(action)};
	}

	protected void openBrowser(String urlString) {
		final IWorkbenchBrowserSupport support = PlatformUI.getWorkbench().getBrowserSupport();
		try {
			support.createBrowser(null).openURL(new URL(urlString));
		} catch (final Exception e) {
			logError(Messages.HttpServiceAccessHandler_EXCEPTION_CREATEBROWSER, e);
		}

	}

	protected void logError(String exceptionString, Throwable e) {
		Activator.getDefault().getLog().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, exceptionString, e));

	}

}