private static final long serialVersionUID = 9058852459426595202L;

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

import org.w3c.dom.html.HTMLBodyElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLBodyElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLBodyElementImpl
    extends HTMLElementImpl
    implements HTMLBodyElement
{
    
    private static final long serialVersionUID = 4120852174621454900L;

    public String getALink()
    {
        return getAttribute( "alink" );
    }

    
    public void setALink(String aLink)
    {
        setAttribute( "alink", aLink );
    }
    
  
    public String getBackground()
    {
        return getAttribute( "background" );
    }
    
  
    public void setBackground( String background )
    {
        setAttribute( "background", background );
    }
    
  
    public String getBgColor()
    {
        return getAttribute( "bgcolor" );
    }
    
    
    public void setBgColor(String bgColor)
    {
        setAttribute( "bgcolor", bgColor );
    }
    
  
    public String getLink()
    {
        return getAttribute( "link" );
    }
  
    
    public void setLink(String link)
    {
        setAttribute( "link", link );
    }
    
  
    public String getText()
    {
        return getAttribute( "text" );
    }
    
  
    public void setText(String text)
    {
        setAttribute( "text", text );
    }
    
  
    public String getVLink()
    {
        return getAttribute( "vlink" );
    }
  
    
    public void  setVLink(String vLink)
    {
        setAttribute( "vlink", vLink );
    }
  
    
      /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLBodyElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }

  
}
