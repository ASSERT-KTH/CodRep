public void handleAsynchEvent(AsynchConnectionEvent event) throws IOException;

package org.eclipse.ecf.internal.comm;

import java.io.IOException;

public interface IAsynchConnectionEventHandler extends IConnectionEventHandler {
	public void handleAsynchEvent(ConnectionEvent event) throws IOException;
}