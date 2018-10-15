public  Content getContent();

package org.eclipse.wst.xml.vex.core.internal.provisional.dom;


/**
 * @model
 */
public interface VEXDocumentFragment {

	/**
	 * Mime type representing document fragments: "text/x-vex-document-fragment"
	 * @model
	 */
	public static final String MIME_TYPE = "application/x-vex-document-fragment";

	/**
	 * Returns the Content object holding this fragment's content.
	 * 
	 * @model
	 */
	public  IContent getContent();

	/**
	 * Returns the number of characters, including sentinels, represented by the
	 * fragment.
	 * 
	 * @model
	 */
	public  int getLength();

	/**
	 * Returns the elements that make up this fragment.
	 * 
	 * @model 
	 */
	public  VEXElement[] getElements();

	/**
	 * Returns an array of element names and Validator.PCDATA representing the
	 * content of the fragment.
	 * 
	 * @model 
	 */
	public  String[] getNodeNames();

	/**
	 * Returns the nodes that make up this fragment, including elements and
	 * <code>Text</code> objects.
	 * 
	 * @model 
	 */
	public  VEXNode[] getNodes();

}
 No newline at end of file