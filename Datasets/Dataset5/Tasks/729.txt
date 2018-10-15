super(parent, PopupDialog.INFOPOPUP_SHELLSTYLE | SWT.ON_TOP, false, false, false, false, false, null, null);

/*******************************************************************************
 * Copyright (c) 2004 - 2006 University Of British Columbia and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     University Of British Columbia - initial API and implementation
 *     Rob Elves - creator of the original TaskListNotificationPopup class
 *******************************************************************************/

package org.eclipse.ecf.presence.ui;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.jface.dialogs.PopupDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.*;
import org.eclipse.ui.*;
import org.eclipse.ui.forms.events.HyperlinkAdapter;
import org.eclipse.ui.forms.events.HyperlinkEvent;
import org.eclipse.ui.forms.widgets.*;

class MessageNotificationPopup extends PopupDialog {

	private FormToolkit toolkit;

	private Form form;

	private Composite sectionClient;

	private IWorkbenchWindow window;

	private String userName;

	private String message;
	private ID userID;

	MessageNotificationPopup(IWorkbenchWindow window, Shell parent, ID userID) {
		super(parent, PopupDialog.INFOPOPUP_SHELLSTYLE | SWT.ON_TOP, false, false, false, false, null, null);
		this.window = window;
		this.userID = userID;
	}

	public boolean close() {
		toolkit.dispose();
		return super.close();
	}

	void setContent(String userName, String message) {
		this.userName = userName;
		this.message = message;
	}

	protected Control createContents(Composite parent) {
		getShell().setBackground(getShell().getDisplay().getSystemColor(SWT.COLOR_GRAY));
		toolkit = new FormToolkit(parent.getDisplay());
		form = toolkit.createForm(parent);
		form.getBody().setLayout(new FillLayout());

		Section section = toolkit.createSection(form.getBody(), ExpandableComposite.TITLE_BAR);
		section.setText(userName);
		section.setLayout(new FillLayout());

		sectionClient = toolkit.createComposite(section);
		sectionClient.setLayout(new GridLayout());
		Hyperlink link = toolkit.createHyperlink(sectionClient, message, SWT.NONE);
		link.addHyperlinkListener(new HyperlinkAdapter() {
			public void linkActivated(HyperlinkEvent e) {
				try {
					MessagesView view = (MessagesView) window.getActivePage().showView(MessagesView.VIEW_ID);
					view.selectTab(null, null, null, userID);
				} catch (CoreException ce) {
					ce.printStackTrace();
				}
			}
		});

		section.setClient(sectionClient);

		ImageHyperlink hyperlink = toolkit.createImageHyperlink(section, SWT.NONE);
		hyperlink.setBackground(null);
		hyperlink.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_DELETE));
		hyperlink.addHyperlinkListener(new HyperlinkAdapter() {
			public void linkActivated(HyperlinkEvent e) {
				close();
			}
		});

		section.setTextClient(hyperlink);

		form.pack();
		return parent;
	}

	/**
	 * Initialize the shell's bounds.
	 */
	public void initializeBounds() {
		getShell().setBounds(restoreBounds());
	}

	private Rectangle restoreBounds() {
		Rectangle bounds = form.getBounds();
		Rectangle maxBounds = window.getShell().getMonitor().getClientArea();

		if (bounds.width > -1 && bounds.height > -1) {
			if (maxBounds != null) {
				bounds.width = Math.min(bounds.width, maxBounds.width);
				bounds.height = Math.min(bounds.height, maxBounds.height);
			}
			// Enforce an absolute minimal size
			bounds.width = Math.max(bounds.width, 30);
			bounds.height = Math.max(bounds.height, 30);
		}

		if (bounds.x > -1 && bounds.y > -1 && maxBounds != null) {
			if (bounds.width > -1 && bounds.height > -1) {
				bounds.x = maxBounds.x + maxBounds.width - bounds.width;
				bounds.y = maxBounds.y + maxBounds.height - bounds.height;
			}
		}

		return bounds;
	}
}