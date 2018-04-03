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

import junit.framework.TestCase;

import org.columba.core.gui.frame.FrameMediator;
import org.columba.core.logging.ColumbaLogger;

import java.util.List;


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

        processor = new DefaultProcessor();
    }

    /**
     * @see TestCase#tearDown()
     */
    protected void tearDown() throws Exception {
        super.tearDown();
    }

    public void testAddOp_PriorityOrdering() {
        TestCommand command1 = new TestCommand(null, null);
        command1.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command1, Command.FIRST_EXECUTION);

        TestCommand command2 = new TestCommand(null, null);
        command2.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command2, Command.FIRST_EXECUTION);

        TestCommand command3 = new TestCommand(null, null);
        command3.setPriority(Command.REALTIME_PRIORITY);
        processor.addOp(command3, Command.FIRST_EXECUTION);

        TestCommand command4 = new TestCommand(null, null);
        command4.setPriority(Command.DAEMON_PRIORITY);
        processor.addOp(command4, Command.FIRST_EXECUTION);

        TestCommand command5 = new TestCommand(null, null);
        command5.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command5, Command.FIRST_EXECUTION);

        List result = processor.getOperationQueue();

        assertTrue(((OperationItem) result.get(0)).getOperation() == command3);
        assertTrue(((OperationItem) result.get(1)).getOperation() == command1);
        assertTrue(((OperationItem) result.get(2)).getOperation() == command2);
        assertTrue(((OperationItem) result.get(3)).getOperation() == command5);
        assertTrue(((OperationItem) result.get(4)).getOperation() == command4);
    }

    public void testAddOp_PriorityOrderingWithSynchronized() {
        TestCommand command1 = new TestCommand(null, null);
        command1.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command1, Command.FIRST_EXECUTION);

        TestCommand command2 = new TestCommand(null, null);
        command2.setPriority(Command.NORMAL_PRIORITY);
        command2.setSynchronize(true);
        processor.addOp(command2, Command.FIRST_EXECUTION);

        TestCommand command3 = new TestCommand(null, null);
        command3.setPriority(Command.REALTIME_PRIORITY);
        command3.setSynchronize(true);
        processor.addOp(command3, Command.FIRST_EXECUTION);

        TestCommand command4 = new TestCommand(null, null);
        command4.setPriority(Command.DAEMON_PRIORITY);
        command4.setSynchronize(true);
        processor.addOp(command4, Command.FIRST_EXECUTION);

        TestCommand command5 = new TestCommand(null, null);
        command5.setPriority(Command.NORMAL_PRIORITY);
        processor.addOp(command5, Command.FIRST_EXECUTION);

        List result = processor.getOperationQueue();

        assertTrue(((OperationItem) result.get(0)).getOperation() == command1);
        assertTrue(((OperationItem) result.get(1)).getOperation() == command2);
        assertTrue(((OperationItem) result.get(2)).getOperation() == command3);
        assertTrue(((OperationItem) result.get(3)).getOperation() == command4);
        assertTrue(((OperationItem) result.get(4)).getOperation() == command5);
    }
}


class TestCommand extends Command {
    public TestCommand(FrameMediator controller,
        DefaultCommandReference[] arguments) {
        super(controller, arguments);
    }

    public void updateGUI() {
    }

    public void execute(Worker worker) throws Exception {
    }
}