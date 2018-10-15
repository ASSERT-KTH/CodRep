package org.eclipse.wst.xquery.set.launching.deploy;

/*******************************************************************************
 * Copyright (c) 2008, 2009 28msec Inc. and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     Gabriel Petrovay (28msec) - initial API and implementation
 *******************************************************************************/
package org.eclipse.wst.xquery.set.internal.launching.deploy;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.jobs.IJobChangeEvent;
import org.eclipse.core.runtime.jobs.IJobChangeListener;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.core.runtime.jobs.JobChangeAdapter;
import org.eclipse.wst.xquery.set.internal.launching.jobs.SETCoreSDKDeployCommandJob;
import org.eclipse.wst.xquery.set.internal.launching.jobs.SETDeployDataJob;
import org.eclipse.wst.xquery.set.internal.launching.jobs.SETDeployProjectJob;

public class Deployer {

    private DeployInfo fDeployInfo;
    private List<Job> fJobs;

    public Deployer(DeployInfo info) {
        fDeployInfo = info;
        initJobs();
    }

    public void initJobs() {
        fJobs = new ArrayList<Job>(1);

        switch (fDeployInfo.getDeployType()) {
        case PROJECT:
            fJobs.add(new SETDeployProjectJob(fDeployInfo, null));
            break;
        case DATA:
            fJobs.add(new SETDeployDataJob(fDeployInfo, null));
            break;
        case PROJECT_AND_DATA:
            fJobs.add(new SETDeployProjectJob(fDeployInfo, null));
            fJobs.add(new SETDeployDataJob(fDeployInfo, null));
            break;
        }
    }

    public DeployInfo getDeployInfo() {
        return fDeployInfo;
    }

    public void setDeployInfo(DeployInfo info) {
        fDeployInfo = info;
        for (Job job : fJobs) {
            if (job instanceof SETCoreSDKDeployCommandJob) {
                ((SETCoreSDKDeployCommandJob)job).setDeployInfo(fDeployInfo);
            }
        }
    }

    private String fLastError;

    public void execute() {
        final Iterator<Job> iterator = fJobs.iterator();

        IJobChangeListener trigger = new JobChangeAdapter() {
            public void done(IJobChangeEvent event) {
                IStatus result = event.getJob().getResult();
                if (result.isOK()) {
                    triggerNextJob(iterator, this);
                } else {
                    setError(result.getMessage());
                }
            }
        };

        triggerNextJob(iterator, trigger);
    }

    public void triggerNextJob(Iterator<Job> jobIterator, IJobChangeListener jobTrigger) {
        if (jobIterator.hasNext()) {
            Job currentJob = jobIterator.next();
            currentJob.addJobChangeListener(jobTrigger);
            currentJob.schedule();
        }
    }

    public void addJobChangeListener(IJobChangeListener listener) {
        for (Job job : fJobs) {
            job.addJobChangeListener(listener);
        }
    }

    private void setError(String error) {
        fLastError = error;
    }

    public String getError() {
        return fLastError;
    }

}