private static final long serialVersionUID = -2401961905874264272L;

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

import org.w3c.dom.html.HTMLMetaElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLMetaElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLMetaElementImpl
    extends HTMLElementImpl
    implements HTMLMetaElement
{

    private static final long serialVersionUID = 3256722862131197489L;

    public String getContent()
    {
        return getAttribute( "content" );
    }
    
    
    public void setContent( String content )
    {
        setAttribute( "content", content );
    }

    
    
      public String getHttpEquiv()
    {
        return getAttribute( "http-equiv" );
    }
    
    
    public void setHttpEquiv( String httpEquiv )
    {
        setAttribute( "http-equiv", httpEquiv );
    }

  
      public String getName()
    {
        return getAttribute( "name" );
    }
    
    
    public void setName( String name )
    {
        setAttribute( "name", name );
    }

    
      public String getScheme()
    {
        return getAttribute( "scheme" );
    }
    
    
    public void setScheme( String scheme )
    {
        setAttribute( "scheme", scheme );
    }
    
    
    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLMetaElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }


}
