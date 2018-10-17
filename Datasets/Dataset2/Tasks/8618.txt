import org.apache.commons.beanutils.PropertyUtils;

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


package com.wintecinc.struts.action;

import java.io.IOException;
import java.util.Locale;
import java.util.Collection;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;
import javax.sql.DataSource;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionError;
import org.apache.struts.action.ActionErrors;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.util.MessageResources;
import org.apache.struts.util.PropertyUtils;


/**
 * <p>Abstract Implementation of <strong>Action</strong> that contains constants and
 * the basic framework and methods for form operations. </p>
 *
 * @author David Winterfeldt
*/
public abstract class GenericAction extends Action {

    /**
     * The request scope attribute under which our Message object is stored
    */
    public final static String MESSAGE_KEY = "com.wintecinc.struts.action.messages";

    /**
     * The request scope attribute under which our Search results object is stored
    */
    public final static String SEARCH_KEY = "com.wintecinc.struts.action.search";

    // Actions
    /**
     * Action constant.
    */
    public final static String CREATE = "create";

    /**
     * Action constant.
    */
    public final static String EDIT = "edit";

    /**
     * Action constant.
    */
    public final static String SAVE_KEY = "button.save";

    /**
     * Action constant.
    */
    public final static String DELETE = "delete";

    /**
     * Action constant.
    */
    public final static String CONFIRM_KEY = "button.confirm";

    /**
     * Action constant.
    */
    public final static String SUBMIT = "submit";

    // Mappings
    /**
     * Mapping constant.
    */
    public final static String SUCCESS = "success";

    /**
     * Mapping constant.
    */
    public final static String FAILURE = "failure";

    /**
     * Mapping constant.
    */
    public final static String SEARCH = "search";
    
    // Action and Mapping
    /**
     * Action and Mapping constant.
    */
    public final static String REPORT = "report";

    /**
     * Action and Mapping constant.
    */
    public final static String INPUT = "input";
            
    /**
     * <p>Process the specified HTTP request, and create the corresponding HTTP
     * response (or forward to another web component that will create it).
     * Return an <code>ActionForward</code> instance describing where and how
     * control should be forwarded, or <code>null</code> if the response has
     * already been completed.<p>
     *
     * @param mapping 	The ActionMapping used to select this instance
     * @param form 	The optional ActionForm bean for this request (if any)
     * @param request 	The HTTP request we are processing
     * @param response 	The HTTP response we are creating
     *
     * @exception IOException if an input/output error occurs
     * @exception ServletException if a servlet exception occurs
     */
    public ActionForward perform(ActionMapping mapping,
				 ActionForm form,
				 HttpServletRequest request,
				 HttpServletResponse response)
	throws IOException, ServletException {

	// Extract attributes and parameters we will need
	Locale locale = getLocale(request);
	MessageResources messages = getResources();
	HttpSession session = request.getSession();
	
	GenericForm info = (GenericForm)form;
	String action = info.getAction();
	
	if (action == null)
	   action = request.getParameter("action");
	if (action == null)
	   action = "Create";

        log(mapping.getAttribute() + ":  Processing " + action + " action");

	// Was this transaction cancelled?
	if (isCancelled(request)) {
	    log(" " + mapping.getAttribute() + " Transaction '" + action + "' was cancelled");
	    
	    cancel(request, info);
	    
	    removeFormBean(mapping, request);

	    return (mapping.findForward(SUCCESS));
	}
	
	String save = messages.getMessage(locale, SAVE_KEY);
	String confirm = messages.getMessage(locale, CONFIRM_KEY);
	
	save = (save != null ? save : "");
	confirm = (confirm != null ? confirm : "");
	
	// Handles Multi-Part Forms
	// assumes the forwards start with 'input' (ex: input1, input2 for page 1, page 2)
	ActionForward input = null;
	ActionForward nextInput = null;

	if (info.getPage() != 0) {
	   input = mapping.findForward(INPUT + info.getPage());
	   nextInput = mapping.findForward(INPUT + (info.getPage() + 1));
	}
	
	// Create with Save button 
	if (action.equalsIgnoreCase(CREATE) && save.equalsIgnoreCase(request.getParameter(SUBMIT))) {
	   // Validate is called here instead of through the framework because otherwise it 
	   // will try to validate on cancels, getInfo, etc.
	   ActionErrors errors = form.validate(mapping, request);	
	
	   if (errors == null || errors.empty()) {
      	      try {
      	      	 //System.out.println("insert");
      	      	 
      	      	 if (nextInput != null)
      	      	    return nextInput;
      	      	 else
      	            insert(request, info);
      	      } catch (DuplicateNameException dne) {
      	         return (new ActionForward(mapping.getInput()));
	      } catch (Exception e) {
		 saveErrors(request, getSystemError());
		 return (mapping.findForward(FAILURE));
	      }
	      
	      removeFormBean(mapping, request);
      	        
      	      return (mapping.findForward(SUCCESS));	
      	   } else {
	      saveErrors(request, errors);
      	      
      	      if (input != null)
      	         return input;
      	      else
	         return (new ActionForward(mapping.getInput()));		
      	   }
      	// Edit with Save button 
	} else if (action.equalsIgnoreCase(EDIT) && save.equalsIgnoreCase(request.getParameter(SUBMIT))) {
      	   ActionErrors errors = form.validate(mapping, request);	
      	
      	   if (errors == null || errors.empty()) {
      	      try {
      	      	 //System.out.println("update");

      	      	 if (nextInput != null)
      	      	    return nextInput;
      	      	 else
      	            update(request, info);
      	      } catch (DuplicateNameException dne) {
      	         return (new ActionForward(mapping.getInput()));
	      } catch (Exception e) {
		 saveErrors(request, getSystemError());
		 return (new ActionForward(mapping.getInput()));
	      }

	      removeFormBean(mapping, request);
                    	      
      	      return (mapping.findForward(SUCCESS));	
      	   } else {
	      saveErrors(request, errors);

      	      if (input != null)
      	         return input;
      	      else
	         return (new ActionForward(mapping.getInput()));	
      	   }
      	// Delete with Confirm button 
	} else if (action.equalsIgnoreCase(DELETE) && confirm.equalsIgnoreCase(request.getParameter(SUBMIT))) {
      	      try {
      	      	 //System.out.println("delete");
      	         delete(request, info);
	      } catch (Exception e) {
		 saveErrors(request, getSystemError());
		 return (mapping.findForward(FAILURE));
	      }

	      removeFormBean(mapping, request);
              
	      return (mapping.findForward(SUCCESS));
	} else if (action.equals(SEARCH)) {
      	   try {
      	      //System.out.println("search");
      	      search(request, info);
	   } catch (Exception e) {
	      saveErrors(request, getSystemError());
	   }	   
	   info.setAction(SEARCH);
	   return (mapping.findForward(SEARCH));
	} else if (action.equals(EDIT)) {
	   //System.out.println("getInfo() edit");
	   try { PropertyUtils.copyProperties(info, getInfo(request, info)); } catch (Exception e) {}
	   info.setAction(EDIT);
	   return (new ActionForward(mapping.getInput()));
	} else if (action.equalsIgnoreCase(DELETE)) {
	   //System.out.println("getInfo() delete");
	   try { PropertyUtils.copyProperties(info, getInfo(request, info)); } catch (Exception e) {}
	   info.setAction(DELETE);
	   return (new ActionForward(mapping.getInput()));
	} else if (action.equals(REPORT)) {
	   try { PropertyUtils.copyProperties(info, getInfo(request, info)); } catch (Exception e) {}
	   info.setAction(REPORT);
	   return mapping.findForward(REPORT);
	} else if (action.equals(CREATE)) {
	    return (new ActionForward(mapping.getInput()));
	}

	// Forward control to the specified success URI
        log(mapping.getAttribute() + " Action failure.");

	saveErrors(request, getSystemError());
	return (mapping.findForward(FAILURE));
    }
    
    /**
     * Cancels an action.
    */  
    protected void cancel(HttpServletRequest request, GenericForm form) { }

    /**
     * Inserts a record.
    */  
    protected abstract void insert(HttpServletRequest request, GenericForm form) throws Exception;

    /**
     * Updates a record.
    */  
    protected abstract void update(HttpServletRequest request, GenericForm form) throws Exception;

    /**
     * Deletes a record.
    */  
    protected abstract void delete(HttpServletRequest request, GenericForm form) throws Exception;

    /**
     * Retrieves a record into a <code>GenericForm</code> object.
    */  
    protected abstract GenericForm getInfo(HttpServletRequest request, GenericForm form);

    /**
     * Perform a search and put the results into request scope.
    */  
    protected abstract void search(HttpServletRequest request, GenericForm form) throws Exception;

    /**
     * Returns a general system error message.
    */  
    protected ActionErrors getSystemError() {
       ActionErrors errors = new ActionErrors();
       errors.add(ActionErrors.GLOBAL_ERROR, new ActionError("error.system"));	
       
       return errors;
    }

    /**
     * Returns a general no results search message.
    */  
    protected ActionMessages getSearchNoResults() {
       ActionMessages messages = new ActionMessages();
       messages.add(new ActionMessage("app.search.noresults"));	       
       
       return messages;
    }

    /**
     * Save the specified messages keys into the appropriate request
     * attribute for use by the &lt;app:messages&gt; tag, if any messages
     * are required.  Otherwise, ensure that the request attribute is not
     * created.
     *
     * @param 	request 	The servlet request we are processing
     * @param 	messages 		Messages object
     */
    protected void saveMessages(HttpServletRequest request, ActionMessages messages) {
	// Remove messages attribute if none are required
	if ((messages == null) || messages.empty()) {
	    request.removeAttribute(MESSAGE_KEY);
	    return;
	}

	// Save the messages we need
	request.setAttribute(MESSAGE_KEY, messages);
    }

    /**
     * Save the specified search results into the appropriate request
     * attribute for use by the search JSP page.
     *
     * @param 	request 	The servlet request we are processing
     * @param 	collection      Messages object
     */
    protected void saveSearchResults(HttpServletRequest request, Collection collection) {

	// Remove any error messages attribute if none are required
	if ((collection == null) || collection.isEmpty()) {
	    request.removeAttribute(SEARCH_KEY);
	    return;
	}

	// Save the error messages we need
	request.setAttribute(SEARCH_KEY, collection);

    }

    /**
     * Convenience method that call the comparable servlet log method and writes 
     * an explanatory message and a stack trace for a given Throwable exception to the 
     * servlet log file.
     *
     * @param 	message		String that describes the error or exception
    */
    protected void log(String message) {
       if (servlet.getDebug() >= 1)
           servlet.log(message);
    }

    /**
     * Convenience method that call the comparable servlet log method and writes 
     * an explanatory message and a stack trace for a given Throwable exception to the 
     * servlet log file.
     *
     * @param 	message		String that describes the error or exception
     * @param 	throwable	Throwable error or exception
    */
    protected void log(String message, Throwable throwable) {
       if (servlet.getDebug() >= 1)
           servlet.log(message, throwable);
    }

    /**
     * Convenience method for removing the obsolete form bean.
     *
     * @param mapping The ActionMapping used to select this instance
     * @param request The HTTP request we are processing
    */    
    protected void removeFormBean(ActionMapping mapping, HttpServletRequest request) {
       // Remove the obsolete form bean
       if (mapping.getAttribute() != null) {
           if ("request".equals(mapping.getScope())) {
               request.removeAttribute(mapping.getAttribute());
           } else {
              HttpSession session = request.getSession();
              session.removeAttribute(mapping.getAttribute());
           }
       }
    }

    /**
     * Get a JDBC Connection to the default database for the web app from the connection pool.
    */
    protected Connection getConnection() throws SQLException {
       DataSource ds = (DataSource)servlet.getServletContext().getAttribute(Action.DATA_SOURCE_KEY);
       return ds.getConnection();
    }
   
    /**
     * Get's the next value from the table and field specified.
     *
     * @param		con		JDBC <code>Connection</code> to use.
     * @param		table		Table
     * @param		field		Primary Key Field
    */
    protected int getNextKey(Connection con, String table, String field) throws SQLException {
        Statement stmt = null;
        ResultSet rs = null;

        int iKey = 0;

        try {
	   stmt = con.createStatement();
           rs = stmt.executeQuery("SELECT MAX(" + field + ") FROM " + table);

           if (rs.next()) {
              iKey = rs.getInt(1) + 1;
           }
        } catch (SQLException e) {
           log("GenericAction::getNextKey() - " + e.getMessage(), e);
           throw e;
        } catch (Exception e) {
           log("GenericAction::getNextKey() - " + e.getMessage(), e);
        } finally {
           if (rs != null)
              try { rs.close(); } catch (Exception e) {}
           if (stmt != null)
              try { stmt.close(); } catch (Exception e) {}
        }
        return iKey;
    }
    
    /**
     * This class is used for throwing an exception if a user tries to
     * insert a duplicate field into a field with a unique key on it.
    */    
    protected class DuplicateNameException extends Exception {

       public DuplicateNameException() {
          super();	
       }	
       
       public DuplicateNameException(String msg) {
          super(msg);	
       }	
    }

}