";charset=ISO-8859-1\");");

/*
 *
 * ====================================================================
 *
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

import java.util.Hashtable;
import java.util.Stack;
import java.util.Vector;
import java.util.Enumeration;
import java.util.StringTokenizer;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.io.File;
import java.io.ObjectOutputStream;
import java.io.FileOutputStream;
import java.net.URL;
import java.net.MalformedURLException;

import javax.servlet.jsp.tagext.TagInfo;
import javax.servlet.jsp.tagext.TagLibraryInfo;

import org.apache.jasper.JasperException;
import org.apache.jasper.Constants;
import org.apache.jasper.JspCompilationContext;

import org.apache.tomcat.util.log.*;

/**
 * JSP code generator "backend".
 *
 * @author Anil K. Vijendran
 */
public class JspParseEventListener extends BaseJspListener {

    private static CommentGenerator commentGenerator = new JakartaCommentGenerator();

    JspCompilationContext ctxt;

    String jspServletBase = Constants.JSP_SERVLET_BASE;
    String serviceMethodName = Constants.SERVICE_METHOD_NAME;
    String servletContentType = Constants.SERVLET_CONTENT_TYPE;

    String extendsClass = "";
    Vector interfaces = new Vector();
    Vector imports = new Vector();

    String error = "";

    boolean genSessionVariable = true;
    boolean singleThreaded = false;
    boolean autoFlush = true;

    Vector generators = new Vector();

    BeanRepository beanInfo;

    int bufferSize = Constants.DEFAULT_BUFFER_SIZE;

    // a set of boolean variables to check if there are multiple attr-val
    // pairs for jsp directive.
    boolean languageDir = false, extendsDir = false, sessionDir = false;
    boolean bufferDir = false, threadsafeDir = false, errorpageDir = false;
    boolean iserrorpageDir = false, infoDir = false, autoFlushDir = false;
    boolean contentTypeDir = false;


    /* support for large files */
    int stringId = 0;
    Vector vector = new Vector();
    String dataFile;

    TagLibraries libraries;

    // Variables shared by all TagBeginGenerator and TagEndGenerator instances
    // to keep track of nested tags and variable names
    private Stack tagHandlerStack;
    private Hashtable tagVarNumbers;

    // This variable keeps track of tag pools.  We only need
    // one tag pool per tag reuse scope.
    private Vector tagPools = new Vector();

    final void addGenerator(Generator gen) throws JasperException {
        gen.init(ctxt);
        generators.addElement(gen);
    }

    public static void setCommentGenerator(CommentGenerator generator) {
	if ( null == commentGenerator) {
	    throw new IllegalArgumentException("null == generator");
	}

	commentGenerator = generator;
    }

    /*
     * Package private since I want everyone to come in through
     * org.apache.jasper.compiler.Main.
     */
    JspParseEventListener(JspCompilationContext ctxt) {
	super(ctxt.getReader(), ctxt.getWriter());
        this.ctxt = ctxt;
	this.beanInfo = new BeanRepository(ctxt.getClassLoader());
        this.libraries = new TagLibraries(ctxt.getClassLoader());

        // FIXME: Is this good enough? (I'm just taking the easy way out - akv)
        if (ctxt.getOptions().getLargeFile())
            dataFile = ctxt.getOutputDir() + File.separatorChar +
                ctxt.getServletPackageName() + "_" +
                ctxt.getServletClassName() + ".dat";
    }

    public void beginPageProcessing() throws JasperException {
	for(int i = 0; i < Constants.STANDARD_IMPORTS.length; i++)
	    imports.addElement(Constants.STANDARD_IMPORTS[i]);
    }

    public void endPageProcessing() throws JasperException {
	generateHeader();
	writer.println();
	generateAll(ServiceMethodPhase.class);
	writer.println();
	generateFooter();
        if (ctxt.getOptions().getLargeFile())
            try {
                ObjectOutputStream o
                    = new ObjectOutputStream(new FileOutputStream(dataFile));

                /*
                 * Serialize an array of char[]'s instead of an
                 * array of String's because there is a limitation
                 * on the size of Strings that can be serialized.
                 */

                char[][] tempCharArray = new char[vector.size()][];
                vector.copyInto(tempCharArray);
                o.writeObject(tempCharArray);
                o.close();
                writer.close();
            } catch (IOException ex) {
                throw new JasperException(Constants.getString(
                                                              "jsp.error.data.file.write"), ex);
            }
        ctxt.setContentType(servletContentType);
    }

    private Stack getTagHandlerStack() {
        if (tagHandlerStack == null) {
            tagHandlerStack = new Stack();
        }
        return tagHandlerStack;
    }

    private Hashtable getTagVarNumbers() {
        if (tagVarNumbers == null) {
            tagVarNumbers = new Hashtable();
        }
        return tagVarNumbers;
    }

    private void generateAll(Class phase) throws JasperException {

	for(int i = 0; i < generators.size(); i++) {
            Generator gen = (Generator) generators.elementAt(i);
            if (phase.isInstance(gen)) {
                gen.generate(writer, phase);
            }
	}

    }

    private void generateHeader() throws JasperException {
        String servletPackageName = ctxt.getServletPackageName();
        String servletClassName = ctxt.getServletClassName();
	// First the package name:
	if (! "".equals(servletPackageName) && servletPackageName != null) {
	    writer.println("package "+servletPackageName+";");
	    writer.println();
	}

	Enumeration e = imports.elements();
	while (e.hasMoreElements())
	    writer.println("import "+(String) e.nextElement()+";");

	writer.println();
	generateAll(FileDeclarationPhase.class);
	writer.println();

	writer.print("public class "+servletClassName+ " extends ");
	writer.print(extendsClass.equals("") ? jspServletBase : extendsClass);

	if (singleThreaded)
	    interfaces.addElement("SingleThreadModel");

	if (interfaces.size() != 0) {
	    writer.println();
	    writer.println("     implements ");

	    for(int i = 0; i < interfaces.size() - 1; i++)
		writer.println(" "+interfaces.elementAt(i)+",");
	    writer.println(" "+interfaces.elementAt(interfaces.size()-1));
	}

	writer.println(" {");

	writer.pushIndent();
	writer.println();
	generateAll(ClassDeclarationPhase.class);
	writer.println();

	writer.println("static {");
	writer.pushIndent();
	generateAll(StaticInitializerPhase.class);
	writer.popIndent();
	writer.println("}");

        writer.println("public "+servletClassName+"( ) {");
        writer.println("}");
        writer.println();

        writer.println("private boolean _jspx_inited = false;");
        writer.println();

        writer.println("public final synchronized void _jspx_init() throws org.apache.jasper.JasperException {");
        writer.pushIndent();
        writer.println("if (! _jspx_inited) {");
        writer.pushIndent();
	generateAll(InitMethodPhase.class);
        writer.println("_jspx_inited = true;");
        writer.popIndent();
        writer.println("}");
        writer.popIndent();
        writer.println("}");
        writer.println();


	writer.println("public void "+serviceMethodName+"("+
		       "HttpServletRequest request, "+
		       "HttpServletResponse  response)");

	writer.println("    throws java.io.IOException, ServletException {");
	writer.pushIndent();
	writer.println();
        writer.println("JspFactory _jspxFactory = null;");
        writer.println("PageContext pageContext = null;");

	if (genSessionVariable)
	    writer.println("HttpSession session = null;");

	if (ctxt.isErrorPage())
            writer.println("Throwable exception = (Throwable) request.getAttribute(\"javax.servlet.jsp.jspException\");");


	writer.println("ServletContext application = null;");
	writer.println("ServletConfig config = null;");
	writer.println("JspWriter out = null;");
        writer.println("Object page = this;");
	writer.println("String  _value = null;");
	writer.println("try {");
	writer.pushIndent();
        writer.println("try {");
        writer.pushIndent();

	writer.println();
        writer.println("_jspx_init();");

	writer.println("_jspxFactory = JspFactory.getDefaultFactory();");
	if (this.contentTypeDir == true)
	    writer.println("response.setContentType(" +
			   writer.quoteString(servletContentType)
			   + ");");
	else
	    writer.println("response.setContentType(\"" +
			   servletContentType +
			   ";charset=8859_1\");");
	writer.println("pageContext = _jspxFactory.getPageContext(this, request, response,\n"
					+ "\t\t\t"
					+ writer.quoteString(error) + ", "
					+ genSessionVariable + ", "
					+ bufferSize + ", "
					+ autoFlush
					+ ");");
	writer.println();

	writer.println("application = pageContext.getServletContext();");
	writer.println("config = pageContext.getServletConfig();");

	if (genSessionVariable)
	    writer.println("session = pageContext.getSession();");

        writer.println("out = pageContext.getOut();");
    }

    private void generateFooter() throws JasperException {
	writer.popIndent();
	//writer.println("} catch (Throwable t) {");
	writer.println("} catch (Exception ex) {");
	writer.pushIndent();
        writer.println("if (out != null && out.getBufferSize() != 0)");
        writer.pushIndent();
	writer.println("out.clearBuffer();");
	writer.popIndent();
	writer.println("if (pageContext != null) pageContext.handlePageException(ex);");
	writer.popIndent();
        writer.println("} catch (Error error) {");
        writer.pushIndent();
        writer.println("throw error;");
        writer.popIndent();
        writer.println("} catch (Throwable throwable) {");
        writer.pushIndent();
        writer.println("throw new ServletException(throwable);");
        writer.popIndent();
        writer.println("}");
        writer.popIndent();
	writer.println("} finally {");
	writer.pushIndent();
	/* Do stuff here for finally actions... */
        //writer.println("out.close();");

	// Use flush buffer ( which just empty JspWriterImpl buffer )
	// instead of commiting the response.
	writer.println("if (out instanceof "
		       + Constants.JSP_RUNTIME_PACKAGE +
		       ".JspWriterImpl) { ");
        writer.println("    ((" +
		       Constants.JSP_RUNTIME_PACKAGE +
		       ".JspWriterImpl)out).flushBuffer();");
	writer.println("}");
	writer.println("if (_jspxFactory != null) _jspxFactory.releasePageContext(pageContext);");
	writer.popIndent();
	writer.println("}");
	// Close the service method:
	writer.popIndent();
	writer.println("}");

	// Close the class definition:
	writer.popIndent();
	writer.println("}");
    }


    public void handleComment(Mark start, Mark stop) throws JasperException {
        Constants.message("jsp.message.htmlcomment",
                          new Object[] { reader.getChars(start, stop) },
                          Log.DEBUG);
    }

    interface PageDirectiveHandler {
        void handlePageDirectiveAttribute(JspParseEventListener listener,
                                          String value,
                                          Mark start, Mark stop)
            throws JasperException;
    }

    static final class PageDirectiveHandlerInfo {
        String attribute;
        PageDirectiveHandler handler;
        PageDirectiveHandlerInfo(String attribute, PageDirectiveHandler handler) {
            this.attribute = attribute;
            this.handler = handler;
        }
    }

    static final String languageStr = "language";
    static final String extendsStr = "extends";
    static final String importStr = "import";
    static final String sessionStr = "session";
    static final String bufferStr = "buffer";
    static final String autoFlushStr = "autoFlush";
    static final String isThreadSafeStr = "isThreadSafe";
    static final String infoStr = "info";
    static final String errorPageStr = "errorPage";
    static final String isErrorPageStr = "isErrorPage";
    static final String contentTypeStr = "contentType";


    PageDirectiveHandlerInfo[] pdhis = new PageDirectiveHandlerInfo[] {
        new PageDirectiveHandlerInfo(languageStr, new LanguageHandler()),
        new PageDirectiveHandlerInfo(extendsStr, new ExtendsHandler()),
        new PageDirectiveHandlerInfo(importStr, new ImportsHandler()),
        new PageDirectiveHandlerInfo(sessionStr, new SessionHandler()),
        new PageDirectiveHandlerInfo(bufferStr, new BufferHandler()),
        new PageDirectiveHandlerInfo(autoFlushStr, new AutoFlushHandler()),
        new PageDirectiveHandlerInfo(isThreadSafeStr, new IsThreadSafeHandler()),
        new PageDirectiveHandlerInfo(infoStr, new InfoHandler()),
        new PageDirectiveHandlerInfo(isErrorPageStr, new IsErrorPageHandler()),
        new PageDirectiveHandlerInfo(contentTypeStr, new ContentTypeHandler()),
        new PageDirectiveHandlerInfo(errorPageStr, new ErrorPageHandler())
    };

    // FIXME: Need to further refine these abstractions by moving the code
    // to handle duplicate directive instance checks to outside.

    static final class ContentTypeHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String contentType,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.contentTypeDir == true)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.multiple.contenttypes"));
            listener.contentTypeDir = true;
            if (contentType == null)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.invalid.contenttype"));
            listener.servletContentType = contentType;
        }
    }

    static final class SessionHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String session,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.sessionDir == true)
                throw new CompileException (start,
					    Constants.getString("jsp.error.page.multiple.session"));
            listener.sessionDir = true;
            if (session == null)
                throw new CompileException (start,
					    Constants.getString("jsp.error.page.invalid.session"));
            if (session.equalsIgnoreCase("true"))
                listener.genSessionVariable = true;
            else if (session.equalsIgnoreCase("false"))
                listener.genSessionVariable = false;
            else
                throw new CompileException(start, "Invalid value for session");
        }
    }

    static final class BufferHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String buffer,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.bufferDir == true)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.multiple.buffer"));
            listener.bufferDir = true;
            if (buffer != null) {
                if (buffer.equalsIgnoreCase("none"))
                    listener.bufferSize = 0;
                else {
                    Integer i = null;
                    try {
                        int ind = buffer.indexOf("k");
                        String num;
                        if (ind == -1)
                            num = buffer;
                        else
                            num = buffer.substring(0, ind);
                        i = new Integer(num);
                    } catch (NumberFormatException n) {
                        throw new CompileException(start, Constants.getString(
					"jsp.error.page.invalid.buffer"));
                    }
                    listener.bufferSize = i.intValue()*1024;
                }
            }
            else
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.invalid.buffer"));
        }
    }

    static final class AutoFlushHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String autoflush,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.autoFlushDir == true)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.multiple.autoflush"));

            listener.autoFlushDir = true;
            if (autoflush == null)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.invalid.autoflush"));

            if (autoflush.equalsIgnoreCase("true"))
                listener.autoFlush = true;
            else if (autoflush.equalsIgnoreCase("false"))
                listener.autoFlush = false;
            else
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.invalid.autoflush"));
        }
    }

    static final class IsThreadSafeHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String threadsafe,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.threadsafeDir == true)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.multiple.threadsafe"));

            listener.threadsafeDir = true;
            if (threadsafe == null)
                throw new CompileException (start,
					    Constants.getString("jsp.error.page.invalid.threadsafe"));

            if (threadsafe.equalsIgnoreCase("true"))
                listener.singleThreaded = false;
            else if (threadsafe.equalsIgnoreCase("false"))
                listener.singleThreaded = true;
            else
                throw new CompileException (start,
					    Constants.getString("jsp.error.page.invalid.threadsafe"));
        }
    }

    static final class InfoHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String info,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.infoDir == true)
                throw new CompileException (start,
					    Constants.getString("jsp.error.page.multiple.info"));

            listener.infoDir = true;
            if (info == null)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.invalid.info"));

            GeneratorWrapper gen = listener. new GeneratorWrapper(new InfoGenerator(info),
                                                                  start, stop);
            listener.addGenerator(gen);
        }
    }

    static final class IsErrorPageHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String iserrorpage,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.iserrorpageDir == true)
                throw new CompileException (start,
					    Constants.getString("jsp.error.page.multiple.iserrorpage"));

            listener.iserrorpageDir = true;
            if (iserrorpage == null)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.invalid.iserrorpage"));

            if (iserrorpage.equalsIgnoreCase("true"))
                listener.ctxt.setErrorPage(true);
            else if (iserrorpage.equalsIgnoreCase("false"))
                listener.ctxt.setErrorPage(false);
            else
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.invalid.iserrorpage"));
        }
    }

    static final class ErrorPageHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String errorpage,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.errorpageDir == true)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.multiple.errorpage"));

            listener.errorpageDir = true;
            if (errorpage != null)
                listener.error = errorpage;
        }
    }

    static final class LanguageHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String language,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.languageDir == true)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.multiple.language"));

            listener.languageDir = true;
            if (language != null)
                if (!language.equalsIgnoreCase("java"))
                    throw new CompileException(start,
					       Constants.getString("jsp.error.page.nomapping.language")+language);
        }
    }

    static final class ImportsHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String importPkgs,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (importPkgs != null) {
                StringTokenizer tokenizer = new StringTokenizer(importPkgs, ",");
                while (tokenizer.hasMoreTokens())
                    listener.imports.addElement(tokenizer.nextToken());
            }
        }
    }

    static final class ExtendsHandler implements PageDirectiveHandler {
        public void handlePageDirectiveAttribute(JspParseEventListener listener,
                                                 String extendsClzz,
                                                 Mark start, Mark stop)
            throws JasperException
        {
            if (listener.extendsDir == true)
                throw new CompileException(start,
					   Constants.getString("jsp.error.page.multiple.extends"));

            listener.extendsDir = true;
            if (extendsClzz != null)  {
                listener.extendsClass = extendsClzz;

		/*
		 * If page superclass is top level class (i.e. not in a pkg)
		 * explicitly import it. If this is not done, the compiler
		 * will assume the extended class is in the same pkg as
		 * the generated servlet.
		 */
		if (extendsClzz.indexOf(".") == -1)  {
                    listener.imports.addElement(extendsClzz);
		}
            }
        }
    }

    public void handleDirective(String directive, Mark start,
				Mark stop, Hashtable attrs)
	throws JasperException
    {
        Constants.message("jsp.message.handling_directive",
                          new Object[] { directive, attrs },
                          Log.DEBUG);

	if (directive.equals("page")) {
	    Enumeration e = attrs.keys();
	    String attr;
	    while (e.hasMoreElements()) {
		attr = (String) e.nextElement();
                for(int i = 0; i < pdhis.length; i++) {
                    PageDirectiveHandlerInfo pdhi = pdhis[i];
                    if (attr.equals(pdhi.attribute)) {
                        String value = (String) attrs.get(pdhi.attribute);
                        pdhi.handler.handlePageDirectiveAttribute(this, value,
                                                                  start, stop);
                    }
                }
            }
        }

        // Do some validations...
        if (bufferSize == 0 && autoFlush == false)
            throw new CompileException(start, Constants.getString(
	    				"jsp.error.page.bad_b_and_a_combo"));

	if (directive.equals("taglib")) {
            String uri = (String) attrs.get("uri");
            String prefix = (String) attrs.get("prefix");
            try {
                TagLibraryInfo tl = new TagLibraryInfoImpl(ctxt,
                                                               prefix,
                                                               uri);
                libraries.addTagLibrary(prefix, tl);
            } catch (Exception ex) {
                Object[] args = new Object[] { uri, ex.getMessage() };
                throw new CompileException(start, Constants.getString("jsp.error.badtaglib",
                                                              args));
            }
	}

	if (directive.equals("include")) {
	    String file = (String) attrs.get("file");
	    if (file == null)
		throw new CompileException(start,
					   Constants.getString("jsp.error.include.missing.file"));

            // jsp.error.include.bad.file needs taking care of here??
            try {
                reader.pushFile(file);
            } catch (FileNotFoundException fnfe) {
                throw new CompileException(start,
					   Constants.getString("jsp.error.include.bad.file"));
            }
	}
    }


    class GeneratorWrapper
        implements Generator, ClassDeclarationPhase,
                   FileDeclarationPhase, ServiceMethodPhase,
                   InitMethodPhase, StaticInitializerPhase
    {
        Generator generator;
        Mark start, stop;

        GeneratorWrapper(Generator generator, Mark start, Mark stop) {
            this.generator = generator;
            this.start = start;
            this.stop = stop;
        }

        /*
         * This is really a no-op.
         */
        public boolean generateCoordinates(Class phase) {
            return generator.generateCoordinates(phase);
        }

        public void init(JspCompilationContext ctxt)
            throws JasperException
        {
            generator.init(ctxt);
        }

        public void generate(ServletWriter out, Class phase)
				throws JasperException
	{
            if (phase.isInstance(generator)) {
                boolean genCoords = generator.generateCoordinates(phase);
                if (genCoords) {
		    commentGenerator.generateStartComment
			(generator, out, start, stop);
                }
                generator.generate(out, phase);
                if (genCoords) {
		    commentGenerator.generateEndComment
			(generator, out, start, stop);
                }
            }
        }
    }

    public void handleDeclaration(Mark start, Mark stop, Hashtable attrs)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new DeclarationGenerator(reader.getChars(
	    			   start, stop)), start, stop);
	addGenerator(gen);
    }

    public void handleScriptlet(Mark start, Mark stop, Hashtable attrs)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new ScriptletGenerator(reader.getChars(
	    			   start, stop)), start, stop);
	addGenerator(gen);
    }

    public void handleExpression(Mark start, Mark stop, Hashtable attrs)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new ExpressionGenerator(reader.getChars(
	    			   start, stop)), start, stop);
	addGenerator(gen);
    }

    public void handleBean(Mark start, Mark stop, Hashtable attrs)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new BeanGenerator(start, attrs, beanInfo,
                                                     genSessionVariable),
                                   start, stop);

	addGenerator(gen);
    }

    public void handleBeanEnd(Mark start, Mark stop, Hashtable attrs)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new BeanEndGenerator(),
                                   start, stop);
	// End the block started by useBean body.
	addGenerator(gen);
    }

    public void handleGetProperty(Mark start, Mark stop, Hashtable attrs)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new GetPropertyGenerator(start, stop, attrs,
	    			   beanInfo), start, stop);

	addGenerator(gen);
    }

    public void handleSetProperty(Mark start, Mark stop, Hashtable attrs)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new SetPropertyGenerator(start, stop, attrs,
	    			   beanInfo), start, stop);

	addGenerator(gen);
    }

    public void handlePlugin(Mark start, Mark stop, Hashtable attrs,
    				Hashtable param, String fallback)
	throws JasperException
    {
        Constants.message("jsp.message.handling_plugin",
                          new Object[] { attrs },
                          Log.DEBUG);

	Generator gen = new GeneratorWrapper (new PluginGenerator (start, attrs,
					      param, fallback), start, stop);
	addGenerator (gen);
    }

    public void handleForward(Mark start, Mark stop, Hashtable attrs, Hashtable param)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new ForwardGenerator(start, attrs, param),
                                   start, stop);

	addGenerator(gen);
    }

    public void handleInclude(Mark start, Mark stop, Hashtable attrs, Hashtable param)
	throws JasperException
    {
        Generator gen
            = new GeneratorWrapper(new IncludeGenerator(start, attrs, param),
                                   start, stop);

	addGenerator(gen);
    }


    public void handleCharData(Mark start, Mark stop, char[] chars) throws JasperException {
        GeneratorBase cdg;

        if (ctxt.getOptions().getLargeFile())
            cdg = new StoredCharDataGenerator(vector, dataFile, stringId++, chars);
        else if(ctxt.getOptions().getMappedFile())
            cdg = new MappedCharDataGenerator(chars);
	else
	    cdg = new CharDataGenerator(chars);


        Generator gen
            = new GeneratorWrapper(cdg,
                                   start, stop);

	addGenerator(gen);
    }

    public void handleTagBegin(Mark start, Mark stop, Hashtable attrs, String prefix,
			       String shortTagName, TagLibraryInfo tli,
			       TagInfo ti)
	throws JasperException
    {
        TagBeginGenerator tbg = new TagBeginGenerator(start, prefix, shortTagName, attrs,
	    tli, ti, libraries, getTagHandlerStack(), getTagVarNumbers());
        Generator gen = new GeneratorWrapper(tbg, start, stop);

	addGenerator(gen);

        // If this is the first tag, then generate code to store reference
        // to tag pool manager.
        if (tagPools.size() == 0) {
            addGenerator(new TagPoolManagerGenerator());
        }

        // if we haven't added a tag pool generator for this tag, then add one
        String tagPoolVarName = TagPoolGenerator.getPoolName(tli, ti, attrs);
        if (! tagPools.contains(tagPoolVarName)) {
            tagPools.addElement(tagPoolVarName);
            TagPoolGenerator tpg = new TagPoolGenerator(prefix, shortTagName, attrs, tli, ti);
            gen = new GeneratorWrapper(tpg, start, stop);
            addGenerator(gen);
        }
    }

    public void handleTagEnd(Mark start, Mark stop, String prefix,
			     String shortTagName, Hashtable attrs,
                             TagLibraryInfo tli, TagInfo ti)
	throws JasperException
    {
        TagEndGenerator teg = new TagEndGenerator(prefix, shortTagName, attrs,
	    tli, ti, libraries, getTagHandlerStack(), getTagVarNumbers());
        Generator gen = new GeneratorWrapper(teg, start, stop);

	addGenerator(gen);
    }

    public TagLibraries getTagLibraries() {
	return libraries;
    }
}