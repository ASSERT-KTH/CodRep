public void handleDisconnectEvent(DisconnectConnectionEvent event);

package org.eclipse.ecf.internal.comm;

public interface IConnectionEventHandler {

	public boolean handleSuspectEvent(ConnectionEvent event);
	public void handleDisconnectEvent(ConnectionEvent event);
	public Object getAdapter(Class clazz);
}