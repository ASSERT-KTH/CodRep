import org.columba.core.gui.base.CheckBoxWithMnemonic;

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
package org.columba.mail.gui.config.account;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSpinner;
import javax.swing.JTextField;
import javax.swing.SpinnerNumberModel;

import org.columba.core.gui.util.CheckBoxWithMnemonic;
import org.columba.mail.config.PopItem;
import org.columba.mail.util.MailResourceLoader;

import com.jgoodies.forms.builder.DefaultFormBuilder;
import com.jgoodies.forms.layout.FormLayout;


/**
 *
 * @author  freddy
 * @version
 */
public class PopAttributPanel implements ActionListener {
    private PopItem item;
    private JCheckBox secureCheckBox;
    private JCheckBox leaveOnServerCheckBox;
    private JCheckBox storePasswordCheckBox;
    private JCheckBox excludeCheckBox;
    private JCheckBox enablePreProcessingFilterCheckBox;
    private JCheckBox removeOldMessagesCheckBox;
    private JSpinner olderThanSpinner;
    private JLabel daysLabel;
  
    private JCheckBox limitMessageDownloadCheckBox;
    private JTextField limitMessageDownloadTextField;
    private JButton configurePreProcessingFilterButton;
    private JPanel jPanel1;
    private JPanel jPanel4;
    private JPanel deleteLocallyPanel;
    private JCheckBox deleteLocallyCheckBox;
    private JPanel jPanel2;
    private JPanel jPanel3;

    private JButton selectButton;

    private JDialog dialog;

    public PopAttributPanel(JDialog dialog, PopItem item) {
        super();
        this.item = item;
        this.dialog = dialog;

        initComponents();
    }

   
    public void updateComponents(boolean b) {
      
        if (b) {
            leaveOnServerCheckBox.setSelected(item.getBoolean(
                    PopItem.LEAVE_MESSAGES_ON_SERVER));
        	removeOldMessagesCheckBox.setSelected(item.getBooleanWithDefault(PopItem.REMOVE_OLD_FROM_SERVER, false));
        	
        	updateRemoveOldMessagesEnabled();

        	olderThanSpinner.getModel().setValue(new Integer( item.getIntegerWithDefault(PopItem.OLDER_THAN, 30)));
        	
            excludeCheckBox.setSelected(item.getBooleanWithDefault(
                    PopItem.EXCLUDE_FROM_CHECKALL, false));

            limitMessageDownloadCheckBox.setSelected(item.getBoolean(
                    PopItem.ENABLE_DOWNLOAD_LIMIT));

            limitMessageDownloadTextField.setText(item.get(PopItem.DOWNLOAD_LIMIT));

        } else {
        	item.setBoolean(PopItem.REMOVE_OLD_FROM_SERVER, removeOldMessagesCheckBox.isSelected());

        	item.setInteger(PopItem.OLDER_THAN, ((SpinnerNumberModel)olderThanSpinner.getModel()).getNumber().intValue() );
        	
        	item.setBoolean(PopItem.LEAVE_MESSAGES_ON_SERVER,
                leaveOnServerCheckBox.isSelected()); //$NON-NLS-1$

            item.setBoolean(PopItem.EXCLUDE_FROM_CHECKALL, excludeCheckBox.isSelected()); //$NON-NLS-1$

            item.setString(PopItem.DOWNLOAD_LIMIT, limitMessageDownloadTextField.getText());

            item.setBoolean(PopItem.ENABLE_DOWNLOAD_LIMIT,
                limitMessageDownloadCheckBox.isSelected());

        }
    }

    /**
	 * 
	 */
	private void updateRemoveOldMessagesEnabled() {
		removeOldMessagesCheckBox.setEnabled(leaveOnServerCheckBox.isSelected());
		olderThanSpinner.setEnabled(leaveOnServerCheckBox.isSelected());
		daysLabel.setEnabled(leaveOnServerCheckBox.isSelected());
	}

	public void createPanel(DefaultFormBuilder builder) {
    	JPanel panel;
    	FormLayout l;
    	DefaultFormBuilder b;
		
    	builder.appendSeparator(MailResourceLoader.getString("dialog",
                "account", "options"));

        builder.append(leaveOnServerCheckBox, 4);
        builder.nextLine();

        builder.setLeadingColumnOffset(2);
        
        panel = new JPanel();
        l = new FormLayout("default, 3dlu, min(50;default), 3dlu, default",
            // 2 columns
            ""); // rows are added dynamically (no need to define them here)

        // create a form builder
        b = new DefaultFormBuilder(panel, l);
        b.append(removeOldMessagesCheckBox);
        b.append(olderThanSpinner);
        b.append(daysLabel);
        builder.append(panel,3);
        builder.nextLine();
        
        builder.setLeadingColumnOffset(1);
        builder.append(excludeCheckBox, 4);
        builder.nextLine();

        panel = new JPanel();
        l = new FormLayout("max(100;default), 3dlu, left:max(50dlu;default)",
                
            // 2 columns
            ""); // rows are added dynamically (no need to define them here)

        // create a form builder
        b = new DefaultFormBuilder(panel, l);
        b.append(limitMessageDownloadCheckBox, limitMessageDownloadTextField);

        builder.append(panel, 4);

    }

    protected void initComponents() {
        leaveOnServerCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", PopItem.LEAVE_MESSAGES_ON_SERVER));
        leaveOnServerCheckBox.setActionCommand("LEAVE_ON_SERVER");
        leaveOnServerCheckBox.addActionListener(this);
        
        limitMessageDownloadCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "limit_message_download_to"));

        limitMessageDownloadCheckBox.setActionCommand("LIMIT_MESSAGE_DOWNLOAD");
        limitMessageDownloadCheckBox.addActionListener(this);


        limitMessageDownloadTextField = new JTextField();

        excludeCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                    "dialog", "account", "exclude_from_fetch_all"));

        removeOldMessagesCheckBox = new CheckBoxWithMnemonic(MailResourceLoader.getString(
                "dialog", "account", PopItem.REMOVE_OLD_FROM_SERVER));
        
        olderThanSpinner = new JSpinner(new SpinnerNumberModel(1,1,Integer.MAX_VALUE,1));
        
        daysLabel = new JLabel(MailResourceLoader.getString(
                "dialog", "account", "days"));
       
    }

    public void actionPerformed(ActionEvent e) {
        String action = e.getActionCommand();

       if (action.equals("LIMIT_MESSAGE_DOWNLOAD")) {
            limitMessageDownloadTextField.setEnabled(limitMessageDownloadCheckBox.isSelected());
        } else if (action.equals("LEAVE_ON_SERVER")) {
        	updateRemoveOldMessagesEnabled();
        }
    }
}