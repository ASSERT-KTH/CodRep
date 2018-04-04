if (!flags.getDeleted()) {

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
//(the "License"); you may not use this file except in compliance with the
//License. You may obtain a copy of the License at http://www.mozilla.org/MPL/
//
//Software distributed under the License is distributed on an "AS IS" basis,
//WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
//for the specific language governing rights and
//limitations under the License.
//
//The Original Code is "The Columba Project"
//
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.gui.table.model;

import org.columba.mail.message.ColumbaHeader;

import org.columba.ristretto.message.Flags;


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
public class BasicTableModelFilter extends TreeTableModelDecorator {
    protected boolean newFlag = false;

    //protected boolean oldFlag = true;
    protected boolean answeredFlag = false;
    protected boolean flaggedFlag = false;
    protected boolean expungedFlag = false;
    protected boolean attachmentFlag = false;

    //protected String patternItem = new String("subject");
    protected String patternString = "";
    protected boolean dataFiltering = false;

    public BasicTableModelFilter(TreeTableModelInterface tableModel) {
        super(tableModel);
    }

    /************** filter view *********************/
    public void setDataFiltering(boolean b) {
        dataFiltering = b;
    }

    public boolean isEnabled() {
        return dataFiltering;
    }

    public void setNewFlag(boolean b) {
        newFlag = b;
    }

    public boolean getNewFlag() {
        return newFlag;
    }

    public void setAnsweredFlag(boolean b) {
        answeredFlag = b;
    }

    public boolean getAnsweredFlag() {
        return answeredFlag;
    }

    public void setFlaggedFlag(boolean b) {
        flaggedFlag = b;
    }

    public boolean getFlaggedFlag() {
        return flaggedFlag;
    }

    public void setExpungedFlag(boolean b) {
        expungedFlag = b;
    }

    public boolean getExpungedFlag() {
        return expungedFlag;
    }

    public void setAttachmentFlag(boolean b) {
        attachmentFlag = b;
    }

    public boolean getAttachmentFlag() {
        return attachmentFlag;
    }

    public void setPatternString(String s) {
        patternString = s;
    }

    public String getPatternString() {
        return patternString;
    }

    protected boolean testString(ColumbaHeader header) {
        String subject = (String) header.get("Subject");

        if (subject != null) {
            String pattern = getPatternString().toLowerCase();

            if (subject.toLowerCase().indexOf(pattern.toLowerCase()) != -1) {
                return true;
            }
        }

        String from = (String) header.get("From");

        if (from != null) {
            String pattern = getPatternString().toLowerCase();

            if (from.toLowerCase().indexOf(pattern.toLowerCase()) != -1) {
                return true;
            }
        }

        return false;
    }

    public boolean addItem(ColumbaHeader header) {
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
            if (flags.getSeen()) {
                result = false;
            }
        }

        if (getAnsweredFlag()) {
            if (!flags.getAnswered()) {
                result = false;
            }
        }

        if (getFlaggedFlag()) {
            if (!flags.getFlagged()) {
                result = false;
            }
        }

        if (getExpungedFlag()) {
            if (!flags.getExpunged()) {
                result = false;
            }
        }

        if (getAttachmentFlag()) {
            Boolean attach = (Boolean) header.get("columba.attachment");
            boolean attachment = attach.booleanValue();

            if (!attachment) {
                result = false;
            }
        }

        if (!(getPatternString().equals(""))) {
            flags2 = true;
            result2 = testString(header);
        } else {
            result2 = true;
        }

        if (result2) {
            if (result) {
                return true;
            }
        }

        return false;
    }
}