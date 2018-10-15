public void addCommEventListener(IConnectionEventHandler listener);

package org.eclipse.ecf.internal.comm;

import java.io.IOException;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;

public interface IConnection {

	public Object connect(ID remote, Object data, int timeout) throws IOException;
	public void disconnect() throws IOException;
	public boolean isConnected();
	public ID getLocalID();
	public void start();
	public void stop();
	public boolean isStarted();
	public Map getProperties();
	public IConnectionEventHandler addCommEventListener(IConnectionEventHandler listener);
	public void removeCommEventListener(IConnectionEventHandler listener);
}