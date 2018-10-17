15 * 60000, 4 * 60 * 60000, 10000);

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
package org.columba.calendar.ui.frame;

import java.awt.Color;
import java.awt.Shape;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.GregorianCalendar;

import com.miginfocom.ashape.shapes.AShape;
import com.miginfocom.calendar.activity.Activity;
import com.miginfocom.calendar.activity.ActivityDepository;
import com.miginfocom.calendar.activity.DefaultActivity;
import com.miginfocom.calendar.activity.recurrence.ByXXXRuleData;
import com.miginfocom.calendar.activity.recurrence.CompositeRecurrence;
import com.miginfocom.calendar.activity.recurrence.RecurrenceRule;
import com.miginfocom.calendar.category.Category;
import com.miginfocom.calendar.category.CategoryDepository;
import com.miginfocom.util.ActivityHelper;
import com.miginfocom.util.dates.ImmutableDateRange;
import com.miginfocom.util.gfx.GfxUtil;
import com.miginfocom.util.gfx.RoundRectangle;
import com.miginfocom.util.gfx.ShapeGradientPaint;

public class TestDataGenerator {

	static final Object[] CATEGORIES = { new Integer(10), new Integer(11),
			new Integer(12), new Integer(13) };

	static final String[] TITLES = { "Going to the Gym",
			"Meeting with the Board", "Taking Mick to Icehockey",
			"Lunch with Susanne", "Lunch with Matt", "Meeting about the Site",
			"Template work", "Fix the car", "Take the car to the shop",
			"Call Chris about the fishing trip", "Major cleaning",
			"Rafactoring code" };

	/**
	 * 
	 */
	public static void generateTestData() {
		Object calendarsID = new Integer(9);
		Object remoteCalendarsID = new Integer(100);
		Object markID = CATEGORIES[0];
		Object susanID = CATEGORIES[1];
		Object michaelID = CATEGORIES[2];
		Object gregID = CATEGORIES[3];

		Category root = CategoryDepository.getRoot();

		Category calendars = root.addSubCategory(calendarsID, "Local");
		calendars.addSubCategory(markID, "Mark");
		calendars.addSubCategory(susanID, "Susan");
		calendars.addSubCategory(michaelID, "Michael");
		calendars.addSubCategory(gregID, "Greg");
		
		root.addSubCategory(remoteCalendarsID, "Web");

		
		
		Shape defaultShape = new RoundRectangle(0, 0, 12, 12, 6, 6);
		Color markColor = new Color(255, 180, 180);
		Color markOutlineColor = GfxUtil.tintColor(markColor, -0.4f);
		CategoryDepository.setOverride(markID, "bg", AShape.A_PAINT, markColor);
		CategoryDepository.setOverride(markID, "bgTrans", AShape.A_PAINT,
				GfxUtil.alphaColor(markColor, 145));
		CategoryDepository.setOverride(markID, "outline", AShape.A_PAINT,
				markOutlineColor);
		CategoryDepository.setOverride(markID, "treeCheckBox", AShape.A_PAINT,
				new ShapeGradientPaint(markColor, 0.2f, 115, false));
		CategoryDepository.setOverride(markID, "treeCheckBoxOutline",
				AShape.A_PAINT, markOutlineColor);
		CategoryDepository.setOverride(markID, "titleText", AShape.A_PAINT,
				markOutlineColor);
		CategoryDepository.setOverride(markID, "mainText", AShape.A_PAINT,
				markOutlineColor);
		CategoryDepository.setOverride(markID, "treeCheckBox", AShape.A_SHAPE,
				defaultShape);
		CategoryDepository.setOverride(markID, "treeCheckBoxOutline",
				AShape.A_SHAPE, defaultShape);

		Color susanColor = new Color(200, 200, 255);
		Color susanOutlineColor = GfxUtil.tintColor(susanColor, -0.4f);
		CategoryDepository.setOverride(susanID, "bg", AShape.A_PAINT,
				susanColor);
		CategoryDepository.setOverride(susanID, "bgTrans", AShape.A_PAINT,
				GfxUtil.alphaColor(susanColor, 145));
		CategoryDepository.setOverride(susanID, "outline", AShape.A_PAINT,
				susanOutlineColor);
		CategoryDepository.setOverride(susanID, "treeCheckBox", AShape.A_PAINT,
				new ShapeGradientPaint(susanColor, 0.2f, 115, false));
		CategoryDepository.setOverride(susanID, "treeCheckBoxOutline",
				AShape.A_PAINT, susanOutlineColor);
		CategoryDepository.setOverride(susanID, "titleText", AShape.A_PAINT,
				susanOutlineColor);
		CategoryDepository.setOverride(susanID, "mainText", AShape.A_PAINT,
				susanOutlineColor);
		CategoryDepository.setOverride(susanID, "treeCheckBox", AShape.A_SHAPE,
				defaultShape);

		Color michaelColor = new Color(255, 235, 100);
		Color michaelOutlineColor = GfxUtil.tintColor(michaelColor, -0.4f);
		CategoryDepository.setOverride(michaelID, "bg", AShape.A_PAINT,
				michaelColor);
		CategoryDepository.setOverride(michaelID, "bgTrans", AShape.A_PAINT,
				GfxUtil.alphaColor(michaelColor, 145));
		CategoryDepository.setOverride(michaelID, "outline", AShape.A_PAINT,
				michaelOutlineColor);
		CategoryDepository.setOverride(michaelID, "treeCheckBox",
				AShape.A_PAINT, new ShapeGradientPaint(michaelColor, 0.2f, 115,
						false));
		CategoryDepository.setOverride(michaelID, "treeCheckBoxOutline",
				AShape.A_PAINT, michaelOutlineColor);
		CategoryDepository.setOverride(michaelID, "titleText", AShape.A_PAINT,
				michaelOutlineColor);
		CategoryDepository.setOverride(michaelID, "mainText", AShape.A_PAINT,
				michaelOutlineColor);
		CategoryDepository.setOverride(michaelID, "treeCheckBox",
				AShape.A_SHAPE, defaultShape);

		Color gregColor = new Color(180, 245, 180);
		Color gregOutlineColor = GfxUtil.tintColor(gregColor, -0.4f);
		CategoryDepository.setOverride(gregID, "bg", AShape.A_PAINT, gregColor);
		CategoryDepository.setOverride(gregID, "bgTrans", AShape.A_PAINT,
				GfxUtil.alphaColor(gregColor, 145));
		CategoryDepository.setOverride(gregID, "outline", AShape.A_PAINT,
				gregOutlineColor);
		CategoryDepository.setOverride(gregID, "treeCheckBox", AShape.A_PAINT,
				new ShapeGradientPaint(gregColor, 0.2f, 115, false));
		CategoryDepository.setOverride(gregID, "treeCheckBoxOutline",
				AShape.A_PAINT, gregOutlineColor);
		CategoryDepository.setOverride(gregID, "titleText", AShape.A_PAINT,
				gregOutlineColor);
		CategoryDepository.setOverride(gregID, "mainText", AShape.A_PAINT,
				gregOutlineColor);
		CategoryDepository.setOverride(gregID, "treeCheckBox", AShape.A_SHAPE,
				defaultShape);

		calendars.setPropertyDeep(Category.PROP_IS_HIDDEN, Boolean.FALSE, null);

		long startMillis = new GregorianCalendar(2005, 0, 0).getTimeInMillis();
		long endMillis = new GregorianCalendar(2005, 12, 31).getTimeInMillis();
		ImmutableDateRange dr = new ImmutableDateRange(startMillis, endMillis,
				false, null, null);

		ArrayList acts = ActivityHelper.createActivities(dr, TITLES, null,
				CATEGORIES, null, 15 * 60000, 60 * 60000, 24 * 60 * 60000,
				15 * 60000, 4 * 60 * 60000);
		ActivityDepository.getInstance().addBrokedActivities(acts,
				TestDataGenerator.class);

		Activity act = createRecurringEvent(new GregorianCalendar(2004, 11, 7,
				11, 00), new GregorianCalendar(2004, 11, 7, 12, 00),
				"Mark's Lunch");

		act.setCategoryIDs(new Object[] { susanID });
		ActivityDepository.getInstance().addBrokedActivity(act,
				TestDataGenerator.class);
	}

	/**
	 * @return
	 */
	public static Activity createRecurringEvent(Calendar startTime,
			Calendar endTime, String description) {

		long startMillis = startTime.getTimeInMillis();
		long endMillis = endTime.getTimeInMillis();
		ImmutableDateRange dr = new ImmutableDateRange(startMillis, endMillis,
				false, null, null);

		// A recurring event
		Activity act = new DefaultActivity(dr, new Integer(1111));
		act.setSummary(description);

		CompositeRecurrence comRec = new CompositeRecurrence();
		comRec.addIncludingRecurrence(new RecurrenceRule(Calendar.DAY_OF_YEAR,
				1));

		RecurrenceRule exWeekEnd = new RecurrenceRule(Calendar.DAY_OF_YEAR, 1);
		exWeekEnd.addByXXXRule(new ByXXXRuleData(Calendar.DAY_OF_WEEK,
				new int[] { Calendar.SATURDAY, Calendar.SUNDAY }));
		comRec.addExcludingRecurrence(exWeekEnd);

		act.setRecurrence(comRec);
		return act;
	}

}