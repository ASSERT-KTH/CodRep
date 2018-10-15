nodeRet, copyNode(node));

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001, 2002 The Apache Software Foundation.  All rights
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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.xs.models;

import org.apache.xerces.xni.QName;
import org.apache.xerces.impl.dtd.models.CMNode;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.xs.XSDeclarationPool;
import org.apache.xerces.impl.xs.XSComplexTypeDecl;
import org.apache.xerces.impl.xs.XSParticleDecl;
import org.apache.xerces.impl.xs.XSModelGroupImpl;
import org.apache.xerces.impl.xs.XSElementDecl;
import org.apache.xerces.impl.xs.models.*;

/**
 * This class constructs content models for a given grammar.
 *
 * @author Elena Litani, IBM
 * @author Sandy Gao, IBM
 * 
 * @version $Id$
 */
public class CMBuilder {

    // REVISIT: should update the decl pool to cache XSCM objects too
    private XSDeclarationPool fDeclPool = null;
    
    // It never changes, so a static member is good enough
    private static XSEmptyCM fEmptyCM = new XSEmptyCM();

    // needed for DFA construction
    private int fLeafCount;
    // needed for UPA
    private int fParticleCount;

    public CMBuilder() {
        fDeclPool = null;
    }

    public CMBuilder(XSDeclarationPool pool) {
        fDeclPool = pool;
    }

    public void setDeclPool(XSDeclarationPool declPool) {
        fDeclPool = declPool;
    }

    /**
     * Get content model for the a given type
     *
     * @param typeDecl  get content model for which complex type 
     * @return          a content model validator
     */
    public XSCMValidator getContentModel(XSComplexTypeDecl typeDecl) {

        // for complex type with empty or simple content,
        // there is no content model validator
        short contentType = typeDecl.fContentType;
        if (contentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE ||
            contentType == XSComplexTypeDecl.CONTENTTYPE_EMPTY) {
            return null;
        }

        XSParticleDecl particle = typeDecl.fParticle;
        
        // if the content is element only or mixed, but no particle
        // is defined, return the empty content model
        if (particle == null)
            return fEmptyCM;
        
        // if the content model contains "all" model group,
        // we create an "all" content model, otherwise a DFA content model
        XSCMValidator cmValidator = null;
        if (particle.fType == XSParticleDecl.PARTICLE_MODELGROUP &&
            ((XSModelGroupImpl)particle.fValue).fCompositor == XSModelGroupImpl.MODELGROUP_ALL) {
            cmValidator = createAllCM(particle);
        }
        else {
            cmValidator = createDFACM(particle);
        }

        // if the validator returned is null, it means there is nothing in
        // the content model, so we return the empty content model.
        if (cmValidator == null)
            cmValidator = fEmptyCM;
            
        return cmValidator;
    }

    XSCMValidator createAllCM(XSParticleDecl particle) {
        if (particle.fMaxOccurs == 0)
            return null;

        // create an all content model. the parameter indicates whether
        // the <all> itself is optional        
        XSAllCM allContent = new XSAllCM(particle.fMinOccurs == 0);
        
        // get the model group, and add all children of it to the content model
        XSModelGroupImpl group = (XSModelGroupImpl)particle.fValue;
        for (int i = 0; i < group.fParticleCount; i++) {
            // for all non-empty particles
            if (group.fParticles[i].fType != XSParticleDecl.PARTICLE_EMPTY &&
                group.fParticles[i].fMaxOccurs != 0)
                // add the element decl to the all content model
                allContent.addElement((XSElementDecl)group.fParticles[i].fValue,
                                      group.fParticles[i].fMinOccurs == 0);
        }
        return allContent;
    }
    
    XSCMValidator createDFACM(XSParticleDecl particle) {
        fLeafCount = 0;
        fParticleCount = 0;
        // convert particle tree to CM tree
        CMNode node = buildSyntaxTree(particle);
        if (node == null)
            return null;
        // build DFA content model from the CM tree
        return new XSDFACM(node, fLeafCount);
    }

    // 1. convert particle tree to CM tree:
    // 2. expand all occurrence values: a{n, unbounded} -> a, a, ..., a+
    //                                  a{n, m} -> a, a, ..., a?, a?, ...
    // 3. convert model groups (a, b, c, ...) or (a | b | c | ...) to
    //    binary tree: (((a,b),c),...) or (((a|b)|c)|...)
    // 4. make sure each leaf node (XSCMLeaf) has a distinct position
    private CMNode buildSyntaxTree(XSParticleDecl particle) {

        int maxOccurs = particle.fMaxOccurs;
        int minOccurs = particle.fMinOccurs;
        short type = particle.fType;
        CMNode nodeRet = null;
        
        if ((type == XSParticleDecl.PARTICLE_WILDCARD) ||
            (type == XSParticleDecl.PARTICLE_ELEMENT)) {
            // (task 1) element and wildcard particles should be converted to
            // leaf nodes
            // REVISIT: Make a clone of the leaf particle, so that if there
            // are two references to the same group, we have two different
            // leaf particles for the same element or wildcard decl.
            // This is useful for checking UPA.
            nodeRet = new XSCMLeaf(particle.fType, particle.fValue, fParticleCount++, fLeafCount++);
            // (task 2) expand occurrence values
            nodeRet = expandContentModel(nodeRet, minOccurs, maxOccurs);
        }
        else if (type == XSParticleDecl.PARTICLE_MODELGROUP) {
            // (task 1,3) convert model groups to binary trees
            XSModelGroupImpl group = (XSModelGroupImpl)particle.fValue;
            CMNode temp = null;
            for (int i = 0; i < group.fParticleCount; i++) {
                // first convert each child to a CM tree
                temp = buildSyntaxTree(group.fParticles[i]);
                // then combine them using binary operation
                if (temp != null) {
                    if (nodeRet == null) {
                        nodeRet = temp;
                    }
                    else {
                        nodeRet = new XSCMBinOp(group.fCompositor, nodeRet, temp);
                    }
                }
            }
            // (task 2) expand occurrence values
            if (nodeRet != null)
                nodeRet = expandContentModel(nodeRet, minOccurs, maxOccurs);
        }

        return nodeRet;
    }

    // 2. expand all occurrence values: a{n, unbounded} -> a, a, ..., a+
    //                                  a{n, m} -> a, a, ..., a?, a?, ...
    // 4. make sure each leaf node (XSCMLeaf) has a distinct position
    private CMNode expandContentModel(CMNode node,
                                      int minOccurs, int maxOccurs) {

        CMNode nodeRet = null;

        if (minOccurs==1 && maxOccurs==1) {
            nodeRet = node;
        }
        else if (minOccurs==0 && maxOccurs==1) {
            //zero or one
            nodeRet = new XSCMUniOp(XSParticleDecl.PARTICLE_ZERO_OR_ONE, node);
        }
        else if (minOccurs == 0 && maxOccurs==SchemaSymbols.OCCURRENCE_UNBOUNDED) {
            //zero or more
            nodeRet = new XSCMUniOp(XSParticleDecl.PARTICLE_ZERO_OR_MORE, node);
        }
        else if (minOccurs == 1 && maxOccurs==SchemaSymbols.OCCURRENCE_UNBOUNDED) {
            //one or more
            nodeRet = new XSCMUniOp(XSParticleDecl.PARTICLE_ONE_OR_MORE, node);
        }
        else if (maxOccurs == SchemaSymbols.OCCURRENCE_UNBOUNDED) {
            // => a,a,..,a+
            // create a+ node first, then put minOccurs-1 a's in front of it
            // for the first time "node" is used, we don't need to make a copy
            // and for other references to node, we make copies
            nodeRet = new XSCMUniOp(XSParticleDecl.PARTICLE_ONE_OR_MORE, node);
            for (int i=0; i < minOccurs-1; i++) {
                // (task 4) we need to call copyNode here, so that we append
                // an entire new copy of the node (a subtree). this is to ensure
                // all leaf nodes have distinct position
                nodeRet = new XSCMBinOp(XSModelGroupImpl.MODELGROUP_SEQUENCE,
                                        copyNode(node), nodeRet);
            }
        }
        else {
            // {n,m} => a,a,a,...(a),(a),...
            // first n a's, then m-n a?'s.
            // copyNode is called, for the same reason as above
            if (minOccurs > 0) {
                nodeRet = node;
                for (int i=0; i<minOccurs-1; i++) {
                    nodeRet = new XSCMBinOp(XSModelGroupImpl.MODELGROUP_SEQUENCE,
                                            nodeRet, copyNode(node));
                }
            }
            if (maxOccurs > minOccurs) {
                node = new XSCMUniOp(XSParticleDecl.PARTICLE_ZERO_OR_ONE, node);
                if (nodeRet == null) {
                    nodeRet = node;
                }
                else {
                    nodeRet = new XSCMBinOp(XSModelGroupImpl.MODELGROUP_SEQUENCE,
                                            nodeRet, copyNode(node));
                }
                for (int i=minOccurs; i<maxOccurs-1; i++) {
                    nodeRet = new XSCMBinOp(XSModelGroupImpl.MODELGROUP_SEQUENCE,
                                            nodeRet, node);
                }
            }
        }

        return nodeRet;
    }
    
    // 4. make sure each leaf node (XSCMLeaf) has a distinct position
    private CMNode copyNode(CMNode node) {
        int type = node.type();
        // for choice or sequence, copy the two subtrees, and combine them
        if (type == XSModelGroupImpl.MODELGROUP_CHOICE ||
            type == XSModelGroupImpl.MODELGROUP_SEQUENCE) {
            XSCMBinOp bin = (XSCMBinOp)node;
            node = new XSCMBinOp(type, copyNode(bin.getLeft()),
                                 copyNode(bin.getRight()));
        }
        // for ?+*, copy the subtree, and put it in a new ?+* node
        else if (type == XSParticleDecl.PARTICLE_ZERO_OR_MORE ||
                 type == XSParticleDecl.PARTICLE_ONE_OR_MORE ||
                 type == XSParticleDecl.PARTICLE_ZERO_OR_ONE) {
            XSCMUniOp uni = (XSCMUniOp)node;
            node = new XSCMUniOp(type, copyNode(uni.getChild()));
        }
        // for element/wildcard (leaf), make a new leaf node,
        // with a distinct position
        else if (type == XSParticleDecl.PARTICLE_ELEMENT ||
                 type == XSParticleDecl.PARTICLE_WILDCARD) {
            XSCMLeaf leaf = (XSCMLeaf)node;
            node = new XSCMLeaf(leaf.type(), leaf.getLeaf(), leaf.getParticleId(), fLeafCount++);
        }
        
        return node;
    }
}