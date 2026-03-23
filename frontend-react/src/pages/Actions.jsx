import React, { useEffect, useState } from 'react';
import { Mail, Briefcase, Calendar, User } from 'lucide-react';

export default function Actions() {
    const [actions, setActions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState('');

    useEffect(() => {
        fetch('/api/v1/actions')
            .then(res => res.json())
            .then(data => {
                setActions(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load actions", err);
                setLoading(false);
            });
    }, []);

    const filteredActions = statusFilter
        ? actions.filter(a => a.status === statusFilter)
        : actions;

    const toggleStatus = async (id, currentStatus) => {
        const nextStatus = currentStatus === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
        try {
            const res = await fetch(`/api/v1/actions/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: nextStatus })
            });
            if (res.ok) {
                setActions(actions.map(a => a.action_id === id ? { ...a, status: nextStatus } : a));
            }
        } catch (err) {
            console.error("Failed to update status", err);
        }
    };

    if (loading) return <div className="loading-state"><span className="spinner"></span> Loading actions...</div>;

    return (
        <section className="page active" id="page-actions">
            <div className="page-actions">
                <div className="filter-group">
                    <select
                        className="filter-select"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        <option value="PENDING">Pending</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="COMPLETED">Completed</option>
                        <option value="CANCELLED">Cancelled</option>
                    </select>
                </div>
            </div>
            <div className="actions-list">
                {filteredActions.map(action => (
                    <div
                        key={action.action_id}
                        className={`action-card status-${action.status}`}
                        onClick={() => toggleStatus(action.action_id, action.status)}
                    >
                        <div className="action-checkbox" style={{ cursor: 'pointer' }}>
                            {action.status === 'COMPLETED' ? '✓' : ''}
                        </div>
                        <div className="action-content">
                            <div className="action-title" style={{ textDecoration: action.status === 'COMPLETED' ? 'line-through' : 'none', opacity: action.status === 'COMPLETED' ? 0.6 : 1 }}>
                                {action.description || action.next_best_action}
                            </div>
                            <div className="action-sub">
                                <span>
                                    <Briefcase size={12} style={{ marginRight: '4px' }} />
                                    {action.status.replace('_', ' ')}
                                </span>
                                {action.assigned_to && (
                                    <span>
                                        <User size={12} style={{ marginRight: '4px' }} />
                                        {action.assigned_to}
                                    </span>
                                )}
                                {action.deadline && (
                                    <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <Calendar size={12} />
                                        <input
                                            type="date"
                                            className="date-editor"
                                            style={{
                                                background: 'transparent',
                                                border: 'none',
                                                color: 'inherit',
                                                fontSize: '0.75rem',
                                                cursor: 'pointer',
                                                padding: '2px'
                                            }}
                                            value={action.deadline.split('T')[0]}
                                            onChange={async (e) => {
                                                const newDate = e.target.value;
                                                // Prevent card click (status toggle)
                                                e.stopPropagation();
                                                try {
                                                    const res = await fetch(`/api/v1/actions/${action.action_id}`, {
                                                        method: 'PUT',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ deadline: newDate })
                                                    });
                                                    if (res.ok) {
                                                        setActions(actions.map(a => a.action_id === action.action_id ? { ...a, deadline: newDate } : a));
                                                    }
                                                } catch (err) {
                                                    console.error("Failed to update deadline", err);
                                                }
                                            }}
                                            onClick={e => e.stopPropagation()}
                                        />
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                {filteredActions.length === 0 && (
                    <div className="empty-state">No actions found.</div>
                )}
            </div>
        </section>
    );
}
