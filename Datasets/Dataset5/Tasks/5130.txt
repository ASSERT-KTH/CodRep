ServiceRegistration endpointListenerRegistration = Activator.getDefault().getContext().registerService(EndpointListener.class.getName(), createEndpointListener(), props);

package org.eclipse.ecf.tests.osgi.services.remoteserviceadmin;

import java.util.Properties;

import org.osgi.framework.ServiceRegistration;
import org.osgi.service.remoteserviceadmin.EndpointDescription;
import org.osgi.service.remoteserviceadmin.EndpointListener;
import org.osgi.service.remoteserviceadmin.RemoteConstants;

import junit.framework.TestCase;

public class EndpointListenerTest extends TestCase {

	private EndpointListener createEndpointListener() {
		return new EndpointListener() {

			public void endpointAdded(EndpointDescription endpoint,
					String matchedFilter) {
				System.out.println("endpointAdded endpoint="+endpoint+",matchedFilter="+matchedFilter);
			}

			public void endpointRemoved(EndpointDescription endpoint,
					String matchedFilter) {
				System.out.println("endpointRemoved endpoint="+endpoint+",matchedFilter="+matchedFilter);
			}
			
		};
	}

	public void testEndpointListenerNotification() throws Exception {
		Properties props = new Properties();
		props.put(org.osgi.service.remoteserviceadmin.EndpointListener.ENDPOINT_LISTENER_SCOPE,"("+RemoteConstants.ENDPOINT_ID+"=*)");
		ServiceRegistration endpointListenerRegistration = Activator.getContext().registerService(EndpointListener.class.getName(), createEndpointListener(), props);
		Thread.sleep(5000);
		endpointListenerRegistration.unregister();
	}
}