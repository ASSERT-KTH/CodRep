private static final long serialVersionUID = 2393622754706230429L;

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

import org.w3c.dom.html.HTMLIFrameElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLIFrameElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLIFrameElementImpl
    extends HTMLElementImpl
    implements HTMLIFrameElement
{

    private static final long serialVersionUID = 3617297817824014903L;

    public String getAlign()
    {
        return capitalize( getAttribute( "align" ) );
    }
    
    
    public void setAlign( String align )
    {
        setAttribute( "align", align );
    }
  
    
    public String getFrameBorder()
    {
        return getAttribute( "frameborder" );
    }
    
    
    public void setFrameBorder( String frameBorder )
    {
        setAttribute( "frameborder", frameBorder );
    }

    
    public String getHeight()
    {
        return getAttribute( "height" );
    }
    
    
    public void setHeight( String height )
    {
        setAttribute( "height", height );
    }
  
    public String getLongDesc()
    {
        return getAttribute( "longdesc" );
    }
    
    
    public void setLongDesc( String longDesc )
    {
        setAttribute( "longdesc", longDesc );
    }
  
  
    public String getMarginHeight()
    {
        return getAttribute( "marginheight" );
    }
    
    
    public void setMarginHeight( String marginHeight )
    {
        setAttribute( "marginheight", marginHeight );
    }
  
  
    public String getMarginWidth()
    {
        return getAttribute( "marginwidth" );
    }
    
    
    public void setMarginWidth( String marginWidth )
    {
        setAttribute( "marginwidth", marginWidth );
    }

  
      public String getName()
    {
        return getAttribute( "name" );
    }
    
    
    public void setName( String name )
    {
        setAttribute( "name", name );
    }

    
    public String getScrolling()
    {
        return capitalize( getAttribute( "scrolling" ) );
    }
    
    
    public void setScrolling( String scrolling )
    {
        setAttribute( "scrolling", scrolling );
    }
    
  
       public String getSrc()
    {
        return getAttribute( "src" );
    }
    
    
    public void setSrc( String src )
    {
        setAttribute( "src", src );
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
    public HTMLIFrameElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }


}
