FilteredTree filteredTree = new FilteredTree(parent, SWT.SINGLE | SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER, new WizardPatternFilter());

/*******************************************************************************
 * Copyright (c) 2000, 2006 IBM Corporation, Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 *******************************************************************************/
package org.eclipse.ecf.ui.wizards;

import java.util.ArrayList;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.core.ContainerTypeDescription;
import org.eclipse.ecf.internal.ui.Activator;
import org.eclipse.ecf.internal.ui.Messages;
import org.eclipse.ecf.internal.ui.wizards.*;
import org.eclipse.ecf.ui.ContainerConfigurationResult;
import org.eclipse.ecf.ui.IConfigurationWizard;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.jface.viewers.*;
import org.eclipse.jface.wizard.IWizardPage;
import org.eclipse.jface.wizard.WizardSelectionPage;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.*;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.activities.ITriggerPoint;
import org.eclipse.ui.activities.WorkbenchActivityHelper;
import org.eclipse.ui.dialogs.FilteredTree;
import org.eclipse.ui.dialogs.PatternFilter;
import org.eclipse.ui.model.AdaptableList;
import org.eclipse.ui.model.WorkbenchLabelProvider;
import org.eclipse.ui.wizards.IWizardCategory;

/**
 * A wizard page for {@link ConfigurationWizardSelectionWizard}.  
 */
public class ConfigurationWizardSelectionPage extends WizardSelectionPage {

	private static final int CONTAINERTYPEDESCRIPTION_ERROR_CODE = 333;

	protected IWorkbench workbench;

	protected TreeViewer treeViewer;

	protected CategorizedWizardSelectionTree wizardSelectionTree;

	protected IStructuredSelection currentResourceSelection;

	protected IWorkbench getWorkbench() {
		return this.workbench;
	}

	protected TreeViewer getTreeViewer() {
		return treeViewer;
	}

	protected void setTreeViewer(TreeViewer viewer) {
		treeViewer = viewer;
	}

	protected class CategorizedWizardSelectionTree {
		private final static int SIZING_LISTS_HEIGHT = 200;

		private IWizardCategory wizardCategories;

		private String message;

		private TreeViewer viewer;

		/**
		 * Constructor for CategorizedWizardSelectionTree
		 * 
		 * @param categories
		 *            root wizard category for the wizard type
		 * @param msg
		 *            message describing what the user should choose from the
		 *            tree.
		 */
		protected CategorizedWizardSelectionTree(IWizardCategory categories, String msg) {
			this.wizardCategories = categories;
			this.message = msg;
		}

		/**
		 * Create the tree viewer and a message describing what the user should
		 * choose from the tree.
		 * 
		 * @param parent
		 *            Composite on which the tree viewer is to be created
		 * @return Comoposite with all widgets
		 */
		protected Composite createControl(Composite parent) {
			Font font = parent.getFont();

			// create composite for page.
			Composite outerContainer = new Composite(parent, SWT.NONE);
			outerContainer.setLayout(new GridLayout());
			outerContainer.setLayoutData(new GridData(GridData.FILL_BOTH));
			outerContainer.setFont(font);

			Label messageLabel = new Label(outerContainer, SWT.NONE);
			if (message != null) {
				messageLabel.setText(message);
			}
			messageLabel.setFont(font);

			createFilteredTree(outerContainer);
			layoutTopControl(viewer.getControl());

			return outerContainer;
		}

		/**
		 * Create the categorized tree viewer.
		 * 
		 * @param parent
		 */
		private void createFilteredTree(Composite parent) {
			// Create a FilteredTree for the categories and wizards
			FilteredTree filteredTree = new FilteredTree(parent, SWT.SINGLE | SWT.H_SCROLL | SWT.V_SCROLL | SWT.BORDER, new WizardPatternFilter(), false);
			viewer = filteredTree.getViewer();
			filteredTree.setFont(parent.getFont());

			viewer.setContentProvider(new WizardContentProvider());
			viewer.setLabelProvider(new WorkbenchLabelProvider());
			viewer.setComparator(new ViewerComparator() {
				public int category(Object element) {
					if (element instanceof WizardCollectionElement) {
						String id = ((WizardCollectionElement) element).getId();
						String wizardCategory = Messages.ConfigurationWizardSelectionPage_WIZARD_CATEGORY;
						if (wizardCategory != null && wizardCategory.equals(id))
							return 1;
						String uncategorizedCategory = Messages.ConfigurationWizardSelectionPage_UNCATEGORIZED_WIZARD_CATEGORY;
						if (uncategorizedCategory != null && uncategorizedCategory.equals(id))
							return 3;
						return 2;
					}
					return super.category(element);
				}
			});

			ArrayList inputArray = new ArrayList();
			boolean expandTop = false;

			if (wizardCategories != null) {
				if (wizardCategories.getParent() == null) {
					IWizardCategory[] children = wizardCategories.getCategories();
					for (int i = 0; i < children.length; i++) {
						inputArray.add(children[i]);
					}
				} else {
					expandTop = true;
					inputArray.add(wizardCategories);
				}
			}

			// ensure the category is expanded. If there is a remembered
			// expansion it will be set later.
			if (expandTop) {
				viewer.setAutoExpandLevel(2);
			}

			AdaptableList input = new AdaptableList(inputArray);

			// filter wizard list according to capabilities that are enabled
			viewer.addFilter(new WizardActivityFilter());

			viewer.setInput(input);
		}

		protected class WizardPatternFilter extends PatternFilter {

			/**
			 * Create a new instance of a WizardPatternFilter
			 * 
			 */
			public WizardPatternFilter() {
				super();
			}

			/*
			 * (non-Javadoc)
			 * 
			 * @see org.eclipse.ui.internal.dialogs.PatternFilter#isElementSelectable(java.lang.Object)
			 */
			public boolean isElementSelectable(Object element) {
				return element instanceof WorkbenchWizardElement;
			}

			/*
			 * (non-Javadoc)
			 * 
			 * @see org.eclipse.ui.internal.dialogs.PatternFilter#isElementMatch(org.eclipse.jface.viewers.Viewer,
			 *      java.lang.Object)
			 */
			protected boolean isLeafMatch(Viewer v, Object element) {
				if (element instanceof WizardCollectionElement)
					return false;

				if (element instanceof WorkbenchWizardElement) {
					WorkbenchWizardElement desc = (WorkbenchWizardElement) element;
					String text = desc.getLabel();
					if (wordMatches(text))
						return true;
				}
				return false;
			}

		}

		/**
		 * 
		 * @return the categorized tree viewer
		 */
		protected TreeViewer getViewer() {
			return viewer;
		}

		/**
		 * Layout for the given control.
		 * 
		 * @param control
		 */
		private void layoutTopControl(Control control) {
			GridData data = new GridData(GridData.FILL_BOTH);

			int availableRows = control.getParent().getDisplay().getClientArea().height / (control.getParent().getFont().getFontData())[0].getHeight();

			// Only give a height hint if the dialog is going to be too small
			if (availableRows > 50) {
				data.heightHint = SIZING_LISTS_HEIGHT;
			} else {
				data.heightHint = availableRows * 3;
			}

			control.setLayoutData(data);
		}
	}

	public ConfigurationWizardSelectionPage(IWorkbench workbench, IStructuredSelection selection) {
		super(Messages.ConfigurationWizardSelectionPage_CONFIGURATION_WIZARD_PAGE_NAME);
		this.workbench = workbench;
		this.currentResourceSelection = selection;
		setTitle(Messages.Select);
	}

	protected ITriggerPoint getTriggerPoint() {
		return getWorkbench().getActivitySupport().getTriggerPointManager().getTriggerPoint(IWizardRegistryConstants.CONFIGURE_EPOINT_ID);
	}

	protected ContainerConfigurationResult getContainerResult() {
		ConfigurationWizardNode cwn = (ConfigurationWizardNode) getSelectedNode();
		if (cwn == null)
			return null;
		return ((IConfigurationWizard) getSelectedNode().getWizard()).getConfigurationResult();
	}

	private ContainerTypeDescription getContainerTypeDescriptionForElement(WorkbenchWizardElement element) {
		ContainerTypeDescription typeDescription = ContainerFactory.getDefault().getDescriptionByName(element.getContainerTypeName());
		if (typeDescription == null) {
			String msg = NLS.bind(Messages.ConfigurationWizardSelectionPage_ERROR_MESSAGE, element);
			setErrorMessage(msg);
			ErrorDialog.openError(getShell(), Messages.ConfigurationWizardSelectionPage_CONFIGRATION_ERROR_TITLE, Messages.ConfigurationWizardSelectionPage_CONFIGURATION_ERROR_MESSAGE, new Status(IStatus.ERROR, Activator.PLUGIN_ID, CONTAINERTYPEDESCRIPTION_ERROR_CODE, msg, null));
			return null;
		}
		return typeDescription;
	}

	protected void updateSelectedNode(WorkbenchWizardElement wizardElement) {
		setErrorMessage(null);
		if (wizardElement == null) {
			updateMessage();
			setSelectedNode(null);
			return;
		}

		setSelectedNode(new ConfigurationWizardNode(getWorkbench(), this, wizardElement, getContainerTypeDescriptionForElement(wizardElement)));
		setMessage(wizardElement.getDescription());
	}

	protected IWizardCategory getRootCategory() {
		return new WizardsRegistryReader(Activator.PLUGIN_ID, IWizardRegistryConstants.CONFIGURE_EPOINT).getWizardElements();
	}

	public IWizardPage getNextPage() {
		ITriggerPoint triggerPoint = getTriggerPoint();

		if (triggerPoint == null || WorkbenchActivityHelper.allowUseOf(triggerPoint, getSelectedNode())) {
			return super.getNextPage();
		}
		return null;
	}

	protected Composite createTreeViewer(Composite parent) {
		IWizardCategory root = getRootCategory();
		wizardSelectionTree = new CategorizedWizardSelectionTree(root, Messages.ConfigurationWizardSelectionPage_SELECT);
		Composite importComp = wizardSelectionTree.createControl(parent);
		wizardSelectionTree.getViewer().addSelectionChangedListener(new ISelectionChangedListener() {
			public void selectionChanged(SelectionChangedEvent event) {
				listSelectionChanged(event.getSelection());
			}
		});
		wizardSelectionTree.getViewer().addDoubleClickListener(new IDoubleClickListener() {
			public void doubleClick(DoubleClickEvent event) {
				treeDoubleClicked(event);
			}
		});
		setTreeViewer(wizardSelectionTree.getViewer());
		return importComp;
	}

	protected void treeDoubleClicked(DoubleClickEvent event) {
		ISelection selection = event.getViewer().getSelection();
		IStructuredSelection ss = (IStructuredSelection) selection;
		listSelectionChanged(ss);

		Object element = ss.getFirstElement();
		TreeViewer v = (TreeViewer) event.getViewer();
		if (v.isExpandable(element)) {
			v.setExpandedState(element, !v.getExpandedState(element));
		} else if (element instanceof WorkbenchWizardElement) {
			if (canFlipToNextPage()) {
				getContainer().showPage(getNextPage());
			}
		}
		getContainer().showPage(getNextPage());
	}

	protected void listSelectionChanged(ISelection selection) {
		setErrorMessage(null);
		IStructuredSelection ss = (IStructuredSelection) selection;
		Object sel = ss.getFirstElement();
		if (sel instanceof WorkbenchWizardElement) {
			WorkbenchWizardElement currentWizardSelection = (WorkbenchWizardElement) sel;
			updateSelectedNode(currentWizardSelection);
		} else {
			updateSelectedNode(null);
		}
	}

	protected void updateMessage() {
		TreeViewer viewer = getTreeViewer();
		if (viewer != null) {
			ISelection selection = viewer.getSelection();
			IStructuredSelection ss = (IStructuredSelection) selection;
			Object sel = ss.getFirstElement();
			if (sel instanceof WorkbenchWizardElement) {
				updateSelectedNode((WorkbenchWizardElement) sel);
			} else {
				setSelectedNode(null);
			}
		} else {
			setMessage(null);
		}
	}

	public void createControl(Composite parent) {
		Font font = parent.getFont();

		Composite outerContainer = new Composite(parent, SWT.NONE);
		outerContainer.setLayout(new GridLayout());
		outerContainer.setLayoutData(new GridData(GridData.FILL_BOTH));
		outerContainer.setFont(font);

		Composite comp = createTreeViewer(outerContainer);

		Dialog.applyDialogFont(comp);

		setControl(outerContainer);

	}

}