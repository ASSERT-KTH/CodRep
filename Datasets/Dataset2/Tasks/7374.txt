return get(emptyFilter);

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

import java.rmi.Remote;
import java.util.Collection;
import java.util.Iterator;


public class RoundRobin extends StubLB {
    private ClusterStubData csd;
    private int len;
    private StubData[] sd;
    private double[] load;
    private double minLoad;

    /**
     * Builds a round robin algorithm on a Collection of StubData objects.
     * @param c a Collection of StubData objects.
     */
    public RoundRobin(ClusterStubData csd, Collection c) {
        this.csd = csd;
        len = c.size();
        sd = new StubData[len];
        load = new double[len];
        Iterator it = c.iterator();
        for (int i = 0; i < len; i++) {
            StubData s = (StubData) it.next();
            sd[i] = s;
        }

        /* a random start choice
         * TODO A fairer choice is a number form 0.0 to 1.0, and simulate a load where
         * each stub has just passed this value
         */
        for (int i = 0; i<SecureRandom.getInt(len); i++) {
            load[i] = sd[i].getLoadIncr();
        }
    }

    private synchronized void ensureCapacity(int minCapacity) {
        int old = sd.length;
        if (old >= minCapacity)
            return;
        int l = (old * 3) / 2 + 1;
        if (l < minCapacity)
            l = minCapacity;
        StubData[] nsd = new StubData[l];
        double[] nload = new double[l];
        System.arraycopy(sd, 0, nsd, 0, old);
        System.arraycopy(load, 0, nload, 0, old);
        sd = nsd;
        load = nload;
    }

    /**
     * This method must be called only by the ClusterStubData to ensure integrity
     * between this load balancer and the cluster stub.
     * @see org.objectweb.carol.cmi.lb.StubLB#add(org.objectweb.carol.cmi.StubData)
     */
    synchronized void add(StubData sd) {
        ensureCapacity(len + 1);
        this.sd[len] = sd;
        load[len] = minLoad;
        len++;
    }

    /**
     * This method must be called only by the ClusterStubData to ensure integrity
     * between this load balancer and the cluster stub.
     * @see org.objectweb.carol.cmi.lb.StubLB#remove(org.objectweb.carol.cmi.StubData)
     */
    synchronized void remove(StubData s) {
        for (int i=0; i<len; i++) {
            if (sd[i] == s) {
                len--;
                sd[i] = sd[len];
                sd[len] = null;
                load[i] = load[len];
                return;
            }
        }
    }

    private static StubLBFilter emptyFilter = new StubLBFilter();

    public synchronized Remote get() throws NoMoreStubException {
        return get(null);
    }

    public synchronized Remote get(StubLBFilter f) throws NoMoreStubException {
        double min = Double.MAX_VALUE;
        double minOk = Double.MAX_VALUE;
        int index = -1;
        for (int i=0; i<len; i++) {
            double l = load[i];
            if (l < minOk) {
                if (!f.contains(sd[i].getStub())) {
                    minOk = l;
                    index = i;
                }
                if (l < min) {
                    min = l;
                }
            }
        }

        if (index < 0) {
            throw new NoMoreStubException();
        }

        // to avoid overflow, restart values when the min is relatively high
        if (min >= 100.0) {
            for (int i=0; i<len; i++) {
                load[i] -= min;
            }
            min = 0;
        }

        StubData s = sd[index];
        load[index] += s.getLoadIncr();
        return s.getStub();
    }

    /**
     * @see org.objectweb.carol.cmi.StubLB#remove(java.rmi.Remote)
     */
    public void remove(Remote stub) {
        csd.removeStub(stub);
    }
}