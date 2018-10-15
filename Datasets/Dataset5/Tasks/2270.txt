parametersViewer = new TableViewer(composite, SWT.V_SCROLL | SWT.FULL_SELECTION | SWT.H_SCROLL | SWT.BORDER);

/*******************************************************************************
 * Copyright (c) 2008 Remy Chi Jian Suen and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Chi Jian Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.remoteservices.ui;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.internal.remoteservices.ui.Messages;
import org.eclipse.ecf.remoteservices.ui.RemoteMethod.Parameter;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ICellModifier;
import org.eclipse.jface.viewers.ILabelProviderListener;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.ITableLabelProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.window.IShellProvider;
import org.eclipse.jface.window.SameShellProvider;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;

/**
 * The MethodInvocationDialog allows a user to select a method given a
 * <code>java.lang.Class</code> to invoke and communicate with a remote
 * service.
 * 
 * @since 2.0
 */
public final class MethodInvocationDialog extends Dialog {

	/**
	 * An integer constant that corresponds to the "Async Listener" selection.
	 * 
	 * @see #getInvocationType()
	 */
	public static final int ASYNC_LISTENER = 0;

	/**
	 * An integer constant that corresponds to the "Async Future Result"
	 * selection.
	 * 
	 * @see #getInvocationType()
	 */
	public static final int ASYNC_FUTURE_RESULT = ASYNC_LISTENER + 1;

	/**
	 * An integer constant that corresponds to the "Async Fire-and-Go"
	 * selection.
	 * 
	 * @see #getInvocationType()
	 */
	public static final int ASYNC_FIRE_AND_GO = ASYNC_FUTURE_RESULT + 1;

	/**
	 * An integer constant that corresponds to the "OSGi Service Proxy"
	 * selection.
	 * 
	 * @see #getInvocationType()
	 */
	public static final int OSGI_SERVICE_PROXY = ASYNC_FIRE_AND_GO + 1;
	/**
	 * An integer constant that corresponds to the "Remote Service Proxy"
	 * selection.
	 * 
	 * @see #getInvocationType()
	 */
	public static final int REMOTE_SERVICE_PROXY = OSGI_SERVICE_PROXY + 1;
	/**
	 * An integer constant that corresponds to the "Synchronous" selection.
	 * 
	 * @see #getInvocationType()
	 */
	public static final int SYNCHRONOUS = REMOTE_SERVICE_PROXY + 1;

	private static final String[] COLUMN_PROPERTIES = {"Parameter", "Argument"}; //$NON-NLS-1$ //$NON-NLS-2$

	/**
	 * Provide a default timeout value of 30,000 milliseconds.
	 */
	private static final String DEFAULT_TIMEOUT_VALUE = "30000"; //$NON-NLS-1$

	private TableViewer methodsViewer;
	private TableViewer parametersViewer;
	private Text timeoutText;
	private Combo invocationCombo;

	private final RemoteMethod[] methods;

	private Method method;
	private Object[] methodArguments;
	private int timeout;
	private int invocationType;

	/**
	 * Creates a new MethodInvocationDialog on top of the specified shell
	 * provider.
	 * 
	 * @param parentShell
	 *            the provider to return the parent shell of this dialog
	 * @param cls
	 *            the class to select the methods from
	 */
	public MethodInvocationDialog(IShellProvider parentShell, Class cls) {
		super(parentShell);
		Assert.isNotNull(cls);

		Method[] methods = cls.getMethods();
		final List validMethods = new ArrayList();
		for (int i = 0; i < methods.length; i++) {
			final Class[] parameters = methods[i].getParameterTypes();
			final String[] types = new String[parameters.length];

			if (types.length == 0) {
				validMethods.add(methods[i]);
				continue;
			}

			boolean match = true;
			for (int j = 0; j < types.length; j++) {
				final String name = parameters[j].getName();
				if (!name.equals("char") && !name.equals("boolean") //$NON-NLS-1$ //$NON-NLS-2$
						&& !name.equals("int") && !name.equals("double") //$NON-NLS-1$ //$NON-NLS-2$
						&& !name.equals("float") && !name.equals("long") //$NON-NLS-1$ //$NON-NLS-2$
						&& !name.equals("short") && !name.equals("byte") //$NON-NLS-1$ //$NON-NLS-2$
						&& !name.equals("java.lang.String")) { //$NON-NLS-1$
					match = false;
					break;
				}
			}
			if (match) {
				validMethods.add(methods[i]);
			}
		}

		methods = (Method[]) validMethods.toArray(new Method[validMethods.size()]);
		this.methods = new RemoteMethod[methods.length];
		for (int i = 0; i < methods.length; i++) {
			this.methods[i] = new RemoteMethod(methods[i]);
		}
	}

	/**
	 * Creates a new MethodInvocationDialog over the provided shell.
	 * 
	 * @param parentShell
	 *            the parent shell
	 * @param cls
	 *            the class to select the methods from
	 */
	public MethodInvocationDialog(Shell parentShell, Class cls) {
		this(new SameShellProvider(parentShell), cls);
	}

	protected void configureShell(Shell newShell) {
		super.configureShell(newShell);
		newShell.setText(Messages.MethodInvocationDialog_ShellTitle);
	}

	protected Control createDialogArea(Composite parent) {
		parent = (Composite) super.createDialogArea(parent);

		final Composite composite = new Composite(parent, SWT.NONE);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(new GridLayout(2, true));

		Label label = new Label(composite, SWT.LEAD);
		label.setText(Messages.MethodInvocationDialog_AvailableMethodsLabel);

		label = new Label(composite, SWT.LEAD);
		label.setText(Messages.MethodInvocationDialog_ArgumentsLabel);

		methodsViewer = new TableViewer(composite, SWT.V_SCROLL | SWT.H_SCROLL | SWT.BORDER);
		methodsViewer.getControl().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		methodsViewer.setContentProvider(new ArrayContentProvider());
		methodsViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			public void selectionChanged(SelectionChangedEvent e) {
				final IStructuredSelection iss = (IStructuredSelection) e.getSelection();
				final Object element = iss.getFirstElement();
				if (element != null) {
					getButton(IDialogConstants.OK_ID).setEnabled(!timeoutText.getText().equals("")); //$NON-NLS-1$
					final RemoteMethod method = (RemoteMethod) element;
					parametersViewer.setInput(method.getParameters());
				}
			}
		});
		methodsViewer.setLabelProvider(new LabelProvider() {
			public String getText(Object element) {
				final RemoteMethod method = (RemoteMethod) element;
				return method.getReturnType() + ' ' + method.getSignature();
			}
		});

		parametersViewer = new TableViewer(composite, SWT.V_SCROLL | SWT.H_SCROLL | SWT.BORDER);
		parametersViewer.getControl().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		parametersViewer.setContentProvider(new ArrayContentProvider());
		parametersViewer.setLabelProvider(new ITableLabelProvider() {
			public Image getColumnImage(Object element, int columnIndex) {
				return null;
			}

			public String getColumnText(Object element, int columnIndex) {
				final Parameter p = (Parameter) element;
				if (columnIndex == 0) {
					final String name = p.getParameter().getName();
					if (name.charAt(0) == 'j') {
						// this is java.lang.String
						return "String"; //$NON-NLS-1$
					} else {
						return name;
					}
				} else {
					return p.getArgument();
				}
			}

			public void addListener(ILabelProviderListener listener) {
			}

			public void dispose() {
			}

			public boolean isLabelProperty(Object element, String property) {
				return true;
			}

			public void removeListener(ILabelProviderListener listener) {
			}
		});
		parametersViewer.setCellEditors(new CellEditor[] {null, new TextCellEditor(parametersViewer.getTable())});
		parametersViewer.setCellModifier(new ICellModifier() {
			public boolean canModify(Object element, String property) {
				return property.equals(COLUMN_PROPERTIES[1]);
			}

			public Object getValue(Object element, String property) {
				return ((Parameter) element).getArgument();
			}

			public void modify(Object element, String property, Object value) {
				if (property.equals(COLUMN_PROPERTIES[1])) {
					if (element instanceof TableItem) {
						final TableItem item = ((TableItem) element);
						final Parameter p = (Parameter) item.getData();
						final String argument = (String) value;
						p.setArgument(argument);
						item.setText(1, argument);
					}
				}
			}
		});
		parametersViewer.setColumnProperties(COLUMN_PROPERTIES);

		final Table table = parametersViewer.getTable();
		table.setHeaderVisible(true);
		table.setLinesVisible(true);
		TableColumn column = new TableColumn(table, SWT.LEAD);
		column.setWidth(150);
		column.setText(Messages.MethodInvocationDialog_ParameterColumn);
		column = new TableColumn(table, SWT.LEAD);
		column.setWidth(150);
		column.setText(Messages.MethodInvocationDialog_ValueColumn);

		methodsViewer.setInput(methods);

		final Composite bottomComposite = new Composite(composite, SWT.NONE);
		bottomComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 2, 1));
		final GridLayout layout = new GridLayout(2, false);
		layout.marginWidth = 0;
		layout.marginHeight = 0;
		bottomComposite.setLayout(layout);

		label = new Label(bottomComposite, SWT.LEAD);
		label.setText(Messages.MethodInvocationDialog_TimeoutLabel);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, true));

		timeoutText = new Text(bottomComposite, SWT.BORDER);
		timeoutText.setText(DEFAULT_TIMEOUT_VALUE);
		timeoutText.addVerifyListener(new VerifyListener() {
			public void verifyText(VerifyEvent e) {
				switch (e.text.length()) {
					case 0 :
						e.doit = true;
						break;
					case 1 :
						e.doit = Character.isDigit(e.text.charAt(0));
						break;
					default :
						e.doit = false;
						break;
				}
			}
		});
		timeoutText.addModifyListener(new ModifyListener() {
			public void modifyText(ModifyEvent e) {
				getButton(IDialogConstants.OK_ID).setEnabled(!timeoutText.getText().equals("") //$NON-NLS-1$
						&& !methodsViewer.getSelection().isEmpty());
			}
		});
		timeoutText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));

		label = new Label(bottomComposite, SWT.LEAD);
		label.setText(Messages.MethodInvocationDialog_InvocationTypeLabel);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, true));

		invocationCombo = new Combo(bottomComposite, SWT.READ_ONLY);
		invocationCombo.setItems(new String[] {Messages.MethodInvocationDialog_InvocationTypeAsyncListener, Messages.MethodInvocationDialog_InvocationTypeAsyncFutureResult, Messages.MethodInvocationDialog_InvocationTypeAsyncFireAndGo, Messages.MethodInvocationDialog_InvocationTypeOSGiServiceProxy, Messages.MethodInvocationDialog_InvocationTypeRemoteServiceProxy, Messages.MethodInvocationDialog_InvocationTypeSynchronous});
		invocationCombo.select(0);
		bottomComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		return parent;
	}

	public void create() {
		super.create();
		final Button okButton = getButton(IDialogConstants.OK_ID);
		okButton.setEnabled(false);
		okButton.setText(Messages.MethodInvocationDialog_BUTTON_INVOKE_TEXT);
	}

	protected void okPressed() {
		final IStructuredSelection selection = (IStructuredSelection) methodsViewer.getSelection();
		final RemoteMethod remoteMethod = (RemoteMethod) selection.getFirstElement();
		method = remoteMethod.getMethod();
		final Parameter[] p = remoteMethod.getParameters();
		methodArguments = new Object[p.length];
		for (int i = 0; i < p.length; i++) {
			final String name = p[i].getParameter().getName();
			final String arg = p[i].getArgument();
			if (name.equals("char")) { //$NON-NLS-1$
				methodArguments[i] = new Character(arg.charAt(0));
			} else if (name.equals("boolean")) { //$NON-NLS-1$
				methodArguments[i] = Boolean.valueOf(arg);
			} else if (name.equals("int")) { //$NON-NLS-1$
				methodArguments[i] = Integer.valueOf(arg);
			} else if (name.equals("double")) { //$NON-NLS-1$
				methodArguments[i] = Double.valueOf(arg);
			} else if (name.equals("float")) { //$NON-NLS-1$
				methodArguments[i] = Float.valueOf(arg);
			} else if (name.equals("long")) { //$NON-NLS-1$
				methodArguments[i] = Long.valueOf(arg);
			} else if (name.equals("short")) { //$NON-NLS-1$
				methodArguments[i] = Short.valueOf(arg);
			} else if (name.equals("byte")) { //$NON-NLS-1$
				methodArguments[i] = Byte.valueOf(arg);
			} else {
				methodArguments[i] = arg;
			}
		}
		timeout = Integer.parseInt(timeoutText.getText());
		invocationType = invocationCombo.getSelectionIndex();
		super.okPressed();
	}

	/**
	 * Returns the method that has been selected by the user.
	 * 
	 * @return the selected method
	 */
	public Method getMethod() {
		return method;
	}

	/**
	 * Returns the arguments that has been specified by the user to pass to the
	 * method.
	 * 
	 * @return the list of arguments to pass into the method
	 */
	public Object[] getMethodArguments() {
		return methodArguments;
	}

	/**
	 * Retrieves the timeout value that has been specified by the user. This
	 * value is in milliseconds.
	 * 
	 * @return the timeout valued specified by the user in milliseconds
	 */
	public int getTimeout() {
		return timeout;
	}

	/**
	 * Returns the type of invocation that should be used to call the selected
	 * method to communicate with a remote service.
	 * 
	 * @return the invocation type selected by the user
	 * @see #ASYNC_LISTENER
	 * @see #ASYNC_FUTURE_RESULT
	 * @see #ASYNC_FIRE_AND_GO
	 * @see #OSGI_SERVICE_PROXY
	 * @see #REMOTE_SERVICE_PROXY
	 * @see #SYNCHRONOUS
	 */
	public int getInvocationType() {
		return invocationType;
	}
}