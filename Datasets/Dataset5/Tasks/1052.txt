if (isXmlFile(info.getAbsolutePath())) {

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

package org.eclipse.xpand2.output;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.StringReader;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.ErrorListener;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.URIResolver;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.eclipse.internal.xtend.util.EncodingDetector;
import org.w3c.dom.Document;
import org.xml.sax.EntityResolver;
import org.xml.sax.ErrorHandler;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

/**
 * *
 * 
 * @author Sven Efftinge (http://www.efftinge.de)
 * @author Bernd Kolb
 */
public class XmlBeautifier implements PostProcessor {

	private final Log log = LogFactory.getLog(getClass());

	private String[] fileExtensions = new String[] { ".xml", ".xsl", ".xsd", ".wsdd", ".wsdl" };

	public void setFileExtensions(final String[] fileExtensions) {
		this.fileExtensions = fileExtensions;
	}

	public void beforeWriteAndClose(final FileHandle info) {
		if (isXmlFile(info.getTargetFile().getAbsolutePath())) {
			try {
				// TODO this is only a heuristic, but it should work for most cases. This really is the beginning of reimplementing
				// the XML parser just because we do RAM rather then file based beautification...
				final String bufferedString = info.getBuffer().toString().trim();
				final int indEncoding = bufferedString.indexOf("encoding");
				final int indEndHeader = bufferedString.indexOf("?>");
				String readEncoding = null;
				Document doc = null;
				if (bufferedString.startsWith("<?xml") && indEncoding > 0 && indEncoding < indEndHeader) {
					readEncoding = info.getFileEncoding();
					doc = parseDocument(bufferedString, readEncoding);
				} else {
					doc = parseDocument(bufferedString, null);
				}

				TransformerFactory tfactory = TransformerFactory.newInstance();
				// see http://forum.java.sun.com/thread.jspa?threadID=562510&tstart=90 , comment from xuemingshen
				try {
					tfactory.setAttribute("indent-number", new Integer(2));
				} catch (IllegalArgumentException ignored) {
					// could lead to this exception 
					// see http://oaw.itemis.de/forum/viewtopic.php?showtopic=788
				}
				tfactory.setURIResolver(new URIResolver() {

					public Source resolve(String href, String base) throws TransformerException {
						return new Source() {

							public String getSystemId() {
								return "";
							}

							public void setSystemId(String systemId) {
							}
						};
					}
				});
				Transformer serializer;
				try {
					serializer = tfactory.newTransformer();

					if (doc.getDoctype() != null) {
						String systemValue = doc.getDoctype().getSystemId();
						String publicID = doc.getDoctype().getPublicId();
						serializer.setOutputProperty(OutputKeys.DOCTYPE_SYSTEM, systemValue);
						serializer.setOutputProperty(OutputKeys.DOCTYPE_PUBLIC, publicID);

					}

					// Setup indenting to "pretty print"
					serializer.setOutputProperty(OutputKeys.INDENT, "yes");
					serializer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "2");
					serializer.setOutputProperty(OutputKeys.ENCODING, info.getFileEncoding());
					serializer.setErrorListener(new ErrorListener() {

						public void error(TransformerException arg0) throws TransformerException {
						}

						public void fatalError(TransformerException arg0) throws TransformerException {
						}

						public void warning(TransformerException arg0) throws TransformerException {
						}
					});
					ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
					serializer.transform(new DOMSource(doc), new StreamResult(new OutputStreamWriter(byteArrayOutputStream, info.getFileEncoding())));
					String string = byteArrayOutputStream.toString(info.getFileEncoding());
					info.setBuffer(new StringBuffer(string));
				} catch (TransformerException e) {
					log.error(e.getMessage(), e);
				}
			} catch (final Exception e) {
				log.error(e.getMessage(), e);
			}
		}

	}

	/**
	 * Parses the XML document. If no encoding is defined in the XML string than
	 * this method will try to guess the encoding.
	 * 
	 * @param bufferedString
	 *            An XML string
	 * @param encoding
	 *            The XML encoding, if specified.
	 * @return The parsed document
	 * @throws Exception
	 */
	private Document parseDocument(String bufferedString, String encoding) throws Exception {
		List<String> encodingsToTry = new ArrayList<String>();
		if (encoding != null) {
			encodingsToTry.add(encoding);
		} else {
			byte[] sampleBytes = bufferedString.substring(0, Math.min(64, bufferedString.length())).getBytes();
			encodingsToTry.add(EncodingDetector.detectEncoding(sampleBytes).displayName());
			encodingsToTry.add("ISO-8859-1");
			encodingsToTry.add("UTF-8");
			encodingsToTry.add("MacRoman");
			encodingsToTry.add("UTF-16");
			encodingsToTry.add("UTF-16BE");
			encodingsToTry.add("UTF-16LE");
		}
		encodingsToTry.add(System.getProperty("file.encoding"));

		Document doc = null;
		Exception lastException = null;
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		factory.setExpandEntityReferences(false);
		factory.setValidating(false);

		DocumentBuilder builder = factory.newDocumentBuilder();

		builder.setEntityResolver(new EntityResolver() {
			public InputSource resolveEntity(String publicId, String systemId) throws SAXException, IOException {
				return new InputSource(new StringReader(""));
			}
		});
		builder.setErrorHandler(new ErrorHandler() {
			public void error(SAXParseException exception) throws SAXException {
				log.warn(exception.getMessage());
			}

			public void fatalError(SAXParseException exception) throws SAXException {
				if (exception.getMessage() != null && exception.getMessage().startsWith("Invalid byte")) {
					// ignore, since we try other encodings
				} else {
					log.warn(exception.getMessage());
				}
			}

			public void warning(SAXParseException exception) throws SAXException {
				log.debug(exception.getMessage());
			}
		});

		for (Iterator<String> it = encodingsToTry.iterator(); it.hasNext();) {
			String enc = it.next();
			try {
				doc = builder.parse(new ByteArrayInputStream(bufferedString.getBytes(enc)));
				// if no error exit here
				break;
			} catch (Exception e) {
				lastException = e;
			}
		}
		if (doc == null && lastException != null) {
			throw lastException;
		} else {
			return doc;
		}
	}

	public boolean isXmlFile(final String absolutePath) {
		for (int i = 0; i < fileExtensions.length; i++) {
			if (absolutePath.endsWith(fileExtensions[i].trim()))
				return true;
		}
		return false;
	}

	public void afterClose(final FileHandle impl) {
		// do nothing here
	}

}