//			System.out.println("XXX " + s + " " + index + " " + endIdx );

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
 * 3. The end-user documentation included with the redistribution, if
 *    any, must include the following acknowlegement:  
 *       "This product includes software developed by the 
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowlegement may appear in the software itself,
 *    if and wherever such third-party acknowlegements normally appear.
 *
 * 4. The names "The Jakarta Project", "Tomcat", and "Apache Software
 *    Foundation" must not be used to endorse or promote products derived
 *    from this software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache"
 *    nor may "Apache" appear in their names without prior written
 *    permission of the Apache Group.
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
 * individuals on behalf of the Apache Software Foundation.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 *
 */ 

package org.apache.tomcat.util;

import java.io.*;

/** General-purpose utilities to help generation of syntetic java
 *  classes
 */
public class JavaGeneratorTool {

    /** Mangle Package names to avoid reserver words
     **/
    public static final String manglePackage( String s ) {
	for (int i = 0; i < keywords.length; i++) {
            char fs = File.separatorChar;
            int index = s.indexOf(keywords[i]);
            if(index == -1 ) continue;
            while (index != -1) {
		int endIdx=index+keywords[i].length();
				System.out.println("XXX " + s + " " + index + " " + endIdx );
		// Is it a full word ?
		if( index>0 && s.charAt( index-1 ) != '/' ) {
		    index = s.indexOf(keywords[i],index+3);
		    continue;
		}
		    
		if( (s.length()>=endIdx) && s.charAt( endIdx ) != '/' ) {
		    index = s.indexOf(keywords[i],index+3);
		    continue;
		}
                String tmpathName = s.substring (0,index) + "_";
                s = tmpathName + s.substring (index);
                index = s.indexOf(keywords[i],index+2);
	    }
        }
	s=fixDigits( s );
	//	System.out.println("XXX " + s );
        return(s);
    }

    public static boolean isKeyword( String s ) {
	for (int i = 0; i < keywords.length; i++) {
	    if( s.equals( keywords[i] ) )
		return true;
	}
	return false;
    }

    /** Make sure package components or class name doesn't start with a digit
     */
    public static  String fixDigits( String s ) {
	int i=0;
	if(s.length() == 0 ) return s;
	if( Character.isDigit( s.charAt( 0 )  )) {
	    s="_" +s;
	}
	do {
	    i= s.indexOf( "/", i+1 );
	    if( i<0 || i==s.length() )
		break;
	    if( Character.isDigit( s.charAt( i + 1 )  ) ) {
		s=s.substring( 0, i+1 ) + "_" + s.substring( i+1 );
		i++;
	    }
	} while( i> 0 );
	
	return s;
    }


    
    /** 
     * 	Generated java files may be versioned, to avoid full reloading
     *  when the source changes.
     *
     *  Before generating a file, we check if it is already generated,
     *  and for that we need the latest version of the file. One way
     *  to do it ( the original jasper ) is to modify the class file
     *  and use a class name without version number, then use a class
     *  loader trick to load the file and extract the version from the
     *  class name.
     * 
     *  This method implements a different strategy - the classes are generate
     *  with version number, and we use a map file to find the latest
     *  version of a class. ( we could list )
     *  That can be improved by using a single version file per directory,
     *  or by listing the directory.
     *
     *  The class file is generated to use _version extension.
     *
     *  @return int version number of the latest class file, or -1 if
     *          the mapFile or the coresponding class file is not found
     */
    public static int readVersion(String classDir, String baseClassName) {
	File mapFile=new File( classDir + "/" + baseClassName + ".ver");
	if( ! mapFile.exists() )
	    return -1;
	
	int version=0;
	try {
	    FileInputStream fis=new FileInputStream( mapFile );
	    version=(int)fis.read();
	    fis.close();
	} catch( Exception ex ) {
	    System.out.println("readVersion() mapPath=" + mapFile + ex);
	    return -1;
	}

	// check if the file exists
	String versionedFileName=classDir + "/" +
	    getVersionedName( baseClassName, version ) + ".class";

	File vF=new File( versionedFileName );
	if( ! vF.exists() )
	    return -1;
	
	return version;
    }

    /** After we compile a page, we save the version in a
	file with known name, so we can restore the state when we
	restart. Note that this should move to a general-purpose
	persist repository ( on my plans for next version of tomcat )
    */
    public static void writeVersion(String classDir, String baseClassName,
				    int version)
    {
	File mapFile=new File( 	classDir + "/" + baseClassName + ".ver");

	try {
	    File dir=new File(mapFile.getParent());
	    dir.mkdirs();
	    FileOutputStream fis=new FileOutputStream( mapFile );
	    fis.write(version);
	    fis.close();
	} catch( Exception ex ) {
	    System.out.println("writeVersion() " + mapFile + ex);
	}
    }

    public static String getVersionedName( String baseName, int version )
    {
	return baseName + "_" + version;
    }

    // -------------------- Constants --------------------
    
    private static final String [] keywords = {
        "abstract", "boolean", "break", "byte",
        "case", "catch", "char", "class",
        "const", "continue", "default", "do",
        "double", "else", "extends", "final",
        "finally", "float", "for", "goto",
        "if", "implements", "import",
        "instanceof", "int", "interface",
        "long", "native", "new", "package",
        "private", "protected", "public",
        "return", "short", "static", "super",
        "switch", "synchronized", "this",
        "throw", "throws", "transient",
        "try", "void", "volatile", "while"
    };

}