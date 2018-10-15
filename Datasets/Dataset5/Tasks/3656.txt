| SWT.V_SCROLL | SWT.READ_ONLY);

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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.presence.ui.Messages;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.eclipse.ecf.presence.im.ITypingMessageSender;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.ActionContributionItem;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.dialogs.IMessageProvider;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.KeyAdapter;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.part.ViewPart;

public class MessagesView extends ViewPart {

	public static final String VIEW_ID = "org.eclipse.ecf.presence.ui.MessagesView"; //$NON-NLS-1$

	private static final int[] WEIGHTS = { 75, 25 };

	private CTabFolder tabFolder;

	private Color redColor;

	private Color blueColor;

	private Image image;

	private FormToolkit toolkit;

	private List switchActions;

	private List menuManagers;

	private Map tabs;

	public MessagesView() {
		menuManagers = new ArrayList();
		switchActions = new ArrayList();
		tabs = new HashMap();
	}

	public void createPartControl(Composite parent) {
		tabFolder = new CTabFolder(parent, SWT.NONE);
		tabFolder.setTabPosition(SWT.BOTTOM);
		toolkit = new FormToolkit(tabFolder.getDisplay());

		tabFolder.addSelectionListener(new SelectionAdapter() {
			public void widgetSelected(SelectionEvent e) {
				Iterator it = tabs.values().iterator();
				while (it.hasNext()) {
					ChatTab tab = (ChatTab) it.next();
					tab.switchItem.getAction().setChecked(tab.item == e.item);
				}
			}
		});

		redColor = new Color(parent.getDisplay(), 255, 0, 0);
		blueColor = new Color(parent.getDisplay(), 0, 0, 255);
	}

	public void dispose() {
		toolkit.dispose();
		redColor.dispose();
		blueColor.dispose();
		super.dispose();
	}

	private ChatTab getTab(IChatMessageSender messageSender,
			ITypingMessageSender typingSender, ID userID) {
		ChatTab tab = (ChatTab) tabs.get(userID);
		if (tab == null) {
			tab = new ChatTab(messageSender, typingSender, userID);
			tabs.put(userID, tab);
		}
		return tab;
	}

	public void displayTypingNotification(ID fromID) {
		ChatTab tab = null;
		synchronized (tabs) {
			tab = (ChatTab) tabs.get(fromID);
		}
		if (tab != null) {
			tab.showIsTyping();
		}
	}

	/**
	 * Opens a new tab for conversing with a user.
	 * 
	 * @param messageSender
	 *            the <tt>IChatMessageSender</tt> interface that can be used
	 *            to send messages to the other user
	 * @param typingSender
	 *            the <tt>ITypingMessageSender</tt> interface to notify the
	 *            other user that the current user is typing a message,
	 *            <tt>null</tt> if unsupported
	 * @param userID
	 *            the unique ID of the other user
	 */
	public synchronized void openTab(IChatMessageSender messageSender,
			ITypingMessageSender typingSender, ID userID) {
		ChatTab tab = getTab(messageSender, typingSender, userID);
		if (tabs.size() == 1) {
			tabFolder.setSelection(tab.item);
		}
	}

	synchronized void selectTab(IChatMessageSender messageSender,
			ITypingMessageSender typingSender, ID userID) {
		ChatTab tab = getTab(messageSender, typingSender, userID);
		for (int i = 0; i < switchActions.size(); i++) {
			IAction action = ((ActionContributionItem) switchActions.get(i))
					.getAction();
			action.setChecked(false);
		}
		tab.switchItem.getAction().setChecked(true);
		tabFolder.setSelection(tab.getCTab());
	}

	/**
	 * Display a message from a user in the chatbox.
	 * 
	 * @param userID
	 *            the ID of the user that the conversation is with
	 * @param fromID
	 *            the ID of the user that sent the message
	 * @param body
	 *            the body of the message
	 */
	public synchronized void showMessage(ID userID, ID fromID, String body) {
		ChatTab tab = (ChatTab) tabs.get(userID);
		if (tab != null) {
			tab.append(fromID, body);
		}
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

		private Form form;

		private StyledText chatText;

		private Text inputText;

		private IMenuManager manager;

		private ActionContributionItem switchItem;

		private IChatMessageSender icms;

		private ITypingMessageSender itms;

		private boolean sendTyping = false;

		private ID remoteID;

		private ChatTab(IChatMessageSender icms, ITypingMessageSender itms,
				ID userID) {
			this.icms = icms;
			this.itms = itms;
			this.remoteID = userID;
			constructWidgets();
			addListeners();
		}

		private void addListeners() {
			inputText.addKeyListener(new KeyAdapter() {
				public void keyPressed(KeyEvent e) {
					switch (e.keyCode) {
					case SWT.CR:
					case SWT.KEYPAD_CR:
						if (e.stateMask == 0) {
							String text = inputText.getText();
							inputText.setText(""); //$NON-NLS-1$
							try {
								if (!text.equals("")) { //$NON-NLS-1$
									icms.sendChatMessage(remoteID, text);
								}
							} catch (ECFException ex) {
								form
										.setMessage(
												NLS
														.bind(
																Messages.MessagesView_CouldNotSendMessage,
																text),
												IMessageProvider.ERROR);
							}
							e.doit = false;
							sendTyping = false;
						}
						break;
					}
				}
			});

			inputText.addModifyListener(new ModifyListener() {
				public void modifyText(ModifyEvent e) {
					if (!sendTyping && itms != null) {
						sendTyping = true;
						try {
							itms.sendTypingMessage(remoteID, true, null);
						} catch (ECFException ex) {
							// ignored since this is not really that important
							return;
						}
					}
				}
			});
		}

		private void append(ID fromID, String body) {
			int length = chatText.getCharCount();
			String name = fromID.getName();
			chatText.append(fromID.getName() + ": " + body + Text.DELIMITER); //$NON-NLS-1$
			if (fromID.equals(remoteID)) {
				chatText.setStyleRange(new StyleRange(length,
						name.length() + 1, redColor, null, SWT.BOLD));
				form.setMessage(null);
			} else {
				chatText.setStyleRange(new StyleRange(length,
						name.length() + 1, blueColor, null, SWT.BOLD));
			}
		}

		private void constructWidgets() {
			item = new CTabItem(tabFolder, SWT.NONE);
			form = toolkit.createForm(tabFolder);
			form.setImage(image);
			toolkit.decorateFormHeading(form);
			form.setText(remoteID.getName());

			form.getBody().setLayout(new GridLayout());

			SashForm sash = new SashForm(form.getBody(), SWT.VERTICAL);
			sash.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

			Composite client = toolkit.createComposite(sash);
			client.setLayout(new FillLayout());

			chatText = new StyledText(client, SWT.BORDER | SWT.MULTI
					| SWT.V_SCROLL);

			client = toolkit.createComposite(sash);
			client.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
			client.setLayout(new FillLayout());

			inputText = new Text(client, SWT.MULTI | SWT.BORDER | SWT.V_SCROLL);

			sash.setWeights(WEIGHTS);

			IAction action = new Action(remoteID.getName() + '\t',
					IAction.AS_RADIO_BUTTON) {
				public void run() {
					tabFolder.setSelection(item);
				}
			};
			switchItem = new ActionContributionItem(action);

			manager = form.getMenuManager();

			switchActions.add(switchItem);
			menuManagers.add(manager);

			for (int i = menuManagers.size() - 1; i > -1; i--) {
				IMenuManager manager = (IMenuManager) menuManagers.get(i);
				manager.removeAll();
				for (int j = 0; j < switchActions.size(); j++) {
					IAction switchAction = ((ActionContributionItem) switchActions
							.get(j)).getAction();
					switchAction.setChecked(false);
					manager.add(new ActionContributionItem(switchAction));
				}
				manager.update();
			}
			action.setChecked(true);

			action = new Action() {
				public void run() {
					item.dispose();
					removeTab(ChatTab.this);
					switchActions.remove(switchItem);
					menuManagers.remove(manager);

					for (int i = 0; i < menuManagers.size(); i++) {
						IMenuManager manager = (IMenuManager) menuManagers
								.get(i);
						manager.remove(switchItem);
						manager.update(true);
					}
				}
			};
			action.setImageDescriptor(PlatformUI.getWorkbench()
					.getSharedImages().getImageDescriptor(
							ISharedImages.IMG_TOOL_DELETE));

			form.getToolBarManager().add(action);
			form.getToolBarManager().update(true);

			item.setControl(form);
			item.setText(remoteID.getName());

			toolkit.paintBordersFor(form.getBody());
		}

		private CTabItem getCTab() {
			return item;
		}

		private void showIsTyping() {
			form.setMessage(NLS.bind(Messages.MessagesView_TypingNotification,
					remoteID.getName()));
		}
	}

}