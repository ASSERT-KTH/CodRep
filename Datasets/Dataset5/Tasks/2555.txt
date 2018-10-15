@SuppressWarnings({"unchecked", "unused"})

// $ANTLR 3.0.1 src/org/eclipse/internal/xpand2/parser/Xpand.g 2009-12-21 07:23:30
 	
package org.eclipse.internal.xpand2.parser; 
	
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.antlr.runtime.BaseRecognizer;
import org.antlr.runtime.BitSet;
import org.antlr.runtime.CommonToken;
import org.antlr.runtime.DFA;
import org.antlr.runtime.IntStream;
import org.antlr.runtime.MismatchedSetException;
import org.antlr.runtime.NoViableAltException;
import org.antlr.runtime.Parser;
import org.antlr.runtime.RecognitionException;
import org.antlr.runtime.Token;
import org.antlr.runtime.TokenStream;
import org.eclipse.internal.xpand2.ast.Advice;
import org.eclipse.internal.xpand2.ast.Definition;
import org.eclipse.internal.xpand2.ast.ErrorStatement;
import org.eclipse.internal.xpand2.ast.ExpandStatement;
import org.eclipse.internal.xpand2.ast.ExpressionStatement;
import org.eclipse.internal.xpand2.ast.ExtensionImportDeclaration;
import org.eclipse.internal.xpand2.ast.FileStatement;
import org.eclipse.internal.xpand2.ast.ForEachStatement;
import org.eclipse.internal.xpand2.ast.IfStatement;
import org.eclipse.internal.xpand2.ast.ImportDeclaration;
import org.eclipse.internal.xpand2.ast.LetStatement;
import org.eclipse.internal.xpand2.ast.ProtectStatement;
import org.eclipse.internal.xpand2.ast.Statement;
import org.eclipse.internal.xpand2.ast.Template;
import org.eclipse.internal.xtend.expression.ast.DeclaredParameter;
import org.eclipse.internal.xtend.expression.ast.Expression;
import org.eclipse.internal.xtend.expression.ast.FeatureCall;
import org.eclipse.internal.xtend.expression.ast.GlobalVarExpression;
import org.eclipse.internal.xtend.expression.ast.Identifier;
@SuppressWarnings({"unchecked", "unused", "null"})
public class XpandParser extends Parser {
    public static final String[] tokenNames = new String[] {
        "<invalid>", "<EOR>", "<DOWN>", "<UP>", "LG", "COMMENT", "TEXT", "StringLiteral", "IntLiteral", "Identifier", "EscapeSequence", "UnicodeEscape", "OctalEscape", "HexDigit", "Letter", "JavaIDDigit", "WS", "ML_COMMENT", "LINE_COMMENT", "RG", "VOCAB", "'IMPORT'", "'EXTENSION'", "'AROUND'", "'('", "','", "'*'", "')'", "'FOR'", "'ENDAROUND'", "'::'", "'DEFINE'", "'ENDDEFINE'", "'-'", "'ERROR'", "'EXPAND'", "'FOREACH'", "'SEPARATOR'", "'FILE'", "'ENDFILE'", "'AS'", "'ITERATOR'", "'ENDFOREACH'", "'IF'", "'ENDIF'", "'ELSEIF'", "'ELSE'", "'LET'", "'ENDLET'", "'PROTECT'", "'CSTART'", "'CEND'", "'ID'", "'DISABLE'", "'ENDPROTECT'", "'let'", "'='", "':'", "'->'", "'?'", "'if'", "'then'", "'else'", "'switch'", "'{'", "'case'", "'default'", "'}'", "'||'", "'&&'", "'implies'", "'=='", "'!='", "'>='", "'<='", "'>'", "'<'", "'+'", "'/'", "'!'", "'.'", "'GLOBALVAR'", "'new'", "'false'", "'true'", "'null'", "'typeSelect'", "'collect'", "'select'", "'selectFirst'", "'reject'", "'exists'", "'notExists'", "'sortBy'", "'forAll'", "'|'", "'Collection'", "'List'", "'Set'", "'['", "']'"
    };
    public static final int IntLiteral=8;
    public static final int Identifier=9;
    public static final int HexDigit=13;
    public static final int WS=16;
    public static final int RG=19;
    public static final int COMMENT=5;
    public static final int StringLiteral=7;
    public static final int LINE_COMMENT=18;
    public static final int JavaIDDigit=15;
    public static final int Letter=14;
    public static final int UnicodeEscape=11;
    public static final int EscapeSequence=10;
    public static final int VOCAB=20;
    public static final int EOF=-1;
    public static final int TEXT=6;
    public static final int OctalEscape=12;
    public static final int ML_COMMENT=17;
    public static final int LG=4;

        public XpandParser(TokenStream input) {
            super(input);
            ruleMemo = new HashMap[54+1];
         }
        

    @Override
	public String[] getTokenNames() { return tokenNames; }
    @Override
	public String getGrammarFileName() { return "src/org/eclipse/internal/xpand2/parser/Xpand.g"; }


    	private XpandFactory factory;
    	
    	public XpandParser(TokenStream stream, XpandFactory factory) {
    		this(stream);
    		this.factory = factory;
    	}
    	
    	protected Identifier id(Token t) {
    		if (t == null)
    			return null;
    		CommonToken ct = (CommonToken) t;
    		Identifier id = new Identifier(t.getText());
    		id.setStart(ct.getStartIndex());
    		id.setEnd(ct.getStopIndex());
    		id.setLine(ct.getLine());
    		return id;
    	}



    // $ANTLR start template
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:44:1: template returns [Template t] : ( LG ( COMMENT TEXT )* ( (imp= anImport | extimp= anExtensionImport ) TEXT ( COMMENT TEXT )* )* ( (d= define | a= around ) TEXT ( COMMENT TEXT )* )* | );
	public Template template() throws RecognitionException {
        Template t = null;

        ImportDeclaration imp = null;

        ExtensionImportDeclaration extimp = null;

        Definition d = null;

        Advice a = null;


        List imports = new ArrayList(),extensions = new ArrayList(), defines = new ArrayList(), advices = new ArrayList();
        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:45:123: ( LG ( COMMENT TEXT )* ( (imp= anImport | extimp= anExtensionImport ) TEXT ( COMMENT TEXT )* )* ( (d= define | a= around ) TEXT ( COMMENT TEXT )* )* | )
            int alt8=2;
            int LA8_0 = input.LA(1);

            if ( (LA8_0==LG) ) {
                alt8=1;
            }
            else if ( (LA8_0==EOF) ) {
                alt8=2;
            }
            else {
                if (backtracking>0) {failed=true; return t;}
                NoViableAltException nvae =
                    new NoViableAltException("44:1: template returns [Template t] : ( LG ( COMMENT TEXT )* ( (imp= anImport | extimp= anExtensionImport ) TEXT ( COMMENT TEXT )* )* ( (d= define | a= around ) TEXT ( COMMENT TEXT )* )* | );", 8, 0, input);

                throw nvae;
            }
            switch (alt8) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:46:2: LG ( COMMENT TEXT )* ( (imp= anImport | extimp= anExtensionImport ) TEXT ( COMMENT TEXT )* )* ( (d= define | a= around ) TEXT ( COMMENT TEXT )* )*
                    {
                    match(input,LG,FOLLOW_LG_in_template47); if (failed) return t;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:47:3: ( COMMENT TEXT )*
                    loop1:
                    do {
                        int alt1=2;
                        int LA1_0 = input.LA(1);

                        if ( (LA1_0==COMMENT) ) {
                            alt1=1;
                        }


                        switch (alt1) {
                    	case 1 :
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:47:4: COMMENT TEXT
                    	    {
                    	    match(input,COMMENT,FOLLOW_COMMENT_in_template52); if (failed) return t;
                    	    match(input,TEXT,FOLLOW_TEXT_in_template54); if (failed) return t;

                    	    }
                    	    break;

                    	default :
                    	    break loop1;
                        }
                    } while (true);

                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:48:3: ( (imp= anImport | extimp= anExtensionImport ) TEXT ( COMMENT TEXT )* )*
                    loop4:
                    do {
                        int alt4=2;
                        int LA4_0 = input.LA(1);

                        if ( ((LA4_0>=21 && LA4_0<=22)) ) {
                            alt4=1;
                        }


                        switch (alt4) {
                    	case 1 :
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:48:4: (imp= anImport | extimp= anExtensionImport ) TEXT ( COMMENT TEXT )*
                    	    {
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:48:4: (imp= anImport | extimp= anExtensionImport )
                    	    int alt2=2;
                    	    int LA2_0 = input.LA(1);

                    	    if ( (LA2_0==21) ) {
                    	        alt2=1;
                    	    }
                    	    else if ( (LA2_0==22) ) {
                    	        alt2=2;
                    	    }
                    	    else {
                    	        if (backtracking>0) {failed=true; return t;}
                    	        NoViableAltException nvae =
                    	            new NoViableAltException("48:4: (imp= anImport | extimp= anExtensionImport )", 2, 0, input);

                    	        throw nvae;
                    	    }
                    	    switch (alt2) {
                    	        case 1 :
                    	            // src/org/eclipse/internal/xpand2/parser/Xpand.g:48:5: imp= anImport
                    	            {
                    	            pushFollow(FOLLOW_anImport_in_template64);
                    	            imp=anImport();
                    	            _fsp--;
                    	            if (failed) return t;
                    	            if ( backtracking==0 ) {
                    	              imports.add(imp);
                    	            }

                    	            }
                    	            break;
                    	        case 2 :
                    	            // src/org/eclipse/internal/xpand2/parser/Xpand.g:48:41: extimp= anExtensionImport
                    	            {
                    	            pushFollow(FOLLOW_anExtensionImport_in_template73);
                    	            extimp=anExtensionImport();
                    	            _fsp--;
                    	            if (failed) return t;
                    	            if ( backtracking==0 ) {
                    	              extensions.add(extimp);
                    	            }

                    	            }
                    	            break;

                    	    }

                    	    match(input,TEXT,FOLLOW_TEXT_in_template78); if (failed) return t;
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:48:98: ( COMMENT TEXT )*
                    	    loop3:
                    	    do {
                    	        int alt3=2;
                    	        int LA3_0 = input.LA(1);

                    	        if ( (LA3_0==COMMENT) ) {
                    	            alt3=1;
                    	        }


                    	        switch (alt3) {
                    	    	case 1 :
                    	    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:48:99: COMMENT TEXT
                    	    	    {
                    	    	    match(input,COMMENT,FOLLOW_COMMENT_in_template81); if (failed) return t;
                    	    	    match(input,TEXT,FOLLOW_TEXT_in_template83); if (failed) return t;

                    	    	    }
                    	    	    break;

                    	    	default :
                    	    	    break loop3;
                    	        }
                    	    } while (true);


                    	    }
                    	    break;

                    	default :
                    	    break loop4;
                        }
                    } while (true);

                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:49:3: ( (d= define | a= around ) TEXT ( COMMENT TEXT )* )*
                    loop7:
                    do {
                        int alt7=2;
                        int LA7_0 = input.LA(1);

                        if ( (LA7_0==23||LA7_0==31) ) {
                            alt7=1;
                        }


                        switch (alt7) {
                    	case 1 :
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:49:4: (d= define | a= around ) TEXT ( COMMENT TEXT )*
                    	    {
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:49:4: (d= define | a= around )
                    	    int alt5=2;
                    	    int LA5_0 = input.LA(1);

                    	    if ( (LA5_0==31) ) {
                    	        alt5=1;
                    	    }
                    	    else if ( (LA5_0==23) ) {
                    	        alt5=2;
                    	    }
                    	    else {
                    	        if (backtracking>0) {failed=true; return t;}
                    	        NoViableAltException nvae =
                    	            new NoViableAltException("49:4: (d= define | a= around )", 5, 0, input);

                    	        throw nvae;
                    	    }
                    	    switch (alt5) {
                    	        case 1 :
                    	            // src/org/eclipse/internal/xpand2/parser/Xpand.g:49:5: d= define
                    	            {
                    	            pushFollow(FOLLOW_define_in_template95);
                    	            d=define();
                    	            _fsp--;
                    	            if (failed) return t;
                    	            if ( backtracking==0 ) {
                    	              defines.add(d);
                    	            }

                    	            }
                    	            break;
                    	        case 2 :
                    	            // src/org/eclipse/internal/xpand2/parser/Xpand.g:49:33: a= around
                    	            {
                    	            pushFollow(FOLLOW_around_in_template102);
                    	            a=around();
                    	            _fsp--;
                    	            if (failed) return t;
                    	            if ( backtracking==0 ) {
                    	              advices.add(a);
                    	            }

                    	            }
                    	            break;

                    	    }

                    	    match(input,TEXT,FOLLOW_TEXT_in_template106); if (failed) return t;
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:49:65: ( COMMENT TEXT )*
                    	    loop6:
                    	    do {
                    	        int alt6=2;
                    	        int LA6_0 = input.LA(1);

                    	        if ( (LA6_0==COMMENT) ) {
                    	            alt6=1;
                    	        }


                    	        switch (alt6) {
                    	    	case 1 :
                    	    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:49:66: COMMENT TEXT
                    	    	    {
                    	    	    match(input,COMMENT,FOLLOW_COMMENT_in_template109); if (failed) return t;
                    	    	    match(input,TEXT,FOLLOW_TEXT_in_template111); if (failed) return t;

                    	    	    }
                    	    	    break;

                    	    	default :
                    	    	    break loop6;
                    	        }
                    	    } while (true);


                    	    }
                    	    break;

                    	default :
                    	    break loop7;
                        }
                    } while (true);

                    if ( backtracking==0 ) {
                      t = factory.createTemplate(imports,extensions,defines,advices);
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:52:1: 
                    {
                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return t;
    }
    // $ANTLR end template


    // $ANTLR start anImport
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:54:1: anImport returns [ImportDeclaration imp] : 'IMPORT' id= simpleType ;
    public ImportDeclaration anImport() throws RecognitionException {
        ImportDeclaration imp = null;

        Identifier id = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:54:42: ( 'IMPORT' id= simpleType )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:55:2: 'IMPORT' id= simpleType
            {
            match(input,21,FOLLOW_21_in_anImport137); if (failed) return imp;
            pushFollow(FOLLOW_simpleType_in_anImport141);
            id=simpleType();
            _fsp--;
            if (failed) return imp;
            if ( backtracking==0 ) {
              imp = factory.createImportDeclaration(id);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return imp;
    }
    // $ANTLR end anImport


    // $ANTLR start anExtensionImport
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:58:1: anExtensionImport returns [ExtensionImportDeclaration imp] : 'EXTENSION' id= simpleType ;
    public ExtensionImportDeclaration anExtensionImport() throws RecognitionException {
        ExtensionImportDeclaration imp = null;

        Identifier id = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:58:59: ( 'EXTENSION' id= simpleType )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:59:2: 'EXTENSION' id= simpleType
            {
            match(input,22,FOLLOW_22_in_anExtensionImport156); if (failed) return imp;
            pushFollow(FOLLOW_simpleType_in_anExtensionImport160);
            id=simpleType();
            _fsp--;
            if (failed) return imp;
            if ( backtracking==0 ) {
              imp = factory.createExtensionImportDeclaration(id);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return imp;
    }
    // $ANTLR end anExtensionImport


    // $ANTLR start around
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:62:1: around returns [Advice a] : 'AROUND' pc= pointcut ( '(' (p= declaredParameterList ( ',' wildparams= '*' )? | wildparams= '*' ) ')' )? 'FOR' t= type s= sequence 'ENDAROUND' ;
    public Advice around() throws RecognitionException {
        Advice a = null;

        Token wildparams=null;
        Identifier pc = null;

        List<DeclaredParameter> p = null;

        Identifier t = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:62:27: ( 'AROUND' pc= pointcut ( '(' (p= declaredParameterList ( ',' wildparams= '*' )? | wildparams= '*' ) ')' )? 'FOR' t= type s= sequence 'ENDAROUND' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:63:4: 'AROUND' pc= pointcut ( '(' (p= declaredParameterList ( ',' wildparams= '*' )? | wildparams= '*' ) ')' )? 'FOR' t= type s= sequence 'ENDAROUND'
            {
            match(input,23,FOLLOW_23_in_around178); if (failed) return a;
            pushFollow(FOLLOW_pointcut_in_around182);
            pc=pointcut();
            _fsp--;
            if (failed) return a;
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:64:4: ( '(' (p= declaredParameterList ( ',' wildparams= '*' )? | wildparams= '*' ) ')' )?
            int alt11=2;
            int LA11_0 = input.LA(1);

            if ( (LA11_0==24) ) {
                alt11=1;
            }
            switch (alt11) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:64:5: '(' (p= declaredParameterList ( ',' wildparams= '*' )? | wildparams= '*' ) ')'
                    {
                    match(input,24,FOLLOW_24_in_around188); if (failed) return a;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:64:9: (p= declaredParameterList ( ',' wildparams= '*' )? | wildparams= '*' )
                    int alt10=2;
                    int LA10_0 = input.LA(1);

                    if ( (LA10_0==Identifier||(LA10_0>=96 && LA10_0<=98)) ) {
                        alt10=1;
                    }
                    else if ( (LA10_0==26) ) {
                        alt10=2;
                    }
                    else {
                        if (backtracking>0) {failed=true; return a;}
                        NoViableAltException nvae =
                            new NoViableAltException("64:9: (p= declaredParameterList ( ',' wildparams= '*' )? | wildparams= '*' )", 10, 0, input);

                        throw nvae;
                    }
                    switch (alt10) {
                        case 1 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:64:10: p= declaredParameterList ( ',' wildparams= '*' )?
                            {
                            pushFollow(FOLLOW_declaredParameterList_in_around193);
                            p=declaredParameterList();
                            _fsp--;
                            if (failed) return a;
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:64:34: ( ',' wildparams= '*' )?
                            int alt9=2;
                            int LA9_0 = input.LA(1);

                            if ( (LA9_0==25) ) {
                                alt9=1;
                            }
                            switch (alt9) {
                                case 1 :
                                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:64:35: ',' wildparams= '*'
                                    {
                                    match(input,25,FOLLOW_25_in_around196); if (failed) return a;
                                    wildparams=input.LT(1);
                                    match(input,26,FOLLOW_26_in_around200); if (failed) return a;

                                    }
                                    break;

                            }


                            }
                            break;
                        case 2 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:64:59: wildparams= '*'
                            {
                            wildparams=input.LT(1);
                            match(input,26,FOLLOW_26_in_around209); if (failed) return a;

                            }
                            break;

                    }

                    match(input,27,FOLLOW_27_in_around213); if (failed) return a;

                    }
                    break;

            }

            match(input,28,FOLLOW_28_in_around217); if (failed) return a;
            pushFollow(FOLLOW_type_in_around221);
            t=type();
            _fsp--;
            if (failed) return a;
            pushFollow(FOLLOW_sequence_in_around229);
            s=sequence();
            _fsp--;
            if (failed) return a;
            match(input,29,FOLLOW_29_in_around234); if (failed) return a;
            if ( backtracking==0 ) {
               a = factory.createAround(pc,p,wildparams!=null,t,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return a;
    }
    // $ANTLR end around


    // $ANTLR start pointcut
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:70:1: pointcut returns [Identifier i] : (x= '*' | i1= identifier ) (x1= '*' | n1= identifier | dc= '::' )* ;
    public Identifier pointcut() throws RecognitionException {
        Identifier i = null;

        Token x=null;
        Token x1=null;
        Token dc=null;
        Identifier i1 = null;

        Identifier n1 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:70:33: ( (x= '*' | i1= identifier ) (x1= '*' | n1= identifier | dc= '::' )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:71:2: (x= '*' | i1= identifier ) (x1= '*' | n1= identifier | dc= '::' )*
            {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:71:2: (x= '*' | i1= identifier )
            int alt12=2;
            int LA12_0 = input.LA(1);

            if ( (LA12_0==26) ) {
                alt12=1;
            }
            else if ( (LA12_0==Identifier) ) {
                alt12=2;
            }
            else {
                if (backtracking>0) {failed=true; return i;}
                NoViableAltException nvae =
                    new NoViableAltException("71:2: (x= '*' | i1= identifier )", 12, 0, input);

                throw nvae;
            }
            switch (alt12) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:71:3: x= '*'
                    {
                    x=input.LT(1);
                    match(input,26,FOLLOW_26_in_pointcut256); if (failed) return i;
                    if ( backtracking==0 ) {
                      i = id(x);
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:71:23: i1= identifier
                    {
                    pushFollow(FOLLOW_identifier_in_pointcut262);
                    i1=identifier();
                    _fsp--;
                    if (failed) return i;
                    if ( backtracking==0 ) {
                      i = i1;
                    }

                    }
                    break;

            }

            // src/org/eclipse/internal/xpand2/parser/Xpand.g:72:2: (x1= '*' | n1= identifier | dc= '::' )*
            loop13:
            do {
                int alt13=4;
                switch ( input.LA(1) ) {
                case 26:
                    {
                    alt13=1;
                    }
                    break;
                case Identifier:
                    {
                    alt13=2;
                    }
                    break;
                case 30:
                    {
                    alt13=3;
                    }
                    break;

                }

                switch (alt13) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:72:3: x1= '*'
            	    {
            	    x1=input.LT(1);
            	    match(input,26,FOLLOW_26_in_pointcut271); if (failed) return i;
            	    if ( backtracking==0 ) {
            	      i.append(id(x1));
            	    }

            	    }
            	    break;
            	case 2 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:72:31: n1= identifier
            	    {
            	    pushFollow(FOLLOW_identifier_in_pointcut277);
            	    n1=identifier();
            	    _fsp--;
            	    if (failed) return i;
            	    if ( backtracking==0 ) {
            	      i.append(n1);
            	    }

            	    }
            	    break;
            	case 3 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:72:62: dc= '::'
            	    {
            	    dc=input.LT(1);
            	    match(input,30,FOLLOW_30_in_pointcut283); if (failed) return i;
            	    if ( backtracking==0 ) {
            	      i.append(id(dc));
            	    }

            	    }
            	    break;

            	default :
            	    break loop13;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return i;
    }
    // $ANTLR end pointcut


    // $ANTLR start define
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:75:1: define returns [Definition d] : 'DEFINE' name= identifier ( '(' p= declaredParameterList ')' )? 'FOR' t= type s= sequence 'ENDDEFINE' ;
    public Definition define() throws RecognitionException {
        Definition d = null;

        Identifier name = null;

        List<DeclaredParameter> p = null;

        Identifier t = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:75:31: ( 'DEFINE' name= identifier ( '(' p= declaredParameterList ')' )? 'FOR' t= type s= sequence 'ENDDEFINE' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:76:4: 'DEFINE' name= identifier ( '(' p= declaredParameterList ')' )? 'FOR' t= type s= sequence 'ENDDEFINE'
            {
            match(input,31,FOLLOW_31_in_define303); if (failed) return d;
            pushFollow(FOLLOW_identifier_in_define307);
            name=identifier();
            _fsp--;
            if (failed) return d;
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:76:29: ( '(' p= declaredParameterList ')' )?
            int alt14=2;
            int LA14_0 = input.LA(1);

            if ( (LA14_0==24) ) {
                alt14=1;
            }
            switch (alt14) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:76:30: '(' p= declaredParameterList ')'
                    {
                    match(input,24,FOLLOW_24_in_define310); if (failed) return d;
                    pushFollow(FOLLOW_declaredParameterList_in_define314);
                    p=declaredParameterList();
                    _fsp--;
                    if (failed) return d;
                    match(input,27,FOLLOW_27_in_define316); if (failed) return d;

                    }
                    break;

            }

            match(input,28,FOLLOW_28_in_define320); if (failed) return d;
            pushFollow(FOLLOW_type_in_define324);
            t=type();
            _fsp--;
            if (failed) return d;
            pushFollow(FOLLOW_sequence_in_define332);
            s=sequence();
            _fsp--;
            if (failed) return d;
            match(input,32,FOLLOW_32_in_define338); if (failed) return d;
            if ( backtracking==0 ) {
               d = factory.createDefinition(name,p,t,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return d;
    }
    // $ANTLR end define


    // $ANTLR start sequence
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:82:1: sequence returns [List<Statement> s=new ArrayList<Statement>()] : s1= textSequence (s2= statement s1= textSequence )* ;
    public List<Statement> sequence() throws RecognitionException {
        List<Statement> s = new ArrayList<Statement>();

        List<Statement> s1 = null;

        Statement s2 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:82:65: (s1= textSequence (s2= statement s1= textSequence )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:83:3: s1= textSequence (s2= statement s1= textSequence )*
            {
            pushFollow(FOLLOW_textSequence_in_sequence361);
            s1=textSequence();
            _fsp--;
            if (failed) return s;
            if ( backtracking==0 ) {
              s.addAll(s1);
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:84:3: (s2= statement s1= textSequence )*
            loop15:
            do {
                int alt15=2;
                int LA15_0 = input.LA(1);

                if ( ((LA15_0>=StringLiteral && LA15_0<=Identifier)||LA15_0==24||(LA15_0>=33 && LA15_0<=36)||LA15_0==38||LA15_0==43||LA15_0==47||LA15_0==49||LA15_0==55||LA15_0==60||(LA15_0>=63 && LA15_0<=64)||LA15_0==79||(LA15_0>=81 && LA15_0<=94)||(LA15_0>=96 && LA15_0<=98)) ) {
                    alt15=1;
                }


                switch (alt15) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:84:4: s2= statement s1= textSequence
            	    {
            	    pushFollow(FOLLOW_statement_in_sequence370);
            	    s2=statement();
            	    _fsp--;
            	    if (failed) return s;
            	    if ( backtracking==0 ) {
            	      s.add(s2);
            	    }
            	    pushFollow(FOLLOW_textSequence_in_sequence379);
            	    s1=textSequence();
            	    _fsp--;
            	    if (failed) return s;
            	    if ( backtracking==0 ) {
            	      s.addAll(s1);
            	    }

            	    }
            	    break;

            	default :
            	    break loop15;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return s;
    }
    // $ANTLR end sequence


    // $ANTLR start statement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:93:1: statement returns [Statement s] : (s1= simpleStatement | s2= fileStatement | s3= foreachStatement | s4= ifStatement | s5= letStatement | s6= protectStatement );
    public Statement statement() throws RecognitionException {
        Statement s = null;

        Statement s1 = null;

        FileStatement s2 = null;

        ForEachStatement s3 = null;

        IfStatement s4 = null;

        LetStatement s5 = null;

        ProtectStatement s6 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:93:33: (s1= simpleStatement | s2= fileStatement | s3= foreachStatement | s4= ifStatement | s5= letStatement | s6= protectStatement )
            int alt16=6;
            switch ( input.LA(1) ) {
            case StringLiteral:
            case IntLiteral:
            case Identifier:
            case 24:
            case 33:
            case 34:
            case 35:
            case 55:
            case 60:
            case 63:
            case 64:
            case 79:
            case 81:
            case 82:
            case 83:
            case 84:
            case 85:
            case 86:
            case 87:
            case 88:
            case 89:
            case 90:
            case 91:
            case 92:
            case 93:
            case 94:
            case 96:
            case 97:
            case 98:
                {
                alt16=1;
                }
                break;
            case 38:
                {
                alt16=2;
                }
                break;
            case 36:
                {
                alt16=3;
                }
                break;
            case 43:
                {
                alt16=4;
                }
                break;
            case 47:
                {
                alt16=5;
                }
                break;
            case 49:
                {
                alt16=6;
                }
                break;
            default:
                if (backtracking>0) {failed=true; return s;}
                NoViableAltException nvae =
                    new NoViableAltException("93:1: statement returns [Statement s] : (s1= simpleStatement | s2= fileStatement | s3= foreachStatement | s4= ifStatement | s5= letStatement | s6= protectStatement );", 16, 0, input);

                throw nvae;
            }

            switch (alt16) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:94:3: s1= simpleStatement
                    {
                    pushFollow(FOLLOW_simpleStatement_in_statement409);
                    s1=simpleStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s1;
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:95:3: s2= fileStatement
                    {
                    pushFollow(FOLLOW_fileStatement_in_statement417);
                    s2=fileStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s2;
                    }

                    }
                    break;
                case 3 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:96:3: s3= foreachStatement
                    {
                    pushFollow(FOLLOW_foreachStatement_in_statement425);
                    s3=foreachStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s3;
                    }

                    }
                    break;
                case 4 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:97:3: s4= ifStatement
                    {
                    pushFollow(FOLLOW_ifStatement_in_statement433);
                    s4=ifStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s4;
                    }

                    }
                    break;
                case 5 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:98:3: s5= letStatement
                    {
                    pushFollow(FOLLOW_letStatement_in_statement441);
                    s5=letStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s5;
                    }

                    }
                    break;
                case 6 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:99:3: s6= protectStatement
                    {
                    pushFollow(FOLLOW_protectStatement_in_statement449);
                    s6=protectStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s6;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return s;
    }
    // $ANTLR end statement


    // $ANTLR start textSequence
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:102:1: textSequence returns [List<Statement> s=new ArrayList<Statement>();] : t= text ( COMMENT t1= text )* ;
    public List<Statement> textSequence() throws RecognitionException {
        List<Statement> s = new ArrayList<Statement>();

        Statement t = null;

        Statement t1 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:102:70: (t= text ( COMMENT t1= text )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:103:2: t= text ( COMMENT t1= text )*
            {
            pushFollow(FOLLOW_text_in_textSequence468);
            t=text();
            _fsp--;
            if (failed) return s;
            if ( backtracking==0 ) {
              s.add(t);
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:104:3: ( COMMENT t1= text )*
            loop17:
            do {
                int alt17=2;
                int LA17_0 = input.LA(1);

                if ( (LA17_0==COMMENT) ) {
                    alt17=1;
                }


                switch (alt17) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:104:4: COMMENT t1= text
            	    {
            	    match(input,COMMENT,FOLLOW_COMMENT_in_textSequence475); if (failed) return s;
            	    pushFollow(FOLLOW_text_in_textSequence479);
            	    t1=text();
            	    _fsp--;
            	    if (failed) return s;
            	    if ( backtracking==0 ) {
            	      s.add(t1);
            	    }

            	    }
            	    break;

            	default :
            	    break loop17;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return s;
    }
    // $ANTLR end textSequence


    // $ANTLR start text
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:107:1: text returns [Statement s] : (m= '-' )? t= TEXT ;
    public Statement text() throws RecognitionException {
        Statement s = null;

        Token m=null;
        Token t=null;

        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:107:28: ( (m= '-' )? t= TEXT )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:108:2: (m= '-' )? t= TEXT
            {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:108:2: (m= '-' )?
            int alt18=2;
            int LA18_0 = input.LA(1);

            if ( (LA18_0==33) ) {
                alt18=1;
            }
            switch (alt18) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:108:3: m= '-'
                    {
                    m=input.LT(1);
                    match(input,33,FOLLOW_33_in_text500); if (failed) return s;

                    }
                    break;

            }

            t=input.LT(1);
            match(input,TEXT,FOLLOW_TEXT_in_text506); if (failed) return s;
            if ( backtracking==0 ) {
              s = factory.createTextStatement(id(t),id(m));
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return s;
    }
    // $ANTLR end text


    // $ANTLR start simpleStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:111:1: simpleStatement returns [Statement s] : (s1= errorStatement | s2= expandStatement | s3= expressionStmt );
    public Statement simpleStatement() throws RecognitionException {
        Statement s = null;

        ErrorStatement s1 = null;

        ExpandStatement s2 = null;

        ExpressionStatement s3 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:111:39: (s1= errorStatement | s2= expandStatement | s3= expressionStmt )
            int alt19=3;
            switch ( input.LA(1) ) {
            case 34:
                {
                alt19=1;
                }
                break;
            case 35:
                {
                alt19=2;
                }
                break;
            case StringLiteral:
            case IntLiteral:
            case Identifier:
            case 24:
            case 33:
            case 55:
            case 60:
            case 63:
            case 64:
            case 79:
            case 81:
            case 82:
            case 83:
            case 84:
            case 85:
            case 86:
            case 87:
            case 88:
            case 89:
            case 90:
            case 91:
            case 92:
            case 93:
            case 94:
            case 96:
            case 97:
            case 98:
                {
                alt19=3;
                }
                break;
            default:
                if (backtracking>0) {failed=true; return s;}
                NoViableAltException nvae =
                    new NoViableAltException("111:1: simpleStatement returns [Statement s] : (s1= errorStatement | s2= expandStatement | s3= expressionStmt );", 19, 0, input);

                throw nvae;
            }

            switch (alt19) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:112:3: s1= errorStatement
                    {
                    pushFollow(FOLLOW_errorStatement_in_simpleStatement525);
                    s1=errorStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s1;
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:113:3: s2= expandStatement
                    {
                    pushFollow(FOLLOW_expandStatement_in_simpleStatement533);
                    s2=expandStatement();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s2;
                    }

                    }
                    break;
                case 3 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:114:3: s3= expressionStmt
                    {
                    pushFollow(FOLLOW_expressionStmt_in_simpleStatement541);
                    s3=expressionStmt();
                    _fsp--;
                    if (failed) return s;
                    if ( backtracking==0 ) {
                      s =s3;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return s;
    }
    // $ANTLR end simpleStatement


    // $ANTLR start errorStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:117:1: errorStatement returns [ErrorStatement e] : 'ERROR' expr= expression ;
    public ErrorStatement errorStatement() throws RecognitionException {
        ErrorStatement e = null;

        Expression expr = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:117:43: ( 'ERROR' expr= expression )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:118:3: 'ERROR' expr= expression
            {
            match(input,34,FOLLOW_34_in_errorStatement558); if (failed) return e;
            pushFollow(FOLLOW_expression_in_errorStatement562);
            expr=expression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
               e = factory.createErrorStatement(expr); 
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end errorStatement


    // $ANTLR start expandStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:121:1: expandStatement returns [ExpandStatement e] : 'EXPAND' t= definitionName ( '(' pl= parameterList ')' )? ( ( 'FOR' expr= expression ) | (fe= 'FOREACH' expr= expression ( 'SEPARATOR' sep= expression )? ) )? ;
    public ExpandStatement expandStatement() throws RecognitionException {
        ExpandStatement e = null;

        Token fe=null;
        Identifier t = null;

        List<Expression> pl = null;

        Expression expr = null;

        Expression sep = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:121:45: ( 'EXPAND' t= definitionName ( '(' pl= parameterList ')' )? ( ( 'FOR' expr= expression ) | (fe= 'FOREACH' expr= expression ( 'SEPARATOR' sep= expression )? ) )? )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:122:3: 'EXPAND' t= definitionName ( '(' pl= parameterList ')' )? ( ( 'FOR' expr= expression ) | (fe= 'FOREACH' expr= expression ( 'SEPARATOR' sep= expression )? ) )?
            {
            match(input,35,FOLLOW_35_in_expandStatement579); if (failed) return e;
            pushFollow(FOLLOW_definitionName_in_expandStatement583);
            t=definitionName();
            _fsp--;
            if (failed) return e;
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:122:29: ( '(' pl= parameterList ')' )?
            int alt20=2;
            int LA20_0 = input.LA(1);

            if ( (LA20_0==24) ) {
                alt20=1;
            }
            switch (alt20) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:122:30: '(' pl= parameterList ')'
                    {
                    match(input,24,FOLLOW_24_in_expandStatement586); if (failed) return e;
                    pushFollow(FOLLOW_parameterList_in_expandStatement590);
                    pl=parameterList();
                    _fsp--;
                    if (failed) return e;
                    match(input,27,FOLLOW_27_in_expandStatement592); if (failed) return e;

                    }
                    break;

            }

            // src/org/eclipse/internal/xpand2/parser/Xpand.g:122:57: ( ( 'FOR' expr= expression ) | (fe= 'FOREACH' expr= expression ( 'SEPARATOR' sep= expression )? ) )?
            int alt22=3;
            int LA22_0 = input.LA(1);

            if ( (LA22_0==28) ) {
                alt22=1;
            }
            else if ( (LA22_0==36) ) {
                alt22=2;
            }
            switch (alt22) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:122:58: ( 'FOR' expr= expression )
                    {
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:122:58: ( 'FOR' expr= expression )
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:122:59: 'FOR' expr= expression
                    {
                    match(input,28,FOLLOW_28_in_expandStatement598); if (failed) return e;
                    pushFollow(FOLLOW_expression_in_expandStatement602);
                    expr=expression();
                    _fsp--;
                    if (failed) return e;

                    }


                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:123:5: (fe= 'FOREACH' expr= expression ( 'SEPARATOR' sep= expression )? )
                    {
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:123:5: (fe= 'FOREACH' expr= expression ( 'SEPARATOR' sep= expression )? )
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:123:6: fe= 'FOREACH' expr= expression ( 'SEPARATOR' sep= expression )?
                    {
                    fe=input.LT(1);
                    match(input,36,FOLLOW_36_in_expandStatement612); if (failed) return e;
                    pushFollow(FOLLOW_expression_in_expandStatement616);
                    expr=expression();
                    _fsp--;
                    if (failed) return e;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:123:35: ( 'SEPARATOR' sep= expression )?
                    int alt21=2;
                    int LA21_0 = input.LA(1);

                    if ( (LA21_0==37) ) {
                        alt21=1;
                    }
                    switch (alt21) {
                        case 1 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:123:36: 'SEPARATOR' sep= expression
                            {
                            match(input,37,FOLLOW_37_in_expandStatement619); if (failed) return e;
                            pushFollow(FOLLOW_expression_in_expandStatement623);
                            sep=expression();
                            _fsp--;
                            if (failed) return e;

                            }
                            break;

                    }


                    }


                    }
                    break;

            }

            if ( backtracking==0 ) {
              e = factory.createExpandStatement(t,pl,expr,fe!=null,sep);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end expandStatement


    // $ANTLR start definitionName
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:128:1: definitionName returns [Identifier id] : id1= simpleType ;
    public Identifier definitionName() throws RecognitionException {
        Identifier id = null;

        Identifier id1 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:128:40: (id1= simpleType )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:129:2: id1= simpleType
            {
            pushFollow(FOLLOW_simpleType_in_definitionName653);
            id1=simpleType();
            _fsp--;
            if (failed) return id;
            if ( backtracking==0 ) {
              id =id1;
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return id;
    }
    // $ANTLR end definitionName


    // $ANTLR start expressionStmt
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:132:1: expressionStmt returns [ExpressionStatement es] : e= expression ;
    public ExpressionStatement expressionStmt() throws RecognitionException {
        ExpressionStatement es = null;

        Expression e = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:132:49: (e= expression )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:133:2: e= expression
            {
            pushFollow(FOLLOW_expression_in_expressionStmt671);
            e=expression();
            _fsp--;
            if (failed) return es;
            if ( backtracking==0 ) {
              es = factory.createExpressionStatement(e);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return es;
    }
    // $ANTLR end expressionStmt


    // $ANTLR start fileStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:136:1: fileStatement returns [FileStatement f] : 'FILE' e= expression (option= identifier )? s= sequence 'ENDFILE' ;
    public FileStatement fileStatement() throws RecognitionException {
        FileStatement f = null;

        Expression e = null;

        Identifier option = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:136:41: ( 'FILE' e= expression (option= identifier )? s= sequence 'ENDFILE' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:137:2: 'FILE' e= expression (option= identifier )? s= sequence 'ENDFILE'
            {
            match(input,38,FOLLOW_38_in_fileStatement687); if (failed) return f;
            pushFollow(FOLLOW_expression_in_fileStatement691);
            e=expression();
            _fsp--;
            if (failed) return f;
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:137:22: (option= identifier )?
            int alt23=2;
            int LA23_0 = input.LA(1);

            if ( (LA23_0==Identifier) ) {
                alt23=1;
            }
            switch (alt23) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:137:23: option= identifier
                    {
                    pushFollow(FOLLOW_identifier_in_fileStatement696);
                    option=identifier();
                    _fsp--;
                    if (failed) return f;

                    }
                    break;

            }

            pushFollow(FOLLOW_sequence_in_fileStatement704);
            s=sequence();
            _fsp--;
            if (failed) return f;
            match(input,39,FOLLOW_39_in_fileStatement708); if (failed) return f;
            if ( backtracking==0 ) {
              f = factory.createFileStatement(e,option,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return f;
    }
    // $ANTLR end fileStatement


    // $ANTLR start foreachStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:143:1: foreachStatement returns [ForEachStatement f] : 'FOREACH' e= expression 'AS' v= identifier ( 'ITERATOR' iter= identifier )? ( 'SEPARATOR' sep= expression )? s= sequence 'ENDFOREACH' ;
    public ForEachStatement foreachStatement() throws RecognitionException {
        ForEachStatement f = null;

        Expression e = null;

        Identifier v = null;

        Identifier iter = null;

        Expression sep = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:143:46: ( 'FOREACH' e= expression 'AS' v= identifier ( 'ITERATOR' iter= identifier )? ( 'SEPARATOR' sep= expression )? s= sequence 'ENDFOREACH' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:144:3: 'FOREACH' e= expression 'AS' v= identifier ( 'ITERATOR' iter= identifier )? ( 'SEPARATOR' sep= expression )? s= sequence 'ENDFOREACH'
            {
            match(input,36,FOLLOW_36_in_foreachStatement726); if (failed) return f;
            pushFollow(FOLLOW_expression_in_foreachStatement730);
            e=expression();
            _fsp--;
            if (failed) return f;
            match(input,40,FOLLOW_40_in_foreachStatement732); if (failed) return f;
            pushFollow(FOLLOW_identifier_in_foreachStatement736);
            v=identifier();
            _fsp--;
            if (failed) return f;
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:144:44: ( 'ITERATOR' iter= identifier )?
            int alt24=2;
            int LA24_0 = input.LA(1);

            if ( (LA24_0==41) ) {
                alt24=1;
            }
            switch (alt24) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:144:45: 'ITERATOR' iter= identifier
                    {
                    match(input,41,FOLLOW_41_in_foreachStatement739); if (failed) return f;
                    pushFollow(FOLLOW_identifier_in_foreachStatement743);
                    iter=identifier();
                    _fsp--;
                    if (failed) return f;

                    }
                    break;

            }

            // src/org/eclipse/internal/xpand2/parser/Xpand.g:144:74: ( 'SEPARATOR' sep= expression )?
            int alt25=2;
            int LA25_0 = input.LA(1);

            if ( (LA25_0==37) ) {
                alt25=1;
            }
            switch (alt25) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:144:75: 'SEPARATOR' sep= expression
                    {
                    match(input,37,FOLLOW_37_in_foreachStatement748); if (failed) return f;
                    pushFollow(FOLLOW_expression_in_foreachStatement752);
                    sep=expression();
                    _fsp--;
                    if (failed) return f;

                    }
                    break;

            }

            pushFollow(FOLLOW_sequence_in_foreachStatement762);
            s=sequence();
            _fsp--;
            if (failed) return f;
            match(input,42,FOLLOW_42_in_foreachStatement767); if (failed) return f;
            if ( backtracking==0 ) {
              f = factory.createForEachStatement(e,v,sep,iter,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return f;
    }
    // $ANTLR end foreachStatement


    // $ANTLR start ifStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:150:1: ifStatement returns [IfStatement i] : 'IF' e= expression s= sequence (elif= elseIfStatement )* (el= elseStatement )? 'ENDIF' ;
    public IfStatement ifStatement() throws RecognitionException {
        IfStatement i = null;

        Expression e = null;

        List<Statement> s = null;

        IfStatement elif = null;

        IfStatement el = null;


        IfStatement temp = null;
        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:150:68: ( 'IF' e= expression s= sequence (elif= elseIfStatement )* (el= elseStatement )? 'ENDIF' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:151:6: 'IF' e= expression s= sequence (elif= elseIfStatement )* (el= elseStatement )? 'ENDIF'
            {
            match(input,43,FOLLOW_43_in_ifStatement793); if (failed) return i;
            pushFollow(FOLLOW_expression_in_ifStatement797);
            e=expression();
            _fsp--;
            if (failed) return i;
            pushFollow(FOLLOW_sequence_in_ifStatement803);
            s=sequence();
            _fsp--;
            if (failed) return i;
            if ( backtracking==0 ) {
              i = factory.createIfStatement(e,s);
              		 temp = i;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:155:3: (elif= elseIfStatement )*
            loop26:
            do {
                int alt26=2;
                int LA26_0 = input.LA(1);

                if ( (LA26_0==45) ) {
                    alt26=1;
                }


                switch (alt26) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:155:4: elif= elseIfStatement
            	    {
            	    pushFollow(FOLLOW_elseIfStatement_in_ifStatement815);
            	    elif=elseIfStatement();
            	    _fsp--;
            	    if (failed) return i;
            	    if ( backtracking==0 ) {
            	      temp.setElseIf(elif);
            	      	 			temp = elif; 
            	    }

            	    }
            	    break;

            	default :
            	    break loop26;
                }
            } while (true);

            // src/org/eclipse/internal/xpand2/parser/Xpand.g:157:3: (el= elseStatement )?
            int alt27=2;
            int LA27_0 = input.LA(1);

            if ( (LA27_0==46) ) {
                alt27=1;
            }
            switch (alt27) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:157:4: el= elseStatement
                    {
                    pushFollow(FOLLOW_elseStatement_in_ifStatement826);
                    el=elseStatement();
                    _fsp--;
                    if (failed) return i;
                    if ( backtracking==0 ) {
                      temp.setElseIf(el);
                      	 			temp = el; 
                    }

                    }
                    break;

            }

            match(input,44,FOLLOW_44_in_ifStatement838); if (failed) return i;

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return i;
    }
    // $ANTLR end ifStatement


    // $ANTLR start elseIfStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:162:1: elseIfStatement returns [IfStatement i] : 'ELSEIF' e= expression s= sequence ;
    public IfStatement elseIfStatement() throws RecognitionException {
        IfStatement i = null;

        Expression e = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:162:41: ( 'ELSEIF' e= expression s= sequence )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:163:2: 'ELSEIF' e= expression s= sequence
            {
            match(input,45,FOLLOW_45_in_elseIfStatement852); if (failed) return i;
            pushFollow(FOLLOW_expression_in_elseIfStatement856);
            e=expression();
            _fsp--;
            if (failed) return i;
            pushFollow(FOLLOW_sequence_in_elseIfStatement862);
            s=sequence();
            _fsp--;
            if (failed) return i;
            if ( backtracking==0 ) {
              i = factory.createIfStatement(e,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return i;
    }
    // $ANTLR end elseIfStatement


    // $ANTLR start elseStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:168:1: elseStatement returns [IfStatement i] : 'ELSE' s= sequence ;
    public IfStatement elseStatement() throws RecognitionException {
        IfStatement i = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:168:39: ( 'ELSE' s= sequence )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:169:2: 'ELSE' s= sequence
            {
            match(input,46,FOLLOW_46_in_elseStatement883); if (failed) return i;
            pushFollow(FOLLOW_sequence_in_elseStatement889);
            s=sequence();
            _fsp--;
            if (failed) return i;
            if ( backtracking==0 ) {
              i = factory.createIfStatement(null,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return i;
    }
    // $ANTLR end elseStatement


    // $ANTLR start letStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:174:1: letStatement returns [LetStatement l] : 'LET' e= expression 'AS' v= identifier s= sequence 'ENDLET' ;
    public LetStatement letStatement() throws RecognitionException {
        LetStatement l = null;

        Expression e = null;

        Identifier v = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:174:39: ( 'LET' e= expression 'AS' v= identifier s= sequence 'ENDLET' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:175:3: 'LET' e= expression 'AS' v= identifier s= sequence 'ENDLET'
            {
            match(input,47,FOLLOW_47_in_letStatement910); if (failed) return l;
            pushFollow(FOLLOW_expression_in_letStatement914);
            e=expression();
            _fsp--;
            if (failed) return l;
            match(input,40,FOLLOW_40_in_letStatement916); if (failed) return l;
            pushFollow(FOLLOW_identifier_in_letStatement920);
            v=identifier();
            _fsp--;
            if (failed) return l;
            pushFollow(FOLLOW_sequence_in_letStatement928);
            s=sequence();
            _fsp--;
            if (failed) return l;
            match(input,48,FOLLOW_48_in_letStatement933); if (failed) return l;
            if ( backtracking==0 ) {
              l = factory.createLetStatement(e,v,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return l;
    }
    // $ANTLR end letStatement


    // $ANTLR start protectStatement
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:181:1: protectStatement returns [ProtectStatement l] : 'PROTECT' 'CSTART' startC= expression 'CEND' endC= expression 'ID' id= expression (disabled= 'DISABLE' )? s= sequence 'ENDPROTECT' ;
    public ProtectStatement protectStatement() throws RecognitionException {
        ProtectStatement l = null;

        Token disabled=null;
        Expression startC = null;

        Expression endC = null;

        Expression id = null;

        List<Statement> s = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:181:47: ( 'PROTECT' 'CSTART' startC= expression 'CEND' endC= expression 'ID' id= expression (disabled= 'DISABLE' )? s= sequence 'ENDPROTECT' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:182:2: 'PROTECT' 'CSTART' startC= expression 'CEND' endC= expression 'ID' id= expression (disabled= 'DISABLE' )? s= sequence 'ENDPROTECT'
            {
            match(input,49,FOLLOW_49_in_protectStatement952); if (failed) return l;
            match(input,50,FOLLOW_50_in_protectStatement957); if (failed) return l;
            pushFollow(FOLLOW_expression_in_protectStatement961);
            startC=expression();
            _fsp--;
            if (failed) return l;
            match(input,51,FOLLOW_51_in_protectStatement966); if (failed) return l;
            pushFollow(FOLLOW_expression_in_protectStatement970);
            endC=expression();
            _fsp--;
            if (failed) return l;
            match(input,52,FOLLOW_52_in_protectStatement983); if (failed) return l;
            pushFollow(FOLLOW_expression_in_protectStatement987);
            id=expression();
            _fsp--;
            if (failed) return l;
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:185:30: (disabled= 'DISABLE' )?
            int alt28=2;
            int LA28_0 = input.LA(1);

            if ( (LA28_0==53) ) {
                alt28=1;
            }
            switch (alt28) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:185:31: disabled= 'DISABLE'
                    {
                    disabled=input.LT(1);
                    match(input,53,FOLLOW_53_in_protectStatement992); if (failed) return l;

                    }
                    break;

            }

            pushFollow(FOLLOW_sequence_in_protectStatement1001);
            s=sequence();
            _fsp--;
            if (failed) return l;
            match(input,54,FOLLOW_54_in_protectStatement1005); if (failed) return l;
            if ( backtracking==0 ) {
              l = factory.createProtectStatement(startC,endC,id,disabled!=null,s);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return l;
    }
    // $ANTLR end protectStatement


    // $ANTLR start expression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:194:1: expression returns [Expression e] : x= letExpression ;
    public Expression expression() throws RecognitionException {
        Expression e = null;

        Expression x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:194:34: (x= letExpression )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:195:2: x= letExpression
            {
            pushFollow(FOLLOW_letExpression_in_expression1027);
            x=letExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end expression


    // $ANTLR start letExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:198:1: letExpression returns [Expression e] : ( 'let' v= identifier '=' varExpr= castedExpression ':' target= expression | x= castedExpression );
    public Expression letExpression() throws RecognitionException {
        Expression e = null;

        Identifier v = null;

        Expression varExpr = null;

        Expression target = null;

        Expression x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:198:39: ( 'let' v= identifier '=' varExpr= castedExpression ':' target= expression | x= castedExpression )
            int alt29=2;
            int LA29_0 = input.LA(1);

            if ( (LA29_0==55) ) {
                alt29=1;
            }
            else if ( ((LA29_0>=StringLiteral && LA29_0<=Identifier)||LA29_0==24||LA29_0==33||LA29_0==60||(LA29_0>=63 && LA29_0<=64)||LA29_0==79||(LA29_0>=81 && LA29_0<=94)||(LA29_0>=96 && LA29_0<=98)) ) {
                alt29=2;
            }
            else {
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("198:1: letExpression returns [Expression e] : ( 'let' v= identifier '=' varExpr= castedExpression ':' target= expression | x= castedExpression );", 29, 0, input);

                throw nvae;
            }
            switch (alt29) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:199:4: 'let' v= identifier '=' varExpr= castedExpression ':' target= expression
                    {
                    match(input,55,FOLLOW_55_in_letExpression1046); if (failed) return e;
                    pushFollow(FOLLOW_identifier_in_letExpression1050);
                    v=identifier();
                    _fsp--;
                    if (failed) return e;
                    match(input,56,FOLLOW_56_in_letExpression1052); if (failed) return e;
                    pushFollow(FOLLOW_castedExpression_in_letExpression1056);
                    varExpr=castedExpression();
                    _fsp--;
                    if (failed) return e;
                    match(input,57,FOLLOW_57_in_letExpression1058); if (failed) return e;
                    pushFollow(FOLLOW_expression_in_letExpression1062);
                    target=expression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =factory.createLetExpression(v,varExpr,target);
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:201:4: x= castedExpression
                    {
                    pushFollow(FOLLOW_castedExpression_in_letExpression1075);
                    x=castedExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end letExpression


    // $ANTLR start castedExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:204:1: castedExpression returns [Expression e] : ( ( '(' type ')' castedExpression )=> '(' t= type ')' x= chainExpression | x= chainExpression );
    public Expression castedExpression() throws RecognitionException {
        Expression e = null;

        Identifier t = null;

        Expression x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:204:41: ( ( '(' type ')' castedExpression )=> '(' t= type ')' x= chainExpression | x= chainExpression )
            int alt30=2;
            alt30 = dfa30.predict(input);
            switch (alt30) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:205:5: ( '(' type ')' castedExpression )=> '(' t= type ')' x= chainExpression
                    {
                    match(input,24,FOLLOW_24_in_castedExpression1106); if (failed) return e;
                    pushFollow(FOLLOW_type_in_castedExpression1110);
                    t=type();
                    _fsp--;
                    if (failed) return e;
                    match(input,27,FOLLOW_27_in_castedExpression1112); if (failed) return e;
                    pushFollow(FOLLOW_chainExpression_in_castedExpression1116);
                    x=chainExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e = factory.createCast(t,x);
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:207:4: x= chainExpression
                    {
                    pushFollow(FOLLOW_chainExpression_in_castedExpression1125);
                    x=chainExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end castedExpression


    // $ANTLR start chainExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:211:1: chainExpression returns [Expression e] : x= ifExpression ( '->' right= ifExpression )* ;
    public Expression chainExpression() throws RecognitionException {
        Expression e = null;

        Expression x = null;

        Expression right = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:211:41: (x= ifExpression ( '->' right= ifExpression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:212:2: x= ifExpression ( '->' right= ifExpression )*
            {
            pushFollow(FOLLOW_ifExpression_in_chainExpression1145);
            x=ifExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:212:25: ( '->' right= ifExpression )*
            loop31:
            do {
                int alt31=2;
                int LA31_0 = input.LA(1);

                if ( (LA31_0==58) ) {
                    alt31=1;
                }


                switch (alt31) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:212:27: '->' right= ifExpression
            	    {
            	    match(input,58,FOLLOW_58_in_chainExpression1151); if (failed) return e;
            	    pushFollow(FOLLOW_ifExpression_in_chainExpression1155);
            	    right=ifExpression();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	      e =factory.createChainExpression(e,right);
            	    }

            	    }
            	    break;

            	default :
            	    break loop31;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end chainExpression


    // $ANTLR start ifExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:215:1: ifExpression returns [Expression e] : (x= switchExpression ( '?' thenPart= switchExpression ':' elsePart= switchExpression )? | 'if' condition= switchExpression 'then' thenPart= switchExpression ( 'else' elsePart= expression )? );
    public Expression ifExpression() throws RecognitionException {
        Expression e = null;

        Expression x = null;

        Expression thenPart = null;

        Expression elsePart = null;

        Expression condition = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:215:38: (x= switchExpression ( '?' thenPart= switchExpression ':' elsePart= switchExpression )? | 'if' condition= switchExpression 'then' thenPart= switchExpression ( 'else' elsePart= expression )? )
            int alt34=2;
            int LA34_0 = input.LA(1);

            if ( ((LA34_0>=StringLiteral && LA34_0<=Identifier)||LA34_0==24||LA34_0==33||(LA34_0>=63 && LA34_0<=64)||LA34_0==79||(LA34_0>=81 && LA34_0<=94)||(LA34_0>=96 && LA34_0<=98)) ) {
                alt34=1;
            }
            else if ( (LA34_0==60) ) {
                alt34=2;
            }
            else {
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("215:1: ifExpression returns [Expression e] : (x= switchExpression ( '?' thenPart= switchExpression ':' elsePart= switchExpression )? | 'if' condition= switchExpression 'then' thenPart= switchExpression ( 'else' elsePart= expression )? );", 34, 0, input);

                throw nvae;
            }
            switch (alt34) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:216:2: x= switchExpression ( '?' thenPart= switchExpression ':' elsePart= switchExpression )?
                    {
                    pushFollow(FOLLOW_switchExpression_in_ifExpression1176);
                    x=switchExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:216:28: ( '?' thenPart= switchExpression ':' elsePart= switchExpression )?
                    int alt32=2;
                    int LA32_0 = input.LA(1);

                    if ( (LA32_0==59) ) {
                        alt32=1;
                    }
                    switch (alt32) {
                        case 1 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:216:29: '?' thenPart= switchExpression ':' elsePart= switchExpression
                            {
                            match(input,59,FOLLOW_59_in_ifExpression1180); if (failed) return e;
                            pushFollow(FOLLOW_switchExpression_in_ifExpression1184);
                            thenPart=switchExpression();
                            _fsp--;
                            if (failed) return e;
                            match(input,57,FOLLOW_57_in_ifExpression1186); if (failed) return e;
                            pushFollow(FOLLOW_switchExpression_in_ifExpression1190);
                            elsePart=switchExpression();
                            _fsp--;
                            if (failed) return e;
                            if ( backtracking==0 ) {
                              e =factory.createIf(e,thenPart,elsePart);
                            }

                            }
                            break;

                    }


                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:217:3: 'if' condition= switchExpression 'then' thenPart= switchExpression ( 'else' elsePart= expression )?
                    {
                    match(input,60,FOLLOW_60_in_ifExpression1198); if (failed) return e;
                    pushFollow(FOLLOW_switchExpression_in_ifExpression1202);
                    condition=switchExpression();
                    _fsp--;
                    if (failed) return e;
                    match(input,61,FOLLOW_61_in_ifExpression1204); if (failed) return e;
                    pushFollow(FOLLOW_switchExpression_in_ifExpression1208);
                    thenPart=switchExpression();
                    _fsp--;
                    if (failed) return e;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:217:68: ( 'else' elsePart= expression )?
                    int alt33=2;
                    int LA33_0 = input.LA(1);

                    if ( (LA33_0==62) ) {
                        alt33=1;
                    }
                    switch (alt33) {
                        case 1 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:217:69: 'else' elsePart= expression
                            {
                            match(input,62,FOLLOW_62_in_ifExpression1211); if (failed) return e;
                            pushFollow(FOLLOW_expression_in_ifExpression1215);
                            elsePart=expression();
                            _fsp--;
                            if (failed) return e;

                            }
                            break;

                    }

                    if ( backtracking==0 ) {
                      e =factory.createIf(condition,thenPart,elsePart);
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end ifExpression


    // $ANTLR start switchExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:221:1: switchExpression returns [Expression e=null] : ( 'switch' ( '(' pred= orExpression ')' )? '{' ( 'case' c= orExpression ':' v= orExpression )* 'default' ':' def= orExpression '}' | x= orExpression );
    public Expression switchExpression() throws RecognitionException {
        Expression e = null;

        Expression pred = null;

        Expression c = null;

        Expression v = null;

        Expression def = null;

        Expression x = null;


        List cases = new ArrayList();
        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:221:85: ( 'switch' ( '(' pred= orExpression ')' )? '{' ( 'case' c= orExpression ':' v= orExpression )* 'default' ':' def= orExpression '}' | x= orExpression )
            int alt37=2;
            int LA37_0 = input.LA(1);

            if ( (LA37_0==63) ) {
                alt37=1;
            }
            else if ( ((LA37_0>=StringLiteral && LA37_0<=Identifier)||LA37_0==24||LA37_0==33||LA37_0==64||LA37_0==79||(LA37_0>=81 && LA37_0<=94)||(LA37_0>=96 && LA37_0<=98)) ) {
                alt37=2;
            }
            else {
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("221:1: switchExpression returns [Expression e=null] : ( 'switch' ( '(' pred= orExpression ')' )? '{' ( 'case' c= orExpression ':' v= orExpression )* 'default' ':' def= orExpression '}' | x= orExpression );", 37, 0, input);

                throw nvae;
            }
            switch (alt37) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:222:4: 'switch' ( '(' pred= orExpression ')' )? '{' ( 'case' c= orExpression ':' v= orExpression )* 'default' ':' def= orExpression '}'
                    {
                    match(input,63,FOLLOW_63_in_switchExpression1242); if (failed) return e;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:222:13: ( '(' pred= orExpression ')' )?
                    int alt35=2;
                    int LA35_0 = input.LA(1);

                    if ( (LA35_0==24) ) {
                        alt35=1;
                    }
                    switch (alt35) {
                        case 1 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:222:14: '(' pred= orExpression ')'
                            {
                            match(input,24,FOLLOW_24_in_switchExpression1245); if (failed) return e;
                            pushFollow(FOLLOW_orExpression_in_switchExpression1251);
                            pred=orExpression();
                            _fsp--;
                            if (failed) return e;
                            match(input,27,FOLLOW_27_in_switchExpression1253); if (failed) return e;

                            }
                            break;

                    }

                    match(input,64,FOLLOW_64_in_switchExpression1260); if (failed) return e;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:224:4: ( 'case' c= orExpression ':' v= orExpression )*
                    loop36:
                    do {
                        int alt36=2;
                        int LA36_0 = input.LA(1);

                        if ( (LA36_0==65) ) {
                            alt36=1;
                        }


                        switch (alt36) {
                    	case 1 :
                    	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:225:6: 'case' c= orExpression ':' v= orExpression
                    	    {
                    	    match(input,65,FOLLOW_65_in_switchExpression1273); if (failed) return e;
                    	    pushFollow(FOLLOW_orExpression_in_switchExpression1277);
                    	    c=orExpression();
                    	    _fsp--;
                    	    if (failed) return e;
                    	    match(input,57,FOLLOW_57_in_switchExpression1280); if (failed) return e;
                    	    pushFollow(FOLLOW_orExpression_in_switchExpression1285);
                    	    v=orExpression();
                    	    _fsp--;
                    	    if (failed) return e;
                    	    if ( backtracking==0 ) {
                    	      cases.add(factory.createCase(c, v));
                    	    }

                    	    }
                    	    break;

                    	default :
                    	    break loop36;
                        }
                    } while (true);

                    match(input,66,FOLLOW_66_in_switchExpression1303); if (failed) return e;
                    match(input,57,FOLLOW_57_in_switchExpression1305); if (failed) return e;
                    pushFollow(FOLLOW_orExpression_in_switchExpression1311);
                    def=orExpression();
                    _fsp--;
                    if (failed) return e;
                    match(input,67,FOLLOW_67_in_switchExpression1316); if (failed) return e;
                    if ( backtracking==0 ) {
                      e = factory.createSwitchExpression(pred,cases,def);
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:231:4: x= orExpression
                    {
                    pushFollow(FOLLOW_orExpression_in_switchExpression1328);
                    x=orExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end switchExpression


    // $ANTLR start orExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:234:1: orExpression returns [Expression e] : x= andExpression (name= '||' r= andExpression )* ;
    public Expression orExpression() throws RecognitionException {
        Expression e = null;

        Token name=null;
        Expression x = null;

        Expression r = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:234:37: (x= andExpression (name= '||' r= andExpression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:235:4: x= andExpression (name= '||' r= andExpression )*
            {
            pushFollow(FOLLOW_andExpression_in_orExpression1348);
            x=andExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:235:28: (name= '||' r= andExpression )*
            loop38:
            do {
                int alt38=2;
                int LA38_0 = input.LA(1);

                if ( (LA38_0==68) ) {
                    alt38=1;
                }


                switch (alt38) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:235:29: name= '||' r= andExpression
            	    {
            	    name=input.LT(1);
            	    match(input,68,FOLLOW_68_in_orExpression1355); if (failed) return e;
            	    pushFollow(FOLLOW_andExpression_in_orExpression1359);
            	    r=andExpression();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	      e = factory.createBooleanOperation(id(name),e,r);
            	    }

            	    }
            	    break;

            	default :
            	    break loop38;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end orExpression


    // $ANTLR start andExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:238:1: andExpression returns [Expression e] : x= impliesExpression (name= '&&' r= impliesExpression )* ;
    public Expression andExpression() throws RecognitionException {
        Expression e = null;

        Token name=null;
        Expression x = null;

        Expression r = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:238:39: (x= impliesExpression (name= '&&' r= impliesExpression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:239:2: x= impliesExpression (name= '&&' r= impliesExpression )*
            {
            pushFollow(FOLLOW_impliesExpression_in_andExpression1382);
            x=impliesExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:239:30: (name= '&&' r= impliesExpression )*
            loop39:
            do {
                int alt39=2;
                int LA39_0 = input.LA(1);

                if ( (LA39_0==69) ) {
                    alt39=1;
                }


                switch (alt39) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:239:31: name= '&&' r= impliesExpression
            	    {
            	    name=input.LT(1);
            	    match(input,69,FOLLOW_69_in_andExpression1389); if (failed) return e;
            	    pushFollow(FOLLOW_impliesExpression_in_andExpression1393);
            	    r=impliesExpression();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	      e = factory.createBooleanOperation(id(name),e,r);
            	    }

            	    }
            	    break;

            	default :
            	    break loop39;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end andExpression


    // $ANTLR start impliesExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:242:1: impliesExpression returns [Expression e] : x= relationalExpression (name= 'implies' r= relationalExpression )* ;
    public Expression impliesExpression() throws RecognitionException {
        Expression e = null;

        Token name=null;
        Expression x = null;

        Expression r = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:242:42: (x= relationalExpression (name= 'implies' r= relationalExpression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:243:2: x= relationalExpression (name= 'implies' r= relationalExpression )*
            {
            pushFollow(FOLLOW_relationalExpression_in_impliesExpression1415);
            x=relationalExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:243:33: (name= 'implies' r= relationalExpression )*
            loop40:
            do {
                int alt40=2;
                int LA40_0 = input.LA(1);

                if ( (LA40_0==70) ) {
                    alt40=1;
                }


                switch (alt40) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:243:34: name= 'implies' r= relationalExpression
            	    {
            	    name=input.LT(1);
            	    match(input,70,FOLLOW_70_in_impliesExpression1422); if (failed) return e;
            	    pushFollow(FOLLOW_relationalExpression_in_impliesExpression1426);
            	    r=relationalExpression();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	      e = factory.createBooleanOperation(id(name),e,r);
            	    }

            	    }
            	    break;

            	default :
            	    break loop40;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end impliesExpression


    // $ANTLR start relationalExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:247:1: relationalExpression returns [Expression e] : x= additiveExpression (name= ( '==' | '!=' | '>=' | '<=' | '>' | '<' ) r= additiveExpression )* ;
    public Expression relationalExpression() throws RecognitionException {
        Expression e = null;

        Token name=null;
        Expression x = null;

        Expression r = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:247:45: (x= additiveExpression (name= ( '==' | '!=' | '>=' | '<=' | '>' | '<' ) r= additiveExpression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:248:2: x= additiveExpression (name= ( '==' | '!=' | '>=' | '<=' | '>' | '<' ) r= additiveExpression )*
            {
            pushFollow(FOLLOW_additiveExpression_in_relationalExpression1450);
            x=additiveExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:249:2: (name= ( '==' | '!=' | '>=' | '<=' | '>' | '<' ) r= additiveExpression )*
            loop41:
            do {
                int alt41=2;
                int LA41_0 = input.LA(1);

                if ( ((LA41_0>=71 && LA41_0<=76)) ) {
                    alt41=1;
                }


                switch (alt41) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:249:3: name= ( '==' | '!=' | '>=' | '<=' | '>' | '<' ) r= additiveExpression
            	    {
            	    name=input.LT(1);
            	    if ( (input.LA(1)>=71 && input.LA(1)<=76) ) {
            	        input.consume();
            	        errorRecovery=false;failed=false;
            	    }
            	    else {
            	        if (backtracking>0) {failed=true; return e;}
            	        MismatchedSetException mse =
            	            new MismatchedSetException(null,input);
            	        recoverFromMismatchedSet(input,mse,FOLLOW_set_in_relationalExpression1458);    throw mse;
            	    }

            	    pushFollow(FOLLOW_additiveExpression_in_relationalExpression1484);
            	    r=additiveExpression();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	      e = factory.createBinaryOperation(id(name),e,r);
            	    }

            	    }
            	    break;

            	default :
            	    break loop41;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end relationalExpression


    // $ANTLR start additiveExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:253:1: additiveExpression returns [Expression e] : x= multiplicativeExpression (name= ( '+' | '-' ) r= multiplicativeExpression )* ;
    public Expression additiveExpression() throws RecognitionException {
        Expression e = null;

        Token name=null;
        Expression x = null;

        Expression r = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:253:43: (x= multiplicativeExpression (name= ( '+' | '-' ) r= multiplicativeExpression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:254:2: x= multiplicativeExpression (name= ( '+' | '-' ) r= multiplicativeExpression )*
            {
            pushFollow(FOLLOW_multiplicativeExpression_in_additiveExpression1505);
            x=multiplicativeExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:255:4: (name= ( '+' | '-' ) r= multiplicativeExpression )*
            loop42:
            do {
                int alt42=2;
                int LA42_0 = input.LA(1);

                if ( (LA42_0==33) ) {
                    int LA42_2 = input.LA(2);

                    if ( ((LA42_2>=StringLiteral && LA42_2<=Identifier)||LA42_2==24||LA42_2==33||LA42_2==64||LA42_2==79||(LA42_2>=81 && LA42_2<=94)||(LA42_2>=96 && LA42_2<=98)) ) {
                        alt42=1;
                    }


                }
                else if ( (LA42_0==77) ) {
                    alt42=1;
                }


                switch (alt42) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:255:5: name= ( '+' | '-' ) r= multiplicativeExpression
            	    {
            	    name=input.LT(1);
            	    if ( input.LA(1)==33||input.LA(1)==77 ) {
            	        input.consume();
            	        errorRecovery=false;failed=false;
            	    }
            	    else {
            	        if (backtracking>0) {failed=true; return e;}
            	        MismatchedSetException mse =
            	            new MismatchedSetException(null,input);
            	        recoverFromMismatchedSet(input,mse,FOLLOW_set_in_additiveExpression1515);    throw mse;
            	    }

            	    pushFollow(FOLLOW_multiplicativeExpression_in_additiveExpression1524);
            	    r=multiplicativeExpression();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	      e = factory.createBinaryOperation(id(name),e,r);
            	    }

            	    }
            	    break;

            	default :
            	    break loop42;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end additiveExpression


    // $ANTLR start multiplicativeExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:258:1: multiplicativeExpression returns [Expression e] : x= unaryExpression (name= ( '*' | '/' ) r= unaryExpression )* ;
    public Expression multiplicativeExpression() throws RecognitionException {
        Expression e = null;

        Token name=null;
        Expression x = null;

        Expression r = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:258:48: (x= unaryExpression (name= ( '*' | '/' ) r= unaryExpression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:259:2: x= unaryExpression (name= ( '*' | '/' ) r= unaryExpression )*
            {
            pushFollow(FOLLOW_unaryExpression_in_multiplicativeExpression1543);
            x=unaryExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:260:2: (name= ( '*' | '/' ) r= unaryExpression )*
            loop43:
            do {
                int alt43=2;
                int LA43_0 = input.LA(1);

                if ( (LA43_0==26||LA43_0==78) ) {
                    alt43=1;
                }


                switch (alt43) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:260:3: name= ( '*' | '/' ) r= unaryExpression
            	    {
            	    name=input.LT(1);
            	    if ( input.LA(1)==26||input.LA(1)==78 ) {
            	        input.consume();
            	        errorRecovery=false;failed=false;
            	    }
            	    else {
            	        if (backtracking>0) {failed=true; return e;}
            	        MismatchedSetException mse =
            	            new MismatchedSetException(null,input);
            	        recoverFromMismatchedSet(input,mse,FOLLOW_set_in_multiplicativeExpression1551);    throw mse;
            	    }

            	    pushFollow(FOLLOW_unaryExpression_in_multiplicativeExpression1561);
            	    r=unaryExpression();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	      e = factory.createBinaryOperation(id(name),e,r);
            	    }

            	    }
            	    break;

            	default :
            	    break loop43;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end multiplicativeExpression


    // $ANTLR start unaryExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:264:1: unaryExpression returns [Expression e] : (x= infixExpression | name= '!' x= infixExpression | name= '-' x= infixExpression );
    public Expression unaryExpression() throws RecognitionException {
        Expression e = null;

        Token name=null;
        Expression x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:264:40: (x= infixExpression | name= '!' x= infixExpression | name= '-' x= infixExpression )
            int alt44=3;
            switch ( input.LA(1) ) {
            case StringLiteral:
            case IntLiteral:
            case Identifier:
            case 24:
            case 64:
            case 81:
            case 82:
            case 83:
            case 84:
            case 85:
            case 86:
            case 87:
            case 88:
            case 89:
            case 90:
            case 91:
            case 92:
            case 93:
            case 94:
            case 96:
            case 97:
            case 98:
                {
                alt44=1;
                }
                break;
            case 79:
                {
                alt44=2;
                }
                break;
            case 33:
                {
                alt44=3;
                }
                break;
            default:
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("264:1: unaryExpression returns [Expression e] : (x= infixExpression | name= '!' x= infixExpression | name= '-' x= infixExpression );", 44, 0, input);

                throw nvae;
            }

            switch (alt44) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:265:2: x= infixExpression
                    {
                    pushFollow(FOLLOW_infixExpression_in_unaryExpression1582);
                    x=infixExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:266:3: name= '!' x= infixExpression
                    {
                    name=input.LT(1);
                    match(input,79,FOLLOW_79_in_unaryExpression1590); if (failed) return e;
                    pushFollow(FOLLOW_infixExpression_in_unaryExpression1594);
                    x=infixExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e = factory.createOperationCall(id(name),x);
                    }

                    }
                    break;
                case 3 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:267:3: name= '-' x= infixExpression
                    {
                    name=input.LT(1);
                    match(input,33,FOLLOW_33_in_unaryExpression1602); if (failed) return e;
                    pushFollow(FOLLOW_infixExpression_in_unaryExpression1606);
                    x=infixExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e = factory.createOperationCall(id(name),x);
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end unaryExpression


    // $ANTLR start infixExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:270:1: infixExpression returns [Expression e] : x= primaryExpression ( '.' op= featureCall )* ;
    public Expression infixExpression() throws RecognitionException {
        Expression e = null;

        Expression x = null;

        FeatureCall op = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:270:40: (x= primaryExpression ( '.' op= featureCall )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:271:2: x= primaryExpression ( '.' op= featureCall )*
            {
            pushFollow(FOLLOW_primaryExpression_in_infixExpression1624);
            x=primaryExpression();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:271:30: ( '.' op= featureCall )*
            loop45:
            do {
                int alt45=2;
                int LA45_0 = input.LA(1);

                if ( (LA45_0==80) ) {
                    alt45=1;
                }


                switch (alt45) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:271:32: '.' op= featureCall
            	    {
            	    match(input,80,FOLLOW_80_in_infixExpression1630); if (failed) return e;
            	    pushFollow(FOLLOW_featureCall_in_infixExpression1634);
            	    op=featureCall();
            	    _fsp--;
            	    if (failed) return e;
            	    if ( backtracking==0 ) {
            	       if (op!=null) { op.setTarget(e);e =op; }
            	    }

            	    }
            	    break;

            	default :
            	    break loop45;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end infixExpression


    // $ANTLR start primaryExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:274:1: primaryExpression returns [Expression e] : (c= StringLiteral | x= featureCall | x= booleanLiteral | x= numberLiteral | x= nullLiteral | x= listLiteral | x= constructorCall | x= globalVarExpression | x= paranthesizedExpression );
    public Expression primaryExpression() throws RecognitionException {
        Expression e = null;

        Token c=null;
        Expression x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:274:44: (c= StringLiteral | x= featureCall | x= booleanLiteral | x= numberLiteral | x= nullLiteral | x= listLiteral | x= constructorCall | x= globalVarExpression | x= paranthesizedExpression )
            int alt46=9;
            switch ( input.LA(1) ) {
            case StringLiteral:
                {
                alt46=1;
                }
                break;
            case Identifier:
            case 86:
            case 87:
            case 88:
            case 89:
            case 90:
            case 91:
            case 92:
            case 93:
            case 94:
            case 96:
            case 97:
            case 98:
                {
                alt46=2;
                }
                break;
            case 83:
            case 84:
                {
                alt46=3;
                }
                break;
            case IntLiteral:
                {
                alt46=4;
                }
                break;
            case 85:
                {
                alt46=5;
                }
                break;
            case 64:
                {
                alt46=6;
                }
                break;
            case 82:
                {
                alt46=7;
                }
                break;
            case 81:
                {
                alt46=8;
                }
                break;
            case 24:
                {
                alt46=9;
                }
                break;
            default:
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("274:1: primaryExpression returns [Expression e] : (c= StringLiteral | x= featureCall | x= booleanLiteral | x= numberLiteral | x= nullLiteral | x= listLiteral | x= constructorCall | x= globalVarExpression | x= paranthesizedExpression );", 46, 0, input);

                throw nvae;
            }

            switch (alt46) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:275:4: c= StringLiteral
                    {
                    c=input.LT(1);
                    match(input,StringLiteral,FOLLOW_StringLiteral_in_primaryExpression1660); if (failed) return e;
                    if ( backtracking==0 ) {
                       e = factory.createStringLiteral(id(c));
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:276:5: x= featureCall
                    {
                    pushFollow(FOLLOW_featureCall_in_primaryExpression1671);
                    x=featureCall();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 3 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:277:5: x= booleanLiteral
                    {
                    pushFollow(FOLLOW_booleanLiteral_in_primaryExpression1681);
                    x=booleanLiteral();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 4 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:278:5: x= numberLiteral
                    {
                    pushFollow(FOLLOW_numberLiteral_in_primaryExpression1691);
                    x=numberLiteral();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 5 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:279:5: x= nullLiteral
                    {
                    pushFollow(FOLLOW_nullLiteral_in_primaryExpression1701);
                    x=nullLiteral();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 6 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:280:5: x= listLiteral
                    {
                    pushFollow(FOLLOW_listLiteral_in_primaryExpression1711);
                    x=listLiteral();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 7 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:281:5: x= constructorCall
                    {
                    pushFollow(FOLLOW_constructorCall_in_primaryExpression1721);
                    x=constructorCall();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 8 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:282:5: x= globalVarExpression
                    {
                    pushFollow(FOLLOW_globalVarExpression_in_primaryExpression1731);
                    x=globalVarExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;
                case 9 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:283:5: x= paranthesizedExpression
                    {
                    pushFollow(FOLLOW_paranthesizedExpression_in_primaryExpression1741);
                    x=paranthesizedExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end primaryExpression


    // $ANTLR start paranthesizedExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:286:1: paranthesizedExpression returns [Expression e] : '(' x= expression ')' ;
    public Expression paranthesizedExpression() throws RecognitionException {
        Expression e = null;

        Expression x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:286:48: ( '(' x= expression ')' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:287:5: '(' x= expression ')'
            {
            match(input,24,FOLLOW_24_in_paranthesizedExpression1760); if (failed) return e;
            pushFollow(FOLLOW_expression_in_paranthesizedExpression1764);
            x=expression();
            _fsp--;
            if (failed) return e;
            match(input,27,FOLLOW_27_in_paranthesizedExpression1766); if (failed) return e;
            if ( backtracking==0 ) {
              e =factory.createParanthesizedExpression(x);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end paranthesizedExpression


    // $ANTLR start globalVarExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:290:1: globalVarExpression returns [GlobalVarExpression e] : 'GLOBALVAR' name= identifier ;
    public GlobalVarExpression globalVarExpression() throws RecognitionException {
        GlobalVarExpression e = null;

        Identifier name = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:290:54: ( 'GLOBALVAR' name= identifier )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:291:5: 'GLOBALVAR' name= identifier
            {
            match(input,81,FOLLOW_81_in_globalVarExpression1786); if (failed) return e;
            pushFollow(FOLLOW_identifier_in_globalVarExpression1790);
            name=identifier();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e = factory.createGlobalVarExpression(name);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end globalVarExpression


    // $ANTLR start featureCall
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:293:1: featureCall returns [FeatureCall e] : (id1= identifier '(' (l= parameterList )? ')' | t= type | x= collectionExpression );
    public FeatureCall featureCall() throws RecognitionException {
        FeatureCall e = null;

        Identifier id1 = null;

        List<Expression> l = null;

        Identifier t = null;

        FeatureCall x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:293:38: (id1= identifier '(' (l= parameterList )? ')' | t= type | x= collectionExpression )
            int alt48=3;
            switch ( input.LA(1) ) {
            case Identifier:
                {
                int LA48_1 = input.LA(2);

                if ( (LA48_1==EOF||LA48_1==TEXT||LA48_1==Identifier||(LA48_1>=25 && LA48_1<=27)||LA48_1==30||LA48_1==33||LA48_1==37||LA48_1==40||(LA48_1>=51 && LA48_1<=53)||(LA48_1>=57 && LA48_1<=59)||(LA48_1>=61 && LA48_1<=62)||(LA48_1>=65 && LA48_1<=78)||LA48_1==80) ) {
                    alt48=2;
                }
                else if ( (LA48_1==24) ) {
                    alt48=1;
                }
                else {
                    if (backtracking>0) {failed=true; return e;}
                    NoViableAltException nvae =
                        new NoViableAltException("293:1: featureCall returns [FeatureCall e] : (id1= identifier '(' (l= parameterList )? ')' | t= type | x= collectionExpression );", 48, 1, input);

                    throw nvae;
                }
                }
                break;
            case 96:
            case 97:
            case 98:
                {
                alt48=2;
                }
                break;
            case 86:
            case 87:
            case 88:
            case 89:
            case 90:
            case 91:
            case 92:
            case 93:
            case 94:
                {
                alt48=3;
                }
                break;
            default:
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("293:1: featureCall returns [FeatureCall e] : (id1= identifier '(' (l= parameterList )? ')' | t= type | x= collectionExpression );", 48, 0, input);

                throw nvae;
            }

            switch (alt48) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:294:2: id1= identifier '(' (l= parameterList )? ')'
                    {
                    pushFollow(FOLLOW_identifier_in_featureCall1808);
                    id1=identifier();
                    _fsp--;
                    if (failed) return e;
                    match(input,24,FOLLOW_24_in_featureCall1810); if (failed) return e;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:294:21: (l= parameterList )?
                    int alt47=2;
                    int LA47_0 = input.LA(1);

                    if ( ((LA47_0>=StringLiteral && LA47_0<=Identifier)||LA47_0==24||LA47_0==33||LA47_0==55||LA47_0==60||(LA47_0>=63 && LA47_0<=64)||LA47_0==79||(LA47_0>=81 && LA47_0<=94)||(LA47_0>=96 && LA47_0<=98)) ) {
                        alt47=1;
                    }
                    switch (alt47) {
                        case 1 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:294:22: l= parameterList
                            {
                            pushFollow(FOLLOW_parameterList_in_featureCall1815);
                            l=parameterList();
                            _fsp--;
                            if (failed) return e;

                            }
                            break;

                    }

                    match(input,27,FOLLOW_27_in_featureCall1819); if (failed) return e;
                    if ( backtracking==0 ) {
                      e = factory.createOperationCall(id1,l);
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:295:5: t= type
                    {
                    pushFollow(FOLLOW_type_in_featureCall1829);
                    t=type();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =factory.createFeatureCall(t,null);
                    }

                    }
                    break;
                case 3 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:296:5: x= collectionExpression
                    {
                    pushFollow(FOLLOW_collectionExpression_in_featureCall1840);
                    x=collectionExpression();
                    _fsp--;
                    if (failed) return e;
                    if ( backtracking==0 ) {
                      e =x;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end featureCall


    // $ANTLR start listLiteral
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:299:1: listLiteral returns [Expression e] : '{' (l= parameterList )? '}' ;
    public Expression listLiteral() throws RecognitionException {
        Expression e = null;

        List<Expression> l = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:299:37: ( '{' (l= parameterList )? '}' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:300:2: '{' (l= parameterList )? '}'
            {
            match(input,64,FOLLOW_64_in_listLiteral1857); if (failed) return e;
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:300:6: (l= parameterList )?
            int alt49=2;
            int LA49_0 = input.LA(1);

            if ( ((LA49_0>=StringLiteral && LA49_0<=Identifier)||LA49_0==24||LA49_0==33||LA49_0==55||LA49_0==60||(LA49_0>=63 && LA49_0<=64)||LA49_0==79||(LA49_0>=81 && LA49_0<=94)||(LA49_0>=96 && LA49_0<=98)) ) {
                alt49=1;
            }
            switch (alt49) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:300:7: l= parameterList
                    {
                    pushFollow(FOLLOW_parameterList_in_listLiteral1862);
                    l=parameterList();
                    _fsp--;
                    if (failed) return e;

                    }
                    break;

            }

            match(input,67,FOLLOW_67_in_listLiteral1866); if (failed) return e;
            if ( backtracking==0 ) {
              e =factory.createListLiteral(l);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end listLiteral


    // $ANTLR start constructorCall
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:303:1: constructorCall returns [Expression e] : 'new' t= simpleType ;
    public Expression constructorCall() throws RecognitionException {
        Expression e = null;

        Identifier t = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:303:41: ( 'new' t= simpleType )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:304:2: 'new' t= simpleType
            {
            match(input,82,FOLLOW_82_in_constructorCall1883); if (failed) return e;
            pushFollow(FOLLOW_simpleType_in_constructorCall1887);
            t=simpleType();
            _fsp--;
            if (failed) return e;
            if ( backtracking==0 ) {
              e = factory.createConstructorCall(t);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end constructorCall


    // $ANTLR start booleanLiteral
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:308:1: booleanLiteral returns [Expression e=factory.createBooleanLiteral(id(input.LT(1)))] : ( 'false' | 'true' );
    public Expression booleanLiteral() throws RecognitionException {
        Expression e = factory.createBooleanLiteral(id(input.LT(1)));

        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:308:86: ( 'false' | 'true' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:
            {
            if ( (input.LA(1)>=83 && input.LA(1)<=84) ) {
                input.consume();
                errorRecovery=false;failed=false;
            }
            else {
                if (backtracking>0) {failed=true; return e;}
                MismatchedSetException mse =
                    new MismatchedSetException(null,input);
                recoverFromMismatchedSet(input,mse,FOLLOW_set_in_booleanLiteral0);    throw mse;
            }


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end booleanLiteral


    // $ANTLR start nullLiteral
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:312:1: nullLiteral returns [Expression e=factory.createNullLiteral(id(input.LT(1)))] : 'null' ;
    public Expression nullLiteral() throws RecognitionException {
        Expression e = factory.createNullLiteral(id(input.LT(1)));

        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:312:80: ( 'null' )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:313:2: 'null'
            {
            match(input,85,FOLLOW_85_in_nullLiteral1922); if (failed) return e;

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end nullLiteral


    // $ANTLR start numberLiteral
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:316:1: numberLiteral returns [Expression e] : (a= IntLiteral | a= IntLiteral b= '.' c= IntLiteral );
    public Expression numberLiteral() throws RecognitionException {
        Expression e = null;

        Token a=null;
        Token b=null;
        Token c=null;

        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:316:39: (a= IntLiteral | a= IntLiteral b= '.' c= IntLiteral )
            int alt50=2;
            int LA50_0 = input.LA(1);

            if ( (LA50_0==IntLiteral) ) {
                int LA50_1 = input.LA(2);

                if ( (LA50_1==80) ) {
                    int LA50_2 = input.LA(3);

                    if ( (LA50_2==IntLiteral) ) {
                        alt50=2;
                    }
                    else if ( (LA50_2==Identifier||(LA50_2>=86 && LA50_2<=94)||(LA50_2>=96 && LA50_2<=98)) ) {
                        alt50=1;
                    }
                    else {
                        if (backtracking>0) {failed=true; return e;}
                        NoViableAltException nvae =
                            new NoViableAltException("316:1: numberLiteral returns [Expression e] : (a= IntLiteral | a= IntLiteral b= '.' c= IntLiteral );", 50, 2, input);

                        throw nvae;
                    }
                }
                else if ( (LA50_1==EOF||LA50_1==TEXT||LA50_1==Identifier||(LA50_1>=25 && LA50_1<=27)||LA50_1==33||LA50_1==37||LA50_1==40||(LA50_1>=51 && LA50_1<=53)||(LA50_1>=57 && LA50_1<=59)||(LA50_1>=61 && LA50_1<=62)||(LA50_1>=65 && LA50_1<=78)) ) {
                    alt50=1;
                }
                else {
                    if (backtracking>0) {failed=true; return e;}
                    NoViableAltException nvae =
                        new NoViableAltException("316:1: numberLiteral returns [Expression e] : (a= IntLiteral | a= IntLiteral b= '.' c= IntLiteral );", 50, 1, input);

                    throw nvae;
                }
            }
            else {
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("316:1: numberLiteral returns [Expression e] : (a= IntLiteral | a= IntLiteral b= '.' c= IntLiteral );", 50, 0, input);

                throw nvae;
            }
            switch (alt50) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:317:4: a= IntLiteral
                    {
                    a=input.LT(1);
                    match(input,IntLiteral,FOLLOW_IntLiteral_in_numberLiteral1941); if (failed) return e;
                    if ( backtracking==0 ) {
                      e =factory.createIntegerLiteral(id(a));
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:318:4: a= IntLiteral b= '.' c= IntLiteral
                    {
                    a=input.LT(1);
                    match(input,IntLiteral,FOLLOW_IntLiteral_in_numberLiteral1950); if (failed) return e;
                    b=input.LT(1);
                    match(input,80,FOLLOW_80_in_numberLiteral1954); if (failed) return e;
                    c=input.LT(1);
                    match(input,IntLiteral,FOLLOW_IntLiteral_in_numberLiteral1958); if (failed) return e;
                    if ( backtracking==0 ) {
                      e =factory.createRealLiteral(id(a).append(id(b)).append(id(c)));
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end numberLiteral


    // $ANTLR start collectionExpression
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:321:1: collectionExpression returns [FeatureCall e] : (name= 'typeSelect' '(' t= type ')' | name= ( 'collect' | 'select' | 'selectFirst' | 'reject' | 'exists' | 'notExists' | 'sortBy' | 'forAll' ) '(' (var= identifier '|' )? x= expression ')' );
    public FeatureCall collectionExpression() throws RecognitionException {
        FeatureCall e = null;

        Token name=null;
        Identifier t = null;

        Identifier var = null;

        Expression x = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:321:47: (name= 'typeSelect' '(' t= type ')' | name= ( 'collect' | 'select' | 'selectFirst' | 'reject' | 'exists' | 'notExists' | 'sortBy' | 'forAll' ) '(' (var= identifier '|' )? x= expression ')' )
            int alt52=2;
            int LA52_0 = input.LA(1);

            if ( (LA52_0==86) ) {
                alt52=1;
            }
            else if ( ((LA52_0>=87 && LA52_0<=94)) ) {
                alt52=2;
            }
            else {
                if (backtracking>0) {failed=true; return e;}
                NoViableAltException nvae =
                    new NoViableAltException("321:1: collectionExpression returns [FeatureCall e] : (name= 'typeSelect' '(' t= type ')' | name= ( 'collect' | 'select' | 'selectFirst' | 'reject' | 'exists' | 'notExists' | 'sortBy' | 'forAll' ) '(' (var= identifier '|' )? x= expression ')' );", 52, 0, input);

                throw nvae;
            }
            switch (alt52) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:322:3: name= 'typeSelect' '(' t= type ')'
                    {
                    name=input.LT(1);
                    match(input,86,FOLLOW_86_in_collectionExpression1978); if (failed) return e;
                    match(input,24,FOLLOW_24_in_collectionExpression1982); if (failed) return e;
                    pushFollow(FOLLOW_type_in_collectionExpression1986);
                    t=type();
                    _fsp--;
                    if (failed) return e;
                    match(input,27,FOLLOW_27_in_collectionExpression1988); if (failed) return e;
                    if ( backtracking==0 ) {
                       e = factory.createTypeSelectExpression(id(name),t);
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:325:5: name= ( 'collect' | 'select' | 'selectFirst' | 'reject' | 'exists' | 'notExists' | 'sortBy' | 'forAll' ) '(' (var= identifier '|' )? x= expression ')'
                    {
                    name=input.LT(1);
                    if ( (input.LA(1)>=87 && input.LA(1)<=94) ) {
                        input.consume();
                        errorRecovery=false;failed=false;
                    }
                    else {
                        if (backtracking>0) {failed=true; return e;}
                        MismatchedSetException mse =
                            new MismatchedSetException(null,input);
                        recoverFromMismatchedSet(input,mse,FOLLOW_set_in_collectionExpression2001);    throw mse;
                    }

                    match(input,24,FOLLOW_24_in_collectionExpression2051); if (failed) return e;
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:332:19: (var= identifier '|' )?
                    int alt51=2;
                    int LA51_0 = input.LA(1);

                    if ( (LA51_0==Identifier) ) {
                        int LA51_1 = input.LA(2);

                        if ( (LA51_1==95) ) {
                            alt51=1;
                        }
                    }
                    switch (alt51) {
                        case 1 :
                            // src/org/eclipse/internal/xpand2/parser/Xpand.g:332:20: var= identifier '|'
                            {
                            pushFollow(FOLLOW_identifier_in_collectionExpression2056);
                            var=identifier();
                            _fsp--;
                            if (failed) return e;
                            match(input,95,FOLLOW_95_in_collectionExpression2058); if (failed) return e;

                            }
                            break;

                    }

                    pushFollow(FOLLOW_expression_in_collectionExpression2064);
                    x=expression();
                    _fsp--;
                    if (failed) return e;
                    match(input,27,FOLLOW_27_in_collectionExpression2066); if (failed) return e;
                    if ( backtracking==0 ) {
                       e = factory.createCollectionExpression(id(name),var,x);
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return e;
    }
    // $ANTLR end collectionExpression


    // $ANTLR start declaredParameterList
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:338:1: declaredParameterList returns [List<DeclaredParameter> l = new ArrayList<DeclaredParameter>()] : dp= declaredParameter ( ',' dp1= declaredParameter )* ;
    public List<DeclaredParameter> declaredParameterList() throws RecognitionException {
        List<DeclaredParameter> l =  new ArrayList<DeclaredParameter>();

        DeclaredParameter dp = null;

        DeclaredParameter dp1 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:338:97: (dp= declaredParameter ( ',' dp1= declaredParameter )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:339:2: dp= declaredParameter ( ',' dp1= declaredParameter )*
            {
            pushFollow(FOLLOW_declaredParameter_in_declaredParameterList2090);
            dp=declaredParameter();
            _fsp--;
            if (failed) return l;
            if ( backtracking==0 ) {
              l.add(dp);
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:339:36: ( ',' dp1= declaredParameter )*
            loop53:
            do {
                int alt53=2;
                int LA53_0 = input.LA(1);

                if ( (LA53_0==25) ) {
                    int LA53_1 = input.LA(2);

                    if ( (LA53_1==Identifier||(LA53_1>=96 && LA53_1<=98)) ) {
                        alt53=1;
                    }


                }


                switch (alt53) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:339:37: ',' dp1= declaredParameter
            	    {
            	    match(input,25,FOLLOW_25_in_declaredParameterList2094); if (failed) return l;
            	    pushFollow(FOLLOW_declaredParameter_in_declaredParameterList2098);
            	    dp1=declaredParameter();
            	    _fsp--;
            	    if (failed) return l;
            	    if ( backtracking==0 ) {
            	      l.add(dp1);
            	    }

            	    }
            	    break;

            	default :
            	    break loop53;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return l;
    }
    // $ANTLR end declaredParameterList


    // $ANTLR start declaredParameter
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:342:1: declaredParameter returns [DeclaredParameter dp] : t= type name= identifier ;
    public DeclaredParameter declaredParameter() throws RecognitionException {
        DeclaredParameter dp = null;

        Identifier t = null;

        Identifier name = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:342:50: (t= type name= identifier )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:343:2: t= type name= identifier
            {
            pushFollow(FOLLOW_type_in_declaredParameter2118);
            t=type();
            _fsp--;
            if (failed) return dp;
            pushFollow(FOLLOW_identifier_in_declaredParameter2122);
            name=identifier();
            _fsp--;
            if (failed) return dp;
            if ( backtracking==0 ) {
              dp = factory.createDeclaredParameter(t,name);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return dp;
    }
    // $ANTLR end declaredParameter


    // $ANTLR start parameterList
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:346:1: parameterList returns [List<Expression> list = new ArrayList<Expression>()] : a= expression ( ',' b= expression )* ;
    public List<Expression> parameterList() throws RecognitionException {
        List<Expression> list =  new ArrayList<Expression>();

        Expression a = null;

        Expression b = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:346:78: (a= expression ( ',' b= expression )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:347:5: a= expression ( ',' b= expression )*
            {
            pushFollow(FOLLOW_expression_in_parameterList2144);
            a=expression();
            _fsp--;
            if (failed) return list;
            if ( backtracking==0 ) {
              list.add(a);
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:347:34: ( ',' b= expression )*
            loop54:
            do {
                int alt54=2;
                int LA54_0 = input.LA(1);

                if ( (LA54_0==25) ) {
                    alt54=1;
                }


                switch (alt54) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:347:35: ',' b= expression
            	    {
            	    match(input,25,FOLLOW_25_in_parameterList2149); if (failed) return list;
            	    pushFollow(FOLLOW_expression_in_parameterList2153);
            	    b=expression();
            	    _fsp--;
            	    if (failed) return list;
            	    if ( backtracking==0 ) {
            	      list.add(b);
            	    }

            	    }
            	    break;

            	default :
            	    break loop54;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return list;
    }
    // $ANTLR end parameterList


    // $ANTLR start type
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:352:1: type returns [Identifier id] : (a= collectionType | b= simpleType );
    public Identifier type() throws RecognitionException {
        Identifier id = null;

        Identifier a = null;

        Identifier b = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:352:30: (a= collectionType | b= simpleType )
            int alt55=2;
            int LA55_0 = input.LA(1);

            if ( ((LA55_0>=96 && LA55_0<=98)) ) {
                alt55=1;
            }
            else if ( (LA55_0==Identifier) ) {
                alt55=2;
            }
            else {
                if (backtracking>0) {failed=true; return id;}
                NoViableAltException nvae =
                    new NoViableAltException("352:1: type returns [Identifier id] : (a= collectionType | b= simpleType );", 55, 0, input);

                throw nvae;
            }
            switch (alt55) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:353:2: a= collectionType
                    {
                    pushFollow(FOLLOW_collectionType_in_type2179);
                    a=collectionType();
                    _fsp--;
                    if (failed) return id;
                    if ( backtracking==0 ) {
                      id =a;
                    }

                    }
                    break;
                case 2 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:354:2: b= simpleType
                    {
                    pushFollow(FOLLOW_simpleType_in_type2189);
                    b=simpleType();
                    _fsp--;
                    if (failed) return id;
                    if ( backtracking==0 ) {
                      id =b;
                    }

                    }
                    break;

            }
        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return id;
    }
    // $ANTLR end type


    // $ANTLR start collectionType
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:357:1: collectionType returns [Identifier id ] : cl= ( 'Collection' | 'List' | 'Set' ) (b= '[' id1= simpleType c= ']' )? ;
    public Identifier collectionType() throws RecognitionException {
        Identifier id = null;

        Token cl=null;
        Token b=null;
        Token c=null;
        Identifier id1 = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:357:42: (cl= ( 'Collection' | 'List' | 'Set' ) (b= '[' id1= simpleType c= ']' )? )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:358:3: cl= ( 'Collection' | 'List' | 'Set' ) (b= '[' id1= simpleType c= ']' )?
            {
            cl=input.LT(1);
            if ( (input.LA(1)>=96 && input.LA(1)<=98) ) {
                input.consume();
                errorRecovery=false;failed=false;
            }
            else {
                if (backtracking>0) {failed=true; return id;}
                MismatchedSetException mse =
                    new MismatchedSetException(null,input);
                recoverFromMismatchedSet(input,mse,FOLLOW_set_in_collectionType2211);    throw mse;
            }

            if ( backtracking==0 ) {
              id = id(cl);
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:359:3: (b= '[' id1= simpleType c= ']' )?
            int alt56=2;
            int LA56_0 = input.LA(1);

            if ( (LA56_0==99) ) {
                alt56=1;
            }
            switch (alt56) {
                case 1 :
                    // src/org/eclipse/internal/xpand2/parser/Xpand.g:359:4: b= '[' id1= simpleType c= ']'
                    {
                    b=input.LT(1);
                    match(input,99,FOLLOW_99_in_collectionType2232); if (failed) return id;
                    pushFollow(FOLLOW_simpleType_in_collectionType2236);
                    id1=simpleType();
                    _fsp--;
                    if (failed) return id;
                    c=input.LT(1);
                    match(input,100,FOLLOW_100_in_collectionType2240); if (failed) return id;
                    if ( backtracking==0 ) {
                       id.append(id(b));id.append(id1);id.append(id(c));
                    }

                    }
                    break;

            }


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return id;
    }
    // $ANTLR end collectionType


    // $ANTLR start simpleType
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:362:1: simpleType returns [Identifier id] : x= identifier (d= '::' end= identifier )* ;
    public Identifier simpleType() throws RecognitionException {
        Identifier id = null;

        Token d=null;
        Identifier x = null;

        Identifier end = null;


        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:362:36: (x= identifier (d= '::' end= identifier )* )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:363:2: x= identifier (d= '::' end= identifier )*
            {
            pushFollow(FOLLOW_identifier_in_simpleType2260);
            x=identifier();
            _fsp--;
            if (failed) return id;
            if ( backtracking==0 ) {
              id =x;
            }
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:364:2: (d= '::' end= identifier )*
            loop57:
            do {
                int alt57=2;
                int LA57_0 = input.LA(1);

                if ( (LA57_0==30) ) {
                    alt57=1;
                }


                switch (alt57) {
            	case 1 :
            	    // src/org/eclipse/internal/xpand2/parser/Xpand.g:364:3: d= '::' end= identifier
            	    {
            	    d=input.LT(1);
            	    match(input,30,FOLLOW_30_in_simpleType2268); if (failed) return id;
            	    pushFollow(FOLLOW_identifier_in_simpleType2272);
            	    end=identifier();
            	    _fsp--;
            	    if (failed) return id;
            	    if ( backtracking==0 ) {
            	      id.append(id(d)); id.append(end);
            	    }

            	    }
            	    break;

            	default :
            	    break loop57;
                }
            } while (true);


            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return id;
    }
    // $ANTLR end simpleType


    // $ANTLR start identifier
    // src/org/eclipse/internal/xpand2/parser/Xpand.g:367:1: identifier returns [Identifier r] : x= Identifier ;
    public Identifier identifier() throws RecognitionException {
        Identifier r = null;

        Token x=null;

        try {
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:367:35: (x= Identifier )
            // src/org/eclipse/internal/xpand2/parser/Xpand.g:368:4: x= Identifier
            {
            x=input.LT(1);
            match(input,Identifier,FOLLOW_Identifier_in_identifier2295); if (failed) return r;
            if ( backtracking==0 ) {
              r =id(x);
            }

            }

        }
        catch (RecognitionException re) {
            reportError(re);
            recover(input,re);
        }
        finally {
        }
        return r;
    }
    // $ANTLR end identifier

    // $ANTLR start synpred1
    public void synpred1_fragment() throws RecognitionException {   
        // src/org/eclipse/internal/xpand2/parser/Xpand.g:205:5: ( '(' type ')' castedExpression )
        // src/org/eclipse/internal/xpand2/parser/Xpand.g:205:6: '(' type ')' castedExpression
        {
        match(input,24,FOLLOW_24_in_synpred11095); if (failed) return ;
        pushFollow(FOLLOW_type_in_synpred11097);
        type();
        _fsp--;
        if (failed) return ;
        match(input,27,FOLLOW_27_in_synpred11099); if (failed) return ;
        pushFollow(FOLLOW_castedExpression_in_synpred11101);
        castedExpression();
        _fsp--;
        if (failed) return ;

        }
    }
    // $ANTLR end synpred1

    public boolean synpred1() {
        backtracking++;
        int start = input.mark();
        try {
            synpred1_fragment(); // can never throw exception
        } catch (RecognitionException re) {
            System.err.println("impossible: "+re);
        }
        boolean success = !failed;
        input.rewind(start);
        backtracking--;
        failed=false;
        return success;
    }


    protected DFA30 dfa30 = new DFA30(this);
    static final String DFA30_eotS =
        "\67\uffff";
    static final String DFA30_eofS =
        "\6\uffff\1\2\60\uffff";
    static final String DFA30_minS =
        "\2\7\1\uffff\1\32\1\30\1\11\1\6\1\11\1\36\2\uffff\1\0\13\uffff\1"+
        "\6\1\uffff\1\32\1\11\1\32\3\0\2\30\4\0\2\11\1\0\1\36\1\11\3\0\2"+
        "\33\1\11\1\0\1\11\1\36\1\33\1\11\1\33\1\36";
    static final String DFA30_maxS =
        "\2\142\1\uffff\1\143\1\120\1\11\1\142\1\11\1\144\2\uffff\1\0\13"+
        "\uffff\1\142\1\uffff\1\120\1\11\1\120\3\0\2\30\4\0\2\11\1\0\1\144"+
        "\1\142\3\0\1\143\1\36\1\11\1\0\1\11\1\144\1\36\1\11\1\33\1\144";
    static final String DFA30_acceptS =
        "\2\uffff\1\2\6\uffff\2\1\1\uffff\13\1\1\uffff\1\1\36\uffff";
    static final String DFA30_specialS =
        "\6\uffff\1\0\4\uffff\1\7\20\uffff\1\10\1\11\1\13\2\uffff\1\12\1"+
        "\14\1\5\1\15\2\uffff\1\2\2\uffff\1\3\1\6\1\4\3\uffff\1\1\6\uffff}>";
    static final String[] DFA30_transitionS = {
            "\3\2\16\uffff\1\1\10\uffff\1\2\32\uffff\1\2\2\uffff\2\2\16\uffff"+
            "\1\2\1\uffff\16\2\1\uffff\3\2",
            "\2\2\1\4\16\uffff\1\2\10\uffff\1\2\25\uffff\1\2\4\uffff\1\2"+
            "\2\uffff\2\2\16\uffff\1\2\1\uffff\16\2\1\uffff\3\3",
            "",
            "\1\2\1\6\5\uffff\1\2\30\uffff\2\2\10\uffff\13\2\1\uffff\1\2"+
            "\22\uffff\1\5",
            "\1\2\1\uffff\1\2\1\6\2\uffff\1\7\2\uffff\1\2\30\uffff\2\2\10"+
            "\uffff\13\2\1\uffff\1\2",
            "\1\10",
            "\1\2\1\12\1\20\1\13\16\uffff\1\25\3\2\5\uffff\1\27\3\uffff\1"+
            "\2\2\uffff\1\2\12\uffff\3\2\3\uffff\3\2\1\30\2\uffff\1\11\1"+
            "\22\2\uffff\14\2\1\26\1\2\1\24\1\23\2\17\1\21\1\15\10\16\1\uffff"+
            "\3\14",
            "\1\31",
            "\1\32\105\uffff\1\33",
            "",
            "",
            "\1\uffff",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "\1\2\1\34\1\42\1\35\16\uffff\1\47\10\uffff\1\2\36\uffff\1\44"+
            "\16\uffff\1\2\1\uffff\1\46\1\45\2\41\1\43\1\37\10\40\1\uffff"+
            "\3\36",
            "",
            "\1\2\1\6\2\uffff\1\7\2\uffff\1\2\30\uffff\2\2\10\uffff\13\2"+
            "\1\uffff\1\2",
            "\1\50",
            "\1\2\1\6\5\uffff\1\2\30\uffff\2\2\10\uffff\13\2\1\uffff\1\2",
            "\1\uffff",
            "\1\uffff",
            "\1\uffff",
            "\1\51",
            "\1\52",
            "\1\uffff",
            "\1\uffff",
            "\1\uffff",
            "\1\uffff",
            "\1\53",
            "\1\54",
            "\1\uffff",
            "\1\32\105\uffff\1\33",
            "\1\56\126\uffff\3\55",
            "\1\uffff",
            "\1\uffff",
            "\1\uffff",
            "\1\60\107\uffff\1\57",
            "\1\60\2\uffff\1\61",
            "\1\62",
            "\1\uffff",
            "\1\63",
            "\1\64\105\uffff\1\65",
            "\1\60\2\uffff\1\61",
            "\1\66",
            "\1\60",
            "\1\64\105\uffff\1\65"
    };

    static final short[] DFA30_eot = DFA.unpackEncodedString(DFA30_eotS);
    static final short[] DFA30_eof = DFA.unpackEncodedString(DFA30_eofS);
    static final char[] DFA30_min = DFA.unpackEncodedStringToUnsignedChars(DFA30_minS);
    static final char[] DFA30_max = DFA.unpackEncodedStringToUnsignedChars(DFA30_maxS);
    static final short[] DFA30_accept = DFA.unpackEncodedString(DFA30_acceptS);
    static final short[] DFA30_special = DFA.unpackEncodedString(DFA30_specialS);
    static final short[][] DFA30_transition;

    static {
        int numStates = DFA30_transitionS.length;
        DFA30_transition = new short[numStates][];
        for (int i=0; i<numStates; i++) {
            DFA30_transition[i] = DFA.unpackEncodedString(DFA30_transitionS[i]);
        }
    }

    class DFA30 extends DFA {

        public DFA30(BaseRecognizer recognizer) {
            this.recognizer = recognizer;
            this.decisionNumber = 30;
            this.eot = DFA30_eot;
            this.eof = DFA30_eof;
            this.min = DFA30_min;
            this.max = DFA30_max;
            this.accept = DFA30_accept;
            this.special = DFA30_special;
            this.transition = DFA30_transition;
        }
        @Override
		public String getDescription() {
            return "204:1: castedExpression returns [Expression e] : ( ( '(' type ')' castedExpression )=> '(' t= type ')' x= chainExpression | x= chainExpression );";
        }
        @Override
		public int specialStateTransition(int s, IntStream input) throws NoViableAltException {
        	int _s = s;
            switch ( s ) {
                    case 0 : 
                        int LA30_6 = input.LA(1);

                         
                        int index30_6 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (LA30_6==63) && (synpred1())) {s = 9;}

                        else if ( (LA30_6==StringLiteral) && (synpred1())) {s = 10;}

                        else if ( (LA30_6==Identifier) ) {s = 11;}

                        else if ( ((LA30_6>=96 && LA30_6<=98)) && (synpred1())) {s = 12;}

                        else if ( (LA30_6==86) && (synpred1())) {s = 13;}

                        else if ( ((LA30_6>=87 && LA30_6<=94)) && (synpred1())) {s = 14;}

                        else if ( ((LA30_6>=83 && LA30_6<=84)) && (synpred1())) {s = 15;}

                        else if ( (LA30_6==IntLiteral) && (synpred1())) {s = 16;}

                        else if ( (LA30_6==85) && (synpred1())) {s = 17;}

                        else if ( (LA30_6==64) && (synpred1())) {s = 18;}

                        else if ( (LA30_6==82) && (synpred1())) {s = 19;}

                        else if ( (LA30_6==81) && (synpred1())) {s = 20;}

                        else if ( (LA30_6==24) && (synpred1())) {s = 21;}

                        else if ( (LA30_6==79) && (synpred1())) {s = 22;}

                        else if ( (LA30_6==33) ) {s = 23;}

                        else if ( (LA30_6==60) && (synpred1())) {s = 24;}

                        else if ( (LA30_6==EOF||LA30_6==TEXT||(LA30_6>=25 && LA30_6<=27)||LA30_6==37||LA30_6==40||(LA30_6>=51 && LA30_6<=53)||(LA30_6>=57 && LA30_6<=59)||(LA30_6>=67 && LA30_6<=78)||LA30_6==80) ) {s = 2;}

                         
                        input.seek(index30_6);
                        if ( s>=0 ) return s;
                        break;
                    case 1 : 
                        int LA30_48 = input.LA(1);

                         
                        int index30_48 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_48);
                        if ( s>=0 ) return s;
                        break;
                    case 2 : 
                        int LA30_39 = input.LA(1);

                         
                        int index30_39 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_39);
                        if ( s>=0 ) return s;
                        break;
                    case 3 : 
                        int LA30_42 = input.LA(1);

                         
                        int index30_42 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_42);
                        if ( s>=0 ) return s;
                        break;
                    case 4 : 
                        int LA30_44 = input.LA(1);

                         
                        int index30_44 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_44);
                        if ( s>=0 ) return s;
                        break;
                    case 5 : 
                        int LA30_35 = input.LA(1);

                         
                        int index30_35 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_35);
                        if ( s>=0 ) return s;
                        break;
                    case 6 : 
                        int LA30_43 = input.LA(1);

                         
                        int index30_43 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_43);
                        if ( s>=0 ) return s;
                        break;
                    case 7 : 
                        int LA30_11 = input.LA(1);

                         
                        int index30_11 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_11);
                        if ( s>=0 ) return s;
                        break;
                    case 8 : 
                        int LA30_28 = input.LA(1);

                         
                        int index30_28 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_28);
                        if ( s>=0 ) return s;
                        break;
                    case 9 : 
                        int LA30_29 = input.LA(1);

                         
                        int index30_29 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_29);
                        if ( s>=0 ) return s;
                        break;
                    case 10 : 
                        int LA30_33 = input.LA(1);

                         
                        int index30_33 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_33);
                        if ( s>=0 ) return s;
                        break;
                    case 11 : 
                        int LA30_30 = input.LA(1);

                         
                        int index30_30 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_30);
                        if ( s>=0 ) return s;
                        break;
                    case 12 : 
                        int LA30_34 = input.LA(1);

                         
                        int index30_34 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_34);
                        if ( s>=0 ) return s;
                        break;
                    case 13 : 
                        int LA30_36 = input.LA(1);

                         
                        int index30_36 = input.index();
                        input.rewind();
                        s = -1;
                        if ( (synpred1()) ) {s = 24;}

                        else if ( (true) ) {s = 2;}

                         
                        input.seek(index30_36);
                        if ( s>=0 ) return s;
                        break;
            }
            if (backtracking>0) {failed=true; return -1;}
            NoViableAltException nvae =
                new NoViableAltException(getDescription(), 30, _s, input);
            error(nvae);
            throw nvae;
        }
    }
 

    public static final BitSet FOLLOW_LG_in_template47 = new BitSet(new long[]{0x0000000080E00022L});
    public static final BitSet FOLLOW_COMMENT_in_template52 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_TEXT_in_template54 = new BitSet(new long[]{0x0000000080E00022L});
    public static final BitSet FOLLOW_anImport_in_template64 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_anExtensionImport_in_template73 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_TEXT_in_template78 = new BitSet(new long[]{0x0000000080E00022L});
    public static final BitSet FOLLOW_COMMENT_in_template81 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_TEXT_in_template83 = new BitSet(new long[]{0x0000000080E00022L});
    public static final BitSet FOLLOW_define_in_template95 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_around_in_template102 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_TEXT_in_template106 = new BitSet(new long[]{0x0000000080800022L});
    public static final BitSet FOLLOW_COMMENT_in_template109 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_TEXT_in_template111 = new BitSet(new long[]{0x0000000080800022L});
    public static final BitSet FOLLOW_21_in_anImport137 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_simpleType_in_anImport141 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_22_in_anExtensionImport156 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_simpleType_in_anExtensionImport160 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_23_in_around178 = new BitSet(new long[]{0x0000000004000200L});
    public static final BitSet FOLLOW_pointcut_in_around182 = new BitSet(new long[]{0x0000000011000000L});
    public static final BitSet FOLLOW_24_in_around188 = new BitSet(new long[]{0x0000000004000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_declaredParameterList_in_around193 = new BitSet(new long[]{0x000000000A000000L});
    public static final BitSet FOLLOW_25_in_around196 = new BitSet(new long[]{0x0000000004000000L});
    public static final BitSet FOLLOW_26_in_around200 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_26_in_around209 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_around213 = new BitSet(new long[]{0x0000000010000000L});
    public static final BitSet FOLLOW_28_in_around217 = new BitSet(new long[]{0x0000000000000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_type_in_around221 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_around229 = new BitSet(new long[]{0x0000000020000000L});
    public static final BitSet FOLLOW_29_in_around234 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_26_in_pointcut256 = new BitSet(new long[]{0x0000000044000202L});
    public static final BitSet FOLLOW_identifier_in_pointcut262 = new BitSet(new long[]{0x0000000044000202L});
    public static final BitSet FOLLOW_26_in_pointcut271 = new BitSet(new long[]{0x0000000044000202L});
    public static final BitSet FOLLOW_identifier_in_pointcut277 = new BitSet(new long[]{0x0000000044000202L});
    public static final BitSet FOLLOW_30_in_pointcut283 = new BitSet(new long[]{0x0000000044000202L});
    public static final BitSet FOLLOW_31_in_define303 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_define307 = new BitSet(new long[]{0x0000000011000000L});
    public static final BitSet FOLLOW_24_in_define310 = new BitSet(new long[]{0x0000000000000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_declaredParameterList_in_define314 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_define316 = new BitSet(new long[]{0x0000000010000000L});
    public static final BitSet FOLLOW_28_in_define320 = new BitSet(new long[]{0x0000000000000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_type_in_define324 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_define332 = new BitSet(new long[]{0x0000000100000000L});
    public static final BitSet FOLLOW_32_in_define338 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_textSequence_in_sequence361 = new BitSet(new long[]{0x9082885E01000382L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_statement_in_sequence370 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_textSequence_in_sequence379 = new BitSet(new long[]{0x9082885E01000382L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_simpleStatement_in_statement409 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_fileStatement_in_statement417 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_foreachStatement_in_statement425 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_ifStatement_in_statement433 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_letStatement_in_statement441 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_protectStatement_in_statement449 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_text_in_textSequence468 = new BitSet(new long[]{0x0000000000000022L});
    public static final BitSet FOLLOW_COMMENT_in_textSequence475 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_text_in_textSequence479 = new BitSet(new long[]{0x0000000000000022L});
    public static final BitSet FOLLOW_33_in_text500 = new BitSet(new long[]{0x0000000000000040L});
    public static final BitSet FOLLOW_TEXT_in_text506 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_errorStatement_in_simpleStatement525 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_expandStatement_in_simpleStatement533 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_expressionStmt_in_simpleStatement541 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_34_in_errorStatement558 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_errorStatement562 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_35_in_expandStatement579 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_definitionName_in_expandStatement583 = new BitSet(new long[]{0x0000001011000002L});
    public static final BitSet FOLLOW_24_in_expandStatement586 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_parameterList_in_expandStatement590 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_expandStatement592 = new BitSet(new long[]{0x0000001010000002L});
    public static final BitSet FOLLOW_28_in_expandStatement598 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_expandStatement602 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_36_in_expandStatement612 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_expandStatement616 = new BitSet(new long[]{0x0000002000000002L});
    public static final BitSet FOLLOW_37_in_expandStatement619 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_expandStatement623 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_simpleType_in_definitionName653 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_expression_in_expressionStmt671 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_38_in_fileStatement687 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_fileStatement691 = new BitSet(new long[]{0x0000000200000240L});
    public static final BitSet FOLLOW_identifier_in_fileStatement696 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_fileStatement704 = new BitSet(new long[]{0x0000008000000000L});
    public static final BitSet FOLLOW_39_in_fileStatement708 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_36_in_foreachStatement726 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_foreachStatement730 = new BitSet(new long[]{0x0000010000000000L});
    public static final BitSet FOLLOW_40_in_foreachStatement732 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_foreachStatement736 = new BitSet(new long[]{0x0000022200000040L});
    public static final BitSet FOLLOW_41_in_foreachStatement739 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_foreachStatement743 = new BitSet(new long[]{0x0000002200000040L});
    public static final BitSet FOLLOW_37_in_foreachStatement748 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_foreachStatement752 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_foreachStatement762 = new BitSet(new long[]{0x0000040000000000L});
    public static final BitSet FOLLOW_42_in_foreachStatement767 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_43_in_ifStatement793 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_ifStatement797 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_ifStatement803 = new BitSet(new long[]{0x0000700000000000L});
    public static final BitSet FOLLOW_elseIfStatement_in_ifStatement815 = new BitSet(new long[]{0x0000700000000000L});
    public static final BitSet FOLLOW_elseStatement_in_ifStatement826 = new BitSet(new long[]{0x0000100000000000L});
    public static final BitSet FOLLOW_44_in_ifStatement838 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_45_in_elseIfStatement852 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_elseIfStatement856 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_elseIfStatement862 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_46_in_elseStatement883 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_elseStatement889 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_47_in_letStatement910 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_letStatement914 = new BitSet(new long[]{0x0000010000000000L});
    public static final BitSet FOLLOW_40_in_letStatement916 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_letStatement920 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_letStatement928 = new BitSet(new long[]{0x0001000000000000L});
    public static final BitSet FOLLOW_48_in_letStatement933 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_49_in_protectStatement952 = new BitSet(new long[]{0x0004000000000000L});
    public static final BitSet FOLLOW_50_in_protectStatement957 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_protectStatement961 = new BitSet(new long[]{0x0008000000000000L});
    public static final BitSet FOLLOW_51_in_protectStatement966 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_protectStatement970 = new BitSet(new long[]{0x0010000000000000L});
    public static final BitSet FOLLOW_52_in_protectStatement983 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_protectStatement987 = new BitSet(new long[]{0x0020000200000040L});
    public static final BitSet FOLLOW_53_in_protectStatement992 = new BitSet(new long[]{0x0000000200000040L});
    public static final BitSet FOLLOW_sequence_in_protectStatement1001 = new BitSet(new long[]{0x0040000000000000L});
    public static final BitSet FOLLOW_54_in_protectStatement1005 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_letExpression_in_expression1027 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_55_in_letExpression1046 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_letExpression1050 = new BitSet(new long[]{0x0100000000000000L});
    public static final BitSet FOLLOW_56_in_letExpression1052 = new BitSet(new long[]{0x9000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_castedExpression_in_letExpression1056 = new BitSet(new long[]{0x0200000000000000L});
    public static final BitSet FOLLOW_57_in_letExpression1058 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_letExpression1062 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_castedExpression_in_letExpression1075 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_24_in_castedExpression1106 = new BitSet(new long[]{0x0000000000000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_type_in_castedExpression1110 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_castedExpression1112 = new BitSet(new long[]{0x9000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_chainExpression_in_castedExpression1116 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_chainExpression_in_castedExpression1125 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_ifExpression_in_chainExpression1145 = new BitSet(new long[]{0x0400000000000002L});
    public static final BitSet FOLLOW_58_in_chainExpression1151 = new BitSet(new long[]{0x9000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_ifExpression_in_chainExpression1155 = new BitSet(new long[]{0x0400000000000002L});
    public static final BitSet FOLLOW_switchExpression_in_ifExpression1176 = new BitSet(new long[]{0x0800000000000002L});
    public static final BitSet FOLLOW_59_in_ifExpression1180 = new BitSet(new long[]{0x8000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_switchExpression_in_ifExpression1184 = new BitSet(new long[]{0x0200000000000000L});
    public static final BitSet FOLLOW_57_in_ifExpression1186 = new BitSet(new long[]{0x8000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_switchExpression_in_ifExpression1190 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_60_in_ifExpression1198 = new BitSet(new long[]{0x8000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_switchExpression_in_ifExpression1202 = new BitSet(new long[]{0x2000000000000000L});
    public static final BitSet FOLLOW_61_in_ifExpression1204 = new BitSet(new long[]{0x8000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_switchExpression_in_ifExpression1208 = new BitSet(new long[]{0x4000000000000002L});
    public static final BitSet FOLLOW_62_in_ifExpression1211 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_ifExpression1215 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_63_in_switchExpression1242 = new BitSet(new long[]{0x0000000001000000L,0x0000000000000001L});
    public static final BitSet FOLLOW_24_in_switchExpression1245 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_orExpression_in_switchExpression1251 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_switchExpression1253 = new BitSet(new long[]{0x0000000000000000L,0x0000000000000001L});
    public static final BitSet FOLLOW_64_in_switchExpression1260 = new BitSet(new long[]{0x0000000000000000L,0x0000000000000006L});
    public static final BitSet FOLLOW_65_in_switchExpression1273 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_orExpression_in_switchExpression1277 = new BitSet(new long[]{0x0200000000000000L});
    public static final BitSet FOLLOW_57_in_switchExpression1280 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_orExpression_in_switchExpression1285 = new BitSet(new long[]{0x0000000000000000L,0x0000000000000006L});
    public static final BitSet FOLLOW_66_in_switchExpression1303 = new BitSet(new long[]{0x0200000000000000L});
    public static final BitSet FOLLOW_57_in_switchExpression1305 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_orExpression_in_switchExpression1311 = new BitSet(new long[]{0x0000000000000000L,0x0000000000000008L});
    public static final BitSet FOLLOW_67_in_switchExpression1316 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_orExpression_in_switchExpression1328 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_andExpression_in_orExpression1348 = new BitSet(new long[]{0x0000000000000002L,0x0000000000000010L});
    public static final BitSet FOLLOW_68_in_orExpression1355 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_andExpression_in_orExpression1359 = new BitSet(new long[]{0x0000000000000002L,0x0000000000000010L});
    public static final BitSet FOLLOW_impliesExpression_in_andExpression1382 = new BitSet(new long[]{0x0000000000000002L,0x0000000000000020L});
    public static final BitSet FOLLOW_69_in_andExpression1389 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_impliesExpression_in_andExpression1393 = new BitSet(new long[]{0x0000000000000002L,0x0000000000000020L});
    public static final BitSet FOLLOW_relationalExpression_in_impliesExpression1415 = new BitSet(new long[]{0x0000000000000002L,0x0000000000000040L});
    public static final BitSet FOLLOW_70_in_impliesExpression1422 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_relationalExpression_in_impliesExpression1426 = new BitSet(new long[]{0x0000000000000002L,0x0000000000000040L});
    public static final BitSet FOLLOW_additiveExpression_in_relationalExpression1450 = new BitSet(new long[]{0x0000000000000002L,0x0000000000001F80L});
    public static final BitSet FOLLOW_set_in_relationalExpression1458 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_additiveExpression_in_relationalExpression1484 = new BitSet(new long[]{0x0000000000000002L,0x0000000000001F80L});
    public static final BitSet FOLLOW_multiplicativeExpression_in_additiveExpression1505 = new BitSet(new long[]{0x0000000200000002L,0x0000000000002000L});
    public static final BitSet FOLLOW_set_in_additiveExpression1515 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_multiplicativeExpression_in_additiveExpression1524 = new BitSet(new long[]{0x0000000200000002L,0x0000000000002000L});
    public static final BitSet FOLLOW_unaryExpression_in_multiplicativeExpression1543 = new BitSet(new long[]{0x0000000004000002L,0x0000000000004000L});
    public static final BitSet FOLLOW_set_in_multiplicativeExpression1551 = new BitSet(new long[]{0x0000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_unaryExpression_in_multiplicativeExpression1561 = new BitSet(new long[]{0x0000000004000002L,0x0000000000004000L});
    public static final BitSet FOLLOW_infixExpression_in_unaryExpression1582 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_79_in_unaryExpression1590 = new BitSet(new long[]{0x0000000001000380L,0x000000077FFE0001L});
    public static final BitSet FOLLOW_infixExpression_in_unaryExpression1594 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_33_in_unaryExpression1602 = new BitSet(new long[]{0x0000000001000380L,0x000000077FFE0001L});
    public static final BitSet FOLLOW_infixExpression_in_unaryExpression1606 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_primaryExpression_in_infixExpression1624 = new BitSet(new long[]{0x0000000000000002L,0x0000000000010000L});
    public static final BitSet FOLLOW_80_in_infixExpression1630 = new BitSet(new long[]{0x0000000000000200L,0x000000077FC00000L});
    public static final BitSet FOLLOW_featureCall_in_infixExpression1634 = new BitSet(new long[]{0x0000000000000002L,0x0000000000010000L});
    public static final BitSet FOLLOW_StringLiteral_in_primaryExpression1660 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_featureCall_in_primaryExpression1671 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_booleanLiteral_in_primaryExpression1681 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_numberLiteral_in_primaryExpression1691 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_nullLiteral_in_primaryExpression1701 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_listLiteral_in_primaryExpression1711 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_constructorCall_in_primaryExpression1721 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_globalVarExpression_in_primaryExpression1731 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_paranthesizedExpression_in_primaryExpression1741 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_24_in_paranthesizedExpression1760 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_paranthesizedExpression1764 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_paranthesizedExpression1766 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_81_in_globalVarExpression1786 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_globalVarExpression1790 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_identifier_in_featureCall1808 = new BitSet(new long[]{0x0000000001000000L});
    public static final BitSet FOLLOW_24_in_featureCall1810 = new BitSet(new long[]{0x9080000209000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_parameterList_in_featureCall1815 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_featureCall1819 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_type_in_featureCall1829 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_collectionExpression_in_featureCall1840 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_64_in_listLiteral1857 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8009L});
    public static final BitSet FOLLOW_parameterList_in_listLiteral1862 = new BitSet(new long[]{0x0000000000000000L,0x0000000000000008L});
    public static final BitSet FOLLOW_67_in_listLiteral1866 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_82_in_constructorCall1883 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_simpleType_in_constructorCall1887 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_set_in_booleanLiteral0 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_85_in_nullLiteral1922 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_IntLiteral_in_numberLiteral1941 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_IntLiteral_in_numberLiteral1950 = new BitSet(new long[]{0x0000000000000000L,0x0000000000010000L});
    public static final BitSet FOLLOW_80_in_numberLiteral1954 = new BitSet(new long[]{0x0000000000000100L});
    public static final BitSet FOLLOW_IntLiteral_in_numberLiteral1958 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_86_in_collectionExpression1978 = new BitSet(new long[]{0x0000000001000000L});
    public static final BitSet FOLLOW_24_in_collectionExpression1982 = new BitSet(new long[]{0x0000000000000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_type_in_collectionExpression1986 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_collectionExpression1988 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_set_in_collectionExpression2001 = new BitSet(new long[]{0x0000000001000000L});
    public static final BitSet FOLLOW_24_in_collectionExpression2051 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_identifier_in_collectionExpression2056 = new BitSet(new long[]{0x0000000000000000L,0x0000000080000000L});
    public static final BitSet FOLLOW_95_in_collectionExpression2058 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_collectionExpression2064 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_collectionExpression2066 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_declaredParameter_in_declaredParameterList2090 = new BitSet(new long[]{0x0000000002000002L});
    public static final BitSet FOLLOW_25_in_declaredParameterList2094 = new BitSet(new long[]{0x0000000000000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_declaredParameter_in_declaredParameterList2098 = new BitSet(new long[]{0x0000000002000002L});
    public static final BitSet FOLLOW_type_in_declaredParameter2118 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_declaredParameter2122 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_expression_in_parameterList2144 = new BitSet(new long[]{0x0000000002000002L});
    public static final BitSet FOLLOW_25_in_parameterList2149 = new BitSet(new long[]{0x9080000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_expression_in_parameterList2153 = new BitSet(new long[]{0x0000000002000002L});
    public static final BitSet FOLLOW_collectionType_in_type2179 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_simpleType_in_type2189 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_set_in_collectionType2211 = new BitSet(new long[]{0x0000000000000002L,0x0000000800000000L});
    public static final BitSet FOLLOW_99_in_collectionType2232 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_simpleType_in_collectionType2236 = new BitSet(new long[]{0x0000000000000000L,0x0000001000000000L});
    public static final BitSet FOLLOW_100_in_collectionType2240 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_identifier_in_simpleType2260 = new BitSet(new long[]{0x0000000040000002L});
    public static final BitSet FOLLOW_30_in_simpleType2268 = new BitSet(new long[]{0x0000000000000200L});
    public static final BitSet FOLLOW_identifier_in_simpleType2272 = new BitSet(new long[]{0x0000000040000002L});
    public static final BitSet FOLLOW_Identifier_in_identifier2295 = new BitSet(new long[]{0x0000000000000002L});
    public static final BitSet FOLLOW_24_in_synpred11095 = new BitSet(new long[]{0x0000000000000200L,0x0000000700000000L});
    public static final BitSet FOLLOW_type_in_synpred11097 = new BitSet(new long[]{0x0000000008000000L});
    public static final BitSet FOLLOW_27_in_synpred11099 = new BitSet(new long[]{0x9000000201000380L,0x000000077FFE8001L});
    public static final BitSet FOLLOW_castedExpression_in_synpred11101 = new BitSet(new long[]{0x0000000000000002L});

}
 No newline at end of file