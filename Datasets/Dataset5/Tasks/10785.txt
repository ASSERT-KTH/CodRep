public synchronized void serviceTypeDiscovered(IServiceTypeEvent anEvent) {

/*******************************************************************************
 * Copyright (c) 2009 Markus Alexander Kuppe.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Markus Alexander Kuppe (ecf-dev_eclipse.org <at> lemmster <dot> de) - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.tests.discovery.listener;

import org.eclipse.ecf.discovery.IServiceTypeEvent;
import org.eclipse.ecf.discovery.IServiceTypeListener;

public class TestServiceTypeListener extends TestListener implements IServiceTypeListener {

	public TestServiceTypeListener(int eventsToExpect) {
		super(eventsToExpect);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.discovery.IServiceTypeListener#serviceTypeDiscovered(org.eclipse.ecf.discovery.IServiceTypeEvent)
	 */
	public void serviceTypeDiscovered(IServiceTypeEvent anEvent) {
		events.add(anEvent);
		if(events.size() == amountOfEventsToExpect) {
			synchronized (this) {
				notifyAll();
			}
		}
	}

}