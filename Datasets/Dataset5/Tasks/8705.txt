package org.eclipse.ecf.internal.example.collab.start;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.example.collab.start;

public class ConnectionDetails {
	
	public static final String CONTAINER_TYPE = "containerType";
	public static final String TARGET_URI =  "targetURI";
	public static final String NICKNAME = "nickname";
	public static final String PASSWORD = "password";
	
	String containerType;
	String targetURI;
	String nickname;
	String password;
	
	public ConnectionDetails(String containerType, String targetURI, String nickname, String password) {
		this.containerType = containerType;
		this.targetURI = targetURI;
		this.nickname = nickname;
		this.password = password;
	}

	/**
	 * @return the containerType
	 */
	public String getContainerType() {
		return containerType;
	}

	/**
	 * @return the nickname
	 */
	public String getNickname() {
		return nickname;
	}

	/**
	 * @return the password
	 */
	public String getPassword() {
		return password;
	}

	/**
	 * @return the targetURI
	 */
	public String getTargetURI() {
		return targetURI;
	}
	
	public String toString() {
		StringBuffer sb = new StringBuffer("ConnectionDetails[");
		sb.append(CONTAINER_TYPE).append("=").append(containerType).append(";");
		sb.append(TARGET_URI).append("=").append(targetURI).append(";");
		sb.append(NICKNAME).append("=").append(nickname).append(";");
		sb.append(PASSWORD).append("=").append(password).append("]");
		return sb.toString();
	}
}