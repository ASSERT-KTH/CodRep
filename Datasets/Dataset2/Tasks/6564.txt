import org.columba.core.filter.FilterRule;

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

package org.columba.mail.folder.search;

import java.util.List;

import org.columba.mail.filter.FilterRule;
import org.columba.mail.folder.imap.IMAPFolder;

/**
 * Performes search requests on the IMAP server-side.
 * <p>
 * Note, that some search-requests are executed using the local
 * caching mechanism.
 * 
 * @see org.columba.mail.imap.SearchRequestBuilder
 * @see org.columba.mail.folder.search.DefaultSearchEngine
 * 
 * @author fdietz
 */
public class IMAPQueryEngine implements QueryEngine {
    /**
 * list of supported search requests
 */

    //  This list is reduced, because most search requests can be 
    // answered anyway, using locally cached headerfields
    private static final String[] CAPABILITY_LIST = {
        "Body", "Subject", "From", "To", "Cc", "Bcc", "Custom Headerfield",
        "Date", "Size"
    };
    private IMAPFolder folder;

    /**
 * Contructor
 *
 * @param f                IMAPFolder
 */
    public IMAPQueryEngine(IMAPFolder f) {
        this.folder = f;
    }

    public String[] getCaps() {
        return CAPABILITY_LIST;
    }

    public void sync() throws Exception {
        // method is not needed by IMAP
    }

    public List queryEngine(FilterRule filter) throws Exception {
        // pass the work to IMAPStore
        return folder.getServer().search(filter, folder);
    }

    public List queryEngine(FilterRule filter, Object[] uids)
        throws Exception {
        // pass the work to IMAPStore
        return folder.getServer().search(uids, filter, folder);
    }

    public void messageAdded(Object uid) throws Exception {
        // method is not needed by IMAP
    }

    public void messageRemoved(Object uid) throws Exception {
        // method is not needed by IMAP
    }

    public void reset() throws Exception {
        // method is not needed by IMAP
    }
}