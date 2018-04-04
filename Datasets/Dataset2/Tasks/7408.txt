import org.columba.core.main.MainInterface;

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Library General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

package org.columba.mail.filter;

import java.util.Vector;

import org.columba.core.command.Command;
import org.columba.core.command.CompoundCommand;
import org.columba.core.config.DefaultItem;
import org.columba.core.xml.XmlElement;
import org.columba.mail.filter.plugins.AbstractFilterAction;
import org.columba.mail.folder.Folder;
import org.columba.mail.plugin.AbstractFilterPluginHandler;
import org.columba.mail.plugin.FilterActionPluginHandler;
import org.columba.main.MainInterface;

public class Filter extends DefaultItem {

	private Vector actionList;
	private FilterRule rule;
	private Folder folder;

	/*
	private AdapterNode actionListNode;
	private AdapterNode nameNode;
	private AdapterNode enabledNode;
	*/

	public Filter(XmlElement root) {
		super(root);

		actionList = new Vector();
		//System.out.println("node: "+node);

	}

	/*
	public AdapterNode getActionListNode() {
		return actionListNode;
	}
	*/

	/*
	public void parseNode() {
		AdapterNode child;
	
		for (int i = 0; i < node.getChildCount(); i++) {
			child = node.getChild(i);
	
			if (child.getName().equals("actionlist")) {
				actionListNode = child;
	
				for (int j = 0; j < child.getChildCount(); j++) {
					AdapterNode subChild = child.getChild(j);
					if (subChild.getName().equals("action"))
						actionList.add(
							new FilterAction(subChild, getDocument()));
				}
	
			} else if (child.getName().equals("filterrule")) {
				rule = new FilterRule(child, getDocument());
			} else if (child.getName().equals("description")) {
				nameNode = child;
			} else if (child.getName().equals("enabled")) {
				enabledNode = child;
			}
		}
	
	}
	*/

	public FilterActionList getFilterActionList() {
		return new FilterActionList(getRoot().getElement("actionlist"));
	}

	public FilterRule getFilterRule() {
		return new FilterRule(getRoot().getElement("rules"));
	}

	/*
	public void addEmptyCriteria() {
		rule.addEmptyCriteria();
	}
	
	public void removeCriteria(int index) {
		rule.remove(index);
	}
	
	public void removeLastCriteria() {
		rule.removeLast();
	}
	*/

	public void setFolder(Folder f) {
		this.folder = f;
	}

	public boolean getEnabled() {
		/*
		String str = (String) getTextValue(enabledNode);
		
		Boolean b = new Boolean(str);
		
		return b;
		*/

		return getBoolean("enabled");
	}

	public void setEnabled(boolean bool) {
		set("enabled", bool);
		//setTextValue(enabledNode, bool.toString());
	}

	public void setName(String s) {
		set("description", s);
		//setTextValue(nameNode, s);
	}
	public String getName() {
		return get("description");

	}

	public CompoundCommand getCommand(
		Folder srcFolder,
		Object[] uids)
		throws Exception {
		CompoundCommand c = new CompoundCommand();

		/*
		FilterActionPluginList actionListItem =
			MailConfig.getFilterActionConfig().getFilterActionList();
		*/
		FilterActionPluginHandler pluginHandler =
			(FilterActionPluginHandler) MainInterface.pluginManager.getHandler(
				"filter_actions");

		FilterActionList list = getFilterActionList();
		for (int i = 0; i < list.getChildCount(); i++) {
			FilterAction action = list.get(i);

			String name = action.getAction();
			AbstractFilterAction instance = null;

			//Object[] args = { frameController, action, srcFolder, uids };

			try {
				instance =
					(AbstractFilterAction)
						(
							(
								AbstractFilterPluginHandler) pluginHandler)
									.getActionPlugin(
						name,
						null);
			} catch (Exception ex) {
				ex.printStackTrace();
			}
			
			Command command = instance.getCommand( action, srcFolder, uids);
			
			if ( command != null ) c.add(command);

			/*
			String className = actionListItem.getActionClassName(name);
			Object[] args = { frameController, action, srcFolder, uids };
			
			try {
				AbstractFilterAction instance =
					(AbstractFilterAction) CClassLoader.instanciate(
						className,
						args);
				c.add(instance.getCommand());
			} catch (Exception ex) {
				ex.printStackTrace();
			}
			*/

			/*
			ClassLoader loader = ClassLoader.getSystemClassLoader();
			try {
				Class actClass = loader.loadClass(className);
			
				Constructor[] constructors = actClass.getConstructors();
				Constructor constructor = constructors[0];
			
				Object[] args = { frameController, action, srcFolder, uids };
				
				AbstractFilterAction instance = (AbstractFilterAction) constructor.newInstance(args);
				
				c.add( instance.getCommand() );
			
			} catch (Exception ex) {
				ex.printStackTrace();
			}
			*/
			/*
			switch (action.getActionInt()) {
			
				case 0 :
					{
						// move
			
						System.out.println("moving messages");
			
						c.add(
							new MoveMessageAction(
								frameController,
								action,
								srcFolder,
								uids)
								.getCommand());
			
						break;
					}
				case 1 :
					{
						// copy
						System.out.println("copying messages");
			
						//System.out.println("treepath: "+ treePath );
			
						c.add( new CopyMessageAction(
							frameController,
							action,
							srcFolder,
							uids)
							.getCommand());
			
						break;
					}
				case 2 :
					{
						System.out.println("mark messages as read");
						c.add(new MarkMessageAsReadFilterAction(
							frameController,
							action,
							srcFolder,
							uids)
							.getCommand());
			
						break;
					}
				case 3 :
					{
						System.out.println("delete messages");
						c.add(new DeleteMessageAction(
							frameController,
							action,
							srcFolder,
							uids)
							.getCommand());
			
						break;
					}
					
			}
			*/

		}

		return c;
	}

}