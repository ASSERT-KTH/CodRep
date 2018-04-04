Logger.log("wrote "+fname);

package org.jboss.proxy;

import java.lang.reflect.*;

// The following code manages bytecode assembly for dynamic proxy
// generation.

class ProxyCompiler {
    Class superclass;
    Runtime runtime;
    Class targetTypes[];
    Method methods[];

    Class proxyType;

    ProxyCompiler(ClassLoader parent, Class superclass, Class targetTypes[], Method methods[]) {
	this.superclass = superclass;
	this.targetTypes = targetTypes;
	this.methods = methods;

	this.runtime = new Runtime( parent );
	this.runtime.targetTypes = targetTypes;
	this.runtime.methods = methods;

	runtime.makeProxyType(this);
    }

    Class getProxyType() {
	return proxyType;
    }


    // this is the only data needed at runtime:
    public static class Runtime extends ClassLoader {
	// These members are common utilities used by ProxyTarget classes.
	// They are all public so they can be linked to from generated code.
	// I.e., they are the runtime support for the code compiled below.
  private ClassLoader parent;

  public Runtime( ClassLoader parent )
  {
  	super( parent );
    this.parent = parent;
  }

	Class targetTypes[];
	Method methods[];
	ProxyCompiler compiler;	// temporary!

	public static final Object NOARGS[] = {};

	public static String toString(Proxies.ProxyTarget target) {
	    // This method is not used if one of the target types declare toString.
	    InvocationHandler invocationHandler = target.getInvocationHandler();
	    return "ProxyTarget[" + invocationHandler + "]";
	}

	public Class[] copyTargetTypes() {
	    try {
		return (Class[]) targetTypes.clone();
	    } catch (IllegalArgumentException ee) {
		return new Class[0];
	    }
	}

	public Object invoke(InvocationHandler invocationHandler, int methodNum, Object values[])
					    throws Throwable {
    Method method = methods[methodNum];
    if (method.getName().equals( "writeReplace" ))
    {
    	return new ProxyProxy( invocationHandler, copyTargetTypes() );

    }
		return invocationHandler.invoke(null, methods[methodNum], values);
	}

	public boolean invokeBoolean(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Boolean)result).booleanValue();
	}
	public byte invokeByte(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Number)result).byteValue();
	}
	public char invokeChar(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Character)result).charValue();
	}
	public short invokeShort(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Number)result).shortValue();
	}
	public int invokeInt(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Number)result).intValue();
	}
	public long invokeLong(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Number)result).longValue();
	}
	public float invokeFloat(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Number)result).floatValue();
	}
	public double invokeDouble(InvocationHandler InvocationHandler, int methodNum, Object values[])
					    throws Throwable {
	    Object result = invoke(InvocationHandler, methodNum, values);
	    return ((Number)result).doubleValue();
	}

	public static Boolean wrap(boolean x) {
	    return new Boolean(x);
	}
	public static Byte wrap(byte x) {
	    return new Byte(x);
	}
	public static Character wrap(char x) {
	    return new Character(x);
	}
	public static Short wrap(short x) {
	    return new Short(x);
	}
	public static Integer wrap(int x) {
	    return new Integer(x);
	}
	public static Long wrap(long x) {
	    return new Long(x);
	}
	public static Float wrap(float x) {
	    return new Float(x);
	}
	public static Double wrap(double x) {
	    return new Double(x);
	}
	// the class loading part

	void makeProxyType(ProxyCompiler compiler) {
	    this.compiler = compiler; // temporary, for use during loading

	    byte code[] = compiler.getCode();
	    /* ---- ---- *
	    try {
		String fname = compiler.getProxyClassName();
		fname = fname.substring(1 + fname.lastIndexOf('.')) + ".class";
		fname = "/tmp/" + fname;
		java.io.OutputStream cf = new java.io.FileOutputStream(fname);
		cf.write(code);
		cf.close();
		System.out.println("wrote "+fname);
	    } catch(java.io.IOException ee) { }
	    //* ---- ---- */

	    compiler.proxyType = super.defineClass(compiler.getProxyClassName(), code, 0, code.length);
	    super.resolveClass(compiler.proxyType);
	    // set the Foo$Impl.info pointer to myself
	    try {
		Field infoField = compiler.proxyType.getField(INFO_FIELD);
		infoField.set(null, this);
	    } catch (IllegalAccessException ee) {
		throw new RuntimeException("unexpected: "+ee);
	    } catch (NoSuchFieldException ee) {
		throw new RuntimeException("unexpected: "+ee);
	    }
	    compiler = null;
	}

	ClassLoader getTargetClassLoader() {
  	return parent;
	  /*  for (int i = 0; i < targetTypes.length; i++) {
		ClassLoader cl = targetTypes[i].getClassLoader();
		if (cl != null) {
		    return cl;
		}
	    }
	    return null; */
	}

	public synchronized Class loadClass(String name, boolean resolve)
		throws ClassNotFoundException {
	    if (name.endsWith(IMPL_SUFFIX)
		    && name.equals(compiler.getProxyClassName())) {
		return compiler.proxyType;
	    }
	    // delegate to the original class loader
	    ClassLoader cl = getTargetClassLoader();
	    if (cl == null) {
		return super.findSystemClass(name);
	    }
	    return cl.loadClass(name);
	}

	public java.io.InputStream getResourceAsStream(String name) {
	    // delegate to the original class loader
	    ClassLoader cl = getTargetClassLoader();
	    if (cl == null) {
		return parent.getSystemResourceAsStream(name);
	    }
	    return cl.getResourceAsStream(name);
	}

	public java.net.URL getResource(String name) {
	    // delegate to the original class loader
	    ClassLoader cl = getTargetClassLoader();
	    if (cl == null) {
		return parent.getSystemResource(name);
	    }
	    return cl.getResource(name);
	}

    }

    // the code generation part

    private static String IMPL_SUFFIX = "$Proxy";
    String getProxyClassName() {
	// Note:  We could reasonably put the $Impl class in either
	// of two packges:  The package of Proxies, or the same package
	// as the target type.  We choose to put it in same package as
	// the target type, to avoid name encoding issues.
	//
	// Note that all infrastructure must be public, because the
	// $Impl class is inside a different class loader.
	String tName = targetTypes[0].getName();
	/*
	String dName = Dispatch.class.getName();
	String pkg = dName.substring(0, 1 + dName.lastIndexOf('.'));
	return pkg + tName.substring(1 + tName.lastIndexOf('.')) + IMPL_SUFFIX;
	*/
	return tName + IMPL_SUFFIX;
    }

    private static String INFO_FIELD = "$info";
    private static String InvocationHandler_FIELD = "$InvocationHandler";

    private static final Class invokeParams[] = {
	InvocationHandler.class, Integer.TYPE, Object[].class
    };
    private static final Class toStringParams[] = {
	Proxies.ProxyTarget.class
    };

    /** Create the implementation class for the given target. */
    private byte[] getCode() {
	String pClass = getProxyClassName();

	int icount = 1;		// don't forget ProxyTarget
	for (int i = 0; i < targetTypes.length; i++) {
	    Class targetType = targetTypes[i];
	    if (targetType.isInterface()) {
		icount++;
	    }
	}
	Class interfaces[] = new Class[icount];
	interfaces[0] = Proxies.ProxyTarget.class;
	icount = 1;
	for (int i = 0; i < targetTypes.length; i++) {
	    Class targetType = targetTypes[i];
	    if (targetType.isInterface()) {
		interfaces[icount++] = targetType;
	    } else if (!superclass.isAssignableFrom(targetType)) {
		throw new RuntimeException("unexpected: "+targetType);
	    }
	}
	ProxyAssembler asm =
	    new ProxyAssembler(pClass,
			       Modifier.PUBLIC | Modifier.FINAL,
			       superclass, interfaces);

	Class rClass = ProxyCompiler.Runtime.class;
	asm.addMember(Modifier.PUBLIC + Modifier.STATIC, rClass, null, INFO_FIELD);

	// ProxyTarget implementation
	Class iClass = InvocationHandler.class;
	asm.addMember(Modifier.PRIVATE, iClass, null, InvocationHandler_FIELD);
	asm.addMember(Modifier.PUBLIC, iClass, "getInvocationHandler",
		      new Class[] {}, null);
	{
	    asm.pushLocal(0);
	    asm.pushField(asm, InvocationHandler_FIELD);
	    asm.ret();
	}
	asm.addMember(Modifier.PUBLIC, Class[].class, "getTargetTypes",
		      new Class[] {}, null);
	{
	    asm.pushLocal(0);
	    asm.pushField(asm, INFO_FIELD);
	    asm.invoke(rClass, "copyTargetTypes", new Class[] {});
	    asm.ret();
	}

	boolean haveToString = false;

	// Implement the methods of the target types.
	for (int i = 0; i < methods.length; i++) {
	    Method m = methods[i];
	    String name = m.getName();
	    Class rtype = m.getReturnType();
	    Class ptypes[] = m.getParameterTypes();
      Class[] exceptions = m.getExceptionTypes();
	    if (name.equals("toString") && ptypes.length == 0) {
		haveToString = true;
	    }
	    asm.addMember(Modifier.PUBLIC + Modifier.FINAL,
			  rtype, name, ptypes, exceptions);
	    {
		// $info.invokeBoolean(InvocationHandler, i, new Object[]{ ... })
		asm.pushField(asm, INFO_FIELD);
		asm.pushLocal(0);
		asm.pushField(asm, InvocationHandler_FIELD);
		asm.pushConstant(i);
		// push the arguments
		if (ptypes.length == 0) {
		    asm.pushField(rClass, "NOARGS");
		} else {
		    asm.pushConstant(ptypes.length);
		    asm.pushNewArray(Object.class);
		    for (int j = 0; j < ptypes.length; j++) {
			Class t = ptypes[j];
			asm.dup();
			asm.pushConstant(j);
			asm.pushLocal(1 + j);
			if (t.isPrimitive()) {
			    asm.invoke(rClass, "wrap", new Class[]{ t });
			}
			asm.setElement(Object.class);
		    }
		}
		// call the InvocationHandler
		String invoke = "invoke";
		if (rtype.isPrimitive() && rtype != Void.TYPE) {
		    String tn = rtype.getName();
		    invoke += Character.toUpperCase(tn.charAt(0))
			    + tn.substring(1);
		}
		asm.invoke(rClass, invoke, invokeParams);
		if (!rtype.isPrimitive() && rtype != Object.class) {
		    asm.checkCast(rtype);
		}
		asm.ret();
	    }
	}

	if (!haveToString) {
	    asm.addMember(Modifier.PUBLIC, String.class, "toString",
			  new Class[] {}, null);
	    {
		asm.pushLocal(0);
		asm.invoke(rClass, "toString", toStringParams);
		asm.ret();
	    }
	}

	// Put in the constructor:
	asm.addMember(Modifier.PUBLIC, Void.TYPE, "<init>",
		      new Class[] { iClass }, null);
	{
	    asm.pushLocal(0);
	    asm.invoke(superclass, "<init>", new Class[0]);
	    asm.pushLocal(0);
	    asm.pushLocal(1);
	    asm.setField(asm, InvocationHandler_FIELD);
	    asm.ret();
	}

	return asm.getCode();
    }
}