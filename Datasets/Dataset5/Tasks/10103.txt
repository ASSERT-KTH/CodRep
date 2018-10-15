protected static final String DEFAULT_CLIENT = "ecf.generic.client";

package org.eclipse.ecf.example.collab.ui;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.eclipse.ecf.core.ContainerDescription;
import org.eclipse.ecf.core.ContainerFactory;
import org.eclipse.ecf.example.collab.ClientPlugin;
import org.eclipse.ecf.example.collab.ClientPluginConstants;
import org.eclipse.jface.dialogs.TitleAreaDialog;
import org.eclipse.jface.viewers.ILabelProviderListener;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.ITableLabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;

public class ConnectionDialog extends TitleAreaDialog {
	protected static final String CLASSNAME = JoinGroupWizardPage.class.getName();
	protected static final String ISSERVER_PROP_NAME = CLASSNAME+".isServer";
	protected static final String DEFAULT_CLIENT = "org.eclipse.ecf.provider.generic.Client";
	
	public ConnectionDialog(Shell parentShell) {
		super(parentShell);
	}

	protected Control createDialogArea(Composite parent) {
		Composite main = new Composite((Composite) super.createDialogArea(parent), SWT.NONE);
		main.setLayout(new GridLayout());
		main.setLayoutData(new GridData(GridData.FILL_BOTH));
		
		Label providerLabel = new Label(main, SWT.NONE);
		providerLabel.setText("Connection Protocol");

		Composite providerComp = new Composite(main, SWT.NONE);
		GridLayout layout = new GridLayout(2, false);
		layout.marginHeight = 0;
		layout.marginWidth = 0;
		providerComp.setLayout(layout);
		providerComp.setLayoutData(new GridData(GridData.FILL_BOTH));
		
		TableViewer viewer = new TableViewer(providerComp, SWT.BORDER
				| SWT.FULL_SELECTION);
		viewer.setContentProvider(new ECFProviderContentProvider());
		viewer.setLabelProvider(new ECFProviderLabelProvider());		
		viewer.addSelectionChangedListener(new ProviderSelector());
		
		Table table = viewer.getTable();
		GridData gData = new GridData(GridData.FILL_VERTICAL);
		gData.widthHint = 150;
		table.setLayoutData(gData);
/*		table.setHeaderVisible(true);
		TableColumn tc = new TableColumn(table, SWT.NONE);
		tc.setText("Name");
		tc = new TableColumn(table, SWT.NONE);
		tc.setText("Classname");*/

		viewer.setInput(ContainerFactory.getDefault().getDescriptions());
		
		Composite paramComp = new Composite(providerComp, SWT.NONE);
		paramComp.setLayout(new GridLayout());
		paramComp.setLayoutData(new GridData(GridData.FILL_BOTH));

		this.setTitle("ECF Connection");
		this.setMessage("Please choose a provider and supply connection parameters.");

		return parent;
	}

	protected Point getInitialSize() {
		return new Point(450, 300);
	}

	private class ECFProviderContentProvider implements IStructuredContentProvider {

		public Object[] getElements(Object inputElement) {		
			List rawDescriptions = (List) inputElement;
			List elements = new ArrayList();
			
			for(Iterator i=rawDescriptions.iterator(); i.hasNext(); ) {
	            final ContainerDescription desc = (ContainerDescription) i.next();
	            Map props = desc.getProperties();
	            String isServer = (String) props.get(ISSERVER_PROP_NAME);
	            if (isServer == null || !isServer.equalsIgnoreCase("true")) {
	                elements.add(desc);
	            }
	        }
			
			return elements.toArray();
		}

		public void dispose() {			
		}

		public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
		}		
	}
	
	private class ECFProviderLabelProvider implements ITableLabelProvider {

		public Image getColumnImage(Object element, int columnIndex) {			
			if (columnIndex == 0) {
				//TODO: If the container description contains an image for the provider, display it here.
				return ClientPlugin.getDefault().getImageRegistry().get(ClientPluginConstants.DECORATION_DEFAULT_PROVIDER);
			}
			
			return null;
		}

		public String getColumnText(Object element, int columnIndex) {
			ContainerDescription desc = (ContainerDescription) element;
			switch(columnIndex) {
			case 0:
				return desc.getDescription();
			case 1:
				return desc.getName();
			}
			
			return "";
		}

		public void addListener(ILabelProviderListener listener) {
		}

		public void dispose() {
		}

		public boolean isLabelProperty(Object element, String property) {
			return false;
		}

		public void removeListener(ILabelProviderListener listener) {
		}
		
	}	
	
	private class ProviderSelector implements ISelectionChangedListener {

		public void selectionChanged(SelectionChangedEvent event) {
			StructuredSelection selection = (StructuredSelection) event.getSelection();
			ContainerDescription desc = (ContainerDescription) selection.getFirstElement();
			
			//desc.
		}
		
	}
}