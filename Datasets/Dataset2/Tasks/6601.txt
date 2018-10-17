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
 *
 */
public class TomcatIterate extends BodyTagSupport {
    PageContext pageContext;
    Enumeration enum;
    Object array[];
    int pos=0;
    String name;
    String type;
    
    public TomcatIterate() {}

    public void setEnumeration( Enumeration e ) {
	enum=e;
    }

    public void setArray( Object array[] ) {
	this.array=array;
	pos=0;
    }

    public void setName( String n ) {
	name=n;
    }

    public String getName() {
	return name;
    }

    public String getType() {
	return type;
    }
    
    public void setType( String type ) {
	this.type=type;
    }
    
    public int doStartTag() throws JspException {
	if( enum == null && array == null ) 
	    return SKIP_BODY;
	if( enum !=null ) {
	    if( ! enum.hasMoreElements() )
		return SKIP_BODY;
	    pageContext.setAttribute( name , enum.nextElement(),
				      PageContext.PAGE_SCOPE );
	    return EVAL_BODY_TAG;
	}
	if( array != null ) {
	    if( array.length==0 )
		return SKIP_BODY;
	    pageContext.setAttribute( name , array[ pos ],
				      PageContext.PAGE_SCOPE );
	    pos++;
	    return EVAL_BODY_TAG;
	}
	return SKIP_BODY;
    }

    public int doAfterBody() throws JspException {
	if( enum!=null )
	    if( enum.hasMoreElements() ) {
		pageContext.setAttribute( name , enum.nextElement(),
					  PageContext.PAGE_SCOPE );
		return EVAL_BODY_TAG;
	}
	if( array!=null ) {
	    if( pos<array.length ) {
		pageContext.setAttribute( name , array[pos++],
					  PageContext.PAGE_SCOPE );
		return EVAL_BODY_TAG;

	    }
	}
	return SKIP_BODY;
    }

    public int doEndTag() throws JspException {
	try {
	    if( bodyContent != null )
		bodyContent.writeOut( bodyContent.getEnclosingWriter());
	} catch (Exception ex ) {
	    ex.printStackTrace();
	}
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
}