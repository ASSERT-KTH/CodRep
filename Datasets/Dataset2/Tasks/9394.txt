CachedHeaderfields.getUserDefinedHeaderfields();

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
package org.columba.mail.folderoptions;

import java.awt.Dimension;
import java.util.Enumeration;

import javax.swing.table.DefaultTableColumnModel;
import javax.swing.table.TableColumn;

import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;
import org.columba.mail.folder.Folder;
import org.columba.mail.folder.headercache.CachedHeaderfields;
import org.columba.mail.gui.frame.MailFrameMediator;
import org.columba.mail.gui.frame.TableViewOwner;
import org.columba.mail.gui.table.TableController;
import org.columba.mail.gui.table.TableView;

/**
 * Stores all visible columns of the message list.
 *
 * @author fdietz
 */
public class ColumnOptionsPlugin extends AbstractFolderOptionsPlugin {

	public final static String[] COLUMNS=
		{
			"Status",
			"Attachment",
			"Flagged",
			"Priority",
			"Subject",
			"From",
			"Date",
			"Size",
			"Spam" };

	/**
	 * Constructor
	 *
	 * @param mediator      mail frame mediator
	 */
	public ColumnOptionsPlugin(MailFrameMediator mediator) {
		super("columns", mediator);
	}

	/**
	 * Get list of available columns.
	 * 
	 * @return		string array of columns
	 */
	public static String[] getColumns() {
		String[] userDefined=
			CachedHeaderfields.getUserDefinedHeaderfieldArray();

		String[] stringList= new String[userDefined.length + COLUMNS.length];
		int index= 0;
		for (int i= 0; i < COLUMNS.length; i++) {
			stringList[i]= COLUMNS[i];
			index= i;
		}

		index++;
		
		for (int i= 0; i < userDefined.length; i++) {
			stringList[index + i]= userDefined[i];
		}

		return stringList;

	}

	/**
	 * Find xml element with attribute name.
	 * 
	 * @param parent        parent element
	 * @param name          name of attribute
	 * @return              child element
	 */
	private XmlElement findColumn(XmlElement parent, String name) {
		for (int i= 0; i < parent.count(); i++) {
			XmlElement child= parent.getElement(i);

			if (child.getAttribute("name").equals(name)) {
				return child;
			}
		}

		return null;
	}

	/**
	 * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#saveOptionsToXml(org.columba.mail.folder.Folder)
	 */
	public void saveOptionsToXml(Folder folder) {
		XmlElement columns= getConfigNode(folder);

		TableController tableController=
			((TableViewOwner) getMediator()).getTableController();
		TableView view= tableController.getView();

		// for each column
		int c= view.getColumnCount();

		Enumeration enum= view.getColumnModel().getColumns();

		// remove all child nodes
		columns.removeAllElements();

		while (enum.hasMoreElements()) {
			TableColumn tc= (TableColumn) enum.nextElement();
			String name= (String) tc.getHeaderValue();

			XmlElement column= new XmlElement("column");
			column.addAttribute("name", name);

			// save width
			int size= tc.getWidth();
			column.addAttribute("width", Integer.toString(size));

			columns.addElement(column);

		}
	}

	/**
	 * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#loadOptionsFromXml(org.columba.mail.folder.Folder)
	 */
	public void loadOptionsFromXml(Folder folder) {
		XmlElement columns= getConfigNode(folder);

		TableController tableController=
			((TableViewOwner) getMediator()).getTableController();
		TableView view= tableController.getView();

		// remove all columns from table model
		tableController.getHeaderTableModel().clearColumns();

		// remove all columns for column model
		view.setColumnModel(new DefaultTableColumnModel());

		// add columns
		for (int i= 0; i < columns.count(); i++) {
			XmlElement column= columns.getElement(i);
			DefaultItem columnItem= new DefaultItem(column);

			String name= columnItem.get("name");
			int size= columnItem.getInteger("width");
			//int position= columnItem.getInteger("position");

			// add column to table model
			tableController.getHeaderTableModel().addColumn(name);

			// add column to JTable column model
			TableColumn tc= view.createTableColumn(name, size);

			//tc.setModelIndex(position);
			tc.setModelIndex(i);

			// resize column width
			tc.setPreferredWidth(size);

			view.addColumn(tc);

		}

		// for some weird reason the table loses its inter-cell spacing
		// property, when changing the underlying column model
		// -> setting this to (0,0) again
		view.setIntercellSpacing(new Dimension(0, 0));

	}

	/**
	   * @see org.columba.mail.folderoptions.AbstractFolderOptionsPlugin#createDefaultElement()
	   */
	public XmlElement createDefaultElement(boolean global) {
		XmlElement columns= super.createDefaultElement(global);

		// these are the items, enabled as default
		columns.addElement(createColumn("Status", "23"));
		columns.addElement(createColumn("Attachment", "23"));
		columns.addElement(createColumn("Flagged", "23"));
		columns.addElement(createColumn("Priority", "23"));
		columns.addElement(createColumn("Subject", "200"));
		columns.addElement(createColumn("From", "100"));
		columns.addElement(createColumn("Date", "100"));
		columns.addElement(createColumn("Size", "50"));
		columns.addElement(createColumn("Spam", "23"));

		return columns;
	}

	/**
	 * Create new XmlElement with custom attributes.
	 *
	 * @param name      name of column
	 * @param width     column width
	 * @param position  column position
	 * @return          parent xml element
	 */
	private static XmlElement createColumn(String name, String width) {
		XmlElement column= new XmlElement("column");
		column.addAttribute("name", name);
		column.addAttribute("width", width);

		return column;
	}
}