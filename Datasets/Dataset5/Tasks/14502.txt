@Test public void testTypeForAdditionalBuiltin () {

/*
Copyright (c) 2008 Arno Haase.
All rights reserved. This program and the accompanying materials
are made available under the terms of the Eclipse Public License v1.0
which accompanies this distribution, and is available at
http://www.eclipse.org/legal/epl-v10.html

Contributors:
    Arno Haase - initial API and implementation
 */
package org.eclipse.xtend.backend.functions;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.util.Arrays;
import java.util.List;

import org.eclipse.xtend.backend.common.EfficientLazyString;
import org.eclipse.xtend.backend.functions.java.internal.IntConverter;
import org.eclipse.xtend.backend.functions.java.internal.JavaBuiltinConverterFactory;
import org.eclipse.xtend.backend.functions.java.internal.ParameterConverter;
import org.eclipse.xtend.backend.types.builtin.DoubleType;
import org.eclipse.xtend.backend.types.builtin.ListType;
import org.eclipse.xtend.backend.types.builtin.LongType;
import org.eclipse.xtend.backend.types.builtin.StringType;
import org.junit.Test;


/**
 * 
 * @author Arno Haase (http://www.haase-consulting.com)
 */
public class JavaBuiltinConverterTest {
    @Test public void testParameterConverter () {
        checkEquals (null, JavaBuiltinConverterFactory.getParameterConverter (Long.class, 0));
        checkEquals (null, JavaBuiltinConverterFactory.getParameterConverter (Long.TYPE, 0));
        checkEquals (null, JavaBuiltinConverterFactory.getParameterConverter (Double.class, 0));
        checkEquals (null, JavaBuiltinConverterFactory.getParameterConverter (Double.TYPE, 0));
        checkEquals (null, JavaBuiltinConverterFactory.getParameterConverter (List.class, 0));
        checkEquals (null, JavaBuiltinConverterFactory.getParameterConverter (CharSequence.class, 0));
        
        final ParameterConverter pc = new ParameterConverter (2, IntConverter.INSTANCE);
        
        final Object[] p = new Object[] {1L, 2L, 3L, 4L, 5L};
        pc.convert(p);
        checkEquals (1L, p[0]);
        checkEquals (2L, p[1]);
        checkEquals (3, p[2]);
        checkEquals (4L, p[3]);
        checkEquals (5L, p[4]);
    }
    
    @Test public void testTypeäForAdditionalBuiltin () {
        checkEquals (LongType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Integer.class));
        checkEquals (LongType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Integer.TYPE));
        checkEquals (LongType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Short.class));
        checkEquals (LongType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Short.TYPE));
        checkEquals (LongType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Byte.class));
        checkEquals (LongType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Byte.TYPE));

        checkEquals (DoubleType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Float.class));
        checkEquals (DoubleType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Float.TYPE));
        
        checkEquals (StringType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Character.class));
        checkEquals (StringType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (Character.TYPE));

        checkEquals (ListType.INSTANCE, JavaBuiltinConverterFactory.getTypeForAdditionalBuiltin (new Object[]{}.getClass()));
    }
    
    @Test public void testLong () {
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Long.TYPE).backendToJava (4L));
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Long.class).backendToJava (4L));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Long.class).backendToJava (null));
        
        checkEquals (new Integer (4), JavaBuiltinConverterFactory.getConverter (Integer.TYPE).backendToJava (4L));
        checkEquals (new Integer (4), JavaBuiltinConverterFactory.getConverter (Integer.class).backendToJava (4L));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Integer.class).backendToJava (null));
        
        checkEquals (new Short ((short) 4), JavaBuiltinConverterFactory.getConverter (Short.TYPE).backendToJava (4L));
        checkEquals (new Short ((short) 4), JavaBuiltinConverterFactory.getConverter (Short.class).backendToJava (4L));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Short.class).backendToJava (null));
        
        checkEquals (new Byte ((byte) 4), JavaBuiltinConverterFactory.getConverter (Byte.TYPE).backendToJava (4L));
        checkEquals (new Byte ((byte) 4), JavaBuiltinConverterFactory.getConverter (Byte.class).backendToJava (4L));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Byte.class).backendToJava (null));
        
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Long.TYPE).javaToBackend (4L));
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Long.class).javaToBackend (4L));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Long.class).javaToBackend (null));
        
        checkEquals (new Long(4), JavaBuiltinConverterFactory.getConverter (Integer.TYPE).javaToBackend (new Integer (4)));
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Integer.class).javaToBackend (new Integer (4)));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Integer.class).javaToBackend (null));
        
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Short.TYPE).javaToBackend ((short) 4));
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Short.class).javaToBackend ((short) 4));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Short.class).javaToBackend (null));
        
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Byte.TYPE).javaToBackend ((byte) 4));
        checkEquals (new Long (4), JavaBuiltinConverterFactory.getConverter (Byte.class).javaToBackend ((byte) 4));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Byte.class).javaToBackend (null));
    }
    
    @Test public void testDouble () {
        checkEquals (new Float (4), JavaBuiltinConverterFactory.getConverter (Float.TYPE).backendToJava (4.0));
        checkEquals (new Float (4), JavaBuiltinConverterFactory.getConverter (Float.class).backendToJava (4.0));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Float.class).backendToJava (null));
        
        checkEquals (new Double (4), JavaBuiltinConverterFactory.getConverter (Float.TYPE).javaToBackend (4.0f));
        checkEquals (new Double (4), JavaBuiltinConverterFactory.getConverter (Float.class).javaToBackend (4.0f));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Float.class).javaToBackend (null));
    }
    
    @Test public void testString () {
        checkEquals (new Character ('a'), JavaBuiltinConverterFactory.getConverter (Character.TYPE).backendToJava ("a"));
        checkEquals (new Character ('a'), JavaBuiltinConverterFactory.getConverter (Character.class).backendToJava ("a"));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Character.class).backendToJava (null));
        
        checkEquals ("a", JavaBuiltinConverterFactory.getConverter (String.class).backendToJava (new StringBuilder ("a")));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (String.class).backendToJava (null));
        
        checkEquals (new StringBuilder ("a"), JavaBuiltinConverterFactory.getConverter (StringBuilder.class).backendToJava ("a"));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (StringBuilder.class).backendToJava (null));
        
        checkEquals (new StringBuffer ("a"), JavaBuiltinConverterFactory.getConverter (StringBuffer.class).backendToJava ("a"));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (StringBuffer.class).backendToJava (null));

        final EfficientLazyString els = (EfficientLazyString) JavaBuiltinConverterFactory.getConverter (EfficientLazyString.class).backendToJava ("a");
        assertEquals ("a", els.toString());
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (EfficientLazyString.class).backendToJava (null));
        
        checkEquals ("a", JavaBuiltinConverterFactory.getConverter (Character.TYPE).javaToBackend ('a'));
        checkEquals ("a", JavaBuiltinConverterFactory.getConverter (Character.class).javaToBackend ('a'));
        checkEquals (null, JavaBuiltinConverterFactory.getConverter (Character.class).javaToBackend (null));
    }
    
    @Test public void testList () {
        checkArraysEqual (new Long[] {1L, 2L, 3L}, (Object[]) JavaBuiltinConverterFactory.getConverter (new Long[0].getClass()).backendToJava(Arrays.asList(1L, 2L, 3L)));
        checkArraysEqual (new String[] {"a", "b", "c"}, (Object[]) JavaBuiltinConverterFactory.getConverter (new String[0].getClass()).backendToJava(Arrays.asList("a", "b", "c")));
    }
    
    
    /**
     * This is necessary because JUnit's assertEquals is lenient in comparing numbers - it always compares their longValue, and
     *  since we are testing type conversion here, that's not what we want ;-) 
     */
    private void checkEquals (Object o1, Object o2) {
        if (o1 == null)
            assertTrue (o2 == null);
        else {
            assertEquals (o1.getClass(), o2.getClass());
            
            // this is necessary because some CharSequence implementations do not have equals methods, e.g. StringBuilder ;-(
            if (o1 instanceof CharSequence)
                assertEquals (o1.toString(), o2.toString());
            else
                assertEquals (o1, o2);
        }
    }
    
    private void checkArraysEqual (Object[] a1, Object[] a2) {
        assertEquals (a1.length, a2.length);
        assertEquals (a1.getClass(), a2.getClass());
        assertEquals (a1.getClass().getComponentType(), a2.getClass().getComponentType());
        assertEquals (Arrays.asList(a1), Arrays.asList(a2));
    }
}