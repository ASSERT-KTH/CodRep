if (selectedFolder != null)

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.addressbook.gui;

import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.*;
import javax.swing.border.AbstractBorder;
import javax.swing.border.Border;
import javax.swing.border.CompoundBorder;

import org.columba.addressbook.config.AdapterNode;
import org.columba.addressbook.folder.Folder;
import org.columba.addressbook.folder.GroupListCard;
import org.columba.addressbook.folder.HeaderItem;
import org.columba.addressbook.folder.HeaderItemList;
import org.columba.addressbook.gui.tree.util.SelectAddressbookFolderDialog;
import org.columba.addressbook.gui.util.AddressbookDNDListView;
import org.columba.addressbook.gui.util.AddressbookListModel;
import org.columba.addressbook.gui.util.AddressbookListRenderer;
import org.columba.addressbook.gui.util.LabelTextFieldPanel;
import org.columba.addressbook.main.AddressbookInterface;
import org.columba.addressbook.util.AddressbookResourceLoader;

import org.columba.core.gui.util.wizard.WizardTopBorder;

public class EditGroupDialog extends JDialog implements ActionListener
{
	//private AddressbookXmlConfig config;
	//private AddressbookTable addressbook;
	private AddressbookDNDListView addressbook;
	//private DefaultListModel addressbookModel;

	private AddressbookDNDListView list;
	private JButton addButton,removeButton,okButton,cancelButton;
	private JLabel nameLabel,descriptionLabel;
	private JTextField nameTextField,descriptionTextField;
	//private AdapterNode groupNode;

	private AddressbookInterface addressbookInterface;
	private AddressbookListModel members;
	private AddressbookListRenderer renderer;
	
	boolean result;

	public EditGroupDialog(
		JFrame frame,
		AddressbookInterface i,
		AdapterNode groupNode)
	{
		super(frame, true);

		this.addressbookInterface = i;

		//this.groupNode = groupNode;

		result = false;

		renderer = new AddressbookListRenderer();
		//set title
		init();
	}

	protected void init()
	{
		getContentPane().setLayout(new BorderLayout());
		
		JPanel mainPanel = new JPanel(new BorderLayout());
		mainPanel.setBorder(BorderFactory.createEmptyBorder(12, 12, 10, 11));

		JPanel panel = new JPanel(new BorderLayout());

		JPanel leftPanel = new JPanel(new BorderLayout());

		LabelTextFieldPanel infoPanel = new LabelTextFieldPanel();
		Border border = BorderFactory.createTitledBorder(
					BorderFactory.createEtchedBorder(),
					" Description ");
		Border margin = BorderFactory.createEmptyBorder(5, 10, 10, 10);
		infoPanel.setBorder(new CompoundBorder(border, margin));

		nameLabel = new JLabel("Name:");
		nameTextField = new JTextField();
		infoPanel.addLabel(nameLabel);
		infoPanel.addTextField(nameTextField);

		descriptionLabel = new JLabel("Description:");
		descriptionTextField = new JTextField();
		infoPanel.addLabel(descriptionLabel);
		infoPanel.addTextField(descriptionTextField);

		leftPanel.add(infoPanel, BorderLayout.NORTH);

		JPanel listPanel = new JPanel();
		listPanel.setLayout(new BorderLayout());
		border = BorderFactory.createTitledBorder(
				BorderFactory.createEtchedBorder(),
				" Members ");
		margin = BorderFactory.createEmptyBorder(5, 10, 10, 10);
		listPanel.setBorder(new CompoundBorder(border, margin));

		members = new AddressbookListModel();

		list = new AddressbookDNDListView(members);
		//list = new JList(members);
		//list.setCellRenderer(renderer);
		JScrollPane toPane = new JScrollPane(list);
		toPane.setPreferredSize(new Dimension(250, 200));
		listPanel.add(toPane, BorderLayout.CENTER);

		leftPanel.add(listPanel, BorderLayout.CENTER);

		panel.add(leftPanel, BorderLayout.CENTER);

		JPanel middlePanel = new JPanel();
		middlePanel.setLayout(new BoxLayout(middlePanel, BoxLayout.Y_AXIS));
		middlePanel.setBorder(BorderFactory.createEmptyBorder(0, 10, 0, 10));

		middlePanel.add(Box.createVerticalGlue());

		addButton = new JButton("<-");
		addButton.addActionListener(this);
		addButton.setActionCommand("ADD");
		middlePanel.add(addButton);
		middlePanel.add(Box.createRigidArea(new Dimension(0, 5)));
		removeButton = new JButton("->");
		removeButton.addActionListener(this);
		removeButton.setActionCommand("REMOVE");
		middlePanel.add(removeButton);

		middlePanel.add(Box.createVerticalGlue());

		panel.add(middlePanel, BorderLayout.EAST);

		mainPanel.add(panel, BorderLayout.WEST);

		JPanel rightPanel = new JPanel(new BorderLayout());
		border = BorderFactory.createTitledBorder(
				BorderFactory.createEtchedBorder(),
				" Addressbook ");
		margin = BorderFactory.createEmptyBorder(5, 10, 10, 10);
		rightPanel.setBorder(new CompoundBorder(border, margin));
		
		addressbook = new AddressbookDNDListView();
		addressbook.setAcceptDrop(false);
		JScrollPane scrollPane = new JScrollPane( addressbook );
		rightPanel.add(scrollPane, BorderLayout.CENTER);

		mainPanel.add(rightPanel, BorderLayout.CENTER);

		getContentPane().add(mainPanel, BorderLayout.CENTER);

		JPanel bottomPanel = new JPanel(new BorderLayout());
		bottomPanel.setBorder(new CompoundBorder(
					new WizardTopBorder(),
					BorderFactory.createEmptyBorder(17, 12, 11, 11)));

		JPanel buttonPanel = new JPanel(new GridLayout(1, 2, 10, 10));
		okButton = new JButton("Ok");
		okButton.setActionCommand("OK");
		okButton.addActionListener(this);
		buttonPanel.add(okButton);
		cancelButton = new JButton("Cancel");
		cancelButton.setActionCommand("CANCEL");
		cancelButton.addActionListener(this);
		buttonPanel.add(cancelButton);
		bottomPanel.add(buttonPanel, BorderLayout.EAST);
		getContentPane().add(bottomPanel, BorderLayout.SOUTH);
		getRootPane().setDefaultButton(okButton);
		getRootPane().registerKeyboardAction(this,"CANCEL",KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE,0),JComponent.WHEN_IN_FOCUSED_WINDOW);
		pack();
		setLocationRelativeTo(null);
	}

	public boolean getResult()
	{
		return result;
	}

	public void setHeaderList(HeaderItemList list)
	{
		//addressbook.setHeaderItemList(list);
		//Vector v = list.getVector();
		
		addressbook.setHeaderList(list);
	}

	public void updateComponents(
		GroupListCard card,
		HeaderItemList list,
		boolean b)
	{
		if (b)
		{
			// gettext
			nameTextField.setText(card.get("displayname"));
			descriptionTextField.setText(card.get("description"));

			members = new AddressbookListModel();
			for (int i = 0; i < list.count(); i++)
			{
				HeaderItem item = list.get(i);
				members.addElement(item);
			}

			this.list.setModel(members);
		}
		else
		{
			// settext
			card.set("displayname", nameTextField.getText());
			card.set("description", descriptionTextField.getText());

			// remove all children
			card.removeMembers();

			// add children
			for (int i = 0; i < members.getSize(); i++)
			{
				HeaderItem item = (HeaderItem) members.get(i);
				Object uid = item.getUid();
				card.addMember(((Integer) uid).toString());
			}
		}
	}

	public void actionPerformed(ActionEvent e)
	{
		String command = e.getActionCommand();

		if (command.equals("CANCEL"))
		{
			result = false;
			setVisible(false);
		}
		else if (command.equals("CHOOSE"))
		{
			SelectAddressbookFolderDialog dialog =
				addressbookInterface.tree.getSelectAddressbookFolderDialog();

			Folder selectedFolder = dialog.getSelectedFolder();
			if (folder != null)
			{
				HeaderItemList list = selectedFolder.getHeaderItemList();
				setHeaderList(list);
			}
		}
		else if (command.equals("OK"))
		{
			if (nameTextField.getText().length() == 0)
			{
				JOptionPane.showMessageDialog(this,
					"You must enter a name for the group!");
				return;
			}
			result = true;
			setVisible(false);
		}
		else if (command.equals("ADD"))
		{
			int[] array = addressbook.getSelectedIndices();
			HeaderItem item;

			for (int j = 0; j < array.length; j++)
			{
				item = (HeaderItem) addressbook.get(array[j]);
				System.out.println("add item:"+item);
				
				members.addElement(item);
			}
		}
		else if (command.equals("REMOVE"))
		{
			int[] array = list.getSelectedIndices();
			for (int j = 0; j < array.length; j++)
			{
				System.out.println("remove index:"+array[j]);
				members.remove(array[j]);
			}
		}
	}
}
