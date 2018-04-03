import org.columba.api.shutdown.IShutdownManager;

package org.columba.core.facade;

import org.columba.core.shutdown.IShutdownManager;
import org.columba.core.shutdown.ShutdownManager;

public class ShutdownFacade {

	public static IShutdownManager getShutdownManager() {
		return (IShutdownManager) ShutdownManager.getInstance();
	}
}