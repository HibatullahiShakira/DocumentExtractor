import { useState, useRef, useCallback } from 'react'
import './App.css'

const HEADER_LABELS = [
  'Company', 'Project Ref', 'Order No', 'Delivery Date',
  'Colour', 'Construction', 'Wall (mm)', 'Foam',
  'Endleiste', 'Motor System', 'Total Qty',
]

const POSITION_COLS = [
  { key: 'line',   label: '#'           },
  { key: 'qty',    label: 'Qty'         },
  { key: 'width',  label: 'Width (mm)'  },
  { key: 'height', label: 'Height (mm)' },
  { key: 'l',      label: 'L'           },
  { key: 'r',      label: 'R'           },
  { key: 'motor',  label: 'Motor'       },
  { key: 'pos',    label: 'Position'    },
  { key: 'notes',  label: 'Notes'       },
  { key: 'meas',   label: 'Meas. (mm)'  },
]

function MotorBadge({ value }) {
  if (value === '1') return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700">IO</span>
  if (value === '2') return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-purple-50 text-purple-700">SMI</span>
  return <span className="text-slate-400">—</span>
}

function NoteBadge({ value }) {
  if (value === '0') return <span className="text-slate-400">—</span>
  if (value === '8') return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-600">Notkurbel</span>
  return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-green-50 text-green-700">{value}</span>
}

function Step({ label, done, active }) {
  const cls = done ? 'text-emerald-600' : active ? 'text-blue-600 font-semibold' : 'text-slate-400'
  const dot = done ? '✓' : active ? '●' : '○'
  return (
    <div className={`flex items-center gap-2.5 text-sm ${cls}`}>
      <span className="w-5 text-center text-xs">{dot}</span>
      <span>{label}</span>
    </div>
  )
}

export default function App() {
  const [file, setFile]         = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [status, setStatus]     = useState('idle')   // idle | loading | done | error
  const [result, setResult]     = useState(null)
  const [error, setError]       = useState('')
  const inputRef = useRef(null)

  const handleFile = useCallback((f) => {
    if (!f) return
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are accepted.')
      setStatus('error')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File exceeds the 10 MB limit.')
      setStatus('error')
      return
    }
    setFile(f)
    setError('')
    setStatus('idle')
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }, [handleFile])

  const handleExtract = async () => {
    if (!file) return
    setStatus('loading')
    setResult(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch('/extract', { method: 'POST', body: form })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail ?? `Server error ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
      setStatus('done')
    } catch (e) {
      setError(e.message)
      setStatus('error')
    }
  }

  const handleDownload = async () => {
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch('/download', { method: 'POST', body: form })
      if (!res.ok) return
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name.replace(/\.pdf$/i, '_mapped.txt')
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      // silently ignore download errors
    }
  }

  const reset = () => {
    setFile(null)
    setResult(null)
    setStatus('idle')
    setError('')
  }

  const dropZoneCls = [
    'border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors duration-200',
    dragOver
      ? 'border-blue-600 bg-blue-50'
      : file
        ? 'border-solid border-blue-600 bg-blue-50'
        : 'border-slate-300 bg-slate-100 hover:border-blue-500 hover:bg-blue-50',
  ].join(' ')

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">

      {/* ── TOP NAV ── */}
      <header className="bg-slate-900 border-b border-slate-800 px-8 h-16 flex items-center sticky top-0 z-50">
        <div className="max-w-[1100px] w-full mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🪟</span>
            <div>
              <h1 className="text-[1.05rem] font-bold text-slate-50 tracking-tight">Rolladen Extractor</h1>
              <p className="text-[0.72rem] text-slate-500 mt-0.5">PDF purchase order extraction &amp; mapping</p>
            </div>
          </div>
          {status === 'done' && (
            <div className="flex gap-2.5">
              <button
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-slate-400 border border-slate-700 hover:bg-slate-800 hover:text-slate-50 transition-colors cursor-pointer"
                onClick={reset}
              >↩ New File</button>
              <button
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold bg-blue-700 text-white hover:bg-blue-800 transition-colors cursor-pointer"
                onClick={handleDownload}
              >↓ Download .txt</button>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-[1100px] mx-auto px-8 py-8">

        {/* ── UPLOAD ── */}
        {(status === 'idle' || status === 'error') && (
          <div className="max-w-[520px] mx-auto mt-16 bg-white rounded-xl p-8 shadow-lg">
            <div
              className={dropZoneCls}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => inputRef.current.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => handleFile(e.target.files[0])}
              />
              {file ? (
                <div className="flex items-center gap-3 text-left">
                  <span className="text-4xl flex-shrink-0">📄</span>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-slate-900 break-all">{file.name}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{(file.size / 1024).toFixed(1)} KB · PDF</p>
                  </div>
                  <button
                    className="px-2.5 py-1 text-xs font-semibold rounded-lg text-slate-400 border border-slate-300 hover:bg-slate-100 cursor-pointer"
                    onClick={(e) => { e.stopPropagation(); setFile(null) }}
                  >✕</button>
                </div>
              ) : (
                <div className="pointer-events-none">
                  <span className="text-5xl block mb-3">📁</span>
                  <p className="text-lg font-semibold mb-1">Drop your PDF here</p>
                  <p className="text-sm text-slate-500">or click to browse — max 10 MB</p>
                </div>
              )}
            </div>

            {status === 'error' && (
              <div className="mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                ⚠ {error}
              </div>
            )}

            <button
              className="mt-4 w-full inline-flex items-center justify-center py-3 rounded-lg text-base font-semibold bg-blue-700 text-white hover:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
              disabled={!file}
              onClick={handleExtract}
            >
              Extract &amp; Map
            </button>
          </div>
        )}

        {/* ── LOADING ── */}
        {status === 'loading' && (
          <div className="max-w-[420px] mx-auto mt-20 bg-white rounded-xl px-10 py-12 shadow-lg text-center">
            <div className="w-12 h-12 rounded-full border-4 border-slate-200 border-t-blue-600 animate-spin mx-auto mb-6" />
            <p className="text-xl font-bold mb-1.5">Extracting data…</p>
            <p className="text-sm text-slate-500 mb-8 leading-relaxed">Sending PDF to vision model — this takes 10–30 seconds</p>
            <div className="flex flex-col gap-3 text-left">
              <Step label="Rendering PDF to image"    done />
              <Step label="Running vision extraction" active />
              <Step label="Applying mapping rules"    />
            </div>
          </div>
        )}

        {/* ── RESULTS ── */}
        {status === 'done' && result && (
          <div className="flex flex-col gap-5">
            <div className="flex items-center gap-2.5 flex-wrap py-1">
              <span className="text-base font-semibold text-slate-900">📄 {result.filename}</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-600">✓ Extracted</span>
              <span className="text-xs text-slate-500 ml-auto">{result.mapped.positions.length} positions</span>
            </div>

            {/* Order header */}
            <section className="bg-white rounded-xl p-6 shadow-sm">
              <h2 className="text-xs font-bold uppercase tracking-widest text-slate-500 mb-5">
                Order Header
              </h2>
              <div className="grid grid-cols-[repeat(auto-fill,minmax(175px,1fr))] gap-2.5">
                {HEADER_LABELS.map((label, i) => (
                  <div key={i} className="bg-slate-50 rounded-lg px-4 py-3 flex flex-col gap-1 border border-slate-200">
                    <span className="text-[0.67rem] font-bold uppercase tracking-wider text-slate-400">{label}</span>
                    <span className="text-sm font-semibold text-slate-900 break-words leading-snug">{result.mapped.header[i] || '—'}</span>
                  </div>
                ))}
              </div>
            </section>

            {/* Positions table */}
            <section className="bg-white rounded-xl p-6 shadow-sm">
              <h2 className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-slate-500 mb-5">
                Positions
                <span className="bg-blue-50 text-blue-700 rounded-full px-2 py-0.5 text-[0.7rem] font-bold">
                  {result.mapped.positions.length}
                </span>
              </h2>
              <div className="overflow-x-auto rounded-lg border border-slate-200">
                <table className="w-full border-collapse text-sm">
                  <thead>
                    <tr>
                      {POSITION_COLS.map(c => (
                        <th key={c.key} className="bg-slate-900 text-slate-400 px-4 py-2.5 text-left text-[0.68rem] font-bold uppercase tracking-wider whitespace-nowrap">
                          {c.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.mapped.positions.map((row, i) => (
                      <tr key={i} className="border-b border-slate-100 last:border-b-0 hover:bg-slate-50">
                        <td className="px-4 py-2.5 font-bold text-slate-400 w-10">{row[0]}</td>
                        <td className="px-4 py-2.5 whitespace-nowrap">{row[1]}</td>
                        <td className="px-4 py-2.5 font-mono font-semibold whitespace-nowrap">{row[2]}</td>
                        <td className="px-4 py-2.5 font-mono font-semibold whitespace-nowrap">{row[3]}</td>
                        <td className="px-4 py-2.5 text-center whitespace-nowrap">
                          {row[4] === '1'
                            ? <span className="text-blue-700 font-extrabold">L</span>
                            : <span className="text-slate-400">—</span>}
                        </td>
                        <td className="px-4 py-2.5 text-center whitespace-nowrap">
                          {row[5] === '1'
                            ? <span className="text-blue-700 font-extrabold">R</span>
                            : <span className="text-slate-400">—</span>}
                        </td>
                        <td className="px-4 py-2.5 whitespace-nowrap"><MotorBadge value={row[6]} /></td>
                        <td className="px-4 py-2.5 font-bold text-xs whitespace-nowrap">{row[7]}</td>
                        <td className="px-4 py-2.5 whitespace-nowrap"><NoteBadge value={row[8]} /></td>
                        <td className="px-4 py-2.5 whitespace-nowrap">
                          {row[9] !== '0' ? row[9] : <span className="text-slate-400">—</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Raw output */}
            <section className="bg-white rounded-xl p-6 shadow-sm">
              <details className="rounded-lg overflow-hidden border border-slate-200">
                <summary className="px-4 py-3 text-sm font-semibold cursor-pointer list-none text-slate-500 select-none bg-slate-50 hover:bg-slate-200 transition-colors">
                  View raw .txt output
                </summary>
                <pre className="bg-slate-900 text-sky-300 px-6 py-5 text-xs leading-relaxed overflow-x-auto font-mono">
                  {result.txt_content}
                </pre>
              </details>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}
