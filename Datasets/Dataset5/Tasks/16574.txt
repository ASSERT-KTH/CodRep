container = ContainerFactory.getDefault().createContainer(type);

package org.eclipse.ecf.example.clients;

import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.ISharedObjectContainer;
import org.eclipse.ecf.core.identity.ID;

public class SOClient {

	IContainer container = null;
	ISharedObjectContainer socontainer = null;
	ID targetID = null;
	
	protected void setupContainer(String type) throws Exception {
		container = ContainerFactory.getDefault().makeContainer(type);
		socontainer = (ISharedObjectContainer) container.getAdapter(ISharedObjectContainer.class);
	}
}