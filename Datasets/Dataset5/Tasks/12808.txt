registrySharedObject.removeRemoteServiceListener(listener);

package org.eclipse.ecf.provider.remoteservice.generic;

import java.util.ArrayList;
import java.util.Dictionary;
import java.util.List;

import org.eclipse.ecf.core.ISharedObjectContainerConfig;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDFactory;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.provider.generic.TCPClientSOContainer;
import org.eclipse.ecf.remoteservice.IRemoteService;
import org.eclipse.ecf.remoteservice.IRemoteServiceContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceListener;
import org.eclipse.ecf.remoteservice.IRemoteServiceReference;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;

public class RemoteServiceContainer extends TCPClientSOContainer
		implements IRemoteServiceContainer {

	private static final String REGISTRY_ID = RemoteServiceContainer.class.getName() + ".registry";
	protected List serviceListener = new ArrayList();
	protected RegistrySharedObject registrySharedObject;
	
	protected RegistrySharedObject createAndAddRegistry() {
		RegistrySharedObject rso = new RegistrySharedObject();
		try {
			getSharedObjectManager().addSharedObject(
					IDFactory.getDefault().createStringID(REGISTRY_ID), rso,
					null);
		} catch (Exception e) {
			// Should not happen...if does throw NullPointerException
			throw new NullPointerException();
			// TODO: handle exception
		}	
		return rso;
	}

	public RemoteServiceContainer(ISharedObjectContainerConfig config) {
		super(config);
		registrySharedObject = createAndAddRegistry();
	}

	public RemoteServiceContainer(ISharedObjectContainerConfig config,
			int ka) {
		super(config, ka);
		registrySharedObject = createAndAddRegistry();
	}

	public void addRemoteServiceListener(IRemoteServiceListener listener) {
		registrySharedObject.addRemoteServiceListener(listener);

	}

	public IRemoteService getRemoteService(IRemoteServiceReference ref)
			throws ECFException {
		return registrySharedObject.getRemoteService(ref);
	}

	public IRemoteServiceReference[] getRemoteServiceReferences(ID[] idFilter,
			String clazz, String filter) throws ECFException {
		return registrySharedObject.getRemoteServiceReferences(idFilter,clazz,filter);
	}

	public IRemoteServiceRegistration registerRemoteService(String[] clazzes,
			Object service, Dictionary properties) throws ECFException {
		return registrySharedObject.registerRemoteService(clazzes,service,properties);
	}

	public void removeRemoteServiceListener(IRemoteServiceListener listener) {
		registrySharedObject.remoteRemoteServiceListener(listener);
	}

	public boolean ungetRemoteService(IRemoteServiceReference ref) {
		return registrySharedObject.ungetRemoteService(ref);
	}
}