import React, { createContext, useContext, useEffect, useState } from 'react';

interface User {
  id: number;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  active_workspace_id: number | null;
}

interface Workspace {
  id: number;
  name: string;
  slug: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  loading: boolean;
  authenticated: boolean;
  workspaceVersion: number;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
  setActiveWorkspace: (workspaceId: number) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [workspaceVersion, setWorkspaceVersion] = useState(0);

  const fetchAuthData = async (isInitial = false) => {
    try {
      const userRes = await fetch('http://127.0.0.1:8000/api/v1/auth/me', { credentials: 'include' });
      if (!userRes.ok) throw new Error('Not authenticated');
      const userData = await userRes.json();
      setUser(userData);

      const workspacesRes = await fetch('http://127.0.0.1:8000/api/v1/workspaces', { credentials: 'include' });
      if (!workspacesRes.ok) throw new Error('Failed to fetch workspaces');
      const workspacesData = await workspacesRes.json();
      setWorkspaces(workspacesData);

      if (userData.active_workspace_id) {
        const active = workspacesData.find((w: Workspace) => w.id === userData.active_workspace_id);
        setActiveWorkspace(active || (workspacesData.length > 0 ? workspacesData[0] : null));
      } else if (workspacesData.length > 0) {
        setActiveWorkspace(workspacesData[0]);
        // Background activate to keep backend in sync
        await fetch(`http://127.0.0.1:8000/api/v1/workspaces/${workspacesData[0].id}/activate`, {
          method: 'POST',
          credentials: 'include'
        }).catch(console.error);
      } else {
        setActiveWorkspace(null);
      }

      // On initial load after OAuth redirect, make a warm-up request
      // to ensure the session cookie is fully established before
      // downstream pages make their own API calls
      if (isInitial && userData) {
        await fetch('http://127.0.0.1:8000/api/v1/system/status', { credentials: 'include' }).catch(() => {});
      }
    } catch (error) {
      setUser(null);
      setWorkspaces([]);
      setActiveWorkspace(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuthData(true);
  }, []);

  const logout = async () => {
    try {
      await fetch('http://127.0.0.1:8000/api/v1/auth/logout', { method: 'POST', credentials: 'include' });
    } catch (e) {
      console.error(e);
    } finally {
      setUser(null);
      setWorkspaces([]);
      setActiveWorkspace(null);
      setWorkspaceVersion(0);
      window.location.href = '/login';
    }
  };

  const handleSetActiveWorkspace = async (workspaceId: number) => {
    try {
      await fetch(`http://127.0.0.1:8000/api/v1/workspaces/${workspaceId}/activate`, { method: 'POST', credentials: 'include' });
      await fetchAuthData();
      // Increment version so downstream pages refetch workspace-scoped data
      setWorkspaceVersion(v => v + 1);
    } catch (error) {
      console.error("Failed to activate workspace", error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        workspaces,
        activeWorkspace,
        loading,
        authenticated: user !== null,
        workspaceVersion,
        refresh: fetchAuthData,
        logout,
        setActiveWorkspace: handleSetActiveWorkspace,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
