private static final long serialVersionUID = -8513050483880341412L;

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

import org.w3c.dom.html.HTMLParamElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLParamElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLParamElementImpl
    extends HTMLElementImpl
    implements HTMLParamElement
{

    private static final long serialVersionUID = 3258412815831020848L;

    public String getName()
    {
        return getAttribute( "name" );
    }
    
    
    public void setName( String name )
    {
        setAttribute( "name", name );
    }
  
  
    public String getType()
    {
        return getAttribute( "type" );
    }
    
    
    public void setType( String type )
    {
        setAttribute( "type", type );
    }
    
    
      public String getValue()
    {
        return getAttribute( "value" );
    }
    
    
    public void setValue( String value )
    {
        setAttribute( "value", value );
    }

    
      public String getValueType()
    {
        return capitalize( getAttribute( "valuetype" ) );
    }
    
    
    public void setValueType( String valueType )
    {
        setAttribute( "valuetype", valueType );
    }


    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLParamElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }

  
}
