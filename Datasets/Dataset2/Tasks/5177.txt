throws SyntaxException {

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
package org.columba.addressbook.model;

import java.awt.Image;
import java.util.Date;
import java.util.Iterator;

import org.columba.addressbook.parser.ParserUtil;
import org.columba.addressbook.parser.SyntaxException;
import org.columba.addressbook.parser.XMLContactDocumentParser;
import org.jdom.Document;

/**
 * Factory creates xml document from contact model or the other way around.
 * 
 * @author fdietz
 */
public class ContactModelFactory {

	public static Document marshall(IContactModel contactModel)
			throws SyntaxException {

		if (contactModel == null)
			throw new IllegalArgumentException("contactModel == null");

		XMLContactDocumentParser parser = new XMLContactDocumentParser();
		parser.setId(contactModel.getId());

		// <sortstring>value</sortstring>
		if (contactModel.getSortString() != null)
			parser.set(VCARD.SORTSTRING, contactModel.getSortString());

		// <fn>value</fn>
		if (contactModel.getFormattedName() != null)
			parser.set(VCARD.FN, contactModel.getFormattedName());
		// <nickname>value</nickname>
		if (contactModel.getNickName() != null)
			parser.set(VCARD.NICKNAME, contactModel.getNickName());

		// <n>
		// <family>value</family>
		// <given>value</given>
		// <prefix>value</prefix>
		// <suffix>value</suffix>
		// <additionalnames>value</additionalnames>
		// </n>
		if (contactModel.getFamilyName() != null)
			parser.set(VCARD.N, VCARD.N_FAMILY, contactModel.getFamilyName());
		if (contactModel.getGivenName() != null)
			parser.set(VCARD.N, VCARD.N_GIVEN, contactModel.getGivenName());
		if (contactModel.getNamePrefix() != null)
			parser.set(VCARD.N, VCARD.N_PREFIX, contactModel.getNamePrefix());
		if (contactModel.getNameSuffix() != null)
			parser.set(VCARD.N, VCARD.N_SUFFIX, contactModel.getNameSuffix());
		if (contactModel.getAdditionalNames() != null)
			parser.set(VCARD.N, VCARD.N_ADDITIONALNAMES, contactModel
					.getAdditionalNames());

		// <url>value</url>
		if (contactModel.getHomePage() != null)
			parser.set(VCARD.URL, contactModel.getHomePage());

		if (contactModel.getWeblog() != null)
			parser.set(VCARD.X_COLUMBA_URL_BLOG, contactModel.getWeblog());
		if (contactModel.getFreeBusy() != null)
			parser.set(VCARD.X_COLUMBA_URL_FREEBUSY, contactModel.getFreeBusy());
		if (contactModel.getCalendar() != null)
			parser.set(VCARD.X_COLUMBA_URL_CALENDAR, contactModel.getCalendar());

		// <org>value</org>
		parser.set(VCARD.ORG, contactModel.getOrganisation());
		// <department>value</department>
		parser.set(VCARD.X_COLUMBA_DEPARTMENT, contactModel.getDepartment());
		// <office>value</office>
		parser.set(VCARD.X_COLUMBA_OFFICE, contactModel.getOffice());

		if (contactModel.getProfession() != null)
			parser.set(VCARD.ROLE, contactModel.getProfession());
		if (contactModel.getTitle() != null)
			parser.set(VCARD.TITLE, contactModel.getTitle());

		Date date = contactModel.getBirthday();
		if (date != null) {
			long time = date.getTime();
			parser.set(VCARD.BDAY, new Long(time).toString());
		}

		// <email>
		// <work>value</work>
		// <home>value</home>
		// </email>
		Iterator it = contactModel.getEmailIterator();
		while (it.hasNext()) {
			IEmailModel m = ((IEmailModel) it.next());
			parser.addEmail(m);
		}

		// <im>
		// <aol>value</aol>
		// <yahoo>value</yahoo>
		// <jabber>value</jabber>
		// </im>
		it = contactModel.getInstantMessagingIterator();
		while (it.hasNext()) {
			InstantMessagingModel m = ((InstantMessagingModel) it.next());
			parser.addInstantMessaging(m);
		}

		// <phone>
		// <business>value</business>
		// <home>value</home>
		// </phone>
		it = contactModel.getPhoneIterator();
		while (it.hasNext()) {
			PhoneModel m = (PhoneModel) it.next();
			parser.addPhone(m);
		}

		// <adr>
		// <work>
		// <pobox>value</pobox>
		// <street>value</street
		// ..
		// </work>
		// ..
		// </adr>
		it = contactModel.getAddressIterator();
		while (it.hasNext()) {
			AddressModel m = (AddressModel) it.next();
			parser.addAddress(m);
		}

		// <label>
		// <type>
		// <label>CDATA[formatted value]</label>
		// </type>
		// ..
		// </label>
		it = contactModel.getLabelIterator();
		while (it.hasNext()) {
			LabelModel m = (LabelModel) it.next();
			parser.addLabel(m);
		}

		if (contactModel.getNote() != null)
			parser.set(VCARD.NOTE, contactModel.getNote());

		// base64 encode photo byte[] to string
		Image image = contactModel.getPhoto();
		if (image != null)
			parser.set(VCARD.PHOTO, ParserUtil
					.createBase64StringFromImage(image));

		// comma-separated category list
		// <category>value1,value2,value3</category>
		if (contactModel.getCategory() != null)
			parser.set(VCARD.CATEGORY, contactModel.getCategory());

		return parser.getDocument();

	}

	@SuppressWarnings("deprecation")
	public static IContactModel unmarshall(Document document, String id)
			throws SyntaxException, IllegalArgumentException {

		if (document == null)
			throw new IllegalArgumentException("document == null");
		if (id == null)
			throw new IllegalArgumentException("id == null");

		XMLContactDocumentParser parser = new XMLContactDocumentParser(document);

		ContactModel model = new ContactModel(id);
		
		model.setSortString(parser.get(VCARD.SORTSTRING));
		// compatibility - using SORTSTRING internally
		if ( model.getSortString() == null) {
			model.setSortString(parser.get(VCARD.DISPLAYNAME));
		}

		model.setFormattedName(parser.get(VCARD.FN));
		model.setNickName(parser.get(VCARD.NICKNAME));

		model.setFamilyName(parser.get(VCARD.N, VCARD.N_FAMILY));
		model.setGivenName(parser.get(VCARD.N, VCARD.N_GIVEN));
		model.setNamePrefix(parser.get(VCARD.N, VCARD.N_PREFIX));
		model.setNameSuffix(parser.get(VCARD.N, VCARD.N_SUFFIX));
		model.setAdditionalNames(parser.get(VCARD.N, VCARD.N_ADDITIONALNAMES));

		model.setHomePage(parser.get(VCARD.URL));
		model.setWeblog(parser.get(VCARD.X_COLUMBA_URL_BLOG));
		model.setFreeBusy(parser.get(VCARD.X_COLUMBA_URL_FREEBUSY));
		model.setCalendar(parser.get(VCARD.X_COLUMBA_URL_CALENDAR));

		model.setOrganisation(parser.get(VCARD.ORG));
		model.setDepartment(parser.get(VCARD.X_COLUMBA_DEPARTMENT));
		model.setOffice(parser.get(VCARD.X_COLUMBA_OFFICE));

		model.setProfession(parser.get(VCARD.ROLE));
		model.setTitle(parser.get(VCARD.TITLE));

		Iterator it = parser.getEmailIterator();
		while (it.hasNext()) {
			model.addEmail((IEmailModel) it.next());
		}

		it = parser.getPhoneIterator();
		while (it.hasNext()) {
			model.addPhone((PhoneModel) it.next());
		}

		it = parser.getInstantMessagingIterator();
		while (it.hasNext()) {
			model.addInstantMessaging((InstantMessagingModel) it.next());
		}

		it = parser.getAddressIterator();
		while (it.hasNext()) {
			model.addAddress((AddressModel) it.next());
		}

		it = parser.getLabelIterator();
		while (it.hasNext()) {
			model.addLabel((LabelModel) it.next());
		}

		model.setNote(parser.get(VCARD.NOTE));

		String imageString = parser.get(VCARD.PHOTO);
		Image image = ParserUtil.createImageFromBase64String(imageString);
		model.setPhoto(image);

		// comma-separated category list
		// <category>value1,value2,value3</category>
		model.setCategory(parser.get(VCARD.CATEGORY));

		return model;
	}
}