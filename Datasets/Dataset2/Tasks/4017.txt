result = flags.get(Flags.DELETED);

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
package org.columba.mail.filter.plugins;

import org.columba.mail.filter.FilterCriteria;
import org.columba.mail.folder.MessageFolder;

import org.columba.ristretto.message.Flags;


/**
 * Search for a certain flag state.
 * <p>
 * Example: Message is read/unread, Marked as Spam/Not Spam
 *
 * @author fdietz
 */
public class FlagsFilter extends AbstractFilter {
    private String criteria;
    private String pattern;

    /**
 * Constructor for FlagsFilter.
 */
    public FlagsFilter() {
        super();
    }

    /**
 * @see org.columba.mail.filter.plugins.AbstractFilter#process(java.lang.Object,
 *      org.columba.mail.folder.Folder, java.lang.Object,
 *      org.columba.core.command.WorkerStatusController)
 */
    public boolean process(MessageFolder folder, Object uid) throws Exception {
        boolean result = false;

        String headerField = pattern;
        int condition = FilterCriteria.getCriteria(criteria);

        String searchHeaderField = null;

        Flags flags = folder.getFlags(uid);

        if (headerField.equalsIgnoreCase("Answered")) {
            result = flags.get(Flags.ANSWERED);
        } else if (headerField.equalsIgnoreCase("Deleted")) {
            result = flags.get(Flags.EXPUNGED);
        } else if (headerField.equalsIgnoreCase("Flagged")) {
            result = flags.get(Flags.FLAGGED);
        } else if (headerField.equalsIgnoreCase("Recent")) {
            result = flags.get(Flags.RECENT);
        } else if (headerField.equalsIgnoreCase("Draft")) {
            result = flags.get(Flags.DRAFT);
        } else if (headerField.equalsIgnoreCase("Seen")) {
            result = flags.get(Flags.SEEN);
        } else if (headerField.equalsIgnoreCase("Spam")) {
            result = ((Boolean) folder.getAttribute(uid, "columba.spam")).booleanValue();
        }

        if (condition == FilterCriteria.IS) {
            return result;
        } else {
            return !result;
        }
    }

    /**
 * @see org.columba.mail.filter.plugins.AbstractFilter#setUp(org.columba.mail.filter.FilterCriteria)
 */
    public void setUp(FilterCriteria f) {
        //  is/is not
        criteria = f.get("criteria");

        // string to search
        pattern = f.get("pattern");
    }
}