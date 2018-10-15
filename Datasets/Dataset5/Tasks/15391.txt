public interface IMultiRosterContentProvider extends ITreeContentProvider {

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

package org.eclipse.ecf.presence.ui;

import org.eclipse.ecf.presence.roster.IRoster;
import org.eclipse.jface.viewers.ITreeContentProvider;

/**
 * Contract implemented by RosterContentProviders.
 * 
 */
public interface IRosterContentProvider extends ITreeContentProvider {

	/**
	 * Add roster to set of known rosters for this content provider.
	 * 
	 * @param roster the roster to add
	 * @return true if roster successfully added. False otherwise.
	 */
	public boolean add(IRoster roster);
	/**
	 * Remove roster from set of known rosters for this content provider.
	 * 
	 * @param roster the roster to remove
	 * @return true if roster successfully removed. False otherwise.
	 */
	public boolean remove(IRoster roster);
	
}