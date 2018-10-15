public interface IRemoteCall {

package org.eclipse.ecf.remoteservice;

import java.util.Dictionary;

public interface IRemoteCallable {
	public String getMethod();
	public Object [] getParameters();
	public Dictionary getProperties();
	public long getTimeout();
}