saxparser=ParserFactory.makeParser("com.sun.xml.parser.Parser");

package org.apache.tomcat.util.xml;

import org.apache.tomcat.util.*;
import java.beans.*;
import java.io.*;
import java.io.IOException;
import java.lang.reflect.*;
import java.net.URL;
import java.net.URLConnection;
import java.util.*;
import java.util.StringTokenizer;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import org.xml.sax.*;
import org.xml.sax.helpers.*;


/**
 * SAX Handler - it will read the XML and construct java objects
 *
 * @author costin@dnt.ro
 */
public class XmlMapper
    extends HandlerBase
    implements SaxContext {

    Locator locator;

    /**
     * The URLs of DTDs that have been registered, keyed by the public
     * identifier that corresponds.
     */
    private Hashtable fileDTDs = new Hashtable();
    private Hashtable resDTDs = new Hashtable();

    // Stack of elements
    Stack oStack=new Stack();
    Object root;
    Object attributeStack[];
    String tagStack[];
    int oSp;
    int sp;

    String body;

    int debug=0;
    boolean validating=false;

    public XmlMapper() {
	attributeStack = new Object[100]; // depth of the xml doc
	tagStack = new String[100];
	initDefaultRules();
    }

    public void setDocumentLocator (Locator locator)
    {
	if( debug>0 ) log("Set locator : " + locator);
	this.locator = locator;
    }

    public void startDocument () throws SAXException
    {
        sp = 0;
    }

    public void endDocument () throws SAXException
    {
        if (sp != 0) {
	    System.out.println("The XML document is probably broken. " + sp);
	}
    }

    public void startElement (String tag, AttributeList attributes)
	throws SAXException
    {
	try {
	    //	    if( debug>0) log(sp + "<" + tag + " " + attributes + ">");
	    attributeStack[sp]=attributes;
	    tagStack[sp]=tag;
	    sp++;
	    matchStart( this);
	    body="";
	} catch (Exception ex) {
	    // do not ignore messages, caller should handle it
	    throw new SAXException( positionToString(), ex );
	}
    }

    private String positionToString() {
	StringBuffer sb=new StringBuffer();
	if( locator!=null ) sb.append("Line ").append(locator.getLineNumber()).append(" ");
	sb.append("/");
	for( int i=0; i< sp ; i++ ) sb.append( tagStack[i] ).append( "/" );
	sb.append(" ");
	AttributeList attributes=(AttributeList) attributeStack[sp-1];
	if( attributes!=null)
	    for (int i = 0; i < attributes.getLength (); i++) {
		sb.append(attributes.getName(i)).append( "=" ).append(attributes.getValue(i));
		sb.append(" ");
	    }

	return sb.toString();
    }

    public void endElement (String tag) throws SAXException
    {
	try {
	    // Find a match for the current tag in the context
	    matchEnd( this);

	    if( sp > 1 ) {
		tagStack[sp] = null;
		attributeStack[sp]=null;
	    }
	    sp--;
	} catch (Exception ex) {
	    // do not ignore messages, caller should handle it
	    throw new SAXException(  positionToString(), ex );
	}

    }

    public void characters (char buf [], int offset, int len)
	throws SAXException
    {
	body=body+ new String(buf, offset, len );
    }

    public void ignorableWhitespace (char buf [], int offset, int len)
	throws SAXException
    {
    }

    public void processingInstruction (String name, String instruction)
	throws SAXException
    {
    }

    // -------------------- Context --------------------
    // provide access to the current stack and XML elements.
    // -------------------- Context --------------------

    public AttributeList getAttributeList( int pos ) {
	return (AttributeList)attributeStack[pos];
    }

    public int getTagCount() {
	return sp;
    }

    public String getTag( int pos ) {
	return tagStack[pos];
    }

    public String getBody() {
	return body;
    }

    public Stack getObjectStack() {
	return oStack;
    }

    public Object getRoot() {
	return root;
    }

    public void setRoot(Object o) {
	root=o;
    }

    // -------------------- Utils --------------------
    // Debug ( to be replaced with the real thing )
    public void setDebug( int level ) {
	if(level!=0) log( "Debug level: " + level );
	debug=level;
    }

    public int getDebug() {
	return debug;
    }

    public void setValidating( boolean validating ) {
	if (debug >= 1)
	    log("Validating = " + validating);
	this.validating = validating;
    }

    public boolean getValidating() {
	return (this.validating);
    }

    public void log(String msg) {
	// log is for debug only, it should't be enabled for anything else
	// ( no dependency on Logger or any external tomcat package )
	System.out.println("XmlMapper: " + msg);
    }

    /** read an XML file, construct and return the object hierarchy
     */
    public Object readXml(File xmlFile, Object root)
	throws Exception
    {
	if(root!=null) {
	    Stack st=this.getObjectStack();
	    this.root=root;
	    st.push( root );
	}
	SAXParser parser=null;
	try {
	    try {
		SAXParserFactory factory = SAXParserFactory.newInstance();
		factory.setNamespaceAware(false);
		factory.setValidating(validating);
		parser = factory.newSAXParser();
		parser.parse(xmlFile, this);
	    } catch (javax.xml.parsers.FactoryConfigurationError jaxpE ) {
		org.xml.sax.Parser saxparser=null;
		if(System.getProperty("org.xml.sax.parser") != null )
		    saxparser=ParserFactory.makeParser();
		else
		    saxparser=ParserFactory.makeParser("org.apache.crimson.parser.Parser");

		saxparser.setDocumentHandler( this );
		saxparser.setEntityResolver( this );
		saxparser.setDTDHandler( this );
		if( debug > 0 ) log("No jaxp, defaulting to old xml style " + xmlFile);
		saxparser.parse(new InputSource( new FileReader( xmlFile)));
	    }

	    return root;
	    // assume the stack is in the right position.
	    // or throw an exception is more than one element is on the stack
   	} catch (IOException ioe) {
	    ioe.printStackTrace();
	    String msg = "Can't open config file: " + xmlFile +
		" due to: " + ioe;
	    throw new Exception(msg);
	} catch (SAXException se) {
	    System.out.println("ERROR reading " + xmlFile);
	    System.out.println("At " + se.getMessage());
	    //	    se.printStackTrace();
	    System.out.println();
	    Exception ex1=se.getException();
	    if( ex1 != null )
		throw ex1;// xerces bug
	    else
		throw se;
	}
    }

    /** read an XML input stream, construct and return the object hierarchy
     */
    public Object readXml(InputStream xmlFile, Object root)
	throws Exception
    {
	if(root!=null) {
	    Stack st=this.getObjectStack();
	    this.root=root;
	    st.push( root );
	}
	SAXParser parser=null;
	try {
	    SAXParserFactory factory = SAXParserFactory.newInstance();
	    factory.setNamespaceAware(false);
	    factory.setValidating(validating);
	    parser = factory.newSAXParser();
	    parser.parse(xmlFile, this);
	    return root;
	    // assume the stack is in the right position.
	    // or throw an exception is more than one element is on the stack
   	} catch (IOException ioe) {
	    String msg = "Can't open config file: " + xmlFile +
		" due to: " + ioe;
	    throw new Exception(msg);
	} catch (SAXException se) {
	    System.out.println("ERROR reading " + xmlFile);
	    System.out.println("At " + se.getMessage());
	    //	    se.printStackTrace();
	    System.out.println();
	    Exception ex1=se.getException();
	    throw ex1;
	}
    }


    /**
     * Register the specified DTD with a local file.
     * This must be called prior to the first call to <code>readXml()</code>.
     *
     * @param publicId Public identifier of the DTD to be resolved
     * @param dtdFile The local file name to use for reading this DTD
     */
    public void registerDTDFile(String publicId, String dtdFile) {
	fileDTDs.put(publicId, dtdFile);
    }

    /**
     * Register the specified DTD to map to a resource in the classpath
     * This must be called prior to the first call to <code>readXml()</code>.
     *
     * @param publicId Public identifier of the DTD to be resolved
     * @param dtdRes local resource name, to be used with getResource()
     */
    public void registerDTDRes(String publicId, String dtdRes) {
	resDTDs.put(publicId, dtdRes);
    }


    class Rule {
	XmlMatch match;
	XmlAction action;
	Rule( XmlMatch match, XmlAction action ) {
	    this.match=match;
	    this.action=action;
	}
    }
    Rule rules[]=new Rule[100];
    Rule matching[]=new Rule[100];
    int ruleCount=0;

    /**
     */
    private void initDefaultRules() {
	// One-time actions, in line
	addRule( "xmlmapper:debug",
		 new XmlAction() {
			 public void start(SaxContext ctx) {
			     int top=ctx.getTagCount()-1;
			     AttributeList attributes = ctx.getAttributeList( top );
			     String levelS=attributes.getValue("level");
			     XmlMapper mapper=(XmlMapper)ctx;
			     if( levelS!=null)
				 mapper.setDebug( new Integer(levelS).intValue());
			 }
		     }
		 );
	// ant-like
	addRule( "xmlmapper:taskdef",
		 new XmlAction() {
			 public void start(SaxContext ctx) {
			     XmlMapper mapper=(XmlMapper)ctx;
			     int top=ctx.getTagCount()-1;
			     AttributeList attributes = ctx.getAttributeList( top );
			     String match=attributes.getValue("match");
			     if(match==null) return; //log
			     String obj=attributes.getValue("object-create");
			     String objA=attributes.getValue("object-create-attrib");
			     if( obj!=null || objA!=null)
				 mapper.addRule( match, new ObjectCreate( obj, objA));
			     obj=attributes.getValue("set-properties");
			     if( obj!=null)
				 mapper.addRule( match, new SetProperties());
			     obj=attributes.getValue("set-parent");
			     if( obj!=null)
				 mapper.addRule( match, new SetParent(obj));
			     obj=attributes.getValue("add-child");
			     objA=attributes.getValue("child-type");
			     if( obj!=null)
				 mapper.addRule( match, new AddChild(obj, objA));

			     // Custom actions
			     obj=attributes.getValue("action");
			     if( obj!=null) {
				 try {
				     Class c=Class.forName( obj );
				     Object o=c.newInstance();
				     mapper.addRule( match, (XmlAction)o);
				 } catch( Exception ex ) {
				     System.out.println("Can't add action " + obj);
				 }
			     }
			 }
		     }
		 );

    }

    public void addRule( String path, XmlAction action ) {
	rules[ruleCount]=new Rule( new PathMatch( path ) , action);
	ruleCount++;
    }

    private int match( SaxContext ctx, Rule matching[] ) {
	int matchCount=0;
	for( int i=0; i< ruleCount; i++ ) {
	    if( rules[i].match.match( ctx ) &&
		rules[i].action != null ) {
		matching[matchCount]=rules[i];
		matchCount++;
	    }
	}
	return matchCount;
    }

    void matchStart(SaxContext ctx ) throws Exception {
	int matchCount=match( ctx, matching );
	for ( int i=0; i< matchCount; i++ ) {
	    matching[i].action.start( ctx );
	}
    }

    void matchEnd(SaxContext ctx ) throws Exception {
	int matchCount=match( ctx, matching );
	for ( int i=0; i< matchCount; i++ )
	    matching[i].action.end( ctx );
	for ( int i=0; i< matchCount; i++ )
	    matching[i].action.cleanup( ctx );
    }


    /**
     * Resolve the requested external entity, replacing it by an internal
     * DTD if one has been registered.
     *
     * @param publicId Public identifier of the entity being referenced
     * @param systemId System identifier of the entity being referenced
     *
     * @exception SAXException if a parsing error occurs
     */
    public InputSource resolveEntity(String publicId, String systemId)
	throws SAXException
    {
	String dtd = (String) fileDTDs.get(publicId);
	if( dtd != null ) {
	    File dtdF=new File( dtd );
	    if( dtdF.exists() )
		try {
		    return new InputSource(new FileInputStream(dtdF));
		} catch( FileNotFoundException ex ) {
		}
	    // else continue
	}

	dtd = (String) resDTDs.get( publicId );
	if( dtd != null ) {
	    InputStream is = this.getClass().getResourceAsStream( dtd );
	    if( is!= null )
		return new InputSource(is);
	    System.out.println("XXX resource not found !!! " + dtd);
	}
	
	log("Can't find resource for entity: " + publicId + " --> " + systemId + " \"" + dtd +"\"");

	return null;
    }

    public void notationDecl (String name,
			      String publicId,
			      String systemId)
    {
	System.out.println("Notation: " + name + " " + publicId +
			   " " + systemId);
    }

    public  void unparsedEntityDecl (String name,
				     String publicId,
				     String systemId,
				     String notationName)
    {
	System.out.println("Unparsed: " + name + " " + publicId +
			   " " + systemId + " " + notationName);
    }


    // -------------------- Factories for "common" actions --------------------
    // XXX Probably it's better to use the real XmlActions, with new FooAction()

    /** Create an object using for a matching tag with the given class name
     */
    public XmlAction objectCreate( String classN ) {
	return new ObjectCreate( classN);
    }

    /** Create an object using an attribute value as the class name
	If no attribute use classN as a default.
     */
    public XmlAction objectCreate( String classN, String attrib ) {
	return new ObjectCreate( classN, attrib);
    }

    /** Set object properties using XML attributes
     */
    public XmlAction setProperties(  ) {
	return new SetProperties();
    }

    /** For the last 2 objects in stack, create a parent-child
     *	and child.childM with parente as parameter
     */
    public XmlAction setParent( String childM ) {
	return new SetParent( childM );
    }

    /** For the last 2 objects in stack, create a parent-child
     * and child.childM with parent as parameter
     */
    public XmlAction setParent( String childM, String argType ) {
	return new SetParent( childM, argType );
    }

    /** For the last 2 objects in stack, create a parent-child
     *  relation by invokeing parent.parentM with the child as parameter
     *  ArgType is the parameter expected by addParent ( null use the current object
     *  type)
     */
    public XmlAction addChild( String parentM, String argType ) {
	return new AddChild( parentM, argType );
    }

    /** If a tag matches, invoke a method on the current object.
	Parameters can be extracted from sub-elements of the current
	tag.
    */
    public XmlAction methodSetter(String method, int paramC) {
	return new MethodSetter(method, paramC);
    }

    /** If a tag matches, invoke a method on the current object.
	Parameters can be extracted from sub-elements of the current
	tag.
    */
    public XmlAction methodSetter(String method, int paramC, String paramTypes[]) {
	return new MethodSetter(method, paramC, paramTypes);
    }

    /** Extract the method param from the body of the tag
     */
    public XmlAction methodParam(int ord) {
	return new MethodParam(ord, null); // use body as value
    }

    /** Extract the method param from a tag attribute
     */
    public XmlAction methodParam(int ord, String attrib) {
	return new MethodParam(ord, attrib);
    }

    /** Pop the object stack
     */
    public XmlAction popStack() {
	return new PopStack();
    }

}

//-------------------- "Core" actions --------------------
// XXX XXX XXX Need to move the "standard" actions in individual files
/**
 * Create an object of the specified or override Java class name.
 */
class ObjectCreate extends XmlAction {
    String className;
    String attrib;

    /**
     * Create an object of the specified class name.
     *
     * @param classN Fully qualified name of the Java class to instantiate
     */
    public ObjectCreate(String classN) {
	className=classN;
    }

    /**
     * Create an object of the specified default class name, unless an
     * attribute with the specified name is present, in which case the value
     * of this attribute overrides the default class name.
     *
     * @param classN Fully qualified name of the Java class to instantiate
     *  if the specified attribute name is not present
     * @param attrib Name of the attribute that may contain a fully qualified
     *  name of a Java class that overrides the default
     */
    public ObjectCreate(String classN, String attrib) {
	className=classN;
	this.attrib=attrib;
    }

    public void start( SaxContext ctx) throws Exception {
	Stack st=ctx.getObjectStack();
	int top=ctx.getTagCount()-1;
	String tag=ctx.getTag(top);
	String classN=className;

	if( attrib!=null) {
	    AttributeList attributes = ctx.getAttributeList( top );
	    if (attributes.getValue(attrib) != null)
		classN= attributes.getValue(attrib);
	}
	Class c=Class.forName( classN );
	Object o=c.newInstance();
	st.push(o);
	if( ctx.getDebug() > 0 ) ctx.log("new "  + attrib + " " + classN + " "  + tag  + " " + o);
    }

    public void cleanup( SaxContext ctx) {
	Stack st=ctx.getObjectStack();
	String tag=ctx.getTag(ctx.getTagCount()-1);
	Object o=st.pop();
	if( ctx.getDebug() > 0 ) ctx.log("pop " + tag + " " + o.getClass().getName() + ": " + o);
    }
}


/** Set object properties using XML attribute list
 */
class SetProperties extends XmlAction {
    //    static Class paramT[]=new Class[] { "String".getClass() };

    public SetProperties() {
    }

    public void start( SaxContext ctx ) {
	Stack st=ctx.getObjectStack();
	Object elem=st.peek();
	int top=ctx.getTagCount()-1;
	AttributeList attributes = ctx.getAttributeList( top );

	for (int i = 0; i < attributes.getLength (); i++) {
	    String type = attributes.getType (i);
	    String name=attributes.getName(i);
	    String value=attributes.getValue(i);

	    setProperty( ctx, elem, name, value );
	}

    }

    /** Find a method with the right name
	If found, call the method ( if param is int or boolean we'll convert value to
	the right type before) - that means you can have setDebug(1).
    */
    static void setProperty( SaxContext ctx, Object o, String name, String value ) {
	if( ctx.getDebug() > 1 ) ctx.log("setProperty(" + o.getClass() + " " +  name + "="  + value  +")" );

	String setter= "set" +capitalize(name);

	try {
	    Method methods[]=o.getClass().getMethods();
	    Method setPropertyMethod=null;

	    // First, the ideal case - a setFoo( String ) method
	    for( int i=0; i< methods.length; i++ ) {
		Class paramT[]=methods[i].getParameterTypes();
		if( setter.equals( methods[i].getName() ) &&
		    paramT.length == 1 &&
		    "java.lang.String".equals( paramT[0].getName())) {

		    methods[i].invoke( o, new Object[] { value } );
		    return;
		}
	    }

	    // Try a setFoo ( int ) or ( boolean )
	    for( int i=0; i< methods.length; i++ ) {
		boolean ok=true;
		if( setter.equals( methods[i].getName() ) &&
		    methods[i].getParameterTypes().length == 1) {

		    // match - find the type and invoke it
		    Class paramType=methods[i].getParameterTypes()[0];
		    Object params[]=new Object[1];
		    if ("java.lang.Integer".equals( paramType.getName()) ||
			"int".equals( paramType.getName())) {
			try {
			    params[0]=new Integer(value);
			} catch( NumberFormatException ex ) {ok=false;}
		    } else if ("java.lang.Boolean".equals( paramType.getName()) ||
			"boolean".equals( paramType.getName())) {
			params[0]=new Boolean(value);
		    } else {
			ctx.log("Unknown type " + paramType.getName() );
		    }

		    if( ok ) {
			//	System.out.println("XXX: " + methods[i] + " " + o + " " + params[0] );
			methods[i].invoke( o, params );
			return;
		    }
		}

		// save "setProperty" for later
		if( "setProperty".equals( methods[i].getName())) {
		    setPropertyMethod=methods[i];
		}
	    }

	    // Ok, no setXXX found, try a setProperty("name", "value")
	    if( setPropertyMethod != null ) {
		Object params[]=new Object[2];
		params[0]=name;
		params[1]=value;
		setPropertyMethod.invoke( o, params );
	    }

	} catch( SecurityException ex1 ) {
	    if( ctx.getDebug() > 0 ) ctx.log("SecurityException for " + o.getClass() + " " +  name + "="  + value  +")" );
	    if( ctx.getDebug() > 1 ) ex1.printStackTrace();
	} catch (IllegalAccessException iae) {
	    if( ctx.getDebug() > 0 ) ctx.log("IllegalAccessException for " + o.getClass() + " " +  name + "="  + value  +")" );
	    if( ctx.getDebug() > 1 ) iae.printStackTrace();
	} catch (InvocationTargetException ie) {
	    if( ctx.getDebug() > 0 ) ctx.log("InvocationTargetException for " + o.getClass() + " " +  name + "="  + value  +")" );
	    if( ctx.getDebug() > 1 ) ie.printStackTrace();
	}
    }

    /** Reverse of Introspector.decapitalize
     */
    static String capitalize(String name) {
	if (name == null || name.length() == 0) {
	    return name;
	}
	char chars[] = name.toCharArray();
	chars[0] = Character.toUpperCase(chars[0]);
	return new String(chars);
    }

}


/** Set parent
 */
class SetParent extends XmlAction {
    String childM;
    String paramT = null;
    public SetParent(String p) {
	childM=p;
    }
    public SetParent(String p, String c) {
	childM=p;
	paramT=c;
    }

    public void end( SaxContext ctx) throws Exception {
	Stack st=ctx.getObjectStack();

	Object obj=st.pop();
	Object parent=st.peek();
	st.push( obj ); // put it back

	String parentC=parent.getClass().getName();
	if( ctx.getDebug() > 0 ) ctx.log("Calling " + obj.getClass().getName() + "." + childM +
					 " " + parentC);

	Class params[]=new Class[1];
	if( paramT==null) {
	    params[0]=parent.getClass();
	} else {
	    params[0]=Class.forName( paramT );
	}
	Method m=obj.getClass().getMethod( childM, params );
	m.invoke(obj, new Object[] { parent } );
    }
}

/** Set parent
 */
class AddChild extends XmlAction {
    String parentM;
    String paramT;

    public AddChild(String p, String c) {
	parentM=p;
	paramT=c;
    }

    public void end( SaxContext ctx) throws Exception {
	Stack st=ctx.getObjectStack();

	Object obj=st.pop();
	Object parent=st.peek();
	st.push( obj ); // put it back

	String parentC=parent.getClass().getName();
	if( ctx.getDebug() >0) ctx.log("Calling " + parentC + "." + parentM  +" " + obj  );

	Class params[]=new Class[1];
	if( paramT==null) {
	    params[0]=obj.getClass();
	} else {
	    params[0]=Class.forName( paramT );
	}
	Method m=parent.getClass().getMethod( parentM, params );
	m.invoke(parent, new Object[] { obj } );
    }
}

/**
 */
class  MethodSetter extends 	    XmlAction {
    String mName;
    int paramC;
    String paramTypes[];

    public MethodSetter( String mName, int paramC) {
	this.mName=mName;
	this.paramC=paramC;
    }

    public MethodSetter( String mName, int paramC, String paramTypes[]) {
	this.mName=mName;
	this.paramC=paramC;
	this.paramTypes=paramTypes;
    }

    public void start( SaxContext ctx) {
	Stack st=ctx.getObjectStack();
	if(paramC==0) return;
	String params[]=new String[paramC];
	st.push( params );
    }

    static final Class STRING_CLASS="String".getClass(); // XXX is String.CLASS valid in 1.1 ?

    public void end( SaxContext ctx) throws Exception {
	Stack st=ctx.getObjectStack();
	String params[]=null;
	if( paramC >0 ) params=(String []) st.pop();
	Object parent=st.peek();

	if( paramC == 0 ) {
	    params=new String[1];
	    params[0]= ctx.getBody().trim();
	    if( ctx.getDebug() > 0 ) ctx.log("" + parent.getClass().getName() + "." + mName + "( " + params[0] + ")");
	}

	Class paramT[]=new Class[params.length];
	Object realParam[]=new Object[params.length];
	for (int i=0; i< params.length; i++ ) {
	    if( paramTypes==null) {
		realParam[i]=params[i];
		paramT[i]=STRING_CLASS;
	    } else {
		// XXX Add more types
		if( "int".equals( paramTypes[i] ) ) {
		    realParam[i]=new Integer( params[i] );
		    paramT[i]=int.class;
		} else {
		    realParam[i]=params[i];
		    paramT[i]=STRING_CLASS;
		}
	    }
	}

	Method m=null;
	try {
	    m=parent.getClass().getMethod( mName, paramT );
	} catch( NoSuchMethodException ex ) {
	    ctx.log("Can't find method " + mName + " in " + parent + " CLASS " + parent.getClass());
	    return;
	}
	m.invoke( parent, realParam );

	if(ctx.getDebug() > 0 ) {
	    // debug
	    StringBuffer sb=new StringBuffer();
	    sb.append("" + parent.getClass().getName() + "." + mName + "( " );
	    for(int i=0; i<paramC; i++ ) {
		if(i>0) sb.append( ", ");
		sb.append(params[i]);
	    }
	    sb.append(")");
	    if( ctx.getDebug() > 0 ) ctx.log(sb.toString());
	}
    }
}

/**
 */
class  MethodParam extends XmlAction {
    int paramId;
    String attrib;

    public MethodParam( int paramId, String attrib) {
	this.paramId=paramId;
	this.attrib=attrib;
    }

    // If param is an attrib, set it
    public void start( SaxContext ctx) {
	if( attrib==null) return;

	Stack st=ctx.getObjectStack();
	String h[]=(String[])st.peek();

	int top=ctx.getTagCount()-1;
	AttributeList attributes = ctx.getAttributeList( top );
	h[paramId]= attributes.getValue(attrib);
    }

    // If param is the body, set it
    public void end( SaxContext ctx) {
	if( attrib!=null) return;
	Stack st=ctx.getObjectStack();
	String h[]=(String[])st.peek();
	h[paramId]= ctx.getBody().trim();
    }
}

/**
 */
class PopStack extends XmlAction {
    public PopStack() {
	super();
    }

    public void end( SaxContext ctx) {
	Stack st=ctx.getObjectStack();
	Object top = st.pop();
	if( ctx.getDebug() > 0 ) ctx.log("Pop " + top.getClass().getName());
    }
}