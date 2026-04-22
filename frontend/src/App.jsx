import { useEffect, useMemo, useState } from 'react';
import FileUpload from './components/FileUpload';
import { getJob, resolveUrl, submitJob } from './lib/api';

const modes = [
  { value: 'translation_only', label: 'Translation Only' },
  { value: 'review_only', label: 'Review Only' },
  { value: 'combined', label: 'Translate + Review' },
];

function StatusBadge({ status }) {
  const map = {
    queued: 'bg-slate-200 text-slate-700',
    processing: 'bg-blue-100 text-blue-700',
    completed: 'bg-emerald-100 text-emerald-700',
    failed: 'bg-red-100 text-red-700',
  };
  return <span className={`px-2 py-1 rounded text-xs ${map[status]}`}>{status}</span>;
}

export default function App() {
  const [mode, setMode] = useState('combined');
  const [files, setFiles] = useState([]);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!job || ['completed', 'failed'].includes(job.status)) return;
    const t = setInterval(async () => {
      const latest = await getJob(job.job_id);
      setJob(latest);
    }, 2500);
    return () => clearInterval(t);
  }, [job]);

  const progress = useMemo(() => {
    if (!job?.files?.length) return 0;
    return Math.round(job.files.reduce((sum, f) => sum + f.progress, 0) / job.files.length);
  }, [job]);

  const onSubmit = async () => {
    try {
      setLoading(true);
      setError('');
      const created = await submitJob(mode, files);
      setJob(created);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-6xl mx-auto py-10 px-4 space-y-6">
      <section className="bg-white rounded-xl shadow p-6 space-y-4">
        <h1 className="text-2xl font-semibold text-slate-800">Procurement AI Suite</h1>
        <p className="text-slate-600 text-sm">Upload legal/procurement documents for bilingual translation and risk review.</p>
        <div className="grid md:grid-cols-3 gap-3">
          {modes.map((item) => (
            <button
              key={item.value}
              onClick={() => setMode(item.value)}
              className={`rounded-lg px-4 py-3 border text-sm ${
                mode === item.value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-700 border-slate-300'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
        <FileUpload files={files} setFiles={setFiles} />
        <button
          onClick={onSubmit}
          disabled={loading || files.length === 0}
          className="bg-slate-900 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Start Processing'}
        </button>
        {error && <p className="text-red-600 text-sm">{error}</p>}
      </section>

      {job && (
        <>
          <section className="bg-white rounded-xl shadow p-6 space-y-3">
            <h2 className="font-semibold text-slate-800">Processing</h2>
            <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-blue-600" style={{ width: `${progress}%` }} />
            </div>
            <p className="text-sm text-slate-600">Overall progress: {progress}%</p>
          </section>

          <section className="bg-white rounded-xl shadow p-6">
            <h2 className="font-semibold text-slate-800 mb-3">Results</h2>
            <div className="space-y-3">
              {job.files.map((file) => (
                <div key={file.file_name} className="border rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-slate-800">{file.file_name}</p>
                    <StatusBadge status={file.status} />
                  </div>
                  <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500" style={{ width: `${file.progress}%` }} />
                  </div>
                  {file.message && <p className="text-sm text-red-600">{file.message}</p>}
                  <div className="flex flex-wrap gap-2 text-sm">
                    {file.bilingual_docx && (
                      <a className="px-3 py-1 rounded bg-blue-100 text-blue-800" href={resolveUrl(file.bilingual_docx)} target="_blank">Download DOCX</a>
                    )}
                    {file.bilingual_pdf && (
                      <a className="px-3 py-1 rounded bg-purple-100 text-purple-800" href={resolveUrl(file.bilingual_pdf)} target="_blank">Download PDF</a>
                    )}
                    {file.review_report && (
                      <a className="px-3 py-1 rounded bg-amber-100 text-amber-800" href={resolveUrl(file.review_report)} target="_blank">Download Review</a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </main>
  );
}
