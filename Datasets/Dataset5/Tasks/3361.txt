Connector c = new Connector(prot,host,port,timeout);

package org.eclipse.ecf.provider.app;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.DocumentType;
import org.w3c.dom.Entity;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.xml.sax.SAXException;

public class ServerConfigParser {

	public static final String SERVER_ELEMENT = "server";
	public static final String CONNECTOR_ELEMENT = "connector";
	public static final String GROUP_ELEMENT = "group";
	
	public static final String PROTOCOL_ATTR = "protocol";
	public static final String HOSTNAME_ATTR = "hostname";
	public static final String PORT_ATTR = "port";
	public static final String TIMEOUT_ATTR = "timeout";
	public static final String NAME_ATTR = "name";
	
	protected void findElementsNamed(Node top, String name, List aList) {
        int type = top.getNodeType();
        switch (type) {
        case Node.DOCUMENT_TYPE_NODE:
            // Print entities if any
            NamedNodeMap nodeMap = ((DocumentType) top).getEntities();
            for (int i = 0; i < nodeMap.getLength(); i++) {
                Entity entity = (Entity) nodeMap.item(i);
                findElementsNamed(entity, name, aList);
            }
            break;
        case Node.ELEMENT_NODE:
            String elementName = top.getNodeName();
            if (name.equals(elementName)) {
                aList.add(top);
            }
        default:
            for (Node child = top.getFirstChild(); child != null; child = child
                    .getNextSibling()) {
                findElementsNamed(child, name, aList);
            }
        }
    }
	protected List processConnectorNodes(List connectorNodes) {
		List res = new ArrayList();
		for(Iterator i=connectorNodes.iterator(); i.hasNext(); ) {
			Node n = (Node) i.next();
			String ports = getAttributeValue(n,PORT_ATTR);
			int port = Connector.DEFAULT_PORT;
			if (ports != null) {
				try {
					Integer porti = new Integer(ports);
					port = porti.intValue();
				} catch (NumberFormatException e) {
					// ignore
				}
			}
			String timeouts = getAttributeValue(n,TIMEOUT_ATTR);
			int timeout = Connector.DEFAULT_TIMEOUT;
			if (timeouts != null) {
				try {
					Integer timeouti = new Integer(timeouts);
					timeout = timeouti.intValue();
				} catch (NumberFormatException e) {
					// ignore
				}
			}
			String prot = getAttributeValue(n,PROTOCOL_ATTR);
			String host = getAttributeValue(n,HOSTNAME_ATTR);
			Connector c = new Connector(this, prot,host,port,timeout);
			processConnector(n,c);
			res.add(c);
		}
		return res;
	}
	protected void processConnector(Node n, Connector c) {
		List groupList = new ArrayList();
		findElementsNamed(n,GROUP_ELEMENT,groupList);
		for(Iterator i=groupList.iterator(); i.hasNext(); ) {
			Node node = (Node) i.next();
			String name = getAttributeValue(node,NAME_ATTR);
			if (name != null && !name.equals("")) {
				NamedGroup g = new NamedGroup(name);
				c.addGroup(g);
				g.setParent(c);
			}
		}
	}
	protected List loadConnectors(Document doc) {
    	List ps = new ArrayList();
    	findElementsNamed(doc,CONNECTOR_ELEMENT,ps);
		return processConnectorNodes(ps);
	}
    protected String getAttributeValue(Node node, String attrName) {
        NamedNodeMap attrs = node.getAttributes();
        Node attrNode = attrs.getNamedItem(attrName);
        if (attrNode != null) {
            return attrNode.getNodeValue();
        } else
            return "";
    }
	public List load(InputStream ins) throws ParserConfigurationException, SAXException, IOException {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document doc = db.parse(ins);
		return loadConnectors(doc);
	}
	
	public static void main(String [] args) throws Exception {
		InputStream ins = new FileInputStream(args[0]);
		ServerConfigParser configParser = new ServerConfigParser();
		List res = configParser.load(ins);
		System.out.println("result is "+res);
	}
}