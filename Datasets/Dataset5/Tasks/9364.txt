if (!document.isSupported("Traversal", "2.0")) {

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:  
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */
package dom.traversal;

import java.awt.*;
import java.awt.event.*;
import java.util.Hashtable;
import java.util.Enumeration;
import javax.swing.*;
import javax.swing.tree.*;
import javax.swing.event.*;
import org.apache.xerces.parsers.*;
import org.w3c.dom.*;
import org.w3c.dom.traversal.*;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import ui.DOMTreeFull;

/** This class shows a DOM Document in a JTree, and presents controls
 *  which allow the user to create and view the progress of a TreeWalker
 *  in the DOM tree.
 */
public class TreeWalkerView 
    extends JFrame 
    implements ActionListener {

    Document document;
    TreeNode lastSelected;
    DOMParser parser;
    JTextArea messageText;
    JScrollPane messageScroll;
    DOMTreeFull jtree;
    TreeWalker treeWalker;
    NameNodeFilter nameNodeFilter;
    
    JButton nextButton;
    JButton prevButton;
    JButton removeButton;
    JButton addButton;
    JTextField addText;
    JButton newIterator;
    JList whatToShow;
    JCheckBox match;
    JTextField nameFilter;
   
    // treeWalker specific buttons    
    JButton parentButton;
    JButton nextSiblingButton;
    JButton previousSiblingButton;
    JButton firstChildButton;
    JButton lastChildButton;
    JButton currentButton;
    
    String whatArray[] = new String [] { 
            "ALL",
            "ELEMENT",
            "ATTRIBUTE",
            "TEXT",
            "CDATA_SECTION",
            "ENTITY_REFERENCE",
            "ENTITY",
            "PROCESSING_INSTRUCTION", 
            "COMMENT", 
            "DOCUMENT", 
            "DOCUMENT_TYPE",
            "DOCUMENT_FRAGMENT",
            "NOTATION" 
            };
    JCheckBox expandERs;
    
    
    /** main */
    public static void main (String args[]) {

        if (args.length > 0) {
            String filename = args[0];
            try {
                TreeWalkerView frame = new TreeWalkerView(filename) ;
                frame.addWindowListener(new java.awt.event.WindowAdapter() {
                 public void windowClosing(java.awt.event.WindowEvent e) {
                     System.exit(0);
                 }
                });
                frame.setSize(640, 700);
                frame.setVisible(true);
                } catch (Exception e) {
                    e.printStackTrace(System.err);
                }
        }
    }
    
    Hashtable treeNodeMap = new Hashtable();

    /** Constructor */
    public TreeWalkerView (String filename) {
        super("TreeWalkerView: "+filename);
        try {
            parser = new DOMParser();
            parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", true);
            parser.setFeature("http://apache.org/xml/features/continue-after-fatal-error", true);
            Errors errors = new Errors();
            parser.setErrorHandler(errors);
            parser.parse(filename);
            document = parser.getDocument();
            
            if (!document.supports("Traversal", "2.0")) {
                // This cannot happen with the DOMParser...
                throw new RuntimeException("This DOM Document does not support Traversal");
            
            }

            // jtree  UI setup
            jtree = new DOMTreeFull((Node)document);
            jtree.getSelectionModel().setSelectionMode
                (TreeSelectionModel.SINGLE_TREE_SELECTION);

            // Listen for when the selection changes, call nodeSelected(node)
            jtree.addTreeSelectionListener(
                new TreeSelectionListener() {
                    public void valueChanged(TreeSelectionEvent e) {
                        TreePath path = (TreePath)e.getPath(); 
                        TreeNode treeNode = (TreeNode)path.getLastPathComponent();
                        if(jtree.getSelectionModel().isPathSelected(path))
                                nodeSelected(treeNode);
                    }
                }
            );
            
            //            
            // controls
            //
            
            BorderLayout borderLayout = new BorderLayout();
            
            //iterate panel
            JPanel iteratePanel = new JPanel();
            iteratePanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Document Order Traversal"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            
            prevButton = new JButton("Previous");
            iteratePanel.add(prevButton);
            prevButton.addActionListener(this);
            
            nextButton = new JButton("Next");
            iteratePanel.add(nextButton);
            nextButton.addActionListener(this);
        
            //walkerPanel
            JPanel walkerPanel = new JPanel();
            walkerPanel.setLayout(new BorderLayout());
            walkerPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Walk"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            
            parentButton = new JButton("Parent");
            walkerPanel.add(parentButton, BorderLayout.NORTH);
            parentButton.addActionListener(this);
           
            
            JPanel childPanel = new JPanel();
            firstChildButton = new JButton("First Child");
            childPanel.add(firstChildButton);
            firstChildButton.addActionListener(this);
   
            lastChildButton = new JButton("Last Child");
            childPanel.add(lastChildButton);
            lastChildButton.addActionListener(this);
            walkerPanel.add(childPanel, BorderLayout.SOUTH);
            
            nextSiblingButton = new JButton("Next Sibling");
            walkerPanel.add(nextSiblingButton, BorderLayout.EAST);
            nextSiblingButton.addActionListener(this);
            
            previousSiblingButton = new JButton("Previous Sibling");
            walkerPanel.add(previousSiblingButton, BorderLayout.WEST);
            previousSiblingButton.addActionListener(this);
            
            //DOM tree panel
            JPanel domPanel = new JPanel();
            domPanel.setLayout(new BorderLayout());
            domPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Selected Node"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            
            JPanel buttonPanel = new JPanel();
            currentButton = new JButton("Current");
            buttonPanel.add(currentButton);
            currentButton.addActionListener(this);
   
            removeButton = new JButton("Remove");
            buttonPanel.add(removeButton);
            removeButton.addActionListener(this);
            
            addButton = new JButton("Append Text");
            addText = new JTextField(10);
            buttonPanel.add(addButton);
            domPanel.add(buttonPanel, BorderLayout.NORTH);
            domPanel.add(addText, BorderLayout.CENTER);
            addButton.addActionListener(this);
         
            // treeWalker settings
            JPanel settingsPanel = new JPanel();
            settingsPanel.setLayout(new BorderLayout());
            settingsPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Filter Settings"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            JPanel treeWalkerPanel = new JPanel();
            treeWalkerPanel.setLayout(new BorderLayout());
            
            newIterator = new JButton("createTreeWalker");
            treeWalkerPanel.add(newIterator, BorderLayout.NORTH);
            expandERs = new JCheckBox("expandEntityReferences");
            expandERs.setSelected(true);
            treeWalkerPanel.add(expandERs, BorderLayout.SOUTH);
            settingsPanel.add(treeWalkerPanel, BorderLayout.NORTH);
            newIterator.addActionListener(this);
    
            JPanel whatPanel = new JPanel();
            whatPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("whatToShow"),
                BorderFactory.createEmptyBorder(0, 0, 0, 0)
                ));
            whatToShow = new JList(whatArray);
            JScrollPane whatScroll = 
            new JScrollPane(whatToShow) {
                    public Dimension getPreferredSize(){
                        return new Dimension(200, 65 );
                    }
                };
            
            whatPanel.add(whatScroll);
            
            
            JPanel filterPanel = new JPanel();
            filterPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("NodeNameFilter"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            filterPanel.setLayout(new BorderLayout());
            match = new JCheckBox("match/ignore node name", true);
            nameFilter = new JTextField(10);
            filterPanel.add(match, BorderLayout.NORTH);
            filterPanel.add(nameFilter, BorderLayout.SOUTH);
            
            settingsPanel.add(treeWalkerPanel, BorderLayout.NORTH);
            settingsPanel.add(whatPanel, BorderLayout.CENTER);
            settingsPanel.add(filterPanel, BorderLayout.SOUTH);
            

            // Listen for when the selection changes, call nodeSelected(node)
            whatToShow.addListSelectionListener(
                new ListSelectionListener() {
                    public void valueChanged(ListSelectionEvent e) {
                        // do nothing on selection...
                    }
                }
            );
            
            
            JPanel controlsPanel = new JPanel(new BorderLayout());
            controlsPanel.setFont(new Font("Dialog", Font.PLAIN, 8));
            JPanel buttonsPanel = new JPanel(new BorderLayout());
            buttonsPanel.add(iteratePanel, BorderLayout.NORTH);
            buttonsPanel.add(walkerPanel, BorderLayout.CENTER);
            buttonsPanel.add(domPanel, BorderLayout.SOUTH);
            controlsPanel.add(buttonsPanel, BorderLayout.NORTH);
            controlsPanel.add(settingsPanel, BorderLayout.CENTER);
            
            controlsPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Controls"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
                
                
            // tree panel    
            JPanel treePanel = new JPanel(new BorderLayout());
                
            JScrollPane treeScroll = new JScrollPane(jtree) ;
            treeScroll.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Tree View"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));

            // message text UI setup
            messageText = new JTextArea(3,5);

            JPanel messagePanel = new JPanel(new BorderLayout());
            messageScroll = new JScrollPane(messageText);
            messagePanel.add(messageScroll);
            messagePanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Messages"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            
            JPanel mainPanel = new JPanel();
            mainPanel.setLayout(new BorderLayout());
            mainPanel.add(controlsPanel, BorderLayout.EAST);
            mainPanel.add(treeScroll, BorderLayout.CENTER);
            mainPanel.add(messagePanel, BorderLayout.SOUTH);
            getContentPane().add(mainPanel);
            
            Hashtable errorNodes = errors.getErrorNodes();
            Enumeration elements = errorNodes.elements();
            while (elements.hasMoreElements()) {
                //*** append errors to messageText
                messageText.append( (String)elements.nextElement());
            }    
            
            boolean expand = expandERs.isSelected();
            treeWalker = ((DocumentTraversal)document).
                createTreeWalker(
                    document, 
                    NodeFilter.SHOW_ALL, 
                    new NameNodeFilter(),
                    expand);
            
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }
    }
               
    public void actionPerformed(ActionEvent e) {
        
        if (e.getSource() == newIterator) {
            
            TreeNode treeNode = (TreeNode)jtree.getLastSelectedPathComponent();
            if (treeNode == null) {
                messageText.append("Must select a tree component.");
                return;
            }
            
            Node node = jtree.getNode(treeNode);
            if (node == null) {
                setMessage("No current Node in TreeNode: "+node);
            }
            
            // whatToShow section
            int  [] indices = whatToShow.getSelectedIndices();
            int mask = 0x0;
            for (int i = 0; i < indices.length; i++) {
                if (indices[i] == 0) {
                    mask = 0xFFFF;
                    break;
                } else {
                    mask = mask | 1<<indices[i]-1;
                }
            }
            
            // filter section
            String nameText = nameFilter.getText();
            boolean matched = match.isSelected();
            if (nameNodeFilter==null) {
                nameNodeFilter = new NameNodeFilter();
            }
            if (nameText.equals("")) {
                setMessage("NodeNameFilter name is \"\". Assuming null.");
                nameText = null;
            }
            nameNodeFilter.setName(nameText);
            nameNodeFilter.setMatch(matched);
            
            // expand Entity References?
            boolean expand = expandERs.isSelected();
            
            treeWalker = ((DocumentTraversal)document).
                createTreeWalker(
                    node, 
                    mask, 
                    nameNodeFilter,
                    expand);
            setMessage("createTreeWalker:"+ 
                        " root="+node+
                        ", whatToShow="+mask+
                        ", match="+matched+
                        ", name="+nameText
                        );
            return;
            
        } 
        
        if (e.getSource() == currentButton) {
            
            TreeNode treeNode = (TreeNode)jtree.getLastSelectedPathComponent();
            if (treeNode == null) {
                messageText.append("Must select a tree component.");
                return;
            }
            
            Node node = jtree.getNode(treeNode);
            if (node == null) {
                setMessage("No current Node in TreeNode: "+node);
            }
            treeWalker.setCurrentNode(node);
            return;
            
        }
        if (e.getSource() == addButton) {
            
            String text = addText.getText();
            
            if (text==null) return;
            
            TreeNode treeNode = (TreeNode)jtree.getLastSelectedPathComponent();
            if (treeNode == null) {
                messageText.append("Must select a tree component to add a child to it.");
                return;
            }
            TreePath path = new TreePath(
                    ((DefaultTreeModel)jtree.getModel()).getPathToRoot(treeNode));
            if (path == null) {
                setMessage("Could not create a path.");
                return;
            }
            if(!jtree.getSelectionModel().isPathSelected(path))
                return;
            Node node = jtree.getNode(treeNode);
            Node textNode = document.createTextNode(text);
            try {
                node.appendChild(textNode);
            } catch (DOMException dome) {
                setMessage("DOMException:"+dome.code+", "+dome);
                return;
            }
            ((DOMTreeFull.Model)jtree.getModel()).insertNode(textNode, (MutableTreeNode)treeNode);
            
            return;
        }
        
        if (e.getSource() == removeButton) {

            /** If the node is not selected don't remove. */
            TreeNode treeNode = (TreeNode)jtree.getLastSelectedPathComponent();
            if (treeNode == null) {
                messageText.append("Must select a tree component to remove it.");
                return;
            }
            TreePath path = new TreePath(
                    ((DefaultTreeModel)jtree.getModel()).getPathToRoot(treeNode));
            if (path == null) {
                setMessage("Could not create a path.");
                return;
            }
            if(!jtree.getSelectionModel().isPathSelected(path))
                return;
            Node node = jtree.getNode(treeNode);
            if (node == null) return;
            Node parent = node.getParentNode();
            if (parent == null) return;

            parent.removeChild(node);
    
            ((DefaultTreeModel)jtree.getModel()).removeNodeFromParent((MutableTreeNode)treeNode);
            return;
        } 
        
        if (e.getSource() == previousSiblingButton) {          
            Node node = treeWalker.previousSibling();
            handleButton(node, "previousSibling()");
            return;
        } 
        
        if (e.getSource() == firstChildButton) {          
            Node node = treeWalker.firstChild();
            handleButton(node, "firstChild()");
            return;
        } 
        
        if (e.getSource() == lastChildButton) {          
            Node node = treeWalker.lastChild();
            handleButton(node, "lastChild()");
            return;
        } 
        
        if (e.getSource() == nextSiblingButton) {          
            Node node = treeWalker.nextSibling();
            handleButton(node, "nextSibling()");
            return;
        } 
        
        if (e.getSource() == parentButton) {          
            Node node = treeWalker.parentNode();
            handleButton(node, "parentNode()");
            return;
        } 
        
        if (e.getSource() == nextButton) {          
            Node node = treeWalker.nextNode();
            handleButton(node, "nextNode()");
            return;
        } 
        
        if (e.getSource() == prevButton) {          
            Node node = treeWalker.previousNode();
            handleButton(node, "previousNode()");
            return;
        }
        
    }
    
    /** handle a button press: output messages and select node. */
    void handleButton( Node node, String function) {
        
        setMessage("treeWalker."+function+" == "+node);
   
        if (node==null) return;

        TreeNode treeNode = jtree.getTreeNode(node);
        if (treeNode == null) {
            setMessage("No JTree TreeNode for Node name:" + node.getNodeName());
            return;
        }
            
        TreePath path = new TreePath(
                ((DefaultTreeModel)jtree.getModel()).getPathToRoot(treeNode));
        jtree.requestFocus();
        jtree.setSelectionPath(path);
        jtree.scrollPathToVisible(path);
    }
    
    /** Helper function to set messages */
    void setMessage(String string) {
        messageText.selectAll();
        messageText.cut();
        messageText.append(string);
        messageText.setCaretPosition(0);
    }
        
    /** called when our JTree's nodes are selected.
     */
    void nodeSelected(TreeNode treeNode) {

        lastSelected = treeNode;
        Node node = jtree.getNode(treeNode);
        
        if (node == null) return;
                            
        setMessage(DOMTreeFull.toString(node));
    }
    
    /** Utility function to expand the jtree */
    void expandTree() {
        for (int i = 0; i < jtree.getRowCount(); i++) {
            jtree.expandRow(i);
        }
    }
    
    class Errors implements ErrorHandler {

        Hashtable errorNodes = new Hashtable();

        public void warning(SAXParseException ex) {
            store(ex, "[Warning]");
        }

        public void error(SAXParseException ex) {
            store(ex, "[Error]");
        }

        public void fatalError(SAXParseException ex) throws SAXException {
            store(ex, "[Fatal Error]");
        }

        public Hashtable getErrorNodes() {
            return errorNodes;
        }

        public Object getError(Node node) {
            return errorNodes.get(node);
        }

        public void clearErrors() {
            errorNodes.clear();
        }

        void store(SAXParseException ex, String type) {

            // build error text
            String errorString= type+" at line number, "+ex.getLineNumber()
                +": "+ex.getMessage()+"\n";

            Node currentNode = null;
            try {
                currentNode = (Node)parser.getProperty("http://apache.org/xml/properties/dom-node");
            } catch (SAXException se) {
                System.err.println(se.getMessage());
                return;
            }
            if (currentNode == null) return;

            // accumulate any multiple errors per node in the Hashtable.
            String previous = (String) errorNodes.get(currentNode);
            if (previous != null)
                errorNodes.put(currentNode, previous +errorString);
            else
                errorNodes.put(currentNode, errorString);
        }
    }
    
}