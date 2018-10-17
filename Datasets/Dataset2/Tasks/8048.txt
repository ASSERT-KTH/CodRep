jspFilePath=FileUtil.safePath( docBase, jspFile, false);

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
package org.apache.jasper.compiler;

import java.util.*;
import java.io.*;
import java.net.*;

import org.apache.jasper.compiler.Mangler;

// utils - can be moved here if needed
import org.apache.tomcat.util.JavaGeneratorTool;
import org.apache.tomcat.util.io.FileUtil;


/** Mangler implementation - use the directory of the jsp file as a package
    name, minimize "special" encoding - in general, simpler and predictible
    names for the common case.

    This file is also using a special mechanism for the "versioned" classes
    ( based on Anil's idea of generating new class each time the jsp file
    changes - without a context restart that looses data ).

    We use an additional file per jsp saving the current version - at
    startup the file will be read to avoid recompilation. That removes the
    need for a "special" class loader and the hacks in reading internal
    class info.
*/
public class JasperMangler implements Mangler{

    public JasperMangler(String workDir, String docBase, String jspFile)
    {
	this.jspFile=jspFile;
	this.workDir=workDir;
	this.docBase=docBase;
	init();
    }

    /** Versioned class name ( without package ).
     */
    public String getClassName() {
	return JavaGeneratorTool.getVersionedName( baseClassN, version );
    }
    
    /**
     *   Full path to the generated java file ( including version )
     */
    public String getJavaFileName() {
	return javaFileName;
    }

    /** The package name ( "." separated ) of the generated
     *  java file
     */
    public String getPackageName() {
	if( pkgDir!=null ) {
	    return pkgDir.replace('/', '.');
	} else {
	    return null;
	}
    }

    /** Full path to the compiled class file ( including version )
     */
    public String getClassFileName() {
	return classFileName;
    }

    // -------------------- JspInterceptor fields --------------------
    
    /** Returns the jsp file, as declared by <jsp-file> in server.xml
     *  or the context-relative path that was extension mapped to jsp
     */
    public String getJspFile() {
	return jspFile;
    }

    /** Returns the directory where the class is located, using
     *  the normal class loader rules.
     */
    public String getClassDir() {
	return classDir;
    }
    
    /** The class name ( package + class + versioning ) of the
     *  compilation result
     */
    public String getServletClassName() {
	if( pkgDir!=null ) {
	    return getPackageName()  + "." + getClassName();
	} else {
	    return getClassName();
	}
    }

    public int getVersion() {
	return version;
    }

    // In Jasper = not used - it's specific to the class scheme
    // used by JspServlet
    // Full path to the class file - without version.
    

    public String getBaseClassName() {
	return baseClassN;
    }

    public String getPackageDir() {
	return pkgDir;
    }
    
    public String getJspFilePath() {
        // lazy evaluation of full path
        if( jspFilePath == null )
            jspFilePath=FileUtil.safePath( docBase, jspFile);
        return jspFilePath;
    }

    private String fixInvalidChars(String className) {
	// Fix for invalid characters. From CommandLineCompiler
	StringBuffer modifiedClassName = new StringBuffer();
	char c='/';
	if( Character.isDigit( className.charAt( 0 )  )) {
	    className="_" +className;
	}
	for (int i = 0; i < className.length(); i++) {
	    char prev=c;
	    c=className.charAt(i);
	    // workaround for common "//" problem. Alternative
	    // would be to encode the dot.
	    if( prev=='/' && c=='/' ) {
		continue;
	    }
	    
	    if (Character.isLetterOrDigit(c) == true ||
		c=='_' ||
		c=='/' )
		modifiedClassName.append(className.substring(i,i+1));
	    else
		modifiedClassName.append(mangleChar(className.charAt(i)));
	}
	return modifiedClassName.toString();
    }

    private static final String mangleChar(char ch) {
        if(ch == File.separatorChar) {
	    ch = '/';
	}
	String s = Integer.toHexString(ch);
	int nzeros = 5 - s.length();
	char[] result = new char[6];
	result[0] = '_';
	for (int i = 1; i <= nzeros; i++)
	    result[i] = '0';
	for (int i = nzeros+1, j = 0; i < 6; i++, j++)
	    result[i] = s.charAt(j);
	return new String(result);
    }


    
    /** compute basic names - pkgDir and baseClassN
     */
    private void init() {
	int lastComp=jspFile.lastIndexOf(  "/" );

	if( lastComp > 0 ) {
	    // has package 
	    // ignore the first "/" of jspFile
	    pkgDir=jspFile.substring( 1, lastComp );
	}
	
	// remove "special" words, replace "."
	if( pkgDir!=null ) {
	    pkgDir=JavaGeneratorTool.manglePackage(pkgDir);
	    pkgDir=pkgDir.replace('.', '_');
	    pkgDir=fixInvalidChars( pkgDir );
	    if ( "/".equals(File.separator) )
		classDir=workDir + File.separator + pkgDir;
            else
		classDir=workDir + File.separator +
                	pkgDir.replace('/',File.separatorChar);
	} else {
	    classDir=workDir;
	}
	
	int extIdx=jspFile.lastIndexOf( "." );

	if( extIdx<0 ) {
	    // no "." 
	    if( lastComp >= 0 )
		baseClassN=jspFile.substring( lastComp+1 );
	    else
		baseClassN=jspFile.substring( 0 );
	} else {
	    if( lastComp >= 0 )
		baseClassN=jspFile.substring( lastComp+1, extIdx );
	    else
		baseClassN=jspFile.substring( 0, extIdx );
	}

	if( JavaGeneratorTool.isKeyword( baseClassN ) )
	    baseClassN="_" + baseClassN;
	
	baseClassN=fixInvalidChars( baseClassN );
	
	//	System.out.println("XXXMangler: " + jspFile + " " +
	// pkgDir + " " + baseClassN);

	// extract version from the .class dir, using the base name
	version=JavaGeneratorTool.readVersion(classDir,
					      baseClassN);
	if( version==-1 ) {
	    version=0;
	} 
	updateVersionPaths();
    }

    private void updateVersionPaths() {
	// version dependent stuff
	String baseName=classDir + File.separator + JavaGeneratorTool.
	    getVersionedName( baseClassN, version);
	
	javaFileName= baseName + ".java";

	classFileName=baseName +  ".class";
    }
    
    /** Move to a new class name, if a changes has been detected.
     */
    public void nextVersion() {
	version++;
	JavaGeneratorTool.writeVersion( getClassDir(), baseClassN, version);
	updateVersionPaths();
    }

    // context-relative jsp path 
    // extracted from the <jsp-file> or the result of a *.jsp mapping
    private String jspFile; 
    private String jspFilePath=null;
    // version of the compiled java file
    private int version;
    private String workDir;
    private String docBase;
    // the "/" separted version
    private String pkgDir;
    // class name without package and version
    private String baseClassN;
    private String classDir;
    private String javaFileName;
    private String classFileName;
}
