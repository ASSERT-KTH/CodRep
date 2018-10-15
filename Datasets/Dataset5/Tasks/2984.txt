package org.eclipse.wst.xml.vex.ui.internal.perspective;

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

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

/**
 * Implements the Document perspective.
 */
public class DocumentPerspective implements IPerspectiveFactory {

	public void createInitialLayout(IPageLayout layout) {
		defineActions(layout);
		defineLayout(layout);
	}

	/**
	 * Defines the initial actions for a page.
	 */
	public void defineActions(IPageLayout layout) {
		// Add "new wizards".
		layout
				.addNewWizardShortcut("org.eclipse.wst.xml.vex.ui.NewDocumentWizard");//$NON-NLS-1$
		layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.folder");//$NON-NLS-1$
		layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.file");//$NON-NLS-1$

		layout.addShowViewShortcut(IPageLayout.ID_RES_NAV);
		layout.addShowViewShortcut(IPageLayout.ID_OUTLINE);
		layout.addShowViewShortcut(IPageLayout.ID_PROP_SHEET);

		// layout.addActionSet(IPageLayout.ID_NAVIGATE_ACTION_SET);
	}

	/**
	 * Defines the initial layout for a page.
	 */
	public void defineLayout(IPageLayout layout) {

		String editorArea = layout.getEditorArea();

		IFolderLayout topLeft = layout.createFolder(
				"topLeft", IPageLayout.LEFT, (float) 0.2, editorArea);//$NON-NLS-1$
		topLeft.addView(IPageLayout.ID_RES_NAV);

		IFolderLayout topRight = layout.createFolder(
				"topRight", IPageLayout.RIGHT, (float) 0.75, editorArea);//$NON-NLS-1$
		topRight.addView(IPageLayout.ID_OUTLINE);

		IFolderLayout bottomRight = layout.createFolder(
				"bottomRight", IPageLayout.BOTTOM, (float) 0.5, "topRight");//$NON-NLS-1$ //$NON-NLS-2$
		bottomRight.addView(IPageLayout.ID_PROP_SHEET);

	}

}