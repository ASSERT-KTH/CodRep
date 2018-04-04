childNode.setEnabled(Boolean.valueOf(enabled).booleanValue());

/*
 * Created on 06.08.2003
 *
 * To change the template for this generated file go to
 * Window>Preferences>Java>Code Generation>Code and Comments
 */
package org.columba.core.gui.plugin;

import java.util.HashMap;
import java.util.List;
import java.util.ListIterator;
import java.util.Map;

import javax.swing.JCheckBox;
import javax.swing.table.TableColumn;
import javax.swing.tree.DefaultTreeModel;

import org.columba.core.gui.util.treetable.Tree;
import org.columba.core.gui.util.treetable.TreeTable;
import org.columba.core.main.MainInterface;
import org.columba.core.xml.XmlElement;

/**
 * TreeTable component responsible for displaying plugins in a categorized
 * way.
 * 
 * Additionally shows plugin version information, the plugin description as
 * tooltip. 
 * 
 * The third column is a checkbox to enable/disable the plugin.
 *
 * @author fdietz
 */
public class PluginTree extends TreeTable {

	final static String[] columns = { "Description", "Version", "Enabled" };

	final static String[] CATEGORIES =
		{
			"Look and Feel",
			"Filter",
			"Filter Action",
			"Spam",
			"Mail Import",
			"Addressbook Import",
			"Interpreter Language",
			"Examples",
			"Uncategorized" };

	protected Map map;
	protected PluginTreeTableModel model;
	
	private JCheckBox enabledCheckBox;

	/**
	 * 
	 */
	public PluginTree() {
		super();

		map = new HashMap();

		model = new PluginTreeTableModel(columns);
		model.setTree((Tree) getTree());
		((DefaultTreeModel) model.getTree().getModel()).setAsksAllowsChildren(
			true);

		initTree();

		setModel(model);

		getTree().setCellRenderer(new DescriptionTreeRenderer());

		// make "version" column fixed size
		TableColumn tc = getColumn(columns[1]);
		tc.setCellRenderer(new VersionRenderer());
		tc.setMaxWidth(80);
		tc.setMinWidth(80);

		
		// make "enabled" column fixed size
		tc = getColumn(columns[2]);
		tc.setCellRenderer(new EnabledRenderer());
		tc.setCellEditor(new EnabledEditor());		
		
		tc.setMaxWidth(80);
		tc.setMinWidth(80);
		
	}

	public void addPlugin(XmlElement pluginElement) {
		//		plugin wasn't correctly loaded
		if (pluginElement == null)
			return;

		String category = pluginElement.getAttribute("category");
		if (category == null) {
			// this plugin doesn't define a category to which it belongs
			category = "Uncategorized";
		}

		PluginNode childNode = new PluginNode();
		childNode.setCategory(false);
		childNode.setId(pluginElement.getAttribute("id"));
		childNode.setTooltip(pluginElement.getAttribute("description"));
		childNode.setVersion(pluginElement.getAttribute("version"));
		String enabled = pluginElement.getAttribute("enabled");
		if (enabled == null)
			enabled = "true";
		childNode.setEnabled(new Boolean(enabled).booleanValue());

		System.out.println("adding plugin to table: "+enabled);
		
		PluginNode node = (PluginNode) map.get(category);
		if (node == null) {
			// unknown category found 
			// -> just add this plugin to "Uncategorized"
			category = "Uncategorized";
			node = (PluginNode) map.get(category);
		}

		node.add(childNode);
		
		// notify table
		model.fireTableDataChanged();
	}

	public void initTree() {
		PluginNode root = new PluginNode();
		root.setId("root");

		initCategories(root);

		List list = MainInterface.pluginManager.getIds();
		ListIterator it = list.listIterator();
		while (it.hasNext()) {
			// plugin id
			String id = (String) it.next();

			XmlElement pluginElement =
				MainInterface.pluginManager.getPluginElement(id);
	
			addPlugin(pluginElement);		
		}

		model.set(root);

	}

	protected void initCategories(PluginNode root) {
		for (int i = 0; i < CATEGORIES.length; i++) {
			String c = CATEGORIES[i];
			PluginNode node = new PluginNode();
			node.setAllowsChildren(true);
			node.setId(c);
			node.setEnabled(true);
			node.setCategory(true);
			root.add(node);
			map.put(c, node);
		}
	}

	public void removePluginNode(PluginNode node) {
		// notify tree
		node.removeFromParent();

		// notify table
		model.fireTableDataChanged();
	}

}