this.tempDir = System.getProperty("java.io.tmpdir");

package org.apache.struts.upload;

import java.io.File;
import java.io.IOException;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.UnsupportedEncodingException;
import javax.servlet.ServletException;
import javax.servlet.ServletInputStream;
import javax.servlet.http.HttpServletRequest;

/**
 * The MultipartIterator class is responsible for reading the
 * input data of a multipart request and splitting it up into
 * input elements, wrapped inside of a
 * {@link org.apache.struts.upload.MultipartElement MultipartElement}
 * for easy definition.  To use this class, create a new instance
 * of MultipartIterator passing it a HttpServletRequest in the
 * constructor.  Then use the {@link #getNextElement() getNextElement}
 * method until it returns null, then you're finished.  Example: <br>
 * <pre>
 *      MultipartIterator iterator = new MultipartIterator(request);
 *      MultipartElement element;
 * 
 *      while ((element = iterator.getNextElement()) != null) {
 *           //do something with element
 *      }
 * </pre>
 *
 * @see org.apache.struts.upload.MultipartElement
 * @author Mike Schachter
 */
public class MultipartIterator {
    
    /**
     * The maximum size in bytes of the buffer used to read lines [4K]
     */
    public static int MAX_LINE_SIZE = 4096;
    
    /**
     * The request instance for this class
     */
    protected HttpServletRequest request;
    
    /**
     * The input stream instance for this class
     */
    protected BufferedMultipartInputStream inputStream;
    
    /**
     * The boundary for this multipart request
     */
    protected String boundary;
    
    /**
     * The byte array representing the boundary for this multipart request
     */
    protected byte[] boundaryBytes;
    
    /**
     * Whether or not the input stream is finished
     */
    protected boolean contentRead = false;
    
    /**
     * The maximum file size in bytes allowed. Ignored if -1
     */
    protected long maxSize = -1;
    
    /**
     * The total bytes read from this request
     */
    protected long totalLength = 0;
    
    /**
     * The content length of this request
     */
    protected int contentLength;
    
    /**
     * The size in bytes written to the filesystem at a time [20K]
     */
    protected int diskBufferSize = 2 * 10240;
    
    /**
     * The amount of data read from a request at a time.
     * This also represents the maximum size in bytes of
     * a line read from the request [4KB]
     */
    protected int bufferSize = 4096;
    
    /**
     * The temporary directory to store files
     */
    protected String tempDir;

    /**
     * Constructs a MultipartIterator with a default buffer size and no file size
     * limit
     * 
     * @param request The multipart request to iterate
     */
    public MultipartIterator(HttpServletRequest request) throws ServletException{
        this(request, -1);
    }
    
    /**
     * Constructs a MultipartIterator with the specified buffer size and
     * no file size limit
     *
     * @param request The multipart request to iterate
     * @param bufferSize The size in bytes that should be read from the input
     *                   stream at a times
     */
    public MultipartIterator(HttpServletRequest request, int bufferSize) throws ServletException {        
       this (request, bufferSize, -1);
    }
    
    /**
     * Constructs a MultipartIterator with the specified buffer size and
     * the specified file size limit in bytes
     *
     * @param request The multipart request to iterate
     * @param bufferSize The size in bytes that should be read from the input
     *                   stream at a times
     * @param maxSize The maximum size in bytes allowed for a multipart element's data
     */
    public MultipartIterator(HttpServletRequest request, int bufferSize, long maxSize) 
                                                                 throws ServletException {
                         
        this(request, bufferSize, maxSize, null);                                                                 
        
    }
    
    public MultipartIterator(HttpServletRequest request,
                             int bufferSize,
                             long maxSize,
                             String tempDir) throws ServletException {
                                 
        this.request = request;
        this.maxSize = maxSize;
        if (bufferSize > -1) {
            this.bufferSize = bufferSize;
        }
        if (tempDir != null) {
            this.tempDir = tempDir;
        }
        else {
            //default to system-wide tempdir
            tempDir = System.getProperty("java.io.tmpdir");
        }
        parseRequest();
    }
    
    /**
     * Retrieves the next element in the iterator if one exists.
     *
     * @throws a ServletException if the post size exceeds the maximum file size
     *         passed in the 3 argument constructor
     * @throws an UnsupportedEncodingException if the "ISO-8859-1" encoding isn't found
     * @return a {@link org.apache.struts.upload.MultipartElement MultipartElement}
     *         representing the next element in the request data
     *
     */
    public MultipartElement getNextElement() throws ServletException, UnsupportedEncodingException {
        //retrieve the "Content-Disposition" header
        //and parse
        String disposition = readLine();
        
        
        if ((disposition != null) && (disposition.startsWith("Content-Disposition"))) {
            String name = parseDispositionName(disposition);
            String filename = parseDispositionFilename(disposition);
                                   
            String contentType = null;
            boolean isFile = (filename != null);
            
            if (isFile) {
                filename = new File(filename).getName();
                
                //check for windows filenames,
                //from linux jdk's the entire filepath
                //isn't parsed correctly from File.getName()
                int colonIndex = filename.indexOf(":");
                if (colonIndex == -1) {
                    //check for Window's SMB server file paths
                    colonIndex = filename.indexOf("\\\\");
                }
                int slashIndex = filename.lastIndexOf("\\");
                
                if ((colonIndex > -1) && (slashIndex > -1)) {
                    //then consider this filename to be a full
                    //windows filepath, and parse it accordingly
                    //to retrieve just the file name
                    filename = filename.substring(slashIndex+1, filename.length());
                }
            
                //get the content type
                contentType = readLine();
                contentType = parseContentType(contentType);
            }
            
           
            
            //ignore next line (whitespace) (unless it's a file
            //without content-type)
	    if (! ((isFile) && contentType == null)) {
		readLine();
            }
            
            MultipartElement element = null;
            
            //process a file element
            if (isFile) {
                try {
                    //create a local file on disk representing the element
                    File elementFile = createLocalFile();

                    element = new MultipartElement(name, filename, contentType, elementFile);
                } catch (IOException ioe) {
                    throw new ServletException("IOException while reading file element: " + ioe.getMessage(), ioe);
                }
            }
            else {
                 //read data into String form, then convert to bytes
                //for text
                StringBuffer textData = new StringBuffer();
                String line;
                //parse for text data
                line = readLine();

                while ((line != null) && (!line.startsWith(boundary))) {
                    textData.append(line);
                    line = readLine();
                }

                if (textData.length() > 0) {
                    //cut off "\r" from the end if necessary
                    if (textData.charAt(textData.length()-1) == '\r') {
                        textData.setLength(textData.length()-1);
                    }
                }
                
                //create the element
                element = new MultipartElement(name, textData.toString());
            }
            return element;
        }       
        
        //reset stream
        if (inputStream.markSupported()) {
            try {
                inputStream.reset();
            }
            catch (IOException ioe) {
                throw new ServletException("IOException while resetting input stream: " +
                    ioe.getMessage());
            }
        }
        return null;       
    }
    
    /**
     * Set the maximum amount of bytes read from a line at one time
     *
     * @see javax.servlet.ServletInputStream#readLine(byte[], int, int)
     */
    public void setBufferSize(int bufferSize) {
        this.bufferSize = bufferSize;
    }
    
    /**
     * Get the maximum amount of bytes read from a line at one time
     *
     * @see javax.servlet.ServletInputStream#readLine(byte[], int, int)
     */
    public int getBufferSize() {
        return bufferSize;
    }
    
    /**
     * Set the maximum post data size allowed for a multipart request
     * @param maxSize The maximum post data size in bytes, set to <code>-1</code>
     *                for no limit
     */
    public void setMaxSize(long maxSize) {
        this.maxSize = maxSize;
    }
    
    /** 
     * Get the maximum post data size allowed for a multipart request
     * @return The maximum post data size in bytes
     */
    public long getMaxSize() {
        return maxSize;
    }
    
    /**
     * Handles retrieving the boundary and setting the input stream
     */
    protected void parseRequest() throws ServletException {
             
        contentLength = request.getContentLength();
        
        //set boundary
        boundary = parseBoundary(request.getContentType());
        boundaryBytes = boundary.getBytes();
        
        try {
            //set the input stream
            inputStream = new BufferedMultipartInputStream(request.getInputStream(),
                                                           bufferSize,
                                                           contentLength,
                                                           maxSize);
            //mark the input stream to allow multiple reads
            if (inputStream.markSupported()) {
                inputStream.mark(contentLength+1);
            }
                
        }
        catch (IOException ioe) {
            throw new ServletException("Problem while reading request: " + 
                ioe.getMessage(), ioe);
        }
       
        if ((boundary == null) || (boundary.length() < 1)) {
            //try retrieving the header through more "normal" means
            boundary = parseBoundary(request.getHeader("Content-type"));
        }
        
        if ((boundary == null) || (boundary.length() < 1)) {
            throw new ServletException("MultipartIterator: cannot retrieve boundary " +
                                       "for multipart request");
        }
        
        //read first line
        try {
	    String firstLine = readLine();

	    if (firstLine == null) {
		throw new ServletException("MultipartIterator: no multipart request data " +
					   "sent");
	    }
            if (!firstLine.startsWith(boundary)) {
                throw new ServletException("MultipartIterator: invalid multipart request " +
                                           "data, doesn't start with boundary");
            }
        }
        catch (UnsupportedEncodingException uee) {
            throw new ServletException("MultipartIterator: encoding \"ISO-8859-1\" not supported");
        }
    }
      
    /**
     * Parses a content-type String for the boundary.  Appends a 
     * "--" to the beginning of the boundary, because thats the
     * real boundary as opposed to the shortened one in the
     * content type.
     */
    public static String parseBoundary(String contentType) {
        if (contentType.lastIndexOf("boundary=") != -1) {
            String _boundary = "--" + 
                               contentType.substring(contentType.lastIndexOf("boundary=")+9);
            if (_boundary.endsWith("\n")) {
                //strip it off
                return _boundary.substring(0, _boundary.length()-1);
            }
            return _boundary; 
        }
        return null;      
    }
    
    /**
     * Parses the "Content-Type" line of a multipart form for a content type
     *
     * @param contentTypeString A String reprsenting the Content-Type line, 
     *        with a trailing "\n"
     * @return The content type specified, or <code>null</code> if one can't be
     *         found.
     */
    public static String parseContentType(String contentTypeString) {
        int nameIndex = contentTypeString.indexOf("Content-Type: ");
        
        if (nameIndex != -1) {
            int endLineIndex = contentTypeString.indexOf("\n");
            if (endLineIndex == -1) {
                endLineIndex = contentTypeString.length()-1;
            }
            return contentTypeString.substring(nameIndex+14, endLineIndex);
        }
        return null;
    }
    
    /**
     * Retrieves the "name" attribute from a content disposition line
     * 
     * @param dispositionString The entire "Content-disposition" string
     * @return <code>null</code> if no name could be found, otherwise,
     *         returns the name
     * @see #parseForAttribute(String, String)
     */
    public static String parseDispositionName(String dispositionString) {
        return parseForAttribute("name", dispositionString);
    }
    
    /** 
     * Retrieves the "filename" attribute from a content disposition line
     *
     * @param dispositionString The entire "Content-disposition" string
     * @return <code>null</code> if no filename could be found, otherwise,
     *         returns the filename
     * @see #parseForAttribute(String, String)
     */
    public static String parseDispositionFilename(String dispositionString) {
        return parseForAttribute("filename", dispositionString);
    }
        
    
    /**
     * Parses a string looking for a attribute-value pair, and returns the value.
     * For example:
     * <pre>
     *      String parseString = "Content-Disposition: filename=\"bob\" name=\"jack\"";
     *      MultipartIterator.parseForAttribute(parseString, "name");
     * </pre>
     * That will return "bob".
     * 
     * @param attribute The name of the attribute you're trying to get
     * @param parseString The string to retrieve the value from
     * @return The value of the attribute, or <code>null</code> if none could be found
     */
    public static String parseForAttribute(String attribute, String parseString) {
        int nameIndex = parseString.indexOf(attribute + "=\"");
        if (nameIndex != -1) {
            
            int endQuoteIndex = parseString.indexOf("\"", nameIndex+attribute.length()+3);
            
            if (endQuoteIndex != -1) {
                return parseString.substring(nameIndex+attribute.length()+2, endQuoteIndex);
            }
            return "";
        }        
        return null;
    }
    
    /**
     * Reads the input stream until it reaches a new line
     */
    protected String readLine() throws ServletException, UnsupportedEncodingException {
       
        byte[] bufferByte = new byte[bufferSize];
        int bytesRead;
        
        if (totalLength >= contentLength) {
            return null;
        }
        
        try {
            bytesRead = inputStream.readLine(bufferByte,
                                             0,
                                             bufferSize);
        }
        catch (IOException ioe) {
            throw new ServletException("IOException while reading multipart request: " + 
				       ioe.getMessage());
        }
        if (bytesRead == -1) {
            return null;
        }
        
        totalLength += bytesRead;
        return new String(bufferByte, 0, bytesRead, "ISO-8859-1");
    }
    
    /**
     * Creates a file on disk from the current mulitpart element
     * @param fileName the name of the multipart file
     */
    protected File createLocalFile() throws IOException {
        
        File tempFile = File.createTempFile("strts", null, new File(tempDir));
        BufferedOutputStream fos = new BufferedOutputStream(new FileOutputStream(tempFile),
                                                            diskBufferSize);
        byte[] lineBuffer = new byte[MAX_LINE_SIZE];
	int bytesRead = inputStream.readLine(lineBuffer, 0, MAX_LINE_SIZE);
        
        boolean cutCarriage = false;
        boolean cutNewline = false;
        
        try {
            while ((bytesRead != -1) && (!equals(lineBuffer, 0, boundaryBytes.length,
                    boundaryBytes))) {

                        if (cutCarriage) {
                            fos.write('\r');
                            cutCarriage = false;
                        }
                        if (cutNewline) {
                            fos.write('\n');
                            cutNewline = false;
                        }
                        if (bytesRead > 0) {
                            if (lineBuffer[bytesRead-1] == '\r') {
                                //bytesRead--;
                                cutCarriage = true;
                                fos.write(lineBuffer, 0, bytesRead-1);                                
                            }
                            else {
                                fos.write(lineBuffer, 0, bytesRead);
                            }                               
                        }
                        if (bytesRead < MAX_LINE_SIZE) {
                            cutNewline = true;
                        }
                        bytesRead = inputStream.readLine(lineBuffer, 0, MAX_LINE_SIZE);
            }
        }
        catch (IOException ioe) {
            fos.close();
            tempFile.delete();
            throw ioe;
        }        
        fos.flush();	
        fos.close();
        return tempFile;
    }
    
   /**
    * Checks bytes for equality.  Two byte arrays are equal if
    * each of their elements are the same.  This method checks
    * comp[offset] with source[0] to source[length-1] with
    * comp[offset + length - 1]
    * @param comp The byte to compare to <code>source</code>
    * @param offset The offset to start at in <code>comp</code>
    * @param length The length of <code>comp</code> to compare to
    * @param source The reference byte to test for equality
    */
   public static boolean equals(byte[] comp, int offset, int length,
                                byte[] source) {
    
       if (length != source.length) {
         return false;
       }
    
       for (int i = 0; i < length; i++) {
           if (comp[offset+i] != source[i]) {
               return false;
           }
       }
       return true;    
   }

}