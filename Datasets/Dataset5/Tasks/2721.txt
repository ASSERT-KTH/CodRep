public boolean disposeChannel(ID channelID);

package org.eclipse.ecf.ds;

import org.eclipse.ecf.core.IReliableContainer;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;

public interface IChannelContainer extends IReliableContainer {
	public IChannel createChannel(ID channelID) throws ECFException;
	public IChannel getChannel(ID channelID);
	public void removeChannel(ID channelID);
}