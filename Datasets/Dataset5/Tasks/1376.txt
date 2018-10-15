return start.run(monitor);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.start;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.jobs.Job;

/**
 * Start job for running extensions of the org.eclipse.ecf.start extension point
 * 
 */
public class ECFStartJob extends Job {

	IECFStart start;

	public ECFStartJob(String name, IECFStart start) {
		super(name);
		this.start = start;
	}

	protected IStatus run(IProgressMonitor monitor) {
		return start.startup(monitor);
	}
}