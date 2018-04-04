public FolderEvent(MessageFolder source, Object changes) {

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

package org.columba.mail.folder;

import java.util.EventObject;

/**
 * Passed to listeners to notify them of changes.
 */
public class FolderEvent extends EventObject {
    protected Object changes;
    
    /**
     * Creates a new event for the given folder.
     */
    public FolderEvent(Folder source, Object changes) {
        super(source);
        this.changes = changes;
    }
    
    /**
     * Encapsulates the changes that have occured.
     */
    public Object getChanges() {
        return changes;
    }
}