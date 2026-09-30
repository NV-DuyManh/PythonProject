import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';

export function Dialog({ titleId, onClose, children }: { titleId: string; onClose: () => void; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current;
    dialog?.showModal();
    return () => dialog?.close();
  }, []);
  return <dialog ref={ref} className="modal" aria-labelledby={titleId} onCancel={event => { event.preventDefault(); onClose(); }}>
    {children}
  </dialog>;
}
