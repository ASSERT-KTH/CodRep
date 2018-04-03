sb.append(" selected=\"selected\"");

/*
 * ====================================================================
 *
 * The Apache Software License, Version 1.1
 *
 * Copyright (c) 1999-2001 The Apache Software Foundation.  All rights
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
 *
 */

package org.apache.struts.taglib.html;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import javax.servlet.jsp.JspException;
import javax.servlet.jsp.JspWriter;
import javax.servlet.jsp.PageContext;
import javax.servlet.jsp.tagext.TagSupport;
import org.apache.struts.util.IteratorAdapter;
import org.apache.struts.util.MessageResources;
import org.apache.struts.util.PropertyUtils;
import org.apache.struts.util.ResponseUtils;
import java.util.Arrays;
import java.util.Collection;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.Map;


/**
 * Tag for creating multiple &lt;select&gt; options from a collection.  The
 * associated values displayed to the user may optionally be specified by a
 * second collection, or will be the same as the values themselves.  Each
 * collection may be an array of objects, a Collection, an Enumeration,
 * an Iterator, or a Map.
 * <b>NOTE</b> - This tag requires a Java2 (JDK 1.2 or later) platform.
 *
 * @author Florent Carpentier
 * @author Craig McClanahan
 */

public class OptionsTag extends TagSupport {

    /**
     * The message resources for this package.
     */
    protected static MessageResources messages =
     MessageResources.getMessageResources(Constants.Package + ".LocalStrings");

    /**
     * The name of the collection containing beans that have properties to
     * provide both the values and the labels (identified by the
     * <code>property</code> and <code>labelProperty</code> attributes).
     */
    protected String collection = null;

    public String getCollection() {
        return (this.collection);
    }

    public void setCollection(String collection) {
        this.collection = collection;
    }


    /**
     * The name of the bean containing the labels collection.
     */
    protected String labelName = null;

    public String getLabelName() {
	return labelName;
    }

    public void setLabelName(String labelName) {
	this.labelName = labelName;
    }

    /**
     * The bean property containing the labels collection.
     */
    protected String labelProperty = null;

    public String getLabelProperty() {
	return labelProperty;
    }

    public void setLabelProperty(String labelProperty) {
	this.labelProperty = labelProperty;
    }

    /**
     * The name of the bean containing the values collection.
     */
    protected String name=null;

    public String getName() {
	return name;
    }

    public void setName(String name) {
	this.name = name;
    }


    /**
     * The name of the property to use to build the values collection.
     */
    protected String property=null;

    public String getProperty() {
	return property;
    }

    public void setProperty(String property) {
	this.property = property;
    }


    /**
     * Process the start of this tag.
     *
     * @exception JspException if a JSP exception has occurred
     */

    public int doStartTag() throws JspException {
	return SKIP_BODY;
    }

    /**
     * Process the end of this tag.
     *
     * @exception JspException if a JSP exception has occurred
     */
    public int doEndTag() throws JspException {

	// Acquire the select tag we are associated with
	SelectTag selectTag =
	  (SelectTag) pageContext.getAttribute(Constants.SELECT_KEY);
	if (selectTag == null)
	    throw new JspException
	        (messages.getMessage("optionsTag.select"));
	StringBuffer sb = new StringBuffer();

        // If a collection was specified, use that mode to render options
        if (collection != null) {
            Iterator collIterator = getIterator(collection, null);
            while (collIterator.hasNext()) {

                Object bean = collIterator.next();
                Object value = null;
                Object label = null;;

                try {
                    value = PropertyUtils.getProperty(bean, property);
                    if (value == null)
                        value = "";
                } catch (IllegalAccessException e) {
                    throw new JspException
                        (messages.getMessage("getter.access",
                                             property, collection));
                } catch (InvocationTargetException e) {
                    Throwable t = e.getTargetException();
                    throw new JspException
                        (messages.getMessage("getter.result",
                                             property, t.toString()));
                } catch (NoSuchMethodException e) {
                    throw new JspException
                        (messages.getMessage("getter.method",
                                             property, collection));
                }

                try {
                    if (labelProperty != null)
                        label =
                            PropertyUtils.getProperty(bean, labelProperty);
                    else
                        label = value;
                    if (label == null)
                        label = "";
                } catch (IllegalAccessException e) {
                    throw new JspException
                        (messages.getMessage("getter.access",
                                             labelProperty, collection));
                } catch (InvocationTargetException e) {
                    Throwable t = e.getTargetException();
                    throw new JspException
                        (messages.getMessage("getter.result",
                                             labelProperty, t.toString()));
                } catch (NoSuchMethodException e) {
                    throw new JspException
                        (messages.getMessage("getter.method",
                                             labelProperty, collection));
                }


                String stringValue = value.toString();
                addOption(sb, stringValue, label.toString(),
                          selectTag.isMatched(stringValue));

            }

        }

        // Otherwise, use the separate iterators mode to render options
        else {

              // Construct iterators for the values and labels collections
              Iterator valuesIterator = getIterator(name, property);
              Iterator labelsIterator = null;
              if ((labelName == null) && (labelProperty == null))
                  labelsIterator = getIterator(name, property); // Same coll.
              else
                  labelsIterator = getIterator(labelName, labelProperty);

              // Render the options tags for each element of the values coll.
              while (valuesIterator.hasNext()) {
                  String value = valuesIterator.next().toString();
                  String label = value;
                  if (labelsIterator.hasNext())
                      label = labelsIterator.next().toString();
                  addOption(sb, value, label,
                            selectTag.isMatched(value));
              }
	}

	// Render this element to our writer
        ResponseUtils.write(pageContext, sb.toString());

        // Evaluate the remainder of this page
	return EVAL_PAGE;

    }


    /**
     * Release any acquired resources.
     */
    public void release() {

	super.release();
        collection = null;
	labelName = null;
	labelProperty = null;
	name = null;
	property = null;

    }


    // ------------------------------------------------------ Protected Methods


    /**
     * Add an option element to the specified StringBuffer based on the
     * specified parameters.
     *
     * @param sb StringBuffer accumulating our results
     * @param value Value to be returned to the server for this option
     * @param label Value to be shown to the user for this option
     * @param matched Should this value be marked as selected?
     */
    protected void addOption(StringBuffer sb, String value, String label,
                             boolean matched) {

        sb.append("<option value=\"");
        sb.append(value);
        sb.append("\"");
        if (matched)
            sb.append(" selected=\"true\"");
        sb.append(">");
        sb.append(ResponseUtils.filter(label));
        sb.append("</option>\r\n");

    }


    /**
     * Return an iterator for the option labels or values, based on our
     * configured properties.
     *
     * @param name Name of the bean attribute (if any)
     * @param property Name of the bean property (if any)
     *
     * @exception JspException if an error occurs
     */
    protected Iterator getIterator(String name, String property)
        throws JspException {

	// Identify the bean containing our collection
	String beanName = name;
	if (beanName == null)
	    beanName = Constants.BEAN_KEY;
	Object bean = pageContext.findAttribute(beanName);
	if (bean == null)
	    throw new JspException
	        (messages.getMessage("getter.bean", beanName));

	// Identify the collection itself
	Object collection = bean;
	if (property != null) {
	    try {
		collection = PropertyUtils.getProperty(bean, property);
	    } catch (IllegalAccessException e) {
		throw new JspException
		    (messages.getMessage("getter.access", property, name));
	    } catch (InvocationTargetException e) {
		Throwable t = e.getTargetException();
		throw new JspException
		    (messages.getMessage("getter.result",
					 property, t.toString()));
	    } catch (NoSuchMethodException e) {
		throw new JspException
		    (messages.getMessage("getter.method", property, name));
	    }
	}

	// Construct and return an appropriate iterator
	if (collection.getClass().isArray())
	    collection = Arrays.asList((Object[]) collection);
	if (collection instanceof Collection)
	    return (((Collection) collection).iterator());
	else if (collection instanceof Iterator)
	    return ((Iterator) collection);
	else if (collection instanceof Map)
	    return (((Map) collection).entrySet().iterator());
    else if (collection instanceof Enumeration)
	    return( new IteratorAdapter((Enumeration)collection));
	else
	    throw new JspException
	        (messages.getMessage("optionsTag.iterator",
	                             collection.toString()));

    }

}