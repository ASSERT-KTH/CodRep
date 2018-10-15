//this.setTitleToolTip(input.getToolTipText());

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

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.URL;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IMarker;
import org.eclipse.core.resources.IResourceChangeEvent;
import org.eclipse.core.resources.IResourceChangeListener;
import org.eclipse.core.resources.IResourceDelta;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.IPath;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Platform;
import org.eclipse.core.runtime.preferences.IPreferencesService;
import org.eclipse.core.runtime.preferences.InstanceScope;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.commands.ActionHandler;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorSite;
import org.eclipse.ui.IFileEditorInput;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.contexts.IContextService;
import org.eclipse.ui.dialogs.SaveAsDialog;
import org.eclipse.ui.editors.text.ILocationProvider;
import org.eclipse.ui.handlers.IHandlerService;
import org.eclipse.ui.part.EditorPart;
import org.eclipse.ui.part.FileEditorInput;
import org.eclipse.ui.views.contentoutline.IContentOutlinePage;
import org.eclipse.ui.views.properties.IPropertySheetPage;
import org.eclipse.ui.views.properties.IPropertySource;
import org.eclipse.ui.views.properties.IPropertySourceProvider;
import org.eclipse.ui.views.properties.PropertySheetPage;
import org.eclipse.wst.xml.vex.core.internal.core.ListenerList;
import org.eclipse.wst.xml.vex.core.internal.dom.Document;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentReader;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentWriter;
import org.eclipse.wst.xml.vex.core.internal.dom.Element;
import org.eclipse.wst.xml.vex.core.internal.dom.IWhitespacePolicy;
import org.eclipse.wst.xml.vex.core.internal.dom.IWhitespacePolicyFactory;
import org.eclipse.wst.xml.vex.core.internal.dom.Validator;
import org.eclipse.wst.xml.vex.core.internal.widget.CssWhitespacePolicy;
import org.eclipse.wst.xml.vex.ui.internal.VexPlugin;
import org.eclipse.wst.xml.vex.ui.internal.action.ChangeElementAction;
import org.eclipse.wst.xml.vex.ui.internal.action.DeleteColumnAction;
import org.eclipse.wst.xml.vex.ui.internal.action.DeleteRowAction;
import org.eclipse.wst.xml.vex.ui.internal.action.DuplicateSelectionAction;
import org.eclipse.wst.xml.vex.ui.internal.action.InsertColumnAfterAction;
import org.eclipse.wst.xml.vex.ui.internal.action.InsertColumnBeforeAction;
import org.eclipse.wst.xml.vex.ui.internal.action.InsertElementAction;
import org.eclipse.wst.xml.vex.ui.internal.action.InsertRowAboveAction;
import org.eclipse.wst.xml.vex.ui.internal.action.InsertRowBelowAction;
import org.eclipse.wst.xml.vex.ui.internal.action.MoveColumnLeftAction;
import org.eclipse.wst.xml.vex.ui.internal.action.MoveColumnRightAction;
import org.eclipse.wst.xml.vex.ui.internal.action.MoveRowDownAction;
import org.eclipse.wst.xml.vex.ui.internal.action.MoveRowUpAction;
import org.eclipse.wst.xml.vex.ui.internal.action.NextTableCellAction;
import org.eclipse.wst.xml.vex.ui.internal.action.PasteTextAction;
import org.eclipse.wst.xml.vex.ui.internal.action.PreviousTableCellAction;
import org.eclipse.wst.xml.vex.ui.internal.action.RemoveElementAction;
import org.eclipse.wst.xml.vex.ui.internal.action.RestoreLastSelectionAction;
import org.eclipse.wst.xml.vex.ui.internal.action.SplitAction;
import org.eclipse.wst.xml.vex.ui.internal.action.SplitItemAction;
import org.eclipse.wst.xml.vex.ui.internal.action.VexActionAdapter;
import org.eclipse.wst.xml.vex.ui.internal.config.ConfigEvent;
import org.eclipse.wst.xml.vex.ui.internal.config.ConfigRegistry;
import org.eclipse.wst.xml.vex.ui.internal.config.DocumentType;
import org.eclipse.wst.xml.vex.ui.internal.config.IConfigListener;
import org.eclipse.wst.xml.vex.ui.internal.config.Style;
import org.eclipse.wst.xml.vex.ui.internal.swt.VexWidget;
import org.osgi.service.prefs.BackingStoreException;
import org.osgi.service.prefs.Preferences;
import org.xml.sax.EntityResolver;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

/**
 * Editor for editing XML file using the VexWidget.
 */
public class VexEditor extends EditorPart {

	/**
	 * ID of this editor extension.
	 */
	public static final String ID = "org.eclipse.wst.xml.vex.ui.internal.editor.VexEditor"; //$NON-NLS-1$

	/**
	 * Class constructor.
	 */
	public VexEditor() {
		this.debugging = VexPlugin.getInstance().isDebugging()
				&& "true".equalsIgnoreCase(Platform.getDebugOption(VexPlugin.ID + "/debug/layout")); //$NON-NLS-1$ //$NON-NLS-2$
	}

	/**
	 * Add a VexEditorListener to the notification list.
	 * 
	 * @param listener
	 *            VexEditorListener to be added.
	 */
	public void addVexEditorListener(IVexEditorListener listener) {
		this.vexEditorListeners.add(listener);
	}

	public void dispose() {
		super.dispose();

		if (this.parentControl != null) {
			// createPartControl was called, so we must de-register from config
			// events
			ConfigRegistry.getInstance().removeConfigListener(
					this.configListener);
		}

		if (getEditorInput() instanceof IFileEditorInput) {
			ResourcesPlugin.getWorkspace().removeResourceChangeListener(
					this.resourceChangeListener);
		}

	}

	public void doSave(IProgressMonitor monitor) {

		IEditorInput input = this.getEditorInput();
		OutputStream os = null;
		try {
			this.resourceChangeListener.setSaving(true);
			DocumentWriter writer = new DocumentWriter();
			writer.setWhitespacePolicy(new CssWhitespacePolicy(this.style
					.getStyleSheet()));

			if (input instanceof IFileEditorInput) {
				ByteArrayOutputStream baos = new ByteArrayOutputStream();
				writer.write(this.doc, baos);
				baos.close();
				ByteArrayInputStream bais = new ByteArrayInputStream(baos
						.toByteArray());
				((IFileEditorInput) input).getFile().setContents(bais, false,
						false, monitor);
			} else {
				os = new FileOutputStream(((ILocationProvider) input).getPath(
						input).toFile());
				writer.write(this.doc, os);
			}

			this.savedUndoDepth = this.vexWidget.getUndoDepth();
			this.firePropertyChange(EditorPart.PROP_DIRTY);

		} catch (Exception ex) {
			monitor.setCanceled(true);
			String title = Messages.getString("VexEditor.errorSaving.title"); //$NON-NLS-1$
			String message = MessageFormat.format(Messages
					.getString("VexEditor.errorSaving.message"), //$NON-NLS-1$
					new Object[] { input.getName(), ex.getMessage() });
			MessageDialog.openError(this.getEditorSite().getShell(), title,
					message);
			VexPlugin.getInstance().log(IStatus.ERROR, message, ex);
		} finally {
			if (os != null) {
				try {
					os.close();
				} catch (IOException e) {
				}
			}
			this.resourceChangeListener.setSaving(false);
		}
	}

	public void doSaveAs() {
		SaveAsDialog dlg = new SaveAsDialog(this.getSite().getShell());
		int result = dlg.open();
		if (result == Window.OK) {
			IPath path = dlg.getResult();
			try {
				this.resourceChangeListener.setSaving(true);
				ByteArrayOutputStream baos = new ByteArrayOutputStream();
				DocumentWriter writer = new DocumentWriter();
				writer.setWhitespacePolicy(new CssWhitespacePolicy(this.style
						.getStyleSheet()));
				writer.write(this.doc, baos);
				baos.close();

				ByteArrayInputStream bais = new ByteArrayInputStream(baos
						.toByteArray());
				IFile file = ResourcesPlugin.getWorkspace().getRoot().getFile(
						path);
				file.create(bais, false, null);

				IFileEditorInput input = new FileEditorInput(file);
				this.setInput(input);
				this.savedUndoDepth = this.vexWidget.getUndoDepth();

				this.firePropertyChange(EditorPart.PROP_DIRTY);
				this.firePropertyChange(EditorPart.PROP_INPUT);
				this.firePropertyChange(EditorPart.PROP_TITLE);

			} catch (Exception ex) {
				String title = Messages
						.getString("VexEditor.errorSaving.title"); //$NON-NLS-1$
				String message = MessageFormat.format(Messages
						.getString("VexEditor.errorSaving.message"), //$NON-NLS-1$
						new Object[] { path, ex.getMessage() });
				MessageDialog.openError(this.getEditorSite().getShell(), title,
						message);
				VexPlugin.getInstance().log(IStatus.ERROR, message, ex);
			} finally {
				this.resourceChangeListener.setSaving(false);
			}
		}

	}

	/**
	 * Return a reasonable style for the given doctype.
	 * 
	 * @param publicId
	 *            Public ID for which to return the style.
	 */
	public static Style findStyleForDoctype(String publicId) {

		IPreferencesService preferences = Platform.getPreferencesService();
		String key = getStylePreferenceKey(publicId);
		String preferredStyleId = preferences.getString(VexPlugin.ID, key,
				null, null);

		Preferences prefs = new InstanceScope().getNode(VexPlugin.ID);
		preferredStyleId = prefs.get(key, null);

		Style firstStyle = null;
		ConfigRegistry registry = ConfigRegistry.getInstance();
		List styles = registry.getAllConfigItems(Style.EXTENSION_POINT);
		for (Iterator it = styles.iterator(); it.hasNext();) {
			Style style = (Style) it.next();
			if (style.appliesTo(publicId)) {
				if (firstStyle == null) {
					firstStyle = style;
				}
				if (style.getUniqueId().equals(preferredStyleId)) {
					return style;
				}
			}
		}
		return firstStyle;
	}

	/**
	 * Returns the DocumentType associated with this editor.
	 */
	public DocumentType getDocumentType() {
		return this.doctype;
	}

	/**
	 * Returns the Style currently associated with the editor. May be null.
	 */
	public Style getStyle() {
		return style;
	}

	/**
	 * Returns the VexWidget that implements this editor.
	 */
	public VexWidget getVexWidget() {
		return this.vexWidget;
	}

	public void gotoMarker(IMarker marker) {
		// TODO Auto-generated method stub

	}

	public void init(IEditorSite site, IEditorInput input)
			throws PartInitException {

		this.setSite(site);
		this.setInput(input);

		this.getEditorSite().setSelectionProvider(this.selectionProvider);
		this.getEditorSite().getSelectionProvider()
				.addSelectionChangedListener(selectionChangedListener);

		if (input instanceof IFileEditorInput) {
			ResourcesPlugin.getWorkspace().addResourceChangeListener(
					this.resourceChangeListener,
					IResourceChangeEvent.POST_CHANGE);
		}
	}

	private void loadInput() {

		if (this.vexWidget != null) {
			this.vexEditorListeners.fireEvent(
					"documentUnloaded", new VexEditorEvent(this)); //$NON-NLS-1$
		}

		this.loaded = false;

		IEditorInput input = this.getEditorInput();

		try {
			long start = System.currentTimeMillis();

			IPath inputPath = null;

			if (input instanceof IFileEditorInput) {
				inputPath = ((IFileEditorInput) input).getFile()
						.getRawLocation();
			} else if (input instanceof ILocationProvider) {
				// Yuck, this a crappy way for Eclipse to do this
				// How about an exposed IJavaFileEditorInput, pleeze?
				inputPath = ((ILocationProvider) input).getPath(input);
			} else {
				String msg = MessageFormat.format(Messages
						.getString("VexEditor.unknownInputClass"), //$NON-NLS-1$
						new Object[] { input.getClass() });
				this.showLabel(msg);
				return;
			}

			URL url = inputPath.toFile().toURL();

			DocumentReader reader = new DocumentReader();
			reader.setDebugging(this.debugging);
			reader.setEntityResolver(entityResolver);
			reader.setWhitespacePolicyFactory(wsFactory);
			this.doctype = null;
			this.doc = reader.read(url);

			if (this.debugging) {
				long end = System.currentTimeMillis();
				System.out
						.println("Parsed document in " + (end - start) + "ms"); //$NON-NLS-1$ //$NON-NLS-2$
			}

			// this.doctype is set either by wsPolicyFactory or entityResolver
			// this.style is set by wsPolicyFactory
			// Otherwise, a PartInitException would have been thrown by now

			Validator validator = this.doctype.getValidator();
			if (validator != null) {
				this.doc.setValidator(validator);
				if (this.debugging) {
					long end = System.currentTimeMillis();
					System.out
							.println("Got validator in " + (end - start) + "ms"); //$NON-NLS-1$ //$NON-NLS-2$
				}
			}

			this.showVexWidget();

			this.vexWidget.setDebugging(debugging);
			this.vexWidget.setDocument(this.doc, this.style.getStyleSheet());

			if (this.updateDoctypeDecl) {
				this.doc.setPublicID(this.doctype.getPublicId());
				this.doc.setSystemID(this.doctype.getSystemId());
				this.doSave(null);
			}

			this.loaded = true;
			this.savedUndoDepth = this.vexWidget.getUndoDepth();
			firePropertyChange(EditorPart.PROP_DIRTY);
			this.wasDirty = isDirty();

			this.vexEditorListeners.fireEvent(
					"documentLoaded", new VexEditorEvent(this)); //$NON-NLS-1$

		} catch (SAXParseException ex) {

			if (ex.getException() instanceof NoRegisteredDoctypeException) {
				// TODO doc did not have document type and the user
				// declined to select another one. Should fail silently.
				String msg;
				NoRegisteredDoctypeException ex2 = (NoRegisteredDoctypeException) ex
						.getException();
				if (ex2.getPublicId() == null) {
					msg = Messages.getString("VexEditor.noDoctype"); //$NON-NLS-1$
				} else {
					msg = MessageFormat.format(Messages
							.getString("VexEditor.unknownDoctype"), //$NON-NLS-1$
							new Object[] { ex2.getPublicId() });
				}
				this.showLabel(msg);
			} else if (ex.getException() instanceof NoStyleForDoctypeException) {
				String msg = MessageFormat.format(Messages
						.getString("VexEditor.noStyles"), //$NON-NLS-1$
						new Object[] { this.doctype.getPublicId() });
				this.showLabel(msg);
			} else {
				String file = ex.getSystemId();
				if (file == null) {
					file = input.getName();
				}

				String msg = MessageFormat.format(Messages
						.getString("VexEditor.parseError"), //$NON-NLS-1$
						new Object[] { new Integer(ex.getLineNumber()), file,
								ex.getLocalizedMessage() });

				this.showLabel(msg);

				VexPlugin.getInstance().log(IStatus.ERROR, msg, ex);
			}

		} catch (Exception ex) {

			String msg = MessageFormat.format(Messages
					.getString("VexEditor.unexpectedError"), //$NON-NLS-1$
					new Object[] { input.getName() });

			VexPlugin.getInstance().log(IStatus.ERROR, msg, ex);

			this.showLabel(msg);
		}
	}

	public boolean isDirty() {
		if (this.vexWidget != null) {
			return this.savedUndoDepth != this.vexWidget.getUndoDepth();
		} else {
			return false;
		}
	}

	/**
	 * Returns true if this editor has finished loading its document.
	 */
	public boolean isLoaded() {
		return this.loaded;
	}

	public boolean isSaveAsAllowed() {
		return true;
	}

	public void createPartControl(Composite parent) {

		this.parentControl = parent;

		ConfigRegistry registry = ConfigRegistry.getInstance();

		registry.addConfigListener(this.configListener);

		if (registry.isConfigLoaded()) {
			this.loadInput();
		} else {
			this.showLabel(Messages.getString("VexEditor.loading")); //$NON-NLS-1$
		}
	}

	/**
	 * Remove a VexEditorListener from the notification list.
	 * 
	 * @param listener
	 *            VexEditorListener to be removed.
	 */
	public void removeVexEditorListener(IVexEditorListener listener) {
		this.vexEditorListeners.remove(listener);
	}

	public void setFocus() {
		if (this.vexWidget != null) {
			this.vexWidget.setFocus();
			setStatus(getLocation());
		}
	}

	protected void setInput(IEditorInput input) {
		super.setInput(input);
		this.setPartName(input.getName());
		this.setContentDescription(input.getName());
		this.setTitleToolTip(input.getToolTipText());
	}

	public void setStatus(String text) {
		// this.statusLabel.setText(text);
		this.getEditorSite().getActionBars().getStatusLineManager().setMessage(
				text);
	}

	/**
	 * Sets the style for this editor.
	 * 
	 * @param style
	 *            Style to use.
	 */
	public void setStyle(Style style) {
		this.style = style;
		if (this.vexWidget != null) {
			this.vexWidget.setStyleSheet(style.getStyleSheet());
			Preferences prefs = new InstanceScope().getNode(VexPlugin.ID);
			String key = getStylePreferenceKey(this.doc.getPublicID());
			prefs.put(key, style.getUniqueId());
			try {
				prefs.flush();
			} catch (BackingStoreException e) {
				VexPlugin
						.getInstance()
						.log(
								IStatus.ERROR,
								Messages
										.getString("VexEditor.errorSavingStylePreference"), e); //$NON-NLS-1$
			}
		}
	}

	// ========================================================= PRIVATE

	private boolean debugging;

	private Composite parentControl;
	private Label loadingLabel;

	private boolean loaded;
	private DocumentType doctype;
	private Document doc;
	private Style style;

	private VexWidget vexWidget;

	private int savedUndoDepth;
	private boolean wasDirty;
	// private Label statusLabel;

	// This is true if the document's doctype decl is missing or unrecognized
	// AND the user selected a new document type
	// AND the user wants to always use the doctype for this document
	private boolean updateDoctypeDecl;

	private ListenerList vexEditorListeners = new ListenerList(
			IVexEditorListener.class, VexEditorEvent.class);

	private SelectionProvider selectionProvider = new SelectionProvider();

	/**
	 * Returns the preference key used to access the style ID for documents with
	 * the same public ID as the current document.
	 */
	private static String getStylePreferenceKey(String publicId) {
		return publicId + ".style"; //$NON-NLS-1$
	}

	private void showLabel(String message) {
		if (this.loadingLabel == null) {
			if (this.vexWidget != null) {
				this.vexWidget.dispose();
				this.vexWidget = null;
			}
			this.loadingLabel = new Label(this.parentControl, SWT.WRAP);
		}
		this.loadingLabel.setText(message);
		this.parentControl.layout(true);
	}

	private void showVexWidget() {

		if (this.vexWidget != null) {
			return;
		}

		if (this.loadingLabel != null) {
			this.loadingLabel.dispose();
			this.loadingLabel = null;
		}

		GridLayout layout = new GridLayout();
		layout.numColumns = 1;
		layout.verticalSpacing = 0;
		layout.marginHeight = 0;
		layout.marginWidth = 0;
		this.parentControl.setLayout(layout);
		GridData gd;

		// StatusPanel statusPanel = new StatusPanel(this.parentControl);

		// Composite statusPanel = new Composite(this.parentControl, SWT.NONE);
		// statusPanel.setLayout(new GridLayout());
		// gd = new GridData();
		// gd.grabExcessHorizontalSpace = true;
		// gd.horizontalAlignment = GridData.FILL;
		// statusPanel.setLayoutData(gd);

		// this.statusLabel = new Label(statusPanel, SWT.NONE);
		// gd = new GridData();
		// gd.grabExcessHorizontalSpace = true;
		// gd.horizontalAlignment = GridData.FILL;
		// this.statusLabel.setLayoutData(gd);

		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.grabExcessVerticalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		gd.verticalAlignment = GridData.FILL;

		this.vexWidget = new VexWidget(this.parentControl, SWT.V_SCROLL);
		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.grabExcessVerticalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		gd.verticalAlignment = GridData.FILL;
		this.vexWidget.setLayoutData(gd);

		VexActionBarContributor contributor = (VexActionBarContributor) this
				.getEditorSite().getActionBarContributor();

		MenuManager menuMgr = contributor.getContextMenuManager();
		this.getSite().registerContextMenu(menuMgr, this.vexWidget);
		this.vexWidget.setMenu(menuMgr.createContextMenu(this.vexWidget));

		this.savedUndoDepth = this.vexWidget.getUndoDepth();

		// new for scopes
		IContextService cs = (IContextService) this.getSite().getService(
				IContextService.class);
		cs.activateContext("org.eclipse.wst.xml.vex.ui.VexEditorContext");

		IHandlerService hs = (IHandlerService) this.getSite().getService(
				IHandlerService.class);

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.ChangeElementAction",
				new ActionHandler(new VexActionAdapter(this,
						new ChangeElementAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.DeleteColumnAction",
				new ActionHandler(new VexActionAdapter(this,
						new DeleteColumnAction())));

		hs.activateHandler("org.eclipse.wst.xml.vex.ui.action.DeleteRowAction",
				new ActionHandler(new VexActionAdapter(this,
						new DeleteRowAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.DuplicateSelectionAction",
				new ActionHandler(new VexActionAdapter(this,
						new DuplicateSelectionAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.InsertColumnAfterAction",
				new ActionHandler(new VexActionAdapter(this,
						new InsertColumnAfterAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.InsertColumnBeforeAction",
				new ActionHandler(new VexActionAdapter(this,
						new InsertColumnBeforeAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.editor.action.InsertElementAction",
				new ActionHandler(new VexActionAdapter(this,
						new InsertElementAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.InsertRowAboveAction",
				new ActionHandler(new VexActionAdapter(this,
						new InsertRowAboveAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.InsertRowBelowAction",
				new ActionHandler(new VexActionAdapter(this,
						new InsertRowBelowAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.MoveColumnLeftAction",
				new ActionHandler(new VexActionAdapter(this,
						new MoveColumnLeftAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.MoveColumnRightAction",
				new ActionHandler(new VexActionAdapter(this,
						new MoveColumnRightAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.MoveRowDownAction",
				new ActionHandler(new VexActionAdapter(this,
						new MoveRowDownAction())));

		hs.activateHandler("org.eclipse.wst.xml.vex.ui.action.MoveRowUpAction",
				new ActionHandler(new VexActionAdapter(this,
						new MoveRowUpAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.NextTableCellAction",
				new ActionHandler(new VexActionAdapter(this,
						new NextTableCellAction())));

		hs.activateHandler("org.eclipse.wst.xml.vex.ui.action.PasteTextAction",
				new ActionHandler(new VexActionAdapter(this,
						new PasteTextAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.PreviousTableCellAction",
				new ActionHandler(new VexActionAdapter(this,
						new PreviousTableCellAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.RemoveElementAction",
				new ActionHandler(new VexActionAdapter(this,
						new RemoveElementAction())));

		hs.activateHandler(
				"org.eclipse.wst.xml.vex.ui.action.RestoreLastSelectionAction",
				new ActionHandler(new VexActionAdapter(this,
						new RestoreLastSelectionAction())));

		hs
				.activateHandler(
						"org.eclipse.wst.xml.vex.ui.action.SplitAction",
						new ActionHandler(new VexActionAdapter(this,
								new SplitAction())));

		hs.activateHandler("org.eclipse.wst.xml.vex.ui.action.SplitItemAction",
				new ActionHandler(new VexActionAdapter(this,
						new SplitItemAction())));

		this.vexWidget.addSelectionChangedListener(this.selectionProvider);

		this.parentControl.layout(true);

	}

	private void handleResourceChanged(IResourceDelta delta) {

		if (delta.getKind() == IResourceDelta.CHANGED) {
			if ((delta.getFlags() & IResourceDelta.CONTENT) != 0) {
				this.handleResourceContentChanged();
			}
		} else if (delta.getKind() == IResourceDelta.REMOVED) {
			if ((delta.getFlags() & IResourceDelta.MOVED_TO) != 0) {
				IPath toPath = delta.getMovedToPath();
				IFile file = ResourcesPlugin.getWorkspace().getRoot().getFile(
						toPath);
				this.setInput(new FileEditorInput(file));
			} else {
				if (!this.isDirty()) {
					this.getEditorSite().getPage().closeEditor(this, false);
				} else {
					this.handleResourceDeleted();
				}
			}
		}

	}

	private void handleResourceContentChanged() {

		if (!this.isDirty()) {
			this.loadInput();
		} else {

			String message = MessageFormat.format(Messages
					.getString("VexEditor.docChanged.message"), //$NON-NLS-1$
					new Object[] { this.getEditorInput().getName() });

			MessageDialog dlg = new MessageDialog(
					this.getSite().getShell(),
					Messages.getString("VexEditor.docChanged.title"), //$NON-NLS-1$
					null,
					message,
					MessageDialog.QUESTION,
					new String[] {
							Messages.getString("VexEditor.docChanged.discard"), //$NON-NLS-1$
							Messages
									.getString("VexEditor.docChanged.overwrite") }, //$NON-NLS-1$
					1);

			int result = dlg.open();

			if (result == 0) { // Discard my changes
				this.loadInput();
			} else { // Overwrite other changes
				this.doSave(null);
			}
		}
	}

	private void handleResourceDeleted() {

		String message = MessageFormat.format(Messages
				.getString("VexEditor.docDeleted.message"), //$NON-NLS-1$
				new Object[] { this.getEditorInput().getName() });

		MessageDialog dlg = new MessageDialog(this.getSite().getShell(),
				Messages.getString("VexEditor.docDeleted.title"), //$NON-NLS-1$
				null, message, MessageDialog.QUESTION, new String[] {
						Messages.getString("VexEditor.docDeleted.discard"), //$NON-NLS-1$ 
						Messages.getString("VexEditor.docDeleted.save") }, //$NON-NLS-1$
				1);

		int result = dlg.open();

		if (result == 0) { // Discard

			this.getEditorSite().getPage().closeEditor(this, false);

		} else { // Save

			this.doSaveAs();

			// Check if they saved or not. If not, close the editor
			if (!this.getEditorInput().exists()) {
				this.getEditorSite().getPage().closeEditor(this, false);
			}
		}
	}

	// Listen for stylesheet changes and respond appropriately
	private IConfigListener configListener = new IConfigListener() {

		public void configChanged(ConfigEvent e) {
			if (style != null) {
				ConfigRegistry registry = ConfigRegistry.getInstance();
				String currId = style.getUniqueId();
				Style newStyle = (Style) registry.getConfigItem(
						Style.EXTENSION_POINT, currId);
				if (newStyle == null) {
					// Oops, style went bye-bye
					// Let's just hold on to it in case it comes back later
				} else {
					vexWidget.setStyleSheet(newStyle.getStyleSheet());
					style = newStyle;
				}
			}
		}

		public void configLoaded(ConfigEvent e) {
			loadInput();
		}
	};

	private ISelectionChangedListener selectionChangedListener = new ISelectionChangedListener() {
		public void selectionChanged(SelectionChangedEvent event) {
			if (isDirty() != wasDirty) {
				firePropertyChange(EditorPart.PROP_DIRTY);
				wasDirty = isDirty();
			}
			setStatus(getLocation());
		}
	};

	private EntityResolver entityResolver = new EntityResolver() {
		public InputSource resolveEntity(String publicId, String systemId)
				throws SAXException, IOException {

			// System.out.println("### Resolving publicId " + publicId +
			// ", systemId " + systemId);

			if (doctype == null) {
				//
				// If doctype hasn't already been set, this must be the doctype
				// decl.
				//
				if (publicId != null) {
					doctype = DocumentType.getDocumentType(publicId);
				}

				if (doctype == null) {
					DocumentTypeSelectionDialog dlg = DocumentTypeSelectionDialog
							.create(getSite().getShell(), publicId);
					dlg.open();
					doctype = dlg.getDoctype();
					updateDoctypeDecl = dlg.alwaysUseThisDoctype();

					if (doctype == null) {
						throw new NoRegisteredDoctypeException(publicId);
					}
				}

				URL url = doctype.getResourceUrl();

				if (url == null) {
					String message = MessageFormat.format(Messages
							.getString("VexEditor.noUrlForDoctype"), //$NON-NLS-1$
							new Object[] { publicId });
					throw new RuntimeException(message);
				}

				return new InputSource(url.toString());
			} else {
				return null;
			}
		}
	};

	private IWhitespacePolicyFactory wsFactory = new IWhitespacePolicyFactory() {
		public IWhitespacePolicy getPolicy(String publicId) {

			if (doctype == null) {
				DocumentTypeSelectionDialog dlg = DocumentTypeSelectionDialog
						.create(getSite().getShell(), publicId);
				dlg.open();
				doctype = dlg.getDoctype();
				updateDoctypeDecl = dlg.alwaysUseThisDoctype();

				if (doctype == null) {
					throw new NoRegisteredDoctypeException(null);
				}
			}

			style = VexEditor.findStyleForDoctype(doctype.getPublicId());
			if (style == null) {
				throw new NoStyleForDoctypeException(doctype);
			}

			return new CssWhitespacePolicy(style.getStyleSheet());
		}

	};

	private class ResourceChangeListener implements IResourceChangeListener {

		public void resourceChanged(IResourceChangeEvent event) {

			if (this.saving) {
				return;
			}

			IPath path = ((IFileEditorInput) getEditorInput()).getFile()
					.getFullPath();
			final IResourceDelta delta = event.getDelta().findMember(path);
			if (delta != null) {
				Display.getDefault().asyncExec(new Runnable() {
					public void run() {
						handleResourceChanged(delta);
					}
				});
			}
		}

		public void setSaving(boolean saving) {
			this.saving = saving;
		}

		// Set to true so we can ignore change events while we're saving.
		private boolean saving;
	};

	private ResourceChangeListener resourceChangeListener = new ResourceChangeListener();

	//
	// wsFactory communicates failures back to init() through the XML parser
	// by throwing one of these exceptions
	//

	/**
	 * Indicates that no document type is registered for the public ID in the
	 * document, or that the document does not have a PUBLIC DOCTYPE decl, in
	 * which case publicId is null.
	 */
	private class NoRegisteredDoctypeException extends RuntimeException {
		public NoRegisteredDoctypeException(String publicId) {
			this.publicId = publicId;
		}

		public String getPublicId() {
			return this.publicId;
		}

		private String publicId;
	}

	/**
	 * Indicates that the document was matched to a registered doctype, but that
	 * the given doctype does not have a matching style.
	 */
	private class NoStyleForDoctypeException extends RuntimeException {

		public NoStyleForDoctypeException(DocumentType doctype) {
			this.doctype = doctype;
		}

		public DocumentType getDoctype() {
			return this.doctype;
		}

		private DocumentType doctype;
	}

	private String getLocation() {
		List path = new ArrayList();
		Element element = this.vexWidget.getCurrentElement();
		while (element != null) {
			path.add(element.getName());
			element = element.getParent();
		}
		Collections.reverse(path);
		StringBuffer sb = new StringBuffer(path.size() * 15);
		for (int i = 0; i < path.size(); i++) {
			sb.append("/"); //$NON-NLS-1$
			sb.append(path.get(i));
		}
		return sb.toString();
	}

	public Object getAdapter(Class adapter) {

		if (adapter == IContentOutlinePage.class) {

			return new DocumentOutlinePage();

		} else if (adapter == IPropertySheetPage.class) {
			PropertySheetPage page = new PropertySheetPage();
			page.setPropertySourceProvider(new IPropertySourceProvider() {
				public IPropertySource getPropertySource(Object object) {
					if (object instanceof Element) {
						IStructuredSelection sel = (IStructuredSelection) vexWidget
								.getSelection();
						boolean multi = (sel != null && sel.size() > 1);
						Validator validator = vexWidget.getDocument()
								.getValidator();
						return new ElementPropertySource((Element) object,
								validator, multi);
					} else {
						return null;
					}
				}
			});
			return page;
		} else {
			return super.getAdapter(adapter);
		}
	}

}