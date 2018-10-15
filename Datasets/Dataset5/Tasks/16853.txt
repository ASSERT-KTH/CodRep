int index = buf.lastIndexOf("dom.util.Assertion.");

/* $Id$ */
/*
 * The Apache Software License, Version 1.1
 * 
 * Copyright (c) 1999 The Apache Software Foundation.  All rights 
 * reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer. 
 * 
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:  
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 * 
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written 
 *    permission, please contact apache\@apache.org.
 * 
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
 * 
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 * ====================================================================
 * 
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Apache Software Foundation, and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.ibm.com .  For more information
 * on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

/**
 * A simple Assertion class (a hack really ;-) to report the source line number
 * where an assertion fails.
 */


package dom.util;

import java.io.StringWriter;
import java.io.PrintWriter;

public class Assertion {

    public static boolean assert(boolean result) {
	return assert(result, null);
    }

    public static boolean assert(boolean result, String error) {
	if (!result) {
	    System.err.print("Assertion failed: ");
	    if (error != null) {
		System.err.print(error);
	    }
	    System.err.println();
	    System.err.println(getSourceLocation());
	}
	return result;
    }

    public static boolean equals(String s1, String s2) {
        boolean result = ((s1 != null && s1.equals(s2))
			  || (s1 == null && s2 == null));
	if (!result) {
	    assert(result);
	    System.err.println("  was: equals(" + s1 + ", \"" + s2 + "\")");
	}
	return result;
    }

    public static String getSourceLocation() {
	RuntimeException ex = new RuntimeException("assertion failed");
	StringWriter writer = new StringWriter();
	PrintWriter printer = new PrintWriter(writer);
	ex.printStackTrace(printer);
	String buf = writer.toString();
	// skip the first line as well as every line related to this class
	int index = buf.lastIndexOf("dom.DOMMemTest.Assertion.");
	index = buf.indexOf('\n', index);
	return buf.substring(index + 1);
    }
}