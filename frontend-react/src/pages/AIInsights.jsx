import React, { useEffect, useState } from 'react';
import { Target, Activity, Flame, ShieldAlert } from 'lucide-react';

export default function AIInsights() {
    const [insights, setInsights] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/v1/insights')
            .then(res => res.json())
            .then(data => {
                setInsights(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load insights", err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="loading-state"><span className="spinner"></span> Loading AI Insights...</div>;

    return (
        <section className="page active" id="page-insights">
            <div className="insights-grid">
                {insights.map(insight => (
                    <div key={insight.insight_id} className="insight-card">
                        <div className="insight-header">
                            <span className="insight-intent">{insight.intent}</span>
                            <span className={`badge badge-${insight.sentiment === 'Positive' ? 'success' : insight.sentiment === 'Negative' ? 'danger' : 'info'}`}>
                                {insight.sentiment}
                            </span>
                        </div>
                        <div className="insight-metrics">
                            <div className="insight-metric">
                                <div className="insight-metric-label">Stage Detected</div>
                                <div className="insight-metric-value">{insight.stage_detected || 'Unknown'}</div>
                            </div>
                            <div className="insight-metric">
                                <div className="insight-metric-label">Urgency</div>
                                <div className="insight-metric-value">{insight.urgency || 'Normal'}</div>
                            </div>
                            <div className="insight-metric" style={{ gridColumn: 'span 2' }}>
                                <div className="insight-metric-label">Lead Score</div>
                                <div className="insight-metric-value highlight-metric">{insight.lead_score} / 100</div>
                                <div className="score-bar">
                                    <div
                                        className={`score-bar-fill score-${insight.lead_score > 70 ? 'high' : insight.lead_score > 40 ? 'mid' : 'low'}`}
                                        style={{ width: `${insight.lead_score}%` }}>
                                    </div>
                                </div>
                            </div>
                            <div className="insight-metric" style={{ gridColumn: 'span 2' }}>
                                <div className="insight-metric-label">Objection Identified</div>
                                <div className="insight-metric-value" style={{ color: insight.objection ? 'var(--danger)' : 'var(--success)' }}>
                                    {insight.objection || 'None'}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
                {insights.length === 0 && (
                    <div className="empty-state" style={{ gridColumn: '1 / -1' }}>No AI Insights found.</div>
                )}
            </div>
        </section>
    );
}
