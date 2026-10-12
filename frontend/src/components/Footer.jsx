import React from 'react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200/80 bg-white mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs text-slate-500">
        <span>Synapt · AI-Powered Supply Chain Disruption Assistant</span>
        <span>Empirical 100k MySQL Warehouse • TreeSHAP Explainability</span>
      </div>
    </footer>
  );
}
