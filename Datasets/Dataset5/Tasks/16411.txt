public ID getFromContainerID();

package org.eclipse.ecf.ds.events;

import org.eclipse.ecf.core.identity.ID;


public interface IChannelMessageEvent extends IChannelEvent {
	public ID getFromID();
	public byte [] getData();
}