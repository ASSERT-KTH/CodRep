package org.eclipse.wst.xml.vex.ui.internal.action;

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
package org.eclipse.wst.xml.vex.core.internal.action;

import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;

/**
 * Abstract Vex action. This class provides default implementations for all
 * methods in IVexAction except for <code>run</code>.
 */
public abstract class AbstractVexAction implements IVexAction {

	/**
	 * Class constructor.
	 */
	public AbstractVexAction() {
	}

	/**
	 * Returns <code>true</code>.
	 */
	public boolean isEnabled(IVexWidget vexWidget) {
		return true;
	}

}