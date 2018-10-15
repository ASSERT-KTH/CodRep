private static final long serialVersionUID = 1293750546025862146L;

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

import org.w3c.dom.html.HTMLOListElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLOListElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLOListElementImpl
    extends HTMLElementImpl
    implements HTMLOListElement
{

    private static final long serialVersionUID = 3544958748826349621L;

    public boolean getCompact()
    {
        return getBinary( "compact" );
    }
    
    
    public void setCompact( boolean compact )
    {
        setAttribute( "compact", compact );
    }
    
    
      public int getStart()
    {
        return getInteger( getAttribute( "start" ) );
    }
    
    
    public void setStart( int start )
    {
        setAttribute( "start", String.valueOf( start ) );
    }
  
  
    public String getType()
    {
        return getAttribute( "type" );
    }
    
    
    public void setType( String type )
    {
        setAttribute( "type", type );
    }
        
        
      /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLOListElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }


}
