return Status.OK_STATUS;

/****************************************************************************
* Copyright (c) 2004, 2007 Composent, Inc. and others.
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
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.StringTokenizer;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.Preferences.PropertyChangeEvent;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.share.User;
import org.eclipse.ecf.example.collab.share.io.FileTransferParams;
import org.eclipse.ecf.ui.views.SimpleLinkTextViewer;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.preference.IPreferenceStore;
import org.eclipse.jface.resource.FontRegistry;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.viewers.ITreeContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerFilter;
import org.eclipse.jface.viewers.ViewerSorter;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseListener;
import org.eclipse.swt.events.MouseMoveListener;
import org.eclipse.swt.events.PaintEvent;
import org.eclipse.swt.events.PaintListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.ElementTreeSelectionDialog;
import org.eclipse.ui.dialogs.ISelectionStatusValidator;
import org.eclipse.ui.progress.UIJob;
import org.eclipse.ui.views.IViewCategory;
import org.eclipse.ui.views.IViewDescriptor;
import org.eclipse.ui.views.IViewRegistry;



public class ChatComposite extends Composite {
	private static final String CHAT_OUTPUT_FONT = "ChatFont";
	private final LineChatClientView view;
	private Color meColor = null;
	private Color otherColor = null;
	private Color systemColor = null;

	Action appShare = null;

	ChatLayout cl = null;
	Action coBrowseURL = null;
	Action messageEclipseComponent = null;
	Action outputClear = null;
	Action outputCopy = null;
	Action outputPaste = null;
	Action outputSelectAll = null;
	Action removeEclipseComponent = null;
	Action sendComponent = null;
	Action sendComponentToServer = null;
	Action sendEclipseComponent = null;
	Action sendFileToGroup = null;
	Action sendFileToGroupAndLaunch = null;
	Action sendMessage = null;
	Action startProgram = null;
	Action closeGroup = null;
	Action sendCVSUpdateRequest = null;
	
	Action sendShowViewRequest = null;
	
	Action showChatWindow;

	protected final String TEXT_INPUT_INIT = MessageLoader
			.getString("LineChatClientView.textinputinit");
    protected static final int DEFAULT_INPUT_HEIGHT = 25;
    protected static final int DEFAULT_INPUT_SEPARATOR = 5;

	Text textinput = null;
	SimpleLinkTextViewer textoutput = null;
	ChatTreeViewer treeView = null;
	ChatDropTarget chatDropTarget = null;
	TreeDropTarget treeDropTarget = null;
	
	ChatWindow chatWindow;
	boolean typing;

	ChatComposite(LineChatClientView view, Composite parent, ChatTreeViewer tree, int options,
			String initText) {
		this(view, parent, tree, options, initText, null);
	}
	
	ChatComposite(LineChatClientView view, Composite parent, ChatTreeViewer tree, int options,
			String initText, ChatWindow chatWindow) {
		super(parent, options);
		this.view = view;
		this.chatWindow = chatWindow;
		
		meColor = colorFromRGBString(ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_ME_TEXT_COLOR));
		otherColor = colorFromRGBString(ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_OTHER_TEXT_COLOR));
		systemColor = colorFromRGBString(ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_SYSTEM_TEXT_COLOR));
		ClientPlugin.getDefault().getPluginPreferences().addPropertyChangeListener(new ColorPropertyChangeListener());
		
		this.addDisposeListener(new DisposeListener() {

			public void widgetDisposed(DisposeEvent e) {
				if (meColor != null) {
					meColor.dispose();
				}
				
				if (otherColor != null) {
					otherColor.dispose();
				}
				
				if (systemColor != null) {
					systemColor.dispose();
				}
			}
			
		});
		
		cl = new ChatLayout(DEFAULT_INPUT_HEIGHT, DEFAULT_INPUT_SEPARATOR);
		setLayout(cl);
		treeView = tree;
		textoutput = new SimpleLinkTextViewer(this, SWT.V_SCROLL | SWT.H_SCROLL
				| SWT.WRAP | SWT.BORDER | SWT.READ_ONLY);
		String fontName = ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_CHAT_FONT);
		if (!(fontName == null) && !(fontName.equals(""))) {
			FontRegistry fr = ClientPlugin.getDefault().getFontRegistry();
			FontData []newFont = {new FontData(fontName)};
			
			fr.put(CHAT_OUTPUT_FONT, newFont);
			textoutput.getTextWidget().setFont(fr.get(CHAT_OUTPUT_FONT));
		}
		
		ClientPlugin.getDefault().getPluginPreferences().addPropertyChangeListener(new FontPropertyChangeListener());
		
		textoutput.append(initText);
		
		textinput = new Text(this, SWT.SINGLE | SWT.BORDER);
		cl.setInputTextHeight(textinput.getFont().getFontData()[0]
				.getHeight() + 2);
		textinput.setText(TEXT_INPUT_INIT);
		
		textinput.selectAll();
		textinput.addKeyListener(new KeyListener() {
			public void keyPressed(KeyEvent evt) {
				handleKeyPressed(evt);
			}

			public void keyReleased(KeyEvent evt) {
				handleKeyReleased(evt);
			}
		});
		textinput.addFocusListener(new FocusListener() {
			public void focusGained(FocusEvent e) {
				String t = textinput.getText();
				if (t.equals(TEXT_INPUT_INIT)) {
					textinput.selectAll();
				}
			}

			public void focusLost(FocusEvent e) {
			}
		});
		textinput.addMouseListener(new MouseListener() {
			public void mouseDoubleClick(MouseEvent e) {
			}

			public void mouseDown(MouseEvent e) {
			}

			public void mouseUp(MouseEvent e) {
				String t = textinput.getText();
				if (t.equals(TEXT_INPUT_INIT)) {
					textinput.selectAll();
				}
			}
		});
		textinput.addModifyListener(new ModifyListener() {
			public void modifyText(ModifyEvent e) {				
				if (typing && textinput.getText().trim().length() == 0)
					typing = false;
				else if (!typing) {
					typing = true;
					ChatComposite.this.view.lch.sendStartedTyping();
				}
			}
		});
		// make actions
		makeActions();
		hookContextMenu();
		contributeToActionBars();
		initializeDropTargets();
	}

	ChatComposite(LineChatClientView view, Composite parent, ChatTreeViewer tree, String initText) {
		this(view, parent, tree, SWT.NULL, initText);
	}

	public void appendText(ChatLine text) {
		StyledText st = textoutput.getTextWidget();
		
		
		if (text == null || textoutput == null || st == null || st.isDisposed())
			return;

//		int startRange = st.getText().length();
		StringBuffer sb = new StringBuffer();
		
		if (text.getOriginator() != null) {
			sb.append(text.getOriginator().getNickname() + ": ");
//			StyleRange sr = new StyleRange();
//			sr.start = startRange;
//			sr.length = sb.length();
//			if (view.userdata.getUserID().equals(text.getOriginator().getUserID())) { 
//				sr.foreground = meColor;
//			} else {
//				sr.foreground = otherColor;
//			}
//			st.append(sb.toString());
//			st.setStyleRange(sr);

			textoutput.append(sb.toString());
		}
		
//		int beforeMessageIndex = st.getText().length();
		
		if(text.getOnClick()==null)
			textoutput.append(text.getText());
		else
			textoutput.appendLink(text.getText(), text.getOnClick());
		
//		if (text.getOriginator() == null) {
//			StyleRange sr = new StyleRange();
//			sr.start = beforeMessageIndex;
//			sr.length = text.getText().length();
//			sr.foreground = systemColor;
//			st.setStyleRange(sr);
//		}
		
		if (!text.isNoCRLF()) {
			textoutput.append("\n");
		}

		// scroll to end
		String t = st.getText();
		if (t == null)
			return;
		st.setSelection(t.length());
	}

	protected void clearInput() {
		textinput.setText("");
	}

	private void contributeToActionBars() {
		IActionBars bars = this.view.view.getViewSite().getActionBars();
		fillLocalPullDown(bars.getMenuManager());
		//fillLocalToolBar(bars.getToolBarManager());
		//bars.getToolBarManager().markDirty();
		
	}

	protected void copyFileLocally(String inputFile, String outputFile)
			throws IOException {
		File aFile = new java.io.File(outputFile);
		File dir = aFile.getParentFile();
		dir.mkdirs();
		java.io.BufferedInputStream ins = new java.io.BufferedInputStream(
				new java.io.FileInputStream(inputFile));
		byte[] buf = new byte[1024];
		java.io.BufferedOutputStream bos = new java.io.BufferedOutputStream(
				new java.io.FileOutputStream(aFile));
		// Actually copy file
		while (ins.read(buf) != -1)
			bos.write(buf);
		// Close input and output streams
		ins.close();
		bos.close();
	}

	protected void enableProxyMessage(boolean val) {
		messageEclipseComponent.setEnabled(val);
		removeEclipseComponent.setEnabled(val);
	}

	private void fillContextMenu(IMenuManager manager) {
		if (chatWindow != null) {
			manager.add(showChatWindow);
			manager.add(new Separator());
		}
		
		manager.add(outputCopy);
		manager.add(outputPaste);
		manager.add(outputClear);
		manager.add(new Separator());
		manager.add(outputSelectAll);
		manager.add(new Separator());
		manager.add(sendFileToGroup);
		//manager.add(sendFileToGroupAndLaunch);
		manager.add(coBrowseURL);
		//manager.add(startProgram);
		//appShare.setEnabled(!LineChatView.appShareActive());
		//manager.add(appShare);
		manager.add(new Separator());
		manager.add(sendMessage);
		manager.add(sendCVSUpdateRequest);
		manager.add(sendShowViewRequest);
		//manager.add(new Separator());
		//manager.add(sendEclipseComponent);
		//manager.add(messageEclipseComponent);
		//manager.add(removeEclipseComponent);
		/*
		 * manager.add(new Separator()); manager.add(sendComponent);
		 * manager.add(sendComponentToServer);
		 */
		manager.add(new Separator());
		manager.add(closeGroup);
		// Other plug-ins can contribute there actions here
		manager.add(new Separator("Additions"));
	}

	private void fillLocalPullDown(IMenuManager manager) {
		if (chatWindow != null) {
			manager.add(showChatWindow);
			manager.add(new Separator());
		}
		
		manager.add(outputCopy);
		manager.add(outputPaste);
		manager.add(outputClear);
		manager.add(new Separator());
		manager.add(outputSelectAll);
		manager.add(new Separator());
		manager.add(sendFileToGroup);
		manager.add(coBrowseURL);
		//manager.add(startProgram);
		manager.add(appShare);
		manager.add(new Separator());
		manager.add(sendMessage);
		manager.add(sendCVSUpdateRequest);
		manager.add(sendShowViewRequest);
		/*
		 * manager.add(new Separator()); manager.add(sendComponent);
		 * manager.add(sendComponentToServer);
		 * manager.add(sendEclipseComponent);
		 */
		manager.add(new Separator());
		manager.add(closeGroup);
	}
	/*
	private void fillLocalToolBar(IToolBarManager manager) {
		manager.add(outputCopy);
		manager.add(outputPaste);
		manager.add(outputClear);
		manager.add(new Separator());
		manager.add(outputSelectAll);
		manager.add(new Separator());
		manager.add(sendFileToGroup);
		manager.add(coBrowseURL);
		manager.add(startProgram);
		manager.add(appShare);
		manager.add(new Separator());
		manager.add(sendMessage);
		//manager.add(new Separator()); manager.add(sendComponent);
		//manager.add(sendComponentToServer);
		//manager.add(sendEclipseComponent);
		manager.add(new Separator());
		manager.add(closeGroup);
	}
	*/
	
	private void fillTreeContextMenu(IMenuManager manager) {
		User ud = treeView.getSelectionUser();
		if (ud != null) {
			fillTreeContextMenuUser(manager, ud);
		} else {
			fillContextMenu(manager);
		}
	}
	
	private class ScreenCaptureJob extends UIJob {
		
		private Color blackColor;
		
		private Color whiteColor;
		
		private boolean isDragging = false;
		
		private int downX = -1;
		
		private int downY = -1;
		
		public ScreenCaptureJob(Display display) {
			super(display, "Screen capturing...");
			blackColor = new Color(display, 0, 0, 0);
			whiteColor = new Color(display, 255, 255, 255);
		}

		public IStatus runInUIThread(IProgressMonitor monitor) {
			final Display display = getDisplay();
			GC context = new GC(display);
			final Image image = new Image(display, display.getBounds());
			context.copyArea(image, 0, 0);
			context.dispose();
		
			final Shell shell = new Shell(display, SWT.NO_TRIM);
			shell.setLayout(new FillLayout());
			shell.setBounds(display.getBounds());
			final GC gc = new GC(shell);
			shell.addPaintListener(new PaintListener() {
				public void paintControl(PaintEvent e) {
					gc.drawImage(image, 0, 0);
				}
			});
		
			shell.addMouseListener(new MouseAdapter() {
				public void mouseDown(MouseEvent e) {
					isDragging = true;
					downX = e.x;
					downY = e.y;
				}
		
				public void mouseUp(MouseEvent e) {
					isDragging = false;
					int width = Math.max(downX, e.x) - Math.min(downX, e.x);
					int height = Math.max(downY, e.y) - Math.min(downY, e.y);
					if (width != 0 && height != 0) {
						final Image copy = new Image(display, width, height);
						gc.copyArea(copy, Math.min(downX, e.x), Math.min(downY, e.y));
						shell.close();
						view.lch.sendImage(new ImageWrapper(copy.getImageData()));
						copy.dispose();
						image.dispose();
						blackColor.dispose();
						whiteColor.dispose();
					}
				}
			});
		
			shell.addMouseMoveListener(new MouseMoveListener() {
				public void mouseMove(MouseEvent e) {
					if (isDragging) {
						gc.drawImage(image, 0, 0);
						gc.setForeground(blackColor);
						gc.drawRectangle(downX, downY, e.x - downX, e.y - downY);
						gc.setForeground(whiteColor);
						gc.drawRectangle(downX - 1, downY - 1, e.x - downX + 2, e.y - downY + 2);
					}
				}
			});
		
			shell.open();
			while (!shell.isDisposed()) {
				if (!display.readAndDispatch()) {
					display.sleep();
				}
			}
			return null;
		}
	}
	
	private void sendImage() {
		final Display display = getDisplay();
		Job job = new ScreenCaptureJob(display);
		job.schedule(5000);
	}

	private void fillTreeContextMenuUser(IMenuManager man, final User user) {
		boolean toUs = false;
		if (this.view.userdata != null) {
			if (this.view.userdata.getUserID().equals(user.getUserID())) {
				// this is us...so we have a special menu
				toUs = true;
			}
		}
		if (!toUs) {
			Action sendImageToUser = new Action() {
				public void run() {
					sendImage();
				}
			};
			sendImageToUser.setText("Send Screen Capture to " + user.getNickname());
			sendImageToUser.setImageDescriptor(PlatformUI.getWorkbench()
					.getSharedImages().getImageDescriptor(
							ISharedImages.IMG_OBJ_FILE));
			man.add(sendImageToUser);
			
			Action sendFileToUser = new Action() {
				public void run() {
					sendFileToUser(user,false);
				}
			};
			sendFileToUser.setText("Send File to " + user.getNickname()
					+ "...");
			sendFileToUser.setImageDescriptor(PlatformUI.getWorkbench()
					.getSharedImages().getImageDescriptor(
							ISharedImages.IMG_OBJ_FILE));
			man.add(sendFileToUser);

			Action sendFileToUserAndLaunch = new Action() {
				public void run() {
					sendFileToUser(user,true);
				}
			};
			sendFileToUserAndLaunch.setText("Send File to " + user.getNickname()+" and launch...");
			sendFileToUserAndLaunch.setImageDescriptor(PlatformUI.getWorkbench()
					.getSharedImages().getImageDescriptor(
							ISharedImages.IMG_OBJ_FILE));
			man.add(sendFileToUserAndLaunch);

			Action coBrowseToUser = new Action() {
				public void run() {
					sendCoBrowseToUser(user);
				}
			};
			coBrowseToUser.setText("Co-Browse Web with "
					+ user.getNickname() + "...");
			man.add(coBrowseToUser);
			/*
			 * Action startProgramToUser = new Action() { public void run() {
			 * startProgram(user); } }; startProgramToUser.setText( "Start
			 * Program for " + user.getNickname() + "...");
			 * man.add(startProgramToUser);
			 */
			man.add(new Separator());

			/*
			Action startAppShareToUser = new Action() {
				public void run() {
					sendAppShare(user.getUserID());
				}
			};
			*/
			//startAppShareToUser.setText("Start Application Share with "
			//		+ user.getNickname() + "...");
			//man.add(startAppShareToUser);
			//startAppShareToUser.setEnabled(Platform.getOS().equalsIgnoreCase(Platform.OS_WIN32)&& !LineChatView.appShareActive());

			man.add(new Separator());
			Action ringUser = new Action() {
				public void run() {
					sendRingMessageToUser(user);
				}
			};
			ringUser.setText("Ring " + user.getNickname() + "...");
			man.add(ringUser);
			Action sendMessageToUser = new Action() {
				public void run() {
					sendPrivateTextMsg(user);
				}
			};
			sendMessageToUser.setText("Send Private Message to "
					+ user.getNickname() + "...");
			man.add(sendMessageToUser);
			
			/*
			Action sendCVSUpdateRequest = new Action() {
			    public void run() {
			        sendCVSUpdateRequest(user);
			    }
			};
			*/
			//sendCVSUpdateRequest.setText("Send CVS Update Request to "+user.getNickname()+"...");
			//man.add(sendCVSUpdateRequest);

			Action sendShowViewRequest = new Action() {
			    public void run() {
			        sendShowViewRequest(user);
			    }
			};
			sendShowViewRequest.setText("Send Show View Request to "+user.getNickname()+"...");
			man.add(sendShowViewRequest);
			/*
			man.add(new Separator());
			Action createProxy = new Action() {
				public void run() {
					sendEclipseComponent(user);
				}
			};
			createProxy.setText("Send EclipseProjectComponent to "
					+ user.getNickname() + "...");
			man.add(createProxy);

			Action messageProxy = new Action() {
				public void run() {
					messageEclipseComponent(user);
				}
			};
			messageProxy.setText("Message EclipseProjectComponent for "
					+ user.getNickname() + "...");
			messageProxy.setEnabled(this.view.proxyObjects.size() > 0);

			man.add(messageProxy);
			Action removeProxy = new Action() {
				public void run() {
					removeEclipseComponent(user);
				}
			};
			removeProxy.setText("Remove EclipseProjectComponent for "
					+ user.getNickname() + "...");
			removeProxy.setEnabled(this.view.proxyObjects.size() > 0);
			man.add(removeProxy);
            */
			/*
			 * man.add(new Separator());
			 * 
			 * Action createObject = new Action() { public void run() {
			 * sendRepObjectToGroup(user); } }; createObject.setText( "Send
			 * Replicated Object to " + user.getNickname() + "...");
			 * man.add(createObject);
			 */

		} else {
			// This is a menu to us
			Action sendMessageToUser = new Action() {
				public void run() {
					MessageDialog.openError(null, "Message to "
							+ user.getNickname(),
							"Talking to yourself again aren't you!!\n\n\tUsername:  "
									+ user.getNickname() + "\n\tID:  "
									+ user.getUserID().getName());
				}
			};
			sendMessageToUser.setText("Send Message to Yourself");
			man.add(sendMessageToUser);
		}
		// Other plug-ins can contribute there actions here
		man.add(new Separator("Additions"));
	}

	protected String[] getArgs(String aString) {
		StringTokenizer st = new StringTokenizer(aString);
		int argscount = st.countTokens() - 1;
		if (argscount < 1)
			return null;
		String[] newArray = new String[argscount];
		st.nextToken();
		int i = 0;
		while (st.hasMoreTokens()) {
			newArray[i++] = st.nextToken();
		}
		return newArray;
	}

	protected String getCommand(String aString) {
		StringTokenizer st = new StringTokenizer(aString);
		return st.nextToken();
	}

	private String getID(String title, String message, String initialValue) {
		InputDialog id = new InputDialog(this.view.view.getSite().getShell(), title,
				message, initialValue, null);
		id.setBlockOnOpen(true);
		int res = id.open();
		if (res == InputDialog.OK)
			return id.getValue();
		else
			return null;
	}

	protected void handleEnter() {
		if(textinput.getText().trim().length() > 0)
			this.view.handleTextInput(textinput.getText());
		
		clearInput();
		typing = false;
	}

	protected void handleKeyPressed(KeyEvent evt) {
		if (evt.character == SWT.CR) {
			handleEnter();
		} else if (evt.character == SWT.ESC && chatWindow != null) {
			chatWindow.getShell().setVisible(false);
		}
	}

	protected void handleKeyReleased(KeyEvent evt) {
	}

	private void hookContextMenu() {
		MenuManager menuMgr = new MenuManager("#PopupMenu");
		menuMgr.setRemoveAllWhenShown(true);
		menuMgr.addMenuListener(new IMenuListener() {
			public void menuAboutToShow(IMenuManager manager) {
				fillContextMenu(manager);
			}
		});
		Menu menu = menuMgr.createContextMenu(textoutput.getTextWidget());
		textoutput.getTextWidget().setMenu(menu);
		// TODO this.view.view.getSite().registerContextMenu(menuMgr, textoutput);

		MenuManager treeMenuMgr = new MenuManager("#PopupMenu");
		treeMenuMgr.setRemoveAllWhenShown(true);
		treeMenuMgr.addMenuListener(new IMenuListener() {
			public void menuAboutToShow(IMenuManager manager) {
				fillTreeContextMenu(manager);
			}
		});
		Menu treeMenu = treeMenuMgr
				.createContextMenu(treeView.getControl());
		treeView.getControl().setMenu(treeMenu);
		this.view.view.getSite().registerContextMenu(treeMenuMgr, treeView);
	}

	protected Control getTreeControl() {
		return treeView.getControl();
	}

	protected Control getTextControl() {
		return textoutput.getTextWidget();
	}

	protected void makeActions() {
		outputSelectAll = new Action() {
			public void run() {
				outputSelectAll();
			}
		};
		outputSelectAll.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.selectall"));
		outputSelectAll
				.setToolTipText(MessageLoader
						.getString("LineChatClientView.contextmenu.selectall.tooltip"));
		outputSelectAll.setAccelerator(SWT.CTRL | 'A');
		outputCopy = new Action() {
			public void run() {
				outputCopy();
			}
		};
		outputCopy.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.copy"));
		outputCopy.setToolTipText(MessageLoader
				.getString("LineChatClientView.contextmenu.copy.tooltip"));
		outputCopy.setAccelerator(SWT.CTRL | 'C');
		outputCopy.setImageDescriptor(PlatformUI.getWorkbench()
				.getSharedImages().getImageDescriptor(
						ISharedImages.IMG_TOOL_COPY));

		outputClear = new Action() {
			public void run() {
				outputClear();
			}
		};
		outputClear.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.clear"));
		outputClear.setToolTipText(MessageLoader
				.getString("LineChatClientView.contextmenu.clear.tooltip"));

		outputPaste = new Action() {
			public void run() {
				outputPaste();
			}
		};
		outputPaste.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.paste"));
		outputPaste.setToolTipText(MessageLoader
				.getString("LineChatClientView.contextmenu.paste.tooltip"));
		outputCopy.setAccelerator(SWT.CTRL | 'V');
		outputPaste.setImageDescriptor(PlatformUI.getWorkbench()
				.getSharedImages().getImageDescriptor(
						ISharedImages.IMG_TOOL_PASTE));

		sendFileToGroup = new Action() {
			public void run() {
				sendFileToGroup(false);
			}
		};
		sendFileToGroup.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.sendfile"));
		sendFileToGroup.setImageDescriptor(PlatformUI.getWorkbench()
				.getSharedImages().getImageDescriptor(
						ISharedImages.IMG_OBJ_FILE));
		/*
		sendFileToGroupAndLaunch = new Action() {
			public void run() {
				sendFileToGroup(true);
			}
		};
		sendFileToGroupAndLaunch.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.sendfileandlaunch"));
		sendFileToGroupAndLaunch.setImageDescriptor(PlatformUI.getWorkbench()
				.getSharedImages().getImageDescriptor(
						ISharedImages.IMG_OBJ_FILE));
        */
		coBrowseURL = new Action() {
			public void run() {
				sendCoBrowseToUser(null);
			}
		};
		coBrowseURL.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.cobrowse"));

		startProgram = new Action() {
			public void run() {
				startProgram(null);
			}
		};
		startProgram.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.runprogram"));

		appShare = new Action() {
			public void run() {
				sendAppShare(null);
			}
		};
		appShare.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.appshare"));
		appShare.setEnabled(Platform.getOS().equalsIgnoreCase(Platform.OS_WIN32));

		sendMessage = new Action() {
			public void run() {
				sendMessageToGroup();
			}
		};
		sendMessage.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.sendmessage"));
		sendComponent = new Action() {
			public void run() {
				sendRepObjectToGroup(null);
			}
		};
		sendComponent.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.repobject"));
		sendComponentToServer = new Action() {
			public void run() {
				sendRepObjectToServer();
			}
		};
		sendComponentToServer
				.setText(MessageLoader
						.getString("LineChatClientView.contextmenu.repobjectserver"));
		sendComponentToServer.setEnabled(false);

		sendEclipseComponent = new Action() {
			public void run() {
				sendEclipseComponent(null);
			}
		};
		sendEclipseComponent.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.send"));

		messageEclipseComponent = new Action() {
			public void run() {
				messageEclipseComponent(null);
			}
		};
		messageEclipseComponent.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.message"));
		messageEclipseComponent.setEnabled(false);
		removeEclipseComponent = new Action() {
			public void run() {
				removeEclipseComponent(null);
			}
		};
		removeEclipseComponent.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.remove"));
		removeEclipseComponent.setEnabled(false);
		// Close projectGroup
		closeGroup = new Action() {
			public void run() {
				closeProjectGroup(null);
			}
		};
		closeGroup.setText(MessageLoader
				.getString("LineChatClientView.contextmenu.leaveGroup"));
		closeGroup.setEnabled(true);
		
		sendCVSUpdateRequest = new Action() {
		    public void run() {
		        sendCVSUpdateRequest(null);
		    }
		};
		sendCVSUpdateRequest.setText(MessageLoader.getString("LineChatClientView.contextmenu.sendCVSUpdateRequest"));
		sendCVSUpdateRequest.setEnabled(this.view.lch.isCVSShared());
		
		sendShowViewRequest = new Action() {
		    public void run() {
		        sendShowViewRequest(null);
		    }
		};
		sendShowViewRequest.setText(MessageLoader.getString("LineChatClientView.contextmenu.sendShowViewRequest"));
		sendShowViewRequest.setEnabled(true);
		
		if (chatWindow != null) {
			showChatWindow = new Action() {
				public void run() {
					chatWindow.open();
					if (!chatWindow.hasFocus())
						chatWindow.getShell().forceActive();
				}
			};
			showChatWindow.setText("Show chat window");
		}
	}
	protected void sendShowViewRequest(User touser) {
		IWorkbenchWindow ww = PlatformUI.getWorkbench()
				.getActiveWorkbenchWindow();
		IWorkbenchPage page = ww.getActivePage();
		if (page == null)
			return;

		ElementTreeSelectionDialog dlg = new ElementTreeSelectionDialog(
				getShell(), 
				new LabelProvider() {
					private HashMap images = new HashMap();
					public Image getImage(Object element) {
						ImageDescriptor desc = null;
						if (element instanceof IViewCategory)
							desc = PlatformUI.getWorkbench().getSharedImages()
									.getImageDescriptor(
											ISharedImages.IMG_OBJ_FOLDER);
						else if (element instanceof IViewDescriptor)
							desc = ((IViewDescriptor) element).getImageDescriptor();

						if (desc == null)
							return null;
						
						Image image = (Image) images.get(desc);
						if (image == null) {
							image = desc.createImage();
							images.put(desc, image);
						}
						
						return image;
					}
					public String getText(Object element) {
						String label;
						if (element instanceof IViewCategory)
							label = ((IViewCategory) element).getLabel();
						else if (element instanceof IViewDescriptor)
							label = ((IViewDescriptor) element).getLabel();
						else
							label = super.getText(element);
						
						for (
								int i = label.indexOf('&'); 
								i >= 0 && i < label.length() - 1; 
								i = label.indexOf('&', i + 1))
							if (!Character.isWhitespace(label.charAt(i + 1)))
								return label.substring(0, i) + label.substring(i + 1);
						
						return label;
					}
					public void dispose() {
						for (Iterator i = images.values().iterator(); i.hasNext();)
							((Image) i.next()).dispose();

						images = null;
						super.dispose();
					}
				}, 
				new ITreeContentProvider() {
					private HashMap parents = new HashMap();
					public Object[] getChildren(Object element) {
						if (element instanceof IViewRegistry)
							return ((IViewRegistry) element).getCategories();
						else if (element instanceof IViewCategory) {
							IViewDescriptor[] children =
								((IViewCategory) element).getViews();
							for (int i = 0; i < children.length; ++i)
								parents.put(children[i], element);
							
							return children; 
						} else
							return new Object[0];
					}
					public Object getParent(Object element) {
						if (element instanceof IViewCategory)
							return PlatformUI.getWorkbench().getViewRegistry();
						else if (element instanceof IViewDescriptor)
							return parents.get(element);
						else
							return null;
					}
					public boolean hasChildren(Object element) {
						if (element instanceof IViewRegistry
								|| element instanceof IViewCategory)
							return true;
						else
							return false;
					}
					public Object[] getElements(Object inputElement) {
						return getChildren(inputElement);
					}
					public void dispose() {
						parents = null;
					}
					public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
						parents.clear();
					}
				});
		dlg.setTitle(MessageLoader
				.getString("LineChatClientView.contextmenu.sendShowViewRequest"));
		dlg.setMessage(MessageLoader
				.getString("LineChatClientView.contextmenu.sendShowViewRequest.dialog.title"));
		dlg.addFilter(new ViewerFilter() {
			public boolean select(Viewer viewer, Object parentElement, Object element) {
				if (element instanceof IViewDescriptor
						&& "org.eclipse.ui.internal.introview".equals(
								((IViewDescriptor) element).getId()))
					return false;
				else
					return true;
			}});
		dlg.setSorter(new ViewerSorter());
		dlg.setValidator(new ISelectionStatusValidator() {
			public IStatus validate(Object[] selection) {
				for (int i = 0; i < selection.length; ++i)
					if (!(selection[i] instanceof IViewDescriptor))
						return new Status(Status.ERROR, ClientPlugin.getDefault().getBundle().getSymbolicName(), 0, "", null);
				
				return new Status(Status.OK, ClientPlugin.getDefault().getBundle().getSymbolicName(), 0, "", null);
			}
		});
		IViewRegistry reg = PlatformUI.getWorkbench().getViewRegistry(); 
		dlg.setInput(reg);
		IDialogSettings dlgSettings = ClientPlugin.getDefault().getDialogSettings();
		final String DIALOG_SETTINGS = "SendShowViewRequestDialog";
		final String SELECTION_SETTING = "SELECTION";
		IDialogSettings section = dlgSettings.getSection(DIALOG_SETTINGS);
		if (section == null)
			section = dlgSettings.addNewSection(DIALOG_SETTINGS);
		else {
			String[] selectedIDs = section.getArray(SELECTION_SETTING);
			if (selectedIDs != null && selectedIDs.length > 0) {
				ArrayList list = new ArrayList(selectedIDs.length);
				for (int i = 0; i < selectedIDs.length; ++i) {
					IViewDescriptor desc = reg.find(selectedIDs[i]);
					if (desc != null)
						list.add(desc);
				}
				
				dlg.setInitialElementSelections(list);
			}
		}

		dlg.open();
		if (dlg.getReturnCode() == Window.CANCEL)
			return;

		Object[] descs = dlg.getResult();
		if (descs == null)
			return;
		
		String[] selectedIDs = new String[descs.length];
		for (int i = 0; i < descs.length; ++i) {
			selectedIDs[i] = ((IViewDescriptor)descs[i]).getId();
			view.lch.sendShowView(touser, selectedIDs[i]);
		}
		
		section.put(SELECTION_SETTING, selectedIDs);
	}
	protected void sendCVSUpdateRequest(User touser) {
	    //String initStr = MessageLoader.getString("LineChatClientView.contextmenu.sendCVSUpdateRequestInitStr");
		//String res = getID(MessageLoader.getString("LineChatClientView.contextmenu.sendCVSUpdateRequestTitle"),
		//        MessageLoader.getString("LineChatClientView.contextmenu.sendCVSUpdateRequestMessage"), initStr);
		this.view.lch.sendCVSProjectUpdateRequest(touser,null);
	}

	protected void closeProjectGroup(User user) {
		if (MessageDialog.openConfirm(null,
		        MessageLoader.getString("LineChatClientView.contextmenu.closeMessageTitle"),
		        MessageLoader.getString("LineChatClientView.contextmenu.closeMessageMessage")+ this.view.name
						+ "'?")) {
			this.view.lch.chatGUIDestroy();
			
		}

	}

	protected void messageEclipseComponent(User user) {
		String res = null;
		ID userID = null;

		String initStr = "";
		if (this.view.proxyObjects.size() > 0) {
			initStr = (String) this.view.proxyObjects.get(this.view.proxyObjects.size() - 1);
		}
		res = initStr;
		if (user != null) {
			res = getID("Message EclipseProjectComponent for "
					+ user.getNickname(), "EclipseProjectComponent Message:",
					initStr);
			userID = user.getUserID();
		} else {
			res = getID("Message EclipseProjectComponent for Group",
					"EclipseProjectComponent Message:", initStr);
		}
		if (res != null) {
			String className = getCommand(res);
			// Find proxy object in local vector
			if (this.view.proxyObjects.contains(className)) {
				String[] args = getArgs(res);
				String meth = "";
				Object[] actualArgs = new Object[0];
				if (args != null && args.length >= 2) {
					meth = args[0];
					actualArgs = new Object[args.length - 1];
					for (int i = 1; i < args.length; i++) {
						actualArgs[i - 1] = args[i];
					}
				}
				// Send message
				this.view.messageProxyObject(userID, className, meth, actualArgs);
			}
		}
	}

	protected void outputClear() {
		if (MessageDialog.openConfirm(null, "Confirm Clear Text Output",
				"Are you sure you want to clear output?"))
			textoutput.getTextWidget().setText("");
	}

	protected void outputCopy() {
		String t = textoutput.getTextWidget().getSelectionText();
		if (t == null || t.length() == 0) {
			textoutput.getTextWidget().selectAll();
		}
		textoutput.getTextWidget().copy();
		textoutput.getTextWidget().setSelection(
				textoutput.getTextWidget().getText().length());
	}

	protected void outputPaste() {
		textinput.paste();
	}

	protected void outputSelectAll() {
		textoutput.getTextWidget().selectAll();
	}

	protected int getChunkPreference() {
		IPreferenceStore pstore = ClientPlugin.getDefault()
				.getPreferenceStore();
		int chunksize = pstore
				.getInt(ClientPlugin.DEFAULT_FILE_TRANSFER_CHUNKTIME_NAME);
		if (chunksize <= 0) {
			chunksize = 1024;
		}
		return chunksize;
	}

	protected int getDelayPreference() {
		IPreferenceStore pstore = ClientPlugin.getDefault()
				.getPreferenceStore();
		int delay = pstore
				.getInt(ClientPlugin.DEFAULT_FILE_TRANSFER_DELAY_NAME);
		if (delay <= 0) {
			delay = 10;
		}
		return delay;
	}

	protected void readStreamAndSend(java.io.InputStream local,
			String fileName, Date startDate, ID target, final boolean launch) {
		try {
			ID eclipseStageID = IDFactory
					.getDefault().createStringID(org.eclipse.ecf.example.collab.share.EclipseCollabSharedObject.ECLIPSEOBJECTNAME);
			java.io.BufferedInputStream ins = new java.io.BufferedInputStream(
					local);
			java.io.File remoteFile = new File((new File(fileName)).getName());
			FileTransferParams sp = new FileTransferParams(remoteFile,
					getChunkPreference(), getDelayPreference(), null, true,
					-1, null);
			final Object[] args = { view, target, ins,
					sp, eclipseStageID };
			// Do it
			new Thread(new Runnable() {
				public void run() {
				    if (launch) {
						ChatComposite.this.view.createObject(
								null,
								org.eclipse.ecf.example.collab.share.io.EclipseFileTransferAndLaunch.class
										.getName(), new String[] {
										FileSenderUI.class.getName(),
										ID.class.getName(),
										java.io.InputStream.class.getName(),
										FileTransferParams.class.getName(),
										ID.class.getName() }, args);
				    } else {
						ChatComposite.this.view.createObject(
								null,
								org.eclipse.ecf.example.collab.share.io.EclipseFileTransfer.class
										.getName(), new String[] {
										FileSenderUI.class.getName(),
										ID.class.getName(),
										java.io.InputStream.class.getName(),
										FileTransferParams.class.getName(),
										ID.class.getName() }, args);
				    }
				}
			}, "FileRepObject creator").start();
		} catch (Exception e) {
			if (this.view.lch != null)
				this.view.lch.chatException(e, "readStreamAndSend()");
		}

	}

	protected void removeEclipseComponent(User user) {
		String initStr = LineChatClientView.DEFAULT_ECLIPSE_COMPONENT_CLASS;

		String res = null;
		ID userID = null;
		if (user != null) {
			res = getID(
					"Remove EclipseProjectComponent for " + user.getNickname(),
					"EclipseProjectComponent Class:", initStr);
			userID = user.getUserID();
		} else {
			res = getID("Remove EclipseProjectComponent",
					"EclipseProjectComponent Class:", initStr);
		}
		if (res != null)
			this.view.removeProxyObject(userID, res);
	}

	protected void sendAppShare(ID receiver) {
		if (this.view.lch == null)
			return;
        /*
		try {
			if (LineChatView.appShareActive()) {
				Display.getDefault().asyncExec(new Runnable() {
					public void run() {
						MessageDialog.openInformation(null,
						        MessageLoader.getString("LineChatClientView.contextmenu.appshare.activetitle"),
						        MessageLoader.getString("LineChatClientView.contextmenu.appshare.activemessage"));
					}
				});
				return;
			}
			if (MessageDialog.openConfirm(null, MessageLoader.getString("LineChatClientView.contextmenu.appshare.confirmtitle"),
			        MessageLoader.getString("LineChatClientView.contextmenu.appshare.confirmmessage"))) {
                
				VNCParams p = new VNCParams();
				p.setHostname(this.view.userdata.getNickname());
				p.setGroupname(this.view.name);
				Object[] args = new Object[] { receiver, p };
				HashMap map = new HashMap();
				map.put("args",args);
				map.put("types",LineChatClientView.APPSHAREARGTYPES);
				ID serverID = this.view.lch.createObject(null, LineChatClientView.APPSHARECLASSNAME, map);
				EclipseAppShareServer server = (EclipseAppShareServer) this.view.lch.getObject(serverID);
				if (server != null) {
					LineChatView.setAppShareID(serverID,server);
					this.view.setAppShareID(serverID);
				}
			    
			}
		} catch (final Exception e) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					MessageDialog.openInformation(null,
					        MessageLoader.getString("LineChatClientView.contextmenu.appshare.cancelledtitle"),
					        MessageLoader.getString("LineChatClientView.contextmenu.appshare.cancelledmessage"));
					ClientPlugin.log("Exception starting application share",e);
				}
			});
		}
        */
	}

	protected void sendCoBrowseToUser(User user) {
		String res = null;
		ID userID = null;
		if (user != null) {
			res = getID("Co-Browse URL to " + user.getNickname(),
					"URL to Browse:", "http://");
			userID = user.getUserID();
		} else {
			res = getID("Co-Browse URL", "URL to Browse:", "http://");
		}
		if (res != null) {
			Object[] args = { userID, res };
			// Do it
			this.view.createObject(null, LineChatClientView.SHOWURLCLASSNAME, LineChatClientView.SHOWURLARGTYPES,
					args);
		}
	}

	protected void sendEclipseComponent(User user) {
		String initStr = LineChatClientView.DEFAULT_ECLIPSE_COMPONENT_CLASS;

		String res = null;
		ID userID = null;
		if (user != null) {
			res = getID("Send EclipseProjectComponent to " + user.getNickname(),
					"EclipseProjectComponent Class:", initStr);
			userID = user.getUserID();
		} else {
			res = getID("Send EclipseProjectComponent", "EclipseProjectComponent Class:",
					initStr);
		}
		if (res != null)
			this.view.createProxyObject(userID, res);
	}

	protected void sendFile(String pathName, final String fileName,
			Date startDate, ID target,boolean launch) {
        
		try {
			copyFileLocally(pathName, fileName);
		} catch (final IOException e) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					MessageDialog.openError(null, "Local File Copy Error",
							"Exception copying file locally.  Cancelling file transfer.\nException: "
									+ e);
				}
			});
			if (this.view.lch != null)
				this.view.lch.chatException(e, "sendFile(" + pathName + "/"
						+ fileName + ")");
			return;
		}
        
		java.io.FileInputStream ins = null;
		try {
			ins = new java.io.FileInputStream(pathName);
		} catch (final java.io.FileNotFoundException e) {
			Display.getDefault().asyncExec(new Runnable() {
				public void run() {
					MessageDialog.openError(null, "File Open Error",
							"File '" + fileName
									+ "' not found\nException: " + e);
				}
			});
			if (this.view.lch != null)
				this.view.lch.chatException(e, "File '" + fileName + "' not found.");
		}
		readStreamAndSend(ins, fileName, startDate, target,launch);
	}

	protected void sendFileToGroup(boolean launch) {
		FileDialog fd = new FileDialog(Display.getDefault()
				.getActiveShell(), SWT.OPEN);
		fd.setFilterPath(System.getProperty("user.dir"));
		fd.setText("Select File for Group");
		String res = fd.open();
		if (res != null) {
			java.io.File selected = new java.io.File(res);
            File localTarget = new File(this.view.downloaddir,selected.getName());
			sendFile(selected.getPath(), localTarget.getAbsolutePath(),
					null, null,launch);
		}
	}

	protected void sendFileToUser(User user,boolean launch) {
		FileDialog fd = new FileDialog(Display.getDefault()
				.getActiveShell(), SWT.OPEN);
		fd.setFilterPath(System.getProperty("user.dir"));
		fd.setText("Select File for " + user.getNickname());
		String res = fd.open();
		if (res != null) {
			java.io.File selected = new java.io.File(res);
            File localTarget = new File(this.view.downloaddir,selected.getName());
			sendFile(selected.getPath(), localTarget.getAbsolutePath(),
					null, user.getUserID(),launch);
		}
	}

	protected void sendMessageToGroup() {
		String res = getID("Send Message to Group", "Message For Group:",
				"");
		if (res != null & !res.equals("")) {
			String[] args = { res, this.view.userdata.getNickname() };
			this.view.createObject(null, LineChatClientView.MESSAGECLASSNAME, args);
		}
	}

	protected void sendPrivateTextMsg(User data) {
		if (this.view.lch != null) {
			String res = getID("Private Message for " + data.getNickname(),
					"Message: ", "");
			if (res != null)
				this.view.lch.sendPrivateMessageToUser(data, res);
		}
	}

	protected void sendRepObjectToGroup(User user) {
		String result = getID(
				"Send Replicated Object",
				"Replicated Object Class and Args (separated by whitespace):",
				"");
		if (result != null && !result.equals("")) {
			this.view.createObject(null, getCommand(result), getArgs(result));
		}
	}

	protected void sendRepObjectToServer() {
		// XXX TODO
	}

	protected void sendRingMessageToUser(User data) {
		String res = null;
		if (this.view.lch != null) {
			if (data != null) {
				res = getID("Ring " + data.getNickname(), "Ring Message: ",
						"");
			} else {
				res = getID("Ring Group", "Ring Message: ", "");
			}
			if (res != null)
				this.view.lch.sendRingMessageToUser(data, res);
		}
	}

	protected void startProgram(User ud) {
		String res = null;
		ID receiver = null;
		if (ud == null) {
			res = getID("Start Program for Group", "Program to Start:", "");
		} else {
			res = getID("Start Program for " + ud.getNickname(),
					"Program to Start for " + ud.getNickname() + ":", "");
			receiver = ud.getUserID();
		}
		if (res != null)
			this.view.runProgram(receiver, res, null);
	}

	protected void initializeDropTargets() {
		chatDropTarget = new ChatDropTarget(view,textoutput.getTextWidget(), this);
		treeDropTarget = new TreeDropTarget(view,treeView.getControl(), this);
	}
	
	private Color colorFromRGBString(String rgb) {
		Color color = null;
		
		if (rgb == null || rgb.equals("")) {
			color = new Color(getShell().getDisplay(), 0, 0, 0);
			return color;
		}
		
		if (color != null) {
			color.dispose();
		}
		
		String[] vals = rgb.split(",");
		color = new Color(getShell().getDisplay(), Integer.parseInt(vals[0]), Integer.parseInt(vals[1]), Integer.parseInt(vals[2]));
		return color;
	}
	
	private class ColorPropertyChangeListener implements org.eclipse.core.runtime.Preferences.IPropertyChangeListener {

		/* (non-Javadoc)
		 * @see org.eclipse.core.runtime.Preferences.IPropertyChangeListener#propertyChange(org.eclipse.core.runtime.Preferences.PropertyChangeEvent)
		 */
		public void propertyChange(PropertyChangeEvent event) {
			meColor = colorFromRGBString(ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_ME_TEXT_COLOR));
			otherColor = colorFromRGBString(ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_OTHER_TEXT_COLOR));
			systemColor = colorFromRGBString(ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_SYSTEM_TEXT_COLOR));
		}
		
	}
	
	private class FontPropertyChangeListener implements org.eclipse.core.runtime.Preferences.IPropertyChangeListener {
		/* (non-Javadoc)
		 * @see org.eclipse.core.runtime.Preferences.IPropertyChangeListener#propertyChange(org.eclipse.core.runtime.Preferences.PropertyChangeEvent)
		 */
		public void propertyChange(org.eclipse.core.runtime.Preferences.PropertyChangeEvent event) {
			if (event.getProperty().equals(ClientPlugin.PREF_CHAT_FONT)) {
				String fontName = ClientPlugin.getDefault().getPluginPreferences().getString(ClientPlugin.PREF_CHAT_FONT);
				if (!(fontName == null) && !(fontName.equals(""))) {
					FontRegistry fr = ClientPlugin.getDefault().getFontRegistry();
					FontData []newFont = {new FontData(fontName)};
					
					fr.put(CHAT_OUTPUT_FONT, newFont);
					textoutput.getTextWidget().setFont(fr.get(CHAT_OUTPUT_FONT));
				}
			}
		}
		
	}

}
 No newline at end of file