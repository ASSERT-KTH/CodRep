Log loghelper = Log.getLog("JASPER_LOG", "JspCompiler");

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

import java.io.File;
import java.io.FileNotFoundException;

import org.apache.jasper.JspCompilationContext;
import org.apache.jasper.Constants;
import org.apache.jasper.JasperException;

import org.apache.tomcat.util.log.*;

/**
 * JspCompiler is an implementation of Compiler with a funky code
 * mangling and code generation scheme!
 *
 * The reason that it is both a sub-class of compiler and an implementation
 * of mangler is because the isOutDated method that is overridden and the
 * name mangulation both depend on the actual existance of other class and
 * java files.  I.e. the value of a mangled name is a function of both the
 * name to be mangled and also of the state of the scratchdir.
 *
 * @author Anil K. Vijendran
 */
public class JspCompiler extends Compiler implements Mangler {
    
    String pkgName, javaFileName, classFileName;
    String realClassName;

    File jsp;
    String outputDir;

    //    ClassFileData cfd;
    boolean outDated;
    static final int JSP_TOKEN_LEN= Constants.JSP_TOKEN.length();

    Log loghelper = new Log("JASPER_LOG", "JspCompiler");
    
    public JspCompiler(JspCompilationContext ctxt) throws JasperException {
        super(ctxt);
        
        this.jsp = new File(ctxt.getJspFile());
        this.outputDir = ctxt.getOutputDir();
        this.outDated = false;
        setMangler(this);

	// If the .class file exists and is outdated, compute a new
	// class name
	if( isOutDated() ) {
	    generateNewClassName();
	}
    }

    private void generateNewClassName() {
	File classFile = new File(getClassFileName());
	if (! classFile.exists()) {
	     String prefix = getPrefix(jsp.getPath());
	     realClassName= prefix + getBaseClassName() +
		 Constants.JSP_TOKEN + "0";
	    return;
	} 

	String cn=getRealClassName();
	String baseClassName = cn.
	    substring(0, cn.lastIndexOf(Constants.JSP_TOKEN));
	int jspTokenIdx=cn.lastIndexOf(Constants.JSP_TOKEN);
	String versionS=cn.substring(jspTokenIdx + JSP_TOKEN_LEN,
				     cn.length());
	int number= Integer.valueOf(versionS).intValue();
	number++;
	realClassName = baseClassName + Constants.JSP_TOKEN + number;
    }
    
    /** Return the real class name for the JSP, including package and
     *   version.
     *
     *  This method is called when the server is started and a .class file
     *  is found from a previous compile or when the .class file is older,
     *  to find next version.
     */
    public final String getRealClassName() {
	if( realClassName!=null ) return realClassName;

        try {
            realClassName = ClassName.getClassName( getClassFileName() );
        } catch( JasperException ex) {
            // ops, getClassName should throw something
	    loghelper.log("Exception in getRealClassName", ex);
	    return null;
        }
	return realClassName;

    }
    
    public final String getClassName() {
        // CFD gives you the whole class name
        // This method returns just the class name sans the package

	String cn=getRealClassName();
        int lastDot = cn.lastIndexOf('.');
	String className=null;
        if (lastDot != -1) 
            className = cn.substring(lastDot+1,
                                     cn.length());
        else // no package name case
            className = cn;

        return className;
    }

    public final String getJavaFileName() {
        if( javaFileName!=null ) return javaFileName;
	javaFileName = getClassName() + ".java";
 	if (outputDir != null && !outputDir.equals(""))
 	    javaFileName = outputDir + File.separatorChar + javaFileName;
	return javaFileName;
    }
    
    public final String getClassFileName() {
        if( classFileName!=null) return classFileName;

	//        computeClassFileName();
        String prefix = getPrefix(jsp.getPath());
        classFileName = prefix + getBaseClassName() + ".class";
	if (outputDir != null && !outputDir.equals(""))
	    classFileName = outputDir + File.separatorChar + classFileName;
	return classFileName;
    }

    
    public static String [] keywords = { 
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

    public final String getPackageName() {
        if( pkgName!=null) return pkgName;

	// compute package name 
	String pathName = jsp.getPath();
	StringBuffer modifiedpkgName = new StringBuffer ();
        int indexOfSepChar = pathName.lastIndexOf(File.separatorChar);
        
	if (indexOfSepChar == -1 || indexOfSepChar == 0)
	    pkgName = null;
	else {
	    for (int i = 0; i < keywords.length; i++) {
		char fs = File.separatorChar;
		int index1 = pathName.indexOf(fs + keywords[i]);
		int index2 = pathName.indexOf(keywords[i]);
		if (index1 == -1 && index2 == -1) continue;
		int index = (index2 == -1) ? index1 : index2;
		while (index != -1) {
		    String tmpathName = pathName.substring (0,index+1) + '%';
		    pathName = tmpathName + pathName.substring (index+2);
		    index = pathName.indexOf(fs + keywords[i]);
		}
	    }
	    
	    // XXX fix for paths containing '.'.
	    // Need to be more elegant here.
            pathName = pathName.replace('.','_');
	    
	    pkgName = pathName.substring(0, pathName.lastIndexOf(
	    		File.separatorChar)).replace(File.separatorChar, '.');
	    for (int i=0; i<pkgName.length(); i++) 
		if (Character.isLetter(pkgName.charAt(i)) == true ||
		    pkgName.charAt(i) == '.') {
		    modifiedpkgName.append(pkgName.substring(i,i+1));
		}
		else
		    modifiedpkgName.append(mangleChar(pkgName.charAt(i)));

	    if (modifiedpkgName.charAt(0) == '.') {
                String modifiedpkgNameString = modifiedpkgName.toString();
                pkgName = modifiedpkgNameString.
		    substring(1, 
			      modifiedpkgName.length ());
            }
	    else 
	        pkgName = modifiedpkgName.toString();
	}
	return pkgName;
    }

    private final String getBaseClassName() {
	String className;
        
        if (jsp.getName().endsWith(".jsp"))
            className = jsp.getName().substring(0, jsp.getName().length() - 4);
        else
            className = jsp.getName();
            
	
	// Fix for invalid characters. If you think of more add to the list.
	StringBuffer modifiedClassName = new StringBuffer();
	for (int i = 0; i < className.length(); i++) {
	    if (Character.isLetterOrDigit(className.charAt(i)) == true)
		modifiedClassName.append(className.substring(i,i+1));
	    else
		modifiedClassName.append(mangleChar(className.charAt(i)));
	}
	
	return modifiedClassName.toString();
    }

    private final String getPrefix(String pathName) {
	if (pathName != null) {
	    StringBuffer modifiedName = new StringBuffer();
	    for (int i = 0; i < pathName.length(); i++) {
		if (Character.isLetter(pathName.charAt(i)) == true)
		    modifiedName.append(pathName.substring(i,i+1));
		else
		    modifiedName.append(mangleChar(pathName.charAt(i)));
 	    }
	    return modifiedName.toString();
	}
	else 
            return "";
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

    /**
     * Determines whether the current JSP class is older than the JSP file
     * from whence it came
     */
    public boolean isOutDated() {
        File jspReal = null;

        String realPath = ctxt.getRealPath(jsp.getPath());
        if (realPath == null)
            return true;

        jspReal = new File(realPath);

		  if(!jspReal.exists()){
			  return true;
		  }

		  File classFile = new File(getClassFileName());
        if (classFile.exists()) {
            outDated = classFile.lastModified() < jspReal.lastModified();
        } else {
            outDated = true;
        }

        return outDated;
    }
}
