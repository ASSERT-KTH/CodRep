public IIDEntry store(ID id) {

/****************************************************************************
 * Copyright (c) 2008 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.internal.storage;

import java.util.ArrayList;
import java.util.List;
import org.eclipse.core.runtime.IAdapterManager;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.ecf.storage.*;
import org.eclipse.equinox.security.storage.*;

/**
 *
 */
public class IDStore implements IIDStore {

	private static final String idStoreNameSegment = "/ECF/Namespace"; //$NON-NLS-1$
	private static final INamespaceEntry[] EMPTY_ARRAY = {};

	private String getIDAsString(ID id) {
		final IIDStoreAdapter idadapter = (IIDStoreAdapter) id.getAdapter(IIDStoreAdapter.class);
		final String idName = (idadapter != null) ? idadapter.getNameForStorage() : id.toExternalForm();
		if (idName == null || idName.equals("")) //$NON-NLS-1$
			return null;
		return EncodingUtils.encodeSlashes(idName);
	}

	protected ISecurePreferences getRoot() {
		return SecurePreferencesFactory.getDefault();
	}

	protected ISecurePreferences getNamespaceRoot() {
		ISecurePreferences root = getRoot();
		if (root == null)
			return null;
		return root.node(idStoreNameSegment);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.storage.IIDStore#getEntry(org.eclipse.ecf.core.identity.ID)
	 */
	public IIDEntry getEntry(ID id) {
		ISecurePreferences namespaceRoot = getNamespaceRoot();
		if (namespaceRoot == null)
			return null;
		INamespaceEntry namespaceEntry = getNamespaceEntry(id.getNamespace());
		final String idAsString = getIDAsString(id);
		if (idAsString == null)
			return null;
		return new IDEntry(namespaceEntry.getPreferences().node(idAsString));
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.storage.IIDStore#getNamespaceEntries()
	 */
	public INamespaceEntry[] getNamespaceEntries() {
		ISecurePreferences namespaceRoot = getNamespaceRoot();
		if (namespaceRoot == null)
			return EMPTY_ARRAY;
		List results = new ArrayList();
		String names[] = namespaceRoot.childrenNames();
		for (int i = 0; i < names.length; i++)
			results.add(new NamespaceEntry(namespaceRoot.node(names[i])));
		return (INamespaceEntry[]) results.toArray(new INamespaceEntry[] {});
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ecf.storage.IIDStore#getNamespaceEntry(org.eclipse.ecf.core.identity.Namespace)
	 */
	public INamespaceEntry getNamespaceEntry(Namespace namespace) {
		if (namespace == null)
			return null;
		final INamespaceStoreAdapter nsadapter = (INamespaceStoreAdapter) namespace.getAdapter(INamespaceStoreAdapter.class);
		final String nsName = (nsadapter != null) ? nsadapter.getNameForStorage() : namespace.getName();
		if (nsName == null)
			return null;
		ISecurePreferences namespaceRoot = getNamespaceRoot();
		if (namespaceRoot == null)
			return null;
		return new NamespaceEntry(namespaceRoot.node(nsName));
	}

	/* (non-Javadoc)
	 * @see org.eclipse.core.runtime.IAdaptable#getAdapter(java.lang.Class)
	 */
	public Object getAdapter(Class adapter) {
		if (adapter == null)
			return null;
		if (adapter.isInstance(this)) {
			return this;
		}
		IAdapterManager adapterManager = Activator.getDefault().getAdapterManager();
		return (adapterManager == null) ? null : adapterManager.loadAdapter(this, adapter.getName());
	}
}