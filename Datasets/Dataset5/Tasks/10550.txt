urlshare.sendURL(entry.getRoster().getUser().getName(),entry.getUser().getID());

package org.eclipse.ecf.presence.collab.ui;

import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.datashare.IChannelContainerAdapter;
import org.eclipse.ecf.internal.presence.collab.ui.Activator;
import org.eclipse.ecf.internal.presence.collab.ui.Messages;
import org.eclipse.ecf.presence.roster.IRosterEntry;
import org.eclipse.ecf.presence.ui.roster.AbstractRosterEntryContributionItem;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;

public class URLShareRosterEntryContributionItem extends
		AbstractRosterEntryContributionItem {

	public URLShareRosterEntryContributionItem() {
	}

	public URLShareRosterEntryContributionItem(String id) {
		super(id);
	}

	protected IAction[] makeActions() {
		// Else check for Roster entry
		final IRosterEntry entry = getSelectedRosterEntry();
		IContainer c = getContainerForRosterEntry(entry);
		// If roster entry is selected and it has a container
		if (entry != null && c != null) {
			final IChannelContainerAdapter channelAdapter = (IChannelContainerAdapter) c
					.getAdapter(IChannelContainerAdapter.class);
			// If the container has channel container adapter and is online/available
			if (channelAdapter != null && isAvailable(entry)) {
				URLShare tmp = URLShareRosterContributionItem.getURLShare(c
						.getID());
				// If there is an URL share associated with this container
				if (tmp != null) {
					final URLShare urlshare = tmp;
					IAction action = new Action() {
						public void run() {
							urlshare.sendURL(entry.getUser().getID());
						}
					};
					action
							.setText(Messages.URLShareRosterEntryContributionItem_SEND_URL_MENU_TEXT);
					action.setImageDescriptor(Activator.imageDescriptorFromPlugin(
							Activator.PLUGIN_ID, Messages.URLShareRosterContributionItem_BROWSER_ICON));
					return new IAction[] { action };
				}
			}
		}
		return null;
	}

}