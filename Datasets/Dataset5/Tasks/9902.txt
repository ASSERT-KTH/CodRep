new ListenerList<ISelectionChangedListener, SelectionChangedEvent>(ISelectionChangedListener.class);

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
package org.eclipse.wst.xml.vex.ui.internal.editor;

import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.wst.xml.vex.core.internal.core.ListenerList;

/**
 * Implementation of ISelectionProvider. This class is also an
 * ISelectionChangedListener; any events received by selectionChanged are
 * relayed to registered listeners.
 */
public class SelectionProvider implements ISelectionProvider,
		ISelectionChangedListener {

	ISelection selection;
	private ListenerList<ISelectionChangedListener, SelectionChangedEvent> listeners =
		new ListenerList<ISelectionChangedListener, SelectionChangedEvent>();

	public void addSelectionChangedListener(ISelectionChangedListener listener) {
		this.listeners.add(listener);
	}

	/**
	 * Fire a SelectionChangedEvent to all registered listeners.
	 * 
	 * @param e Event to be passed to the listeners' selectionChanged method.
	 */
	public void fireSelectionChanged(SelectionChangedEvent e) {
		this.selection = e.getSelection();
		this.listeners.fireEvent("selectionChanged", e); //$NON-NLS-1$
	}

	public ISelection getSelection() {
		return this.selection;
	}

	public void removeSelectionChangedListener(
			ISelectionChangedListener listener) {
		this.listeners.remove(listener);
	}

	public void setSelection(ISelection selection) {
		this.selection = selection;
	}

	public void selectionChanged(SelectionChangedEvent event) {
		this.fireSelectionChanged(event);
	}

}