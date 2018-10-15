static final int DEFAULT_TREE_WIDGET_PERCENT = 15;

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.internal.example.collab.ui;

import java.util.List;

import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.ecf.internal.example.collab.ClientPlugin;
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.ToolBar;

class TeamChat extends Composite {
	ChatComposite chat = null;
	SashForm sash = null;
	TableViewer tableView = null;
	ToolBar bar;
	LineChatClientView view;
	ChatWindow chatWindow;

	static final int DEFAULT_TREE_WIDGET_PERCENT = 10;

	TeamChat(LineChatClientView view, Composite parent, int options,
			String initText) {
		super(parent, options);

		this.view = view;
		setLayout(new FillLayout());
		boolean useChatWindow = ClientPlugin.getDefault()
				.getPluginPreferences().getBoolean(
						ClientPlugin.PREF_USE_CHAT_WINDOW);
		int[] w = null;
		if (!useChatWindow) {
			sash = new SashForm(this, SWT.NORMAL);
			sash.setLayout(new FillLayout());
			sash.setOrientation(SWT.HORIZONTAL);
			w = new int[2];
			w[0] = DEFAULT_TREE_WIDGET_PERCENT;
			w[1] = 100 - w[0];
		}

		tableView = new TableViewer(useChatWindow ? (Composite) this
				: (Composite) sash, SWT.MULTI | SWT.H_SCROLL | SWT.V_SCROLL
				| SWT.BORDER);
		tableView.setContentProvider(new ViewContentProvider());
		tableView.setLabelProvider(new ViewLabelProvider());

		if (useChatWindow) {
			chatWindow = new ChatWindow(view, tableView, initText);
			chatWindow.create();
			chat = chatWindow.getChat();
		} else {
			chat = new ChatComposite(view, sash, tableView, initText);
			sash.setWeights(w);
		}
	}

	void appendText(ChatLine text) {
		if (chatWindow != null && chatWindow.getShell() != null
				&& !chatWindow.getShell().isDisposed()
				&& !chatWindow.hasFocus()) {

			if (chatWindow.getShell().isVisible())
				chatWindow.flash();
			else
				chatWindow.open();
		}

		chat.appendText(text);
		setStatus(null);
	}

	void setStatus(String status) {
		if (chatWindow != null)
			chatWindow.setStatus(status);
	}

	void clearInput() {
		chat.clearInput();
	}

	TableViewer getTableViewer() {
		return tableView;
	}

	Control getTreeControl() {
		return tableView.getControl();
	}

	Control getTextControl() {
		return chat.getTextControl();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.swt.widgets.Widget#dispose()
	 */
	public void dispose() {
		if (chatWindow != null) {
			chatWindow.close();
			chatWindow = null;
		}

		super.dispose();
	}

	private class ViewContentProvider implements IStructuredContentProvider {

		public void dispose() {
		}

		public Object[] getElements(Object parent) {
			return ((List) parent).toArray();
		}

		public void inputChanged(Viewer v, Object oldInput, Object newInput) {
		}
	}

	private class ViewLabelProvider extends LabelProvider {
		public Image getImage(Object obj) {
			return obj instanceof User ? SharedImages
					.getImage(SharedImages.IMG_USER_AVAILABLE) : null;
		}
	}
}
 No newline at end of file