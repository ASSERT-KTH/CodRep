if (e != null) e.printStackTrace(printStream);

/****************************************************************************
* Copyright (c) 2004 Composent, Inc. and others.
* All rights reserved. This program and the accompanying materials
* are made available under the terms of the Eclipse Public License v1.0
* which accompanies this distribution, and is available at
* http://www.eclipse.org/legal/epl-v10.html
*
* Contributors:
*    Composent, Inc. - initial API and implementation
*****************************************************************************/

package org.eclipse.ecf.provider;

import java.io.File;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import org.eclipse.core.runtime.Platform;

public class Trace {
    private static final String TRACENAME = "org.eclipse.ecf.provider.Trace";

	public static final String tracePrefix = "(trace)";
    
    public static boolean ON = true;
    protected static boolean isEclipse = false;
    protected static String pluginName = "";
    protected static String debugPrefix = "/debug/";
    protected static Trace errTrace = new Trace("org.eclipse.ecf.provider.Trace.err");
    
    protected static PrintStream getPrintStream(String outputFileName) {
    	if (outputFileName != null) try {
    		File f = new File(outputFileName);
    		PrintStream ps = new PrintStream(new FileOutputStream(f,true));
        	System.out.println(TRACENAME+" directed to "+f.getCanonicalPath());
        	return ps;
    	} catch (Exception e) {
    		System.err.println("Exception opening output file '"+outputFileName+"' for tracing...using System.out");
    	}
    	return System.out;
    }
    
    protected static PrintStream printStream = null;
    
    static {
        String val = System.getProperty(TRACENAME);
    	printStream = getPrintStream(val);
        if (val != null) {
        	ON = true;
        	isEclipse = false;
        } else {
	        try {
	            ON = Platform.inDebugMode();
	            pluginName = ProviderPlugin.getDefault().getBundle().getSymbolicName();
	        } catch (Exception e) {
	        	System.out.println("WARNING: Platform not available for trace");
	        }
	        isEclipse = true;
        }
    }

    public static Trace create(String key) {
        if (isEclipse) {
            String res = "";
            try {
                res = Platform.getDebugOption(pluginName + debugPrefix + key);
            } catch (Exception e) {
                // ignore...this means that the Platform class not found.
            }
            if (res != null) {
                Boolean on = new Boolean(res);
                if (on.booleanValue())
                    return new Trace(pluginName + "(" + key + ")");
                else
                    return null;
            } else {
                return null;
            }
        } else
            return new Trace(key);
    }

    String name;

    public void dumpStack(Throwable e, String msg) {
        msg(msg);
        e.printStackTrace(printStream);
    }

    public static void errDumpStack(Throwable e, String msg) {
    	errTrace.dumpStack(e,msg);
    }
    public void msg(String msg) {
        StringBuffer sb = new StringBuffer(name);
        sb.append(getTimeString()).append(msg);
        printStream.println(sb.toString());
    }
    public static void errMsg(String msg) {
    	errTrace.msg(msg);
    }
    protected static String getTimeString() {
        Date d = new Date();
        SimpleDateFormat df = new SimpleDateFormat("[MM/dd/yy;HH:mm:ss:SSS]");
        return df.format(d);
    }

    protected Trace(String str) {
        name = tracePrefix+str;
    }

}
 No newline at end of file