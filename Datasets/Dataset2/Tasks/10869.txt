public abstract void execute(WorkerStatusController worker) throws Exception;

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

import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.util.Lock;

import java.lang.reflect.Array;


/**
 * A Command uses the information provided from {@link DefaultCommandReference}
 * to execute itself.
 *
 * @author Timo Stich <tstich@users.sourceforge.net>
 */
public abstract class Command {
    /**
     * Command Types
    * Commands that can be undone, e.g. move message
    * line for constructor:
    * commandType = Command.UNDOABLE_OPERATION;
    */
    public static final int UNDOABLE_OPERATION = 0;

    /**
     * Commands that can not be undone but previous commands
    * can be undone, e.g. view message (default)
    * line for constructor:
    * commandType = Command.NORMAL_OPERATION;
    */
    public static final int NORMAL_OPERATION = 1;

    /**
     * Commands that can not be undone and previous commands
    * cannot be undone anymore, e.g. delete message from trash
    * line for constructor:
    * commandType = Command.NO_UNDO_OPERATION;
    */
    public static final int NO_UNDO_OPERATION = 2;

    /**
     * Priorities:
    * Commands that are started by an automated process, e.g. auto-check
    * for new messages
    */
    public static final int DAEMON_PRIORITY = -10;

    /**
     * Normal priority for e.g. copying (default)
     */
    public static final int NORMAL_PRIORITY = 0;

    /** 
     * Commands that the user waits for to finish, e.g. view message
     */
    public static final int REALTIME_PRIORITY = 10;

    /**
     * Never Use this!! - internally highest priority
     */ 
    public static final int DEFINETLY_NEXT_OPERATION_PRIORITY = 20;

    /**
     * Never use these!!! - for internal state control only
     */
    
    public static final int FIRST_EXECUTION = 0;
    public static final int UNDO = 1;
    public static final int REDO = 2;
    
    protected int priority;
    protected int commandType;
    protected boolean synchronize;
    protected int timeStamp;
    protected Lock[] folderLocks;
    private DefaultCommandReference[] references;
    private DefaultCommandReference[] undoReferences;
    protected FrameMediator frameMediator;

    public Command(DefaultCommandReference[] references) {
        this.references = references;

        commandType = NORMAL_OPERATION;
        priority = NORMAL_PRIORITY;
    }

    public Command(FrameMediator frameMediator,
        DefaultCommandReference[] references) {
        this.references = references;
        this.frameMediator = frameMediator;

        commandType = NORMAL_OPERATION;
        priority = NORMAL_PRIORITY;
    }

    public void process(Worker worker, int operationMode)
        throws Exception {
        setTimeStamp(worker.getTimeStamp());

        switch (operationMode) {
        case FIRST_EXECUTION:
            execute(worker);

            break;

        case UNDO:
            undo(worker);

            break;

        case REDO:
            redo(worker);

            break;
        }
    }

    public void updateGUI() throws Exception {
    }

    /**
     * Command must implement this method
     * Executes the Command when run the first time
     *
     * @param worker
     * @throws Exception
     */
    public abstract void execute(Worker worker) throws Exception;

    /**
     * Command must implement this method
     * Undos the command after command was executed or redone.
     *
     * @param worker
     * @throws Exception
     */
    public void undo(Worker worker) throws Exception {
    }

    /**
     * Command must implement this method
     * Redos the command after command was undone.
     *
     * @param worker
     * @throws Exception
     */
    public void redo(Worker worker) throws Exception {
    }

    public boolean canBeProcessed(int operationMode) {
        DefaultCommandReference[] references = getReferences(operationMode);
        int size = Array.getLength(references);

        boolean success = true;

        for (int i = 0; (i < size) && success; i++) {
            if (references[i] != null) {
                success &= references[i].tryToGetLock(this);
            }
        }

        if (!success) {
            releaseAllFolderLocks(operationMode);
        }

        return success;
    }

    public void releaseAllFolderLocks(int operationMode) {
        DefaultCommandReference[] references = getReferences(operationMode);
        int size = Array.getLength(references);

        for (int i = 0; i < size; i++) {
            if (references[i] != null) {
                references[i].releaseLock(this);
            }
        }
    }

    /************* Methods for interacting with the Operator *************/
    public DefaultCommandReference[] getReferences(int operationMode) {
        if (operationMode == UNDO) {
            return getUndoReferences();
        } else {
            return getReferences();
        }
    }

    public int getCommandType() {
        return commandType;
    }

    public int getPriority() {
        return priority;
    }

    public void incPriority() {
        priority++;
    }

    public boolean isSynchronize() {
        return synchronize;
    }

    public void setSynchronize(boolean synchronize) {
        this.synchronize = synchronize;
    }

    public void setPriority(int priority) {
        this.priority = priority;
    }

    /**
     * Sets the undoReferences.
     * @param undoReferences The undoReferences to set
     */
    public void setUndoReferences(DefaultCommandReference[] undoReferences) {
        this.undoReferences = undoReferences;
    }

    /**
     * Returns the timeStamp.
     * @return int
     */
    public int getTimeStamp() {
        return timeStamp;
    }

    /**
     * Sets the timeStamp.This method is for testing only!
     * @param timeStamp The timeStamp to set
     */
    public void setTimeStamp(int timeStamp) {
        this.timeStamp = timeStamp;
    }

    /**
     * Returns the references.
     * @return DefaultCommandReference[]
     */
    public DefaultCommandReference[] getReferences() {
        return references;
    }

    /**
     * Returns the undoReferences.
     * @return DefaultCommandReference[]
     */
    public DefaultCommandReference[] getUndoReferences() {
        return undoReferences;
    }

    public void finish() throws Exception {
        updateGUI();
    }

    /**
     * Returns the frameMediator.
     * @return FrameController
     */
    public FrameMediator getFrameMediator() {
        return frameMediator;
    }
}