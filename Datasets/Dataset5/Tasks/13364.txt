import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IVEXElement;

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
package org.eclipse.wst.xml.vex.ui.internal.outline;

import org.eclipse.jface.viewers.IBaseLabelProvider;
import org.eclipse.jface.viewers.ITreeContentProvider;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;
import org.eclipse.wst.xml.vex.ui.internal.editor.VexEditor;

/**
 * Implemented by objects that can provide a document outline.
 */
public interface IOutlineProvider {

	/**
	 * Initialize this outline provider. This method is guaranteed to be called
	 * befor any other in this class. The document has been fully created by the
	 * time this method is called, so it is acceptable to access the Vex Widget
	 * and its associated stylesheet and document.
	 * 
	 * @param editor
	 *            VexEditor with which this outline page is associated.
	 */
	public void init(VexEditor editor);

	/**
	 * Returns the content provider that supplies elements representing the
	 * document outline.
	 */
	public ITreeContentProvider getContentProvider();

	/**
	 * Returns the label provider for the outline.
	 */
	public IBaseLabelProvider getLabelProvider();

	/**
	 * Returns the outline element closest to the given child. If
	 * <code>child</code> is an outline element, it is returned directly.
	 * 
	 * @param child
	 *            Element for which to find the outline element.
	 */
	public IVEXElement getOutlineElement(IVEXElement child);
}