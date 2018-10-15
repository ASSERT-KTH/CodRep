package org.eclipse.ecf.internal.ui.deprecated.views;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.ui.dialogs;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.ecf.presence.chatroom.IChatRoomInfo;
import org.eclipse.ecf.presence.chatroom.IChatRoomManager;
import org.eclipse.jface.dialogs.TitleAreaDialog;
import org.eclipse.jface.viewers.DoubleClickEvent;
import org.eclipse.jface.viewers.IDoubleClickListener;
import org.eclipse.jface.viewers.ILabelProviderListener;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredContentProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.ITableLabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;

public class ChatRoomSelectionDialog extends TitleAreaDialog {
	IChatRoomManager[] managers = null;

	private Room selectedRoom = null;

	public class Room {
		IChatRoomInfo info;

		IChatRoomManager manager;

		public Room(IChatRoomInfo info, IChatRoomManager man) {
			this.info = info;
			this.manager = man;
		}

		public IChatRoomInfo getRoomInfo() {
			return info;
		}

		public IChatRoomManager getManager() {
			return manager;
		}
	}

	public ChatRoomSelectionDialog(Shell parentShell,
			IChatRoomManager[] managers) {
		super(parentShell);
		this.managers = managers;
	}

	protected Control createDialogArea(Composite parent) {
		Composite main = new Composite(parent, SWT.NONE);
		main.setLayout(new GridLayout());
		main.setLayoutData(new GridData(GridData.FILL_BOTH));

		TableViewer viewer = new TableViewer(main, SWT.BORDER | SWT.H_SCROLL
				| SWT.V_SCROLL | SWT.FULL_SELECTION);
		Table table = viewer.getTable();

		table.setHeaderVisible(true);
		table.setLinesVisible(true);
		table.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		TableColumn tc = new TableColumn(table, SWT.NONE);
		tc.setText("Room Name");
		tc.pack();
		int width = tc.getWidth();
		tc.setWidth(width + (width / 4));
		tc = new TableColumn(table, SWT.NONE);
		tc.setText("Subject");
		tc.pack();
		width = tc.getWidth();
		tc.setWidth(width + (width / 4));
		tc = new TableColumn(table, SWT.NONE);
		tc.setText("Description");
		tc.pack();
		width = tc.getWidth();
		tc.setWidth(width + (width / 3));
		tc = new TableColumn(table, SWT.NONE);
		tc.setText("Members");
		tc.pack();
		tc = new TableColumn(table, SWT.NONE);
		tc.setText("Moderated");
		tc.pack();
		tc = new TableColumn(table, SWT.NONE);
		tc.setText("Persistent");
		tc.pack();
		tc = new TableColumn(table, SWT.NONE);
		tc.setText("Account");
		tc.pack();
		width = tc.getWidth();
		tc.setWidth(width * 3);

		viewer.addSelectionChangedListener(new ISelectionChangedListener() {

			public void selectionChanged(SelectionChangedEvent event) {
				if (!event.getSelection().isEmpty()) {
					ChatRoomSelectionDialog.this.getButton(Window.OK)
							.setEnabled(true);
				}
			}

		});

		viewer.setContentProvider(new ChatRoomContentProvider());
		viewer.setLabelProvider(new ChatRoomLabelProvider());

		List all = new ArrayList();
		for (int i = 0; i < managers.length; i++) {
			IChatRoomInfo[] infos = managers[i].getChatRoomInfos();
			if (infos != null) {
				for (int j = 0; j < infos.length; j++) {
					if (infos[j] != null && managers[i] != null) {
						all.add(new Room(infos[j], managers[i]));
					}
				}
			}
		}
		viewer.setInput(all.toArray());

		this.setTitle("Chat Room Selection");
		this.setMessage("Select a Chat Room to Enter");

		viewer.addSelectionChangedListener(new ISelectionChangedListener() {
			public void selectionChanged(SelectionChangedEvent e) {
				IStructuredSelection s = (IStructuredSelection) e
						.getSelection();
				Object o = s.getFirstElement();
				if (o instanceof Room) {
					selectedRoom = (Room) o;
				}
			}

		});

		viewer.addDoubleClickListener(new IDoubleClickListener() {

			public void doubleClick(DoubleClickEvent event) {
				if (selectedRoom != null) {
					ChatRoomSelectionDialog.this.okPressed();
				}
			}

		});

		return parent;
	}

	private class ChatRoomContentProvider implements IStructuredContentProvider {

		public Object[] getElements(Object inputElement) {
			return (Object[]) inputElement;
		}

		public void dispose() {
		}

		public void inputChanged(Viewer viewer, Object oldInput, Object newInput) {
		}

	}

	private class ChatRoomLabelProvider implements ITableLabelProvider {

		public Image getColumnImage(Object element, int columnIndex) {
			return null;
		}

		public String getColumnText(Object element, int columnIndex) {
			Room room = (Room) element;

			IChatRoomInfo info = room.getRoomInfo();
			switch (columnIndex) {
			case 0:
				return info.getName();
			case 1:
				return info.getSubject();
			case 2:
				return info.getDescription();
			case 3:
				return String.valueOf(info.getParticipantsCount());
			case 4:
				return String.valueOf(info.isModerated());
			case 5:
				return String.valueOf(info.isPersistent());
			case 6:
				return info.getConnectedID().getName();
			default:
				return "";

			}

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

	protected Control createButtonBar(Composite parent) {
		Control bar = super.createButtonBar(parent);
		this.getButton(Window.OK).setText("Enter Chat");
		this.getButton(Window.OK).setEnabled(false);
		return bar;
	}

	public Room getSelectedRoom() {
		return selectedRoom;
	}
}