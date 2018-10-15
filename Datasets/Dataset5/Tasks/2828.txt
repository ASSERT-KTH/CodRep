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
 *  <code>DOMWriter</code> provides an API for serializing (writing) a DOM 
 * document out in an XML document. The XML data is written to an output 
 * stream, the type of which depends on the specific language bindings in 
 * use. 
 * <p> During serialization of XML data, namespace fixup is done when 
 * possible.  allows empty strings as a real namespace URI. If the 
 * <code>namespaceURI</code> of a <code>Node</code> is empty string, the 
 * serialization will treat them as <code>null</code>, ignoring the prefix 
 * if any. 
 * <p> <code>DOMWriter</code> accepts any node type for serialization. For 
 * nodes of type <code>Document</code> or <code>Entity</code>, well formed 
 * XML will be created if possible. The serialized output for these node 
 * types is either as a Document or an External Entity, respectively, and is 
 * acceptable input for an XML parser. For all other types of nodes the 
 * serialized form is not specified, but should be something useful to a 
 * human for debugging or diagnostic purposes. Note: rigorously designing an 
 * external (source) form for stand-alone node types that don't already have 
 * one defined in  seems a bit much to take on here. 
 * <p>Within a Document, DocumentFragment, or Entity being serialized, Nodes 
 * are processed as follows Documents are written including an XML 
 * declaration and a DTD subset, if one exists in the DOM. Writing a 
 * document node serializes the entire document. Entity nodes, when written 
 * directly by <code>writeNode</code> defined in the <code>DOMWriter</code> 
 * interface, output the entity expansion but no namespace fixup is done. 
 * The resulting output will be valid as an external entity.  Entity 
 * reference nodes are serialized as an entity reference of the form "
 * <code>&amp;entityName;</code>" in the output. Child nodes (the expansion) 
 * of the entity reference are ignored.  CDATA sections containing content 
 * characters that can not be represented in the specified output encoding 
 * are handled according to the "split-cdata-sections" feature.If the 
 * feature is <code>true</code>, CDATA sections are split, and the 
 * unrepresentable characters are serialized as numeric character references 
 * in ordinary content. The exact position and number of splits is not 
 * specified. If the feature is <code>false</code>, unrepresentable 
 * characters in a CDATA section are reported as errors. The error is not 
 * recoverable - there is no mechanism for supplying alternative characters 
 * and continuing with the serialization. DocumentFragment nodes are 
 * serialized by serializing the children of the document fragment in the 
 * order they appear in the document fragment.  All other node types 
 * (Element, Text, etc.) are serialized to their corresponding XML source 
 * form.  The serialization of a DOM Node does not always generate a 
 * well-formed XML document, i.e. a <code>DOMBuilder</code> might through 
 * fatal errors when parsing the resulting serialization. 
 * <p> Within the character data of a document (outside of markup), any 
 * characters that cannot be represented directly are replaced with 
 * character references. Occurrences of '&lt;' and '&amp;' are replaced by 
 * the predefined entities &amp;lt; and &amp;amp. The other predefined 
 * entities (&amp;gt, &amp;apos, etc.) are not used; these characters can be 
 * included directly. Any character that can not be represented directly in 
 * the output character encoding is serialized as a numeric character 
 * reference. 
 * <p> Attributes not containing quotes are serialized in quotes. Attributes 
 * containing quotes but no apostrophes are serialized in apostrophes 
 * (single quotes). Attributes containing both forms of quotes are 
 * serialized in quotes, with quotes within the value represented by the 
 * predefined entity &amp;quot;. Any character that can not be represented 
 * directly in the output character encoding is serialized as a numeric 
 * character reference. 
 * <p> Within markup, but outside of attributes, any occurrence of a character 
 * that cannot be represented in the output character encoding is reported 
 * as an error. An example would be serializing the element 
 * &lt;LaCañada/&gt; with the encoding="us-ascii". 
 * <p> When requested by setting the <code>normalize-characters</code> feature 
 * on <code>DOMWriter</code>, all data to be serialized, both markup and 
 * character data, is W3C Text normalized according to the rules defined in 
 * . The W3C Text normalization process affects only the data as it is being 
 * written; it does not alter the DOM's view of the document after 
 * serialization has completed. 
 * <p>Namespaces are fixed up during serialization, the serialization process 
 * will verify that namespace declarations, namespace prefixes and the 
 * namespace URIs associated with Elements and Attributes are consistent. If 
 * inconsistencies are found, the serialized form of the document will be 
 * altered to remove them. The algorithm used for doing the namespace fixup 
 * while serializing a document is a combination of the algorithms used for 
 * lookupNamespaceURI and lookupNamespacePrefix . previous paragraph to be 
 * defined closer here.
 * <p>Any changes made affect only the namespace prefixes and declarations 
 * appearing in the serialized data. The DOM's view of the document is not 
 * altered by the serialization operation, and does not reflect any changes 
 * made to namespace declarations or prefixes in the serialized output. 
 * <p> While serializing a document the serializer will write out 
 * non-specified values (such as attributes whose <code>specified</code> is 
 * <code>false</code>) if the <code>discard-default-content</code> feature 
 * is set to <code>true</code>. If the <code>discard-default-content</code> 
 * flag is set to <code>false</code> and a schema is used for validation, 
 * the schema will be also used to determine if a value is specified or not. 
 * If no schema is used, the <code>specified</code> flag on attribute nodes 
 * is used to determine if attribute values should be written out. 
 * <p> Ref to Core spec (1.1.9, XML namespaces, 5th paragraph) entity ref 
 * description about warning about unbound entity refs. Entity refs are 
 * always serialized as <code>&amp;foo;</code>, also mention this in the 
 * load part of this spec. 
 * <p> <code>DOMWriter</code>s have a number of named features that can be 
 * queried or set. The name of <code>DOMWriter</code> features must be valid 
 * XML names. Implementation specific features (extensions) should choose an 
 * implementation dependent prefix to avoid name collisions. 
 * <p>Here is a list of features that must be recognized by all 
 * implementations.  Using these features does affect the <code>Node</code> 
 * being serialized, only its serialized form is affected.
 * <dl>
 * <dt>
 * <code>"discard-default-content"</code></dt>
 * <dd> This feature is equivalent to the 
 * one provided on <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"entities"</code></dt>
 * <dd> This feature is equivalent to the one provided on 
 * <code>Document.setNormalizationFeature</code> in . </dd>
 * <dt>
 * <code>"canonical-form"</code></dt>
 * <dd>
 * <dl>
 * <dt><code>true</code></dt>
 * <dd>[optional] This formatting 
 * writes the document according to the rules specified in . Setting this 
 * feature to true will set the feature <code>"format-pretty-print"</code> 
 * to false. </dd>
 * <dt><code>false</code></dt>
 * <dd>[required] (default) Do not canonicalize the 
 * output. </dd>
 * </dl></dd>
 * <dt><code>"format-pretty-print"</code></dt>
 * <dd>
 * <dl>
 * <dt><code>true</code></dt>
 * <dd>[optional] 
 * Formatting the output by adding whitespace to produce a pretty-printed, 
 * indented, human-readable form. The exact form of the transformations is 
 * not specified by this specification. Setting this feature to true will 
 * set the feature "canonical-form" to false. </dd>
 * <dt><code>false</code></dt>
 * <dd>[required] (
 * default) Don't pretty-print the result. </dd>
 * </dl></dd>
 * <dt>
 * <code>"normalize-characters"</code></dt>
 * <dd> This feature is equivalent to the one 
 * provided on <code>Document.setNormalizationFeature</code> in . Unlike in 
 * the Core, the default value for this feature is <code>true</code>. </dd>
 * <dt>
 * <code>"split-cdata-sections"</code></dt>
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
public interface DOMWriter {
    /**
     * Set the state of a feature.
     * <br>The feature name has the same form as a DOM hasFeature string.
     * <br>It is possible for a <code>DOMWriter</code> to recognize a feature 
     * name but to be unable to set its value.
     * @param name The feature name.
     * @param state The requested state of the feature (<code>true</code> or 
     *   <code>false</code>).
     * @exception DOMException
     *   NOT_SUPPORTED_ERR: Raised when the <code>DOMWriter</code> recognizes 
     *   the feature name but cannot set the requested value. 
     *   <br>Raise a NOT_FOUND_ERR When the <code>DOMWriter</code> does not 
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
     *   NOT_FOUND_ERR: Raised when the <code>DOMWriter</code> does not 
     *   recognize the feature name.
     */
    public boolean getFeature(String name)
                              throws DOMException;

    /**
     *  The character encoding in which the output will be written. 
     * <br> The encoding to use when writing is determined as follows: If the 
     * encoding attribute has been set, that value will be used.If the 
     * encoding attribute is <code>null</code> or empty, but the item to be 
     * written, or the owner document of the item, specifies an encoding 
     * (i.e. the "actualEncoding" from the document) specified encoding, 
     * that value will be used.If neither of the above provides an encoding 
     * name, a default encoding of "UTF-8" will be used.
     * <br>The default value is <code>null</code>.
     */
    public String getEncoding();
    /**
     *  The character encoding in which the output will be written. 
     * <br> The encoding to use when writing is determined as follows: If the 
     * encoding attribute has been set, that value will be used.If the 
     * encoding attribute is <code>null</code> or empty, but the item to be 
     * written, or the owner document of the item, specifies an encoding 
     * (i.e. the "actualEncoding" from the document) specified encoding, 
     * that value will be used.If neither of the above provides an encoding 
     * name, a default encoding of "UTF-8" will be used.
     * <br>The default value is <code>null</code>.
     */
    public void setEncoding(String encoding);

    /**
     *  The end-of-line sequence of characters to be used in the XML being 
     * written out. Any string is supported, but these are the recommended 
     * end-of-line sequences (using other character sequences than these 
     * recommended ones can result in a document that is either not 
     * serializable or not well-formed): 
     * <dl>
     * <dt><code>null</code></dt>
     * <dd> Use a default 
     * end-of-line sequence. DOM implementations should choose the default 
     * to match the usual convention for text files in the environment being 
     * used. Implementations must choose a default sequence that matches one 
     * of those allowed by  2.11 "End-of-Line Handling". </dd>
     * <dt>CR</dt>
     * <dd>The 
     * carriage-return character (#xD).</dd>
     * <dt>CR-LF</dt>
     * <dd> The carriage-return and 
     * line-feed characters (#xD #xA). </dd>
     * <dt>LF</dt>
     * <dd> The line-feed character (#xA). </dd>
     * </dl>
     * <br>The default value for this attribute is <code>null</code>.
     */
    public String getNewLine();
    /**
     *  The end-of-line sequence of characters to be used in the XML being 
     * written out. Any string is supported, but these are the recommended 
     * end-of-line sequences (using other character sequences than these 
     * recommended ones can result in a document that is either not 
     * serializable or not well-formed): 
     * <dl>
     * <dt><code>null</code></dt>
     * <dd> Use a default 
     * end-of-line sequence. DOM implementations should choose the default 
     * to match the usual convention for text files in the environment being 
     * used. Implementations must choose a default sequence that matches one 
     * of those allowed by  2.11 "End-of-Line Handling". </dd>
     * <dt>CR</dt>
     * <dd>The 
     * carriage-return character (#xD).</dd>
     * <dt>CR-LF</dt>
     * <dd> The carriage-return and 
     * line-feed characters (#xD #xA). </dd>
     * <dt>LF</dt>
     * <dd> The line-feed character (#xA). </dd>
     * </dl>
     * <br>The default value for this attribute is <code>null</code>.
     */
    public void setNewLine(String newLine);

    /**
     *  When the application provides a filter, the serializer will call out 
     * to the filter before serializing each Node. Attribute nodes are never 
     * passed to the filter. The filter implementation can choose to remove 
     * the node from the stream or to terminate the serialization early. 
     */
    public DOMWriterFilter getFilter();
    /**
     *  When the application provides a filter, the serializer will call out 
     * to the filter before serializing each Node. Attribute nodes are never 
     * passed to the filter. The filter implementation can choose to remove 
     * the node from the stream or to terminate the serialization early. 
     */
    public void setFilter(DOMWriterFilter filter);

    /**
     *  The error handler that will receive error notifications during 
     * serialization. The node where the error occured is passed to this 
     * error handler, any modification to nodes from within an error 
     * callback should be avoided since this will result in undefined, 
     * implementation dependent behavior. 
     */
    public DOMErrorHandler getErrorHandler();
    /**
     *  The error handler that will receive error notifications during 
     * serialization. The node where the error occured is passed to this 
     * error handler, any modification to nodes from within an error 
     * callback should be avoided since this will result in undefined, 
     * implementation dependent behavior. 
     */
    public void setErrorHandler(DOMErrorHandler errorHandler);

    /**
     * Write out the specified node as described above in the description of 
     * <code>DOMWriter</code>. Writing a Document or Entity node produces a 
     * serialized form that is well formed XML, when possible (Entity nodes 
     * might not always be well formed XML in themselves). Writing other 
     * node types produces a fragment of text in a form that is not fully 
     * defined by this document, but that should be useful to a human for 
     * debugging or diagnostic purposes. 
     * <br> If the specified encoding is not supported the error handler is 
     * called and the serialization is interrupted. 
     * @param destination The destination for the data to be written.
     * @param wnode The <code>Document</code> or <code>Entity</code> node to 
     *   be written. For other node types, something sensible should be 
     *   written, but the exact serialized form is not specified.
     * @return  Returns <code>true</code> if <code>node</code> was 
     *   successfully serialized and <code>false</code> in case a failure 
     *   occured and the failure wasn't canceled by the error handler. 
     * @exception DOMSystemException
     *   This exception will be raised in response to any sort of IO or system 
     *   error that occurs while writing to the destination. It may wrap an 
     *   underlying system exception.
     */
    public boolean writeNode(java.io.OutputStream destination, 
                             Node wnode)
                             throws Exception;

    /**
     *  Serialize the specified node as described above in the description of 
     * <code>DOMWriter</code>. The result of serializing the node is 
     * returned as a DOMString (this method completely ignores all the 
     * encoding information avaliable). Writing a Document or Entity node 
     * produces a serialized form that is well formed XML. Writing other 
     * node types produces a fragment of text in a form that is not fully 
     * defined by this document, but that should be useful to a human for 
     * debugging or diagnostic purposes. 
     * <br> Error handler is called if encoding not supported... 
     * @param wnode  The node to be written. 
     * @return  Returns the serialized data, or <code>null</code> in case a 
     *   failure occured and the failure wasn't canceled by the error 
     *   handler. 
     * @exception DOMException
     *    DOMSTRING_SIZE_ERR: Raised if the resulting string is too long to 
     *   fit in a <code>DOMString</code>. 
     */
    public String writeToString(Node wnode)
                                throws DOMException;

}