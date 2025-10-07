'use server';

import { redirect } from 'next/navigation';
import { api } from '@/lib/api';
import { revalidatePath } from 'next/cache';

export async function submitAnalysis(formData: FormData) {
  const url = formData.get('url') as string;
  
  if (!url) {
    return { error: 'URL is required' };
  }

  try {
    const result = await api.startAnalysis(url);
    revalidatePath('/jobs');
    redirect('/jobs');
  } catch (error) {
    return { 
      error: error instanceof Error ? error.message : 'Failed to submit analysis' 
    };
  }
}

export async function downloadReport(jobId: string) {
  try {
    const blob = await api.downloadReport(jobId);
    return { success: true, blob };
  } catch (error) {
    return { 
      error: error instanceof Error ? error.message : 'Failed to download report' 
    };
  }
}