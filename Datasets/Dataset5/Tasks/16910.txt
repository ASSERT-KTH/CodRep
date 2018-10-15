return this.uri.compareTo((Object) ((URIID) o).uri);

/*******************************************************************************
 * Copyright (c) 2009 EclipseSource and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *   EclipseSource - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.core.identity;

import java.net.URI;
import org.eclipse.core.runtime.Assert;

/**
 * URI ID class.
 * 
 * @since 3.0
 */
public class URIID extends BaseID implements IResourceID {

	private static final long serialVersionUID = 7328962407044918278L;
	private final URI uri;

	public URIID(Namespace namespace, URI uri) {
		super(namespace);
		Assert.isNotNull(uri);
		this.uri = uri;
	}

	protected int namespaceCompareTo(BaseID o) {
		if (this == o)
			return 0;
		if (!this.getClass().equals(o.getClass()))
			return Integer.MIN_VALUE;
		return this.uri.compareTo(((URIID) o).uri);
	}

	protected boolean namespaceEquals(BaseID o) {
		if (this == o)
			return true;
		if (!this.getClass().equals(o.getClass()))
			return false;
		return this.uri.equals(((URIID) o).uri);
	}

	protected String namespaceGetName() {
		return uri.toString();
	}

	protected int namespaceHashCode() {
		return uri.hashCode();
	}

	public URI toURI() {
		return uri;
	}

}