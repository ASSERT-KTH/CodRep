ClientPlugin.getDefault().getPluginPreferences().getBoolean(ClientPlugin.PREF_USE_CHAT_WINDOW);

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

package org.eclipse.ecf.example.collab.ui;

import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.ToolBar;

class TeamChat extends Composite {
	ChatComposite chat = null;
	SashForm sash = null;
	ChatTreeViewer treeView = null;
	ViewContentProvider vc;
	ToolBar bar;
	LineChatClientView view;
	ChatWindow chatWindow;

    static final int DEFAULT_TREE_WIDGET_PERCENT = 40;

	TeamChat(LineChatClientView view,Composite parent, int options, String initText) {
		super(parent, options);

		this.view = view;
		setLayout(new FillLayout());
		boolean useChatWindow =
			ClientPlugin.getDefault().getPluginPreferences().getBoolean(ClientPlugin.USE_CHAT_WINDOW);
		int[] w = null;
		if (!useChatWindow) {
			sash = new SashForm(this, SWT.NORMAL);
			sash.setLayout(new FillLayout());
			sash.setOrientation(SWT.HORIZONTAL);
			w = new int[2];
			w[0] = DEFAULT_TREE_WIDGET_PERCENT;
			w[1] = 100 - w[0];
		}

		treeView = 
			new ChatTreeViewer(
				useChatWindow ? (Composite) this : (Composite) sash, SWT.MULTI | SWT.H_SCROLL | SWT.V_SCROLL);
		treeView.setAutoExpandLevel(LineChatClientView.TREE_EXPANSION_LEVELS);
		vc = new ViewContentProvider(view);
		
		treeView.setContentProvider(vc);
		treeView.setLabelProvider(new ViewLabelProvider());
		treeView.setInput(ResourcesPlugin.getWorkspace());
		

		if (useChatWindow) {
			chatWindow = new ChatWindow(view, this, treeView, initText);
			chatWindow.create();
			chat = chatWindow.getChat();
		} else {
			chat = new ChatComposite(view, sash, treeView, SWT.NORMAL, initText);
			sash.setWeights(w);
		}
	}

	void appendText(String text) {
		if (chatWindow != null 
				&& chatWindow.getShell() != null 
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

	void enableProxyMessage(boolean val) {
		chat.enableProxyMessage(val);
	}

	ChatTreeViewer getTree() {
		return treeView;
	}

	Control getTreeControl() {
		return treeView.getControl();
	}

	Control getTextControl() {
		return chat.getTextControl();
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.swt.widgets.Widget#dispose()
	 */
	public void dispose() {
		if (chatWindow != null) {
			chatWindow.close();
			chatWindow = null;
		}
		
		super.dispose();
	}
}
 No newline at end of file