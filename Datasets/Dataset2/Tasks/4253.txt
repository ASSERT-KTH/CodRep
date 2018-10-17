//folder.setName(accountItem.getName());

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

package org.columba.mail.gui.config.account;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.BorderFactory;
import javax.swing.JDialog;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import org.columba.core.gui.button.CancelButton;
import org.columba.core.gui.button.HelpButton;
import org.columba.core.gui.button.OkButton;
import org.columba.core.gui.util.CTabbedPane;
import org.columba.core.gui.util.DialogStore;
import org.columba.core.gui.util.wizard.WizardTopBorder;
import org.columba.main.MainInterface;
import org.columba.mail.config.AccountItem;
import org.columba.mail.config.IdentityItem;
import org.columba.mail.config.ImapItem;
import org.columba.mail.config.PopItem;
import org.columba.mail.config.SmtpItem;
import org.columba.mail.folder.imap.IMAPRootFolder;
import org.columba.mail.pop3.POP3ServerController;
import org.columba.mail.util.MailResourceLoader;

/**
 * Title:
 * Description:
 * Copyright:    Copyright (c) 2001
 * Company:
 * @author
 * @version 1.0
 */

public class AccountDialog implements ActionListener, ListSelectionListener
{
	private JDialog dialog;

	private AccountItem accountItem;

	private IdentityPanel identityPanel;
	private IncomingServerPanel incomingServerPanel;
	private OutgoingServerPanel outgoingServerPanel;
	private SecurityPanel securityPanel;
	private SpecialFoldersPanel specialFoldersPanel;
	private ReceiveOptionsPanel receiveOptionsPanel;
	
	private OkButton okButton;
	private CancelButton cancelButton;
	private HelpButton helpButton;
	
	//private PanelChooser panelChooser;
	
	private JPanel selected = null;

	public AccountDialog(AccountItem item)
	{
		dialog = DialogStore.getDialog();
		dialog.setTitle( MailResourceLoader.getString("dialog","account","dialog_title") );
		this.accountItem = item;
		dialog.addWindowListener(new WindowAdapter()
		{
			public void windowClosing(WindowEvent e)
			{
				dialog.setVisible(false);
			}
		});

		createPanels();
		initComponents();
		
		//panelChooser.addListSelectionListener(this);
		
		dialog.pack();
		
		//dialog.setSize( new Dimension( 700,550 ) );
		
		/*
		java.awt.Dimension dim = dialog.getSize();


        Dimension screenSize = Toolkit.getDefaultToolkit().getScreenSize();

        dialog.setLocation(screenSize.width/2 - dim.width/2, screenSize.height/2 - dim.height/2);
        */
        
        dialog.setLocationRelativeTo(null);
		dialog.setVisible(true);
		
		//setSize( new Dimension( 600,500 ) );
	}

	protected void createPanels()
	{
		
		IdentityItem identityItem = accountItem.getIdentityItem();
		identityPanel = new IdentityPanel( accountItem, identityItem);
		
		receiveOptionsPanel = new ReceiveOptionsPanel( accountItem );
		
		if (accountItem.isPopAccount())
		{
			PopItem popItem = accountItem.getPopItem();

			incomingServerPanel =
				new IncomingServerPanel( accountItem, popItem, receiveOptionsPanel);
			
		}
		else
		{
			ImapItem imapItem = accountItem.getImapItem();
			incomingServerPanel =
				new IncomingServerPanel( accountItem, imapItem, receiveOptionsPanel);
			
		}

		SmtpItem smtpItem = accountItem.getSmtpItem();
		outgoingServerPanel = new OutgoingServerPanel( accountItem, smtpItem);
		
		
		

		specialFoldersPanel =
			new SpecialFoldersPanel(
				accountItem,
				accountItem.getSpecialFoldersItem());
		

		securityPanel = new SecurityPanel( accountItem.getPGPItem());
	}
	
	
	protected void initComponents()
	{
		dialog.getContentPane().setLayout(new BorderLayout());
		
		JPanel mainPanel = new JPanel();
		mainPanel.setLayout( new BorderLayout() );
		mainPanel.setBorder( BorderFactory.createEmptyBorder(0,0,10,0) );		
		dialog.getContentPane().add( mainPanel, BorderLayout.CENTER );
		
		CTabbedPane tp = new CTabbedPane();
		tp.setBorder(BorderFactory.createEmptyBorder(0, 5, 0, 5));

		/*
		IdentityItem identityItem = accountItem.getIdentityItem();
		identityPanel = new IdentityPanel( accountItem, identityItem);
		*/
		
		tp.add(
			MailResourceLoader.getString("dialog","account",  "identity"),
			identityPanel);
		//$NON-NLS-1$

		if (accountItem.isPopAccount())
		{
			PopItem popItem = accountItem.getPopItem();

			/*
			incomingServerPanel =
				new IncomingServerPanel( accountItem, popItem);
			*/	
			tp.add(
				MailResourceLoader.getString(
					"dialog","account",
					
					"incomingserverpop3"),
				incomingServerPanel);
			//$NON-NLS-1$
		}
		else
		{
			ImapItem imapItem = accountItem.getImapItem();
			/*
			incomingServerPanel =
				new IncomingServerPanel( accountItem, imapItem);
				*/
			tp.add(
				MailResourceLoader.getString(
					"dialog","account",
				
					"incomingserverimap"),
				incomingServerPanel);
			//$NON-NLS-1$
		}
		
		tp.add( "Receive Options", receiveOptionsPanel );

		SmtpItem smtpItem = accountItem.getSmtpItem();
		/*
		outgoingServerPanel = new OutgoingServerPanel( smtpItem);
		*/
		tp.add(
			MailResourceLoader.getString("dialog","account",  "outgoingserver"),
			outgoingServerPanel);
		//$NON-NLS-1$

		/*
		specialFoldersPanel =
			new SpecialFoldersPanel(
				accountItem,
				accountItem.getSpecialFoldersItem());
		*/
		tp.add(
			MailResourceLoader.getString("dialog","account",  "specialfolders"),
			specialFoldersPanel);
		//$NON-NLS-1$

		/*
		securityPanel = new SecurityPanel( accountItem.getPGPItem());
		*/
		tp.add(
			MailResourceLoader.getString("dialog","account", "security"),
			securityPanel);
		//$NON-NLS-1$

		mainPanel.add( tp, BorderLayout.CENTER );
		
		dialog.getContentPane().add(mainPanel, BorderLayout.CENTER);
		
		
		JPanel bottomPanel = new JPanel();
		bottomPanel.setBorder( new WizardTopBorder() );
		bottomPanel.setLayout( new BorderLayout() );
		
		JPanel buttonPanel = createButtonPanel();
		bottomPanel.add( buttonPanel, BorderLayout.CENTER );
		
		dialog.getContentPane().add( bottomPanel, BorderLayout.SOUTH );

		/*
		JPanel bottom = new JPanel();
		bottom.setLayout(new BorderLayout());
		//bottom.setLayout( new BoxLayout( bottom, BoxLayout.X_AXIS ) );
		bottom.setBorder(BorderFactory.createEmptyBorder(10, 5, 10, 5));

		//bottom.add( Box.createHorizontalStrut());

		
		//cancelButton = new JButton(GlobalResourceLoader.getString("dialog", "cancel"));
		cancelButton = new CancelButton();
		//$NON-NLS-1$ //$NON-NLS-2$
		cancelButton.addActionListener(this);
		cancelButton.setActionCommand("CANCEL"); //$NON-NLS-1$

		//okButton = new JButton(GlobalResourceLoader.getString("dialog", "ok"));
		//$NON-NLS-1$ //$NON-NLS-2$
		okButton = new OkButton();
		okButton.addActionListener(this);
		okButton.setActionCommand("OK"); //$NON-NLS-1$
		okButton.setDefaultCapable(true);
		dialog.getRootPane().setDefaultButton(okButton);

		//helpButton = new JButton(GlobalResourceLoader.getString("dialog", "help"));
		helpButton = new HelpButton();
		//$NON-NLS-1$ //$NON-NLS-2$

		JPanel buttonPanel = new JPanel();
		buttonPanel.setLayout(new GridLayout(1, 3, 10, 0));
		buttonPanel.add(helpButton);
		buttonPanel.add(cancelButton);
		buttonPanel.add(okButton);

		//bottom.add( Box.createHorizontalGlue() );

		bottom.add(buttonPanel, BorderLayout.EAST);

		

		dialog.getContentPane().add(bottom, BorderLayout.SOUTH);
		*/
	}
	
	
	/*
	protected void initComponents()
	{
		dialog.getContentPane().setLayout(new BorderLayout());
		
		
		
		dialog.getContentPane().add( identityPanel, BorderLayout.CENTER );
		selected = identityPanel;
		
		panelChooser = new PanelChooser();
		dialog.getContentPane().add( panelChooser, BorderLayout.WEST );
		
		JPanel bottomPanel = new JPanel();
		bottomPanel.setBorder( new WizardTopBorder() );
		bottomPanel.setLayout( new BorderLayout() );
		
		JPanel buttonPanel = createButtonPanel();
		bottomPanel.add( buttonPanel, BorderLayout.CENTER );
		
		dialog.getContentPane().add( bottomPanel, BorderLayout.SOUTH );
		
	}
	*/
	
	protected JPanel createButtonPanel()
	{
		JPanel bottom = new JPanel();
		bottom.setLayout(new BorderLayout());
		//bottom.setLayout( new BoxLayout( bottom, BoxLayout.X_AXIS ) );
		bottom.setBorder(BorderFactory.createEmptyBorder(10, 5, 10, 5));

		//bottom.add( Box.createHorizontalStrut());

		
		//cancelButton = new JButton(GlobalResourceLoader.getString("dialog", "cancel"));
		cancelButton = new CancelButton();
		//$NON-NLS-1$ //$NON-NLS-2$
		cancelButton.addActionListener(this);
		cancelButton.setActionCommand("CANCEL"); //$NON-NLS-1$

		//okButton = new JButton(GlobalResourceLoader.getString("dialog", "ok"));
		//$NON-NLS-1$ //$NON-NLS-2$
		okButton = new OkButton();
		okButton.addActionListener(this);
		okButton.setActionCommand("OK"); //$NON-NLS-1$
		okButton.setDefaultCapable(true);
		dialog.getRootPane().setDefaultButton(okButton);

		//helpButton = new JButton(GlobalResourceLoader.getString("dialog", "help"));
		helpButton = new HelpButton();
		//$NON-NLS-1$ //$NON-NLS-2$

		JPanel buttonPanel = new JPanel();
		buttonPanel.setLayout(new GridLayout(1, 3, 10, 0));
		buttonPanel.add(helpButton);
		buttonPanel.add(cancelButton);
		buttonPanel.add(okButton);

		//bottom.add( Box.createHorizontalGlue() );

		bottom.add(buttonPanel, BorderLayout.EAST);

		

		return bottom;
	}
	

	public void actionPerformed(ActionEvent e)
	{
		String action = e.getActionCommand();

		if (action.equals("OK")) //$NON-NLS-1$
		{

			identityPanel.updateComponents(false);
			incomingServerPanel.updateComponents(false);
			receiveOptionsPanel.updateComponents(false);
			outgoingServerPanel.updateComponents(false);
			securityPanel.updateComponents(false);
			specialFoldersPanel.updateComponents(false);

			if (accountItem.isPopAccount())
			{
				// update pop3 fetch menu
				MainInterface.frameController.getMenu().updatePopServerMenu();

				int uid = accountItem.getUid();
				POP3ServerController c = MainInterface.popServerCollection.uidGet(uid);
				//c.restartTimer();

				//MainInterface.popServerCollection.enableMailCheckIcon();
			}
			else
			{
				// update tree label
				int uid = accountItem.getUid();

				IMAPRootFolder folder = (IMAPRootFolder) MainInterface.treeModel.getImapFolder(uid);
				folder.setName(accountItem.getName());
				
				//folder.restartTimer();
				
			}

			dialog.setVisible(false);
		}
		else if (action.equals("CANCEL")) //$NON-NLS-1$
		{
			dialog.setVisible(false);
		}

	}
	
	protected void setSelection( JPanel panel )
	{
		dialog.getContentPane().remove(selected);
		dialog.getContentPane().add( panel, BorderLayout.CENTER );
		dialog.validate();
		dialog.repaint();
		selected = panel;
	}
	

	public void valueChanged(ListSelectionEvent e) {
		JList lsm = (JList)e.getSource();
		switch( lsm.getSelectedIndex() ){
		case 0:
			setSelection( identityPanel );
			break;
		case 1:
			setSelection( incomingServerPanel );
			break;
		case 2:
			setSelection( outgoingServerPanel );
			break;
		case 3:
			setSelection( specialFoldersPanel );
			break;
		case 4:
			setSelection( securityPanel );
			break;
		}
	}
}