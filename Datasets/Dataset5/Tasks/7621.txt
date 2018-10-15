stackshare.sendShareConsoleSelection(entry.getRoster().getUser().getName(), entry.getUser().getID(), selection.getText());

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/
package org.eclipse.ecf.presence.collab.ui.console;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.datashare.IChannelContainerAdapter;
import org.eclipse.ecf.internal.presence.collab.ui.Activator;
import org.eclipse.ecf.internal.presence.collab.ui.Messages;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.ui.roster.AbstractRosterEntryContributionItem;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.text.TextSelection;

public class ConsoleShareRosterEntryContributionItem extends AbstractRosterEntryContributionItem {

	public ConsoleShareRosterEntryContributionItem() {
	}

	public ConsoleShareRosterEntryContributionItem(String id) {
		super(id);
	}

	protected IAction[] makeActions() {
		final TextSelection selection = ConsoleShare.getSelection();
		if (selection == null)
			return null;
		// Else check for Roster entry
		final IRosterEntry entry = getSelectedRosterEntry();
		final IContainer c = getContainerForRosterEntry(entry);
		// If roster entry is selected and it has a container
		if (entry != null && c != null) {
			final IChannelContainerAdapter channelAdapter = (IChannelContainerAdapter) c.getAdapter(IChannelContainerAdapter.class);
			// If the container has channel container adapter and is online/available
			if (channelAdapter != null && isAvailable(entry)) {
				final ConsoleShare tmp = ConsoleShare.getStackShare(c.getID());
				// If there is an URL share associated with this container
				if (tmp != null) {
					final ConsoleShare stackshare = tmp;
					final IAction action = new Action() {
						public void run() {
							stackshare.sendShareStackRequest(entry.getRoster().getUser().getName(), entry.getUser().getID(), selection.getText());
						}
					};
					action.setText(Messages.ConsoleShare_RosterEntryMenu);
					action.setImageDescriptor(Activator.imageDescriptorFromPlugin(Activator.PLUGIN_ID, Messages.ConsoleShare_RosterContributionItem_CONSOLE_ICON));
					return new IAction[] {action};
				}
			}
		}
		return null;
	}
}