package org.eclipse.ecf.internal.presence.ui.handlers;

/*******************************************************************************
 * Copyright (c) 2007 Chris Aniszczyk and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Chris Aniszczyk <caniszczyk@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.presence.ui.handlers;

import org.eclipse.core.commands.AbstractHandler;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.ExecutionException;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.internal.presence.ui.Activator;
import org.eclipse.ecf.presence.im.IChatManager;
import org.eclipse.ecf.presence.im.IChatMessageSender;
import org.eclipse.ecf.presence.im.ITypingMessageSender;
import org.eclipse.ecf.presence.roster.IRoster;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.ui.MessagesView;
import org.eclipse.jface.window.Window;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.handlers.HandlerUtil;

/**
 * Our sample handler extends AbstractHandler, an IHandler base class.
 * @see org.eclipse.core.commands.IHandler
 * @see org.eclipse.core.commands.AbstractHandler
 */
public class BrowseHandler extends AbstractHandler {
	/**
	 * The constructor.
	 */
	public BrowseHandler() {}

	/**
	 * the command has been executed, so extract extract the needed information
	 * from the application context.
	 */
	public Object execute(ExecutionEvent event) throws ExecutionException {
		IWorkbenchWindow window = 
			HandlerUtil.getActiveWorkbenchWindowChecked(event);
		
		IContainerManager containerManager = Activator.getDefault().getContainerManager();
		IContainer[] containers = containerManager.getAllContainers();
		
		BrowseDialog dialog = new BrowseDialog(window.getShell(), containers);
		int status = dialog.open();
		if(status == Window.OK) {
			Object[] object = dialog.getResult();
			IRosterEntry entry = (IRosterEntry) object[0];
			IRoster roster = entry.getRoster();
			if (roster != null) {
				IChatManager manager = 
					roster.getPresenceContainerAdapter().getChatManager();
				IChatMessageSender icms = manager.getChatMessageSender();
				ITypingMessageSender itms = manager.getTypingMessageSender();
				try {
					MessagesView view = 
						(MessagesView) window.getActivePage().showView(MessagesView.VIEW_ID);
					view.selectTab(icms, itms, roster.getUser().getID(), entry
							.getUser().getID());
				} catch (PartInitException e) {
					e.printStackTrace();
				}
			}
		}
		
		return null;
	}
}