'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Cluster {
    cluster_id: number;
    title: string;
    domain: string;
    cluster_state: string;
    last_updated_at: string;
    // New fields for v2.0 Civilization System
    scores: {
        consistency: number;
        contradiction_ratio: number;
        risk: number;
    };
    evidence_counts: {
        total: number;
        L5: number;
        L4: number;
        L3: number;
    };
    deltas: {
        evidence_weighted: number;
        uncertainty: number;
        claims: number;
    };
    times: {
        tick: string;
        published: string;
        seq: number;
    };
    lens_type: string;
    anthropic_scores?: {
        aix: number;
        aud: number;
    };
}

// Helper for client-side clock
function Clock() {
    const [time, setTime] = useState<string>("");
    useEffect(() => {
        setTime(new Date().toISOString().split('T')[1].split('.')[0]);
        const timer = setInterval(() => {
            setTime(new Date().toISOString().split('T')[1].split('.')[0]);
        }, 1000);
        return () => clearInterval(timer);
    }, []);
    return <>{time}<span className="text-gray-600 text-lg ml-2">Z</span></>;
}

export default function Home() {
    const [clusters, setClusters] = useState<Cluster[]>([]);
    const [loading, setLoading] = useState(true);

    // Use Env Var for API URL (Deployment Support)
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

    useEffect(() => {
        fetch(`${API_BASE}/api/clusters`)
            .then(res => res.json())
            .then(data => {
                setClusters(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const getDomainColor = (domain: string) => {
        const map: any = {
            'Universe': 'border-purple-500/50 text-purple-400 bg-purple-900/20',
            'Earth': 'border-emerald-500/50 text-emerald-400 bg-emerald-900/20',
            'Human': 'border-orange-500/50 text-orange-400 bg-orange-900/20',
            'Power': 'border-red-500/50 text-red-400 bg-red-900/20',
            'Tech': 'border-cyan-500/50 text-cyan-400 bg-cyan-900/20',
            'Culture': 'border-pink-500/50 text-pink-400 bg-pink-900/20',
        };
        return map[domain] || 'border-gray-500/50 text-gray-400';
    };

    const getLensBadge = (type: string) => {
        const activeClass = "bg-white text-black font-bold border-white";
        const inactiveClass = "bg-transparent text-gray-600 border-gray-800 opacity-50";

        return (
            <div className="flex items-center gap-1 bg-[#050505] p-0.5 rounded border border-gray-800">
                <span className={`px-1.5 py-[1px] rounded-[1px] text-[9px] tracking-tighter ${type === 'OBS' ? activeClass : inactiveClass}`}>OBS</span>
                <span className={`px-1.5 py-[1px] rounded-[1px] text-[9px] tracking-tighter ${type === 'ANTH' ? activeClass : inactiveClass}`}>ANTH</span>
            </div>
        );
    };

    const getStateBadge = (cluster: Cluster) => {
        const state = cluster.cluster_state;
        let colorClass = "bg-gray-500/10 text-gray-500 border-gray-500/20";
        if (state === 'Active') colorClass = "bg-green-500/10 text-green-400 border-green-500/20";
        if (state === 'Disputed') colorClass = "bg-red-500/10 text-red-400 border-red-500/20";

        return (
            <div className="flex items-center gap-2">
                {state === 'Disputed' && (
                    <span className="text-[10px] font-mono text-red-500">CR {cluster.scores.contradiction_ratio.toFixed(2)}</span>
                )}
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider border ${colorClass}`}>{state.toUpperCase()}</span>
            </div>
        );
    };

    return (
        <main className="min-h-screen bg-[#050505] text-gray-100 p-8 font-sans selection:bg-cyan-900 selection:text-white">
            {/* Header */}
            <header className="w-full max-w-[1920px] mx-auto px-10 mb-16 flex justify-between items-end border-b border-white/5 pb-8">
                <div>
                    <h1 className="text-6xl font-light tracking-tight mb-2 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500">
                        AI Civilization <span className="text-cyan-500 font-normal">Observer</span>
                    </h1>
                    <div className="flex items-center gap-4 mt-4">
                        <span className="px-3 py-1 rounded-full border border-white/10 text-xs text-gray-400 tracking-widest uppercase bg-white/5 backdrop-blur-md">System v2.0.0</span>
                        <span className="px-3 py-1 rounded-full border border-cyan-900/30 text-xs text-cyan-400/80 tracking-widest uppercase bg-cyan-900/10 backdrop-blur-md">Gov_1.1 Active</span>
                    </div>
                </div>
                <div className="flex gap-10 text-right">
                    <div className="flex flex-col items-end">
                        <span className="text-gray-600 text-xs uppercase tracking-[0.2em] mb-1">System Time (UTC)</span>
                        <span className="text-white text-3xl font-light font-mono tracking-widest">
                            <Clock />
                        </span>
                    </div>
                </div>
            </header>

            {/* Grid */}
            <section className="w-full max-w-[1920px] mx-auto px-10">
                <div className="flex justify-between items-center mb-10">
                    <h2 className="text-sm font-bold text-cyan-500 tracking-[0.3em] uppercase opacity-80 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
                        Active Event Matrix (v1.0 Cards)
                    </h2>
                    <div className="flex gap-2">
                        <button className="px-3 py-1 rounded bg-white/5 border border-white/10 hover:bg-white/10 text-xs">Filter: All Domains</button>
                    </div>
                </div>

                {loading ? (
                    <div className="text-center py-20 text-gray-500 animate-pulse">Initializing Neural Link...</div>
                ) : clusters.length === 0 ? (
                    <div className="text-center py-20 border border-dashed border-white/10 rounded-lg">
                        <p className="text-gray-500">No active clusters observed.</p>
                        <p className="text-xs text-gray-600 mt-2">Connect Ingestor to begin observation.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3 gap-8">
                        {clusters.map(cluster => (
                            <Link href={`/cluster/${cluster.cluster_id}`} key={cluster.cluster_id} className="group relative block bg-[#0a0a0a]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 transition-all duration-500 hover:border-cyan-500/30 hover:bg-[#0f0f0f] hover:shadow-[0_0_50px_-20px_rgba(6,182,212,0.1)] overflow-hidden">

                                {/* Top Decorator */}
                                <div className={`absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r ${cluster.domain === 'Power' ? 'from-red-900 to-transparent' : 'from-cyan-900 to-transparent'}`}></div>

                                {/* A. Meta Row */}
                                <div className="flex justify-between items-center mb-6">
                                    <div className="flex items-center gap-3">
                                        <div className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase border ${getDomainColor(cluster.domain)} bg-opacity-10`}>
                                            {cluster.domain}
                                        </div>
                                        {getLensBadge(cluster.lens_type)}
                                    </div>
                                    {getStateBadge(cluster)}
                                </div>

                                {/* B. Title Block */}
                                <h3 className="text-2xl font-light text-white mb-6 line-clamp-3 group-hover:text-cyan-100 transition-colors leading-snug">
                                    {cluster.cluster_state === 'Disputed' && <span className="text-red-500 font-bold mr-2">DISPUTED:</span>}
                                    {cluster.title}
                                </h3>

                                {/* C. Civilization Strip (NEW) */}
                                <div className="mb-6 flex items-center justify-between py-2 border-t border-b border-white/5 group-hover:border-white/10 transition-colors">
                                    {/* C1. Evidence Counts */}
                                    <div className="flex items-center gap-3 font-mono text-[10px] text-gray-400">
                                        {cluster.evidence_counts?.L5 > 0 ? (
                                            <span className="text-green-400 font-bold">L5 <span className="text-white">{cluster.evidence_counts.L5}</span></span>
                                        ) : <span className="opacity-20">L5 0</span>}
                                        <span className={cluster.evidence_counts?.L4 > 0 ? "text-blue-400" : "opacity-30"}>L4 <span className="text-gray-300">{cluster.evidence_counts?.L4 || 0}</span></span>
                                        <span className="opacity-30">L3 {cluster.evidence_counts?.L3 || 0}</span>
                                    </div>

                                    {/* C2. Deltas */}
                                    {cluster.deltas && (
                                        <div className="flex items-center gap-3 font-mono text-[10px]">
                                            <span className="text-gray-500">ΔE <span className="text-gray-300">+{cluster.deltas.evidence_weighted}</span></span>
                                            <span className={`${cluster.deltas.uncertainty < 0 ? 'text-green-500' : 'text-gray-500'}`}>ΔU {cluster.deltas.uncertainty}</span>
                                            {cluster.deltas.claims > 0 && <span className="text-purple-400">ΔC {cluster.deltas.claims}</span>}
                                        </div>
                                    )}
                                </div>

                                {/* D. Time Row */}
                                <div className="flex items-end justify-between font-mono text-[10px] text-gray-500 tracking-wide">
                                    <div className="flex flex-col gap-1">
                                        <div className="flex items-center gap-2">
                                            <span className="w-1 h-1 rounded-full bg-cyan-500 animate-pulse"></span>
                                            <span className="opacity-50">TICK</span>
                                            <span className="text-cyan-500">{cluster.times?.tick ? new Date(cluster.times.tick).toLocaleTimeString() : '--:--'}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="w-1 h-1 rounded-full bg-gray-600"></span>
                                            <span className="opacity-50">PUB</span>
                                            {cluster.times?.published ? (
                                                <span className="text-gray-300">{new Date(cluster.times.published).toLocaleTimeString()} <span className="text-gray-600">v{cluster.times.seq}</span></span>
                                            ) : (
                                                <span className="text-gray-600 italic">pending</span>
                                            )}
                                        </div>
                                    </div>

                                    <div className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center group-hover:bg-cyan-500/10 group-hover:border-cyan-500/30 transition-all">
                                        <span className="text-gray-400 group-hover:text-cyan-400 text-lg transition-colors">↗</span>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </section>
        </main >
    );
}
