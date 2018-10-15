sof.runWithProgress(progressRunnable);

/*******************************************************************************
* Copyright (c) 2008 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.core.util;

import org.eclipse.core.runtime.Assert;
import org.eclipse.core.runtime.IProgressMonitor;

public class ThreadsExecutor extends AbstractExecutor {

	public ThreadsExecutor() {
		// nothing
	}

	protected String createThreadName(IProgressRunnable runnable) {
		return "ThreadsExecutor(" + runnable.toString() + ")"; //$NON-NLS-1$ //$NON-NLS-2$
	}

	protected Runnable createRunnable(final ISafeProgressRunner sof, final IProgressRunnable progressRunnable) {
		return new Runnable() {
			public void run() {
				preSafeRun();
				sof.safeRun(progressRunnable);
				postSafeRun();
			}
		};
	}

	public void configureThreadForExecution(Thread t) {
		// By default, we'll make the thread a daemon thread
		t.setDaemon(true);
	}

	protected AbstractFuture createFuture(IProgressMonitor monitor) {
		return new SingleOperationFuture(monitor);
	}

	public synchronized IFuture execute(IProgressRunnable runnable, IProgressMonitor monitor) throws IllegalThreadStateException {
		Assert.isNotNull(runnable);
		// Now create future
		AbstractFuture sof = createFuture(monitor);
		// Create the thread for this operation
		Thread thread = new Thread(createRunnable(sof, runnable), createThreadName(runnable));
		configureThreadForExecution(thread);
		// start thread
		thread.start();
		return sof;
	}

}