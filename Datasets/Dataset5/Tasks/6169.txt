private ImageDescriptor topMenuImageDescriptor = Activator.getDefault().getImageRegistry().getDescriptor(Activator.COLLABORATION_IMAGE);

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
package org.eclipse.ecf.presence.ui.menu;

import java.util.*;
import org.eclipse.core.commands.Command;
import org.eclipse.core.commands.IHandler;
import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.core.IContainer;
import org.eclipse.ecf.core.IContainerManager;
import org.eclipse.ecf.internal.presence.ui.Activator;
import org.eclipse.ecf.presence.IPresence;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.roster.*;
import org.eclipse.ecf.ui.SharedImages;
import org.eclipse.jface.action.*;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.actions.CompoundContributionItem;
import org.eclipse.ui.commands.ICommandService;
import org.eclipse.ui.handlers.IHandlerService;
import org.eclipse.ui.menus.CommandContributionItem;
import org.eclipse.ui.services.IServiceLocator;

/**
 * A contribution that dynamically constructs a menu for the currently connected rosters.  
 * This class may be subclassed in order to create a {@link AbstractRosterMenuHandler} for 
 * handling selection of a given {@link IRosterEntry} from the menu.
 */
public abstract class AbstractRosterMenuContributionItem extends CompoundContributionItem {

	private static final String DEFAULT_TOP_MENU_NAME = "Share"; //$NON-NLS-1$

	protected static final IContributionItem[] NO_CONTRIBUTIONS = new IContributionItem[] {};

	private static final String ROSTERCOMMAND_PREFIX = "org.eclipse.ecf.presence.ui.rosterCommand."; //$NON-NLS-1$
	private static final List contributionItems = new ArrayList();
	private static final List handlerActivations = new ArrayList();
	private static int commandIdIndex = 0;

	private IServiceLocator serviceLocator;
	private IHandlerService handlerService;
	private ICommandService commandService;

	private String topMenuName = DEFAULT_TOP_MENU_NAME;

	private ImageDescriptor topMenuImageDescriptor = Activator.getDefault().getImageRegistry().getDescriptor(Activator.CONTACTS_IMAGE);

	protected void setTopMenuName(String name) {
		this.topMenuName = name;
	}

	public void setTopMenuImageDescriptor(ImageDescriptor image) {
		this.topMenuImageDescriptor = image;
	}

	protected ImageDescriptor getTopMenuImageDescriptor() {
		return this.topMenuImageDescriptor;
	}

	private void initialize() {
		serviceLocator = PlatformUI.getWorkbench();
		Assert.isNotNull(serviceLocator);
		handlerService = (IHandlerService) serviceLocator.getService(IHandlerService.class);
		Assert.isNotNull(handlerService);
		commandService = (ICommandService) serviceLocator.getService(ICommandService.class);
		Assert.isNotNull(commandService);
	}

	public AbstractRosterMenuContributionItem() {
		initialize();
	}

	public AbstractRosterMenuContributionItem(String id) {
		super(id);
		initialize();
	}

	/**
	 * Create contribution items for a given roster.  Subclasses may override as appropriate
	 * to customize the creation of contributions with an alternative strategy.
	 * @param roster the roster to create contribution items for.  Must not be <code>null</code>.
	 * @return IContributionItem[] for given IRoster.  Will not return <code>null</code>.
	 * 
	 */
	protected IContributionItem[] createContributionItemsForRoster(IRoster roster) {
		Collection rosterItems = roster.getItems();
		List contributions = new ArrayList();
		for (Iterator i = rosterItems.iterator(); i.hasNext();) {
			IRosterItem item = (IRosterItem) i.next();
			IContributionItem[] adds = null;
			if (item instanceof IRosterEntry) {
				adds = createContributionItemsForEntry((IRosterEntry) item);
			} else if (item instanceof IRosterGroup) {
				adds = createContributionItemsForGroup((IRosterGroup) item);
			}
			if (adds != null) {
				for (int j = 0; j < adds.length; j++) {
					contributions.add(adds[j]);
				}
			}
		}
		return (IContributionItem[]) contributions.toArray(new IContributionItem[] {});
	}

	/**
	 * Create contribution items for a given roster.  Subclasses may override as appropriate
	 * to customize the creation of contributions with an alternative strategy.
	 * @param group the IRosterGroup to create contribution items for.  Must not be <code>null</code>.
	 * @return IContributionItem[] for given IRosterGroup.  Will not return <code>null</code>.
	 * 
	 */
	protected IContributionItem[] createContributionItemsForGroup(IRosterGroup group) {
		Collection entries = group.getEntries();
		MenuManager menuManager = null;
		for (Iterator i = entries.iterator(); i.hasNext();) {
			IRosterEntry entry = (IRosterEntry) i.next();
			IContributionItem[] menuContributions = createContributionItemsForEntry(entry);
			if (menuContributions != null && menuContributions.length > 0) {
				for (int j = 0; j < menuContributions.length; j++) {
					if (menuManager == null) {
						menuManager = createMenuManagerForGroup(group);
					}
					menuManager.add(menuContributions[j]);
				}
			}
		}
		if (menuManager != null)
			return new IContributionItem[] {menuManager};
		return NO_CONTRIBUTIONS;
	}

	/**
	 * Create a MenuManager for the given {@link IRosterGroup}.
	 * @param group the IRosterGroup to create the menu manager for.  Will not be <code>null</code>.
	 * @return the menu manager.  Should not be <code>null</code>.
	 */
	protected MenuManager createMenuManagerForGroup(IRosterGroup group) {
		return new MenuManager(group.getName(), SharedImages.getImageDescriptor(SharedImages.IMG_GROUP), null);
	}

	/**
	 * Create contribution items for a given presence container adapter.  Subclasses may override as 
	 * appropriate to customize the creation of contributions with an alternative strategy.
	 * @param presenceContainerAdapter the IPresenceContainerAdapter to create contribution items for.  Must not be <code>null</code>.
	 * @return IContributionItem[] for given IPresenceContainerAdapter.  Will not return <code>null</code>.
	 * 
	 */
	protected IContributionItem[] createContributionItemsForPresenceContainer(IPresenceContainerAdapter presenceContainerAdapter) {
		IRoster roster = presenceContainerAdapter.getRosterManager().getRoster();
		IContributionItem[] contributions = createContributionItemsForRoster(roster);
		if (contributions == null || contributions.length == 0)
			return NO_CONTRIBUTIONS;
		MenuManager menuManager = createMenuManagerForRoster(roster);
		for (int i = 0; i < contributions.length; i++) {
			menuManager.add(contributions[i]);
		}
		return new IContributionItem[] {menuManager};
	}

	/**
	 * Create a MenuManager for the given {@link IRosterGroup}.
	 * @param roster the IRosterGroup to create the menu manager for.  Will not be <code>null</code>.
	 * @return the menu manager.  Should not be <code>null</code>.
	 */
	protected MenuManager createMenuManagerForRoster(IRoster roster) {
		return new MenuManager(roster.getUser().getName(), SharedImages.getImageDescriptor(SharedImages.IMG_IDENTITY), null);
	}

	private int getNextCommandIdIndex() {
		return commandIdIndex++;
	}

	/**
	 * Create a {@link AbstractRosterMenuHandler} for a given IRosterEntry instance.  Implementers of this method
	 * should construct and return a new {@link AbstractRosterMenuHandler}.  When a menu selection is made for 
	 * a given {@link IRosterEntry} menu item, the associated {@link AbstractRosterMenuHandler} instance will have its
	 * {@link AbstractRosterMenuHandler#execute(org.eclipse.core.commands.ExecutionEvent)} method will
	 * be called.  This way, subclasses may define arbitrary behavior for the dynamic menu item
	 * selection.
	 *  
	 * @param rosterEntry the {@link IRosterEntry} for the {@link AbstractRosterMenuHandler}.  Will not be <code>null</code>.
	 * @return {@link AbstractRosterMenuHandler} instance.  Must not be <code>null</code>.
	 */
	protected abstract AbstractRosterMenuHandler createRosterEntryHandler(IRosterEntry rosterEntry);

	/**
	 * Determines whether given entry should be added for IContribution.  This implementation only
	 * returns <code>true</code> if the given {@link IRosterEntry#getPresence()} IPresence.Type is
	 * AVAILABLE, and IPresence.Mode is AVAILABLE.  Subclasses may override as appropriate
	 * to customize the behavior of this contribution item.
	 * 
	 * @param entry the IRosterEntry to check.  Must not be <code>null</code>.
	 * @return <code>true</code> if the given IRosterEntry should be added, <code>false</code> otherwise.
	 */
	protected boolean addEntry(IRosterEntry entry) {
		IPresence presence = entry.getPresence();
		if (presence == null)
			return false;
		return (presence.getType().equals(IPresence.Type.AVAILABLE) && presence.getMode().equals(IPresence.Mode.AVAILABLE));
	}

	/**
	 * Create contribution items for a given roster entry.  Subclasses may override as 
	 * appropriate to customize the creation of contributions with an alternative strategy.
	 * @param entry the IRosterEntry to create contribution items for.  Must not be <code>null</code>.
	 * @return IContributionItem[] for given IPresenceContainerAdapter.  Will not return <code>null</code>.
	 * 
	 */
	protected IContributionItem[] createContributionItemsForEntry(IRosterEntry entry) {
		if (addEntry(entry)) {
			String commandId = ROSTERCOMMAND_PREFIX + getNextCommandIdIndex();
			// Get existing/new command
			Command command = commandService.getCommand(commandId);
			command.define(commandId, null, commandService.getCategory(commandId + ".c")); //$NON-NLS-1$
			IHandler handler = command.getHandler();
			// Only mess with it if it was of old type
			if (handler != null && handler instanceof AbstractRosterMenuHandler) {
				AbstractRosterMenuHandler drh = (AbstractRosterMenuHandler) handler;
				if (drh != null) {
					drh.fireHandlerChangeEvent();
					drh.dispose();
				}
			}
			IHandler newHandler = createRosterEntryHandler(entry);
			command.setHandler(newHandler);
			handlerActivations.add(handlerService.activateHandler(commandId, newHandler));
			return new IContributionItem[] {createCommandContributionItemForEntry(commandId, entry)};
		}
		return NO_CONTRIBUTIONS;
	}

	protected ImageDescriptor getRosterEntryImageDescriptor(IRosterEntry entry) {
		IPresence p = entry.getPresence();
		if (p != null) {
			IPresence.Type pType = p.getType();
			IPresence.Mode pMode = p.getMode();
			// If type is unavailable then we're unavailable
			if (pType.equals(IPresence.Type.AVAILABLE)) {
				// if type and mode are both 'available' then we're actually
				// available
				if (pMode.equals(IPresence.Mode.AVAILABLE))
					return SharedImages.getImageDescriptor(SharedImages.IMG_USER_AVAILABLE);
				// If mode is away then we're away
				else if (pMode.equals(IPresence.Mode.AWAY) || pMode.equals(IPresence.Mode.EXTENDED_AWAY))
					return SharedImages.getImageDescriptor(SharedImages.IMG_USER_AWAY);
				else if (pMode.equals(IPresence.Mode.DND))
					return SharedImages.getImageDescriptor(SharedImages.IMG_USER_DND);
			}
		}
		return SharedImages.getImageDescriptor(SharedImages.IMG_USER_UNAVAILABLE);
	}

	/**
	 * Create a command contribution item for the given entry with the given commandId.  
	 * 
	 * @param commandId the commandId for the new CommandContributionItem.  Must not be <code>null</code>.
	 * @param rosterEntry the IRosterEntry for the new CommandContributionItem.  Must not be <code>null</code>.
	 * @return CommandContributionItem created.  Must not return <code>null</code>.
	 */
	protected CommandContributionItem createCommandContributionItemForEntry(String commandId, IRosterEntry rosterEntry) {
		return new CommandContributionItem(serviceLocator, null, commandId, new HashMap(), getRosterEntryImageDescriptor(rosterEntry), null, null, rosterEntry.getName(), null, null, CommandContributionItem.STYLE_PUSH);
	}

	/* (non-Javadoc)
	 * @see org.eclipse.jface.action.ContributionItem#dispose()
	 */
	public void dispose() {
		super.dispose();
		contributionItems.clear();
		if (handlerService != null) {
			handlerService.deactivateHandlers(handlerActivations);
			handlerService = null;

		}
		handlerActivations.clear();
		commandService = null;
	}

	protected void clearOldContributions() {
		contributionItems.clear();
		handlerService.deactivateHandlers(handlerActivations);
	}

	protected List getPresenceContainerAdapters() {
		List presenceContainers = new ArrayList();
		IContainerManager containerManager = Activator.getDefault().getContainerManager();
		if (containerManager == null)
			return presenceContainers;
		IContainer[] containers = containerManager.getAllContainers();
		for (int i = 0; i < containers.length; i++) {
			IPresenceContainerAdapter presenceContainerAdapter = (IPresenceContainerAdapter) containers[i].getAdapter(IPresenceContainerAdapter.class);
			if ((containers[i].getConnectedID() != null) && (presenceContainerAdapter != null)) {
				presenceContainers.add(presenceContainerAdapter);
			}
		}
		return presenceContainers;
	}

	/* (non-Javadoc)
	 * @see org.eclipse.ui.actions.CompoundContributionItem#getContributionItems()
	 */
	protected IContributionItem[] getContributionItems() {
		clearOldContributions();
		List presenceContainers = getPresenceContainerAdapters();
		if (presenceContainers.size() == 0)
			return NO_CONTRIBUTIONS;
		List contributions = new ArrayList();
		for (Iterator i = presenceContainers.iterator(); i.hasNext();) {
			IContributionItem[] items = createContributionItemsForPresenceContainer((IPresenceContainerAdapter) i.next());
			for (int j = 0; j < items.length; j++)
				contributions.add(items[j]);
		}
		if (contributions.size() > 0) {
			MenuManager menuManager = createMenuManagerForTop();
			IContributionItem[] items = (IContributionItem[]) contributions.toArray(new IContributionItem[] {});
			for (int i = 0; i < items.length; i++)
				menuManager.add(items[i]);
			return new IContributionItem[] {new Separator(), menuManager};
		}
		return NO_CONTRIBUTIONS;
	}

	/**
	 * Create a MenuManager for the top level menu.
	 * @return the menu manager.  Should not be <code>null</code>.
	 */
	protected MenuManager createMenuManagerForTop() {
		return new MenuManager(topMenuName, topMenuImageDescriptor, null);
	}

}