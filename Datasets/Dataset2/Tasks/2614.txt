import org.columba.core.pluginhandler.ViewPluginHandler;

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.

package org.columba.mail.gui.composer;

import org.columba.addressbook.folder.Folder;
import org.columba.addressbook.folder.HeaderItem;
import org.columba.addressbook.folder.HeaderItemList;
import org.columba.addressbook.main.AddressbookInterface;

import org.columba.core.charset.CharsetEvent;
import org.columba.core.charset.CharsetListener;
import org.columba.core.charset.CharsetOwnerInterface;
import org.columba.core.config.ViewItem;
import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.frame.AbstractFrameView;
import org.columba.core.gui.view.AbstractView;
import org.columba.core.gui.util.NotifyDialog;
import org.columba.core.main.MainInterface;
import org.columba.core.plugin.PluginHandlerNotFoundException;
import org.columba.core.plugin.ViewPluginHandler;
import org.columba.core.xml.XmlElement;

import org.columba.mail.gui.composer.html.HtmlEditorController;
import org.columba.mail.gui.composer.text.TextEditorController;
import org.columba.mail.gui.composer.util.IdentityInfoPanel;
import org.columba.mail.gui.view.AbstractComposerView;
import org.columba.mail.main.MailInterface;
import org.columba.mail.parser.text.HtmlParser;
import org.columba.mail.util.AddressCollector;
import org.frappucino.swing.MultipleTransferHandler;

import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.awt.event.ContainerListener;

import java.nio.charset.Charset;
import java.nio.charset.UnsupportedCharsetException;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Observable;
import java.util.Observer;
import java.util.logging.Logger;

import javax.swing.JEditorPane;
import javax.swing.event.EventListenerList;

/**
 * @author frd
 *
 * controller for message composer dialog
 */
public class ComposerController extends AbstractFrameController
    implements CharsetOwnerInterface, ComponentListener, Observer {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.gui.composer");

    private IdentityInfoPanel identityInfoPanel;
    private AttachmentController attachmentController;
    private SubjectController subjectController;
    private PriorityController priorityController;
    private AccountController accountController;

    //private TextEditorController editorController;
    private AbstractEditorController editorController;
    private HeaderController headerController;

    //private MessageComposer messageComposer;
    private ComposerSpellCheck composerSpellCheck;
    private ComposerModel composerModel;
    private Charset charset;
    private EventListenerList listenerList = new EventListenerList();

    /** Buffer for listeners used by addContainerListenerForEditor and createView */
    private List containerListenerBuffer;

    public ComposerController(ViewItem view) {
        super("Composer", view);
    }

    public boolean checkState() {
        // update ComposerModel based on user-changes in ComposerView
        updateComponents(false);

        if (!subjectController.checkState()) {
            return false;
        }

        return !headerController.checkState();
    }

    public void updateComponents(boolean b) {
        subjectController.updateComponents(b);
        editorController.updateComponents(b);
        priorityController.updateComponents(b);
        accountController.updateComponents(b);
        attachmentController.updateComponents(b);
        headerController.updateComponents(b);

        //headerController.appendRow();
    }

    protected void initAddressCompletion() {
        AddressCollector.clear();

        HeaderItemList list = ((Folder) AddressbookInterface.addressbookTreeModel.getFolder(101)).getHeaderItemList();

        for (int i = 0; i < list.count(); i++) {
            HeaderItem item = list.get(i);

            if (item.contains("displayname")) {
                AddressCollector.addAddress((String) item.get("displayname"),
                    item); //$NON-NLS-1$ //$NON-NLS-2$
            }

            if (item.contains("email;internet")) {
                AddressCollector.addAddress((String) item.get("email;internet"),
                    item); //$NON-NLS-1$ //$NON-NLS-2$
            }
        }

        list = ((Folder) AddressbookInterface.addressbookTreeModel.getFolder(102)).getHeaderItemList();

        for (int i = 0; i < list.count(); i++) {
            HeaderItem item = list.get(i);

            if (item.contains("displayname")) {
                AddressCollector.addAddress((String) item.get("displayname"),
                    item); //$NON-NLS-1$ //$NON-NLS-2$
            }

            if (item.contains("email;internet")) {
                AddressCollector.addAddress((String) item.get("email;internet"),
                    item); //$NON-NLS-1$ //$NON-NLS-2$
            }
        }
    }

    /*
    protected void updateAddressbookFrame() {

            if ((view.getLocation().x
                    - composerInterface.addressbookFrame.getSize().width
                    < 0)
                    || (view.getLocation().y < 0)) {
                    int x =
                            view.getLocation().x
                                    - composerInterface.addressbookFrame.getSize().width;
                    int y = view.getLocation().y;

                    if (x <= 0)
                            x = 0;
                    if (y <= 0)
                            y = 0;

                    view.setLocation(
                            x + composerInterface.addressbookFrame.getSize().width,
                            y);

            }

            composerInterface.addressbookFrame.setLocation(
                    view.getLocation().x
                            - composerInterface.addressbookFrame.getSize().width,
                    view.getLocation().y);

    }*/
    public void componentHidden(ComponentEvent e) {
    }

    public void componentMoved(ComponentEvent e) {
        /*
        if (composerInterface.addressbookFrame.isVisible()) {
                updateAddressbookFrame();
        }*/
    }

    public void componentResized(ComponentEvent e) {
    }

    public void componentShown(ComponentEvent e) {
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.FrameController#createView()
     */
    protected AbstractView createView() {
        //ComposerView view = new ComposerView(this);
        // Load "plugin" view instead
        ViewPluginHandler handler = null;

        try {
            handler = (ViewPluginHandler) MainInterface.pluginManager.getHandler(
                    "org.columba.core.view");
        } catch (PluginHandlerNotFoundException ex) {
            NotifyDialog d = new NotifyDialog();
            d.showDialog(ex);
        }

        // get view using the plugin handler found above
        Object[] args = {this};

        try {
            view = (AbstractView) handler.getPlugin(
                getViewItem().getRoot().getAttribute("frame", id), args);
        } catch (Exception ex) {
            ex.printStackTrace();
        }


        // *20030917, karlpeder* If ContainerListeners are waiting to be
        // added, add them now.
        if (containerListenerBuffer != null) {
            LOG.fine("Adding ContainerListeners from buffer");

            Iterator ite = containerListenerBuffer.iterator();

            while (ite.hasNext()) {
                ContainerListener cl = (ContainerListener) ite.next();
                ((AbstractComposerView)view).getEditorPanel().addContainerListener(cl);
            }

            containerListenerBuffer = null; // done, the buffer has been emptied
        }

        headerController.view.initFocus(subjectController.view);

        return view;
    }

    public void openView() {
        super.openView();
        initAddressCompletion();
        headerController.getView().editLastRow();
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.FrameController#initInternActions()
     */
    protected void initInternActions() {
    }

    /**
     * @return AccountController
     */
    public AccountController getAccountController() {
        return accountController;
    }

    /**
     * @return AttachmentController
     */
    public AttachmentController getAttachmentController() {
        return attachmentController;
    }

    /**
     * @return ComposerSpellCheck
     */
    public ComposerSpellCheck getComposerSpellCheck() {
        return composerSpellCheck;
    }

    /**
     * @return TextEditorController
     */
    public AbstractEditorController getEditorController() {
        /*
         * *20030906, karlpeder* Method signature changed to
         * return an AbstractEditorController
         */
        return editorController;
    }

    /**
     * @return HeaderController
     */
    public HeaderController getHeaderController() {
        return headerController;
    }

    /**
     * @return IdentityInfoPanel
     */
    public IdentityInfoPanel getIdentityInfoPanel() {
        return identityInfoPanel;
    }

    /**
     * @return PriorityController
     */
    public PriorityController getPriorityController() {
        return priorityController;
    }

    /**
     * @return SubjectController
     */
    public SubjectController getSubjectController() {
        return subjectController;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.FrameController#init()
     */
    protected void init() {
        // init model (defaults to empty plain text message)
        composerModel = new ComposerModel();

        // init controllers for different parts of the composer
        identityInfoPanel = new IdentityInfoPanel();
        attachmentController = new AttachmentController(this);
        headerController = new HeaderController(this);
        subjectController = new SubjectController(this);
        priorityController = new PriorityController(this);
        accountController = new AccountController(this);
        composerSpellCheck = new ComposerSpellCheck(this);

        // set default html or text based on stored option
        // ... can be overridden by setting the composer model
        XmlElement optionsElement = MailInterface.config.get("composer_options")
                                                        .getElement("/options");
        XmlElement htmlElement = optionsElement.getElement("html");

        // create default element if not available
        if (htmlElement == null) {
            htmlElement = optionsElement.addSubElement("html");
        }

        String enableHtml = htmlElement.getAttribute("enable", "false");

        // set model based on configuration
        if (enableHtml.equals("true")) {
            getModel().setHtml(true);
        } else {
            getModel().setHtml(false);
        }

        // Add the composer controller as observer
        htmlElement.addObserver(this);

        // init controller for the editor depending on message type
        if (getModel().isHtml()) {
            editorController = new HtmlEditorController(this);
        } else {
            editorController = new TextEditorController(this);
        }

        // Hack to ensure charset is set correctly at start-up
        XmlElement charsetElement = optionsElement.getElement("charset");

        if (charsetElement != null) {
            String charset = charsetElement.getAttribute("name");

            if (charset != null) {
                try {
                    setCharset(Charset.forName(charset));
                } catch (UnsupportedCharsetException ex) {
                    //ignore this
                }
            }
        }
        
        // Setup DnD for the text and attachment list control.
        ComposerAttachmentTransferHandler dndTransferHandler = new ComposerAttachmentTransferHandler(attachmentController);
        attachmentController.view.setDragEnabled(true);
        attachmentController.view.setTransferHandler(dndTransferHandler);

        JEditorPane editorComponent = (JEditorPane) getEditorController().getComponent();
        MultipleTransferHandler compositeHandler = new MultipleTransferHandler();
        compositeHandler.addTransferHandler(editorComponent.getTransferHandler());
        compositeHandler.addTransferHandler(dndTransferHandler);
        editorComponent.setDragEnabled(true);
        editorComponent.setTransferHandler(compositeHandler);
    }

    /**
     * Returns the composer model
     * @return        Composer model
     */
    public ComposerModel getModel() {
        //if (composerModel == null) // *20030907, karlpeder* initialized in init
        //  composerModel = new ComposerModel();
        return composerModel;
    }

    /**
     * Sets the composer model. If the message type of the new
     * model (html / text) is different from the message type of
     * the existing, the editor controller is changed and the
     * view is changed accordingly.
     * <br>
     * Finally the components are updated according to the new model.
     *
     * @param         model        New composer model
     */
    public void setComposerModel(ComposerModel model) {
        boolean wasHtml = composerModel.isHtml();
        composerModel = model;

        if (wasHtml != composerModel.isHtml()) {
            // new editor controller needed
            switchEditor(composerModel.isHtml());

            XmlElement optionsElement = MailInterface.config.get(
                    "composer_options").getElement("/options");
            XmlElement htmlElement = optionsElement.getElement("html");

            //create default element if not available
            if (htmlElement == null) {
                htmlElement = optionsElement.addSubElement("html");
            }

            // change configuration based on new model
            htmlElement.addAttribute("enable",
                Boolean.toString(composerModel.isHtml()));

            // notify observers - this includes this object - but here it will
            // do nothing, since the model is already setup correctly
            htmlElement.notifyObservers();
        }

        // Update all component according to the new model
        updateComponents(true);
    }

    /**
     * Private utility for switching btw. html and text.
     * This includes instantiating a new editor controller
     * and refreshing the editor view accordingly.
     * <br>
     * Pre-condition: The caller should set the composer model
     * before calling this method. If a message was already entered
     * in the UI, then updateComponents should have been called to
     * synchronize model with view before switching, else data will be lost.
     * <br>
     * Post-condition: The caller must call updateComponents afterwards
     * to display model data using the new controller-view pair
     *
     * @param        html        True if we should switch to html, false for text
     */
    private void switchEditor(boolean html) {
        if (composerModel.isHtml()) {
            LOG.fine("Switching to html editor");
            editorController.deleteObservers(); // clean up
            editorController = new HtmlEditorController(this);
        } else {
            LOG.fine("Switching to text editor");
            editorController.deleteObservers(); // clean up
            editorController = new TextEditorController(this);
        }

        // an update of the view is also necessary.
        ((AbstractComposerView) getView()).setNewEditorView();
    }

    /**
     * Register ContainerListener for the panel, that holds the
     * editor view. By registering as listener it is possible to
     * get information when the editor changes.
     * <br>
     * If the view is not yet created, the listener is stored in
     * a buffer - add then added in createView. This is necessary to
     * handle the timing involved in setting up the controller-view
     * framework for the composer
     */
    public void addContainerListenerForEditor(ContainerListener cl) {
        if (view != null) {
            // add listener
            ((AbstractComposerView) view).getEditorPanel().addContainerListener(cl);
        } else {
            // view not yet created - store listener in buffer
            if (containerListenerBuffer == null) {
                containerListenerBuffer = new ArrayList();
            }

            containerListenerBuffer.add(cl);
        }
    }

    /**
     * Removes a ContainerListener from the panel, that holds the
     * editor view (previously registered using
     * addContainListenerForEditor)
     */
    public void removeContainerListenerForEditor(ContainerListener cl) {
        ((AbstractComposerView) getView()).getEditorPanel().removeContainerListener(cl);
    }

    public Charset getCharset() {
        return charset;
    }

    public void setCharset(Charset charset) {
        this.charset = charset;

        XmlElement optionsElement = MailInterface.config.get("composer_options")
                                                        .getElement("/options");
        XmlElement charsetElement = optionsElement.getElement("charset");

        if (charset == null) {
            optionsElement.removeElement(charsetElement);
        } else {
            if (charsetElement == null) {
                charsetElement = new XmlElement("charset");
                optionsElement.addElement(charsetElement);
            }

            charsetElement.addAttribute("name", charset.name());
        }

        ((ComposerModel) getModel()).setCharset(charset);
        fireCharsetChanged(new CharsetEvent(this, charset));
    }

    public void addCharsetListener(CharsetListener l) {
        listenerList.add(CharsetListener.class, l);
    }

    public void removeCharsetListener(CharsetListener l) {
        listenerList.remove(CharsetListener.class, l);
    }

    protected void fireCharsetChanged(CharsetEvent e) {
        // Guaranteed to return a non-null array
        Object[] listeners = listenerList.getListenerList();

        // Process the listeners last to first, notifying
        // those that are interested in this event
        for (int i = listeners.length - 2; i >= 0; i -= 2) {
            if (listeners[i] == CharsetListener.class) {
                ((CharsetListener) listeners[i + 1]).charsetChanged(e);
            }
        }
    }

    /**
     * Used for listenen to the enable html option
     *
     * @see java.util.Observer#update(java.util.Observable, java.lang.Object)
     */
    public void update(Observable o, Object arg) {
        XmlElement e = (XmlElement) o;

        if (e.getName().equals("html")) {
            // switch btw. html and text if necessary
            String enableHtml = e.getAttribute("enable", "false");
            boolean html = Boolean.valueOf(enableHtml).booleanValue();
            boolean wasHtml = composerModel.isHtml();

            if (html != wasHtml) {
                composerModel.setHtml(html);

                // sync model with the current (old) view
                updateComponents(false);

                // convert body text to comply with new editor format
                String oldBody = composerModel.getBodyText();
                String newBody;

                if (html) {
                    LOG.fine("Converting body text to html");
                    newBody = HtmlParser.textToHtml(oldBody, "", null);
                } else {
                    LOG.fine("Converting body text to text");
                    newBody = HtmlParser.htmlToText(oldBody);
                }

                composerModel.setBodyText(newBody);

                // switch editor and resync view with model
                switchEditor(composerModel.isHtml());
                updateComponents(true);
            }
        }
    }
}