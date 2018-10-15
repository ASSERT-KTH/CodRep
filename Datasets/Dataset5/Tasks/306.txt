public List<VEXElement> getChildElements();

package org.eclipse.wst.xml.vex.core.internal.provisional.dom;

import java.util.Iterator;
import java.util.List;

import org.eclipse.wst.xml.vex.core.internal.dom.DocumentValidationException;

/**
 * 
 * @author dcarver
 * 
 * @model
 */
public interface VEXElement extends VEXNode {

	/**
	 * Adds the given child to the end of the child list. Sets the parent
	 * attribute of the given element to this element.
	 * 
	 * @model
	 */
	public void addChild(VEXElement child);

	/**
	 * Clones the element and its attributes. The returned element has no parent
	 * or children.
	 * 
	 * @model
	 */
	public Object clone();

	/**
	 * Returns the value of an attribute given its name. If no such attribute
	 * exists, returns null.
	 * 
	 * @param name
	 *            Name of the attribute.
	 * @model
	 */
	public String getAttribute(String name);

	/**
	 * Returns an array of names of the attributes in the element.
	 * 
	 * @model 
	 */
	public List<String> getAttributeNames();

	/**
	 * Returns an iterator over the children. Used by
	 * <code>Document.delete</code> to safely delete children.
	 * 
	 * 
	 */
	public Iterator getChildIterator();

	/**
	 * Returns an array of the elements children.
	 * 
	 * @model  
	 */
	public VEXElement[] getChildElements();

	/**
	 * Returns an array of nodes representing the content of this element. The
	 * array includes child elements and runs of text returned as
	 * <code>Text</code> objects.
	 * 
	 * @model 
	 */
	public VEXNode[] getChildNodes();

	/**
	 * @return The document to which this element belongs. Returns null if this
	 *         element is part of a document fragment.
	 * @model
	 */
	public VEXDocument getDocument();

	/**
	 * Returns the name of the element.
	 * 
	 * @model
	 */
	public String getName();

	/**
	 * Returns true if the element has no content.
	 * 
	 * @model
	 */
	public boolean isEmpty();

	/**
	 * Removes the given attribute from the array.
	 * 
	 * @param name
	 *            name of the attribute to remove.
	 * @model
	 */
	public void removeAttribute(String name) throws DocumentValidationException;

	/**
	 * Sets the value of an attribute for this element.
	 * 
	 * @param name
	 *            Name of the attribute to be set.
	 * @param value
	 *            New value for the attribute. If null, this call has the same
	 *            effect as removeAttribute(name).
	 * @model
	 */
	public void setAttribute(String name, String value)
			throws DocumentValidationException;

	/**
	 * Returns the parent of this element, or null if this is the root element.
	 * 
	 * @model 
	 */
	public VEXElement getParent();

	/**
	 * Sets the parent of this element.
	 * 
	 * @param parent
	 *            Parent element.
	 * 
	 */
	public void setParent(VEXElement parent);

	/**
	 * 
	 * @return
	 * 
	 */
	public String toString();

	/**
	 * 
	 * @param content
	 * @param offset
	 * @param i
	 * @model
	 */
	public void setContent(Content content, int offset, int i);

	/**
	 * 
	 * @param index
	 * @param child
	 * @model
	 */
	public void insertChild(int index, VEXElement child);

}
 No newline at end of file