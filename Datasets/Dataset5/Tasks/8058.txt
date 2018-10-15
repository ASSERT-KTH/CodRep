throw new RuntimeException("org.apache.xerces.utils.regex.Token#getRange(): Unknown Unicode category: "+type);

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

package org.apache.xerces.utils.regex;

import java.util.Vector;
import java.util.Hashtable;

/**
 * This class represents a node in parse tree.
 */
class Token implements java.io.Serializable {
    static final boolean COUNTTOKENS = true;
    static int tokens = 0;

    static final int CHAR = 0;                  // Literal char
    static final int DOT = 11;                  // .
    static final int CONCAT = 1;                // XY
    static final int UNION = 2;                 // X|Y|Z
    static final int CLOSURE = 3;               // X*
    static final int RANGE = 4;                 // [a-zA-Z] etc.
    static final int NRANGE = 5;                // [^a-zA-Z] etc.
    static final int PAREN = 6;                 // (X) or (?:X)
    static final int EMPTY = 7;                 //
    static final int ANCHOR = 8;                // ^ $ \b \B \< \> \A \Z \z
    static final int NONGREEDYCLOSURE = 9;      // *? +?
    static final int STRING = 10;               // strings
    static final int BACKREFERENCE = 12;        // back references
    static final int LOOKAHEAD = 20;            // (?=...)
    static final int NEGATIVELOOKAHEAD = 21;    // (?!...)
    static final int LOOKBEHIND = 22;           // (?<=...)
    static final int NEGATIVELOOKBEHIND = 23;   // (?<!...)
    static final int INDEPENDENT = 24;          // (?>...)
    static final int MODIFIERGROUP = 25;        // (?ims-ims:...)
    static final int CONDITION = 26;            // (?(...)yes|no)

    static final int UTF16_MAX = 0x10ffff;

    int type;

    static protected Token token_dot;
    static protected Token token_0to9;
    static protected Token token_wordchars;
    static protected Token token_not_0to9;
    static protected Token token_not_wordchars;
    static protected Token token_spaces;
    static protected Token token_not_spaces;
    static protected Token token_empty;
    static protected Token token_linebeginning;
    static protected Token token_linebeginning2;
    static protected Token token_lineend;
    static protected Token token_stringbeginning;
    static protected Token token_stringend;
    static protected Token token_stringend2;
    static protected Token token_wordedge;
    static protected Token token_not_wordedge;
    static protected Token token_wordbeginning;
    static protected Token token_wordend;
    static {
        Token.token_empty = new Token(Token.EMPTY);

        Token.token_linebeginning = Token.createAnchor('^');
        Token.token_linebeginning2 = Token.createAnchor('@');
        Token.token_lineend = Token.createAnchor('$');
        Token.token_stringbeginning = Token.createAnchor('A');
        Token.token_stringend = Token.createAnchor('z');
        Token.token_stringend2 = Token.createAnchor('Z');
        Token.token_wordedge = Token.createAnchor('b');
        Token.token_not_wordedge = Token.createAnchor('B');
        Token.token_wordbeginning = Token.createAnchor('<');
        Token.token_wordend = Token.createAnchor('>');

        Token.token_dot = new Token(Token.DOT);

        Token.token_0to9 = Token.createRange();
        Token.token_0to9.addRange('0', '9');
        Token.token_wordchars = Token.createRange();
        Token.token_wordchars.addRange('0', '9');
        Token.token_wordchars.addRange('A', 'Z');
        Token.token_wordchars.addRange('_', '_');
        Token.token_wordchars.addRange('a', 'z');
        Token.token_spaces = Token.createRange();
        Token.token_spaces.addRange('\t', '\t');
        Token.token_spaces.addRange('\n', '\n');
        Token.token_spaces.addRange('\f', '\f');
        Token.token_spaces.addRange('\r', '\r');
        Token.token_spaces.addRange(' ', ' ');

        Token.token_not_0to9 = Token.complementRanges(Token.token_0to9);
        Token.token_not_wordchars = Token.complementRanges(Token.token_wordchars);
        Token.token_not_spaces = Token.complementRanges(Token.token_spaces);
    }

    static Token.ParenToken createLook(int type, Token child) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.ParenToken(type, child, 0);
    }
    static Token.ParenToken createParen(Token child, int pnumber) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.ParenToken(Token.PAREN, child, pnumber);
    }
    static Token.ClosureToken createClosure(Token tok) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.ClosureToken(Token.CLOSURE, tok);
    }
    static Token.ClosureToken createNGClosure(Token tok) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.ClosureToken(Token.NONGREEDYCLOSURE, tok);
    }
    static Token.ConcatToken createConcat(Token tok1, Token tok2) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.ConcatToken(tok1, tok2);
    }
    static Token.UnionToken createConcat() {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.UnionToken(Token.CONCAT); // *** It is not a bug.
    }
    static Token.UnionToken createUnion() {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.UnionToken(Token.UNION);
    }
    static Token createEmpty() {
        return Token.token_empty;
    }
    static RangeToken createRange() {
        if (COUNTTOKENS)  Token.tokens ++;
        return new RangeToken(Token.RANGE);
    }
    static RangeToken createNRange() {
        if (COUNTTOKENS)  Token.tokens ++;
        return new RangeToken(Token.NRANGE);
    }
    static Token.CharToken createChar(int ch) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.CharToken(Token.CHAR, ch);
    }
    static private Token.CharToken createAnchor(int ch) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.CharToken(Token.ANCHOR, ch);
    }
    static Token.StringToken createBackReference(int refno) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.StringToken(Token.BACKREFERENCE, null, refno);
    }
    static Token.StringToken createString(String str) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.StringToken(Token.STRING, str, 0);
    }
    static Token.ModifierToken createModifierGroup(Token child, int add, int mask) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.ModifierToken(child, add, mask);
    }
    static Token.ConditionToken createCondition(int refno, Token condition,
                                                Token yespat, Token nopat) {
        if (COUNTTOKENS)  Token.tokens ++;
        return new Token.ConditionToken(refno, condition, yespat, nopat);
    }

    protected Token(int type) {
        this.type = type;
    }

    /**
     * A number of children.
     */
    int size() {
        return 0;
    }
    Token getChild(int index) {
        return null;
    }
    void addChild(Token tok) {
        throw new RuntimeException("Not supported.");
    }

                                                // for RANGE or NRANGE
    protected void addRange(int start, int end) {
        throw new RuntimeException("Not supported.");
    }
    protected void sortRanges() {
        throw new RuntimeException("Not supported.");
    }
    protected void compactRanges() {
        throw new RuntimeException("Not supported.");
    }
    protected void mergeRanges(Token tok) {
        throw new RuntimeException("Not supported.");
    }
    protected void subtractRanges(Token tok) {
        throw new RuntimeException("Not supported.");
    }
    protected void intersectRanges(Token tok) {
        throw new RuntimeException("Not supported.");
    }
    static Token complementRanges(Token tok) {
        return RangeToken.complementRanges(tok);
    }


    void setMin(int min) {                      // for CLOSURE
    }
    void setMax(int max) {                      // for CLOSURE
    }
    int getMin() {                              // for CLOSURE
        return -1;
    }
    int getMax() {                              // for CLOSURE
        return -1;
    }
    int getReferenceNumber() {                  // for STRING
        return 0;
    }
    String getString() {                        // for STRING
        return null;
    }

    int getParenNumber() {
        return 0;
    }
    int getChar() {
        return -1;
    }

    public String toString() {
        return this.type == Token.DOT ? "." : "";
    }

    /**
     * How many characters are needed?
     */
    final int getMinLength() {
        switch (this.type) {
          case CONCAT:
            int sum = 0;
            for (int i = 0;  i < this.size();  i ++)
                sum += this.getChild(i).getMinLength();
            return sum;

          case CONDITION:
          case UNION:
            if (this.size() == 0)
                return 0;
            int ret = this.getChild(0).getMinLength();
            for (int i = 1;  i < this.size();  i ++) {
                int min = this.getChild(i).getMinLength();
                if (min < ret)  ret = min;
            }
            return ret;

          case CLOSURE:
          case NONGREEDYCLOSURE:
            if (this.getMin() >= 0)
                return this.getMin() * this.getChild(0).getMinLength();
            return 0;

          case EMPTY:
          case ANCHOR:
            return 0;

          case DOT:
          case CHAR:
          case RANGE:
          case NRANGE:
            return 1;

          case INDEPENDENT:
          case PAREN:
          case MODIFIERGROUP:
            return this.getChild(0).getMinLength();

          case BACKREFERENCE:
            return 0;                           // *******

          case STRING:
            return this.getString().length();

          case LOOKAHEAD:
          case NEGATIVELOOKAHEAD:
          case LOOKBEHIND:
          case NEGATIVELOOKBEHIND:
            return 0;                           // ***** Really?

          default:
            throw new RuntimeException("Token#getMinLength(): Invalid Type: "+this.type);
        }
    }

    final int getMaxLength() {
        switch (this.type) {
          case CONCAT:
            int sum = 0;
            for (int i = 0;  i < this.size();  i ++) {
                int d = this.getChild(i).getMaxLength();
                if (d < 0)  return -1;
                sum += d;
            }
            return sum;

          case CONDITION:
          case UNION:
            if (this.size() == 0)
                return 0;
            int ret = this.getChild(0).getMaxLength();
            for (int i = 1;  ret >= 0 && i < this.size();  i ++) {
                int max = this.getChild(i).getMaxLength();
                if (max < 0) {                  // infinity
                    ret = -1;
                    break;
                }
                if (max > ret)  ret = max;
            }
            return ret;

          case CLOSURE:
          case NONGREEDYCLOSURE:
            if (this.getMax() >= 0)
                                                // When this.child.getMaxLength() < 0,
                                                // this returns minus value
                return this.getMax() * this.getChild(0).getMaxLength();
            return -1;

          case EMPTY:
          case ANCHOR:
            return 0;

          case CHAR:
            return 1;
          case DOT:
          case RANGE:
          case NRANGE:
            return 2;

          case INDEPENDENT:
          case PAREN:
          case MODIFIERGROUP:
            return this.getChild(0).getMaxLength();

          case BACKREFERENCE:
            return -1;                          // ******

          case STRING:
            return this.getString().length();

          case LOOKAHEAD:
          case NEGATIVELOOKAHEAD:
          case LOOKBEHIND:
          case NEGATIVELOOKBEHIND:
            return 0;                           // ***** Really?

          default:
            throw new RuntimeException("Token#getMaxLength(): Invalid Type: "+this.type);
        }
    }

    static final int FC_CONTINUE = 0;
    static final int FC_TERMINAL = 1;
    static final int FC_ANY = 2;
    private static final boolean isSet(int options, int flag) {
        return (options & flag) == flag;
    }
    final int analyzeFirstCharacter(RangeToken result, int options) {
        switch (this.type) {
          case CONCAT:
            int ret = FC_CONTINUE;
            for (int i = 0;  i < this.size();  i ++)
                if ((ret = this.getChild(i).analyzeFirstCharacter(result, options)) != FC_CONTINUE)
                    break;
            return ret;

          case UNION:
            if (this.size() == 0)
                return FC_CONTINUE;
            /*
             *  a|b|c -> FC_TERMINAL
             *  a|.|c -> FC_ANY
             *  a|b|  -> FC_CONTINUE
             */
            int ret2 = FC_CONTINUE;
            boolean hasEmpty = false;
            for (int i = 0;  i < this.size();  i ++) {
                ret2 = this.getChild(i).analyzeFirstCharacter(result, options);
                if (ret2 == FC_ANY)
                    break;
                else if (ret2 == FC_CONTINUE)
                    hasEmpty = true;
            }
            return hasEmpty ? FC_CONTINUE : ret2;

          case CONDITION:
            int ret3 = this.getChild(0).analyzeFirstCharacter(result, options);
            if (this.size() == 1)  return FC_CONTINUE;
            if (ret3 == FC_ANY)  return ret3;
            int ret4 = this.getChild(1).analyzeFirstCharacter(result, options);
            if (ret4 == FC_ANY)  return ret4;
            return ret3 == FC_CONTINUE || ret4 == FC_CONTINUE ? FC_CONTINUE : FC_TERMINAL;

          case CLOSURE:
          case NONGREEDYCLOSURE:
            this.getChild(0).analyzeFirstCharacter(result, options);
            return FC_CONTINUE;

          case EMPTY:
          case ANCHOR:
            return FC_CONTINUE;

          case CHAR:
            int ch = this.getChar();
            result.addRange(ch, ch);
            if (ch < 0x10000 && isSet(options, RegularExpression.IGNORE_CASE)) {
                ch = Character.toUpperCase((char)ch);
                result.addRange(ch, ch);
                ch = Character.toLowerCase((char)ch);
                result.addRange(ch, ch);
            }
            return FC_TERMINAL;

          case DOT:                             // ****
            if (isSet(options, RegularExpression.SINGLE_LINE)) {
                return FC_CONTINUE;             // **** We can not optimize.
            } else {
                return FC_CONTINUE;
                /*
                result.addRange(0, RegularExpression.LINE_FEED-1);
                result.addRange(RegularExpression.LINE_FEED+1, RegularExpression.CARRIAGE_RETURN-1);
                result.addRange(RegularExpression.CARRIAGE_RETURN+1,
                                RegularExpression.LINE_SEPARATOR-1);
                result.addRange(RegularExpression.PARAGRAPH_SEPARATOR+1, UTF16_MAX);
                return 1;
                */
            }

          case RANGE:
            if (isSet(options, RegularExpression.IGNORE_CASE)) {
                result.mergeRanges(((RangeToken)this).getCaseInsensitiveToken());
            } else {
                result.mergeRanges(this);
            }
            return FC_TERMINAL;

          case NRANGE:                          // ****
            if (isSet(options, RegularExpression.IGNORE_CASE)) {
                result.mergeRanges(Token.complementRanges(((RangeToken)this).getCaseInsensitiveToken()));
            } else {
                result.mergeRanges(Token.complementRanges(this));
            }
            return FC_TERMINAL;

          case INDEPENDENT:
          case PAREN:
            return this.getChild(0).analyzeFirstCharacter(result, options);

          case MODIFIERGROUP:
            options |= ((ModifierToken)this).getOptions();
            options &= ~((ModifierToken)this).getOptionsMask();
            return this.getChild(0).analyzeFirstCharacter(result, options);

          case BACKREFERENCE:
            result.addRange(0, UTF16_MAX);  // **** We can not optimize.
            return FC_ANY;

          case STRING:
            int cha = this.getString().charAt(0);
            int ch2;
            if (REUtil.isHighSurrogate(cha)
                && this.getString().length() >= 2
                && REUtil.isLowSurrogate((ch2 = this.getString().charAt(1))))
                cha = REUtil.composeFromSurrogates(cha, ch2);
            result.addRange(cha, cha);
            if (cha < 0x10000 && isSet(options, RegularExpression.IGNORE_CASE)) {
                cha = Character.toUpperCase((char)cha);
                result.addRange(cha, cha);
                cha = Character.toLowerCase((char)cha);
                result.addRange(cha, cha);
            }
            return FC_TERMINAL;

          case LOOKAHEAD:
          case NEGATIVELOOKAHEAD:
          case LOOKBEHIND:
          case NEGATIVELOOKBEHIND:
            return FC_CONTINUE;

          default:
            throw new RuntimeException("Token#analyzeHeadCharacter(): Invalid Type: "+this.type);
        }
    }

    private final boolean isShorterThan(Token tok) {
        if (tok == null)  return false;
        /*
        int mylength;
        if (this.type == STRING)  mylength = this.getString().length();
        else if (this.type == CHAR)  mylength = this.getChar() >= 0x10000 ? 2 : 1;
        else throw new RuntimeException("Internal Error: Illegal type: "+this.type);
        int otherlength;
        if (tok.type == STRING)  otherlength = tok.getString().length();
        else if (tok.type == CHAR)  otherlength = tok.getChar() >= 0x10000 ? 2 : 1;
        else throw new RuntimeException("Internal Error: Illegal type: "+tok.type);
        */
        int mylength;
        if (this.type == STRING)  mylength = this.getString().length();
        else throw new RuntimeException("Internal Error: Illegal type: "+this.type);
        int otherlength;
        if (tok.type == STRING)  otherlength = tok.getString().length();
        else throw new RuntimeException("Internal Error: Illegal type: "+tok.type);
        return mylength < otherlength;
    }

    static class FixedStringContainer {
        Token token = null;
        int options = 0;
        FixedStringContainer() {
        }
    }

    final void findFixedString(FixedStringContainer container, int options) {
        switch (this.type) {
          case CONCAT:
            Token prevToken = null;
            int prevOptions = 0;
            for (int i = 0;  i < this.size();  i ++) {
                this.getChild(i).findFixedString(container, options);
                if (prevToken == null || prevToken.isShorterThan(container.token)) {
                    prevToken = container.token;
                    prevOptions = container.options;
                }
            }
            container.token = prevToken;
            container.options = prevOptions;
            return;

          case UNION:
          case CLOSURE:
          case NONGREEDYCLOSURE:
          case EMPTY:
          case ANCHOR:
          case RANGE:
          case DOT:
          case NRANGE:
          case BACKREFERENCE:
          case LOOKAHEAD:
          case NEGATIVELOOKAHEAD:
          case LOOKBEHIND:
          case NEGATIVELOOKBEHIND:
          case CONDITION:
            container.token = null;
            return;

          case CHAR:                            // Ignore CHAR tokens.
            container.token = null;             // **
            return;                             // **

          case STRING:
            container.token = this;
            container.options = options;
            return;

          case INDEPENDENT:
          case PAREN:
            this.getChild(0).findFixedString(container, options);
            return;

          case MODIFIERGROUP:
            options |= ((ModifierToken)this).getOptions();
            options &= ~((ModifierToken)this).getOptionsMask();
            this.getChild(0).findFixedString(container, options);
            return;

          default:
            throw new RuntimeException("Token#findFixedString(): Invalid Type: "+this.type);
        }
    }

    boolean match(int ch) {
        throw new RuntimeException("NFAArrow#match(): Internal error: "+this.type);
    }

    // ------------------------------------------------------
    static protected Hashtable categories = new Hashtable();
    static protected Hashtable categories2 = null;
    static final String[] categoryNames = {
        "Cn", "Lu", "Ll", "Lt", "Lm", "Lo", "Mn", "Me", "Mc", "Nd",
        "Nl", "No", "Zs", "Zl", "Zp", "Cc", "Cf", null, "Co", "Cs",
        "Pd", "Ps", "Pe", "Pc", "Po", "Sm", "Sc", "Sk", "So", // 28
        "L", "M", "N", "Z", "C", "P", "S",      // 29-35
    };
    static final int CHAR_LETTER = 29;
    static final int CHAR_MARK = 30;
    static final int CHAR_NUMBER = 31;
    static final int CHAR_SEPARATOR = 32;
    static final int CHAR_OTHER = 33;
    static final int CHAR_PUNCTUATION = 34;
    static final int CHAR_SYMBOL = 35;
    static final String[] blockNames = {
        "Basic Latin",                          // 0
        "Latin-1 Supplement",
        "Latin Extended-A",
        "Latin Extended-B",
        "IPA Extensions",
        "Spacing Modifier Letters",
        "Combining Diacritical Marks",
        "Greek",
        "Cyrillic",                             // 8
        "Armenian",
        "Hebrew",
        "Arabic",
        "Devanagari",
        "Bengali",
        "Gurmukhi",
        "Gujarati",
        "Oriya",                                // 16
        "Tamil",
        "Telugu",
        "Kannada",
        "Malayalam",
        "Thai",
        "Lao",
        "Tibetan",
        "Georgian",                             // 24
        "Hangul Jamo",
        "Latin Extended Additional",
        "Greek Extended",
        "General Punctuation",
        "Superscripts and Subscripts",
        "Currency Symbols",
        "Combining Marks for Symbols",
        "Letterlike Symbols",                   // 32
        "Number Forms",
        "Arrows",
        "Mathematical Operators",
        "Miscellaneous Technical",
        "Control Pictures",
        "Optical Character Recognition",
        "Enclosed Alphanumerics",
        "Box Drawing",                          // 40
        "Block Elements",
        "Geometric Shapes",
        "Miscellaneous Symbols",
        "Dingbats",
        "CJK Symbols and Punctuation",
        "Hiragana",
        "Katakana",
        "Bopomofo",                             // 48
        "Hangul Compatibility Jamo",
        "Kanbun",
        "Enclosed CJK Letters and Months",
        "CJK Compatibility",
        "CJK Unified Ideographs",
        "Hangul Syllables",
        "High Surrogates",
        "High Private Use Surrogates",          // 56
        "Low Surrogates",
        "Private Use",
        "CJK Compatibility Ideographs",
        "Alphabetic Presentation Forms",
        "Arabic Presentation Forms-A",
        "Combining Half Marks",
        "CJK Compatibility Forms",
        "Small Form Variants",                  // 64
        "Arabic Presentation Forms-B",
        "Specials",
        "Halfwidth and Fullwidth Forms",        // 67
    };
    static final String blockRanges =
    "\u0000\u007F\u0080\u00FF\u0100\u017F\u0180\u024F\u0250\u02AF\u02B0\u02FF"
    +"\u0300\u036F\u0370\u03FF\u0400\u04FF\u0530\u058F\u0590\u05FF\u0600\u06FF"
    +"\u0900\u097F\u0980\u09FF\u0A00\u0A7F\u0A80\u0AFF\u0B00\u0B7F\u0B80\u0BFF"
    +"\u0C00\u0C7F\u0C80\u0CFF\u0D00\u0D7F\u0E00\u0E7F\u0E80\u0EFF\u0F00\u0FBF"
    +"\u10A0\u10FF\u1100\u11FF\u1E00\u1EFF\u1F00\u1FFF\u2000\u206F\u2070\u209F"
    +"\u20A0\u20CF\u20D0\u20FF\u2100\u214F\u2150\u218F\u2190\u21FF\u2200\u22FF"
    +"\u2300\u23FF\u2400\u243F\u2440\u245F\u2460\u24FF\u2500\u257F\u2580\u259F"
    +"\u25A0\u25FF\u2600\u26FF\u2700\u27BF\u3000\u303F\u3040\u309F\u30A0\u30FF"
    +"\u3100\u312F\u3130\u318F\u3190\u319F\u3200\u32FF\u3300\u33FF\u4E00\u9FFF"
    +"\uAC00\uD7A3\uD800\uDB7F\uDB80\uDBFF\uDC00\uDFFF\uE000\uF8FF\uF900\uFAFF"
    +"\uFB00\uFB4F\uFB50\uFDFF\uFE20\uFE2F\uFE30\uFE4F\uFE50\uFE6F\uFE70\uFEFE"
    +"\uFEFF\uFEFF\uFF00\uFFEF";

    static protected RangeToken getRange(String name, boolean positive) {
        if (Token.categories.size() == 0) {
            synchronized (Token.categories) {
                Token[] ranges = new Token[Token.categoryNames.length];
                for (int i = 0;  i < ranges.length;  i ++) {
                    ranges[i] = Token.createRange();
                }
                for (int i = 0;  i < 0x10000;  i ++) {
                    int type = Character.getType((char)i);
                    ranges[type].addRange(i, i);
                    switch (type) {
                      case Character.UPPERCASE_LETTER:
                      case Character.LOWERCASE_LETTER:
                      case Character.TITLECASE_LETTER:
                      case Character.MODIFIER_LETTER:
                      case Character.OTHER_LETTER:
                        type = CHAR_LETTER;
                        break;
                      case Character.NON_SPACING_MARK:
                      case Character.COMBINING_SPACING_MARK:
                      case Character.ENCLOSING_MARK:
                        type = CHAR_MARK;
                        break;
                      case Character.DECIMAL_DIGIT_NUMBER:
                      case Character.LETTER_NUMBER:
                      case Character.OTHER_NUMBER:
                        type = CHAR_NUMBER;
                        break;
                      case Character.SPACE_SEPARATOR:
                      case Character.LINE_SEPARATOR:
                      case Character.PARAGRAPH_SEPARATOR:
                        type = CHAR_SEPARATOR;
                        break;
                      case Character.CONTROL:
                      case Character.FORMAT:
                      case Character.SURROGATE:
                      case Character.PRIVATE_USE:
                      case Character.UNASSIGNED:
                        type = CHAR_OTHER;
                        break;
                      case Character.CONNECTOR_PUNCTUATION:
                      case Character.DASH_PUNCTUATION:
                      case Character.START_PUNCTUATION:
                      case Character.END_PUNCTUATION:
                      case Character.OTHER_PUNCTUATION:
                        type = CHAR_PUNCTUATION;
                        break;
                      case Character.MATH_SYMBOL:
                      case Character.CURRENCY_SYMBOL:
                      case Character.MODIFIER_SYMBOL:
                      case Character.OTHER_SYMBOL:
                        type = CHAR_SYMBOL;
                        break;
                      default:
                        throw new RuntimeException("com.ibm.regex.Token#getRange(): Unknown Unicode category: "+type);
                    }
                    ranges[type].addRange(i, i);
                } // for all characters
                ranges[Character.UNASSIGNED].addRange(0x10000, Token.UTF16_MAX);

                Token.categories2 = new Hashtable();
                for (int i = 0;  i < ranges.length;  i ++) {
                    if (Token.categoryNames[i] != null) {
                        if (i == Character.UNASSIGNED) { // Unassigned
                            ranges[i].addRange(0x10000, Token.UTF16_MAX);
                        }
                        Token.categories.put(Token.categoryNames[i], ranges[i]);
                        Token.categories2.put(Token.categoryNames[i],
                                              Token.complementRanges(ranges[i]));
                    }
                }
                for (int i = 0;  i < Token.blockNames.length;  i ++) {
                    Token r1 = Token.createRange();
                    int rstart = Token.blockRanges.charAt(i*2);
                    int rend = Token.blockRanges.charAt(i*2+1);
                    String n = Token.blockNames[i];
                    r1.addRange(rstart, rend);
                    if (n.equals("Specials"))
                        r1.addRange(0xfff0, 0xfffd);
                    Token.categories.put(n, r1);
                    Token.categories2.put(n, Token.complementRanges(r1));
                    if (n.indexOf(' ') >= 0) {
                        StringBuffer buffer = new StringBuffer(n.length());
                        for (int ci = 0;  ci < n.length();  ci ++)
                            if (n.charAt(ci) != ' ')  buffer.append((char)n.charAt(ci));
                        Token.setAlias(buffer.toString(), n, true);
                    }
                }

                                                // TR#18 1.2
                Token.setAlias("ASSIGNED", "Cn", false);
                Token.setAlias("UNASSIGNED", "Cn", true);
                Token all = Token.createRange();
                all.addRange(0, Token.UTF16_MAX);
                Token.categories.put("ALL", all);
                Token.categories2.put("ALL", Token.complementRanges(all));

                Token isalpha = Token.createRange();
                isalpha.mergeRanges(ranges[Character.UPPERCASE_LETTER]); // Lu
                isalpha.mergeRanges(ranges[Character.LOWERCASE_LETTER]); // Ll
                isalpha.mergeRanges(ranges[Character.OTHER_LETTER]); // Lo
                Token.categories.put("IsAlpha", isalpha);
                Token.categories2.put("IsAlpha", Token.complementRanges(isalpha));

                Token isalnum = Token.createRange();
                isalnum.mergeRanges(isalpha);   // Lu Ll Lo
                isalnum.mergeRanges(ranges[Character.DECIMAL_DIGIT_NUMBER]); // Nd
                Token.categories.put("IsAlnum", isalnum);
                Token.categories2.put("IsAlnum", Token.complementRanges(isalnum));

                Token isspace = Token.createRange();
                isspace.mergeRanges(Token.token_spaces);
                isspace.mergeRanges(ranges[CHAR_SEPARATOR]); // Z
                Token.categories.put("IsSpace", isspace);
                Token.categories2.put("IsSpace", Token.complementRanges(isspace));

                Token isword = Token.createRange();
                isword.mergeRanges(isalnum);     // Lu Ll Lo Nd
                isword.addRange('_', '_');
                Token.categories.put("IsWord", isword);
                Token.categories2.put("IsWord", Token.complementRanges(isword));

                Token isascii = Token.createRange();
                isascii.addRange(0, 127);
                Token.categories.put("IsASCII", isascii);
                Token.categories2.put("IsASCII", Token.complementRanges(isascii));

                Token isnotgraph = Token.createRange();
                isnotgraph.mergeRanges(ranges[CHAR_OTHER]);
                isnotgraph.addRange(' ', ' ');
                Token.categories.put("IsGraph", Token.complementRanges(isnotgraph));
                Token.categories2.put("IsGraph", isnotgraph);

                Token isxdigit = Token.createRange();
                isxdigit.addRange('0', '9');
                isxdigit.addRange('A', 'F');
                isxdigit.addRange('a', 'f');
                Token.categories.put("IsXDigit", Token.complementRanges(isxdigit));
                Token.categories2.put("IsXDigit", isxdigit);
                
                Token.setAlias("IsDigit", "Nd", true);
                Token.setAlias("IsUpper", "Lu", true);
                Token.setAlias("IsLower", "Ll", true);
                Token.setAlias("IsCntrl", "C", true);
                Token.setAlias("IsPrint", "C", false);
                Token.setAlias("IsPunct", "P", true);

                Token.setAlias("alpha", "IsAlpha", true);
                Token.setAlias("alnum", "IsAlnum", true);
                Token.setAlias("ascii", "IsASCII", true);
                Token.setAlias("cntrl", "IsCntrl", true);
                Token.setAlias("digit", "IsDigit", true);
                Token.setAlias("graph", "IsGraph", true);
                Token.setAlias("lower", "IsLower", true);
                Token.setAlias("print", "IsPrint", true);
                Token.setAlias("punct", "IsPunct", true);
                Token.setAlias("space", "IsSpace", true);
                Token.setAlias("upper", "IsUpper", true);
                Token.setAlias("word", "IsWord", true); // Perl extension
                Token.setAlias("xdigit", "IsXDigit", true);

            } // synchronized
        } // if null
        RangeToken tok = positive ? (RangeToken)Token.categories.get(name)
            : (RangeToken)Token.categories2.get(name);
        return tok;
    }

    private static void setAlias(String newName, String name, boolean positive) {
        Token t1 = (Token)Token.categories.get(name);
        Token t2 = (Token)Token.categories2.get(name);
        if (positive) {
            Token.categories.put(newName, t1);
            Token.categories2.put(newName, t2);
        } else {
            Token.categories2.put(newName, t1);
            Token.categories.put(newName, t2);
        }
    }

    // ------------------------------------------------------

    static final String viramaString =
    "\u094D"// ;DEVANAGARI SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u09CD"//;BENGALI SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0A4D"//;GURMUKHI SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0ACD"//;GUJARATI SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0B4D"//;ORIYA SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0BCD"//;TAMIL SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0C4D"//;TELUGU SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0CCD"//;KANNADA SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0D4D"//;MALAYALAM SIGN VIRAMA;Mn;9;ON;;;;;N;;;;;
    +"\u0E3A"//;THAI CHARACTER PHINTHU;Mn;9;ON;;;;;N;THAI VOWEL SIGN PHINTHU;;;;
    +"\u0F84";//;TIBETAN MARK HALANTA;Mn;9;ON;;;;;N;TIBETAN VIRAMA;;;;

    static private Token token_grapheme = null;
    static synchronized protected Token getGraphemePattern() {
        if (Token.token_grapheme != null)
            return Token.token_grapheme;

        Token base_char = Token.createRange();  // [{ASSIGNED}]-[{M},{C}]
        base_char.mergeRanges(Token.getRange("ASSIGNED", true));
        base_char.subtractRanges(Token.getRange("M", true));
        base_char.subtractRanges(Token.getRange("C", true));

        Token virama = Token.createRange();
        for (int i = 0;  i < Token.viramaString.length();  i ++) {
            int ch = viramaString.charAt(i);
            virama.addRange(i, i);
        }

        Token combiner_wo_virama = Token.createRange();
        combiner_wo_virama.mergeRanges(Token.getRange("M", true));
        combiner_wo_virama.addRange(0x1160, 0x11ff); // hangul_medial and hangul_final
        combiner_wo_virama.addRange(0xff9e, 0xff9f); // extras

        Token left = Token.createUnion();       // base_char?
        left.addChild(base_char);
        left.addChild(Token.token_empty);

        Token foo = Token.createUnion();
        foo.addChild(Token.createConcat(virama, Token.getRange("L", true)));
        foo.addChild(combiner_wo_virama);

        foo = Token.createClosure(foo);

        foo = Token.createConcat(left, foo);

        Token.token_grapheme = foo;
        return Token.token_grapheme;
    }

    // ------------------------------------------------------

    // ------------------------------------------------------
    /**
     * This class represents a node in parse tree.
     */
    static class StringToken extends Token implements java.io.Serializable {
        String string;
        int refNumber;

        StringToken(int type, String str, int n) {
            super(type);
            this.string = str;
            this.refNumber = n;
        }

        int getReferenceNumber() {              // for STRING
            return this.refNumber;
        }
        String getString() {                    // for STRING
            return this.string;
        }
        
        public String toString() {
            if (this.type == BACKREFERENCE)
                return "\\"+this.refNumber;
            else
                return REUtil.quoteMeta(this.string);
        }
    }

    /**
     * This class represents a node in parse tree.
     */
    static class ConcatToken extends Token implements java.io.Serializable {
        Token child;
        Token child2;
        
        ConcatToken(Token t1, Token t2) {
            super(Token.CONCAT);
            this.child = t1;
            this.child2 = t2;
        }

        int size() {
            return 2;
        }
        Token getChild(int index) {
            return index == 0 ? this.child : this.child2;
        }

        public String toString() {
            String ret;
            if (this.child2.type == CLOSURE && this.child2.getChild(0) == this.child) {
                ret = this.child.toString()+"+";
            } else if (this.child2.type == NONGREEDYCLOSURE && this.child2.getChild(0) == this.child) {
                ret = this.child.toString()+"+?";
            } else
                ret = this.child.toString()+this.child2.toString();
            return ret;
        }
    }

    /**
     * This class represents a node in parse tree.
     */
    static class CharToken extends Token implements java.io.Serializable {
        int chardata;

        CharToken(int type, int ch) {
            super(type);
            this.chardata = ch;
        }

        int getChar() {
            return this.chardata;
        }

        public String toString() {
            String ret;
            switch (this.type) {
              case CHAR:
                switch (this.chardata) {
                  case '|':  case '*':  case '+':  case '?':
                  case '(':  case ')':  case '.':  case '[':
                  case '{':  case '\\':
                    ret = "\\"+(char)this.chardata;
                    break;
                  case '\f':  ret = "\\f";  break;
                  case '\n':  ret = "\\n";  break;
                  case '\r':  ret = "\\r";  break;
                  case '\t':  ret = "\\t";  break;
                  case 0x1b:  ret = "\\e";  break;
                    //case 0x0b:  ret = "\\v";  break;
                  default:
                    if (this.chardata >= 0x10000) {
                        String pre = "0"+Integer.toHexString(this.chardata);
                        ret = "\\v"+pre.substring(pre.length()-6, pre.length());
                    } else
                        ret = ""+(char)this.chardata;
                }
                break;

              case ANCHOR:
                if (this == Token.token_linebeginning || this == Token.token_lineend)
                    ret = ""+(char)this.chardata;
                else 
                    ret = "\\"+(char)this.chardata;
                break;

              default:
                ret = null;
            }
            return ret;
        }

        boolean match(int ch) {
            if (this.type == CHAR) {
                return ch == this.chardata;
            } else
                throw new RuntimeException("NFAArrow#match(): Internal error: "+this.type);
        }
    }

    /**
     * This class represents a node in parse tree.
     */
    static class ClosureToken extends Token implements java.io.Serializable {
        int min;
        int max;
        Token child;

        ClosureToken(int type, Token tok) {
            super(type);
            this.child = tok;
            this.setMin(-1);
            this.setMax(-1);
        }

        int size() {
            return 1;
        }
        Token getChild(int index) {
            return this.child;
        }

        final void setMin(int min) {
            this.min = min;
        }
        final void setMax(int max) {
            this.max = max;
        }
        final int getMin() {
            return this.min;
        }
        final int getMax() {
            return this.max;
        }

        public String toString() {
            String ret;
            if (this.type == CLOSURE) {
                if (this.getMin() < 0 && this.getMax() < 0) {
                    ret = this.child.toString()+"*";
                } else if (this.getMin() == this.getMax()) {
                    ret = this.child.toString()+"{"+this.getMin()+"}";
                } else if (this.getMin() >= 0 && this.getMax() >= 0) {
                    ret = this.child.toString()+"{"+this.getMin()+","+this.getMax()+"}";
                } else if (this.getMin() >= 0 && this.getMax() < 0) {
                    ret = this.child.toString()+"{"+this.getMin()+",}";
                } else
                    throw new RuntimeException("Token#toString(): CLOSURE "
                                               +this.getMin()+", "+this.getMax());
            } else {
                if (this.getMin() < 0 && this.getMax() < 0) {
                    ret = this.child.toString()+"*?";
                } else if (this.getMin() == this.getMax()) {
                    ret = this.child.toString()+"{"+this.getMin()+"}?";
                } else if (this.getMin() >= 0 && this.getMax() >= 0) {
                    ret = this.child.toString()+"{"+this.getMin()+","+this.getMax()+"}?";
                } else if (this.getMin() >= 0 && this.getMax() < 0) {
                    ret = this.child.toString()+"{"+this.getMin()+",}?";
                } else
                    throw new RuntimeException("Token#toString(): NONGREEDYCLOSURE "
                                               +this.getMin()+", "+this.getMax());
            }
            return ret;
        }
    }

    /**
     * This class represents a node in parse tree.
     */
    static class ParenToken extends Token implements java.io.Serializable {
        Token child;
        int parennumber;

        ParenToken(int type, Token tok, int paren) {
            super(type);
            this.child = tok;
            this.parennumber = paren;
        }

        int size() {
            return 1;
        }
        Token getChild(int index) {
            return this.child;
        }

        int getParenNumber() {
            return this.parennumber;
        }

        public String toString() {
            String ret = null;
            switch (this.type) {
              case PAREN:
                if (this.parennumber == 0) {
                    ret = "(?:"+this.child.toString()+")";
                } else {
                    ret = "("+this.child.toString()+")";
                }
                break;

              case LOOKAHEAD:
                ret = "(?="+this.child.toString()+")";
                break;
              case NEGATIVELOOKAHEAD:
                ret = "(?!"+this.child.toString()+")";
                break;
              case LOOKBEHIND:
                ret = "(?<="+this.child.toString()+")";
                break;
              case NEGATIVELOOKBEHIND:
                ret = "(?<!"+this.child.toString()+")";
                break;
              case INDEPENDENT:
                ret = "(?>"+this.child.toString()+")";
                break;
            }
            return ret;
        }
    }

    /**
     * (?(condition)yes-pattern|no-pattern)
     */
    static class ConditionToken extends Token implements java.io.Serializable {
        int refNumber;
        Token condition;
        Token yes;
        Token no;
        ConditionToken(int refno, Token cond, Token yespat, Token nopat) {
            super(Token.CONDITION);
            this.refNumber = refno;
            this.condition = cond;
            this.yes = yespat;
            this.no = nopat;
        }
        int size() {
            return this.no == null ? 1 : 2;
        }
        Token getChild(int index) {
            if (index == 0)  return this.yes;
            if (index == 1)  return this.no;
            throw new RuntimeException("Internal Error: "+index);
        }

        public String toString() {
            String ret;
            if (refNumber > 0) {
                ret = "(?("+refNumber+")";
            } else if (this.condition.type == Token.ANCHOR) {
                ret = "(?("+this.condition+")";
            } else {
                ret = "(?"+this.condition;
            }

            if (this.no == null) {
                ret += this.yes+")";
            } else {
                ret += this.yes+"|"+this.no+")";
            }
            return ret;
        }
    }

    /**
     * (ims-ims: .... )
     */
    static class ModifierToken extends Token implements java.io.Serializable {
        Token child;
        int add;
        int mask;

        ModifierToken(Token tok, int add, int mask) {
            super(Token.MODIFIERGROUP);
            this.child = tok;
            this.add = add;
            this.mask = mask;
        }

        int size() {
            return 1;
        }
        Token getChild(int index) {
            return this.child;
        }

        int getOptions() {
            return this.add;
        }
        int getOptionsMask() {
            return this.mask;
        }

        public String toString() {
            return "(?"
                +(this.add == 0 ? "" : REUtil.createOptionString(this.add))
                +(this.mask == 0 ? "" : REUtil.createOptionString(this.mask))
                +":"
                +this.child.toString()
                +")";
        }
    }

    /**
     * This class represents a node in parse tree.
     * for UNION or CONCAT.
     */
    static class UnionToken extends Token implements java.io.Serializable {
        Vector children;

        UnionToken(int type) {
            super(type);
        }

        void addChild(Token tok) {
            if (tok == null)  return;
            if (this.children == null)  this.children = new Vector();
            if (this.type == UNION) {
                this.children.addElement(tok);
                return;
            }
                                                // This is CONCAT, and new child is CONCAT.
            if (tok.type == CONCAT) {
                for (int i = 0;  i < tok.size();  i ++)
                    this.addChild(tok.getChild(i)); // Recursion
                return;
            }
            int size = this.children.size();
            if (size == 0) {
                this.children.addElement(tok);
                return;
            }
            Token previous = (Token)this.children.elementAt(size-1);
            if (!((previous.type == CHAR || previous.type == STRING)
                  && (tok.type == CHAR || tok.type == STRING))) {
                this.children.addElement(tok);
                return;
            }
            
            //System.err.println("Merge '"+previous+"' and '"+tok+"'.");

            StringBuffer buffer;
            int nextMaxLength = (tok.type == CHAR ? 2 : tok.getString().length());
            if (previous.type == CHAR) {        // Replace previous token by STRING
                buffer = new StringBuffer(2 + nextMaxLength);
                int ch = previous.getChar();
                if (ch >= 0x10000)
                    buffer.append(REUtil.decomposeToSurrogates(ch));
                else
                    buffer.append((char)ch);
                previous = Token.createString(null);
                this.children.setElementAt(previous, size-1);
            } else {                            // STRING
                buffer = new StringBuffer(previous.getString().length() + nextMaxLength);
                buffer.append(previous.getString());
            }

            if (tok.type == CHAR) {
                int ch = tok.getChar();
                if (ch >= 0x10000)
                    buffer.append(REUtil.decomposeToSurrogates(ch));
                else
                    buffer.append((char)ch);
            } else {
                buffer.append(tok.getString());
            }

            ((StringToken)previous).string = buffer.toString();
        }

        int size() {
            return this.children == null ? 0 : this.children.size();
        }
        Token getChild(int index) {
            return (Token)this.children.elementAt(index);
        }

        public String toString() {
            String ret;
            if (this.type == CONCAT) {
                if (this.children.size() == 2) {
                    Token ch = this.getChild(0);
                    Token ch2 = this.getChild(1);
                    if (ch2.type == CLOSURE && ch2.getChild(0) == ch) {
                        ret = ch.toString()+"+";
                    } else if (ch2.type == NONGREEDYCLOSURE && ch2.getChild(0) == ch) {
                        ret = ch.toString()+"+?";
                    } else
                        ret = ch.toString()+ch2.toString();
                } else {
                    StringBuffer sb = new StringBuffer();
                    for (int i = 0;  i < this.children.size();  i ++) {
                        sb.append(this.children.elementAt(i).toString());
                    }
                    ret = sb.toString();
                }
                return ret;
            }
            if (this.children.size() == 2 && this.getChild(1).type == EMPTY) {
                ret = this.getChild(0).toString()+"?";
            } else if (this.children.size() == 2
                       && this.getChild(0).type == EMPTY) {
                ret = this.getChild(1).toString()+"??";
            } else {
                StringBuffer sb = new StringBuffer();
                sb.append(this.children.elementAt(0).toString());
                for (int i = 1;  i < this.children.size();  i ++) {
                    sb.append((char)'|');
                    sb.append(this.children.elementAt(i).toString());
                }
                ret = sb.toString();
            }
            return ret;
        }
    }
}