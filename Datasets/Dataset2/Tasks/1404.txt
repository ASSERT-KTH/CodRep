Log loghelper = Log.getLog("JASPER_LOG", "JspReader");

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

import java.io.InputStreamReader;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.Reader;
import java.io.CharArrayWriter;
import java.io.IOException;
import java.io.FileNotFoundException;
import java.io.File;
import java.util.Hashtable;
import java.util.Vector;
import java.util.Stack;

import org.apache.jasper.Constants;
import org.apache.jasper.JspCompilationContext;
import org.apache.tomcat.util.log.*;

/**
 * JspReader is an input buffer for the JSP parser. It should allow
 * unlimited lookahead and pushback. It also has a bunch of parsing
 * utility methods for understanding htmlesque thingies.
 *
 * @author Anil K. Vijendran
 * @author Anselm Baird-Smith
 * @author Harish Prabandham
 * @author Rajiv Mordani
 * @author Mandar Raje
 */
public class JspReader {
    protected Mark current  = null;
    String master = null;

    Vector sourceFiles = new Vector();
    int currFileId = 0;
    int size = 0;
    
    private JspCompilationContext context;

    Log loghelper = new Log("JASPER_LOG", "JspReader");
    //    LogHelper loghelper = new LogHelper("JASPER_LOG", "JspReader");
    
    /*
     * Default encoding used. The JspReader is created with the
     * "top file" encoding. This is then the encoding used for the
     * included files (same translation unit).
     */
    private String encoding = null;

    public String getFile(int fileid) {
	return (String) sourceFiles.elementAt(fileid);
    }

    /**
     * Register a new source file.
     * This method is used to implement file inclusion. Each included file
     * gets a uniq identifier (which is the index in the array of source files).
     * @return The index of the now registered file.
     */
    protected int registerSourceFile(String file) {
        if (sourceFiles.contains(file))
            return -1;
	sourceFiles.addElement(file);
	this.size++;
	return sourceFiles.size() - 1;
    }
    

    /**
     * Unregister the source file.
     * This method is used to implement file inclusion. Each included file
     * gets a uniq identifier (which is the index in the array of source files).
     * @return The index of the now registered file.
     */
    protected int unregisterSourceFile(String file) {
        if (!sourceFiles.contains(file))
            return -1;
	sourceFiles.removeElement(file);
	this.size--;
	return sourceFiles.size() - 1;
    }

    /**
     * Push a new file onto the stack.
     * The name of the file is resolved to a fully qualified filename.
     * @param name The name of the file.
     */
    public void pushFile(String name) 
	throws ParseException, FileNotFoundException
    {
	pushFile(name, this.encoding);
    }

    /**
     * Push a new file onto the stack.
     * The name of the file is resolved to a fully qualified filename.
     * @param name The name of the file.
     * @param encoding The optional encoding for the file.
     */
    public void pushFile(String name, String encoding) 
	throws ParseException, FileNotFoundException
    {
        String parent = master == null ?
            null : master.substring(0, master.lastIndexOf("/") + 1);
        boolean isAbsolute = name.startsWith("/");

	if (parent == null || isAbsolute) {
	    master = name;
	    pushFile(new File(name), encoding);
	} else {
	    master = parent + name;
	    pushFile(new File(master), encoding);
	}
    }

    /**
     * Push a new file to be parsed onto the stack.
     * @param inputFile The fully qualified path of the file.
     * @param encoding Optional encoding to read the file.
     */
    private void pushFile(File file, String encoding) 
	throws ParseException, FileNotFoundException 
    {
        // Default encoding if needed:
	if (encoding == null) {
            encoding = this.encoding;
            // XXX - longer term, this should really be:
	    //   System.getProperty("file.encoding", "8859_1");
            // but this doesn't work right now, so we stick with ASCII
        }

	// Register the file, and read its content:
	String longName = (context == null)
	    ? file.getAbsolutePath()
	    : context.getRealPath(file.toString());

	if (longName == null)
	    throw new FileNotFoundException(file.toString());

	int fileid = registerSourceFile(longName);
	
        if (fileid == -1)
            throw new ParseException(Constants.getString("jsp.error.file.already.registered",
                                                         new Object[] { 
                                                             file 
                                                         }));
	currFileId = fileid;
                                     
	InputStreamReader reader = null;
	try {
            if (context == null)
                reader = new InputStreamReader(new FileInputStream(file),
                                               encoding);
            else {
	        String fileName = context.getRealPath(file.toString());
		InputStream in = context.getResourceAsStream(file.toString());
                if (in == null)
                    throw new FileNotFoundException(fileName);
                
                try {
                    reader = new InputStreamReader(in, encoding);
                } catch (Throwable ex) {
                    throw new FileNotFoundException(fileName + ": "+ ex.getMessage());
                }
            }
            
	    CharArrayWriter caw   = new CharArrayWriter();
	    char            buf[] = new char[1024];
	    for (int i = 0 ; (i = reader.read(buf)) != -1 ; )
		caw.write(buf, 0, i);
	    caw.close();
	    if (current == null) {
		current = new Mark( this, caw.toCharArray(), fileid, getFile(fileid),
				    master, encoding );
	    } else {
		current.pushStream( caw.toCharArray(), fileid, getFile(fileid),
				    master, encoding );
	    }

        } catch (FileNotFoundException fnfe) {
            throw fnfe;
	} catch (Throwable ex) {
	    loghelper.log("Exception parsing file " + file, ex);
	    // Pop state being constructed:
	    popFile();
	    throw new ParseException(Constants.getString("jsp.error.file.cannot.read",
							new Object[] { file }));
	} finally {
	    if ( reader != null ) {
		try { reader.close(); } catch (Exception any) {}
	    }
	}
    }

    public boolean popFile() throws ParseException {
	// Is stack created ? (will happen if the Jsp file we'r looking at is
	// missing.
	if (current == null) 
		return false;

	// Restore parser state:
	//size--;
	if (currFileId < 0) {
	    throw new ParseException(
		          Constants.getString("jsp.error.no.more.content"));
	}

	String fName = getFile(currFileId);
	currFileId = unregisterSourceFile(fName);
	if (currFileId < -1)
	    throw new ParseException
		(Constants.getString("jsp.error.file.not.registered",
				     new Object[] {fName}));

	boolean r = current.popStream();
	if (r)
		master = current.baseDir;
	return r;
    }
	
    protected JspReader(String file, JspCompilationContext ctx, String encoding) 
	throws ParseException, FileNotFoundException
    {
        this.context = ctx;
	this.encoding = encoding;
	if (this.encoding == null) this.encoding = "8859_1";
	pushFile(file, encoding);
    }

    public static JspReader createJspReader(String file, JspCompilationContext ctx, String encoding) 
	throws ParseException, FileNotFoundException
    {
	return new JspReader(file, ctx, encoding);
    }

    public boolean hasMoreInput() throws ParseException {
	if (current.cursor >= current.stream.length) {
	    while (popFile()) {
		if (current.cursor < current.stream.length) return true;
	    }
	    return false;
	}
	return true;
    }
    
    public int nextChar() throws ParseException {
	if (!hasMoreInput())
	    return -1;
	
	int ch = current.stream[current.cursor];

	current.cursor++;
	
	if (ch == '\n') {
	    current.line++;
	    current.col = 0;
	} else {
	    current.col++;
	}
	return ch;
    }

    /**
     * Gets Content until the next potential JSP element.  Because all elements
     * begin with a '&lt;' we can just move until we see the next one.
     */
    String nextContent() {
        int cur_cursor = current.cursor;
	int len = current.stream.length;
 	char ch;

	if (peekChar() == '\n') {
	    current.line++;
	    current.col = 0;
	}
	else current.col++;
	
	// pure obsfuscated genius!
        while ((++current.cursor < len) && 
	    ((ch = current.stream[current.cursor]) != '<')) {

	    if (ch == '\n') {
		current.line++;
		current.col = 0;
	    } else {
  		current.col++;
	    }
	}

	return new String(current.stream, cur_cursor, current.cursor-cur_cursor);
    }

    char[] getChars(Mark start, Mark stop) throws ParseException {
	Mark oldstart = mark();
	reset(start);
	CharArrayWriter caw = new CharArrayWriter();
	while (!stop.equals(mark()))
	    caw.write(nextChar());
	caw.close();
	reset(oldstart);
	return caw.toCharArray();
    }

    public int peekChar() {
	return current.stream[current.cursor];
    }

    public Mark mark() {
	return new Mark(current);
    }

    public void reset(Mark mark) {
	current = new Mark(mark);
    }

    public boolean matchesIgnoreCase(String string) throws ParseException {
	Mark mark = mark();
	int ch = 0;
	int i = 0;
	do {
	    ch = nextChar();
	    if (Character.toLowerCase((char) ch) != string.charAt(i++)) {
		reset(mark);
		return false;
	    }
	} while (i < string.length());
	reset(mark);
	return true;
    }

    public boolean matches(String string) throws ParseException {
	Mark mark = mark();
	int ch = 0;
	int i = 0;
	do {
	    ch = nextChar();
	    if (((char) ch) != string.charAt(i++)) {
		reset(mark);
		return false;
	    }
	} while (i < string.length());
	reset(mark);
	return true;
    }
    
    public void advance(int n) throws ParseException {
	while (--n >= 0)
	    nextChar();
    }

    public int skipSpaces() throws ParseException {
	int i = 0;
	while (isSpace()) {
	    i++;
	    nextChar();
	}
	return i;
    }

    /**
     * Skip until the given string is matched in the stream.
     * When returned, the context is positioned past the end of the match.
     * @param s The String to match.
     * @return A non-null <code>Mark</code> instance if found,
     * <strong>null</strong> otherwise.
     */
    public Mark skipUntil(String limit)
    throws ParseException {
	Mark ret = null;
	int limlen = limit.length();
	int ch;
	
    skip:
	for (ret = mark(), ch = nextChar() ; ch != -1 ; ret = mark(), ch = nextChar()) {
	    
	    if ( ch == limit.charAt(0) ) {
		for (int i = 1 ; i < limlen ; i++) {
		    if (Character.toLowerCase((char) nextChar()) != limit.charAt(i))
			continue skip;
		}
		return ret;
	    }
	}
	return null;
    }
    
    final boolean isSpace() {
	return peekChar() <= ' ';
    }

    /**
     * Parse a space delimited token.
     * If quoted the token will consume all characters up to a matching quote,
     * otherwise, it consumes up to the first delimiter character.
     * @param quoted If <strong>true</strong> accept quoted strings.
     */

    public String parseToken(boolean quoted) 
	throws ParseException
    {
	StringBuffer stringBuffer = new StringBuffer();
	skipSpaces();
	stringBuffer.setLength(0);
	
	int ch = peekChar();
	
	if (quoted) {
	    if ( ch == '"' || ch == '\'') {

		char endQuote = ch == '"' ? '"' : '\'';
		// Consume the open quote: 
		ch = nextChar();
		for(ch = nextChar(); ch != -1 && ch != endQuote; ch = nextChar()) {
		    if (ch == '\\') 
			ch = nextChar();
		    stringBuffer.append((char) ch);
		}
		// Check end of quote, skip closing quote:
		if ( ch == -1 ) 
		    throw new ParseException(mark(), 
				Constants.getString("jsp.error.quotes.unterminated"));
	    }
	    else throw new ParseException(mark(),
				Constants.getString("jsp.error.attr.quoted"));
	} else {
	    if (!isDelimiter())
		// Read value until delimiter is found:
		do {
		    ch = nextChar();
		    // Take care of the quoting here.
		    if (ch == '\\') {
			if (peekChar() == '"' || peekChar() == '\'' ||
			       peekChar() == '>' || peekChar() == '%')
			    ch = nextChar();
		    }
		    stringBuffer.append((char) ch);
		} while ( !isDelimiter() );
	}
	return stringBuffer.toString();
    }

    /**
     * Parse an attribute/value pair, and store it in provided hash table.
     * The attribute/value pair is defined by:
     * <pre>
     * av := spaces token spaces '=' spaces token spaces
     * </pre>
     * Where <em>token</em> is defined by <code>parseToken</code> and
     * <em>spaces</em> is defined by <code>skipSpaces</code>.
     * The name is always considered case insensitive, hence stored in its
     * lower case version.
     * @param into The Hashtable instance to save the result to.
     */

    private void parseAttributeValue(Hashtable into)
	throws ParseException
    {
	// Get the attribute name:
	skipSpaces();
	String name = parseToken(false);
	// Check for an equal sign:
	skipSpaces();
	if ( peekChar() != '=' ) 
	    throw new ParseException(mark(), Constants.getString("jsp.error.attr.novalue",
						new Object[] { name }));
	char ch = (char) nextChar();
	// Get the attribute value:
	skipSpaces();
	String value = parseToken(true);
	skipSpaces();
	// Add the binding to the provided hashtable:
	into.put(name, value);
	return;
    }

    /**
     * Parse some tag attributes for Beans.
     * The stream is assumed to be positioned right after the tag name. The
     * syntax recognized is:
     * <pre>
     * tag-attrs := empty | attr-list ("&gt;" | "--&gt;" | %&gt;)
     * attr-list := empty | av spaces attr-list
     * empty     := spaces 
     * </pre>
     * Where <em>av</em> is defined by <code>parseAttributeValue</code>.
     * @return A Hashtable mapping String instances (variable names) into
     * String instances (variable values).
     */

    public Hashtable parseTagAttributesBean() 
	throws ParseException
    {
      Hashtable values = new Hashtable(11);
	while ( true ) {
	    skipSpaces();
	    int ch = peekChar();
	    if ( ch == '>' ) {
		// End of the useBean tag.
		return values;

	    } else if ( ch == '/' ) {
		Mark mark = mark();
		nextChar();
		// XMLesque Close tags 
		try {
		    if ( nextChar() == '>' )
		      return values;
		} finally {
		    reset(mark);
		}
	    }
	    if ( ch == -1 )
		break;
	    // Parse as an attribute=value:
	    parseAttributeValue(values);
	}
	// Reached EOF:
	throw new ParseException(mark(),
			Constants.getString("jsp.error.tag.attr.unterminated"));
    }

    /**
     * Parse some tag attributes.
     * The stream is assumed to be positioned right after the tag name. The
     * syntax recognized is:
     * <pre>
     * tag-attrs := empty | attr-list ("&gt;" | "--&gt;" | %&gt;)
     * attr-list := empty | av spaces attr-list
     * empty     := spaces 
     * </pre>
     * Where <em>av</em> is defined by <code>parseAttributeValue</code>.
     * @return A Hashtable mapping String instances (variable names) into
     * String instances (variable values).
     */

    public Hashtable parseTagAttributes() 
	throws ParseException
    {
	Hashtable values = new Hashtable(11);
	while ( true ) {
	    skipSpaces();
	    int ch = peekChar();
	    if ( ch == '>' ) {
		return values;
	    }
	    if ( ch == '-' ) {
		Mark mark = mark();
		nextChar();
		// Close NCSA like attributes "->"
		try {
		    if ( nextChar() == '-' && nextChar() == '>' )
			return values;
		} finally {
		    reset(mark);
		}
	    } else if ( ch == '%' ) {
		Mark mark = mark();
		nextChar();
		// Close variable like attributes "%>"
		try {
		    if ( nextChar() == '>' )
			return values;
		} finally {
		    reset(mark);
		}
	    } else if ( ch == '/' ) {
		Mark mark = mark();
		nextChar();
		// XMLesque Close tags 
		try {
		    if ( nextChar() == '>' )
			return values;
		} finally {
		    reset(mark);
		}
	    }
	    if ( ch == -1 )
		break;
	    // Parse as an attribute=value:
	    parseAttributeValue(values);
	}
	// Reached EOF:
	throw new ParseException(mark(),
			Constants.getString("jsp.error.tag.attr.unterminated"));
    }

    /**
     * Parse PARAM tag attributes into the given hashtable.
     * Parses the PARAM tag as defined by:
     * <pre>
     * &lt;PARAM tag-attributes %gt;
     * </pre>
     * Two special tag attributes are recognized here:
     * <ol>
     * <li>The <strong>name</strong> attribute,
     * <li>The <strong>value</strong> attribute.
     * </ol>
     * The resulting name, value pair is stored in the provided hash table.
     * @param into Storage for parameter values.
     */
    public void parseParamTag(Hashtable into) 
	throws ParseException
    {
	// Really check for a param tag:
	if ( matches("param") ) {
	    advance(6);
	    parseParams (into);
	} else {
	    // False alarm, just skip it
	}
    }

    /**
     * Parse jsp:param tag attributes into the given hashtable.
     * Parses the jsp:param tag as defined by:
     * <pre>
     * &lt;jsp:param tag-attributes %gt;
     * </pre>
     * Two special tag attributes are recognized here:
     * <ol>
     * <li>The <strong>name</strong> attribute,
     * <li>The <strong>value</strong> attribute.
     * </ol>
     * The resulting name, value pair is stored in the provided hash table.
     * @param into Storage for parameter values.
     */
    public void parsePluginParamTag(Hashtable into) 
	throws ParseException
    {
	// Really check for a param tag:
	if ( matches("<jsp:param") ) {
	    advance(11);
	    parseParams (into);
	} else {
	    // False alarm, just skip it
	}
    }

    private void parseParams (Hashtable into) 
        throws ParseException
    {
	Hashtable attrs = parseTagAttributes();
	// Check attributes (name and value):
	String name  = (String) attrs.get("name");
	String value = (String) attrs.get("value");
	if ( name == null )
 	    throw new ParseException(mark(), Constants.getString("jsp.error.param.noname"));
	if ( value == null )
 	    throw new ParseException(mark(), Constants.getString("jsp.error.param.novalue"));
	// Put that new binding into the params hashatble:
	String oldval[] = (String[]) into.get(name);
	if ( oldval == null ) {
	    String newval[] = new String[1];
	    newval[0] = value;
	    into.put(name, newval);
	} else {
	    String newval[] = new String[oldval.length+1];
	    System.arraycopy(oldval, 0, newval, 0, oldval.length);
	    newval[oldval.length] = value;
	    into.put(name, newval);
        }
    }

    /**
     * Parse utils - Is current character a token delimiter ?
     * Delimiters are currently defined to be =, &gt;, &lt;, ", and ' or any
     * any space character as defined by <code>isSpace</code>.
     * @return A boolean.
     */
    private boolean isDelimiter() throws ParseException {
	if ( ! isSpace() ) {
	    int ch = peekChar();
	    // Look for a single-char work delimiter:
	    if ( ch == '=' || ch == '>' || ch == '"' || ch == '\'' || ch == '/') 
		return true;
	    // Look for an end-of-comment or end-of-tag:		
	    if ( ch == '-' ) {
		Mark mark = mark();
		if ( ((ch = nextChar()) == '>')
		     || ((ch == '-') && (nextChar() == '>')) ) {
		    reset(mark);
		    return true;
		} else {
		    reset(mark);
		    return false;
		}
	    }
	    return false;
	} else {
	    return true;
	}
    }
}
