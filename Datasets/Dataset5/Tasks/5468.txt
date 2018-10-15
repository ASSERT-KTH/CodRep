outputPaste.setAccelerator(SWT.CTRL | 'V');

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

package org.eclipse.ecf.ui.views;

import java.net.URI;
import java.net.URISyntaxException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.presence.IParticipantListener;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.chatroom.IChatRoomContainer;
import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomInvitationListener;
import org.eclipse.ecf.presence.chatroom.IChatRoomMessageSender;
import org.eclipse.ecf.presence.im.IChatID;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ListViewer;
import org.eclipse.swt.SWT;
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
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.progress.IWorkbenchSiteProgressService;

public class ChatRoomView extends ViewPart implements IParticipantListener, IChatRoomInvitationListener {
	private static final String USERNAME_HOST_DELIMETER = "@";

	private static final int RATIO_WRITE_PANE = 2;

	private static final int RATIO_READ_PANE = 7;

	private static final int RATIO_READ_WRITE_PANE = 85;

	private static final int RATIO_PRESENCE_PANE = 15;

	protected static final String DEFAULT_ME_COLOR = "0,255,0";

	protected static final String DEFAULT_OTHER_COLOR = "0,0,0";

	protected static final String DEFAULT_SYSTEM_COLOR = "0,0,255";

	protected static final String DEFAULT_DATE_COLOR = "0,0,0";

	protected static final String VIEW_PREFIX = "Chat: ";

	protected static final String DEFAULT_TIME_FORMAT = "HH:mm:ss";

	protected static final String DEFAULT_DATE_FORMAT = "yyyy-MM-dd";

	protected static final int DEFAULT_INPUT_HEIGHT = 25;

	protected static final int DEFAULT_INPUT_SEPARATOR = 5;

	private Composite mainComp = null;

	private IChatRoomInfo roomInfo = null;

	private Text writeText = null;

	private SimpleLinkTextViewer readText = null;

	private ListViewer memberViewer = null;

	IChatRoomViewCloseListener closeListener = null;

	IChatRoomMessageSender messageSender = null;

	IChatRoomContainer chatRoomContainer = null;

	String viewID = null;

	private Color meColor = null;

	private Color otherColor = null;

	private Color systemColor = null;

	private Color dateColor = null;

	private IUser localUser = null;

	private List otherUsers = Collections.synchronizedList(new ArrayList());

	Action outputClear = null;

	Action outputCopy = null;

	Action outputPaste = null;

	Action outputSelectAll = null;

	boolean disposed = false;

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

	public void createPartControl(Composite parent) {

		meColor = colorFromRGBString(DEFAULT_ME_COLOR);
		otherColor = colorFromRGBString(DEFAULT_OTHER_COLOR);
		systemColor = colorFromRGBString(DEFAULT_SYSTEM_COLOR);
		dateColor = colorFromRGBString(DEFAULT_DATE_COLOR);

		mainComp = new Composite(parent, SWT.NONE);
		mainComp.setLayout(new FillLayout());

		SashForm form = new SashForm(mainComp, SWT.HORIZONTAL);
		form.setLayout(new FillLayout());

		Composite memberComp = new Composite(form, SWT.NONE);
		memberComp.setLayout(new FillLayout());
		memberViewer = new ListViewer(memberComp, SWT.BORDER | SWT.V_SCROLL
				| SWT.H_SCROLL);

		Composite rightComp = new Composite(form, SWT.NONE);
		rightComp.setLayout(new FillLayout());

		SashForm rightSash = new SashForm(rightComp, SWT.VERTICAL);
		rightSash.setLayout(new FillLayout());

		Composite readComp = new Composite(rightSash, SWT.BORDER);
		readComp.setLayout(new FillLayout());
		Composite readInlayComp = new Composite(readComp, SWT.NONE);
		readInlayComp.setLayout(new GridLayout());
		readInlayComp.setLayoutData(new GridData(GridData.FILL_BOTH));
		readInlayComp.setBackground(memberViewer.getList().getBackground());
		readText = new SimpleLinkTextViewer(readInlayComp, SWT.V_SCROLL
				| SWT.H_SCROLL | SWT.WRAP);

		readText.getTextWidget().setEditable(false);
		readText.getTextWidget()
				.setLayoutData(new GridData(GridData.FILL_BOTH));

		Composite writeComp = new Composite(rightSash, SWT.NONE);
		writeComp.setLayout(new FillLayout());
		writeText = new Text(writeComp, SWT.BORDER | SWT.MULTI | SWT.WRAP
				| SWT.V_SCROLL);
		writeText.addKeyListener(new KeyListener() {
			public void keyPressed(KeyEvent evt) {
				handleKeyPressed(evt);
			}

			public void keyReleased(KeyEvent evt) {
				handleKeyReleased(evt);
			}
		});

		form
				.setWeights(new int[] { RATIO_PRESENCE_PANE,
						RATIO_READ_WRITE_PANE });
		rightSash.setWeights(new int[] { RATIO_READ_PANE, RATIO_WRITE_PANE });
		setEnabled(false);
		makeActions();
		hookContextMenu();
	}

	protected void setEnabled(boolean enabled) {
		if (!writeText.isDisposed())
			writeText.setEnabled(enabled);
	}

	protected void clearInput() {
		writeText.setText("");
	}

	protected void handleTextInput(String text) {
		if (messageSender == null) {
			MessageDialog.openError(getViewSite().getShell(), "Not connect",
					"Not connected to chat room");
			return;
		} else {
			try {
				messageSender.sendMessage(text);
			} catch (ECFException e) {
				// And cut ourselves off
				removeLocalUser();
			}
		}
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

	public IChatRoomInfo getRoomInfo() {
		return roomInfo;
	}

	public void initialize(final IChatRoomViewCloseListener parent,
			final String secondaryID, final IChatRoomContainer container,
			final IChatRoomInfo info, final IChatRoomMessageSender sender) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				removeAllParticipants();
				otherUsers.clear();
				localUser = null;
				ChatRoomView.this.viewID = secondaryID;
				ChatRoomView.this.closeListener = parent;
				ChatRoomView.this.chatRoomContainer = container;
				ChatRoomView.this.messageSender = sender;
				ChatRoomView.this.roomInfo = info;
				ID roomID = info.getRoomID();
				ChatRoomView.this.setPartName(VIEW_PREFIX + roomInfo.getName());
				ChatRoomView.this.setTitleToolTip("Room ID: "
						+ roomID.getName() + ", Description: "
						+ roomInfo.getDescription());
				setEnabled(true);
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
				appendText(new ChatLine(messageBody, new Participant(fromID)));
			}
		});
	}

	private String trimUserID(ID userID) {
		URI aURI = null;
		IChatID chatID = (IChatID) userID.getAdapter(IChatID.class);
		if (chatID != null)
			return chatID.getUsername();
		else {
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

		/* (non-Javadoc)
		 * @see org.eclipse.ecf.core.user.IUser#getNickname()
		 */
		public String getNickname() {
			return getName();
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

	protected void addParticipant(IUser p) {
		if (p != null) {
			ID id = p.getID();
			if (id != null) {
				appendText(new ChatLine("(" + getDateTime() + ") "
						+ trimUserID(id) + " entered", null));
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

	protected void cleanUp() {
		if (closeListener != null) {
			closeListener.chatRoomViewClosing(viewID);
			closeListener = null;
			viewID = null;
			chatRoomContainer = null;
			messageSender = null;
			roomInfo = null;
		}
		otherUsers.clear();
		localUser = null;
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
				appendText(new ChatLine("(" + getDateTime() + ") "
						+ trimUserID(id) + " left", null));
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

	public void handleInvitationReceived(ID roomID, ID from, String subject,
			String body) {
		System.out.println("invitation room=" + roomID + ",from=" + from
				+ ",subject=" + subject + ",body=" + body);
	}

	protected void appendText(ChatLine text) {
		StyledText st = readText.getTextWidget();

		if (text == null || readText == null || st == null)
			return;

		int startRange = st.getText().length();
		StringBuffer sb = new StringBuffer();

		if (text.getOriginator() != null) {
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

			if (localUser != null
					&& localUser.getID().equals(text.getOriginator().getID())) {
				sr.foreground = meColor;
			} else {
				sr.foreground = otherColor;
			}
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

	public void handleJoin(IUser user) {
		if (disposed)
			return;
		otherUsers.add(user.getID());
	}

	public void handleLeave(IUser user) {
		if (disposed)
			return;
		otherUsers.remove(user.getID());
	}

	public void handleUpdated(IUser user) {
		// XXX todo
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

}