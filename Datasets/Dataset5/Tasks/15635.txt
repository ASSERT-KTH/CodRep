import org.apache.xerces.impl.dtd.XMLDTDValidator;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001 The Apache Software Foundation.  All rights 
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
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:  
 *       "This product includes software developed by the
 *        Apache Software Foundation (http://www.apache.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Xerces" and "Apache Software Foundation" must
 *    not be used to endorse or promote products derived from this
 *    software without prior written permission. For written 
 *    permission, please contact apache@apache.org.
 *
 * 5. Products derived from this software may not be called "Apache",
 *    nor may "Apache" appear in their name, without prior written
 *    permission of the Apache Software Foundation.
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
 * individuals on behalf of the Apache Software Foundation and was
 * originally based on software copyright (c) 1999, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package xni.parser;

import org.apache.xerces.impl.XMLDTDValidator;
import org.apache.xerces.impl.XMLNamespaceBinder;
import org.apache.xerces.parsers.StandardParserConfiguration;
import org.apache.xerces.util.SymbolTable;

/**
 * Non-validating parser configuration.
 *
 * @see XMLComponent
 * @see XMLParserConfiguration
 *
 * @author Andy Clark, IBM
 *
 * @version $Id$
 */
public class NonValidatingParserConfiguration 
    extends StandardParserConfiguration {

    //
    // Data
    //

    // components (configurable)

    /** Namespace binder. */
    protected XMLNamespaceBinder fNamespaceBinder;

    //
    // Constructors
    //

    /**
     * Constructs a document parser using the default symbol table and grammar
     * pool or the ones specified by the application (through the properties).
     */
    public NonValidatingParserConfiguration() {

        // create and register missing components
        fNamespaceBinder = new XMLNamespaceBinder();
        addComponent(fNamespaceBinder);

    } // <init>()

    //
    // Protected methods
    //
    
    /** Configures the pipeline. */
    protected void configurePipeline() {

        // REVISIT: This should be better designed. In other words, we
        //          need to figure out what is the best way for people to
        //          re-use *most* of the standard configuration but do 
        //          common things such as remove a component (e.g.the
        //          validator), insert a new component (e.g. XInclude), 
        //          etc... -Ac

        // setup document pipeline
        fScanner.setDocumentHandler(fNamespaceBinder);
        fNamespaceBinder.setDocumentHandler(fDocumentHandler);

    } // configurePipeline()

    // factory methods

    /** Create a null validator. */
    protected XMLDTDValidator createDTDValidator() {
        return null;
    } // createDTDValidator():XMLDTDValidator

} // class NonValidatingParserConfiguration