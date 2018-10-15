container.disconnect();

/*******************************************************************************
 * Copyright (c) 2004, 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *    Jacek Pospychala <jacek.pospychala@pl.ibm.com> - bug 192762, 197329
 *    Abner Ballardo <modlost@modlost.net> - bug 192756, 199336
 ******************************************************************************/
package org.eclipse.ecf.presence.ui.chatroom;

import java.net.URI;
import java.net.URISyntaxException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Map;

import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Preferences;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.presence.ui.Activator;
import org.eclipse.ecf.internal.presence.ui.ChatLine;
import org.eclipse.ecf.internal.presence.ui.Messages;
import org.eclipse.ecf.internal.presence.ui.preferences.PreferenceConstants;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomInvitationListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessage;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageEvent;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener;
import org.eclipse.ecf.presence.im.IChatID;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.text.Document;
import org.eclipse.jface.text.ITextSelection;
import org.eclipse.jface.text.TextSelection;
import org.eclipse.jface.text.source.SourceViewer;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.ViewerSorter;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabFolder2Listener;
import org.eclipse.swt.custom.CTabFolderEvent;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.ScrollBar;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IActionFilter;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IWorkbenchActionConstants;
import org.eclipse.ui.IWorkbenchPreferenceConstants;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.editors.text.EditorsUI;
import org.eclipse.ui.editors.text.TextSourceViewerConfiguration;
import org.eclipse.ui.part.ViewPart;

public class ChatRoomManagerView extends ViewPart implements
		IChatRoomInvitationListener {

	private static final String ATSIGN = "@"; //$NON-NLS-1$

	public static final String VIEW_ID = "org.eclipse.ecf.presence.ui.chatroom.ChatRoomManagerView"; //$NON-NLS-1$

	public static final String PARTICIPANTS_MENU_ID = "org.eclipse.ecf.presence.ui.chatroom.participantsView"; //$NON-NLS-1$ 
	
	private static final int RATIO_WRITE_PANE = 1;

	private static final int RATIO_READ_PANE = 9;

	private static final int RATIO_READ_WRITE_PANE = 85;

	private static final int RATIO_PRESENCE_PANE = 15;
	
	protected static final int DEFAULT_INPUT_HEIGHT = 25;

	protected static final int DEFAULT_INPUT_SEPARATOR = 5;

	private CTabFolder rootTabFolder = null;

	private ChatRoomTab rootChannelTab = null;

	private IChatRoomViewCloseListener rootCloseListener = null;

	private IChatRoomMessageSender rootMessageSender = null;
	
	/**
	 * UI independent renderer, that is aware of displaying any special fragments
	 * of message, like formatting, graphical attachments, emotional content, etc.
	 */
	private IMessageRenderer messageRenderer = null;

	Action outputClear = null;

	Action outputCopy = null;

	Action outputPaste = null;

	Action outputSelectAll = null;

	boolean rootDisposed = false;

	private boolean rootEnabled = false;

	private Hashtable chatRooms = new Hashtable();

	private IChatRoomCommandListener commandListener = null;
	
	private IChatRoomContainer container = null;

	private String localUserName = Messages.ChatRoomManagerView_DEFAULT_USER;

	private String hostName = Messages.ChatRoomManagerView_DEFAULT_HOST;

	class ChatRoomTab {
		private SashForm fullChat;

		private CTabItem tabItem;

		private SashForm rightSash;

		private StyledText outputText;

		private Text inputText;

		private TableViewer participantsTable;

		private Action tabSelectAll;
		private Action tabCopy;
		private Action tabClear;
		private Action tabPaste;

		private boolean withParticipants;

		ChatRoomTab(CTabFolder parent, String name) {
			this(true, parent, name, null);
		}

		ChatRoomTab(boolean withParticipantsList, CTabFolder parent,
				String name, KeyListener keyListener) {
			withParticipants = withParticipantsList;
			tabItem = new CTabItem(parent, SWT.NULL);
			tabItem.setText(name);
			if (withParticipants) {
				fullChat = new SashForm(parent, SWT.HORIZONTAL);
				fullChat.setLayout(new FillLayout());
				Composite memberComp = new Composite(fullChat, SWT.NONE);
				memberComp.setLayout(new FillLayout());
				participantsTable = new TableViewer(memberComp, SWT.BORDER
						| SWT.V_SCROLL | SWT.H_SCROLL | SWT.MULTI);
				participantsTable.setSorter(new ViewerSorter());
				Composite rightComp = new Composite(fullChat, SWT.NONE);
				rightComp.setLayout(new FillLayout());
				rightSash = new SashForm(rightComp, SWT.VERTICAL);
			} else
				rightSash = new SashForm(parent, SWT.VERTICAL);

			outputText = createStyledTextWidget(rightSash);
			outputText.setEditable(false);
			outputText.setLayoutData(new GridData(GridData.FILL_BOTH));

			inputText = new Text(rightSash, SWT.BORDER | SWT.MULTI | SWT.WRAP
					| SWT.V_SCROLL);
			if (keyListener != null)
				inputText.addKeyListener(keyListener);
			rightSash
					.setWeights(new int[] { RATIO_READ_PANE, RATIO_WRITE_PANE });
			if (withParticipants) {
				fullChat.setWeights(new int[] { RATIO_PRESENCE_PANE,
						RATIO_READ_WRITE_PANE });
				tabItem.setControl(fullChat);
			} else
				tabItem.setControl(rightSash);

			parent.setSelection(tabItem);

			makeActions();
			hookContextMenu();
			if (withParticipants) {
				hookParticipantsContextMenu();
			}
			
			StyledText st = getOutputText();
			if (st != null) {
				ScrollBar vsb = st.getVerticalBar();
				if (vsb != null) {
					vsb.addSelectionListener(scrollSelectionListener);
					vsb.addDisposeListener(new DisposeListener() {
						public void widgetDisposed(DisposeEvent e) {
							StyledText st = getOutputText();
							if (st != null) {
								ScrollBar vsb = st.getVerticalBar();
								if (vsb != null) vsb.removeSelectionListener(scrollSelectionListener);
							}
						}});
				}
			}

		}

		private SelectionListener scrollSelectionListener = new SelectionListener() {

			public void widgetDefaultSelected(SelectionEvent e) {
			}

			public void widgetSelected(SelectionEvent e) {
				if (!isLastOutputInvisible(getOutputText())) {
					makeTabItemNormal();
				}
			}
			
		};

		protected void makeTabItemBold() {
			changeTabItem(true);
		}

		protected void makeTabItemNormal() {
			changeTabItem(false);
		}

		protected void changeTabItem(boolean bold) {
			CTabItem item = tabItem;
			Font oldFont = item.getFont();
			FontData[] fd = oldFont.getFontData();
			item.setFont(new Font(oldFont.getDevice(), fd[0].getName(), fd[0]
					.getHeight(), (bold) ? SWT.BOLD : SWT.NORMAL));
		}


		private StyledText createStyledTextWidget(Composite parent) {
			try {
				SourceViewer result = new SourceViewer(parent, null, null,
						true, SWT.BORDER | SWT.WRAP | SWT.V_SCROLL | SWT.MULTI
								| SWT.READ_ONLY);
				result.configure(new TextSourceViewerConfiguration(EditorsUI
						.getPreferenceStore()));
				result.setDocument(new Document());
				return result.getTextWidget();
			} catch (Exception e) {
				Activator
						.getDefault()
						.getLog()
						.log(
								new Status(
										IStatus.WARNING,
										Activator.PLUGIN_ID,
										IStatus.WARNING,
										Messages.ChatRoomManagerView_WARNING_HYPERLINKING_NOT_AVAILABLE,
										e));
				return new StyledText(parent, SWT.BORDER | SWT.WRAP
						| SWT.V_SCROLL | SWT.MULTI | SWT.READ_ONLY);
			}
		}


		protected void outputClear() {
			if (MessageDialog
					.openConfirm(
							null,
							Messages.ChatRoomManagerView_CONFIRM_CLEAR_TEXT_OUTPUT_TITLE,
							Messages.ChatRoomManagerView_CONFIRM_CLEAR_TEXT_OUTPUT_MESSAGE)) {
				outputText.setText(""); //$NON-NLS-1$
			}
		}

		protected void outputCopy() {
			String t = outputText.getSelectionText();
			if (t == null || t.length() == 0) {
				outputText.selectAll();
			}
			outputText.copy();
			outputText.setSelection(outputText.getText().length());
		}

		private void fillContextMenu(IMenuManager manager) {
			manager.add(outputCopy);
			manager.add(outputClear);
			manager.add(new Separator());
			manager.add(outputSelectAll);
			manager.add(new Separator(IWorkbenchActionConstants.MB_ADDITIONS));
		}

		private void hookContextMenu() {
			MenuManager menuMgr = new MenuManager(); 
			menuMgr.setRemoveAllWhenShown(true);
			menuMgr.addMenuListener(new IMenuListener() {
				public void menuAboutToShow(IMenuManager manager) {
					fillContextMenu(manager);
				}
			});
			Menu menu = menuMgr.createContextMenu(outputText);
			outputText.setMenu(menu);
			ISelectionProvider selectionProvider = new ISelectionProvider() {

				public void addSelectionChangedListener(
						ISelectionChangedListener listener) {
				}

				public ISelection getSelection() {
					ISelection selection = new TextSelection(outputText
							.getSelectionRange().x, outputText
							.getSelectionRange().y);

					return selection;
				}

				public void removeSelectionChangedListener(
						ISelectionChangedListener listener) {
				}

				public void setSelection(ISelection selection) {
					if (selection instanceof ITextSelection) {
						ITextSelection textSelection = (ITextSelection) selection;
						outputText.setSelection(textSelection.getOffset(),
								textSelection.getOffset()
										+ textSelection.getLength());
					}
				}

			};
			getSite().registerContextMenu(menuMgr, selectionProvider);
		}
		
		private void hookParticipantsContextMenu() {
			MenuManager menuMgr = new MenuManager();
			menuMgr.addMenuListener(new IMenuListener() {
				public void menuAboutToShow(IMenuManager manager) {
					manager.add(new Separator(IWorkbenchActionConstants.MB_ADDITIONS));
				}
			});
			menuMgr.setRemoveAllWhenShown(true);
			Control control = participantsTable.getControl();
			Menu menu = menuMgr.createContextMenu(control);
			control.setMenu(menu);
			getSite().registerContextMenu(PARTICIPANTS_MENU_ID, menuMgr, participantsTable);
		}
		
		private void makeActions() {
			tabSelectAll = new Action() {
				public void run() {
					outputText.selectAll();
				}
			};
			tabSelectAll.setText(Messages.ChatRoomManagerView_SELECT_ALL_TEXT);
			tabSelectAll
					.setToolTipText(Messages.ChatRoomManagerView_SELECT_ALL_TOOLTIP);
			tabSelectAll.setAccelerator(SWT.CTRL | 'A');
			tabCopy = new Action() {
				public void run() {
					outputCopy();
				}
			};
			tabCopy.setText(Messages.ChatRoomManagerView_COPY_TEXT);
			tabCopy.setToolTipText(Messages.ChatRoomManagerView_COPY_TOOLTIP);
			tabCopy.setAccelerator(SWT.CTRL | 'C');
			tabCopy.setImageDescriptor(PlatformUI.getWorkbench()
					.getSharedImages().getImageDescriptor(
							ISharedImages.IMG_TOOL_COPY));
			tabClear = new Action() {
				public void run() {
					outputClear();
				}
			};
			tabClear.setText(Messages.ChatRoomManagerView_CLEAR_TEXT);
			tabClear.setToolTipText(Messages.ChatRoomManagerView_CLEAR_TOOLTIP);
			tabPaste = new Action() {
				public void run() {
					getInputText().paste();
				}
			};
			tabPaste.setAccelerator(SWT.CTRL | 'V');
			tabPaste.setImageDescriptor(PlatformUI.getWorkbench()
					.getSharedImages().getImageDescriptor(
							ISharedImages.IMG_TOOL_PASTE));

		}

		protected Text getInputText() {
			return inputText;
		}

		protected void setKeyListener(KeyListener listener) {
			if (listener != null)
				inputText.addKeyListener(listener);
		}

		protected TableViewer getParticipantsViewer() {
			return participantsTable;
		}

		/**
		 * @return
		 */
		public StyledText getOutputText() {
			return outputText;
		}
	}

	public void createPartControl(Composite parent) {
		Composite rootComposite = new Composite(parent, SWT.NONE);
		rootComposite.setLayout(new FillLayout());
		boolean useTraditionalTabFolder = PlatformUI
				.getPreferenceStore()
				.getBoolean(
						IWorkbenchPreferenceConstants.SHOW_TRADITIONAL_STYLE_TABS);
		rootTabFolder = new CTabFolder(rootComposite, SWT.NORMAL | SWT.CLOSE);
		rootTabFolder.setUnselectedCloseVisible(false);
		rootTabFolder.setSimple(useTraditionalTabFolder);
		PlatformUI.getPreferenceStore().addPropertyChangeListener(
				new IPropertyChangeListener() {
					public void propertyChange(PropertyChangeEvent event) {
						if (event
								.getProperty()
								.equals(
										IWorkbenchPreferenceConstants.SHOW_TRADITIONAL_STYLE_TABS)
								&& !rootTabFolder.isDisposed()) {
							rootTabFolder.setSimple(((Boolean) event
									.getNewValue()).booleanValue());
							rootTabFolder.redraw();
						}
					}
				});

		rootTabFolder.addCTabFolder2Listener(new CTabFolder2Listener() {
			public void close(CTabFolderEvent event) {
				event.doit = closeTabItem((CTabItem) event.item);
			}

			public void maximize(CTabFolderEvent event) {
			}

			public void minimize(CTabFolderEvent event) {
			}

			public void restore(CTabFolderEvent event) {
			}

			public void showList(CTabFolderEvent event) {
			}
		});
	}

	private boolean closeTabItem(CTabItem tabItem) {
		ChatRoom chatRoom = findChatRoomForTabItem(tabItem);
		if (chatRoom == null) {
			return true;
		} else {
			if (MessageDialog
					.openQuestion(
							getSite().getShell(),
							Messages.ChatRoomManagerView_CLOSE_CHAT_ROOM_TITLE,
							NLS
									.bind(
											Messages.ChatRoomManagerView_CLOSE_CHAT_ROOM_MESSAGE,
											tabItem.getText()))) {
				chatRoom.chatRoomDisconnect();
				return true;
			} else
				return false;
		}
	}

	/**
	 * @return chat room container of currently selected tab or null if none found.
	 */
	public IChatRoomContainer getActiveChatRoomContainer() {
		CTabItem selection = rootTabFolder.getSelection();
		if (selection != null) {
			ChatRoom chatRoom = findChatRoomForTabItem(selection);
			if (chatRoom != null) {
				return chatRoom.chatRoomContainer;
			}
		}
		
		return null;
	}
	
	private ChatRoom findChatRoomForTabItem(CTabItem tabItem) {
		for (Iterator i = chatRooms.values().iterator(); i.hasNext();) {
			ChatRoom cr = (ChatRoom) i.next();
			if (tabItem == cr.chatRoomTab.tabItem)
				return cr;
		}
		return null;
	}

	private Text getRootTextInput() {
		if (rootChannelTab == null)
			return null;
		else
			return rootChannelTab.getInputText();
	}

	private StyledText getRootTextOutput() {
		if (rootChannelTab == null)
			return null;
		else
			return rootChannelTab.getOutputText();
	}

	public void initializeWithoutManager(String localUserName, String hostName,
			final IChatRoomCommandListener commandListener,
			final IChatRoomViewCloseListener closeListener) {
		initializeWithManager(localUserName, hostName, null, commandListener,
				closeListener);
	}

	public void initializeWithManager(String localUserName, String hostName,
			final IChatRoomContainer rootChatRoomContainer,
			final IChatRoomCommandListener commandListener,
			final IChatRoomViewCloseListener closeListener) {
		ChatRoomManagerView.this.localUserName = (localUserName == null) ? Messages.ChatRoomManagerView_DEFAULT_USER
				: localUserName;
		ChatRoomManagerView.this.hostName = (hostName == null) ? Messages.ChatRoomManagerView_DEFAULT_HOST
				: hostName;
		ChatRoomManagerView.this.rootCloseListener = closeListener;
		ChatRoomManagerView.this.commandListener = commandListener;
		String viewTitle = localUserName + ATSIGN + hostName;
		ChatRoomManagerView.this.setPartName(NLS.bind(
				Messages.ChatRoomManagerView_VIEW_TITLE, viewTitle));
		ChatRoomManagerView.this
				.setTitleToolTip(Messages.ChatRoomManagerView_VIEW_TITLE_HOST_PREFIX
						+ ChatRoomManagerView.this.hostName);
		if (rootChatRoomContainer != null) {
			ChatRoomManagerView.this.container = rootChatRoomContainer;
			ChatRoomManagerView.this.rootMessageSender = rootChatRoomContainer
					.getChatRoomMessageSender();
			rootChannelTab = new ChatRoomTab(false, rootTabFolder,
					ChatRoomManagerView.this.hostName, new KeyListener() {
						public void keyPressed(KeyEvent evt) {
							handleKeyPressed(evt);
						}

						public void keyReleased(KeyEvent evt) {
						}
					});
			makeActions();
			hookContextMenu();
			if (rootChatRoomContainer.getConnectedID() == null) {
				StyledText outputText = getRootTextOutput();
				if (!outputText.isDisposed())
					outputText
							.setText(new SimpleDateFormat(
									Messages.ChatRoomManagerView_CONNECT_DATE_TIME_FORMAT)
									.format(new Date())
									+ NLS
											.bind(
													Messages.ChatRoomManagerView_CONNECT_MESSAGE,
													viewTitle));
			}
		}
		setEnabled(false);
	}

	public void setEnabled(boolean enabled) {
		this.rootEnabled = enabled;
		Text inputText = getRootTextInput();
		if (inputText != null && !inputText.isDisposed())
			inputText.setEnabled(enabled);
	}

	public boolean isEnabled() {
		return rootEnabled;
	}

	protected void clearInput() {
		Text textInput = getRootTextInput();
		if (textInput != null)
			textInput.setText(""); //$NON-NLS-1$
	}

	public void sendMessageLine(String line) {
		try {
			if (rootMessageSender != null)
				rootMessageSender.sendMessage(line);
		} catch (ECFException e) {
			// And cut ourselves off
			removeLocalUser();
		}
	}

	public void disconnected() {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (rootDisposed)
					return;
				setEnabled(false);
				setPartName(NLS.bind(
						Messages.ChatRoomManagerView_VIEW_DISABLED_NAME,
						getPartName()));
			}
		});
	}

	protected CTabItem getTabItem(String targetName) {
		CTabItem[] items = rootTabFolder.getItems();
		for (int i = 0; i < items.length; i++) {
			if (items[i].getText().equals(targetName)) {
				return items[i];
			}
		}
		return null;
	}

	protected void doJoinRoom(final IChatRoomInfo roomInfo,
			final String password) {
		final ID targetRoomID = roomInfo.getRoomID();
		final String targetRoomName = targetRoomID.getName();
		// first, check to see if we already have it open. If so just activate
		ChatRoom room = (ChatRoom) chatRooms.get(targetRoomName);

		if (room != null && room.isConnected()) {
			room.setSelected();
			return;
		}

		// Then we create a new chatRoomContainer from the roomInfo
		try {
			final IChatRoomContainer chatRoomContainer = roomInfo
					.createChatRoomContainer();

			// Setup new user interface (new tab)
			final ChatRoom chatroom = new ChatRoom(chatRoomContainer,
					new ChatRoomTab(rootTabFolder, targetRoomName));
			// setup message listener
			chatRoomContainer.addMessageListener(new IIMMessageListener() {
				public void handleMessageEvent(IIMMessageEvent messageEvent) {
					if (messageEvent instanceof IChatRoomMessageEvent) {
						IChatRoomMessage m = ((IChatRoomMessageEvent) messageEvent)
								.getChatRoomMessage();
						chatroom.handleMessage(m.getFromID(), m.getMessage());
					}
				}
			});
			// setup participant listener
			chatRoomContainer
					.addChatRoomParticipantListener(new IChatRoomParticipantListener() {
						public void handlePresenceUpdated(ID fromID,
								IPresence presence) {
							chatroom.handlePresence(fromID, presence);
						}

						public void handleArrived(IUser participant) {
						}

						public void handleUpdated(IUser updatedParticipant) {
						}

						public void handleDeparted(IUser participant) {
						}
					});
			chatRoomContainer.addListener(new IContainerListener() {
				public void handleEvent(IContainerEvent evt) {
					if (evt instanceof IContainerDisconnectedEvent) {
						chatroom.disconnected();
					}
				}
			});
			// Now connect/join
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					try {
						chatRoomContainer
								.connect(targetRoomID, ConnectContextFactory
										.createPasswordConnectContext(password));
						chatRooms.put(targetRoomName, chatroom);
					} catch (Exception e) {
						MessageDialog
								.openError(
										getSite().getShell(),
										"Connect Error", //$NON-NLS-1$
										NLS
												.bind(
														"Could not connect to {0}.\n\nError is {1}.", //$NON-NLS-1$
														targetRoomName,
														e.getLocalizedMessage()));
					}
				}
			});
		} catch (Exception e) {
			MessageDialog
					.openError(getSite().getShell(),
							"Container Create Error", //$NON-NLS-1$
							NLS
									.bind(
											"Could not create chatRoomContainer for {0}.\n\nError is {1}.", //$NON-NLS-1$
											targetRoomName, e
													.getLocalizedMessage()));
		}
	}

	class ChatRoom implements IChatRoomInvitationListener, KeyListener {

		private IChatRoomContainer chatRoomContainer;

		private ChatRoomTab chatRoomTab;

		private IChatRoomMessageSender chatRoomMessageSender;

		private IUser localUser;

		private TableViewer chatRoomParticipantViewer = null;

		/**
		 * A list of available nicknames for nickname completion via the 'tab'
		 * key.
		 */
		private ArrayList options;

		/**
		 * Denotes the number of options that should be available for the user
		 * to cycle through when pressing the 'tab' key to perform nickname
		 * completion. The default value is set to 5.
		 */
		private int maximumCyclingOptions = 5;

		/**
		 * The length of a nickname's prefix that has already been typed in by
		 * the user. This is used to remove the beginning part of the available
		 * nickname choices.
		 */
		private int prefixLength;

		/**
		 * The index of the next nickname to select from {@link #options}.
		 */
		private int choice = 0;

		/**
		 * The length of the user's nickname that remains resulting from
		 * subtracting the nickname's length from the prefix that the user has
		 * keyed in already.
		 */
		private int nickRemainder;

		/**
		 * The caret position of {@link #inputText} when the user first started
		 * cycling through nickname completion options.
		 */
		private int caret;

		/**
		 * The character to enter after the user's nickname has been
		 * autocompleted. The default value is a colon (':').
		 */
		private char nickCompletionSuffix = ':';

		/**
		 * Indicates whether the user is currently cycling over the list of
		 * nicknames for nickname completion.
		 */
		private boolean isCycling = false;

		/**
		 * Check to see whether the user is currently starting the line of text
		 * with a nickname at the beginning of the message. This determines
		 * whether {@link #nickCompletionSuffix} should be inserted when
		 * performing autocompletion. If the user is not at the beginning of the
		 * message, it is likely that the user is typing another user's name to
		 * reference that person and not to direct the message to said person,
		 * as such, the <code>nickCompletionSuffix</code> does not need to be
		 * appeneded.
		 */
		private boolean isAtStart = false;

		private CTabItem itemSelected = null;

		private Text getInputText() {
			return chatRoomTab.getInputText();
		}

		private StyledText getOutputText() {
			return chatRoomTab.getOutputText();
		}

		ChatRoom(IChatRoomContainer container, ChatRoomTab tabItem) {
			Assert.isNotNull(container);
			Assert.isNotNull(tabItem);
			this.chatRoomContainer = container;
			this.chatRoomMessageSender = container.getChatRoomMessageSender();
			this.chatRoomTab = tabItem;
			options = new ArrayList();
			this.chatRoomTab.setKeyListener(this);
			this.chatRoomParticipantViewer = this.chatRoomTab.getParticipantsViewer();
				
			rootTabFolder.setUnselectedCloseVisible(true);

			rootTabFolder.addSelectionListener(new SelectionListener() {

				public void widgetDefaultSelected(SelectionEvent e) {
				}

				public void widgetSelected(SelectionEvent e) {
					itemSelected = (CTabItem) e.item;
					if (itemSelected == chatRoomTab.tabItem)
						makeTabItemNormal();
					if (itemSelected == rootChannelTab.tabItem) rootChannelTab.makeTabItemNormal();
				}
			});
			
			StyledText st = getOutputText();
			if (st != null) {
				ScrollBar vsb = st.getVerticalBar();
				if (vsb != null) {
					vsb.addSelectionListener(scrollSelectionListener);
					vsb.addDisposeListener(new DisposeListener() {
						public void widgetDisposed(DisposeEvent e) {
							StyledText st = getOutputText();
							if (st != null) {
								ScrollBar vsb = st.getVerticalBar();
								if (vsb != null) vsb.removeSelectionListener(scrollSelectionListener);
							}
						}});
				}
			}
		}
		
		private SelectionListener scrollSelectionListener = new SelectionListener() {

			public void widgetDefaultSelected(SelectionEvent e) {
			}

			public void widgetSelected(SelectionEvent e) {
				if (!isLastOutputInvisible(getOutputText())) {
					makeTabItemNormal();
				}
			}
			
		};

		protected void makeTabItemBold() {
			changeTabItem(true);
		}

		protected void makeTabItemNormal() {
			changeTabItem(false);
		}

		protected void changeTabItem(boolean bold) {
			CTabItem item = chatRoomTab.tabItem;
			Font oldFont = item.getFont();
			FontData[] fd = oldFont.getFontData();
			item.setFont(new Font(oldFont.getDevice(), fd[0].getName(), fd[0]
					.getHeight(), (bold) ? SWT.BOLD : SWT.NORMAL));
		}

		public void handleMessage(final ID fromID, final String messageBody) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					if (rootDisposed)
						return;
					appendText(chatRoomTab, getOutputText(), new ChatLine(messageBody,
							new ChatRoomParticipant(fromID)));
				}
			});
		}

		public void handleInvitationReceived(ID roomID, ID from,
				String subject, String body) {
			// XXX TODO show UI for invitation
		}

		public void keyPressed(KeyEvent e) {
			handleKeyPressed(e);
		}

		public void keyReleased(KeyEvent e) {
			handleKeyReleased(e);
		}

		protected void handleKeyPressed(KeyEvent evt) {
			Text inputText = getInputText();
			if (evt.character == SWT.CR) {
				if (inputText.getText().trim().length() > 0)
					handleTextInput(inputText.getText());
				clearInput();
				makeTabItemNormal();
				scrollToEnd(getOutputText());
				evt.doit = false;
				isCycling = false;
			} else if (evt.character == SWT.TAB) {
				// don't propogate the event upwards and insert a tab character
				evt.doit = false;
				int pos = inputText.getCaretPosition();
				// if the user is at the beginning of the line, do nothing
				if (pos == 0)
					return;
				String text = inputText.getText();
				// check to see if the user is currently cycling through the
				// available nicknames
				if (isCycling) {
					// if everything's been cycled over, start over at zero
					if (choice == options.size()) {
						choice = 0;
					}
					// cut of the user's nickname based on what's already
					// entered and at a trailing space
					String append = ((String) options.get(choice++))
							.substring(prefixLength)
							+ (isAtStart ? nickCompletionSuffix + " " : " "); //$NON-NLS-1$ //$NON-NLS-2$
					// add what's been typed along with the next nickname option
					// and the rest of the message
					inputText.setText(text.substring(0, caret) + append
							+ text.substring(caret + nickRemainder));
					nickRemainder = append.length();
					// set the caret position to be the place where the nickname
					// completion ended
					inputText.setSelection(caret + nickRemainder, caret
							+ nickRemainder);
				} else {
					// the user is not cycling, so we need to identify what the
					// user has typed based on the current caret position
					int count = pos - 1;
					// keep looping until the whitespace has been identified or
					// the beginning of the message has been reached
					while (count > -1
							&& !Character.isWhitespace(text.charAt(count))) {
						count--;
					}
					count++;
					// remove all previous options
					options.clear();
					// get the prefix that the user typed
					String prefix = text.substring(count, pos);
					isAtStart = count == 0;
					// if what's found was actually whitespace, do nothing
					if (prefix.trim().equals("")) { //$NON-NLS-1$
						return;
					}
					// get all of the users in this room and store them if they
					// start with the prefix that the user has typed
					TableItem[] participants = chatRoomParticipantViewer.getTable().getItems();
					for (int i = 0; i < participants.length; i++) {
						if (participants[i].getText().startsWith(prefix)) {
							options.add(participants[i].getText());
						}
					}

					// simply return if no matches have been found
					if (options.isEmpty())
						return;

					prefixLength = prefix.length();
					if (options.size() == 1) {
						String nickname = (String) options.get(0);
						// since only one nickname is available, simply insert
						// it after truncating the prefix
						nickname = nickname.substring(prefixLength);
						inputText
								.insert(nickname
										+ (isAtStart ? nickCompletionSuffix
												+ " " : " ")); //$NON-NLS-1$ //$NON-NLS-2$
					} else if (options.size() <= maximumCyclingOptions) {
						// note that the user is currently cycling through
						// options and also store the current caret position
						isCycling = true;
						caret = pos;
						choice = 0;
						// insert the nickname after removing the prefix
						String nickname = options.get(choice++)
								+ (isAtStart ? nickCompletionSuffix + " " : " "); //$NON-NLS-1$ //$NON-NLS-2$
						nickname = nickname.substring(prefixLength);
						inputText.insert(nickname);
						// store the length of this truncated nickname so that
						// it can be removed when the user is cycling
						nickRemainder = nickname.length();
					} else {
						// as there are too many choices for the user to pick
						// from, simply display all of the available ones on the
						// chat window so that the user can get a visual
						// indicator of what's available and narrow down the
						// choices by typing a few more additional characters
						StringBuffer choices = new StringBuffer();
						synchronized (choices) {
							for (int i = 0; i < options.size(); i++) {
								choices.append(options.get(i)).append(' ');
							}
							choices.delete(choices.length() - 1, choices
									.length());
						}
						appendText(chatRoomTab, getOutputText(), new ChatLine(choices
								.toString()));
					}
				}
			} else {
				// remove the cycling marking for any other key pressed
				isCycling = false;
			}
		}

		protected void handleKeyReleased(KeyEvent evt) {
			if (evt.character == SWT.TAB) {
				// don't move to the next widget or try to add tabs
				evt.doit = false;
			}
		}

		protected void handleTextInput(String text) {
			if (chatRoomMessageSender == null) {
				MessageDialog.openError(getViewSite().getShell(),
						Messages.ChatRoomManagerView_NOT_CONNECTED_TITLE,
						Messages.ChatRoomManagerView_NOT_CONNECTED_MESSAGE);
				return;
			} else {
				String output = processForCommand(chatRoomContainer, text);
				if (output != null) sendMessageLine(output);
			}
		}

		protected void chatRoomDisconnect() {
			if (chatRoomContainer != null)
				chatRoomContainer.disconnect();
		}

		protected void clearInput() {
			getInputText().setText(""); //$NON-NLS-1$
		}

		protected void sendMessageLine(String line) {
			try {
				chatRoomMessageSender.sendMessage(line);
			} catch (ECFException e) {
				disconnected();
			}
		}

		public void handlePresence(final ID fromID, final IPresence presence) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					if (rootDisposed)
						return;
					boolean isAdd = presence.getType().equals(
							IPresence.Type.AVAILABLE);
					ChatRoomParticipant p = new ChatRoomParticipant(fromID);
					if (isAdd) {
						if (localUser == null)
							localUser = p;
						addParticipant(p);
					} else
						removeParticipant(p);
				}
			});
		}

		public void disconnected() {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					if (rootDisposed)
						return;
					Text inputText = getInputText();
					if (!inputText.isDisposed())
						inputText.setEnabled(false);
				}
			});
		}

		protected boolean isConnected() {
			Text inputText = getInputText();
			return !inputText.isDisposed() && inputText.isEnabled();
		}

		protected void setSelected() {
			rootTabFolder.setSelection(chatRoomTab.tabItem);
		}

		protected void addParticipant(IUser p) {
			if (p != null) {
				ID id = p.getID();
				if (id != null) {
					Preferences prefs = Activator.getDefault()
							.getPluginPreferences();
					
					if (prefs.getBoolean(PreferenceConstants.CHATROOM_SHOW_USER_PRESENCE)) 
						appendText(chatRoomTab, getOutputText(), new ChatLine(NLS.bind(
								Messages.ChatRoomManagerView_ENTERED_MESSAGE,
								getUsernameFromID(id)), null));
					chatRoomParticipantViewer.add(p);
				}
			}
		}

		protected boolean isLocalUser(ID id) {
			if (localUser == null)
				return false;
			else if (localUser.getID().equals(id))
				return true;
			else
				return false;
		}

		protected void removeLocalUser() {
			// It's us that's gone away... so we're outta here
			String title = getPartName();
			setPartName(NLS.bind(
					Messages.ChatRoomManagerView_VIEW_DISABLED_NAME, title));
			removeAllParticipants();
			disconnect();
			setEnabled(false);
		}

		protected void removeParticipant(IUser p) {
			if (p != null) {
				ID id = p.getID();
				if (id != null) {
					Preferences prefs = Activator.getDefault()
					.getPluginPreferences();
			
					if (prefs.getBoolean(PreferenceConstants.CHATROOM_SHOW_USER_PRESENCE)) 
						appendText(chatRoomTab,getOutputText(), new ChatLine(NLS.bind(
								Messages.ChatRoomManagerView_LEFT_MESSAGE,
								getUsernameFromID(id)), null));
					chatRoomParticipantViewer.remove(p);
				}
			}
		}

		protected void removeAllParticipants() {
			Table t = chatRoomParticipantViewer.getTable();
			for (int i = 0; i < t.getItemCount(); i++) {
				Object o = chatRoomParticipantViewer.getElementAt(i);
				if (o != null)
					chatRoomParticipantViewer.remove(o);
			}
		}
	}

	protected void handleTextInput(String text) {
		if (rootMessageSender == null) {
			MessageDialog.openError(getViewSite().getShell(),
					Messages.ChatRoomManagerView_NOT_CONNECTED_TITLE,
					Messages.ChatRoomManagerView_NOT_CONNECTED_MESSAGE);
			return;
		} else {
			String output = processForCommand(null, text);
			if (output != null) sendMessageLine(output);
		}
	}

	protected String processForCommand(IChatRoomContainer chatRoomContainer,
			String text) {
		IChatRoomCommandListener l = commandListener;
		if (l != null)
			return l.handleCommand(chatRoomContainer, text);
		else
			return text;
	}

	protected void handleEnter() {
		Text inputText = getRootTextInput();
		if (inputText.getText().trim().length() > 0)
			handleTextInput(inputText.getText());
		clearInput();
		scrollToEnd(getRootTextOutput());
		rootChannelTab.makeTabItemNormal();
	}

	protected void handleKeyPressed(KeyEvent evt) {
		if (evt.character == SWT.CR) {
			handleEnter();
			evt.doit = false;
		}
	}

	public void setFocus() {
		Text text = getRootTextInput();
		if (text != null)
			text.setFocus();
	}

	public void joinRoom(final IChatRoomInfo info, final String password) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				if (rootDisposed)
					return;
				doJoinRoom(info, password);
			}
		});
	}

	public void dispose() {
		disconnect();
		rootDisposed = true;
		super.dispose();
	}

	protected String getMessageString(ID fromID, String text) {
		return NLS.bind(Messages.ChatRoomManagerView_MESSAGE, fromID.getName(),
				text);
	}

	public void handleMessage(final ID fromID, final String messageBody) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (rootDisposed)
					return;
				appendText(rootChannelTab, getRootTextOutput(), new ChatLine(messageBody,
						new ChatRoomParticipant(fromID)));
				if (rootChannelTab != null) rootChannelTab.makeTabItemBold();
			}
		});
	}

	/**
	 * @return String username for given <code>targetID</code>
	 */
	public static String getUsernameFromID(ID targetID) {
		IChatID chatID = (IChatID) targetID.getAdapter(IChatID.class);
		if (chatID != null)
			return chatID.getUsername();
		else
			try {
				URI uri = new URI(targetID.getName());
				String user = uri.getUserInfo();
				return user == null ? targetID.getName() : user;
			} catch (URISyntaxException e) {
				String userAtHost = targetID.getName();
				int atIndex = userAtHost.lastIndexOf(ATSIGN);
				if (atIndex != -1)
					userAtHost = userAtHost.substring(0, atIndex);
				return userAtHost;
			}
	}

	/**
	 * @return String hostname for given <code>targetID</code>
	 */
	public static String getHostnameFromID(ID targetID) {
		IChatID chatID = (IChatID) targetID.getAdapter(IChatID.class);
		if (chatID != null)
			return chatID.getHostname();
		else
			try {
				URI uri = new URI(targetID.getName());
				String host = uri.getHost();
				return host == null ? targetID.getName() : host;
			} catch (URISyntaxException e) {
				String userAtHost = targetID.getName();
				int atIndex = userAtHost.lastIndexOf(ATSIGN);
				if (atIndex != -1)
					userAtHost = userAtHost.substring(atIndex + 1);
				return userAtHost;
			}
	}

	class ChatRoomParticipant implements IUser, IActionFilter {
		private static final long serialVersionUID = 2008114088656711572L;

		ID id;

		public ChatRoomParticipant(ID id) {
			this.id = id;
		}

		public ID getID() {
			return id;
		}

		public String getName() {
			return toString();
		}

		public boolean equals(Object other) {
			if (!(other instanceof ChatRoomParticipant))
				return false;
			ChatRoomParticipant o = (ChatRoomParticipant) other;
			if (id.equals(o.id))
				return true;
			return false;
		}

		public int hashCode() {
			return id.hashCode();
		}

		public String toString() {
			return getUsernameFromID(id);
		}

		public Map getProperties() {
			return null;
		}

		public Object getAdapter(Class adapter) {
			return null;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.eclipse.ecf.core.user.IUser#getNickname()
		 */
		public String getNickname() {
			return getName();
		}

		public boolean testAttribute(Object target, String name, String value) {
			if(name.equals("scheme")) { //$NON-NLS-1$
				IChatRoomContainer container = ChatRoomManagerView.this.container;
				String scheme = container.getConnectedID().getNamespace().getScheme();
				return scheme.equalsIgnoreCase(value);
			}
			return false;
		}
	}

	public void disconnect() {
		if (rootCloseListener != null) {
			rootCloseListener.chatRoomViewClosing();
		}
		// disconnect from each chat room container
		for (Iterator i = chatRooms.values().iterator(); i.hasNext();) {
			ChatRoom chatRoom = (ChatRoom) i.next();
			IChatRoomContainer container = chatRoom.chatRoomContainer;
			if (container != null)
				container.dispose();
		}
		rootMessageSender = null;
		rootCloseListener = null;
		chatRooms.clear();
	}

	protected void removeLocalUser() {
		// It's us that's gone away... so we're outta here
		String title = getPartName();
		setPartName(NLS.bind(Messages.ChatRoomManagerView_VIEW_DISABLED_NAME,
				title));
		disconnect();
		setEnabled(false);
	}

	public void handleInvitationReceived(ID roomID, ID from, String subject,
			String body) {
		// XXX TODO
	}
	
	private boolean isLastOutputInvisible(StyledText chatText) {
		Point locAtEnd = chatText.getLocationAtOffset(chatText.getText().length());
		Rectangle bounds = chatText.getBounds();
		return (locAtEnd.y > bounds.height + 5);
	}

	private void scrollToEnd(StyledText chatText) {
		chatText.setSelection(chatText.getText().length());
	}
	
	protected void appendText(ChatRoomTab chatRoomTab, StyledText st, ChatLine text) {
		if (st == null || text == null) {
			return;
		}
		
		boolean isAtEndBeforeAppend = !isLastOutputInvisible(st);
		
		String originator = null;
		if (text.getOriginator() != null) {
			originator = text.getOriginator().getNickname(); 
		}
		
		if (messageRenderer == null) messageRenderer = new MessageRenderer();
		
		String output = messageRenderer.render(text.getText(), originator, localUserName);
		StyleRange[] ranges = messageRenderer.getStyleRanges();
		
		if (output == null) {
			return;
		}
		
		int startRange = st.getText().length();
			
		if (!text.isNoCRLF()) {
			output += "\n"; //$NON-NLS-1$
		}
		
		st.append(output);
		if (ranges != null) {

			// set all ranges to start as message line starts
			for (int i = 0; i < ranges.length; i++) {
				ranges[i].start += startRange;
				st.setStyleRange(ranges[i]);
			} 	
		}
		
		if (isAtEndBeforeAppend) scrollToEnd(st);
		if (isCurrentlyActive(chatRoomTab)) chatRoomTab.makeTabItemNormal();
		else chatRoomTab.makeTabItemBold();
	}

	protected void outputClear() {
		if (MessageDialog.openConfirm(null,
				Messages.ChatRoomManagerView_CLEAR_CONFIRM_TITLE,
				Messages.ChatRoomManagerView_CLEAR_CONFIRM_MESSAGE)) {
			getRootTextOutput().setText(""); //$NON-NLS-1$
		}
	}

	protected void outputCopy() {
		StyledText outputText = getRootTextOutput();
		String t = outputText.getSelectionText();
		if (t == null || t.length() == 0) {
			outputText.selectAll();
		}
		outputText.copy();
		outputText.setSelection(outputText.getText().length());
	}

	protected void outputSelectAll() {
		getRootTextOutput().selectAll();
	}

	protected void makeActions() {

		outputSelectAll = new Action() {
			public void run() {
				outputSelectAll();
			}
		};
		outputSelectAll.setText(Messages.ChatRoomManagerView_SELECT_ALL_TEXT);
		outputSelectAll
				.setToolTipText(Messages.ChatRoomManagerView_SELECT_ALL_TOOLTIP);
		outputSelectAll.setAccelerator(SWT.CTRL | 'A');
		outputCopy = new Action() {
			public void run() {
				outputCopy();
			}
		};
		outputCopy.setText(Messages.ChatRoomManagerView_COPY_TEXT);
		outputCopy.setToolTipText(Messages.ChatRoomManagerView_COPY_TOOLTIP);
		outputCopy.setAccelerator(SWT.CTRL | 'C');
		outputCopy.setImageDescriptor(PlatformUI.getWorkbench()
				.getSharedImages().getImageDescriptor(
						ISharedImages.IMG_TOOL_COPY));
		outputClear = new Action() {
			public void run() {
				outputClear();
			}
		};
		outputClear.setText(Messages.ChatRoomManagerView_CLEAR_TEXT);
		outputClear.setToolTipText(Messages.ChatRoomManagerView_CLEAR_TOOLTIP);
		outputPaste = new Action() {
			public void run() {
				getRootTextInput().paste();
			}
		};
		outputPaste.setText(Messages.ChatRoomManagerView_PASTE_TEXT);
		outputPaste.setToolTipText(Messages.ChatRoomManagerView_PASTE_TOOLTIP);
		outputPaste.setAccelerator(SWT.CTRL | 'V');
		outputPaste.setImageDescriptor(PlatformUI.getWorkbench()
				.getSharedImages().getImageDescriptor(
						ISharedImages.IMG_TOOL_PASTE));
	}

	private void fillContextMenu(IMenuManager manager) {
		manager.add(outputCopy);
		manager.add(outputPaste);
		manager.add(outputClear);
		manager.add(new Separator());
		manager.add(outputSelectAll);
		manager.add(new Separator(IWorkbenchActionConstants.MB_ADDITIONS));
	}

	private void hookContextMenu() {
		MenuManager menuMgr = new MenuManager(); 
		menuMgr.setRemoveAllWhenShown(true);
		menuMgr.addMenuListener(new IMenuListener() {
			public void menuAboutToShow(IMenuManager manager) {
				fillContextMenu(manager);
			}
		});
		StyledText outputText = getRootTextOutput();
		Menu menu = menuMgr.createContextMenu(outputText);
		outputText.setMenu(menu);
		ISelectionProvider selectionProvider = new ISelectionProvider() {

			public void addSelectionChangedListener(
					ISelectionChangedListener listener) {
			}

			public ISelection getSelection() {
				StyledText outputText = getRootTextOutput();
				ISelection selection = new TextSelection(outputText
						.getSelectionRange().x,
						outputText.getSelectionRange().y);

				return selection;
			}

			public void removeSelectionChangedListener(
					ISelectionChangedListener listener) {
			}

			public void setSelection(ISelection selection) {
				StyledText outputText = getRootTextOutput();
				if (selection instanceof ITextSelection) {
					ITextSelection textSelection = (ITextSelection) selection;
					outputText.setSelection(textSelection.getOffset(),
							textSelection.getOffset()
									+ textSelection.getLength());
				}
			}

		};
		getSite().registerContextMenu(menuMgr, selectionProvider);
	}

	public void setMessageRenderer(IMessageRenderer defaultMessageRenderer) {
		this.messageRenderer = defaultMessageRenderer;
	}
	
	private boolean isCurrentlyActive(ChatRoomTab chatRoomTab) {
		int selected = rootTabFolder.getSelectionIndex();
		if (selected != -1) {
			CTabItem item = rootTabFolder.getItem(selected);
			if (item == chatRoomTab.tabItem) return true;
		}
		return false;
	}
}
 No newline at end of file