private static final long serialVersionUID = -7324749629151493210L;

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

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.w3c.dom.html.HTMLCollection;
import org.w3c.dom.html.HTMLFormElement;

/**
 * @xerces.internal
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.html.HTMLFormElement
 * @see org.apache.xerces.dom.ElementImpl
 */
public class HTMLFormElementImpl
    extends HTMLElementImpl
    implements HTMLFormElement
{

    private static final long serialVersionUID = 3690757284875876658L;

    public HTMLCollection getElements()
    {
        if ( _elements == null )
            _elements = new HTMLCollectionImpl( this, HTMLCollectionImpl.ELEMENT );
        return _elements;
    }
  

    public int getLength()
    {
        return getElements().getLength();
    }
  
  
    public String getName()
    {
        return getAttribute( "name" );
    }
    
    
    public void setName( String name )
    {
        setAttribute( "name", name );
    }

    
    public String getAcceptCharset()
    {
        return getAttribute( "accept-charset" );
    }
    
    
    public void setAcceptCharset( String acceptCharset )
    {
        setAttribute( "accept-charset", acceptCharset );
    }

  
      public String getAction()
    {
        return getAttribute( "action" );
    }
    
    
    public void setAction( String action )
    {
        setAttribute( "action", action );
    }
  
  
      public String getEnctype()
    {
        return getAttribute( "enctype" );
    }
    
    
    public void setEnctype( String enctype )
    {
        setAttribute( "enctype", enctype );
    }

    
      public String getMethod()
    {
        return capitalize( getAttribute( "method" ) );
    }
    
    
    public void setMethod( String method )
    {
        setAttribute( "method", method );
    }
  
  
    public String getTarget()
    {
        return getAttribute( "target" );
    }
    
    
    public void setTarget( String target )
    {
        setAttribute( "target", target );
    }

    
    public void submit()
    {
        // No scripting in server-side DOM. This method is moot.
    }

    
    public void reset()
    {
        // No scripting in server-side DOM. This method is moot.
    }

    /*
     * Explicit implementation of getChildNodes() to avoid problems with
     * overriding the getLength() method hidden in the super class.
     */
    public NodeList getChildNodes() {
        return getChildNodesUnoptimized();
    }
    
    /**
     * Explicit implementation of cloneNode() to ensure that cache used
     * for getElements() gets cleared.
     */
    public Node cloneNode( boolean deep ) {
        HTMLFormElementImpl clonedNode = (HTMLFormElementImpl)super.cloneNode( deep );
        clonedNode._elements = null;
        return clonedNode;
    }
    
    /**
     * Constructor requires owner document.
     * 
     * @param owner The owner HTML document
     */
    public HTMLFormElementImpl( HTMLDocumentImpl owner, String name )
    {
        super( owner, name );
    }
  
    
    /**
     * Collection of all elements contained in this FORM.
     */
    private HTMLCollectionImpl    _elements;
    
}
