System.getProperties().put( installSysProp, home );

/*
 * ====================================================================
 *
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
 * [Additional notices, if required by prior licensing conditions]
 *
 */ 


package org.apache.tomcat.util;
import java.lang.reflect.*;
import java.net.*;
import java.io.*;
import java.util.*;

// Depends: JDK1.1

/**
 *  Utils for introspection and reflection
 */
public final class IntrospectionUtils {

    /** Call execute() - any ant-like task should work
     */
    public static void execute( Object proxy, String method  )
	throws Exception
    {
	Method executeM=null;
	Class c=proxy.getClass();
	Class params[]=new Class[0];
	//	params[0]=args.getClass();
	executeM=c.getMethod( method, params );
	if( executeM == null ) {
	    throw new RuntimeException("No execute in " + proxy.getClass() );
	}
	executeM.invoke(proxy, null );//new Object[] { args });
    }

    /** 
     *  Call void setAttribute( String ,Object )
     */
    public static void setAttribute( Object proxy, String n, Object v)
	throws Exception
    {
	Method executeM=null;
	Class c=proxy.getClass();
	Class params[]=new Class[2];
	params[0]= String.class;
	params[1]= Object.class;
	executeM=c.getMethod( "setAttribute", params );
	if( executeM == null ) {
	    System.out.println("No setAttribute in " + proxy.getClass() );
	    return;
	}
	if( false )
	    System.out.println("Setting " + n + "=" + v + "  in " + proxy);
	executeM.invoke(proxy, new Object[] { n, v });
	return; 
    }

    /** Construct a URLClassLoader. Will compile and work in JDK1.1 too.
     */
    public static ClassLoader getURLClassLoader( URL urls[],
						 ClassLoader parent )
    {
	try {
	    Class urlCL=Class.forName( "java.net.URLClassLoader");
	    Class paramT[]=new Class[2];
	    paramT[0]= urls.getClass();
	    paramT[1]=ClassLoader.class;
	    Method m=urlCL.getMethod( "newInstance", paramT);
	    
	    ClassLoader cl=(ClassLoader)m.invoke( urlCL,
						  new Object[] { urls,
								 parent } );
	    return cl;
	} catch(ClassNotFoundException ex ) {
	    // jdk1.1
	    return null;
	} catch(Exception ex ) {
	    ex.printStackTrace();
	    return null;
	}
    }


    public static String guessInstall(String installSysProp,
		String homeSysProp, String jarName) {
	return guessInstall( installSysProp, homeSysProp, jarName, null);
    }
    
    /** Guess a product install/home by analyzing the class path.
     *  It works for product using the pattern: lib/executable.jar
     *  or if executable.jar is included in classpath by a shell
     *  script. ( java -jar also works )
     *
     *  Insures both "install" and "home" System properties are set.
     *  If either or both System properties are unset, "install" and
     *  "home" will be set to the same value.  This value will be
     *  the other System  property that is set, or the guessed value
     *  if neither is set.
     */
    public static String guessInstall(String installSysProp, String homeSysProp,
			String jarName,	String classFile) {
	String install=null;
	String home=null;
	
	if ( installSysProp != null )
	    install=System.getProperty( installSysProp );

	if( homeSysProp != null )
	    home=System.getProperty( homeSysProp );

	if ( install != null ) {
	    if ( home == null )
		System.getProperties().put( homeSysProp, install );
	    return install;
	}
	if ( home != null ) {
	    System.setProperty( installSysProp, home );
	    return home;
	}

	// Find the directory where jarName.jar is located
	
	String cpath=System.getProperty( "java.class.path");
	String pathSep=System.getProperty( "path.separator");
	StringTokenizer st=new StringTokenizer( cpath, pathSep );
	while( st.hasMoreTokens() ) {
	    String path=st.nextToken();
	    //	    log( "path " + path );
	    if( path.endsWith( jarName ) ) {
		home=path.substring( 0, path.length() - jarName.length() );
		try {
		    File f=new File( home );
		    File f1=new File ( f, "..");
		    install = f1.getCanonicalPath();
		    if( installSysProp != null )
			System.getProperties().put( installSysProp, install );
		    if( homeSysProp != null )
			System.getProperties().put( homeSysProp, install );
		    return install;
		} catch( Exception ex ) {
		    ex.printStackTrace();
		}
	    } else  {
		String fname=path + ( path.endsWith("/") ?"":"/" ) + classFile;
		if( new File( fname ).exists()) {
		    try {
			File f=new File( path );
			File f1=new File ( f, "..");
			install = f1.getCanonicalPath();
			if( installSysProp != null )
			    System.getProperties().put( installSysProp, install );
			if( homeSysProp != null )
			    System.getProperties().put( homeSysProp, install );
			return install;
		    } catch( Exception ex ) {
			ex.printStackTrace();
		    }
		}
	    }
	}
	return null;
    }


    /** Find a method with the right name
	If found, call the method ( if param is int or boolean we'll convert
	value to the right type before) - that means you can have setDebug(1).
    */
    public static void setProperty( Object o, String name, String value ) {
	if( dbg > 1 ) d("setProperty(" +
			o.getClass() + " " +  name + "="  +
			value  +")" );

	String setter= "set" +capitalize(name);

	try {
	    Method methods[]=o.getClass().getMethods();
	    Method setPropertyMethod=null;

	    // First, the ideal case - a setFoo( String ) method
	    for( int i=0; i< methods.length; i++ ) {
		Class paramT[]=methods[i].getParameterTypes();
		if( setter.equals( methods[i].getName() ) &&
		    paramT.length == 1 &&
		    "java.lang.String".equals( paramT[0].getName())) {
		    
		    methods[i].invoke( o, new Object[] { value } );
		    return;
		}
	    }
	    
	    // Try a setFoo ( int ) or ( boolean )
	    for( int i=0; i< methods.length; i++ ) {
		boolean ok=true;
		if( setter.equals( methods[i].getName() ) &&
		    methods[i].getParameterTypes().length == 1) {

		    // match - find the type and invoke it
		    Class paramType=methods[i].getParameterTypes()[0];
		    Object params[]=new Object[1];
		    if ("java.lang.Integer".equals( paramType.getName()) ||
			"int".equals( paramType.getName())) {
			try {
			    params[0]=new Integer(value);
			} catch( NumberFormatException ex ) {ok=false;}
		    } else if ("java.lang.Boolean".
			       equals( paramType.getName()) ||
			"boolean".equals( paramType.getName())) {
			params[0]=new Boolean(value);
		    } else {
			d("Unknown type " + paramType.getName() );
		    }

		    if( ok ) {
			methods[i].invoke( o, params );
			return;
		    }
		}

		// save "setProperty" for later
		if( "setProperty".equals( methods[i].getName())) {
		    setPropertyMethod=methods[i];
		}
	    }

	    // Ok, no setXXX found, try a setProperty("name", "value")
	    if( setPropertyMethod != null ) {
		Object params[]=new Object[2];
		params[0]=name;
		params[1]=value;
		setPropertyMethod.invoke( o, params );
	    }

	} catch( SecurityException ex1 ) {
	    if( dbg > 0 )
		d("SecurityException for " + o.getClass() + " " +
			name + "="  + value  +")" );
	    if( dbg > 1 ) ex1.printStackTrace();
	} catch (IllegalAccessException iae) {
	    if( dbg > 0 )
		d("IllegalAccessException for " +
			o.getClass() + " " +  name + "="  + value  +")" );
	    if( dbg > 1 ) iae.printStackTrace();
	} catch (InvocationTargetException ie) {
	    if( dbg > 0 )
		d("InvocationTargetException for " + o.getClass() +
			" " +  name + "="  + value  +")" );
	    if( dbg > 1 ) ie.printStackTrace();
	}
    }

    /** Replace ${NAME} with the property value
     */
    public static String replaceProperties(String value,
					   Object getter )
    {
        StringBuffer sb=new StringBuffer();
        int i=0;
        int prev=0;
        // assert value!=nil
        int pos;
        while( (pos=value.indexOf( "$", prev )) >= 0 ) {
            if(pos>0) {
                sb.append( value.substring( prev, pos ) );
            }
            if( pos == (value.length() - 1)) {
                sb.append('$');
                prev = pos + 1;
            }
            else if (value.charAt( pos + 1 ) != '{' ) {
                sb.append( value.charAt( pos + 1 ) );
                prev=pos+2; // XXX
            } else {
                int endName=value.indexOf( '}', pos );
                if( endName < 0 ) {
		    sb.append( value.substring( pos ));
		    prev=value.length();
		    continue;
                }
                String n=value.substring( pos+2, endName );
		String v= null;
		if( getter instanceof Hashtable ) {
		    v=(String)((Hashtable)getter).get(n);
		} else if ( getter instanceof PropertySource ) {
		    v=((PropertySource)getter).getProperty( n );
		}
		if( v== null )
		    v = "${"+n+"}"; 
                
                sb.append( v );
                prev=endName+1;
            }
        }
        if( prev < value.length() ) sb.append( value.substring( prev ) );
        return sb.toString();
    }
    
    /** Reverse of Introspector.decapitalize
     */
    public static String capitalize(String name) {
	if (name == null || name.length() == 0) {
	    return name;
	}
	char chars[] = name.toCharArray();
	chars[0] = Character.toUpperCase(chars[0]);
	return new String(chars);
    }

    // -------------------- Get property --------------------
    // This provides a layer of abstraction

    public static interface PropertySource {

	public String getProperty( String key );
	
    }

    
    // debug --------------------
    static final int dbg=0;
    static void d(String s ) {
	System.out.println("IntrospectionUtils: " + s );
    }
}