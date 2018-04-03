("TSVPrinter constructor requires a non-null writer"); //EXCEPTION

package org.tigris.scarab.screens;

/* ================================================================
 * Copyright (c) 2003 CollabNet.  All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * 
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * 
 * 3. The end-user documentation included with the redistribution, if
 * any, must include the following acknowlegement: "This product includes
 * software developed by CollabNet <http://www.collab.net/>."
 * Alternately, this acknowlegement may appear in the software itself, if
 * and wherever such third-party acknowlegements normally appear.
 * 
 * 4. The hosted project names must not be used to endorse or promote
 * products derived from this software without prior written
 * permission. For written permission, please contact info@collab.net.
 * 
 * 5. Products derived from this software may not use the "Tigris" or 
 * "Scarab" names nor may "Tigris" or "Scarab" appear in their names without 
 * prior written permission of CollabNet.
 * 
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL COLLABNET OR ITS CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 * GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
 * IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * ====================================================================
 * 
 * This software consists of voluntary contributions made by many
 * individuals on behalf of CollabNet.
 */ 

import java.io.Writer;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.OutputStreamWriter;
import java.util.List;

import org.apache.commons.lang.StringUtils;

import org.apache.turbine.Turbine;
import org.apache.turbine.RunData;
import org.apache.turbine.TemplateContext;

import org.tigris.scarab.util.ScarabUtil;
import org.tigris.scarab.util.export.ExportFormat;


/**
 * <p>Sends file contents directly to the output stream, setting the
 * <code>Content-Type</code> and writing back to the browser a
 * tab-delimited file (Excel digests this fine).  We used to use <a
 * href="http://jakarta.apache.org/poi/">POI</a> to compose an Excel
 * binary data file, but its outrageous memory consumption didn't
 * scale for large result sets. POI assembles the its output in
 * memory.  After study of the native OLE2 Excel file format, it
 * appears very difficult to generate the file in another fashion.</p>
 *
 * <p>Regards output encoding, for now we're assuming the response
 * stream is appropriately set upon fetching. Also, we're assuming
 * that Excel will do the right thing on receipt of our TSV file with
 * Japanese or other multibyte characters (we're not setting an
 * encoding on the <code>Content-Type</code> we return).  Both of the
 * above to be verified.</p>
 *
 * @author <a href="mailto:jmcnally@collab.net">John McNally</a>
 * @author <a href="mailto:stack@collab.net">St.Ack</a>
 * @author <a href="mailto:dlr@collab.net">Daniel Rall</a>
 * @since Scarab 1.0
 */
class DataExport extends Default
{
    /**
     * What to show if a cell is empty.  The empty string is dealt
     * with best by spreadsheet applications.
     */
    protected static final String NO_CONTENT = "";

    /**
     * Sets the <code>Content-Type</code> header for the response.
     * Since this assumes we're writing the reponse ourself, indicates
     * no target to render by setting it to <code>null</code>.
     */
    public void doBuildTemplate(RunData data, TemplateContext context)
        throws Exception 
    {
        super.doBuildTemplate(data, context);
        String format = ScarabUtil.findValue(data, ExportFormat.KEY_NAME);

        // look for a configuration toggle for the encoding to which to
        // export.  TODO : make this per request configurable (with a per-
        // language default) to allow use of scarab in a multilingual 
        // environment.
        if (ExportFormat.EXCEL_FORMAT.equalsIgnoreCase(format))
        {
            data.getResponse().setContentType("application/vnd.ms-excel");
        }
        else
        {
            // we want to set a charset on the response -- so clients
            // can detect it properly -- if we have a known encoding
            String encoding = getEncodingForExport(data);
            String contentType = "text/plain";
            if (encoding != null && !encoding.equals(""))
            {
                contentType = contentType + "; charset=" + encoding;
            }
            data.getResponse().setContentType(contentType);
        }
        // Since we're streaming the TSV content directly from our
        // data source, we don't know its length ahead of time.
        //data.getResponse().setContentLength(?);
        
        // FIXME: Provide work hooks here...
        //TSVPrinter printer = new TSVPrinter(data.getResponse().getWriter());
        //writeHeading(printer, mitlist, l10n, rmuas);
        //writeRows(printer, mitlist, l10n, scarabR, rmuas);

        // Above we sent the response, so no target to render
        data.setTarget(null);
    }

    /**
     * This function encapsulates the logic of determining which encoding 
     * to use.  Right now, the encoding isn't per-request, but that should
     * be changed.
     */
    protected String getEncodingForExport(RunData data)
    {
        String encoding = Turbine.getConfiguration()
            .getString("scarab.dataexport.encoding");
        return encoding;
    }

    /**
     * This function is available to subclasses -- it is used to provide
     * a Writer based on the current request and the site configuration,
     * taking encoding issues into consideration.
     */
    protected Writer getWriter(RunData data)
        throws IOException
    {
        Writer writer = null;
        String encoding = getEncodingForExport(data);
        if (encoding != null && !encoding.equals(""))
        {
            writer =
                new OutputStreamWriter(data.getResponse().getOutputStream(),
                                       encoding);
        }
        else
        {
            writer = data.getResponse().getWriter();
        }
        return writer;
    }

    /**
     * Escape any commas in passed string.
     *
     * @param s String to check.
     * @return Passed string with commas escaped.
     */
    protected String escapeCommas(String s)
    {
        // Not sure how to escape commas.  What to use instead?  Quote
        // for now.
        return quote(s);
    }

    protected final boolean containsElements(List l)
    {
        return l != null && !l.isEmpty();
    }

    /**
     * Quote the string argument.
     *
     * @param s Text to quote.
     * @return Passed string, quoted.
     */
    private static String quote(String s)
    {
        return '"' + StringUtils.replace(s, "\"", "\"\"") + '"';
    }

    /**
     * Uses a <code>PrintWriter</code> internally to do actual
     * writing.  If content with tabs and newlines in it is
     * double-quoted, Excel does the Right Thing when parsing.
     *
     * @see <a href="http://ostermiller.org/utils/ExcelCSVPrinter.java.html">ExcelCSVPrinter.java</a>
     */
    protected class TSVPrinter
    {
        /**
         * Flag indicating start of a new line.
         */
        private boolean lineStart = true;

        /**
         * Printer write on.
         */
        private PrintWriter printer = null;

        /**
         * Creates a new instance.
         *
         * @param writer Writer to output to.
         * @throws IllegalArgumentException If <code>writer</code> is
         * <code>null</code>.
         */
        public TSVPrinter(Writer writer)
        {
            if (writer == null)
            {
                throw new IllegalArgumentException
                    ("TSVPrinter constructor requires a non-null writer");
            }
            
            if (writer instanceof PrintWriter)
            {
                this.printer = (PrintWriter) writer;
            }
            else
            {
                this.printer = new PrintWriter(writer);
            }
        }

        /**
         * Prints one field at a time.
         */
        public void print(String s)
        {
            if (!lineStart)
            {
                // Print a tab seperator before we print our field content.
                printer.print('\t');
            }
            lineStart = false;

            if (StringUtils.isNotEmpty(s))
            {
                printer.print(escape(s));
            }
        }

        /**
         * Must be called when done writing a line -- this prints a newline
         * and flushes the printer.
         */
        public void println()
        {
            printer.println();  
            printer.flush();
            lineStart = true;
        }

        /**
         * Quote the string argument.
         *
         * @param s Text to quote.
         * @return Passed string, quoted.
         */
        protected String quote(String s)
        {
            return DataExport.quote(s);
        }

        /**
         * If the passed string has any problematic characters, quote the
         * whole thing after escaping any quotes already present. Excel
         * does the right thing parsing if it gets quoted content.
         *
         * @param s String to escape.
         * @return An escaped version of the passed string.
         */
        private String escape(String s)
        {
            if (StringUtils.isNotEmpty(s))
            {
                for (int i = 0; i < s.length(); i++)
                {
                    char c = s.charAt(i);
                    if (c == '"' || c == '\t' || c == '\n' || c == '\r')
                    {
                        s = quote(s);
                        break;
                    }
                }
            }

            return s;
        }
    }
}