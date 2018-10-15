public SharedObjectDescription[] getReplicaDescriptions(ID [] remotes);

package org.eclipse.ecf.provider.generic.sobject;

import org.eclipse.ecf.core.IIdentifiable;
import org.eclipse.ecf.core.ISharedObjectContext;
import org.eclipse.ecf.core.SharedObjectDescription;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.util.IEventProcessor;

public interface ISharedObjectInternal extends IIdentifiable {
	public void addEventProcessor(IEventProcessor ep);
	public boolean removeEventProcessor(IEventProcessor ep);
	
	public ISharedObjectContext getContext();
	public boolean isPrimary();
	public ID getHomeID();
	public SharedObjectDescription getReplicaDescription(ID remote);
	public void destroySelf();
}