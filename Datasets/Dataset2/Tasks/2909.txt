req.getURLDecoder().convert( pathMB , false );

/*
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
 * [Additional notices, if required by prior licensing conditions]
 *
 */ 

package org.apache.tomcat.modules.mappers;

import org.apache.tomcat.core.*;
import org.apache.tomcat.util.buf.*;
import org.apache.tomcat.util.http.*;
import java.util.*;
import java.io.*;

/**
 * Default actions after receiving the request: get charset, unescape,
 * pre-process.  This intercept can optionally normalize the request
 * and check for certain unsafe escapes.  Both of these options
 * are on by default.
 * 
 */
public class DecodeInterceptor extends  BaseInterceptor  {
    private String defaultEncoding=null;
    // debug, default will be false, null, null
    private boolean useSessionEncoding=true; 
    private String charsetAttribute="charset";
    private String charsetURIAttribute=";charset=";

    // Note ids
    private int encodingInfoNote;
    // req.decoded - Is set after the request is decoded. The value is the
    // module that provided the decoding ( test for not null only )
    private int decodedNote;
    private int encodingSourceNote;
    private int sessionEncodingNote;

    private boolean normalize=true;
    private boolean safe=true;
    private boolean saveOriginal=false;
    public DecodeInterceptor() {
    }

    /* -------------------- Config  -------------------- */

    /** Set server-wide default encoding. 
     *  UTF-8 is recommended ( if you want to brake the standard spec, which
     *  requires 8859-1 )
     */
    public void setDefaultEncoding( String s ) {
	defaultEncoding=s;
    }

    public void setUseSessionEncoding( boolean b ) {
	useSessionEncoding=b;
    }

    public void setCharsetAttribute( String s ) {
	charsetAttribute=s;
	charsetURIAttribute=";" + charsetAttribute + "=";
    }

    /** Decode interceptor can normalize urls, per RFC 1630
    */
    public void setNormalize( boolean b ) {
	normalize=b;
    }

    /** Save the original uri before decoding. Default is false,
     *  for consistency among servers.
     */
    public void setSaveOriginal( boolean b ) {
	saveOriginal=b;
    }

    /** Decode interceptor can reject unsafe urls. These are
        URL's containing the following escapes:
        %25 = '%'
        %2E = '.'
        %2F = '/'
        %5C = '\'
        These are rejected because they interfere with URL's
        pattern matching with reguard to security issues.
    */
    public void setSafe( boolean b ) {
	safe=b;
    }
    
    /* -------------------- Initialization -------------------- */
    
    public void engineInit( ContextManager cm )
	throws TomcatException
    {
	encodingInfoNote=cm.getNoteId(ContextManager.REQUEST_NOTE,
				  "req.encoding" );
	encodingSourceNote=cm.getNoteId(ContextManager.REQUEST_NOTE,
				  "req.encodingSource" );
	sessionEncodingNote=cm.getNoteId(ContextManager.SESSION_NOTE,
				  "session.encoding" );
	decodedNote=cm.getNoteId(ContextManager.REQUEST_NOTE,
				  "req.decoded" );
    }
    /* -------------------- Request mapping -------------------- */


    // Based on Apache's path normalization code
    private void normalizePath(MessageBytes pathMB ) {
	if( debug> 0 ) log( "Normalize " + pathMB.toString());
	if( pathMB.getType() == MessageBytes.T_BYTES ) {
	    boolean modified=normalize( pathMB.getByteChunk());
	    if( modified ) {
		pathMB.resetStringValue();
	    }
	} else if( pathMB.getType() == MessageBytes.T_CHARS ) {
	    String orig=pathMB.toString();
	    String str1=normalize( orig );
	    if( orig!=str1 ) {
		pathMB.resetStringValue();
		pathMB.setString( str1 );
	    }
	} else if( pathMB.getType() == MessageBytes.T_STR ) {
	    String orig=pathMB.toString();
	    String str1=normalize( orig );
	    if( orig!=str1 ) {
		pathMB.resetStringValue();
		pathMB.setString( str1 );
	    }
	}

    }

    private boolean normalize(  ByteChunk bc ) {
	int start=bc.getStart();
	int end=bc.getEnd();
	byte buff[]=bc.getBytes();
	int i=0;
	int j=0;
	boolean modified=false;
	String orig=null;
	if( debug>0 ) orig=new String( buff, start, end-start);
	
	// remove //
	for( i=start, j=start; i<end-1; i++ ) {
	    if( buff[i]== '/' && buff[i+1]=='/' ) {
		while( buff[i+1]=='/' ) i++;
	    } 
	    buff[j++]=buff[i];
	}
	if( i!=j ) {
	    buff[j++]=buff[end-1];
	    end=j;
	    bc.setEnd( end );
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate // " + orig + " " + start + " " + end );
	    }
	}
	
	// remove /./
	for( i=start, j=start; i<end-1; i++ ) {
	    if( buff[i]== '.' && buff[i+1]=='/' &&
		( i==0 || buff[i-1]=='/' )) {
		// "/./"
		i+=1;
		if( i==end-1 ) j--; // cut the ending /
	    } else {
		buff[j++]=buff[i];
	    }
	}
	if( i!=j ) {
	    buff[j++]=buff[end-1];
	    end=j;
	    bc.setEnd( end );
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate /./ " + orig);
	    }
	}
	
	// remove  /. at the end
	j=end;
	if( end==start+1 && buff[start]== '.' )
	    end--;
	else if( end > start+1 && buff[ end-1 ] == '.' &&
		 buff[end-2]=='/' ) {
	    end=end-2;
	}
	if( end!=j ) {
	    bc.setEnd( end );
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate ending /. " + orig);
	    }
	}

	// remove /../
	for( i=start, j=start; i<end-2; i++ ) {
	    if( buff[i] == '.' &&
		buff[i+1] == '.' &&
		buff[i+2]== '/' &&
		( i==0 || buff[ i-1 ] == '/' ) ) {

		i+=1;
		// look for the previous /
	        j=j-2;
		while( j>0 && buff[j]!='/' ) {
		    j--;
		}
	    } else {
		buff[j++]=buff[i];
	    }
	}
	if( i!=j ) {
	    buff[j++]=buff[end-2];
	    buff[j++]=buff[end-1];
	    end=j;
	    bc.setEnd( end );
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate /../ " + orig);
	    }
	}


	// remove trailing xx/..
	j=end;
	if( end>start + 3 &&
	    buff[end-1]=='.' &&
	    buff[end-2]=='.' &&
	    buff[end-3]=='/' ) {
	    end-=4;
	    while( end>0 &&  buff[end]!='/' )
		end--; 
	}
	if( end!=j ) {
	    bc.setEnd( end );
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate ending /.. " + orig);
	    }
	}
	return modified;
    }

    private String normalize(  String str ) {
	int start=0;
	int end=str.length();
	char buff[]=str.toCharArray();
	int i=0;
	int j=0;
	boolean modified=false;
	String orig=str;
	
	// remove //
	for( i=start, j=start; i<end-1; i++ ) {
	    if( buff[i]== '/' && buff[i+1]=='/' ) {
		while( buff[i+1]=='/' ) i++;
	    } 
	    buff[j++]=buff[i];
	}
	if( i!=j ) {
	    buff[j++]=buff[end-1];
	    end=j;
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate // " + orig + " " + start + " " + end );
	    }
	}
	
	// remove /./
	for( i=start, j=start; i<end-1; i++ ) {
	    if( buff[i]== '.' && buff[i+1]=='/' &&
		( i==0 || buff[i-1]=='/' )) {
		// "/./"
		i+=1;
		if( i==end-1 ) j--; // cut the ending /
	    } else {
		buff[j++]=buff[i];
	    }
	}
	if( i!=j ) {
	    buff[j++]=buff[end-1];
	    end=j;
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate /./ " + orig);
	    }
	}
	
	// remove  /. at the end
	j=end;
	if( end==start+1 && buff[start]== '.' )
	    end--;
	else if( end > start+1 && buff[ end-1 ] == '.' &&
		 buff[end-2]=='/' ) {
	    end=end-2;
	}
	if( end!=j ) {
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate ending /. " + orig);
	    }
	}

	// remove /../
	for( i=start, j=start; i<end-2; i++ ) {
	    if( buff[i] == '.' &&
		buff[i+1] == '.' &&
		buff[i+2]== '/' &&
		( i==0 || buff[ i-1 ] == '/' ) ) {

		i+=1;
		// look for the previous /
	        j=j-2;
		while( j>0 && buff[j]!='/' ) {
		    j--;
		}
	    } else {
		buff[j++]=buff[i];
	    }
	}
	if( i!=j ) {
	    buff[j++]=buff[end-2];
	    buff[j++]=buff[end-1];
	    end=j;
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate /../ " + orig);
	    }
	}


	// remove trailing xx/..
	j=end;
	if( end>start + 3 &&
	    buff[end-1]=='.' &&
	    buff[end-2]=='.' &&
	    buff[end-3]=='/' ) {
	    end-=4;
	    while( end>0 &&  buff[end]!='/' )
		end--; 
	}
	if( end!=j ) {
	    modified=true;
	    if( debug > 0 ) {
		log( "Eliminate ending /.. " +orig);
	    }
	}
	if( modified )
	    return new String( buff, 0, end );
	else
	    return str;
    }

    private boolean isSafeURI(MessageBytes pathMB) {
        int start = pathMB.indexOf('%');
        if( start >= 0 ) {
            if( pathMB.indexOfIgnoreCase("%25",start) >= 0 )
                return false;

            if( pathMB.indexOfIgnoreCase("%2E",start) >= 0 )
                return false;

            if( pathMB.indexOfIgnoreCase("%2F",start) >= 0 )
                return false;

            if( pathMB.indexOfIgnoreCase("%5C",start) >= 0 )
                return false;
        }

        return true;
    }
    
    public int postReadRequest( Request req ) {
	MessageBytes pathMB = req.requestURI();
	// copy the request 
	
	if( pathMB.isNull())
	    throw new RuntimeException("ASSERT: null path in request URI");

	//if( path.indexOf("?") >=0 )
	//   throw new RuntimeException("ASSERT: ? in requestURI");

        // If path is unsafe, return forbidden
        if( safe && !isSafeURI(pathMB) ){
            req.setAttribute("javax.servlet.error.message","Unsafe URL");
            return 403;
	}
	if( normalize &&
	    ( pathMB.indexOf("//") >= 0 ||
	      pathMB.indexOf("/." ) >=0
	      )) {
	    //debug=1;
	    normalizePath( pathMB );
	    if( debug > 0 )
		log( "Normalized url "  + pathMB );
	}

	// Set the char encoding first
	String charEncoding=null;	
	MimeHeaders headers=req.getMimeHeaders();

	MessageBytes contentType = req.contentType();
	if( contentType != null ) {
	    // XXX use message bytes, optimize !!!
	    String contentTypeString=contentType.toString();
	    charEncoding = ContentType.
		getCharsetFromContentType(contentTypeString);
	    if( debug > 0 ) log( "Got encoding from content-type " +
				 charEncoding + " " + contentTypeString  );
	    req.setNote( encodingSourceNote, "Content-Type" );
	}

	if( debug > 99 ) dumpHeaders(headers);
	
	// No explicit encoding - try to guess it from Accept-Language
	//MessageBytes acceptC= headers.getValue( "Accept-Charset" );

	// No explicit encoding - try to guess it from Accept-Language
	// MessageBytes acceptL= headers.getValue( "Accept-Language" );

	// Special trick: ;charset= attribute ( similar with sessionId )
	// That's perfect for multibyte chars in URLs
	if(charEncoding==null && charsetURIAttribute != null ) {
	    int idxCharset=req.requestURI().indexOf( charsetURIAttribute );
	    if( idxCharset >= 0 ) {
		String uri=req.requestURI().toString();
		int nextAtt=uri.indexOf( ';', idxCharset + 1 );
		String next=null;
		if( nextAtt > 0 ) {
		    next=uri.substring( nextAtt );
		    charEncoding=
			uri.substring(idxCharset+
				      charsetURIAttribute.length(),nextAtt);
		    req.requestURI().
			setString(uri.substring(0, idxCharset) + next);
		    req.setNote( encodingSourceNote, "Request-Attribute" );
		} else {
		    charEncoding=uri.substring(idxCharset+
					       charsetURIAttribute.length());
		    req.requestURI().
			setString(uri.substring(0, idxCharset));
		    req.setNote( encodingSourceNote, "Request-Attribute" );
		}
		
		if( debug > 0 )
		    log("ReqAtt= " + charEncoding + " " +
			req.requestURI() );
	    }
	}
	
	
	// Global Default 
	if( charEncoding==null ) {
	    if( debug > 0 ) log( "Default encoding " + defaultEncoding );
	    if( defaultEncoding != null )
		charEncoding=defaultEncoding;
	}

	if( charEncoding != null )
	    req.setCharEncoding( charEncoding );

	// Decode request, save the original for the facade

	// Already decoded
	if( req.getNote( decodedNote ) != null ) {
	    if( debug> 5 ) log("Already decoded " + req.getNote( decodedNote ));
	    return 0;
	}
	if( saveOriginal ) {
	    try {
		req.unparsedURI().duplicate( pathMB );
	    } catch( IOException ex ) {
		// If it happens, do default processing
		log( "Error copying request ",ex);
	    }
	}
	if (pathMB.indexOf('%') >= 0 || pathMB.indexOf( '+' ) >= 0) {
	    try {
		if(debug>1 )
		    log( "Before " + pathMB.toString());
		req.getURLDecoder().convert( pathMB );
		pathMB.resetStringValue();
		if(debug>1 )
		    log( "After " + pathMB.toString());
		if( pathMB.indexOf( '\0' ) >=0 ) {
		    return 404; // XXX should be 400 
		}
		req.setNote( decodedNote, this );
	    } catch( IOException ex ) {
		log( "Error decoding request ", ex);
		return 400;
	    }
	}

	return 0;
    }

    /** Hook - before the response is sent, get the response encoding
     *  and save it per session ( if we are in a session ). All browsers
     *  I know will use the same encoding in the next request.
     *  Since this is not part of the spec, it's disabled by default.
     *  
     */
    public int beforeBody( Request req, Response res ) {
	if( useSessionEncoding ) {
	    ServerSession sess=req.getSession( false );
	    if( sess!=null ) {
		String charset=res.getCharacterEncoding();
		if( charset!=null ) {
		    sess.setNote( sessionEncodingNote, charset );
		    if( debug > 0 )
			log( "Setting per session encoding " + charset);
		}
	    }
	}
	return DECLINED;
    }

    
    public Object getInfo( Context ctx, Request req, int info, String k ) {
	// Try to get the encoding info ( this is called later )
	if( info == encodingInfoNote ) {
	    // Second attempt to guess the encoding, the request is processed
	    String charset=null;

	    // Use request attributes
	    if( charset==null && charsetAttribute != null ) {
		charset=(String)req.getAttribute( charsetAttribute );
		if( debug>0 && charset != null )
		    log( "Charset from attribute " + charsetAttribute + " "
			 + charset );
	    }
	    
	    // Use session attributes
	    if( charset==null && useSessionEncoding ) {
		ServerSession sess=req.getSession( false );
		if( sess!=null ) {
		    charset=(String)sess.getNote( sessionEncodingNote );
		    if( debug > 0 && charset!=null )
			log("Charset from session " + charset );
		}
	    }

	    // Per context default
	    
	    if( charset != null ) return charset;
	    
	    charset=ctx.getProperty("charset");
	    if( debug > 0 && charset!=null )
		log( "Default per context " + charset );
	    // Use per context default
	    return charset;
	}
	return null;
    }

    public int setInfo( Context ctx, Request req, int info,
			 String k, Object v )
    {
	return DECLINED;
    }

    private void dumpHeaders( MimeHeaders mh ) {
	for( int i=0; i<mh.size(); i++ ) {
	    log( mh.getName(i) + ": " + mh.getValue( i ) );
	}

    }
}
