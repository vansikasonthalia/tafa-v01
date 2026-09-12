'use client';

import { useState, useRef } from 'react';

export default function FileDropZone({ onUpload, disabled }) {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const inputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!['csv', 'xlsx'].includes(ext)) {
      setResult({ error: 'Please upload a .csv or .xlsx file.' });
      return;
    }

    setUploading(true);
    setResult(null);

    try {
      const res = await onUpload(file);
      setResult(res);
    } catch (err) {
      setResult({ error: err.message || 'Upload failed.' });
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer?.files?.[0];
    handleFile(file);
  };

  const handleChange = (e) => {
    const file = e.target.files?.[0];
    handleFile(file);
    // Reset input so same file can be re-uploaded
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div>
      <div
        className={`dropzone ${dragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx"
          onChange={handleChange}
          disabled={disabled || uploading}
        />
        {uploading ? (
          <>
            <div className="spinner" style={{ margin: '0 auto 12px' }}></div>
            <p className="dropzone-title">Uploading...</p>
          </>
        ) : (
          <>
            <p className="dropzone-title">
              Drop your stock list here, or click to browse
            </p>
            <p className="dropzone-sub">
              <code>.csv</code> or <code>.xlsx</code> with a column named{' '}
              <code>ticker</code> (or symbols in the first column)
            </p>
          </>
        )}
      </div>

      {result && (
        <div
          style={{
            marginTop: '12px',
            padding: '10px 16px',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.8rem',
            background: result.error ? 'var(--red-muted)' : 'var(--green-muted)',
            color: result.error ? 'var(--red)' : 'var(--green)',
            border: `1px solid ${result.error ? 'rgba(248,113,113,0.2)' : 'rgba(52,211,153,0.2)'}`,
          }}
        >
          {result.error
            ? `❌ ${result.error}`
            : `✓ Added ${result.added} ticker${result.added !== 1 ? 's' : ''}${result.skipped ? `, ${result.skipped} already existed` : ''}. Total: ${result.total}`
          }
        </div>
      )}
    </div>
  );
}
