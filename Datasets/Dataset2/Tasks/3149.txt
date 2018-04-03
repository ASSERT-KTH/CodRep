view = new HtmlEditorView(null);

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
package org.columba.mail.gui.composer.html;

import java.awt.Font;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.util.logging.Logger;

import javax.swing.JComponent;
import javax.swing.JTextPane;
import javax.swing.event.CaretEvent;
import javax.swing.event.CaretListener;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.text.BadLocationException;
import javax.swing.text.ChangedCharSetException;
import javax.swing.text.Document;
import javax.swing.text.EditorKit;
import javax.swing.text.html.HTML;

import org.columba.mail.gui.composer.AbstractEditorController;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.html.util.FormatInfo;

/**
 * Controller part of controller-view frame work for composing html messages
 * 
 * @author Karl Peder Olesen
 * 
 */
public class HtmlEditorController extends AbstractEditorController implements
		DocumentListener, CaretListener {

	/** JDK 1.4+ logging framework logger, used for logging. */
	private static final Logger LOG = Logger
			.getLogger("org.columba.mail.gui.composer.html");

	/** Main view (WYSIWYG) */
	protected HtmlEditorView view;

	/**
	 * Default constructor.
	 */
	public HtmlEditorController(ComposerController controller) {
		super(controller);

		// create view (by passing null as document, the view creates it)
		view = new HtmlEditorView(this, null);

		// FocusManager.getInstance().registerComponent(this);
		view.addCaretListener(this);
	}

	/**
	 * Installs this controller as DocumentListener on the view
	 */
	public void installListener() {
		view.installListener(this);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.composer.AbstractEditorController#updateComponents(boolean)
	 */
	public void updateComponents(boolean b) {
		if (b) {
			if (this.getController().getModel().getBodyText() != null) {
				this.setViewText(this.getController().getModel().getBodyText());
			}
		} else {
			if (view.getText() != null) {
				this.getController().getModel().setBodyText(view.getText());
			}
		}
	}

	/** ************* Methods for setting html specific formatting ************ */
	/**
	 * Toggle bold font in the view on/off
	 */
	public void toggleBold() {
		view.toggleBold();
	}

	/**
	 * Toggle italic font in the view on/off
	 */
	public void toggleItalic() {
		view.toggleItalic();
	}

	/**
	 * Toggle underline font in the view on/off
	 */
	public void toggleUnderline() {
		view.toggleUnderline();
	}

	/**
	 * Toggle strikeout font in the view on/off
	 */
	public void toggleStrikeout() {
		view.toggleStrikeout();
	}

	/**
	 * Toggle teletyper font (type written text) in the view on/off
	 */
	public void toggleTeleTyper() {
		view.toggleTeleTyper();
	}

	/**
	 * Sets alignment in the view to left, center or right
	 * 
	 * @param align
	 *            One of StyleConstants.ALIGN_LEFT, StyleConstants.ALIGN_CENTER
	 *            or StyleConstants.ALIGN_RIGHT
	 */
	public void setAlignment(int align) {
		view.setTextAlignment(align);

		/*
		 * notify observers about format change - this is necessary to update
		 * the state of alignment buttons / menues (same notification as made in
		 * caretUpdate
		 */
		boolean textSelected = false;
		String text = view.getSelectedText();

		if (text == null) {
			textSelected = false;
		} else if (text.length() > 0) {
			textSelected = true;
		}

		int pos = view.getCaretPosition();
		setChanged();
		notifyObservers(new FormatInfo(view.getHtmlDoc(), pos, textSelected));
	}

	/**
	 * Sets paragraph format for selected paragraphs or current paragraph if no
	 * text is selected
	 * 
	 * @param tag
	 *            Html tag specifying the format to set
	 */
	public void setParagraphFormat(HTML.Tag tag) {
		view.setParagraphFormat(tag);
	}

	/**
	 * Method for inserting a break (BR) element
	 */
	public void insertBreak() {
		view.insertBreak();
	}

	/** **************** FocusOwner implementation **************************** */

	// the following lines add cut/copy/paste/undo/redo/selectall
	// actions support using the Columba action objects.
	//
	// This means that we only have a single instance of these
	// specific actions, which is shared by all menuitems and
	// toolbar buttons.
	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#isCutActionEnabled()
	 */
	public boolean isCutActionEnabled() {
		if (view.getSelectedText() == null) {
			return false;
		}

		if (view.getSelectedText().length() > 0) {
			return true;
		}

		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#isCopyActionEnabled()
	 */
	public boolean isCopyActionEnabled() {
		if (view.getSelectedText() == null) {
			return false;
		}

		if (view.getSelectedText().length() > 0) {
			return true;
		}

		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#isPasteActionEnabled()
	 */
	public boolean isPasteActionEnabled() {
		return true;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#isDeleteActionEnabled()
	 */
	public boolean isDeleteActionEnabled() {
		if (view.getSelectedText() == null) {
			return false;
		}

		if (view.getSelectedText().length() > 0) {
			return true;
		}

		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#isSelectAllActionEnabled()
	 */
	public boolean isSelectAllActionEnabled() {
		return true;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#isRedoActionEnabled()
	 */
	public boolean isRedoActionEnabled() {
		// TODO (@author karlpeder): Implementation of undo/redo missing
		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#isUndoActionEnabled()
	 */
	public boolean isUndoActionEnabled() {
		// TODO (@author karlpeder): Implementation of undo/redo missing
		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#cut()
	 */
	public void cut() {
		view.cut();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#copy()
	 */
	public void copy() {
		view.copy();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#paste()
	 */
	public void paste() {
		view.paste();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#delete()
	 */
	public void delete() {
		view.replaceSelection("");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#redo()
	 */
	public void redo() {
		// TODO (@author karlpeder): Implementation of undo/redo missing
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#undo()
	 */
	public void undo() {
		// TODO (@author karlpeder): Implementation of undo/redo missing
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#selectAll()
	 */
	public void selectAll() {
		view.selectAll();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.core.gui.focus.FocusOwner#getComponent()
	 */
	public JComponent getComponent() {
		return view;
	}

	/** *************** Methods necessary to hide view from clients *********** */

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.composer.AbstractEditorController#getViewFont()
	 */
	public Font getViewFont() {
		return view.getFont();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.composer.AbstractEditorController#setViewFont(java.awt.Font)
	 */
	public void setViewFont(Font f) {
		view.setFont(f);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.composer.AbstractEditorController#getViewText()
	 */
	public String getViewText() {
		return view.getText();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.composer.AbstractEditorController#setViewText(java.lang.String)
	 */
	public void setViewText(String text) {
		// // This doesn't handle ChangedCharsetExceptions correctly.
		// view.setText(text);
		try {
			loadHtmlIntoView(text, false);
		} catch (ChangedCharSetException ccse) {
			// try again, but ignore charset specification in the html
			try {
				loadHtmlIntoView(text, true);
			} catch (IOException e) {
				LOG.severe("Error setting view content, "
						+ "even after ignore charset spec: " + e.getMessage());
			}
		} catch (IOException e) {
			// other IOExceptions than ChangedCharsetException
			LOG.severe("Error setting view content: " + e.getMessage());
		}
	}

	/**
	 * Private utility for loading html into the view. Is called from
	 * setViewText. <br>
	 * The method works mostly as calling view.setText() directly, but is
	 * necessary to be able to handle ChangedCharsetExceptions
	 * 
	 * @param text
	 *            Text to load into the view
	 * @param ignoreCharset
	 *            If set to true, charset specifications in the html will be
	 *            ignore
	 * @throws IOException
	 */
	private void loadHtmlIntoView(String text, boolean ignoreCharset)
			throws IOException {
		// clear existing text
		Document doc = view.getDocument();

		try {
			// delete old contents
			doc.remove(0, doc.getLength());

			// if no text is specified, we are done now
			if ((text == null) || (text.equals(""))) {
				return;
			}

			// load contents into document
			if (ignoreCharset) {
				view.getHtmlDoc().putProperty("IgnoreCharsetDirective",
						Boolean.TRUE);
			}

			Reader r = new StringReader(text);
			EditorKit kit = view.getEditorKit();
			kit.read(r, doc, 0); // this can throw a ChangedCharsetException
		} catch (BadLocationException e) {
			LOG.severe("Error deleting old view content: " + e.getMessage());

			return;
		}
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.composer.AbstractEditorController#getViewUIComponent()
	 */
	public JTextPane getViewUIComponent() {
		return view;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.composer.AbstractEditorController#setViewEnabled(boolean)
	 */
	public void setViewEnabled(boolean enabled) {
		view.setEnabled(enabled);
	}

	/** *************** DocumentListener Implementation *********************** */

	/*
	 * (non-Javadoc)
	 * 
	 * @see javax.swing.event.DocumentListener#changedUpdate(javax.swing.event.DocumentEvent)
	 */
	public void changedUpdate(DocumentEvent e) {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see javax.swing.event.DocumentListener#insertUpdate(javax.swing.event.DocumentEvent)
	 */
	public void insertUpdate(DocumentEvent e) {
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see javax.swing.event.DocumentListener#removeUpdate(javax.swing.event.DocumentEvent)
	 */
	public void removeUpdate(DocumentEvent e) {
	}

	/** ***************** CaretListener Implementation ************************ */
	/**
	 * Used to update actions (cut, copy, etc.) via the focusManager. This is
	 * done since charet updates may have coursed text selections etc. to
	 * change, which in turn should enable/disable cut, copy, etc. actions.
	 * <p>
	 * This method also notifies all observers which are specific to the HTML
	 * component only. This includes almost all actions in package
	 * org.columba.mail.gui.composer.html.action
	 * <p>
	 * The information to the observers contains information about the format at
	 * the current caret position and about text selections. The information is
	 * encapsulated in a FormatInfo object.
	 * 
	 * @see javax.swing.event.CaretListener#caretUpdate(javax.swing.event.CaretEvent)
	 */
	public void caretUpdate(CaretEvent e) {
		// update state of actions such as cut, copy, paste, undo...
		// FIXME focus manager
		// FocusManager.getInstance().updateActions();

		// get info on current text selection
		boolean textSelected = false;
		String text = view.getSelectedText();

		if (text == null) {
			textSelected = false;
		} else if (text.length() > 0) {
			textSelected = true;
		}

		// get current caret position
		int pos = e.getDot();

		// notify observers (typically formatting actions).
		setChanged();
		notifyObservers(new FormatInfo(view.getHtmlDoc(), pos, textSelected));
	}
}