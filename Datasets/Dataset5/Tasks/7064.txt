SingleVariableDeclaration parameter = AnnotationUtils.getMethodParameter(compilationUnit,

/*******************************************************************************
 * Copyright (c) 2009 Shane Clarke.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *    Shane Clarke - initial API and implementation
 *******************************************************************************/
package org.eclipse.jst.ws.internal.jaxws.ui.annotations.contentassist;

import java.util.Collections;
import java.util.List;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jdt.core.CompletionContext;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IMethod;
import org.eclipse.jdt.core.JavaModelException;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.Annotation;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.Expression;
import org.eclipse.jdt.core.dom.IExtendedModifier;
import org.eclipse.jdt.core.dom.MemberValuePair;
import org.eclipse.jdt.core.dom.NormalAnnotation;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.ui.text.java.ContentAssistInvocationContext;
import org.eclipse.jdt.ui.text.java.IJavaCompletionProposalComputer;
import org.eclipse.jdt.ui.text.java.JavaContentAssistInvocationContext;
import org.eclipse.jface.text.contentassist.ICompletionProposal;
import org.eclipse.jst.ws.annotations.core.AnnotationsManager;
import org.eclipse.jst.ws.annotations.core.initialization.IAnnotationAttributeInitializer;
import org.eclipse.jst.ws.annotations.core.utils.AnnotationUtils;
import org.eclipse.jst.ws.internal.jaxws.ui.JAXWSUIPlugin;
import org.eclipse.jst.ws.jaxws.core.utils.JDTUtils;

/**
 * 
 * @author sclarke
 *
 */
public class AnnotationCompletionProposalComputer implements IJavaCompletionProposalComputer {

	public AnnotationCompletionProposalComputer() {
		super();
	}

	@SuppressWarnings("unchecked")
	public List computeCompletionProposals(ContentAssistInvocationContext context, IProgressMonitor monitor) {
	    if (context instanceof JavaContentAssistInvocationContext) {
	        return computeCompletionProposals((JavaContentAssistInvocationContext) context);
	    }
 	    return Collections.emptyList();
	}

	@SuppressWarnings("unchecked")
	private List<ICompletionProposal> computeCompletionProposals(JavaContentAssistInvocationContext context) {
        CompletionContext completionContext = context.getCoreContext();
	    int tokenStart = completionContext.getTokenStart();
	    
	    ICompilationUnit source = context.getCompilationUnit();
		try {
			IJavaElement javaElement = source.getElementAt(tokenStart);
			if (javaElement != null) {
		        
			    CompilationUnit compilationUnit = JDTUtils.getCompilationUnit(source);
			    int elementType = javaElement.getElementType();
			    
                if (elementType == IJavaElement.PACKAGE_DECLARATION) {
                    PackageDeclaration packageDeclaration = compilationUnit.getPackage();
                    List<Annotation> packageAnnotations = packageDeclaration.annotations();
                    for (Annotation annotation : packageAnnotations) {
                        if (annotation instanceof NormalAnnotation) {
                            NormalAnnotation normalAnnotation = (NormalAnnotation) annotation;
                            MemberValuePair memberValuePair = getMemberValuePairForPosition(normalAnnotation,
                                    tokenStart);
                            if (memberValuePair != null) {
                                return getCompletionProposalsForASTNode(normalAnnotation, memberValuePair,
                                        packageDeclaration);                            
                            }
                        }
                    }
                }
                if (elementType == IJavaElement.TYPE || elementType == IJavaElement.FIELD) {
			        return getCompletionProposalsForJavaElement(AnnotationUtils.getExtendedModifiers(
			                compilationUnit, javaElement), javaElement, tokenStart);
                }
                
                if (elementType == IJavaElement.METHOD) {
                    SingleVariableDeclaration parameter = AnnotationUtils.getMethodParameter(
                            (IMethod)javaElement, tokenStart);
                    if (parameter != null) {
                        return getCompletionProposalsForASTNode(parameter.modifiers(), parameter, tokenStart);
                    } else {
                        return getCompletionProposalsForJavaElement(AnnotationUtils.getExtendedModifiers(
                                compilationUnit, javaElement), javaElement, tokenStart);
                    }
                }
			}
		} catch (JavaModelException jme) {
		    JAXWSUIPlugin.log(jme.getStatus());
		}
		return Collections.emptyList();
	}
	
	private List<ICompletionProposal> getCompletionProposalsForASTNode(List<IExtendedModifier> modifiers,
	        ASTNode astNode, int offset) {
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier.isAnnotation() && extendedModifier instanceof NormalAnnotation) {
                NormalAnnotation normalAnnotation = (NormalAnnotation) extendedModifier;
                MemberValuePair memberValuePair = getMemberValuePairForPosition(normalAnnotation, offset);
                if(memberValuePair != null) {
                    return getCompletionProposalsForASTNode(normalAnnotation, memberValuePair,
                            astNode);
                }
            }
        }
	    return Collections.emptyList();
	}

	private List<ICompletionProposal> getCompletionProposalsForJavaElement(List<IExtendedModifier> modifiers,
	        IJavaElement javaElement, int offset) {
        for (IExtendedModifier extendedModifier : modifiers) {
            if (extendedModifier.isAnnotation() && extendedModifier instanceof NormalAnnotation) {
                NormalAnnotation normalAnnotation = (NormalAnnotation) extendedModifier;
                MemberValuePair memberValuePair = getMemberValuePairForPosition(normalAnnotation, offset);
                if(memberValuePair != null) {
                    return getCompletionProposalsForJavaElement(normalAnnotation, memberValuePair, 
                            javaElement);
                }
            }
        }
        return Collections.emptyList();
    }
	
	private List<ICompletionProposal> getCompletionProposalsForASTNode(NormalAnnotation normalAnnotation,
	        MemberValuePair memberValuePair, ASTNode astNode) {
	    IAnnotationAttributeInitializer annotationAttributeInitializer = AnnotationsManager
                .getAnnotationAttributeInitializerForName(normalAnnotation.getTypeName());
	    if (annotationAttributeInitializer != null) {
	        return annotationAttributeInitializer.getCompletionProposalsForMemberValuePair(astNode,
	                memberValuePair);
	    }
        return Collections.emptyList();
	}
	
	private List<ICompletionProposal> getCompletionProposalsForJavaElement(NormalAnnotation normalAnnotation,
	        MemberValuePair memberValuePair, IJavaElement javaElement) {
        IAnnotationAttributeInitializer annotationAttributeInitializer = AnnotationsManager
                .getAnnotationAttributeInitializerForName(normalAnnotation.getTypeName());
        if (annotationAttributeInitializer != null) {
            return annotationAttributeInitializer.getCompletionProposalsForMemberValuePair(javaElement,
                    memberValuePair);
        }
        return Collections.emptyList();
    }

	@SuppressWarnings("unchecked")
	private MemberValuePair getMemberValuePairForPosition(NormalAnnotation normalAnnotation, int offset) {
        List<MemberValuePair> memberValuePairs = normalAnnotation.values();
        for (MemberValuePair memberValuePair : memberValuePairs) {
            Expression value = memberValuePair.getValue();
            int valueStartPosition = value.getStartPosition();
            int valueLength = value.getLength();
            if (offset >= valueStartPosition
                    && offset <= valueStartPosition + valueLength) {
                return memberValuePair;
            }
        }
        return null;
	}
	
	@SuppressWarnings("unchecked")
	public List computeContextInformation(ContentAssistInvocationContext context, IProgressMonitor monitor) {
		return Collections.emptyList();
	}

	public String getErrorMessage() {
		return null;
	}

	public void sessionEnded() {
	}

	public void sessionStarted() {
	}

}