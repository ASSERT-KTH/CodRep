e.remove();

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

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Vector;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.share.EclipseMessage;
import org.eclipse.ecf.example.collab.share.TreeItem;
import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.ecf.example.collab.share.url.ExecProg;
import org.eclipse.ecf.example.collab.share.url.ExecURL;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.part.ViewPart;

public class LineChatClientView implements FileSenderUI {
	/*
	 * public static final String[] APPSHAREARGTYPES = { ID.class.getName(),
	 * VNCParams.class.getName() }; public static final String APPSHARECLASSNAME =
	 * EclipseAppShareServer.class .getName();
	 */
	public static final String CLIENT_PREFIX = " says";
	protected static final String DEFAULT_ECLIPSE_COMPONENT_CLASS = org.eclipse.ecf.example.collab.share.TestEclipseSessionComponent.class
			.getName();
	public static final String DEFAULT_UNIX_BROWSER = "mozilla";
	public static final String ENTER_STRING = "ARRIVED";
	public static final String EXECPROGARGTYPES[] = { ID.class.getName(),
			"[Ljava.lang.String;", "[Ljava.lang.String;",
			Boolean.class.getName(), Boolean.class.getName() };
	public static final String EXECPROGCLASSNAME = ExecProg.class.getName();
	public static final String HOST_PREFIX = "You say";
	public static final String LEFT_STRING = "LEFT";
	public static final String MESSAGECLASSNAME = EclipseMessage.class
			.getName();
	public static final String REMOTEFILEPATH = null;
	public static final String SHOWURLARGTYPES[] = { ID.class.getName(),
			"java.lang.String" };
	public static final String SHOWURLCLASSNAME = ExecURL.class.getName();
	protected static final int TREE_EXPANSION_LEVELS = 1;
	public static final String TREE_HEADER = "Participants";
	private boolean showTimestamp = ClientPlugin.getDefault().getPreferenceStore().getBoolean(ClientPlugin.PREF_DISPLAY_TIMESTAMP);
	SimpleDateFormat df = new SimpleDateFormat("MM/dd hh:mm a");
	String downloaddir;
	LineChatHandler lch;
	Hashtable myNames = new Hashtable();
	String name;
	Vector proxyObjects = new Vector();
	TeamChat teamChat;
	User userdata;
	LineChatView view;
	protected ID appShareID = null;

	protected ID getAppShareID() {
		return appShareID;
	}

	protected void setAppShareID(ID val) {
		appShareID = val;
	}

	public LineChatClientView(LineChatHandler lch, LineChatView view,
			String name, String initText, String downloaddir) {
		super();
		this.lch = lch;
		this.view = view;
		this.name = name;
		this.teamChat = new TeamChat(this, view.tabFolder, SWT.NULL, initText);
		this.userdata = lch.getUser();
		this.downloaddir = downloaddir;
		if (userdata != null)
			addUser(userdata);
		
		ClientPlugin.getDefault().getPreferenceStore().addPropertyChangeListener(new IPropertyChangeListener() {

			public void propertyChange(PropertyChangeEvent event) {
				if (event.getProperty().equals(ClientPlugin.PREF_DISPLAY_TIMESTAMP)) {
					showTimestamp = ((Boolean)event.getNewValue()).booleanValue();
				}	
			}
			
		});
	}

	public ViewPart getView() {
		return view;
	}

	public Control getTextControl() {
		return teamChat.getTextControl();
	}

	public Control getTreeControl() {
		return teamChat.getTreeControl();
	}

	public boolean addUser(User ud) {
		if (ud == null)
			return false;
		ID userID = ud.getUserID();
		String username = ud.getNickname();
		if (myNames.containsKey(userID)) {
			String existingName = (String) myNames.get(userID);
			if (!existingName.equals(username)) {
				myNames.put(userID, username);
				final String str = existingName + " changed name to "
						+ username;
				showText(new ChatLine(str));
			}
			return false;
		} else {
			myNames.put(userID, username);
			final String str = makeChatLine(username + " " + ENTER_STRING);
			addUserToTree(ud);
			showText(new ChatLine(str));
			return true;
		}
	}

	/**
	 * This method is used to create an output string for the chat window.
	 * Any user-defined preferences regarding output shall be handled here.
	 * @param line Input text
	 * @return User-defined output of chat text.
	 */
	private String makeChatLine(String line) {
		if (showTimestamp) {
			return dateTime() + line;
		}
		
		return line;
	}

	protected void addUserToTree(User ud) {
		if (ud == null)
			return;
		TreeParent root = getPresenceRoot();
		if (root == null)
			return;
		TreeUser top = makeUserNode(ud);
		if (top == null)
			return;
		root.addChild(top);
		refreshTreeView();
	}

	protected void appendAndScrollToBottom(final ChatLine str) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (teamChat != null)
					teamChat.appendText(str);
			}
		});
	}

	public boolean changeUser(User user) {
		return changeUserInTree(user);
	}

	protected boolean changeUserInTree(User userdata) {
		if (userdata == null)
			return false;
		// First, find node for user
		TreeParent top = getPresenceRoot();
		for (Iterator childs = top.children().iterator(); childs.hasNext();) {
			TreeUser child = (TreeUser) childs.next();
			User ud = (User) child.getUser();
			if (ud.getUserID().equals(userdata.getUserID())) {
				// We've found it...so remove existing data
				top.removeChild(child);
				addUserToTree(userdata);
				return true;
			}
		}
		return false;
	}

	protected void closeClient() {
		if (lch != null) {
			lch.chatGUIDestroy();
		}
	}

	protected String dateTime() {
		StringBuffer sb = new StringBuffer("[");
		sb.append(df.format(new Date())).append("] ");
		return sb.toString();
	}

	public void disposeClient() {
		myNames.clear();
		if (teamChat != null) {
            final ChatWindow chatWindow = teamChat.chatWindow; 
			if (chatWindow != null && !Display.getDefault().isDisposed()) {
                Display.getDefault().syncExec(new Runnable() {
                    public void run() {
						if (chatWindow != null)
							chatWindow.close();
                    }
                });
            }

			teamChat = null;
		}
		if (lch != null) {
			lch = null;
		}
        view.disposeClient(this);
	}

	protected void expandAll() {
		if (teamChat != null) {
			teamChat.getTree().expandToLevel(TREE_EXPANSION_LEVELS);
		}
	}

	protected String getPrefix(ID objID) {
		String prefix = "";
		if (userdata.getUserID().equals(objID)) {
			prefix += makeChatLine(" " + HOST_PREFIX + ":  ");
		} else {
			String tmp = getUserData(objID);
			if (tmp == null) {
				tmp = objID.toString();
			}
			prefix += makeChatLine(" " + tmp + CLIENT_PREFIX + ":  ");
		}
		return prefix;
	}

	protected TreeParent getPresenceRoot() {
		if (teamChat == null)
			return null;
		ViewContentProvider vcp = (ViewContentProvider) teamChat.getTree()
				.getContentProvider();
		if (vcp == null)
			return null;
		else
			return vcp.getPresenceRoot();
	}

	protected String getPrivatePrefix(ID objID) {
		String prefix = "";
		if (userdata.getUserID().equals(objID)) {
			prefix += makeChatLine(" " + HOST_PREFIX + " (private):  ");
		} else {
			String tmp = getUserData(objID);
			if (tmp == null) {
				tmp = objID.toString();
			}
			prefix += makeChatLine(" " + tmp + CLIENT_PREFIX + " (private):  ");
		}
		return prefix;
	}

	protected TeamChat getTeamChat() {
		return teamChat;
	}

	protected String getUserData(ID id) {
		return (String) myNames.get(id);
	}

	public User getUser(ID id) {
		if (id == null)
			return null;
		TreeParent top = getPresenceRoot();
		for (Iterator e = top.children().iterator(); e.hasNext();) {
			TreeUser tn = (TreeUser) e.next();
			User ud = (User) tn.getUser();
			if (id.equals(ud.getUserID())) {
				return ud;
			}
		}
		return null;
	}

	protected void handleTextInput(String text) {
		if (showTimestamp) {
			text = dateTime() + text;
		}
		
		ChatLine line = new ChatLine(text);
		
		if (lch != null) {
			line.setOriginator(userdata);
		}
		appendAndScrollToBottom(line);
		teamChat.clearInput();
		
		if (lch != null)
			lch.inputText(text);
	}

	protected void makeObject(ID target, String className, String[] args) {
		makeObject(target, className, null, args);
	}

	protected void makeObject(ID target, final String className,
			String[] argTypes, Object[] args) {
		if (lch != null) {
			HashMap map = new HashMap();
			map.put("args", args);
			map.put("types", argTypes);
			try {
				lch.makeObject(target, className, map);
			} catch (final Exception e) {
				Display.getDefault().asyncExec(new Runnable() {
					public void run() {
						MessageDialog.openInformation(null,
								"Make Object Exception",
								"Exception creating instance of '" + className
										+ "'. \nException: " + e);
					}
				});
				e.printStackTrace();
				lch.chatException(e, "makeObject(" + className + ")");
			}
		}
	}

	protected void makeProxyObject(ID target, final String className) {
		if (lch != null) {
			try {
				// With this interface, we'll simply supply the class name
				// as the instance name. Eventually, the user interface should
				// allow the creation of some other instance name
				lch.makeProxyObject(target, className, className);
				proxyObjects.add(className);
				teamChat.enableProxyMessage(true);
			} catch (final Exception e) {
				Display.getDefault().asyncExec(new Runnable() {
					public void run() {
						MessageDialog.openInformation(null,
								"Make Proxy Object Exception",
								"Exception creating instance of '" + className
										+ "'. \nException: " + e);
					}
				});
				e.printStackTrace();
				lch.chatException(e, "makeProxyObject(" + className + ")");
			}
		}
	}

	protected TreeParent makeUserNode(TreeParent node, Vector ht) {
		if (node == null || ht == null)
			return null;
		for (Enumeration e = ht.elements(); e.hasMoreElements();) {
			TreeItem ti = (TreeItem) e.nextElement();
			Object val = ti.getValue();
			final TreeParent tn = new TreeParent(this, ti);
			if (val instanceof Vector) {
				// Create new tree node
				makeUserNode(tn, (Vector) val);
			}
			node.addChild(tn);
		}
		refreshTreeView();
		return node;
	}

	protected TreeUser makeUserNode(User ud) {
		if (ud == null)
			return null;
		TreeUser tu = new TreeUser(this, ud);
		return (TreeUser) makeUserNode(tu, ud.getUserFields());
	}

	protected void messageProxyObject(ID target, String classname, String meth,
			Object[] args) {
		if (lch != null) {
			lch.messageProxyObject(target, classname, meth, args);
		}
	}

	protected void refreshTreeView() {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (teamChat != null) {
					try {
						// teamChat.getTree().refresh(getPresenceRoot(), true);
						teamChat.getTree().refresh();
						expandAll();
					} catch (Exception e) {
					}
				}
			}
		});
	}

	protected void removeProxyObject(ID target, final String className) {
		if (lch != null) {
			try {
				// With this interface, we'll simply supply the class name
				// as the instance name. Eventually, the user interface should
				// allow the creation of some other instance name
				lch.removeProxyObject(target, className);
				proxyObjects.remove(className);
				teamChat.enableProxyMessage(proxyObjects.size() > 0);
			} catch (final Exception e) {
				Display.getDefault().asyncExec(new Runnable() {
					public void run() {
						MessageDialog.openInformation(null,
								"Remove Proxy Object Exception",
								"Exception creating instance of '" + className
										+ "'. \nException: " + e);
					}
				});
				e.printStackTrace();
				lch.chatException(e, "removeProxyObject(" + className + ")");
			}
		}
	}

	public void removeUser(ID id) {
		String name = getUserData(id);
		if (name != null) {
			final String str = makeChatLine(name + " " + LEFT_STRING);
			showText(new ChatLine(str));
		}
		myNames.remove(id);
		removeUserFromTree(id);
	}

	protected void removeUserFromTree(ID id) {
		if (id == null)
			return;
		TreeParent top = getPresenceRoot();
		if (top != null) {
			for (Iterator e = top.children().iterator(); e.hasNext();) {
				TreeUser tn = (TreeUser) e.next();
				User ud = (User) tn.getUser();
				if (id.equals(ud.getUserID())) {
					top.removeChild(tn);
					refreshTreeView();
				}
			}
		}
	}

	protected void runProgram(ID receiver, String program, String[] env) {
		String[] cmds = { program };
		Object[] args = { receiver, cmds, env, new Boolean(receiver == null),
				new Boolean(false) };
		// Do it
		makeObject(null, EXECPROGCLASSNAME, EXECPROGARGTYPES, args);
	}

	public void sendData(File aFile, long dataLength) {
	}

	public void sendDone(File aFile, Exception e) {
		if (e != null) {
			showText(new ChatLine("Exception '" + e.getMessage() + "' sending file '"
					+ aFile.getName()));
		} else {
			showText(new ChatLine("\tSend of '" + aFile.getName() + "' completed"));
			if (lch != null)
				lch.refreshProject();
		}
	}

	public void sendStart(File aFile, long length, float rate) {
		// present user with notification that file is being transferred
		showText(new ChatLine("\tSending '" + aFile.getName() + "'"));
	}

	public void setTitle(String title) {
		// NOTHING HAPPENS
	}

	public void setVisible(boolean visible) {
		// NOTHING HAPPENS
		// teamChat.setVisible(visible);
	}

	public void showLine(ChatLine line) {
		appendAndScrollToBottom(line);
	}


	public void startedTyping(final User user) {
		Display.getDefault().asyncExec(new Runnable() {
			public void run() {
				if (teamChat != null)
					teamChat.setStatus(user.getNickname() + " is typing...");
			}
		});
	}

	protected void showText(final ChatLine line) {
		appendAndScrollToBottom(line);
	}

	public void toFront() {
		view.setActiveTab(name);
	}

	protected TreeParent updateSubtree(TreeParent root, TreeItem item) {
		root.removeAllChildren();
		TreeParent newRoot = new TreeParent(this, item);
		Object val = item.getValue();
		if (val instanceof Vector) {
			return makeUserNode(newRoot, (Vector) val);
		} else
			return newRoot;
	}

	public boolean updateTreeDisplay(ID user, TreeItem item) {
		if (user == null || item == null)
			return false;
		TreeParent root = getPresenceRoot();
		for (Iterator childs = root.children().iterator(); childs.hasNext();) {
			TreeUser ut = (TreeUser) childs.next();
			User a = ut.getUser();
			if (a != null && (user.equals(a.getUserID()))) {
				// Found user...now find tree item
				updateUserTree(ut, item);
				refreshTreeView();
				return true;
			}
		}
		return false;
	}

	protected boolean updateUserTree(TreeParent userNode, TreeItem item) {
		if (userNode == null || item == null)
			return false;
		int i = 0;
		for (Iterator e = userNode.children().iterator(); e.hasNext(); i++) {
			TreeParent child = (TreeParent) e.next();
			TreeItem existing = child.getTreeItem();
			if (item.equals(existing)) {
				TreeParent newChild = updateSubtree(child, item);
				userNode.removeChild(child);
				userNode.addChild(newChild);
				return true;
			} else {
				Object val = existing.getValue();
				if (val instanceof Vector) {
					Vector v = (Vector) val;
					for (Enumeration ev = v.elements(); ev.hasMoreElements();) {
						TreeItem ti = (TreeItem) ev.nextElement();
						updateUserTree(child, ti);
					}
				}
			}
		}
		return false;
	}
}
 No newline at end of file