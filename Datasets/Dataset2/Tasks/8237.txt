param3 = "1";

package org.jboss.ejb.plugins.cmp.jdbc.ejbql;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import org.jboss.ejb.plugins.cmp.ejbql.Alternation;
import org.jboss.ejb.plugins.cmp.ejbql.Assembler;
import org.jboss.ejb.plugins.cmp.ejbql.Assembly;
import org.jboss.ejb.plugins.cmp.ejbql.InputParameter;
import org.jboss.ejb.plugins.cmp.ejbql.InputParameterToken;
import org.jboss.ejb.plugins.cmp.ejbql.Literal;
import org.jboss.ejb.plugins.cmp.ejbql.NumericLiteral;
import org.jboss.ejb.plugins.cmp.ejbql.Optional;
import org.jboss.ejb.plugins.cmp.ejbql.Parser;
import org.jboss.ejb.plugins.cmp.ejbql.Repetition;
import org.jboss.ejb.plugins.cmp.ejbql.Sequence;
import org.jboss.ejb.plugins.cmp.ejbql.StringLiteral;
import org.jboss.ejb.plugins.cmp.ejbql.Symbol;
import org.jboss.ejb.plugins.cmp.ejbql.Token;
import org.jboss.ejb.plugins.cmp.ejbql.Word;

public class EJBQLParser {

   public EJBQLParser() {
   }
   
   // EJB QL ::= select_clause from_clause [where_clause]
   public Parser ejbqlQuery() {
      Sequence a = new Sequence();
      a.add(selectClause());
      a.add(fromClause());
      a.add(new Optional(whereClause()));
      
      return a;
   }
   
   // from_clause ::=FROM identification_variable_declaration [, identification_variable_declaration]*
   protected Parser fromClause() {
      Sequence s = new Sequence();
      s.add(new Literal("FROM").discard());
      s.add(identificationVariableDeclaration());
      
      Sequence commaList = new Sequence();
      commaList.add(new Symbol(",").discard());
      commaList.add(identificationVariableDeclaration());
      
      s.add(new Repetition(commaList));
      
      s.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            Token t = a.peekToken();
            // did we totaly match the from clause?
            // only true if there are no tokens left of the next token is "WHERE"
            if(t == null || t.toString().equalsIgnoreCase("WHERE")) {
               SQLTarget target = (SQLTarget)a.getTarget();
               List path = (List)a.pop();
               target.setSelectPath(path);
            } else {
               a.setInvalid();
            }
         }
      });

      return s;
   }

   // identification_variable_declaration ::= collection_member_declaration | range_variable_declaration
   private Alternation identVarDec;
   protected Parser identificationVariableDeclaration() {
      if(identVarDec == null) {
         identVarDec = new Alternation();
         identVarDec.add(collectionMemberDeclaration());
         identVarDec.add(rangeVariableDeclaration());
      }
      return identVarDec;
   }

   // collection_member_declaration ::=IN (collection_valued_path_expression) [AS ] identifier
   private Sequence colMemDec;
   protected Parser collectionMemberDeclaration() {
      if(colMemDec == null) {
         colMemDec = new Sequence();
         colMemDec.add(new Literal("IN").discard());
         colMemDec.add(new Symbol("(").discard());
         colMemDec.add(collectionValuedPathExpression());
         colMemDec.add(new Symbol(")").discard());
         colMemDec.add(new Optional(new Literal("AS").discard()));
         colMemDec.add(identifier());
         colMemDec.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String identifier = a.pop().toString();
               String path = (String)a.pop();

               target.registerIdentifier(path, identifier);
            }
         });

      }
      return colMemDec;
   }

   // range_variable_declaration ::= abstract_schema_name [AS ] identifier
   private Sequence rngVarDec;
   protected Parser rangeVariableDeclaration() {
      if(rngVarDec == null) {
         rngVarDec = new Sequence();
         rngVarDec.add(abstractSchemaName());
         rngVarDec.add(new Optional(new Literal("AS").discard()));
         rngVarDec.add(identifier());
         
         rngVarDec.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String identifier = a.pop().toString();
               AbstractSchema abstractSchema = (AbstractSchema)a.pop();

               target.registerIdentifier(abstractSchema, identifier);
            }
         });
      }
      return rngVarDec;
   }
   
   // single_valued_path_expression ::= {single_valued_navigation | identification_variable}.cmp_field | single_valued_navigation
   private Alternation singleValPathExp;
   protected Parser singleValuedPathExpression() {
      if(singleValPathExp == null) {
         
         // {single_valued_navigation | identification_variable}
         Alternation navOrIdent = new Alternation();
         navOrIdent.add(singleValuedNavigation());
         navOrIdent.add(identificationVariable());
         
         // {above}.cmp_field
         Sequence cmpFieldExp = new Sequence();
         cmpFieldExp.add(navOrIdent);
         cmpFieldExp.add(new Symbol(".").discard());
         cmpFieldExp.add(cmpField());
         
         singleValPathExp = new Alternation();
         singleValPathExp.add(cmpFieldExp);
         singleValPathExp.add(singleValuedNavigation());
      }
      return singleValPathExp;
   }

   // single_valued_navigation ::= identification_variable.[single_valued_cmr_field.]* single_valued_cmr_field
   private Sequence singleValNav;
   protected Parser singleValuedNavigation() {
      if(singleValNav == null) {
         singleValNav = new Sequence();
         singleValNav.add(identificationVariable());
         singleValNav.add(new Symbol(".").discard());
         
         Sequence nav = new Sequence();
         nav.add(singleValuedCmrField());
         nav.add(new Symbol(".").discard());

         singleValNav.add(new Repetition(nav));
         singleValNav.add(singleValuedCmrField());
      }
      return singleValNav;
   }

   // collection_valued_path_expression ::= identification_variable.[single_valued_cmr_field.]*collection_valued_cmr_field
   private Sequence colValPathExp;
   protected Parser collectionValuedPathExpression() {
      if(colValPathExp == null) {
         colValPathExp = new Sequence();
         colValPathExp.add(identificationVariable());
         colValPathExp.add(new Symbol(".").discard());
         
         Sequence path = new Sequence();
         path.add(singleValuedCmrField());
         path.add(new Symbol(".").discard());

         colValPathExp.add(new Repetition(path));
         colValPathExp.add(collectionValuedCmrField());
      }
      return colValPathExp;
   }

   // select_clause ::=SELECT [DISTINCT ] {single_valued_path_expression | OBJECT (identification_variable)}
   private Sequence selClau;
   protected Parser selectClause() {
      if(selClau == null) {
         selClau = new Sequence();
         selClau.add(new Literal("SELECT"));
         selClau.add(new Optional(new Literal("DISTINCT")));
         
         Alternation selectTarget = new Alternation();
            Sequence selectPath = new Sequence();
            selectPath.add(new Word());
            selectPath.add(new Symbol(".").discard());
               Sequence nav = new Sequence();
               nav.add(new Word());
               nav.add(new Symbol(".").discard());
            selectPath.add(new Repetition(nav));
            selectPath.add(new Word());
         selectTarget.add(selectPath);         
            Sequence objectTarget = new Sequence();
            objectTarget.add(new Literal("OBJECT"));
            objectTarget.add(new Symbol("(").discard());
            objectTarget.add(new Word());
            objectTarget.add(new Symbol(")").discard());         
         selectTarget.add(objectTarget);
         
         selClau.add(selectTarget);
         
         selClau.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               List path = new ArrayList();
               while(true) {
                  String element = a.pop().toString();
                  
                  if(element.equalsIgnoreCase("SELECT")) {
                     Collections.reverse(path);
                     a.push(path);
                     return;
                  } else if(element.equalsIgnoreCase("DISTINCT")) {
                     target.setSelectDistinct();
                  } else if(element.equalsIgnoreCase("OBJECT")) {
                     // ignore the object keyword, it is just sugar to make parsing easy.
                  } else {
                     path.add(element);
                  }
               }
            }
         });
      }
      return selClau;
   }

   // where_clause ::= WHERE conditional_expression
   private Sequence whrClau;
   protected Parser whereClause() {
      if(whrClau == null) {
         whrClau = new Sequence();
         whrClau.add(new Literal("WHERE"));
         whrClau.add(conditionalExpression());
         whrClau.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               
               List clause = new ArrayList();
               for(String s = a.pop().toString(); 
                     !"WHERE".equalsIgnoreCase(s); 
                     s = a.pop().toString()) {

                  clause.add(s);
               }
               
               Collections.reverse(clause);
               StringBuffer buf = new StringBuffer();
               for(Iterator i=clause.iterator(); i.hasNext(); ) {
                  buf.append((String)i.next()).append(" ");
               }
               target.setWhereClause(buf.toString().trim());
            }
         });
      }
      return whrClau;
   }

   // conditional_expression ::= conditional_term | conditional_expression OR conditional_term
   // convert to elimiate infinite recursion
   // conditional_expression ::= conditional_term {OR conditional_term}*
   private Sequence condExp;
   protected Parser conditionalExpression() {
      if(condExp == null) {
         condExp = new Sequence();
         condExp.add(conditionalTerm());
         
         Sequence orExps = new Sequence();
         orExps.add(new Literal("OR"));
         orExps.add(conditionalTerm());
   
         condExp.add(new Repetition(orExps));
      }
      return condExp;
   }
   
   // conditional_term ::= conditional_factor | conditional_term AND conditional_factor
   // convert to elimiate infinite recursion
   // conditional_term ::= conditional_factor {AND conditional_factor}*
   private Sequence condTerm;
   protected Parser conditionalTerm() {
      if(condTerm == null) {
         condTerm = new Sequence();
         condTerm.add(conditionalFactor());
         
         Sequence andTerms = new Sequence();
         andTerms.add(new Literal("AND"));
         andTerms.add(conditionalFactor());
      
         condTerm.add(new Repetition(andTerms));
      }
      return condTerm;
   }
      
   // conditional_factor ::= [NOT ] conditional_test
   private Sequence condFactor;
   protected Parser conditionalFactor() {
      if(condFactor == null) {
         condFactor = new Sequence();
         condFactor.add(new Optional(new Literal("NOT")));
         condFactor.add(conditionalTest());
      }
      return condFactor;
   }
   
   // conditional_test :: = conditional_primary
   protected Parser conditionalTest() {
      return conditionalPrimary();
   }
   
   // conditional_primary ::= simple_cond_expression | (conditional_expression)
   private Alternation condPrimary;
   protected Parser conditionalPrimary() {
      if(condPrimary == null) {
         condPrimary = new Alternation();
         condPrimary.add(simpleCondExpression());
         
         Sequence parenExp = new Sequence();
         parenExp.add(new Symbol("("));
         parenExp.add(conditionalExpression());
         parenExp.add(new Symbol(")"));
         
         condPrimary.add(parenExp);
      }
      return condPrimary;
   }

   // simple_cond_expression ::= comparison_expression | 
   //    between_expression | like_expression |
   //    in_expression | null_comparison_expression |
   //    empty_collection_comparison_expression |
   //    collection_member_expression
   private Alternation simpleCondExp;
   protected Parser simpleCondExpression() {
      if(simpleCondExp == null) {
         simpleCondExp = new Alternation();
         simpleCondExp.add(comparisonExpression());
         simpleCondExp.add(betweenExpression());
         simpleCondExp.add(likeExpression());
         simpleCondExp.add(inExpression());
         simpleCondExp.add(nullComparisonExpression());
         simpleCondExp.add(emptyCollectionComparisonExpression());
         simpleCondExp.add(collectionMemberExpression());
      }
      return simpleCondExp;
   }

   
   // between_expression ::= arithmetic_expression [NOT ]BETWEEN arithmetic_expression AND arithmetic_expression
   private Sequence betweenExp;
   protected Parser betweenExpression() {
      if(betweenExp == null) {
         betweenExp = new Sequence();
         betweenExp.add(arithmeticExpression());
         betweenExp.add(new Optional(new Literal("NOT")));
         betweenExp.add(new Literal("BETWEEN"));
         betweenExp.add(arithmeticExpression());
         betweenExp.add(new Literal("AND"));
         betweenExp.add(arithmeticExpression());         
      }
      return betweenExp;
   }
   
   // in_expression ::= single_valued_path_expression [NOT ]IN (string_literal [, string_literal]* )
   private Sequence inExp;
   protected Parser inExpression() {
      if(inExp == null) {
         inExp = new Sequence();
         inExp.add(stringValuedPathExpression());
         inExp.add(new Optional(new Literal("NOT")));
         inExp.add(new Literal("IN"));
         inExp.add(new Symbol("("));
         inExp.add(new StringLiteral());
         
         Sequence commaList =  new Sequence();
         commaList.add(new Symbol(","));
         commaList.add(new StringLiteral());
         
         inExp.add(new Repetition(commaList));
         
         inExp.add(new Symbol(")"));
      }
      return inExp;
   }
   
   // like_expression ::= single_valued_path_expression [NOT ]LIKE pattern_value [ESCAPE escape-character]
   private Sequence likeExp;
   protected Parser likeExpression() {
      if(likeExp == null) {
         likeExp = new Sequence();
         likeExp.add(stringValuedPathExpression());
         likeExp.add(new Optional(new Literal("NOT")));
         likeExp.add(new Literal("LIKE"));
         likeExp.add(patternValue());
         
         Sequence excSeq = new Sequence();
         excSeq.add(new Literal("ESCAPE").discard());
         excSeq.add(escapeCharacter());
         
         likeExp.add(new Optional(excSeq));
      }
      return likeExp;
   }
   
   // null_comparison_expression ::= single_valued_path_expression IS [NOT ] NULL
   private Sequence nullComparisonExp;
   protected Parser nullComparisonExpression() {
      if(nullComparisonExp == null) {
         nullComparisonExp = new Sequence();
         nullComparisonExp.add(singleValuedPathExpression());
         nullComparisonExp.add(new Literal("IS").discard());
         nullComparisonExp.add(new Optional(new Literal("NOT")));
         nullComparisonExp.add(new Literal("NULL").discard());
         nullComparisonExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               boolean not = false;
               String path = a.pop().toString();
               if(path.equalsIgnoreCase("NOT")) {
                  not = true;
                  path = a.pop().toString();
               }
               
               String nullComp = target.getNullComparison(path, not);
               if(nullComp == null) {
                  a.setInvalid();
               } else {
                  a.push(nullComp);
               }
            }
         });
      }
      return nullComparisonExp;
   }
   
   // empty_collection_comparison_expression ::= collection_valued_path_expression IS [NOT] EMPTY
   private Alternation emptyColCompExp;
   protected Parser emptyCollectionComparisonExpression() {
      if(emptyColCompExp == null) {
         emptyColCompExp = new Alternation();
         
         Sequence isNotEmptyColCompExp = new Sequence();
         isNotEmptyColCompExp.add(collectionValuedPathExpression());
         isNotEmptyColCompExp.add(new Literal("IS").discard());
         isNotEmptyColCompExp.add(new Literal("NOT").discard());
         isNotEmptyColCompExp.add(new Literal("EMPTY").discard());
         isNotEmptyColCompExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               // just pop of the path and replace with 'TRUE'
               // the check will be done by the path compare
               // code.
               String path = (String)a.pop();
               a.push("TRUE");
            }
         });
         emptyColCompExp.add(isNotEmptyColCompExp);
         
         // identification_vaiable [.single_valued_cmr_field]* .word IS EMPTY
         Sequence isEmptyColCompExp = new Sequence();
         isEmptyColCompExp.add(identificationVariable());
         
         Sequence singleCMRPath = new Sequence();
         singleCMRPath.add(new Symbol(".").discard());
         singleCMRPath.add(singleValuedCmrField());
         isEmptyColCompExp.add(new Repetition(singleCMRPath));
         
         isEmptyColCompExp.add(new Symbol(".").discard());
         isEmptyColCompExp.add(new Word());
         
         isEmptyColCompExp.add(new Literal("IS").discard());
         isEmptyColCompExp.add(new Literal("EMPTY").discard());
         
         isEmptyColCompExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String field = a.pop().toString();
               String path = (String)a.pop();
               
               String notExistsClause = target.getNotExistsClause(path, field);
               if(notExistsClause == null) {
                  a.setInvalid();
               } else {
                  a.push(notExistsClause);
               }
            }
         });
         emptyColCompExp.add(isEmptyColCompExp);
         
      }
      return emptyColCompExp;
   }
   
   // collection_member_expression ::=
   // {single_valued_navigation | identification_variable | input_parameter}
   // [NOT ]MEMBER [OF ] collection_valued_path_expression
   private Sequence colMemExp;
   protected Parser collectionMemberExpression() {
      if(colMemExp == null) {
         colMemExp = new Sequence();
         
         Alternation varOrParam = new Alternation();
         varOrParam.add(singleValuedNavigation());
         varOrParam.add(identificationVariable());
         varOrParam.add(entityBeanValuedParameter());

         colMemExp.add(varOrParam);
         colMemExp.add(new Optional(new Literal("NOT")));
         colMemExp.add(new Literal("MEMBER").discard());
         colMemExp.add(new Optional(new Literal("OF").discard()));
         colMemExp.add(collectionValuedPathExpression());
         colMemExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String compareTo = a.pop().toString();
               String compareSymbol = "=";
               Object compareFrom = a.pop();
               if(compareFrom.toString().equalsIgnoreCase("NOT")) {
                  compareSymbol = "<>";
                  compareFrom = a.pop();
               }
               
               String comparison;
               if(compareFrom instanceof InputParameterToken) {
                  // backwards, but won't make a differance
                  comparison = target.getEntityWherePathToParameter(
                     compareTo,
                     compareSymbol,
                     (InputParameterToken)compareFrom);
               } else {
                  comparison = target.getEntityWherePathToPath(
                     compareFrom.toString(),
                     compareSymbol,
                     compareTo);
               }
               
               if(comparison == null) {
                  a.setInvalid();
               } else {
                  a.push(comparison);
               }
            }
         });
      }
      return colMemExp;
   }

   // comparison_expression ::=
   //    string_value { =|<>} string_expression |
   //    boolean_value { =|<>} boolean_expression} |
   //    datetime_value { = | <> | > | < } datetime_expression |
   //    entity_bean_value { = | <> } entity_bean_expression |
   //    arithmetic_value comparison_operator single_value_designator
   private Alternation compExp;
   protected Parser comparisonExpression() {
      if(compExp == null) {
         compExp = new Alternation();
         
         Sequence stringComp = new Sequence();
         stringComp.add(stringValue());
         stringComp.add(new Alternation().add(new Symbol("=")).add(new Symbol("<>")));
         stringComp.add(stringExpression());
         compExp.add(stringComp);
         
         Sequence booleanComp = new Sequence();
         booleanComp.add(booleanValue());
         booleanComp.add(new Alternation().add(new Symbol("=")).add(new Symbol("<>")));
         booleanComp.add(booleanExpression());
         compExp.add(booleanComp);
         
         Sequence datetimeComp = new Sequence();
         datetimeComp.add(datetimeValue());
         datetimeComp.add(new Alternation().add(new Symbol("=")).add(new Symbol("<>")).add(new Symbol(">")).add(new Symbol("<")));
         datetimeComp.add(datetimeExpression());
         compExp.add(datetimeComp);
         
         Sequence entityBeanComp = new Sequence();
         entityBeanComp.add(entityBeanValue());
         entityBeanComp.add(new Alternation().add(new Symbol("=")).add(new Symbol("<>")));
         entityBeanComp.add(entityBeanExpression());
         entityBeanComp.setAssembler(entityBeanComparisonAssembler());
         compExp.add(entityBeanComp);

         Sequence arithComp = new Sequence();
         arithComp.add(arithmeticValue());
         arithComp.add(comparisonOperator());
         arithComp.add(singleValueDesignator());
         compExp.add(arithComp);

         // Non-compliant addition to compare dependent value objects
         Sequence valueObjectComp = new Sequence();
         valueObjectComp.add(valueObjectValue());
         valueObjectComp.add(new Alternation().add(new Symbol("=")).add(new Symbol("<>")));
         valueObjectComp.add(valueObjectExpression());
         valueObjectComp.setAssembler(valueObjectBeanComparisonAssembler());
         compExp.add(valueObjectComp);         
      }
      return compExp;
   }

   // arithmetic_value ::= single_valued_path_expression | functions_returning_numerics
   private Alternation arithValue;
   protected Parser arithmeticValue() {
      if(arithValue == null) {
         arithValue = new Alternation();
         arithValue.add(arithmeticValuedPathExpression());
         arithValue.add(functionsReturningNumerics());
      }
      return arithValue;
   }
   
   // single_value_designator ::= scalar_expression
   protected Parser singleValueDesignator() {
      return scalarExpression();
   }
   
   // comparison_operator ::=   = | > | >= | < | <= | <>
   private Alternation compOpp;
   protected Parser comparisonOperator() {
      if(compOpp == null) {
         compOpp = new Alternation();
         compOpp.add(new Symbol("="));
         compOpp.add(new Symbol(">"));
         compOpp.add(new Symbol(">="));
         compOpp.add(new Symbol("<"));
         compOpp.add(new Symbol("<="));
         compOpp.add(new Symbol("<>"));
      }
      return compOpp;
   }
   
   // scalar_expression ::= arithmetic_expression
   protected Parser scalarExpression() {
      return arithmeticExpression();
   }
   
   // arithmetic_expression ::= arithmetic_term | arithmetic_expression { + | - } arithmetic_term
   // convert to elimiate infinite recursion
   // arithmetic_expression ::= arithmetic_term {{ + | - } arithmetic_term}*
   private Sequence arithExp;
   protected Parser arithmeticExpression() {
      if(arithExp == null) {
         arithExp = new Sequence();
         arithExp.add(arithmeticTerm());
         
         Sequence addSeq = new Sequence();
         addSeq.add(new Alternation().add(new Symbol("+")).add(new Symbol("-")));
         addSeq.add(arithmeticTerm());
         
         arithExp.add(new Repetition(addSeq));
      }
      return arithExp;
   }
   
   // arithmetic_term ::= arithmetic_factor | arithmetic_term { * | / } arithmetic_factor
   // convert to elimiate infinite recursion
   // arithmetic_term ::= arithmetic_factor {{ * | / } arithmetic_factor}*
   private Sequence arithTerm;
   protected Parser arithmeticTerm() {
      if(arithTerm == null) {
         arithTerm = new Sequence();
         arithTerm.add(arithmeticFactor());

         Sequence multSeq = new Sequence();
         multSeq.add(new Alternation().add(new Symbol("*")).add(new Symbol("/")));
         multSeq.add(arithmeticFactor());
         
         arithTerm.add(new Repetition(multSeq));
      }
      return arithTerm;
   }

   // arithmetic_factor ::= { + |- } arithmetic_primary
   // Note: changed due from obvious typo in pfd2
   // arithmetic_factor ::= [ + |- ] arithmetic_primary
   private Sequence arithFactor;
   protected Parser arithmeticFactor() {
      if(arithFactor == null) {
         arithFactor = new Sequence();
         arithFactor.add(new Optional(new Alternation().add(new Symbol("+")).add(new Symbol("-"))));
         arithFactor.add(arithmeticPrimary());
      }
      return arithFactor;
   }
   
   // arithmetic_primary ::= single_valued_path_expression | literal | (arithmetic_expression) | input_parameter | functions_returning_numerics
   private Alternation arithPrim;
   protected Parser arithmeticPrimary() {
      if(arithPrim == null) {
         arithPrim = new Alternation();
         arithPrim.add(arithmeticValuedPathExpression());
         arithPrim.add(new NumericLiteral());
         
         Sequence parenExp = new Sequence();
         parenExp.add(new Symbol("("));
         parenExp.add(arithmeticExpression());
         parenExp.add(new Symbol(")"));
         arithPrim.add(parenExp);
         
         arithPrim.add(arithmeticValuedParameter());
         arithPrim.add(functionsReturningNumerics());
      }
      return arithPrim;
   }
   
   // string_value ::= single_valued_path_expression | functions_returning_strings
   private Alternation strValue;
   protected Parser stringValue() {
      if(strValue == null) {
         strValue = new Alternation();
         strValue.add(stringValuedPathExpression());
         strValue.add(functionsReturningStrings());
      }
      return strValue;
   }
   
   // string_expression ::= string_primary | input_expression
   private Alternation strExp;
   protected Parser stringExpression() {
      if(strExp == null) {
         strExp = new Alternation();
         strExp.add(stringPrimary());
         strExp.add(stringValuedParameter());
      }
      return strExp;
   }
      
   // string_primary ::= single_valued_path_expression | literal | (string_expression) | functions_returning_strings
   private Alternation strPrim;
   protected Parser stringPrimary() {
      if(strPrim == null) {
         strPrim = new Alternation();
         strPrim.add(stringValuedPathExpression());
         strPrim.add(new StringLiteral());
         
         Sequence parenExp = new Sequence();
         parenExp.add(new Symbol("("));
         parenExp.add(stringExpression());
         parenExp.add(new Symbol(")"));
         strPrim.add(parenExp);
      
         strPrim.add(functionsReturningStrings());
      }
      return strPrim;
   }
   
   // datetime_value ::= single_valued_path_expression
   protected Parser datetimeValue() {
      return datetimeValuedPathExpression();
   }
   
   // datetime_expression ::= datetime_value | input_parameter
   private Alternation dateExp;
   protected Parser datetimeExpression() {
      if(dateExp == null) {
         dateExp = new Alternation();
         dateExp.add(datetimeValue());
         dateExp.add(datetimeValuedParameter());
      }
      return dateExp;
   }
   
   // boolean_value ::= single_valued_path_expression
   protected Parser booleanValue() {
      return booleanValuedPathExpression();
   }
   
   // boolean_expression ::= single_valued_path_expression | literal | input_parameter
   private Alternation boolExp;
   protected Parser booleanExpression() {
      if(boolExp == null) {
         boolExp = new Alternation();
         boolExp.add(booleanValuedPathExpression());
         boolExp.add(new Literal("TRUE"));
         boolExp.add(new Literal("FALSE"));
         boolExp.add(booleanValuedParameter());
      }
      return boolExp;
   }
   
   // entity_bean_value ::= single_valued_path_expression | identification_variable
   private Alternation entBeanVal;
   protected Parser entityBeanValue() {
      if(entBeanVal == null) {
         entBeanVal = new Alternation();
         entBeanVal.add(entityBeanValuedPathExpression());
         entBeanVal.add(identificationVariable());
      }
      return entBeanVal;
   }
   
   // CHANGED in FD
   // entity_bean_expression ::= entity_bean_value | input_parameter
   private Alternation entBeanExp;
   protected Parser entityBeanExpression() {
      if(entBeanExp == null) {
         entBeanExp = new Alternation();
         entBeanExp.add(entityBeanValue());
         entBeanExp.add(entityBeanValuedParameter());
      }
      return entBeanExp;
   }
      
   // non-compliant adition to compare dependant value objects
   protected Parser valueObjectValue() {
      return valueObjectValuedPathExpression();
   }
   
   // non-compliant adition to compare dependant value objects
   private Alternation valueObjectExp;
   protected Parser valueObjectExpression() {
      if(valueObjectExp == null) {
         valueObjectExp = new Alternation();
         valueObjectExp.add(valueObjectValue());
         valueObjectExp.add(valueObjectValuedParameter());
      }
      return valueObjectExp;
   }

   // functions_returning_strings ::= CONCAT (string_expression, string_expression) |
   //    SUBSTRING (string_expression, arithmetic_expression, arithmetic_expression)
   private Alternation funRetStr;
   protected Parser functionsReturningStrings() {
      if(funRetStr == null) {
         funRetStr = new Alternation();
         
         Sequence concat = new Sequence();
         concat.add(new Literal("CONCAT").discard());
         concat.add(new Symbol("(").discard());
         concat.add(stringExpression());
         concat.add(new Symbol(",").discard());
         concat.add(stringExpression());
         concat.add(new Symbol(")").discard());
         concat.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String param2 = a.pop().toString();
               String param1 = a.pop().toString();
               a.push(target.getConcatFunction(param1, param2));
            }
         });
         funRetStr.add(concat);
         
         Sequence substring = new Sequence();
         substring.add(new Literal("SUBSTRING").discard());
         substring.add(new Symbol("(").discard());
         substring.add(stringExpression());
         substring.add(new Symbol(",").discard());
         substring.add(arithmeticExpression());
         substring.add(new Symbol(",").discard());
         substring.add(arithmeticExpression());
         substring.add(new Symbol(")").discard());
         substring.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String param3 = a.pop().toString();
               String param2 = a.pop().toString();
               String param1 = a.pop().toString();
               a.push(target.getSubstringFunction(param1, param2, param3));
            }
         });
         funRetStr.add(substring);

      }
      return funRetStr;
   }


   // functions_returning_numerics::=
   //    LENGTH (string_expression) |
   //    LOCATE (string_expression, string_expression[, arithmetic_expression]) |
   //    ABS (arithmetic_expression) |
   //    SQRT (arithmetic_expression)
   private Alternation funRetNum;
   protected Parser functionsReturningNumerics() {
      if(funRetNum == null) {
         funRetNum = new Alternation();
         
         Sequence length = new Sequence();
         length.add(new Literal("LENGTH").discard());
         length.add(new Symbol("(").discard());
         length.add(stringExpression());
         length.add(new Symbol(")").discard());
         length.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String param = a.pop().toString();
               a.push(target.getLengthFunction(param));
            }
         });
         funRetNum.add(length);
         
         Sequence locate = new Sequence();
         locate.add(new Literal("LOCATE"));
         locate.add(new Symbol("(").discard());
         locate.add(stringExpression());
         locate.add(new Symbol(",").discard());
         locate.add(stringExpression());
            Sequence start = new Sequence();
            start.add(new Symbol(",").discard());
            start.add(arithmeticExpression());
         locate.add(new Optional(start));
         locate.add(new Symbol(")").discard());
         locate.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String param3 = a.pop().toString();
               String param2 = a.pop().toString();
               String param1 = a.pop().toString();
               if(param1.equalsIgnoreCase("LOCATE")) {
                  param1 = param2;
                  param2 = param3;
                  param3 = "0";
               } else {
                  a.pop(); // pop the token "LOCATE"
               }
               a.push(target.getLocateFunction(param1, param2, param3));
            }
         });
         funRetNum.add(locate);

         Sequence abs = new Sequence();
         abs.add(new Literal("ABS").discard());
         abs.add(new Symbol("(").discard());
         abs.add(arithmeticExpression());
         abs.add(new Symbol(")").discard());
         abs.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               String param = a.pop().toString();
               SQLTarget target = (SQLTarget)a.getTarget();
               a.push(target.getAbsFunction(param));
            }
         });
         funRetNum.add(abs);

         Sequence sqrt = new Sequence();
         sqrt.add(new Literal("SQRT").discard());
         sqrt.add(new Symbol("(").discard());
         sqrt.add(arithmeticExpression());
         sqrt.add(new Symbol(")").discard());
         sqrt.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String param = a.pop().toString();
               a.push(target.getSqrtFunction(param));
            }
         });
         funRetNum.add(sqrt);
      }
      return funRetNum;
   }
   
   protected Parser abstractSchemaName() {
      Word abstractSchemaName = new Word();
      abstractSchemaName.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            SQLTarget target = (SQLTarget)a.getTarget();
            String name = a.pop().toString();

            AbstractSchema schema = target.createAbstractSchema(name);
             if(schema == null) {
               a.setInvalid();
            } else {
               a.push(schema);
            }
         }
      });
      return abstractSchemaName;
   }

   protected Parser identifier() {
      Word identifier = new Word();
      identifier.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            // convert identifier to lowercase
            // identifiers are case insensitive
            a.push(a.pop().toString().toLowerCase());
         }
      });
      return identifier;
   }

   protected Parser cmpField() {
      Word cmpFieldParser = new Word();
      cmpFieldParser.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            SQLTarget target = (SQLTarget)a.getTarget();
            String cmpFieldName = a.pop().toString();
            String path = (String)a.pop();

            String fullPath = target.getCMPField(path, cmpFieldName);
             if(fullPath == null) {
               a.setInvalid();
            } else {
               a.push(fullPath);
            }
         }
      });
      return cmpFieldParser;
   }
   
   protected Parser singleValuedCmrField() {
      Word cmrFieldParser = new Word();
      cmrFieldParser.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            SQLTarget target = (SQLTarget)a.getTarget();
            String cmrFieldName = a.pop().toString();
            String path = (String)a.pop();

            String fullPath = target.getSingleValuedCMRField(path, cmrFieldName);
             if(fullPath == null) {
               a.setInvalid();
            } else {
               a.push(fullPath);
            }
         }
      });
      return cmrFieldParser;
   }
   
   protected Parser collectionValuedCmrField() {
      Word cmrFieldParser = new Word();
      cmrFieldParser.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            SQLTarget target = (SQLTarget)a.getTarget();
            String cmrFieldName = a.pop().toString();
            String path = (String)a.pop();

            String fullPath = target.getCollectionValuedCMRField(path, cmrFieldName);
             if(fullPath == null) {
               a.setInvalid();
            } else {
               a.push(fullPath);
            }
         }
      });
      return cmrFieldParser;
   }
   
   protected Parser identificationVariable() {
      Word identificationVariable = new Word();
      identificationVariable.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            SQLTarget target = (SQLTarget)a.getTarget();
            // convert identifier to lowercase 
            // identifiers are case insensitive
            String identifier = a.pop().toString().toLowerCase();

            if(!target.isIdentifierRegistered(identifier)) {
               a.setInvalid();
            } else {
               a.push(identifier);
            }
         }
      });
      return identificationVariable;
   }

   private Sequence stringPathExp;
   protected Parser stringValuedPathExpression () {
      if(stringPathExp == null) {
         stringPathExp = new Sequence();
         stringPathExp.add(singleValuedPathExpression());
         stringPathExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String path = (String)a.pop();
            
               if(!target.isStringTypePath(path)) {
                  a.setInvalid();
               } else {
                  a.push(target.getCMPFieldColumnNamesClause(path));
               }
            }
         });
      }
      return stringPathExp;
   }
   
   private Parser stringParam;
   protected Parser stringValuedParameter() {
      if(stringParam == null) {
         stringParam = new InputParameter();
         stringParam.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               InputParameterToken token = (InputParameterToken)a.pop();
            
               if(!target.isStringTypeParameter(token.getNumber())) {
                  a.setInvalid();
               } else {
                  target.registerParameter(token);
                  a.push("?");
               }
            }
         });
      }
      return stringParam;
   }
   
   private Sequence booleanPathExp;
   protected Parser booleanValuedPathExpression () {
      if(booleanPathExp == null) {
         booleanPathExp = new Sequence();
         booleanPathExp.add(singleValuedPathExpression());
         booleanPathExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String path = (String)a.pop();
            
               if(!target.isBooleanTypePath(path)) {
                  a.setInvalid();
               } else {
                  a.push(target.getCMPFieldColumnNamesClause(path));
               }
            }
         });
      }
      return booleanPathExp;
   }
   
   private Parser booleanParam;
   protected Parser booleanValuedParameter() {
      if(booleanParam == null) {
         booleanParam = new InputParameter();
         booleanParam.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               InputParameterToken token = (InputParameterToken)a.pop();
            
               if(!target.isBooleanTypeParameter(token.getNumber())) {
                  a.setInvalid();
               } else {
                  target.registerParameter(token);
                  a.push("?");
               }
            }
         });
      }
      return booleanParam;
   }
 
   private Sequence datetimePathExp;
   protected Parser datetimeValuedPathExpression () {
      if(datetimePathExp == null) {
         datetimePathExp = new Sequence();
         datetimePathExp.add(singleValuedPathExpression());
         datetimePathExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String path = (String)a.pop();
            
               if(!target.isDatetimeTypePath(path)) {
                  a.setInvalid();
               } else {
                  a.push(target.getCMPFieldColumnNamesClause(path));
               }
            }
         });
      }
      return datetimePathExp;
   }

   private Parser datetimeParam;
   protected Parser datetimeValuedParameter() {
      if(datetimeParam == null) {
         datetimeParam = new InputParameter();
         datetimeParam.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               InputParameterToken token = (InputParameterToken)a.pop();
            
               if(!target.isDatetimeTypeParameter(token.getNumber())) {
                  a.setInvalid();
               } else {
                  target.registerParameter(token);
                  a.push("?");
               }
            }
         });
      }
      return datetimeParam;
   }
    
   private Sequence entityBeanPathExp;
   protected Parser entityBeanValuedPathExpression () {
      if(entityBeanPathExp == null) {
         entityBeanPathExp = new Sequence();
         entityBeanPathExp.add(singleValuedPathExpression());
         entityBeanPathExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String path = (String)a.pop();
            
               if(!target.isEntityBeanTypePath(path)) {
                  a.setInvalid();
               } else {
                  a.push(path);
               }
            }
         });
      }
      return entityBeanPathExp;
   }
   
   private Parser entityBeanParam;
   protected Parser entityBeanValuedParameter() {
      if(entityBeanParam == null) {
         entityBeanParam = new InputParameter();
         entityBeanParam.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               InputParameterToken token = (InputParameterToken)a.pop();
            
               if(!target.isEntityBeanTypeParameter(token.getNumber())) {
                  a.setInvalid();
               } else {
                  a.push(token);
               }
            }
         });
      }
      return entityBeanParam;
   }
    
   private Sequence arithmeticPathExp;
   protected Parser arithmeticValuedPathExpression () {
      if(arithmeticPathExp == null) {
         arithmeticPathExp = new Sequence();
         arithmeticPathExp.add(singleValuedPathExpression());
         arithmeticPathExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String path = (String)a.pop();
            
               if(!target.isArithmeticTypePath(path)) {
                  a.setInvalid();
               } else {
                  a.push(target.getCMPFieldColumnNamesClause(path));
               }
            }
         });
      }
      return arithmeticPathExp;
   }

   private Parser arithmeticParam;
   protected Parser arithmeticValuedParameter() {
      if(arithmeticParam == null) {
         arithmeticParam = new InputParameter();
         arithmeticParam.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               InputParameterToken token = (InputParameterToken)a.pop();
            
               if(!target.isArithmeticTypeParameter(token.getNumber())) {
                  a.setInvalid();
               } else {
                  target.registerParameter(token);
                  a.push("?");
               }
            }
         });
      }
      return arithmeticParam;
   }
   
   private Sequence valueObjectPathExp;
   protected Parser valueObjectValuedPathExpression () {
      if(valueObjectPathExp == null) {
         valueObjectPathExp = new Sequence();
         valueObjectPathExp.add(singleValuedPathExpression());
         valueObjectPathExp.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               String path = (String)a.pop();
            
               if(!target.isValueObjectTypePath(path)) {
                  a.setInvalid();
               } else {
                  a.push(path);
               }
            }
         });
      }
      return valueObjectPathExp;
   }

   private Parser valueObjectParam;
   protected Parser valueObjectValuedParameter() {
      if(valueObjectParam == null) {
         valueObjectParam = new InputParameter();
         valueObjectParam.setAssembler(new Assembler() {
            public void workOn(Assembly a) {
               SQLTarget target = (SQLTarget)a.getTarget();
               InputParameterToken token = (InputParameterToken)a.pop();
            
               if(!target.isValueObjectTypeParameter(token.getNumber())) {
                  a.setInvalid();
               } else {
                  a.push(token);
               }
            }
         });
      }
      return valueObjectParam;
   }
    


   private Assembler entityBeanComparisonAssembler() {
      return new Assembler() {
         public void workOn(Assembly a) {
            SQLTarget target = (SQLTarget)a.getTarget();
            Object compareTo = a.pop();
            String compareSymbol = a.pop().toString();
            String compareFromPath = (String)a.pop();

            String comparison;
            if(compareTo instanceof InputParameterToken) {
               // path = ?1
               comparison = target.getEntityWherePathToParameter(
                     compareFromPath, 
                     compareSymbol,
                     (InputParameterToken)compareTo);               
            } else {
               // path = path
               comparison = target.getEntityWherePathToPath(
                     compareFromPath, 
                     compareSymbol, 
                     compareTo.toString());
            }
            if(comparison == null) {
               a.setInvalid();
            } else {
               a.push(comparison);
            }
         }
      };
   }

   private Assembler valueObjectBeanComparisonAssembler() {
      return new Assembler() {
         public void workOn(Assembly a) {
            SQLTarget target = (SQLTarget)a.getTarget();
            Object compareTo = a.pop();
            String compareSymbol = a.pop().toString();
            String compareFromPath = (String)a.pop(); // always a path

            String comparison;
            if(compareTo instanceof InputParameterToken) {
               // path = ?1
               comparison = target.getValueObjectWherePathToParameter(
                     compareFromPath,
                     compareSymbol,
                     (InputParameterToken)compareTo);
            } else {
               // path = path
               comparison = target.getValueObjectWherePathToPath(
                     compareFromPath,
                     compareSymbol, 
                     compareTo.toString());
            }
            if(comparison == null) {
               a.setInvalid();
            } else {
               a.push(comparison);
            }
         }
      };
   }

   protected Parser patternValue() {
      return new Word();
   }

   protected Parser escapeCharacter() {
      Parser escChar = new StringLiteral();
      escChar.setAssembler(new Assembler() {
         public void workOn(Assembly a) {
            String character = a.pop().toString();
            if(character.length() != 3) {
               a.setInvalid();
            } else {
               a.push("{escape "+character+"}");
            }
         }
      });
      return escChar;
   }
}