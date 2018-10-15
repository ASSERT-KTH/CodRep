public Object run(IProgressMonitor monitor) throws Exception {

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

import org.eclipse.core.runtime.IProgressMonitor;

public abstract class AbstractExecutor implements IRunnableExecutor, IExecutor {

	public void execute(final Runnable runnable) {
		execute(new IProgressRunnable() {
			public Object run(IProgressMonitor monitor) throws Throwable {
				runnable.run();
				return null;
			}
		}, null);
	}

	public abstract IFuture execute(IProgressRunnable runnable, IProgressMonitor monitor);

	protected abstract AbstractFuture createFuture(IProgressMonitor progressMonitor);

	protected void preSafeRun() {
		// By default do nothing
	}

	protected void postSafeRun() {
		// By default do nothing
	}

}