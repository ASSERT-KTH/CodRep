return Messages.getString("dialog.addElement.title"); //$NON-NLS-1$

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
package org.eclipse.wst.xml.vex.ui.internal.contentassist;

import org.eclipse.jface.action.IAction;
import org.eclipse.wst.xml.vex.ui.internal.editor.Messages;
import org.eclipse.wst.xml.vex.ui.internal.swt.VexWidget;

/**
 * Content assistant that shows valid elements to be inserted at the current
 * point.
 */
public class InsertAssistant extends ContentAssistant {

	public IAction[] getActions(VexWidget vexWidget) {
		return vexWidget.getValidInsertActions();
	}

	public String getTitle(VexWidget vexWidget) {
		return Messages.getString("InsertAssistant.title"); //$NON-NLS-1$
	}
}