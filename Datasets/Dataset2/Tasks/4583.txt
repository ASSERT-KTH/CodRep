import org.columba.core.gui.frame.FrameController;

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

import java.util.Vector;

import junit.framework.TestCase;

import org.columba.core.gui.FrameController;
import org.columba.core.logging.ColumbaLogger;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class UndoManagerTest extends TestCase {

	private DefaultProcessor processor;
	private UndoManager undoManager;
	private DefaultCommandReference[] nullReferences;
	
	/**
	 * Constructor for UndoManagerTest.
	 * @param arg0
	 */
	public UndoManagerTest(String arg0) {
		super(arg0);
	}

	/**
	 * @see TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		
		new ColumbaLogger();
		
		processor = new DefaultProcessor();
		undoManager = processor.getUndoManager();		
		
		nullReferences = new DefaultCommandReference[1];
		nullReferences[0] = new DefaultCommandReference();
	}

	/**
	 * @see TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();		
		processor = null;
	}

	/**
	 * Method testAddToUndo_TimeStampOrdering.
	 * Tests if the Commands are sorted in respect to
	 * increasing TimeStamps.
	 */
	public void testAddToUndo_TimeStampOrdering() {
		Command command1 = new TestUndoCommand(null,nullReferences);
		command1.setTimeStamp(0);
		undoManager.addToUndo(command1);

		Command command2 = new TestUndoCommand(null,nullReferences);
		command2.setTimeStamp(4);
		undoManager.addToUndo(command2);

		Command command3 = new TestUndoCommand(null,nullReferences);
		command3.setTimeStamp(2);
		undoManager.addToUndo(command3);

		Command command4 = new TestUndoCommand(null,nullReferences);
		command4.setTimeStamp(7);
		undoManager.addToUndo(command4);
		
		Vector result = undoManager.getUndoQueue();
		assertTrue( result.elementAt(0) == command1);
		assertTrue( result.elementAt(1) == command3);
		assertTrue( result.elementAt(2) == command2);
		assertTrue( result.elementAt(3) == command4);
	}

	public void testUndoLast() {
		Command command1 = new TestUndoCommand(null,nullReferences);
		command1.setTimeStamp(0);
		undoManager.addToUndo(command1);

		Command command2 = new TestUndoCommand(null,nullReferences);
		command2.setTimeStamp(4);
		undoManager.addToUndo(command2);

		Command command3 = new TestUndoCommand(null,nullReferences);
		command3.setTimeStamp(2);
		undoManager.addToUndo(command3);

		Command command4 = new TestUndoCommand(null,nullReferences);
		command4.setTimeStamp(7);
		undoManager.addToUndo(command4);

		undoManager.undoLast();
		undoManager.undoLast();
		undoManager.undoLast();
		undoManager.undoLast();
		
		Vector result = processor.getOperationQueue();
		assertTrue( ((OperationItem)result.elementAt(0)).operation == command4);
		assertTrue( ((OperationItem)result.elementAt(1)).operation == command2);
		assertTrue( ((OperationItem)result.elementAt(2)).operation == command3);
		assertTrue( ((OperationItem)result.elementAt(3)).operation == command1);		
	}

	public void testRedoLast() {
		Command command1 = new TestUndoCommand(null,nullReferences);
		command1.setTimeStamp(0);
		undoManager.addToUndo(command1);

		Command command2 = new TestUndoCommand(null,nullReferences);
		command2.setTimeStamp(4);
		undoManager.addToUndo(command2);

		Command command3 = new TestUndoCommand(null,nullReferences);
		command3.setTimeStamp(2);
		undoManager.addToUndo(command3);

		Command command4 = new TestUndoCommand(null,nullReferences);
		command4.setTimeStamp(7);
		undoManager.addToUndo(command4);

		undoManager.undoLast();
		undoManager.undoLast();
		undoManager.undoLast();
		undoManager.undoLast();
		
		Vector result = processor.getOperationQueue();
		result.clear();

		undoManager.redoLast();
		undoManager.redoLast();
		undoManager.redoLast();
		undoManager.redoLast();		
		
		assertTrue( ((OperationItem)result.elementAt(0)).operation == command1);
		assertTrue( ((OperationItem)result.elementAt(1)).operation == command3);
		assertTrue( ((OperationItem)result.elementAt(2)).operation == command2);
		assertTrue( ((OperationItem)result.elementAt(3)).operation == command4);		
	}


}

class TestUndoCommand extends Command {
	
	public TestUndoCommand( FrameController controller, DefaultCommandReference[] arguments ) {
		super( controller, arguments );
		
		commandType = Command.UNDOABLE_OPERATION;
	}

	public void updateGUI()
	{}

	public void execute( Worker worker ) throws Exception {
		
	}
	
	public void undo( Worker worker ) throws Exception {
		
	}

	public void redo( Worker worker ) throws Exception {
		
	}
}

class TestNoChangeCommand extends Command {
	
	public TestNoChangeCommand( FrameController controller, DefaultCommandReference[] arguments ) {
		super( controller, arguments );		
	}

	public void updateGUI()
	{}

	public void execute( Worker worker ) throws Exception {
		
	}	
}
