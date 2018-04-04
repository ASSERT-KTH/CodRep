import org.columba.mail.gui.message.AttachmentModel;

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
package org.columba.mail.folder.command;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;
import java.util.logging.Logger;

import javax.swing.JCheckBox;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.filechooser.FileFilter;

import org.columba.core.command.Command;
import org.columba.core.command.ICommandReference;
import org.columba.core.command.StatusObservableImpl;
import org.columba.core.command.Worker;
import org.columba.core.command.WorkerStatusController;
import org.columba.core.config.Config;
import org.columba.core.io.DiskIO;
import org.columba.core.io.StreamUtils;
import org.columba.core.xml.XmlElement;
import org.columba.mail.command.MailFolderCommandReference;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.AbstractMessageFolder;
import org.columba.mail.gui.attachment.AttachmentModel;
import org.columba.mail.gui.message.util.DocumentParser;
import org.columba.mail.parser.text.HtmlParser;
import org.columba.mail.util.MailResourceLoader;
import org.columba.ristretto.coder.Base64DecoderInputStream;
import org.columba.ristretto.coder.CharsetDecoderInputStream;
import org.columba.ristretto.coder.QuotedPrintableDecoderInputStream;
import org.columba.ristretto.message.BasicHeader;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.MimeHeader;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.message.StreamableMimePart;


/**
 * This class is used to save a message to file either as a html file or a text
 * file.
 *
 * @author Karl Peder Olesen (karlpeder), 20030611
 */
public class SaveMessageBodyAsCommand extends Command {

    /** JDK 1.4+ logging framework logger, used for logging. */
    private static final Logger LOG = Logger.getLogger("org.columba.mail.folder.command");

    /** Static field representing the system line separator */
    private static final String NL = "\n";

    //System.getProperty("line.separator");

    /** The charset to use for decoding messages before save */
    private Charset charset;

	private Header header;

	private MimeHeader bodyHeader;
	private InputStream bodyStream;

	private List attachments;
	
    /**
     * Constructor for SaveMessageBodyAsCommand. Calls super constructor and
     * saves charset for later use
     *
     * @param references
     * @param charset
     *            Charset to use for decoding messages before save
     */
    public SaveMessageBodyAsCommand(ICommandReference reference,
        Charset charset) {
        super(reference);
        this.charset = charset;
    }


    /**
     * This method executes the save action, i.e. it saves the selected
     * messages to disk as either plain text or as html. <br>At the momemt no
     * header or attachment information is saved with the message!
     *
     * @param worker
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(WorkerStatusController worker)
        throws Exception {
        MailFolderCommandReference r = (MailFolderCommandReference) getReference();
        Object[] uids = r.getUids(); // uid for messages to save
        AbstractMessageFolder srcFolder = (AbstractMessageFolder) r.getSourceFolder();

        //	register for status events
        ((StatusObservableImpl) srcFolder.getObservable()).setWorker(worker);

        JFileChooser fileChooser = new JFileChooser();

        // save each message
        for (int j = 0; j < uids.length; j++) {
            Object uid = uids[j];
            LOG.info("Saving UID=" + uid);

            header = srcFolder.getAllHeaderFields(uid);
            setupMessageBodyPart(uid, srcFolder,worker);
            
            AttachmentModel attMod = new AttachmentModel();
            attMod.setCollection(srcFolder.getMimePartTree(uid));

            attachments = attMod.getDisplayedMimeParts();
            
			// determine type of body part
            boolean ishtml = false;

            if (bodyHeader.getMimeType().getSubtype().equals("html")) {
                ishtml = true;
            }

            // setup filters and filename for file chooser dialog
            ExtensionFileFilter txtFilter = new ExtensionFileFilter("txt",
                    "Text (*.txt)");
            ExtensionFileFilter htmlFilter = new ExtensionFileFilter("html",
                    "Html (*.html)");
            fileChooser.resetChoosableFileFilters();
            fileChooser.setAcceptAllFileFilterUsed(false);
            fileChooser.addChoosableFileFilter(txtFilter);
            fileChooser.addChoosableFileFilter(htmlFilter);

            // add check box for incl. of headers
            JCheckBox inclHeaders = new JCheckBox(MailResourceLoader.getString(
                        "dialog", "saveas", "save_all_headers"),
                    getInclAllHeadersOption());
            fileChooser.setAccessory(inclHeaders);

            // setup dialog title, active filter and file name
            String defaultName = getValidFilename((String) header.get("Subject"),
                    false);

            if (ishtml) {
                fileChooser.setDialogTitle(MailResourceLoader.getString(
                        "dialog", "saveas", "save_html_message"));
                fileChooser.setFileFilter(htmlFilter);

                if (defaultName.length() > 0) {
                    fileChooser.setSelectedFile(new File(defaultName + "."
                            + htmlFilter.getExtension()));
                }
            } else {
                fileChooser.setDialogTitle(MailResourceLoader.getString(
                        "dialog", "saveas", "save_text_message"));
                fileChooser.setFileFilter(txtFilter);

                if (defaultName.length() > 0) {
                    fileChooser.setSelectedFile(new File(defaultName + "."
                            + txtFilter.getExtension()));
                }
            }

            // show dialog
            int res = fileChooser.showSaveDialog(null);

            if (res == JFileChooser.APPROVE_OPTION) {
                File f = fileChooser.getSelectedFile();
                ExtensionFileFilter filter = (ExtensionFileFilter) fileChooser.getFileFilter();

                // Add default extension if no extension is given by the user
                if (ExtensionFileFilter.getFileExtension(f) == null) {
                    f = new File(f.getAbsolutePath() + "."
                            + filter.getExtension());
                }

                int confirm;

                if (f.exists()) {
                    // file exists, user needs to confirm overwrite
                    confirm = JOptionPane.showConfirmDialog(null,
                            MailResourceLoader.getString("dialog", "saveas",
                                "overwrite_existing_file"),
                            MailResourceLoader.getString("dialog", "saveas",
                                "file_exists"), JOptionPane.YES_NO_OPTION,
                            JOptionPane.QUESTION_MESSAGE);
                } else {
                    confirm = JOptionPane.YES_OPTION;
                }

                if (confirm == JOptionPane.YES_OPTION) {
                    // store whether all headers should be incl.
                    boolean incl = inclHeaders.isSelected();
                    storeInclAllHeadersOption(incl);
                    LOG.info("Incl. all headers: " + incl);

                    // save message
                    if (filter.getExtension().equals(htmlFilter.getExtension())) {
                        saveMsgBodyAsHtml(incl, f);
                    } else {
                        saveMsgBodyAsText(incl, f);
                    }
                }
            }
        }

        // end of for loop over uids to save
    }

    /**
     * Private utility to extract a valid filename from a message subject or
     * another string. <br>This means remove the chars: / \ : , \n \t NB: If
     * the input string is null, an empty string is returned
     *
     * @param subj
     *            Message subject
     * @param replSpaces
     *            If true, spaces are replaced by _
     * @return A valid filename without the chars mentioned
     */
    private String getValidFilename(String subj, boolean replSpaces) {
        if (subj == null) {
            return "";
        }

        StringBuffer buf = new StringBuffer();

        for (int i = 0; i < subj.length(); i++) {
            char c = subj.charAt(i);

            if ((c == '\\') || (c == '/') || (c == ':') || (c == ',')
                    || (c == '\n') || (c == '\t')) {
                // dismiss char
            } else if ((c == ' ') && (replSpaces)) {
                buf.append('_');
            } else {
                buf.append(c);
            }
        }

        return buf.toString();
    }

    /**
     * Gets the value of the option "Incl. all headers"
     *
     * @return true if all headers should be included, else false
     */
    private boolean getInclAllHeadersOption() {
        boolean defaultValue = false; // default value

        XmlElement options = Config.getInstance().get("options").getElement("/options");

        if (options == null) {
            return defaultValue;
        }

        XmlElement savemsg = options.getElement("/savemsg");

        if (savemsg != null) {
            if (savemsg.getAttribute("incl_all_headers",
                        String.valueOf(defaultValue)).equals("true")) {
                return true;
            } else {
                return false;
            }
        } else {
            return defaultValue;
        }
    }

    /**
     * Saves the option "Incl. all headers"
     *
     * @param val
     *            Value of the option (true to incl. all headers)
     */
    private void storeInclAllHeadersOption(boolean val) {
        XmlElement options = Config.getInstance().get("options").getElement("/options");

        if (options == null) {
            return;
        }

        XmlElement savemsg = options.getElement("/savemsg");

        if (savemsg == null) {
            // create new
            savemsg = new XmlElement("savemsg");
            savemsg.addAttribute("incl_all_headers", String.valueOf(val));
            options.addElement(savemsg);
        } else {
            savemsg.addAttribute("incl_all_headers", String.valueOf(val));
        }
    }

    /**
     * Private utility to get body part of a message. User preferences
     * regarding html messages is used to select what to retrieve. If the body
     * part retrieved is null, a fake one containing a simple text is returned
     *
     * @param uid
     *            ID of message
     * @param srcFolder
     *            AbstractMessageFolder containing the message
     * @param worker
     * @return body part of message
     */
    private void setupMessageBodyPart(Object uid, AbstractMessageFolder srcFolder,
        WorkerStatusController worker) throws Exception {
        // Does the user prefer html or plain text?
        XmlElement html = MailConfig.getInstance().getMainFrameOptionsConfig()
                                              .getRoot().getElement("/options/html");

        // Get body of message depending on user preferences
        MimeTree mimePartTree = srcFolder.getMimePartTree(uid);

        MimePart bodyPart = null;

        if (Boolean.valueOf(html.getAttribute("prefer")).booleanValue()) {
            bodyPart = mimePartTree.getFirstTextPart("html");
        } else {
            bodyPart = mimePartTree.getFirstTextPart("plain");
        }
        
        if (bodyPart == null) {
        	bodyHeader = new MimeHeader();
        	bodyStream = new ByteArrayInputStream(new byte[0]);
        } else {
        	bodyHeader = bodyPart.getHeader();
            bodyStream = srcFolder.getMimePartBodyStream(uid, bodyPart.getAddress());
        }
    }

    /**
     * Private utility to decode the message body with the proper charset
     *
     * @param bodyPart
     *            The body of the message
     * @return Decoded message body
     * @author Karl Peder Olesen (karlpeder), 20030601
     */
    private String getDecodedMessageBody()
        throws IOException {
        int encoding = bodyHeader.getContentTransferEncoding();

        switch (encoding) {
        case MimeHeader.QUOTED_PRINTABLE: {
            bodyStream = new QuotedPrintableDecoderInputStream(bodyStream);

            break;
        }

        case MimeHeader.BASE64: {
            bodyStream = new Base64DecoderInputStream(bodyStream);

            break;
        }
        }

        // First determine which charset to use
        if (charset == null) {
            try {
                // get charset from message
                charset = Charset.forName(bodyHeader.getContentParameter("charset"));
            } catch (Exception ex) {
                // decode using default charset
                charset = Charset.forName(System.getProperty("file.encoding"));
            }
        }

        bodyStream = new CharsetDecoderInputStream(bodyStream, charset);

        return StreamUtils.readInString(bodyStream).toString();
    }

    /**
     * Method for saving a message body as a html file. No headers are saved
     * with the message.
     *
     * @param header
     *            Message headers
     * @param bodyPart
     *            Body of message
     * @param attachments
     *            List of attachments as MimePart objects
     * @param inclAllHeaders
     *            If true all (except Content-Type and Mime-Version) headers
     *            are output. If false, only a small subset is included
     * @param file
     *            File to output to
     */
    private void saveMsgBodyAsHtml(boolean inclAllHeaders,
        File file) throws IOException {
        // decode message body with respect to charset
        String decodedBody = getDecodedMessageBody();

        String body;

        if (!bodyHeader.getMimeType().getSubtype().equals("html")) {
            try {
                // substitute special characters like: <,>,&,\t,\n
                body = HtmlParser.substituteSpecialCharacters(decodedBody);

                // parse for urls / email adr. and substite with HTML-code
                body = HtmlParser.substituteURL(body);
                body = HtmlParser.substituteEmailAddress(body);

                // mark quotings with special font
                body = DocumentParser.markQuotings(body);
            } catch (Exception e) {
                LOG.severe("Error parsing body: " +  e.getMessage());
                body = "<em>Error parsing body!!!</em>";
            }

            // encapsulate bodytext in html-code
            String css = getDefaultStyleSheet();
            body = "<html><head>" + NL + css + NL
                    + "<title>E-mail saved by Columba</title>" + NL
                    + "</head><body><p class=\"bodytext\">" + NL + body + NL
                    + "</p></body></html>";
        } else {
            // use body as is
            body = HtmlParser.validateHTMLString(decodedBody);
        }

        // headers
        String[][] headers = getHeadersToSave(inclAllHeaders);
        String msg = insertHtmlHeaderTable(body, headers);

        // save message
        try {
            DiskIO.saveStringInFile(file, msg);
            LOG.fine("Html msg saved as " + file.getAbsolutePath());
        } catch (IOException ioe) {
            LOG.severe("Error saving message to file: " + ioe.getMessage());
        }
    }

    /**
     * Defines and returns a default stylesheet for use when text messages are
     * saved as html. <br>This stylesheet should be the same as the one
     * defined in BodyTextViewer for use when displaying text messages.
     */
    private String getDefaultStyleSheet() {
        // read configuration from options.xml file
        XmlElement textFont = Config.getInstance().get("options").getElement("/options/gui/textfont");
        String name = textFont.getAttribute("name");
        String size = textFont.getAttribute("size");

        // create css-stylesheet string
        String css = "<style type=\"text/css\"><!-- .bodytext {font-family:\""
            + name + "\"; font-size:\"" + size + "pt; \"}"
            + ".quoting {color:#949494;}; --></style>";

        return css;
    }

    /**
     * Inserts a table with headers in a html message. The table is inserted
     * just after the body tag.
     *
     * @param body
     *            Original message body
     * @param headers
     *            Array with headers (keys and values)
     * @return message body with header table inserted
     */
    private String insertHtmlHeaderTable(String body, String[][] headers) {
        // create header table
        StringBuffer buf = new StringBuffer();
        String csskey = "border: 1px solid black; font-size: 8pt; font-weight: bold;";
        String cssval = "border: 1px solid black; font-size: 8pt;";
        buf.append(
            "<table style=\"background-color: #dddddd;\" cellspacing=\"0\">");
        buf.append(NL);

        for (int i = 0; i < headers[0].length; i++) {
            // process header value
            String val = headers[1][i];

            try {
                val = HtmlParser.substituteSpecialCharactersInHeaderfields(val);
                val = HtmlParser.substituteURL(val);
                val = HtmlParser.substituteEmailAddress(val);
            } catch (Exception e) {
                LOG.severe("Error parsing header value: " + e.getMessage());
            }

            buf.append("<tr><td style=\"" + csskey + "\">");
            buf.append(headers[0][i]);
            buf.append("</td>");
            buf.append("<td style=\"" + cssval + "\">");
            buf.append(val);
            buf.append("</td></tr>");
            buf.append(NL);
        }

        buf.append("</table>");
        buf.append("<br>" + NL);

        String headertbl = buf.toString();

        // insert into message right after <body...>
        int pos = body.toLowerCase().indexOf("<body");
        pos = body.indexOf(">", pos);
        pos++;

        String msg = body.substring(0, pos) + headertbl + body.substring(pos);

        return msg;
    }

    /**
     * Method for saving a message in a text file.
     *
     * @param header  Message headers
     * @param bodyPart  Body of message
     * @param attachments  List of attachments as MimePart objects
     * @param inclAllHeaders  If true all (except Content-Type and Mime-Version) headers
     *            are output. If false, only a small subset is included
     * @param file  File to output to
     */
    private void saveMsgBodyAsText(boolean inclAllHeaders,
        File file) throws IOException {
        //DocumentParser parser = new DocumentParser();
        // decode message body with respect to charset
        String decodedBody = getDecodedMessageBody();

        String body;

        if (bodyHeader.getMimeType().getSubtype().equals("html")) {
            // strip tags
            //body = parser.stripHTMLTags(decodedBody, true);
            //body = parser.restoreSpecialCharacters(body);
            body = HtmlParser.htmlToText(decodedBody);
        } else {
            // use body as is
            body = decodedBody;
        }

        // headers
        String[][] headers = getHeadersToSave(inclAllHeaders);
        StringBuffer buf = new StringBuffer();

        for (int i = 0; i < headers[0].length; i++) {
            buf.append(headers[0][i]);
            buf.append(": ");
            buf.append(headers[1][i]);
            buf.append(NL);
        }

        buf.append(NL);

        // message composed of headers and body
        String msg = buf.toString() + body;

        // save message
        DiskIO.saveStringInFile(file, msg);
        LOG.fine("Text msg saved as " + file.getAbsolutePath());
    }

    /**
     * Private utility to get headers to save. Headers are returned in a 2D
     * array, so [0][i] is key[i] and [1][i] is value[i].
     *
     * @param header  All message headers
     * @param attachments  Attachments, header lines with file names are added
     * @param inclAll  true if all headers except Content-Type and Mime-Version
     *            should be included
     * @return Array of headers to include when saving
     */
    private String[][] getHeadersToSave(boolean inclAll) {
        List keyList = new ArrayList();
        List valueList = new ArrayList();
        BasicHeader basicHeader = new BasicHeader(header);

        String from = (header.get("columba.from")).toString();
        String to = (basicHeader.getTo()[0]).toString();

        DateFormat df = DateFormat.getDateTimeInstance(DateFormat.LONG,
                DateFormat.MEDIUM);
        String date = df.format(basicHeader.getDate());

        String subject = (String) header.get("columba.subject");

        // loop over all headers
        Enumeration keys = header.getKeys();

        while (keys.hasMoreElements()) {
            String key = (String) keys.nextElement();

            if (key.equals("From")) {
            } else if (key.equals("To")) {
            } else if (key.equals("Subject")) {
            } else if (key.equals("Date")) {
                // ignore - columba.date is used instead
            } else if (key.startsWith("Content-")) {
                // ignore
            } else if (key.equals("Mime-Version")
                        || key.equals("MIME-Version")) {
                // ignore
            } else if (key.startsWith("columba")) {
                if (key.equals("columba.date")) {
                } else {
                    // ignore
                }
            } else {
                if (inclAll) {
                    // all headers should be included
                    keyList.add(key);
                    valueList.add((String) header.get(key));
                }
            }
        }

        // add from, to, date, subj so they are the last elements
        keyList.add(MailResourceLoader.getString("header", "from"));
        valueList.add(from);
        keyList.add(MailResourceLoader.getString("header", "to"));
        valueList.add(to);
        keyList.add(MailResourceLoader.getString("header", "date"));
        valueList.add(date);
        keyList.add(MailResourceLoader.getString("header", "subject"));
        valueList.add(subject);

        for (int i = 0; i < attachments.size(); i++) {
            String name = ((StreamableMimePart) attachments.get(i)).getHeader()
                           .getFileName();

            if (name != null) {
                keyList.add(MailResourceLoader.getString("header", "attachment"));
                valueList.add(name);
            }
        }

        // create array and return
        String[][] headerArray = new String[2][];
        headerArray[0] = new String[keyList.size()];
        headerArray[1] = new String[keyList.size()];

        for (int i = 0; i < keyList.size(); i++) {
            headerArray[0][i] = (String) keyList.get(i);
            headerArray[1][i] = (String) valueList.get(i);
        }

        return headerArray;
    }
}


/**
 * Represents a file filter selecting only a given type of files. <br>
 * Extension is used to recognize files. <br>Default file type is txt files.
 */
class ExtensionFileFilter extends FileFilter {
    /** extension to accept */
    private String extension = "txt";

    /** description of the file type */
    private String description = "Text files (*.txt)";

    /** Constructor setting the extension to accept and a type description */
    public ExtensionFileFilter(String extension, String description) {
        super();
        this.extension = extension;
        this.description = description;
    }

    /** Returns true if a given file is of the correct type */
    public boolean accept(File f) {
        if (f.isDirectory()) {
            return true;
        }

        // test on extension
        String ext = getFileExtension(f);

        if ((ext != null) && (this.extension.toLowerCase().equals(ext))) {
            return true;
        } else {
            return false;
        }
    }

    /**
     * Static method for extracting the extension of a filename
     *
     * @return f File to get extension for
     * @return extension or null if no extension exist
     */
    public static String getFileExtension(File f) {
        String ext = null;
        String s = f.getName();
        int i = s.lastIndexOf('.');

        if ((i > 0) && (i < (s.length() - 1))) {
            ext = s.substring(i + 1).toLowerCase();
        }

        return ext;
    }

    /** Returns the description of this filter / file type */
    public String getDescription() {
        return this.description;
    }

    /** Returns the extension used by this filter */
    public String getExtension() {
        return this.extension;
    }
}