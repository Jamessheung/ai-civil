'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Cluster {
    cluster_id: number;
    title: string;
    domain: string;
    cluster_state: string;
    last_updated_at: string;
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

    useEffect(() => {
        fetch('http://localhost:8001/api/clusters')
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
        switch (domain) {
            case 'Power': return 'bg-yellow-900/50 text-yellow-200 border-yellow-800';
            case 'Tech': return 'bg-cyan-900/50 text-cyan-200 border-cyan-800';
            case 'Earth': return 'bg-emerald-900/50 text-emerald-200 border-emerald-800';
            default: return 'bg-neutral-800 text-neutral-400 border-neutral-700';
        }
    };

    const getStateBadge = (state: string) => {
        if (state === 'Active') return <span className="px-2 py-0.5 rounded text-xs font-bold bg-green-500/20 text-green-400 border border-green-500/30">ACTIVE</span>;
        if (state === 'Disputed') return <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">DISPUTED</span>;
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-gray-500/20 text-gray-400 border border-gray-500/30">{state.toUpperCase()}</span>;
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
                        <span className="px-3 py-1 rounded-full border border-white/10 text-xs text-gray-400 tracking-widest uppercase bg-white/5 backdrop-blur-md">System v1.1.1</span>
                        <span className="px-3 py-1 rounded-full border border-cyan-900/30 text-xs text-cyan-400/80 tracking-widest uppercase bg-cyan-900/10 backdrop-blur-md">Gov_1.0 Active</span>
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
                        Active Event Matrix
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
                            <Link href={`/cluster/${cluster.cluster_id}`} key={cluster.cluster_id} className="group relative block bg-[#0a0a0a]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-10 transition-all duration-500 hover:border-cyan-500/30 hover:bg-[#0f0f0f] hover:shadow-[0_0_50px_-20px_rgba(6,182,212,0.1)] overflow-hidden">

                                {/* Decorator Line */}
                                <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${cluster.domain === 'Power' ? 'from-yellow-900/50 to-transparent' : 'from-cyan-900/50 to-transparent'}`}></div>

                                <div className="flex justify-between items-start mb-8">
                                    <div className={`px-4 py-1.5 rounded-full text-xs font-medium tracking-widest uppercase border ${getDomainColor(cluster.domain)} bg-opacity-10`}>
                                        {cluster.domain}
                                    </div>
                                    {getStateBadge(cluster.cluster_state)}
                                </div>

                                <h3 className="text-3xl font-light text-white mb-6 line-clamp-3 group-hover:text-cyan-200 transition-colors leading-snug tracking-wide">
                                    {cluster.title}
                                </h3>

                                <div className="mt-12 flex items-center justify-between border-t border-white/5 pt-6 group-hover:border-white/10 transition-colors">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Last Update</span>
                                        <span className="text-sm font-mono text-gray-300">{new Date(cluster.last_updated_at).toLocaleTimeString()}</span>
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
