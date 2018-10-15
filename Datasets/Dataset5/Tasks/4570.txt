private static final long serialVersionUID = 5409562635656244263L;

/*
 * Copyright 1999,2000,2004,2005 The Apache Software Foundation.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.html.dom;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.html.HTMLCollection;
import org.w3c.dom.html.HTMLElement;
import org.w3c.dom.html.HTMLTableCellElement;
import org.w3c.dom.html.HTMLTableElement;
import org.w3c.dom.html.HTMLTableRowElement;
import org.w3c.dom.html.HTMLTableSectionElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLTableRowElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLTableRowElementImpl
    extends HTMLElementImpl
    implements HTMLTableRowElement
{

    private static final long serialVersionUID = 3545231444772468278L;

    public int getRowIndex()
    {
        Node    parent;
        
        parent = getParentNode();
        if ( parent instanceof HTMLTableSectionElement )
            parent = parent.getParentNode();
        if ( parent instanceof HTMLTableElement )
            return getRowIndex( parent );;
        return -1;
    }
    
    
    public void setRowIndex( int rowIndex )
    {
        Node    parent;
        
        parent = getParentNode();
        if ( parent instanceof HTMLTableSectionElement )
            parent = parent.getParentNode();
        if ( parent instanceof HTMLTableElement )
            ( (HTMLTableElementImpl) parent ).insertRowX( rowIndex, this );
    }

  
    public int getSectionRowIndex()
    {
        Node    parent;
        
        parent = getParentNode();
        if ( parent instanceof HTMLTableSectionElement )
            return getRowIndex( parent );
        else
            return -1;
    }
    
    
    public void setSectionRowIndex( int sectionRowIndex )
    {
        Node    parent;
        
        parent = getParentNode();
        if ( parent instanceof HTMLTableSectionElement )
            ( (HTMLTableSectionElementImpl) parent ).insertRowX( sectionRowIndex, this );
    }
  
  
    int getRowIndex( Node parent )
    {
        NodeList    rows;
        int            i;
        
        // Use getElementsByTagName() which creates a snapshot of all the
        // TR elements under the TABLE/section. Access to the returned NodeList
        // is very fast and the snapshot solves many synchronization problems.
        rows = ( (HTMLElement) parent ).getElementsByTagName( "TR" );
        for ( i = 0 ; i < rows.getLength() ; ++i )
            if ( rows.item( i ) == this )
                return i;
        return -1;
    }

  
    public HTMLCollection  getCells()
    {
        if ( _cells == null )
            _cells = new HTMLCollectionImpl( this, HTMLCollectionImpl.CELL );
        return _cells;
    }
    
    
    public void setCells( HTMLCollection cells )
    {
        Node    child;
        int        i;
        
        child = getFirstChild();
        while ( child != null )
        {
            removeChild( child );
            child = child.getNextSibling();
        }
        i = 0;
        child = cells.item( i );
        while ( child != null )
        {
            appendChild ( child );
            ++i;
            child = cells.item( i );
        }
    }

  
    public HTMLElement insertCell( int index )
    {
        Node        child;
        HTMLElement    newCell;
        
        newCell = new HTMLTableCellElementImpl( (HTMLDocumentImpl) getOwnerDocument(), "TD" );
        child = getFirstChild();
        while ( child != null )
        {
            if ( child instanceof HTMLTableCellElement )
            {
                if ( index == 0 )
                {
                    insertBefore( newCell, child );
                    return newCell;
                }
                --index;
            }
            child = child.getNextSibling();
        }
        appendChild( newCell );
        return newCell;
    }
    
    
    public void deleteCell( int index )
    {
        Node    child;
        
        child = getFirstChild();
        while ( child != null )
        {
            if ( child instanceof HTMLTableCellElement )
            {
                if ( index == 0 )
                {
                    removeChild ( child );
                    return;
                }
                --index;
            }
            child = child.getNextSibling();
        }
    }

  
    public String getAlign()
    {
        return capitalize( getAttribute( "align" ) );
    }
    
    
    public void setAlign( String align )
    {
        setAttribute( "align", align );
    }

    
    public String getBgColor()
    {
        return getAttribute( "bgcolor" );
    }
    
    
    public void setBgColor( String bgColor )
    {
        setAttribute( "bgcolor", bgColor );
    }

  
    public String getCh()
    {
        String    ch;
        
        // Make sure that the access key is a single character.
        ch = getAttribute( "char" );
        if ( ch != null && ch.length() > 1 )
            ch = ch.substring( 0, 1 );
        return ch;
    }
    
    
    public void setCh( String ch )
    {
        // Make sure that the access key is a single character.
        if ( ch != null && ch.length() > 1 )
            ch = ch.substring( 0, 1 );
        setAttribute( "char", ch );
    }

    
    public String getChOff()
    {
        return getAttribute( "charoff" );
    }
    
    
    public void setChOff( String chOff )
    {
        setAttribute( "charoff", chOff );
    }
  
  
    public String getVAlign()
    {
        return capitalize( getAttribute( "valign" ) );
    }
    
    
    public void setVAlign( String vAlign )
    {
        setAttribute( "valign", vAlign );
    }
    
    /**
     * Explicit implementation of cloneNode() to ensure that cache used
     * for getCells() gets cleared.
     */
    public Node cloneNode( boolean deep ) {
        HTMLTableRowElementImpl clonedNode = (HTMLTableRowElementImpl)super.cloneNode( deep );
        clonedNode._cells = null;
        return clonedNode;
    }
    
    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLTableRowElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }
  
  
    HTMLCollection    _cells;

  
}
