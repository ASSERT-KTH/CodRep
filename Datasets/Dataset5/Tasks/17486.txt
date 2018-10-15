return new LongID(ns, (Long) args[0]);

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core.identity;

import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.ecf.core.identity.provider.IDInstantiator;

public class LongID extends BaseID {

    Long value = null;

    public static class Creator implements IDInstantiator {
        public ID makeInstance(Namespace ns, Class[] argTypes, Object[] args)
                throws IDInstantiationException {
            return new StringID(ns, (String) args[0]);
        }
    }
    public static final String LONGID_INSTANTIATOR_CLASS = LongID.Creator.class
            .getName();

    public static final String LONGID_NAME = LongID.class.getName();

    protected LongID(Namespace n, Long v) {
        super(n);
        value = v;
    }
    protected LongID(Namespace n, long v) {
        super(n);
        value = new Long(v);
    }
    protected int namespaceCompareTo(BaseID o) {
        Long ovalue = ((LongID) o).value;
        return value.compareTo(ovalue);
    }

    protected boolean namespaceEquals(BaseID o) {
        if (!(o instanceof LongID))
            return false;
        LongID obj = (LongID) o;
        return value.equals(obj);
    }

    protected String namespaceGetName() {
        return value.toString();
    }

    protected int namespaceHashCode() {
        return value.hashCode();
    }

    protected URI namespaceToURI() throws URISyntaxException {
        throw new URISyntaxException(value.toString(),
                "LongID instances cannot create URL values");
    }

    public long longValue() {
        return value.longValue();
    }
}
 No newline at end of file