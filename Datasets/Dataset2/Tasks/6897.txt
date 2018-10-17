"In-Reply-To", "References", "X-Beenthere", "X-BeenThere"

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.composer.command;

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.Worker;
import org.columba.core.xml.XmlElement;

import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.composer.MessageBuilderHelper;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.MailConfig;
import org.columba.mail.folder.Folder;
import org.columba.mail.gui.composer.ComposerController;
import org.columba.mail.gui.composer.ComposerModel;
import org.columba.mail.message.ColumbaMessage;

import org.columba.ristretto.coder.EncodedWord;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.LocalMimePart;
import org.columba.ristretto.message.MimeHeader;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.message.io.CharSequenceSource;


/**
 * Reply to mailinglist.
 * <p>
 * Uses the X-BeenThere: headerfield to determine the To: address
 *
 * @author fdizet
 */
public class ReplyToMailingListCommand extends FolderCommand {
    protected ComposerController controller;
    protected ComposerModel model;

    /**
     * Constructor for ReplyToMailingListCommand.
     *
     * @param frameMediator
     * @param references
     */
    public ReplyToMailingListCommand(DefaultCommandReference[] references) {
        super(references);
    }

    public void updateGUI() throws Exception {
        // open composer frame
        controller = new ComposerController();

        // apply model
        controller.setComposerModel(model);

        // model->view update
        controller.updateComponents(true);
    }

    public void execute(Worker worker) throws Exception {
        // get selected folder
        Folder folder = (Folder) ((FolderCommandReference) getReferences()[0]).getFolder();

        // get first selected message
        Object[] uids = ((FolderCommandReference) getReferences()[0]).getUids();

        // create new message object
        ColumbaMessage message = new ColumbaMessage();

        //		get headerfields
        Header header = folder.getHeaderFields(uids[0],
                new String[] {
                    "Subject", "From", "To", "Reply-To", "Message-ID",
                    "In-Reply-To", "References", "X-BeenThere"
                });
        message.setHeader(header);

        // get mimeparts
        MimeTree mimePartTree = folder.getMimePartTree(uids[0]);
        message.setMimePartTree(mimePartTree);

        XmlElement html = MailConfig.getMainFrameOptionsConfig().getRoot()
                                    .getElement("/options/html");

        // Which Bodypart shall be shown? (html/plain)
        MimePart bodyPart = null;

        if (Boolean.valueOf(html.getAttribute("prefer")).booleanValue()) {
            bodyPart = mimePartTree.getFirstTextPart("html");
        } else {
            bodyPart = mimePartTree.getFirstTextPart("plain");
        }

        if (bodyPart == null) {
            bodyPart = new LocalMimePart(new MimeHeader(header));
            ((LocalMimePart) bodyPart).setBody(new CharSequenceSource(
                    "<No Message-Text>"));
        } else {
            bodyPart = folder.getMimePart(uids[0], bodyPart.getAddress());
        }

        message.setBodyPart(bodyPart);

        // create composer model
        model = new ComposerModel();

        // set character set
        bodyPart = message.getBodyPart();

        if (bodyPart != null) {
            String charset = bodyPart.getHeader().getContentParameter("charset");

            if (charset != null) {
                model.setCharsetName(charset);
            }
        }

        // set subject
        model.setSubject(MessageBuilderHelper.createReplySubject(header.get(
                    "Subject")));

        // decode To: headerfield
        String to = MessageBuilderHelper.createToMailinglist(header);

        if (to != null) {
            to = EncodedWord.decode(to).toString();
            model.setTo(to);

            // TODO: automatically add sender to addressbook
            // -> split to-headerfield, there can be more than only one
            // recipients!
            MessageBuilderHelper.addSenderToAddressbook(to);
        }

        // create In-Reply-To:, References: headerfields
        MessageBuilderHelper.createMailingListHeaderItems(header, model);

        // try to good guess the correct account
        Integer accountUid = null;

        if (folder.getAttribute(uids[0], "columba.accountuid") != null) {
            accountUid = (Integer) folder.getAttribute(uids[0],
                    "columba.accountuid");
        }

        String host = null;

        if (folder.getAttribute(uids[0], "columba.host") != null) {
            host = (String) folder.getAttribute(uids[0], "columba.host");
        }

        String address = header.get("To");
        AccountItem accountItem = MessageBuilderHelper.getAccountItem(accountUid,
                host, address);
        model.setAccountItem(accountItem);

        /*
         * original message is sent "inline" - model is setup according to the
         * type of the original message. NB: If the original message was plain
         * text, the message type seen here is always text. If the original
         * message contained html, the message type seen here will depend on
         * the "prefer html" option.
         */
        MimeHeader bodyHeader = message.getBodyPart().getHeader();

        if (bodyHeader.getMimeType().getSubtype().equals("html")) {
            model.setHtml(true);
        } else {
            model.setHtml(false);
        }

        // prepend "> " to every line of the bodytext
        String bodyText = MessageBuilderHelper.createQuotedBodyText(message.getBodyPart(),
                model.isHtml());

        if (bodyText == null) {
            bodyText = "[Error parsing bodytext]";
        }

        model.setBodyText(bodyText);
    }
}