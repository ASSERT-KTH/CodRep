public interface IFuture extends IAdaptable {

/*******************************************************************************
* Copyright (c) 2008 EclipseSource and others. All rights reserved. This
* program and the accompanying materials are made available under the terms of
* the Eclipse Public License v1.0 which accompanies this distribution, and is
* available at http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*   EclipseSource - initial API and implementation
******************************************************************************/
package org.eclipse.ecf.core.util;

import org.eclipse.core.runtime.*;

/**
 * <p>
 * A future represents the future outcome of some operation(s).
 * </p>
 * <p>
 * It allows clients to access information about whether operation(s) have
 * completed (#isDone()), along with method to access status information
 * associated with the completed operation(s) ({@link #getStatus()}), and 
 * the actual result(s) of the operation(s) if completed successfully (i.e. {@link #get()} and
 * {@link #get(long)}.
 * </p>
 * <p>
 * Clients may also access an associated IProgressMonitor via {@link #getProgressMonitor()},
 * and the returned progress monitor allows cancellation of the underlying operation(s) via
 * {@link IProgressMonitor#setCanceled(boolean)}.
 * </p>
 * <p>
 * Clients may also access information about whether all operations have completed (if multiple
 * operations are involved) by calling {@link #isDone()}, and access information about whether
 * any of multiple operations have completed by calling {@link #hasValue()}.
 * </p>
 * 
 * @see IStatus
 * 
 */
public interface IFuture {

	/**
	 * Cancel the operation
	 * @return <tt>false</tt> if the operation could not be canceled,
	 * typically because it has already completed normally;
	 * <tt>true</tt> otherwise
	 */
	public boolean cancel();

	/**
	 * Waits if necessary for one or more operations to complete, and then returns result(s).
	 * This method will block until either a) at least one result is available; or b) at 
	 * least one operation throws an exception.
	 * 
	 * @return Object result of the asynchronous operation(s)
	 * @throws InterruptedException
	 *             if thread calling this method is interrupted.
	 * @throws OperationCanceledException
	 *             if the operation has been canceled via progress monitor {@link #getProgressMonitor()}.
	 */
	Object get() throws InterruptedException, OperationCanceledException;

	/**
	 * Waits if necessary for one or more operations to complete, and then returns result(s).
	 * This method will block until either a) at least one result is available; or b) at 
	 * least one operation throws an exception.
	 * 
	 * @param waitTimeInMillis
	 *            the maximum time to wait in milliseconds for the operation(s) to complete.
	 * @return Object result of the asynchronous operation(s)
	 * @throws InterruptedException
	 *             if thread calling this method is interrupted.
	 * @throws TimeoutException
	 *             if the given wait time is exceeded without getting result.
	 * @throws OperationCanceledException
	 *             if the operation has been canceled via progress monitor {@link #getProgressMonitor()}.
	 */
	Object get(long waitTimeInMillis) throws InterruptedException, TimeoutException, OperationCanceledException;

	/**
	 * <p>
	 * Get status for operation.  Will return <code>null</code> until at least one operation(s) are
	 * complete.
	 * </p>
	 * <p>
	 * If {@link #hasValue()} returns <code>true</code>, this method will return a non-<code>null</code>
	 * IStatus.  If {@link #hasValue()} returns <code>false</code>, this method will return <code>null</code>.
	 * </p>
	 * <p>
	 * Note that the returned IStatus instance may be an IMultiStatus, meaning that multiple operations have
	 * completed or are pending completion.
	 * </p>
	 * @return IStatus the status of completed operation(s).  Will return <code>null</code> if {@link #hasValue()}
	 * returns <code>false</code>.
	 * 
	 * @see #hasValue()
	 */
	public IStatus getStatus();

	/**
	 * <p>
	 * Returns <tt>true</tt> if <b>any</b> underlying operation(s) have completed.
	 * </p>
	 * <p>
	 * If this future represents access to just one operation, then this method
	 * and {@link #isDone()} will always return the same value.  That is, when a single
	 * operation has a value, it is then considered done/completed and both
	 * {@link #isDone()} and this method will return <code>true</code>.
	 * </p>
	 * <p>
	 * If this future represents multiple operations, then this method will 
	 * return <code>true</code> when <b>any</b> of the operations have 
	 * completed.  Until the first operation is completed, it will 
	 * return <code>false</code>.
	 * </p>
	 * @return <tt>true</tt> if any operations represented by this future have 
	 * completed.
	 */
	boolean hasValue();

	/**
	 * <p>
	 * Returns <tt>true</tt> if <b>all</b> underlying operation(s) have been completed.  
	 * </p>
	 * <p>
	 * If this future represents access to just one operation, then this method
	 * and {@link #hasValue()} will always return the same value.  That is, when a single
	 * operation has a value, it is then considered done/completed and both
	 * {@link #hasValue()} and #isDone will return <code>true</code>.
	 * </p>
	 * <p>
	 * If this future represents multiple operations, then this method will only
	 * return <code>true</code> when <b>all</b> of the operations have 
	 * completed.  Until all operations have completed, it will return <code>false</code>.
	 * </p>
	 * <p>
	 * Completion can be due to normal operation completion, an exception, or
	 * user cancellation -- in all of these cases, this method will return
	 * <tt>true</tt> if all underlying operation(s) have been completed.
	 * </p>
	 * 
	 * @return <tt>true</tt> if all operation(s) have completed in some manner.
	 */
	boolean isDone();

}