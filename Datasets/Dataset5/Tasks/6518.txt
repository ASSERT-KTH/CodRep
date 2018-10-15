package org.eclipse.ecf.provider.discovery;

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
package org.eclipse.ecf.internal.provider.discovery;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.discovery.IServiceEvent;
import org.eclipse.ecf.discovery.ServiceContainerEvent;

public class CompositeServiceContainerEvent extends ServiceContainerEvent implements IServiceEvent {

	private ID origId;

	public CompositeServiceContainerEvent(IServiceEvent event, ID connectedId) {
		super(event.getServiceInfo(), connectedId);
		origId = event.getLocalContainerID();
	}

	/**
	 * @return the origId
	 */
	public ID getOriginalLocalContainerID() {
		return origId;
	}
}