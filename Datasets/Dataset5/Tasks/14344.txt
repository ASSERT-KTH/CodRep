.addActionSet("org.eclipse.ecf.example.collab.ui.actionSet"); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2000, 2007 IBM Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.internal.example.collab.ui.perspective;

import org.eclipse.ecf.internal.example.collab.ui.CollabDiscoveryView;
import org.eclipse.ecf.internal.example.collab.ui.LineChatView;
import org.eclipse.ecf.presence.ui.MessagesView;
import org.eclipse.ecf.presence.ui.MultiRosterView;
import org.eclipse.ecf.presence.ui.chatroom.ChatRoomManagerView;
import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

public class CommunicationPerspective implements IPerspectiveFactory {

	public void createInitialLayout(IPageLayout layout) {
		defineActions(layout);
		defineLayout(layout);
	}

	private void defineActions(IPageLayout layout) {
		// Add "new wizards".
		layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.folder");//$NON-NLS-1$
		layout.addNewWizardShortcut("org.eclipse.ui.wizards.new.file");//$NON-NLS-1$

		// Add "show views".
		layout.addShowViewShortcut(IPageLayout.ID_RES_NAV);
		layout.addShowViewShortcut(IPageLayout.ID_BOOKMARKS);
		layout.addShowViewShortcut(IPageLayout.ID_OUTLINE);
		layout.addShowViewShortcut(IPageLayout.ID_PROP_SHEET);
		layout.addShowViewShortcut(IPageLayout.ID_PROBLEM_VIEW);
		layout.addShowViewShortcut(IPageLayout.ID_PROGRESS_VIEW);
		layout.addShowViewShortcut(IPageLayout.ID_TASK_LIST);

		layout
				.addActionSet("org.eclipse.ecf.internal.example.collab.ui.actionSet"); //$NON-NLS-1$
	}

	private void defineLayout(IPageLayout layout) {
		// Editors are placed for free.
		String editorArea = layout.getEditorArea();

		// Top left.
		IFolderLayout topLeft = layout.createFolder("topLeft", //$NON-NLS-1$
				IPageLayout.LEFT, (float) 0.26, editorArea);
		topLeft.addView("org.eclipse.ui.navigator.ProjectExplorer"); //$NON-NLS-1$
		topLeft.addPlaceholder(IPageLayout.ID_BOOKMARKS);

		// Bottom left.
		IFolderLayout bottomLeft = layout.createFolder(
				"bottomLeft", IPageLayout.BOTTOM, 0.50f,//$NON-NLS-1$
				"topLeft");//$NON-NLS-1$
		bottomLeft.addView(IPageLayout.ID_OUTLINE);
		bottomLeft.addPlaceholder(MultiRosterView.VIEW_ID);

		// Bottom right.
		IFolderLayout bottomRight = layout.createFolder("bottomRight", //$NON-NLS-1$
				IPageLayout.BOTTOM, 0.66f, editorArea);

		bottomRight.addView(IPageLayout.ID_PROBLEM_VIEW);
		bottomRight.addView(IPageLayout.ID_TASK_LIST);
		bottomRight.addView(LineChatView.VIEW_ID);
		bottomRight.addPlaceholder(CollabDiscoveryView.VIEW_ID);
		bottomRight.addPlaceholder(ChatRoomManagerView.VIEW_ID);
		bottomRight.addPlaceholder(MessagesView.VIEW_ID);
	}
}