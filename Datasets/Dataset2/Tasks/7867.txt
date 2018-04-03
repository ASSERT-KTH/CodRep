//setDisplayText("");

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

import java.util.List;
import java.util.Vector;

import org.columba.core.gui.frame.AbstractFrameController;
import org.columba.core.gui.statusbar.event.WorkerStatusChangeListener;
import org.columba.core.gui.statusbar.event.WorkerStatusChangedEvent;
import org.columba.core.gui.util.ExceptionDialog;
import org.columba.core.logging.ColumbaLogger;
import org.columba.core.util.SwingWorker;

public class Worker extends SwingWorker implements WorkerStatusController {
	protected Command op;
	protected int operationMode;
	protected DefaultProcessor boss;

	protected String displayText;
	protected int progressBarMax;
	protected int progressBarValue;

	protected boolean cancelled;

	protected List workerStatusChangeListeners;

	private int timeStamp;

	public Worker(DefaultProcessor parent) {
		super();
		
		this.boss = parent;

		displayText = "";
		progressBarValue = 0;
		progressBarMax = 0;

		cancelled = false;

		workerStatusChangeListeners = new Vector();
	}

	public void process(Command op, int operationMode, int timeStamp) {
		this.op = op;
		this.operationMode = operationMode;
		this.timeStamp = timeStamp;
	}

	public int getPriority() {
		return op.getPriority();
	}

	private void returnLocks(int opMode) {
		op.releaseAllFolderLocks(operationMode);
	}

	/*
	private void setWorkerStatusController() {
		FolderController[] controller = op.getFolderLocks();
		int size = Array.getLength(controller);
		
		for( int i=0; i<size; i++ ) {
			controller[i].setWorkerStatusController(this);
		}		
	}	
	*/

	public Object construct() {
		//setWorkerStatusController();

		try {
			op.process(this, operationMode);
			if (!cancelled() && (operationMode == Command.FIRST_EXECUTION))
				boss.getUndoManager().addToUndo(op);
		} catch (CommandCancelledException e) {
                        ColumbaLogger.log.debug("Command cancelled");
		} catch (Exception e) {
			// Must create a ExceptionProcessor
			e.printStackTrace();

			ExceptionDialog dialog = new ExceptionDialog();
			dialog.showDialog(e);
		}

		returnLocks(operationMode);

		return null;
	}

	public void finished() {
		try {
			op.finish();

			setDisplayText("");
		} catch (Exception e) {
			// Must create a ExceptionProcessor
			e.printStackTrace();
		}

		unregister();
		boss.operationFinished(op, this);
	}

	public void register(TaskManager t) {
		this.taskManager = t;

		taskManager.register(this);
	}

	public void unregister() {
		taskManager.unregister(threadVar);
		WorkerStatusChangedEvent e = new WorkerStatusChangedEvent();
		e.setType(WorkerStatusChangedEvent.FINISHED);
		fireWorkerStatusChanged(e);
		workerStatusChangeListeners.clear();
		displayText = "";
		progressBarValue = 0;
		progressBarMax = 0;
	}

	public void setProgressBarMaximum(int max) {
		WorkerStatusChangedEvent e = new WorkerStatusChangedEvent();
		e.setType(WorkerStatusChangedEvent.PROGRESSBAR_MAX_CHANGED);
		e.setOldValue(new Integer(progressBarMax));

		progressBarMax = max;

		e.setNewValue(new Integer(progressBarMax));
		fireWorkerStatusChanged(e);
	}

	public void setProgressBarValue(int value) {
		WorkerStatusChangedEvent e = new WorkerStatusChangedEvent();
		e.setType(WorkerStatusChangedEvent.PROGRESSBAR_VALUE_CHANGED);
		e.setOldValue(new Integer(progressBarValue));

		progressBarValue = value;

		e.setNewValue(new Integer(progressBarValue));
		fireWorkerStatusChanged(e);
	}
	
	public int getProgessBarMaximum() {
		return progressBarMax;
	}

	public int getProgressBarValue() {
		return progressBarValue;
	}

	public String getDisplayText() {
		return displayText;
	}

	public void setDisplayText(String displayText) {
		WorkerStatusChangedEvent e = new WorkerStatusChangedEvent();
		e.setType(WorkerStatusChangedEvent.DISPLAY_TEXT_CHANGED);
		e.setOldValue(displayText);

		this.displayText = displayText;

		e.setNewValue(displayText);
		fireWorkerStatusChanged(e);
	}

	public void addWorkerStatusChangeListener(WorkerStatusChangeListener l) {
		workerStatusChangeListeners.add(l);
	}

	public void removeWorkerStatusChangeListener(WorkerStatusChangeListener l) {
		workerStatusChangeListeners.remove(l);
	}

	protected void fireWorkerStatusChanged(WorkerStatusChangedEvent e) {
		// if we use the commented statement, the exceptio java.util.ConcurrentModificationException
		// is thrown ... is the worker not thread save?
		// for (Iterator it = workerStatusChangeListeners.iterator(); it.hasNext();) {
			// ((WorkerStatusChangeListener) it.next()).workerStatusChanged(e);
		 for (int i = 0; i < workerStatusChangeListeners.size(); i++) {
			 (
				 (WorkerStatusChangeListener) workerStatusChangeListeners.get(
					 i)).workerStatusChanged(
				 e);
		}
	}

	public void cancel() {
		cancelled = true;
	}

	public boolean cancelled() {
		return cancelled;
	}

	/**
	 * Returns the timeStamp.
	 * @return int
	 */
	public int getTimeStamp() {
		return timeStamp;
	}

	public AbstractFrameController getFrameController() {
		return op.getFrameController();
	}
}