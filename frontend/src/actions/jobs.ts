'use server';

import { revalidatePath } from 'next/cache';

export async function refreshJobs() {
  revalidatePath('/jobs');
  return { success: true };
}