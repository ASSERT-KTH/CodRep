package org.eclipse.ecf.internal.example.collab;

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

package org.eclipse.ecf.example.collab;

import java.io.File;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import org.eclipse.core.runtime.Platform;

public class Trace {
    private static final String TRACENAME = "org.eclipse.ecf.example.collab.Trace";

    public static final String tracePrefix = "(trace)";
    
    public static boolean ON = false;
    protected static boolean isEclipse = false;
    protected static String pluginName = "";
    protected static String debugPrefix = "/debug/";
    
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
	            pluginName = ClientPlugin.getDefault().getBundle().getSymbolicName();
	        } catch (Exception e) {
	        	System.out.println("WARNING: Platform not available for trace");
	        }
	        isEclipse = true;
        }
    }

    public static Trace create(String key) {
        if (isEclipse) {
            String res = Platform
                    .getDebugOption(pluginName + debugPrefix + key);
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

    public void msg(String msg) {
        StringBuffer sb = new StringBuffer(name);
        sb.append(getTimeString()).append(msg);
        printStream.println(sb.toString());
    }

    protected static String getTimeString() {
        Date d = new Date();
        SimpleDateFormat df = new SimpleDateFormat("[MM/dd/yy;HH:mm:ss:SSS]");
        return df.format(d);
    }

    protected Trace(String str) {
        name = tracePrefix+str;
    }
    public static String convertStringAToString(String [] strings) {
        if (strings==null) return "";
        StringBuffer sb = new StringBuffer();
        for(int i=0; i < strings.length; i++) {
            if (strings[i]==null) sb.append("(null)");
            else sb.append(strings[i]);
            if (i != (strings.length-1)) sb.append(";");
        }
        return sb.toString();
    }
    public static String convertObjectAToString(Object [] objs) {
        if (objs==null) return "";
        StringBuffer sb = new StringBuffer();
        for(int i=0; i < objs.length; i++) {
            if (objs[i]==null) sb.append("(null)");
            else sb.append(objs[i].toString());
            if (i != (objs.length-1)) sb.append(";");
        }
        return sb.toString();
    }

    public static void setThreadDebugGroup(Object obj) {
        // Do nothing
    }
}
 No newline at end of file