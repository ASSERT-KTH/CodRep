for (Iterator iterator = resultList.getResults().iterator(); iterator.hasNext();) {

/*******************************************************************************
 * Copyright (c) 2008 Marcelo Mayworm. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: 	Marcelo Mayworm - initial API and implementation
 *
 ******************************************************************************/
package org.eclipse.ecf.internal.presence.ui.dialogs;

import java.util.Iterator;
import org.eclipse.core.runtime.*;
import org.eclipse.ecf.core.util.ECFException;
import org.eclipse.ecf.internal.presence.ui.Activator;
import org.eclipse.ecf.internal.presence.ui.Messages;
import org.eclipse.ecf.presence.IPresenceContainerAdapter;
import org.eclipse.ecf.presence.roster.IRosterSubscriptionSender;
import org.eclipse.ecf.presence.search.*;
import org.eclipse.ecf.presence.ui.MultiRosterAccount;
import org.eclipse.ecf.presence.ui.UserSearchView;
import org.eclipse.jface.dialogs.*;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.TableEditor;
import org.eclipse.swt.events.*;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.*;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.progress.UIJob;

/**
 * 
 * @since 3.0
 *
 */
public class SearchContactDialog extends Dialog {

	Button closeButton;

	Button searchButton;

	MultiRosterAccount account;

	Button addContactButton;

	Button runInBackgroundButton;

	Table tableResult;

	Table tableFields;

	public SearchContactDialog(Shell parentShell, MultiRosterAccount account) {
		super(parentShell);
		this.account = account;

	}

	protected void addListeners() {

		searchButton.addMouseListener(new MouseAdapter() {
			public void mouseUp(MouseEvent e) {
				IUserSearchManager userManager = account.getPresenceContainerAdapter().getUserSearchManager();
				try {
					//selection to build the criteria
					IRestriction selection = userManager.createRestriction();
					//create a specific criteria 
					final ICriteria criteria = userManager.createCriteria();
					//fields to consider on XMPP server side search
					TableItem items[] = tableFields.getItems();
					for (int i = 0; i < items.length; i++) {
						TableItem item = items[i];
						if (item.getChecked()) {
							//build criterion field=value
							ICriterion criterion = selection.eq(item.getText(0), item.getText(1));
							criteria.add(criterion);
						}
					}
					//Run in a block or non-block way using the criteria built previously
					if (runInBackgroundButton.getSelection()) {
						callAsynchronous(userManager, criteria);
						//close the UI
						close();
					} else {
						//call the block search
						ISearch search = userManager.search(criteria);
						//the collection of IResult
						IResultList resultList = search.getResultList();
						//clean the table for a new result list
						tableResult.removeAll();
						for (Iterator iterator = resultList.geResults().iterator(); iterator.hasNext();) {
							IResult result = (IResult) iterator.next();
							TableItem item = new TableItem(tableResult, SWT.NONE);
							item.setText(0, result.getUser().getName());
							item.setText(1, result.getUser().getID().getName());
						}
					}

				} catch (UserSearchException e1) {
					Activator.getDefault().getLog().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, e1.getLocalizedMessage(), e1));
				}
			}
		});

		addContactButton.addMouseListener(new MouseAdapter() {
			public void mouseUp(MouseEvent e) {
				TableItem contact = tableResult.getSelection()[0];
				if (MessageDialog.openConfirm(null, Messages.AddContactDialog_DialogTitle, NLS.bind(Messages.SearchContactDialog_AddContactMessage, contact.getText(0)))) {

					IPresenceContainerAdapter ipca = account.getPresenceContainerAdapter();
					IRosterSubscriptionSender sender = ipca.getRosterManager().getRosterSubscriptionSender();
					try {
						sender.sendRosterAdd(contact.getText(1), contact.getText(0), null);
					} catch (ECFException e1) {
						Activator.getDefault().getLog().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, e1.getLocalizedMessage(), e1));
					}
					close();
				}
			}
		});

	}

	protected void configureShell(Shell newShell) {
		super.configureShell(newShell);
		newShell.setText(Messages.SearchContactDialog_DialogTitle);
	}

	/*
	 * Create just a close button for the Dialog
	 * (non-Javadoc)
	 * @see org.eclipse.jface.dialogs.Dialog#createButtonsForButtonBar(org.eclipse.swt.widgets.Composite)
	 */
	protected void createButtonsForButtonBar(Composite parent) {
		createButton(parent, IDialogConstants.OK_ID, IDialogConstants.CLOSE_LABEL, true);
		closeButton = getButton(IDialogConstants.OK_ID);
		closeButton.setEnabled(true);
	}

	protected Control createDialogArea(Composite parent) {
		final int editableColumn = 1;
		try {
			parent = (Composite) super.createDialogArea(parent);
			parent.setLayout(new GridLayout(2, false));
			String fields[] = null;
			IUserSearchManager userManager = account.getPresenceContainerAdapter().getUserSearchManager();
			fields = userManager.getUserPropertiesFields();

			GridData searchButtonData = new GridData(SWT.RIGHT, GridData.FILL_HORIZONTAL, false, false, 1, 1);
			GridData addContactData = new GridData(SWT.RIGHT, GridData.FILL_HORIZONTAL, true, false, 1, 1);

			Group group = new Group(parent, SWT.SHADOW_ETCHED_IN);
			group.setLayout(new GridLayout(2, false));
			group.setText(Messages.SearchContactDialog_InfoSearchFields);

			Group groupContact = new Group(parent, SWT.SHADOW_ETCHED_IN);
			groupContact.setLayout(new GridLayout(2, false));
			groupContact.setText(Messages.SearchContactDialog_InfoContactFields);

			tableResult = new Table(groupContact, SWT.MULTI | SWT.BORDER | SWT.FULL_SELECTION);
			tableResult.setLinesVisible(true);
			tableResult.setHeaderVisible(true);
			GridData dataTable = new GridData(GridData.FILL_HORIZONTAL, GridData.FILL_VERTICAL, true, true, 2, 1);
			dataTable.heightHint = 200;
			tableResult.setLayoutData(dataTable);

			new TableColumn(tableResult, SWT.NONE).setText(Messages.SearchContactDialog_TableResultColumnName);
			new TableColumn(tableResult, SWT.NONE).setText(Messages.SearchContactDialog_TableResultColumnUsername);
			new TableItem(tableResult, SWT.NONE);

			for (int i = 0; i < 2; i++) {
				tableResult.getColumn(i).setWidth(130);
			}

			addContactButton = new Button(groupContact, SWT.PUSH | SWT.RIGHT);
			addContactButton.setText(Messages.SearchContactDialog_ButtonAddContact);
			addContactButton.setLayoutData(addContactData);

			tableFields = new Table(group, SWT.BORDER | SWT.MULTI | SWT.CHECK);
			tableFields.setLinesVisible(true);
			tableFields.setHeaderVisible(true);
			dataTable = new GridData(GridData.FILL_HORIZONTAL, GridData.FILL_VERTICAL, true, true, 2, 1);
			dataTable.heightHint = 200;
			tableFields.setLayoutData(dataTable);

			TableColumn colField = new TableColumn(tableFields, SWT.NONE);
			colField.setText(Messages.SearchContactDialog_TableSearchColumnField);
			TableColumn colValue = new TableColumn(tableFields, SWT.NONE);
			colValue.setText(Messages.SearchContactDialog_TableSearchColumnValue);
			colValue.setWidth(130);

			for (int i = 0; i < fields.length; i++) {
				TableItem item = new TableItem(tableFields, SWT.NONE);
				item.setText(new String[] {fields[i], ""}); //$NON-NLS-1$
				item.setChecked(true);
			}

			TableItem[] items = tableFields.getItems();
			for (int i = 0; i < items.length; i++) {
				final TableEditor editor = new TableEditor(tableFields);
				Text text = new Text(tableFields, SWT.NONE);
				text.setText(items[i].getText(editableColumn));
				text.addModifyListener(new ModifyListener() {
					public void modifyText(ModifyEvent e) {
						editor.getItem().setText(editableColumn, ((Text) editor.getEditor()).getText());
					}
				});
				text.selectAll();
				text.setFocus();
				editor.grabHorizontal = true;
				editor.setEditor(text, items[i], editableColumn);

			}
			colField.pack();

			runInBackgroundButton = new Button(group, SWT.CHECK);
			runInBackgroundButton.setText(Messages.SearchContactDialog_RunInBackground);
			runInBackgroundButton.setToolTipText(Messages.SearchContactDialog_RunInBackGroundToolTip);

			searchButton = new Button(group, SWT.PUSH | SWT.RIGHT);
			searchButton.setText(Messages.SearchContactDialog_ButtonSearch);
			searchButton.setLayoutData(searchButtonData);

		} catch (ECFException e) {
			Activator.getDefault().getLog().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, e.getLocalizedMessage(), e));
			new Label(parent, SWT.LEFT).setText(e.getLocalizedMessage());
		}
		addListeners();
		applyDialogFont(parent);
		return parent;
	}

	/**
	 * Call the user search and open the view 
	 * asynchronous
	 * @param userManager
	 * @param criteria
	 */
	protected void callAsynchronous(final IUserSearchManager userManager, final ICriteria criteria) {

		IUserSearchListener listener = new IUserSearchListener() {
			public void handleUserSearchEvent(IUserSearchEvent event) {
				if (event instanceof IUserSearchCompleteEvent) {
					fireEventComplete((IUserSearchCompleteEvent) event);
				}

			}

		};
		userManager.search(criteria, listener);

	}

	/**
	 * 
	 * @param event
	 */
	protected void fireEventComplete(final IUserSearchCompleteEvent event) {
		new UIJob(Messages.SearchContactDialog_UserSearchJobName) {
			public IStatus runInUIThread(IProgressMonitor monitor) {
				try {
					final UserSearchView view = (UserSearchView) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(UserSearchView.VIEW_ID);
					view.showMessage(Messages.SearchContactDialog_SearchingMessage);
					view.addMultiRosterAccount(account);
					view.addResult(event.getSearch().getResultList());
				} catch (PartInitException e) {
					Activator.getDefault().getLog().log(new Status(IStatus.ERROR, Activator.PLUGIN_ID, IStatus.ERROR, e.getLocalizedMessage(), e));
					return Status.CANCEL_STATUS;
				}
				return Status.OK_STATUS;
			}
		}.schedule(3000);

	}

}