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
 * Interface implemented by command objects that can act on a VexWidget.
 */
public interface IVexAction {

	/**
	 * Performs the action on the VexWidget.
	 * 
	 * @param vexWidget
	 *            IVexWidget on which the action is to be performed.
	 */
	public void run(IVexWidget vexWidget);

	/**
	 * Returns true if the action is valid for the given VexWidget.
	 * 
	 * @param vexWidget
	 *            IVexWidget against which to test validity.
	 */
	public boolean isEnabled(IVexWidget vexWidget);
}