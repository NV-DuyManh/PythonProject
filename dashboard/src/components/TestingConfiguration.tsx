import React, { useState, useEffect } from 'react';
import { CodeGateAPI } from '../api/client';
import { Settings, Save } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface TestingConfigurationProps {
  repositoryId: number;
}

export function TestingConfiguration({ repositoryId }: TestingConfigurationProps) {
  const { activeWorkspace } = useAuth();
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Read-only if Reviewer or Developer
  const canEdit = activeWorkspace?.role === 'ADMIN' || activeWorkspace?.role === 'MAINTAINER';

  useEffect(() => {
    CodeGateAPI.getTestingConfiguration(repositoryId)
      .then(data => {
        setConfig(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [repositoryId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canEdit) return;
    
    setSaving(true);
    setError(null);
    setSuccess(false);
    
    try {
      await CodeGateAPI.updateTestingConfiguration(repositoryId, config);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="skeleton skeleton--panel" />;

  return (
    <div className="dashboard-panel mt-6">
      <div className="dashboard-panel__head">
        <div className="dashboard-panel__title">
          <Settings size={18} strokeWidth={1.8} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
          Testing Configuration
        </div>
      </div>
      <div className="dashboard-panel__body">
        {error && (
          <div className="p-3 mb-4 rounded-md bg-red-900/50 text-red-200 text-sm border border-red-800">
            {error}
          </div>
        )}
        {success && (
          <div className="p-3 mb-4 rounded-md bg-green-900/50 text-green-200 text-sm border border-green-800">
            Configuration saved successfully.
          </div>
        )}
        
        <form onSubmit={handleSave} className="space-y-4">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
              <input 
                type="checkbox" 
                checked={config?.enabled || false}
                onChange={e => setConfig({...config, enabled: e.target.checked})}
                disabled={!canEdit}
                className="rounded bg-gray-800 border-gray-700"
              />
              Enable Testing
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
              <input 
                type="checkbox" 
                checked={config?.coverage_enabled || false}
                onChange={e => setConfig({...config, coverage_enabled: e.target.checked})}
                disabled={!canEdit}
                className="rounded bg-gray-800 border-gray-700"
              />
              Enable Coverage Parsing
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
              <input 
                type="checkbox" 
                checked={config?.network_enabled || false}
                onChange={e => setConfig({...config, network_enabled: e.target.checked})}
                disabled={!canEdit}
                className="rounded bg-gray-800 border-gray-700"
              />
              Allow Network Access
            </label>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Executor Type</label>
              <select 
                value={config?.executor_type?.toUpperCase() || 'DISABLED'}
                onChange={e => setConfig({...config, executor_type: e.target.value})}
                disabled={!canEdit}
                className="w-full bg-[#1a1b1e] border border-gray-800 rounded-md p-2 text-gray-200 text-sm focus:border-indigo-500 focus:outline-none"
              >
                <option value="DISABLED">Disabled</option>
                <option value="LOCAL_TRUSTED">Local Trusted (Warning: Unsafe)</option>
                <option value="DOCKER">Docker Isolated (Recommended)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Docker Image</label>
              <input 
                type="text" 
                value={config?.docker_image || ''}
                onChange={e => setConfig({...config, docker_image: e.target.value})}
                disabled={!canEdit}
                placeholder="e.g. python:3.12-slim"
                className="w-full bg-[#1a1b1e] border border-gray-800 rounded-md p-2 text-gray-200 text-sm focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Install Command</label>
              <input 
                type="text" 
                value={config?.install_command || ''}
                onChange={e => setConfig({...config, install_command: e.target.value})}
                disabled={!canEdit}
                placeholder="e.g. pip install -r requirements.txt"
                className="w-full bg-[#1a1b1e] border border-gray-800 rounded-md p-2 text-gray-200 text-sm focus:border-indigo-500 focus:outline-none"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Test Command</label>
              <input 
                type="text" 
                value={config?.test_command || ''}
                onChange={e => setConfig({...config, test_command: e.target.value})}
                disabled={!canEdit}
                placeholder="e.g. pytest"
                className="w-full bg-[#1a1b1e] border border-gray-800 rounded-md p-2 text-gray-200 text-sm focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>
          
          {canEdit && (
            <div className="pt-2">
              <button 
                type="submit" 
                disabled={saving}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
              >
                <Save size={16} />
                {saving ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
