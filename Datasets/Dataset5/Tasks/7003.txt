throw new NullPointerException( "HTM014 Argument 'title' is null." );

package org.apache.html.dom;
    

import org.w3c.dom.DOMException;
import org.w3c.dom.html.*;
import org.apache.xerces.dom.DOMImplementationImpl;


/**
 * Provides number of methods for performing operations that are independent
 * of any particular instance of the document object model. This class is
 * unconstructable, the only way to obtain an instance of a DOM implementation
 * is by calling the static method {@link #getDOMImplementation}.
 * 
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see org.w3c.dom.DOMImplementation
 */
public class HTMLDOMImplementationImpl
    extends DOMImplementationImpl
    implements HTMLDOMImplementation
{


    /**
     * Holds a reference to the single instance of the DOM implementation.
     * Only one instance is required since this class is multiple entry.
     */
    private static HTMLDOMImplementation _instance = new HTMLDOMImplementationImpl();


    /**
     * Private constructor assures that an object of this class cannot
     * be created. The only way to obtain an object is by calling {@link
     * #getDOMImplementation}.
     */
    private HTMLDOMImplementationImpl()
    {
    }


    /**
     * Create a new HTML document of the specified <TT>TITLE</TT> text.
     *
     * @param title The document title text
     * @return New HTML document
     */
    public final HTMLDocument createHTMLDocument( String title )
        throws DOMException
    {
	HTMLDocument doc;

	if ( title == null )
	    throw new NullPointerException( "Argument 'title' is null." );
	doc = new HTMLDocumentImpl();
	doc.setTitle( title );
	return doc;
    }


    /**
     * Returns an instance of a {@link HTMLDOMImplementation} that can be
     * used to perform operations that are not specific to a particular
     * document instance, e.g. to create a new document.
     *
     * @return Reference to a valid DOM implementation
     */
    public static HTMLDOMImplementation getHTMLDOMImplementation()
    {
	return _instance;
    }


}