setEditable(false);

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
import java.awt.Insets;
import java.io.File;
import java.net.URL;
import java.util.Observable;
import java.util.Observer;

import javax.swing.JTextPane;
import javax.swing.text.html.HTMLDocument;
import javax.swing.text.html.HTMLEditorKit;

import org.columba.core.config.Config;
import org.columba.core.gui.util.FontProperties;
import org.columba.core.io.DiskIO;
import org.columba.core.io.TempFileStore;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;
import org.columba.mail.config.MailConfig;
import org.columba.mail.gui.message.util.DocumentParser;
import org.columba.mail.parser.text.HtmlParser;

/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class BodyTextViewer extends JTextPane implements Observer {

	// stylesheet is created dynamically because
	// user configurable fonts are used
	private String css = "";

	// parser to transform text to html
	private DocumentParser parser;

	private HTMLEditorKit htmlEditorKit;

	// enable/disable smilies configuration 
	private XmlElement smilies;

	private boolean enableSmilies;

	// name of font
	private String name;

	// size of font
	private String size;

	// overwrite look and feel font settings
	private boolean overwrite;

	public BodyTextViewer() {
		setMargin(new Insets(5, 5, 5, 5));
		setEditable(true);

		htmlEditorKit = new HTMLEditorKit();
		setEditorKit(htmlEditorKit);

		parser = new DocumentParser();

		setContentType("text/html");

		XmlElement gui = MailConfig.get("options").getElement("/options/gui");
		XmlElement messageviewer = gui.getElement("messageviewer");
		if (messageviewer == null) {
			messageviewer = gui.addSubElement("messageviewer");
		}
		smilies = messageviewer.getElement("smilies");
		if (smilies == null) {
			smilies = gui.addSubElement("smilies");
		}

		// register as configuration change listener
		smilies.addObserver(this);

		String enable = smilies.getAttribute("enabled", "true");
		if (enable.equals("true"))
			enableSmilies = true;
		else
			enableSmilies = false;

		XmlElement quote = messageviewer.getElement("quote");
		if (quote == null) {
			quote = messageviewer.addSubElement("quote");
		}

		// register as configuration change listener
		quote.addObserver(this);

		// TODO use value in initStyleSheet()
		String enabled = quote.getAttribute("enabled", "true");
		String color = quote.getAttribute("color", "0");

		// register for configuration changes

		Font font = FontProperties.getTextFont();
		name = font.getName();
		size = new Integer(font.getSize()).toString();
		XmlElement options = Config.get("options").getElement("/options");
		XmlElement gui1 = options.getElement("gui");
		XmlElement fonts = gui1.getElement("fonts");
		if (fonts == null)
			fonts = gui1.addSubElement("fonts");

		// register interest on configuratin changes
		fonts.addObserver(this);

		initStyleSheet();

	}

	/**
	 * 
	 * read text-properties from configuration and 
	 * create a stylesheet for the html-document 
	 *
	 */
	protected void initStyleSheet() {

		// read configuration from options.xml file

		// create css-stylesheet string 
		// set font of html-element <P> 
		css =
			"<style type=\"text/css\"><!-- .bodytext {font-family:\""
				+ name
				+ "\"; font-size:\""
				+ size
				+ "pt; \"}"
				+ ".quoting {color:#949494;}; --></style>";
	}

	public void setBodyText(String bodyText, boolean html) {

		if (html) {
			try {
				// this is a HTML message

				// try to fix broken html-strings
				String validated = HtmlParser.validateHTMLString(bodyText);
				ColumbaLogger.log.debug("validated bodytext:\n" + validated);

				// create temporary file
				File tempFile = TempFileStore.createTempFileWithSuffix("html");

				// save bodytext to file
				DiskIO.saveStringInFile(tempFile, validated);

				URL url = tempFile.toURL();

				// use asynchronous loading method setPage to display
				// URL correctly
				setPage(url);

				// this is the old method which doesn't work
				// for many html-messages
				/* 
				getDocument().remove(0,getDocument().getLength()-1);
								
				((HTMLDocument) getDocument()).getParser().parse(
					new StringReader(validated),
					((HTMLDocument) getDocument()).getReader(0),
					true);
				*/

				// scroll window to the beginning
				setCaretPosition(0);

			} catch (Exception e) {
				e.printStackTrace();
			}
		} else {

			// this is a text/plain message
			try {
				// substitute special characters like:
				//  <,>,&,\t,\n		
				String r = HtmlParser.substituteSpecialCharacters(bodyText);

				// parse for urls and substite with HTML-code
				r = HtmlParser.substituteURL(r);
				// parse for email addresses and substite with HTML-code
				r = HtmlParser.substituteEmailAddress(r);

				// parse for quotings and color the darkgray
				r = parser.markQuotings(r);

				// add smilies
				if (enableSmilies == true)
					r = parser.addSmilies(r);

				// encapsulate bodytext in html-code
				r = transformToHTML(new StringBuffer(r));

				ColumbaLogger.log.debug("validated bodytext:\n" + r);

				// display bodytext
				setText(r);

				//		setup base url in order to be able to display images
				// in html-component
				URL baseUrl = DiskIO.getResourceURL("org/columba/core/images/");
				ColumbaLogger.log.debug(baseUrl.toString());
				((HTMLDocument) getDocument()).setBase(baseUrl);
			} catch (Exception ex) {
				ex.printStackTrace();
			}

			// scroll window to the beginning
			setCaretPosition(0);
		}
	}

	/*
	 * 
	 * encapsulate bodytext in HTML code
	 * 
	 */
	protected String transformToHTML(StringBuffer buf) {
		// prepend
		buf.insert(
			0,
			"<HTML><HEAD>" + css + "</HEAD><BODY class=\"bodytext\"><P>");
		// append
		buf.append("</P></BODY></HTML>");
		return buf.toString();
	}

	/* (non-Javadoc)
	 * 
	 * @see org.columba.mail.gui.config.general.MailOptionsDialog
	 * 
	 * @see java.util.Observer#update(java.util.Observable, java.lang.Object)
	 */
	public void update(Observable arg0, Object arg1) {
		Font font = FontProperties.getTextFont();
		name = font.getName();
		size = new Integer(font.getSize()).toString();

		initStyleSheet();

	}

}