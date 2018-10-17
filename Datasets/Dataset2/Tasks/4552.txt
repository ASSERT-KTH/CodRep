public void updateGUI()

package org.columba.core.command;

import java.util.Vector;

import junit.framework.TestCase;

import org.columba.core.gui.FrameController;
import org.columba.core.logging.ColumbaLogger;

/**
 * @author Timo Stich (tstich@users.sourceforge.net)
 * 
 */
public class DefaultProcessorTest extends TestCase {

	private DefaultProcessor processor;

	/**
	 * Constructor for DefaultProcessorTest.
	 * @param arg0
	 */
	public DefaultProcessorTest(String arg0) {
		super(arg0);
	}

	/**
	 * @see TestCase#setUp()
	 */
	protected void setUp() throws Exception {
		super.setUp();
		
		new ColumbaLogger();
		
		processor = new DefaultProcessor();
	}

	/**
	 * @see TestCase#tearDown()
	 */
	protected void tearDown() throws Exception {
		super.tearDown();
	}

	public void testAddOp_PriorityOrdering() {
		TestCommand command1 = new TestCommand( null, null );
		command1.setPriority(Command.NORMAL_PRIORITY);
		processor.addOp(command1,Command.FIRST_EXECUTION);
				
		TestCommand command2 = new TestCommand( null, null );
		command2.setPriority(Command.NORMAL_PRIORITY);
		processor.addOp(command2,Command.FIRST_EXECUTION);

		TestCommand command3 = new TestCommand( null, null );
		command3.setPriority(Command.REALTIME_PRIORITY);
		processor.addOp(command3,Command.FIRST_EXECUTION);

		TestCommand command4 = new TestCommand( null, null );
		command4.setPriority(Command.DAEMON_PRIORITY);
		processor.addOp(command4,Command.FIRST_EXECUTION);

		TestCommand command5 = new TestCommand( null, null );
		command5.setPriority(Command.NORMAL_PRIORITY);
		processor.addOp(command5,Command.FIRST_EXECUTION);

		Vector result = processor.getOperationQueue();

		assertTrue( ((OperationItem)result.elementAt(0)).operation == command3);
		assertTrue( ((OperationItem)result.elementAt(1)).operation == command1);
		assertTrue( ((OperationItem)result.elementAt(2)).operation == command2);
		assertTrue( ((OperationItem)result.elementAt(3)).operation == command5);		
		assertTrue( ((OperationItem)result.elementAt(4)).operation == command4);		
	}

	public void testAddOp_PriorityOrderingWithSynchronized() {
		TestCommand command1 = new TestCommand( null, null );
		command1.setPriority(Command.NORMAL_PRIORITY);
		processor.addOp(command1,Command.FIRST_EXECUTION);
				
		TestCommand command2 = new TestCommand( null, null );
		command2.setPriority(Command.NORMAL_PRIORITY);
		command2.setSynchronize(true);
		processor.addOp(command2,Command.FIRST_EXECUTION);

		TestCommand command3 = new TestCommand( null, null );
		command3.setPriority(Command.REALTIME_PRIORITY);
		command3.setSynchronize(true);
		processor.addOp(command3,Command.FIRST_EXECUTION);

		TestCommand command4 = new TestCommand( null, null );
		command4.setPriority(Command.DAEMON_PRIORITY);
		command4.setSynchronize(true);
		processor.addOp(command4,Command.FIRST_EXECUTION);

		TestCommand command5 = new TestCommand( null, null );
		command5.setPriority(Command.NORMAL_PRIORITY);
		processor.addOp(command5,Command.FIRST_EXECUTION);

		Vector result = processor.getOperationQueue();

		assertTrue( ((OperationItem)result.elementAt(0)).operation == command1);
		assertTrue( ((OperationItem)result.elementAt(1)).operation == command2);
		assertTrue( ((OperationItem)result.elementAt(2)).operation == command3);
		assertTrue( ((OperationItem)result.elementAt(3)).operation == command4);		
		assertTrue( ((OperationItem)result.elementAt(4)).operation == command5);		
	}


}

class TestCommand extends Command {
	
	public TestCommand( FrameController controller, DefaultCommandReference[] arguments ) {
		super( controller, arguments );		
	}

	public void updateSelectedGUI()
	{}

	public void execute( Worker worker ) throws Exception {
		
	}	
}