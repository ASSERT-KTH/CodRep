if (evt.character == SWT.CR) {

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

import java.text.SimpleDateFormat;
import java.util.Date;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.user.IUser;
import org.eclipse.ecf.ui.Trace;
import org.eclipse.ecf.ui.UiPlugin;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.text.Document;
import org.eclipse.jface.text.TextViewer;
import org.eclipse.jface.util.IPropertyChangeListener;
import org.eclipse.jface.util.PropertyChangeEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IWorkbenchActionConstants;
import org.eclipse.ui.PlatformUI;

public class TextChatComposite extends Composite {
    
    public static final Trace trace = Trace.create("textchatcomposite");
    
    protected static final int DEFAULT_INPUT_HEIGHT = 25;
    protected static final int DEFAULT_INPUT_SEPARATOR = 5;
    
    protected String TEXT_INPUT_INIT = MessageLoader
    .getString("TextChatComposite.textinputinit");

    protected Color meColor = null;
    protected Color otherColor = null;
    protected Color systemColor = null;

    protected StyledText styledText;
    protected TextViewer textoutput;
    protected Text textinput;

    protected int [] sashWeights = new int[] { 90, 10 };
    
    protected ChatLayout cl = null;
    protected boolean isTyping;
    protected String initText;
    protected ITextInputHandler inputHandler;
    SimpleDateFormat df = new SimpleDateFormat("hh:mm a");
    protected IUser localUser;
    protected IUser remoteUser;
    protected boolean showTimestamp = true;
    
    private Action outputClear = null;
    private Action outputCopy = null;
    private Action outputPaste = null;
    private Action outputSelectAll = null;

    public TextChatComposite(Composite parent, int style, String initText, ITextInputHandler handler, IUser localUser, IUser remoteUser) {
        super(parent, style);

        this.initText = initText;
        this.inputHandler = handler;
        
        this.localUser = localUser;
        this.remoteUser = remoteUser;
        
        this.meColor = new Color(getShell().getDisplay(), 23, 135, 65);
        this.otherColor = new Color(getShell().getDisplay(), 65, 13, 165);
        this.systemColor = new Color(getShell().getDisplay(), 123, 135, 165);
        
        this.addDisposeListener(new DisposeListener() {

            public void widgetDisposed(DisposeEvent e) {
                meColor.dispose();
                otherColor.dispose();
                systemColor.dispose();
            }
            
        });
        
        // Setup layout
        cl = new ChatLayout(DEFAULT_INPUT_HEIGHT, DEFAULT_INPUT_SEPARATOR);
        setLayout(cl);

        // Setup text output
        textoutput = new TextViewer(this, SWT.BORDER | SWT.V_SCROLL | SWT.WRAP);
        styledText = textoutput.getTextWidget();
        styledText.setEditable(false);
        textoutput.setDocument(new Document(this.initText));

        textoutput.setEditable(false);
        
        // Setup text input
        textinput = new Text(this, SWT.SINGLE | SWT.BORDER | SWT.H_SCROLL);
        cl.setInputTextHeight(textinput.getFont().getFontData()[0]
                .getHeight() + 2);
        textinput.setText(TEXT_INPUT_INIT);
        
        textinput.selectAll();
        textinput.addKeyListener(new KeyListener() {
            public void keyPressed(KeyEvent evt) {
                handleKeyPressed(evt);
            }

            public void keyReleased(KeyEvent evt) {
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
                if (isTyping && textinput.getText().trim().length() == 0)
                    isTyping = false;
                else if (!isTyping) {
                    isTyping = true;
                    sendStartedTyping();
                }
            }
        });

        makeActions();
        hookContextMenu();
        
        UiPlugin.getDefault().getPreferenceStore().addPropertyChangeListener(new IPropertyChangeListener() {
            public void propertyChange(PropertyChangeEvent event) {
                if (event.getProperty().equals(UiPlugin.PREF_DISPLAY_TIMESTAMP)) {
                    showTimestamp = ((Boolean)event.getNewValue()).booleanValue();
                }   
            }
            
        });

    }

    private void makeActions() {
        outputSelectAll = new Action() {
            public void run() {
                outputSelectAll();
            }
        };
        outputSelectAll.setText("Select All");
        outputSelectAll.setAccelerator(SWT.CTRL | 'A');
        outputCopy = new Action() {
            public void run() {
                outputCopy();
            }
        };
        outputCopy.setText("Copy");
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

        outputPaste = new Action() {
            public void run() {
                outputPaste();
            }
        };
        outputPaste.setText("Paste");
        outputCopy.setAccelerator(SWT.CTRL | 'V');
        outputPaste.setImageDescriptor(PlatformUI.getWorkbench()
                .getSharedImages().getImageDescriptor(
                        ISharedImages.IMG_TOOL_PASTE));

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

    private void hookContextMenu() {
        MenuManager menuMgr = new MenuManager("#PopupMenu");
        menuMgr.setRemoveAllWhenShown(true);
        menuMgr.addMenuListener(new IMenuListener() {
            public void menuAboutToShow(IMenuManager manager) {
                fillContextMenu(manager);
            }
        });
        Menu menu = menuMgr.createContextMenu(textoutput.getControl());
        textoutput.getControl().setMenu(menu);
        PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().getActivePart().getSite().registerContextMenu(menuMgr,textoutput);
        //registerContextMenu(menuMgr, textoutput);
    }

    private void fillContextMenu(IMenuManager manager) {
        manager.add(outputCopy);
        manager.add(outputPaste);
        manager.add(outputClear);
        manager.add(new Separator());
        manager.add(outputSelectAll);
        manager.add(new Separator());
        manager.add(new Separator());
        // Other plug-ins can contribute there actions here
        manager.add(new Separator(IWorkbenchActionConstants.MB_ADDITIONS));
    }

    public void setLocalUser(IUser newUser) {
        this.localUser = newUser;
    }
    public void setRemoteUser(IUser remoteUser) {
        this.remoteUser = remoteUser;
    }
    public IUser getRemoteUser() {
        return this.remoteUser;
    }
    protected String getCurrentDateTime() {
        StringBuffer sb = new StringBuffer("(");
        sb.append(df.format(new Date())).append(") ");
        return sb.toString();
    }
    private String makeLineWithTimestamp(String line) {
        if (showTimestamp) {
            return getCurrentDateTime() + line;
        }
        return line;
    }

    public IUser getLocalUser() {
        return localUser;
    }
    public void appendText(ChatLine text) {
        StyledText st = textoutput.getTextWidget();
        
        if (text == null || textoutput == null || st == null)
            return;

        int startRange = st.getText().length();
        StringBuffer sb = new StringBuffer();
        
        if (text.getOriginator() != null) {
            sb.append(makeLineWithTimestamp(text.getOriginator().getName() + ": "));
            StyleRange sr = new StyleRange();
            sr.start = startRange;
            sr.length = sb.length();
            IUser localUser = getLocalUser();
            if (localUser != null && localUser.getID().equals(text.getOriginator().getID())) { 
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
            st.setStyleRange(sr);
        }
        
        if (!text.isNoCRLF()) {
            st.append("\n");
        }
        
        String t = st.getText();
        if (t == null)
            return;
        st.setSelection(t.length());
    }

    protected void handleKeyPressed(KeyEvent evt) {
        if (evt.keyCode == SWT.CR) {
            handleEnter();
        } 
    }

    protected void handleEnter() {
        String text = textinput.getText().trim();
        if(text.length() > 0) sendTextLineInput(text);
        
        clearInput();
        isTyping = false;
    }

    protected void clearInput() {
        textinput.setText("");
    }

    protected void sendTextLineInput(String text) {
        if (inputHandler != null) {
            IUser localUser = getLocalUser();
            IUser remoteUser = getRemoteUser();
            if (localUser != null && remoteUser != null) {
                inputHandler.handleTextLine(remoteUser.getID(),text);
                appendText(new ChatLine(text,localUser));
            } else {
                UiPlugin.getDefault().getLog().log(new Status(Status.ERROR,UiPlugin.PLUGIN_ID,100,"Null localUser or remoteUser for textchatcomposite",new NullPointerException()));
            }
        } else {
            UiPlugin.getDefault().getLog().log(new Status(Status.ERROR,UiPlugin.PLUGIN_ID,100,"No inputhandler available for textchatcomposite",new NullPointerException()));
        }
    }

    protected void sendStartedTyping() {
        if (inputHandler != null) {
            IUser localUser = getLocalUser();
            IUser remoteUser = getRemoteUser();
            if (localUser != null && remoteUser != null) {
                inputHandler.handleStartTyping(remoteUser.getID());
            } else {
                UiPlugin.getDefault().getLog().log(new Status(Status.ERROR,UiPlugin.PLUGIN_ID,100,"Null localUser or remoteUser for textchatcomposite",new NullPointerException()));
            }
        } else {
            UiPlugin.getDefault().getLog().log(new Status(Status.ERROR,UiPlugin.PLUGIN_ID,100,"No inputhandler available for textchatcomposite",new NullPointerException()));
        }
    }
    
    protected String getShellName() {
        return "org.eclipse.ecf.ui.views.TextChatComposite";
    }
    public void dispose() {
        super.dispose();
    }

    protected void setDisposed() {
        textinput.setEnabled(false);
    }
    protected void checkSubclass() {
    }
}