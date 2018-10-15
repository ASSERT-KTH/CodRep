//	suite.addTestSuite(WpValidationTest.class);

/*******************************************************************************
 * Copyright (c) 2009 by SAP AG, Walldorf. 
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     SAP AG - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.jaxws.dom.runtime.tests;

import junit.framework.Test;
import junit.framework.TestSuite;

import org.eclipse.jst.ws.jaxws.dom.runtime.tests.annotations.AnnotationFactoryTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.annotations.AnnotationsTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.annotations.ArrayValueImplTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.annotations.ComplexAnnotationImplTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.annotations.ParamValuePairImplTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.annotations.QualifiedNameValueImplTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.WsDOMRuntimeManagerTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.WsDOMRuntimeRegistryTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.JaxWsDefaultsCalculatorTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.JaxWsWorkspaceResourceTests;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.Jee5WsDomRuntimeExtensionTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.ProjectAddingTests;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.WorkspaceCUFinderTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.annotation.AnnotationAdapterFactoryTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.annotation.impl.AnnotationAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.defaults.MethodPropertyDefaultsAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.defaults.ParameterPropertyDefaultsAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.defaults.SeiPropertyDefaultsAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.defaults.WsPropertyDefaultsAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.serializer.AbstractSerializerAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.serializer.MethodSerializerAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.serializer.ParameterSerializerAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.serializer.SeiSerializerAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.serializer.SerializerAdapterFactoryTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.serializer.WsSerializerAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.state.MethodPropertyStateAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.state.ParameterPropertyStateAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.state.PropertyStateAdapterFactoryTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.state.SeiPropertyStateAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.state.WsPropertyStateAdapterTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.AbstractModelSynchronizerTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.ImplicitSeiMethodSynchronizationTests;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.MethodParamsSynchronizationTests;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.ModelSynchronizationTests;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.OnEventModelSyncronizerTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.SeiMethodSyncronizationTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.SeiSyncronizationTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.persistence.sync.WsSynchronizationTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.util.Dom2ResourceMapperTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.util.DomUtilTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.validation.EndpointIsSessionBeanRuleTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.validation.SeiValidationTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.validation.WmValidationTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.validation.WpValidationTest;
import org.eclipse.jst.ws.jaxws.dom.runtime.tests.dom.validation.WsValidationTest;

public class AllTestsSuite
{
	public static Test suite()
	{
		TestSuite suite = new TestSuite();

		suite.addTestSuite(AnnotationFactoryTest.class);
		suite.addTestSuite(AnnotationsTest.class);
		suite.addTestSuite(ParamValuePairImplTest.class);
		suite.addTestSuite(ComplexAnnotationImplTest.class);
		suite.addTestSuite(QualifiedNameValueImplTest.class);
		suite.addTestSuite(ArrayValueImplTest.class);
		suite.addTestSuite(WsDOMRuntimeRegistryTest.class);
		suite.addTestSuite(WsDOMRuntimeManagerTest.class);
		suite.addTestSuite(Dom2ResourceMapperTest.class);
		suite.addTestSuite(DomUtilTest.class);
		
		// DOM tests
		suite.addTestSuite(Jee5WsDomRuntimeExtensionTest.class);
		suite.addTestSuite(JaxWsWorkspaceResourceTests.class);
		suite.addTestSuite(ProjectAddingTests.class);
		suite.addTestSuite(WorkspaceCUFinderTest.class);
		// DOM sync tests
		suite.addTestSuite(AbstractModelSynchronizerTest.class);
		suite.addTestSuite(OnEventModelSyncronizerTest.class);
		suite.addTestSuite(ImplicitSeiMethodSynchronizationTests.class);
		suite.addTestSuite(MethodParamsSynchronizationTests.class);		
		suite.addTestSuite(ModelSynchronizationTests.class);
		suite.addTestSuite(SeiMethodSyncronizationTest.class);
		suite.addTestSuite(SeiSyncronizationTest.class);
		suite.addTestSuite(WsSynchronizationTest.class);
		suite.addTestSuite(JaxWsDefaultsCalculatorTest.class);
		// state adapters tests
		suite.addTestSuite(MethodPropertyStateAdapterTest.class);
		suite.addTestSuite(PropertyStateAdapterFactoryTest.class);
		suite.addTestSuite(SeiPropertyStateAdapterTest.class);
		suite.addTestSuite(WsPropertyStateAdapterTest.class);
		suite.addTestSuite(ParameterPropertyStateAdapterTest.class);
		// serialize adapter tests
		suite.addTestSuite(AbstractSerializerAdapterTest.class);
		suite.addTestSuite(MethodSerializerAdapterTest.class);
		suite.addTestSuite(SeiSerializerAdapterTest.class);
		suite.addTestSuite(SerializerAdapterFactoryTest.class);
		suite.addTestSuite(WsSerializerAdapterTest.class);
		suite.addTestSuite(ParameterSerializerAdapterTest.class);
		// default values adapter tests
		suite.addTestSuite(MethodPropertyDefaultsAdapterTest.class);
		suite.addTestSuite(WsPropertyDefaultsAdapterTest.class);
		suite.addTestSuite(SeiPropertyDefaultsAdapterTest.class);
		suite.addTestSuite(ParameterPropertyDefaultsAdapterTest.class);
		// other adapters tests
		suite.addTestSuite(AnnotationAdapterTest.class);
		suite.addTestSuite(AnnotationAdapterFactoryTest.class);
		// validation tests
		suite.addTestSuite(SeiValidationTest.class);
		suite.addTestSuite(WsValidationTest.class);
		suite.addTestSuite(WmValidationTest.class);
		suite.addTestSuite(WpValidationTest.class);
		suite.addTestSuite(EndpointIsSessionBeanRuleTest.class);
		
		return suite;
	}
}
 No newline at end of file