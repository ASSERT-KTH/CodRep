import org.eclipse.wst.xml.vex.core.internal.provisional.dom.IValidator;

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

import java.util.Arrays;
import java.util.Set;

import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.wst.xml.vex.core.internal.dom.IValidator;
import org.eclipse.wst.xml.vex.ui.internal.VexPlugin;
import org.eclipse.wst.xml.vex.ui.internal.config.DocumentType;

/**
 * Wizard page for selecting the document type and root element for the new
 * document.
 */
public class DocumentTypeSelectionPage extends WizardPage {

	private static final String SETTINGS_PUBLIC_ID = "publicId"; //$NON-NLS-1$
	private static final String SETTINGS_ROOT_ELEMENT_PREFIX = "root."; //$NON-NLS-1$

	/**
	 * Class constructor.
	 */
	public DocumentTypeSelectionPage() {
		super(Messages.getString("DocumentTypeSelectionPage.pageName")); //$NON-NLS-1$
		this.setPageComplete(false);

		IDialogSettings rootSettings = VexPlugin.getInstance()
				.getDialogSettings();
		this.settings = rootSettings.getSection("newDocument"); //$NON-NLS-1$
		if (this.settings == null) {
			this.settings = rootSettings.addNewSection("newDocument"); //$NON-NLS-1$
		}

		this.doctypes = DocumentType.getDocumentTypesWithStyles();
		Arrays.sort(this.doctypes);
	}

	public void createControl(Composite parent) {

		Composite pane = new Composite(parent, SWT.NONE);
		GridLayout layout = new GridLayout();
		layout.numColumns = 2;
		pane.setLayout(layout);
		GridData gd;

		Label label = new Label(pane, SWT.NONE);
		label.setText(Messages.getString("DocumentTypeSelectionPage.doctype")); //$NON-NLS-1$

		this.typeCombo = new Combo(pane, SWT.DROP_DOWN | SWT.READ_ONLY);
		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		this.typeCombo.setLayoutData(gd);
		this.typeCombo.addSelectionListener(typeComboSelectionListener);

		label = new Label(pane, SWT.NONE);
		label.setText(Messages
				.getString("DocumentTypeSelectionPage.rootElement")); //$NON-NLS-1$
		this.setControl(pane);

		this.elementCombo = new Combo(pane, SWT.DROP_DOWN | SWT.READ_ONLY);
		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		this.elementCombo.setLayoutData(gd);
		this.elementCombo.addSelectionListener(elementComboSelectionListener);

		String publicId = this.settings.get(SETTINGS_PUBLIC_ID);
		int initSelection = -1;
		String[] typeNames = new String[this.doctypes.length];
		for (int i = 0; i < this.doctypes.length; i++) {
			typeNames[i] = this.doctypes[i].getName();
			if (this.doctypes[i].getPublicId().equals(publicId)) {
				initSelection = i;
			}
		}

		this.typeCombo.setItems(typeNames);

		if (initSelection != -1) {
			this.typeCombo.select(initSelection);
			// calling select() does not fire the selection listener,
			// so we update it manually
			this.updateElementCombo();
		}

		this.setTitle(Messages.getString("DocumentTypeSelectionPage.title")); //$NON-NLS-1$
		this.setDescription(Messages
				.getString("DocumentTypeSelectionPage.desc")); //$NON-NLS-1$
	}

	/**
	 * Returns the selected document type.
	 */
	public DocumentType getDocumentType() {
		int i = this.typeCombo.getSelectionIndex();
		if (i == -1) {
			return null;
		} else {
			return this.doctypes[i];
		}
	}

	/**
	 * Returns the selected name of the root element.
	 */
	public String getRootElementName() {
		return this.elementCombo.getText();
	}

	/**
	 * Called from the wizard's performFinal method to save the settings for
	 * this page.
	 */
	public void saveSettings() {
		DocumentType doctype = this.getDocumentType();
		if (doctype != null) {
			this.settings.put(SETTINGS_PUBLIC_ID, doctype.getPublicId());
			String key = SETTINGS_ROOT_ELEMENT_PREFIX + doctype.getPublicId();
			this.settings.put(key, this.getRootElementName());
		}
	}

	// ============================================================== PRIVATE

	private IDialogSettings settings;
	private DocumentType[] doctypes;
	private Combo typeCombo;
	private Combo elementCombo;

	/**
	 * Update the elementCombo to reflect elements in the currently selected
	 * type.
	 */
	private void updateElementCombo() {
		int index = this.typeCombo.getSelectionIndex();
		DocumentType dt = this.doctypes[index];
		this.elementCombo.removeAll();

		String[] roots = getDocumentType().getRootElements();
		String selectedRoot = null;

		if (roots.length == 0) {
			IValidator validator = dt.getValidator();
			if (validator != null) {
				Set set = validator.getValidRootElements();
				roots = (String[]) set.toArray(new String[set.size()]);
			}
		} else {
			selectedRoot = roots[0];
		}

		Arrays.sort(roots);
		this.elementCombo.setItems(roots);

		if (selectedRoot == null) {
			// Restore the last used root element
			String key = SETTINGS_ROOT_ELEMENT_PREFIX + dt.getPublicId();
			selectedRoot = this.settings.get(key);
		}

		this.setPageComplete(false);
		if (selectedRoot != null) {
			for (int i = 0; i < roots.length; i++) {
				if (roots[i].equals(selectedRoot)) {
					this.elementCombo.select(i);
					this.setPageComplete(true);
					break;
				}
			}
		}
	}

	/**
	 * Sets the root element combo box when the document type combo box is
	 * selected.
	 */
	private SelectionListener typeComboSelectionListener = new SelectionListener() {
		public void widgetSelected(SelectionEvent e) {
			updateElementCombo();
		}

		public void widgetDefaultSelected(SelectionEvent e) {
		}
	};

	/**
	 * When a root element is selected, mark the page as complete.
	 */
	private SelectionListener elementComboSelectionListener = new SelectionListener() {
		public void widgetSelected(SelectionEvent e) {
			setPageComplete(true);
		}

		public void widgetDefaultSelected(SelectionEvent e) {
		}
	};

}