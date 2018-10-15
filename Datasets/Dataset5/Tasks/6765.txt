package org.eclipse.wst.xml.vex.ui.internal.swt;

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.internal.swt;

import org.eclipse.swt.widgets.Display;

/**
 * Periodic timer, built using the Display.timerExec method.
 */
public class Timer {

	/**
	 * Class constructor. The timer must be explicitly started using the start()
	 * method.
	 * 
	 * @param periodMs
	 *            Milliseconds between each invocation.
	 * @param runnable
	 *            Runnable to execute when the period expires.
	 */
	public Timer(int periodMs, Runnable runnable) {
		this.periodMs = periodMs;
		this.runnable = runnable;
	}

	/**
	 * Reset the timer so that it waits another period before firing.
	 */
	public void reset() {
		if (this.started) {
			this.stop();
			this.start();
		}
	}

	/**
	 * Start the timer.
	 */
	public void start() {
		if (!this.started) {
			this.innerRunnable = new InnerRunnable();
			Display.getCurrent().timerExec(this.periodMs, this.innerRunnable);
			this.started = true;
		}
	}

	/**
	 * Stop the timer.
	 */
	public void stop() {
		if (this.started) {
			this.innerRunnable.discarded = true;
			this.innerRunnable = null;
			this.started = false;
		}
	}

	// ==================================================== PRIVATE

	private Runnable runnable;
	private int periodMs;
	private boolean started = false;
	private InnerRunnable innerRunnable;

	private class InnerRunnable implements Runnable {
		public boolean discarded = false;

		public void run() {
			if (!discarded) {
				runnable.run();
				// Display display = Display.getCurrent();
				Display.getCurrent().timerExec(periodMs, this);
			}
		}
	}
}