private static final String DEFAULT_FACTORY_CLASS = "org.apache.xerces.impl.dv.xs.SchemaDVFactoryImpl";

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

package org.apache.xerces.impl.dv;

import java.util.Hashtable;

/**
 * Defines a factory API that enables applications to <p>
 * 1. to get the instance of specified SchemaDVFactory implementation <p>
 * 2. to create/return built-in schema simple types <p>
 * 3. to create user defined simple types. <p>
 *
 * Implementations of this abstract class can be used to get built-in simple
 * types and create user-defined simle types. <p>
 *
 * The implementation should store the built-in datatypes in static data, so
 * that they can be shared by multiple parser instance, and multiple threads.
 *
 * @author Sandy Gao, IBM
 *
 * @version $Id$
 */
public abstract class SchemaDVFactory {

    private static final String DEFAULT_FACTORY_CLASS = "org.apache.xerces.impl.dv.xs_new.SchemaDVFactoryImpl";

    private static String          fFactoryClass    = null;
    private static SchemaDVFactory fFactoryInstance = null;

    /**
     * Set the class name of the schema dv factory implementation. This method
     * can only be called before the first time the method <code>getInstance</code>
     * successfully returns, otherwise a DVFactoryException will be thrown.
     *
     * @param className  the class name of the SchemaDVFactory implementation
     * @exception DVFactoryException  the method cannot be called at this time
     */
    public static final void setFactoryClass(String factoryClass) throws DVFactoryException {
        // if the factory instance has been created, it's an error.
        if (fFactoryInstance != null)
            throw new DVFactoryException("Cannot set the class name now. The class name '"+fFactoryClass+"' is already used.");

        // synchronize on the string value
        synchronized (DEFAULT_FACTORY_CLASS) {
            // in case this thread was waiting for another thread
            if (fFactoryInstance != null)
                throw new DVFactoryException("Cannot set the class name now. The class name '"+fFactoryClass+"' is already used.");

            fFactoryClass = factoryClass;
        }
    }

    /**
     * Get an instance of SchemaDVFactory implementation.
     *
     * If <code>setFactoryClass</code> is called before this method,
     * the passed-in class name will be used to create the factory instance.
     * Otherwise, a default implementation is used.
     *
     * After the first time this method successfully returns, any subsequent
     * invocation to this method returns the same instance.
     *
     * @return  an instance of SchemaDVFactory implementation
     * @exception DVFactoryException  cannot create an instance of the specified
     *                                class name or the default class name
     */
    public static final SchemaDVFactory getInstance() throws DVFactoryException {
        // if the factory instance has been created, just return it.
        if (fFactoryInstance != null)
            return fFactoryInstance;

        // synchronize on the string value, to make sure that we don't create
        // two instance of the dv factory class
        synchronized (DEFAULT_FACTORY_CLASS) {
            // in case this thread was waiting for another thread to create
            // the factory instance, just return the instance created by the
            // other thread.
            if (fFactoryInstance != null)
                return fFactoryInstance;

            try {
                // if the class name is not specified, use the default one
                if (fFactoryClass == null)
                    fFactoryClass = DEFAULT_FACTORY_CLASS;
                fFactoryInstance = (SchemaDVFactory)(Class.forName(fFactoryClass).newInstance());
            } catch (ClassNotFoundException e1) {
                throw new DVFactoryException("Schema factory class " + fFactoryClass + " not found.");
            } catch (IllegalAccessException e2) {
                throw new DVFactoryException("Schema factory class " + fFactoryClass + " found but cannot be loaded.");
            } catch (InstantiationException e3) {
                throw new DVFactoryException("Schema factory class " + fFactoryClass + " loaded but cannot be instantiated (no empty public constructor?).");
            } catch (ClassCastException e4) {
                throw new DVFactoryException("Schema factory class " + fFactoryClass + " does not extend from SchemaDVFactory.");
            }
        }

        // return the newly created dv factory instance
        return fFactoryInstance;
    }

    // can't create a new object of this class
    protected SchemaDVFactory(){}

    /**
     * Get a built-in simple type of the given name
     * REVISIT: its still not decided within the Schema WG how to define the
     *          ur-types and if all simple types should be derived from a
     *          complex type, so as of now we ignore the fact that anySimpleType
     *          is derived from anyType, and pass 'null' as the base of
     *          anySimpleType. It needs to be changed as per the decision taken.
     *
     * @param name  the name of the datatype
     * @return      the datatype validator of the given name
     */
    public abstract XSSimpleType getBuiltInType(String name);

    /**
     * get all built-in simple types, which are stored in a hashtable keyed by
     * the name
     *
     * @return      a hashtable which contains all built-in simple types
     */
    public abstract Hashtable getBuiltInTypes();

    /**
     * Create a new simple type which is derived by restriction from another
     * simple type.
     *
     * @param name              name of the new type, could be null
     * @param targetNamespace   target namespace of the new type, could be null
     * @param finalSet          value of "final"
     * @param base              base type of the new type
     * @return                  the newly created simple type
     */
    public abstract XSSimpleType createTypeRestriction(String name, String targetNamespace,
                                                       short finalSet, XSSimpleType base);

    /**
     * Create a new simple type which is derived by list from another simple
     * type.
     *
     * @param name              name of the new type, could be null
     * @param targetNamespace   target namespace of the new type, could be null
     * @param finalSet          value of "final"
     * @param itemType          item type of the list type
     * @return                  the newly created simple type
     */
    public abstract XSListSimpleType createTypeList(String name, String targetNamespace,
                                                    short finalSet, XSSimpleType itemType);

    /**
     * Create a new simple type which is derived by union from a list of other
     * simple types.
     *
     * @param name              name of the new type, could be null
     * @param targetNamespace   target namespace of the new type, could be null
     * @param finalSet          value of "final"
     * @param base              member types of the union type
     * @return                  the newly created simple type
     */
    public abstract XSUnionSimpleType createTypeUnion(String name, String targetNamespace,
                                                      short finalSet, XSSimpleType[] memberTypes);

}