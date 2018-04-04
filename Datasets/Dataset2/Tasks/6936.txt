import org.columba.addressbook.config.AdapterNode;

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

package org.columba.addressbook.folder;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.columba.core.config.AdapterNode;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

public class GroupListCard extends DefaultCard
{
	public GroupListCard()
	{
		super();
		
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();

		try
		{
			DocumentBuilder builder = factory.newDocumentBuilder();
			document = builder.newDocument();

			Element root = (Element) document.createElement("grouplist");
			document.appendChild(root);

		}
		catch (ParserConfigurationException pce)
		{
			// Parser with specified options can't be built
			pce.printStackTrace();
		}

		AdapterNode node = new AdapterNode(getDocument());
		this.rootNode = node.getChild(0);
	}
	
	public GroupListCard( Document doc, AdapterNode root )
	{
		super( doc, root );
		
		if (doc != null)
		{
			if (getRootNode() == null)
			{
				AdapterNode node = new AdapterNode(getDocument());

				this.rootNode = node.getChild(0);

			}
		}
	}
	
	public int members()
	{
		AdapterNode membersRoot = getRootNode().getChild("list");
		if (membersRoot != null )
		{
			return membersRoot.getChildCount();
		}
		else
		{
			return 0;	
		}
		
	}
	
	public String getMember( int index )
	{
		AdapterNode membersRoot = getRootNode().getChild("list");
		if ( membersRoot != null )
		{
			AdapterNode child = membersRoot.getChildAt(index);
			if ( child != null ) return getTextValue(child);
		}
		return "";
	}
	
	public void addMember( String uid )
	{
		AdapterNode membersRoot = getRootNode().getChild("list");
		if ( membersRoot != null )
		{
			addKey( membersRoot, "uid", uid );
		}
		else
		{
			Element e = createElementNode( "list" );
			AdapterNode newNode = new AdapterNode( e );
        		getRootNode().add( newNode );
        		addKey( newNode, "uid", uid);
		}
	}
	
	public void removeMembers()
	{
		AdapterNode membersRoot = getRootNode().getChild("list");
		if ( membersRoot != null )
		{
			membersRoot.removeChildren();
		}
	}
	
	public Object[] getUids()
	{
		Object[] uids = new Object[ members() ];
		
		for ( int i=0; i<members(); i++ )
		{
			Object uid = getMember(i);
			uids[i] = uid;
			System.out.println("uid["+i+"]="+uid);
		}
		
		return uids;
	}

}