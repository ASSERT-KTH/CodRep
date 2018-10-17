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


import javax.servlet.jsp.tagext.TagData;
import javax.servlet.jsp.tagext.TagExtraInfo;
import javax.servlet.jsp.tagext.VariableInfo;

public class TomcatIterateTEI extends TagExtraInfo {

    public VariableInfo[] getVariableInfo(TagData data) {
	return (new VariableInfo[] {
	    new VariableInfo(data.getAttributeString( "name" ),
			     data.getAttributeString( "type" ),
			     true,
			     VariableInfo.NESTED ), 
			     
	    new VariableInfo("ctx2", "org.apache.tomcat.core.Context",
			     true,  VariableInfo.NESTED)
	});

    }


}