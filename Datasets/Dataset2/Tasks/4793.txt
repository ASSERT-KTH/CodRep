ColumbaLogger.log.info("found recent message");

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
package org.columba.mail.gui.table.model;

import org.columba.core.logging.ColumbaLogger;

import org.columba.mail.message.ColumbaHeader;
import org.columba.mail.message.HeaderList;

import java.text.Collator;

import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.StringTokenizer;


/**
 * Title:
 * Description:
 * Copyright:    Copyright (c) 2001
 * Company:
 * @author
 * @version 1.0
 */
public class TableModelThreadedView extends TreeTableModelDecorator {
    private boolean enabled;
    private HashMap hashtable;
    private int idCount = 0;
    private Collator collator;

    public TableModelThreadedView(TreeTableModelInterface tableModel) {
        super(tableModel);

        enabled = false;

        collator = Collator.getInstance();
    }

    public void toggleView(boolean b) {
        setEnabled(b);

        /*
        getHeaderTableModel().update();
        */
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean b) {
        enabled = b;
    }

    protected String parseSubject(String subject) {
        if ((subject == null) || (subject.length() == 0)) {
            return "";
        }

        int start = 0;
        int length = subject.length();

        boolean done = false;

        try {
            while (!done) {
                done = true;

                if (start >= length) {
                    return "";
                }

                while (subject.charAt(start) <= ' ')
                    start++;

                if ((start < (length - 2)) &&
                        ((subject.charAt(start) == 'r') ||
                        (subject.charAt(start) == 'R')) &&
                        ((subject.charAt(start + 1) == 'e') ||
                        (subject.charAt(start + 1) == 'E'))) {
                    if (subject.charAt(start + 2) == ':') {
                        // skip "Re:"
                        start += 3;
                        done = false;
                    } else if ((start < (length - 2)) &&
                            ((subject.charAt(start + 2) == '[') ||
                            (subject.charAt(start + 2) == '('))) {
                        int i = start + 3;

                        // skip  character in "[|
                        while ((i < length) && (subject.charAt(i) >= ' ') &&
                                (subject.charAt(i) <= '9'))
                            i++;

                        if ((i < (length - 1)) &&
                                ((subject.charAt(i) == ']') ||
                                (subject.charAt(i) == ')')) &&
                                (subject.charAt(i + 1) == ':')) {
                            // skip "]:"
                            start = i + 2;
                            done = false;
                        }
                    }
                }
            }

            int end = length;

            while ((end > start) && (subject.charAt(end - 1) < ' '))
                end--;

            if ((start == 0) && (end == length)) {
                return subject;
            } else {
                return subject.substring(start, end);
            }
        } catch (StringIndexOutOfBoundsException e) {
            e.printStackTrace();

            return subject;
        }
    }

    /*
    protected String parseSubject( String subject )
    {
        String result = subject;

        if ( result == null ) return new String("");

        if ( result.length() == 0 ) return result;


        while ( result.toLowerCase().indexOf("re:") != -1)
            {

                if ( result.toLowerCase().startsWith("re:") )
                {
                    // delete only the leading 3 char
                    result = result.substring( 3, result.length() );
                    result = result.trim();
                }
                else
                {
                    // maybe there es a [nautilus] in front of the re:
                    int index = result.toLowerCase().indexOf("re:");
                    result = result.substring( index+3, result.length() );
                    result = result.trim();
                }

            }

        if ( result.startsWith("[") )
        {
            if ( result.endsWith("]") ) return result;

            int index = result.indexOf("]");
            result = result.substring( index+1, result.length() );
            result = result.trim();
        }



        return result;
    }
    */
    protected String[] parseReferences(String references) {
        //System.out.println("references: "+ references );
        StringTokenizer tk = new StringTokenizer(references, ">");
        String[] list = new String[tk.countTokens()];
        int i = 0;

        while (tk.hasMoreTokens()) {
            String str = (String) tk.nextToken();
            str = str.trim();
            str = str + ">";
            list[i++] = str;

            //System.out.println("reference: "+ str );
        }

        return list;
    }

    protected boolean add(MessageNode node, MessageNode rootNode) {
        ColumbaHeader header = node.getHeader();
        String references = (String) header.get("References");
        String inReply = (String) header.get("In-Reply-To");

        if (inReply != null) {
            inReply = inReply.trim();

            if (hashtable.containsKey(inReply)) {
                //System.out.println("contains: "+ inReply );
                MessageNode parent = (MessageNode) hashtable.get(inReply);
                parent.add(node);

                return true;
            } else {
                return false;
            }
        } else if (references != null) {
            references = references.trim();

            String[] referenceList = parseReferences(references);
            int count = referenceList.length;

            if (count >= 1) {
                // create empty container
                MessageNode parent = null;
                parent = generateDummy(node, 0, referenceList, rootNode);

                if (parent != null) {
                    parent.add(node);

                    return true;
                } else {
                    return false;
                }

                //return true;
            }
        } else {
            return false;
        }

        return false;
    }

    // create tree structure
    protected void thread(MessageNode rootNode) {
        idCount = 0;

        if (rootNode == null) {
            return;
        }

        hashtable = new HashMap();

        // save every message-id in hashtable for later reference
        for (Enumeration enum = rootNode.children(); enum.hasMoreElements();) {
            MessageNode node = (MessageNode) enum.nextElement();
            ColumbaHeader header = node.getHeader();

            String id = (String) header.get("Message-ID");

            if (id == null) {
                id = (String) header.get("Message-Id");
            }

            //System.out.println("id: "+id);
            if (id == null) {
                id = new String("<bogus-id:" + (idCount++) + ">");
            }

            id = id.trim();

            header.set("Message-ID", id);
            hashtable.put(id, node);

            /*
            String subject = (String) header.get("Subject");
            //System.out.println("subject: "+ subject);
            subject = parseSubject(subject);
            node.setParsedSubject(subject);
            */
        }

        /* for each element in the message-header-reference or in-reply-to headerfield:
            - find a container whose message-id matches and add message
               otherwise create empty container
        */
        for (int i = 0; i < rootNode.getChildCount(); i++) {
            MessageNode node = (MessageNode) rootNode.getChildAt(i);
            boolean result = add(node, rootNode);

            if (result) {
                i--;
            }
        }

        // group everything together which is in no group, because
        // of missing in-reply-to or reference headerfield, or
        // because of missing parent reference
        //
        // use parsed subject for grouping
        /*
        for ( int i=0; i<rootNode.getChildCount(); i++ )
        {
            MessageNode node = (MessageNode) rootNode.getChildAt( i );
            String parsedSubject = node.getParsedSubject();


            // do not use vector
            boolean alreadyDec = false;

            for ( int j=0; j<rootNode.getChildCount(); j++ )
            {
                if ( j==i ) continue;

                MessageNode node2 = (MessageNode) rootNode.getChildAt( j );
                String subject2 = node2.getParsedSubject();
                String subject = (String) node2.getMessage().getHeader().get("Subject");

                if ( parsedSubject.equals( subject2 ) )
                {
                    if ( subject.toLowerCase().indexOf("re:") == -1 )
                    {
                        //node.insert( node2, node.getChildCount() );
                        node2.add( node );
                        if ( alreadyDec == false )
                        {
                            i--;
                            alreadyDec = true;
                        }
                    }
                }
            }

        }
        */
        // go through whole tree and sort the siblings after date
        sort(rootNode);
    }

    protected MessageNode generateDummy(MessageNode node, int i,
        String[] referenceList, MessageNode rootNode) {
        MessageNode parent = null;

        /*
        MessageNode child = null;
        for ( int index=i; index<referenceList.length; index++ )
        {

            if ( hashtable.containsKey( referenceList[index].trim() ) == true )
            {
                //System.out.println("reference is in hashtable: "+index);
                parent = (MessageNode) hashtable.get( referenceList[index].trim() );
                continue;
            }
            else
            {
                Message message = new Message();
                message.getHeader().set("Message-ID", referenceList[index].trim() );
                message.getHeader().set("Subject", node.getParsedSubject()+ " (message not available)" );
                child = new MessageNode( message, null );
                child.enableDummy(true);
                hashtable.put( referenceList[index].trim(), child );

                if ( parent != null )
                {
                   parent.add( child );
                }
                else
                {
                    int pos = rootNode.getIndex( node );
                    rootNode.insert( child, pos );
                    //rootNode.add( child );
                }

                parent = child;
            }
        }
        */
        if (hashtable.containsKey(
                    referenceList[referenceList.length - 1].trim())) {
            //System.out.println("reference is in hashtable: "+index);
            parent = (MessageNode) hashtable.get(referenceList[referenceList.length -
                    1].trim());
        }

        return parent;
    }

    /**
     *
     * sort all children after date
     *
     * @param node        root MessageNode
     */
    protected void sort(MessageNode node) {
        for (int i = 0; i < node.getChildCount(); i++) {
            MessageNode child = (MessageNode) node.getChildAt(i);

            //if ( ( child.isLeaf() == false ) && ( !child.getParent().equals( node ) ) )
            if (!child.isLeaf()) {
                // has children
                List v = child.getVector();
                Collections.sort(v,
                    new MessageHeaderComparator(getRealModel().getColumnNumber("Date"),
                        true));

                // check if there are messages marked as recent
                //  -> in case underline parent node
                boolean contains = containsRecentChildren(child);
                child.setHasRecentChildren(contains);
            }
        }
    }

    protected boolean containsRecentChildren(MessageNode parent) {
        for (int i = 0; i < parent.getChildCount(); i++) {
            MessageNode child = (MessageNode) parent.getChildAt(i);

            if (((ColumbaHeader) child.getHeader()).getFlags().getRecent()) {
                // recent found
                ColumbaLogger.log.debug("found recent message");

                return true;
            } else {
                containsRecentChildren(child);
            }
        }

        return false;
    }

    /*
    public boolean manipulateModel(int mode) {
            //System.out.println("threading enabled: "+ isEnabled() );

            if (!isEnabled())
                    return false;

            switch (mode) {
                    case TableModelPlugin.STRUCTURE_CHANGE :
                            {

                                    //System.out.println("starting to thread");

                                    MessageNode rootNode = getHeaderTableModel().getRootNode();

                                    //Vector v = new Vector();

                                    thread(rootNode);

                                    //System.out.println("finished threading");

                                    return true;
                            }

                    case TableModelPlugin.NODES_INSERTED :
                            {
                                    // FIXME

                                    return true;
                            }

            }

            return false;
    }
    */
    public MessageNode addItem(MessageNode child) {
        MessageNode rootNode = getRealModel().getRootNode();
        ColumbaHeader childHeader = child.getHeader();

        String id = (String) childHeader.get("Message-ID");

        if (id == null) {
            id = (String) childHeader.get("Message-Id");
        }

        ;

        if (id == null) {
            id = new String("<bogus-id:" + (idCount++) + ">");
        }

        childHeader.set("Message-ID", id);
        hashtable.put(id, child);

        add(child, rootNode);

        /*
        // we did not find a parent, just group message with subject
        String childSubject = (String) childHeader.get("Subject");
        childSubject = parseSubject( childSubject );
        child.setParsedSubject( childSubject );

        // group everything together
        for ( int i=0; i<rootNode.getChildCount(); i++ )
        {
            MessageNode node = (MessageNode) rootNode.getChildAt( i );
            String subject = node.getParsedSubject();
            if ( subject == null )
            {
                Message message = (Message) node.getUserObject();
                Rfc822Header header = message.getHeader();
                subject = (String) header.get("Subject");

                if ( subject.equals( childSubject ) ) return node;
            }
        }
        */
        return rootNode;

        /*
        Message childMessage = (Message) child.getUserObject();
        Rfc822Header childHeader = childMessage.getHeader();
        String childSubject = (String) childHeader.get("Subject");

        childSubject = parseSubject( childSubject );
        child.setParsedSubject( childSubject );

        // group everything together
        for ( int i=0; i<rootNode.getChildCount(); i++ )
        {

            MessageNode node = (MessageNode) rootNode.getChildAt( i );
            String subject = node.getParsedSubject();
            if ( subject == null )
            {
                Message message = (Message) node.getUserObject();
                Rfc822Header header = message.getHeader();
                subject = (String) header.get("Subject");

                if ( subject == null )
                   subject = new String("");
                else
                   subject = parseSubject( subject );

                node.setParsedSubject( subject );
            }


            if ( childSubject.equals( subject ) ) return node;

        }
        */
    }

    /******************************* implements TableModelModifier *******************/

    /* (non-Javadoc)
     * @see org.columba.mail.gui.table.model.TableModelModifier#modify(java.lang.Object[])
     */
    public void modify(Object[] uids) {
        super.modify(uids);
    }

    /* (non-Javadoc)
     * @see org.columba.mail.gui.table.model.TableModelModifier#remove(java.lang.Object[])
     */
    public void remove(Object[] uids) {
        super.remove(uids);
    }

    /* (non-Javadoc)
             * @see org.columba.mail.gui.table.model.TreeTableModelInterface#set(org.columba.mail.message.HeaderList)
             */
    public void set(HeaderList headerList) {
        super.set(headerList);

        update();
    }

    /* (non-Javadoc)
     * @see org.columba.mail.gui.table.model.TableModelModifier#update()
     */
    public void update() {
        super.update();

        if (isEnabled()) {
            thread(getRootNode());
        }
    }

    /*
    public MessageNode getChildAtRow( int row, JTree tree )
    {
        int index = 0;

        MessageNode rootNode = getHeaderTableModel().getRootNode();

        for ( int i=0; i<rootNode.getChildCount(); i++ )
        {
            MessageNode node = (MessageNode) rootNode.getChildAt( i );


            if ( node.isLeaf() == true )
            {

            }


        }

        return rootNode;
    }
    */
    class MessageHeaderComparator implements Comparator {
        protected int column;
        protected boolean ascending;

        public MessageHeaderComparator(int sortCol, boolean sortAsc) {
            column = sortCol;
            ascending = sortAsc;
        }

        public int compare(Object o1, Object o2) {
            //Integer int1 = (Integer) o1;
            //Integer int2 = (Integer) o2;
            MessageNode node1 = (MessageNode) o1;
            MessageNode node2 = (MessageNode) o2;

            //Message message1 = folder.get( int1.intValue() );
            //Message message1 = (Message) node1.getUserObject();
            //Message message2 = folder.get( int2.intValue() );
            //Message message2 =(Message)  node2.getUserObject();
            ColumbaHeader header1 = node1.getHeader();
            ColumbaHeader header2 = node2.getHeader();

            if ((header1 == null) || (header2 == null)) {
                return 0;
            }

            int result = 0;

            String columnName = getRealModel().getColumnName(column);

            if (columnName.equals("Date")) {
                Date d1 = (Date) header1.get("columba.date");
                Date d2 = (Date) header2.get("columba.date");

                if ((d1 == null) || (d2 == null)) {
                    result = 0;
                } else {
                    result = d1.compareTo(d2);
                }
            } else {
                Object item1 = header1.get(columnName);
                Object item2 = header2.get(columnName);

                if ((item1 != null) && (item2 == null)) {
                    result = 1;
                } else if ((item1 == null) && (item2 != null)) {
                    result = -1;
                } else if ((item1 == null) && (item2 == null)) {
                    result = 0;
                }
                else if (item1 instanceof String) {
                    result = collator.compare((String) item1, (String) item2);
                }
            }

            if (!ascending) {
                result = -result;
            }

            return result;
        }

        public boolean equals(Object obj) {
            if (obj instanceof MessageHeaderComparator) {
                MessageHeaderComparator compObj = (MessageHeaderComparator) obj;

                return (compObj.column == column) &&
                (compObj.ascending == ascending);
            }

            return false;
        }
    }
}