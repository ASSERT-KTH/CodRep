public class XSWildcardDecl  {

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

package org.apache.xerces.impl.v2;

import org.apache.xerces.xni.QName;
import java.util.Vector;

/**
 * The XML representation for a wildcard declaration
 * schema component is an <any> or <anyAttribute> element information item
 *
 * @author Sandy Gao, IBM
 * @author Rahul Srivastava, Sun Microsystems Inc.
 *
 * @version $Id$
 */
public class XSWildcardDecl  extends XSElementDecl {

    // types of wildcard
    // namespace="##any"
    public static final short WILDCARD_ANY   = 0;
    // namespace="##other"
    public static final short WILDCARD_OTHER = 1;
    // namespace= (list of (anyURI | ##targetNamespace | ##local))
    public static final short WILDCARD_LIST  = 2;

    // types of process contents
    // processContents="strict"
    public static final short WILDCARD_STRICT = 0;
    // processContents="lax"
    public static final short WILDCARD_LAX    = 1;
    // processContents="skip"
    public static final short WILDCARD_SKIP   = 2;

    // the type of wildcard: any, other, or list
    public short fType = WILDCARD_ANY;
    // the type of process contents: strict, lax, or skip
    public short fProcessContents = WILDCARD_STRICT;
    // the namespace list:
    // for WILDCARD_LIST, it means one of the namespaces in the list
    // for WILDCARD_OTHER, it means not any of the namespaces in the list
    public String[] fNamespaceList;

    /**
     * Whether a namespace is allowed by this wildcard
     */
    public boolean allowNamespace(String namespace) {
        // ##any allows any namespace
        if (fType == WILDCARD_ANY)
            return true;

        // ##other doesn't allow target namespace and empty namespace
        if (fType == WILDCARD_OTHER) {
            return namespace != fNamespaceList[0] &&
                   namespace != fNamespaceList[1];
        }

        // list allows any one in the list
        int listNum = fNamespaceList.length;
        for (int i = 0; i < listNum; i++) {
            if (namespace == fNamespaceList[i])
                return true;
        }

        return false;
    }

    //NOTE: ##OTHER means not targetNamespace, according to spec.
    //      We are not considering it as, not and a set of URI's, where targetNamespace is
    //      one of the element in the set. This may be taken as an enhanced feature, later.

    public boolean isSubsetOf(XSWildcardDecl superWildcard) {
        // For a namespace constraint (call it sub) to be an intensional subset of another namespace
        // constraint (call it super) one of the following must be true:

        // 1 super must be any.
    if (superWildcard.fType == WILDCARD_ANY) {
        return true;
    }
    // 2 All of the following must be true:
    //   2.1 sub must be a pair of not and a namespace name or ·absent·.
    //   2.2 super must be a pair of not and the same value.
    else if ( (fType == WILDCARD_OTHER) && (superWildcard.fType == WILDCARD_OTHER) ){
        return (fNamespaceList[0] == superWildcard.fNamespaceList[0]);
    }
    // 3 All of the following must be true:
    //   3.1 sub must be a set whose members are either namespace names or ·absent·.
    //   3.2 One of the following must be true:
    //       3.2.1 super must be the same set or a superset thereof.
    //       3.2.2 super must be a pair of not and a namespace name or ·absent· and
    //             that value must not be in sub's set.
    else if (fType == WILDCARD_LIST) {
        if (superWildcard.fType == WILDCARD_LIST) {
            boolean found;

            for (int i=0; i<fNamespaceList.length; i++) {
                found = false;
                for (int j=0; j<superWildcard.fNamespaceList.length; j++)
                    if (fNamespaceList[i] == superWildcard.fNamespaceList[j]) {
                        found = true;
                        break;
                    }
                if (!found) return false;
            }
            return true;
        }
        else if (superWildcard.fType == WILDCARD_OTHER) {
            for (int i=0; i<fNamespaceList.length; i++) {
                if (superWildcard.fNamespaceList[0] == fNamespaceList[i])
                    return false;
            }
            return true;
        }
    }

    return false;
    }


    public XSWildcardDecl performUnionWith(XSWildcardDecl wildcard) {
        // For a wildcard's {namespace constraint} value to be the intensional union of two other such
        // values (call them O1 and O2): the appropriate case among the following must be true:

    XSWildcardDecl unionWildcard = new XSWildcardDecl();

        // 1 If O1 and O2 are the same value, then that value must be the value.
    if (areSame(wildcard)) {
        unionWildcard.fType = fType;
        if (fType != WILDCARD_ANY)
            //REVISIT: Is it okay to copy like this.
            unionWildcard.fNamespaceList = fNamespaceList;
    }
    // 2 If either O1 or O2 is any, then any must be the value.
    else if ( (fType == WILDCARD_ANY) || (wildcard.fType == WILDCARD_ANY) ) {
        unionWildcard.fType = WILDCARD_ANY;
    }
    // 3 If both O1 and O2 are sets of (namespace names or ·absent·), then the union of those sets
    //   must be the value.
    else if ( (fType == WILDCARD_LIST) && (wildcard.fType == WILDCARD_LIST) ) {
        boolean found;
        Vector union = null;

        // This way, the vector may be resized exactly once or none.
        if (fNamespaceList.length > wildcard.fNamespaceList.length)
            union = new Vector(fNamespaceList.length, wildcard.fNamespaceList.length);
        else
            union = new Vector(wildcard.fNamespaceList.length, fNamespaceList.length);

        for (int i=0; i<fNamespaceList.length; i++)
            union.addElement(fNamespaceList[i]);

        for (int i=0; i<wildcard.fNamespaceList.length; i++) {
            found = false;
            for (int j=0; j<fNamespaceList.length; j++)
                if (fNamespaceList[j] == wildcard.fNamespaceList[i]) {
                    found = true;
                    break;
                }
            if (!found)
                union.addElement(wildcard.fNamespaceList[i]);
        }

            unionWildcard.fType = WILDCARD_LIST;
            // copy elements from vector to array
            int size = union.size();
            unionWildcard.fNamespaceList = new String[size];
            union.copyInto(unionWildcard.fNamespaceList);
    }

    //REVISIT: 4 If the two are negations of different namespace names, then the intersection is not expressible.

    // 5 If either O1 or O2 is a pair of not and a namespace name and the other is a set of
    //   (namespace names or ·absent·), then The appropriate case among the following must be true:
        //      5.1 If the set includes the negated namespace name, then any must be the value.
        //      5.2 If the set does not include the negated namespace name, then whichever of O1 or O2
        //          is a pair of not and a namespace name must be the value.
    else if ( ((fType == WILDCARD_OTHER) && (wildcard.fType == WILDCARD_LIST)) ||
              ((fType == WILDCARD_LIST) && (wildcard.fType == WILDCARD_OTHER)) ) {

        int i=0;

        if (fType == WILDCARD_OTHER) {
            for (i=0; i<wildcard.fNamespaceList.length; i++)
                if (fNamespaceList[0] == wildcard.fNamespaceList[i]) {
                    unionWildcard.fType = WILDCARD_ANY;
                    break;
                }
            // Loop traversed completely. This means, negated namespace viz. tNS (here)
            // is not in the other list. So, union is other.
            if (i == wildcard.fNamespaceList.length) {
                unionWildcard.fType = fType;
                //REVISIT: Is it okay to copy like this.
                unionWildcard.fNamespaceList = fNamespaceList;
            }
        }
        else {
            for (i=0; i<fNamespaceList.length; i++)
                if (wildcard.fNamespaceList[0] == fNamespaceList[i]) {
                    unionWildcard.fType = WILDCARD_ANY;
                    break;
                }
            // Loop traversed completely. This means, negated namespace viz. tNS (here)
            // is not in the other list. So, union is other.
            if (i == fNamespaceList.length) {
                unionWildcard.fType = wildcard.fType;
                //REVISIT: Is it okay to copy like this.
                unionWildcard.fNamespaceList = wildcard.fNamespaceList;
            }
        }
    }

    unionWildcard.fProcessContents = fProcessContents;
    return unionWildcard;

    } // performUnionWith


    public XSWildcardDecl performIntersectionWith(XSWildcardDecl wildcard) {
        // For a wildcard's {namespace constraint} value to be the intensional intersection of two other
        // such values (call them O1 and O2): the appropriate case among the following must be true:

    XSWildcardDecl intersectWildcard = new XSWildcardDecl();

        // 1 If O1 and O2 are the same value, then that value must be the value.
    if (areSame(wildcard)) {
        intersectWildcard.fType = fType;
        if (fType != WILDCARD_ANY)
            //REVISIT: Is it okay to copy like this.
            intersectWildcard.fNamespaceList = fNamespaceList;
    }
    // 2 If either O1 or O2 is any, then the other must be the value.
    else if ( (fType == WILDCARD_ANY) || (wildcard.fType == WILDCARD_ANY) ) {
        if (fType == WILDCARD_ANY) {
            intersectWildcard.fType = wildcard.fType;
            // both cannot be ANY, if we have reached here.
            //REVISIT: Is it okay to copy like this.
            intersectWildcard.fNamespaceList = wildcard.fNamespaceList;
        }
        else {
            intersectWildcard.fType = fType;
            // both cannot be ANY, if we have reached here.
            //REVISIT: Is it okay to copy like this.
            intersectWildcard.fNamespaceList = fNamespaceList;
        }
    }
    // 3 If either O1 or O2 is a pair of not and a namespace name and the other is a set of
    //   (namespace names or ·absent·), then that set, minus the negated namespace name if it was in
    //   the set, must be the value.
    else if ( ((fType == WILDCARD_OTHER) && (wildcard.fType == WILDCARD_LIST)) ||
              ((fType == WILDCARD_LIST) && (wildcard.fType == WILDCARD_OTHER)) ) {
            Vector intersect = null;
            if (fType == WILDCARD_OTHER) {
                intersect = new Vector(wildcard.fNamespaceList.length);
                for (int i=0; i<wildcard.fNamespaceList.length; i++)
                    if (fNamespaceList[0] != wildcard.fNamespaceList[i])
                        intersect.addElement(wildcard.fNamespaceList[i]);
            }
            else {
                intersect = new Vector(fNamespaceList.length);
                for (int i=0; i<fNamespaceList.length; i++)
                    if (wildcard.fNamespaceList[0] != fNamespaceList[i])
                        intersect.addElement(fNamespaceList[i]);
            }
        intersectWildcard.fType = WILDCARD_LIST;
            // copy elements from vector to array
            int size = intersect.size();
            intersectWildcard.fNamespaceList = new String[size];
            intersect.copyInto(intersectWildcard.fNamespaceList);
    }
    // 4 If both O1 and O2 are sets of (namespace names or ·absent·), then the intersection of those
    //   sets must be the value.
    else if ( (fType == WILDCARD_LIST) && (wildcard.fType == WILDCARD_LIST) ) {
        boolean found;
        Vector intersect = null;

        if (fNamespaceList.length < wildcard.fNamespaceList.length)
            intersect = new Vector(fNamespaceList.length);
        else
            intersect = new Vector(wildcard.fNamespaceList.length);

        for (int i=0; i<fNamespaceList.length; i++) {
            found = false;
            for (int j=0; j<wildcard.fNamespaceList.length; j++)
                if (fNamespaceList[i] == wildcard.fNamespaceList[j]) {
                    found = true;
                    break;
                }
            if (found)
                intersect.addElement(fNamespaceList[i]);
        }

        intersectWildcard.fType = WILDCARD_LIST;
            // copy elements from vector to array
            int size = intersect.size();
            intersectWildcard.fNamespaceList = new String[size];
            intersect.copyInto(intersectWildcard.fNamespaceList);
    }
    //REVISIT: 5 If the two are negations of different namespace names, then the intersection is not expressible.

    intersectWildcard.fProcessContents = fProcessContents;
    return intersectWildcard;

    } // performIntersectionWith

    private boolean areSame(XSWildcardDecl wildcard) {
    if (fType == wildcard.fType) {
        if (fType == WILDCARD_ANY)
            return true;
        else {
            if (fNamespaceList.length == wildcard.fNamespaceList.length) {
                int i=0;
                for (; i<fNamespaceList.length; i++) {
                    if (fNamespaceList[i] != wildcard.fNamespaceList[i])
                        break;
                }
                if (i == fNamespaceList.length)
                    return true;
            }
        }
    }

    return false;

    } // areSame

    // REVISIT: how to prepresent wildcard in string.
    //          "namespace:usr=someuri," is not so descriptive
    public String toString() {
        String ret = null;
        switch (fType) {
        case WILDCARD_ANY:
            ret = SchemaSymbols.ATTVAL_TWOPOUNDANY;
            break;
        case WILDCARD_OTHER:
            ret = SchemaSymbols.ATTVAL_TWOPOUNDOTHER + ":uri=" + fNamespaceList[0];
            break;
        case WILDCARD_LIST:
            ret = "namespace:uri=" + fNamespaceList[0];
            for (int i = 1; i < fNamespaceList.length; i++)
                ret += "," + fNamespaceList[i];
            break;
        }

        return ret;
    }
} // class XSWildcardDecl