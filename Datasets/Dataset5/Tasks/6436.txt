//this.setToolTipText(Messages.getString(key + ".tooltip")); //$NON-NLS-1$

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

import org.eclipse.jface.action.Action;
import org.eclipse.wst.xml.vex.ui.internal.action.IVexAction;
import org.eclipse.wst.xml.vex.ui.internal.editor.Messages;
import org.eclipse.wst.xml.vex.ui.internal.editor.VexEditor;
import org.eclipse.wst.xml.vex.ui.internal.swt.VexWidget;

/**
 * Adapts a JFace Action to an IVexAction instance. The ID and definition ID of
 * the resulting action is set to the classname of the action. Localized strings
 * for the action are pulled from the classname of the given action. For
 * example, if the action is
 * "org.eclipse.wst.vex.ui.internal.action.PasteTextAction", the following
 * properties are retrieved from plugin.xml:
 * 
 * <dl>
 * <dt>PasteTextAction.label</dt>
 * <dd>The action's label.</dd>
 * <dt>PasteTextAction.tooltip</dt>
 * <dd>The action's tooltip.</dd>
 * </dl>
 */
public class VexActionAdapter extends Action {

	/**
	 * Class constructor.
	 * 
	 * @param editor
	 *            VexEditor to which the action will apply.
	 * @param action
	 *            IVexAction to be invoked.
	 */
	public VexActionAdapter(VexEditor editor, IVexAction action) {

		this.editor = editor;
		this.action = action;

		String id = action.getClass().getName();
		int i = id.lastIndexOf("."); //$NON-NLS-1$
		String key = id.substring(i + 1);

		this.setId(id);
		this.setActionDefinitionId(id);
		this.setText(Messages.getString(key + ".label")); //$NON-NLS-1$
		this.setToolTipText(Messages.getString(key + ".tooltip")); //$NON-NLS-1$
	}

	public void run() {
		VexWidget vexWidget = this.editor.getVexWidget();
		if (vexWidget != null) {
			this.action.run(vexWidget);
		}
	}

	private VexEditor editor;
	private IVexAction action;
}