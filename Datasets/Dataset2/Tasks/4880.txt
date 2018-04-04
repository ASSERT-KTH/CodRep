import org.apache.tomcat.helper.RequestUtil;

package tadm;
import java.util.Vector;
import java.util.Enumeration;
import java.io.File;
import java.net.URL;
import javax.servlet.http.*;

import javax.servlet.jsp.*;
import javax.servlet.jsp.tagext.*;
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
public class TomcatAdmin extends TagSupport {
    private ContextManager cm;
    String ctxPathParam;
    String ctxPath;
    FacadeManager facadeM;
    PageContext pageContext;
    
    public TomcatAdmin() {}

    public int doStartTag() throws JspException {
	try {
	    HttpServletRequest req=(HttpServletRequest)pageContext.
		getRequest();
	    init(req);
	    pageContext.setAttribute("cm", cm);
	    if( ctxPathParam != null ) {
		ctxPath=req.getParameter( ctxPathParam );
	    }
	    if( ctxPath != null ) {
		Context ctx=cm.getContext( ctxPath );
		pageContext.setAttribute("ctx", ctx);
	    }
	} catch (Exception ex ) {
	    ex.printStackTrace();
	}
	return EVAL_BODY_INCLUDE;
    }

    public int doEndTag() throws JspException {
	return EVAL_PAGE;
    }
    
    public void setPageContext(PageContext pctx ) {
	this.pageContext=pctx;
    }

    public void setParent( Tag parent ) {
	super.setParent( parent);
    }

    public void release() {
    }

    private void init(HttpServletRequest request) {
	facadeM=(FacadeManager)request.
	    getAttribute( FacadeManager.FACADE_ATTRIBUTE);
	Request realRequest = facadeM.getRealRequest(request);
	cm = realRequest.getContext().getContextManager();
    }

    public ContextManager getContextManager(HttpServletRequest request ) {
	if( facadeM==null ) init( request );
        return cm;
    }

    public void setCtxPathParam( String ctx ) {
	ctxPathParam=ctx;
    }

    public void setCtxPath( String ctx ) {
	ctxPath=ctx;
    }

}