columbaHeader.set("columba.uid", "");

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
package org.columba.mail.message;

import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.Message;
import org.columba.ristretto.message.MimePart;
import org.columba.ristretto.message.MimeTree;
import org.columba.ristretto.message.io.CharSequenceSource;
import org.columba.ristretto.message.io.Source;


/**
 * Adds Columba-specific features to the default {@link Message}
 * object found in the Ristretto API.
 * <p>
 *
 *
 * @author fdietz, tstich
 */
public class ColumbaMessage {
    protected ColumbaHeader columbaHeader;
    protected Flags flags;
    protected Message message;
    protected MimePart bodyPart;

    public ColumbaMessage() {
        this(new ColumbaHeader());
    }

    public ColumbaMessage(ColumbaHeader header) {
        columbaHeader = header;
        message = new Message();

        flags = columbaHeader.getFlags();
    }

    public ColumbaMessage(Message m) {
        columbaHeader = new ColumbaHeader(m.getHeader());
        message = m;

        flags = columbaHeader.getFlags();
    }

    public ColumbaMessage(Header header) {
        columbaHeader = new ColumbaHeader(header);
        message = new Message();
        message.setHeader(header);

        flags = columbaHeader.getFlags();
    }

    public ColumbaMessage(ColumbaHeader h, Message m) {
        columbaHeader = h;
        flags = columbaHeader.getFlags();

        columbaHeader.setHeader(m.getHeader());
        message = m;
    }

    public String getStringSource() {
        return getSource().toString();
    }

    public void setStringSource(String s) {
        message.setSource(new CharSequenceSource(s));
    }

    public void setBodyPart(MimePart body) {
        bodyPart = body;
    }

    public void setUID(Object o) {
        if (o != null) {
            columbaHeader.set("columba.uid", o);
        } else {
            columbaHeader.set("columba.uid", new String(""));
        }

        //uid = o;
    }

    public Object getUID() {
        return getHeader().get("columba.uid");
    }

    public MimeTree getMimePartTree() {
        return message.getMimePartTree();
    }

    public void setMimePartTree(MimeTree ac) {
        message.setMimePartTree(ac);
    }

    public void freeMemory() {
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#getHeader()
     */
    public ColumbaHeader getHeader() {
        return columbaHeader;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#setHeader(org.columba.ristretto.message.Header)
     */
    public void setHeader(ColumbaHeader h) {
        columbaHeader = h;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#getBodyPart()
     */
    public MimePart getBodyPart() {
        return bodyPart;
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#getMimePart(int)
     */
    public MimePart getMimePart(int number) {
        return message.getMimePart(number);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#getMimePartCount()
     */
    public int getMimePartCount() {
        return message.getMimePartCount();
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#getSource()
     */
    public Source getSource() {
        return message.getSource();
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#setHeader(org.columba.ristretto.message.Header)
     */
    public void setHeader(Header h) {
        message.setHeader(h);
    }

    /*
     * (non-Javadoc)
     *
     * @see org.columba.ristretto.message.Message#setSource(org.columba.ristretto.message.io.Source)
     */
    public void setSource(Source source) {
        message.setSource(source);
    }

    /**
     * @return
     */
    public Flags getFlags() {
        return flags;
    }
}