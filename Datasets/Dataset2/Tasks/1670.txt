import org.columba.api.command.ICommandReference;

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

import org.columba.core.command.ICommandReference;
import org.columba.mail.composer.MessageBuilderHelper;
import org.columba.mail.config.AccountItem;
import org.columba.mail.folder.AbstractMessageFolder;
import org.columba.ristretto.message.Address;
import org.columba.ristretto.message.BasicHeader;
import org.columba.ristretto.message.Header;


/**
 * Reply to mailinglist.
 * <p>
 * Uses the X-BeenThere: headerfield to determine the To: address
 *
 * @author fdizet
 */
public class ReplyToMailingListCommand extends ReplyCommand {
    protected final String[] headerfields = new String[] {
            "Subject", "From", "To", "Reply-To", "Message-ID", "In-Reply-To",
            "References", "X-Beenthere", "X-BeenThere"
        };

    /**
     * Constructor for ReplyToMailingListCommand.
     *
     * @param frameMediator
     * @param references
     */
    public ReplyToMailingListCommand(ICommandReference reference) {
        super(reference);
    }

    protected void initHeader(AbstractMessageFolder folder, Object[] uids)
        throws Exception {
        // get headerfields
        Header header = folder.getHeaderFields(uids[0], headerfields);

        BasicHeader rfcHeader = new BasicHeader(header);

        // set subject
        model.setSubject(MessageBuilderHelper.createReplySubject(
                rfcHeader.getSubject()));

        // Use reply-to field if given, else use from
        Address to = rfcHeader.getBeenThere();

        if (to == null) {
            Address[] replyTo = rfcHeader.getReplyTo();

            if (replyTo.length > 0) {
                to = replyTo[0];
            }
        }

        if (to == null) {
            to = rfcHeader.getFrom();
        }

        MessageBuilderHelper.addAddressesToAddressbook(new Address[] { to });
        model.setTo(new Address[] { to });

        // create In-Reply-To:, References: headerfields
        MessageBuilderHelper.createMailingListHeaderItems(header, model);

        // select the account this mail was received from
        Integer accountUid = (Integer) folder.getAttribute(uids[0],
                "columba.accountuid");
        AccountItem accountItem = MessageBuilderHelper.getAccountItem(accountUid);
        model.setAccountItem(accountItem);
    }
}