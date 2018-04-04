IntrospectionUtils.setProperty( elem, name, value1 );

package org.apache.tomcat.util.xml;

import org.apache.tomcat.util.IntrospectionUtils;
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

import org.apache.tomcat.util.compat.*;

/**
 * SAX Handler - it will read the XML and construct java objects
 *
 * @author costin@dnt.ro
 */
public class XmlMapper  extends HandlerBase implements SaxContext
{
    Locator locator;

    /**
     * The URLs of DTDs that have been registered, keyed by the public
     * identifier that corresponds.
     */
    private Hashtable fileDTDs = new Hashtable();
    private Hashtable resDTDs = new Hashtable();
    private Hashtable variables = new Hashtable();
    
    // Stack of elements
    Stack oStack=new Stack();
    Object root;
    Object attributeStack[];
    String tagStack[];
    int oSp;
    int sp;
    ErrorHandler errorHandler;
    
    String body;

    int debug=0;
    boolean validating=false;
    private Hashtable entities = new Hashtable();
    
    public XmlMapper() {
	attributeStack = new Object[200]; // depth of the xml doc
	tagStack = new String[200];
	initDefaultRules();
    }

    public void setDocumentLocator (Locator locator)
    {
	if( debug>0 ) log("Set locator : " + locator);
	this.locator = locator;
    }

    public Locator getLocator() {
	return locator;
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
	    if( debug>5) log(sp + " <" + tag + " " + attributes + ">");
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

    public String positionToString() {
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

    public AttributeList getCurrentAttributes() {
	return (AttributeList)attributeStack[sp-1];
    }

    public int getTagCount() {
	return sp;
    }

    public String getTag( int pos ) {
	return tagStack[pos];
    }

    public String getCurrentElement() {
	return tagStack[sp-1];
    }

    public String getBody() {
	return body;
    }

    public Stack getObjectStack() {
	return oStack;
    }

    public Object popObject() {
	return oStack.pop();
    }

    public Object currentObject() {
	return oStack.peek();
    }

    public Object previousObject() {
	Object o=oStack.pop();
	Object result=oStack.peek();
	oStack.push( o );
	return result;
    }

    public void pushObject(Object o) {
	oStack.push( o );
    }

    public Object getRoot() {
	return root;
    }

    public void setRoot(Object o) {
	root=o;
    }

    // -------------------- Support for ${prop} replacement ----------

    Object propSource;

    public void setPropertySource( Object src ) {
	this.propSource=src;
    }

    public Object getPropertySource() {
	return propSource;
    }

    public String replaceProperties( String k ) {
	if( propSource==null ) return k;
	return IntrospectionUtils.replaceProperties( k, propSource);
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

    public void setVariable( String name, Object value ) {
	if( value==null)
	    variables.remove(name);
	else
	    variables.put( name, value );
    }

    public Object getVariable( String name ) {
	return variables.get( name );
    }

    public XmlMapper getMapper() {
	return this;
    }

    public void setErrorHandler( ErrorHandler eh ) {
	errorHandler=eh;
    }
    
    boolean useLocalLoader=true;
    
    public void useLocalLoader(boolean b ) {
	useLocalLoader=b;
    }
    static final Jdk11Compat jdk11Compat=Jdk11Compat.getJdkCompat();

    /** read an XML file, construct and return the object hierarchy
     */
    public Object readXml(File xmlFile, Object root)
	throws Exception
    {
	if(root!=null) {
	    this.root=root;
	    this.pushObject( root );
	}
	try {
	    // reset the context loader, so we find the parser in the current dir
	    ClassLoader cl=null;
	    if( useLocalLoader ) {
		cl=jdk11Compat.getContextClassLoader();
		jdk11Compat.setContextClassLoader( this.getClass().getClassLoader());
	    }
	    
	    SAXParser parser=null;
	    SAXParserFactory factory = SAXParserFactory.newInstance();
	    factory.setNamespaceAware(false);
	    factory.setValidating(validating);
	    parser = factory.newSAXParser();
	    Parser saxParser=parser.getParser();
	    saxParser.setDocumentHandler( this );
	    saxParser.setEntityResolver( this );
	    if( errorHandler!=null ) {
		saxParser.setErrorHandler( errorHandler );
	    }

	    String uri = "file:" + xmlFile.getAbsolutePath();
	    if (File.separatorChar == '\\') {
		uri = uri.replace('\\', '/');
	    }
	    InputSource input = new InputSource(uri);

	    saxParser.parse(input);

	    if( useLocalLoader && cl!= null ) {
		jdk11Compat.setContextClassLoader(cl);
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
	    this.root=root;
	    this.pushObject( root );
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

    public Hashtable getEntities() {
	return entities;
    }

    class Rule {
	XmlMatch match;
	XmlAction action;
	Rule( XmlMatch match, XmlAction action ) {
	    this.match=match;
	    this.action=action;
	}
    }
    Rule rules[]=new Rule[200];
    Rule matching[]=new Rule[200];
    int ruleCount=0;

    /**
     */
    private void initDefaultRules() {
	// One-time actions, in line
	addRule( "xmlmapper:debug",
		 new XmlAction() {
			 public void start(SaxContext ctx) {
			     AttributeList attributes =
				 ctx.getCurrentAttributes();
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
			     AttributeList attributes =
				 ctx.getCurrentAttributes();
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
				     ClassLoader cl=getClassLoader();
				     Class c=cl.loadClass( obj );
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
	if( ruleCount >= rules.length ) {
	    Rule tmp[]=new Rule[ 2* rules.length ];
	    System.arraycopy( rules, 0, tmp, 0, rules.length);
	    rules=tmp;
	}
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
        if(publicId == null) {
           log("publicID is 'null'");
           return null;
        }
        
        if(systemId == null) {
           log("systemId is 'null'");
           systemId="";
        }

	entities.put( publicId, systemId );
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
	    InputStream is = getClassLoader().getResourceAsStream( dtd );
	    if( is!= null )
		return new InputSource(is);
	    dumpCP( getClassLoader() );
	}
	
	log("Can't find resource for entity: " + publicId + " --> " +
	    systemId + " \"" + dtd +"\"");
	return null;
    }

    public static void dumpCP(  ClassLoader cl ) {
	org.apache.tomcat.util.compat.Jdk11Compat jdk=
	    org.apache.tomcat.util.compat.Jdk11Compat.getJdkCompat();
	URL urls[]=jdk.getURLs( cl, 0 );
	System.out.println("CLASSPATH " );
	for( int i=0; i< urls.length; i++ ) {
	    System.out.println("    " + urls[i] );
	}
	urls=jdk.getURLs( cl, 1 );
	System.out.println();
	for( int i=0; i< urls.length; i++ ) {
	    System.out.println("    " + urls[i] );
	}
	urls=jdk.getURLs( cl, 2 );
	System.out.println();
	for( int i=0; i< urls.length; i++ ) {
	    System.out.println("    " + urls[i] );
	}
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

    /** Create an object using an attribute value as the class name
	If no attribute use classN as a default. If the class name
	has no ".", use the third parameter as prefix
     */
    public XmlAction objectCreate( String classN, String attrib,String pref[])
    {
	return new ObjectCreate( classN, attrib, pref);
    }

    /** Set object properties using XML attributes
     */
    public XmlAction setProperties() {
	return new SetProperties();
    }

    /** Set a variable varName using the value of an attribute
     */
    public XmlAction setVar( String varName, String attName ) {
	return new SetVar( varName, attName );
    }

    /** Set a variable varName using the value of an attribute
     */
    public XmlAction setVar( String varName, String nameAtt,
				  String valueAtt, boolean reset) {
	return new SetVar(varName, nameAtt, valueAtt, reset);
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

    ClassLoader loader;
    public ClassLoader getClassLoader() {
	if( loader==null )
	    loader=this.getClass().getClassLoader();
	return loader;
    }

    public void setClassLoader( ClassLoader loader ) {
	this.loader=loader;
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
    String pref[]=null;

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

    public ObjectCreate(String classN, String attrib, String pref[]) {
	className=classN;
	this.attrib=attrib;
	this.pref=pref;
    }

    
    public void start( SaxContext ctx) throws Exception {
	String tag=ctx.getCurrentElement();
	String classN=className;
	ClassLoader cl=ctx.getClassLoader();

	if( attrib!=null) {
	    AttributeList attributes = ctx.getCurrentAttributes();
	    if (attributes.getValue(attrib) != null)
		classN= attributes.getValue(attrib);
	}
	Class c=null;
	if( pref!=null && classN.indexOf( "." ) <0 ) {
	    for( int i=0; i<pref.length; i++ ) {
		try {
		    c=cl.loadClass( pref[i] + classN );
		    if( c!=null ) break;
		} catch( Exception ex ) {
		    if( ctx.getDebug() > 0 )
			ctx.log( "Try " + pref[i] + classN );
		    // ignore
		}
	    }
	}
	if( c==null ) {
	    c=cl.loadClass( classN );
	}
	Object o=c.newInstance();
	ctx.pushObject(o);
	if( ctx.getDebug() > 0 )
	    ctx.log("new "  + attrib + " " + classN + " "  + tag  + " " + o);
    }

    public void cleanup( SaxContext ctx) {
	String tag=ctx.getCurrentElement();
	Object o=ctx.popObject();
	if( ctx.getDebug() > 0 ) ctx.log("pop " + tag + " " +
					 o.getClass().getName() + ": " + o);
    }
}


/** Set object properties using XML attribute list
 */
class SetProperties extends XmlAction {
    public SetProperties() {
    }

    public void start( SaxContext ctx ) {
	Object elem=ctx.currentObject();
	AttributeList attributes = ctx.getCurrentAttributes();
	XmlMapper xh=ctx.getMapper();
	
	for (int i = 0; i < attributes.getLength (); i++) {
	    String type = attributes.getType (i);
	    String name=attributes.getName(i);
	    String value=attributes.getValue(i);

	    String value1=xh.replaceProperties( value );
	    if( !value1.equals(value) && ctx.getDebug() > -1 )
		ctx.log( "Replace " + value + " " + value1 );
		
	    IntrospectionUtils.setProperty( elem, name, value );
	}
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
	Object obj=ctx.currentObject();
	Object parent=ctx.previousObject();

	IntrospectionUtils.callMethod1( obj, childM, parent, paramT,
					this.getClass().getClassLoader());
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
	Object obj=ctx.currentObject();
	Object parent=ctx.previousObject();

	IntrospectionUtils.callMethod1( parent, parentM, obj, paramT,
					this.getClass().getClassLoader());
    }
}

/**
 */
class  MethodSetter extends XmlAction {
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
	String params[]=new String[paramC];
	ctx.pushObject( params );
    }

    static final Class STRING_CLASS="String".getClass(); 

    public void end( SaxContext ctx) throws Exception {
	String params[]=(String [])ctx.popObject();
	Object parent=ctx.currentObject();

	// XXX ???
	if( paramC == 0 ) {
	    params=new String[1];
	    params[0]= ctx.getBody().trim();
	    if( ctx.getDebug() > 0 )
		ctx.log("" + parent.getClass().getName() + "." +
			mName + "( " + params[0] + ")");
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
	m=IntrospectionUtils.findMethod( parent.getClass(), mName, paramT );
	if( m== null ) {
	    ctx.log("Can't find method " + mName + " in " +
		    parent + " CLASS " + parent.getClass());
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
	String h[]=(String[])ctx.currentObject();
	AttributeList attributes = ctx.getCurrentAttributes();
	h[paramId]= attributes.getValue(attrib);
    }

    // If param is the body, set it
    public void end( SaxContext ctx) {
	if( attrib!=null) return;
	String h[]=(String[])ctx.currentObject();
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
	Object top = ctx.popObject();
	if( ctx.getDebug() > 0 )
	    ctx.log("Pop " +
		    ((top==null) ? "null" : 
		    top.getClass().getName()));
    }
}

/**
 */
class SetVar extends XmlAction {
    String varName;
    String nameAtt;
    String valAtt;
    boolean reset=false;
    
    public SetVar(String varName, String attributeN) {
	super();
	this.varName=varName;
	this.valAtt=attributeN;
	reset=true;
    }
    
    public SetVar(String varName, String nameAtt, String valueAtt,
		       boolean reset) {
	super();
	this.varName=varName;
	this.nameAtt=nameAtt;
	this.valAtt=valueAtt;
	this.reset=reset;
    }
    
    public void start( SaxContext ctx) throws Exception {
	AttributeList attributes = ctx.getCurrentAttributes();
	String n=varName;
	if( n==null )
	    n=attributes.getValue( nameAtt );
	String v=attributes.getValue( valAtt );
	
	if( n!=null && v!=null )
	    ctx.setVariable( n, v);

	if( ctx.getDebug() > 0 )
	    ctx.log("setVariable " + n + " " + v );
    }

    public void cleanup( SaxContext ctx) {
	if( ! reset ) return;
	if(varName!=null)
	    ctx.setVariable( varName, null);
	// for name="foo" val="bar" - we don't reset it 
	if( ctx.getDebug() > 0 )
	    ctx.log("setVariable " + varName + " null");
    }
}