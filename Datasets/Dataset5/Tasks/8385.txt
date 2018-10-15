package org.eclipse.ecf.core.sharedobject;

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core;

import java.io.Serializable;
import java.util.Map;
import org.eclipse.ecf.core.identity.ID;

/**
 * Description of a remote ISharedObject instance.
 * 
 */
public class ReplicaSharedObjectDescription extends SharedObjectDescription
		implements Serializable {
	private static final long serialVersionUID = 2764430278848370713L;
	
	protected static long staticID = 0;
	public static long getNextUniqueIdentifier() {
		return staticID++;
	}
	
	protected ID homeID;
	protected long identifier;
	
	public ReplicaSharedObjectDescription(SharedObjectTypeDescription type, ID objectID, ID homeID, Map props, long ident) {
		super(type,objectID,props);
		this.homeID = homeID;
		this.identifier = ident;
	}
	public ReplicaSharedObjectDescription(String typeName, ID objectID, ID homeID, Map props, long ident) {
		super(new SharedObjectTypeDescription(typeName, null, null, null), objectID, props);
		this.homeID = homeID;
		this.identifier = ident;
	}
	public ReplicaSharedObjectDescription(String typeName, ID objectID, ID homeID, Map props) {
		this(typeName,objectID,homeID,props,getNextUniqueIdentifier());
	}
	public ReplicaSharedObjectDescription(String typeName, ID objectID, ID homeID) {
		this(typeName,objectID,homeID,null);
	}
	public ReplicaSharedObjectDescription(Class clazz, ID objectID, ID homeID, Map props, long ident) {
		super(new SharedObjectTypeDescription(clazz.getName(),null),objectID,props);
		this.homeID = homeID;
		this.identifier = ident;
	}
	public ReplicaSharedObjectDescription(Class clazz, ID objectID, ID homeID, Map props) {
		this(clazz,objectID,homeID,props,getNextUniqueIdentifier());
	}
	public ReplicaSharedObjectDescription(Class clazz, ID objectID, ID homeID) {
		this(clazz,objectID,homeID,null);
	}
	public ReplicaSharedObjectDescription(Class clazz, ID objectID) {
		this(clazz,objectID,null,null);
	}
	public ID getHomeID() {
		return homeID;
	}
	public long getIdentifier() {
		return identifier;
	}
	public void setHomeID(ID theID) {
		this.homeID = theID;
	}
	public void setID(ID theID) {
		this.id = theID;
	}
	public void setIdentifier(long identifier) {
		this.identifier = identifier;
	}
	public void setProperties(Map props) {
		this.properties = props;
	}
	public String toString() {
		StringBuffer sb = new StringBuffer("ReplicaSharedObjectDescription[");
		sb.append("type=").append(typeDescription).append(";");
		sb.append("id:").append(id).append(";");
		sb.append("homeID:").append(homeID).append(";");
		sb.append("props:").append(properties).append(";");
		sb.append("ident:").append(identifier).append("]");
		return sb.toString();
	}
}
 No newline at end of file