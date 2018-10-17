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
 
 
package com.wintecinc.struts.validation;

import java.util.Locale;
import javax.servlet.ServletContext;
import javax.servlet.http.HttpServletRequest;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionError;
import org.apache.struts.action.ActionErrors;
import org.apache.struts.util.MessageResources;
import org.apache.struts.util.PropertyUtils;
import com.wintecinc.struts.action.ValidatorServlet;

/**
 * <p>This class helps provides some useful methods for retrieving objects 
 * from different scopes of the application.</p>
 *
 * @author David Winterfeldt
*/
public class ValidatorUtil  {
   
   private static Locale defaultLocale = Locale.getDefault();

   /**
    * <p>Replace part of a <code>String</code> with another value.</p>
    *
    * @param	value		<code>String</code> to perform the replacement on.
    * @param	key		The name of the constant.
    * @param	replaceValue	The value of the constant.
   */
   public static String replace(String value, String key, String replaceValue) {
      if (value != null && key != null && replaceValue != null) {
         int pos = value.indexOf(key);
          
         if (pos >= 0) {
            int length = value.length();
            int start = pos;
            int end = pos + key.length();
         
            if (length == key.length()) {
               value = replaceValue;
            } else if (end == length) {
               value = value.substring(0, start) + replaceValue; //+ value.substring(end);
            } else {
            	value = value.substring(0, start) + replaceValue + replace(value.substring(end), key, replaceValue);
            }
         }
      }
      return value;
   }

   /**
    * Convenience method for getting a value from a bean property as a <code>String</code>.
   */
   public static String getValueAsString(Object bean, String property) {
      Object value = null;

      try {
         value = PropertyUtils.getProperty(bean, property);	
      } catch (Exception e) {
         //log("ValidatorUtil::getValueAsString() - " + e.getMessage(), e);
      }
   	
      return (value != null ? value.toString() : null);    	
   }
   
   /**
    * Retrieve <code>ValidatorResources</code> for the application.
   */
   public static ValidatorResources getValidatorResources(ServletContext application) {
      return (ValidatorResources)application.getAttribute(ValidatorServlet.VALIDATOR_KEY);
   }

   /**
    * Retrieve <code>MessageResources</code> for the application.
   */
   public static MessageResources getMessageResources(ServletContext application) {
      return (MessageResources)application.getAttribute(Action.MESSAGES_KEY);
   }

   /**
    * Get the <code>Locale</code> of the current user.
   */
   public static Locale getLocale(HttpServletRequest request) {
      Locale locale = null;
      try {
          locale = (Locale) request.getSession().getAttribute(Action.LOCALE_KEY);
      } catch (IllegalStateException e) {	// Invalidated session
          locale = null;
      }
      if (locale == null)
          locale = defaultLocale;
          
      return locale;
   }
   
   /**
    * Gets the <code>Locale</code> sensitive value based on the key passed in.
   */
   public static String getMessage(MessageResources messages, Locale locale, String key) {
      String message = null;                       
      
      if (messages != null)
         message = messages.getMessage(locale, key);
      if (message == null)
         message = "";
      
      return message;
   }

   /**
    * Gets the <code>Locale</code> sensitive value based on the key passed in.
   */
   public static String getMessage(ServletContext application, HttpServletRequest request, String key) {
      MessageResources messages = getMessageResources(application);
      
      return getMessage(messages, getLocale(request), key);
   }

   /**
    * Gets the locale sensitive message based on the <code>ValidatorAction</code> message and the 
    * <code>Field</code>'s arg objects.
   */
   public static String getMessage(MessageResources messages, Locale locale, 
                                   ValidatorAction va, Field field) {

      String arg[] = getArgs(va.getName(), messages, locale, field);
      String msg = (field.getMsg(va.getName()) != null ? field.getMsg(va.getName()) : va.getMsg());
      
      return messages.getMessage(locale, msg, arg[0], arg[1], arg[2], arg[3]);
   }

   /**
    * Gets the <code>ActionError</code> based on the <code>ValidatorAction</code> message and the 
    * <code>Field</code>'s arg objects.
   */
   public static ActionError getActionError(ServletContext application, HttpServletRequest request, 
                                            ValidatorAction va, Field field) {

      String arg[] = getArgs(va.getName(), getMessageResources(application), getLocale(request), field);
      String msg = (field.getMsg(va.getName()) != null ? field.getMsg(va.getName()) : va.getMsg());
      
      return new ActionError(msg, arg[0], arg[1], arg[2], arg[3]);
   }

   /**
    * Gets the message arguments based on the current <code>ValidatorAction</code> 
    * and <code>Field</code>.
   */
   public static String[] getArgs(String actionName, MessageResources messages, 
                                  Locale locale, Field field) {
      
      Arg arg0 = field.getArg0(actionName);
      Arg arg1 = field.getArg1(actionName);
      Arg arg2 = field.getArg2(actionName);
      Arg arg3 = field.getArg3(actionName);
      
      String sArg0 = null;
      String sArg1 = null;
      String sArg2 = null;
      String sArg3 = null;
      
      if (arg0 != null) {
         if ("true".equals(arg0.getResource()))
            sArg0 = getMessage(messages, locale, arg0.getKey());
         else
            sArg0 = arg0.getKey();
      }
      
      if (arg1 != null) {
         if ("true".equals(arg1.getResource()))
            sArg1 = getMessage(messages, locale, arg1.getKey());
         else
            sArg1 = arg1.getKey();
      }
      
      if (arg2 != null) {
         if ("true".equals(arg2.getResource()))
            sArg2 = getMessage(messages, locale, arg2.getKey());
         else
            sArg2 = arg2.getKey();
      }
      
      if (arg3 != null) {
         if ("true".equals(arg3.getResource()))
            sArg3 = getMessage(messages, locale, arg3.getKey());
         else
            sArg3 = arg3.getKey();
      }   	
   	 
      return new String[] { sArg0, sArg1, sArg2, sArg3 };
      
   }
   
   /**
    * Writes a message based on the <code>Writer</code> defined in <code>MessageResources</code>.
   */
   public static void log(ServletContext application, String message) {
      MessageResources messages = getMessageResources(application);
      
      if (messages != null)
         messages.log(message);
   }

   /**
    * Writes a message based on the <code>Writer</code> defined in <code>MessageResources</code>.
   */
   public static void log(ServletContext application, String message, Throwable t) {
      MessageResources messages = getMessageResources(application);
      
      if (messages != null)
         messages.log(message, t);
   }
   
}