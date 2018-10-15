public List<VEXNode> getNodes(int startOffset, int endOffset);

package org.eclipse.wst.xml.vex.core.internal.provisional.dom;

import org.eclipse.wst.xml.vex.core.internal.dom.DocumentEvent;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentListener;
import org.eclipse.wst.xml.vex.core.internal.dom.DocumentValidationException;
import java.util.List;

/**
 * 
 * @author dcarver
 * @model
 */
public interface VEXDocument {

	/**
	 * Adds a document listener to the list of listeners to be notified of
	 * document changes.
	 * 
	 * @param listener
	 *            <code>DocumentListener</code> to add.
	 * 
	 */
	public void addDocumentListener(DocumentListener listener);

	/**
	 * Returns true if the given document fragment can be inserted at the given
	 * offset.
	 * 
	 * @param offset
	 *            offset where the insertion is to occur
	 * @param fragment
	 *            fragment to be inserted
	 * @model
	 */
	public boolean canInsertFragment(int offset, VEXDocumentFragment fragment);

	/**
	 * Returns true if text can be inserted at the given offset.
	 * 
	 * @param offset
	 *            offset where the insertion is to occur
	 * @model
	 */
	public boolean canInsertText(int offset);

	/**
	 * Creates a <code>Position</code> object at the given character offset.
	 * 
	 * @param offset
	 *            initial character offset of the position
	 * @model
	 */
	public Position createPosition(int offset);

	/**
	 * Deletes a portion of the document. No element may straddle the deletion
	 * span.
	 * 
	 * @param startOffset
	 *            start of the range to delete
	 * @param endOffset
	 *            end of the range to delete
	 * @throws DocumentValidationException
	 *             if the change would result in an invalid document.
	 * @model
	 */
	public void delete(int startOffset, int endOffset)
			throws DocumentValidationException;

	/**
	 * Finds the lowest element that contains both of the given offsets.
	 * 
	 * @param offset1
	 *            the first offset
	 * @param offset2
	 *            the second offset
	 * @model
	 */
	public VEXElement findCommonElement(int offset1, int offset2);

	/**
	 * Returns the character at the given offset.
	 * 
	 * @model
	 */
	public char getCharacterAt(int offset);

	/**
	 * Returns the element at the given offset. The given offset must be greater
	 * or equal to 1 and less than the current document length.
	 * 
	 * @model
	 */
	public VEXElement getElementAt(int offset);

	/**
	 * Returns the encoding used for this document, or null if no encoding has
	 * been declared.
	 * 
	 * @model
	 */
	public String getEncoding();

	/**
	 * Create a <code>DocumentFragment</code> representing the given range of
	 * offsets.
	 * 
	 * @return
	 * 
	 * @model
	 */
	public VEXDocumentFragment getFragment(int startOffset, int endOffset);

	/**
	 * Returns the length of the document in characters, including the null
	 * characters that delimit each element.
	 * 
	 * @model
	 */
	public int getLength();

	/**
	 * Returns an array of element names and Validator.PCDATA representing the
	 * content between the given offsets. The given offsets must both be
	 * directly in the same element.
	 * 
	 * @param startOffset
	 *            the offset at which the sequence begins
	 * @param endOffset
	 *            the offset at which the sequence ends
	 * @model 
	 */
	public List<String> getNodeNames(int startOffset, int endOffset);

	/**
	 * Returns an array of Nodes representing the selected range. The given
	 * offsets must both be directly in the same element.
	 * 
	 * @param startOffset
	 *            the offset at which the sequence begins
	 * @param endOffset
	 *            the offset at which the sequence ends
	 * 
	 * @model 
	 */
	public VEXNode[] getNodes(int startOffset, int endOffset);


	/**
	 * Returns the text between the two given offsets. Unlike getText, sentinel
	 * characters are not removed.
	 * 
	 * @param startOffset
	 *            character offset of the start of the text
	 * @param endOffset
	 *            character offset of the end of the text
	 * @model
	 */
	public String getRawText(int startOffset, int endOffset);

	/**
	 * Returns the root element of this document.
	 * 
	 * @model
	 */
	public VEXElement getRootElement();


	/**
	 * Returns the text between the two given offsets. Sentinal characters are
	 * removed.
	 * 
	 * @param startOffset
	 *            character offset of the start of the text
	 * @param endOffset
	 *            character offset of the end of the text
	 * @model
	 */
	public String getText(int startOffset, int endOffset);

	/**
	 * Returns the validator used to validate the document, or null if a
	 * validator has not been set. Note that the DocumentFactory does not
	 * automatically create a validator.
	 * 
	 * @model
	 */
	public Validator getValidator();

	/**
	 * Inserts an element at the given position.
	 * 
	 * @param offset
	 *            character offset at which the element is to be inserted. Must
	 *            be greater or equal to 1 and less than the current length of
	 *            the document, i.e. it must be within the range of the root
	 *            element.
	 * @param defaults
	 *            element to insert
	 * @throws DocumentValidationException
	 *             if the change would result in an invalid document.
	 * @model
	 */
	public void insertElement(int offset, VEXElement defaults)
			throws DocumentValidationException;

	/**
	 * Inserts a document fragment at the given position.
	 * 
	 * @param offset
	 *            character offset at which the element is to be inserted. Must
	 *            be greater or equal to 1 and less than the current length of
	 *            the document, i.e. it must be within the range of the root
	 *            element.
	 * @param fragment
	 *            fragment to insert
	 * @throws DocumentValidationException
	 *             if the change would result in an invalid document.
	 * @model
	 */
	public void insertFragment(int offset, VEXDocumentFragment fragment)
			throws DocumentValidationException;

	/**
	 * Inserts text at the given position.
	 * 
	 * @param offset
	 *            character offset at which the text is to be inserted. Must be
	 *            greater or equal to 1 and less than the current length of the
	 *            document, i.e. it must be within the range of the root
	 *            element.
	 * @param text
	 *            text to insert
	 * @return UndoableEdit that can be used to undo the deletion
	 * @throws DocumentValidationException
	 *             if the change would result in an invalid document.
	 * @model
	 */
	public void insertText(int offset, String text)
			throws DocumentValidationException;

	/**
	 * Returns true if undo is enabled, that is, undoable edit events are fired
	 * to registered listeners.
	 * 
	 * @model
	 */
	public boolean isUndoEnabled();

	/**
	 * Removes a document listener from the list of listeners so that it is no
	 * longer notified of document changes.
	 * 
	 * @param listener
	 *            <code>DocumentListener</code> to remove.
	 * 
	 */
	public void removeDocumentListener(DocumentListener listener);

	/**
	 * Returns the public ID of the document type.
	 * @model
	 */
	public String getPublicID();
	
	/**
	 * Sets the public ID for the document's document type.
	 * 
	 * @param publicID
	 *            New value for the public ID.
	 *  
	 */
	public void setPublicID(String publicID);

	/**
	 * Sets the system ID for the document's document type.
	 * 
	 * @param systemID
	 *            New value for the system ID.
	 * 
	 */
	public void setSystemID(String systemID);

	/**
	 * Returns the system ID of the document type.
	 */
	public String getSystemID();
	
	/**
	 * Sets whether undo events are enabled. Typically, undo events are disabled
	 * while an edit is being undone or redone.
	 * 
	 * @param undoEnabled
	 *            If true, undoable edit events are fired to registered
	 *            listeners.
	 * 
	 */
	public void setUndoEnabled(boolean undoEnabled);

	/**
	 * Sets the validator to use for this document.
	 * 
	 * @param validator
	 *            Validator to use for this document.
	 * 
	 */
	public void setValidator(Validator validator);

	/**
	 * @param documentEvent
	 * 
	 */
	public void fireAttributeChanged(DocumentEvent documentEvent);

}
 No newline at end of file