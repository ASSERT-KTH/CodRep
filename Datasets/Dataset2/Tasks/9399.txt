public void execute(WorkerStatusController worker) throws Exception {

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
package org.columba.core.command;

import org.columba.mail.command.FolderCommandReference;
import org.columba.mail.folder.FolderTreeNode;

import java.util.Iterator;
import java.util.List;
import java.util.Vector;


/**
 * Special type of {@link Command} which is used for a set
 * of different commands.
 * <p>
 * This is used by {@link FilterAction} and {@link VirtualFolder}
 * to execute commands, which work on a set of references.
 *
 * @author tstich, fdietz
 */
public class CompoundCommand extends Command {
    protected List commandList;
    protected List referenceList;

    /**
     * Constructor for CompoundCommand.
     * Caution : Never use this command with Virtual Folders!
     * @param frameMediator
     * @param references
     */
    public CompoundCommand() {
        super(null, null);
        commandList = new Vector();
        referenceList = new Vector();

        priority = Command.NORMAL_PRIORITY;
        commandType = Command.NORMAL_OPERATION;
    }

    public void add(Command c) {
        commandList.add(c);

        FolderCommandReference[] commandRefs = (FolderCommandReference[]) c.getReferences();

        for (int i = 0; i < commandRefs.length; i++) {
            if (!referenceList.contains(commandRefs[i].getFolder())) {
                referenceList.add(commandRefs[i].getFolder());
            }
        }
    }

    public void finish() throws Exception {
        Command c;

        for (Iterator it = commandList.iterator(); it.hasNext();) {
            c = (Command) it.next();

            //		for (int i = 0; i < commandList.size(); i++) {
            //			c = (Command) commandList.get(i);
            c.finish();
        }
    }

    /**
     * @see org.columba.core.command.Command#execute(Worker)
     */
    public void execute(Worker worker) throws Exception {
        Command c;

        for (Iterator it = commandList.iterator(); it.hasNext();) {
            c = (Command) it.next();

            //		for (int i = 0; i < commandList.size(); i++) {
            //			c = (Command) commandList.get(i);
            c.execute(worker);
        }
    }

    //	/**
    //	 * @see org.columba.core.command.Command#canBeProcessed(int)
    //	 */
    //	public boolean canBeProcessed(int operationMode) {
    //
    //		boolean result = true;
    //		Command c;
    //		for (int i = 0; i < commandList.size(); i++) {
    //			c = (Command) commandList.get(i);
    //			result &= c.canBeProcessed(operationMode);
    //		}
    //
    //		if (!result) {
    //
    //			releaseAllFolderLocks(operationMode);
    //		}
    //
    //		return result;
    //	}
    //
    //	/**
    //	 * @see org.columba.core.command.Command#releaseAllFolderLocks(int)
    //	 */
    //	public void releaseAllFolderLocks(int operationMode) {
    //		Command c;
    //		for (int i = 0; i < commandList.size(); i++) {
    //			c = (Command) commandList.get(i);
    //			c.releaseAllFolderLocks(operationMode);
    //		}
    //	}

    /**
     * @see org.columba.core.command.Command#getReferences()
     */
    public DefaultCommandReference[] getReferences() {
        FolderCommandReference[] refs = new FolderCommandReference[referenceList.size()];

        for (int i = 0; i < referenceList.size(); i++) {
            refs[i] = new FolderCommandReference((FolderTreeNode) referenceList.get(
                        i));
        }

        return refs;
    }
}