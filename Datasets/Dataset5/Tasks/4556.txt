private static final long serialVersionUID = 2276953229932965067L;

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

import org.w3c.dom.html.HTMLObjectElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLObjectElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLObjectElementImpl
    extends HTMLElementImpl
    implements HTMLObjectElement, HTMLFormControl
{
    
    private static final long serialVersionUID = 3617014156759479090L;

    public String getCode()
    {
        return getAttribute( "code" );
    }
    
    
    public void setCode( String code )
    {
        setAttribute( "code", code );
    }

  
    public String getAlign()
    {
        return capitalize( getAttribute( "align" ) );
    }
    
    
    public void setAlign( String align )
    {
        setAttribute( "align", align );
    }
  
    
    public String getArchive()
    {
        return getAttribute( "archive" );
    }
    
    
    public void setArchive( String archive )
    {
        setAttribute( "archive", archive );
    }
    
    public String getBorder()
    {
        return getAttribute( "border" );
    }
    
    
    public void setBorder( String border )
    {
        setAttribute( "border", border );
    }

    
    public String getCodeBase()
    {
        return getAttribute( "codebase" );
    }
    
    
    public void setCodeBase( String codeBase )
    {
        setAttribute( "codebase", codeBase );
    }

    
    public String getCodeType()
    {
        return getAttribute( "codetype" );
    }
    
    
    public void setCodeType( String codeType )
    {
        setAttribute( "codetype", codeType );
    }

    
    public String getData()
    {
        return getAttribute( "data" );
    }
    
    
    public void setData( String data )
    {
        setAttribute( "data", data );
    }

  
      public boolean getDeclare()
    {
        return getBinary( "declare" );
    }
    
    
    public void setDeclare( boolean declare )
    {
        setAttribute( "declare", declare );
    }

    
    public String getHeight()
    {
        return getAttribute( "height" );
    }
    
    
    public void setHeight( String height )
    {
        setAttribute( "height", height );
    }

    
    public String getHspace()
    {
        return getAttribute( "hspace" );
    }
    
    
    public void setHspace( String hspace )
    {
        setAttribute( "hspace", hspace );
    }
  
    public String getName()
    {
        return getAttribute( "name" );
    }
    
    
    public void setName( String name )
    {
        setAttribute( "name", name );
    }

    
    public String getStandby()
    {
        return getAttribute( "standby" );
    }
    
    
    public void setStandby( String standby )
    {
        setAttribute( "standby", standby );
    }
  
      public int getTabIndex()
    {
        try
        {
            return Integer.parseInt( getAttribute( "tabindex" ) );
        }
        catch ( NumberFormatException except )
        {
            return 0;
        }
    }
    
    
    public void setTabIndex( int tabIndex )
    {
        setAttribute( "tabindex", String.valueOf( tabIndex ) );
    }

    
    public String getType()
    {
        return getAttribute( "type" );
    }
    
    
    public void setType( String type )
    {
        setAttribute( "type", type );
    }
    
    
    public String getUseMap()
    {
        return getAttribute( "useMap" );
    }
    
    
    public void setUseMap( String useMap )
    {
        setAttribute( "useMap", useMap );
    }
    
    
    public String getVspace()
    {
        return getAttribute( "vspace" );
    }
    
    
    public void setVspace( String vspace )
    {
        setAttribute( "vspace", vspace );
    }

  
    public String getWidth()
    {
        return getAttribute( "width" );
    }
    
    
    public void setWidth( String width )
    {
        setAttribute( "width", width );
    }

    
    
    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLObjectElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }


}
