Thread.sleep(3000);

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

import junit.framework.TestCase;

import org.columba.mail.command.FolderCommandReference;


/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 *
 */
public class DefaultProcessorTest extends TestCase {
    private CommandProcessor processor;
    
    int executedID;
    int finishedID;
    
    /**
 * Constructor for DefaultProcessorTest.
 * @param arg0
 */
    public DefaultProcessorTest(String arg0) {
        super(arg0);
    }

    public void testAddOp_PriorityOrdering() {
    	processor = new CommandProcessor(false);
    	
    	TestCommand command1 = new TestCommand(this, 1);
        command1.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command1);

        TestCommand command2 = new TestCommand(this, 2);
        command2.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command2);

        TestCommand command3 = new TestCommand(this, 3);
        command3.setPriority(Command.REALTIME_PRIORITY);
        processor.addOp(command3);

        TestCommand command4 = new TestCommand(this, 4);
        command4.setPriority(Command.DAEMON_PRIORITY);
        processor.addOp(command4);

        TestCommand command5 = new TestCommand(this, 5);
        command5.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command5);

        assertEquals(3, ((TestCommand)((OperationItem) processor.operationQueue.get(0)).getOperation()).getId());
        assertEquals(1, ((TestCommand)((OperationItem) processor.operationQueue.get(1)).getOperation()).getId());
        assertEquals(2, ((TestCommand)((OperationItem) processor.operationQueue.get(2)).getOperation()).getId());
        assertEquals(5, ((TestCommand)((OperationItem) processor.operationQueue.get(3)).getOperation()).getId());
        assertEquals(4, ((TestCommand)((OperationItem) processor.operationQueue.get(4)).getOperation()).getId());
    }

    public void testAddOp_PriorityOrderingWithSynchronized() {
    	processor = new CommandProcessor(false);
    	
        TestCommand command1 = new TestCommand(this, 1);
        command1.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command1, Command.FIRST_EXECUTION);

        TestCommand command2 = new TestCommand(this, 2);
        command2.setPriority(Command.NORMAL_PRIORITY);
        command2.setSynchronize(true);
        processor.addOp(command2, Command.FIRST_EXECUTION);

        TestCommand command3 = new TestCommand(this, 3);
        command3.setPriority(Command.REALTIME_PRIORITY);
        processor.addOp(command3, Command.FIRST_EXECUTION);

        TestCommand command4 = new TestCommand(this, 4);
        command4.setPriority(Command.DAEMON_PRIORITY);
        command4.setSynchronize(true);
        processor.addOp(command4, Command.FIRST_EXECUTION);

        TestCommand command5 = new TestCommand(this, 5);
        command5.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command5, Command.FIRST_EXECUTION);

        assertEquals(1, ((TestCommand)((OperationItem) processor.operationQueue.get(0)).getOperation()).getId());
        assertEquals(2, ((TestCommand)((OperationItem) processor.operationQueue.get(1)).getOperation()).getId());
        assertEquals(3, ((TestCommand)((OperationItem) processor.operationQueue.get(2)).getOperation()).getId());
        assertEquals(4, ((TestCommand)((OperationItem) processor.operationQueue.get(3)).getOperation()).getId());
        assertEquals(5, ((TestCommand)((OperationItem) processor.operationQueue.get(4)).getOperation()).getId());
    }


    public void testReserveForRealtime() throws Exception {
    	processor = new CommandProcessor(false);
	
    	// empty the worker list until one is left
    	while( processor.getWorker(Command.NORMAL_PRIORITY) != null );
    	
    	assertEquals( 1, processor.worker.size());
    	
    	assertTrue( processor.getWorker(Command.REALTIME_PRIORITY) != null );
    }
    
    public void testRunOne() throws Exception {
    	processor = new CommandProcessor(false);

    	TestCommand command1 = new TestCommand(this, 1);
        command1.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command1, Command.FIRST_EXECUTION);

        TestCommand command2 = new TestCommand(this, 2);
        command2.setPriority(Command.NORMAL_PRIORITY);
        command2.setSynchronize(true);
        processor.addOp(command2, Command.FIRST_EXECUTION);
    	
    	processor.startOperation();
    	assertEquals(CommandProcessor.MAX_WORKERS-1, processor.worker.size());
    	
    	Thread.sleep(1000);
    	
    	assertEquals( 1, executedID );
    	assertEquals(CommandProcessor.MAX_WORKERS, processor.worker.size());
    	
    	processor.startOperation();
    	assertEquals(CommandProcessor.MAX_WORKERS-1, processor.worker.size());
    	
    	Thread.sleep(1000);
    	
    	assertEquals( 2, executedID );
    	assertEquals(CommandProcessor.MAX_WORKERS, processor.worker.size());
    }
    
    public void testRunMultiple() throws Exception {
    	processor = new CommandProcessor(false);

    	TestCommand command1 = new TestCommand(this, 1);
        command1.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command1, Command.FIRST_EXECUTION);

        TestCommand command2 = new TestCommand(this, 2);
        command2.setPriority(Command.NORMAL_PRIORITY);
        command2.setSynchronize(true);
        processor.addOp(command2, Command.FIRST_EXECUTION);
    	
    	processor.startOperation();
    	processor.startOperation();
    	assertEquals(CommandProcessor.MAX_WORKERS-2, processor.worker.size());
    	
    	Thread.sleep(1000);
    	
    	assertEquals( 2, executedID );
    	assertEquals(CommandProcessor.MAX_WORKERS, processor.worker.size());
    }
    
    public void testRunMax() throws Exception {
    	processor = new CommandProcessor(false);

        processor.addOp( new TestCommand(this, 1));
        processor.addOp( new TestCommand(this, 2));
        processor.addOp( new TestCommand(this, 3));
        processor.addOp( new TestCommand(this, 4));
        processor.addOp( new TestCommand(this, 5));

    	
    	processor.startOperation();
    	processor.startOperation();
    	processor.startOperation();
    	processor.startOperation();
    	processor.startOperation();
    	assertEquals(1, processor.worker.size());
    	
    	Thread.sleep(1000);
    	
    	assertEquals( 1, processor.operationQueue.size() );
    	assertEquals(CommandProcessor.MAX_WORKERS, processor.worker.size());

    	processor.startOperation();
    	assertEquals(CommandProcessor.MAX_WORKERS - 1, processor.worker.size());
    	assertEquals( 0, processor.operationQueue.size()  );
    }

    public void testRunRealtime() throws Exception {
    	processor = new CommandProcessor(true);

        processor.addOp( new TestCommand(this, 1));
        processor.addOp( new TestCommand(this, 2));
        processor.addOp( new TestCommand(this, 3));
        processor.addOp( new TestCommand(this, 4, Command.REALTIME_PRIORITY));
        processor.addOp( new TestCommand(this, 5));
        processor.addOp( new TestCommand(this, 1));
        processor.addOp( new TestCommand(this, 2));
        processor.addOp( new TestCommand(this, 3));
        processor.addOp( new TestCommand(this, 4));
        processor.addOp( new TestCommand(this, 5, Command.REALTIME_PRIORITY));
        processor.addOp( new TestCommand(this, 1));
        processor.addOp( new TestCommand(this, 2));
        processor.addOp( new TestCommand(this, 3));
        processor.addOp( new TestCommand(this, 4));
        processor.addOp( new TestCommand(this, 5));

    	Thread.sleep(2000);

    	assertEquals( 0, processor.operationQueue.size()  );
    	assertEquals( CommandProcessor.MAX_WORKERS, processor.worker.size());
    }
    
}

class TestCommand extends Command {
	private int id;
	private DefaultProcessorTest test;
	
    public TestCommand(DefaultProcessorTest test, int id) {
    	this( test, id, Command.NORMAL_PRIORITY);
    }

    public TestCommand(DefaultProcessorTest test, int id, int priority ) {
        super(null, new FolderCommandReference[0]);
        this.id = id;
        this.test = test;
        this.priority = priority; 
    }

    public void updateGUI() {
    	test.finishedID = id;
    }

    public void execute(WorkerStatusController worker)
        throws Exception {
    	test.executedID = id;
    	Thread.sleep(50);
    }
	/**
	 * @return Returns the id.
	 */
	public int getId() {
		return id;
	}
	/**
	 * @param id The id to set.
	 */
	public void setId(int id) {
		this.id = id;
	}
}