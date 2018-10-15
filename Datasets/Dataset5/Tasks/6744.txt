import org.eclipse.wst.xml.vex.ui.internal.swt.VexWidget;

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

import java.text.MessageFormat;

import org.eclipse.jface.action.IAction;
import org.eclipse.wst.xml.vex.core.internal.swt.VexWidget;

/**
 * Content assistant that shows valid elements to be inserted at the current
 * point.
 */
public class MorphAssistant extends ContentAssistant {

	public IAction[] getActions(VexWidget vexWidget) {
		return vexWidget.getValidMorphActions();
	}

	public String getTitle(VexWidget vexWidget) {
		String message = Messages
				.getString("ChangeElementAction.dynamic.label"); //$NON-NLS-1$
		String name = vexWidget.getCurrentElement().getName();
		return MessageFormat.format(message, new Object[] { name });
	}

}