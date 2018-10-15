public Class[][] getSupportedParameterTypes() {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.provider.filetransfer.identity;

import java.net.URL;

import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.IDCreateException;
import org.eclipse.ecf.core.identity.Namespace;

/**
 * URL file namespace class. This defines a namespace that understands how to
 * create IFileID instances from arbitary URLs
 */
public class URLFileNamespace extends Namespace {

	private static final long serialVersionUID = 8204058147686930765L;

	public static final String PROTOCOL = "ecf.provider.filetransfer.url";

	public static final String NAMESPACE_NAME = PROTOCOL;

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.Namespace#createInstance(java.lang.Object[])
	 */
	public ID createInstance(Object[] args) throws IDCreateException {
		if (args == null || args.length == 0)
			throw new IDCreateException("arguments is null or empty");
		try {
			if (args[0] instanceof URL)
				return new URLFileID(this, (URL) args[0]);
			if (args[0] instanceof String)
				return new URLFileID(this, new URL((String) args[0]));
		} catch (Exception e) {
			throw new IDCreateException("Exception in createInstance", e);
		}
		throw new IDCreateException(
				"arguments not correct to create instance of URLFileNamespace");
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.Namespace#getScheme()
	 */
	public String getScheme() {
		return PROTOCOL;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.eclipse.ecf.core.identity.Namespace#getSupportedParameterTypesForCreateInstance()
	 */
	public Class[][] getSupportedParameterTypesForCreateInstance() {
		return new Class[][] { { URL.class }, { String.class } };
	}

}