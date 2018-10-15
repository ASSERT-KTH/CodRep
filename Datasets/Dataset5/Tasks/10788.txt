public abstract class AbstractSharedObjectTest extends ContainerAbstractTestCase {

/*******************************************************************************
* Copyright (c) 2009 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.tests.sharedobject;

import java.io.IOException;
import java.util.Map;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.sharedobject.ISharedObject;
import org.eclipse.ecf.core.sharedobject.ISharedObjectContainer;
import org.eclipse.ecf.core.sharedobject.ISharedObjectManager;
import org.eclipse.ecf.core.sharedobject.SharedObjectAddException;
import org.eclipse.ecf.tests.ContainerAbstractTestCase;

public class AbstractSharedObjectTest extends ContainerAbstractTestCase {

	
	public ISharedObjectContainer getClientSOContainer(int clientindex) {
		return (ISharedObjectContainer) getClient(clientindex);
	}
	
	public ISharedObjectManager getClientSOManager(int clientindex) {
		return getClientSOContainer(clientindex).getSharedObjectManager();
	}
	
	public ID addClientSharedObject(int clientindex, ID sharedObjectID, ISharedObject so, Map properties) throws SharedObjectAddException {
		return getClientSOManager(clientindex).addSharedObject(sharedObjectID, so, properties);
	}
	
	public ISharedObjectContainer getServerSOContainer() {
		return (ISharedObjectContainer) getServer();
	}
	
	public ISharedObjectManager getServerSOManager() {
		return getServerSOContainer().getSharedObjectManager();
	}
	
	public ID addServerSharedObject(int clientindex, ID sharedObjectID, ISharedObject so, Map properties) throws SharedObjectAddException {
		return getClientSOManager(clientindex).addSharedObject(sharedObjectID, so, properties);
	}

	public ISharedObject getClientSharedObject(int clientindex, ID sharedObjectID) {
		return getClientSOManager(clientindex).getSharedObject(sharedObjectID);
	}
	
	public ISharedObject getServerSharedObject(ID sharedObjectID) {
		return getServerSOManager().getSharedObject(sharedObjectID);
	}

	public void sendMessage(IMessageSender sender, ID targetID, Object message) throws IOException {
		sender.sendMessage(targetID, message);
	}
}