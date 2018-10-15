private static final long serialVersionUID = 640139325394332007L;

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

import org.w3c.dom.html.HTMLInputElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLInputElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLInputElementImpl
    extends HTMLElementImpl
    implements HTMLInputElement, HTMLFormControl
{

    private static final long serialVersionUID = 3905799764707980082L;

    public String getDefaultValue()
    {
        // ! NOT FULLY IMPLEMENTED !
        return getAttribute( "defaultValue" );
    }
    
    
    public void setDefaultValue( String defaultValue )
    {
        // ! NOT FULLY IMPLEMENTED !
        setAttribute( "defaultValue", defaultValue );
    }
    
    
    public boolean getDefaultChecked()
    {
        // ! NOT FULLY IMPLEMENTED !
        return getBinary( "defaultChecked" );
    }
    
    
    public void setDefaultChecked( boolean defaultChecked )
    {
        // ! NOT FULLY IMPLEMENTED !
        setAttribute( "defaultChecked", defaultChecked );
    }
  
    
    public String getAccept()
    {
        return getAttribute( "accept" );
    }
    
    
    public void setAccept( String accept )
    {
        setAttribute( "accept", accept );
    }   
    
    
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
    
    
    public boolean getChecked()
    {
        return getBinary( "checked" );
    }
    
    
    public void setChecked( boolean checked )
    {
        setAttribute( "checked", checked );
    }
  
    
    public boolean getDisabled()
    {
        return getBinary( "disabled" );
    }
    
    
    public void setDisabled( boolean disabled )
    {
        setAttribute( "disabled", disabled );
    }
    
    
    public int getMaxLength()
    {
        return getInteger( getAttribute( "maxlength" ) );
    }
    
    
    public void setMaxLength( int maxLength )
    {
        setAttribute( "maxlength", String.valueOf( maxLength ) );
    }
    
    
    public String getName()
    {
        return getAttribute( "name" );
    }
    
    
    public void setName( String name )
    {
        setAttribute( "name", name );
    }
    
    
    public boolean getReadOnly()
    {
        return getBinary( "readonly" );
    }
    
    
    public void setReadOnly( boolean readOnly )
    {
        setAttribute( "readonly", readOnly );
    }
    
    
    public String getSize()
    {
        return getAttribute( "size" );
    }
    
    
    public void setSize( String size )
    {
        setAttribute( "size", size );
    }
    
    
    public String getSrc()
    {
        return getAttribute( "src" );
    }
    
    
    public void setSrc( String src )
    {
        setAttribute( "src", src );
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
    
    
    public String getUseMap()
    {
        return getAttribute( "useMap" );
    }
    
    
    public void setUseMap( String useMap )
    {
        setAttribute( "useMap", useMap );
    }
    
    
    public String getValue()
    {
        return getAttribute( "value" );
    }
    
    
    public void setValue( String value )
    {
        setAttribute( "value", value );
    }
    
    
    public void blur()
    {
        // No scripting in server-side DOM. This method is moot.
    }
    
    
    public void focus()
    {
        // No scripting in server-side DOM. This method is moot.
    }
    
    
    public void select()
    {
        // No scripting in server-side DOM. This method is moot.
    }
    
    
    public void click()
    {
        // No scripting in server-side DOM. This method is moot.
    }

  
    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLInputElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }


}

