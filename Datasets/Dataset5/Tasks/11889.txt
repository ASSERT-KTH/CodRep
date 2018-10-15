//e.printStackTrace();

/*******************************************************************************
 *  Copyright (c)2010 REMAIN B.V. The Netherlands. (http://www.remainsoftware.com).
 *  All rights reserved. This program and the accompanying materials
 *  are made available under the terms of the Eclipse Public License v1.0
 *  which accompanies this distribution, and is available at
 *  http://www.eclipse.org/legal/epl-v10.html
 * 
 *  Contributors:
 *     Ahmed Aadel - initial API and implementation     
 *******************************************************************************/
package org.eclipse.ecf.provider.zookeeper.util;

import java.util.HashSet;
import java.util.Set;

import org.eclipse.ecf.provider.zookeeper.DiscoveryActivator;
import org.eclipse.ecf.provider.zookeeper.core.ZooDiscoveryContainer;
import org.osgi.service.log.LogService;

/**
 * @author Ahmed Aadel
 * @since 0.1
 */
public class Logger {
	private static Set<LogService> logServices = new HashSet<LogService>();

	public static void bindLogService(org.osgi.service.log.LogService ls) {
		logServices.add(ls);
	}

	public static void unbindLogService(org.osgi.service.log.LogService ls) {
		logServices.remove(ls);
	}

	public static void log(int level, String message, Exception e) {
		if (logServices.isEmpty()) {
			e.printStackTrace();
			return;
		}
		for (LogService ls : logServices) {
			ls.log(DiscoveryActivator.getContext().getServiceReference(
					ZooDiscoveryContainer.class.getName()), level, message, e);
		}
	}

	public static void log(int level, String message, Throwable t) {
		if (logServices.isEmpty()) {
			t.printStackTrace();
			return;
		}
		for (LogService ls : logServices) {
			ls.log(DiscoveryActivator.getContext().getServiceReference(
					ZooDiscoveryContainer.class.getName()), level, message, t);
		}
	}
}