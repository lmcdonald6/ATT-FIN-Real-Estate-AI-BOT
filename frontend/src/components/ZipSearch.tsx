import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { Search } from 'lucide-react';

interface ZipSearchProps {
  onSearch?: (zip: string) => void;
  redirectToDashboard?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  isLoading?: boolean;
}

export default function ZipSearch({ 
  onSearch, 
  redirectToDashboard = false, 
  size = 'md', 
  className = '',
  isLoading = false
}: ZipSearchProps) {
  const [zipCode, setZipCode] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const validateZip = (zip: string) => {
    const zipRegex = /^\d{5}$/;
    return zipRegex.test(zip);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateZip(zipCode)) {
      setError('Please enter a valid 5-digit ZIP code');
      return;
    }
    
    setError('');
    
    if (onSearch) {
      onSearch(zipCode);
    }
    
    if (redirectToDashboard) {
      router.push(`/dashboard?zip=${zipCode}`);
    }
  };

  const sizeClasses = {
    sm: 'h-8 text-sm',
    md: 'h-10 text-base',
    lg: 'h-12 text-lg',
  };

  return (
    <div className={`w-full max-w-md mx-auto ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <input
            type="text"
            value={zipCode}
            onChange={(e) => setZipCode(e.target.value.slice(0, 5))}
            placeholder="Enter ZIP code..."
            className={`w-full rounded-lg border border-gray-300 bg-white px-4 pr-12 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 ${sizeClasses[size]}`}
            maxLength={5}
            disabled={isLoading}
          />
          <button
            type="submit"
            className="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-blue-600 disabled:text-gray-400"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
            ) : (
              <Search className="h-5 w-5" />
            )}
          </button>
        </div>
        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
      </form>
    </div>
  );
}
