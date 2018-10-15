if (disposed) {

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

import org.eclipse.core.runtime.Path;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.ui.UiPlugin;
import org.eclipse.ecf.ui.messaging.IMessageViewer;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.window.ApplicationWindow;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.ShellAdapter;
import org.eclipse.swt.events.ShellEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.PaletteData;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.part.ViewPart;

/**
 * @author pnehrer
 * 
 */
public class ChatWindow extends ApplicationWindow implements IMessageViewer {
	
	protected static final String ICONS_PERSON_GIF = "icons/person.gif";
    private static final long FLASH_INTERVAL = 600;

	private String initText;
	private TextChatComposite chat;
	private Image image;
	private Image blank;
	private boolean flashing;
    
    private String titleBarText;
    
    protected ViewPart view;
    protected IUser localUser;
    protected IUser remoteUser;
    
    protected boolean disposed = false;
    protected Thread flashThread = null;
    
    protected IUser getLocalUser() {
        return localUser;
    }
    
    protected IUser getRemoteUser() {
        return remoteUser;
    }
	private final Runnable flipImage = new Runnable() {
		public void run() {
			Shell shell = getShell();
			if (!shell.isDisposed()) 
				if (blank == shell.getImage()) {
					if (image != null && !image.isDisposed())
						shell.setImage(image);
				} else {
					if (blank != null && !blank.isDisposed())
						shell.setImage(blank);
				}
		}
	};

	private final Runnable showImageRunnable = new Runnable() {
		public void run() {
			Shell shell = getShell();
			if (!shell.isDisposed() && image != null && !image.isDisposed())
				shell.setImage(image);
		}
	};

	private Flash flash;

	private class Flash implements Runnable  {
		
		private final Display display;
		
		public Flash(Display display) {
			this.display = display;
		}
		
		public void run() {
			while (true) {
				synchronized (this) {
					try {
						while (!flashing)
							wait();
					} catch (InterruptedException e) {
						break;
					}
				}
				
				if (display.isDisposed())
					break;

				display.syncExec(flipImage);
				synchronized (this) {
					try {
						wait(FLASH_INTERVAL);
					} catch (InterruptedException e) {
						break;
					}
				}
			}
		}
	};

	public ChatWindow(ViewPart view, String titleBarText, String initOutputText, IUser localUser, IUser remoteUser) {
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
        String shellTitlePrefix = MessageLoader.getString("ChatWindow.titleprefix");
        if (shellTitlePrefix != null && !shellTitlePrefix.equals("")) {
            shellTitlePrefix = shellTitlePrefix + ": ";
        }
        titleBarText = shellTitlePrefix + titleBarText;
        newShell.setText(titleBarText);
		image = ImageDescriptor.createFromURL(
				UiPlugin.getDefault().find(new Path(ICONS_PERSON_GIF)))
				.createImage();
		newShell.setImage(image);
		RGB[] colors = new RGB[2];
		colors[0] = new RGB(0, 0, 0);
		colors[1] = new RGB(255, 255, 255);
		ImageData data = new ImageData(16, 16, 1, new PaletteData(colors));
		data.transparentPixel = 0;
		blank = new Image(newShell.getDisplay(), data);

		flash = new Flash(newShell.getDisplay());
        flashThread = new Thread(flash);
        flashThread.start();
		
		newShell.addDisposeListener(new DisposeListener() {
			public void widgetDisposed(DisposeEvent e) {
				flash();
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

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.jface.window.Window#createContents(org.eclipse.swt.widgets.Composite)
	 */
	protected Control createContents(Composite parent) {
        if (view == null) throw new NullPointerException("view cannot be null");
        // Get ITextInputHandler from view
        ITextInputHandler inputHandler = null;
        Object obj = view.getAdapter(ITextInputHandler.class);
        if (obj == null) {
            throw new NullPointerException("view "+view+" did not provide ITextInputHandler adapter");
        } else if (obj instanceof ITextInputHandler) {
            inputHandler = (ITextInputHandler) obj;
        }
		chat = new TextChatComposite(parent, SWT.NORMAL, initText, inputHandler,getLocalUser(),getRemoteUser());
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
        boolean result = false;
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
		synchronized (flash) {
			if (!flashing) {
				flashing = true;
				flash.notify();
			}
		}
	}

	private void stopFlashing() {
		synchronized (flash) {
			if (flashing) {
				flashing = false;
				if (!getShell().isDisposed() && image != null && !image.isDisposed())
					getShell().setImage(image);
                flash.notify();
			}
		}
	}

    public void setDisposed(final String message) {
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                disposed = true;
                if (flashThread != null) {
                    flashThread.interrupt();
                    flashThread = null;
                }
                if (chat != null) {
                    chat.setDisposed();
                }
                if (!getShell().isDisposed()) {
                    getShell().setText(getShell().getText()+" (inactive)");
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
            if (!disposed) {
                chat.dispose();
                chat = null;
                getShell().dispose();
            } else {
                getShell().setVisible(false);
            }
        }
	}

    /* (non-Javadoc)
     * @see org.eclipse.ecf.ui.messaging.IMessageViewer#showMessage(org.eclipse.ecf.core.identity.ID, org.eclipse.ecf.core.identity.ID, org.eclipse.ecf.ui.messaging.IMessageViewer.Type, java.lang.String, java.lang.String)
     */
    public void showMessage(final ID fromID, ID toID, Type type, String subject, final String message) {
        Display.getDefault().syncExec(new Runnable() {
            public void run() {
                if (!disposed && chat != null) {
                    chat.appendText(new ChatLine(message,getRemoteUser()));
                }
            }            
        });
    }
}
 No newline at end of file