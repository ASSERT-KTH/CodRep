import org.apache.xerces.dom3.DOMErrorHandler;

/*
 * Copyright (c) 2002 World Wide Web Consortium,
 * (Massachusetts Institute of Technology, Institut National de
 * Recherche en Informatique et en Automatique, Keio University). All
 * Rights Reserved. This program is distributed under the W3C's Software
 * Intellectual Property License. This program is distributed in the
 * hope that it will be useful, but WITHOUT ANY WARRANTY; without even
 * the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.
 * See W3C License http://www.w3.org/Consortium/Legal/ for more details.
 */

package org.w3c.dom.ls;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.DOMException;
import org.w3c.dom.DOMErrorHandler;

/**
 * DOM Level 3 WD Experimental:
 * The DOM Level 3 specification is at the stage 
 * of Working Draft, which represents work in 
 * progress and thus may be updated, replaced, 
 * or obsoleted by other documents at any time. 
 * <p>
 * A interface to an object that is able to build a DOM tree from various 
 * input sources.
 * <p><code>DOMBuilder</code> provides an API for parsing XML documents and 
 * building the corresponding DOM document tree. A <code>DOMBuilder</code> 
 * instance is obtained from the <code>DOMImplementationLS</code> interface 
 * by invoking its <code>createDOMBuilder</code>method.
 * <p> As specified in , when a document is first made available via the 
 * DOMBuilder: there is only one <code>Text</code> node for each block of 
 * text. The <code>Text</code> nodes are into "normal" form: only structure 
 * (e.g., elements, comments, processing instructions, CDATA sections, and 
 * entity references) separates <code>Text</code> nodes, i.e., there are 
 * neither adjacent <code>Text</code> nodes nor empty <code>Text</code> 
 * nodes.  it is expected that the <code>value</code> and 
 * <code>nodeValue</code> attributes of an <code>Attr</code> node initially 
 * return the XML 1.0 normalized value. However, if the features 
 * <code>validate-if-schema</code> and <code>datatype-normalization</code> 
 * are set to <code>true</code>, depending on the attribute normalization 
 * used, the attribute values may differ from the ones obtained by the XML 
 * 1.0 attribute normalization. If the feature 
 * <code>datatype-normalization</code> is not set to <code>true</code>, the 
 * XML 1.0 attribute normalization is guaranteed to occur, and if attributes 
 * list does not contain namespace declarations, the <code>attributes</code> 
 * attribute on <code>Element</code> node represents the property 
 * [attributes] defined in  .  XML Schemas does not modify the XML attribute 
 * normalization but represents their normalized value in an other 
 * information item property: [schema normalized value]XML Schema 
 * normalization only occurs if <code>datatype-normalization</code> is set 
 * to <code>true</code>.
 * <p> Asynchronous <code>DOMBuilder</code> objects are expected to also 
 * implement the <code>events::EventTarget</code> interface so that event 
 * listeners can be registerd on asynchronous <code>DOMBuilder</code> 
 * objects. 
 * <p> Events supported by asynchronous <code>DOMBuilder</code> are: load: The 
 * document that's being loaded is completely parsed, see the definition of 
 * <code>LSLoadEvent</code>progress: Progress notification, see the 
 * definition of <code>LSProgressEvent</code> All events defined in this 
 * specification use the namespace URI 
 * <code>"http://www.w3.org/2002/DOMLS"</code>. 
 * <p> <code>DOMBuilder</code>s have a number of named features that can be 
 * queried or set. The name of <code>DOMBuilder</code> features must be 
 * valid XML names. Implementation specific features (extensions) should 
 * choose a implementation specific prefix to avoid name collisions. 
 * <p> Even if all features must be recognized by all implementations, being 
 * able to set a state (<code>true</code> or <code>false</code>) is not 
 * always required. The following list of recognized features indicates the 
 * definitions of each feature state, if setting the state to 
 * <code>true</code> or <code>false</code> must be supported or is optional 
 * and, which state is the default one: 
 * <dl>
 * <dt><code>"cdata-sections"</code></dt>
 * <dd> This 
 * feature is equivalent to the one provided on 
 * <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt><code>"comments"</code></dt>
 * <dd>
 *  This feature is equivalent to the one provided on 
 * <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"charset-overrides-xml-encoding"</code></dt>
 * <dd>
 * <dl>
 * <dt><code>true</code></dt>
 * <dd>[required] (
 * default) If a higher level protocol such as HTTP  provides an indication 
 * of the character encoding of the input stream being processed, that will 
 * override any encoding specified in the XML declaration or the Text 
 * declaration (see also  4.3.3 "Character Encoding in Entities"). 
 * Explicitly setting an encoding in the <code>DOMInputSource</code> 
 * overrides encodings from the protocol. </dd>
 * <dt><code>false</code></dt>
 * <dd>[required] Any 
 * character set encoding information from higher level protocols is ignored 
 * by the parser. </dd>
 * </dl></dd>
 * <dt><code>"datatype-normalization"</code></dt>
 * <dd> This feature is 
 * equivalent to the one provided on 
 * <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt><code>"entities"</code></dt>
 * <dd>
 *  This feature is equivalent to the one provided on 
 * <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"canonical-form"</code></dt>
 * <dd> This feature is equivalent to the one 
 * provided on <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"infoset"</code></dt>
 * <dd> This feature is equivalent to the one provided on 
 * <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"namespaces"</code></dt>
 * <dd> This feature is equivalent to the one provided 
 * on <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"namespace-declarations"</code></dt>
 * <dd> This feature is equivalent to the 
 * one provided on <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"supported-mediatypes-only"</code></dt>
 * <dd>
 * <dl>
 * <dt><code>true</code></dt>
 * <dd>[optional] Check 
 * that the media type of the parsed resource is a supported media type and 
 * call the error handler if an unsupported media type is encountered. The 
 * media types defined in  must be accepted. </dd>
 * <dt><code>false</code></dt>
 * <dd>[required] (
 * default) Don't check the media type, accept any type of data. </dd>
 * </dl></dd>
 * <dt>
 * <code>"validate-if-schema"</code></dt>
 * <dd> This feature is equivalent to the one 
 * provided on <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"validation"</code></dt>
 * <dd> This feature is equivalent to the one provided 
 * on <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"whitespace-in-element-content"</code></dt>
 * <dd> This feature is equivalent 
 * to the one provided on <code>Document.setNormalizationFeature</code> in . </dd>
 * </dl>
 * <p>See also the <a href='http://www.w3.org/TR/2002/WD-DOM-Level-3-ASLS-20020409'>Document Object Model (DOM) Level 3 Abstract Schemas and Load
and Save Specification</a>.
 */
public interface DOMBuilder {
    /**
     * If a <code>DOMEntityResolver</code> has been specified, each time a 
     * reference to an external entity is encountered the 
     * <code>DOMBuilder</code> will pass the public and system IDs to the 
     * entity resolver, which can then specify the actual source of the 
     * entity.
     */
    public DOMEntityResolver getEntityResolver();
    /**
     * If a <code>DOMEntityResolver</code> has been specified, each time a 
     * reference to an external entity is encountered the 
     * <code>DOMBuilder</code> will pass the public and system IDs to the 
     * entity resolver, which can then specify the actual source of the 
     * entity.
     */
    public void setEntityResolver(DOMEntityResolver entityResolver);

    /**
     *  In the event that an error is encountered in the XML document being 
     * parsed, the <code>DOMDocumentBuilder</code> will call back to the 
     * <code>errorHandler</code> with the error information. When the 
     * document loading process calls the error handler the node closest to 
     * where the error occured is passed to the error handler, if the 
     * implementation is unable to pass the node where the error occures the 
     * document Node is passed to the error handler. In addition to passing 
     * the Node closest to to where the error occured, the implementation 
     * should also pass any other valuable information to the error handler, 
     * such as file name, line number, and so on. Mutations to the document 
     * from within an error handler will result in implementation dependent 
     * behavour. 
     */
    public DOMErrorHandler getErrorHandler();
    /**
     *  In the event that an error is encountered in the XML document being 
     * parsed, the <code>DOMDocumentBuilder</code> will call back to the 
     * <code>errorHandler</code> with the error information. When the 
     * document loading process calls the error handler the node closest to 
     * where the error occured is passed to the error handler, if the 
     * implementation is unable to pass the node where the error occures the 
     * document Node is passed to the error handler. In addition to passing 
     * the Node closest to to where the error occured, the implementation 
     * should also pass any other valuable information to the error handler, 
     * such as file name, line number, and so on. Mutations to the document 
     * from within an error handler will result in implementation dependent 
     * behavour. 
     */
    public void setErrorHandler(DOMErrorHandler errorHandler);

    /**
     *  When the application provides a filter, the parser will call out to 
     * the filter at the completion of the construction of each 
     * <code>Element</code> node. The filter implementation can choose to 
     * remove the element from the document being constructed (unless the 
     * element is the document element) or to terminate the parse early. If 
     * the document is being validated when it's loaded the validation 
     * happens before the filter is called. 
     */
    public DOMBuilderFilter getFilter();
    /**
     *  When the application provides a filter, the parser will call out to 
     * the filter at the completion of the construction of each 
     * <code>Element</code> node. The filter implementation can choose to 
     * remove the element from the document being constructed (unless the 
     * element is the document element) or to terminate the parse early. If 
     * the document is being validated when it's loaded the validation 
     * happens before the filter is called. 
     */
    public void setFilter(DOMBuilderFilter filter);

    /**
     * Set the state of a feature.
     * <br>The feature name has the same form as a DOM hasFeature string.
     * <br>It is possible for a <code>DOMBuilder</code> to recognize a feature 
     * name but to be unable to set its value.
     * @param name The feature name.
     * @param state The requested state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @exception DOMException
     *   NOT_SUPPORTED_ERR: Raised when the <code>DOMBuilder</code> recognizes 
     *   the feature name but cannot set the requested value. 
     *   <br>NOT_FOUND_ERR: Raised when the <code>DOMBuilder</code> does not 
     *   recognize the feature name.
     */
    public void setFeature(String name, 
                           boolean state)
                           throws DOMException;

    /**
     * Query whether setting a feature to a specific value is supported.
     * <br>The feature name has the same form as a DOM hasFeature string.
     * @param name The feature name, which is a DOM has-feature style string.
     * @param state The requested state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @return <code>true</code> if the feature could be successfully set to 
     *   the specified value, or <code>false</code> if the feature is not 
     *   recognized or the requested value is not supported. The value of 
     *   the feature itself is not changed.
     */
    public boolean canSetFeature(String name, 
                                 boolean state);

    /**
     * Look up the value of a feature.
     * <br>The feature name has the same form as a DOM hasFeature string
     * @param name The feature name, which is a string with DOM has-feature 
     *   syntax.
     * @return The current state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @exception DOMException
     *   NOT_FOUND_ERR: Raised when the <code>DOMBuilder</code> does not 
     *   recognize the feature name.
     */
    public boolean getFeature(String name)
                              throws DOMException;

    /**
     *  Parse an XML document from a location identified by a URI reference . 
     * If the URI contains a fragment identifier (see section 4.1 in ), the 
     * behavior is not defined by this specification, but future versions of 
     * this specification might define the behavior. 
     * @param uri The location of the XML document to be read.
     * @return If the <code>DOMBuilder</code> is a synchronous 
     *   <code>DOMBuilder</code> the newly created and populated 
     *   <code>Document</code> is returned. If the <code>DOMBuilder</code> 
     *   is asynchronous then <code>null</code> is returned since the 
     *   document object is not yet parsed when this method returns.
     */
    public Document parseURI(String uri);

    /**
     * Parse an XML document from a resource identified by a 
     * <code>DOMInputSource</code>.
     * @param is The <code>DOMInputSource</code> from which the source 
     *   document is to be read. 
     * @return If the <code>DOMBuilder</code> is a synchronous 
     *   <code>DOMBuilder</code> the newly created and populated 
     *   <code>Document</code> is returned. If the <code>DOMBuilder</code> 
     *   is asynchronous then <code>null</code> is returned since the 
     *   document object is not yet parsed when this method returns.
     * @exception DOMSystemException
     *   Exceptions raised by <code>parse</code> originate with the installed 
     *   ErrorHandler, and thus depend on the implementation of the 
     *   <code>DOMErrorHandler</code> interfaces. The default ErrorHandlers 
     *   will raise a <code>DOMSystemException</code> if any form I/O or 
     *   other system error occurs during the parse, but application defined 
     *   ErrorHandlers are not required to do so. 
     */
    public Document parse(DOMInputSource is)
                          throws Exception;

    // ACTION_TYPES
    /**
     * Replace the context node with the result of parsing the input source. 
     * For this action to work the context node must have a parent and the 
     * context node must be an <code>Element</code>, <code>Text</code>, 
     * <code>CDATASection</code>, <code>Comment</code>, 
     * <code>ProcessingInstruction</code>, or <code>EntityReference</code> 
     * node.
     */
    public static final short ACTION_REPLACE            = 1;
    /**
     * Append the result of the input source as children of the context node. 
     * For this action to work, the context node must be an 
     * <code>Element</code> or a <code>DocumentFragment</code>.
     */
    public static final short ACTION_APPEND_AS_CHILDREN = 2;
    /**
     * Insert the result of parsing the input source after the context node. 
     * For this action to work the context nodes parent must be an 
     * <code>Element</code>.
     */
    public static final short ACTION_INSERT_AFTER       = 3;
    /**
     * Insert the result of parsing the input source before the context node. 
     * For this action to work the context nodes parent must be an 
     * <code>Element</code>.
     */
    public static final short ACTION_INSERT_BEFORE      = 4;

    /**
     *  Parse an XML document or fragment from a resource identified by a 
     * <code>DOMInputSource</code> and insert the content into an existing 
     * document at the position specified with the <code>contextNode</code> 
     * and <code>action</code> arguments. When parsing the input stream the 
     * context node is used for resolving unbound namespace prefixes. 
     * <br> As the new data is inserted into the document at least one 
     * mutation event is fired per immidate child (or sibling) of context 
     * node. 
     * <br> If an error occurs while parsing, the caller is notified through 
     * the error handler. 
     * @param is  The <code>DOMInputSource</code> from which the source 
     *   document is to be read. 
     * @param cnode  The node that is used as the context for the data that 
     *   is being parsed. This node must be a <code>Document</code> node, a 
     *   <code>DocumentFragment</code> node, or a node of a type that is 
     *   allowed as a child of an element, e.g. it can not be an attribute 
     *   node. 
     * @param action This parameter describes which action should be taken 
     *   between the new set of node being inserted and the existing 
     *   children of the context node. The set of possible actions is 
     *   defined above.
     * @exception DOMException
     *   NOT_SUPPORTED_ERR: Raised when the <code>DOMBuilder</code> doesn't 
     *   support this method.
     *   <br>NO_MODIFICATION_ALLOWED_ERR: Raised if the context node is 
     *   readonly.
     */
    public void parseWithContext(DOMInputSource is, 
                                 Node cnode, 
                                 short action)
                                 throws DOMException;

}