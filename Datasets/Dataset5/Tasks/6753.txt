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
 * Represents a class that can fire selection change events to
 * {@link SelectionChangeListener}s.
 */
public interface SelectionProvider {

	/**
	 * Add the given {@link SelectionChangeListener} to be notified when the
	 * current selection changes.
	 * 
	 * @param listener
	 *            SelectionChangeListener to add.
	 */
	public void addSelectionListener(SelectionListener listener);

	/**
	 * Remove the given {@link SelectionChangeListener} from the notification
	 * list.
	 * 
	 * @param listener
	 *            SelectionChangeListener to remove.
	 */
	public void removeSelectionListener(SelectionListener listener);

}