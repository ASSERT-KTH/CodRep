if (!flags.getExpunged())

/*
 * Created on 30.07.2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.mail.gui.table.model;

import org.columba.mail.message.ColumbaHeader;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.HeaderInterface;

/**
 * @author fdietz
 *
 * Adds basic filter capabilities to the TableModel
 * 
 * Items which can be filtered are:
 *  - unseen flag
 *  - answered flag
 *  - flagged flag
 *  - expunged flag
 *  - has attachment 
 *  - String in Subject or Sender
 * 
 */
public class BasicTableModelFilter extends TreeTableModelDecorator{

	protected boolean newFlag = false;
	//protected boolean oldFlag = true;
	protected boolean answeredFlag = false;
	protected boolean flaggedFlag = false;
	protected boolean expungedFlag = false;
	protected boolean attachmentFlag = false;
	//protected String patternItem = new String("subject");
	protected String patternString = new String();

	protected boolean dataFiltering = false;

	

	public BasicTableModelFilter(TreeTableModelInterface tableModel) {
		super(tableModel);

	}

	/************** filter view *********************/

	public void setDataFiltering(boolean b) throws Exception {
		dataFiltering = b;

	}

	public boolean isEnabled() {
		return dataFiltering;
	}

	public void setNewFlag(boolean b) throws Exception {
		newFlag = b;

	}

	public boolean getNewFlag() {
		return newFlag;
	}

	public void setAnsweredFlag(boolean b) throws Exception {
		answeredFlag = b;

	}

	public boolean getAnsweredFlag() {
		return answeredFlag;
	}

	public void setFlaggedFlag(boolean b) throws Exception {
		flaggedFlag = b;

	}

	public boolean getFlaggedFlag() {
		return flaggedFlag;
	}
	public void setExpungedFlag(boolean b) throws Exception {
		expungedFlag = b;

	}

	public boolean getExpungedFlag() {
		return expungedFlag;
	}
	public void setAttachmentFlag(boolean b) throws Exception {
		attachmentFlag = b;

	}

	public boolean getAttachmentFlag() {
		return attachmentFlag;
	}

	public void setPatternString(String s) throws Exception {
		patternString = s;

	}

	public String getPatternString() {
		return patternString;
	}

	protected boolean testString(HeaderInterface header) {
		String subject = (String) header.get("Subject");
		if (subject != null) {

			String pattern = getPatternString().toLowerCase();

			if (subject.toLowerCase().indexOf(pattern.toLowerCase()) != -1)
				return true;

		}

		String from = (String) header.get("From");
		if (from != null) {

			String pattern = getPatternString().toLowerCase();

			if (from.toLowerCase().indexOf(pattern.toLowerCase()) != -1)
				return true;

		}

		return false;
	}

	public boolean addItem(HeaderInterface header) {
		boolean result = true;
		boolean result2 = false;
		//boolean result3 = true;
		boolean flags1 = false;
		boolean flags2 = false;

		Flags flags = ((ColumbaHeader) header).getFlags();

		if (flags == null) {
			System.out.println("flags is null");
			return false;
		}

		if (getNewFlag()) {
			if (flags.getSeen())
				result = false;

		}

		if (getAnsweredFlag()) {
			if (!flags.getAnswered())
				result = false;
		}
		if (getFlaggedFlag()) {
			if (!flags.getFlagged())
				result = false;
		}
		if (getExpungedFlag()) {
			if (!flags.getDeleted())
				result = false;

		}
		if (getAttachmentFlag()) {

			Boolean attach = (Boolean) header.get("columba.attachment");
			boolean attachment = attach.booleanValue();

			if (!attachment)
				result = false;
		}

		if (!(getPatternString().equals(""))) {
			flags2 = true;
			result2 = testString(header);

		} else
			result2 = true;

		if (result2) {
			if (result) {

				return true;
			}
		}

		return false;
	}
	
}