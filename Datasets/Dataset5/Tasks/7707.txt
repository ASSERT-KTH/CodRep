public abstract class BaseSerializer

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:  
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */


package org.apache.xml.serialize;


import java.io.*;
import java.util.Vector;
import java.util.Hashtable;
import java.util.StringTokenizer;

import org.w3c.dom.*;
import org.xml.sax.DocumentHandler;
import org.xml.sax.DTDHandler;
import org.xml.sax.Locator;
import org.xml.sax.SAXException;
import org.xml.sax.misc.LexicalHandler;
import org.xml.sax.misc.DeclHandler;


/**
 * Base class for a serializer supporting both DOM and SAX pretty
 * serializing of XML/HTML/XHTML documents. Derives classes perform
 * the method-specific serializing, this class provides the common
 * serializing mechanisms.
 * <p>
 * The serializer must be initialized with the proper writer and
 * output format before it can be used by calling {@link #init}.
 * The serializer can be reused any number of times, but cannot
 * be used concurrently by two threads.
 * <p>
 * If an output stream is used, the encoding is taken from the
 * output format (defaults to <tt>UTF8</tt>). If a writer is
 * used, make sure the writer uses the same encoding (if applies)
 * as specified in the output format.
 * <p>
 * The serializer supports both DOM and SAX. DOM serializing is done
 * by calling {@link #serialize} and SAX serializing is done by firing
 * SAX events and using the serializer as a document handler.
 * This also applies to derived class.
 * <p>
 * If an I/O exception occurs while serializing, the serializer
 * will not throw an exception directly, but only throw it
 * at the end of serializing (either DOM or SAX's {@link
 * org.xml.sax.DocumentHandler#endDocument}.
 * <p>
 * For elements that are not specified as whitespace preserving,
 * the serializer will potentially break long text lines at space
 * boundaries, indent lines, and serialize elements on separate
 * lines. Line terminators will be regarded as spaces, and
 * spaces at beginning of line will be stripped.
 * <p>
 * When indenting, the serializer is capable of detecting seemingly
 * element content, and serializing these elements indented on separate
 * lines. An element is serialized indented when it is the first or
 * last child of an element, or immediate following or preceding
 * another element.
 * 
 *
 * @version
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see Serializer
 * @see XMLSerializer
 */
abstract class BaseSerializer
    extends Serializer
    implements DocumentHandler, LexicalHandler, DTDHandler, DeclHandler
{


    /**
     * Identifies the last printable character in the Unicode range
     * that is supported by the encoding used with this serializer.
     * For 8-bit encodings this will be either 0x7E or 0xFF.
     * For 16-bit encodings this will be 0xFFFF. Characters that are
     * not printable will be escaped using character references.
     */
    private int              _lastPrintable = 0x7E;


    /**
     * The output format associated with this serializer. This will never
     * be a null reference. If no format was passed to the constructor,
     * the default one for this document type will be used. The format
     * object is never changed by the serializer.
     */
    protected OutputFormat  _format;


    /**
     * The writer to which the document is written.
     */
    private Writer          _writer;


    /**
     * Holds the currently accumulating text line. This buffer will constantly
     * be reused by deleting its contents instead of reallocating it.
     */
    private StringBuffer    _line;


    /**
     * Holds the currently accumulating text that follows {@link #_line}.
     * When the end of the part is identified by a call to {@link #printSpace}
     * or {@link #breakLine}, this part is added to the accumulated line.
     */
    private StringBuffer    _text;


    /**
     * Counts how many white spaces come between the accumulated line and the
     * current accumulated text. Multiple spaces at the end of the a line
     * will not be printed.
     */
    private int             _spaces;


    /**
     * Holds the indentation for the current line that is now accumulating in
     * memory and will be sent for printing shortly.
     */
    private int             _thisIndent;
    
    
    /**
     * Holds the indentation for the next line to be printed. After this line is
     * printed, {@link #_nextIndent} is assigned to {@link #_thisIndent}.
     */
    private int             _nextIndent;


    /**
     * Holds the exception thrown by the serializer.  Exceptions do not cause
     * the serializer to quit, but are held and one is thrown at the end.
     */
    protected IOException   _exception;


    /**
     * Holds array of all element states that have been entered.
     * The array is automatically resized. When leaving an element,
     * it's state is not removed but reused when later returning
     * to the same nesting level.
     */
    private ElementState[]  _elementStates = new ElementState[ 5 ];


    /**
     * The index of the next state to place in the array,
     * or one plus the index of the current state. When zero,
     * we are in no state.
     */
    private int             _elementStateCount;


    /**
     * Vector holding comments and PIs that come before the root
     * element (even after it), see {@link #serializePreRoot}.
     */
    private Vector          _preRoot;


    /**
     * If the document has been started (header serialized), this
     * flag is set to true so it's not started twice.
     */
    protected boolean       _started;


    /**
     * The DTD writer. When we switch to DTD mode, all output is
     * accumulated in this DTD writer. When we switch out of it,
     * the output is obtained as a string. Must not be reset to
     * null until we're done with the document.
     */
    private StringWriter    _dtdWriter;


    /**
     * Holds a reference to the document writer while we are
     * in DTD mode.
     */
    private Writer          _docWriter;

    


    //--------------------------------//
    // Constructor and initialization //
    //--------------------------------//


    /**
     * Protected constructor can only be used by derived class.
     * Must initialize the serializer before serializing any document,
     * see {@link #init}.
     */
    protected BaseSerializer()
    {
	int i;

	for ( i = 0 ; i < _elementStates.length ; ++i )
	    _elementStates[ i ] = new ElementState();
    }


    /**
     * Initialize the serializer with the specified writer and output format.
     * Must be called before calling any of the serialize methods.
     *
     * @param writer The writer to use
     * @param format The output format
     */
    public synchronized void init( Writer writer, OutputFormat format )
    {
	if ( format == null )
	    throw new NullPointerException( "Argument 'format' is null." );
	_format = format;
	if ( writer == null )
	    throw new NullPointerException( "Argument 'format' is null." );
	_writer = new BufferedWriter( writer );

	// Determine the last printable character based on the output format
	_lastPrintable = _format.getLastPrintable();

	// Initialize everything for a first/second run.
	_line = new StringBuffer( 80 );
	_text = new StringBuffer( 20 );
	_spaces = 0;
	_thisIndent = _nextIndent = 0;
	_exception = null;
	_elementStateCount = 0;
	_started = false;
	_dtdWriter = null;
    }


    /**
     * Initialize the serializer with the specified output stream and output format.
     * Must be called before calling any of the serialize methods.
     *
     * @param output The output stream to use
     * @param format The output format
     * @throws UnsupportedEncodingException The encoding specified
     *   in the output format is not supported
     */
    public synchronized void init( OutputStream output, OutputFormat format )
        throws UnsupportedEncodingException
    {
	String encoding;

	encoding = ( format.getEncoding() == null ? "ASCII" : format.getEncoding() );
	init( new OutputStreamWriter( output, encoding ), format );
    }


    //-------------------------------//
    // DOM document serializing methods //
    //-------------------------------//


    /**
     * Serializes the DOM element using the previously specified
     * writer and output format. Throws an exception only if
     * an I/O exception occured while serializing.
     *
     * @param elem The element to serialize
     * @throws IOException An I/O exception occured while
     *   serializing
     */
    public void serialize( Element elem )
        throws IOException
    {
	try {
	    startDocument();
	} catch ( SAXException except ) { }
	serializeNode( elem );
	flush();
	if ( _exception != null )
	    throw _exception;
    }


    /**
     * Serializes the DOM document using the previously specified
     * writer and output format. Throws an exception only if
     * an I/O exception occured while serializing.
     *
     * @param doc The document to serialize
     * @throws IOException An I/O exception occured while
     *   serializing
     */
    public void serialize( Document doc )
        throws IOException
    {
	try {
	    startDocument();
	} catch ( SAXException except ) { }
	serializeNode( doc );
	serializePreRoot();
        flush();
	if ( _exception != null )
	    throw _exception;
    }


    //---------------------------------------//
    // SAX document handler serializing methods //
    //---------------------------------------//


    public void characters( char[] chars, int start, int length )
    {
	characters( new String( chars, start, length ), false, false );
    }


    public void ignorableWhitespace( char[] chars, int start, int length )
    {
	int i;

	content();

	// Print ignorable whitespaces only when indenting, after
	// all they are indentation. Cancel the indentation to
	// not indent twice.
	if ( _format.getIndenting() ) {
	    _thisIndent = 0;
	    for ( i = start ; length-- > 0 ; ++i ) {
		if ( chars[ i ] == '\n' || chars[ i ] == '\r' )
		    breakLine();
		else
		    _text.append( chars[ i ] );
	    }
	}
    }


    public void processingInstruction( String target, String code )
    {
	int          index;
	StringBuffer buffer;
	ElementState state;

	state = content();
	buffer = new StringBuffer( 40 );

	// Create the processing instruction textual representation.
	// Make sure we don't have '?>' inside either target or code.
	index = target.indexOf( "?>" );
	if ( index >= 0 )
	    buffer.append( "<?" ).append( target.substring( 0, index ) );
	else
	    buffer.append( "<?" ).append( target );
	if ( code != null ) {
	    buffer.append( ' ' );
	    index = code.indexOf( "?>" );
	    if ( index >= 0 )
		buffer.append( code.substring( 0, index ) );
	    else
		buffer.append( code );
	}
	buffer.append( "?>" );

	// If before the root element (or after it), do not print
	// the PI directly but place it in the pre-root vector.
	if ( state == null ) {
	    if ( _preRoot == null )
		_preRoot = new Vector();
	    _preRoot.addElement( buffer.toString() );
	}
	else {
	    indent();
	    printText( buffer, true );
	    unindent();
	}
    }


    public void comment( char[] chars, int start, int length )
    {
	comment( new String( chars, start, length ) );
    }


    public void comment( String text )
    {
	StringBuffer buffer;
	int          index;
	ElementState state;

	state  = content();
	buffer = new StringBuffer( 40 );
	// Create the processing comment textual representation.
	// Make sure we don't have '-->' inside the comment.
	index = text.indexOf( "-->" );
	if ( index >= 0 )
	    buffer.append( "<!--" ).append( text.substring( 0, index ) ).append( "-->" );
	else
	    buffer.append( "<!--" ).append( text ).append( "-->" );

	// If before the root element (or after it), do not print
	// the comment directly but place it in the pre-root vector.
	if ( state == null ) {
	    if ( _preRoot == null )
		_preRoot = new Vector();
	    _preRoot.addElement( buffer.toString() );
	}
	else {
	    indent();
	    printText( buffer, false );
	    unindent();
	}
    }


    public void startCDATA()
    {
	ElementState state;

	state = getElementState();
	if ( state != null )
	    state.cdata = true;
    }


    public void endCDATA()
    {
	ElementState state;

	state = getElementState();
	if ( state != null )
	    state.cdata = false;
    }


    /**
     * Called at the end of the document to wrap it up.
     * Will flush the output stream and throw an exception
     * if any I/O error occured while serializing.
     *
     * @throws SAXException An I/O exception occured during
     *  serializing
     */
    public void endDocument()
        throws SAXException
    {
	// Print all the elements accumulated outside of
	// the root element.
	serializePreRoot();
	// Flush the output, this is necessary for buffered output.
        flush();
	// If an exception was thrown during serializing, this would
	// be the best time to report it.
	if ( _exception != null )
	    throw new SAXException( _exception );
    }


    public void startEntity( String name )
    {
	// ???
    }


    public void endEntity( String name )
    {
	// ???
    }


    public void setDocumentLocator( Locator locator )
    {
	// Nothing to do
    }


    //---------------------------------------//
    // SAX DTD/Decl handler serializing methods //
    //---------------------------------------//


    public void startDTD( String name, String publicId, String systemId )
    {
	enterDTD();
	// For the moment this simply overrides any settings performed
	// on the output format.
	_format.setDoctype( publicId, systemId );
    }


    public void endDTD()
    {
	// Nothing to do here, all the magic occurs in startDocument(String).
    }


    public void elementDecl( String name, String model )
    {
	enterDTD();
	printText( "<!ELEMENT " + name + " " + model + ">" );
	if ( _format.getIndenting() )
	    breakLine();
    }


    public void attributeDecl( String eName, String aName, String type,
			       String valueDefault, String value )
    {
	StringBuffer buffer;

	enterDTD();
	buffer = new StringBuffer( 40 );
	buffer.append( "<!ATTLIST " ).append( eName ).append( ' ' );
	buffer.append( aName ).append( ' ' ).append( type );
	if ( valueDefault != null )
	    buffer.append( ' ' ).append( valueDefault );
	if ( value != null )
	    buffer.append( " \"" ).append( escape( value ) ).append( '"' );
	buffer.append( '>' );
	printText( buffer.toString() );
	if ( _format.getIndenting() )
	    breakLine();
    }


    public void internalEntityDecl( String name, String value )
    {
	enterDTD();
	printText( "<!ENTITY " + name + " \"" + escape( value ) + "\">" );
	if ( _format.getIndenting() )
	    breakLine();
    }


    public void externalEntityDecl( String name, String publicId, String systemId )
    {
	enterDTD();
	unparsedEntityDecl( name, publicId, systemId, null );
    }


    public void unparsedEntityDecl( String name, String publicId,
				    String systemId, String notationName )
    {
	enterDTD();
	if ( publicId != null ) {
	    printText( "<!ENTITY " + name + " SYSTEM " );
	    printDoctypeURL( systemId );
	} else {
	    printText( "<!ENTITY " + name + " PUBLIC " );
	    printDoctypeURL( publicId );
	    printText( " " );
	    printDoctypeURL( systemId );
	}
	if ( notationName != null )
	    printText( " NDATA " + notationName );
	printText( ">" );
	if ( _format.getIndenting() )
	    breakLine();
    }


    public void notationDecl( String name, String publicId, String systemId )
    {
	enterDTD();
	if ( publicId != null ) {
	    printText( "<!NOTATION " + name + " PUBLIC " );
	    printDoctypeURL( publicId );
	    if ( systemId != null ) {
		printText( "  " );
		printDoctypeURL( systemId );
	    }
	} else {
	    printText( "<!NOTATION " + name + " SYSTEM " );
	    printDoctypeURL( systemId );
	}
	printText( ">" );
	if ( _format.getIndenting() )
	    breakLine();
    }


    /**
     * Called by any of the DTD handlers to enter DTD mode.
     * Once entered, all output will be accumulated in a string
     * that can be printed as part of the document's DTD.
     * This method may be called any number of time but will only
     * have affect the first time it's called. To exist DTD state
     * and get the accumulated DTD, call {@link #leaveDTD}.
     */
    protected void enterDTD()
    {
	// Can only enter DTD state once. Once we're out of DTD
	// state, can no longer re-enter it.
	if ( _dtdWriter == null ) {
	    _line.append( _text );
	    _text = new StringBuffer( 20 );
	    flushLine();
	    _dtdWriter = new StringWriter();
	    _docWriter = _writer;
	    _writer = _dtdWriter;
	}
    }


    /**
     * Called by the root element to leave DTD mode and if any
     * DTD parts were printer, will return a string with their
     * textual content.
     */
    protected String leaveDTD()
    {
	// Only works if we're going out of DTD mode.
	if ( _writer == _dtdWriter ) {
	    _line.append( _text );
	    _text = new StringBuffer( 20 );
	    flushLine();
	    _writer = _docWriter;
	    return _dtdWriter.toString();
	} else
	    return null;
    }


    //------------------------------------------//
    // Generic node serializing methods methods //
    //------------------------------------------//


    /**
     * Serialize the DOM node. This method is shared across XML, HTML and XHTML
     * serializers and the differences are masked out in a separate {@link
     * #serializeElement}.
     *
     * @param node The node to serialize
     * @see #serializeElement
     */
    protected void serializeNode( Node node )
    {
	// Based on the node type call the suitable SAX handler.
	// Only comments entities and documents which are not
	// handled by SAX are serialized directly.
        switch ( node.getNodeType() ) {
	case Node.TEXT_NODE :
	    characters( node.getNodeValue(), false, false );
	    break;

	case Node.CDATA_SECTION_NODE :
	    characters( node.getNodeValue(), true, false );
	    break;

	case Node.COMMENT_NODE :
	    comment( node.getNodeValue() );
	    break;

	case Node.ENTITY_REFERENCE_NODE :
	    // Entity reference printed directly in text, do not break or pause.
	    content();
	    printText( '&' + node.getNodeName() + ';' );
	    break;

	case Node.PROCESSING_INSTRUCTION_NODE :
	    processingInstruction( node.getNodeName(), node.getNodeValue() );
	    break;

	case Node.ELEMENT_NODE :
	    serializeElement( (Element) node );
	    break;

	case Node.DOCUMENT_NODE :
	    DocumentType docType;
	    NamedNodeMap map;
	    Entity       entity;
	    Notation     notation;
	    int          i;
	 
	    // If there is a document type, use the SAX events to
	    // serialize it.
	    docType = ( (Document) node ).getDoctype();
	    if ( docType != null ) {
		startDTD( docType.getName(), null, null );
		map = docType.getEntities();
		if ( map != null ) {
		    for ( i = 0 ; i < map.getLength() ; ++i ) {
			entity = (Entity) map.item( i );
			unparsedEntityDecl( entity.getNodeName(), entity.getPublicId(),
				    entity.getSystemId(), entity.getNotationName() );
		    }
		}
		map = docType.getNotations();
		if ( map != null ) {
		    for ( i = 0 ; i < map.getLength() ; ++i ) {
			notation = (Notation) map.item( i );
			notationDecl( notation.getNodeName(), notation.getPublicId(), notation.getSystemId() );
		    }
		}
		endDTD();
	    }
	    // !! Fall through
	case Node.DOCUMENT_FRAGMENT_NODE : {
	    Node         child;
	    
	    // By definition this will happen if the node is a document,
	    // document fragment, etc. Just serialize its contents. It will
	    // work well for other nodes that we do not know how to serialize.
	    child = node.getFirstChild();
	    while ( child != null ) {
		serializeNode( child );
		child = child.getNextSibling();
	    }
	    break;
	}

	default:
	    break;
	}
    }


    /**
     * Must be called by a method about to print any type of content.
     * If the element was just opened, the opening tag is closed and
     * will be matched to a closing tag. Returns the current element
     * state with <tt>empty</tt> and <tt>afterElement</tt> set to false.
     *
     * @return The current element state
     */    
    protected ElementState content()
    {
	ElementState state;

	state = getElementState();
	if ( state != null ) {
	    // If this is the first content in the element,
	    // change the state to not-empty and close the
	    // opening element tag.
	    if ( state.empty ) {
		printText( ">" );
		state.empty = false;
	    }
	    // Except for one content type, all of them
	    // are not last element. That one content
	    // type will take care of itself.
	    state.afterElement = false;
	}
	return state;
    }


    /**
     * Called to print the text contents in the prevailing element format.
     * Since this method is capable of printing text as CDATA, it is used
     * for that purpose as well. White space handling is determined by the
     * current element state. In addition, the output format can dictate
     * whether the text is printed as CDATA or unescaped.
     *
     * @param text The text to print
     * @param cdata True is should print as CDATA
     * @param unescaped True is should print unescaped
     */
    protected void characters( String text, boolean cdata, boolean unescaped )
    {
	ElementState state;

	state = content();
	cdata = state.cdata;
	// Check if text should be print as CDATA section or unescaped
	// based on elements listed in the output format (the element
	// state) or whether we are inside a CDATA section or entity.
	if ( state != null ) {
	    cdata = cdata || state.cdata;
	    unescaped = unescaped || state.unescaped;
	}

	if ( cdata ) {
	    StringBuffer buffer;
	    int          index;
	    int          saveIndent;

	    // Print a CDATA section. The text is not escaped, but ']]>'
	    // appearing in the code must be identified and dealt with.
	    // The contents of a text node is considered space preserving.
	    buffer = new StringBuffer( text.length() );
	    index = text.indexOf( "]]>" );
	    while ( index >= 0 ) {
		buffer.append( "<![CDATA[" ).append( text.substring( 0, index + 2 ) ).append( "]]>" );
		text = text.substring( index + 2 );
		index = text.indexOf( "]]>" );
	    }
	    buffer.append( "<![CDATA[" ).append( text ).append( "]]>" );
	    saveIndent = _nextIndent;
	    _nextIndent = 0;
	    printText( buffer, true );
	    _nextIndent = saveIndent;

	} else {

	    int saveIndent;

	    if ( unescaped ) {
		// If the text node of this element should be printed
		// unescaped, then cancel indentation and print it
		// directly without escaping.
		saveIndent = _nextIndent;
		_nextIndent = 0;
		printText( text, true );
		_nextIndent = saveIndent;
		
	    } else if ( state != null && state.preserveSpace ) {
		// If preserving space then hold of indentation so no
		// excessive spaces are printed at line breaks, escape
		// the text content without replacing spaces and print
		// the text breaking only at line breaks.
		saveIndent = _nextIndent;
		_nextIndent = 0;
		printText( escape( text ), true );
		_nextIndent = saveIndent;
		
	    } else {
		// This is the last, but the most common case of
		// printing without preserving spaces. If indentation was
		// requested, line will wrap at space boundaries.
		// All whitespaces will print as space characters.
		printText( escape( text ), false );
	    }

	}
    }


    /**
     * Returns the suitable entity reference for this character value,
     * or null if no such entity exists. Calling this method with <tt>'&amp;'</tt>
     * will return <tt>"&amp;amp;"</tt>.
     *
     * @param ch Character value
     * @return Character entity name, or null
     */
    protected abstract String getEntityRef( char ch );


    /**
     * Called to serializee the DOM element. The element is serialized based on
     * the serializer's method (XML, HTML, XHTML).
     *
     * @param elem The element to serialize
     */
    protected abstract void serializeElement( Element elem );


    /**
     * Comments and PIs cannot be serialized before the root element,
     * because the root element serializes the document type, which
     * generally comes first. Instead such PIs and comments are
     * accumulated inside a vector and serialized by calling this
     * method. Will be called when the root element is serialized
     * and when the document finished serializing.
     */
    protected void serializePreRoot()
    {
	int i;

	if ( _preRoot != null ) {
	    for ( i = 0 ; i < _preRoot.size() ; ++i ) {
		printText( (String) _preRoot.elementAt( i ), true );
		breakLine();
	    }
	    _preRoot.removeAllElements();
	}
    }


    //---------------------------------------------//
    // Text pretty printing and formatting methods //
    //---------------------------------------------//


    /**
     * Called to print additional text. Each time this method is called
     * it accumulates more text. When a space is printed ({@link
     * #printSpace}) all the accumulated text becomes one part and is
     * added to the accumulate line. When a line is long enough, it can
     * be broken at its text boundary.
     *
     * @param text The text to print
     */
    protected final void printText( String text )
    {
	// Add this text to the accumulated text which will not be
	// print until the next space break.
	_text.append( text );
    }


    protected final void printText( char[] chars, int start, int end )
    {
	_text.append( chars, start, end );
    }


    /**
     * Called to print additional text with whitespace handling.
     * If spaces are preserved, the text is printed as if by calling
     * {@link #printText(String)} with a call to {@link #breakLine}
     * for each new line. If spaces are not preserved, the text is
     * broken at space boundaries if longer than the line width;
     * Multiple spaces are printed as such, but spaces at beginning
     * of line are removed.
     *
     * @param text The text to print
     * @param preserveSpace Space preserving flag
     */
    protected final void printText( String text, boolean preserveSpace )
    {
	int index;
	char ch;

        if ( preserveSpace ) {
	    // Preserving spaces: the text must print exactly as it is,
	    // without breaking when spaces appear in the text and without
	    // consolidating spaces. If a line terminator is used, a line
	    // break will occur.
	    for ( index = 0 ; index < text.length() ; ++index ) {
		ch = text.charAt( index );
		if ( ch == '\n' || ch == '\r' )
		    breakLine();
		else
		    _text.append( ch );
	    }
        }
        else
        {
	    // Not preserving spaces: print one part at a time, and
	    // use spaces between parts to break them into different
	    // lines. Spaces at beginning of line will be stripped
	    // by printing mechanism. Line terminator is treated
	    // no different than other text part.
	    for ( index = 0 ; index < text.length() ; ++index ) {
		ch = text.charAt( index );
		if ( ch == ' ' || ch == '\f' || ch == '\t' || ch == '\n' || ch == '\r' )
		    printSpace();
		else
		    _text.append( ch );		    
	    }
        }
    }


    protected final void printText( StringBuffer text, boolean preserveSpace )
    {
	int index;
	char ch;

        if ( preserveSpace ) {
	    // Preserving spaces: the text must print exactly as it is,
	    // without breaking when spaces appear in the text and without
	    // consolidating spaces. If a line terminator is used, a line
	    // break will occur.
	    for ( index = 0 ; index < text.length() ; ++index ) {
		ch = text.charAt( index );
		if ( ch == '\n' || ch == '\r' )
		    breakLine();
		else
		    _text.append( ch );
	    }
        }
        else
        {
	    // Not preserving spaces: print one part at a time, and
	    // use spaces between parts to break them into different
	    // lines. Spaces at beginning of line will be stripped
	    // by printing mechanism. Line terminator is treated
	    // no different than other text part.
	    for ( index = 0 ; index < text.length() ; ++index ) {
		ch = text.charAt( index );
		if ( ch == ' ' || ch == '\f' || ch == '\t' || ch == '\n' || ch == '\r' )
		    printSpace();
		else
		    _text.append( ch );		    
	    }
        }
    }


    /**
     * Called to print a single space between text parts that may be
     * broken into separate lines. Must not be called to print a space
     * when preserving spaces. The text accumulated so far with {@link
     * #printText} will be added to the accumulated line, and a space
     * separator will be counted. If the line accumulated so far is
     * long enough, it will be printed.
     */
    protected final void printSpace()
    {
	// The line consists of the text accumulated in _line,
	// followed by one or more spaces as counted by _spaces,
	// followed by more space accumulated in _text:
	// -  Text is printed and accumulated into _text.
	// -  A space is printed, so _text is added to _line and
	//    a space is counted.
	// -  More text is printed and accumulated into _text.
	// -  A space is printed, the previous spaces are added
	//    to _line, the _text is added to _line, and a new
	//    space is counted.

	// If text was accumulated with printText(), then the space
	// means we have to move that text into the line and
	// start accumulating new text with printText().
	if ( _text.length() > 0 ) {

	    // If the text breaks a line bounary, wrap to the next line.
	    // The printed line size consists of the indentation we're going
	    // to use next, the accumulated line so far, some spaces and the
	    // accumulated text so far.
	    if ( _format.getLineWidth() > 0 &&
		 _thisIndent + _line.length() + _spaces + _text.length() > _format.getLineWidth() ) {
		flushLine();
		try {
		    // Print line and new line, then zero the line contents.
		    _writer.write( _format.getLineSeparator() );
		} catch ( IOException except ) {
		    // We don't throw an exception, but hold it
		    // until the end of the document.
		    if ( _exception == null )
			_exception = except;
		}
	    }

	    // Add as many spaces as we accumulaed before.
	    // At the end of this loop, _spaces is zero.
	    while ( _spaces > 0 ) {
		_line.append( ' ' );
		--_spaces;
	    }
	    _line.append( _text );
	    _text = new StringBuffer( 20 );
	}
	// Starting a new word: accumulate the text between the line
	// and this new word; not a new word: just add another space.
	++_spaces;
    }


    /**
     * Called to print a line consisting of the text accumulated so
     * far. This is equivalent to calling {@link #printSpace} but
     * forcing the line to print and starting a new line ({@link
     * #printSpace} will only start a new line if the current line
     * is long enough).
     */
    protected final void breakLine()
    {
	// Equivalent to calling printSpace and forcing a flushLine.
	if ( _text.length() > 0 ) {
	    while ( _spaces > 0 ) {
		_line.append( ' ' );
		--_spaces;
	    }	    
	    _line.append( _text );
	    _text = new StringBuffer( 20 );
	}
        flushLine();
	try {
	    // Print line and new line, then zero the line contents.
	    _writer.write( _format.getLineSeparator() );
	} catch ( IOException except ) {
	    // We don't throw an exception, but hold it
	    // until the end of the document.
	    if ( _exception == null )
		_exception = except;
	}
    }


    /**
     * Flushes the line accumulated so far to the writer and get ready
     * to accumulate the next line. This method is called by {@link
     * #printText} and {@link #printSpace} when the accumulated line plus
     * accumulated text are two long to fit on a given line. At the end of
     * this method {@link #_line} is empty and {@link #_spaces} is zero.
     */
    private void flushLine()
    {
        int     indent;

	if ( _line.length() > 0 ) {
	    try {

		if ( _format.getIndenting() ) {
		    // Make sure the indentation does not blow us away.
		    indent = _thisIndent;
		    if ( ( 2 * indent ) > _format.getLineWidth() && _format.getLineWidth() > 0 )
			indent = _format.getLineWidth() / 2;
		    // Print the indentation as spaces and set the current
		    // indentation to the next expected indentation.
		    while ( indent > 0 ) {
			_writer.write( ' ' );
			--indent;
		    }
		}
		_thisIndent = _nextIndent;

		// There is no need to print the spaces at the end of the line,
		// they are simply stripped and replaced with a single line
		// separator.
		_spaces = 0;
		_writer.write( _line.toString() );

		_line = new StringBuffer( 40 );
	    } catch ( IOException except ) {
		// We don't throw an exception, but hold it
		// until the end of the document.
		if ( _exception == null )
		    _exception = except;
	    }
	}
    }


    /**
     * Flush the output stream. Must be called when done printing
     * the document, otherwise some text might be buffered.
     */
    public void flush()
    {
	breakLine();
	try {
	    _writer.flush();
	} catch ( IOException except ) {
	    // We don't throw an exception, but hold it
	    // until the end of the document.
	    if ( _exception == null )
		_exception = except;
	}
    }


    /**
     * Increment the indentation for the next line.
     */
    protected void indent()
    {
	_nextIndent += _format.getIndent();
    }


    /**
     * Decrement the indentation for the next line.
     */
    protected void unindent()
    {
	_nextIndent -= _format.getIndent();
	if ( _nextIndent < 0 )
	    _nextIndent = 0;
	// If there is no current line and we're de-identing then
	// this indentation level is actually the next level.
	if ( ( _line.length() + _spaces + _text.length() ) == 0 )
	    _thisIndent = _nextIndent;
    }


    /**
     * Print a document type public or system identifier URL.
     * Encapsulates the URL in double quotes, escapes non-printing
     * characters and print it equivalent to {@link #printText}.
     *
     * @param url The document type url to print
     */
    protected void printDoctypeURL( String url )
    {
        StringBuffer    result;
        int                i;

        _text.append( '"' );
        for( i = 0 ; i < url.length() ; ++i ) {
            if ( url.charAt( i ) == '"' ||  url.charAt( i ) < 0x20 || url.charAt( i ) > 0x7F )
                _text.append( "%" ).append( Integer.toHexString( url.charAt( i ) ) );
            else
                _text.append( url.charAt( i ) );
        }
        _text.append( '"' );
    }


    /**
     * Escapes a string so it may be printed as text content or attribute
     * value. Non printable characters are escaped using character references.
     * Where the format specifies a deault entity reference, that reference
     * is used (e.g. <tt>&amp;lt;</tt>).
     *
     * @param source The string to escape
     * @return The escaped string
     */
    protected String escape( String source )
    {
        StringBuffer    result;
        int             i;
        char            ch;
        String          charRef;

        result = new StringBuffer( source.length() );
        for ( i = 0 ; i < source.length() ; ++i )  {
            ch = source.charAt( i );
	    // If the character is not printable, print as character reference.
	    // Non printables are below ASCII space but not tab or line
	    // terminator, ASCII delete, or above a certain Unicode threshold.
	    if ( ( ch < ' ' && ch != '\t' && ch != '\n' && ch != '\r' ) ||
		 ch > _lastPrintable || ch == 0xF7 )
		    result.append( "&#" ).append( Integer.toString( ch ) ).append( ';' );
	    else {
		    // If there is a suitable entity reference for this
		    // character, print it. The list of available entity
		    // references is almost but not identical between
		    // XML and HTML.
		    charRef = getEntityRef( ch );
		    if ( charRef == null )
			result.append( ch );
		    else
			result.append( '&' ).append( charRef ).append( ';' );
	    }
        }
        return result.toString();
    }


    //--------------------------------//
    // Element state handling methods //
    //--------------------------------//


    /**
     * Return the state of the current element, or null
     * if not within any element (e.g. before entering
     * root element).
     *
     * @return Current element state, or null
     */
    protected ElementState getElementState()
    {
	if ( _elementStateCount == 0 )
	    return null;
	else
	    return _elementStates[ _elementStateCount - 1 ];
    }


    /**
     * Enter a new element state for the specified element.
     * Tag name and space preserving is specified, element
     * state is initially empty.
     *
     * @return Current element state, or null
     */
    protected ElementState enterElementState( String tagName, boolean preserveSpace )
    {
	ElementState state;

	if ( _elementStateCount == _elementStates.length ) {
	    ElementState[] newStates;
	    int            i;

	    // Need to create a larger array of states.
	    // This does not happen often, unless the document
	    // is really deep.
	    newStates = new ElementState[ _elementStates.length + 5 ];
	    System.arraycopy( _elementStates, 0, newStates, 0, _elementStates.length );
	    _elementStates = newStates;
	    for ( i = _elementStateCount ; i < _elementStates.length ; ++i )
		_elementStates[ i ] = new ElementState();
	}
	state = _elementStates[ _elementStateCount ];
	state.tagName = tagName;
	state.preserveSpace = preserveSpace;
	state.empty = true;
	state.afterElement = false;
	++_elementStateCount;
	return state;
    }


    /**
     * Leave the current element state and return to the
     * state of the parent element, or no state if this
     * is the root element.
     *
     * @return Previous element state, or null
     */
    protected ElementState leaveElementState()
    {
	if ( _elementStateCount > 1 ) {
	    -- _elementStateCount;
	    return _elementStates[ _elementStateCount - 1 ];
	} else if ( _elementStateCount == 1 ) {
	    -- _elementStateCount;
	    return null;
	} else
	    return null;
    }


}