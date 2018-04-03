DefaultSearchEngine engine = parentFolder.getSearchEngine();

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

import org.columba.core.command.DefaultCommandReference;
import org.columba.core.command.WorkerStatusController;

import org.columba.mail.command.FolderCommand;
import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.LocalFolder;
import org.columba.mail.folder.search.DefaultSearchEngine;
import org.columba.mail.main.MailInterface;

/**
 * Sync search engine.
 *
 *
 * @author fdietz
 */
public class SyncSearchEngineCommand extends FolderCommand {
    private LocalFolder parentFolder;

    public SyncSearchEngineCommand(DefaultCommandReference[] references) {
        super(references);
    }

    public void updateGUI() throws Exception {
        // update treemodel
        MailInterface.treeModel.nodeStructureChanged(parentFolder);
    }

    public void execute(WorkerStatusController worker)
        throws Exception {
        // get source folder
        parentFolder = (LocalFolder) ((FolderCommandReference) getReferences()[0]).getFolder();

        // resync search engine
        // -> this is only needed for Lucene right now
        DefaultSearchEngine engine = parentFolder.getSearchEngineInstance();
        engine.sync();
    }
}