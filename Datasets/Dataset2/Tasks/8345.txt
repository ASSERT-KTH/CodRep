import org.columba.addressbook.config.AdapterNode;

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


package org.columba.mail.config;


import java.io.File;

import org.columba.core.config.AdapterNode;
import org.columba.core.config.DefaultXmlConfig;
import org.columba.core.config.GuiItem;
import org.columba.core.config.TableItem;
import org.columba.core.config.ViewItem;
import org.columba.core.config.WindowItem;


public class MainFrameOptionsXmlConfig extends DefaultXmlConfig
{
   // private File file;

	WindowItem windowItem;
	GuiItem guiItem;
	TableItem headerTableItem;
	ViewItem viewItem;
	
    public MainFrameOptionsXmlConfig( File file )
    {
        super( file );
    }

	/*
    public AdapterNode getRootNode()
    {
        AdapterNode node = new AdapterNode( getDocument() );

        AdapterNode rootNode = node.getChild( 0 );
        return rootNode;
    }
	*/
	
    public TableItem getTableItem()
    {
    	if ( headerTableItem ==  null )
    	{
    		headerTableItem = new TableItem(getRoot().getElement("/options/gui/table"));
    	}
    	
    	return headerTableItem;
    	
    	/*
	HeaderTableItem headerTableItem = new HeaderTableItem();

        AdapterNode rootNode = getRootNode();
        AdapterNode guiNode = rootNode.getChild("gui");


        AdapterNode headerTableItemNode = guiNode.getChild("headertable");


        for ( int i=0; i< headerTableItemNode.getChildCount(); i++)
        {
            AdapterNode parent = headerTableItemNode.getChild(i);

            headerTableItem.addHeaderItem( parent.getChild(0),
                                           parent.getChild(3),
                                           parent.getChild(1),
                                           parent.getChild(2)
                                           );
        }

	return headerTableItem;
	*/
	
	
    }

    public TableItem getPop3HeaderTableItem()
    {
    	/*
	HeaderTableItem headerTableItem = new HeaderTableItem();

        AdapterNode rootNode = getRootNode();
        AdapterNode guiNode = rootNode.getChild("gui");


        AdapterNode headerTableItemNode = guiNode.getChild("pop3headertable");


        for ( int i=0; i< headerTableItemNode.getChildCount(); i++)
        {
            AdapterNode parent = headerTableItemNode.getChild(i);

            headerTableItem.addHeaderItem( parent.getChild(0),
                                           parent.getChild(3),
                                           parent.getChild(1),
                                           parent.getChild(2)
                                           );
        }

	return headerTableItem;
	*/
	
	return null;
    }
    
    public ViewItem getViewItem()
    {
    	if ( viewItem == null )
    	{
    		viewItem = new ViewItem( getRoot().getElement("/options/gui/viewlist/view") );
    	}
    	
    	return viewItem;
    }

	public GuiItem getGuiItem()
	{
		if ( guiItem == null )
		{
			guiItem = new GuiItem(getRoot().getElement("/options/gui"));
		}
		
		return guiItem;
	}
	
    public WindowItem getWindowItem()
    {
    	if ( windowItem == null )
    	{
    		
    		windowItem = new WindowItem(getRoot().getElement("/options/gui/viewlist/view/window"));
    		
    	}
       /*

        AdapterNode rootNode = getRootNode();
        AdapterNode guiNode = rootNode.getChild("gui");
        AdapterNode windowNode = guiNode.getChild("window");

      



        return new WindowItem( getDocument(), windowNode );
        */
        
        return windowItem;

    }

    public AdapterNode getMimeTypeNode()
    {
    	/*
        AdapterNode rootNode = getRootNode();
        AdapterNode node = rootNode.getChild("mimetypes");

        return node;
        */
        
        return null;
    }



}



