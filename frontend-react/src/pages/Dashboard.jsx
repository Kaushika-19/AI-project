import React, { useEffect, useState } from 'react';
import { Phone, MessageCircle, Mail, Users, PlusCircle } from 'lucide-react';
import InteractionModal from '../components/InteractionModal';

export default function Dashboard() {
    const [pipeline, setPipeline] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [stats, setStats] = useState({
        totalCustomers: 0,
        activePipeline: 0,
        wonRevenue: 0,
        totalConversations: 0
    });

    const fetchDashboardData = async () => {
        try {
            const [pipelineRes, customersRes, actionsRes] = await Promise.all([
                fetch('/api/v1/pipeline'),
                fetch('/api/v1/customers'),
                fetch('/api/v1/actions')
            ]);

            const pipelineData = await pipelineRes.json();
            const customersData = await customersRes.json();
            const actionsData = await actionsRes.json();

            setPipeline(pipelineData);

            const activeDeals = pipelineData.filter(d => d.status !== 'CLOSED_WON' && d.status !== 'CLOSED_LOST');
            const wonDeals = pipelineData.filter(d => d.status === 'CLOSED_WON');
            const activeValue = activeDeals.reduce((sum, d) => sum + (d.deal_value || 0), 0);
            const wonValue = wonDeals.reduce((sum, d) => sum + (d.deal_value || 0), 0);

            setStats({
                totalCustomers: customersData.length || 0,
                activePipeline: activeValue || 0,
                wonRevenue: wonValue || 0,
                pendingActions: actionsData.filter(a => a.status === 'PENDING').length || 0
            });

        } catch (err) {
            console.error("Failed to load dashboard data", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const stages = ['LEAD', 'DISCOVERY', 'EVALUATION', 'CONSIDERATION', 'NEGOTIATION', 'PROPOSAL', 'CLOSING'];

    if (loading) return <div className="loading-state"><span className="spinner"></span> Loading dashboard...</div>;

    return (
        <section className="page active" id="page-dashboard">
            <div className="page-actions" style={{ justifyContent: 'space-between', marginBottom: '28px' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Overview</h2>
                <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
                    <PlusCircle size={18} /> Record New Interaction
                </button>
            </div>

            <InteractionModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onComplete={fetchDashboardData}
            />

            <div className="stats-grid">
                <div className="stat-card stat-customers">
                    <div className="stat-label">Total Customers</div>
                    <div className="stat-value">{stats.totalCustomers}</div>
                    <div className="stat-sub">Active in database</div>
                </div>
                <div className="stat-card stat-pipeline">
                    <div className="stat-label">Active Pipeline</div>
                    <div className="stat-value">{stats.activePipeline.toLocaleString()}</div>
                    <div className="stat-sub">Across open deals</div>
                </div>
                <div className="stat-card stat-won highlighted">
                    <div className="stat-label">Closed Won (YTD)</div>
                    <div className="stat-value">{stats.wonRevenue.toLocaleString()}</div>
                    <div className="stat-sub">Total earned revenue</div>
                </div>
                <div className="stat-card stat-convos">
                    <div className="stat-label">Pending Actions</div>
                    <div className="stat-value">{stats.pendingActions}</div>
                    <div className="stat-sub">Waiting for execution</div>
                </div>
            </div>

            <div className="dashboard-grid">
                {/* Reminders Section Removed */}

                <div className="card">
                    <div className="card-header">
                        <h3>Pipeline Stages Overview</h3>
                        <span className="badge badge-accent">Live</span>
                    </div>
                    <div className="pipeline-stages">
                        {stages.map(stage => {
                            const count = pipeline.filter(p => p.stage === stage && p.status !== 'CLOSED_WON' && p.status !== 'CLOSED_LOST').length;
                            const isActive = count > 0;
                            return (
                                <div key={stage} className={`stage-pill ${isActive ? 'active-stage' : ''}`}>
                                    <div className="stage-count">{count}</div>
                                    <div className="stage-name">{stage}</div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3>All Active Deals</h3>
                    </div>
                    <div className="activity-feed">
                        {pipeline.filter(o => o.status !== 'CLOSED_WON' && o.status !== 'CLOSED_LOST').slice(0, 10).map(opp => (
                            <div key={opp.opportunity_id} className="activity-item">
                                <div className="activity-icon icon-meeting">
                                    <Users size={18} />
                                </div>
                                <div className="activity-text">
                                    <div className="activity-title">{opp.opportunity_name}</div>
                                    <div className="activity-time">
                                        {opp.customer_name} &bull; <span style={{ color: "var(--accent-light)" }}>{opp.deal_value.toLocaleString()}</span> &bull; {opp.stage}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button
                                        className="btn"
                                        style={{
                                            padding: '6px 14px',
                                            fontSize: '0.75rem',
                                            background: 'rgba(34, 197, 94, 0.1)',
                                            color: '#4ade80',
                                            border: '1px solid rgba(34, 197, 94, 0.3)',
                                            fontWeight: '700'
                                        }}
                                        onClick={async () => {
                                            if (confirm("Close this deal as WON?")) {
                                                try {
                                                    const res = await fetch(`/api/v1/opportunities/${opp.opportunity_id}`, {
                                                        method: 'PUT',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ status: 'CLOSED_WON', closed_date: new Date().toISOString().split('T')[0] })
                                                    });
                                                    if (!res.ok) throw new Error(await res.text());
                                                    fetchDashboardData();
                                                } catch (err) {
                                                    alert("Failed to close deal: " + err.message);
                                                }
                                            }
                                        }}
                                    >
                                        WON
                                    </button>
                                    <button
                                        className="btn"
                                        style={{
                                            padding: '6px 14px',
                                            fontSize: '0.75rem',
                                            background: 'rgba(239, 68, 68, 0.1)',
                                            color: '#f87171',
                                            border: '1px solid rgba(239, 68, 68, 0.3)',
                                            fontWeight: '700'
                                        }}
                                        onClick={async () => {
                                            if (confirm("Close this deal as LOST?")) {
                                                try {
                                                    const res = await fetch(`/api/v1/opportunities/${opp.opportunity_id}`, {
                                                        method: 'PUT',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ status: 'CLOSED_LOST', closed_date: new Date().toISOString().split('T')[0] })
                                                    });
                                                    if (!res.ok) throw new Error(await res.text());
                                                    fetchDashboardData();
                                                } catch (err) {
                                                    alert("Failed to close deal: " + err.message);
                                                }
                                            }
                                        }}
                                    >
                                        LOST
                                    </button>
                                </div>
                            </div>
                        ))}
                        {pipeline.length === 0 && <div className="empty-state">No active deals found.</div>}
                    </div>
                </div>
            </div>
        </section>
    );
}
