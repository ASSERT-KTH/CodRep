String tchome=ctx.getContextManager().getInstallDir();

package org.apache.tomcat.context;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.*;
import org.apache.tomcat.util.xml.*;
import java.beans.*;
import java.io.*;
import java.io.IOException;
import java.lang.reflect.*;
import java.util.*;
import java.util.StringTokenizer;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.*;
import org.xml.sax.helpers.*;
import org.w3c.dom.*;

/**
 * @author costin@dnt.ro
 */
public class WebXmlReader extends BaseInterceptor {

    private static StringManager sm =StringManager.getManager("org.apache.tomcat.core");

    public WebXmlReader() {
    }

    public void contextInit(Context ctx) throws TomcatException {
	if( ctx.getDebug() > 0 ) ctx.log("XmlReader - init  " + ctx.getPath() + " " + ctx.getDocBase() );

	// read default web.xml
	try {
            String home = ctx.getContextManager().getHome();
	    // XXX make it configurable
	    File default_xml=new File( home + "/conf/web.xml" );

	    // try the default ( installation ) 
	    if( ! default_xml.exists() ) {
		String tchome=ctx.getContextManager().getTomcatHome();
		if( tchome != null )
		    default_xml=new File( tchome + "/conf/web.xml");
	    }
	    
	    if( ! default_xml.exists() )
		throw new TomcatException("Can't find default web.xml configuration");
	    
	    processFile(ctx, default_xml.toString());
	    ctx.expectUserWelcomeFiles();
	    
	    File inf_xml = new File(ctx.getDocBase() + "/WEB-INF/web.xml");
	    // if relative, base it to cm.home
	    if (!inf_xml.isAbsolute())
		inf_xml = new File(home, inf_xml.toString());

	    processFile(ctx, inf_xml.toString());
	    XmlMapper xh=new XmlMapper();
	} catch (Exception e) {
	    String msg = sm.getString("context.getConfig.e",ctx.getPath() + " " + ctx.getDocBase());
	    System.out.println(msg);
	}

    }

    void processFile( Context ctx, String file) {
	try {
	    File f=new File(FileUtil.patch(file));
	    if( ! f.exists() ) {
		ctx.log( "File not found " + f + ", using only defaults" );
		return;
	    }
	    if( ctx.getDebug() > 0 ) ctx.log("Reading " + file );
	    XmlMapper xh=new XmlMapper();
	    //	    if( ctx.getDebug() > 5 ) xh.setDebug( 3 );

	    xh.addRule("web-app/context-param", xh.methodSetter("addInitParameter", 2) );
	    xh.addRule("web-app/context-param/param-name", xh.methodParam(0) );
	    xh.addRule("web-app/context-param/param-value", xh.methodParam(1) );

	    xh.addRule("web-app/description", xh.methodSetter("setDescription", 0) );
	    xh.addRule("web-app/icon/small-icon", xh.methodSetter("setIcon", 0) );
	    xh.addRule("web-app/distributable", xh.methodSetter("setDistributable", 0) );

	    xh.addRule("web-app/servlet-mapping", xh.methodSetter("addServletMapping", 2) );
	    xh.addRule("web-app/servlet-mapping/servlet-name", xh.methodParam(1) );
	    xh.addRule("web-app/servlet-mapping/url-pattern", xh.methodParam(0) );

	    xh.addRule("web-app/taglib", xh.methodSetter("addTaglib", 2) );
	    xh.addRule("web-app/taglib/taglib-uri", xh.methodParam(0) );
	    xh.addRule("web-app/taglib/taglib-location", xh.methodParam(1) );

	    xh.addRule("web-app/env-entry", xh.methodSetter("addTaglib", 4) );
	    xh.addRule("web-app/env-entry/env-entry-name", xh.methodParam(0) );
	    xh.addRule("web-app/env-entry/env-entry-type", xh.methodParam(1) );
	    xh.addRule("web-app/env-entry/env-entry-value", xh.methodParam(2) );
	    xh.addRule("web-app/env-entry/description", xh.methodParam(3) );

	    xh.addRule("web-app/login-config", xh.methodSetter("setLoginConfig", 4) );
	    xh.addRule("web-app/login-config/auth-method", xh.methodParam(0) );
	    xh.addRule("web-app/login-config/realm-name", xh.methodParam(1) );
	    xh.addRule("web-app/login-config/form-login-config/form-login-page", xh.methodParam(2) );
	    xh.addRule("web-app/login-config/form-login-config/form-error-page", xh.methodParam(3) );

	    xh.addRule("web-app/mime-mapping", xh.methodSetter("addContentType", 2) );
	    xh.addRule("web-app/mime-mapping/extension", xh.methodParam(0) );
	    xh.addRule("web-app/mime-mapping/mime-type", xh.methodParam(1) );

	    xh.addRule("web-app/welcome-file-list/welcome-file", xh.methodSetter("addWelcomeFile", 0) );

	    xh.addRule("web-app/error-page", xh.methodSetter("addErrorPage",2) );
	    xh.addRule("web-app/error-page/error-code", xh.methodParam(0) );
	    xh.addRule("web-app/error-page/exception-type", xh.methodParam(0) );
	    xh.addRule("web-app/error-page/location", xh.methodParam(1) );

	    xh.addRule("web-app/session-config", xh.methodSetter("setSessionTimeOut", 1, new String[]{"int"}));
	    xh.addRule("web-app/session-config/session-timeout", xh.methodParam(0));

	    // Servlet
	    xh.addRule("web-app/servlet", xh.objectCreate("org.apache.tomcat.core.ServletWrapper") ); // servlet-wrapper
	    xh.addRule("web-app/servlet", xh.setParent( "setContext") ); // remove it from stack when done
	    xh.addRule("web-app/servlet", xh.addChild("addServlet", null) ); // remove it from stack when done
	    xh.addRule("web-app/servlet/servlet-name", xh.methodSetter("setServletName",0) );
	    xh.addRule("web-app/servlet/servlet-class", xh.methodSetter("setServletClass",0));
	    xh.addRule("web-app/servlet/jsp-file",xh.methodSetter("setPath",0));

	    xh.addRule("web-app/servlet/security-role-ref", xh.methodSetter("addSecurityMapping", 3) );
	    xh.addRule("web-app/servlet/security-role-ref/role-name", xh.methodParam(0) );
	    xh.addRule("web-app/servlet/security-role-ref/role-link", xh.methodParam(1) );
	    xh.addRule("web-app/servlet/security-role-ref/description", xh.methodParam(2) );

	    xh.addRule("web-app/servlet/init-param", xh.methodSetter("addInitParam", 2) ); // addXXX
	    xh.addRule("web-app/servlet/init-param/param-name", xh.methodParam(0) );
	    xh.addRule("web-app/servlet/init-param/param-value", xh.methodParam(1) );

	    xh.addRule("web-app/servlet/icon/small-icon", xh.methodSetter("setIcon",0 )); // icon, body
	    xh.addRule("web-app/servlet/description", xh.methodSetter("setDescription", 0) ); // description, body
	    xh.addRule("web-app/servlet/load-on-startup", xh.methodSetter("setLoadOnStartUp", 0 ));


	    addSecurity( xh );

	    Object ctx1=xh.readXml(f, ctx);
	} catch(Exception ex ) {
	    System.out.println("ERROR reading " + file);
	    ex.printStackTrace();
	    // XXX we should invalidate the context and un-load it !!!
	}
    }

    // Add security rules - complex code
    void addSecurity( XmlMapper xh ) {
	xh.addRule("web-app/security-constraint",
		   new SCAction() );

	xh.addRule("web-app/security-constraint/user-data-constraint/transport-guarantee",
		   new XmlAction() {
			   public void end( SaxContext ctx) throws Exception {
			       Stack st=ctx.getObjectStack();
			       SecurityConstraint rc=(SecurityConstraint)st.peek();
			       String  body=ctx.getBody().trim();
			       rc.setTransport( body );
			   }
		       }
		   );
	xh.addRule("web-app/security-constraint/auth-constraint/role-name",
		   new XmlAction() {
			   public void end( SaxContext ctx) throws Exception {
			       Stack st=ctx.getObjectStack();
			       SecurityConstraint rc=(SecurityConstraint)st.peek();
			       String  body=ctx.getBody().trim();
			       rc.addRole( body );
			   }
		       }
		   );

	xh.addRule("web-app/security-constraint/web-resource-collection",
		   new XmlAction() {
			   public void start( SaxContext ctx) throws Exception {
			       Stack st=ctx.getObjectStack();
			       st.push(new ResourceCollection());
			   }
			   public void end( SaxContext ctx) throws Exception {
			       Stack st=ctx.getObjectStack();
			       ResourceCollection rc=(ResourceCollection)st.pop();
			       SecurityConstraint sc=(SecurityConstraint)st.peek();
			       st.push( rc );
			       sc.addResourceCollection( rc );
			   }
			   public void cleanup( SaxContext ctx) {
			       Stack st=ctx.getObjectStack();
			       Object o=st.pop();
			   }
		       }
		   );

	xh.addRule("web-app/security-constraint/web-resource-collection/url-pattern",
		   new XmlAction() {
			   public void end( SaxContext ctx) throws Exception {
			       Stack st=ctx.getObjectStack();
			       ResourceCollection rc=(ResourceCollection)st.peek();
			       String  body=ctx.getBody().trim();
			       rc.addUrlPattern( body );
			   }
		       }
		   );
	xh.addRule("web-app/security-constraint/web-resource-collection/http-method",
		   new XmlAction() {
			   public void end( SaxContext ctx) throws Exception {
			       Stack st=ctx.getObjectStack();
			       ResourceCollection rc=(ResourceCollection)st.peek();
			       String  body=ctx.getBody().trim();
			       rc.addHttpMethod( body );
			   }
		       }
		   );
    }

}

/** Specific action for Security-constraint
 */
class SCAction extends XmlAction {
    public void start( SaxContext ctx) throws Exception {
	Stack st=ctx.getObjectStack();
	st.push(new SecurityConstraint());
    }
    public void end( SaxContext ctx) throws Exception {
	Stack st=ctx.getObjectStack();
	String tag=ctx.getTag(ctx.getTagCount()-1);
	SecurityConstraint sc=(SecurityConstraint)st.pop();
	Context context=(Context)st.peek();

	st.push( sc ); // restore stack
	// add all patterns that will need security

	String roles[]=sc.getRoles();
	String transport=sc.getTransport();
	Enumeration en=sc.getResourceCollections();
	while( en.hasMoreElements()) {
	    ResourceCollection rc=(ResourceCollection)en.nextElement();
	    String paths[]=rc.getPatterns();
	    String meths[]=rc.getMethods();
	    context.addSecurityConstraint(  paths, meths ,
					    roles, transport);
	}
    }
    public void cleanup( SaxContext ctx) {
	Stack st=ctx.getObjectStack();
	Object o=st.pop();
    }
}

class SecurityConstraint {
    Vector roles=new Vector();
    String transport;
    Vector resourceC=new Vector();

    public SecurityConstraint() {
    }

    public void setTransport( String transport ) {
	this.transport=transport;
    }

    public String getTransport() {
	return this.transport;
    }

    public void addRole(String role ) {
	roles.addElement( role );
    }

    public void addResourceCollection( ResourceCollection rc ) {
	resourceC.addElement( rc );
    }

    public String []getRoles() {
	String rolesA[]=new String[roles.size()];
	for( int i=0; i< rolesA.length; i++ ) {
	    rolesA[i]=(String)roles.elementAt( i );
	}
	return rolesA;
    }
    public Enumeration getResourceCollections() {
	return resourceC.elements();
    }
}

class ResourceCollection {
    Vector urlP=new Vector();
    Vector methods=new Vector();

    public ResourceCollection() {
    }

    public void addUrlPattern( String pattern ) {
	urlP.addElement( pattern );
    }

    public void addHttpMethod( String method ) {
	methods.addElement( method );
    }

    public String []getMethods() {
	String methodsA[]=new String[methods.size()];
	for( int i=0; i< methodsA.length; i++ ) {
	    methodsA[i]=(String)methods.elementAt( i );
	}
	return methodsA;
    }

    public String []getPatterns() {
	String patternsA[]=new String[urlP.size()];
	for( int i=0; i< patternsA.length; i++ ) {
	    patternsA[i]=(String)urlP.elementAt( i );
	}
	return patternsA;
    }


}