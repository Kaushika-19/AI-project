import React, { useEffect, useState } from 'react';
import AddOpportunityModal from '../components/AddOpportunityModal';

export default function Pipeline() {
    const [pipeline, setPipeline] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchPipeline = () => {
        setLoading(true);
        fetch('/api/v1/pipeline')
            .then(res => res.json())
            .then(data => {
                setPipeline(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load pipeline", err);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchPipeline();
    }, []);

    const filteredPipeline = statusFilter
        ? pipeline.filter(p => p.status === statusFilter)
        : pipeline;

    if (loading && pipeline.length === 0) return <div className="loading-state"><span className="spinner"></span> Loading pipeline...</div>;

    return (
        <section className="page active" id="page-pipeline">
            <div className="page-actions">
                <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>+ New Opportunity</button>
                <AddOpportunityModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onComplete={fetchPipeline}
                />
                <div className="filter-group">
                    <select
                        className="filter-select"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        <option value="OPEN">Open</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="ON_HOLD">On Hold</option>
                        <option value="CLOSED_WON">Closed Won</option>
                        <option value="CLOSED_LOST">Closed Lost</option>
                    </select>
                </div>
            </div>
            <div className="pipeline-board">
                {filteredPipeline.map(opp => (
                    <div key={opp.opportunity_id} className={`opportunity-card status-${opp.status}`}>
                        <div className="opp-header">
                            <div>
                                <div className="opp-name">{opp.opportunity_name}</div>
                                <div className="opp-customer">{opp.customer_name} ({opp.company})</div>
                            </div>
                            <span className={`badge badge-${opp.status === 'CLOSED_WON' ? 'success' : opp.status === 'CLOSED_LOST' ? 'danger' : 'info'}`}>
                                {opp.status.replace('_', ' ')}
                            </span>
                        </div>
                        <div className="opp-details">
                            <div className="opp-detail-item">
                                <span className="opp-detail-label">Deal Value</span>
                                <span className="opp-detail-value highlight-value">{opp.deal_value.toLocaleString()}</span>
                            </div>
                            <div className="opp-detail-item">
                                <span className="opp-detail-label">Stage</span>
                                <span className="opp-detail-value">{opp.stage}</span>
                            </div>
                            <div className="opp-detail-item">
                                <span className="opp-detail-label">Lead Score</span>
                                <span className="opp-detail-value highlight-value">{opp.latest_lead_score || 'N/A'}</span>
                            </div>
                            <div className="opp-detail-item">
                                <span className="opp-detail-label">Probability</span>
                                <span className="opp-detail-value">{opp.probability}%</span>
                            </div>
                        </div>
                    </div>
                ))}
                {filteredPipeline.length === 0 && (
                    <div className="empty-state" style={{ gridColumn: '1 / -1' }}>No opportunities found matching criteria.</div>
                )}
            </div>
        </section>
    );
}
