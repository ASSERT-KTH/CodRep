public IUser getLocalUser() {

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

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.presence.IIMMessageEvent;
import org.eclipse.ecf.presence.IIMMessageListener;
import org.eclipse.ecf.presence.im.IChatMessage;
import org.eclipse.ecf.presence.im.IChatMessageEvent;
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.jface.window.ApplicationWindow;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.ShellAdapter;
import org.eclipse.swt.events.ShellEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.PaletteData;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.progress.UIJob;

public class ChatWindow extends ApplicationWindow implements IIMMessageListener {

	private static final long FLASH_INTERVAL = 600;

	private String initText;

	private TextChatComposite chat;

	private Image image;

	private Image blank;

	private String titleBarText;

	protected ViewPart view;

	protected IUser localUser;

	protected IUser remoteUser;

	protected boolean disposed = false;

	protected IUser getLocalUser() {
		return localUser;
	}

	protected IUser getRemoteUser() {
		return remoteUser;
	}

	private UIJob flasher;

	public ChatWindow(ViewPart view, String titleBarText,
			String initOutputText, IUser localUser, IUser remoteUser) {
		super(null);
		this.view = view;
		this.titleBarText = titleBarText;
		this.initText = initOutputText;
		this.localUser = localUser;
		this.remoteUser = remoteUser;
		addStatusLine();
	}

	public void setStatus(final String status) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				ChatWindow.super.setStatus(status);
			}
		});
	}

	protected String getShellName() {
		return chat.getShellName();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.jface.window.Window#configureShell(org.eclipse.swt.widgets.Shell)
	 */
	protected void configureShell(final Shell newShell) {
		super.configureShell(newShell);
		String shellTitlePrefix = MessageLoader
				.getString("ChatWindow.titleprefix");
		if (shellTitlePrefix != null && !shellTitlePrefix.equals("")) {
			shellTitlePrefix = shellTitlePrefix + ": ";
		}
		titleBarText = shellTitlePrefix + titleBarText;
		newShell.setText(titleBarText);
		image = SharedImages.getImage(SharedImages.IMG_USER_AVAILABLE);
		newShell.setImage(image);
		RGB[] colors = new RGB[2];
		colors[0] = new RGB(0, 0, 0);
		colors[1] = new RGB(255, 255, 255);
		ImageData data = new ImageData(16, 16, 1, new PaletteData(colors));
		data.transparentPixel = 0;
		blank = new Image(newShell.getDisplay(), data);

		flasher = new UIJob("Chat View Icon Flasher") {

			public IStatus runInUIThread(IProgressMonitor monitor) {
				Shell shell = getShell();
				if (shell.getImage() == image)
					shell.setImage(blank);
				else
					shell.setImage(image);

				schedule(FLASH_INTERVAL);
				return Status.OK_STATUS;
			}

			public boolean shouldRun() {
				return !getShell().isDisposed();
			}
		};

		flasher.setSystem(true);

		newShell.addDisposeListener(new DisposeListener() {
			public void widgetDisposed(DisposeEvent e) {
				flasher.cancel();
				if (image != null)
					image.dispose();

				if (blank != null)
					blank.dispose();
			}
		});

		newShell.addShellListener(new ShellAdapter() {
			public void shellActivated(ShellEvent e) {
				stopFlashing();
				if (!chat.isDisposed())
					chat.textinput.setFocus();
			}
		});
	}

	protected Point getInitialSize() {
		return new Point(320, 240);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.jface.window.Window#createContents(org.eclipse.swt.widgets.Composite)
	 */
	protected Control createContents(Composite parent) {
		if (view == null)
			throw new NullPointerException("view cannot be null");
		// Get ILocalInputHandler from view
		ILocalInputHandler inputHandler = null;
		Object obj = view.getAdapter(ILocalInputHandler.class);
		if (obj == null)
			throw new NullPointerException("view " + view
					+ " did not provide ILocalInputHandler adapter");
		else if (obj instanceof ILocalInputHandler) {
			inputHandler = (ILocalInputHandler) obj;
		}
		chat = new TextChatComposite(parent, SWT.NORMAL, initText,
				inputHandler, getLocalUser(), getRemoteUser());
		chat.setLayoutData(new GridData(GridData.FILL_BOTH));
		chat.setFont(parent.getFont());
		return chat;
	}

	public void setLocalUser(IUser localUser) {
		this.localUser = localUser;
		chat.setLocalUser(localUser);
	}

	public void setRemoteUser(IUser remoteUser) {
		this.remoteUser = remoteUser;
		chat.setRemoteUser(remoteUser);
	}

	protected TextChatComposite getTextChatComposite() {
		return chat;
	}

	private boolean hasFocus = false;

	private int openResult = 0;

	public int open() {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				openResult = ChatWindow.super.open();
			}
		});
		return openResult;
	}

	public void create() {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				ChatWindow.super.create();
			}
		});
	}

	public boolean hasFocus() {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				if (getShell().isDisposed())
					hasFocus = false;
				else
					hasFocus = hasFocus(getShell());
			}
		});
		return hasFocus;
	}

	private boolean hasFocus(Composite composite) {
		if (composite.isFocusControl())
			return true;
		else {
			Control[] children = composite.getChildren();
			for (int i = 0; i < children.length; ++i)
				if (children[i] instanceof Composite
						&& hasFocus((Composite) children[i]))
					return true;
				else if (children[i].isFocusControl())
					return true;
		}

		return false;
	}

	public void flash() {
		flasher.schedule();
	}

	private void stopFlashing() {
		flasher.cancel();
		if (getShell().getImage() != image)
			getShell().setImage(image);
	}

	public void setDisposed(final String message) {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				disposed = true;
				if (chat != null) {
					chat.setDisposed();
				}
				if (!getShell().isDisposed()) {
					getShell().setText(getShell().getText() + " (inactive)");
				}
				setStatus(message);
			}
		});
	}

	public void openAndFlash() {
		Display.getDefault().syncExec(new Runnable() {
			public void run() {
				flash();
				if (!getShell().isVisible()) {
					open();
				}
			}
		});
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.jface.window.Window#handleShellCloseEvent()
	 */
	protected void handleShellCloseEvent() {
		if (!getShell().isDisposed()) {
			if (disposed) {
				chat.dispose();
				chat = null;
				getShell().dispose();
			} else {
				getShell().setVisible(false);
			}
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.presence.IIMMessageListener#handleMessageEvent(org.eclipse.ecf.presence.IIMMessageEvent)
	 */
	public void handleMessageEvent(IIMMessageEvent messageEvent) {
		if (messageEvent instanceof IChatMessageEvent) {
			final IChatMessage m = ((IChatMessageEvent) messageEvent).getChatMessage();
			Display.getDefault().syncExec(new Runnable() {
				public void run() {
					if (!disposed && chat != null) {
						chat.appendText(new ChatLine(m.getBody(), getRemoteUser()));
					}
				}
			});
		}
		
	}
}
 No newline at end of file