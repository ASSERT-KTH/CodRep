results.append("	    this." + jscriptVar + " = new Array(\"" + field.getKey() + "\", \"" + message + "\", ");

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
 * 4. The names "The Jakarta Project", "Struts", and "Apache Software
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
 */


package com.wintecinc.struts.taglib.html;


import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections; 
import java.util.Comparator; 
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import javax.servlet.jsp.JspException;
import javax.servlet.jsp.JspWriter;
import javax.servlet.jsp.PageContext;
import javax.servlet.jsp.tagext.BodyTagSupport;
import org.apache.struts.action.Action;
import org.apache.struts.util.MessageResources;
import com.wintecinc.struts.action.ValidatorServlet;
import com.wintecinc.struts.validation.Field;
import com.wintecinc.struts.validation.Form;
import com.wintecinc.struts.validation.ValidatorAction;
import com.wintecinc.struts.validation.ValidatorResources;
import com.wintecinc.struts.validation.ValidatorUtil;
import com.wintecinc.struts.validation.Var;


/**
 * Custom tag that generates Javascript for client side validation based 
 * on the validation.xml file.
 *
 * @author David Winterfeldt
*/
public class JavascriptValidatorTag extends BodyTagSupport {


    // ----------------------------------------------------------- Properties


    /**
     * The servlet context attribute key for our resources.
     */
    protected String bundle = Action.MESSAGES_KEY;


    /**
     * The default locale on our server.
     */
    protected static Locale defaultLocale = Locale.getDefault();

    /**
     * The name of the form that corresponds with the action name 
     * in struts-config.xml.  This won't be needed if this is incorporated
     * as an option in the html:form tag (ex: javascript="true").
     */
    protected String formName = null;

    /**
     * The page number we are on in a multi-part form.  This won't be needed 
     * if this is incorporated as an option in the html:form tag (should be able to be set 
     * or retrieved from scope).
    */
    protected int page = 0;

    /**
     * This will be used as is for the Javascript validation method name if it has a value.  This is 
     * the method name of the main Javascript method that the form calls to perform validations.
    */
    protected String methodName = null;

    /**
     * The static JavaScript methods will only be printed if this is set to "true".
    */
    protected String staticJavascript = "true";

    /**
     * The dynamic JavaScript objects will only be generated if this is set to "true".
    */
    protected String dynamicJavascript = "true";

    /**
     * The src attribute for html script element (used to include an external script resource).
    */
    protected String src = null;
    
    public String getFormName() {
       return formName;	
    }
    
    public void setFormName(String formName) {
       this.formName = formName;
    }
    
    public int getPage() {
       return page;	
    }
    
    public void setPage(int page) {
       this.page = page;
    }

    public String getMethod() {
       return methodName;	
    }
    
    public void setMethod(String methodName) {
       this.methodName = methodName;
    }
    
    public String getStaticJavascript() {
       return staticJavascript;	
    }
    
    public void setStaticJavascript(String staticJavascript) {
       this.staticJavascript = staticJavascript;
    }

    public String getDynamicJavascript() {
       return dynamicJavascript;	
    }
    
    public void setDynamicJavascript(String dynamicJavascript) {
       this.dynamicJavascript = dynamicJavascript;
    }

    public String getSrc() {
       return src;	
    }
    
    public void setSrc(String src) {
       this.src = src;
    }
        
    /**
     * Render the JavaScript for to perform validations based on the form name.
     *
     * @exception JspException if a JSP exception has occurred
     */
    public int doStartTag() throws JspException {
       StringBuffer results = new StringBuffer();
       
       ValidatorResources resources = (ValidatorResources)
          pageContext.getAttribute(ValidatorServlet.VALIDATOR_KEY, PageContext.APPLICATION_SCOPE);

       Locale locale = null;
       try {
           locale = (Locale) pageContext.getAttribute(Action.LOCALE_KEY, PageContext.SESSION_SCOPE);
       } catch (IllegalStateException e) {	// Invalidated session
           locale = null;
       }
       
       if (locale == null)
           locale = defaultLocale;

       Form form = null;
       if ((form = resources.get(locale, formName)) != null && "true".equals(dynamicJavascript)) {
          MessageResources messages = (MessageResources)
             pageContext.getAttribute(bundle, PageContext.APPLICATION_SCOPE);
          
          List lActions = new ArrayList();
          List lActionMethods = new ArrayList();
          
          // Get List of actions for this Form
          for (Iterator i = form.getFields().iterator(); i.hasNext(); ) {
             Field field = (Field)i.next();
          
             for (Iterator x = field.getDependencies().iterator(); x.hasNext(); ) {   
             	Object o = x.next();
             	
             	if (o != null && !lActionMethods.contains(o))
                   lActionMethods.add(o);
             }
             
          }
          
          // Create list of ValidatorActions based on lActionMethods
          for (Iterator i = lActionMethods.iterator(); i.hasNext(); ) {
             ValidatorAction va = resources.getValidatorAction((String)i.next());
             
             String javascript = va.getJavascript();
             if (javascript != null && javascript.length() > 0)
                lActions.add(va);
             else 
                i.remove();
          }
          
          Collections.sort(lActions, new Comparator() {
             public int compare(Object o1, Object o2) {
                ValidatorAction va1 = (ValidatorAction)o1;
                ValidatorAction va2 = (ValidatorAction)o2;
          
	         if ((va1.getDepends() == null || va1.getDepends().length() == 0) && 
	               (va2.getDepends() == null || va2.getDepends().length() == 0)) {
                   return 0;
                } else if ((va1.getDepends() != null && va1.getDepends().length() > 0) &&
                           (va2.getDepends() == null || va2.getDepends().length() == 0)) {
                   return 1;
                } else if ((va1.getDepends() == null || va1.getDepends().length() == 0) && 
                         (va2.getDepends() != null && va2.getDepends().length() > 0)) {
                   return -1;
                } else {
                   return va1.getDependencies().size() - va2.getDependencies().size();
                }
             }
          });  	   
          
          String methods = null;
          for (Iterator i = lActions.iterator(); i.hasNext(); ) {
             ValidatorAction va = (ValidatorAction)i.next();
             
             if (methods == null)
                methods = va.getMethod() + "(form)";
             else 
                methods += " && " + va.getMethod() + "(form)";
          }
          
          results.append(getJavascriptBegin(methods));
          
          for (Iterator i = lActions.iterator(); i.hasNext(); ) {
             ValidatorAction va = (ValidatorAction)i.next();
             String jscriptVar = null;
             String functionName = null;
             
             if (va.getJsFunctionName() != null && va.getJsFunctionName().length() > 0)
                functionName = va.getJsFunctionName();
             else 
                functionName = va.getName();
             
             results.append("	 function " + functionName + " () { \n");
             for (Iterator x = form.getFields().iterator(); x.hasNext(); ) {
                Field field = (Field)x.next();         
          
                if (field.getPage() == page && field.isDependency(va.getName())) {
	   	   String message = ValidatorUtil.getMessage(messages, locale, va, field);
	   	   message = (message != null ? message : "");
          
                   jscriptVar = getNextVar(jscriptVar);
          
                   results.append("	    this." + jscriptVar + " = new Array(\"" + field.getProperty() + "\", \"" + message + "\", ");
                   
                   
                   results.append("new Function (\"varName\", \"");
                   
                   Map hVars = field.getVars();
                   // Loop through the field's variables.
                   for (Iterator iVars = hVars.keySet().iterator(); iVars.hasNext(); ) {
                      String varKey = (String)iVars.next();
                      Var var = (Var)hVars.get(varKey);
                      String varValue = var.getValue();
                      String jsType = var.getJsType();
	               
	               if (Var.JSTYPE_INT.equalsIgnoreCase(jsType))
	                  results.append("this." + varKey + "=" + ValidatorUtil.replace(varValue, "\\", "\\\\") + "; ");
	               else if (Var.JSTYPE_REGEXP.equalsIgnoreCase(jsType))
	                  results.append("this." + varKey + "=/" + ValidatorUtil.replace(varValue, "\\", "\\\\") + "/; ");
	               else if (Var.JSTYPE_STRING.equalsIgnoreCase(jsType))
	                  results.append("this." + varKey + "='" + ValidatorUtil.replace(varValue, "\\", "\\\\") + "'; ");
	               // So everyone using the latest format doesn't need to change their xml files immediately.
	               else if ("mask".equalsIgnoreCase(varKey))
	                  results.append("this." + varKey + "=/" + ValidatorUtil.replace(varValue, "\\", "\\\\") + "/; ");
	               else
	                  results.append("this." + varKey + "='" + ValidatorUtil.replace(varValue, "\\", "\\\\") + "'; ");
                   }
                                               
                   results.append(" return this[varName];\"));\n");
                }
             }
             results.append("	 } \n\n");
          }
       }

       if ("true".equals(staticJavascript))
          results.append(getJavascriptStaticMethods(resources));
       
       if ("true".equals(dynamicJavascript))
          results.append(getJavascriptEnd());
       
       // Print this field to our output writer
       JspWriter writer = pageContext.getOut();
       try {
           writer.print(results.toString());
       } catch (IOException e) {
       	   throw new JspException(e.getMessage());
           //throw new JspException(messages.getMessage("common.io", e.toString()));
       }
       
       // Continue processing this page
       return (EVAL_BODY_TAG);

    }

    /**
     * Release any acquired resources.
     */
    public void release() {
	super.release();
        bundle = Action.MESSAGES_KEY;
        formName = null;
        page = 0;
        methodName = null;
        staticJavascript = "true";
        dynamicJavascript = "true";
        src = null;
    }


    protected String getJavascriptBegin(String methods) {
       StringBuffer sb = new StringBuffer();
       String name = formName.substring(0, 1).toUpperCase() + formName.substring(1, formName.length());
       
       if (src != null)
          sb.append("<SCRIPT LANGUAGE=\"Javascript1.1\" src=\"" + src + "\"> \n");
       else
          sb.append("<SCRIPT LANGUAGE=\"Javascript1.1\"> \n");
          
       sb.append("<!-- Begin \n");
       sb.append("\n	 var bCancel = false; \n\n");

       if (methodName == null || methodName.length() == 0)
          sb.append("	 function validate" + name + "(form) {                                                                   \n");
       else              
          sb.append("	 function " + methodName + "(form) {                                                                   \n");
                         
       sb.append("	      if (bCancel) \n");
       sb.append("	 	return true; \n");
       sb.append("	      else \n");     
       sb.append("	 	return " + methods + "; \n");
       sb.append("	 } \n\n");
       
       return sb.toString();
    }
    
    protected String getJavascriptStaticMethods(ValidatorResources resources) {
       StringBuffer sb = new StringBuffer();
       
       sb.append("\n\n");

       for (Iterator i = resources.getValidatorActions().values().iterator(); i.hasNext(); ) {
          ValidatorAction va = (ValidatorAction)i.next();
          if (va != null) {
             String javascript = va.getJavascript();
             if (javascript != null && javascript.length() > 0)
                sb.append(javascript + "\n");
          }
       }

       return sb.toString();
    }

    protected String getJavascriptEnd() {
       StringBuffer sb = new StringBuffer();
       
       sb.append("\n");
       sb.append("//  End -->\n");
       sb.append("</SCRIPT>\n\n");
       
       return sb.toString();
    }    
    /**
     * The value <code>null</code> will be returned at the end of the sequence.  
     * &nbsp;&nbsp;&nbsp; ex: "zz" will return <code>null</code>
    */ 
    private String getNextVar(String input) {
       if (input == null)
          return "aa";
          
       input = input.toLowerCase();
       
       for (int i = input.length(); i > 0; i--) {
       	 int pos = i - 1;
       	 
          char c = input.charAt(pos);
          c++;
          
          if (c <= 'z') {
             if (i == 0)
                return c + input.substring(pos, input.length());
             else if (i == input.length())
                return input.substring(0, pos) + c;
             else
                return input.substring(0, pos) + c + input.substring(pos, input.length() - 1);
          } else {
             input = replaceChar(input, pos, 'a');
          }
       
       }
       
       return null;
      
    }
    
    /**
     * Replaces a single character in a <code>String</code>
    */
    private String replaceChar(String input, int pos, char c) {
             if (pos == 0)
                return c + input.substring(pos, input.length());
             else if (pos == input.length())
                return input.substring(0, pos) + c;
             else
                return input.substring(0, pos) + c + input.substring(pos, input.length() - 1);
    }

    
}