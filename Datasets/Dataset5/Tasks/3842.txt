public IIDEntry store(ID id);

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

package org.eclipse.ecf.storage;

import org.eclipse.core.runtime.IAdaptable;
import org.eclipse.ecf.core.identity.ID;
import org.eclipse.ecf.core.identity.Namespace;
import org.eclipse.equinox.security.storage.ISecurePreferences;

/**
 * ID storage service interface.  This interface defines access for storing and retrieving ID instances.  
 * It also allows creating ID instances from previously stored {@link IIDEntry}s.
 */
public interface IIDStore extends IAdaptable {

	/**
	 * Get the {@link INamespaceEntry}s previously stored in this IIDStore.
	 * 
	 * @return array of {@link INamespaceEntry}s that have been previously stored in this store.  
	 * Will return <b>empty array</b> if no INamespaceEntries have been previously stored, and will return <code>null</code>
	 * if the underlying {@link ISecurePreferences} store cannot be accessed.  
	 * <p>
	 * </p>
	 * Each INamespaceEntry represents a distinct {@link Namespace} that has previously been stored in this store.
	 */
	public INamespaceEntry[] getNamespaceEntries();

	/**
	 * Get the given {@link INamespaceEntry} in this store.
	 * 
	 * @param namespace the {@link Namespace} to get.  Must not be <code>null</code>.
	 * @return the {@link INamespaceEntry} for the given {@link Namespace}.  Will not return <code>null</code>.  If entry
	 * was not present previously, it will be created.
	 */
	public INamespaceEntry getNamespaceEntry(Namespace namespace);

	/**
	 * Get {@link IIDEntry} in this IDStore for a given ID.  If an IIDEntry did not exist in this store previously, 
	 * one is created.  If it did exist in this store previously the existing one is
	 * returned.
	 * @param id the ID to get the IIDEntry for.
	 * @return ISecurePreferences for the given ID.  Will not return <code>null</code>.  
	 * Will return an existing {@link IIDEntry} if ID is already present, and a new {@link IIDEntry} if not previously
	 * stored.
	 */
	public IIDEntry getEntry(ID id);

}