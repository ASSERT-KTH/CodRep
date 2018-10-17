import org.columba.mail.gui.table.selection.MessageSelectionListener;

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
import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.net.URL;

import javax.swing.JButton;
import javax.swing.JEditorPane;
import javax.swing.JPopupMenu;
import javax.swing.SwingUtilities;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.HyperlinkListener;
import javax.swing.text.AttributeSet;
import javax.swing.text.Element;
import javax.swing.text.html.HTML;
import javax.swing.text.html.HTMLDocument;

import org.columba.core.config.Config;
import org.columba.core.util.CharsetEvent;
import org.columba.core.util.CharsetListener;
import org.columba.core.xml.XmlElement;
import org.columba.mail.coder.CoderRouter;
import org.columba.mail.coder.Decoder;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.frame.MailFrameController;
import org.columba.mail.gui.message.action.MessageActionListener;
import org.columba.mail.gui.message.action.MessageFocusListener;
import org.columba.mail.gui.message.action.MessagePopupListener;
import org.columba.mail.gui.message.menu.MessageMenu;
import org.columba.mail.gui.table.MessageSelectionListener;
import org.columba.mail.gui.util.URLController;
import org.columba.mail.message.HeaderInterface;
import org.columba.mail.message.MimePart;
import org.columba.mail.message.MimePartTree;

/**
 * this class shows the messagebody
 */

public class MessageController
	implements
		MessageSelectionListener,
		HyperlinkListener,
		MouseListener, CharsetListener
{

	private Folder folder;
	private Object uid;

	private MessageMenu menu;

	private MessageFocusListener focusListener;

	private MessagePopupListener popupListener;

	private JButton button;

	private String activeCharset;

	private MessageView view;
	private MessageActionListener actionListener;

	protected MailFrameController mailFrameController;

	//private MessageSelectionManager messageSelectionManager;

	public MessageController(MailFrameController mailFrameController) {

		this.mailFrameController = mailFrameController;

		activeCharset = "auto";

		view = new MessageView(this);
		view.addHyperlinkListener(this);
		view.addMouseListener(this);

		//messageSelectionManager = new MessageSelectionManager();

		actionListener = new MessageActionListener(this);

		/*
		String[] keys = new String[4];
		keys[0] = new String("Subject");
		keys[1] = new String("From");
		keys[2] = new String("Date");
		keys[3] = new String("To");
		*/

		Font mainFont = Config.getOptionsConfig().getGuiItem().getMainFont();

		menu = new MessageMenu(this);

	}

	public void messageSelectionChanged(Object[] newUidList) {
		//System.out.println("received new message-selection changed event");

		/*
		FolderCommandReference[] reference = (FolderCommandReference[]) MainInterface.frameController.tableController.getTableSelectionManager().getSelection();
		
		FolderTreeNode treeNode = reference[0].getFolder();
		Object[] uids = reference[0].getUids();
		
		// this is no message-viewing action,
		// but a selection of multiple messages
		if ( uids.length > 1 ) return;
		
		MainInterface.frameController.attachmentController.getAttachmentSelectionManager().setFolder(treeNode);
		MainInterface.frameController.attachmentController.getAttachmentSelectionManager().setUids(uids);
		
		MainInterface.processor.addOp(
			new ViewMessageCommand(
				mailFrameController,
				reference));
		*/

		/*
		MainInterface.crossbar.operate(
				new GuiOperation(Operation.MESSAGEBODY, 4, (Folder) selectionManager.getFolder(), newUidList[0]));
				*/
	}

	public MessageActionListener getActionListener() {
		return actionListener;
	}

	public MessageView getView() {

		//new MessageActionListener( view );

		return view;
	}

	public JPopupMenu getPopupMenu() {
		return menu.getPopupMenu();
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

	public void showMessage(
		HeaderInterface header,
		MimePart bodyPart,
		MimePartTree mimePartTree)
		throws Exception {

		XmlElement html =
			MailConfig.getMainFrameOptionsConfig().getRoot().getElement(
				"/options/html");
		boolean htmlViewer =
			new Boolean(html.getAttribute("prefer")).booleanValue();

		// Which Charset shall we use ?

		String charset;

		if (activeCharset.equals("auto"))
			charset = bodyPart.getHeader().getContentParameter("charset");
		else
			charset = activeCharset;

		Decoder decoder =
			CoderRouter.getDecoder(
				bodyPart.getHeader().contentTransferEncoding);

		// Shall we use the HTML-Viewer?

		htmlViewer =
			bodyPart.getHeader().contentSubtype.equalsIgnoreCase("html");

		// Update the MessageHeaderPane
		/*
		messageHeader.setValues(message);
		*/

		String decodedBody = null;

		// Decode the Text using the specified Charset				
		try {
			decodedBody = decoder.decode(bodyPart.getBody(), charset);
		} catch (UnsupportedEncodingException ex) {
			// If Charset not supported fall back to standard Charset

			try {
				decodedBody = decoder.decode(bodyPart.getBody(), null);
			} catch (UnsupportedEncodingException never) {

			}
		}

		boolean hasAttachments = false;

		
		if ((mimePartTree.count() > 1)
			|| (!mimePartTree.get(0).getHeader().contentType.equals("text")))
			hasAttachments = true;

			getMailFrameController().attachmentController.setMimePartTree(
							mimePartTree);
							/*
		if (hasAttachments)
			getMailFrameController().attachmentController.setMimePartTree(
				mimePartTree);
		else
			getMailFrameController().attachmentController.setMimePartTree(null);
		*/
		getView().setDoc(header, decodedBody, htmlViewer, hasAttachments);

		getView().getVerticalScrollBar().setValue(0);

	}

	public void showMessageSource(String rawText) throws Exception {
		getView().setDoc(null, rawText, false, false);

		getView().getVerticalScrollBar().setValue(0);

	}
	/*
	 * 
	public MessageActionListener getActionListener()
	{
		return actionListener;
	}
	
	public MessageFocusListener getFocusListener()
	{
		return focusListener;
	}
	
	public String getAddress()
	{
		HyperlinkTextViewer viewer =
			(HyperlinkTextViewer) view.getViewer(MessageView.ADVANCED);
	
		if (viewer != null)
			return viewer.getAddress();
		else
			return new String();
	}
	
	public String getLink()
	{
		HyperlinkTextViewer viewer =
			(HyperlinkTextViewer) view.getViewer(MessageView.ADVANCED);
	
		if (viewer != null)
			return viewer.getLink();
		else
			return new String();
	}
	*/

	/*	
	public void charsetChanged( CharsetEvent e ) {
		activeCharset = e.getValue();				
	}
	*/

	public void hyperlinkUpdate(HyperlinkEvent e) {
		/*
		if (e.getEventType() == HyperlinkEvent.EventType.ACTIVATED) {
			JEditorPane pane = (JEditorPane) e.getSource();
			if (e instanceof HTMLFrameHyperlinkEvent) {
				HTMLFrameHyperlinkEvent evt = (HTMLFrameHyperlinkEvent) e;
				HTMLDocument doc = (HTMLDocument) pane.getDocument();
				doc.processHTMLFrameHyperlinkEvent(evt);
			} else {
				URL url = e.getURL();
				if (url != null) {
		
					if (url.getProtocol().equalsIgnoreCase("mailto")) {
						// found email address
						URLController c = new URLController();
						JPopupMenu menu = c.createContactMenu(url.getFile());
						menu.setVisible(true);
		
					} else {
		
						URLController c = new URLController();
						c.open(url);
					}
				}
			}
		}
		*/

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
		if (!SwingUtilities.isLeftMouseButton(event))
			return;

		URL url = extractURL(event);
		if (url == null)
			return;
		URLController c = new URLController();
		if (url.getProtocol().equalsIgnoreCase("mailto"))
			c.compose(url.getFile());
		else
			c.open(url);
	}

	/*
	    private String getMapHREF(JEditorPane html, HTMLDocument hdoc,
	                              Element elem, AttributeSet attr, int offset,
	                              int x, int y) {
	        Object useMap = attr.getAttribute(HTML.Attribute.USEMAP);
	        if (useMap != null && (useMap instanceof String)) {
	            Map m = hdoc.getMap((String)useMap);
	            if (m != null && offset < hdoc.getLength()) {
	                Rectangle bounds;
	                TextUI ui = html.getUI();
	                try {
	                    Shape lBounds = ui.modelToView(html, offset,
	                                               Position.Bias.Forward);
	                    Shape rBounds = ui.modelToView(html, offset + 1,
	                                               Position.Bias.Backward);
	                    bounds = lBounds.getBounds();
	                    bounds.add((rBounds instanceof Rectangle) ?
	                                (Rectangle)rBounds : rBounds.getBounds());
	                } catch (BadLocationException ble) {
	                    bounds = null;
	                }
	                if (bounds != null) {
	                    AttributeSet area = m.getArea(x - bounds.x,
	                                                  y - bounds.y,
	                                                  bounds.width,
	                                                  bounds.height);
	                    if (area != null) {
	                        return (String)area.getAttribute(HTML.Attribute.
	                                                         HREF);
	                    }
	                }
	            }
	        }
	        return null;
	    }
	*/

	protected URL extractURL(MouseEvent event) {
		JEditorPane pane = (JEditorPane) event.getSource();
		HTMLDocument doc = (HTMLDocument) pane.getDocument();

		Element e = doc.getCharacterElement(pane.viewToModel(event.getPoint()));
		AttributeSet a = e.getAttributes();
		AttributeSet anchor = (AttributeSet) a.getAttribute(HTML.Tag.A);
		/*
		if ( anchor == null )
			s = getMapHREF(pane, doc, e, a, pane.viewToModel(event.getPoint()), event.getX(), event.getY() );
		*/
		if (anchor == null)
			return null;

		URL url = null;
		try {
			url = new URL((String) anchor.getAttribute(HTML.Attribute.HREF));
		} catch (MalformedURLException mue) {
		}
		return url;
	}

	protected void processPopup(MouseEvent event) {
		URL url = extractURL(event);
		URLController c = new URLController();
		JPopupMenu menu = c.createMenu(url);
		menu.show(getView(), event.getX(), event.getY());
	}

	/********************* context menu *******************************************/

	/**
	 * Returns the mailFrameController.
	 * @return MailFrameController
	 */
	public MailFrameController getMailFrameController() {
		return mailFrameController;
	}

	/* (non-Javadoc)
	 * @see org.columba.core.util.CharsetListener#charsetChanged(org.columba.core.util.CharsetEvent)
	 */
	public void charsetChanged(CharsetEvent e) {
		activeCharset = e.getValue();

	}

}