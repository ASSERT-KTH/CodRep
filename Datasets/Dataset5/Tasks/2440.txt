public interface VEXNode {

package org.eclipse.wst.xml.vex.core.internal.provisional.dom;


/**
 * @model
 */
public interface IVEXNode {

	/**
	 * Returns the document associated with this node. Null if the node has not
	 * yet been inserted into a document.
	 * 
	 * @model
	 */
	public  IContent getContent();

	/**
	 * Returns the character offset corresponding to the end of the node.
	 * 
	 * @model
	 */
	public  int getEndOffset();

	/**
	 * Returns the <code>Position</code> corresponding to the end of the node.
	 * 
	 * @model
	 */
	public  IPosition getEndPosition();

	/**
	 * Returns the character offset corresponding to the start of the node.
	 * 
	 * @model
	 */
	public  int getStartOffset();

	/**
	 * Returns the <code>Position</code> corresponding to the start of the node.
	 * 
	 * @model
	 */
	public  IPosition getStartPosition();

	/**
	 * Returns the text contained by this node. If this node is an element, the
	 * text in all child nodes is included.
	 * 
	 * @model
	 */
	public  String getText();

}
 No newline at end of file