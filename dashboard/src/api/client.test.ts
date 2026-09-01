import { describe, it, expect, vi, beforeEach } from 'vitest';
import { CodeGateAPI } from './client';

describe('CodeGateAPI', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('aborts previous request when a new request with same key is made', async () => {
    let callCount = 0;
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (_url: any, opts: any) => {
      callCount++;
      const isFirst = callCount === 1;
      
      if (isFirst) {
        return new Promise((_res, rej) => {
          opts?.signal?.addEventListener('abort', () => rej(new Error('AbortError')));
        });
      } else {
        return new Response(JSON.stringify([{ id: 2, name: 'tenant-b-repo' }]), { status: 200 });
      }
    });

    const req1 = CodeGateAPI.getRepositories();
    const req2 = CodeGateAPI.getRepositories();

    await expect(req1).rejects.toThrow('AbortError');
    const res2 = await req2;
    expect(res2).toEqual([{ id: 2, name: 'tenant-b-repo' }]);
  });
});
