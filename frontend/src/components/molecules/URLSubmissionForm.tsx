'use client';

import { useState } from 'react';
import { useFormStatus } from 'react-dom';
import Input from '@/components/atoms/Input';
import Button from '@/components/atoms/Button';
import { submitAnalysis } from '@/actions/analysis';
import toast from 'react-hot-toast';

function SubmitButton() {
  const { pending } = useFormStatus();
  
  return (
    <Button type="submit" loading={pending} className="w-full">
      {pending ? 'Analyzing...' : 'Start Analysis'}
    </Button>
  );
}

const URLSubmissionForm = () => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (formData: FormData) => {
    setError('');
    const result = await submitAnalysis(formData);
    
    if (result?.error) {
      setError(result.error);
      toast.error(result.error);
    } else {
      toast.success('Analysis started successfully!');
      setUrl('');
    }
  };

  return (
    <form action={handleSubmit} className="space-y-4">
      <Input
        name="url"
        type="url"
        placeholder="https://example.com"
        label="Website URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        error={error}
        required
      />
      <SubmitButton />
    </form>
  );
};

export default URLSubmissionForm;