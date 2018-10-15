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

import org.w3c.dom.DOMConfiguration;
import org.w3c.dom.Node;
import org.w3c.dom.DOMException;

/**
 *  <code>DOMSerializer</code> provides an API for serializing (writing) a DOM 
 * document out into XML. The XML data is written to a string or an output 
 * stream. 
 * <p> During serialization of XML data, namespace fixup is done as defined in [<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609'>DOM Level 3 Core</a>]
 * , Appendix B. [<a href='http://www.w3.org/TR/2000/REC-DOM-Level-2-Core-20001113'>DOM Level 2 Core</a>]
 *  allows empty strings as a real namespace URI. If the 
 * <code>namespaceURI</code> of a <code>Node</code> is empty string, the 
 * serialization will treat them as <code>null</code>, ignoring the prefix 
 * if any. 
 * <p> <code>DOMSerializer</code> accepts any node type for serialization. For 
 * nodes of type <code>Document</code> or <code>Entity</code>, well-formed 
 * XML will be created when possible (well-formedness is guaranteed if the 
 * document or entity comes from a parse operation and is unchanged since it 
 * was created). The serialized output for these node types is either as a 
 * XML document or an External XML Entity, respectively, and is acceptable 
 * input for an XML parser. For all other types of nodes the serialized form 
 * is not specified, but should be something useful to a human for debugging 
 * or diagnostic purposes. 
 * <p>Within a <code>Document</code>, <code>DocumentFragment</code>, or 
 * <code>Entity</code> being serialized, <code>Nodes</code> are processed as 
 * follows
 * <ul>
 * <li> <code>Document</code> nodes are written, including the XML 
 * declaration (unless the parameter "xml-declaration" is set to 
 * <code>false</code>) and a DTD subset, if one exists in the DOM. Writing a 
 * <code>Document</code> node serializes the entire document. 
 * </li>
 * <li> 
 * <code>Entity</code> nodes, when written directly by 
 * <code>DOMSerializer.write</code>, outputs the entity expansion but no 
 * namespace fixup is done. The resulting output will be valid as an 
 * external entity. 
 * </li>
 * <li> <code>EntityReference</code> nodes are serialized as an 
 * entity reference of the form "<code>&amp;entityName;</code>" in the 
 * output. Child nodes (the expansion) of the entity reference are ignored. 
 * </li>
 * <li> 
 * CDATA sections containing content characters that cannot be represented 
 * in the specified output encoding are handled according to the "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-split-cdata-sections'>
 * split-cdata-sections</a>" parameter.  If the parameter is set to <code>true</code>, CDATA sections 
 * are split, and the unrepresentable characters are serialized as numeric 
 * character references in ordinary content. The exact position and number 
 * of splits is not specified.  If the parameter is set to <code>false</code>
 * , unrepresentable characters in a CDATA section are reported as 
 * <code>"invalid-data-in-cdata-section"</code> errors. The error is not 
 * recoverable - there is no mechanism for supplying alternative characters 
 * and continuing with the serialization. 
 * </li>
 * <li> <code>DocumentFragment</code> 
 * nodes are serialized by serializing the children of the document fragment 
 * in the order they appear in the document fragment. 
 * </li>
 * <li> All other node types 
 * (Element, Text, etc.) are serialized to their corresponding XML source 
 * form. 
 * </li>
 * </ul>
 * <p ><b>Note:</b>  The serialization of a <code>Node</code> does not always 
 * generate a well-formed XML document, i.e. a <code>DOMParser</code> might 
 * throw fatal errors when parsing the resulting serialization. 
 * <p> Within the character data of a document (outside of markup), any 
 * characters that cannot be represented directly are replaced with 
 * character references. Occurrences of '&lt;' and '&amp;' are replaced by 
 * the predefined entities &amp;lt; and &amp;amp;. The other predefined 
 * entities (&amp;gt;, &amp;apos;, and &amp;quot;) might not be used, except 
 * where needed (e.g. using &amp;gt; in cases such as ']]&gt;'). Any 
 * characters that cannot be represented directly in the output character 
 * encoding are serialized as numeric character references. 
 * <p> To allow attribute values to contain both single and double quotes, the 
 * apostrophe or single-quote character (') may be represented as 
 * "&amp;apos;", and the double-quote character (")  as "&amp;quot;". New 
 * line characters and other characters that cannot be represented directly 
 * in attribute values in the output character encoding are serialized as a 
 * numeric character reference. 
 * <p> Within markup, but outside of attributes, any occurrence of a character 
 * that cannot be represented in the output character encoding is reported 
 * as an error. An example would be serializing the element 
 * &lt;LaCa\u00f1ada/&gt; with <code>encoding="us-ascii"</code>. 
 * <p> When requested by setting the parameter "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-normalize-characters'>
 * normalize-characters</a>" on <code>DOMSerializer</code> to true, character normalization is 
 * performed according to the rules defined in [<a href='http://www.w3.org/TR/2002/WD-charmod-20020430'>CharModel</a>] on all 
 * data to be serialized, both markup and character data. The character 
 * normalization process affects only the data as it is being written; it 
 * does not alter the DOM's view of the document after serialization has 
 * completed. 
 * <p> When outputting unicode data, whether or not a byte order mark is 
 * serialized, or if the output is big-endian or little-endian, is 
 * implementation dependent. 
 * <p> Namespaces are fixed up during serialization, the serialization process 
 * will verify that namespace declarations, namespace prefixes and the 
 * namespace URI's associated with elements and attributes are consistent. 
 * If inconsistencies are found, the serialized form of the document will be 
 * altered to remove them. The method used for doing the namespace fixup 
 * while serializing a document is the algorithm defined in Appendix B.1, 
 * "Namespace normalization", of [<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609'>DOM Level 3 Core</a>]
 * . 
 * <p> Any changes made affect only the namespace prefixes and declarations 
 * appearing in the serialized data. The DOM's view of the document is not 
 * altered by the serialization operation, and does not reflect any changes 
 * made to namespace declarations or prefixes in the serialized output.  We 
 * may take back what we say in the above paragraph depending on feedback 
 * from implementors, but for now the belief is that the DOM's view of the 
 * document is not changed during serialization. 
 * <p> While serializing a document, the parameter "discard-default-content" 
 * controls whether or not non-specified data is serialized. 
 * <p> While serializing, errors are reported to the application through the 
 * error handler (<code>DOMSerializer.config</code>'s "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-error-handler'>
 * error-handler</a>" parameter). This specification does in no way try to define all possible 
 * errors that can occur while serializing a DOM node, but some common error 
 * cases are defined. The types (<code>DOMError.type</code>) of errors and 
 * warnings defined by this specification are: 
 * <dl>
 * <dt>
 * <code>"invalid-data-in-cdata-section" [fatal]</code></dt>
 * <dd> Raised if the 
 * configuration parameter "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-split-cdata-sections'>
 * split-cdata-sections</a>" is set to <code>false</code> and invalid data is encountered in a CDATA 
 * section. </dd>
 * <dt><code>"unsupported-encoding" [fatal]</code></dt>
 * <dd> Raised if an 
 * unsupported encoding is encountered. </dd>
 * <dt>
 * <code>"unbound-namespace-in-entity" [warning]</code></dt>
 * <dd> Raised if the 
 * configuration parameter "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-entities'>
 * entities</a>" is set to <code>true</code> and an unbound namespace prefix is 
 * encounterd in a referenced entity. </dd>
 * <dt>
 * <code>"no-output-specified" [fatal]</code></dt>
 * <dd> Raised when writing to a 
 * <code>DOMOutput</code> if no output is specified in the 
 * <code>DOMOutput</code>. </dd>
 * </dl> 
 * <p> In addition to raising the defined errors and warnings, implementations 
 * are expected to raise implementation specific errors and warnings for any 
 * other error and warning cases such as IO errors (file not found, 
 * permission denied,...) and so on. 
 * <p>See also the <a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-LS-20030619'>Document Object Model (DOM) Level 3 Load
and Save Specification</a>.
 */
public interface DOMSerializer {
    /**
     *  The <code>DOMConfiguration</code> object used by the 
     * <code>DOMSerializer</code> when serializing a DOM node. 
     * <br> In addition to the parameters recognized in the [<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609'>DOM Level 3 Core</a>]
     * , the <code>DOMConfiguration</code> objects for 
     * <code>DOMSerializer</code> adds, or modifies, the following 
     * parameters: 
     * <dl>
     * <dt><code>"canonical-form"</code></dt>
     * <dd>
     * <dl>
     * <dt><code>true</code></dt>
     * <dd>[<em>optional</em>] This formatting writes the document according to the rules specified in [<a href='http://www.w3.org/TR/2001/REC-xml-c14n-20010315'>Canonical XML</a>]. 
     * Setting this parameter to <code>true</code> will set the parameter "
     * format-pretty-print" to <code>false</code>. </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) Do not canonicalize the output. </dd>
     * </dl></dd>
     * <dt><code>"discard-default-content"</code></dt>
     * <dd>
     * <dl>
     * <dt>
     * <code>true</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) Use the <code>Attr.specified</code> attribute to decide what attributes 
     * should be discarded. Note that some implementations might use 
     * whatever information available to the implementation (i.e. XML 
     * schema, DTD, the <code>Attr.specified</code> attribute, and so on) to 
     * determine what attributes and content to discard if this parameter is 
     * set to <code>true</code>. </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>required</em>]Keep all attributes and all content.</dd>
     * </dl></dd>
     * <dt><code>"format-pretty-print"</code></dt>
     * <dd>
     * <dl>
     * <dt>
     * <code>true</code></dt>
     * <dd>[<em>optional</em>] Formatting the output by adding whitespace to produce a pretty-printed, 
     * indented, human-readable form. The exact form of the transformations 
     * is not specified by this specification. Pretty-printing changes the 
     * content of the document and may affect the validity of the document, 
     * validating implementations should preserve validity. Setting this 
     * parameter to <code>true</code> will set the parameter "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-canonical-form'>
     * canonical-form</a>" to <code>false</code>. </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) Don't pretty-print the result. </dd>
     * </dl></dd>
     * <dt> 
     * <code>"ignore-unknown-character-denormalizations"</code> </dt>
     * <dd>
     * <dl>
     * <dt>
     * <code>true</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) If, while verifying full normalization when [<a href='http://www.w3.org/TR/2002/CR-xml11-20021015/'>XML 1.1</a>] is 
     * supported, a character is encountered for which the normalization 
     * properties cannot be determined, then raise a 
     * <code>"unknown-character-denormalization"</code> warning (instead of 
     * raising an error, if this parameter is not set) and ignore any 
     * possible denormalizations caused by these characters.  IMO it would 
     * make sense to move this parameter into the DOM Level 3 Core spec, and 
     * the error/warning should be defined there. </dd>
     * <dt><code>false</code></dt>
     * <dd>[<em>optional</em>] Report an fatal error if a character is encountered for which the 
     * processor cannot determine the normalization properties. </dd>
     * </dl></dd>
     * <dt>
     * <code>"normalize-characters"</code></dt>
     * <dd> This parameter is equivalent to 
     * the one defined by <code>DOMConfiguration</code> in [<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609'>DOM Level 3 Core</a>]
     * . Unlike in the Core, the default value for this parameter is 
     * <code>true</code>. While DOM implementations are not required to 
     * support fully normalizing the characters in the document according to 
     * the rules defined in [<a href='http://www.w3.org/TR/2002/WD-charmod-20020430'>CharModel</a>] 
     * supplemented by the definitions of relevant constructs from Section 
     * 2.13 of [<a href='http://www.w3.org/TR/2002/CR-xml11-20021015/'>XML 1.1</a>], this 
     * parameter must be activated by default if supported. </dd>
     * <dt>
     * <code>"xml-declaration"</code></dt>
     * <dd>
     * <dl>
     * <dt><code>true</code></dt>
     * <dd>[<em>required</em>] (<em>default</em>) If a <code>Document</code>, <code>Element</code>, or <code>Entity</code>
     *  node is serialized, the XML declaration, or text declaration, should 
     * be included. The version (<code>Document.xmlVersion</code> if the 
     * document is a Level 3 document, and the version is non-null, 
     * otherwise use the value "1.0"), and possibly an encoding (
     * <code>DOMSerializer.encoding</code>, or 
     * <code>Document.actualEncoding</code> or 
     * <code>Document.xmlEncoding</code> if the document is a Level 3 
     * document) is specified in the serialized XML declaration. </dd>
     * <dt>
     * <code>false</code></dt>
     * <dd>[<em>required</em>] Do not serialize the XML and text declarations. Report a 
     * <code>"xml-declaration-needed"</code> warning if this will cause 
     * problems (i.e. the serialized data is of an XML version other than [<a href='http://www.w3.org/TR/2000/REC-xml-20001006'>XML 1.0</a>], or an 
     * encoding would be needed to be able to re-parse the serialized data). </dd>
     * </dl></dd>
     * </dl>
     * <br> The parameters "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-well-formed'>
     * well-formed</a>", "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-namespaces'>
     * namespaces</a>", and "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-namespace-declarations'>
     * namespace-declarations</a>" cannot be set to <code>false</code>. 
     */
    public DOMConfiguration getConfig();

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
     * of those allowed by section 2.11, "End-of-Line Handling" in [<a href='http://www.w3.org/TR/2000/REC-xml-20001006'>XML 1.0</a>], if the 
     * serialized content is XML 1.0 or section 2.11, "End-of-Line Handling" 
     * in [<a href='http://www.w3.org/TR/2002/CR-xml11-20021015/'>XML 1.1</a>], if the 
     * serialized content is XML 1.1. </dd>
     * <dt>CR</dt>
     * <dd>The carriage-return character (#xD).</dd>
     * <dt>
     * CR-LF</dt>
     * <dd> The carriage-return and line-feed characters (#xD #xA). </dd>
     * <dt>LF</dt>
     * <dd> The 
     * line-feed character (#xA). </dd>
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
     * of those allowed by section 2.11, "End-of-Line Handling" in [<a href='http://www.w3.org/TR/2000/REC-xml-20001006'>XML 1.0</a>], if the 
     * serialized content is XML 1.0 or section 2.11, "End-of-Line Handling" 
     * in [<a href='http://www.w3.org/TR/2002/CR-xml11-20021015/'>XML 1.1</a>], if the 
     * serialized content is XML 1.1. </dd>
     * <dt>CR</dt>
     * <dd>The carriage-return character (#xD).</dd>
     * <dt>
     * CR-LF</dt>
     * <dd> The carriage-return and line-feed characters (#xD #xA). </dd>
     * <dt>LF</dt>
     * <dd> The 
     * line-feed character (#xA). </dd>
     * </dl>
     * <br>The default value for this attribute is <code>null</code>.
     */
    public void setNewLine(String newLine);

    /**
     *  When the application provides a filter, the serializer will call out 
     * to the filter before serializing each Node. The filter implementation 
     * can choose to remove the node from the stream or to terminate the 
     * serialization early. 
     * <br> The filter is invoked before the operations requested by the 
     * <code>DOMConfiguration</code> parameters have been applied. For 
     * example, CDATA sections are passed to the filter even if "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-cdata-sections'>
     * cdata-sections</a>" is set to <code>false</code>. 
     */
    public DOMSerializerFilter getFilter();
    /**
     *  When the application provides a filter, the serializer will call out 
     * to the filter before serializing each Node. The filter implementation 
     * can choose to remove the node from the stream or to terminate the 
     * serialization early. 
     * <br> The filter is invoked before the operations requested by the 
     * <code>DOMConfiguration</code> parameters have been applied. For 
     * example, CDATA sections are passed to the filter even if "<a href='http://www.w3.org/TR/2003/WD-DOM-Level-3-Core-20030609/core.html#parameter-cdata-sections'>
     * cdata-sections</a>" is set to <code>false</code>. 
     */
    public void setFilter(DOMSerializerFilter filter);

    /**
     *  Serialize the specified node as described above in the general 
     * description of the <code>DOMSerializer</code> interface. The output 
     * is written to the supplied <code>DOMOutput</code>. 
     * <br> When writing to a <code>DOMOutput</code>, the encoding is found by 
     * looking at the encoding information that is reachable through the 
     * <code>DOMOutput</code> and the item to be written (or its owner 
     * document) in this order: 
     * <ol>
     * <li> <code>DOMOutput.encoding</code>, 
     * </li>
     * <li> 
     * <code>Document.actualEncoding</code>, 
     * </li>
     * <li> 
     * <code>Document.xmlEncoding</code>. 
     * </li>
     * </ol>
     * <br> If no encoding is reachable through the above properties, a 
     * default encoding of "UTF-8" will be used. 
     * <br> If the specified encoding is not supported an 
     * "unsupported-encoding" error is raised. 
     * <br> If no output is specified in the <code>DOMOutput</code>, a 
     * "no-output-specified" error is raised. 
     * @param node  The node to serialize. 
     * @param destination The destination for the serialized DOM.
     * @return  Returns <code>true</code> if <code>node</code> was 
     *   successfully serialized and <code>false</code> in case the node 
     *   couldn't be serialized. 
     */
    public boolean write(Node node, 
                         DOMOutput destination);

    /**
     *  Serialize the specified node as described above in the general 
     * description of the <code>DOMSerializer</code> interface. The output 
     * is written to the supplied URI. 
     * <br> When writing to a URI, the encoding is found by looking at the 
     * encoding information that is reachable through the item to be written 
     * (or its owner document) in this order: 
     * <ol>
     * <li> 
     * <code>Document.actualEncoding</code>, 
     * </li>
     * <li> 
     * <code>Document.xmlEncoding</code>. 
     * </li>
     * </ol>
     * <br> If no encoding is reachable through the above properties, a 
     * default encoding of "UTF-8" will be used. 
     * <br> If the specified encoding is not supported an 
     * "unsupported-encoding" error is raised. 
     * @param node  The node to serialize. 
     * @param URI The URI to write to.
     * @return  Returns <code>true</code> if <code>node</code> was 
     *   successfully serialized and <code>false</code> in case the node 
     *   couldn't be serialized. 
     */
    public boolean writeURI(Node node, 
                            String URI);

    /**
     *  Serialize the specified node as described above in the general 
     * description of the <code>DOMSerializer</code> interface. The output 
     * is written to a <code>DOMString</code> that is returned to the caller 
     * (this method completely ignores all the encoding information 
     * available). 
     * @param node  The node to serialize. 
     * @return  Returns the serialized data, or <code>null</code> in case the 
     *   node couldn't be serialized. 
     * @exception DOMException
     *    DOMSTRING_SIZE_ERR: Raised if the resulting string is too long to 
     *   fit in a <code>DOMString</code>. 
     */
    public String writeToString(Node node)
                                throws DOMException;

}