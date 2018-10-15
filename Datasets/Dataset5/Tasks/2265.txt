throw new IllegalArgumentException("Unknown literal: " + literal); //$NON-NLS-1$

/*******************************************************************************
 * Copyright (c) 2005, 2007 Remy Suen
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Remy Suen <remy.suen@gmail.com> - initial API and implementation
 ******************************************************************************/
package org.eclipse.ecf.protocol.msn;

/**
 * <p>
 * The Status class represents the different states that a user can be in.
 * </p>
 * 
 * <p>
 * <b>Note:</b> This class/interface is part of an interim API that is still
 * under development and expected to change significantly before reaching
 * stability. It is being made available at this early stage to solicit feedback
 * from pioneering adopters on the understanding that any code that uses this
 * API will almost certainly be broken (repeatedly) as the API evolves.
 * </p>
 */
public final class Status {

	public static final Status ONLINE = new Status("NLN"); //$NON-NLS-1$

	public static final Status BUSY = new Status("BSY"); //$NON-NLS-1$

	public static final Status BE_RIGHT_BACK = new Status("BRB"); //$NON-NLS-1$

	public static final Status AWAY = new Status("AWY"); //$NON-NLS-1$
	
	public static final Status IDLE = new Status("IDL"); //$NON-NLS-1$

	public static final Status ON_THE_PHONE = new Status("PHN"); //$NON-NLS-1$

	public static final Status OUT_TO_LUNCH = new Status("LUN"); //$NON-NLS-1$

	public static final Status APPEAR_OFFLINE = new Status("HDN"); //$NON-NLS-1$

	public static final Status OFFLINE = new Status(null);

	private String literal;

	static Status getStatus(String literal) {
		if (literal.equals("NLN")) { //$NON-NLS-1$
			return ONLINE;
		} else if (literal.equals("AWY")) { //$NON-NLS-1$
			return AWAY;
		} else if (literal.equals("IDL")) { //$NON-NLS-1$
			return IDLE;
		} else if (literal.equals("BSY")) { //$NON-NLS-1$
			return BUSY;
		} else if (literal.equals("BRB")) { //$NON-NLS-1$
			return BE_RIGHT_BACK;
		} else if (literal.equals("PHN")) { //$NON-NLS-1$
			return ON_THE_PHONE;
		} else if (literal.equals("LUN")) { //$NON-NLS-1$
			return OUT_TO_LUNCH;
		} else if (literal.equals("HDN")) { //$NON-NLS-1$
			return APPEAR_OFFLINE;
		} else {
			throw new IllegalArgumentException("Unknown literal: " + literal);
		}
	}

	private Status(String literal) {
		this.literal = literal;
	}

	String getLiteral() {
		return literal;
	}

}