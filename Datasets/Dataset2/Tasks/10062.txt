import org.columba.core.gui.toolbar.ToolbarButton;

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

package org.columba.addressbook.gui.toolbar;


import java.util.ResourceBundle;

import javax.swing.JToolBar;

import org.columba.addressbook.main.AddressbookInterface;
import org.columba.core.gui.util.ToolbarButton;



public class AddressbookToolBar extends JToolBar
{
    private AddressbookInterface addressbookInterface;

    private ResourceBundle toolbarLabels;

    public AddressbookToolBar( AddressbookInterface addressbookInterface )
        {
            super();
            this.addressbookInterface = addressbookInterface;




            addCButtons();

	    putClientProperty("JToolBar.isRollover",Boolean.TRUE);

            setFloatable(false);
        }

    public void addButton( ToolbarButton button )
    {
        add( button  );
        button.setRolloverEnabled( true );
          //button.setBorder( new ColumbaButtonBorder() );
    }

    public void addCButtons()
        {
        	

/*
	    //MouseAdapter handler = MainInterface.statusBar.getHandler();
	    ToolbarButton button;

	    addSeparator();

		
	    button = new ToolbarButton( addressbookInterface.actionListener.addContactAction);
	    addButton( button  );

            button = new ToolbarButton( addressbookInterface.actionListener.addGroupAction);
	    addButton( button  );

            addSeparator();

            button = new ToolbarButton( addressbookInterface.actionListener.propertiesAction);
	    addButton( button  );

            button = new ToolbarButton( addressbookInterface.actionListener.removeAction);
	    addButton( button  );

            addSeparator();
*/
		
        }


}