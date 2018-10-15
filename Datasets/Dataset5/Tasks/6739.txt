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
 * Restore the selection to what it was before it last changed.
 */
public class RestoreLastSelectionAction extends AbstractVexAction {

	public void run(IVexWidget vexWidget) {
		throw new UnsupportedOperationException(
				"RestoreLastSelectionAction is not yet implemented.");
	}

	public boolean isEnabled(IVexWidget vexWidget) {
		return false;
	}
}