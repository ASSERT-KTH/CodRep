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
package org.eclipse.wst.xml.vex.core.internal.css;

import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IVEXElement;

/**
 * Represents a :before or :after pseudo-element.
 */
public class PseudoElement extends Element {

	public static final String AFTER = "after";
	public static final String BEFORE = "before";

	/**
	 * Class constructor.
	 * 
	 * @param parent
	 *            Parent element to this pseudo-element.
	 * @param name
	 *            Name of this pseudo-element, e.g. PseudoElement.BEFORE.
	 */
	public PseudoElement(IVEXElement parent, String name) {
		super(name);
		this.setParent(parent);
	}

	/**
	 * @see java.lang.Object#equals(java.lang.Object)
	 */
	public boolean equals(Object o) {
		if (o == null || o.getClass() != this.getClass()) {
			return false;
		}
		PseudoElement other = (PseudoElement) o;
		return this.getParent() == other.getParent()
				&& this.getName().equals(other.getName());
	}

	/**
	 * @see java.lang.Object#hashCode()
	 */
	public int hashCode() {
		return this.getParent().hashCode() + this.getName().hashCode();
	}
}