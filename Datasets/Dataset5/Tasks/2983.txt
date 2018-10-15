package org.eclipse.wst.xml.vex.ui.internal.contentassist;

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

import org.eclipse.jface.action.IAction;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.ControlListener;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseListener;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.events.ShellEvent;
import org.eclipse.swt.events.ShellListener;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.widgets.Tree;
import org.eclipse.swt.widgets.TreeItem;
import org.eclipse.wst.xml.vex.ui.internal.VexPlugin;
import org.eclipse.wst.xml.vex.ui.internal.swt.VexWidget;

/**
 * Class that owns the content assistant window, the popup where the user can
 * select elements or other content to insert. This class is a singleton owned
 * by VexPlugin. It should not be instantiated directly.
 */
public abstract class ContentAssistant {

	/**
	 * Class constructor.
	 */
	public ContentAssistant() {
	}

	/**
	 * Returns the list of actions to be displayed in this assistant.
	 * 
	 * @param vexWidget
	 *            VexWidget to which the actions apply.
	 */
	public abstract IAction[] getActions(VexWidget widget);

	/**
	 * Returns the title to be displayed in the assistant's title bar.
	 * 
	 * @param vexWidget
	 *            VexWidget for which we are displaying the assistant.
	 */
	public abstract String getTitle(VexWidget widget);

	/**
	 * Show the content assitant window for the given editor.
	 * 
	 * @param vexWidget
	 *            VexWidget for which we are displaying the assistant.
	 */
	public void show(VexWidget vexWidget) {

		this.actions = this.getActions(vexWidget);

		Shell parent = vexWidget.getShell();
		this.assistantShell = new Shell(parent, SWT.DIALOG_TRIM | SWT.RESIZE
				| SWT.MODELESS);
		this.assistantShell.setText(this.getTitle(vexWidget));
		this.assistantShell.addControlListener(this.controlListener);
		this.assistantShell.addDisposeListener(this.disposeListener);
		this.assistantShell.addShellListener(this.shellListener);

		GridLayout layout = new GridLayout();
		layout.numColumns = 1;
		this.assistantShell.setLayout(layout);
		GridData gd;

		this.textWidget = new Text(this.assistantShell, SWT.SINGLE);
		this.textWidget.addModifyListener(this.modifyListener);

		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		this.textWidget.setLayoutData(gd);
		this.textWidget.addKeyListener(this.keyListener);
		this.textWidget.addModifyListener(this.modifyListener);

		this.treeWidget = new Tree(assistantShell, SWT.SINGLE);
		this.treeWidget.addKeyListener(this.keyListener);
		this.treeWidget.addMouseListener(this.mouseListener);
		this.treeWidget.addSelectionListener(this.selectionListener);

		gd = new GridData();
		gd.grabExcessHorizontalSpace = true;
		gd.horizontalAlignment = GridData.FILL;
		gd.grabExcessVerticalSpace = true;
		gd.verticalAlignment = GridData.FILL;
		this.treeWidget.setLayoutData(gd);

		this.assistantShell.setBounds(this.getSize());
		this.repopulateList();
		this.mouseDown = false;
		this.assistantShell.open();

	}

	// ======================================================== PRIVATE

	private static final String SETTINGS_SECTION = "contentAssistant"; //$NON-NLS-1$
	private static final String SETTINGS_X = "x"; //$NON-NLS-1$
	private static final String SETTINGS_Y = "y"; //$NON-NLS-1$
	private static final String SETTINGS_WIDTH = "width"; //$NON-NLS-1$
	private static final String SETTINGS_HEIGHT = "height"; //$NON-NLS-1$

	private Shell assistantShell;
	private Text textWidget;
	private Tree treeWidget;
	private IAction[] actions;
	private boolean mouseDown;

	/**
	 * Perform the action that is currently selected in the tree view, if any,
	 * and dispose the assistant shell.
	 */
	private void doAction() {
		TreeItem[] items = treeWidget.getSelection();
		if (items.length > 0) {
			IAction action = (IAction) items[0].getData();
			action.run();
		}
		assistantShell.dispose();
	}

	private IDialogSettings getSettings() {
		IDialogSettings rootSettings = VexPlugin.getInstance()
				.getDialogSettings();
		IDialogSettings settings = rootSettings.getSection(SETTINGS_SECTION);
		if (settings == null) {
			settings = rootSettings.addNewSection(SETTINGS_SECTION);
		}
		return settings;
	}

	private Rectangle getSize() {
		IDialogSettings settings = this.getSettings();
		int x = 100;
		int y = 100;
		int width = 200;
		int height = 300;
		if (settings.get(SETTINGS_X) != null) {
			x = settings.getInt(SETTINGS_X);
			y = settings.getInt(SETTINGS_Y);
			width = settings.getInt(SETTINGS_WIDTH);
			height = settings.getInt(SETTINGS_HEIGHT);
		}
		return new Rectangle(x, y, width, height);
	}

	private void repopulateList() {
		String prefix = this.textWidget.getText();
		this.treeWidget.removeAll();
		TreeItem first = null;
		for (int i = 0; i < this.actions.length; i++) {
			IAction action = this.actions[i];
			if (action.getText().startsWith(prefix)) {
				TreeItem item = new TreeItem(this.treeWidget, SWT.NONE);
				if (first == null) {
					first = item;
				}
				item.setData(action);
				item.setText(action.getText());
			}
		}

		if (first != null) {
			this.treeWidget.setSelection(new TreeItem[] { first });
		}
	}

	private void saveSize() {
		IDialogSettings settings = this.getSettings();
		Rectangle bounds = this.assistantShell.getBounds();
		settings.put(SETTINGS_X, bounds.x);
		settings.put(SETTINGS_Y, bounds.y);
		settings.put(SETTINGS_WIDTH, bounds.width);
		settings.put(SETTINGS_HEIGHT, bounds.height);
	}

	private ControlListener controlListener = new ControlListener() {
		public void controlMoved(ControlEvent e) {
			saveSize();
		}

		public void controlResized(ControlEvent e) {
			saveSize();
		}
	};

	private DisposeListener disposeListener = new DisposeListener() {
		public void widgetDisposed(DisposeEvent e) {
			assistantShell = null;
		}
	};

	private KeyListener keyListener = new KeyListener() {
		public void keyPressed(KeyEvent e) {
			if (e.keyCode == 13) {
				doAction();
			} else if (e.widget == textWidget && e.keyCode == SWT.ARROW_DOWN) {
				treeWidget.setFocus();
			}

		}

		public void keyReleased(KeyEvent e) {
		}
	};

	private ModifyListener modifyListener = new ModifyListener() {
		public void modifyText(ModifyEvent e) {
			repopulateList();
		}
	};

	private MouseListener mouseListener = new MouseListener() {
		public void mouseDoubleClick(MouseEvent e) {
		}

		public void mouseDown(MouseEvent e) {
			mouseDown = true;
		}

		public void mouseUp(MouseEvent e) {
			mouseDown = false;
		}

	};

	private SelectionListener selectionListener = new SelectionListener() {
		public void widgetSelected(SelectionEvent e) {
			// If selected with the mouse, we do the selected action.
			if (mouseDown) {
				doAction();
			}
		}

		public void widgetDefaultSelected(SelectionEvent e) {
		}
	};

	private ShellListener shellListener = new ShellListener() {
		public void shellActivated(ShellEvent e) {
		}

		public void shellClosed(ShellEvent e) {
		}

		public void shellDeactivated(ShellEvent e) {
			assistantShell.dispose();
		}

		public void shellDeiconified(ShellEvent e) {
		}

		public void shellIconified(ShellEvent e) {
		}
	};
}