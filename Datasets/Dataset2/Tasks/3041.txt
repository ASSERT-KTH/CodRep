//initPopupMenu();

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
package org.columba.mail.gui.table.menu;

import java.awt.event.KeyEvent;
import java.awt.event.MouseAdapter;

import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import javax.swing.KeyStroke;

import org.columba.core.gui.util.CMenu;
import org.columba.core.gui.util.CMenuItem;
import org.columba.mail.gui.table.TableController;
import org.columba.mail.gui.table.action.HeaderTableActionListener;
import org.columba.mail.gui.table.action.HeaderTableMouseListener;
import org.columba.mail.util.MailResourceLoader;

/**
 * menu for the tableviewer
 */


public class HeaderTableMenu
{
    private JPopupMenu popupMenu;
    private TableController headerTableViewer;

    public HeaderTableMenu( TableController headerTableViewer )
    {
        this.headerTableViewer = headerTableViewer;

        initPopupMenu();
    }

    public JPopupMenu getPopupMenu()
    {
        return popupMenu;
    }

    protected HeaderTableMouseListener getMouseListener()
    {
        return headerTableViewer.getHeaderTableMouseListener();
    }

    protected HeaderTableActionListener getActionListener()
    {
        return headerTableViewer.getActionListener();
    }

    protected void initPopupMenu()
        {
           
	    popupMenu  = new JPopupMenu();
            //MouseListener popupListener = new PopupListener();
            headerTableViewer.getView().addMouseListener( getMouseListener() );

	    MouseAdapter handler = headerTableViewer.getMailFrameController().getMouseTooltipHandler();
            JMenuItem menuItem;
	    JMenu subMenu;

		menuItem = new CMenuItem( getActionListener().openMessageWithComposerAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );
	    
        

            menuItem = new CMenuItem( getActionListener().printAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );
	    
	        menuItem = new CMenuItem( getActionListener().saveAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );
	    

            popupMenu.addSeparator();

	    menuItem = new CMenuItem( getActionListener().replyAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

			
	    /*
	    subMenu = new JMenu( GlobalResourceLoader.getString("menu","mainframe","menu_message_replysubmenu"));
		popupMenu.add( subMenu );
		*/
		
	    menuItem = new CMenuItem( getActionListener().replyToAllAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );
	    
	    menuItem = new CMenuItem( getActionListener().replyToAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );
	    
	    menuItem = new CMenuItem( getActionListener().replyAsAttachmentAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

	    menuItem = new CMenuItem( getActionListener().forwardAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

            menuItem = new CMenuItem( getActionListener().forwardInlineAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

	  	// add the bounce-action 
			// bounce is reply with an error message
			menuItem = new CMenuItem( getActionListener().bounceAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

	    popupMenu.addSeparator();

	    menuItem = new CMenuItem( getActionListener().moveMessageAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

	    menuItem = new CMenuItem( getActionListener().copyMessageAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

            menuItem = new CMenuItem( getActionListener().deleteMessageAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

            popupMenu.addSeparator();

            menuItem = new CMenuItem( getActionListener().addSenderAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

            menuItem = new CMenuItem( getActionListener().addAllSendersAction );
	    menuItem.addMouseListener( handler );
	    popupMenu.add( menuItem );

	    popupMenu.addSeparator();

	    subMenu = new CMenu( MailResourceLoader.getString("menu","mainframe", "menu_message_mark") );
	    subMenu.setMnemonic( KeyEvent.VK_K );

	    menuItem = new org.columba.core.gui.util.CMenuItem(getActionListener().markAsReadAction);
	    menuItem.addMouseListener( handler );
	    subMenu.add( menuItem );
	    menuItem = new CMenuItem( "menu_message_markthreadasread", KeyEvent.VK_T);
	    menuItem.setEnabled(false);
	    subMenu.add( menuItem );
	    menuItem = new CMenuItem( "menu_message_markallasread", KeyEvent.VK_A);
	    menuItem.setAccelerator( KeyStroke.getKeyStroke("A") );
	    menuItem.setEnabled(false);
	    subMenu.add( menuItem );
	    subMenu.addSeparator();
	    menuItem = new org.columba.core.gui.util.CMenuItem(getActionListener().markAsFlaggedAction);
	    menuItem.addMouseListener( handler );
	    subMenu.add( menuItem );
	    menuItem = new org.columba.core.gui.util.CMenuItem(getActionListener().markAsExpungedAction);
	    menuItem.addMouseListener( handler );
	    subMenu.add( menuItem );



	    popupMenu.add( subMenu );


        }

}