import org.eclipse.wst.xml.vex.ui.internal.contentassist.MorphAssistant;

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
package org.eclipse.wst.xml.vex.ui.internal.action;

import org.eclipse.wst.xml.vex.core.internal.widget.IVexWidget;
import org.eclipse.wst.xml.vex.ui.internal.action.IVexAction;
import org.eclipse.wst.xml.vex.ui.internal.editor.MorphAssistant;
import org.eclipse.wst.xml.vex.ui.internal.swt.VexWidget;

/**
 * Displays the Change Element dialog.
 */
public class ChangeElementAction implements IVexAction {

	public void run(IVexWidget vexWidget) {
		new MorphAssistant().show((VexWidget) vexWidget);
	}

	public boolean isEnabled(IVexWidget vexWidget) {
		return true;
	}

}