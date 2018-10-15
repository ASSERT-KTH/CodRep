static final String RUN_METHOD = "run"; //$NON-NLS-1$

package org.eclipse.ecf.ui.actions;

import org.eclipse.ecf.core.ContainerConnectException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.security.IConnectContext;
import org.eclipse.ecf.core.util.IExceptionHandler;
import org.eclipse.ecf.core.util.Trace;
import org.eclipse.ecf.internal.ui.Activator;
import org.eclipse.ecf.internal.ui.UIDebugOptions;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.IWorkbenchWindowActionDelegate;

public class SynchContainerConnectAction implements
		IWorkbenchWindowActionDelegate {

	private static final String RUN_METHOD = "run";

	protected IWorkbenchWindow window;

	protected ID targetID;

	protected IConnectContext connectContext;

	protected IContainer container;

	protected IExceptionHandler exceptionHandler;

	public SynchContainerConnectAction(IContainer container, ID targetID,
			IConnectContext connectContext, IExceptionHandler exceptionHandler) {
		this.container = container;
		this.targetID = targetID;
		this.connectContext = connectContext;
		this.exceptionHandler = exceptionHandler;
	}

	public SynchContainerConnectAction(IContainer container, ID targetID,
			IConnectContext connectContext) {
		this(container, targetID, connectContext, null);
	}

	public void dispose() {
		this.container = null;
		this.targetID = null;
		this.connectContext = null;
		this.window = null;
	}

	protected void handleConnectException(IAction action,
			ContainerConnectException e) {
		if (exceptionHandler != null)
			exceptionHandler.handleException(e);
	}

	public void init(IWorkbenchWindow window) {
		this.window = window;
	}

	public void run(IAction action) {
		try {
			Trace.entering(Activator.PLUGIN_ID,
					UIDebugOptions.METHODS_ENTERING, this.getClass(), RUN_METHOD,
					action);
			container.connect(this.targetID, this.connectContext);
		} catch (ContainerConnectException e) {
			// First Trace
			Trace.catching(Activator.PLUGIN_ID,
					UIDebugOptions.METHODS_ENTERING, this.getClass(), RUN_METHOD, e);
			handleConnectException(action, e);
		} finally {
			Trace.exiting(Activator.PLUGIN_ID,
					UIDebugOptions.METHODS_EXITING, this.getClass(), RUN_METHOD);
		}
	}

	public void selectionChanged(IAction action, ISelection selection) {
	}

	protected IWorkbenchWindow getWindow() {
		return window;
	}

	protected ID getTargetID() {
		return targetID;
	}

	protected IConnectContext getConnectContext() {
		return connectContext;
	}

	protected IContainer getContainer() {
		return container;
	}

	protected IExceptionHandler getExceptionHandler() {
		return exceptionHandler;
	}

}