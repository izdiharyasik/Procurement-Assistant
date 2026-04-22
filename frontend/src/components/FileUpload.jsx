import { useDropzone } from 'react-dropzone';

export default function FileUpload({ files, setFiles }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    onDrop: (accepted) => setFiles((prev) => [...prev, ...accepted]),
  });

  return (
    <div
      {...getRootProps()}
      className={`rounded-xl border-2 border-dashed p-8 text-center cursor-pointer ${
        isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-white'
      }`}
    >
      <input {...getInputProps()} />
      <p className="font-medium text-slate-700">Drag and drop .docx files here</p>
      <p className="text-sm text-slate-500 mt-1">or click to select files</p>
      {files.length > 0 && (
        <ul className="mt-4 text-left text-sm text-slate-700 space-y-1">
          {files.map((file, idx) => (
            <li key={`${file.name}-${idx}`} className="bg-slate-50 rounded p-2">{file.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
