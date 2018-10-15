import org.eclipse.ecf.remoteservice.rest.RestCallableFactory;

/******************************************************************************* 
* Copyright (c) 2009 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
*******************************************************************************/ 
package org.eclipse.ecf.tests.remoteservice.rest;

import java.util.Dictionary;
import java.util.Hashtable;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.remoteservice.IRemoteServiceID;
import org.eclipse.ecf.remoteservice.IRemoteServiceRegistration;
import org.eclipse.ecf.remoteservice.client.IRemoteCallable;
import org.eclipse.ecf.remoteservice.rest.client.RestCallableFactory;

public class RestServiceRegistrationTest extends AbstractRestTestCase {
	
	private IRemoteServiceRegistration registration;
	private IContainer container;

	protected void setUp() throws Exception {
		container = createRestContainer(RestConstants.TEST_TWITTER_TARGET);
		Dictionary properties = new Hashtable();
		properties.put("user", "null");
		IRemoteCallable callable = RestCallableFactory.createCallable("resourcePath");
		registration = registerCallable(container, callable, properties);
	}
	
	protected void tearDown() throws Exception {
		registration = null;
	}
	
	public void testCreateServiceRegistration() {		
		assertNotNull(registration);
	}
	
	public void testGetProperty() {
		Object property = registration.getProperty("user");
		assertTrue(property instanceof String);
		String prop = (String) property;
		assertEquals("null", prop);
	}
	
	public void testGetPropertyKeys() {
		String[] keys = registration.getPropertyKeys();
		assertEquals(1, keys.length);
		assertEquals(keys[0], "user");
	}
	
	public void testSetProperties() {
		Dictionary properties = new Hashtable();
		properties.put("user", "holger");
		properties.put("pass", "null");
		Object property = registration.getProperty("user");
		assertEquals("null", property);
		registration.setProperties(properties);
		property = registration.getProperty("user");
		assertEquals("holger", property);
	}
	
	public void testGetId() {
		IRemoteServiceID id = registration.getID();
		assertNotNull(id);
		assertTrue(id instanceof IRemoteServiceID);
		assertEquals(container.getID(), id.getContainerID());
	}
	
	public void testGetContainerId() {
		assertEquals(container.getID(), registration.getContainerID());
	}
	
}