public interface Position {

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
package org.eclipse.wst.xml.vex.core.internal.provisional.dom;

/**
 * Represents a logical location in a document. As the document is modified,
 * existing <code>Position</code> objects are updated to reflect the appropriate
 * character offset in the document.
 * @model
 */
public interface IPosition {

	/**
	 * Returns the character offset corresponding to the position.
	 * @model
	 */
	public int getOffset();
}