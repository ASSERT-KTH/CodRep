chatText.append(fromID.getName() + ": " + body + Text.DELIMITER); //$NON-NLS-1$

/****************************************************************************
 * Copyright (c) 2007 Remy Suen, Composent, Inc., and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.presence.ui;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabFolder2Adapter;
import org.eclipse.swt.custom.CTabFolderEvent;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.KeyAdapter;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IWorkbenchPreferenceConstants;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

public class MessagesView extends ViewPart {

	public static final String VIEW_ID = "org.eclipse.ecf.presence.ui.MessagesView"; //$NON-NLS-1$

	private static final int[] WEIGHTS = { 75, 25 };

	private Map tabs;

	private CTabFolder tabFolder;

	private Color redColor;

	private Color blueColor;

	private IPropertyChangeListener listener;

	public MessagesView() {
		tabs = new HashMap();
	}

	public void createPartControl(Composite parent) {
		parent.setLayout(new FillLayout());
		tabFolder = new CTabFolder(parent, SWT.BOTTOM);
		redColor = new Color(parent.getDisplay(), 255, 0, 0);
		blueColor = new Color(parent.getDisplay(), 0, 0, 255);
		listener = new PropertyChangeListener();
		IPreferenceStore store = PlatformUI.getPreferenceStore();
		store.addPropertyChangeListener(listener);
		tabFolder
				.setSimple(store
						.getBoolean(IWorkbenchPreferenceConstants.SHOW_TRADITIONAL_STYLE_TABS));
	}

	public void dispose() {
		PlatformUI.getPreferenceStore().removePropertyChangeListener(listener);
		redColor.dispose();
		blueColor.dispose();
		super.dispose();
	}

	private ChatTab getTab(IChatMessageSender icms, ID userID, ID threadID) {
		ChatTab tab = (ChatTab) tabs.get(threadID);
		if (tab == null) {
			tab = new ChatTab(icms, userID, threadID);
			tabs.put(threadID, tab);
		}
		return tab;
	}

	synchronized void openTab(IChatMessageSender icms, ID userID, ID threadID) {
		tabFolder.setSelection(getTab(icms, userID, threadID).getCTab());
	}

	public synchronized void showMessage(IChatMessageSender icms, ID userID,
			ID fromID, ID threadID, String body) {
		getTab(icms, userID, threadID).append(fromID, body);
	}

	private synchronized void removeTab(ChatTab tab) {
		for (Iterator it = tabs.keySet().iterator(); it.hasNext();) {
			Object key = it.next();
			if (tabs.get(key) == tab) {
				tabs.remove(key);
				return;
			}
		}
	}

	public void setFocus() {
		tabFolder.setFocus();
	}

	private class ChatTab {

		private CTabItem item;

		private StyledText chatText;

		private Text inputText;

		private IChatMessageSender icms;

		private ID userID;

		private ID threadID;

		private ChatTab(IChatMessageSender icms, ID userID, ID threadID) {
			this.icms = icms;
			this.threadID = threadID;
			this.userID = userID;
			constructWidgets();
			addListeners();
		}

		private void addListeners() {
			tabFolder.addCTabFolder2Listener(new CTabFolder2Adapter() {
				public void close(CTabFolderEvent e) {
					removeTab(ChatTab.this);
				}
			});

			inputText.addKeyListener(new KeyAdapter() {
				public void keyPressed(KeyEvent e) {
					switch (e.keyCode) {
					case SWT.CR:
					case SWT.KEYPAD_CR:
						if (e.stateMask == 0) {
							try {
								String text = inputText.getText();
								inputText.setText(""); //$NON-NLS-1$
								if (!text.equals("")) { //$NON-NLS-1$
									icms.sendChatMessage(threadID, text);
								}
							} catch (ECFException ex) {
								ex.printStackTrace();
							}
							e.doit = false;
						}
						break;
					}
				}
			});
		}

		private void append(ID fromID, String body) {
			int length = chatText.getCharCount();
			String name = fromID.getName();
			chatText.append(fromID.getName() + ": " + body + Text.DELIMITER);
			if (fromID.equals(userID)) {
				chatText.setStyleRange(new StyleRange(length,
						name.length() + 1, blueColor, null, SWT.BOLD));
			} else {
				chatText.setStyleRange(new StyleRange(length,
						name.length() + 1, redColor, null, SWT.BOLD));
			}
		}

		private void constructWidgets() {
			item = new CTabItem(tabFolder, SWT.CLOSE);
			SashForm form = new SashForm(tabFolder, SWT.VERTICAL);
			chatText = new StyledText(form, SWT.MULTI | SWT.READ_ONLY);
			inputText = new Text(form, SWT.MULTI | SWT.V_SCROLL);
			form.setWeights(WEIGHTS);
			item.setControl(form);
			item.setText(threadID.getName());
		}

		private CTabItem getCTab() {
			return item;
		}
	}

	private class PropertyChangeListener implements IPropertyChangeListener {
		public void propertyChange(PropertyChangeEvent e) {
			if (e.getProperty().equals(
					IWorkbenchPreferenceConstants.SHOW_TRADITIONAL_STYLE_TABS)) {
				tabFolder.setSimple(((Boolean) e.getNewValue()).booleanValue());
			}
		}
	}

}