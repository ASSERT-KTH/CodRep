import org.eclipse.ecf.core.util.SimpleQueueImpl;

/*
 * Created on Dec 6, 2004
 *
 */
package org.eclipse.ecf.internal.impl.standalone;

import org.eclipse.ecf.core.util.EnqueuePredicate;
import org.eclipse.ecf.core.util.Event;
import org.eclipse.ecf.core.util.QueueEnqueue;
import org.eclipse.ecf.core.util.QueueException;
import org.eclipse.ecf.internal.util.queue.SimpleQueueImpl;

public class QueueEnqueueImpl implements QueueEnqueue {

    SimpleQueueImpl queue = null;
    
    public QueueEnqueueImpl(SimpleQueueImpl impl) {
        super();
        this.queue = impl;
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#enqueue(org.eclipse.ecf.core.util.Event)
     */
    public void enqueue(Event element) throws QueueException {
        queue.enqueue(element);
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#enqueue(org.eclipse.ecf.core.util.Event[])
     */
    public void enqueue(Event[] elements) throws QueueException {
        if (elements != null) {
            for(int i=0; i < elements.length; i++) {
                enqueue(elements[i]);
            }
        }
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#enqueue_prepare(org.eclipse.ecf.core.util.Event[])
     */
    public Object enqueue_prepare(Event[] elements) throws QueueException {
        return elements;
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#enqueue_commit(java.lang.Object)
     */
    public void enqueue_commit(Object enqueue_key) {
        if (enqueue_key instanceof Event[]) {
            Event [] events = (Event []) enqueue_key;
            try {
                enqueue(events);
            } catch (QueueException e) {
                // this should not happen
                e.printStackTrace(System.err);
            }
        }

    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#enqueue_abort(java.lang.Object)
     */
    public void enqueue_abort(Object enqueue_key) {
        // Do nothing
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#enqueue_lossy(org.eclipse.ecf.core.util.Event)
     */
    public boolean enqueue_lossy(Event element) {
        queue.enqueue(element);
        return true;
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#setEnqueuePredicate(org.eclipse.ecf.core.util.EnqueuePredicate)
     */
    public void setEnqueuePredicate(EnqueuePredicate pred) {
        // This queue does not support enqueue predicate
        // So we do nothing
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#getEnqueuePredicate()
     */
    public EnqueuePredicate getEnqueuePredicate() {
        // We don't support enqueue predicate, so return null;
        return null;
    }

    /* (non-Javadoc)
     * @see org.eclipse.ecf.core.util.QueueEnqueue#size()
     */
    public int size() {
        return queue.size();
    }

}