public void handleEvent(IRemoteCallEvent event) {

package org.eclipse.ecf.remoteservice;

import org.eclipse.ecf.remoteservice.events.*;

/**
 * Abstract implementer of IRemoteCallListener.  This utility class may be used
 * to simplify the implementation of IRemoteCallListener.
 * 
 * @since 3.0
 */
public abstract class AbstractRemoteCallListener implements IRemoteCallListener {

	protected IRemoteCall remoteCall;
	protected IRemoteServiceReference remoteReference;

	public void handleServiceEvent(IRemoteServiceEvent event) {
		if (event instanceof IRemoteCallStartEvent)
			this.handleRemoteCallStartEvent((IRemoteCallStartEvent) event);
		else if (event instanceof IRemoteCallCompleteEvent)
			this.handleRemoteCallCompleteEvent((IRemoteCallCompleteEvent) event);
	}

	protected IRemoteCall getRemoteCall() {
		return remoteCall;
	}

	protected IRemoteServiceReference getRemoteServiceReference() {
		return remoteReference;
	}

	protected void handleRemoteCallCompleteEvent(IRemoteCallCompleteEvent event) {
		if (event.hadException())
			handleRemoteCallException(event.getException());
		else
			handleRemoteCallComplete(event.getResponse());
		// In either case, null out references
		remoteCall = null;
		remoteReference = null;
	}

	/**
	 * Handle remote call complete.  If the remote call completes successfully,
	 * this method will then be called with the given result of the call passed
	 * as the parameter.  If the remote call throws an exception, then {@link #handleRemoteCallException(Throwable)}
	 * will be called instead.
	 * 
	 * @param result the result of the remote call.  May be <code>null</code>.
	 * @see #handleRemoteCallException(Throwable)
	 */
	protected abstract void handleRemoteCallComplete(Object result);

	/**
	 * Handle remote call exception.  If the remote call does not complete successfully,
	 * this method will be called with the Throwable exception that occurred.  If
	 * it did complete successfully, then 
	 * 
	 * @param exception the Throwable that occurred during execution of the remote call. 
	 * Will not be <code>null</code>.
	 */
	protected abstract void handleRemoteCallException(Throwable exception);

	protected void handleRemoteCallStartEvent(IRemoteCallStartEvent event) {
		remoteCall = event.getCall();
		remoteReference = event.getReference();
	}

}