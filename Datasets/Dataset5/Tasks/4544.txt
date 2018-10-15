private static final long serialVersionUID = 1424360710977241315L;

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

import org.w3c.dom.html.HTMLImageElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLImageElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLImageElementImpl
    extends HTMLElementImpl
    implements HTMLImageElement
{

    private static final long serialVersionUID = 3545514006426300471L;

    public String getLowSrc()
    {
        return getAttribute( "lowsrc" );
    }
    
    
    public void setLowSrc( String lowSrc )
    {
        setAttribute( "lowsrc", lowSrc );
    }

  
       public String getSrc()
    {
        return getAttribute( "src" );
    }
    
    
    public void setSrc( String src )
    {
        setAttribute( "src", src );
    }

    
      public String getName()
    {
        return getAttribute( "name" );
    }
    
    
    public void setName( String name )
    {
        setAttribute( "name", name );
    }

    
    public String getAlign()
    {
        return capitalize( getAttribute( "align" ) );
    }
    
    
    public void setAlign( String align )
    {
        setAttribute( "align", align );
    }
  
    
    public String getAlt()
    {
        return getAttribute( "alt" );
    }
    
    
    public void setAlt( String alt )
    {
        setAttribute( "alt", alt );
    }

    
    public String getBorder()
    {
        return getAttribute( "border" );
    }
    
    
    public void setBorder( String border )
    {
        setAttribute( "border", border );
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
    
  
    public boolean getIsMap()
    {
        return getBinary( "ismap" );
    }
    
    
    public void setIsMap( boolean isMap )
    {
        setAttribute( "ismap", isMap );
    }

    
    public String getLongDesc()
    {
        return getAttribute( "longdesc" );
    }
    
    
    public void setLongDesc( String longDesc )
    {
        setAttribute( "longdesc", longDesc );
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
    public HTMLImageElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }


}
