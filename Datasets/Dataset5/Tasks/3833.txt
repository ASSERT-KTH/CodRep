if (nameText.length() == 0) {

/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package dom.traversal;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Enumeration;
import java.util.Hashtable;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JFrame;
import javax.swing.JList;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.event.TreeSelectionEvent;
import javax.swing.event.TreeSelectionListener;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.MutableTreeNode;
import javax.swing.tree.TreeNode;
import javax.swing.tree.TreePath;
import javax.swing.tree.TreeSelectionModel;

import org.apache.xerces.parsers.DOMParser;
import org.w3c.dom.DOMException;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.traversal.DocumentTraversal;
import org.w3c.dom.traversal.NodeFilter;
import org.w3c.dom.traversal.NodeIterator;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import ui.DOMTreeFull;

/** This class shows a DOM Document in a JTree, and presents controls
 *  which allow the user to create and view the progress of a NodeIterator
 *  in the DOM tree.
 */
public class IteratorView 
    extends JFrame 
    implements ActionListener {
    
    private static final long serialVersionUID = 3256726186452662580L;
    
    Document document;
    TreeNode lastSelected;
    DOMParser parser;
    JTextArea messageText;
    JScrollPane messageScroll;
    DOMTreeFull jtree;
    NodeIterator iterator;
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
    
    Hashtable treeNodeMap = new Hashtable();
    
    
    /** main */
    public static void main (String args[]) {

        if (args.length > 0) {
            String filename = args[0];
            try {
                IteratorView frame = new IteratorView(filename) ;
                frame.addWindowListener(new java.awt.event.WindowAdapter() {
                 public void windowClosing(java.awt.event.WindowEvent e) {
                     System.exit(0);
                 }
                });
                frame.setSize(640, 480);
                frame.setVisible(true);
                } catch (Exception e) {
                    e.printStackTrace(System.err);
                }
        }
    }
    
    /** Constructor */
    public IteratorView (String filename) {
        super("IteratorView: "+filename);
        try {
            parser = new DOMParser();
            parser.setFeature("http://apache.org/xml/features/dom/defer-node-expansion", true);
            parser.setFeature("http://apache.org/xml/features/continue-after-fatal-error", true);
            Errors errors = new Errors();
            parser.setErrorHandler(errors);
            parser.parse(filename);
            document = parser.getDocument();
            
            if (!document.isSupported("Traversal", "2.0")) {
                // This cannot happen with ou DOMParser...
                throw new RuntimeException("This DOM Document does not support Traversal");
            }

            // jtree  UI setup
            jtree = new DOMTreeFull((Node)document);
            jtree.getSelectionModel().setSelectionMode
                (TreeSelectionModel.SINGLE_TREE_SELECTION);
            jtree.setRootVisible(false);

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
            
            
            //expandTree();
            
                        
            // controls
            
            //iterate panel
            JPanel iteratePanel = new JPanel();
            iteratePanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Iterate"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            
            prevButton = new JButton("Previous");
            iteratePanel.add(prevButton);
            prevButton.addActionListener(this);
            
            nextButton = new JButton("Next");
            iteratePanel.add(nextButton);
            nextButton.addActionListener(this);
        
            //DOM tree panel
            JPanel domPanel = new JPanel();
            domPanel.setLayout(new BorderLayout());
            domPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Selected Node"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            
            removeButton = new JButton("Remove Selected Node");
            domPanel.add(removeButton, BorderLayout.NORTH);
            removeButton.addActionListener(this);
            
            addButton = new JButton("Add Text Node");
            addText = new JTextField(10);
            domPanel.add(addButton, BorderLayout.CENTER);
            domPanel.add(addText, BorderLayout.SOUTH);
            addButton.addActionListener(this);
         
            // iterator settings
            JPanel settingsPanel = new JPanel();
            settingsPanel.setLayout(new BorderLayout());
            settingsPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Iterator Settings"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            JPanel iteratorPanel = new JPanel();
            newIterator = new JButton("createNodeIterator");
            expandERs = new JCheckBox("expandEntityReferences");
            iteratorPanel.add(newIterator);
            expandERs.setSelected(true);
            iteratorPanel.add(expandERs);
            settingsPanel.add(iteratorPanel, BorderLayout.NORTH);
            newIterator.addActionListener(this);
    
            JPanel whatPanel = new JPanel();
            whatPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("whatToShow"),
                BorderFactory.createEmptyBorder(4, 4, 4, 4)
                ));
            whatToShow = new JList(DOMTreeFull.whatArray);
            JScrollPane whatScroll = 
            new JScrollPane(whatToShow) {
                    private static final long serialVersionUID = 3546357344813724213L;
                    public Dimension getPreferredSize(){
                        return new Dimension(200, 75 );
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
            
            settingsPanel.add(whatPanel, BorderLayout.WEST);
            settingsPanel.add(filterPanel, BorderLayout.EAST);
            

            // Listen for when the selection changes, call nodeSelected(node)
            whatToShow.addListSelectionListener(
                new ListSelectionListener() {
                    public void valueChanged(ListSelectionEvent e) {
                        // do nothing on selection...
                    }
                }
            );
            
            
            JPanel controlsPanel = new JPanel(new BorderLayout());
            JPanel buttonsPanel = new JPanel(new BorderLayout());
            buttonsPanel.add(iteratePanel, BorderLayout.NORTH);
            buttonsPanel.add(domPanel, BorderLayout.SOUTH);
            controlsPanel.add(buttonsPanel, BorderLayout.WEST);
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
            mainPanel.add(controlsPanel, BorderLayout.NORTH);
            mainPanel.add(treeScroll, BorderLayout.CENTER);
            mainPanel.add(messagePanel, BorderLayout.SOUTH);
            getContentPane().add(mainPanel);
            
            Hashtable errorNodes = errors.getErrorNodes();
            Enumeration elements = errorNodes.elements();
            while (elements.hasMoreElements()) {
                //*** append errors to messageText
                messageText.append( (String)elements.nextElement());
            }    
            
            // This cast must work, because we have tested above
            // with document.isSupported("Traversal")
            iterator = ((DocumentTraversal)document).
                createNodeIterator(
                    document, 
                    NodeFilter.SHOW_ALL, 
                    new NameNodeFilter(),
                    true);
            
        } catch (Exception e) {
            e.printStackTrace(System.err);
        }
    }
    
    public void actionPerformed(ActionEvent e) {
        
        if (e.getSource() == newIterator) {
            Node node = document;
            
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
            
            if (iterator !=null) iterator.detach();
            boolean expand = expandERs.isSelected();
            iterator = ((DocumentTraversal)document).
                createNodeIterator(
                    node, 
                    (short)mask, 
                    nameNodeFilter,
                    expand);
            setMessage("doc.createNodeIterator("+ 
                        " root="+node+
                        ", whatToShow="+mask+
                        ", match="+matched+
                        ", name="+nameText+")"
                        );
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
        if (e.getSource() == nextButton) {          
            Node node = iterator.nextNode();
            if (node==null) {
                setMessage("iterator.nextNode() == null");
                return;
            } 
            
            setMessage("iterator.nextNode() == "+node);

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
            return;
        } 
        
        if (e.getSource() == prevButton) {          
            Node node = iterator.previousNode();
            if (node==null) {
                setMessage("iterator.previousNode() == null");
                return;
            } 
            
            setMessage("iterator.previousNode() == "+node);

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
        
        System.out.println("nodeSelected.node="+node);
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