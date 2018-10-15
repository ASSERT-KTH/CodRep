import org.eclipse.ecf.internal.example.collab.ClientPlugin;

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

package org.eclipse.ecf.example.collab.share.url;

import java.net.URL;

import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.help.browser.IBrowser;
import org.eclipse.help.internal.browser.BrowserManager;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWTError;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.browser.IWorkbenchBrowserSupport;

public class GetExec {

	protected static void displayURL(String url, boolean external) {
		IBrowser browser = null;
		Shell [] shells = Display.getCurrent().getShells();
		try {
			browser = BrowserManager.getInstance().createBrowser(
					external);
		} catch (SWTError swterror) {
			try {
				if (shells != null && shells.length > 0) {
					MessageDialog.openError(shells[0], "Error in Browser Creation", "Cannot launch browser.  Something is wrong with config for using external browser");
				}
			} catch (Exception e1) {}
			ClientPlugin.log("Cannot create browser for URL: " + url, swterror);
			return;
		}
		try {
			browser.displayURL(url);
		} catch (Exception e) {
			try {
				if (shells != null && shells.length > 0) {
					MessageDialog.openError(shells[0], "Error in URL", "Cannot display URL");
				}
			} catch (Exception e1) {}
			ClientPlugin.log("Cannot display URL: " + url, e);
		} catch (SWTError swterror) {
			
		}
	}
	public static void showURL(final String url,
		final boolean considerInternal) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				displayURL(url, considerInternal);
			}
		});
	}
	public static void openURL(final URL anURL,final boolean internal) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				IWorkbenchBrowserSupport support = PlatformUI.getWorkbench().getBrowserSupport();
				try {
					if (internal)
						support.createBrowser(IWorkbenchBrowserSupport.LOCATION_BAR | IWorkbenchBrowserSupport.NAVIGATION_BAR,
								anURL.toExternalForm(), null, null).openURL(anURL);
					else {
						displayURL(anURL.toExternalForm(),false);
					}
				}
				catch (PartInitException e) {
					MessageDialog.openError(PlatformUI.getWorkbench().getDisplay().getActiveShell(),
							"Error in URL", e.getLocalizedMessage());
				}
			}
		});
	}
}
 No newline at end of file