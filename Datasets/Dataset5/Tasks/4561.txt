private static final long serialVersionUID = -4195360849946217644L;

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

import org.w3c.dom.html.HTMLPreElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLPreElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLPreElementImpl
    extends HTMLElementImpl
    implements HTMLPreElement
{

    private static final long serialVersionUID = 3257282552271156784L;

    public int getWidth()
    {
        return getInteger( getAttribute( "width" ) );
    }
    
    
    public void setWidth( int width )
    {
        setAttribute( "width", String.valueOf( width ) );
    }

    
    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLPreElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }

  
}
