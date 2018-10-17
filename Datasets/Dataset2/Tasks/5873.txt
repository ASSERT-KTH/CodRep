} catch ( Throwable t ) {

package org.apache.tomcat.util.compat;

import java.net.Socket;

public class CertCompat {
    /** Return the client certificate.
     */
    public Object getX509Certificates(Socket s)
    {
        return null;
    }

    // -------------------- Factory --------------------
    /** Get a compatibility helper class.
     */
    public static CertCompat getCertCompat() {
        return compat;
    }

    static CertCompat compat;

    static {
        init();
    }

    static final String JSSE_SUPPORT=
        "org.apache.tomcat.util.compat.JSSECertCompat";

    private static void init() {
        try {
            Class c=Class.forName(JSSE_SUPPORT);
            compat=(CertCompat)c.newInstance();
        } catch( Exception ex ) {
            compat=new CertCompat();
        }
    }
}