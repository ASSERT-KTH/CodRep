private static final long serialVersionUID = 7164004431531608995L;

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

import org.w3c.dom.html.HTMLAreaElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLAreaElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLAreaElementImpl
    extends HTMLElementImpl
    implements HTMLAreaElement
{

    private static final long serialVersionUID = 3977019543719523380L;

    public String getAccessKey()
    {
        String    accessKey;
        
        // Make sure that the access key is a single character.
        accessKey = getAttribute( "accesskey" );
        if ( accessKey != null && accessKey.length() > 1 )
            accessKey = accessKey.substring( 0, 1 );
        return accessKey;
    }
    
    
    public void setAccessKey( String accessKey )
    {
        // Make sure that the access key is a single character.
        if ( accessKey != null && accessKey.length() > 1 )
            accessKey = accessKey.substring( 0, 1 );
        setAttribute( "accesskey", accessKey );
    }

    
    public String getAlt()
    {
        return getAttribute( "alt" );
    }
    
    
    public void setAlt( String alt )
    {
        setAttribute( "alt", alt );
    }
    
    public String getCoords()
    {
        return getAttribute( "coords" );
    }
    
    
    public void setCoords( String coords )
    {
        setAttribute( "coords", coords );
    }
  
  
    public String getHref()
    {
        return getAttribute( "href" );
    }
    
    
    public void setHref( String href )
    {
        setAttribute( "href", href );
    }

    
    public boolean getNoHref()
    {
        return getBinary( "href" );
    }
    
    
    public void setNoHref( boolean noHref )
    {
        setAttribute( "nohref", noHref );
    }
    
    
    public String getShape()
    {
        return capitalize( getAttribute( "shape" ) );
    }
    
    
    public void setShape( String shape )
    {
        setAttribute( "shape", shape );
    }

    
    public int getTabIndex()
    {
        return getInteger( getAttribute( "tabindex" ) );
    }
    
    
    public void setTabIndex( int tabIndex )
    {
        setAttribute( "tabindex", String.valueOf( tabIndex ) );
    }

    
    public String getTarget()
    {
        return getAttribute( "target" );
    }
    
    
    public void setTarget( String target )
    {
        setAttribute( "target", target );
    }
    
    
    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLAreaElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }
    
}
