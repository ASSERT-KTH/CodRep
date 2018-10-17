import org.columba.addressbook.config.AdapterNode;

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
package org.columba.core.config;

import java.util.Enumeration;
import java.util.Vector;

import javax.swing.event.TreeModelEvent;
import javax.swing.event.TreeModelListener;
import javax.swing.tree.TreeModel;
import javax.swing.tree.TreePath;

import org.columba.addressbook.config.*;
import org.w3c.dom.Document;

public class DomToTreeModelAdapter implements TreeModel 
{
    Document document;
    
    public DomToTreeModelAdapter(Document document)
    {
	
	this.document = document;
	
    }

        /* ===================================================================== */
        // methods for TreeModel implementation

    
    public Object  getRoot() 
    {
	
	return new AdapterNode(document);
    }
    
    public boolean isLeaf(Object aNode) 
    {
	// Determines whether the icon shows up to the left.
	// Return true for any node with no children
	AdapterNode node = (AdapterNode) aNode;
	if (node.getChildCount() > 0) return false;
	return true;
    }
    
    public int getChildCount(Object parent) 
    {
        AdapterNode node = (AdapterNode) parent;
        return node.getChildCount();
    }
    
    public Object getChild(Object parent, int index) 
    {
        AdapterNode node = (AdapterNode) parent;
        return node.getChild(index);
    }

    public int getIndexOfChild(Object parent, Object child) 
    {
        AdapterNode node = (AdapterNode) parent;
        return node.getIndex((AdapterNode) child);
    }
    
    public void valueForPathChanged(TreePath path, Object newValue) 
    {
    }

	/*
	 * Use these methods to add and remove event listeners.
	 * (Needed to satisfy TreeModel interface, but not used.)
	 */
    private Vector listenerList = new Vector();

    public void addTreeModelListener(TreeModelListener listener) 
    {
        if ( listener != null 
             && ! listenerList.contains( listener ) ) 
        {
            listenerList.addElement( listener );
        }
    }
    
    public void removeTreeModelListener(TreeModelListener listener) 
    {
        if ( listener != null ) 
        {
            listenerList.removeElement( listener );
        }
    }


        /* ==================================================================================== */
        // TreeModelEvents

      public void fireTreeNodesChanged( TreeModelEvent e ) {
        Enumeration listeners = listenerList.elements();
        while ( listeners.hasMoreElements() ) {
          TreeModelListener listener = 
            (TreeModelListener)listeners.nextElement();
          listener.treeNodesChanged( e );
        }
      } 
      public void fireTreeNodesInserted( TreeModelEvent e ) {
        Enumeration listeners = listenerList.elements();
        while ( listeners.hasMoreElements() ) {
           TreeModelListener listener =
             (TreeModelListener)listeners.nextElement();
           listener.treeNodesInserted( e );
        }
      }   
      public void fireTreeNodesRemoved( TreeModelEvent e ) {
        Enumeration listeners = listenerList.elements();
        while ( listeners.hasMoreElements() ) {
          TreeModelListener listener = 
            (TreeModelListener)listeners.nextElement();
          listener.treeNodesRemoved( e );
        }
      }   
      public void fireTreeStructureChanged( TreeModelEvent e ) {
        Enumeration listeners = listenerList.elements();
        while ( listeners.hasMoreElements() ) {
          TreeModelListener listener =
            (TreeModelListener)listeners.nextElement();
          listener.treeStructureChanged( e );
        }
      }
    }