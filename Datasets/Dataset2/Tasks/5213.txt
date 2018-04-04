import org.apache.tomcat.helper.RequestUtil;

import java.util.Vector;
import java.util.Enumeration;
import java.io.File;
import java.net.URL;
import javax.servlet.http.*;

import org.apache.tomcat.core.Request;
import org.apache.tomcat.core.FacadeManager;
import org.apache.tomcat.core.Context;
import org.apache.tomcat.core.ContextManager;
import org.apache.tomcat.util.RequestUtil;

/**
 * A context administration class. Contexts can be
 * viewed, added, and removed from the context manager.
 *
 */

public class ContextAdmin {
    private ContextManager cm;
    private Request realRequest;

    private String submit = null;
    private String addContextPath = null;
    private String addContextDocBase = null;
    private String removeContextName = null;

    public void setSubmit(String s) {
	submit = s;
    }

    public void setAddContextPath(String s) {
	addContextPath = s;
    }

    public void setAddContextDocBase(String s) {
	addContextDocBase = s;
    }

    public void setRemoveContextName(String s) {
	removeContextName = s;
    }

    public void init(HttpServletRequest request) {
	FacadeManager facadeM=(FacadeManager)request.getAttribute( FacadeManager.FACADE_ATTRIBUTE);
	realRequest = facadeM.getRealRequest(request);
	cm = realRequest.getContext().getContextManager();
    }

    public Enumeration getContextNames() {
        return (Enumeration) cm.getContextNames();
    }

    public String[] getContextInfo(String contextName) {
	Enumeration enum;
	String key;
        Context context;
        Vector v = new Vector();


	context = cm.getContext(contextName);

	v.addElement("DOC BASE: " + context.getDocBase());
	v.addElement("FULL DOC BASE: " + context.getAbsolutePath());
	v.addElement("PATH: " + context.getPath());
	if (context.getWorkDir() != null)
	   v.addElement("WORK DIR: " + RequestUtil.URLDecode(context.getWorkDir().getName()));

	v.addElement("DESCRIPTION: " + context.getDescription());
	v.addElement("SESSION TIMEOUT: " + new Integer(context.getSessionTimeOut()).toString());

        enum = context.getInitParameterNames();
	while (enum.hasMoreElements()) {
	    key = (String)enum.nextElement();
	    v.addElement("INIT PARAMETER NAME: " + key);
	    v.addElement("INIT PARAMETER: " + context.getInitParameter(key));
	}

        enum = context.getAttributeNames();
	while (enum.hasMoreElements()) {
	    key = (String)enum.nextElement();
	    v.addElement("ATTRIBUTE NAME: " + key);
	    v.addElement("ATTRIBUTE: " + RequestUtil.URLDecode(context.getAttribute(key).toString()));
	}

	v.addElement("SERVER INFO: " + context.getEngineHeader());

	String[] s = new String[v.size()];
	v.copyInto(s);
	return s;
    }

    public String addContext() {
	if ((addContextPath != null) && (addContextDocBase != null)) {
            Context context = new Context();
            context.setContextManager(cm);
            context.setPath(addContextPath);
            context.setDocBase(addContextDocBase);

	    try {
                cm.addContext(context);
                cm.initContext(context);
	    }
	    catch(org.apache.tomcat.core.TomcatException ex) {
	        ex.printStackTrace();
	    }
	    return ("Added New Context: " + addContextPath);
	}
	else return ("ERROR: Null Context Values");
    }

    public String removeContext() {
        if (removeContextName != null) {
            Enumeration enum = cm.getContextNames();
            while (enum.hasMoreElements()) {
	        String name = (String)enum.nextElement();
		if (removeContextName.equals(name)) {
	            try {
		        cm.removeContext(removeContextName);
		    }
	            catch(org.apache.tomcat.core.TomcatException ex) {
	                ex.printStackTrace();
	            }
		    return("Context Name: " + removeContextName + " Removed");
		}
	    }
	    return("Context Name: " + removeContextName + " Not Found");
	}
	else return("ERROR: Null Context Name");

    }
}