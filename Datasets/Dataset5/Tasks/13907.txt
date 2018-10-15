public static final String ID = "org.eclipse.m2t.common.recipe.recipeBrowser.RecipeBrowserView"; //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2005, 2007 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/

package org.eclipse.m2t.common.recipe.ui.recipeBrowser;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IResourceChangeEvent;
import org.eclipse.core.resources.IResourceChangeListener;
import org.eclipse.core.resources.IResourceDelta;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.ActionContributionItem;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.viewers.ColumnPixelData;
import org.eclipse.jface.viewers.IDoubleClickListener;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerFilter;
import org.eclipse.m2t.common.recipe.core.Check;
import org.eclipse.m2t.common.recipe.core.CheckParameter;
import org.eclipse.m2t.common.recipe.core.CheckSet;
import org.eclipse.m2t.common.recipe.core.EvalStatus;
import org.eclipse.m2t.common.recipe.core.EvalTrigger;
import org.eclipse.m2t.common.recipe.eval.EvaluationContext;
import org.eclipse.m2t.common.recipe.io.CheckRegistry;
import org.eclipse.m2t.common.recipe.ui.RecipePlugin;
import org.eclipse.m2t.common.recipe.ui.recipeBrowser.providers.ParameterContentProvider;
import org.eclipse.m2t.common.recipe.ui.recipeBrowser.providers.ParameterLabelProvider;
import org.eclipse.m2t.common.recipe.ui.recipeBrowser.providers.RecipeContentProvider;
import org.eclipse.m2t.common.recipe.ui.recipeBrowser.providers.RecipeLabelProvider;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.dnd.Clipboard;
import org.eclipse.swt.dnd.TextTransfer;
import org.eclipse.swt.dnd.Transfer;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IWorkbenchActionConstants;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.progress.IWorkbenchSiteProgressService;

public class RecipeBrowserView extends ViewPart implements IResourceChangeListener, ISelectionChangedListener {

	public static final String ID = "org.openarchitectureware.eclipse.recipeBrowser.RecipeBrowserView"; //$NON-NLS-1$

	private Table parameterTable;

	private TableViewer tableViewer;

	private RecipeContentProvider contentProvider;

	private RecipeLabelProvider labelProvider;

	private TreeViewer treeViewer;

	private ViewerFilter okFilter = null;

	private Text descriptionText;

	private IWorkbenchSiteProgressService siteService = null;

	private Label statusLabel;

	private IFile currentFileResource;

	public static final long NOT_SET = -1;

	private long lastEventTimestamp = NOT_SET;

	private WatcherThread watcherThread;

	public void createPartControl(Composite parent) {
		siteService = (IWorkbenchSiteProgressService) this.getSite().getAdapter(IWorkbenchSiteProgressService.class);
		GridLayout layout = new GridLayout(1, false);
		parent.setLayout(layout);
		SashForm s = new SashForm(parent, SWT.HORIZONTAL);
		s.setLayoutData(new GridData(GridData.FILL_BOTH));
		createLeftSide(s);
		createRightSide(s);
		statusLabel = new Label(parent, SWT.NONE);
		statusLabel.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		createFilter();
		update();

		// FIXME: add fix me again
		// addButton(new QuickFixAllCmd());
		addButton(new CollapseAllCmd());
		addButton(new EvaluateCmd());
		addButton(new HideOkCmd());
		// addMenuSeparator();
		addMenuItem(new EvaluateAllCmd());
		addMenuItem(new ReloadCmd());

		watcherThread = new WatcherThread();
		watcherThread.start();
	}

	public void setFocus() {
		treeViewer.getControl().setFocus();
	}

	private void createRightSide(SashForm parent) {
		SashForm s = new SashForm(parent, SWT.VERTICAL);
		createTable(s);
		createTableViewer();
		descriptionText = new Text(s, SWT.MULTI | SWT.WRAP);
	}

	private void createTableViewer() {
		tableViewer = new TableViewer(parameterTable);
		tableViewer.setContentProvider(new ParameterContentProvider());
		tableViewer.setLabelProvider(new ParameterLabelProvider());
		tableViewer.setInput(null);
		tableViewer.addDoubleClickListener(new IDoubleClickListener() {
			public void doubleClick(org.eclipse.jface.viewers.DoubleClickEvent event) {
				IStructuredSelection sel = (IStructuredSelection) tableViewer.getSelection();
				if (sel != null) {
					CheckParameter p = (CheckParameter) sel.getFirstElement();
					Clipboard clipboard = new Clipboard(Display.getCurrent());
					clipboard.setContents(new String[] { p.getValue().toString() }, new Transfer[] { TextTransfer.getInstance() });
				}
			};
		});
	}

	private void createTable(Composite parent) {
		parameterTable = new Table(parent, SWT.MULTI | SWT.FULL_SELECTION);
		AutoResizeTableLayout autoResizeTableLayout = new AutoResizeTableLayout(parameterTable);
		parameterTable.setLayout(autoResizeTableLayout);
		parameterTable.setHeaderVisible(true);
		parameterTable.setLinesVisible(true);
		TableColumn iconC = new TableColumn(parameterTable, SWT.LEFT);
		iconC.setText(""); //$NON-NLS-1$
		autoResizeTableLayout.addColumnData(new ColumnPixelData(20, true));
		TableColumn typeC = new TableColumn(parameterTable, SWT.LEFT);
		typeC.setText(Messages.getString("RecipeBrowserView.Name")); //$NON-NLS-1$
		autoResizeTableLayout.addColumnData(new ColumnPixelData(100, true));
		TableColumn valueC = new TableColumn(parameterTable, SWT.LEFT);
		valueC.setText(Messages.getString("RecipeBrowserView.Value")); //$NON-NLS-1$
		autoResizeTableLayout.addColumnData(new ColumnPixelData(200, true));
	}

	private void createFilter() {
		okFilter = new ViewerFilter() {
			public boolean select(Viewer viewer, Object parentElement, Object element) {
				Check c = (Check) element;
				return c.getStatus() != EvalStatus.OK;
			}
		};
	}

	private void reload(boolean evaluate) {
		siteService.schedule(new LoadJob(treeViewer, siteService, evaluate), 0, true);
	}

	private void evaluate(EvaluationContext ctx) {
		siteService.schedule(new EvalJob(CheckRegistry.getChecks(), treeViewer, siteService, ctx), 0, true);
	}

	// This thread has the role to refresh the checks' state
	class WatcherThread extends Thread {
		// the longer the timeout's value is, the safer, but also...the longer!
		private static final int TIMEOUT = 2000;

		public void run() {
			while (true) {
				if ((lastEventTimestamp < (System.currentTimeMillis() - TIMEOUT)) && (lastEventTimestamp != NOT_SET)) {
					EvaluationContext ctx = new EvaluationContext();
					ctx.setEvaluateAll(true);
					ctx.setTrigger(EvalTrigger.ON_CHANGE);
					evaluate(ctx);
					lastEventTimestamp = NOT_SET;
				} else {
					try {
						sleep(3000);
					} catch (InterruptedException e) {
					}
				}
			}
		}
	}

	public void update() {
		if (CheckRegistry.getChecks() != null) {
			treeViewer.setInput(CheckRegistry.getChecks());
		}
	}

	private void createLeftSide(Composite parent) {
		contentProvider = new RecipeContentProvider();
		labelProvider = new RecipeLabelProvider();
		treeViewer = new TreeViewer(parent);
		treeViewer.setLabelProvider(labelProvider);
		treeViewer.setContentProvider(contentProvider);
		MenuManager menuMgr = new MenuManager("#PopupMenu"); //$NON-NLS-1$
		menuMgr.setRemoveAllWhenShown(true);
		menuMgr.addMenuListener(new IMenuListener() {
			public void menuAboutToShow(IMenuManager manager) {

				Check c = (Check) ((IStructuredSelection) treeViewer.getSelection()).getFirstElement();

				// To programmatically avoid
				// !MESSAGE Context menu missing standard group
				// 'org.eclipse.ui.IWorkbenchActionConstants.MB_ADDITIONS'.
				// (menu ids =
				// [org.openarchitectureware.eclipse.recipeBrowser.RecipeBrowserView])
				// part id =
				// org.openarchitectureware.eclipse.recipeBrowser.RecipeBrowserView)
				// error messages in the .log file :
				manager.add(new Separator(IWorkbenchActionConstants.MB_ADDITIONS));

				manager.add(new EvalCmd(c));

				// here we add a quick fix option in the contextual menu
				// but only for failed checks, that's of course !
				// we get the (first) element of a selection (in the case of a
				// multiple selection, like clicking and holding ctrl)
				// ... and we only fix composite checks (nodes, no
				// leaves) to ensure that the implicit dependance chain between
				// checks (which is the same as for quick fixers) is respected.

				// FIXME: add fix me again
				// if ((c instanceof CompositeCheck && c.getStatus() ==
				// EvalStatus.SOMECHILDRENFAILED))
				// manager.add(new QuickFixCmd(c));
			}
		});

		Menu menu = menuMgr.createContextMenu(treeViewer.getControl());
		treeViewer.getControl().setMenu(menu);
		// Be sure to register it so that other plug-ins can add actions.
		getSite().registerContextMenu(menuMgr, treeViewer);
		treeViewer.addSelectionChangedListener(contentProvider);
		treeViewer.addSelectionChangedListener(this);
	}

	public void selectionChanged(SelectionChangedEvent event) {
		if (event.getSelection() != null) {
			IStructuredSelection sel = (IStructuredSelection) event.getSelection();
			if (sel.getFirstElement() != null) {
				if (sel.getFirstElement() instanceof Check) {
					Check c = (Check) sel.getFirstElement();
					updateParameters(c);
					updateDescription(c);
					updateStatus(c);
				}
			}
		}

	}

	private void updateParameters(Check c) {
		((ParameterLabelProvider) tableViewer.getLabelProvider()).setCurrentCheck(c);
		tableViewer.setInput(c);
	}

	private void updateDescription(Check c) {
		if (c.getLongDescription() != null) {
			descriptionText.setText(c.getLongDescription());
		} else {
			descriptionText.setText(""); //$NON-NLS-1$
		}
	}

	private void updateStatus(Check c) {
		if (c.getStatusMessage() != null) {
			statusLabel.setText(" " + c.getStatusMessage()); //$NON-NLS-1$
		} else {
			statusLabel.setText(""); //$NON-NLS-1$
		}
	}

	public void resourceChanged(IResourceChangeEvent event) {
		handleDeltaForReload(event.getDelta());
		lastEventTimestamp = System.currentTimeMillis();
	}

	private void handleDeltaForReload(IResourceDelta delta) {
		// In some cases (e.g. closing a project) delta can be null
		if (delta==null) return;
		
		if (delta.getResource().equals(currentFileResource)) {
			EvaluationContext ctx = new EvaluationContext();
			ctx.setEvaluateAll(true);
			reload(true);
		} else {
			for (int i = 0; i < delta.getAffectedChildren().length; i++) {
				IResourceDelta d = delta.getAffectedChildren()[i];
				handleDeltaForReload(d);
			}
		}
	}

	public void openRecipeFile(IFile file) {
		if (currentFileResource != null) {
			currentFileResource.getWorkspace().removeResourceChangeListener(this);
		}
		currentFileResource = file;
		if (currentFileResource != null) {
			currentFileResource.getWorkspace().addResourceChangeListener(this);
		}

		if (file.getLocation() == null) {
			CheckRegistry.setChecksFileName(file.getFullPath().makeAbsolute().toFile().getAbsolutePath());
		} else {
			CheckRegistry.setChecksFileName(file.getLocation().toOSString());
		}
		reload(true);
	}

	protected ActionContributionItem addButton(Action cmd) {
		ActionContributionItem item = new ActionContributionItem(cmd);
		IToolBarManager m = getViewSite().getActionBars().getToolBarManager();
		m.add(item);
		return item;
	}

	protected void addButtonSeparator() {
		IToolBarManager m = getViewSite().getActionBars().getToolBarManager();
		m.add(new Separator());
	}

	protected void addMenuItem(Action cmd) {
		IMenuManager m = getViewSite().getActionBars().getMenuManager();
		m.add(cmd);
	}

	protected void addMenuSeparator() {
		IMenuManager m = getViewSite().getActionBars().getMenuManager();
		m.add(new Separator());
	}

	// ---------------------------------------------
	// COMMANDS

	class UpdateDumpCmd extends Action {
		public UpdateDumpCmd() {
			super(Messages.getString("RecipeBrowserView.Update"), RecipePlugin.getDefault().getImageDescriptor( //$NON-NLS-1$
					"refresh.gif")); //$NON-NLS-1$
		}

		public void run() {
			update();
		}
	}

	class EvaluateCmd extends Action {
		public EvaluateCmd() {
			super(Messages.getString("RecipeBrowserView.evaluateFailedLabel"), RecipePlugin.getDefault() //$NON-NLS-1$
					.getImageDescriptor("eval.gif")); //$NON-NLS-1$
		}

		public void run() {
			evaluate(new EvaluationContext());
		}
	}

	class EvaluateAllCmd extends Action {
		public EvaluateAllCmd() {
			super(Messages.getString("RecipeBrowserView.reevaluateAllLabel"), RecipePlugin.getDefault() //$NON-NLS-1$
					.getImageDescriptor("evalAll.gif")); //$NON-NLS-1$
		}

		public void run() {
			EvaluationContext ctx = new EvaluationContext();
			ctx.setEvaluateAll(true);
			evaluate(ctx);
		}
	}

	class ReloadCmd extends Action {
		public ReloadCmd() {
			super(Messages.getString("RecipeBrowserView.reloadRecipeFileLabel"), RecipePlugin.getDefault() //$NON-NLS-1$
					.getImageDescriptor("refresh.gif")); //$NON-NLS-1$
		}

		public void run() {
			reload(true);
		}
	}

	class HideOkCmd extends Action {
		public HideOkCmd() {
			super(Messages.getString("RecipeBrowserView.filterLabel"), IAction.AS_CHECK_BOX); //$NON-NLS-1$
			setImageDescriptor(RecipePlugin.getDefault().getImageDescriptor("filter.gif")); //$NON-NLS-1$
		}

		public void run() {
			if (treeViewer.getFilters().length > 0) { // has Filter!
				treeViewer.removeFilter(okFilter);
			} else {
				treeViewer.addFilter(okFilter);
			}
		}
	}

	class CollapseAllCmd extends Action {
		public CollapseAllCmd() {
			super(Messages.getString("RecipeBrowserView.collapseAllLabel"), RecipePlugin.getDefault().getImageDescriptor( //$NON-NLS-1$
					"collapseAll.gif")); //$NON-NLS-1$
		}

		public void run() {
			treeViewer.collapseAll();
		}
	}

	class EvalCmd extends Action {
		private Check check;

		public EvalCmd(Check c) {
			super(Messages.getString("RecipeBrowserView.evalAllLabel"), RecipePlugin.getDefault().getImageDescriptor( //$NON-NLS-1$
					"evalAll.gif")); //$NON-NLS-1$
			this.check = c;
		}

		public void run() {
			new EvalJob(check, treeViewer, siteService).schedule();
		}
	}

	/*
	 * This inner class has the purpose to fix as many trivial composite checks
	 * as possible
	 */
	class QuickFixAllCmd extends Action {

		public QuickFixAllCmd() {
			// super(Messages.getString("RecipeBrowserView.quickFixAllLabel"),
			// RecipePlugin.getDefault().getImageDescriptor("quickFixAll.gif"));
			// //$NON-NLS-1$
			super(Messages.getString("RecipeBrowserView.quickFixAllLabel"), RecipePlugin.getDefault().getImageDescriptor("quickFixAll.gif")); //$NON-NLS-1$
		}

		public void run() {

			// OPTIMISTIC :
			// We assume that the LoadJob has done its job so that
			// CheckRegistry.getChecks() won't return null (if ever checks
			// hasn't be loaded from .recipes file yet)
			// PESSIMISTIC would be to check if CheckRegistry.getChecks() is
			// null, if so then queue a new Load job using the private method
			// RecipeBrowserView#reload and open a dialog saying to user that
			// massive quick fixing is impossible since checks haven't been
			// loaded from file yet, and else launch the atomic quick fixes
			// normally.
			// However, to obtain the NullPointerException that could
			// justify this pessimistic functionning, the execution has to be
			// slow enough to allow the user to click the massive quick fix
			// action button before the LoadJob completes its task.
			CheckSet checkSet = CheckRegistry.getChecks();

			// TODO: it may be better (safer) to retrieve checks from the
			// Treeviewer.. to be surer all checks have been loaded from file
			// before the user could be able to launch a massive quick fix
			// command...to this day functionning is OPTIMISTIC (see
			// RecipeBrowserViex#QuickFixAll) like this :
			//
			// CheckSet checkSet=new CheckSet();
			// List<Check> listChecks = ((IStructuredSelection)
			// this.treeViewer.getSelection()).toList();
			// for (Check c:listChecks) checkSet.add(c);

			for (Check check : checkSet.getChecks()) {
				if (check.getStatus() == EvalStatus.SOMECHILDRENFAILED) {
					// IProgressMonitor
					// pm=Job.getJobManager().createProgressGroup();
					// q.setProgressGroup(pm, IProgressMonitor.UNKNOWN);
					// q.schedule();
				}
			}

			reload(true);

		}

	}

	public void dispose() {
		super.dispose();
		// watcherThread.stop();
		watcherThread = null;
	}

}