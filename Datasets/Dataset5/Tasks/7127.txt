// OK

/*******************************************************************************
 * Copyright (c) 2005, 2009 committers of openArchitectureWare and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     committers of openArchitectureWare - initial API and implementation
 *******************************************************************************/
package org.eclipse.xpand.internal.tests.pr;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Collection;

import junit.framework.TestCase;

import org.eclipse.internal.xpand2.pr.ProtectedRegionResolverImpl;
import org.eclipse.internal.xpand2.pr.ProtectedRegionSyntaxException;
import org.eclipse.internal.xpand2.pr.ProtectedRegionResolverImpl.ProtectedRegionImpl;
import org.eclipse.internal.xpand2.pr.util.FSIO;


/**
 * Unittest for class {@link ProtectedRegionResolverImpl}.
 * @author Karsten Thoms
 */
public class ProtectedRegionResolverImplTest extends TestCase {
	private File file1;
	private File file2;
	private File tempDir;
	/**
	 * Provides access to protected methods that should be tested here.
	 */
	class ProtectedRegionResolverTestImpl extends ProtectedRegionResolverImpl {
	    public Collection<ProtectedRegionImpl> _getAllRegions(final File file) throws ProtectedRegionSyntaxException, IOException {
	    	return super.getAllRegions(file);
	    }
	}
	
	/** Instance under test */
	private ProtectedRegionResolverTestImpl prResolver;
	
	@Override
	public void setUp () throws Exception {
		prResolver = new ProtectedRegionResolverTestImpl();
		
		// create a temporary directory for this test. The directory will be deleted automatically.
		tempDir = new File(System.getProperty("java.io.tmpdir")+"/xpand/");
		tempDir.mkdir();
		tempDir.deleteOnExit();
		
		// Use the temp dir for scanning
		prResolver.setSrcPathes(tempDir.getPath());

		// Create a test file with the content of 'testfile1.txt'
		file1 = new File(tempDir.getPath(),"file1.txt");
		file1.deleteOnExit();
		FSIO.writeSingleFile(new FileWriter(file1), new InputStreamReader(getClass().getResourceAsStream("testfile1.txt")));
		
		// Create a test file with the content of 'testfile2.txt'
		file2 = new File(tempDir.getPath(),"file2.txt");
		file2.deleteOnExit();
		FSIO.writeSingleFile(new FileWriter(file2), new InputStreamReader(getClass().getResourceAsStream("testfile2.txt")));
	}
	
	/**
	 * Tests method <tt>getAllRegions()</tt>. 
	 * @throws Exception
	 * @since 22.01.2008
	 */
	public void testGetAllRegions () throws Exception {
		Collection<ProtectedRegionImpl> allRegions = prResolver._getAllRegions(file1);
		assertNotNull(allRegions);
		assertTrue("File must contain protected regions", !allRegions.isEmpty());
		// disabled protected regions are overread
		assertEquals("Enabled protected regions", 2, allRegions.size());
	}
	
	/**
	 * Tests method {@link ProtectedRegionResolverImpl#getProtectedRegion(String)}. 
	 */
	public void testGetProtectedRegion () {
		assertNull ("Disabled protected region must not be found", prResolver.getProtectedRegion("region1"));
		assertNotNull ("Enabled protected region must be found", prResolver.getProtectedRegion("region2"));
	}
	
	public void testGetEnabledRegion2 () throws Exception {
		ProtectedRegionImpl pr = (ProtectedRegionImpl) prResolver.getProtectedRegion("region2");
		assertNotNull ("Enabled protected region must be found", pr);
		assertEquals("id", "region2", pr.getId());
		assertEquals("body", "this is an enabled protected region", pr.getBody("//", "").trim());
		assertEquals("startString", "//PROTECTED REGION ID(region2) ENABLED START", pr.getStartString("//", ""));
		assertEquals("endString", "//PROTECTED REGION END", pr.getEndString("//", ""));
		// these tests do not make sense, as if the value would be wrong, the previous test would fail (see implementation)
//		assertEquals("startIndex", 225, pr.getStartIndex());
//		assertEquals("endIndex", 264, pr.getEndIndex());
		assertNull("fileEncoding", pr.getFileEncoding());
		assertEquals("file", file1, pr.getFile());
		assertEquals("useBASE64", false, pr.isUseBASE64());
		assertEquals("disabled", false, pr.isDisabled());
	}
	
	/**
	 * In Bug#185493 it is reported that using '&&' as Protected Region ID.  
	 * @throws Exception On any unexpected exception
	 * @see https://bugs.eclipse.org/bugs/show_bug.cgi?id=185493
	 */
	public void testBug185493 () throws Exception {
		File file = new File(tempDir.getPath(),"testbug185493.txt");
		FSIO.writeSingleFile(new FileWriter(file), new InputStreamReader(getClass().getResourceAsStream("testbug185493.txt")));
		file.deleteOnExit();
		ProtectedRegionImpl pr = (ProtectedRegionImpl) prResolver.getProtectedRegion("&&");
		assertNotNull(pr);
	}
	
	/**
	 * Bug#206137 reports that setting multiple source paths in a comma separated list will fail when 
	 * {@link ProtectedRegionResolverImpl#init()} is called.
	 * 
	 * @since 22.01.2008
	 * @see https://bugs.eclipse.org/bugs/show_bug.cgi?id=206137
	 */
	public void testBug206137 () throws Exception{
		File dir1 = new File(tempDir, "dir1/");
		dir1.mkdir();
		dir1.deleteOnExit();
		
		File dir2 = new File(tempDir, "dir2/");
		dir2.mkdir();
		dir2.deleteOnExit();
		
		try {
			// With Bug#206137 this will raise an IllegalArgumentException
			prResolver.setSrcPathes(dir1.getAbsolutePath()+", "+dir2.getAbsolutePath());
			prResolver.init();
		} catch (IllegalArgumentException e) {
			fail ("Failure of Bug#206137 detected");
		}
	}
	
	/**
	 * Sets an invalid value for srcPaths and checks that the appropriate exception is thrown
	 * 
	 * @since 22.01.2008
	 */
	public void testInitWithNonExistingDir () {
		File dir1 = new File(tempDir, getName());
		assertFalse(dir1.exists());
		try {
			prResolver.setSrcPathes(dir1.getAbsolutePath());
			fail("IllegalArgumentException expected.");
		} catch (IllegalArgumentException e) {
			; // OK 
		}
	}
	
	/**
	 * Bug#282350 reports that protected regions are not parsable if the markers are linewrapped
	 * for whatever reason.
	 * 
	 * @since 06.07.2009
	 * @see https://bugs.eclipse.org/bugs/show_bug.cgi?id=282350
	 */
	public void testWrappedMarkers() throws Exception {
		Collection<ProtectedRegionImpl> allRegions = prResolver._getAllRegions(file2);
		assertNotNull(allRegions);
		assertTrue("File must contain protected regions", !allRegions.isEmpty());
		// disabled protected regions are overread
		assertEquals("Enabled protected regions", 1, allRegions.size());
	}
}