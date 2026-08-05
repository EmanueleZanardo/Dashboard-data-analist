import Link from "next/link";

export default function SingularityPage() {
  return (
    <div className="w-full h-screen bg-[#030712] flex flex-col">
      {/* Header con tasto per tornare al sito principale */}
      <div className="p-4 bg-[#111827] border-b border-gray-800 flex justify-between items-center z-10">
        <h1 className="text-blue-400 font-mono text-lg font-bold">💠 Singularity Quant ETRM</h1>
        <Link 
          href="/" 
          className="text-sm font-mono text-gray-400 hover:text-white bg-gray-800 px-3 py-1 rounded transition-colors"
        >
          ← Torna al Portfolio
        </Link>
      </div>
      
      {/* Dashboard Streamlit con permessi abilitati */}
      <div className="flex-grow w-full relative">
        <iframe
          src="https://czpox8o8x6arnxw96txnvt.streamlit.app/?embed=true"
          className="absolute inset-0 w-full h-full border-none"
          title="Singularity ETRM Dashboard"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
        />
      </div>
    </div>
  );
}
