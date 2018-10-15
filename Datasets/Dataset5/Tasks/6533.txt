import org.apache.xerces.dom3.DOMConfiguration;

/*
 * Copyright (c) 2003 World Wide Web Consortium,
 *
 * (Massachusetts Institute of Technology, European Research Consortium for
 * Informatics and Mathematics, Keio University). All Rights Reserved. This
 * work is distributed under the W3C(r) Software License [1] in the hope that
 * it will be useful, but WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * [1] http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231
 */

package org.w3c.dom.ls;

import org.w3c.dom.Document;
import org.w3c.dom.DOMConfiguration;
import org.w3c.dom.Node;
import org.w3c.dom.DOMException;

/**
 *  An interface to an object that is able to build, or augment, a DOM tree 
 * from various input sources. 
 * <p> <code>DOMParser</code> provides an API for parsing XML and building the 
 * corresponding DOM document structure. A <code>DOMParser</code> instance 
 * can be obtained by invoking the 
 * <code>DOMImplementationLS.createDOMParser()</code> method. 
 * <p> As specified in [<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609'>DOM Level 3 Core</a>]
 * , when a document is first made available via the DOMParser: 
 * <ul>
 * <li> there is 
 * only one <code>Text</code> node for each block of text. The 
 * <code>Text</code> nodes are in "normal" form: only structure (e.g. 
 * elements, comments, processing instructions, CDATA sections, and entity 
 * references) separates <code>Text</code> nodes, i.e., there are neither 
 * adjacent nor empty <code>Text</code> nodes. 
 * </li>
 * <li> it is expected that the 
 * <code>value</code> and <code>nodeValue</code> attributes of an 
 * <code>Attr</code> node initially return the <a href='http://www.w3.org/TR/2000/REC-xml-20001006#AVNormalize'>XML 1.0 
 * normalized value</a>. However, if the parameters "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-validate-if-schema'>
 * validate-if-schema</a>" and "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-datatype-normalization'>
 * datatype-normalization</a>" are set to <code>true</code>, depending on the attribute normalization 
 * used, the attribute values may differ from the ones obtained by the XML 
 * 1.0 attribute normalization. If the parameters 
 * <code>data-type-normalization</code> is set to <code>false</code>, the 
 * XML 1.0 attribute normalization is guaranteed to occur, and if the 
 * attributes list does not contain namespace declarations, the 
 * <code>attributes</code> attribute on <code>Element</code> node represents 
 * the property <b>[attributes]</b> defined in [<a href='http://www.w3.org/TR/2001/REC-xml-infoset-20011024/'>XML Information set</a>]
 * . 
 * </li>
 * </ul>
 * <p> Asynchronous <code>DOMParser</code> objects are expected to also 
 * implement the <code>events::EventTarget</code> interface so that event 
 * listeners can be registered on asynchronous <code>DOMParser</code> 
 * objects. 
 * <p> Events supported by asynchronous <code>DOMParser</code> objects are: 
 * <dl>
 * <dt>
 * load</dt>
 * <dd> The <code>DOMParser</code> finishes to load the document. See also 
 * the definition of the <code>LSLoadEvent</code> interface. </dd>
 * <dt>progress</dt>
 * <dd> The 
 * <code>DOMParser</code> signals a progress as a document is parsed. See 
 * also the definition of the <code>LSProgressEvent</code> interface. </dd>
 * </dl>
 * <p ><b>Note:</b>  All events defined in this specification use the 
 * namespace URI <code>"http://www.w3.org/2002/DOMLS"</code>. 
 * <p> While parsing an input source, errors are reported to the application 
 * through the error handler (<code>DOMParser.config</code>'s "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-error-handler'>
 * error-handler</a>" parameter). This specification does in no way try to define all possible 
 * errors that can occur while parsing XML, or any other markup, but some 
 * common error cases are defined. The types (<code>DOMError.type</code>) of 
 * errors and warnings defined by this specification are: 
 * <dl>
 * <dt>
 * <code>"unsupported-media-type" [fatal]</code></dt>
 * <dd> Raised if the configuration 
 * parameter "supported-media-types-only" is set to <code>true</code> and an 
 * unsupported media type is encountered. </dd>
 * <dt>
 * <code>"unsupported-encoding" [fatal]</code></dt>
 * <dd> Raised if an unsupported 
 * encoding is encountered. </dd>
 * <dt><code>"doctype-not-allowed" [fatal]</code></dt>
 * <dd> 
 * Raised if the configuration parameter "disallow-doctype" is set to 
 * <code>true</code> and a doctype is encountered. </dd>
 * <dt>
 * <code>"unknown-character-denormalization" [fatal]</code></dt>
 * <dd> Raised if the 
 * configuration parameter "ignore-unknown-character-denormalizations" is 
 * set to <code>false</code> and a character is encountered for which the 
 * processor cannot determine the normalization properties. </dd>
 * <dt>
 * <code>"unbound-namespace-in-entity" [warning]</code></dt>
 * <dd> Raised if the 
 * configuration parameter "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-entities'>
 * entities</a>" is set to <code>true</code> and an unbound namespace prefix is 
 * encounterd in an entity declaration. </dd>
 * <dt>
 * <code>"pi-base-uri-not-preserved" [warning]</code></dt>
 * <dd> Raised if a processing 
 * instruction is encoutered in a location where the base URI of the 
 * processing instruction can not be preserved.  One example of a case where 
 * this warning will be raised is if the configuration parameter "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-entities'>
 * entities</a>" is set to <code>false</code> and the following XML file is parsed: 
 * <pre>
 * &lt;!DOCTYPE root [ &lt;!ENTITY e SYSTEM 'subdir/myentity.ent' ]&gt; 
 * &lt;root&gt; &amp;e; &lt;/root&gt;</pre>
 *  And <code>subdir/myentity.ent</code> 
 * looks like this: 
 * <pre>&lt;one&gt; &lt;two/&gt; &lt;/one&gt; &lt;?pi 
 * 3.14159?&gt; &lt;more/&gt;</pre>
 * </dd>
 * </dl> 
 * <p> In addition to raising the defined errors and warnings, implementations 
 * are expected to raise implementation specific errors and warnings for any 
 * other error and warning cases such as IO errors (file not found, 
 * permission denied,...), XML well-formedness errors, and so on. 
 * <p>See also the <a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-LS-20030619'>Document Object Model (DOM) Level 3 Load
and Save Specification</a>.
 */
public interface DOMParser {
    /**
     *  The <code>DOMConfiguration</code> object used when parsing an input 
     * source. This <code>DOMConfiguration</code> is specific to the parse 
     * operation and no parameter values from this 
     * <code>DOMConfiguration</code> object are passed automatically to the 
     * <code>DOMConfiguration</code> object on the <code>Document</code> 
     * that is created, or used, by the parse operation. The DOM application 
     * is responsible for passing any needed parameter values from this 
     * <code>DOMConfiguration</code> object to the 
     * <code>DOMConfiguration</code> object referenced by the 
     * <code>Document</code> object. 
     * <br> In addition to the parameters recognized in [<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609'>DOM Level 3 Core</a>]
     * , the <code>DOMConfiguration</code> objects for <code>DOMParser</code>
     *  adds or modifies the following parameters: 
     * <dl>
     * <dt>
     * <code>"charset-overrides-xml-encoding"</code></dt>
     * <dd>
     * <dl>
     * <dt><code>true</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) If a higher level protocol such as HTTP [<a href='http://www.ietf.org/rfc/rfc2616.txt'>IETF RFC 2616</a>] provides an 
     * indication of the character encoding of the input stream being 
     * processed, that will override any encoding specified in the XML 
     * declaration or the Text declaration (see also section 4.3.3, 
     * "Character Encoding in Entities", in [<a href='http://www.w3.org/TR/2000/REC-xml-20001006'>XML 1.0</a>]). 
     * Explicitly setting an encoding in the <code>DOMInput</code> overrides 
     * any encoding from the protocol. </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>required</em>] The parser ignores any character set encoding information from 
     * higher-level protocols. </dd>
     * </dl></dd>
     * <dt><code>"disallow-doctype"</code></dt>
     * <dd>
     * <dl>
     * <dt>
     * <code>true</code></dt>
     * <dd>[<em>optional</em>] Throw a fatal <b>"doctype-not-allowed"</b> error if a doctype node is found while parsing the document. This is 
     * useful when dealing with things like SOAP envelopes where doctype 
     * nodes are not allowed. </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) Allow doctype nodes in the document. </dd>
     * </dl></dd>
     * <dt>
     * <code>"ignore-unknown-character-denormalizations"</code></dt>
     * <dd>
     * <dl>
     * <dt>
     * <code>true</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) If, while verifying full normalization when [<a href='http://www.w3.org/TR/2002/CR-xml11-20021015/'>XML 1.1</a>] is 
     * supported, a processor encounters characters for which it cannot 
     * determine the normalization properties, then the processor will 
     * ignore any possible denormalizations caused by these characters.  
     * This parameter is ignored for [<a href='http://www.w3.org/TR/2000/REC-xml-20001006'>XML 1.0</a>]. </dd>
     * <dt>
     * <code>false</code></dt>
     * <dd>[<em>optional</em>] Report an fatal <b>"unknown-character-denormalization"</b> error if a character is encountered for which the processor cannot 
     * determine the normalization properties. </dd>
     * </dl></dd>
     * <dt><code>"infoset"</code></dt>
     * <dd> See 
     * the definition of <code>DOMConfiguration</code> for a description of 
     * this parameter. Unlike in [<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609'>DOM Level 3 Core</a>]
     * , this parameter will default to <code>true</code> for 
     * <code>DOMParser</code>. </dd>
     * <dt><code>"namespaces"</code></dt>
     * <dd>
     * <dl>
     * <dt><code>true</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) Perform the namespace processing as defined in [<a href='http://www.w3.org/TR/1999/REC-xml-names-19990114/'>XML Namespaces</a>]
     * . </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>optional</em>] Do not perform the namespace processing. </dd>
     * </dl></dd>
     * <dt>
     * <code>"supported-media-types-only"</code></dt>
     * <dd>
     * <dl>
     * <dt><code>true</code></dt>
     * <dd>[<em>optional</em>] Check that the media type of the parsed resource is a supported media 
     * type. If an unsupported media type is encountered, a fatal error of 
     * type <b>"unsupported-media-type"</b> will be raised. The media types defined in [<a href='http://www.ietf.org/rfc/rfc3023.txt'>IETF RFC 3023</a>] must always 
     * be accepted. </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) Accept any media type. </dd>
     * </dl></dd>
     * </dl>
     * <br> The parameter "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-well-formed'>
     * well-formed</a>" cannot be set to <code>false</code>. 
     */
    public DOMConfiguration getConfig();

    /**
     *  When a filter is provided, the implementation will call out to the 
     * filter as it is constructing the DOM tree structure. The filter can 
     * choose to remove elements from the document being constructed, or to 
     * terminate the parsing early. 
     * <br> The filter is invoked after the operations requested by the 
     * <code>DOMConfiguration</code> parameters have been applied. For 
     * example, if "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-validate'>
     * validate</a>" is set to <code>true</code>, the validation is done before invoking the 
     * filter. 
     */
    public DOMParserFilter getFilter();
    /**
     *  When a filter is provided, the implementation will call out to the 
     * filter as it is constructing the DOM tree structure. The filter can 
     * choose to remove elements from the document being constructed, or to 
     * terminate the parsing early. 
     * <br> The filter is invoked after the operations requested by the 
     * <code>DOMConfiguration</code> parameters have been applied. For 
     * example, if "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-validate'>
     * validate</a>" is set to <code>true</code>, the validation is done before invoking the 
     * filter. 
     */
    public void setFilter(DOMParserFilter filter);

    /**
     *  <code>true</code> if the <code>DOMParser</code> is asynchronous, 
     * <code>false</code> if it is synchronous. 
     */
    public boolean getAsync();

    /**
     *  <code>true</code> if the <code>DOMParser</code> is currently busy 
     * loading a document, otherwise <code>false</code>. 
     */
    public boolean getBusy();

    /**
     * Parse an XML document from a resource identified by a 
     * <code>DOMInput</code>.
     * @param is  The <code>DOMInput</code> from which the source of the 
     *   document is to be read. 
     * @return  If the <code>DOMParser</code> is a synchronous 
     *   <code>DOMParser</code>, the newly created and populated 
     *   <code>Document</code> is returned. If the <code>DOMParser</code> is 
     *   asynchronous, <code>null</code> is returned since the document 
     *   object may not yet be constructed when this method returns. 
     * @exception DOMException
     *    INVALID_STATE_ERR: Raised if the <code>DOMParser</code>'s 
     *   <code>DOMParser.busy</code> attribute is <code>true</code>. 
     */
    public Document parse(DOMInput is)
                          throws DOMException;

    /**
     *  Parse an XML document from a location identified by a URI reference [<a href='http://www.ietf.org/rfc/rfc2396.txt'>IETF RFC 2396</a>]. If the URI 
     * contains a fragment identifier (see section 4.1 in [<a href='http://www.ietf.org/rfc/rfc2396.txt'>IETF RFC 2396</a>]), the 
     * behavior is not defined by this specification, future versions of 
     * this specification may define the behavior. 
     * @param uri The location of the XML document to be read.
     * @return  If the <code>DOMParser</code> is a synchronous 
     *   <code>DOMParser</code>, the newly created and populated 
     *   <code>Document</code> is returned. If the <code>DOMParser</code> is 
     *   asynchronous, <code>null</code> is returned since the document 
     *   object may not yet be constructed when this method returns. 
     * @exception DOMException
     *    INVALID_STATE_ERR: Raised if the <code>DOMParser.busy</code> 
     *   attribute is <code>true</code>. 
     */
    public Document parseURI(String uri)
                             throws DOMException;

    // ACTION_TYPES
    /**
     *  Append the result of the parse operation as children of the context 
     * node. For this action to work, the context node must be an 
     * <code>Element</code> or a <code>DocumentFragment</code>. 
     */
    public static final short ACTION_APPEND_AS_CHILDREN = 1;
    /**
     *  Replace all the children of the context node with the result of the 
     * parse operation. For this action to work, the context node must be an 
     * <code>Element</code>, a <code>Document</code>, or a 
     * <code>DocumentFragment</code>. 
     */
    public static final short ACTION_REPLACE_CHILDREN   = 2;
    /**
     *  Insert the result of the parse operation as the immediately preceding 
     * sibling of the context node. For this action to work the context 
     * node's parent must be an <code>Element</code> or a 
     * <code>DocumentFragment</code>. 
     */
    public static final short ACTION_INSERT_BEFORE      = 3;
    /**
     *  Insert the result of the parse operation as the immediately following 
     * sibling of the context node. For this action to work the context 
     * node's parent must be an <code>Element</code> or a 
     * <code>DocumentFragment</code>. 
     */
    public static final short ACTION_INSERT_AFTER       = 4;
    /**
     *  Replace the context node with the result of the parse operation. For 
     * this action to work, the context node must have a parent, and the 
     * parent must be an <code>Element</code> or a 
     * <code>DocumentFragment</code>. 
     */
    public static final short ACTION_REPLACE            = 5;

    /**
     *  Parse an XML fragment from a resource identified by a 
     * <code>DOMInput</code> and insert the content into an existing 
     * document at the position specified with the <code>context</code> and 
     * <code>action</code> arguments. When parsing the input stream, the 
     * context node is used for resolving unbound namespace prefixes. The 
     * context node's <code>ownerDocument</code> node (or the node itself if 
     * the node of type <code>DOCUMENT_NODE</code>) is used to resolve 
     * default attributes and entity references. 
     * <br> As the new data is inserted into the document, at least one 
     * mutation event is fired per new immediate child or sibling of the 
     * context node. 
     * <br> If the context node is a <code>Document</code> node and the action 
     * is <code>ACTION_REPLACE_CHILDREN</code>, then the document that is 
     * passed as the context node will be changed such that it's 
     * <code>xmlEncoding</code>, <code>documentURI</code>, 
     * <code>xmlVersion</code>, <code>actualEncoding</code>, 
     * <code>xmlStandalone</code>, and all other such attributes are set to 
     * what they would be set to if the input source was parsed using 
     * <code>DOMParser.parse()</code>. 
     * <br> If the <code>DOMParser</code> is asynchronous then the insertion 
     * of the resulting DOM structure is atomic, e.g. the whole structure is 
     * inserted only once the whole input stream is completely parsed 
     * without errors. 
     * <br> If an error occurs while parsing, the caller is notified through 
     * the <code>ErrorHandler</code> instance associated with the "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-error-handler'>
     * error-handler</a>" parameter of the <code>DOMConfiguration</code>. 
     * <br> When calling <code>parseWithContext</code>, the values of the 
     * following configuration parameters will be ignored and their default 
     * values will always be used instead: "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-validate'>
     * validate</a>", "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-validate-if-schema'>
     * validate-if-schema</a>", and "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-whitespace-in-element-content'>
     * whitespace-in-element-content</a>". 
     * @param input  The <code>DOMInput</code> from which the source document 
     *   is to be read. The source document must be an XML fragment, i.e. 
     *   anything except a complete XML document (except in the case where 
     *   the context node of type <code>DOCUMENT_NODE</code>, and the action 
     *   is <code>ACTION_REPLACE_CHILDREN</code>), a DOCTYPE (internal 
     *   subset), entity declaration(s), notation declaration(s), or XML or 
     *   text declaration(s). 
     * @param context  The node that is used as the context for the data that 
     *   is being parsed. This node must be a <code>Document</code> node, a 
     *   <code>DocumentFragment</code> node, or a node of a type that is 
     *   allowed as a child of an <code>Element</code> node, e.g. it cannot 
     *   be an <code>Attribute</code> node. 
     * @param action  This parameter describes which action should be taken 
     *   between the new set of nodes being inserted and the existing 
     *   children of the context node. The set of possible actions is 
     *   defined in <code>ACTION_TYPES</code> above. 
     * @return  Return the node that is the result of the parse operation. If 
     *   the result is more than one top-level node, the first one is 
     *   returned. 
     * @exception DOMException
     *    NOT_SUPPORTED_ERR: Raised if the <code>DOMParser</code> doesn't 
     *   support this method. 
     *   <br> NO_MODIFICATION_ALLOWED_ERR: Raised if the context node is a 
     *   read only node.
     *   <br> INVALID_STATE_ERR: Raised if the <code>DOMParser.busy</code> 
     *   attribute is <code>true</code>. 
     */
    public Node parseWithContext(DOMInput input, 
                                 Node context, 
                                 short action)
                                 throws DOMException;

    /**
     *  Abort the loading of the document that is currently being loaded by 
     * the <code>DOMParser</code>. If the <code>DOMParser</code> is 
     * currently not busy, a call to this method does nothing. 
     */
    public void abort();

}