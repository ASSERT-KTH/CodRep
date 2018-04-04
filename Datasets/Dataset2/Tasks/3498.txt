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

package org.columba.mail.gui.util;

import java.awt.Point;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;

import javax.swing.BoxLayout;
import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JPopupMenu;

import org.columba.main.MainInterface;

public class AddressLabel extends JPanel implements MouseListener//, ActionListener
{
    private String address;
    private JLabel[] list = new JLabel[3];

    //private AddressbookXmlConfig addressbookXmlConfig;
    private JFrame frame;

    private JPopupMenu popup;
    private JMenuItem menuItem;

    public AddressLabel( String str )
    {
        super();
        //this.frame = MainInterface.frameController.getView();
        //this.addressbookXmlConfig = MainInterface.config.getAddressbookConfig();

        setLayout( new BoxLayout( this, BoxLayout.X_AXIS ) );
        setBorder( null );
        this.address = str;

        parse();

        URLController controller = new URLController();

        if ( list[1] != null )
        {
            controller.setAddress( list[1].getText() );
            popup = controller.createContactMenu( list[1].getText() );
        }
        else
        {
            controller.setAddress( address );
            popup = controller.createContactMenu( address );
        }
    }

    protected void parse()
    {
        int index1 = address.indexOf("<");
        int index2 = address.indexOf(">");

        if ( index1 != -1 )
        {
            String str = address.substring( 0, index1+1 );
            list[0] = new JLabel( str );
            add( list[0] );

            str = address.substring( index1+1, index2 );
            list[1] = new LinkLabel( str );
            list[1].addMouseListener( this );
            add( list[1] );

            str = address.substring( index2, address.length() );
            list[2] = new JLabel( str );
            add( list[2] );
        }
        else //if ( address.indexOf("@") != -1 )
        {
            String str = address;

            int index = str.indexOf(",");
            if ( index != -1 )
            {
                // we got this from headerfieldtree
                list[0] = new JLabel();
                add( list[0] );

                list[1] = new LinkLabel( str.substring(0, index) );
                list[1].addMouseListener( this );
                add( list[1] );

                list[2] = new JLabel( str.substring(index, str.length() ) );
                add( list[2] );
            }
            else
            {
                list[0] = new JLabel();
                add( list[0] );

                list[1] = new LinkLabel( str );
                list[1].addMouseListener( this );
                add( list[1] );
            }

        }


    }

    public void setIcon( ImageIcon icon )
    {
        //list[2].setHorizontalTextPosition( JLabel.LEADING );
        if ( list[0] != null )list[0].setIcon( icon );
    }

    public void mouseClicked( MouseEvent e )
    {
        Point point = e.getPoint();
        popup.show( e.getComponent(),
                    e.getX(), e.getY() );
    }

    public void mouseEntered( MouseEvent e ){}
    public void mouseExited( MouseEvent e ){}
    public void mousePressed( MouseEvent e ){}
    public void mouseReleased( MouseEvent e ){}
}