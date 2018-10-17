CDATA cdata = (CDATA) e7.getContent().get(0);

// The contents of this file are subject to the Mozilla Public License Version
// 1.1
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
//The Initial Developers of the Original Code are Frederik Dietz and Timo
// Stich.
//Portions created by Frederik Dietz and Timo Stich are Copyright (C) 2003.
//
//All Rights Reserved.
package org.columba.addressbook.parser;

import java.util.Iterator;
import java.util.Vector;

import org.columba.addressbook.model.AddressModel;
import org.columba.addressbook.model.EmailModel;
import org.columba.addressbook.model.IEmailModel;
import org.columba.addressbook.model.InstantMessagingModel;
import org.columba.addressbook.model.PhoneModel;
import org.columba.addressbook.model.VCARD;
import org.jdom.CDATA;
import org.jdom.Document;
import org.jdom.Element;

/**
 * Wraps an xml document containing vCard data and offers many convienience
 * methods to access vCard attributes.
 * <p>
 * 
 * @author fdietz
 */
public class XMLContactDocumentParser {

	private Document doc;

	protected Element parentElement;

	private Element root;

	public XMLContactDocumentParser() {
		doc = new Document();
		root = new Element(VCARD.VCARD);
		doc.addContent(root);

		parentElement = root;
	}

	public XMLContactDocumentParser(Document document) throws SyntaxException {
		if (document == null)
			throw new IllegalArgumentException("document == null");

		this.doc = document;

		this.root = doc.getRootElement();

		if (!root.getName().equalsIgnoreCase(VCARD.VCARD)) {
			// wrong xml-format
			throw new SyntaxException("Root element must be <vcard>!");
		}

		parentElement = root;
	}

	public Element getRootElement() {
		return root;
	}

	/**
	 * @return Returns the parentElement.
	 */
	protected Element getParentElement() {
		return parentElement;
	}

	public void set(String key, String value) {
		Element child = getParentElement().getChild(key);
		if (child == null) {
			child = new Element(key);
			getParentElement().addContent(child);
		}
		child.setText(value);
	}

	public void set(String key, String prefix, String value) {
		Element child = getParentElement().getChild(key);
		if (child == null) {
			child = new Element(key);
			getParentElement().addContent(child);
		}
		Element prefixchild = child.getChild(prefix);
		if (prefixchild == null) {
			prefixchild = new Element(prefix);
			child.addContent(prefixchild);
		}
		prefixchild.setText(value);
	}

	public String get(String key) {
		Element child = getParentElement().getChild(key);
		if (child == null) {
			child = new Element(key);
			getParentElement().addContent(child);
		}
		return child.getTextNormalize();
	}

	public String get(String key, String prefix) {
		Element child = getParentElement().getChild(key);
		if (child == null) {
			child = new Element(key);
			getParentElement().addContent(child);
		}
		Element prefixchild = child.getChild(prefix);
		if (prefixchild == null) {
			prefixchild = new Element(prefix);
			child.addContent(prefixchild);
		}

		return prefixchild.getTextNormalize();
	}

	public Document getDocument() {
		return doc;
	}

	/**
	 * @return Returns the id.
	 */
	public String getId() {
		return get(VCARD.ID);
	}

	public void setId(String id) {
		set(VCARD.ID, id);
	}

	public void addEmail(IEmailModel model) {
		// create <email> element, if it doesn't exist yet
		Element child = getParentElement().getChild(VCARD.EMAIL);
		if (child == null) {
			child = new Element(VCARD.EMAIL);
			getParentElement().addContent(child);
		}

		// create <type> element
		Element prefixchild = new Element(model.getTypeString());
		child.addContent(prefixchild);

		prefixchild.setText(model.getAddress());
	}

	public Iterator getEmailIterator() {
		Element child = getParentElement().getChild(VCARD.EMAIL);
		// if not specified return empty iterator
		if (child == null)
			return new Vector().iterator();

		Iterator it = child.getChildren().iterator();
		Vector v = new Vector();
		while (it.hasNext()) {
			Element e = (Element) it.next();
			v.add(new EmailModel(e.getValue(), e.getName()));
		}

		return v.iterator();
	}

	public Iterator getAddressIterator() {
		Vector<AddressModel> v = new Vector<AddressModel>();

		Element child = getParentElement().getChild(VCARD.ADR);
		// if not specified return empty iterator
		if (child == null)
			return v.iterator();

		Iterator it = child.getChildren().iterator();
		// iterate over all type elements
		while (it.hasNext()) {
			Element typeElement = (Element) it.next();

			String poBox = "";
			Element e1 = typeElement.getChild(VCARD.ADR_POSTOFFICEBOX);
			if (e1 != null)
				poBox = e1.getText();
			String street = "";
			Element e2 = typeElement.getChild(VCARD.ADR_STREETADDRESS);
			if (e2 != null)
				street = e2.getText();
			String locality = "";
			Element e3 = typeElement.getChild(VCARD.ADR_LOCALITY);
			if (e3 != null)
				locality = e3.getText();
			String postalCode = "";
			Element e4 = typeElement.getChild(VCARD.ADR_POSTALCODE);
			if (e4 != null)
				postalCode = e4.getText();
			String region = "";
			Element e5 = typeElement.getChild(VCARD.ADR_REGION);
			if (e5 != null)
				region = e5.getText();
			String country = "";
			Element e6 = typeElement.getChild(VCARD.ADR_COUNTRY);
			if (e6 != null)
				country = e6.getText();
			String label = "";
			Element e7 = typeElement.getChild(VCARD.LABEL);
			if ( e7 != null) {
				if (e7.getContent() != null && e7.getContent().size() > 0) {
					CDATA cdata = (CDATA) typeElement.getContent().get(0);
					if ( cdata != null)
						label = cdata.getText();
				}
			}
			
			v.add(new AddressModel(poBox, street, locality, postalCode, region,
					country, label, typeElement.getName()));

		}

		return v.iterator();

	}

	public void addAddress(AddressModel m) {
		// create <adr>, if it doesn't exist
		Element child = getParentElement().getChild(VCARD.ADR);
		if (child == null) {
			child = new Element(VCARD.ADR);
			getParentElement().addContent(child);
		}

		// create <type> element
		Element prefixchild = new Element(m.getTypeString());
		child.addContent(prefixchild);

		Element poBoxElement = new Element(VCARD.ADR_POSTOFFICEBOX);
		poBoxElement.setText(m.getPoBox());
		prefixchild.addContent(poBoxElement);

		Element streetElement = new Element(VCARD.ADR_STREETADDRESS);
		streetElement.setText(m.getStreet());
		prefixchild.addContent(streetElement);

		Element cityElement = new Element(VCARD.ADR_LOCALITY);
		cityElement.setText(m.getCity());
		prefixchild.addContent(cityElement);

		Element zipPostalCodeElement = new Element(VCARD.ADR_POSTALCODE);
		zipPostalCodeElement.setText(m.getZipPostalCode());
		prefixchild.addContent(zipPostalCodeElement);

		Element stateProvinceCountyElement = new Element(VCARD.ADR_REGION);
		stateProvinceCountyElement.setText(m.getStateProvinceCounty());
		prefixchild.addContent(stateProvinceCountyElement);

		Element countryElement = new Element(VCARD.ADR_COUNTRY);
		countryElement.setText(m.getCountry());
		prefixchild.addContent(countryElement);
		
		// create a CDATA section for the label
		Element labelElement = new Element(VCARD.LABEL);
		labelElement.addContent(new CDATA(m.getLabel()));
		prefixchild.addContent(labelElement);

	}

	public Iterator getPhoneIterator() {
		Element child = getParentElement().getChild(VCARD.TEL);
		// if not specified return empty iterator
		if (child == null)
			return new Vector().iterator();

		Iterator it = child.getChildren().iterator();
		Vector v = new Vector();
		while (it.hasNext()) {
			Element e = (Element) it.next();
			v.add(new PhoneModel(e.getValue(), e.getName()));
		}

		return v.iterator();
	}

	public void addPhone(PhoneModel m) {
		Element child = getParentElement().getChild(VCARD.TEL);
		if (child == null) {
			child = new Element(VCARD.TEL);
			getParentElement().addContent(child);
		}

		Element prefixchild = new Element(m.getTypeString());
		child.addContent(prefixchild);

		prefixchild.setText(m.getNumber());

	}

	public Iterator getInstantMessagingIterator() {
		Element child = getParentElement().getChild(VCARD.IM);
		// if not specified return empty iterator
		if (child == null)
			return new Vector().iterator();

		Iterator it = child.getChildren().iterator();
		Vector v = new Vector();
		while (it.hasNext()) {
			Element e = (Element) it.next();
			v.add(new InstantMessagingModel(e.getValue(), e.getName()));
		}

		return v.iterator();
	}

	public void addInstantMessaging(InstantMessagingModel m) {
		Element child = getParentElement().getChild(VCARD.IM);
		if (child == null) {
			child = new Element(VCARD.IM);
			getParentElement().addContent(child);
		}

		Element prefixchild = new Element(m.getTypeString());
		child.addContent(prefixchild);

		prefixchild.setText(m.getUserId());

	}
}