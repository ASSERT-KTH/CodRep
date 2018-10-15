if (decl == fElemMap[inIndex])

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 1999-2001 The Apache Software Foundation.  All rights
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

import org.apache.xerces.impl.v2.msg.ImplementationMessages;
import org.apache.xerces.xni.QName;
import org.apache.xerces.impl.validation.models.CMNode;
import org.apache.xerces.impl.validation.models.CMStateSet;

/**
 * DFAContentModel is the implementation of XSCMValidator that does
 * all of the non-trivial element content validation. This class does
 * the conversion from the regular expression to the DFA that
 * it then uses in its validation algorithm.
 *
 * @author Neil Graham, IBM
 * @version $Id$
 */
public class XSDFACM
    implements XSCMValidator {

    //
    // Constants
    //
    // special strings

    /** Epsilon string. */
    private static final int EPSILON = -2;

    /** End-of-content string. */
    private static final int EOC     = -3;

    // debugging

    /** Set to true to debug content model validation. */
    private static final boolean DEBUG_VALIDATE_CONTENT = false;

    //
    // Data
    //

    /**
     * This is the map of unique input symbol elements to indices into
     * each state's per-input symbol transition table entry. This is part
     * of the built DFA information that must be kept around to do the
     * actual validation.  Note tat since either XSElementDecl or XSParticleDecl object
     * can live here, we've got to use an Object.
     */
    private Object fElemMap[] = null;

    /**
     * This is a map of whether the element map contains information
     * related to ANY models.
     */
    private int fElemMapType[] = null;

    /** The element map size. */
    private int fElemMapSize = 0;

    /* Used to indicate a mixed model */
    private boolean fMixed;

    /**
     * The string index for the 'end of content' string that we add to
     * the string pool. This is used as the special name of an element
     * that represents the end of the syntax tree.
     */
    private static String fEOCString = "<<CMNODE_EOC>>";

    /**
     * The NFA position of the special EOC (end of content) node. This
     * is saved away since it's used during the DFA build.
     */
    private int fEOCPos = 0;

    /**
     * The string index for the 'epsilon' string that we add to the
     * string pool. This represents epsilon node transitions in the
     * syntax tree.
     */
    private static String fEpsilonString = "<<CMNODE_EPSILON>>";

    /**
     * This is an array of booleans, one per state (there are
     * fTransTableSize states in the DFA) that indicates whether that
     * state is a final state.
     */
    private boolean fFinalStateFlags[] = null;

    /**
     * The list of follow positions for each NFA position (i.e. for each
     * non-epsilon leaf node.) This is only used during the building of
     * the DFA, and is let go afterwards.
     */
    private CMStateSet fFollowList[] = null;

    /**
     * This is the head node of our intermediate representation. It is
     * only non-null during the building of the DFA (just so that it
     * does not have to be passed all around.) Once the DFA is built,
     * this is no longer required so its nulled out.
     */
    private CMNode fHeadNode = null;

    /**
     * The count of leaf nodes. This is an important number that set some
     * limits on the sizes of data structures in the DFA process.
     */
    private int fLeafCount = 0;

    /**
     * An array of non-epsilon leaf nodes, which is used during the DFA
     * build operation, then dropped.
     */
    private XSCMLeaf fLeafList[] = null;

    /** Array mapping ANY types to the leaf list. */
    private int fLeafListType[] = null;

    /**
     * This is the transition table that is the main by product of all
     * of the effort here. It is an array of arrays of ints. The first
     * dimension is the number of states we end up with in the DFA. The
     * second dimensions is the number of unique elements in the content
     * model (fElemMapSize). Each entry in the second dimension indicates
     * the new state given that input for the first dimension's start
     * state.
     * <p>
     * The fElemMap array handles mapping from element indexes to
     * positions in the second dimension of the transition table.
     */
    private int fTransTable[][] = null;

    /**
     * The number of valid entries in the transition table, and in the other
     * related tables such as fFinalStateFlags.
     */
    private int fTransTableSize = 0;

    /**
     * Flag that indicates that even though we have a "complicated"
     * content model, it is valid to have no content. In other words,
     * all parts of the content model are optional. For example:
     * <pre>
     *      &lt;!ELEMENT AllOptional (Optional*,NotRequired?)&gt;
     * </pre>
     */
    private boolean fEmptyContentIsValid = false;

    // temp variables

    /** Temporary element declaration. */
    private Object fElementDecl = new Object();

    /** initializing static members **/
    static {
        fEpsilonString = fEpsilonString.intern();
        fEOCString = fEOCString.intern();
    }

    //
    // Constructors
    //

    /**
     * Constructs a DFA content model.
     *
     * @param symbolTable    The symbol table.
     * @param syntaxTree    The syntax tree of the content model.
     * @param leafCount     The number of leaves.
     *
     * @exception RuntimeException Thrown if DFA can't be built.
     */

   public XSDFACM(CMNode syntaxTree,
                          int leafCount) {
       this(syntaxTree, leafCount, false);
   }

    /**
     * Constructs a DFA content model.
     *
     * @param symbolTable    The symbol table.
     * @param syntaxTree    The syntax tree of the content model.
     * @param leafCount     The number of leaves.
     *
     * @exception RuntimeException Thrown if DFA can't be built.
     */

   public XSDFACM(CMNode syntaxTree,
                          int leafCount, boolean mixed) {

        // Store away our index and pools in members
        fLeafCount = leafCount;

        //
        //  Create some string pool indexes that represent the names of some
        //  magical nodes in the syntax tree.
        //  (already done in static initialization...
        //

        fMixed = mixed;

        //
        //  Ok, so lets grind through the building of the DFA. This method
        //  handles the high level logic of the algorithm, but it uses a
        //  number of helper classes to do its thing.
        //
        //  In order to avoid having hundreds of references to the error and
        //  string handlers around, this guy and all of his helper classes
        //  just throw a simple exception and we then pass it along.
        //

        if(DEBUG_VALIDATE_CONTENT) {
            XSDFACM.time -= System.currentTimeMillis();
        }

        buildDFA(syntaxTree);

        if(DEBUG_VALIDATE_CONTENT) {
            XSDFACM.time += System.currentTimeMillis();
            System.out.println("DFA build: " + XSDFACM.time + "ms");
        }
    }

    private static long time = 0;

    //
    // XSCMValidator methods
    //

    /**
     * check whether the given state is one of the final states
     *
     * @param state       the state to check
     *
     * @return whether it's a final state
     */
    public boolean isFinalState (int state) {
        return (state < 0)? false :
            fFinalStateFlags[state];
    }

    /**
     * one transition only
     *
     * @param curElem     The current element's QName
     * @param stateStack  stack to store the previous state
     * @param curPos      the current position of the stack
     *
     * @return:  null if transition is invalid; otherwise the Object corresponding to the
     *      XSElementDecl or XSWildcardDecl identified.  Also, the
     *      state array will be modified to include the new state; this so that the validator can
     *      store it away.
     *
     * @exception RuntimeException thrown on error
     */
    public Object oneTransition(QName curElem, int[] state, SubstitutionGroupHandler subGroupHandler) {
        int curState = state[0];

        if(curState == XSCMValidator.FIRST_ERROR || curState == XSCMValidator.SUBSEQUENT_ERROR) {
            // there was an error last time; so just go find correct Object in fElemmMap.
            // ... after resetting state[0].
            if(curState == XSCMValidator.FIRST_ERROR)
                state[0] = XSCMValidator.SUBSEQUENT_ERROR;

            return findMatchingDecl(curElem, subGroupHandler);
        }

        int nextState = 0;
        int elemIndex = 0;
        Object matchingDecl = null;

        for (; elemIndex < fElemMapSize; elemIndex++) {
            int type = fElemMapType[elemIndex] ;
            if (type == XSParticleDecl.PARTICLE_ELEMENT) {
                matchingDecl = subGroupHandler.getMatchingElemDecl(curElem, (XSElementDecl)fElemMap[elemIndex]);

                if (matchingDecl != null) {
                    nextState = fTransTable[curState][elemIndex];
                    if (nextState != -1)
                        break;
                }
            }
            else if (type == XSParticleDecl.PARTICLE_WILDCARD) {
                if(((XSWildcardDecl)fElemMap[elemIndex]).allowNamespace(curElem.uri)) {
                    matchingDecl = fElemMap[elemIndex];
                    nextState = fTransTable[curState][elemIndex];
                    if (nextState != -1)
                      break;
                }
            }
        }

        // if we still can't find a match, set the state to first_error
        // and return null
        if (elemIndex == fElemMapSize) {
            state[0] = XSCMValidator.FIRST_ERROR;
            return findMatchingDecl(curElem, subGroupHandler);
        }

        state[0] = nextState;
        return matchingDecl;
    } // oneTransition(QName, int[], SubstitutionGroupHandler):  Object

    Object findMatchingDecl(QName curElem, SubstitutionGroupHandler subGroupHandler) {
        Object matchingDecl = null;

        for (int elemIndex = 0; elemIndex < fElemMapSize; elemIndex++) {
            int type = fElemMapType[elemIndex] ;
            if (type == XSParticleDecl.PARTICLE_ELEMENT) {
                matchingDecl = subGroupHandler.getMatchingElemDecl(curElem, (XSElementDecl)fElemMap[elemIndex]);
                if (matchingDecl != null) {
                    return matchingDecl;
                }
            }
            else if (type == XSParticleDecl.PARTICLE_WILDCARD) {
                if(((XSWildcardDecl)fElemMap[elemIndex]).allowNamespace(curElem.uri))
                    return fElemMap[elemIndex];
            }
        }

        return null;
    }

    // This method returns the start states of the content model.
    public int[] startContentModel() {
        int[] val = new int[1];
        val[0]=0;
        return val;
    } // startContentModel():int[]

    // this method returns whether the last state was a valid final state
    public boolean endContentModel(int[] state) {
        return fFinalStateFlags[state[0]];
    } // endContentModel(int[]):  boolean

    // Killed off whatCanGoHere; we may need it for DOM canInsert(...) etc.,
    // but we can put it back later.

    // Unique Particle Attribution
    // REVISIT:  implement UPA!
    // store the conflict results between any two elements in fElemMap
    // -1: not compared; 0: no conflict; 1: conflict
    /******
    private byte fConflictTable[][];

    // check UPA after build the DFA
    public void checkUniqueParticleAttribution(SchemaGrammar gram) {
        // rename back
        for (int i = 0; i < fElemMapSize; i++)
            fElemMap[i].uri = gram.getContentSpecOrgUri(fElemMap[i].uri);

        // initialize the conflict table
        fConflictTable = new byte[fElemMapSize][fElemMapSize];
        for (int j = 0; j < fElemMapSize; j++) {
            for (int k = j+1; k < fElemMapSize; k++)
                fConflictTable[j][k] = -1;
        }

        // for each state, check whether it has overlap transitions
        for (int i = 0; i < fTransTable.length && fTransTable[i] != null; i++) {
            for (int j = 0; j < fElemMapSize; j++) {
                for (int k = j+1; k < fElemMapSize; k++) {
                    if (fTransTable[i][j] != -1 &&
                        fTransTable[i][k] != -1) {
                        if (fConflictTable[j][k] == -1) {
                            fConflictTable[j][k] = ElementWildcard.conflict
                                                   (fElemMapType[j],
                                                    fElemMap[j].localpart,
                                                    fElemMap[j].uri,
                                                    fElemMapType[k],
                                                    fElemMap[k].localpart,
                                                    fElemMap[k].uri,
                                                    comparator) ? (byte)1 : (byte)0;
                        }
                    }
                }
            }
        }

        fConflictTable = null;
    }
    // Unique Particle Attribution
    ******** End commented-out code *****/

    //
    // Private methods
    //

    /**
     * Builds the internal DFA transition table from the given syntax tree.
     *
     * @param syntaxTree The syntax tree.
     *
     * @exception RuntimeException Thrown if DFA cannot be built.
     */
    private void buildDFA(CMNode syntaxTree) {
        //
        //  The first step we need to take is to rewrite the content model
        //  using our CMNode objects, and in the process get rid of any
        //  repetition short cuts, converting them into '*' style repetitions
        //  or getting rid of repetitions altogether.
        //
        //  The conversions done are:
        //
        //  x+ -> (x|x*)
        //  x? -> (x|epsilon)
        //
        //  This is a relatively complex scenario. What is happening is that
        //  we create a top level binary node of which the special EOC value
        //  is set as the right side node. The the left side is set to the
        //  rewritten syntax tree. The source is the original content model
        //  info from the decl pool. The rewrite is done by buildSyntaxTree()
        //  which recurses the decl pool's content of the element and builds
        //  a new tree in the process.
        //
        //  Note that, during this operation, we set each non-epsilon leaf
        //  node's DFA state position and count the number of such leafs, which
        //  is left in the fLeafCount member.
        //
        //  The nodeTmp object is passed in just as a temp node to use during
        //  the recursion. Otherwise, we'd have to create a new node on every
        //  level of recursion, which would be piggy in Java (as is everything
        //  for that matter.)
        //

        /* MODIFIED (Jan, 2001)
         *
         * Use following rules.
         *   nullable(x+) := nullable(x), first(x+) := first(x),  last(x+) := last(x)
         *   nullable(x?) := true, first(x?) := first(x),  last(x?) := last(x)
         *
         * The same computation of follow as x* is applied to x+
         *
         * The modification drastically reduces computation time of
         * "(a, (b, a+, (c, (b, a+)+, a+, (d,  (c, (b, a+)+, a+)+, (b, a+)+, a+)+)+)+)+"
         */

        fElementDecl = new XSElementDecl();
        ((XSElementDecl)fElementDecl).fName = fEOCString;
        XSCMLeaf nodeEOC = new XSCMLeaf((XSElementDecl)fElementDecl);
        fHeadNode = new XSCMBinOp(
        XSParticleDecl.PARTICLE_SEQUENCE
            , syntaxTree
            , nodeEOC
        );

        //
        //  And handle specially the EOC node, which also must be numbered
        //  and counted as a non-epsilon leaf node. It could not be handled
        //  in the above tree build because it was created before all that
        //  started. We save the EOC position since its used during the DFA
        //  building loop.
        //
        fEOCPos = fLeafCount;
        nodeEOC.setPosition(fLeafCount++);

        //
        //  Ok, so now we have to iterate the new tree and do a little more
        //  work now that we know the leaf count. One thing we need to do is
        //  to calculate the first and last position sets of each node. This
        //  is cached away in each of the nodes.
        //
        //  Along the way we also set the leaf count in each node as the
        //  maximum state count. They must know this in order to create their
        //  first/last pos sets.
        //
        //  We also need to build an array of references to the non-epsilon
        //  leaf nodes. Since we iterate it in the same way as before, this
        //  will put them in the array according to their position values.
        //
        fLeafList = new XSCMLeaf[fLeafCount];
        fLeafListType = new int[fLeafCount];
        postTreeBuildInit(fHeadNode, 0);

        //
        //  And, moving onward... We now need to build the follow position
        //  sets for all the nodes. So we allocate an array of state sets,
        //  one for each leaf node (i.e. each DFA position.)
        //
        fFollowList = new CMStateSet[fLeafCount];
        for (int index = 0; index < fLeafCount; index++)
            fFollowList[index] = new CMStateSet(fLeafCount);
        calcFollowList(fHeadNode);
        //
        //  And finally the big push... Now we build the DFA using all the
        //  states and the tree we've built up. First we set up the various
        //  data structures we are going to use while we do this.
        //
        //  First of all we need an array of unique element names in our
        //  content model. For each transition table entry, we need a set of
        //  contiguous indices to represent the transitions for a particular
        //  input element. So we need to a zero based range of indexes that
        //  map to element types. This element map provides that mapping.
        //
        fElemMap = new Object [fLeafCount];
        fElemMapType = new int[fLeafCount];
        fElemMapSize = 0;
        for (int outIndex = 0; outIndex < fLeafCount; outIndex++) {
            // optimization from Henry Zongaro:
            //fElemMap[outIndex] = new Object ();
            fElemMap[outIndex] = null;

            int inIndex = 0;
            final Object decl = fLeafList[outIndex].getDecl();
            if (fLeafListType[outIndex] == XSParticleDecl.PARTICLE_WILDCARD) {
                for (; inIndex < fElemMapSize; inIndex++) {
                    if (decl == fLeafList[inIndex])
                        break;
                }
            } else {
                // Get the current leaf's element
                final XSElementDecl element = (XSElementDecl)decl;
                if (element.fName == fEOCString)
                    continue;

                // See if the current leaf node's element index is in the list
                for (; inIndex < fElemMapSize; inIndex++) {
                    if (fElemMapType[inIndex] == fLeafListType[outIndex] &&
                        ((XSElementDecl)fElemMap[inIndex]).fTargetNamespace == element.fTargetNamespace &&
                        ((XSElementDecl)fElemMap[inIndex]).fName == element.fName)
                        break;
                }
            }

            // If it was not in the list, then add it, if not the EOC node
            if (inIndex == fElemMapSize) {
                fElemMap[fElemMapSize] = decl;
                fElemMapType[fElemMapSize] = fLeafListType[outIndex];
                fElemMapSize++;
            }
        }
        // set up the fLeafNameTypeVector object if there is one.
        /**** but apparently there never will be since this was commented out for some reason...
        if (fLeafNameTypeVector != null) {
            fLeafNameTypeVector.setValues(fElemMap, fElemMapType, fElemMapSize);
        }
        ******/

        /***
         * Optimization(Jan, 2001); We sort fLeafList according to
         * elemIndex which is *uniquely* associated to each leaf.
         * We are *assuming* that each element appears in at least one leaf.
         **/

        int[] fLeafSorter = new int[fLeafCount + fElemMapSize];
        int fSortCount = 0;

        for (int elemIndex = 0; elemIndex < fElemMapSize; elemIndex++) {
            final Object decl = fElemMap[elemIndex];
            for (int leafIndex = 0; leafIndex < fLeafCount; leafIndex++) {
                if (fElemMapType[elemIndex] != fLeafListType[leafIndex])
                    continue;

                if (fLeafListType[leafIndex] == XSParticleDecl.PARTICLE_WILDCARD) {
                    if (decl == fLeafList[leafIndex].getDecl())
                        fLeafSorter[fSortCount++] = leafIndex;
                } else {
                    final XSElementDecl leaf = (XSElementDecl)fLeafList[leafIndex].getDecl();
                    final XSElementDecl element = (XSElementDecl)decl;
                    if (leaf.fTargetNamespace == element.fTargetNamespace &&
                        leaf.fName == element.fName ) {
                        fLeafSorter[fSortCount++] = leafIndex;
                    }
                }
            }
            fLeafSorter[fSortCount++] = -1;
        }

        /* Optimization(Jan, 2001) */

        //
        //  Next lets create some arrays, some that hold transient
        //  information during the DFA build and some that are permament.
        //  These are kind of sticky since we cannot know how big they will
        //  get, but we don't want to use any Java collections because of
        //  performance.
        //
        //  Basically they will probably be about fLeafCount*2 on average,
        //  but can be as large as 2^(fLeafCount*2), worst case. So we start
        //  with fLeafCount*4 as a middle ground. This will be very unlikely
        //  to ever have to expand, though it if does, the overhead will be
        //  somewhat ugly.
        //
        int curArraySize = fLeafCount * 4;
        CMStateSet[] statesToDo = new CMStateSet[curArraySize];
        fFinalStateFlags = new boolean[curArraySize];
        fTransTable = new int[curArraySize][];

        //
        //  Ok we start with the initial set as the first pos set of the
        //  head node (which is the seq node that holds the content model
        //  and the EOC node.)
        //
        CMStateSet setT = fHeadNode.firstPos();

        //
        //  Init our two state flags. Basically the unmarked state counter
        //  is always chasing the current state counter. When it catches up,
        //  that means we made a pass through that did not add any new states
        //  to the lists, at which time we are done. We could have used a
        //  expanding array of flags which we used to mark off states as we
        //  complete them, but this is easier though less readable maybe.
        //
        int unmarkedState = 0;
        int curState = 0;

        //
        //  Init the first transition table entry, and put the initial state
        //  into the states to do list, then bump the current state.
        //
        fTransTable[curState] = makeDefStateList();
        statesToDo[curState] = setT;
        curState++;

        /* Optimization(Jan, 2001); This is faster for
         * a large content model such as, "(t001+|t002+|.... |t500+)".
         */

        java.util.Hashtable stateTable = new java.util.Hashtable();

        /* Optimization(Jan, 2001) */

        //
        //  Ok, almost done with the algorithm... We now enter the
        //  loop where we go until the states done counter catches up with
        //  the states to do counter.
        //
        while (unmarkedState < curState) {
            //
            //  Get the first unmarked state out of the list of states to do.
            //  And get the associated transition table entry.
            //
            setT = statesToDo[unmarkedState];
            int[] transEntry = fTransTable[unmarkedState];

            // Mark this one final if it contains the EOC state
            fFinalStateFlags[unmarkedState] = setT.getBit(fEOCPos);

            // Bump up the unmarked state count, marking this state done
            unmarkedState++;

            // Loop through each possible input symbol in the element map
            CMStateSet newSet = null;
            /* Optimization(Jan, 2001) */
            int sorterIndex = 0;
            /* Optimization(Jan, 2001) */
            for (int elemIndex = 0; elemIndex < fElemMapSize; elemIndex++) {
                //
                //  Build up a set of states which is the union of all of
                //  the follow sets of DFA positions that are in the current
                //  state. If we gave away the new set last time through then
                //  create a new one. Otherwise, zero out the existing one.
                //
                if (newSet == null)
                    newSet = new CMStateSet(fLeafCount);
                else
                    newSet.zeroBits();

                /* Optimization(Jan, 2001) */
                int leafIndex = fLeafSorter[sorterIndex++];

                while (leafIndex != -1) {
                    // If this leaf index (DFA position) is in the current set...
                    if (setT.getBit(leafIndex)) {
                        //
                        //  If this leaf is the current input symbol, then we
                        //  want to add its follow list to the set of states to
                        //  transition to from the current state.
                        //
                        newSet.union(fFollowList[leafIndex]);
                    }

                   leafIndex = fLeafSorter[sorterIndex++];
                }
                /* Optimization(Jan, 2001) */

                //
                //  If this new set is not empty, then see if its in the list
                //  of states to do. If not, then add it.
                //
                if (!newSet.isEmpty()) {
                    //
                    //  Search the 'states to do' list to see if this new
                    //  state set is already in there.
                    //

                    /* Optimization(Jan, 2001) */
                    Integer stateObj = (Integer)stateTable.get(newSet);
                    int stateIndex = (stateObj == null ? curState : stateObj.intValue());
                    /* Optimization(Jan, 2001) */

                    // If we did not find it, then add it
                    if (stateIndex == curState) {
                        //
                        //  Put this new state into the states to do and init
                        //  a new entry at the same index in the transition
                        //  table.
                        //
                        statesToDo[curState] = newSet;
                        fTransTable[curState] = makeDefStateList();

                        /* Optimization(Jan, 2001) */
                        stateTable.put(newSet, new Integer(curState));
                        /* Optimization(Jan, 2001) */

                        // We now have a new state to do so bump the count
                        curState++;

                        //
                        //  Null out the new set to indicate we adopted it.
                        //  This will cause the creation of a new set on the
                        //  next time around the loop.
                        //
                        newSet = null;
                    }

                    //
                    //  Now set this state in the transition table's entry
                    //  for this element (using its index), with the DFA
                    //  state we will move to from the current state when we
                    //  see this input element.
                    //
                    transEntry[elemIndex] = stateIndex;

                    // Expand the arrays if we're full
                    if (curState == curArraySize) {
                        //
                        //  Yikes, we overflowed the initial array size, so
                        //  we've got to expand all of these arrays. So adjust
                        //  up the size by 50% and allocate new arrays.
                        //
                        final int newSize = (int)(curArraySize * 1.5);
                        CMStateSet[] newToDo = new CMStateSet[newSize];
                        boolean[] newFinalFlags = new boolean[newSize];
                        int[][] newTransTable = new int[newSize][];

                        // Copy over all of the existing content
                        for (int expIndex = 0; expIndex < curArraySize; expIndex++) {
                            newToDo[expIndex] = statesToDo[expIndex];
                            newFinalFlags[expIndex] = fFinalStateFlags[expIndex];
                            newTransTable[expIndex] = fTransTable[expIndex];
                        }

                        // Store the new array size
                        curArraySize = newSize;
                        statesToDo = newToDo;
                        fFinalStateFlags = newFinalFlags;
                        fTransTable = newTransTable;
                    }
                }
            }
        }

        // Check to see if we can set the fEmptyContentIsValid flag.
        fEmptyContentIsValid = ((XSCMBinOp)fHeadNode).getLeft().isNullable();

        //
        //  And now we can say bye bye to the temp representation since we've
        //  built the DFA.
        //
        if (DEBUG_VALIDATE_CONTENT)
            dumpTree(fHeadNode, 0);
        fHeadNode = null;
        fLeafList = null;
        fFollowList = null;

    }

    /**
     * Calculates the follow list of the current node.
     *
     * @param nodeCur The curent node.
     *
     * @exception RuntimeException Thrown if follow list cannot be calculated.
     */
    private void calcFollowList(CMNode nodeCur) {
        // Recurse as required
        if (nodeCur.type() == XSParticleDecl.PARTICLE_CHOICE) {
            // Recurse only
            calcFollowList(((XSCMBinOp)nodeCur).getLeft());
            calcFollowList(((XSCMBinOp)nodeCur).getRight());
        }
         else if (nodeCur.type() == XSParticleDecl.PARTICLE_SEQUENCE) {
            // Recurse first
            calcFollowList(((XSCMBinOp)nodeCur).getLeft());
            calcFollowList(((XSCMBinOp)nodeCur).getRight());

            //
            //  Now handle our level. We use our left child's last pos
            //  set and our right child's first pos set, so go ahead and
            //  get them ahead of time.
            //
            final CMStateSet last  = ((XSCMBinOp)nodeCur).getLeft().lastPos();
            final CMStateSet first = ((XSCMBinOp)nodeCur).getRight().firstPos();

            //
            //  Now, for every position which is in our left child's last set
            //  add all of the states in our right child's first set to the
            //  follow set for that position.
            //
            for (int index = 0; index < fLeafCount; index++) {
                if (last.getBit(index))
                    fFollowList[index].union(first);
            }
        }
         else if (nodeCur.type() == XSParticleDecl.PARTICLE_ZERO_OR_MORE
        || nodeCur.type() == XSParticleDecl.PARTICLE_ONE_OR_MORE) {
            // Recurse first
            calcFollowList(((XSCMUniOp)nodeCur).getChild());

            //
            //  Now handle our level. We use our own first and last position
            //  sets, so get them up front.
            //
            final CMStateSet first = nodeCur.firstPos();
            final CMStateSet last  = nodeCur.lastPos();

            //
            //  For every position which is in our last position set, add all
            //  of our first position states to the follow set for that
            //  position.
            //
            for (int index = 0; index < fLeafCount; index++) {
                if (last.getBit(index))
                    fFollowList[index].union(first);
            }
        }

        else if (nodeCur.type() == XSParticleDecl.PARTICLE_ZERO_OR_ONE) {
            // Recurse only
            calcFollowList(((XSCMUniOp)nodeCur).getChild());
        }

    }

    /**
     * Dumps the tree of the current node to standard output.
     *
     * @param nodeCur The current node.
     * @param level   The maximum levels to output.
     *
     * @exception RuntimeException Thrown on error.
     */
    private void dumpTree(CMNode nodeCur, int level) {
        for (int index = 0; index < level; index++)
            System.out.print("   ");

        int type = nodeCur.type();

        switch(type ) {

        case XSParticleDecl.PARTICLE_CHOICE:
        case XSParticleDecl.PARTICLE_SEQUENCE: {
            if (type == XSParticleDecl.PARTICLE_CHOICE)
                System.out.print("Choice Node ");
            else
                System.out.print("Seq Node ");

            if (nodeCur.isNullable())
                System.out.print("Nullable ");

            System.out.print("firstPos=");
            System.out.print(nodeCur.firstPos().toString());
            System.out.print(" lastPos=");
            System.out.println(nodeCur.lastPos().toString());

            dumpTree(((XSCMBinOp)nodeCur).getLeft(), level+1);
            dumpTree(((XSCMBinOp)nodeCur).getRight(), level+1);
            break;
        }
        case XSParticleDecl.PARTICLE_ZERO_OR_MORE:
        case XSParticleDecl.PARTICLE_ONE_OR_MORE:
        case XSParticleDecl.PARTICLE_ZERO_OR_ONE: {
            System.out.print("Rep Node ");

            if (nodeCur.isNullable())
                System.out.print("Nullable ");

            System.out.print("firstPos=");
            System.out.print(nodeCur.firstPos().toString());
            System.out.print(" lastPos=");
            System.out.println(nodeCur.lastPos().toString());

            dumpTree(((XSCMUniOp)nodeCur).getChild(), level+1);
            break;
        }
        case XSParticleDecl.PARTICLE_ELEMENT: {
            System.out.print
            (
                "Leaf: (pos="
                + ((XSCMLeaf)nodeCur).getPosition()
                + "), "
                + ((XSCMLeaf)nodeCur).getDecl()
                + "(elemIndex="
                + ((XSCMLeaf)nodeCur).getDecl()
                + ") "
            );

            if (nodeCur.isNullable())
                System.out.print(" Nullable ");

            System.out.print("firstPos=");
            System.out.print(nodeCur.firstPos().toString());
            System.out.print(" lastPos=");
            System.out.println(nodeCur.lastPos().toString());
            break;
        }
        case XSParticleDecl.PARTICLE_WILDCARD:
              System.out.print("Any Node: ");

            System.out.print("firstPos=");
            System.out.print(nodeCur.firstPos().toString());
            System.out.print(" lastPos=");
            System.out.println(nodeCur.lastPos().toString());
            break;
        default: {
            throw new RuntimeException("ImplementationMessages.VAL_NIICM");
        }
        }

    }


    /**
     * -1 is used to represent bad transitions in the transition table
     * entry for each state. So each entry is initialized to an all -1
     * array. This method creates a new entry and initializes it.
     */
    private int[] makeDefStateList()
    {
        int[] retArray = new int[fElemMapSize];
        for (int index = 0; index < fElemMapSize; index++)
            retArray[index] = -1;
        return retArray;
    }

    /** Post tree build initialization. */
    private int postTreeBuildInit(CMNode nodeCur, int curIndex) throws RuntimeException {
        // Set the maximum states on this node
        nodeCur.setMaxStates(fLeafCount);

        // Recurse as required
        if (nodeCur.type() == XSParticleDecl.PARTICLE_WILDCARD) {
            fElementDecl = ((XSCMLeaf)nodeCur).getDecl();
            fLeafList[curIndex] = (XSCMLeaf)nodeCur;
            fLeafListType[curIndex] = XSParticleDecl.PARTICLE_WILDCARD;
            curIndex++;
        }
        else if ((nodeCur.type() == XSParticleDecl.PARTICLE_CHOICE)
        ||  (nodeCur.type() == XSParticleDecl.PARTICLE_SEQUENCE))
        {
            curIndex = postTreeBuildInit(((XSCMBinOp)nodeCur).getLeft(), curIndex);
            curIndex = postTreeBuildInit(((XSCMBinOp)nodeCur).getRight(), curIndex);
        }
         else if (nodeCur.type() == XSParticleDecl.PARTICLE_ZERO_OR_MORE
         || nodeCur.type() == XSParticleDecl.PARTICLE_ONE_OR_MORE
         || nodeCur.type() == XSParticleDecl.PARTICLE_ZERO_OR_ONE)
        {
            curIndex = postTreeBuildInit(((XSCMUniOp)nodeCur).getChild(), curIndex);
        }
         else if (nodeCur.type() == XSParticleDecl.PARTICLE_ELEMENT) {
            //
            //  Put this node in the leaf list at the current index if its
            //  a non-epsilon leaf.
            //
            final XSElementDecl elementDecl = (XSElementDecl)((XSCMLeaf)nodeCur).getDecl();
            if (elementDecl.fName != fEpsilonString) {
                fLeafList[curIndex] = (XSCMLeaf)nodeCur;
                fLeafListType[curIndex] = XSParticleDecl.PARTICLE_ELEMENT;
                curIndex++;
            }
        }
         else
        {
            throw new RuntimeException("ImplementationMessages.VAL_NIICM");
        }
        return curIndex;
    }


} // class DFAContentModel