parser.flushCharData(parser.tmplStart, parser.tmplStop);

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
 * 4. The names "The Jakarta Project", "Tomcat", and "Apache Software
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
package org.apache.jasper.compiler;

import java.util.Vector;
import java.util.Hashtable;
import java.util.Enumeration;

import java.io.CharArrayWriter;
import org.apache.jasper.JasperException;
import org.apache.jasper.Constants;

import javax.servlet.jsp.tagext.TagLibraryInfo;
import javax.servlet.jsp.tagext.TagInfo;

import org.apache.tomcat.logging.Logger;

/**
 * The class that parses the JSP input and calls the right methods on
 * the code generator backend. 
 *
 * @author Anil K. Vijendran
 * @author Rajiv Mordani
 */
public class Parser {
    /**
     * The input source we read from...
     */
    private JspReader reader;

    /**
     * The backend that is notified of constructs recognized in the input... 
     */
    private ParseEventListener listener;

    /*
     * Char buffer for HTML data
     */
    CharArrayWriter caw;

    /*
     * Marker for start and end of the tempate data.
     */
    Mark tmplStart;
    Mark tmplStop;

    /*
     * Name of the current file.
     * Useful to preserve the line number information in
     * case of an include.
     */
    String currentFile;

    public interface Action {
        void execute(Mark start, Mark stop) throws JasperException;
    }

    public Parser(JspReader reader, final ParseEventListener lnr) {
	this.reader = reader;
	this.listener = new DelegatingListener(lnr,
                                               new Action() {
                                                       public void execute(Mark start, Mark stop) 
                                                           throws JasperException 
                                                       {
                                                           Parser.this.flushCharData(start, stop);
                                                       }
                                                   });
	this.caw = new CharArrayWriter();
	this.currentFile = reader.mark().getFile();
    }

    static final Vector coreElements = new Vector();

    /*
     * JSP directives
     */
    static final class Directive implements CoreElement {
	private static final String OPEN_DIRECTIVE  = "<%@";
	private static final String CLOSE_DIRECTIVE = "%>";

	static final String[] directives = {
	  "page",
	  "include",
	  "taglib"
	};

	private static final JspUtil.ValidAttribute[] pageDvalidAttrs = {
	    new JspUtil.ValidAttribute ("language"),
	    new JspUtil.ValidAttribute ("extends"),
	    new JspUtil.ValidAttribute ("import"),
	    new JspUtil.ValidAttribute ("session"),
	    new JspUtil.ValidAttribute ("buffer"),
	    new JspUtil.ValidAttribute ("autoFlush"),
	    new JspUtil.ValidAttribute ("isThreadSafe"),
	    new JspUtil.ValidAttribute ("info"),
	    new JspUtil.ValidAttribute ("errorPage"),
	    new JspUtil.ValidAttribute ("isErrorPage"),
	    new JspUtil.ValidAttribute ("contentType")
	};

	private static final JspUtil.ValidAttribute[] includeDvalidAttrs = {
	    new JspUtil.ValidAttribute ("file", true)
	};

	private static final JspUtil.ValidAttribute[] tagDvalidAttrs = {
	    new JspUtil.ValidAttribute ("uri", true),
	    new JspUtil.ValidAttribute ("prefix", true)
	};

	public boolean accept(ParseEventListener listener, JspReader reader, 
			      Parser parser) throws JasperException
	{
	    String close;
	    String open;
	    
	    if (reader.matches(OPEN_DIRECTIVE)) {
		open = OPEN_DIRECTIVE;
		close = CLOSE_DIRECTIVE;
	    } else
		return false;

	    Mark start = reader.mark();
	    reader.advance(open.length());
	    reader.skipSpaces();
	    
	    // Check which directive it is.
	    String match = null;
	    for(int i = 0; i < directives.length; i++)
		if (reader.matches(directives[i])) {
		    match = directives[i];
		    break;
		}
	    if (match == null)
		throw new ParseException(reader.mark(),
					 Constants.getString("jsp.error.invalid.directive"));

	    reader.advance(match.length());

	    // Parse the attr-val pairs.
	    Hashtable attrs = reader.parseTagAttributes();
	    if (match.equals ("page"))
	        JspUtil.checkAttributes ("Page directive", attrs, 
					 pageDvalidAttrs);
	    else if (match.equals("include"))
	        JspUtil.checkAttributes ("Include directive", attrs, 
					 includeDvalidAttrs);
	    else if (match.equals("taglib"))
	        JspUtil.checkAttributes ("Taglib directive", attrs, 
					 tagDvalidAttrs);
	    
	    // Match close.
	    reader.skipSpaces();
	    if (!reader.matches(close))
                throw new ParseException(reader.mark(), 
                                         Constants.getString("jsp.error.unterminated", 
                                                             new Object[] { open }));
	    else
		reader.advance(close.length());

	    Mark stop = reader.mark();

	    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);
	    listener.handleDirective(match, start, stop, attrs);
	    return true;
	}

    }
  
    static {
	coreElements.addElement(new Directive());
    }

    /*
     * Include action
     */
    static final class Include implements CoreElement {
	private static final String OPEN_INCLUDE = "<jsp:include";
	private static final String CLOSE_INCLUDE_NO_BODY = "/>";
	private static final String CLOSE_INCLUDE_BODY = ">";
	private static final String CLOSE_INCLUDE = "</jsp:include>";
	private static final String OPEN_INDIVIDUAL_PARAM = "<jsp:param";
	private static final String CLOSE_INDIVIDUAL_PARAM = "/>";

	private static final JspUtil.ValidAttribute[] validAttributes = {
            new JspUtil.ValidAttribute("page", true),
            new JspUtil.ValidAttribute("flush")
	};

	public boolean accept(ParseEventListener listener, JspReader reader, 
                              Parser parser) 
	    throws JasperException 
	{
	    if (reader.matches(OPEN_INCLUDE)) {
		Hashtable param = new Hashtable();
		Mark start = reader.mark();
		reader.advance(OPEN_INCLUDE.length());
		Hashtable attrs = reader.parseTagAttributes();
		JspUtil.checkAttributes ("Include", attrs, validAttributes);
		reader.skipSpaces();
		
		if (!reader.matches(CLOSE_INCLUDE_NO_BODY)) {
		    
		    if (!reader.matches(CLOSE_INCLUDE_BODY))
			throw new ParseException(reader.mark(), 
						 Constants.getString
						 ("jsp.error.unterminated", 
						  new Object[] { OPEN_INCLUDE }));
		    reader.advance(CLOSE_INCLUDE_BODY.length());

		    reader.skipSpaces();
		    if (!reader.matches(CLOSE_INCLUDE)) {
			
			// Parse the params.
			reader.skipSpaces();
			if (!reader.matches (OPEN_INDIVIDUAL_PARAM))
			    throw new ParseException (reader.mark(),
						      Constants.getString
						      ("jsp.error.paramexpected"));

			//Parse zero or more param tags.
			while (reader.matches(OPEN_INDIVIDUAL_PARAM)) {
			
			    reader.parsePluginParamTag(param);
			    reader.skipSpaces ();
			
			    if (!reader.matches (CLOSE_INDIVIDUAL_PARAM))
				throw new ParseException (reader.mark(),
							  Constants.getString
							  ("jsp.error.unterminated",
							   new Object[] {OPEN_INDIVIDUAL_PARAM}));
			    reader.advance (CLOSE_INDIVIDUAL_PARAM.length ());
			    reader.skipSpaces();
			}
		    }
		    
		    if (!reader.matches(CLOSE_INCLUDE))
			throw new ParseException(reader.mark(), 
						 Constants.getString
						 ("jsp.error.unterminated", 
						  new Object[] { OPEN_INCLUDE }));
		    reader.advance(CLOSE_INCLUDE.length());
		}
		else
		    reader.advance(CLOSE_INCLUDE_NO_BODY.length());
		Mark stop = reader.mark();
		listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		
		listener.handleInclude(start, stop, attrs, param);
		return true;
	    } else
		return false;
	}
    }

    static {
	coreElements.addElement(new Include());
    }
  
    /*
     * Forward action
     */
    static final class Forward implements CoreElement {
	private static final String OPEN_FORWARD = "<jsp:forward";
	private static final String CLOSE_FORWARD_NO_BODY = "/>";
	private static final String CLOSE_FORWARD_BODY = ">";
	private static final String CLOSE_FORWARD = "</jsp:forward>";
	private static final String OPEN_INDIVIDUAL_PARAM = "<jsp:param";
	private static final String CLOSE_INDIVIDUAL_PARAM = "/>";

	private static final JspUtil.ValidAttribute[] validAttributes = {
	   new JspUtil.ValidAttribute("page", true)
	};
	public boolean accept(ParseEventListener listener, JspReader reader, 
				Parser parser) 
	    throws JasperException 
	{
	    if (reader.matches(OPEN_FORWARD)) {
		Mark start = reader.mark();
		reader.advance(OPEN_FORWARD.length());
		Hashtable attrs = reader.parseTagAttributes();
		Hashtable param = new Hashtable();
	        JspUtil.checkAttributes ("Forward", attrs, validAttributes);
		reader.skipSpaces();
		if (!reader.matches(CLOSE_FORWARD_NO_BODY)) {
		    if (!reader.matches(CLOSE_FORWARD_BODY))
			throw new ParseException(reader.mark(), 
						 Constants.getString
						 ("jsp.error.unterminated", 
						  new Object[] { OPEN_FORWARD }));
		    reader.advance(CLOSE_FORWARD_BODY.length());
		    reader.skipSpaces();

		    if (!reader.matches(CLOSE_FORWARD)) {
			
			// Parse the params.
			reader.skipSpaces();
			if (!reader.matches (OPEN_INDIVIDUAL_PARAM))
			    throw new ParseException (reader.mark(),
						      Constants.getString
						      ("jsp.error.paramexpected"));
			// Parse zero or more param tags.
			while (reader.matches(OPEN_INDIVIDUAL_PARAM)) {
			    
			    //Borrow plugin's parse function.
			    reader.parsePluginParamTag(param);
			    reader.skipSpaces();
			    
			    if (!reader.matches (CLOSE_INDIVIDUAL_PARAM))
				throw new ParseException (reader.mark(),
							  Constants.getString
							  ("jsp.error.unterminated",
							   new Object[] {OPEN_INDIVIDUAL_PARAM}));
			    reader.advance (CLOSE_INDIVIDUAL_PARAM.length ());
			    reader.skipSpaces();
			}
		    }
		    
		    if (!reader.matches(CLOSE_FORWARD))
			throw new ParseException(reader.mark(), 
						 Constants.getString
						 ("jsp.error.unterminated", 
						  new Object[] { OPEN_FORWARD }));
		    reader.advance(CLOSE_FORWARD.length());
		}
		else
		    reader.advance(CLOSE_FORWARD_NO_BODY.length());
		
		Mark stop = reader.mark();
		listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		
		listener.handleForward(start, stop, attrs, param);
		return true;
	    } else
		return false;
	}
    }

    static {
	coreElements.addElement(new Forward());
    }


    /*
     * Jsp comments <%--  stuff --%>
     */

    // declarations
    static final class Comment implements CoreElement {

	private static final String OPEN_COMMENT  = "<%--";
	private static final String CLOSE_COMMENT = "--%>";

	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
	    throws JasperException 
	{

	    if (reader.matches(OPEN_COMMENT)) {
		reader.advance(OPEN_COMMENT.length());
		Mark start = reader.mark();
		Mark stop = reader.skipUntil(CLOSE_COMMENT);
		if (stop == null)
		    throw new ParseException(Constants.getString("jsp.error.unterminated", 
                                                                 new Object[] { OPEN_COMMENT }));
		
		parser.flushCharData(start, stop);
		return true;
	    }
	    return false;
	}
    }
	
    static {
	coreElements.addElement(new Comment());
    }

    /*
     * Scripting elements
     */
    
    // declarations
    static final class Declaration implements CoreElement {

	private static final String OPEN_DECL  = "<%!";
	private static final String CLOSE_DECL = "%>";

        private static final JspUtil.ValidAttribute[] validAttributes = {
        };

	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
	    throws JasperException 
	{
	    String close, open, end_open = null;
            Hashtable attrs = null;
				
	    if (reader.matches(OPEN_DECL)) {
		open = OPEN_DECL;
		close = CLOSE_DECL;
	    } else
		return false;

	    reader.advance(open.length());

            if (end_open != null) {
                attrs = reader.parseTagAttributes();

		reader.skipSpaces();
		if (!reader.matches(end_open)) 
		    throw new ParseException(reader.mark(),
			Constants.getString("jsp.error.unterminated"));
	        reader.advance(end_open.length());
		reader.skipSpaces();

		JspUtil.checkAttributes("Declaration", attrs, validAttributes);
            }

	    Mark start = reader.mark();
	    Mark stop = reader.skipUntil(close);
	    if (stop == null)
		throw new ParseException(Constants.getString("jsp.error.unterminated", 
                                                             new Object[] { open }));

	    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);	    
	    listener.handleDeclaration(start, stop, attrs);
	    return true;
	}
    }
	
    static {
	coreElements.addElement(new Declaration());
    }
    
    
    // expressions
    static final class Expression implements CoreElement {

	private static final String OPEN_EXPR  = "<%=";
	private static final String CLOSE_EXPR = "%>";

        private static final JspUtil.ValidAttribute[] validAttributes = {
        };

	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
	    throws JasperException
	{
	    String close, open, end_open=null;
            Hashtable attrs = null;
		
	    if (reader.matches(OPEN_EXPR)) {
		open = OPEN_EXPR;
		close = CLOSE_EXPR;
	    } else
		return false;

	    reader.advance(open.length());

            if (end_open != null) {
                attrs = reader.parseTagAttributes();

		reader.skipSpaces();
		if (!reader.matches(end_open)) 
		    throw new ParseException(reader.mark(),
			Constants.getString("jsp.error.unterminated"));
	        reader.advance(end_open.length());
		reader.skipSpaces();

                JspUtil.checkAttributes("Expression", attrs, validAttributes);
            }

	    Mark start = reader.mark();
	    Mark stop = reader.skipUntil(close);
	    if (stop == null)
		throw new ParseException(reader.mark(), 
                                         Constants.getString("jsp.error.unterminated", 
                                                                 new Object[] { open }));
	    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);	    
	    listener.handleExpression(start, stop, attrs);
	    return true;
	}
    }

    static {
	coreElements.addElement(new Expression());
    }

    // scriptlets
    static final class Scriptlet implements CoreElement {

	private static final String OPEN_SCRIPTLET  = "<%";
	private static final String CLOSE_SCRIPTLET = "%>";

        private static final JspUtil.ValidAttribute[] validAttributes = {
        };

	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
	    throws JasperException
	{
	    String close, open, end_open = null;
            Hashtable attrs = null;
	    
	    if (reader.matches(OPEN_SCRIPTLET)) {
		open = OPEN_SCRIPTLET;
		close = CLOSE_SCRIPTLET;
	    } else
		return false;
		
	    reader.advance(open.length());

            if (end_open != null) {
                attrs = reader.parseTagAttributes();

		reader.skipSpaces();
		if (!reader.matches(end_open)) 
		    throw new ParseException(reader.mark(),
			Constants.getString("jsp.error.unterminated"));
	        reader.advance(end_open.length());
		reader.skipSpaces();

                JspUtil.checkAttributes("Scriptlet", attrs, validAttributes);
            }

	    Mark start = reader.mark();
	    Mark stop = reader.skipUntil(close);
	    if (stop == null)
		throw new ParseException(reader.mark(), 
                                         Constants.getString("jsp.error.unterminated", 
                                                                 new Object[] { open }));
	    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);	    
	    listener.handleScriptlet(start, stop, attrs);
	    return true;
	}
    }

    static {
	coreElements.addElement(new Scriptlet());
    }

    /*
     * UseBean
     */
    static final class Bean implements CoreElement {

	private static final String OPEN_BEAN  = "<jsp:useBean";
	private static final String CLOSE_BEAN = "/>";
	private static final String CLOSE_BEAN_2 = "</jsp:useBean>";
	private static final String CLOSE_BEAN_3 = ">";

	private static final JspUtil.ValidAttribute[] validAttributes = {
	   new JspUtil.ValidAttribute("id"),
	   new JspUtil.ValidAttribute("scope"),
	   new JspUtil.ValidAttribute("class"),
	   new JspUtil.ValidAttribute("type"),
	   new JspUtil.ValidAttribute("beanName")
	};

	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
	    throws JasperException 
	{
	    if (reader.matches(OPEN_BEAN)) {
		Mark start = reader.mark();
		reader.advance(OPEN_BEAN.length());
		Hashtable attrs = reader.parseTagAttributesBean();
	        JspUtil.checkAttributes ("useBean", attrs, validAttributes);
		reader.skipSpaces();
		if (!reader.matches(CLOSE_BEAN)) {
		    if (!reader.matches(CLOSE_BEAN_3))
			throw new ParseException(reader.mark(),
                                                 Constants.getString("jsp.error.unterminated", 
                                                                 new Object[] { "useBean" }));
		    reader.advance(CLOSE_BEAN_3.length());
                    Mark stop = reader.mark();
		    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		    
                    listener.handleBean(start, stop, attrs);
		    int oldSize = reader.size;
		    parser.parse(CLOSE_BEAN_2);
		    if (oldSize != reader.size) {
			throw new ParseException (reader.mark(), 
                                                  Constants.getString("jsp.error.usebean.notinsamefile"));
		    }
		    if (!reader.matches(CLOSE_BEAN_2))
			throw new ParseException(reader.mark(), 
                                                 Constants.getString("jsp.error.unterminated"
								     , 
                                                                     new Object[] { OPEN_BEAN })
						 );

		    reader.advance (CLOSE_BEAN_2.length());
		    
                    listener.handleBeanEnd(start, stop, attrs);
                    return true;
		} else {
                    reader.advance(CLOSE_BEAN.length());
                    Mark stop = reader.mark();
		    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		    
                    listener.handleBean(start, stop, attrs);
                    listener.handleBeanEnd(start, stop, attrs);
                    return true;
                }
	    } else
		return false;
	}
    }

    static {
	coreElements.addElement(new Bean());
    }

    /*
     * GetProperty
     */
    static final class GetProperty implements CoreElement {

	private static final String OPEN_GETPROPERTY  = "<jsp:getProperty";
	private static final String CLOSE_GETPROPERTY = "/>";
	
	private static final JspUtil.ValidAttribute[] validAttributes = {
	   new JspUtil.ValidAttribute("name", true),
	   new JspUtil.ValidAttribute("property", true)
	};

	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
	    throws JasperException 
	{
	    if (reader.matches(OPEN_GETPROPERTY)) {
		Mark start = reader.mark();
		reader.advance(OPEN_GETPROPERTY.length());
		Hashtable attrs = reader.parseTagAttributes ();
	        JspUtil.checkAttributes ("getProperty", attrs, validAttributes);
		reader.skipSpaces();
		if (!reader.matches(CLOSE_GETPROPERTY))
		    throw new ParseException(reader.mark(), 
                                             Constants.getString("jsp.error.unterminated", 
                                                                 new Object[] { OPEN_GETPROPERTY }));
		else
		    reader.advance(CLOSE_GETPROPERTY.length());
		Mark stop = reader.mark();
		listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		
		listener.handleGetProperty(start, stop, attrs);
		return true;
	    } else
		return false;
	}
    }

    static {
	coreElements.addElement(new GetProperty());
    }
    
    /*
     * SetProperty
     */
    static final class SetProperty implements CoreElement {

	private static final String OPEN_SETPROPERTY  = "<jsp:setProperty";
	private static final String CLOSE_SETPROPERTY = "/>";
	
	private static final JspUtil.ValidAttribute[] validAttributes = {
	   new JspUtil.ValidAttribute("name", true),
	   new JspUtil.ValidAttribute("property", true),
	   new JspUtil.ValidAttribute("value"),
	   new JspUtil.ValidAttribute("param")
	};

	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
	    throws JasperException 
	{
	    if (reader.matches(OPEN_SETPROPERTY)) {
		Mark start = reader.mark();
		reader.advance(OPEN_SETPROPERTY.length());
		Hashtable attrs = reader.parseTagAttributes ();
	        JspUtil.checkAttributes ("setProperty", attrs, validAttributes);
		reader.skipSpaces();
		if (!reader.matches(CLOSE_SETPROPERTY))
		    throw new ParseException(reader.mark(), 
                                             Constants.getString("jsp.error.unterminated", 
                                                                 new Object[] { OPEN_SETPROPERTY }));
		else
		    reader.advance(CLOSE_SETPROPERTY.length());
		Mark stop = reader.mark();
		listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		
		listener.handleSetProperty(start, stop, attrs);
		return true;
	    } else
		return false;
	}
    }

    static {
	coreElements.addElement(new SetProperty());
    }

    /*
     * User-defined Tags
     */
    static final class Tag implements CoreElement {
        
        private static final String CLOSE_1 = "/>";
        private static final String CLOSE = ">";
        
	public boolean accept(ParseEventListener listener, JspReader reader, 
                              Parser parser) throws JasperException 
	{
            if (reader.peekChar() != '<')
                return false;

            Mark start = reader.mark();
            reader.nextChar();
            String tag = reader.parseToken(false);

            /*
             * Extract the prefix and the short tag name.
             */
            int i = tag.indexOf(':');
            if (i == -1) {
                reader.reset(start);
                return false;
            }
            String prefix = tag.substring(0, i);
            String shortTagName = null;
            if (++i < tag.length()-1) 
                shortTagName = tag.substring(i);

            
            /*
             * Check if this is a user-defined tag; otherwise we won't touch this...
             */

            TagLibraries libraries = listener.getTagLibraries();
            
            if (!libraries.isUserDefinedTag(prefix, shortTagName)) {
                reader.reset(start);
                return false;
            }

            if (shortTagName == null)
                throw new ParseException(start, "Nothing after the :");

            
            TagLibraryInfoImpl tli = libraries.getTagLibInfo(prefix);
            TagInfo ti = tli.getTag(shortTagName);
            
            if (ti == null)
                throw new ParseException(start, "Unable to locate TagInfo for "+tag);

	    String bc = ti.getBodyContent();

            Hashtable attrs = reader.parseTagAttributes();
            reader.skipSpaces();
            Mark bodyStart = null;
            Mark bodyStop = null;

	    
	    
	    if (reader.matches(CLOSE_1)
		|| bc.equalsIgnoreCase(TagInfo.BODY_CONTENT_EMPTY)) {
		if (reader.matches(CLOSE_1))
		    reader.advance(CLOSE_1.length());
		else
		    throw new ParseException(start, "Body is supposed to be empty for "+tag);

		listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		
		listener.handleTagBegin(start, reader.mark(), attrs, prefix,
					shortTagName, tli, ti);
		listener.handleTagEnd(start, reader.mark(), prefix, 
				      shortTagName, attrs, tli, ti);
	    } else { 
		// Body can be either
		//     - JSP tags
		//     - tag dependent stuff
		if (reader.matches(CLOSE)) {
		    reader.advance(CLOSE.length());
		    bodyStart = reader.mark();
		    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		    
		    listener.handleTagBegin(start, bodyStart, attrs, prefix, 
					    shortTagName, tli, ti);
                    if (bc.equalsIgnoreCase(TagInfo.BODY_CONTENT_TAG_DEPENDENT) ||
                        bc.equalsIgnoreCase(TagInfo.BODY_CONTENT_JSP)) 
                        {
                            String tagEnd = "</"+tag+">";
                            // Parse until the end of the tag body. 
                            // Then skip the tag end... 
                            if (bc.equalsIgnoreCase(TagInfo.BODY_CONTENT_TAG_DEPENDENT))
                                // accept no core elements for tag dependent,
                                // i.e. literal inclusion of the content
                                parser.parse(tagEnd, new Class[] {});
                            else
                                // it is JSP body content, so accept all core elements
                                parser.parse(tagEnd);
                            reader.advance(tagEnd.length());
			    listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);
                            listener.handleTagEnd(parser.tmplStop, reader.mark(), prefix, 
                                                  shortTagName, attrs, tli, ti);
                        } else
                            throw new ParseException(start, 
                                                     "Internal Error: Invalid BODY_CONTENT type");
		} else 
		    throw new ParseException(start, 
					     "Unterminated user-defined tag");
	    }
            return true;
        }
    }

    static {
        coreElements.addElement(new Tag());
    }
    
    

    /*
     * Plugin
     */
    static final class Plugin implements CoreElement {
	private static final String OPEN_PLUGIN  = "<jsp:plugin";
	private static final String END_OPEN_PLUGIN  = ">";
	private static final String CLOSE_PLUGIN = "</jsp:plugin>";
	private static final String OPEN_PARAMS = "<jsp:params>";
	private static final String CLOSE_PARAMS = "</jsp:params>";
	private static final String OPEN_INDIVIDUAL_PARAM = "<jsp:param";
	private static final String CLOSE_INDIVIDUAL_PARAM = "/>";
	private static final String OPEN_FALLBACK = "<jsp:fallback>";
	private static final String CLOSE_FALLBACK = "</jsp:fallback>";

	private static final JspUtil.ValidAttribute[] validAttributes = {
	   new JspUtil.ValidAttribute ("type",true),
	   new JspUtil.ValidAttribute("code", true),
	   new JspUtil.ValidAttribute("codebase"),
	   new JspUtil.ValidAttribute("align"),
	   new JspUtil.ValidAttribute("archive"),
	   new JspUtil.ValidAttribute("height"),
	   new JspUtil.ValidAttribute("hspace"),
	   new JspUtil.ValidAttribute("jreversion"),
	   new JspUtil.ValidAttribute("name"),
	   new JspUtil.ValidAttribute("vspace"),
	   new JspUtil.ValidAttribute("width"),
	   new JspUtil.ValidAttribute("nspluginurl"),
	   new JspUtil.ValidAttribute("iepluginurl")
	};

	public boolean accept(ParseEventListener listener, JspReader reader, 
				Parser parser) throws JasperException 
	{
	    if (reader.matches(OPEN_PLUGIN)) {
		Mark start = reader.mark();
		reader.advance(OPEN_PLUGIN.length());
		Hashtable attrs = reader.parseTagAttributes ();
		reader.skipSpaces ();

	    if (!reader.matches(END_OPEN_PLUGIN))
	        throw new ParseException (reader.mark(),
	                   Constants.getString("jsp.error.plugin.notclosed"));
	    
	    reader.advance (END_OPEN_PLUGIN.length ());
	    reader.skipSpaces ();

		Hashtable param = null;
		String fallback = null;

	        JspUtil.checkAttributes ("plugin", attrs, validAttributes);
		if (reader.matches (OPEN_PARAMS)) {
		    param = new Hashtable ();
		    boolean paramsClosed = false;
		    reader.advance (OPEN_PARAMS.length ());

		    /**
		     * Can have more than one param tag. Hence get all the
		     * params.
		     */

		    while (reader.hasMoreInput ()) {
		        reader.skipSpaces ();
		        if (reader.matches (CLOSE_PARAMS)) {
			    paramsClosed = true;
			    reader.advance (CLOSE_PARAMS.length ());
			    break;
			}
		        if (!reader.matches (OPEN_INDIVIDUAL_PARAM))
		    	    throw new ParseException (reader.mark(),
				Constants.getString("jsp.error.paramexpected"));

			reader.parsePluginParamTag(param);
			reader.skipSpaces ();

		        if (!reader.matches (CLOSE_INDIVIDUAL_PARAM))
		    	    throw new ParseException (reader.mark(),
				Constants.getString(
					"jsp.error.closeindividualparam"));
			reader.advance (CLOSE_INDIVIDUAL_PARAM.length ());
		    }
		    if (!paramsClosed)
		    	    throw new ParseException (reader.mark(),
				Constants.getString("jsp.error.closeparams"));
		    reader.skipSpaces ();
		}
		
		if (reader.matches (OPEN_FALLBACK)) {
		    reader.advance(OPEN_FALLBACK.length ());
		    reader.skipSpaces ();
		    Mark fallBackStart = reader.mark ();
		    Mark fallBackStop = reader.skipUntil (CLOSE_FALLBACK);
		    fallback = new String (reader.getChars(fallBackStart,
		    					         fallBackStop));
		    reader.skipSpaces ();
		}

		if (!reader.matches(CLOSE_PLUGIN)) 
		    throw new ParseException(reader.mark(), 
                                          Constants.getString(
					  "jsp.error.unterminated", 
                                           new Object[] { OPEN_PLUGIN }));

		reader.advance(CLOSE_PLUGIN.length());
		Mark stop = reader.mark();
		listener.setTemplateInfo(parser.tmplStart, parser.tmplStop);		
		listener.handlePlugin(start, stop, attrs, param, fallback);
		return true;
	    } else
		return false;
	}
    }

    static {
	coreElements.addElement(new Plugin());
    }

    /*
     * Quoting in template text.
     * Entities &apos; and &quote;
     */
    static final class QuoteEscape implements CoreElement {
        /**
         * constants for escapes
         */
        private static String QUOTED_START_TAG = "<\\%";
        private static String QUOTED_END_TAG = "%\\>";
        private static String START_TAG = "<%";
        private static String END_TAG = "%>";

	private static final String APOS = "&apos;";
	private static final String QUOTE = "&quote;";
        
	public boolean accept(ParseEventListener listener, JspReader reader, Parser parser) 
            throws JasperException 
	{
            try {
		Mark start = reader.mark();
                if (reader.matches(QUOTED_START_TAG)) {
                    reader.advance(QUOTED_START_TAG.length());
		    Mark end = reader.mark();
                    parser.caw.write(START_TAG);
                    parser.flushCharData(start, end);
                    return true;
                } else if (reader.matches(APOS)) {
                    reader.advance(APOS.length());
		    Mark end = reader.mark();
                    parser.caw.write("\'");
                    parser.flushCharData(start, end);
                    return true;
                }
                else if (reader.matches(QUOTE)) {
                    reader.advance(QUOTE.length());
		    Mark end = reader.mark();
                    parser.caw.write("\"");
                    parser.flushCharData(start, end);
                    return true;
                }
            } catch (java.io.IOException ex) {
                System.out.println (ex.getMessage());
            }
            return false;
	}
    }
    
    static {
	coreElements.addElement(new QuoteEscape());
    }

    void flushCharData(Mark start, Mark stop) throws JasperException {
        char[] array = caw.toCharArray();
        if (array.length != 0) // Avoid unnecessary out.write("") statements...
            listener.handleCharData(start, stop, caw.toCharArray());
        caw = new CharArrayWriter();
    }

    public void parse() throws JasperException {
        parse(null);
    }

    public void parse(String until) throws JasperException {
        parse(until, null);
    }
    
    public void parse(String until, Class[] accept) throws JasperException {

	boolean noJspElement = false;
	while (reader.hasMoreInput()) {
            if (until != null && reader.matches(until)) 
                return;

	    // If the file has changed because of a 'push' or a 'pop'
	    // we must flush the character data for the old file.
	    if (!reader.mark().getFile().equals(currentFile)) {
		flushCharData(tmplStart, tmplStop);
		currentFile = reader.mark().getFile();
		tmplStart = reader.mark();
	    }
	    
	    Enumeration e = coreElements.elements(); 

            if (accept != null) {
                Vector v = new Vector();
                while (e.hasMoreElements()) {
                    CoreElement c = (CoreElement) e.nextElement();
                    for(int i = 0; i < accept.length; i++)
                        if (c.getClass().equals(accept[i]))
                            v.addElement(c);
                }
                e = v.elements();
            }

	    boolean accepted = false;
	    while (e.hasMoreElements()) {
		CoreElement c = (CoreElement) e.nextElement();
		Mark m = reader.mark();
		if (c.accept(listener, reader, this)) {
                    Constants.message("jsp.message.accepted",
                                      new Object[] { c.getClass().getName(), m },
                                      Logger.DEBUG);
		    accepted = true;
		    noJspElement = false;
		    break;
		} 
	    }
	    if (!accepted) {

		// This is a hack. "reader.nextContent()" will just return 
		// after it sees "<" -- not necessarily a JSP element. Using
		// a boolean we will ensure that tmplStart changes only when
		// strictly necessary.
		if (noJspElement == false) {
		    tmplStart = reader.mark();
		    noJspElement = true;
		}
		String s = reader.nextContent();
		tmplStop = reader.mark();
		caw.write(s, 0, s.length());
	    }
	}
	flushCharData(tmplStart, tmplStop);
    }
}
