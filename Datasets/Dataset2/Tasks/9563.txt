return (Assembly)completeMatches.iterator().next();

package org.jboss.ejb.plugins.cmp.ejbql;

import java.util.Iterator;

public abstract class Parser {
	private Assembler assembler;

	public Parser() {
	}

	public abstract AssemblySet match(AssemblySet in);
	
	public AssemblySet matchAndAssemble(AssemblySet in) {
		AssemblySet matchedSet = match(in);
		if(assembler == null) {
			return matchedSet;
		}
		
		AssemblySet out = new AssemblySet();
		for(Iterator i = matchedSet.iterator(); i.hasNext(); ) {
			Assembly a = (Assembly)i.next();
			assembler.workOn(a);
			if(a.isValid()) {
				out.add(a);
			}
		}
		return out;
	}
	
	public Assembly bestMatch(Assembly a) {
		AssemblySet set = new AssemblySet();
		set.add(a);
		set = matchAndAssemble(set);
		return best(set);
	}
	
	public Assembly completeMatch(Assembly a) {
		Assembly best = bestMatch(a);
		if(best == null || best.hasNextToken()) {
			return null;
		}
		return best;
	}
	
	public Assembly soleMatch(Assembly in) {
		AssemblySet set = new AssemblySet();
		set.add(in);
		set = matchAndAssemble(set);
		
		AssemblySet completeMatches = new AssemblySet();
		for(Iterator i = set.iterator(); i.hasNext(); ) {
			Assembly a = (Assembly) i.next();

			// is this a complete match, can't get better then that
			if(!a.hasNextToken()) {
				completeMatches.add(a);
			}
		}

		if(completeMatches.size()==0) {
			return best(set);
		}
		if(completeMatches.size() > 1) {
			throw new IllegalStateException("Multiple assemblies matched: "+set.size());
		}
		return (Assembly)completeMatches.iterator().next();;
	}
	
	public void setAssembler(Assembler assembler) {
		this.assembler = assembler;
	}
	
	private Assembly best(AssemblySet set) {
		Assembly best = null;
		for(Iterator i = set.iterator(); i.hasNext(); ) {
			Assembly a = (Assembly) i.next();

			// is this a complete match, can't get better then that
			if(!a.hasNextToken()) {
				return a;
			}
			
			// do we have a best
			if(best == null) {
				best = a;
			} else {
				// did a match more tokens then the current best
				if(a.getTokensUsed() > best.getTokensUsed()) {
					best = a;
				}
			}
		}
		return best;
	}	
}