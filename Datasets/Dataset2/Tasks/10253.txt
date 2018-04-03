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


/**
 * Default query engine used by {@link DefaultSearchEngine}.
 *
 * @author fdietz
 */
public class DummyQueryEngine implements QueryEngine {
    /**
 *
 * @see org.columba.mail.folder.search.QueryEngine#getCaps()
 */
    public String[] getCaps() {
        return new String[] {  };
    }

    /**
 * @see org.columba.mail.folder.search.QueryEngine#sync()
 */
    public void sync() throws Exception {
    }

    /**
 * @see org.columba.mail.folder.search.QueryEngine#queryEngine(org.columba.mail.filter.FilterRule)
 */
    public List queryEngine(FilterRule filter) throws Exception {
        return null;
    }

    /**
 * @see org.columba.mail.folder.search.QueryEngine#queryEngine(org.columba.mail.filter.FilterRule, java.lang.Object[])
 */
    public List queryEngine(FilterRule filter, Object[] uids)
        throws Exception {
        return null;
    }

    /**
 * @see org.columba.mail.folder.search.QueryEngine#messageAdded(org.columba.mail.message.ColumbaMessage)
 */
    public void messageAdded(Object uid) throws Exception {
    }

    /**
 * @see org.columba.mail.folder.search.QueryEngine#messageRemoved(java.lang.Object)
 */
    public void messageRemoved(Object uid) throws Exception {
    }

    /**
 * @see org.columba.mail.folder.search.QueryEngine#reset()
 */
    public void reset() throws Exception {
    }
}