package org.eclipse.ecf.ds.events;

package org.eclipse.ecf.ds;

import org.eclipse.ecf.core.identity.ID;


public interface IChannelMessageEvent extends IChannelEvent {
	public ID getFromID();
	public byte [] getData();
}