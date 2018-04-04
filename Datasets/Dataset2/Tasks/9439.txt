import org.columba.core.main.MainInterface;

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

import javax.swing.JTable;
import javax.swing.ListSelectionModel;
import javax.swing.table.TableColumn;

import org.columba.core.config.Config;
import org.columba.mail.config.AccountList;
import org.columba.mail.gui.config.account.util.AccountHeaderRenderer;
import org.columba.mail.gui.config.account.util.NameRenderer;
import org.columba.mail.gui.config.account.util.StringAccountRenderer;
import org.columba.mail.util.MailResourceLoader;
import org.columba.main.MainInterface;

class AccountListTable extends JTable
{
    private AccountListDataModel model;
    private Config config;
    private AccountList AccountList;

    public AccountListTable(AccountList accountList, ConfigFrame frame)
    {
        super();

	this.AccountList = accountList;
        config = MainInterface.config;

        setSelectionMode( ListSelectionModel.SINGLE_SELECTION );


        model = new AccountListDataModel( AccountList );
        //update();

        setModel( model );

        setShowGrid(false);
        setIntercellSpacing(new java.awt.Dimension(0, 0));
		

        TableColumn tc = getColumn( MailResourceLoader.getString("dialog","account", "accountname") ); //$NON-NLS-1$
        tc.setCellRenderer( new NameRenderer() );
        tc.setHeaderRenderer( new AccountHeaderRenderer( MailResourceLoader.getString("dialog","account", "list_accountname") ) ); //$NON-NLS-1$
	

        tc = getColumn( MailResourceLoader.getString("dialog","account", "type") ); //$NON-NLS-1$
        tc.setMaxWidth(100);
        tc.setMinWidth(100);
        tc.setCellRenderer( new StringAccountRenderer(true) );
        tc.setHeaderRenderer( new AccountHeaderRenderer( MailResourceLoader.getString("dialog","account", "type") ) ); //$NON-NLS-1$


        sizeColumnsToFit( AUTO_RESIZE_NEXT_COLUMN );
    }

    public void update()
    {
        model.fireTableDataChanged();

    }



}

