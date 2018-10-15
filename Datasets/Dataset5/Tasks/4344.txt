package org.eclipse.wst.xml.security.ui.preferences;

/*******************************************************************************
 * Copyright (c) 2008 Dominik Schadow - http://www.xml-sicherheit.de
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Dominik Schadow - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xml.security.core.preferences;

/**
 * <p>This utility class contains some preference values for the XML Security Tools preference pages.
 * All other values (like algorithms) are defined in the <code>Algorithms</code> class in the
 * <code>org.eclipse.wst.xml.security.core.utils</code> package.</p>
 *
 * @author Dominik Schadow
 * @version 0.5.0
 */
public final class PreferenceValues {
    /**
     * Utility class, no instance required.
     */
    private PreferenceValues() {
    }

    /** Canonicalization types. */
    protected static final String[][] CANON_TYPES = {{"&Exclusive", "exclusive"},
            {"&Inclusive", "inclusive"}};
    /** Canonicalization targets. */
    protected static final String[][] CANON_TARGETS = {{"&Same Document", "internal"},
            {"&New Document", "external"}};
    /** Signature types. */
    protected static final String[][] SIGNATURE_TYPES = {{"Enveloping", "enveloping"},
            {"Enveloped", "enveloped"}};
    /** Encryption types. */
    protected static final String[][] ENCRYPTION_TYPES = {{"Enveloping", "enveloping"}};
}