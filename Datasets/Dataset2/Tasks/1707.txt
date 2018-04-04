throw new IllegalArgumentException("Too long array for a cluster ID");

/*
 * Copyright (C) 2002-2003, Simon Nieuviarts
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
 * USA
 */
package org.objectweb.carol.cmi;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.io.Serializable;
import java.util.Arrays;

/**
 * @author nieuviar
 *
 */
public class ClusterId implements Serializable {
    private static WeakCache wc = new WeakCache();
    private transient byte id[];
    private transient int hash = 0;

    private ClusterId() {
    }

    private ClusterId(byte id[]) {
        if (id.length > Short.MAX_VALUE) {
            throw new IllegalArgumentException("Too long array");
        }
        this.id = id;
        redoHash();
    }

    public static ClusterId toClusterId(byte[] id) {
        ClusterId cid = new ClusterId(id);
        return (ClusterId) wc.getCached(cid);
    }

    private void redoHash() {
        int h = 0;
        int l = id.length;
        int n = 1;
        for (int i=0; i<l; i++) {
            h += id[i] * n;
            n *= 31;
        }
        hash = h;
    }

    public int hashCode() {
        return hash;
    }

    public boolean match(byte ar[]) {
        return Arrays.equals(id, ar);
    }

    public boolean equals(Object o) {
        if (o instanceof ClusterId) {
            ClusterId i = (ClusterId)o;
            return match(i.id);
        }
        return false;
    }

    /**
     * Readable format.
     * @return cluster id in a human readable format
     */
    public String toString() {
        String s = "";
        int i;
        for (i = 0; i < id.length; i++) {
            int n = id[i];
            if (n < 0) {
                n += 256;
            }
            if (i > 0) {
                s += "-";
            }
            s += n;
        }
        return s;
    }

//    /**
//     * @return a copy of the byte array of this Cluster Id
//     */
//    public byte[] toByteArray() {
//        return (byte[]) id.clone();
//    }
//
    public void write(DataOutput out) throws IOException {
        out.writeShort(id.length);
        out.write(id);
    }

    public static ClusterId read(DataInput in) throws IOException {
        int l = in.readShort();
        byte[] a = new byte[l];
        in.readFully(a);
        ClusterId id = new ClusterId();
        id.id = a;
        id.redoHash();
        return (ClusterId) wc.getCached(id);
    }

    private void writeObject(java.io.ObjectOutputStream out)
        throws IOException {
        out.writeShort(id.length);
        out.write(id, 0, id.length);
    }

    private void readObject(java.io.ObjectInputStream in)
        throws IOException, ClassNotFoundException {
        int l = in.readShort();
        id = new byte[l];
        in.readFully(id);
        redoHash();
    }
}