package org.eclipse.ecf.internal.ui.deprecated.views;

/****************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Composent, Inc. - initial API and implementation
 *****************************************************************************/

package org.eclipse.ecf.ui.views;

import org.eclipse.ecf.core.user.IUser;

public class ChatLine {
	private IUser originator = null; //

	private String text = null;

	private boolean isPrivate = false;

	private boolean isRaw = false;

	private boolean noCRLF = false;

	public ChatLine() {

	}

	public ChatLine(String text) {
		this.text = text;

	}

	public ChatLine(String text, IUser user) {
		this.text = text;
		this.originator = user;
	}

	/**
	 * @return Returns the originator.
	 */
	public IUser getOriginator() {
		return originator;
	}

	/**
	 * @param originator
	 *            The originator to set.
	 */
	public void setOriginator(IUser originator) {
		this.originator = originator;
	}

	/**
	 * @return Returns the text.
	 */
	public String getText() {
		return text;
	}

	/**
	 * @param text
	 *            The text to set.
	 */
	public void setText(String text) {
		this.text = text;
	}

	/**
	 * @return Returns the isPrivate.
	 */
	public boolean isPrivate() {
		return isPrivate;
	}

	/**
	 * @param isPrivate
	 *            The isPrivate to set.
	 */
	public void setPrivate(boolean isPrivate) {
		this.isPrivate = isPrivate;
	}

	/**
	 * @return Returns the isRaw.
	 */
	public boolean isRaw() {
		return isRaw;
	}

	/**
	 * @param isRaw
	 *            The isRaw to set.
	 */
	public void setRaw(boolean isRaw) {
		this.isRaw = isRaw;
	}

	/**
	 * @return Returns the noCRLF.
	 */
	public boolean isNoCRLF() {
		return noCRLF;
	}

	/**
	 * @param noCRLF
	 *            The noCRLF to set.
	 */
	public void setNoCRLF(boolean noCRLF) {
		this.noCRLF = noCRLF;
	}
}