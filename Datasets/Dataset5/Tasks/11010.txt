Display.getDefault().asyncExec(new Runnable() {

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
package org.eclipse.ecf.ui.views;

import java.net.MalformedURLException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.StringTokenizer;

import org.eclipse.ecf.core.IContainerListener;
import org.eclipse.ecf.core.events.IContainerDisconnectedEvent;
import org.eclipse.ecf.core.events.IContainerEvent;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.security.ConnectContextFactory;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.ui.Activator;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.IParticipantListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomInvitationListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessage;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageEvent;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;
import org.eclipse.ecf.presence.chatroom.IChatRoomParticipantListener;
import org.eclipse.ecf.ui.ChatPreferencePage;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.jface.viewers.ListViewer;
import org.eclipse.jface.viewers.ViewerSorter;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabFolder2Listener;
import org.eclipse.swt.custom.CTabFolderEvent;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IWorkbenchPreferenceConstants;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.browser.IWorkbenchBrowserSupport;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.progress.IWorkbenchSiteProgressService;

public class ChatRoomManagerView extends ViewPart implements
		IChatRoomInvitationListener {
	private static final String COMMAND_PREFIX = "/";

	private static final String COMMAND_DELIM = " ";

	private static final String USERNAME_HOST_DELIMETER = "@";

	private static final int RATIO_WRITE_PANE = 1;

	private static final int RATIO_READ_PANE = 7;

	private static final int RATIO_READ_WRITE_PANE = 85;

	private static final int RATIO_PRESENCE_PANE = 15;

	protected static final String DEFAULT_ME_COLOR = "0,255,0";

	protected static final String DEFAULT_OTHER_COLOR = "0,0,0";

	protected static final String DEFAULT_SYSTEM_COLOR = "0,0,255";

	/**
	 * The default color used to highlight the string of text when the user's
	 * name is referred to in the chatroom. The default color is red.
	 */
	protected static final String DEFAULT_HIGHLIGHT_COLOR = "255,0,0";

	protected static final String DEFAULT_DATE_COLOR = "0,0,0";

	protected static final String DEFAULT_TIME_FORMAT = "HH:mm:ss";

	protected static final String DEFAULT_DATE_FORMAT = "yyyy-MM-dd";

	protected static final int DEFAULT_INPUT_HEIGHT = 25;

	protected static final int DEFAULT_INPUT_SEPARATOR = 5;

	private Composite mainComp = null;

	private SimpleLinkTextViewer readText = null;

	private Text writeText = null;

	private CTabFolder tabFolder = null;

	private Manager rootChatRoomTabItem = null;

	private IWorkbenchBrowserSupport browserSupport = PlatformUI.getWorkbench()
			.getBrowserSupport();

	IChatRoomViewCloseListener closeListener = null;

	IChatRoomMessageSender messageSender = null;

	IChatRoomContainer chatRoomContainer = null;

	IChatRoomManager chatRoomManager = null;

	private Color otherColor = null;

	private Color systemColor = null;

	private Color dateColor = null;

	private Color highlightColor = null;

	Action outputClear = null;

	Action outputCopy = null;

	Action outputPaste = null;

	Action outputSelectAll = null;

	boolean disposed = false;

	private ID chatHostID;

	private String userName = "<user>";

	private String hostName = "<host>";

	private boolean enabled = false;

	class Manager {
		SashForm fullChat;

		CTabItem tabItem;

		SashForm rightSash;

		KeyListener keyListener;

		SimpleLinkTextViewer textOutput;

		Text textInput;

		ListViewer listViewer;

		Manager(CTabFolder parent, String name) {
			this(true, parent, name, null);
		}

		Manager(boolean withParticipantsList, CTabFolder parent, String name,
				KeyListener keyListener) {
			tabItem = new CTabItem(parent, SWT.NULL);
			tabItem.setText(name);
			if (withParticipantsList) {
				fullChat = new SashForm(parent, SWT.HORIZONTAL);
				fullChat.setLayout(new FillLayout());
				Composite memberComp = new Composite(fullChat, SWT.NONE);
				memberComp.setLayout(new FillLayout());
				listViewer = new ListViewer(memberComp, SWT.BORDER
						| SWT.V_SCROLL | SWT.H_SCROLL);
				listViewer.setSorter(new ViewerSorter());
				Composite rightComp = new Composite(fullChat, SWT.NONE);
				rightComp.setLayout(new FillLayout());
				rightSash = new SashForm(rightComp, SWT.VERTICAL);
			} else
				rightSash = new SashForm(parent, SWT.VERTICAL);
			Composite readInlayComp = new Composite(rightSash, SWT.FILL);
			readInlayComp.setLayout(new GridLayout());
			readInlayComp.setLayoutData(new GridData(GridData.FILL_BOTH));
			textOutput = new SimpleLinkTextViewer(readInlayComp, SWT.V_SCROLL
					| SWT.H_SCROLL | SWT.WRAP);
			textOutput.getTextWidget().setEditable(false);
			textOutput.getTextWidget().setLayoutData(
					new GridData(GridData.FILL_BOTH));
			Composite writeComp = new Composite(rightSash, SWT.NONE);
			writeComp.setLayout(new FillLayout());
			textInput = new Text(writeComp, SWT.BORDER | SWT.MULTI | SWT.WRAP
					| SWT.V_SCROLL);
			if (keyListener != null)
				textInput.addKeyListener(keyListener);
			rightSash
					.setWeights(new int[] { RATIO_READ_PANE, RATIO_WRITE_PANE });
			if (withParticipantsList) {
				fullChat.setWeights(new int[] { RATIO_PRESENCE_PANE,
						RATIO_READ_WRITE_PANE });
				tabItem.setControl(fullChat);
			} else
				tabItem.setControl(rightSash);
			parent.setSelection(tabItem);
		}

		protected void setTabName(String name) {
			tabItem.setText(name);
		}

		protected Text getTextInput() {
			return textInput;
		}

		protected SimpleLinkTextViewer getTextOutput() {
			return textOutput;
		}

		protected void setKeyListener(KeyListener listener) {
			if (listener != null)
				textInput.addKeyListener(listener);
		}

		protected ListViewer getListViewer() {
			return listViewer;
		}
	}

	public void createPartControl(Composite parent) {
		otherColor = colorFromRGBString(DEFAULT_OTHER_COLOR);
		systemColor = colorFromRGBString(DEFAULT_SYSTEM_COLOR);
		highlightColor = colorFromRGBString(DEFAULT_HIGHLIGHT_COLOR);
		dateColor = colorFromRGBString(DEFAULT_DATE_COLOR);
		mainComp = new Composite(parent, SWT.NONE);
		mainComp.setLayout(new FillLayout());
		boolean useTraditionalTabFolder = PlatformUI
				.getPreferenceStore()
				.getBoolean(
						IWorkbenchPreferenceConstants.SHOW_TRADITIONAL_STYLE_TABS);
		tabFolder = new CTabFolder(mainComp, SWT.NORMAL);
		// The following will allow tab folder to have close buttons on tab
		// items
		// tabFolder = new CTabFolder(mainComp, SWT.CLOSE);
		// tabFolder.setUnselectedCloseVisible(false);
		tabFolder.setSimple(useTraditionalTabFolder);
		PlatformUI.getPreferenceStore().addPropertyChangeListener(
				new IPropertyChangeListener() {
					public void propertyChange(PropertyChangeEvent event) {
						if (event
								.getProperty()
								.equals(
										IWorkbenchPreferenceConstants.SHOW_TRADITIONAL_STYLE_TABS)
								&& !tabFolder.isDisposed()) {
							tabFolder.setSimple(((Boolean) event.getNewValue())
									.booleanValue());
							tabFolder.redraw();
						}
					}
				});

		tabFolder.addCTabFolder2Listener(new CTabFolder2Listener() {
			public void close(CTabFolderEvent event) {
				System.out.println("close(" + event + ")");
			}

			public void maximize(CTabFolderEvent event) {
				System.out.println("maximize(" + event + ")");
			}

			public void minimize(CTabFolderEvent event) {
				System.out.println("minimize(" + event + ")");
			}

			public void restore(CTabFolderEvent event) {
				System.out.println("restore(" + event + ")");
			}

			public void showList(CTabFolderEvent event) {
				System.out.println("showList(" + event + ")");
			}
		});
		rootChatRoomTabItem = new Manager(false, tabFolder, hostName,
				new KeyListener() {
					public void keyPressed(KeyEvent evt) {
						handleKeyPressed(evt);
					}

					public void keyReleased(KeyEvent evt) {
						handleKeyReleased(evt);
					}
				});
		writeText = rootChatRoomTabItem.getTextInput();
		readText = rootChatRoomTabItem.getTextOutput();
		setEnabled(false);
		makeActions();
		hookContextMenu();
	}

	public void initialize(final IChatRoomViewCloseListener parent,
			final IChatRoomContainer container,
			final IChatRoomManager chatRoomManager, final ID targetID,
			final IChatRoomMessageSender sender) {
		ChatRoomManagerView.this.chatRoomManager = chatRoomManager;
		ChatRoomManagerView.this.closeListener = parent;
		ChatRoomManagerView.this.chatRoomContainer = container;
		ChatRoomManagerView.this.chatHostID = targetID;
		ChatRoomManagerView.this.messageSender = sender;
		setUsernameAndHost(ChatRoomManagerView.this.chatHostID);
		ChatRoomManagerView.this.setPartName(userName + USERNAME_HOST_DELIMETER
				+ hostName);
		ChatRoomManagerView.this.setTitleToolTip("IRC Host: " + hostName);
		ChatRoomManagerView.this.rootChatRoomTabItem.setTabName(hostName);
		setEnabled(true);
	}

	protected void setEnabled(boolean enabled) {
		this.enabled = enabled;
		if (!writeText.isDisposed())
			writeText.setEnabled(enabled);
	}

	public boolean isEnabled() {
		return enabled;
	}

	protected void clearInput() {
		writeText.setText("");
	}

	protected void handleCommands(String line, String[] tokens) {
		// Look at first one and switch
		String command = tokens[0];
		while (command.startsWith(COMMAND_PREFIX))
			command = command.substring(1);
		String[] args = new String[tokens.length - 1];
		System.arraycopy(tokens, 1, args, 0, tokens.length - 1);
		if (command.equalsIgnoreCase("QUIT")) {
			doQuit();
		} else if (command.equalsIgnoreCase("JOIN")) {
			String arg1 = args[0];
			String arg2 = "";
			if (args.length > 1) {
				arg2 = args[1];
			}
			doJoin(arg1, arg2);
		} else
			sendMessageLine(line);
	}

	protected void sendMessageLine(String line) {
		try {
			messageSender.sendMessage(line);
		} catch (ECFException e) {
			// And cut ourselves off
			removeLocalUser();
		}
	}

	public void disconnected() {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (disposed)
					return;
				setEnabled(false);
				setPartName("(" + getPartName() + ")");
			}
		});
	}

	protected void doQuit() {
		cleanUp();
	}

	protected void doJoin(String target, String key) {
		// With manager, first thing we do is get the IChatRoomInfo for the
		// target
		// channel
		IChatRoomInfo roomInfo = chatRoomManager.getChatRoomInfo(target);
		// If it's null, we give up
		if (roomInfo == null)
			// no room info for given target...give error message and skip
			return;
		else {
			IChatRoomContainer chatRoomContainer = null;
			try {
				// Then we create a new container from the roomInfo
				chatRoomContainer = roomInfo.createChatRoomContainer();
				// Setup new user interface (new tab)
				final ChatRoom chatroomview = new ChatRoom(chatRoomContainer,
						new Manager(tabFolder, target));
				// setup message listener
				chatRoomContainer.addMessageListener(new IIMMessageListener() {
					public void handleMessageEvent(IIMMessageEvent messageEvent) {
						if (messageEvent instanceof IChatRoomMessageEvent) {
							IChatRoomMessage m = ((IChatRoomMessageEvent) messageEvent)
									.getChatRoomMessage();
							chatroomview.handleMessage(m.getFromID(), m
									.getMessage());
						}
					}
				});
				// setup participant listener
				chatRoomContainer
						.addChatRoomParticipantListener(new IChatRoomParticipantListener() {
							public void handlePresence(ID fromID,
									IPresence presence) {
								chatroomview.handlePresence(fromID, presence);
							}

							public void handleArrivedInChat(ID participant) {
								chatroomview.handleJoin(participant);
							}

							public void handleDepartedFromChat(ID participant) {
								chatroomview.handleLeave(participant);
							}
						});
				chatRoomContainer.addListener(new IContainerListener() {
					public void handleEvent(IContainerEvent evt) {
						if (evt instanceof IContainerDisconnectedEvent) {
							chatroomview.disconnected();
						}
					}
				});
				// Now connect/join
				chatRoomContainer
						.connect(
								IDFactory.getDefault()
										.createID(
												chatRoomContainer
														.getConnectNamespace(),
												target), ConnectContextFactory
										.createPasswordConnectContext(key));
			} catch (Exception e) {
				// TODO: handle exception properly
				e.printStackTrace();
			}
		}
	}

	class ChatRoom implements IChatRoomInvitationListener,
			IParticipantListener, KeyListener {
		IChatRoomContainer container;

		Manager tabUI;

		Text inputText;

		SimpleLinkTextViewer outputText;

		IChatRoomMessageSender channelMessageSender;

		private List otherUsers = Collections.synchronizedList(new ArrayList());

		IUser localUser;

		private ListViewer memberViewer = null;

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

		ChatRoom(IChatRoomContainer container, Manager tabItem) {
			this.container = container;
			this.channelMessageSender = container.getChatRoomMessageSender();
			this.tabUI = tabItem;
			inputText = this.tabUI.getTextInput();
			outputText = this.tabUI.getTextOutput();
			memberViewer = this.tabUI.getListViewer();
			options = new ArrayList();
			this.tabUI.setKeyListener(this);
		}

		public void handleMessage(final ID fromID, final String messageBody) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					if (disposed)
						return;
					appendText(outputText, new ChatLine(messageBody,
							new Participant(fromID)));
				}
			});
		}

		public void handleInvitationReceived(ID roomID, ID from,
				String subject, String body) {
			System.out.println("invitation room=" + roomID + ",from=" + from
					+ ",subject=" + subject + ",body=" + body);
		}

		public void keyPressed(KeyEvent e) {
			handleKeyPressed(e);
		}

		public void keyReleased(KeyEvent e) {
			handleKeyReleased(e);
		}

		protected void handleKeyPressed(KeyEvent evt) {
			if (evt.character == SWT.CR) {
				if (inputText.getText().trim().length() > 0)
					handleTextInput(inputText.getText());
				clearInput();
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
							+ (isAtStart ? nickCompletionSuffix + " " : " ");
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
					if (prefix.trim().equals(""))
						return;
					// get all of the users in this room and store them if they
					// start with the prefix that the user has typed
					String[] participants = memberViewer.getList().getItems();
					for (int i = 0; i < participants.length; i++) {
						if (participants[i].startsWith(prefix)) {
							options.add(participants[i]);
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
												+ " " : " "));
					} else if (options.size() <= maximumCyclingOptions) {
						// note that the user is currently cycling through
						// options and also store the current caret position
						isCycling = true;
						caret = pos;
						choice = 0;
						// insert the nickname after removing the prefix
						String nickname = options.get(choice++)
								+ (isAtStart ? nickCompletionSuffix + " " : " ");
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
								choices.append(options.get(i)).append(" ");
							}
							choices.delete(choices.length() - 1, choices
									.length());
						}
						appendText(outputText, new ChatLine(choices.toString()));
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
			if (channelMessageSender == null) {
				MessageDialog.openError(getViewSite().getShell(),
						"Not connect", "Not connected to channel room");
				return;
			} else
				handleInputLine(text);
		}

		protected void handleInputLine(String line) {
			if ((line != null && line.startsWith(COMMAND_PREFIX))) {
				StringTokenizer st = new StringTokenizer(line, COMMAND_DELIM);
				int countTokens = st.countTokens();
				String toks[] = new String[countTokens];
				for (int i = 0; i < countTokens; i++) {
					toks[i] = st.nextToken();
				}
				String[] tokens = toks;
				handleCommands(line, tokens);
			} else
				sendMessageLine(line);
		}

		protected void handleCommands(String line, String[] tokens) {
			// Look at first one and switch
			String command = tokens[0];
			while (command.startsWith(COMMAND_PREFIX))
				command = command.substring(1);
			String[] args = new String[tokens.length - 1];
			System.arraycopy(tokens, 1, args, 0, tokens.length - 1);
			if (command.equalsIgnoreCase("QUIT")) {
				doQuit();
			} else if (command.equalsIgnoreCase("PART")) {
				doPartChannel();
			} else
				sendMessageLine(line);
		}

		protected void doPartChannel() {
			if (container != null)
				container.disconnect();
		}

		protected void clearInput() {
			inputText.setText("");
		}

		protected void sendMessageLine(String line) {
			try {
				channelMessageSender.sendMessage(line);
			} catch (ECFException e) {
				// XXX handle gracefully
				e.printStackTrace();
			}
		}

		public void handlePresence(final ID fromID, final IPresence presence) {
			Display.getDefault().syncExec(new Runnable() {
				public void run() {
					if (disposed)
						return;
					boolean isAdd = presence.getType().equals(
							IPresence.Type.AVAILABLE);
					Participant p = new Participant(fromID);
					if (isAdd) {
						if (localUser == null && !otherUsers.contains(fromID)) {
							localUser = p;
						}
						addParticipant(p);
					} else {
						removeParticipant(p);
						if (isLocalUser(fromID))
							removeLocalUser();
					}
				}
			});
		}

		public void disconnected() {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					if (disposed)
						return;
					if (!inputText.isDisposed())
						inputText.setEnabled(false);
				}
			});
		}

		protected void addParticipant(IUser p) {
			if (p != null) {
				ID id = p.getID();
				if (id != null) {
					appendText(outputText, new ChatLine("(" + getDateTime()
							+ ") " + trimUserID(id) + " entered", null));
					memberViewer.add(p);
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
			setPartName("(" + title + ")");
			removeAllParticipants();
			cleanUp();
			setEnabled(false);
		}

		protected void removeParticipant(IUser p) {
			if (p != null) {
				ID id = p.getID();
				if (id != null) {
					if (otherUsers.contains(id))
						appendText(outputText, new ChatLine("(" + getDateTime()
								+ ") " + trimUserID(id) + " left", null));
					memberViewer.remove(p);
					if (isLocalUser(id))
						removeLocalUser();
				}
			}
		}

		protected void removeAllParticipants() {
			org.eclipse.swt.widgets.List l = memberViewer.getList();
			for (int i = 0; i < l.getItemCount(); i++) {
				Object o = memberViewer.getElementAt(i);
				if (o != null)
					memberViewer.remove(o);
			}
		}

		public void handleJoin(ID user) {
			if (disposed)
				return;
			otherUsers.add(user);
		}

		public void handleLeave(ID user) {
			if (disposed)
				return;
			otherUsers.remove(user);
		}
	}

	protected void handleInputLine(String line) {
		if ((line != null && line.startsWith(COMMAND_PREFIX))) {
			StringTokenizer st = new StringTokenizer(line, COMMAND_DELIM);
			int countTokens = st.countTokens();
			String toks[] = new String[countTokens];
			for (int i = 0; i < countTokens; i++) {
				toks[i] = st.nextToken();
			}
			String[] tokens = toks;
			handleCommands(line, tokens);
		} else
			sendMessageLine(line);
	}

	protected void handleTextInput(String text) {
		if (messageSender == null) {
			MessageDialog.openError(getViewSite().getShell(), "Not connect",
					"Not connected to chat room");
			return;
		} else
			handleInputLine(text);
	}

	protected void handleEnter() {
		if (writeText.getText().trim().length() > 0)
			handleTextInput(writeText.getText());
		clearInput();
	}

	protected void handleKeyPressed(KeyEvent evt) {
		if (evt.character == SWT.CR) {
			handleEnter();
			evt.doit = false;
		}
	}

	protected void handleKeyReleased(KeyEvent evt) {
	}

	public void setFocus() {
		writeText.setFocus();
	}

	protected void setUsernameAndHost(ID chatHostID) {
		URI uri = null;
		try {
			uri = new URI(chatHostID.getName());
			String tmp = uri.getUserInfo();
			if (tmp != null)
				userName = tmp;
			tmp = uri.getHost();
			if (tmp != null)
				hostName = tmp;
		} catch (URISyntaxException e) {
		}
	}

	public void joinRoom(final String room) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (disposed)
					return;
				if (room != null)
					doJoin(room, null);
			}
		});
	}

	public void dispose() {
		disposed = true;
		cleanUp();
		super.dispose();
	}

	protected String getMessageString(ID fromID, String text) {
		return fromID.getName() + ": " + text + "\n";
	}

	public void handleMessage(final ID fromID, final String messageBody) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (disposed)
					return;
				appendText(readText, new ChatLine(messageBody, new Participant(
						fromID)));
			}
		});
	}

	private String trimUserID(ID userID) {
		URI aURI = null;
		try {
			aURI = new URI(userID.getName());
		} catch (URISyntaxException e) {
			aURI = null;
		}
		if (aURI != null) {
			String user = aURI.getUserInfo();
			if (user != null)
				return user;
			else
				return userID.getName();
		} else {
			String userathost = userID.getName();
			int atIndex = userathost.lastIndexOf(USERNAME_HOST_DELIMETER);
			if (atIndex != -1) {
				userathost = userathost.substring(0, atIndex);
			}
			return userathost;
		}
	}

	class Participant implements IUser {
		private static final long serialVersionUID = 2008114088656711572L;

		ID id;

		public Participant(ID id) {
			this.id = id;
		}

		public ID getID() {
			return id;
		}

		public String getName() {
			return toString();
		}

		public boolean equals(Object other) {
			if (!(other instanceof Participant))
				return false;
			Participant o = (Participant) other;
			if (id.equals(o.id))
				return true;
			return false;
		}

		public int hashCode() {
			return id.hashCode();
		}

		public String toString() {
			return trimUserID(id);
		}

		public Map getProperties() {
			return null;
		}

		public Object getAdapter(Class adapter) {
			return null;
		}
	}

	protected String getCurrentDate(String format) {
		SimpleDateFormat sdf = new SimpleDateFormat(format);
		String res = sdf.format(new Date());
		return res;
	}

	protected String getDateTime() {
		StringBuffer buf = new StringBuffer();
		buf.append(getCurrentDate(DEFAULT_DATE_FORMAT)).append(" ").append(
				getCurrentDate(DEFAULT_TIME_FORMAT));
		return buf.toString();
	}

	protected void cleanUp() {
		if (closeListener != null) {
			if (chatHostID == null)
				closeListener.chatRoomViewClosing(null);
			else
				closeListener.chatRoomViewClosing(chatHostID.getName());
			closeListener = null;
			chatRoomContainer = null;
			messageSender = null;
		}
	}

	protected void removeLocalUser() {
		// It's us that's gone away... so we're outta here
		String title = getPartName();
		setPartName("(" + title + ")");
		cleanUp();
		setEnabled(false);
	}

	public void handleInvitationReceived(ID roomID, ID from, String subject,
			String body) {
		System.out.println("invitation room=" + roomID + ",from=" + from
				+ ",subject=" + subject + ",body=" + body);
	}

	private boolean intelligentAppend(SimpleLinkTextViewer readText,
			StyledText st, ChatLine text) {
		String line = text.getText();
		// check to see if a link exists in this line
		int index = line.indexOf("http://"); //$NON-NLS-1$
		if (index == -1) {
			index = line.indexOf("https://"); //$NON-NLS-1$
			if (index == -1) {
				index = line.indexOf("www."); //$NON-NLS-1$
				if (index == -1) {
					return false;
				}
			}
		} else {
			int nextIndex = line.indexOf("https://"); //$NON-NLS-1$
			if (nextIndex != -1 && nextIndex < index) {
				index = nextIndex;
			}

			nextIndex = line.indexOf("www."); //$NON-NLS-1$
			if (nextIndex != -1 && nextIndex < index) {
				index = nextIndex;
			}
		}

		int startRange = st.getText().length();
		StringBuffer sb = new StringBuffer();
		// check to see if the message has the user's name contained within
		boolean nickContained = text.getText().indexOf(userName) != -1;
		if (text.getOriginator() != null) {
			// check to make sure that the person referring to the user's name
			// is not the user himself, no highlighting is required in this case
			// as the user is already aware that his name is being referenced
			nickContained = !text.getOriginator().getName().equals(userName)
					&& nickContained;
			sb.append('(').append(getCurrentDate(DEFAULT_TIME_FORMAT)).append(
					") "); //$NON-NLS-1$
			StyleRange dateStyle = new StyleRange();
			dateStyle.start = startRange;
			dateStyle.length = sb.length();
			dateStyle.foreground = dateColor;
			dateStyle.fontStyle = SWT.NORMAL;
			st.append(sb.toString());
			st.setStyleRange(dateStyle);
			sb = new StringBuffer();
			sb.append(text.getOriginator().getName()).append(": "); //$NON-NLS-1$
			StyleRange sr = new StyleRange();
			sr.start = startRange + dateStyle.length;
			sr.length = sb.length();
			sr.fontStyle = SWT.BOLD;
			// check to see which color should be used
			sr.foreground = nickContained ? highlightColor : otherColor;
			st.append(sb.toString());
			st.setStyleRange(sr);
		}

		while (index != -1) {
			String front = line.substring(0, index);
			line = line.substring(index);
			int beforeMessageIndex = st.getText().length();
			st.append(front);
			if (text.getOriginator() == null) {
				StyleRange sr = new StyleRange();
				sr.start = beforeMessageIndex;
				sr.length = front.length();
				sr.foreground = systemColor;
				sr.fontStyle = SWT.BOLD;
				st.setStyleRange(sr);
			} else if (nickContained) {
				// highlight the message itself as necessary
				StyleRange sr = new StyleRange();
				sr.start = beforeMessageIndex;
				sr.length = front.length();
				sr.foreground = highlightColor;
				st.setStyleRange(sr);
			}

			int spaceIndex = line.indexOf(' ');
			if (spaceIndex != -1) {
				String url = line.substring(0, spaceIndex);
				if (!url.startsWith("http")) { //$NON-NLS-1$
					readText.appendLink(url, createLinkRunnable("http://" //$NON-NLS-1$
							+ url));
				} else {
					readText.appendLink(url, createLinkRunnable(url));
				}
				line = line.substring(spaceIndex);
				index = line.indexOf("http://"); //$NON-NLS-1$
				if (index == -1) {
					index = line.indexOf("https://"); //$NON-NLS-1$
					if (index == -1) {
						index = line.indexOf("www."); //$NON-NLS-1$
						if (index == -1) {
							return false;
						}
					}
				} else {
					int nextIndex = line.indexOf("https://"); //$NON-NLS-1$
					if (nextIndex != -1 && nextIndex < index) {
						index = nextIndex;
					}

					nextIndex = line.indexOf("www."); //$NON-NLS-1$
					if (nextIndex != -1 && nextIndex < index) {
						index = nextIndex;
					}
				}
			} else {
				if (!line.startsWith("http")) { //$NON-NLS-1$
					readText.appendLink(line, createLinkRunnable("http://" //$NON-NLS-1$
							+ line));
				} else {
					readText.appendLink(line, createLinkRunnable(line));
				}
				line = null;
				break;
			}
		}

		if (line != null && !line.equals("")) { //$NON-NLS-1$
			int beforeMessageIndex = st.getText().length();
			st.append(line);
			if (text.getOriginator() == null) {
				StyleRange sr = new StyleRange();
				sr.start = beforeMessageIndex;
				sr.length = line.length();
				sr.foreground = systemColor;
				sr.fontStyle = SWT.BOLD;
				st.setStyleRange(sr);
			} else if (nickContained) {
				// highlight the message itself as necessary
				StyleRange sr = new StyleRange();
				sr.start = beforeMessageIndex;
				sr.length = line.length();
				sr.foreground = highlightColor;
				st.setStyleRange(sr);
			}
		}

		if (!text.isNoCRLF()) {
			st.append("\n"); //$NON-NLS-1$
		}

		return true;
	}

	private Runnable createLinkRunnable(final String url) {
		return new Runnable() {
			public void run() {
				URL link = null;
				try {
					link = new URL(url);
				} catch (MalformedURLException e) {
					MessageDialog.openError(getSite().getShell(), "Link Error",
							"The link is not of a proper form");
					return;
				}
				if (browserSupport.isInternalWebBrowserAvailable()) {
					String pref = Activator
							.getDefault()
							.getPreferenceStore()
							.getString(ChatPreferencePage.PREF_BROWSER_FOR_CHAT);
					try {
						if (pref.equals(ChatPreferencePage.VIEW)) {
							browserSupport.createBrowser(
									IWorkbenchBrowserSupport.AS_VIEW,
									"org.eclipse.ecf", url, url).openURL(link);
						} else if (pref.equals(ChatPreferencePage.EDITOR)) {
							browserSupport.createBrowser(
									IWorkbenchBrowserSupport.AS_EDITOR,
									"org.eclipse.ecf", url, url).openURL(link);
						} else {
							try {
								browserSupport.getExternalBrowser().openURL(
										link);
							} catch (PartInitException ex) {
								MessageDialog.openError(getSite().getShell(),
										"Browser Error",
										"Could not open a browser instance.");
							}
						}
					} catch (PartInitException e) {
						try {
							browserSupport.getExternalBrowser().openURL(link);
						} catch (PartInitException ex) {
							MessageDialog.openError(getSite().getShell(),
									"Browser Error",
									"Could not open a browser instance.");
						}
					}
				} else {
					try {
						browserSupport.getExternalBrowser().openURL(link);
					} catch (PartInitException e) {
						MessageDialog.openError(getSite().getShell(),
								"Browser Error",
								"Could not open a browser instance.");
					}
				}
			}
		};
	}

	protected void appendText(SimpleLinkTextViewer readText, ChatLine text) {
		if (readText == null || text == null) {
			return;
		}
		StyledText st = readText.getTextWidget();
		if (st == null || intelligentAppend(readText, st, text)) {
			return;
		}
		int startRange = st.getText().length();
		StringBuffer sb = new StringBuffer();
		// check to see if the message has the user's name contained within
		boolean nickContained = text.getText().indexOf(userName) != -1;
		if (text.getOriginator() != null) {
			// check to make sure that the person referring to the user's name
			// is not the user himself, no highlighting is required in this case
			// as the user is already aware that his name is being referenced
			nickContained = !text.getOriginator().getName().equals(userName)
					&& nickContained;
			sb.append("(").append(getCurrentDate(DEFAULT_TIME_FORMAT)).append(
					") ");
			StyleRange dateStyle = new StyleRange();
			dateStyle.start = startRange;
			dateStyle.length = sb.length();
			dateStyle.foreground = dateColor;
			dateStyle.fontStyle = SWT.NORMAL;
			st.append(sb.toString());
			st.setStyleRange(dateStyle);
			sb = new StringBuffer();
			sb.append(text.getOriginator().getName()).append(": ");
			StyleRange sr = new StyleRange();
			sr.start = startRange + dateStyle.length;
			sr.length = sb.length();
			sr.fontStyle = SWT.BOLD;
			// check to see which color should be used
			sr.foreground = nickContained ? highlightColor : otherColor;
			st.append(sb.toString());
			st.setStyleRange(sr);
		}
		int beforeMessageIndex = st.getText().length();
		st.append(text.getText());
		if (text.getOriginator() == null) {
			StyleRange sr = new StyleRange();
			sr.start = beforeMessageIndex;
			sr.length = text.getText().length();
			sr.foreground = systemColor;
			sr.fontStyle = SWT.BOLD;
			st.setStyleRange(sr);
		} else if (nickContained) {
			// highlight the message itself as necessary
			StyleRange sr = new StyleRange();
			sr.start = beforeMessageIndex;
			sr.length = text.getText().length();
			sr.foreground = highlightColor;
			st.setStyleRange(sr);
		}
		if (!text.isNoCRLF()) {
			st.append("\n");
		}
		String t = st.getText();
		if (t == null)
			return;
		st.setSelection(t.length());
		// Bold title if view is not visible.
		IWorkbenchSiteProgressService pservice = (IWorkbenchSiteProgressService) this
				.getSite().getAdapter(IWorkbenchSiteProgressService.class);
		pservice.warnOfContentChange();
	}

	protected void outputClear() {
		if (MessageDialog.openConfirm(null, "Confirm Clear Text Output",
				"Are you sure you want to clear output?"))
			readText.getTextWidget().setText("");
	}

	protected void outputCopy() {
		String t = readText.getTextWidget().getSelectionText();
		if (t == null || t.length() == 0) {
			readText.getTextWidget().selectAll();
		}
		readText.getTextWidget().copy();
		readText.getTextWidget().setSelection(
				readText.getTextWidget().getText().length());
	}

	protected void outputPaste() {
		writeText.paste();
	}

	protected void outputSelectAll() {
		readText.getTextWidget().selectAll();
	}

	protected void makeActions() {
		outputSelectAll = new Action() {
			public void run() {
				outputSelectAll();
			}
		};
		outputSelectAll.setText("Select All");
		outputSelectAll.setToolTipText("Select All");
		outputSelectAll.setAccelerator(SWT.CTRL | 'A');
		outputCopy = new Action() {
			public void run() {
				outputCopy();
			}
		};
		outputCopy.setText("Copy");
		outputCopy.setToolTipText("Copy Selected");
		outputCopy.setAccelerator(SWT.CTRL | 'C');
		outputCopy.setImageDescriptor(PlatformUI.getWorkbench()
				.getSharedImages().getImageDescriptor(
						ISharedImages.IMG_TOOL_COPY));
		outputClear = new Action() {
			public void run() {
				outputClear();
			}
		};
		outputClear.setText("Clear");
		outputClear.setToolTipText("Clear output window");
		outputPaste = new Action() {
			public void run() {
				outputPaste();
			}
		};
		outputPaste.setText("Paste");
		outputPaste.setToolTipText("Paste");
		outputCopy.setAccelerator(SWT.CTRL | 'V');
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
		manager.add(new Separator("Additions"));
	}

	private void hookContextMenu() {
		MenuManager menuMgr = new MenuManager("#PopupMenu");
		menuMgr.setRemoveAllWhenShown(true);
		menuMgr.addMenuListener(new IMenuListener() {
			public void menuAboutToShow(IMenuManager manager) {
				fillContextMenu(manager);
			}
		});
		Menu menu = menuMgr.createContextMenu(readText.getControl());
		readText.getControl().setMenu(menu);
		getSite().registerContextMenu(menuMgr, readText);
	}

	private Color colorFromRGBString(String rgb) {
		Color color = null;
		if (rgb == null || rgb.equals("")) {
			color = new Color(getViewSite().getShell().getDisplay(), 0, 0, 0);
			return color;
		}
		if (color != null) {
			color.dispose();
		}
		String[] vals = rgb.split(",");
		color = new Color(getViewSite().getShell().getDisplay(), Integer
				.parseInt(vals[0]), Integer.parseInt(vals[1]), Integer
				.parseInt(vals[2]));
		return color;
	}
}
 No newline at end of file