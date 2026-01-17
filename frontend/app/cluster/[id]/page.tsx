'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

interface Evidence {
    evidence_id: number;
    level: number;
    extract: string;
    reliability_score: number;
    pointer: any;
}

interface Claim {
    claim_id: number;
    content: string;
    claim_status: string;
    confidence_score: number;
}

interface DetailData {
    event_cluster: any;
    evidence: Evidence[];
    latest_score: any;
    claims?: Claim[];
}

export default function ClusterDetail() {
    const params = useParams();
    const [data, setData] = useState<DetailData | null>(null);

    useEffect(() => {
        if (!params.id) return;
        fetch(`http://localhost:8001/api/cluster/${params.id}`)
            .then(res => res.json())
            .then(setData)
            .catch(console.error);
    }, [params.id]);

    if (!data) return <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center">Loading Data Stream...</div>;

    const { event_cluster: cluster, evidence, latest_score: score } = data;

    const getLevelStyle = (level: number) => {
        if (level === 5) return 'border-l-4 border-l-green-500 bg-green-900/10';
        if (level === 4) return 'border-l-4 border-l-blue-500 bg-blue-900/10';
        if (level === 3) return 'border-l-4 border-l-yellow-500 bg-yellow-900/10';
        if (level <= 2) return 'border-l-4 border-l-red-500 bg-red-900/10 opacity-60';
        return 'border-l-4 border-gray-500';
    };

    return (
        <div className="h-[100dvh] bg-[#050505] text-gray-200 font-sans flex flex-col overflow-hidden">
            {/* Navbar */}
            <nav className="border-b border-white/10 px-6 py-4 flex items-center gap-4 bg-[#0a0a0a] shrink-0 z-50">
                <a href="/" className="text-gray-500 hover:text-white transition-colors">&larr; Back to Matrix</a>
                <div className="h-4 w-px bg-white/10"></div>
                <span className="font-mono text-sm text-cyan-500">CLUSTER_{cluster.cluster_id}</span>
            </nav>

            <main className="flex-1 grid grid-cols-12 overflow-hidden min-h-0">

                {/* LEFT: EVIDENCE PANEL */}
                <div className="col-span-4 border-r border-white/10 flex flex-col bg-[#080808] h-full overflow-hidden">
                    <div className="p-4 border-b border-white/10 bg-[#0a0a0a]">
                        <h2 className="text-lg font-bold text-gray-400 uppercase tracking-wider">Evidence Log</h2>
                        <div className="text-base text-gray-600 mt-1">{evidence.length} Records Verified</div>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {evidence.map(ev => (
                            <div key={ev.evidence_id} className={`p-5 rounded-r text-lg ${getLevelStyle(ev.level)}`}>
                                <div className="flex justify-between items-start mb-2">
                                    <span className={`text-sm font-bold px-2 py-0.5 rounded ${ev.level >= 4 ? 'bg-white/10 text-white' : 'bg-black/20 text-gray-400'}`}>
                                        L{ev.level}
                                    </span>
                                    <a href={ev.pointer.url} target="_blank" className="text-sm text-cyan-600 hover:text-cyan-400 truncate max-w-[150px]">
                                        SOURCE LINK ↗
                                    </a>
                                </div>
                                <p className="leading-relaxed text-gray-300">"{ev.extract}"</p>
                                <div className="mt-3 text-sm text-gray-600 font-mono">
                                    REL: {(ev.reliability_score * 100).toFixed(0)}%
                                </div>
                            </div>
                        ))}
                        <div className="h-64 w-full shrink-0 flex flex-col items-center justify-center opacity-30">
                            <div className="w-1 h-8 bg-gray-700 mb-2"></div>
                            <span className="text-xs font-mono uppercase tracking-widest text-gray-600">End of Verified Log</span>
                        </div>
                    </div>
                </div>

                {/* CENTER: ANALYSIS / LENS */}
                <div className="col-span-5 border-r border-white/10 flex flex-col bg-[#050505] h-full overflow-hidden">
                    <div className="flex-1 overflow-y-auto p-8">
                        <div className="inline-block px-3 py-1 rounded bg-white/10 text-white text-base font-bold mb-5">
                            {cluster.cluster_state.toUpperCase()}
                        </div>
                        <h1 className="text-5xl font-bold text-white mb-8 leading-tight">
                            {cluster.title}
                        </h1>

                        {/* Observer Lens Metrics */}
                        {score && (
                            <div className="grid grid-cols-2 gap-4 mb-8">
                                <div className="p-5 rounded bg-white/5 border border-white/10">
                                    <div className="text-base text-gray-500 mb-1">CONSISTENCY</div>
                                    <div className="text-4xl font-mono text-white">{(score.consistency * 100).toFixed(1)}%</div>
                                </div>
                                <div className={`p-5 rounded bg-white/5 border border-white/10 ${score.risk > 0.5 ? 'border-red-900/50' : ''}`}>
                                    <div className="text-base text-gray-500 mb-1">RISK LEVEL</div>
                                    <div className={`text-4xl font-mono ${score.risk > 0.5 ? 'text-red-400' : 'text-green-400'}`}>{(score.risk * 100).toFixed(1)}%</div>
                                </div>
                            </div>
                        )}

                        {/* Claims Layer (v2.0) */}
                        {data.claims && data.claims.length > 0 && (
                            <div className="mb-10 animate-fade-in-up">
                                <h3 className="text-xl font-bold text-gray-300 mb-4 flex items-center gap-2">
                                    <span className="w-2 h-2 rounded bg-purple-500"></span>
                                    CORE ASSERTION (Claim Layer)
                                </h3>
                                {data.claims.map(claim => (
                                    <div key={claim.claim_id} className="p-6 rounded border border-purple-500/20 bg-purple-900/10">
                                        <p className="text-2xl text-purple-100 font-light italic leading-relaxed mb-4">
                                            "{claim.content.replace('ASSERTION: ', '')}"
                                        </p>
                                        <div className="flex justify-between items-center text-sm font-mono text-purple-400/60">
                                            <span>STATUS: {claim.claim_status.toUpperCase()}</span>
                                            <span>CONFIDENCE: {(claim.confidence_score * 100).toFixed(0)}%</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}


                        <div className="bg-blue-900/10 border border-blue-900/30 p-6 rounded text-lg text-blue-200 leading-relaxed">
                            <strong className="block mb-3 text-blue-400 text-xl">Observer Lens Active</strong>
                            {cluster.summary || "Analysis indicates high variance in reporting sources. Secondary structure suggests evolving narrative."}
                        </div>
                        <div className="h-32 w-full shrink-0"></div>
                    </div>
                </div>

                {/* RIGHT: TIMELINE / VERSIONS */}
                <div className="col-span-3 bg-[#080808] flex flex-col h-full overflow-hidden">
                    <div className="p-4 border-b border-white/10 bg-[#0a0a0a]">
                        <h2 className="text-lg font-bold text-gray-400 uppercase tracking-wider">System Ticks</h2>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4">
                        <div className="border-l border-white/10 pl-4 space-y-8">
                            <div className="relative">
                                <div className="absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full bg-cyan-500 shadow-[0_0_10px_cyan]"></div>
                                <div className="text-base text-cyan-500 font-mono mb-1">NOW (LIVE)</div>
                                <div className="text-lg text-gray-400">Monitoring incoming streams...</div>
                            </div>
                            {/* Mock History */}
                            <div className="relative opacity-50">
                                <div className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-gray-600"></div>
                                <div className="text-xs text-gray-600 font-mono mb-1">T-10 MIN</div>
                                <div className="text-sm text-gray-500">Internal Tick: Consistency check passed.</div>
                            </div>
                            <div className="relative opacity-30">
                                <div className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-gray-600"></div>
                                <div className="text-xs text-gray-600 font-mono mb-1">T-20 MIN</div>
                                <div className="text-sm text-gray-500">New Evidence (L5) ingested.</div>
                            </div>
                        </div>
                    </div>
                </div>

            </main>
        </div>
    );
}
