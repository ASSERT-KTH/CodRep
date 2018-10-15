private static final long serialVersionUID = 6424581972706750120L;

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

import org.w3c.dom.html.HTMLModElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLModElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLModElementImpl
    extends HTMLElementImpl
    implements HTMLModElement
{

    private static final long serialVersionUID = 3905801976649625913L;

    public String getCite()
    {
        return getAttribute( "cite" );
    }
    
    
    public void setCite( String cite )
    {
        setAttribute( "cite", cite );
    }
    
    
      public String getDateTime()
    {
        return getAttribute( "datetime" );
    }
    
    
    public void setDateTime( String dateTime )
    {
        setAttribute( "datetime", dateTime );
    }
    

    /**
     * Constructor requires owner document and tag name.
     * 
     * @param owner The owner HTML document
     */
    public HTMLModElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }


}
