JButton cancelButton = new JButton(MailResourceLoader.getString("global", "cancel"));

//The contents of this file are subject to the Mozilla Public License Version 1.1
//(the "License"); you may not use this file except in compliance with the 
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License 
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003. 
//
//All Rights Reserved.

package org.columba.mail.gui.config.general;

import java.awt.BorderLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import javax.swing.*;

import org.columba.core.gui.config.themes.ThemePanel;

import org.columba.mail.util.MailResourceLoader;

public class GeneralOptionsDialog extends JDialog implements ActionListener
{
	JTabbedPane centerPane;
	GeneralPanel generalPanel;
	ComposerPanel composerPanel;
	ThemePanel themePanel;
	FontPanel fontPanel;

	JButton okButton;
	JButton cancelButton;
	boolean result;

	public GeneralOptionsDialog( JFrame frame )
	{
		//LOCALIZE
		super( frame, "General Options", true );
		initComponents();
		pack();
		setLocationRelativeTo(null);
	}

	public void updateComponents( boolean b )
	{
		generalPanel.updateComponents( b );
		composerPanel.updateComponents( b );
		themePanel.updateComponents( b );
		fontPanel.updateComponents( b );
	}


	protected void initComponents()
	{
		JPanel contentPane = new JPanel();
		contentPane.setLayout(new BorderLayout(0,0));
		centerPane = new JTabbedPane();
		generalPanel = new GeneralPanel();
		//LOCALIZE
		centerPane.add( generalPanel, "General" );
		composerPanel = new ComposerPanel();
		//LOCALIZE
		centerPane.add( composerPanel, "Composer" );
		themePanel = new ThemePanel();
		//LOCALIZE
		centerPane.add( themePanel, "Themes and Icons" );
		fontPanel = new FontPanel();
		//LOCALIZE
		centerPane.add( fontPanel, "Fonts" );
		contentPane.add(centerPane, BorderLayout.CENTER);
		JPanel bottomPanel = new JPanel(new BorderLayout(0,0));
		bottomPanel.setBorder(BorderFactory.createEmptyBorder(17, 0, 11, 11));
		JPanel buttonPanel = new JPanel(new GridLayout(1, 2, 5, 0));
		okButton = new JButton(MailResourceLoader.getString("global", "ok"));
		//mnemonic
		okButton.setActionCommand("OK");
		okButton.addActionListener(this);
		buttonPanel.add(okButton);
		JButton cancelButton = new JButton(MailResourceLoader.getString("global", "ok"));
		//mnemonic
		cancelButton.setActionCommand("CANCEL");
		cancelButton.addActionListener(this);
		buttonPanel.add(cancelButton);
		bottomPanel.add(buttonPanel, BorderLayout.EAST);
		contentPane.add(bottomPanel, BorderLayout.SOUTH);
		setContentPane(contentPane);
		getRootPane().setDefaultButton(okButton);
		getRootPane().registerKeyboardAction(this,"CANCEL",
						KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE,0),
						JComponent.WHEN_IN_FOCUSED_WINDOW);
	}

	public void actionPerformed(ActionEvent event)
	{
		String action = event.getActionCommand();

		if (action.equals("OK"))
		{
			result = true;
			setVisible(false);

		}
		else if (action.equals("CANCEL"))
		{
			result = false;
			setVisible(false);

		}
	}

	public boolean getResult()
	{
		return result;
	}
}