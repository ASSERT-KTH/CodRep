public interface IQueueDequeue {

/*******************************************************************************
 * Copyright (c) 2004 Composent, Inc. and others. All rights reserved. This
 * program and the accompanying materials are made available under the terms of
 * the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 * 
 * Contributors: Composent, Inc. - initial API and implementation
 ******************************************************************************/

package org.eclipse.ecf.core.util;

public interface QueueDequeue {
    /*
     * Dequeue a single event. Returns null if no Events available for dequeue
     * @return Event the Event dequeued. Null if queue is empty.
     */
    Event dequeue();
    /*
     * Dequeue several events in one operation. num events are dequeued.
     * 
     * @return Event[] the Events dequeue. Returns null if there are not
     * sufficient events on queue to support dequeuing num events
     */
    Event[] dequeue(int num);
    /*
     * Dequeue all available Events. @return Event[] the events on this queue.
     * Returns null if there are no events in queue
     */
    Event[] dequeue_all();
    /*
     * Dequeue a single Event. Blocks until an Event is available for dequeue,
     * or until timeout_millis have elapsed. If timeout_millis is -1, dequeue
     * does not timeout. @param timeout_millis the timeout for a dequeue in
     * milliseconds. @return Event removed from queue. Returns null if no events
     * on queue.
     */
    Event blocking_dequeue(int timeout_millis);
    /*
     * Dequeue a multiple Events. Blocks until num Events are available for
     * dequeue, or until timeout_millis have elapsed. If timeout_millis is -1,
     * dequeue does not timeout. @param timeout_millis the timeout for a dequeue
     * in milliseconds. @param num the number of Events to dequeue @return Event []
     * the num Events removed from queue
     */
    Event[] blocking_dequeue(int timeout_millis, int num);
    /*
     * Dequeue all Events currently on queue. Blocks until num Events are
     * available for dequeue, or until timeout_millis have elapsed. If
     * timeout_millis is -1, dequeue does not timeout. @param timeout_millis the
     * timeout for a dequeue in milliseconds. @param num the number of Events to
     * dequeue @return Event [] the num Events removed from queue
     */
    Event[] blocking_dequeue_all(int timeout_millis);
    /*
     * Provide the current size of the queue (the number of Events) currently on
     * the queue. @return size the int size of the queue
     */
    int size();
}
 No newline at end of file