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

package org.columba.addressbook.gui.frame;

import java.awt.BorderLayout;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Toolkit;

import javax.swing.JFrame;
import javax.swing.JSplitPane;

import org.columba.addressbook.gui.menu.AddressbookMenu;
import org.columba.addressbook.gui.table.AddressbookTable;
import org.columba.addressbook.gui.toolbar.AddressbookToolBar;
import org.columba.addressbook.gui.tree.AddressbookTree;
import org.columba.addressbook.main.AddressbookInterface;
import org.columba.core.gui.statusbar.StatusBar;
import org.columba.core.gui.util.ImageLoader;
import org.columba.main.MainInterface;


public class AddressbookView extends JFrame
{
    private AddressbookInterface addressbookInterface;
    private AddressbookTree tree;
    private AddressbookTable table;

    public AddressbookView()
    {
        super( "Columba v"+MainInterface.version+" - Addressbook" );
	this.setIconImage( ImageLoader.getImageIcon("ColumbaIcon.png").getImage());

        addressbookInterface = MainInterface.addressbookInterface;
        addressbookInterface.frame = this;
        // FIXME
        
        //addressbookInterface.actionListener = new AddressbookActionListener( addressbookInterface );
        addressbookInterface.menu = new AddressbookMenu( addressbookInterface );

        init();
    }

    public void init()
    {
        Container c = getContentPane();

        setJMenuBar( addressbookInterface.menu.getMenuBar() );

        AddressbookToolBar toolbar = new AddressbookToolBar( addressbookInterface );

        c.add( toolbar, BorderLayout.NORTH );

        tree = createTree( addressbookInterface );

        addressbookInterface.tree = tree;
        table = new AddressbookTable( addressbookInterface );
        table.setupRenderer();
        addressbookInterface.table = table;

        JSplitPane splitPane = new JSplitPane( JSplitPane.HORIZONTAL_SPLIT, tree.scrollPane, table );
        splitPane.setBorder( null );

        c.add( splitPane, BorderLayout.CENTER );

        StatusBar statusbar = new StatusBar(addressbookInterface.taskManager);
        addressbookInterface.statusbar = statusbar;

        c.add( statusbar, BorderLayout.SOUTH );

        pack();
	
	Dimension size=getSize();
	Dimension screenSize=Toolkit.getDefaultToolkit().getScreenSize();
	setLocation((screenSize.width-size.width)/2,(screenSize.height-size.height)/2);

        //setVisible(true);
    }

    protected AddressbookTree createTree( AddressbookInterface addressbookInterface )
    {
    	AddressbookTree tree = new AddressbookTree( addressbookInterface );
    	return tree;
    }
}

