sof.runWithProgress(runnable);

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

/**
 * <p>
 * Executes {@link IProgressRunnable} instances immediately.
 * </p>
 * <p>
 * <b>NOTE</b>:  {@link #execute(IProgressRunnable, IProgressMonitor)} should be used with some
 * degree of caution with this implementation, as unlike other implementations the {@link IProgressRunnable#run(IProgressMonitor)}
 * method will be called by the thread that calls {@link #execute(IProgressRunnable, IProgressMonitor)}, meaning
 * that calling #execute(IProgressRunnable, IProgressMonitor) may block the calling thread indefinitely.
 * </p>
 * @see JobsExecutor
 * @see ThreadsExecutor
 */
public class ImmediateExecutor extends AbstractExecutor implements IExecutor, IRunnableExecutor {

	protected AbstractFuture createFuture(IProgressMonitor monitor) {
		return new SingleOperationFuture(monitor);
	}

	public IFuture execute(IProgressRunnable runnable, IProgressMonitor monitor) {
		Assert.isNotNull(runnable);
		AbstractFuture sof = createFuture(monitor);
		// Actually run the runnable immediately.  See NOTE above
		sof.safeRun(runnable);
		return sof;
	}

}