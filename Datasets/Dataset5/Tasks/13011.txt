return checkSimpleDerivation((DatatypeValidator)directBase,

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999,2000 The Apache Software Foundation.  All rights
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

package org.apache.xerces.impl.v2;

import org.apache.xerces.impl.v2.datatypes.*;
import java.util.Vector;

/**
 * Constaints shared by traversers and validator
 *
 * @author Sandy Gao, IBM
 *
 * @version $Id$
 */
public class XSConstraints {

    /**
     * check whether derived is valid derived from base, given a subset
     * of {restriction, extension}.
     */
    public static boolean checkTypeDerivationOk(XSTypeDecl derived, XSTypeDecl base, int block) {
        // if derived is anyType, then it's valid only if base is anyType too
        if (derived == SchemaGrammar.fAnyType)
            return derived == base;
        // if derived is anySimpleType, then it's valid only if the base
        // is ur-type
        if (derived == SchemaGrammar.fAnySimpleType) {
            return (base == SchemaGrammar.fAnyType ||
                    base == SchemaGrammar.fAnySimpleType);
        }

        // if derived is simple type
        if (derived.getXSType() == XSTypeDecl.SIMPLE_TYPE) {
            // if base is complex type
            if (base.getXSType() == XSTypeDecl.COMPLEX_TYPE) {
                // if base is anyType, change base to anySimpleType,
                // otherwise, not valid
                if (base == SchemaGrammar.fAnyType)
                    base = SchemaGrammar.fAnySimpleType;
                else
                    return false;
            }
            return checkSimpleDerivation((DatatypeValidator)derived,
                                         (DatatypeValidator)base, block);
        } else {
            return checkComplexDerivation((XSComplexTypeDecl)derived, base, block);
        }
    }

    /**
     * check whether simple type derived is valid derived from base,
     * given a subset of {restriction, extension}.
     */
    public static boolean checkSimpleDerivationOk(DatatypeValidator derived, XSTypeDecl base, int block) {
        // if derived is anySimpleType, then it's valid only if the base
        // is ur-type
        if (derived == SchemaGrammar.fAnySimpleType) {
            return (base == SchemaGrammar.fAnyType ||
                    base == SchemaGrammar.fAnySimpleType);
        }

        // if base is complex type
        if (base.getXSType() == XSTypeDecl.COMPLEX_TYPE) {
            // if base is anyType, change base to anySimpleType,
            // otherwise, not valid
            if (base == SchemaGrammar.fAnyType)
                base = SchemaGrammar.fAnySimpleType;
            else
                return false;
        }
        return checkSimpleDerivation((DatatypeValidator)derived,
                                     (DatatypeValidator)base, block);
    }

    /**
     * check whether complex type derived is valid derived from base,
     * given a subset of {restriction, extension}.
     */
    public static boolean checkComplexDerivationOk(XSComplexTypeDecl derived, XSTypeDecl base, int block) {
        // if derived is anyType, then it's valid only if base is anyType too
        if (derived == SchemaGrammar.fAnyType)
            return derived == base;
        return checkComplexDerivation((XSComplexTypeDecl)derived, base, block);
    }

    /**
     * Note: this will be a private method, and it assumes that derived is not
     *       anySimpleType, and base is not anyType. Another method will be
     *       introduced for public use, which will call this method.
     */
    private static boolean checkSimpleDerivation(DatatypeValidator derived, DatatypeValidator base, int block) {
        // 1 They are the same type definition.
        if (derived == base)
            return true;

        // 2 All of the following must be true:
        // 2.1 restriction is not in the subset, or in the {final} of its own {base type definition};
        if ((block & SchemaSymbols.RESTRICTION) != 0 ||
            (derived.getBaseValidator().getFinalSet() & SchemaSymbols.RESTRICTION) != 0) {
            return false;
        }

        // 2.2 One of the following must be true:
        // 2.2.1 D's ·base type definition· is B.
        DatatypeValidator directBase = derived.getBaseValidator();
        if (directBase == base)
            return true;

        // 2.2.2 D's ·base type definition· is not the ·simple ur-type definition· and is validly derived from B given the subset, as defined by this constraint.
        if (directBase != SchemaGrammar.fAnySimpleType &&
            checkSimpleDerivation(directBase, base, block)) {
            return true;
        }

        // 2.2.3 D's {variety} is list or union and B is the ·simple ur-type definition·.
        if ((derived instanceof ListDatatypeValidator ||
             derived instanceof UnionDatatypeValidator) &&
            base == SchemaGrammar.fAnySimpleType) {
            return true;
        }

        // 2.2.4 B's {variety} is union and D is validly derived from a type definition in B's {member type definitions} given the subset, as defined by this constraint.
        if (base instanceof UnionDatatypeValidator) {
            Vector subUnionMemberDV = ((UnionDatatypeValidator)base).getBaseValidators();
            int subUnionSize = subUnionMemberDV.size();
            for (int i=0; i<subUnionSize; i++) {
                base = (DatatypeValidator)subUnionMemberDV.elementAt(i);
                if (checkSimpleDerivation(derived, base, block))
                    return true;
            }
        }

        return false;
    }

    /**
     * Note: this will be a private method, and it assumes that derived is not
     *       anyType. Another method will be introduced for public use,
     *       which will call this method.
     */
    private static boolean checkComplexDerivation(XSComplexTypeDecl derived, XSTypeDecl base, int block) {
        // 2.1 B and D must be the same type definition.
        if (derived == base)
            return true;

        // 1 If B and D are not the same type definition, then the {derivation method} of D must not be in the subset.
        if ((derived.fDerivedBy & block) != 0)
            return false;

        // 2 One of the following must be true:
        XSTypeDecl directBase = derived.fBaseType;
        // 2.2 B must be D's {base type definition}.
        if (directBase == base)
            return true;

        // 2.3 All of the following must be true:
        // 2.3.1 D's {base type definition} must not be the ·ur-type definition·.
        if (directBase == SchemaGrammar.fAnyType ||
            directBase == SchemaGrammar.fAnySimpleType) {
            return false;
        }

        // 2.3.2 The appropriate case among the following must be true:
        // 2.3.2.1 If D's {base type definition} is complex, then it must be validly derived from B given the subset as defined by this constraint.
        if (directBase.getXSType() == XSTypeDecl.COMPLEX_TYPE)
            return checkComplexDerivation((XSComplexTypeDecl)directBase, base, block);

        // 2.3.2.2 If D's {base type definition} is simple, then it must be validly derived from B given the subset as defined in Type Derivation OK (Simple) (§3.14.6).
        if (directBase.getXSType() == XSTypeDecl.SIMPLE_TYPE) {
            // if base is complex type
            if (base.getXSType() == XSTypeDecl.COMPLEX_TYPE) {
                // if base is anyType, change base to anySimpleType,
                // otherwise, not valid
                if (base == SchemaGrammar.fAnyType)
                    base = SchemaGrammar.fAnySimpleType;
                else
                    return false;
            }
            return checkSimpleDerivation((DatatypeValidator)derived,
                                         (DatatypeValidator)base, block);
        }

        return false;
    }

    /**
     * check whether a value is a valid default for some type
     */
    public static boolean ElementDefaultValidImmediate(XSTypeDecl type, String value) {
        return true;
    }
} // class XSContraints