return start.startup(monitor);

package org.eclipse.ecf.core.start;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.jobs.Job;

/**
 * Start job for running extensions of the org.eclipse.ecf.start 
 * extension point
 *
 */
public class ECFStartJob extends Job {
	
	IECFStart start;
	
	public ECFStartJob(String name, IECFStart start) {
		super(name);
		this.start = start;
	}
	protected IStatus run(IProgressMonitor monitor) {
		return start.start(monitor);
	}
}