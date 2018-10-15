package org.eclipse.wst.xml.vex.ui.internal.swing;

/*******************************************************************************
 * Copyright (c) 2004, 2008 John Krasnay and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors:
 *     John Krasnay - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.vex.core.internal.swing;

/**
 * Interface for receiving selection change events. Typically, objects
 * implementing this interface are registered with a {@link SelectionProvider}.
 * 
 * @see Selection
 */
public interface SelectionListener {

	/**
	 * Called by a selection provider when the current selection changes.
	 * 
	 * @param selection
	 *            the new {@link Selection}.
	 */
	public void selectionChanged(Selection selection);
}