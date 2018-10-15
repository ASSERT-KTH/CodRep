int trials = 40;

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.debug.debugger.zorba.translator;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.ListenerList;
import org.eclipse.core.runtime.Status;
import org.eclipse.debug.core.model.IBreakpoint;
import org.eclipse.dltk.dbgp.internal.DbgpTermination;
import org.eclipse.wst.xquery.debug.core.XQDTDebugCorePlugin;
import org.eclipse.wst.xquery.debug.dbgp.IDebuggerEngine;
import org.eclipse.wst.xquery.debug.debugger.zorba.ZorbaDebuggerPlugin;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.communication.MessageReader;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.communication.ProtocolException;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.communication.SocketClientConnection;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.communication.SocketServerConnection;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.AbstractCommandMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.AbstractMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.AbstractReplyMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.ClearMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.CommandNotImplementedException;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.EvaluateMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.EvaluatedMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.FramesMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.ICommandSets;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.InvalidCommandException;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.MessageFactory;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.MessageFormatException;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.ReplyMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.SetMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.StepMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.VariablesMessage;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.messages.VariablesPayload;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.model.QueryLocation;
import org.eclipse.wst.xquery.debug.debugger.zorba.translator.model.Variable;

@SuppressWarnings("restriction")
public class ZorbaDebuggerEngine extends DbgpTermination implements IDebuggerEngine {
    public final static int STEP_INTO = 1;
    public final static int STEP_OVER = 2;
    public final static int STEP_RETURN = 3;

    private boolean fTerminated = false;
    private boolean fSuspended = false;

    private SocketClientConnection fRequestConnection;
    private SocketServerConnection fEventConnection;
    private MessageReader fReplyReader;
    private MessageReader fEventReader;

    private EventListener fEventListener;
    private LinkedList<AbstractMessage> fReceivedEvents = new LinkedList<AbstractMessage>();

    private ListenerList fEventListeners = new ListenerList(ListenerList.IDENTITY);
    private Map<Integer, IDebugEventListener> fEvalEventListenerMap = new HashMap<Integer, IDebugEventListener>();

    private class EventListener implements Runnable {

        public void run() {
            try {
                fEventConnection.connect();
                fEventReader = new MessageReader(fEventConnection.getInput());
            } catch (IOException e) {
                handleException(e);
            }

            AbstractCommandMessage event;
            try {
                while (!fTerminated) {
                    try {
                        event = (AbstractCommandMessage)fEventReader.readMessage();
                        if (event != null) {
                            fReceivedEvents.add(event);
                            notifyListeners(event);
                        }
                        event = null;
                    } catch (IOException se) {
                        if (!fTerminated) {
                            fTerminated = true;
                            terminate();
                            fireObjectTerminated(se);
                        }
                    } catch (ProtocolException pe) {
                        ZorbaDebuggerPlugin.getDefault().getLog().log(
                                new Status(IStatus.ERROR, ZorbaDebuggerPlugin.PLUGIN_ID, pe.getMessage(), pe));
                    }
                }
            } catch (Exception e) {
                handleException(e);
            }
        }

        private IStatus handleException(Exception exception) {
            exception.printStackTrace();
            return new Status(IStatus.ERROR, XQDTDebugCorePlugin.PLUGIN_ID, 0, exception.getMessage(), exception);
        }

    }

    public ZorbaDebuggerEngine(int requestPort, int eventPort) {
        fRequestConnection = new SocketClientConnection(requestPort);
        fEventConnection = new SocketServerConnection(eventPort);
        fEventListener = new EventListener();
    }

    private void notifyListeners(AbstractCommandMessage event) {
        if (event instanceof EvaluatedMessage) {
            EvaluatedMessage evaled = (EvaluatedMessage)event;
            int key = evaled.getExprId();
            IDebugEventListener listener = fEvalEventListenerMap.get(new Integer(key));
            if (listener != null) {
                listener.handleDebugEvent(event);
            } else {
                IDebugEventListener[] listeners = new IDebugEventListener[fEvalEventListenerMap.size()];
                fEvalEventListenerMap.values().toArray(listeners);
                for (int i = 0; i < listeners.length; i++) {
                    listeners[i].handleDebugEvent(event);
                }
            }

        } else {
            Object[] listeners = fEventListeners.getListeners();
            for (int i = 0; i < listeners.length; i++) {
                ((IDebugEventListener)listeners[i]).handleDebugEvent(event);
            }
        }
    }

    public void addDebugEventListener(IDebugEventListener listener) {
        fEventListeners.add(listener);
    }

    public void addEvalEventListener(IDebugEventListener listener) {
        addEvalEventListener(listener, listener.hashCode());
    }

    public void addEvalEventListener(IDebugEventListener listener, int exprId) {
        fEvalEventListenerMap.put(exprId, listener);
    }

    public void removeDebugEventListener(IDebugEventListener listener) {
        fEventListeners.remove(listener);
    }

    public void removeEvalEventListener(IDebugEventListener listener) {
        fEvalEventListenerMap.remove(listener.hashCode());
    }

    public void connect() throws IOException {
        // start listening
        Thread thread = new Thread(fEventListener, "Engine Event Listener");
        thread.setDaemon(true);
        thread.start();

        int trials = 4;
        while (true) {
            try {
                fRequestConnection.connect();
                fReplyReader = new MessageReader(fRequestConnection.getInput());
                return;
            } catch (IOException e) {
                try {
                    if (--trials < 0) {
                        fTerminated = true;
                        terminate();
                        throw new IOException(
                                "Failed to connect to the debug engine. Connection failed after 5 connection attempts.");
                    }
                    Thread.sleep(1000);
                } catch (InterruptedException e1) {
                }
            }
        }
    }

    public void terminate() {
        sendCommand(ICommandSets.COMMAND_TERMINATE);
        // handleReply(reply);

        if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
            System.out.println("Terminating engine");
        }
        fTerminated = true;
        if (fRequestConnection != null) {
            if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
                System.out.println("Terminating engine command connection");
            }
            fRequestConnection.close();
            if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
                System.out.println("connection open: " + fRequestConnection.isOpen());
            }
            fRequestConnection = null;
        }

        if (fEventConnection != null) {
            if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
                System.out.println("Terminating engine event listener");
            }
            fEventConnection.close();
            if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
                System.out.println("connection open: " + fEventConnection.isOpen());
            }
            fEventConnection = null;
        }
        fReplyReader = null;
        // fEventReader = null;

        fEventListeners.clear();
    }

    private AbstractReplyMessage sendCommand(int command) {
        return sendCommand(MessageFactory.buildCommand(command));
    }

    public AbstractReplyMessage sendCommand(AbstractCommandMessage message) {
        if (ZorbaDebuggerPlugin.DEBUG_ZORBA_DEBUG_PROTOCOL) {
            System.out.println("Sending command: " + message.getClass().getSimpleName());
        }

        AbstractReplyMessage reply = null;
        try {
            if (ZorbaDebuggerPlugin.DEBUG_ZORBA_DEBUG_PROTOCOL) {
                System.out.println("Sending to engine:" + new String(message.toByteArray()));
            }
            fRequestConnection.writePacket(message.toByteArray());
            if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
                System.out.println("Waiting fo reply...");
            }
            reply = (AbstractReplyMessage)fReplyReader.readMessage();
            if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
                System.out.println("Reply received");
            }
        } catch (IOException e) {
            //e.printStackTrace();
        }

        return reply;
    }

    public void run() {
        AbstractReplyMessage reply = sendCommand(ICommandSets.COMMAND_RUN);
        handleReply(reply);
    }

    public void suspend() {
        AbstractReplyMessage reply = sendCommand(ICommandSets.COMMAND_SUSPEND);
        handleReply(reply);
    }

    public void resume() {
        AbstractReplyMessage reply = sendCommand(ICommandSets.COMMAND_RESUME);
        handleReply(reply);
    }

    private void handleReply(AbstractReplyMessage reply) {
        if (reply == null) {
            throw new ProtocolException("null reply message");
        }

        if (reply.getErrorCode() == IErrorCodes.NO_ERROR) {
            return;
        }

        ReplyMessage errorReply = (ReplyMessage)reply;

        switch (errorReply.getErrorCode()) {
        case IErrorCodes.ERROR_INVALID_COMMAND:
            int errorCode = -1;
            if (errorReply.getData() != null) {
                ;
            }
            try {
                errorCode = Integer.parseInt(new String(errorReply.getData()));
            } catch (NumberFormatException e) {
            }
            throw new InvalidCommandException(errorCode);
        case IErrorCodes.ERROR_COMMAND_NOT_IMPLEMENTED:
            errorCode = -1;
            if (errorReply.getData() != null) {
                ;
            }
            try {
                errorCode = Integer.parseInt(new String(errorReply.getData()));
            } catch (NumberFormatException e) {
            }
            throw new CommandNotImplementedException(errorCode);
        case IErrorCodes.ERROR_INVALID_MESSAGE_FORMAT:
            throw new MessageFormatException("The message received by the engine had an invalid format.");
        case IErrorCodes.ERROR_UNKNOWN:
            throw new ProtocolException();
        default:
            try {
                // Handle this case!!!
                throw new ProtocolException("Unknown error code: " + errorReply.getErrorCode());
            } catch (Exception e) {
                e.printStackTrace();
            }

        }
    }

    public boolean isSuspended() {
        return fSuspended;
    }

    public void setSuspended(boolean suspended) {
        fSuspended = suspended;
    }

    public boolean isTerminated() {
        return fTerminated;
    }

    public void setTerminated(boolean terminated) {
        fTerminated = terminated;
    }

    public void setBreakpoint(IBreakpoint breakpoint) {
        // if (!(breakpoint instanceof XQueryLineBreakpoint))
        // return;

        SetMessage message = (SetMessage)MessageFactory.buildCommand(ICommandSets.COMMAND_SET);
        // try {
        // XQueryLineBreakpoint xlb = (XQueryLineBreakpoint)breakpoint;
        // message.addBreakpoint(new Breakpoint(Math.abs(breakpoint.hashCode()), new
        // QueryLocation(xlb.getFileName(), xlb.getLineNumber(), 1, xlb.getLineNumber(), 1)));
        // } catch (CoreException e) {
        // e.printStackTrace();
        // return;
        // }

        AbstractReplyMessage reply = sendCommand(message);
        handleReply(reply);
    }

    public void setBreakpoints(List<IBreakpoint> breakpoints) {
        if (breakpoints == null || breakpoints.size() == 0) {
            return;
        }
        SetMessage message = (SetMessage)MessageFactory.buildCommand(ICommandSets.COMMAND_SET);
        // boolean hasBreakpoints = false;
        // for (IBreakpoint breakpoint : breakpoints) {
        // try {
        // XQueryLineBreakpoint xlb = (XQueryLineBreakpoint)breakpoint;
        // message.addBreakpoint(new Breakpoint(Math.abs(xlb.hashCode()), new
        // QueryLocation(xlb.getFileName(), xlb.getLineNumber(), 1, xlb.getLineNumber(), 1)));
        // hasBreakpoints = true;
        // } catch (CoreException e) {
        // e.printStackTrace();
        // }
        // }
        // if(!hasBreakpoints)
        // return;

        AbstractReplyMessage reply = sendCommand(message);
        handleReply(reply);
    }

    public void clearBreakpoint(IBreakpoint breakpoint) {
        // if (!(breakpoint instanceof XQueryLineBreakpoint))
        // return;

        ClearMessage message = (ClearMessage)MessageFactory.buildCommand(ICommandSets.COMMAND_CLEAR);
        message.addBreakpointId(Math.abs(breakpoint.hashCode()));

        AbstractReplyMessage reply = sendCommand(message);
        handleReply(reply);
    }

    public Variable[] getVariables() {
        VariablesMessage command = new VariablesMessage();
        ReplyMessage reply = (ReplyMessage)sendCommand(command);
        VariablesPayload payload = command.getVariables(reply);

        List<Variable> vars = new ArrayList<Variable>();
        for (Variable variable : payload.getGlobalVariables()) {
            variable.setIsGlobal(true);
            vars.add(variable);
        }
        vars.addAll(payload.getLocalVariables());

        return vars.toArray(new Variable[vars.size()]);
    }

    public QueryLocation[] getStackFrames() {
        FramesMessage command = new FramesMessage();
        ReplyMessage reply = (ReplyMessage)sendCommand(command);
        return command.readLocations(reply);
    }

    public void step(int stepType) {
        AbstractReplyMessage reply = sendCommand(new StepMessage(stepType));
        handleReply(reply);
    }

    public void evaluate(String expression, int listenerId) {
        if (ZorbaDebuggerPlugin.DEBUG_DEBUGGER_ENGINE) {
            System.out.println("Evaluating: " + expression);
        }
        EvaluateMessage command = new EvaluateMessage(listenerId, expression);
        AbstractReplyMessage reply = sendCommand(command);
        handleReply(reply);
    }

    public void requestTermination() {
        // System.err.println("requestTermination");
    }

    public void waitTerminated() throws InterruptedException {
        // System.err.println("waitTerminated");
    }

    public void addDebugEventListener(Object listener) {
        // TODO Auto-generated method stub

    }

    public void removeDebugEventListener(Object listener) {
        // TODO Auto-generated method stub

    }

    public Object sendCommand(Object command) {
        // TODO Auto-generated method stub
        return null;
    }

}