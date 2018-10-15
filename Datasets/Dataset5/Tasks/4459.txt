String message = NLS.bind(Messages.MessageRenderer_DEFAULT_DATETIME_FORMAT, getCurrentDate(DEFAULT_TIME_FORMAT)) + " ";

/****************************************************************************
 * Copyright (c) 2007 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Jacek Pospychala <jacek.pospychala@pl.ibm.com> - bug 197329
 *****************************************************************************/
package org.eclipse.ecf.presence.ui.chatroom;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.eclipse.core.runtime.Assert;
import org.eclipse.ecf.internal.presence.ui.Messages;
import org.eclipse.osgi.util.NLS;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyleRange;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Display;

/**
 * Default implementation of {@link IMessageRenderer}.
 *
 */
public class MessageRenderer implements IMessageRenderer {

	private Color otherColor = null;
	private Color systemColor = null;
	private Color dateColor = null;
	private Color highlightColor = null;
	
	private StringBuffer buffer;
	
	private List styleRanges = new ArrayList();
	
	protected static final String DEFAULT_ME_COLOR = "0,255,0"; //$NON-NLS-1$
	protected static final String DEFAULT_OTHER_COLOR = "0,0,0"; //$NON-NLS-1$
	protected static final String DEFAULT_SYSTEM_COLOR = "0,0,255"; //$NON-NLS-1$

	/**
	 * The default color used to highlight the string of text when the user's
	 * name is referred to in the chatroom. The default color is red.
	 */
	protected static final String DEFAULT_HIGHLIGHT_COLOR = "255,0,0"; //$NON-NLS-1$
	protected static final String DEFAULT_DATE_COLOR = "0,0,0"; //$NON-NLS-1$
	
	protected static final String DEFAULT_TIME_FORMAT = Messages.MessageRenderer_DEFAULT_TIME_FORMAT;

	protected static final String DEFAULT_DATE_FORMAT = Messages.MessageRenderer_DEFAULT_DATE_FORMAT;
	
	protected boolean nickContained;
	protected String message;
	protected String originator;
	
	public MessageRenderer() {
		otherColor = colorFromRGBString(DEFAULT_OTHER_COLOR);
		systemColor = colorFromRGBString(DEFAULT_SYSTEM_COLOR);
		highlightColor = colorFromRGBString(DEFAULT_HIGHLIGHT_COLOR);
		dateColor = colorFromRGBString(DEFAULT_DATE_COLOR);
	}
	
	public StyleRange[] getStyleRanges() {
		return (StyleRange[]) styleRanges.toArray(new StyleRange[styleRanges.size()]);
	}
	
	public String render(String message, String originator, String localUserName) {
		Assert.isNotNull(localUserName);
		
		styleRanges.clear();
		
		if (message == null) {
			return null;
		}
		
		buffer = new StringBuffer();
		
		
		this.message = message;
		this.originator = originator;
		
		// check to see if the message has the user's name contained within
		// and make sure that the person referring to the user's name
		// is not the user himself, no highlighting is required in this case
		// as the user is already aware that his name is being referenced
		nickContained = (message.indexOf(localUserName) != -1) && (! localUserName.equals(originator));
		
		doRender();
		
		return buffer.toString();
	}
	
	protected void doRender() {
		
		appendDateTime();
		if (originator != null) {
			appendNickname();
		}
		appendMessage();
	}
	
	protected void appendDateTime() {
		String message = NLS.bind(Messages.MessageRenderer_DEFAULT_DATETIME_FORMAT, getCurrentDate(DEFAULT_TIME_FORMAT));
		append(message, dateColor, null, SWT.NORMAL);
	}

	protected void appendNickname() {
		String message = originator + ": "; //$NON-NLS-1$
		// check to see which color should be used
		Color foreground = nickContained ? highlightColor : otherColor;
		append(message, foreground, null, SWT.BOLD);
	}
	
	protected void appendMessage() {
		Color color = null;
		int style = SWT.NONE;
		if (originator == null) {
			color = systemColor;
			style = SWT.BOLD;
		} else if (nickContained) {
			// highlight the message itself as necessary			
			color = highlightColor;
		}
		append(message, color, null, style);
	}
	
	protected void append(String message, Color foreground, Color background, int style) {
		if (message == null) {
			return;
		}
		
		int start = buffer.length();
		
		buffer.append(message);
		
		if (foreground == null && background == null && style == SWT.NONE) {
			return;
		}
		
		StyleRange styleRange = new StyleRange(start, message.length(), foreground, background, style);
		styleRanges.add(styleRange);
	}
	
	private Color colorFromRGBString(String rgb) {
		Color color = null;
		if (rgb == null || rgb.equals("")) { //$NON-NLS-1$
			color = new Color(Display.getCurrent(), 0, 0, 0);
			return color;
		}
		if (color != null) {
			color.dispose();
		}
		String[] vals = rgb.split(","); //$NON-NLS-1$
		color = new Color(Display.getCurrent(), Integer
				.parseInt(vals[0]), Integer.parseInt(vals[1]), Integer
				.parseInt(vals[2]));
		return color;
	}
	
	protected String getCurrentDate(String format) {
		SimpleDateFormat sdf = new SimpleDateFormat(format);
		String res = sdf.format(new Date());
		return res;
	}

	protected String getDateTime() {
		StringBuffer buf = new StringBuffer();
		buf.append(getCurrentDate(DEFAULT_DATE_FORMAT)).append(" ").append( //$NON-NLS-1$
				getCurrentDate(DEFAULT_TIME_FORMAT));
		return buf.toString();
	}
}