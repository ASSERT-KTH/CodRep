public class HttpDeleteRequestType extends AbstractRequestType {

/*******************************************************************************
* Copyright (c) 2009 Composent, Inc. and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   Composent, Inc. - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.remoteservice.rest.client;



import java.util.Map;

public class HttpDeleteRequestType extends AbstractRestRequestType {

	public HttpDeleteRequestType(Map defaultRequestHeaders) {
		super(defaultRequestHeaders);
	}

	public HttpDeleteRequestType() {
		// nothing to do
	}
}