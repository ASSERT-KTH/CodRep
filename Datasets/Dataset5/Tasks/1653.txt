import org.eclipse.ecf.core.status.SerializableStatus;

package org.eclipse.ecf.tests.core.util;

import junit.framework.TestCase;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.ecf.core.util.SerializableStatus;
import org.eclipse.ecf.internal.tests.Activator;

public class SerializableStatusTest extends TestCase {

	
	protected IStatus createOKStatus() {
		return SerializableStatus.OK_STATUS;
	}
	
	protected IStatus createErrorStatus() {
		return new SerializableStatus(IStatus.ERROR,Activator.PLUGIN_ID,IStatus.ERROR,"error",new IllegalArgumentException("myexception"));
	}
	
	public static class MyNotSerializableException extends Exception {
		
		Object notSerializableObject = new Object();
		
		public MyNotSerializableException(String message) {
			super(message);
		}
	}
	
	protected IStatus createNotSerializableExceptionStatus() {
		return new SerializableStatus(IStatus.ERROR,Activator.PLUGIN_ID,IStatus.ERROR,"error",new MyNotSerializableException("myexception"));
	}
	
	public void testCreateStatus() throws Exception {
		IStatus s = createOKStatus();
		assertNotNull(s);
		assertTrue(s.isOK());
		assertTrue(s.getCode() == SerializableStatus.OK);
		assertTrue(s.getMessage().equals("ok"));
		assertTrue(s.getException() == null);
	}
	
	public void testCreateExceptionStatus() throws Exception {
		IStatus s = createErrorStatus();
		assertNotNull(s);
		assertFalse(s.isOK());
		assertTrue(s.getCode() == IStatus.ERROR);
		assertFalse(s.getMessage().equals("ok"));
		assertFalse(s.getException() == null);
	}

	public void testCreateNotSerializableExceptionStatus() throws Exception {
		IStatus s = createNotSerializableExceptionStatus();
		assertNotNull(s);
		assertFalse(s.isOK());
		assertTrue(s.getCode() == IStatus.ERROR);
		assertFalse(s.getMessage().equals("ok"));
		assertFalse(s.getException() == null);
		Throwable t = s.getException();
		assertFalse(t instanceof MyNotSerializableException);
	}
}