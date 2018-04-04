args.put( "debug", s);

package tadm;
import java.util.*;
import java.io.*;
import java.net.URL;
import javax.servlet.http.*;
import javax.servlet.*;

import javax.servlet.jsp.*;
import javax.servlet.jsp.tagext.*;

import org.apache.tools.ant.*;

/**
 * This tag will run ant tasks
 * 
 */
public class AntTag extends TagSupport {
    
    public AntTag() {}

    public int doStartTag() throws JspException {
	try {
	    pageContext.setAttribute("antProperties",
				     args);
	} catch (Exception ex ) {
	    ex.printStackTrace();
	}
	return EVAL_BODY_INCLUDE;
    }

    public int doEndTag() throws JspException {
	runTest();
	return EVAL_PAGE;
    }

    // -------------------- child tag support --------------------
    Properties args=new Properties();
    Vector targets=new Vector();
    
    public void setProperty( String name, String value ) {
	System.out.println("Adding property " + name + "=" + value );
	args.put(name, value );
    }

    public String getProperty( String name ) {
	System.out.println("Getting property " + name  );
	return args.getProperty(name );
    }

    public void addTarget( String n ) {
	System.out.println("Adding target " + n );
	targets.addElement( n );
    }
    
    //-------------------- Properties --------------------

    /** Set the name of the test.xml, relative to the base dir.
     *  For example, /WEB-INF/test-tomcat.xml
     */
    public void setTestFile( String s ) {
	args.put("ant.file", s);
    }

    /** Set the target - a subset of tests to be run
     */
    public void setTarget( String s ) {
	addTarget(s);
    }

    public void setDebug( String s ) {
	args.setProperty( "debug", s);
    }

    // -------------------- Implementation methods --------------------
    
    private void runTest() throws JspException {
	PrintWriter out=null;
	try {
	    out=pageContext.getResponse().getWriter();
	    pageContext.getOut().flush();
	    out.flush(); // we need a writer for ant
	    
	    Project project=new Project();
	    
	    AntServletLogger log=new AntServletLogger();
	    log.setWriter( out );
	    project.addBuildListener( log );
	    
	    project.init();

	    Enumeration argsE=args.propertyNames();
	    while( argsE.hasMoreElements() ) {
		String k=(String)argsE.nextElement();
		String v=args.getProperty( k );
		if( k!=null && v!= null )
		    project.setUserProperty( k, v );
	    }

	    String antFileN=args.getProperty("ant.file");
	    if( antFileN==null )
		throw new JspException( "ant.file not specified");
	    File antF=new File(antFileN);
	    ProjectHelper.configureProject( project,
					   antF );

	    // pre-execution properties
	    Hashtable antProperties=project.getProperties();
	    argsE=antProperties.keys();
	    while( argsE.hasMoreElements() ) {
		String k=(String)argsE.nextElement();
		String v=(String)antProperties.get( k );
		if( k!=null && v!= null )
		    args.put( k, v ); // includes "revision"
	    }
	    
	    if( targets.size()==0 ) {
		//targets.addElement("client");
	    }

	    project.executeTargets( targets );

	    // post-execution properties
	    antProperties=project.getProperties();

	    argsE=antProperties.keys();
	    while( argsE.hasMoreElements() ) {
		String k=(String)argsE.nextElement();
		String v=(String)antProperties.get( k );
		if( k!=null && v!= null )
		    args.put( k, v ); 
	    }
	    
	} catch( BuildException ex ) {
	    if( out==null ) out=new PrintWriter(System.out);
	    ex.printStackTrace(out);
	    Throwable ex1=ex.getException();
	    out.println("Root cause: " );
	    if( ex1!=null)
		ex1.printStackTrace(out);
	    out.flush();
	    throw new JspException( ex.toString() );
	} catch( IOException ioex ) {
	    if( out==null ) out=new PrintWriter(System.out);
	    ioex.printStackTrace(out);
	    throw new JspException( ioex.toString() );
	}
    }
}