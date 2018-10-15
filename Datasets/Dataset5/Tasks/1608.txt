package org.eclipse.ecf.core.comm;

package org.eclipse.ecf.internal.comm;

public class ConnectionInstantiationException extends Exception {

    public ConnectionInstantiationException() {
        super();
    }

    /**
     * @param message
     */
    public ConnectionInstantiationException(String message) {
        super(message);
    }

    /**
     * @param cause
     */
    public ConnectionInstantiationException(Throwable cause) {
        super(cause);
    }

    /**
     * @param message
     * @param cause
     */
    public ConnectionInstantiationException(String message, Throwable cause) {
        super(message, cause);
    }

}