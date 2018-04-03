import org.columba.core.gui.base.ColorFactory;

//The contents of this file are subject to the Mozilla Public License Version 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.mail.message;

import java.util.logging.Logger;

import org.columba.core.gui.util.ColorFactory;
import org.columba.mail.folder.headercache.CachedHeaderfields;
import org.columba.ristretto.message.Address;
import org.columba.ristretto.message.Attributes;
import org.columba.ristretto.message.BasicHeader;
import org.columba.ristretto.message.Flags;
import org.columba.ristretto.message.Header;
import org.columba.ristretto.message.MimeHeader;
import org.columba.ristretto.message.MimeType;
import org.columba.ristretto.parser.HeaderParser;


/**
 * Represents a RFC822-compliant header
 * <p>
 * Every headerfield is saved in {@HeaderList}.
 * <p>
 * Generally every headerfield is a string,
 * but for optimization reasons some items
 * are going to change to for example a Date class
 * <p>
 * These items are saved in {@link Attributes} to separate
 * them clearly from general RFC822 headerfields.
 *
 * <p>
 * @see CachedHeaderfields
 *
 * @author tstich, fdietz
 */
public class ColumbaHeader implements IColumbaHeader {
    
    private static final Logger LOG = Logger.getLogger("org.columba.mail.message");
    
    protected Header header;
    protected Attributes attributes;
    protected Flags flags;

    public ColumbaHeader(ColumbaHeader header) {
        this.header = header.getHeader();
        this.attributes = header.getAttributes();
        this.flags = header.getFlags();
    }

    public ColumbaHeader() {
        this(new Header());
    }

    public ColumbaHeader(Header header) {
        this.header = header;
        flags = new Flags();
        attributes = new Attributes();

        BasicHeader basicHeader = new BasicHeader(header);

        attributes.put("columba.alreadyfetched", Boolean.FALSE);
        attributes.put("columba.spam", Boolean.FALSE);

        attributes.put("columba.priority",
            new Integer(basicHeader.getPriority()));

        Address from = basicHeader.getFrom();

        if (from != null) {
            attributes.put("columba.from", from);
        } else {
            attributes.put("columba.from", "");
        }

        Address[] to = basicHeader.getTo();

        if (to.length > 0) {
            //We save only the first item in the to-list
            attributes.put("columba.to", to[0]);
        } else {
            attributes.put("columba.to", "");
        }

        Address[] cc = basicHeader.getCc();

        if (cc.length > 0) {
            //We save only the first item in the cc-list            
            attributes.put("columba.cc", cc[0]);
        } else {
            attributes.put("columba.cc", "");
        }

        attributes.put("columba.host", "");
        attributes.put("columba.date", basicHeader.getDate());

        String subject = basicHeader.getSubject();

        if (subject != null) {
            attributes.put("columba.subject", subject);
        } else {
            attributes.put("columba.subject", "");
        }

        attributes.put("columba.attachment", hasAttachments());
        attributes.put("columba.size", new Integer(0));

        // message colour should be black as default
        attributes.put("columba.color", ColorFactory.getColor(0));

        // use default account 
        attributes.put("columba.accountuid", new Integer(0));
    }

    public Object clone() {
        ColumbaHeader clone;
        try {
            clone = (ColumbaHeader) super.clone();
            clone.attributes = (Attributes) this.attributes.clone();
            clone.flags = (Flags) this.flags.clone();
            clone.header = (Header) this.header.clone();
        } catch (CloneNotSupportedException e) {
            LOG.warning("Internal error when cloning object: " + e);
            throw new RuntimeException("Unknown error when cloning ColumbaHeader.", e);
        }
        return clone;
    }

    public void copyColumbaKeys(IColumbaHeader header) {
        header.setFlags( (Flags) flags.clone());
        header.setAttributes( (Attributes) attributes.clone());
    }

    /* (non-Javadoc)
     * @see org.columba.mail.message.HeaderInterface#count()
     */
    public int count() {
        return attributes.count() + header.count() + 5;
    }

    /* (non-Javadoc)
     * @see org.columba.mail.message.HeaderInterface#getFlags()
     */
    public Flags getFlags() {
        return flags;
    }

    /**
     * Note: Don't use this method anymore when accessing
     * attributes like "columba.size", use getAttribute() instead
     *
     */
    public Object get(String s) {
        if (s.startsWith("columba.flags.")) {
            String flag = s.substring("columba.flags.".length());

            if (flag.equals("seen")) {
                return Boolean.valueOf(flags.get(Flags.SEEN));
            } else if (flag.equals("recent")) {
                return Boolean.valueOf(flags.get(Flags.RECENT));
            } else if (flag.equals("answered")) {
                return Boolean.valueOf(flags.get(Flags.ANSWERED));
            } else if (flag.equals("draft")) {
                return Boolean.valueOf(flags.get(Flags.DRAFT));
            } else if (flag.equals("flagged")) {
                return Boolean.valueOf(flags.get(Flags.FLAGGED));
            } else if (flag.equals("expunged")) {
                return Boolean.valueOf(flags.get(Flags.DELETED));
            }
        }

        if (s.startsWith("columba.")) {
            return attributes.get(s);
        }

        return header.get(HeaderParser.normalizeKey(s));
    }

    /* (non-Javadoc)
     * @see org.columba.mail.message.HeaderInterface#set(java.lang.String, java.lang.Object)
     */
    public void set(String s, Object o) {
        if (o == null) {
            return;
        }
        if (s.startsWith("columba.flags")) {
            String flag = s.substring("columba.flags.".length());
            boolean value = ((Boolean) o).booleanValue();

            if (flag.equals("seen")) {
                flags.set(Flags.SEEN, value);

                return;
            }

            if (flag.equals("recent")) {
                flags.set(Flags.RECENT, value);

                return;
            }

            if (flag.equals("answered")) {
                flags.set(Flags.ANSWERED, value);

                return;
            }

            if (flag.equals("expunged")) {
                flags.set(Flags.DELETED, value);

                return;
            }

            if (flag.equals("draft")) {
                flags.set(Flags.DRAFT, value);

                return;
            }

            if (flag.equals("flagged")) {
                flags.set(Flags.FLAGGED, value);
            }
        }

        if (s.startsWith("columba.")) {
            attributes.put(s, o);
        } else {
            header.set(HeaderParser.normalizeKey(s), (String) o);
        }
    }

    /**
     * @return
     */
    public Header getHeader() {
        return header;
    }

    /**
     * @return
     */
    public Attributes getAttributes() {
        return attributes;
    }

    /**
     * @param attributes
     */
    public void setAttributes(Attributes attributes) {
        this.attributes = attributes;
    }

    /**
     * @param flags
     */
    public void setFlags(Flags flags) {
        this.flags = flags;
    }

    /**
     * @param header
     */
    public void setHeader(Header header) {
        this.header = header;
    }

    public Boolean hasAttachments() {
        boolean hasAttachments = false;
        MimeType mimeType = new MimeHeader(header).getMimeType();
        hasAttachments = !mimeType.getType().equals("text") &&
            !mimeType.getSubtype().equals("alternative");

        return Boolean.valueOf(hasAttachments);
    }
}