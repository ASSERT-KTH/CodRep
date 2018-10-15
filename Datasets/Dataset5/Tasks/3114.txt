if(events.size() == amountOfEventsToExpect) {

/*******************************************************************************
 * Copyright (c) 2009 Markus Alexander Kuppe.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.tests.discovery.listener;

import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.IServiceListener;

public class TestServiceListener extends TestListener implements IServiceListener {

	public TestServiceListener(int eventsToExpect) {
		super(eventsToExpect);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.discovery.IServiceListener#serviceDiscovered(org.eclipse.ecf.discovery.IServiceEvent)
	 */
	public void serviceDiscovered(IServiceEvent anEvent) {
		events.add(anEvent);
		if(getEventCount() == amountOfEventsToExpect) {
			synchronized (this) {
				notifyAll();
			}
		}
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.discovery.IServiceListener#serviceUndiscovered(org.eclipse.ecf.discovery.IServiceEvent)
	 */
	public void serviceUndiscovered(IServiceEvent anEvent) {
		throw new java.lang.UnsupportedOperationException("TestServiceListener#serviceUndiscovered not yet implemented");
	}
}