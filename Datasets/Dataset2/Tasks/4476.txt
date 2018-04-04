//System.out.println("Component [" + component.getName() + "]");

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
package org.columba.calendar.parser;

import java.io.File;
import java.io.FileInputStream;
import java.net.URL;
import java.util.Calendar;
import java.util.Iterator;
import java.util.Vector;

import net.fortuna.ical4j.data.CalendarBuilder;
import net.fortuna.ical4j.model.Component;
import net.fortuna.ical4j.model.DateTime;
import net.fortuna.ical4j.model.Property;
import net.fortuna.ical4j.model.property.DtEnd;
import net.fortuna.ical4j.model.property.DtStamp;
import net.fortuna.ical4j.model.property.DtStart;

import org.columba.calendar.model.Event;
import org.columba.calendar.model.api.IEvent;

public class CalendarImporter {

	public CalendarImporter() {
		super();
	}

	public Iterator<IEvent> importCalendar(File file) throws Exception {
		Vector<IEvent> v = new Vector<IEvent>();

		FileInputStream in = new FileInputStream(file);

		CalendarBuilder builder = new CalendarBuilder();

		net.fortuna.ical4j.model.Calendar calendar = builder.build(in);

		for (Iterator i = calendar.getComponents().iterator(); i.hasNext();) {
			net.fortuna.ical4j.model.Component component = (net.fortuna.ical4j.model.Component) i
					.next();
			System.out.println("Component [" + component.getName() + "]");

			// only import VEVENT for now
			if (component.getName().equals(Component.VEVENT)) {

				Calendar dtStart = null;
				Calendar dtEnd = null;
				Calendar dtStamp = null;
				String summary = null;
				String location = null;
				String uid = null;
				URL url = null;
				for (Iterator j = component.getProperties().iterator(); j
						.hasNext();) {
					Property property = (Property) j.next();
					String name = property.getName();
					String value = property.getValue();

					System.out.println("Property [" + property.getName() + ", "
							+ property.getValue() + "]");

					if (name.equals(Property.DTSTART)) {
						DtStart dtStart1 = (DtStart) property;
						DateTime dateTime = (DateTime) dtStart1.getDate();
						// ensure tzid matches date-time timezone..
//						Parameter tzId = dtStart1.getParameters().getParameter(
//								Parameter.TZID);

						
						dtStart = Calendar.getInstance();

						dtStart.setTimeInMillis(dateTime.getTime());
						dtStart.setTimeZone(dateTime.getTimeZone());

					} else if (name.equals(Property.DTEND)) {
						DtEnd dtEnd1 = (DtEnd) property;
						DateTime dateTime = (DateTime) dtEnd1.getDate();
						// ensure tzid matches date-time timezone..
//						Parameter tzId = dtEnd1.getParameters().getParameter(
//								Parameter.TZID);

						
						dtEnd = Calendar.getInstance();

						dtEnd.setTimeInMillis(dateTime.getTime());
						dtEnd.setTimeZone(dateTime.getTimeZone());
					} else if (name.equals(Property.SUMMARY)) {
						summary = value;
					} else if (name.equals(Property.LOCATION)) {
						location = value;
					} else if (name.equals(Property.DTSTAMP)) {
						DtStamp dtStamp1 = (DtStamp) property;
						DateTime dateTime = (DateTime) dtStamp1.getDate();
						// ensure tzid matches date-time timezone..
//						Parameter tzId = dtStamp1.getParameters().getParameter(
//								Parameter.TZID);

						
						dtStamp = Calendar.getInstance();

						dtStamp.setTimeInMillis(dateTime.getTime());
						dtStamp.setTimeZone(dateTime.getTimeZone());
					} else if (name.equals(Property.UID)) {
						uid = value;
					} else if (name.equals(Property.URL)) {
						url = new URL(value);
					}

				}

				// skip, if UID, dtStart or dtEnd is not defined
				if (uid == null || dtStart == null || dtEnd == null)
					continue;

				IEvent event = new Event(uid);

				event.setDtStart(dtStart);
				event.setDtEnt(dtEnd);
				event.setDtStamp(dtStamp);

				if (summary != null)
					event.setSummary(summary);
				if (location != null)
					event.setLocation(location);
				if (url != null)
					event.setUrl(url);

				v.add(event);
			} else if (component.getName().equals(Component.VTIMEZONE)) {
				for (Iterator j = component.getProperties().iterator(); j
						.hasNext();) {
					Property property = (Property) j.next();
				

					System.out.println("Property [" + property.getName() + ", "
							+ property.getValue() + "]");
				}
			}
		}

		in.close();

		return v.iterator();
	}

}