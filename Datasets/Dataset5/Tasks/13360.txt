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
package org.eclipse.wst.xml.vex.ui.internal.config;

import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.dialogs.PropertyPage;
import org.eclipse.wst.xml.vex.core.internal.dom.IValidator;
import org.eclipse.wst.xml.vex.ui.internal.VexPlugin;

/**
 * Property page for .dtd files.
 */
public class DoctypePropertyPage extends PropertyPage {

	protected Control createContents(final Composite parent) {

		pane = new Composite(parent, SWT.NONE);

		createPropertySheet();

		configListener = new IConfigListener() {

			public void configChanged(ConfigEvent e) {

				// This is fired when we open properties for a new doctype
				// and we force it to be re-built to get a validator
				// from which we get our list of prospective root elements.

				String resourcePath = ((IFile) getElement())
						.getProjectRelativePath().toString();

				ConfigSource config = getPluginProject();

				doctype = (DocumentType) config
						.getItemForResource(resourcePath);

				populateRootElements();
			}

			public void configLoaded(final ConfigEvent e) {

				setMessage(getTitle());
				populateDoctype();
				setValid(true);

				try { // force an incremental build
					getPluginProject().writeConfigXml();
				} catch (Exception ex) {
					String message = MessageFormat
							.format(
									Messages
											.getString("DoctypePropertyPage.errorWritingConfig"), //$NON-NLS-1$
									new Object[] { PluginProject.PLUGIN_XML });
					VexPlugin.getInstance().log(IStatus.ERROR, message, ex);
				}

			}
		};

		ConfigRegistry.getInstance().addConfigListener(configListener);

		if (ConfigRegistry.getInstance().isConfigLoaded()) {

			populateDoctype();
			populateRootElements();

		} else {

			setValid(false);

			setMessage(Messages.getString("DoctypePropertyPage.loading")); //$NON-NLS-1$

		}

		return pane;
	}

	private void createPropertySheet() {

		GridLayout layout = new GridLayout();
		layout.numColumns = 2;
		pane.setLayout(layout);
		GridData gd;

		Label label;

		label = new Label(pane, SWT.NONE);
		label.setText(Messages.getString("DoctypePropertyPage.name")); //$NON-NLS-1$
		this.nameText = new Text(pane, SWT.BORDER);
		gd = new GridData();
		gd.widthHint = NAME_WIDTH;
		this.nameText.setLayoutData(gd);

		label = new Label(pane, SWT.NONE);
		label.setText(Messages.getString("DoctypePropertyPage.publicId")); //$NON-NLS-1$
		this.publicIdText = new Text(pane, SWT.BORDER);
		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		this.publicIdText.setLayoutData(gd);

		label = new Label(pane, SWT.NONE);
		label.setText(Messages.getString("DoctypePropertyPage.systemId")); //$NON-NLS-1$
		this.systemIdText = new Text(pane, SWT.BORDER);
		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		this.systemIdText.setLayoutData(gd);

		final String resourcePath = ((IFile) this.getElement())
				.getProjectRelativePath().toString();

		final ConfigSource config = this.getPluginProject();

		this.doctype = (DocumentType) config.getItemForResource(resourcePath);
		if (this.doctype == null) {
			this.doctype = new DocumentType(config);
			this.doctype.setResourcePath(resourcePath);
			config.addItem(this.doctype);
		}

		// Generate a simple ID for this one if necessary
		if (this.doctype.getSimpleId() == null
				|| this.doctype.getSimpleId().length() == 0) {
			this.doctype.setSimpleId(this.doctype.generateSimpleId());
		}

		// need to do GridLayout and GridData for this guy them fill with items

		label = new Label(pane, SWT.NONE);
		label.setText(Messages.getString("DoctypePropertyPage.rootElements")); //$NON-NLS-1$

		gd = new GridData();
		// gd.widthHint = COLUMN_1_WIDTH;
		gd.verticalAlignment = GridData.BEGINNING;
		gd.horizontalSpan = 2;
		label.setLayoutData(gd);

		final Composite tablePane = new Composite(pane, SWT.BORDER);

		gd = new GridData(GridData.FILL_BOTH);
		gd.heightHint = 200;
		gd.horizontalSpan = 2;
		tablePane.setLayoutData(gd);

		final FillLayout fillLayout = new FillLayout();
		tablePane.setLayout(fillLayout);

		this.rootElementsTable = new Table(tablePane, SWT.CHECK);
	}

	/**
	 * Returns the PluginProject associated with this resource.
	 * 
	 * @return
	 */
	public PluginProject getPluginProject() {
		IFile file = (IFile) this.getElement();
		return PluginProject.get(file.getProject());
	}

	public boolean performOk() {

		performApply();

		return super.performOk();
	}

	public void performApply() {

		this.doctype.setName(this.nameText.getText());
		this.doctype.setPublicId(this.publicIdText.getText());
		this.doctype.setSystemId(this.systemIdText.getText());

		// collect root Elements from the rootElementsTable

		final TableItem[] tia = this.rootElementsTable.getItems();

		final ArrayList selectedRootElements = new ArrayList();

		for (int i = 0; i < tia.length; i++) {
			if (tia[i].getChecked()) {
				selectedRootElements.add(tia[i].getText());
			}
		}

		final String[] selectedRootElementsArray = new String[selectedRootElements
				.size()];

		for (int i = 0; i < selectedRootElementsArray.length; i++) {
			selectedRootElementsArray[i] = (String) selectedRootElements.get(i);
		}

		this.doctype.setRootElements(selectedRootElementsArray);

		try {
			this.getPluginProject().writeConfigXml();
		} catch (Exception ex) {
			String message = MessageFormat.format(Messages
					.getString("DoctypePropertyPage.errorWritingConfig"), //$NON-NLS-1$
					new Object[] { PluginProject.PLUGIN_XML });
			VexPlugin.getInstance().log(IStatus.ERROR, message, ex);
		}

		ConfigRegistry.getInstance().fireConfigChanged(new ConfigEvent(this));
	}

	public void performDefaults() {

		super.performDefaults();

		populateDoctype();

		populateRootElements();
	}

	public void dispose() {
		super.dispose();

		if (this.configListener != null) {
			ConfigRegistry.getInstance().removeConfigListener(
					this.configListener);
		}
	}

	// ======================================================= PRIVATE

	private DocumentType doctype;

	private static final int NAME_WIDTH = 150;

	private Composite pane;

	private Text nameText;

	private Text publicIdText;

	private Text systemIdText;

	private Table rootElementsTable;

	private IConfigListener configListener;

	private void populateDoctype() {
		this.setText(this.nameText, this.doctype.getName());
		this.setText(this.publicIdText, this.doctype.getPublicId());
		this.setText(this.systemIdText, this.doctype.getSystemId());
	}

	/*
     *  
     */

	private void populateRootElements() {

		final String resourcePath = ((IFile) this.getElement())
				.getProjectRelativePath().toString();

		final IValidator validator = (IValidator) ((ConfigSource) this
				.getPluginProject()).getParsedResource(resourcePath);

		if (validator != null) {

			final List list = Arrays.asList(doctype.getRootElements());
			final Set selectedRootElements = new TreeSet(list);

			rootElementsTable.removeAll();

			final java.util.List l = new ArrayList(validator
					.getValidRootElements());
			Collections.sort(l);
			for (int i = 0; i < l.size(); i++) {

				TableItem item1 = new TableItem(rootElementsTable, SWT.NONE);
				item1.setText((String) l.get(i));

				if (selectedRootElements.contains((String) l.get(i))) {
					item1.setChecked(true);
				}
			}
		} else {

			try {
				this.getPluginProject().writeConfigXml();
			} catch (Exception ex) {
				String message = MessageFormat.format(Messages
						.getString("DoctypePropertyPage.errorWritingConfig"), //$NON-NLS-1$
						new Object[] { PluginProject.PLUGIN_XML });
				VexPlugin.getInstance().log(IStatus.ERROR, message, ex);
			}
		}
	}

	private void setText(Text textBox, String s) {
		textBox.setText(s == null ? "" : s); //$NON-NLS-1$
	}
}
 No newline at end of file