Boolean b = Boolean.valueOf(((JCheckBox) component).isSelected());

/*
 * Created on 07.08.2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.core.gui.plugin;

import java.awt.Component;

import javax.swing.AbstractCellEditor;
import javax.swing.JCheckBox;
import javax.swing.JTable;
import javax.swing.SwingConstants;
import javax.swing.table.TableCellEditor;

/**
 * @author frd
 *
 * To change the template for this generated type comment go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
public class EnabledEditor
	extends AbstractCellEditor
	implements TableCellEditor {

	JCheckBox component = new JCheckBox();

	PluginNode currentNode;

	/**
	 * 
	 */
	public EnabledEditor() {

		component.setHorizontalAlignment(SwingConstants.CENTER);
		
	}
	
	public int getClickCountToStart() {
		return 1;
	}

	//	This method is called when a cell value is edited by the user.
	public Component getTableCellEditorComponent(
		JTable table,
		Object value,
		boolean isSelected,
		int rowIndex,
		int vColIndex) {

		currentNode = (PluginNode) value;

		// Configure the component with the specified value
		 ((JCheckBox) component).setSelected(currentNode.isEnabled());

		if (isSelected) {

			((JCheckBox) component).setBackground(
				table.getSelectionBackground());
		} else {

			((JCheckBox) component).setBackground(table.getBackground());

		}

		// Return the configured component
		return component;
	}

	// This method is called when editing is completed.
	// It must return the new value to be stored in the cell.
	public Object getCellEditorValue() {
		
		Boolean b = new Boolean(((JCheckBox) component).isSelected());
		
		// enable/disable tree node
		currentNode.setEnabled(b.booleanValue());
		
		/*
		// enable/disable plugin
		String id = currentNode.getId();

		MainInterface.pluginManager.setEnabled(id, b.booleanValue());
		*/
		
		System.out.println("cell-editor="+b);
		
		return b;
	}
	
	public Component getComponent()
	{
		return component;
	}
	
	
}