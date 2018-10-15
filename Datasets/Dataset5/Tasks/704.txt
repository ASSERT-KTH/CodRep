_format.setMethod( Method.XML );

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


import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.io.OutputStream;
import java.io.Writer;
import java.util.Enumeration;

import org.w3c.dom.*;
import org.xml.sax.DocumentHandler;
import org.xml.sax.ContentHandler;
import org.xml.sax.AttributeList;
import org.xml.sax.Attributes;


/**
 * Implements an XML serializer supporting both DOM and SAX pretty
 * serializing. For usage instructions see {@link Serializer}.
 * <p>
 * If an output stream is used, the encoding is taken from the
 * output format (defaults to <tt>UTF-8</tt>). If a writer is
 * used, make sure the writer uses the same encoding (if applies)
 * as specified in the output format.
 * <p>
 * The serializer supports both DOM and SAX. DOM serializing is done
 * by calling {@link #serialize} and SAX serializing is done by firing
 * SAX events and using the serializer as a document handler.
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
 *
 *
 * @version $Revision$ $Date$
 * @author <a href="mailto:arkin@exoffice.com">Assaf Arkin</a>
 * @see Serializer
 */
public final class XMLSerializer
    extends BaseMarkupSerializer
{


    /**
     * Constructs a new serializer. The serializer cannot be used without
     * calling {@link #setOutputCharStream} or {@link #setOutputByteStream}
     * first.
     */
    public XMLSerializer()
    {
        super( new OutputFormat( Method.XML, null, false ) );
    }


    /**
     * Constructs a new serializer. The serializer cannot be used without
     * calling {@link #setOutputCharStream} or {@link #setOutputByteStream}
     * first.
     */
    public XMLSerializer( OutputFormat format )
    {
        super( format != null ? format : new OutputFormat( Method.XML, null, false ) );
        format.setMethod( Method.XML );
    }


    /**
     * Constructs a new serializer that writes to the specified writer
     * using the specified output format. If <tt>format</tt> is null,
     * will use a default output format.
     *
     * @param writer The writer to use
     * @param format The output format to use, null for the default
     */
    public XMLSerializer( Writer writer, OutputFormat format )
    {
        super( format != null ? format : new OutputFormat( Method.XML, null, false ) );
        _format.setMethod( Method.XML );
        setOutputCharStream( writer );
    }


    /**
     * Constructs a new serializer that writes to the specified output
     * stream using the specified output format. If <tt>format</tt>
     * is null, will use a default output format.
     *
     * @param output The output stream to use
     * @param format The output format to use, null for the default
     */
    public XMLSerializer( OutputStream output, OutputFormat format )
    {
        super( format != null ? format : new OutputFormat( Method.XML, null, false ) );
        _format.setMethod( Method.XML );
        setOutputByteStream( output );
    }


    public void setOutputFormat( OutputFormat format )
    {
        super.setOutputFormat( format != null ? format : new OutputFormat( Method.XML, null, false ) );
    }


    //-----------------------------------------//
    // SAX content handler serializing methods //
    //-----------------------------------------//


    public void startElement( String namespaceURI, String localName,
                              String rawName, Attributes attrs )
    {
        int          i;
        boolean      preserveSpace;
        ElementState state;
        String       name;
        String       value;
        boolean      addNSAttr = false;

        if ( _printer == null )
            throw new IllegalStateException( "SER002 No writer supplied for serializer" );

        state = getElementState();
        if ( isDocumentState() ) {
            // If this is the root element handle it differently.
            // If the first root element in the document, serialize
            // the document's DOCTYPE. Space preserving defaults
            // to that of the output format.
            if ( ! _started )
                startDocument( localName == null ? rawName : localName );
        } else {
            // For any other element, if first in parent, then
            // close parent's opening tag and use the parnet's
            // space preserving.
            if ( state.empty )
                _printer.printText( '>' );
            // Must leave CData section first
            if ( state.inCData )
            {
                _printer.printText( "]]>" );
                state.inCData = false;
            }
            // Indent this element on a new line if the first
            // content of the parent element or immediately
            // following an element.
            if ( _indenting && ! state.preserveSpace &&
                 ( state.empty || state.afterElement ) )
                _printer.breakLine();
        }
        preserveSpace = state.preserveSpace;

        // Do not change the current element state yet.
        // This only happens in endElement().
        if ( rawName == null ) {
            rawName = localName;
            if ( namespaceURI != null ) {
                String prefix;
                prefix = getPrefix( namespaceURI );
                if ( prefix.length() > 0 )
                    rawName = prefix + ":" + localName;
            }
            addNSAttr = true;
        }

        _printer.printText( '<' );
        _printer.printText( rawName );
        _printer.indent();

        // For each attribute print it's name and value as one part,
        // separated with a space so the element can be broken on
        // multiple lines.
        if ( attrs != null ) {
            for ( i = 0 ; i < attrs.getLength() ; ++i ) {
                _printer.printSpace();

                name = attrs.getQName( i );
                if ( name == null ) {
                    String prefix;
                    String attrURI;

                    name = attrs.getLocalName( i );
                    attrURI = attrs.getURI( i );
                    if ( attrURI != null && ( namespaceURI == null ||
                                              ! attrURI.equals( namespaceURI ) ) ) {
                        prefix = getPrefix( attrURI );
                        if ( prefix != null && prefix.length() > 0 )
                            name = prefix + ":" + name;
                    }
                }

                value = attrs.getValue( i );
                if ( value == null )
                    value = "";
                _printer.printText( name );
                _printer.printText( "=\"" );
                printEscaped( value );
                _printer.printText( '"' );

                // If the attribute xml:space exists, determine whether
                // to preserve spaces in this and child nodes based on
                // its value.
                if ( name.equals( "xml:space" ) ) {
                    if ( value.equals( "preserve" ) )
                        preserveSpace = true;
                    else
                        preserveSpace = _format.getPreserveSpace();
                }
            }
        }

        if ( addNSAttr ) {
            Enumeration enum;

            enum = _prefixes.keys();
            while ( enum.hasMoreElements() ) {
                _printer.printSpace();
                value = (String) enum.nextElement();
                name = (String) _prefixes.get( value );
                if ( name.length() == 0 ) {
                    _printer.printText( "xmlns=\"" );
                    printEscaped( value );
                    _printer.printText( '"' );
                } else {
                    _printer.printText( "xmlns:" );
                    _printer.printText( name );
                    _printer.printText( "=\"" );
                    printEscaped( value );
                    _printer.printText( '"' );
                }
            }
        }

        // Now it's time to enter a new element state
        // with the tag name and space preserving.
        // We still do not change the curent element state.
        state = enterElementState( namespaceURI, localName, rawName, preserveSpace );
        state.doCData = _format.isCDataElement( namespaceURI == null ? rawName :
                                                namespaceURI + "^" + localName );
        state.unescaped = _format.isNonEscapingElement( namespaceURI == null ? rawName :
                                                        namespaceURI + "^" + localName );
    }


    public void endElement( String namespaceURI, String localName,
                            String rawName )
    {
        ElementState state;

        // Works much like content() with additions for closing
        // an element. Note the different checks for the closed
        // element's state and the parent element's state.
        _printer.unindent();
        state = getElementState();
        if ( state.empty ) {
            _printer.printText( "/>" );
        } else {
            // Must leave CData section first
            if ( state.inCData )
                _printer.printText( "]]>" );
            // This element is not empty and that last content was
            // another element, so print a line break before that
            // last element and this element's closing tag.
            if ( _indenting && ! state.preserveSpace && state.afterElement )
                _printer.breakLine();
            _printer.printText( "</" );
            _printer.printText( state.rawName );
            _printer.printText( '>' );
        }
        // Leave the element state and update that of the parent
        // (if we're not root) to not empty and after element.
        state = leaveElementState();
        state.afterElement = true;
        state.empty = false;
        if ( isDocumentState() )
            _printer.flush();
    }


    //------------------------------------------//
    // SAX document handler serializing methods //
    //------------------------------------------//


    public void startDocument()
    {
        if ( _printer == null )
            throw new IllegalStateException( "SER002 No writer supplied for serializer" );
        // Nothing to do here. All the magic happens in startDocument(String)
    }


    public void startElement( String tagName, AttributeList attrs )
    {
        int          i;
        boolean      preserveSpace;
        ElementState state;
        String       name;
        String       value;

        if ( _printer == null )
            throw new IllegalStateException( "SER002 No writer supplied for serializer" );

        state = getElementState();
        if ( isDocumentState() ) {
            // If this is the root element handle it differently.
            // If the first root element in the document, serialize
            // the document's DOCTYPE. Space preserving defaults
            // to that of the output format.
            if ( ! _started )
                startDocument( tagName );
        } else {
            // For any other element, if first in parent, then
            // close parent's opening tag and use the parnet's
            // space preserving.
            if ( state.empty )
                _printer.printText( '>' );
            // Must leave CData section first
            if ( state.inCData )
            {
                _printer.printText( "]]>" );
                state.inCData = false;
            }
            // Indent this element on a new line if the first
            // content of the parent element or immediately
            // following an element.
            if ( _indenting && ! state.preserveSpace &&
                 ( state.empty || state.afterElement ) )
                _printer.breakLine();
        }
        preserveSpace = state.preserveSpace;

        // Do not change the current element state yet.
        // This only happens in endElement().

        _printer.printText( '<' );
        _printer.printText( tagName );
        _printer.indent();

        // For each attribute print it's name and value as one part,
        // separated with a space so the element can be broken on
        // multiple lines.
        if ( attrs != null ) {
            for ( i = 0 ; i < attrs.getLength() ; ++i ) {
                _printer.printSpace();
                name = attrs.getName( i );
                value = attrs.getValue( i );
                if ( value != null ) {
                    _printer.printText( name );
                    _printer.printText( "=\"" );
                    printEscaped( value );
                    _printer.printText( '"' );
                }

                // If the attribute xml:space exists, determine whether
                // to preserve spaces in this and child nodes based on
                // its value.
                if ( name.equals( "xml:space" ) ) {
                    if ( value.equals( "preserve" ) )
                        preserveSpace = true;
                    else
                        preserveSpace = _format.getPreserveSpace();
                }
            }
        }
        // Now it's time to enter a new element state
        // with the tag name and space preserving.
        // We still do not change the curent element state.
        state = enterElementState( null, null, tagName, preserveSpace );
        state.doCData = _format.isCDataElement( tagName );
        state.unescaped = _format.isNonEscapingElement( tagName );
    }


    public void endElement( String tagName )
    {
        endElement( null, null, tagName );
    }



    //------------------------------------------//
    // Generic node serializing methods methods //
    //------------------------------------------//


    /**
     * Called to serialize the document's DOCTYPE by the root element.
     * The document type declaration must name the root element,
     * but the root element is only known when that element is serialized,
     * and not at the start of the document.
     * <p>
     * This method will check if it has not been called before ({@link #_started}),
     * will serialize the document type declaration, and will serialize all
     * pre-root comments and PIs that were accumulated in the document
     * (see {@link #serializePreRoot}). Pre-root will be serialized even if
     * this is not the first root element of the document.
     */
    protected void startDocument( String rootTagName )
    {
        int    i;
        String dtd;

        dtd = _printer.leaveDTD();
        if ( ! _started ) {

            if ( ! _format.getOmitXMLDeclaration() ) {
                StringBuffer    buffer;

                // Serialize the document declaration appreaing at the head
                // of very XML document (unless asked not to).
                buffer = new StringBuffer( "<?xml version=\"" );
                if ( _format.getVersion() != null )
                    buffer.append( _format.getVersion() );
                else
                    buffer.append( "1.0" );
                buffer.append( '"' );
                if ( _format.getEncoding() != null ) {
                    buffer.append( " encoding=\"" );
                    buffer.append( _format.getEncoding() );
                    buffer.append( '"' );
                }
                if ( _format.getStandalone() && _docTypeSystemId == null &&
                     _docTypePublicId == null )
                    buffer.append( " standalone=\"yes\"" );
                buffer.append( "?>" );
                _printer.printText( buffer );
                _printer.breakLine();
            }

            if ( _docTypeSystemId != null ) {
                // System identifier must be specified to print DOCTYPE.
                // If public identifier is specified print 'PUBLIC
                // <public> <system>', if not, print 'SYSTEM <system>'.
                _printer.printText( "<!DOCTYPE " );
                _printer.printText( rootTagName );
                if ( _docTypePublicId != null ) {
                    _printer.printText( " PUBLIC " );
                    printDoctypeURL( _docTypePublicId );
                    if ( _indenting ) {
                        _printer.breakLine();
                        for ( i = 0 ; i < 18 + rootTagName.length() ; ++i )
                            _printer.printText( " " );
                    } else
                        _printer.printText( " " );
                    printDoctypeURL( _docTypeSystemId );
                }
                else {
                    _printer.printText( " SYSTEM " );
                    printDoctypeURL( _docTypeSystemId );
                }

                // If we accumulated any DTD contents while printing.
                // this would be the place to print it.
                if ( dtd != null && dtd.length() > 0 ) {
                    _printer.printText( " [" );
                    printText( dtd, true, true );
                    _printer.printText( ']' );
                }

                _printer.printText( ">" );
                _printer.breakLine();
            } else if ( dtd != null && dtd.length() > 0 ) {
                _printer.printText( "<!DOCTYPE " );
                _printer.printText( rootTagName );
                _printer.printText( " [" );
                printText( dtd, true, true );
                _printer.printText( "]>" );
                _printer.breakLine();
            }
        }
        _started = true;
        // Always serialize these, even if not te first root element.
        serializePreRoot();
    }


    /**
     * Called to serialize a DOM element. Equivalent to calling {@link
     * #startElement}, {@link #endElement} and serializing everything
     * inbetween, but better optimized.
     */
    protected void serializeElement( Element elem )
    {
        Attr         attr;
        NamedNodeMap attrMap;
        int          i;
        Node         child;
        ElementState state;
        boolean      preserveSpace;
        String       name;
        String       value;
        String       tagName;

        tagName = elem.getTagName();
        state = getElementState();
        if ( isDocumentState() ) {
            // If this is the root element handle it differently.
            // If the first root element in the document, serialize
            // the document's DOCTYPE. Space preserving defaults
            // to that of the output format.
            if ( ! _started )
                startDocument( tagName );
        } else {
            // For any other element, if first in parent, then
            // close parent's opening tag and use the parnet's
            // space preserving.
            if ( state.empty )
                _printer.printText( '>' );
            // Must leave CData section first
            if ( state.inCData )
            {
                _printer.printText( "]]>" );
                state.inCData = false;
            }
            // Indent this element on a new line if the first
            // content of the parent element or immediately
            // following an element.
            if ( _indenting && ! state.preserveSpace &&
                 ( state.empty || state.afterElement ) )
                _printer.breakLine();
        }
        preserveSpace = state.preserveSpace;

        // Do not change the current element state yet.
        // This only happens in endElement().

        _printer.printText( '<' );
        _printer.printText( tagName );
        _printer.indent();

        // Lookup the element's attribute, but only print specified
        // attributes. (Unspecified attributes are derived from the DTD.
        // For each attribute print it's name and value as one part,
        // separated with a space so the element can be broken on
        // multiple lines.
        attrMap = elem.getAttributes();
        if ( attrMap != null ) {
            for ( i = 0 ; i < attrMap.getLength() ; ++i ) {
                attr = (Attr) attrMap.item( i );
                name = attr.getName();
                value = attr.getValue();
                if ( value == null )
                    value = "";
                if ( attr.getSpecified() ) {
                    _printer.printSpace();
                    _printer.printText( name );
                    _printer.printText( "=\"" );
                    printEscaped( value );
                    _printer.printText( '"' );
                }
                // If the attribute xml:space exists, determine whether
                // to preserve spaces in this and child nodes based on
                // its value.
                if ( name.equals( "xml:space" ) ) {
                    if ( value.equals( "preserve" ) )
                        preserveSpace = true;
                    else
                        preserveSpace = _format.getPreserveSpace();
                }
            }
        }

        // If element has children, then serialize them, otherwise
        // serialize en empty tag.
        if ( elem.hasChildNodes() ) {
            // Enter an element state, and serialize the children
            // one by one. Finally, end the element.
            state = enterElementState( null, null, tagName, preserveSpace );
            state.doCData = _format.isCDataElement( tagName );
            state.unescaped = _format.isNonEscapingElement( tagName );
            child = elem.getFirstChild();
            while ( child != null ) {
                serializeNode( child );
                child = child.getNextSibling();
            }
            endElement( tagName );
        } else {
            _printer.unindent();
            _printer.printText( "/>" );
            // After element but parent element is no longer empty.
            state.afterElement = true;
            state.empty = false;
            if ( isDocumentState() )
                _printer.flush();
        }
    }


    protected String getEntityRef( char ch )
    {
        // Encode special XML characters into the equivalent character references.
        // These five are defined by default for all XML documents.
        switch ( ch ) {
        case '<':
            return "lt";
        case '>':
            return "gt";
        case '"':
            return "quot";
        case '\'':
            return "apos";
        case '&':
            return "amp";
        }
        return null;
    }


}

