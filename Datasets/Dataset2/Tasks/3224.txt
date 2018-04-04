ColumbaLogger.log.info(baseUrl.toString());

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

import org.columba.core.io.DiskIO;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.xml.XmlElement;

import org.columba.mail.config.MailConfig;
import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.parser.text.HtmlParser;

import org.columba.ristretto.message.Address;
import org.columba.ristretto.message.AddressListRenderer;
import org.columba.ristretto.message.BasicHeader;

import java.awt.Font;
import java.awt.Insets;

import java.net.URL;

import java.text.DateFormat;

import java.util.Date;
import java.util.Iterator;
import java.util.List;
import java.util.StringTokenizer;
import java.util.Vector;

import javax.swing.JTextPane;
import javax.swing.UIManager;
import javax.swing.text.html.HTMLDocument;
import javax.swing.text.html.HTMLEditorKit;


/**
 * @author freddy
 *
 * To change this generated comment edit the template variable "typecomment":
 * Window>Preferences>Java>Templates.
 * To enable and disable the creation of type comments go to
 * Window>Preferences>Java>Code Generation.
 */
public class HeaderViewer extends JTextPane {
    /*
     * *20030720, karlpeder* Adjusted layout of header table to avoid lines
     * extending the right margin (bug #774117)
     */

    // background: ebebeb
    // frame: d5d5d5
    private static final String LEFT_COLUMN_PROPERTIES = "border=\"0\" nowrap font=\"dialog\" align=\"right\" valign=\"top\" width=\"5%\""; //width=\"65\"";
    private static final String RIGHT_COLUMN_PROPERTIES = "border=\"0\" align=\"left\" valign=\"top\" width=\"90%\""; //width=\"100%\"";
    private static final String OUTTER_TABLE_PROPERTIES =
        "border=\"1\" cellspacing=\"1\" cellpadding=\"1\" " +
        "align=\"left\" width=\"100%\" " +
        "style=\"border-width:1px; border-style:solid;  background-color:#ebebeb\"";

    // stylesheet is created dynamically because
    // user configurable fonts are used
    private String css = "";

    // contains headerfields which are to be displayed
    List keys;

    public HeaderViewer() {
        setMargin(new Insets(5, 5, 5, 5));
        setEditable(false);

        HTMLEditorKit editorKit = new HTMLEditorKit();

        setEditorKit(editorKit);

        // setup base url in order to be able to display images
        // in html-component
        URL baseUrl = DiskIO.getResourceURL("org/columba/core/images/");
        ColumbaLogger.log.debug(baseUrl.toString());
        ((HTMLDocument) getDocument()).setBase(baseUrl);

        // add headerfields which are about to show up
        initHeaderFields();

        initStyleSheet();
    }

    protected void initHeaderFields() {
        // add headerfields which are about to show up
        XmlElement headerviewerElement = MailConfig.get("options").getElement("/options/headerviewer");
        String list = headerviewerElement.getAttribute("headerfields");

        StringTokenizer tok = new StringTokenizer(list, " ");
        keys = new Vector();

        while (tok.hasMoreTokens()) {
            String key = (String) tok.nextToken();
            keys.add(key);
        }

        /*
                        keys = new String[7];
                        keys[0] = "Subject";
                        keys[1] = "Date";
                        keys[2] = "Reply-To";
                        keys[3] = "From";
                        keys[4] = "To";
                        keys[5] = "Cc";
                        keys[6] = "Bcc";
                        */
    }

    /**
    *
    * read text-properties from configuration and
    * create a stylesheet for the html-document
    *
    */
    protected void initStyleSheet() {
        /*
        //        read configuration from options.xml file
        XmlElement mainFont =
                Config.get("options").getElement("/options/gui/mainfont");
        String name = mainFont.getAttribute("name");
        String size = mainFont.getAttribute("size");
        Font font = new Font(name, Font.PLAIN, Integer.parseInt(size));
        */
        Font font = UIManager.getFont("Label.font");
        String name = font.getName();
        int size = font.getSize();

        // create css-stylesheet string 
        // set font of html-element <TD> 
        css = "<style type=\"text/css\"><!--td {font-family:\"" + name +
            "\"; font-size:\"" + size + "pt\"}--></style>";
    }

    void setHeader(ColumbaHeader header, boolean hasAttachments)
        throws Exception {
        // border #949494
        // background #989898
        // #a0a0a0
        // bright #d5d5d5
        StringBuffer buf = new StringBuffer();

        // prepend HTML-code
        buf.append("<HTML><HEAD>" + css + "</HEAD><BODY ><TABLE " +
            OUTTER_TABLE_PROPERTIES + ">");

        // for every existing headerfield
        for (Iterator it = keys.iterator(); it.hasNext();) {
            String key = (String) it.next();

            // for (int i = 0; i < keys.size(); i++) {
            // String key = (String) keys.get(i);
            if (key == null) {
                continue;
            }

            // message doesn't contain this headerfield
            if (header.get(key) == null) {
                continue;
            }

            // headerfield is empty
            if (((String) header.get(key)).length() == 0) {
                continue;
            }

            // create left column
            buf.append("<TR><TD " + LEFT_COLUMN_PROPERTIES + ">");

            // set left column text
            buf.append("<B>" + key + " : </B></TD>");

            // create right column
            buf.append("<TD " + RIGHT_COLUMN_PROPERTIES + ">");

            // set right column text
            // look for special headers like subject, to, date
            String str = null;

            if (key.equals("Subject")) {
                str = (String) header.get("columba.subject");

                // substitute special characters like:
                //  <,>,&,\t,\n,"
                str = HtmlParser.substituteSpecialCharactersInHeaderfields(str);
            } else if (key.equals("To")) {
                BasicHeader bHeader = new BasicHeader(header.getHeader());
                str = AddressListRenderer.renderToHTMLWithLinks(bHeader.getTo())
                                         .toString();
            } else if (key.equals("Reply-To")) {
                BasicHeader bHeader = new BasicHeader(header.getHeader());
                str = AddressListRenderer.renderToHTMLWithLinks(bHeader.getReplyTo())
                                         .toString();
            } else if (key.equals("From")) {
                BasicHeader bHeader = new BasicHeader(header.getHeader());
                str = AddressListRenderer.renderToHTMLWithLinks(new Address[] {
                            (Address) bHeader.getFrom()
                        }).toString();
            } else if (key.equals("Date")) {
                DateFormat df = DateFormat.getDateTimeInstance(DateFormat.LONG,
                        DateFormat.MEDIUM);
                str = df.format((Date) header.get("columba.date"));

                // substitute special characters like:
                //  <,>,&,\t,\n,"
                str = HtmlParser.substituteSpecialCharactersInHeaderfields(str);
            } else {
                str = (String) header.get(key);

                // substitute special characters like:
                //  <,>,&,\t,\n,"
                str = HtmlParser.substituteSpecialCharactersInHeaderfields(str);
            }

            // parse for email addresses and substite with HTML-code
            //str = HtmlParser.substituteEmailAddress(str);
            // append HTML-code
            buf.append(" " + str + "</TD>");

            buf.append("</TR>");
        }

        if (hasAttachments) {
            // email has attachments 
            //  -> display attachment icon
            buf.append("<TR><TD " + LEFT_COLUMN_PROPERTIES + ">");

            buf.append("<IMG SRC=\"stock_attach.png\"></TD>");

            buf.append("<TD " + RIGHT_COLUMN_PROPERTIES + ">");
            buf.append(" " + "</TD>");
        }

        // close HTML document
        buf.append("</TABLE></BODY></HTML>");

        // display html-text
        setText(buf.toString());
    }
}