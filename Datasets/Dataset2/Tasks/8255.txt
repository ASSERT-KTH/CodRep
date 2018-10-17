getPopupMenu().show(event.getComponent(), event.getX(), event.getY());

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
package org.columba.mail.gui.message;

import java.awt.Font;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.Charset;
import java.nio.charset.UnsupportedCharsetException;

import javax.swing.JButton;
import javax.swing.JComponent;
import javax.swing.JEditorPane;
import javax.swing.JPopupMenu;
import javax.swing.SwingUtilities;
import javax.swing.event.CaretEvent;
import javax.swing.event.CaretListener;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.HyperlinkListener;
import javax.swing.text.AttributeSet;
import javax.swing.text.Element;
import javax.swing.text.html.HTML;
import javax.swing.text.html.HTMLDocument;

import org.columba.core.charset.CharsetEvent;
import org.columba.core.charset.CharsetListener;
import org.columba.core.charset.CharsetOwnerInterface;
import org.columba.core.gui.focus.FocusOwner;
import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.main.MainInterface;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.attachment.AttachmentController;
import org.columba.mail.gui.frame.AbstractMailFrameController;
import org.columba.mail.gui.message.command.ViewMessageCommand;
import org.columba.mail.gui.util.URLController;
import org.columba.mail.message.ColumbaHeader;
import org.columba.ristretto.coder.Base64DecoderInputStream;
import org.columba.ristretto.coder.CharsetDecoderInputStream;
import org.columba.ristretto.coder.QuotedPrintableDecoderInputStream;
import org.columba.ristretto.message.MimeHeader;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.message.StreamableMimePart;


/**
 * this class shows the messagebody
 */
public class MessageController implements HyperlinkListener, MouseListener,
    CharsetListener, FocusOwner, CaretListener {
    private Folder folder;
    private Object uid;
    private MessageMenu menu;
    private JButton button;
    private String activeCharset;
    private MessageView view;
    private URLObservable urlObservable;
    protected AbstractMailFrameController abstractFrameController;
    protected AttachmentController attachmentController;

    //private MessageSelectionManager messageSelectionManager;
    public MessageController(
        AbstractMailFrameController abstractFrameController,
        AttachmentController attachmentController) {
        this.abstractFrameController = abstractFrameController;
        this.attachmentController = attachmentController;
        activeCharset = "auto";

        view = new MessageView(this, attachmentController.getView());

        //view.addHyperlinkListener(this);
        view.addMouseListener(this);

        ((CharsetOwnerInterface) getFrameController()).getCharsetManager()
         .addCharsetListener(this);

        MainInterface.focusManager.registerComponent(this);

        view.bodyTextViewer.addCaretListener(this);

        urlObservable = new URLObservable();
    }

    public MessageView getView() {
        return view;
    }

    public void createPopupMenu() {
        menu = new MessageMenu(abstractFrameController);
    }

    /**
    * return the PopupMenu for the message viewer
    */
    public JPopupMenu getPopupMenu() {
        return menu;
    }

    public void setViewerFont(Font font) {
        //textPane.setFont( font );
    }

    public Object getUid() {
        return uid;
    }

    public Folder getFolder() {
        return folder;
    }

    public void setFolder(Folder f) {
        this.folder = f;
    }

    public void setUid(Object o) {
        this.uid = o;
    }

    public void showMessage(ColumbaHeader header, MimePart bodyPart,
        MimeTree mimePartTree) throws Exception {
        if ((header == null) || (bodyPart == null)) {
            return;
        }

        // Which Charset shall we use ?
        String charsetName;

        if (activeCharset.equals("auto")) {
            charsetName = bodyPart.getHeader().getContentParameter("charset");

            ((CharsetOwnerInterface) getFrameController()).getCharsetManager()
             .displayCharset(charsetName);
        } else {
            charsetName = activeCharset;
        }

        // Shall we use the HTML-Viewer?
        boolean htmlViewer = bodyPart.getHeader().getMimeType().getSubtype()
                                     .equals("html");

        InputStream bodyStream = ((StreamableMimePart) bodyPart).getInputStream();

        int encoding = bodyPart.getHeader().getContentTransferEncoding();

        switch( encoding ) {
            case MimeHeader.QUOTED_PRINTABLE : {
                    bodyStream = new QuotedPrintableDecoderInputStream(bodyStream);
                    break;
                } 
                
               case MimeHeader.BASE64 : {
                       bodyStream = new Base64DecoderInputStream(bodyStream);
                       break;
                   }
        }
        
        if (charsetName != null) {
            Charset charset;

            try {
                charset = Charset.forName(charsetName);
            } catch (UnsupportedCharsetException e) {
                charset = Charset.forName(System.getProperty("file.encoding"));
            }

            bodyStream = new CharsetDecoderInputStream(bodyStream, charset);
        }

        boolean hasAttachments = header.hasAttachments().booleanValue();
        
        attachmentController.setMimePartTree(mimePartTree);

        getView().setDoc(header, bodyStream, htmlViewer, hasAttachments);

        getView().getVerticalScrollBar().setValue(0);
    }

    public void setPGPMessage(int value, String message) {
        getView().getPgp().setValue(value, message);
    }

    public void hyperlinkUpdate(HyperlinkEvent e) {
    }

    public void mousePressed(MouseEvent event) {
        if (event.isPopupTrigger()) {
            processPopup(event);
        }
    }

    public void mouseReleased(MouseEvent event) {
        if (event.isPopupTrigger()) {
            processPopup(event);
        }
    }

    public void mouseEntered(MouseEvent event) {
    }

    public void mouseExited(MouseEvent event) {
    }

    public void mouseClicked(MouseEvent event) {
        if (!SwingUtilities.isLeftMouseButton(event)) {
            return;
        }

        URL url = extractURL(event);

        if (url == null) {
            return;
        }

        URLController c = new URLController();

        if (url.getProtocol().equalsIgnoreCase("mailto")) {
            c.compose(url.getFile());
        } else {
            c.open(url);
        }
    }

    protected URL extractURL(MouseEvent event) {
        JEditorPane pane = (JEditorPane) event.getSource();
        HTMLDocument doc = (HTMLDocument) pane.getDocument();

        Element e = doc.getCharacterElement(pane.viewToModel(event.getPoint()));
        AttributeSet a = e.getAttributes();
        AttributeSet anchor = (AttributeSet) a.getAttribute(HTML.Tag.A);

        if (anchor == null) {
            return null;
        }

        URL url = null;

        try {
            url = new URL((String) anchor.getAttribute(HTML.Attribute.HREF));
        } catch (MalformedURLException mue) {
            return null;
        }

        return url;
    }

    protected void processPopup(MouseEvent ev) {
        final URL url = extractURL(ev);
        final MouseEvent event = ev;

        if (url == null) {
            urlObservable.setUrl(null);
        } else {
            urlObservable.setUrl(url);
        }

        // open context-menu 
        // -> this has to happen in the awt-event dispatcher thread
        SwingUtilities.invokeLater(new Runnable() {
                public void run() {
                    getPopupMenu().show(getView(), event.getX(), event.getY());
                }
            });
    }

    /********************* context menu *******************************************/
    /**
     * Returns the mailFrameController.
     * @return MailFrameController
     */
    public FrameMediator getFrameController() {
        return abstractFrameController;
    }

    /* (non-Javadoc)
     * @see org.columba.core.util.CharsetListener#charsetChanged(org.columba.core.util.CharsetEvent)
     */
    public void charsetChanged(CharsetEvent e) {
        activeCharset = e.getValue();

        MainInterface.processor.addOp(new ViewMessageCommand(
                getFrameController(),
                ((AbstractMailFrameController) getFrameController()).getTableSelection()));
    }

    /******************* FocusOwner interface ***********************/

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#copy()
     */
    public void copy() {
        view.bodyTextViewer.copy();
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#cut()
     */
    public void cut() {
        // not supported
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#delete()
     */
    public void delete() {
        // not supported
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#getComponent()
     */
    public JComponent getComponent() {
        return view.bodyTextViewer;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#isCopyActionEnabled()
     */
    public boolean isCopyActionEnabled() {
        if (view.bodyTextViewer.getSelectedText() == null) {
            return false;
        }

        if (view.bodyTextViewer.getSelectedText().length() > 0) {
            return true;
        }

        return false;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#isCutActionEnabled()
     */
    public boolean isCutActionEnabled() {
        // action not support
        return false;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#isDeleteActionEnabled()
     */
    public boolean isDeleteActionEnabled() {
        // action not supported
        return false;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#isPasteActionEnabled()
     */
    public boolean isPasteActionEnabled() {
        // action not supported
        return false;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#isRedoActionEnabled()
     */
    public boolean isRedoActionEnabled() {
        // action not supported
        return false;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#isSelectAllActionEnabled()
     */
    public boolean isSelectAllActionEnabled() {
        return true;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#isUndoActionEnabled()
     */
    public boolean isUndoActionEnabled() {
        // action not supported
        return false;
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#paste()
     */
    public void paste() {
        // action not supported
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#redo()
     */
    public void redo() {
        // action not supported
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#selectAll()
     */
    public void selectAll() {
        view.bodyTextViewer.selectAll();
    }

    /* (non-Javadoc)
     * @see org.columba.core.gui.focus.FocusOwner#undo()
     */
    public void undo() {
        // TODO Auto-generated method stub
    }

    /************************** CaretUpdateListener interface *****************/

    /* (non-Javadoc)
     * @see javax.swing.event.CaretListener#caretUpdate(javax.swing.event.CaretEvent)
     */
    public void caretUpdate(CaretEvent arg0) {
        MainInterface.focusManager.updateActions();
    }

    /**
     * @return
     */
    public URLObservable getUrlObservable() {
        return urlObservable;
    }
}