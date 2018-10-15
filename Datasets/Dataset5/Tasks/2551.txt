public IChannel createChannel(IChannelConfig config) throws ECFException;

package org.eclipse.ecf.ds;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.ECFException;

public interface IChannelContainer {
	public IChannel createChannel(IChannelDescription description) throws ECFException;
	public IChannel getChannel(ID channelID);
	public boolean disposeChannel(ID channelID);
}