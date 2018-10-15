nodeRet = new XSCMLeaf(XSParticleDecl.PARTICLE_ELEMENT, (XSElementDecl)(startNode.fValue), fLeafCount++);

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
 * originally based on software copyright (c) 2001, International
 * Business Machines, Inc., http://www.apache.org.  For more
 * information on the Apache Software Foundation, please see
 * <http://www.apache.org/>.
 */

package org.apache.xerces.impl.v2;

import org.apache.xerces.xni.QName;
import org.apache.xerces.impl.validation.models.CMNode;

/**
 * This class constructs content models for a given grammar.
 *
 * @author Elena Litani, IBM
 * @version $Id$
 */
public class CMBuilder {

    private final QName fQName1 = new QName();
    private final QName fQName2 = new QName();

    private XSDeclarationPool fDeclPool = null;

    // needed for DFA construction
    private int fLeafCount;

    //REVISIT: add substitution comparator!!

    public CMBuilder (XSDeclarationPool pool){
        fDeclPool = pool;
    }

    /**
     * Get content model for the a given type
     *
     * @param elementDeclIndex
     * @param comparator
     * @return
     * @exception Exception
     */
    public XSCMValidator getContentModel(XSComplexTypeDecl typeDecl) {

        // REVISIT: can we assume that this method never called for elements of simpleType
        // content?
        short contentType = typeDecl.fContentType;
        if (contentType == XSComplexTypeDecl.CONTENTTYPE_SIMPLE ||
            contentType == XSComplexTypeDecl.CONTENTTYPE_EMPTY) {
            return null;
        }

        XSCMValidator cmValidator = null;

        XSParticleDecl particle = typeDecl.fParticle;
        
        // This check is performed in XSComplexTypeDecl.
        //if (cmValidator != null)
        //    return cmValidator;
        
        
        if (particle != null)
            particle = expandParticleTree( (XSParticleDecl)particle);

        // REVISIT: should we expand?? or throw away the expanded tree??
        //typeDecl.fParticle

        // And create the content model according to the spec type

        if (particle == null) {
            // create special content model for no element content
            cmValidator = new XSEmptyCM();
        }
        else if (contentType == XSComplexTypeDecl.CONTENTTYPE_MIXED) {
               //
              // Create a child model as
              // per the element-only case              
            cmValidator = createChildModel(particle, true);        
        }
        else if (contentType == XSComplexTypeDecl.CONTENTTYPE_ELEMENT) {
            //  This method will create an optimal model for the complexity
            //  of the element's defined model. If its simple, it will create
            //  a SimpleContentModel object. If its a simple list, it will
            //  create a SimpleListContentModel object. If its complex, it
            //  will create a DFAContentModel object.
            //
            cmValidator = createChildModel(particle, false);
        }
        else {
            throw new RuntimeException("Unknown content type for a element decl "
                                       + "in getElementContentModelValidator() in Grammar class");
        }
        // Add the new model to the content model for this element
        typeDecl.fCMValidator = cmValidator;

        return cmValidator;
    }


    private XSParticleDecl expandParticleTree( XSParticleDecl particle) {

        // We may want to consider trying to combine this with buildSyntaxTree at some
        // point (if possible)

        //REVISIT: need access to grammar object
        //if (!grammar.fDeferParticleExpantion) {
        //    return particle;
        //}
        int maxOccurs = particle.fMaxOccurs;
        int minOccurs = particle.fMinOccurs;
        short type = particle.fType;
        if ((type == XSParticleDecl.PARTICLE_WILDCARD) ||
            (type == XSParticleDecl.PARTICLE_ELEMENT)) {

            // When checking Unique Particle Attribution, rename leaf elements
            //if (grammar.fUPAChecking) {
            // REVISIT: implement
            //}
            
            return expandContentModel(particle, minOccurs, maxOccurs);
        }
        else if (type == XSParticleDecl.PARTICLE_CHOICE ||
                 type == XSParticleDecl.PARTICLE_ALL ||
                 type == XSParticleDecl.PARTICLE_SEQUENCE) {

            Object left = particle.fValue;
            Object right = particle.fOtherValue;

            //REVISIT: look at uri and switch grammar if necessary
            left =  expandParticleTree( (XSParticleDecl)left);
            if (right != null) 
                right =  expandParticleTree( (XSParticleDecl)right);
            
            // At this point, by expanding the particle tree, we may have a null left or right
            if (left==null && right==null) 
                return null;
          
            if (left == null)
                return expandContentModel((XSParticleDecl)right, minOccurs, maxOccurs);

            if (right == null)
                return expandContentModel((XSParticleDecl)left, minOccurs, maxOccurs);

            // When checking Unique Particle Attribution, we always create new
            // new node to store different name for different groups
            //if (grammar.fUPAChecking) {
            //REVISIT:
            //contentSpecIndex = addContentSpecNode (type, left, right, false);
            //}

            particle.fValue = left;
            particle.fOtherValue = right;
            return expandContentModel((XSParticleDecl)particle, minOccurs, maxOccurs);
        }
        else if (type == XSParticleDecl.PARTICLE_EMPTY) {
            return null;
        }
        else {
            // When checking Unique Particle Attribution, we have to rename
            // uri even on zero_or_one, zero_or_more and one_or_more
            //if (grammar.fUPAChecking)
            //REVISIT:
            //return addContentSpecNode (type,
            //                           convertContentSpecTree(particle.fValue),
            //                           convertContentSpecTree(particle.fOtherValue),
            //                           false);
        }
        return particle;
    }



    /**
     * When the element has a 'CONTENTTYPE_ELEMENT' model, this method is called to
     * create the content model object. It looks for some special case simple
     * models and creates SimpleContentModel objects for those. For the rest
     * it creates the standard DFA style model.
     *
     * @param grammar
     * @param fParticleIndex
     * @return
     */
    private XSCMValidator createChildModel(XSParticleDecl particle, boolean isMixed) {

        //
        //  Get the content spec node for the element we are working on.
        //  This will tell us what kind of node it is, which tells us what
        //  kind of model we will try to create.
        //
        //XMLContentSpec fParticle = new XMLContentSpec();
        short type = particle.fType;
        if (type == XSParticleDecl.PARTICLE_WILDCARD) {
            // let fall through to build a DFAContentModel
        }
        else if (isMixed) {
            if (type ==XSParticleDecl.PARTICLE_ALL) {
                // All the nodes under an ALL must be additional ALL nodes and
                // ELEMENTs (or ELEMENTs under ZERO_OR_ONE nodes.)
                // We collapse the ELEMENTs into a single vector.
                XSAllCM allContent = new XSAllCM(false);
                gatherAllLeaves ((XSParticleDecl)(particle.fValue), allContent);
                gatherAllLeaves ((XSParticleDecl)(particle.fOtherValue), allContent);
                return allContent; 
                
            }
            else if (type == XSParticleDecl.PARTICLE_ZERO_OR_ONE) {
                 XSParticleDecl left = (XSParticleDecl)particle.fValue;


                // An ALL node can appear under a ZERO_OR_ONE node.
                if (type ==XSParticleDecl.PARTICLE_ALL) {
                    XSAllCM allContent = new XSAllCM(true);
                    gatherAllLeaves (left, allContent);
                    return allContent;

                }
            }
            // otherwise, let fall through to build a DFAContentModel
        }
        else if (type == XSParticleDecl.PARTICLE_ELEMENT) {
            //
            //  Check that the left value is not null, since any content model
            //  with PCDATA should be MIXED, so we should not have gotten here.
            //
            if (particle.fValue == null &&
                particle.fOtherValue == null)
                throw new RuntimeException("ImplementationMessages.VAL_NPCD");

            //
            //  Its a single leaf, so its an 'a' type of content model, i.e.
            //  just one instance of one element. That one is definitely a
            //  simple content model.
            //
            // pass element declaration
            
            return new XSSimpleCM(type, (XSElementDecl)particle.fValue);
        }
        else if ((type == XSParticleDecl.PARTICLE_CHOICE)
                 ||  (type == XSParticleDecl.PARTICLE_SEQUENCE)) {
            //
            //  Lets see if both of the children are leafs. If so, then it
            //  it has to be a simple content model
            //
            XSParticleDecl left = (XSParticleDecl)particle.fValue;
            XSParticleDecl right = (XSParticleDecl)particle.fOtherValue;

            if ((right.fType == XSParticleDecl.PARTICLE_ELEMENT)
                &&  (left.fType == XSParticleDecl.PARTICLE_ELEMENT)) {
                //
                //  Its a simple choice or sequence, so we can do a simple
                //  content model for it.
                //
                // pass both element decls
                return new XSSimpleCM(type, (XSElementDecl)left.fValue, (XSElementDecl)right.fValue);
            }

        }
	else if (type == XSParticleDecl.PARTICLE_ALL) {
        
            XSParticleDecl left = (XSParticleDecl)particle.fValue;
            XSParticleDecl right = (XSParticleDecl)particle.fOtherValue;
            
            XSAllCM allContent = new XSAllCM(false);

            gatherAllLeaves (left, allContent);
            gatherAllLeaves (right, allContent);
            return allContent;
        }
        else if ((type == XSParticleDecl.PARTICLE_ZERO_OR_ONE)
                 ||  (type == XSParticleDecl.PARTICLE_ZERO_OR_MORE)
                 ||  (type == XSParticleDecl.PARTICLE_ONE_OR_MORE)) {
            //
            //  Its a repetition, so see if its one child is a leaf. If so
            //  its a repetition of a single element, so we can do a simple
            //  content model for that.
            XSParticleDecl left = (XSParticleDecl) particle.fValue;

            if (left.fType == XSParticleDecl.PARTICLE_ELEMENT) {
                //
                //  It is, so we can create a simple content model here that
                //  will check for this repetition. We pass -1 for the unused
                //  right node.
                //
                return new XSSimpleCM(type, (XSElementDecl)left.fValue);
            }
            else if (left.fType==XSParticleDecl.PARTICLE_ALL) {
		 		 XSAllCM allContent = new XSAllCM(true);
                gatherAllLeaves (left, allContent);
                return allContent;
            }


        }
        else {
            throw new RuntimeException("ImplementationMessages.VAL_CST");
        }

        //
        //  Its not a simple content model, so here we have to create a DFA
        //  for this element. So we create a DFAContentModel object. He
        //  encapsulates all of the work to create the DFA.
        //

        //REVISIT: add DFA Content Model
        fLeafCount = 0;
        CMNode node = buildSyntaxTree(particle);
        return new XSDFACM(node, fLeafCount, isMixed);
    }



    private XSParticleDecl expandContentModel(XSParticleDecl particle,
                                              int minOccurs, int maxOccurs) {


        // REVISIT: should we handle (maxOccurs - minOccurs) = {1,2} as
        //          separate case?

        XSParticleDecl leafParticle = particle;
        XSParticleDecl optional = null;
        if (minOccurs==1 && maxOccurs==1) {
            return particle;
        }
        else if (minOccurs==0 && maxOccurs==1) {
            //zero or one
            return createParticle ( XSParticleDecl.PARTICLE_ZERO_OR_ONE,particle,null);
        }
        else if (minOccurs == 0 && maxOccurs==SchemaSymbols.OCCURRENCE_UNBOUNDED) {
            //zero or more
            return createParticle (XSParticleDecl.PARTICLE_ZERO_OR_MORE, particle, null);
        }
        else if (minOccurs == 1 && maxOccurs==SchemaSymbols.OCCURRENCE_UNBOUNDED) {
            //one or more
            return createParticle (XSParticleDecl.PARTICLE_ONE_OR_MORE, particle, null);
        }
        else if (maxOccurs == SchemaSymbols.OCCURRENCE_UNBOUNDED) {
            if (minOccurs<2) {
                //REVISIT
            }

            // => a,a,..,a+
            particle = createParticle (XSParticleDecl.PARTICLE_ONE_OR_MORE,
                                       particle, null);

            for (int i=0; i < (minOccurs-1); i++) {
                particle = createParticle (XSParticleDecl.PARTICLE_SEQUENCE, leafParticle, particle);
            }
            return particle;

        }
        else {
            // {n,m} => a,a,a,...(a),(a),...


            if (minOccurs==0) {
                optional = createParticle (XSParticleDecl.PARTICLE_ZERO_OR_ONE,
                                           leafParticle,
                                           null);
                particle = optional;
                for (int i=0; i < (maxOccurs-minOccurs-1); i++) {
                    particle = createParticle (XSParticleDecl.PARTICLE_SEQUENCE,
                                               particle,
                                               optional);
                }
            }
            else {
                for (int i=0; i<(minOccurs-1); i++) {
                    particle = createParticle (XSParticleDecl.PARTICLE_SEQUENCE,
                                               particle,
                                               leafParticle);
                }

                optional = createParticle(XSParticleDecl.PARTICLE_ZERO_OR_ONE,
                                          leafParticle,
                                          null);

                for (int i=0; i < (maxOccurs-minOccurs); i++) {
                    particle = createParticle(XSParticleDecl.PARTICLE_SEQUENCE,
                                              particle,
                                              optional);
                }
            }
        }

        return particle;
    }

    /**
     *  Recursively builds an AllContentModel based on a particle tree
     *  rooted at an ALL node.
     */
     private void gatherAllLeaves(XSParticleDecl particle,
                                        XSAllCM allContent) {
        Object left = particle.fValue;
        Object right = particle.fOtherValue;        
        int type = particle.fType;

        if (type == XSParticleDecl.PARTICLE_ALL) {
          
            // At an all node, visit left and right subtrees
            gatherAllLeaves ((XSParticleDecl)left, allContent);
            gatherAllLeaves ((XSParticleDecl) particle.fOtherValue, allContent);
        }
        else if (type == XSParticleDecl.PARTICLE_ELEMENT) {
          
            // At leaf, add the element to list of elements permitted in the all
            allContent.addElement ((XSElementDecl)left, false);
        }
        else if (type == XSParticleDecl.PARTICLE_ZERO_OR_ONE) {
          
            // At ZERO_OR_ONE node, subtree must be an element
            // that was specified with minOccurs=0, maxOccurs=1
            // Add the optional element to list of elements permitted in the all
          
            if (((XSParticleDecl)left).fType == XSParticleDecl.PARTICLE_ELEMENT) {
                allContent.addElement ((XSElementDecl)(((XSParticleDecl)left).fValue), true);
            }
            else {
            // report error
		throw new RuntimeException("ImplementationMessages.VAL_CST");
            }		  		 
        }
        else { 
            // report error
            throw new RuntimeException("ImplementationMessages.VAL_CSTA");
        }
    }

    private XSParticleDecl createParticle (short type,
                                           XSParticleDecl left,
                                           XSParticleDecl right) {

        XSParticleDecl newParticle = new XSParticleDecl();
        newParticle.fType = type;
        newParticle.fValue = (Object) left;
        newParticle.fOtherValue = (Object)right;
        return newParticle;
    }

    // this method is needed to convert a tree of ParticleDecl
    // nodes into a tree of content models that XSDFACM methods can then use as input.
    private final CMNode buildSyntaxTree(XSParticleDecl startNode) {

        // We will build a node at this level for the new tree
        CMNode nodeRet = null;
        if (startNode.fType == XSParticleDecl.PARTICLE_WILDCARD) {
            nodeRet = new XSCMAny(startNode.fType, ((XSWildcardDecl)startNode.fValue), fLeafCount++);
        }
        //
        //  If this node is a leaf, then its an easy one. We just add it
        //  to the tree.
        //
        else if (startNode.fType == XSParticleDecl.PARTICLE_ELEMENT) {
            //
            //  Create a new leaf node, and pass it the current leaf count,
            //  which is its DFA state position. Bump the leaf count after
            //  storing it. This makes the positions zero based since we
            //  store first and then increment.
            //
            nodeRet = new XSCMLeaf((XSElementDecl)(startNode.fValue), fLeafCount++);
        } 
        else {
            //
            //  Its not a leaf, so we have to recurse its left and maybe right
            //  nodes. Save both values before we recurse and trash the node.
            final XSParticleDecl leftNode = ((XSParticleDecl)startNode.fValue);
            final XSParticleDecl rightNode = ((XSParticleDecl)startNode.fOtherValue);

            if ((startNode.fType == XSParticleDecl.PARTICLE_CHOICE)
                ||  (startNode.fType == XSParticleDecl.PARTICLE_SEQUENCE)) {
                //
                //  Recurse on both children, and return a binary op node
                //  with the two created sub nodes as its children. The node
                //  type is the same type as the source.
                //

                nodeRet = new XSCMBinOp( startNode.fType, buildSyntaxTree(leftNode)
                                       , buildSyntaxTree(rightNode));
            } 
            else if (startNode.fType == XSParticleDecl.PARTICLE_ZERO_OR_MORE
		       || startNode.fType == XSParticleDecl.PARTICLE_ZERO_OR_ONE
		       || startNode.fType == XSParticleDecl.PARTICLE_ONE_OR_MORE) {
                nodeRet = new XSCMUniOp(startNode.fType, buildSyntaxTree(leftNode));
            } 
            else {
		        throw new RuntimeException("ImplementationMessages.VAL_CST");
            }
        }
        // And return our new node for this level
        return nodeRet;
    }
   
}