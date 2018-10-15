import org.eclipse.wst.xml.vex.core.internal.provisional.dom.I.VEXElement;

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
package org.eclipse.wst.xml.vex.ui.internal.outline;

import java.text.MessageFormat;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.TreeItem;
import org.eclipse.ui.part.IPageSite;
import org.eclipse.ui.part.Page;
import org.eclipse.ui.views.contentoutline.IContentOutlinePage;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.provisional.dom.VEXElement;
import org.eclipse.wst.xml.vex.ui.internal.VexPlugin;
import org.eclipse.wst.xml.vex.ui.internal.config.DocumentType;
import org.eclipse.wst.xml.vex.ui.internal.editor.IVexEditorListener;
import org.eclipse.wst.xml.vex.ui.internal.editor.Messages;
import org.eclipse.wst.xml.vex.ui.internal.editor.SelectionProvider;
import org.eclipse.wst.xml.vex.ui.internal.editor.VexEditor;
import org.eclipse.wst.xml.vex.ui.internal.editor.VexEditorEvent;
import org.eclipse.wst.xml.vex.ui.internal.swt.VexWidget;
import org.osgi.framework.Bundle;

/**
 * Outline page for documents. Determination of the outline itself is deferred
 * to a doctype-specific implementation of IOutlineProvider.
 */
public class DocumentOutlinePage extends Page implements IContentOutlinePage {

	public void createControl(Composite parent) {

		this.composite = new Composite(parent, SWT.NONE);
		this.composite.setLayout(new FillLayout());

		if (this.vexEditor.isLoaded()) {
			this.showTreeViewer();
		} else {
			this.showLabel(Messages.getString("DocumentOutlinePage.loading")); //$NON-NLS-1$
		}

	}

	public void dispose() {
		this.vexEditor.removeVexEditorListener(this.vexEditorListener);
		this.vexEditor.getEditorSite().getSelectionProvider()
				.removeSelectionChangedListener(this.selectionListener);
	}

	public Control getControl() {
		return this.composite;
	}

	public void init(IPageSite pageSite) {
		super.init(pageSite);
		this.vexEditor = (VexEditor) pageSite.getPage().getActiveEditor();
		this.vexEditor.addVexEditorListener(this.vexEditorListener);
		this.vexEditor.getEditorSite().getSelectionProvider()
				.addSelectionChangedListener(this.selectionListener);
	}

	public void setFocus() {
		if (this.treeViewer != null) {
			treeViewer.getControl().setFocus();
		}
	}

	public void addSelectionChangedListener(ISelectionChangedListener listener) {
		this.selectionProvider.addSelectionChangedListener(listener);
	}

	public ISelection getSelection() {
		return this.selectionProvider.getSelection();
	}

	/**
	 * Returns the TreeViewer associated with this page. May return null, if
	 * VexPlugin has not yet loaded its configuration.
	 */
	public TreeViewer getTreeViewer() {
		return this.treeViewer;
	}

	public void removeSelectionChangedListener(
			ISelectionChangedListener listener) {
		this.selectionProvider.removeSelectionChangedListener(listener);

	}

	public void setSelection(ISelection selection) {
		this.selectionProvider.setSelection(selection);
	}

	// ===================================================== PRIVATE

	private Composite composite;

	private Label label;
	private TreeViewer treeViewer;

	private VexEditor vexEditor;

	private IOutlineProvider outlineProvider;

	private SelectionProvider selectionProvider = new SelectionProvider();

	private void showLabel(String message) {

		if (this.treeViewer != null) {
			this.treeViewer
					.removeSelectionChangedListener(this.selectionListener);
			this.treeViewer.getTree().dispose();
			this.treeViewer = null;
		}

		if (this.label == null) {
			this.label = new Label(this.composite, SWT.NONE);
			this.label.setText(message);
			this.composite.layout(true);
		}

		this.label.setText(message);
	}

	private void showTreeViewer() {

		if (this.treeViewer != null) {
			return;
		}

		if (this.label != null) {
			this.label.dispose();
			this.label = null;
		}

		this.treeViewer = new TreeViewer(this.composite, SWT.NONE);
		this.composite.layout();

		DocumentType doctype = this.vexEditor.getDocumentType();

		if (doctype == null) {
			return;
		}

		String ns = doctype.getConfig().getUniqueIdentifer();
		Bundle bundle = Platform.getBundle(ns);
		String providerClassName = doctype.getOutlineProvider();
		if (bundle != null && providerClassName != null) {
			try {
				Class clazz = bundle.loadClass(providerClassName);
				this.outlineProvider = (IOutlineProvider) clazz.newInstance();
			} catch (Exception ex) {
				String message = Messages
						.getString("DocumentOutlinePage.loadingError"); //$NON-NLS-1$
				VexPlugin.getInstance().log(
						IStatus.WARNING,
						MessageFormat.format(message, new Object[] {
								providerClassName, ns, ex }));
			}
		}

		if (this.outlineProvider == null) {
			this.outlineProvider = new DefaultOutlineProvider();
		}

		this.outlineProvider.init(this.vexEditor);

		this.treeViewer.setContentProvider(this.outlineProvider
				.getContentProvider());
		this.treeViewer.setLabelProvider(this.outlineProvider
				.getLabelProvider());
		this.treeViewer.setAutoExpandLevel(2);

		this.treeViewer.setInput(this.vexEditor.getVexWidget().getDocument());

		this.treeViewer.addSelectionChangedListener(this.selectionListener);

	}

	/**
	 * Receives selection changed events from both our TreeViewer and the
	 * VexWidget. Generally, we use this to synchronize the selection between
	 * the two, but we also do the following...
	 * 
	 * - when a notification comes from VexWidget, we create the treeViewer if
	 * needed (that is, if the part was created before VexPlugin was done
	 * loading its configuration.
	 * 
	 * - notifications from the TreeViewer are passed on to our
	 * SelectionChangedListeners.
	 */
	private ISelectionChangedListener selectionListener = new ISelectionChangedListener() {
		public void selectionChanged(SelectionChangedEvent event) {

			if (event.getSource() instanceof VexWidget) {

				VexWidget vexWidget = (VexWidget) event.getSource();
				if (vexWidget.isFocusControl() && getTreeViewer() != null) {
					VEXElement element = vexWidget.getCurrentElement();
					VEXElement outlineElement = outlineProvider
							.getOutlineElement(element);
					getTreeViewer().refresh(outlineElement);
					getTreeViewer().setSelection(
							new StructuredSelection(outlineElement), true);
				}

			} else {

				// it's our tree control being selected
				TreeViewer treeViewer = (TreeViewer) event.getSource();
				if (treeViewer.getTree().isFocusControl()) {
					TreeItem[] selected = treeViewer.getTree().getSelection();
					if (selected.length > 0) {

						Element element = (Element) selected[0].getData();
						VexWidget vexWidget = vexEditor.getVexWidget();

						// Moving to the end of the element first is a cheap
						// way to make sure we end up with the
						// caret at the top of the viewport
						vexWidget.moveTo(element.getEndOffset());
						vexWidget.moveTo(element.getStartOffset() + 1);

					}
				}
			}
		}
	};

	private IVexEditorListener vexEditorListener = new IVexEditorListener() {

		public void documentLoaded(VexEditorEvent event) {
			showTreeViewer();
		}

		public void documentUnloaded(VexEditorEvent event) {
			showLabel(Messages.getString("DocumentOutlinePage.reloading")); //$NON-NLS-1$
		}

	};
}