import org.apache.xerces.impl.dv.ValidationContext;

/*
 * The Apache Software License, Version 1.1
 *
 *
 * Copyright (c) 2001 The Apache Software Foundation.
 * All rights reserved.
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

package simpletype;

import org.apache.xerces.impl.dv.SchemaDVFactory;
import org.apache.xerces.impl.dv.XSSimpleType;
import org.apache.xerces.impl.dv.XSFacets;
import org.apache.xerces.impl.dv.ValidatedInfo;
import org.apache.xerces.impl.dv.InvalidDatatypeFacetException;
import org.apache.xerces.impl.dv.InvalidDatatypeValueException;
import org.apache.xerces.impl.xs.XSTypeDecl;
import org.apache.xerces.impl.xs.SchemaSymbols;
import org.apache.xerces.impl.validation.ValidationContext;
import org.apache.xerces.impl.validation.ValidationState;
import org.apache.xerces.impl.xs.psvi.*;

import java.util.Vector;

/**
 *  It demonstrates how to use the interfaces defined in 'org.apache.xerces.impl.dv'
 *  package for the purpose of
 * 1. how to query property information of Simple Type Definition Schema Component.
 * 2. how to get instance of SchemaDVFactory implementation.
 * 3. how to get built-in type/s and create new types as derived by restriction, list
 *      or union, using factory methods of SchemaDVFactory.
 * 4. how to use those simple type (built-in/created) to validate the values.
 *    This class is  useful for any application which wants to use the simple type
 * implementation directly as separate module.
 *
 * @author Neeraj Bajaj     Sun Microsystems, inc.
 *
 */

public class SimpleTypeUsage{

static SchemaDVFactory factory = null;
XSFacets facets = new XSFacets();

short fPresentFacets ;
short fFixedFacets ;
short fFinalSet ;


public SimpleTypeUsage(){

        //Any application willing to switch to different implementation should
        //call SchemaDVFactory#setFactoryClass() as the first step before calling
        //SchemaDVFactory#getInstance().
        //Suppose application wants to use class 'MySchemaDVFactoryImpl' as SchemaDVFactory
        // implementation which resides in say 'myApp.simpleType' package.
    
        //SchemaDVFactory.setFactoryClass("myApp.simpleType.MySchemaDVFactoryImpl.class");

        //this will give the instance of default implementation (SchemaDVFactoryImpl)
        // in 'org.apache.xerces.impl.dv.xs_new' package.
        factory = SchemaDVFactory.getInstance();

} //SimpleTypeUsage()


/**
*	Get proper validation context, it provides the information required for the validation of datatypes id, idref, 
*	entity, notation, qname , we need to get appropriate validation context for validating the content or creating 
*	simple type (applyFacets).
*	@return ValidationContext
*/

private ValidationContext getValidationContext(){

        ValidationState validationState = null;
        
    // create an instance of 'ValidationState' providing the information required for the
    // validation of datatypes id, idref, entity, notation, qname.
    //	application can also provide its own implementation of ValidationContext if required, 
    // an implementation of 'ValidationContext' is in 'org.apache.xerces.impl.validation' package.
    validationState = new ValidationState();
    
        // application need to pass validation context while validating string, object or creating simple type (applyFacets)
        // derived by restriction, should set the following information accordingly 
            
    //application should provide the namespace support by calling
    //validationState.setNamespaceSupport(...);

    //application can also provide 'SymbolTable' (org.apache.xerces.util.SymbolTable) like    
    //validationState.setSymbolTable(....);

        //set proper value (true/false) for the given validation context 
        //validationState.setFacetChecking(true);
        
        //set proper value (true/false) for the given validation context	
        //validationState.setExtraChecking(false);	
                
        return validationState;
        
}

/**
 * this method shows how to validate the content against the given simple type.
 *
 * @param String content to validate
 * @param XSSimpleType SimpleType Definition schema component against which to validate the content.
 *
 * @return ValidatedInfo validatedInfo object.
 */
public ValidatedInfo validateString(String content, XSSimpleType simpleType){

    //create an instance of 'ValidatedInfo' to get back information (like actual value,
    //normalizedValue etc..)after content is validated.
    ValidatedInfo validatedInfo = new ValidatedInfo();

        //get proper validation context , this is very important we need to get appropriate validation context while validating content
        //validation context passed is generally different while validating content and  creating simple type (applyFacets)
        ValidationContext validationState = getValidationContext();

    try{
        simpleType.validate(content, validationState, validatedInfo);
    }catch(InvalidDatatypeValueException ex){
        System.err.println(ex.getMessage());
    }

    //now 'validatedInfo' object contains information

    // for number types (decimal, double, float, and types derived from them),
    // Object return is BigDecimal, Double, Float respectively.
    // for some types (string and derived), they just return the string itself
    Object value = validatedInfo.actualValue;
    //so returned Object can be casted to actual java object like..
    //Boolean booleanDT = (Boolean)value;

    //The normalized value of a string value
    String normalizedValue = validatedInfo.normalizedValue ;

    //If the type is a union type, then the member type which
    //actually validated the string value.
    XSSimpleType memberType = validatedInfo.memberType ;

    return validatedInfo;

}//validateString()

/**
 * this method shows how to query information about the different properties of 'Simple Type'
 * definiton schema component. It prints the values of properties of 'SimpleType Definition
 * Schema Component'.
 *
 * @param simpleType    object of XSSimpleType
 */
public void querySimpleType(XSSimpleType simpleType){

    //getting information about the different properties of 'Simple Type' definition schema component.
    System.err.println();
    System.err.println( "Properties information of 'Simple Type' definiton schema component" );
    System.err.println();
    // 'name' property
    if( simpleType.getIsAnonymous() )
        System.err.println( "Anonymous Simple Type" );
    else{
        System.err.println("'name' \t\t\t\t: " + simpleType.getName()  );
    }

    //'target namespace' property
    String targetNameSpace = simpleType.getNamespace() ;
    System.err.println("'target namespace' \t\t: " + targetNameSpace  );

    // 'variety' property
    short variety = simpleType.getVariety();
    printVariety(variety);

    //'base type definition' property
    XSTypeDecl baseType = (XSTypeDecl)simpleType.getBaseType() ;
    System.err.println("'base type definition' name \t: " + ( baseType != null ? baseType.getName() : "null" )   );
    System.err.println("'base type definition' target namespace : " + ( baseType != null ? baseType.getNamespace() : "null" )   );

    //check if base type is simple or complex
    if(baseType != null && (baseType.getTypeCategory() == XSTypeDecl.SIMPLE_TYPE) ){
        //now we can get all the details of base type
        XSSimpleType simpleTypeDecl = (XSSimpleType)baseType;
    }

    // 'facets' property
    // gives bit combination of the constants defined in XSSimpleType interface.
    short facets = simpleType.getDefinedFacets() ;
    printFacets(facets);

    //'final' property
    //the explicit values of this property extension, restriction, list and union prevent further
    //derivations by extension (to yield a complex type) and restriction (to yield a simple type)
    //and use in constructing lists and unions respectively.
    short finalSet = simpleType.getFinal() ;
    printFinal(finalSet);

    //if variety is 'list'
    if( variety == XSSimpleType.VARIETY_LIST ){
        // 'Item Type definition' property of List Simple Type Definition Schema Component.
        XSSimpleType listDecl = (XSSimpleType)simpleType.getItemType();
    }else if(variety == XSSimpleType.VARIETY_UNION ){
        // 'Member Type definitions' property of Union Simple Type Definition Schema Component.
        XSObjectList memberTypes = simpleType.getMemberTypes();
    }
    
    //fundamental facet information
    
    //ordered schema component
    short ordered = simpleType.getOrdered();
    printOrdered(ordered);

    //bounded schema component
    boolean bounded = simpleType.getIsBounded();    
    if(bounded){
        System.err.println("'bounded' \t\t\t\t: true"  );
    }
    else{
        System.err.println("'bounded' \t\t\t\t: false"  );
    }
    
    //cardinality schema component
    boolean isFinite = simpleType.getIsFinite();
    printCardinality(isFinite);
    
    //numeric schema component
    boolean numeric = simpleType.getIsNumeric();
    if(numeric){
        System.err.println("'numeric' \t\t\t\t: true"  );
    }
    else{
        System.err.println("'numeric' \t\t\t\t: false"  );
    }
    


}//getInformation()

void printOrdered (short ordered){

    switch(ordered){
    
        case XSSimpleType.ORDERED_FALSE:
            System.err.println("'ordered' \t\t\t\t: false"  );
            break;
            
        case XSSimpleType.ORDERED_PARTIAL:
            System.err.println("'ordered' \t\t\t\t: partial"  );
            break;
            
        case XSSimpleType.ORDERED_TOTAL:
            System.err.println("'ordered' \t\t\t\t: total"  );
            break;
            
    }
}//printOrdered()

void printCardinality (boolean isFinite){
    
    if(!isFinite)
        System.err.println("'cardinality' \t\t\t\t: countably infinite"  );
    else
        System.err.println("'cardinality' \t\t\t\t: finite"  );

}//printCardinality()

void printFacets(short facets){

    System.err.println("'facets' present \t\t: " );

    if(( facets & XSSimpleType.FACET_ENUMERATION) != 0){
        System.err.println("\t\t\t\t ENUMERATION");
    }
    if((facets & XSSimpleType.FACET_LENGTH) != 0){
        System.err.println("\t\t\t\t LENGTH");
    }
    if((facets & XSSimpleType.FACET_MINLENGTH) != 0){
        System.err.println("\t\t\t\t MINLENGTH");
    }
    if((facets & XSSimpleType.FACET_MAXLENGTH) != 0){
        System.err.println("\t\t\t\t MAXLENGTH");
    }
    if((facets & XSSimpleType.FACET_PATTERN) != 0){
        System.err.println("\t\t\t\t PATTERN");
    }
    if((facets & XSSimpleType.FACET_WHITESPACE) != 0){
        System.err.println("\t\t\t\t WHITESPACE");
    }
    if((facets & XSSimpleType.FACET_MAXINCLUSIVE) != 0){
        System.err.println("\t\t\t\t MAXINCLUSIVE");
    }
    if((facets & XSSimpleType.FACET_MAXEXCLUSIVE) != 0){
        System.err.println("\t\t\t\t MAXEXCLUSIVE");
    }
    if((facets & XSSimpleType.FACET_MININCLUSIVE) != 0){
        System.err.println("\t\t\t\t MININCLUSIVE");
    }
    if((facets & XSSimpleType.FACET_MINEXCLUSIVE) != 0){
        System.err.println("\t\t\t\t MINEXCLUSIVE");
    }
    if((facets & XSSimpleType.FACET_TOTALDIGITS) != 0){
        System.err.println("\t\t\t\t TOTALDIGITS");
    }
    if((facets & XSSimpleType.FACET_FRACTIONDIGITS) != 0){
        System.err.println("\t\t\t\t FRACTIONDIGITS");
    }

}//printFacets()

void printFinal(short finalSet){

    System.err.println("'final' values \t\t\t: " );

    if ((finalSet & XSConstants.DERIVATION_EXTENSION ) != 0){
        System.err.println("\t\t\t\t Extension");
    }
    if ((finalSet & XSConstants.DERIVATION_RESTRICTION) != 0){
        System.err.println("\t\t\t\t Restriction");
    }
    if((finalSet & XSConstants.DERIVATION_LIST ) != 0){
        System.err.println("\t\t\t\t List");
    }
    if((finalSet & XSConstants.DERIVATION_UNION ) != 0){
        System.err.println("\t\t\t\t Union");
    }
    if((finalSet & XSConstants.DERIVATION_NONE ) != 0){
        System.err.println("\t\t\t\t EMPTY");
    }

}

void printVariety(short variety){

    switch(variety){

    case XSSimpleType.VARIETY_ATOMIC:
        System.err.println("'variety' \t\t\t: ATOMIC");
        break;

    case XSSimpleType.VARIETY_LIST:
        System.err.println("'variety' \t\t\t: LIST");
        break;

    case XSSimpleType.VARIETY_UNION:
        System.err.println("'variety' \t\t\t: UNION");
        break;

    default:
        System.err.println("Invalid value of 'Variety' property , it should be one of atomic, list or union.");
        break;
    }


} //printVariety()


public static void main(String [] args){

    SimpleTypeUsage usage = new SimpleTypeUsage();

    if(args.length == 1 ){         
        XSSimpleType builtInType = factory.getBuiltInType(args[0]);
        if(builtInType == null){
            System.err.println("Invalid built-in Simple datatype given as argument.");
            printUsage();
        }
        else {
            usage.querySimpleType(builtInType);
        }

    }else{
        printUsage();
    }

}//main()

static void printUsage(){
        System.err.println("USAGE: java simpletype.SimpleTypeUsage  'Built-InDatatypeName' ");
        System.err.println();

        System.err.println("  Built-InDatatypeName  \t\tBuilt-In Datatype name as defined by W3C Schema Spec, \n\t\t\t\t\t \"http://www.w3.org/TR/xmlschema-2/#built-in-datatypes\" .");        
        System.err.println();
}

}//class SimpleTypeUsage