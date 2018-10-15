public Runnable setter(final ICallable function) {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core.util;

import java.lang.reflect.InvocationTargetException;

public class AsynchResult {
    protected Object resultValue = null;
    protected boolean resultReady = false;
    protected InvocationTargetException resultException = null;

    public AsynchResult() {
    }
    public Runnable setter(final Callable function) {
        return new Runnable() {
            public void run() {
                try {
                    set(function.call());
                } catch (Throwable ex) {
                    setException(ex);
                }
            }
        };
    }
    protected Object doGet() throws InvocationTargetException {
        if (resultException != null)
            throw resultException;
        else
            return resultValue;
    }
    public synchronized Object get() throws InterruptedException,
            InvocationTargetException {
        while (!resultReady)
            wait();
        return doGet();
    }
    public synchronized Object get(long msecs) throws TimeoutException,
            InterruptedException, InvocationTargetException {
        long startTime = (msecs <= 0) ? 0 : System.currentTimeMillis();
        long waitTime = msecs;
        if (resultReady)
            return doGet();
        else if (waitTime <= 0)
            throw new TimeoutException(msecs);
        else {
            for (;;) {
                wait(waitTime);
                if (resultReady)
                    return doGet();
                else {
                    waitTime = msecs - (System.currentTimeMillis() - startTime);
                    if (waitTime <= 0)
                        throw new TimeoutException(msecs);
                }
            }
        }
    }
    public synchronized void set(Object newValue) {
        resultValue = newValue;
        resultReady = true;
        notifyAll();
    }
    public synchronized void setException(Throwable ex) {
        resultException = new InvocationTargetException(ex);
        resultReady = true;
        notifyAll();
    }
    public synchronized InvocationTargetException getException() {
        return resultException;
    }
    public synchronized boolean isReady() {
        return resultReady;
    }
    public synchronized Object peek() {
        return resultValue;
    }
    public synchronized void clear() {
        resultValue = null;
        resultException = null;
        resultReady = false;
    }

}
 No newline at end of file